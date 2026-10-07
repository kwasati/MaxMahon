---
project: MaxMahon
created: 2026-04-25
last_updated: 2026-04-25
status: done
---

# Pipeline Performance Overhaul — cache + parallel fetch + progress logging

> Reduce scan time from ~30 min (right at timeout limit) → ~5-6 min via 3 changes: (1) day-scoped per-symbol cache so re-runs same day skip fetch entirely, (2) ThreadPoolExecutor 5 workers parallel fetch (IO bound network calls), (3) progress logging every 50 stocks + ETA. Touches 2 files: scripts/fetch_data.py + scripts/screen_stocks.py. Sequential phases (cache→parallel→logging→test). After this ship, can revert subprocess timeout 3600→1800 if desired since margin huge.

## Phase 1: Cache layer — day-scoped per-symbol snapshots
- [x] เพิ่ม 2 helper functions ใน `projects/MaxMahon/scripts/fetch_data.py` ก่อน function `fetch_multi_year` (~line 199): `_cache_dir_today()` returns `Path('data/screener_cache') / datetime.now().strftime('%Y-%m-%d')` และ `_load_from_cache(symbol)` returns dict | None (อ่านจาก `{cache_dir}/{symbol}.json` ถ้ามี + parse แล้วต้องมี field 'fetched_at' ที่อยู่ในวันเดียวกัน เพื่อกัน corrupted cache, ถ้า parse fail return None silently) และ `_save_to_cache(symbol, data)` writes data to `{cache_dir}/{symbol}.json` (skip ถ้า data.get('delisted') หรือ not data.get('price') — ไม่ cache failures), use `ensure_ascii=False, indent=None` (compact). Scope: **ห้ามแก้** fetch_multi_year function เอง — แค่เพิ่ม helpers. Acceptance: `py -m py_compile scripts/fetch_data.py` exit 0; manually test `_cache_dir_today()` returns valid Path with today's date
- [x] แก้ `fetch_multi_year_safe(symbol)` ใน scripts/fetch_data.py (~line 232-254) เพิ่ม cache check ก่อน fetch + cache save หลัง fetch สำเร็จ: เพิ่ม optional param `use_cache: bool = True`, ถ้า use_cache → call `_load_from_cache(symbol)` ก่อน → ถ้าได้ data return ทันที (skip fetch). หลัง fetch เสร็จ + ไม่ delisted/error → call `_save_to_cache(symbol, result)`. Scope: **ห้ามแก้ logic อื่น** — แค่เพิ่ม cache wrapper. Backward compat: caller เก่าไม่ต้องส่ง use_cache (default True). Acceptance: รัน `py -c "from scripts.fetch_data import fetch_multi_year_safe; d = fetch_multi_year_safe('AOT.BK'); print(bool(d.get('price')))"` first time → fetch; second time → instant load from cache (verify by deleting cache file → re-run takes longer)

### Reference
```python
# new helpers in fetch_data.py — place before def fetch_multi_year
CACHE_ROOT = Path(__file__).parent.parent / 'data' / 'screener_cache'

def _cache_dir_today() -> Path:
    today = datetime.now().strftime('%Y-%m-%d')
    return CACHE_ROOT / today

def _load_from_cache(symbol: str) -> dict | None:
    p = _cache_dir_today() / f'{symbol}.json'
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
        # Sanity check: fetched_at must be from today (cache file might be stale on day rollover)
        fa = data.get('fetched_at', '')
        if fa.startswith(datetime.now().strftime('%Y-%m-%d')):
            return data
    except Exception:
        pass
    return None

def _save_to_cache(symbol: str, data: dict) -> None:
    if not data or data.get('delisted') or not data.get('price'):
        return  # don't cache failures
    cache_dir = _cache_dir_today()
    cache_dir.mkdir(parents=True, exist_ok=True)
    p = cache_dir / f'{symbol}.json'
    try:
        p.write_text(json.dumps(data, ensure_ascii=False, default=str), encoding='utf-8')
    except Exception as e:
        logger.warning(f'cache save failed for {symbol}: {e}')

# modified fetch_multi_year_safe (replace existing ~line 232-254)
def fetch_multi_year_safe(symbol: str, use_cache: bool = True) -> dict:
    if use_cache:
        cached = _load_from_cache(symbol)
        if cached is not None:
            return cached
    try:
        result = fetch_multi_year(symbol)
    except Exception as e:
        logger.warning(f'fetch failed for {symbol}: {e}')
        return {'symbol': symbol, 'delisted': True, 'error': str(e)}
    if isinstance(result, dict) and 'error' in result and not result.get('price'):
        err = result.get('error', 'unknown')
        logger.warning(f'fetch returned error for {symbol}: {err}')
        return {'symbol': symbol, 'delisted': True, 'error': str(err)}
    if use_cache:
        _save_to_cache(symbol, result)
    return result
```

