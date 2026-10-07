---
project: 4-MaxMahon
created: 2026-05-19
last_updated: 2026-05-19
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: ดึง DPS event-by-event จาก set.or.th public JSON API ใส่ cache local → แทน yahoo เป็น primary source ของ `dividend_history` → ผลลัพธ์ตรง SETSMART real FY DPS ภายใน ±5% สำหรับ HTC + 4 ตัว ground truth (BBL, ILM, KBANK, PTT, AMATA)

### รายละเอียด
- Discovery: set.or.th มี public JSON endpoint `https://www.set.or.th/api/set/stock/{SYM}/corporate-action?lang=en` ที่ return list ของ events รวม Cash Dividend (caType=XD) + ratios + meetings (XM, filter ทิ้ง)
- Endpoint return per event: `dividend` (DPS), `beginOperation` + `endOperation` (FY period YYYY-MM-DD), `paymentDate`, `xdate`, `dividendType` (Cash Dividend vs Stock Dividend) — มี operation period ตรงๆ ไม่ต้อง heuristic
- Cloudflare block direct requests (403) → ต้อง Playwright bootstrap cookies ครั้งแรก แล้ว reuse cookies + headers สำหรับ subsequent calls (Playwright APIRequestContext ใช้ได้เลย ไม่ต้อง browser navigate ทุก call)
- FY attribution: ใช้ `endOperation.year` ตรงๆ (ไม่ใช้ heuristic Jan-Jun/Jul-Dec ของ `_attribute_dividends_to_fiscal_years` เดิม) — สรุป: events ที่ endOperation 2024-12-31 = FY 2024
- Cache schema: `{symbol, fetched_at, events: [{xdate, payment_date, begin_operation, end_operation, dps, dividend_type, source_of_dividend}, ...]}` — เก็บ raw events ไม่ pre-aggregate (ให้ caller compute FY ได้)
- Stock Dividend (dividendType=Stock Dividend หรือ ratio != null) ต้อง skip ตอน compute DPS sum (เป็น stock split/dividend ไม่ใช่ cash)
- Cache path: `projects/4-MaxMahon/data/set_dividend_cache/{SYMBOL}.json` — รายตัว gitignore
- Cache TTL: refresh ทุก 7 วัน (dividend ไม่เปลี่ยนบ่อย, weekly cron พอ)
- Integration patch: `data_adapter.py` line 791-792 — เปลี่ยน priority: set_official → yahoo fallback → empty
- Fallback: set.or.th fail (Cloudflare block / network error / empty list) → ใช้ yahoo + add tag `DPS_SOURCE_YAHOO` ใน warnings
- Cron job: extend `apply_schedule()` ใน `server/app.py` — add `weekly_dividend_refresh` job, รัน Sunday 06:00 Asia/Bangkok (ก่อน weekly scan 09:00) refresh cache ทุก stock ใน universe 933 ตัว
- Rate limit: sequential per stock + 1.5s delay (เลี่ยง SET block), full universe ~30-40 นาที first run, subsequent runs ใช้ cache
- Verify ground truth: HTC FY 2022/2023/2024/2025 = 1.52/1.52/1.05/0.99 (จาก SETSMART screenshot), BBL/ILM/KBANK/PTT/AMATA = ดึงจาก setsmart.com manual + เก็บใน verify script
- Tolerance: ±5% per FY DPS sum — ถ้าเกิน = FAIL acceptance
- Playwright Chromium headless อยู่แล้วใน MaxMahon (verified `from playwright.sync_api import sync_playwright` works) — ต้องเพิ่ม `playwright>=1.40` ใน requirements.txt

### Scope Boundary
**In scope:**
- projects/4-MaxMahon/scripts/set_official_adapter.py (new module)
- projects/4-MaxMahon/data/set_dividend_cache/ (new cache dir, add to .gitignore)
- projects/4-MaxMahon/scripts/data_adapter.py (integration patch line ~791-792)
- projects/4-MaxMahon/scripts/_verify_dps_set_fix.py (verify script)
- projects/4-MaxMahon/CLAUDE.md (update Data Sources section: + Layer 0.5 set.or.th dividend)
- projects/4-MaxMahon/requirements.txt (add playwright>=1.40)
- projects/4-MaxMahon/server/app.py (extend apply_schedule with weekly_dividend_refresh job)

**Out of scope:**
- UI changes (no admin trigger button)
- Re-scan ทั้ง universe immediately (รันหลัง deploy เป็นรอบแรก)
- Update Max algo scoring (separate cycle)
- Scrape corporate action อื่น (XM/XR/XS) — เฉพาะ XD Cash Dividend
- Retroactive update screener_*.json เก่า

### Non-goals
- ไม่ทำ general SET data adapter (ใช้กับ dividend อย่างเดียว - กัน scope creep)
- ไม่ port เป็น public Python package (Max-specific only)
- ไม่ implement setsmart.com session login (อาร์ทเลือก set.or.th แล้ว)
- ไม่ใช้ adjusted DPS - ดึงตัวเลข raw ตาม operation period ที่ SET เผยแพร่
- ไม่ทำ UI สำหรับ visualize dividend history per stock

# set.or.th Dividend Scraper - Replace Yahoo DPS Source

> แก้ปัญหา Yahoo split-adjustment artifact (HTC DPS pre-2024 ผิด 50%) ทำให้ Niwes 'ปันผลเพิ่มทุกปี' check ใน manual ranking 2026-05-19 ผิด - ดึง DPS จาก set.or.th public JSON API (มี operation period ตรงๆ) แทน yahoo + Playwright bootstrap Cloudflare cookies + cache local + weekly refresh.

## Phase 1: Adapter Module + Cache Layer
- [x] สร้าง `projects/4-MaxMahon/scripts/set_official_adapter.py` — module ใหม่ มี 3 public functions: `fetch_dividends(symbol)` (Playwright bootstrap + API call) / `cached_dividends(symbol, max_age_days=7)` (cache + fetch) / `dps_by_fiscal_year(symbol)` (return {year: total_dps} จาก endOperation.year). Scope: ห้าม touch data_adapter.py ใน phase นี้. Acceptance: รัน `py scripts/set_official_adapter.py` smoke test → fetch HTC → print 9+ events รวม dividend 0.54/0.45/0.57/0.48/0.56/0.96/0.97/0.55/0.96 ตรง SETSMART screenshot.
- [x] เพิ่ม module-level constants ใน `set_official_adapter.py`: `BASE_URL = 'https://www.set.or.th/api/set/stock'` / `CACHE_DIR = Path('data/set_dividend_cache')` / `CACHE_TTL_DAYS = 7` / `REQUEST_DELAY_SEC = 1.5`. Scope: ห้าม hardcode path เป็น absolute. Acceptance: `CACHE_DIR.mkdir(parents=True, exist_ok=True)` work ตอน module import.
- [x] Implement `_get_browser_context()` ใน `set_official_adapter.py`: lazy-init Playwright Chromium headless + new_context + visit `https://www.set.or.th/en/market` รอ Cloudflare cookies (wait_until='domcontentloaded' + sleep 2s). Return APIRequestContext. Scope: 1 browser instance reuse ทั้ง session, ไม่ปิดระหว่าง batch. Acceptance: เรียก 2 ครั้งต่อกัน → ใช้ browser เดิม (`_browser is not None` check).
- [x] Implement `fetch_dividends(symbol: str) -> list[dict]` ใน `set_official_adapter.py`: ใช้ APIRequestContext จาก `_get_browser_context()` ยิง `{BASE_URL}/{symbol}/corporate-action?lang=en` + Referer header. Filter caType=='XD' + dividendType=='Cash Dividend'. Return list ของ event dicts: `{xdate, payment_date, begin_operation, end_operation, dps, dividend_type, source_of_dividend}` (date เป็น YYYY-MM-DD string, dps เป็น float). Scope: skip events ที่ endOperation == null. Acceptance: `fetch_dividends('HTC')` return >= 9 events, ตัวล่าสุด dps=0.54 end_operation='2025-12-31'.
- [x] Implement `cached_dividends(symbol, max_age_days=7)` ใน `set_official_adapter.py`: อ่าน cache file ที่ `CACHE_DIR/{SYMBOL}.json` ถ้ามี + อายุ < max_age_days → return cached events. ไม่งั้น call `fetch_dividends()` + write cache (atomic write: temp file + os.replace). Return `events` list. Scope: cache invalid (corrupt JSON / missing keys) → re-fetch. Acceptance: เรียก 2 ครั้งติด → call 2 hit cache (ไม่ Playwright launch).
- [x] Implement `dps_by_fiscal_year(symbol) -> dict[int, float]` ใน `set_official_adapter.py`: เรียก `cached_dividends()` + group by `int(end_operation[:4])` (= FY year) + sum dps + round 4. Return `{2022: 1.52, 2023: 1.52, 2024: 1.05, 2025: 0.99, ...}`. Scope: skip events ที่ end_operation parse ไม่ได้. Acceptance: `dps_by_fiscal_year('HTC')` มี key 2022/2023/2024/2025 value ตรง SETSMART ภายใน ±0.01.