## Phase 2: Parallel fetch — ThreadPoolExecutor 5 workers
- [x] Refactor `main()` ใน `projects/MaxMahon/scripts/screen_stocks.py` (~line 670) แยกเป็น 2 phases: **Phase A** parallel fetch all symbols ที่ไม่ blacklisted ผ่าน `ThreadPoolExecutor(max_workers=5)`, collect dict `fetched_data: dict[str, dict] = {sym: data}`. **Phase B** serial post-process (existing filter/score/save baseline logic) iterate symbols + lookup `fetched_data.get(sym)`. ห้ามเปลี่ยน Phase B logic — แค่ย้าย `data = fetch_multi_year_safe(sym)` call ออก. Import `from concurrent.futures import ThreadPoolExecutor, as_completed` ที่ต้นไฟล์. **Thread safety:** fetch_multi_year_safe is read-only HTTP + per-file cache write (independent files = no conflict). baselines/candidates/etc. อยู่ใน Phase B เดียวเท่านั้น = no race. Print '[fetched i/total] {sym}' ทุกครั้งที่ future complete (ใน Phase A) แทน sequential print เก่า. Scope: **ห้ามแตะ** function อื่น (load_exit_baselines, save_exit_baseline, hard_filter, quality_score, etc). Acceptance: `py -m py_compile scripts/screen_stocks.py` exit 0; รัน scan 50 stocks subset → fetched_data populated ครบ + Phase B output identical กับก่อน parallelize
- [x] Refactor `main()` ใน `projects/MaxMahon/scripts/fetch_data.py` (~line 256) ใช้ ThreadPoolExecutor 5 workers parallel fetch watchlist symbols (เหมือน screen_stocks). ลบ `time.sleep(0.3)` ออก — parallel ไม่ต้อง throttle. เก็บ output ลง snapshot_{date}.json เหมือนเดิม (รักษา compat กับ scan.py downstream). Scope: ห้ามเปลี่ยน output JSON shape. Acceptance: `py -m py_compile scripts/fetch_data.py` exit 0; รัน `py scripts/fetch_data.py` ด้วย watchlist 5-10 ตัว → snapshot file format ตรงเหมือนเดิม + เร็วกว่าเดิมเห็นได้

### Reference
```python
# screen_stocks.py — new main() structure
from concurrent.futures import ThreadPoolExecutor, as_completed
import time as _time_module

def main():
    universe = json.loads(UNIVERSE.read_text(encoding='utf-8'))
    user_data = json.loads(USER_DATA.read_text(encoding='utf-8'))
    watched = set(user_data.get('watchlist', []))
    blacklisted = set(user_data.get('blacklist', []))
    symbols = universe['symbols']
    print(f'Max Mahon v5 screening {len(symbols)} stocks (Niwes 5-5-5-5)...')
    baselines = load_exit_baselines()
    prior_screener_files = load_prior_screener_files()

    # ===== Phase A — parallel fetch =====
    fetch_targets = [s for s in symbols if s not in blacklisted]
    fetched_data: dict[str, dict] = {}
    fetch_start = _time_module.time()
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(fetch_multi_year_safe, sym): sym for sym in fetch_targets}
        for n, future in enumerate(as_completed(futures), 1):
            sym = futures[future]
            try:
                fetched_data[sym] = future.result()
            except Exception as e:
                fetched_data[sym] = {'symbol': sym, 'delisted': True, 'error': str(e)}
            print(f'  [fetched {n}/{len(fetch_targets)}] {sym}')
    fetch_elapsed = _time_module.time() - fetch_start
    print(f'\n=== Fetch phase done in {fetch_elapsed:.1f}s ({fetch_elapsed/len(fetch_targets):.2f}s/stock avg) ===\n')

    # ===== Phase B — serial post-process (existing logic) =====
    candidates = []
    review_candidates: list[dict] = []
    filtered_stocks = []
    filtered_out = 0
    error_count = 0
    for i, sym in enumerate(symbols):
        if sym in blacklisted:
            print(f'  [{i+1}/{len(symbols)}] {sym} — blacklisted, skipping')
            continue
        try:
            data = fetched_data.get(sym)
            # ... existing logic from current main() — UNCHANGED ...
        except Exception as e:
            error_count += 1
            print(f'  [{i+1}/{len(symbols)}] {sym} — exception: {e}')
    # ... rest of main (write screener_*.json) unchanged ...
```

## Phase 3: Progress logging — summary + ETA
- [x] เพิ่ม progress summary ใน Phase A loop ของ `screen_stocks.py main()` — ทุก 50 stocks completed (mod 50 == 0) print 1 บรรทัด: `=== Progress: 50/933 (5.4%) elapsed=98s avg=1.96s/stock ETA=1731s ===`. คำนวณ ETA = (avg × remaining). ใช้ `time.time()` จับ elapsed จาก fetch_start. Scope: ห้ามแก้ Phase B (เก็บ per-stock log เดิม). Acceptance: scan 933 stocks → summary lines ปรากฏที่ 50, 100, 150, ..., 900 = 18 summary lines

## Phase 4: Smoke test + verify
- [x] Validate ทั้ง pipeline locally: (1) `py -m py_compile scripts/fetch_data.py scripts/screen_stocks.py` exit 0, (2) ลบ cache `rm -rf data/screener_cache/$(date +%Y-%m-%d)` (clean slate), (3) วัด time แรก: `time py scripts/screen_stocks.py 2>&1 | tail -30` — ต้องเสร็จ < 15 นาที (จากเดิม ~30+ นาที), (4) วัด time ครั้งสองทันที (cache hit): ต้องเสร็จ < 30 วินาที (cache load only), (5) เปรียบเทียบ output `data/screener_*.json` ใหม่กับ run ก่อนหน้า (vimdiff หรือ jq diff) — pass count + score top 10 ต้องเหมือนหรือใกล้เคียงมาก (<5% drift, แค่ราคา realtime อาจต่าง). Scope: ห้ามแก้ source — verification only. Acceptance: ทั้ง 5 checks pass + screenshot tail output แปะ Karl