### Reference
```python
# Pattern for Playwright browser singleton + API call (set_official_adapter.py)
import json
from pathlib import Path
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright, Browser, BrowserContext

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / 'data' / 'set_dividend_cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)
BASE_URL = 'https://www.set.or.th/api/set/stock'
CACHE_TTL_DAYS = 7
REQUEST_DELAY_SEC = 1.5

_playwright = None
_browser = None
_context = None

def _get_browser_context() -> BrowserContext:
    global _playwright, _browser, _context
    if _context is not None:
        return _context
    _playwright = sync_playwright().start()
    _browser = _playwright.chromium.launch(headless=True)
    _context = _browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    )
    page = _context.new_page()
    page.goto('https://www.set.or.th/en/market', wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(2000)
    page.close()
    return _context

def fetch_dividends(symbol: str) -> list[dict]:
    ctx = _get_browser_context()
    url = f'{BASE_URL}/{symbol}/corporate-action?lang=en'
    resp = ctx.request.get(url, headers={
        'Referer': f'https://www.set.or.th/en/market/product/stock/quote/{symbol}/rights-benefits',
        'Accept': 'application/json',
    })
    if resp.status != 200:
        raise RuntimeError(f'set.or.th API returned {resp.status} for {symbol}')
    data = json.loads(resp.body().decode('utf-8'))
    events = []
    for ev in data:
        if ev.get('caType') != 'XD':
            continue
        if ev.get('dividendType') != 'Cash Dividend':
            continue
        end_op = ev.get('endOperation')
        if not end_op:
            continue
        events.append({
            'xdate': (ev.get('xdate') or '')[:10],
            'payment_date': (ev.get('paymentDate') or '')[:10],
            'begin_operation': (ev.get('beginOperation') or '')[:10],
            'end_operation': end_op[:10],
            'dps': float(ev.get('dividend') or 0),
            'dividend_type': ev.get('dividendType'),
            'source_of_dividend': ev.get('sourceOfDividend'),
        })
    return events
```

## Phase 2: Integration into data_adapter.py
- [x] แก้ `projects/4-MaxMahon/scripts/data_adapter.py` import section (บนสุดของไฟล์) — เพิ่ม `from set_official_adapter import dps_by_fiscal_year as _set_dps_by_fy, cached_dividends as _set_cached_divs` พร้อม try/except ImportError fallback (กรณี Playwright ติดตั้งไม่ครบ → log warning + ไม่ raise). Scope: ห้ามแก้ existing imports. Acceptance: รัน `py -c 'from scripts.data_adapter import fetch_fundamentals'` ไม่ error.
- [x] แก้ `projects/4-MaxMahon/scripts/data_adapter.py` บรรทัด 791-792 — เปลี่ยน priority chain: ลอง `_set_dps_by_fy(symbol)` ก่อน, ถ้า return empty dict หรือ raise → fallback `yf_dps_by_fy` (yahoo). Add `dividend_source` field เก็บ 'set_official' หรือ 'yahoo' ลง returned dict ของ `fetch_fundamentals()`. Scope: ห้ามแก้ logic ใต้บรรทัด 792 ที่ patch capex/operating_income. Acceptance: รัน `fetch_fundamentals('HTC.BK')` → return dict มี `dividend_history` = {2022:1.52, 2023:1.52, 2024:1.05, ...} + `dividend_source='set_official'`.
- [x] เพิ่ม warning tag `DPS_SOURCE_YAHOO` ใน `data_adapter.py` หลัง integration patch (ใน fallback branch): ถ้า fallback ไป yahoo → append 'DPS_SOURCE_YAHOO' ลง `warnings` list ของ returned dict. Scope: ห้ามแก้ existing warning logic. Acceptance: simulate set.or.th fail (mock raise) → `warnings` รวม 'DPS_SOURCE_YAHOO'.
- [x] อัพเดท `.gitignore` ของ MaxMahon repo (หรือ root) — เพิ่ม `projects/4-MaxMahon/data/set_dividend_cache/`. Scope: ห้าม remove existing entries. Acceptance: `git status` ไม่ขึ้นไฟล์ใน cache dir.

### Reference
```python
# current (data_adapter.py:791-792)
# Build dividend_history from Yahoo DPS attributed to fiscal year (SET DIY methodology)
dividend_history = {y: round(dps, 4) for y, dps in yf_dps_by_fy.items()}

# new
# Build dividend_history — set.or.th primary, yahoo fallback
sym_clean = symbol.replace('.BK', '').upper()
dividend_source = 'unknown'
warnings = c.get('warnings', []) if 'warnings' in dir(c) else []
try:
    set_fy_dps = _set_dps_by_fy(sym_clean)
    if set_fy_dps:
        dividend_history = {y: round(dps, 4) for y, dps in set_fy_dps.items()}
        dividend_source = 'set_official'
    else:
        raise ValueError('set.or.th returned empty')
except Exception as e:
    logger.warning(f'set.or.th DPS fetch failed for {symbol}: {e}; falling back to yahoo')
    dividend_history = {y: round(dps, 4) for y, dps in yf_dps_by_fy.items()}
    dividend_source = 'yahoo'
    warnings.append('DPS_SOURCE_YAHOO')
```

## Phase 3: Verify Script + Ground Truth Test
- [x] สร้าง `projects/4-MaxMahon/scripts/_verify_dps_set_fix.py` — verify script ที่ fetch HTC + BBL + ILM + KBANK + PTT + AMATA ผ่าน `set_official_adapter.dps_by_fiscal_year()` + เทียบกับ ground truth dict (hardcoded ใน script). Output report ไฟล์ `docs/dps-set-fix-verification-{YYYY-MM-DD}.md`. Scope: ห้าม run yahoo (test เฉพาะ set.or.th path). Acceptance: รัน `py scripts/_verify_dps_set_fix.py` → output report + summary 'PASS X/6' / 'FAIL X/6' โดย HTC FY2022/23/24/25 ต้อง match ภายใน ±5%.
- [x] เพิ่ม `GROUND_TRUTH` dict ใน `_verify_dps_set_fix.py` — HTC = {2022:1.52, 2023:1.52, 2024:1.05, 2025:0.99} (จาก SETSMART screenshot). BBL/ILM/KBANK/PTT/AMATA: pull ผ่าน adapter ครั้งแรก + ให้ user manual verify ก่อน hardcode (init เป็น dict ว่าง, ใส่ comment 'pending manual verify'). Scope: ห้ามใส่ค่าที่ไม่ verify จาก setsmart.com manual. Acceptance: HTC PASS 4/4 FY (within ±5%), อีก 5 ตัวแสดง 'pending manual ground truth - data fetched OK'.

### Reference
```python
# Pattern for verify script (_verify_dps_set_fix.py)
import sys
from pathlib import Path
from datetime import datetime
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from set_official_adapter import dps_by_fiscal_year

GROUND_TRUTH = {
    'HTC': {2022: 1.52, 2023: 1.52, 2024: 1.05, 2025: 0.99},
    'BBL': {},  # pending manual verify from setsmart.com
    'ILM': {},
    'KBANK': {},
    'PTT': {},
    'AMATA': {},
}
TOLERANCE_PCT = 5.0

def verify_symbol(sym, truth):
    fetched = dps_by_fiscal_year(sym)
    results = []
    for fy, expected in truth.items():
        actual = fetched.get(fy)
        if actual is None:
            results.append((fy, expected, None, 'MISSING'))
            continue
        diff_pct = abs(actual - expected) / expected * 100
        status = 'PASS' if diff_pct <= TOLERANCE_PCT else 'FAIL'
        results.append((fy, expected, actual, status))
    return fetched, results
```

## Phase 4: Weekly Cron + Docs Update
- [x] เพิ่ม `scheduled_dividend_refresh_job()` function ใน `projects/4-MaxMahon/server/app.py` — load universe จาก `data/set_universe.json` + loop call `set_official_adapter.cached_dividends(sym)` ทุก stock + log progress + sleep 1.5s/stock. Scope: ห้ามแก้ existing scheduled functions. Acceptance: เรียก function ตรงๆ → log แสดง '[scheduler] dividend refresh started for N stocks' + '[scheduler] dividend refresh done'.
- [x] Extend `apply_schedule()` ใน `projects/4-MaxMahon/server/app.py` — เพิ่ม `weekly_dividend_refresh` job: cron Sunday 06:00 Asia/Bangkok (3 ชม. ก่อน weekly scan 09:00). Scope: ห้ามแก้ existing max_pipeline / daily_price_refresh jobs. Acceptance: server start → log แสดง '[scheduler] weekly_dividend_refresh scheduled: sun 06:00 Asia/Bangkok'.
- [x] เพิ่ม `playwright>=1.40` ใน `projects/4-MaxMahon/requirements.txt`. Scope: ห้าม touch existing deps. Acceptance: `py -m pip install -r requirements.txt` ทำงานปกติ + `from playwright.sync_api import sync_playwright` import ได้.
- [x] อัพเดท `projects/4-MaxMahon/CLAUDE.md` Data Sources section — เพิ่ม `Layer 0.5 set.or.th dividend` ระหว่าง Layer 0 (SETSMART) กับ Layer 1 (thaifin). Note: 'set.or.th public JSON API + Playwright Cloudflare bootstrap, cache 7 วัน, DPS event-by-event ตามจริง ไม่ split-adjust'. Scope: ห้ามแก้ section อื่น. Acceptance: grep 'Layer 0.5 set.or.th' พบใน CLAUDE.md.

### Reference
```python
# current (server/app.py apply_schedule, ~บรรทัด 1094-1131)
def apply_schedule(config: dict):
    sched = config.get('schedule', DEFAULT_CONFIG['schedule'])
    try:
        scheduler.remove_job('max_pipeline')
    except Exception:
        pass
    if sched.get('enabled', True):
        scheduler.add_job(scheduled_run, 'cron', id='max_pipeline', ...)
    # Daily price refresh - 19:00 Asia/Bangkok
    try:
        scheduler.remove_job('daily_price_refresh')
    except Exception:
        pass
    scheduler.add_job(scheduled_price_refresh_job, 'cron', id='daily_price_refresh', hour=19, minute=0, timezone='Asia/Bangkok')

# new — add weekly_dividend_refresh job
def apply_schedule(config: dict):
    # ... existing max_pipeline + daily_price_refresh code unchanged ...
    # Weekly dividend refresh - Sunday 06:00 Asia/Bangkok (3hr before weekly scan)
    try:
        scheduler.remove_job('weekly_dividend_refresh')
    except Exception:
        pass
    scheduler.add_job(
        scheduled_dividend_refresh_job,
        'cron',
        id='weekly_dividend_refresh',
        day_of_week='sun',
        hour=6,
        minute=0,
        timezone='Asia/Bangkok',
    )
    logging.info('[scheduler] weekly_dividend_refresh scheduled: sun 06:00 Asia/Bangkok')
```
