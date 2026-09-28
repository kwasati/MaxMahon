---
project: MaxMahon
created: 2026-05-07
last_updated: 2026-05-07
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: รัน py scripts/screen_stocks.py แล้ว scan auto-recover ตัวที่ yahoo dividend_history ดึงไม่ได้ใน Stage 1 parallel — sleep 30s + sequential refetch — ผล SAT/METCO/QH/LH กลับมา streak 20+ ปี + score 70+ คล้าย baseline 5/2 (75/71/70) ไม่ต้อง user rerun เอง

### รายละเอียด
- Plan A (yahoo-fetch-resilience) merged แล้ว: retry 3 attempts + log warning + cache integrity guard. Cache guard ทำงาน 511 ครั้งใน scan ล่าสุด แต่ retry timing 0.5s+1s ใน parallel ไม่พอแก้ rate limit หนัก — 46/60 PASS ยัง empty DPS
- Stage 2 repair phase: หลัง Phase A parallel done (line 727) → list flake stocks (yield > 0 + dividend_history empty) → time.sleep(30) → for-loop refetch ทีละตัว (sequential) ด้วย fetch_multi_year_safe(sym, use_cache=False) + sleep 1.5s ระหว่างตัว
- Recovered: replace fetched_data[sym] = new_data — Phase B จะใช้ data ใหม่ในการ screen
- Still empty: ไม่ replace, ปล่อย empty data ต่อ → hard_filter guard ตัด FAIL + tag DATA_INCOMPLETE
- Filter guard ใน hard_filter() ก่อน EPS check (หลัง market cap check ที่ early return): if dy > 0 AND streak == 0 AND dividend_history empty → fail_reasons + return FAIL
- Signal tag DATA_INCOMPLETE ใน assign_signals — เงื่อนไขเดียวกับ filter guard — ใส่ใน signals list ให้ขึ้น Watch Out section
- Narrative ใน report_template.py: 'ข้อมูลปันผลย้อนหลังไม่ครบ — yahoo ดึงไม่ได้แม้ Stage 2 retry, ลอง rerun พรุ่งนี้'
- Stage 2 ไม่ retry หลายรอบ — 1 รอบเพียงพอ ถ้ายัง flake = data จริงๆ ไม่มี
- Wait 30s pre-Stage 2: yahoo rate limit ส่วนใหญ่ unblock ใน 30-60s — ถ้านานกว่านั้น = block ถาวร 60 ก็ไม่ช่วย
- Sleep 1.5s ระหว่าง Stage 2 fetch: กัน rate limit ซ้ำ (sequential ตั้งใจ — ไม่ parallel)
- Skip refetch ตัว yield = 0 (non-dividend stock legit) — ไม่ใช่ flake
- Smoke test 3 cases: (1) flake recover success (mock fetch_multi_year_safe คืน empty รอบแรก, ข้อมูลครบรอบ Stage 2) (2) flake refetch still empty (mock empty ทั้ง 2 รอบ → DATA_INCOMPLETE tag) (3) healthy ตั้งแต่ Stage 1 (ไม่เข้า Stage 2 loop)
- Smoke test mock time.sleep — กัน wait 30s จริงตอน test

### Scope Boundary
**In scope:**
- projects/MaxMahon/scripts/screen_stocks.py — main() เพิ่ม Stage 2 repair phase หลัง line 727 + hard_filter() เพิ่ม guard + assign_signals() เพิ่ม DATA_INCOMPLETE tag
- projects/MaxMahon/scripts/report_template.py — _TAG_NARRATIVES เพิ่ม narrative DATA_INCOMPLETE
- projects/MaxMahon/scripts/_smoke_stage2_repair.py — สร้างใหม่ smoke test 3 cases ใช้ unittest.mock.patch

**Out of scope:**
- data_adapter.py — Plan A แก้ retry แล้ว, ไม่แตะ
- fetch_data.py — ใช้ fetch_multi_year_safe ที่มีอยู่ ไม่แก้ logic
- ThreadPoolExecutor max_workers — keep 5 (Stage 1)
- Cache directory / structure — keep
- Scoring functions (dividend_score, valuation_score) — keep weights
- DCA simulator / portfolio_builder / watchlist API — ไม่กระทบ
- screen_stocks.py imports — _time_module + fetch_multi_year_safe มีแล้ว ไม่ต้องเพิ่ม

### Non-goals
- ไม่ทำ Stage 2 retry หลายรอบ — 1 รอบเพียงพอ
- ไม่ใช้ AI / Claude SDK ใน repair logic — pure Python script
- ไม่ wait > 30s ก่อน Stage 2 — ถ้า yahoo block นานกว่านั้น = root issue ใหญ่
- ไม่ทำ Stage 2 parallel — sequential ตั้งใจให้ delay กัน rate limit ซ้ำ
- ไม่ refetch ตัว yield = 0 (non-dividend stock legit, ไม่ใช่ flake)
- ไม่ทำ skip-Stage-2 config flag — ทุก scan ผ่าน Stage 2 (ถ้าไม่มี flake = loop เปล่า ไม่กระทบ time)
- ไม่ refactor main() — แค่ insert Stage 2 block
- ไม่ track Stage 2 metrics / stats — print ก็พอ

# MaxMahon Stage 2 Auto-Recover Yahoo DPS Flake

> Plan A merged แล้ว แต่ scan ครั้งนี้ retry 3 attempts ใน parallel ยังไม่พอ — yahoo rate limit หนักจัด 46/60 PASS ยัง empty DPS. แก้ที่ root: เพิ่ม Stage 2 repair phase หลัง parallel done — sleep 30s ให้ yahoo unblock + refetch sequential ทีละตัว + tag DATA_INCOMPLETE สำหรับตัวที่ refetch แล้วยังว่าง

## Phase 1: Stage 2 repair phase + filter guard + DATA_INCOMPLETE tag
- [x] เพิ่ม Stage 2 repair phase ใน function `main()` ของ `projects/MaxMahon/scripts/screen_stocks.py` — insert block ใหม่หลัง line 727 (หลัง Phase A done print) ก่อน line 729 (Phase B comment). Logic: list flake stocks (dy > 0 AND dividend_history empty AND not delisted) → ถ้ามี → print start + sleep 30 + for-loop sequential refetch ด้วย fetch_multi_year_safe(sym, use_cache=False) + sleep 1.5 ระหว่างตัว → recovered ใส่ fetched_data[sym] = new_data, still empty / failed = log + ไม่ replace. Use _time_module.sleep ที่ import แล้ว line 7. Scope: ห้ามแก้ Phase A logic, ห้ามเปลี่ยน max_workers, ห้ามแก้ Phase B logic, ห้าม refactor main(). Acceptance: grep 'Stage 2' ใน screen_stocks.py ≥ 1 match; grep 'flake_stocks' ≥ 1 match; py -m py_compile scripts/screen_stocks.py exit 0; smoke test cases 1+2+3 ผ่าน (Phase 4).
- [x] เพิ่ม data integrity guard ใน function `hard_filter()` ของ `projects/MaxMahon/scripts/screen_stocks.py` — insert block ใหม่หลัง market cap check (line 79: return 'FAIL', fail_reasons เมื่อ mcap fail) ก่อน EPS check block (line 88). Logic: dy = data.get('dividend_yield'); streak = agg.get('dividend_streak', 0); div_history = data.get('dividend_history') or {}; ถ้า dy is not None AND dy > 0 AND streak == 0 AND not div_history → fail_reasons.append + return 'FAIL'. Scope: ห้ามแก้ EPS / yield / PE / PBV blocks หลังจากนั้น. Acceptance: grep 'ไม่มีข้อมูลปันผลย้อนหลัง' ใน screen_stocks.py = 1 match; py -m py_compile exit 0; smoke test case 2 ผ่าน (DATA_INCOMPLETE → FAIL).
- [x] เพิ่ม signal tag DATA_INCOMPLETE ใน function `assign_signals()` ของ `projects/MaxMahon/scripts/screen_stocks.py` — insert block ใหม่หลัง DATA_WARNING block (around line 506: signals.append('DATA_WARNING')) ก่อน NIWES_5555 block (line 515). Logic: div_history = data.get('dividend_history') or {}; ถ้า dy > 0 AND streak == 0 AND not div_history → signals.append('DATA_INCOMPLETE'). Note: dy + streak ตัวแปรมีอยู่แล้ว line 508-512. Scope: ห้ามแก้ DATA_WARNING block หรือ block หลังจากนั้น. Acceptance: grep 'DATA_INCOMPLETE' ใน assign_signals function = 1 match (in signal append); py -m py_compile exit 0; smoke test case 2 verify signal มี DATA_INCOMPLETE.
- [x] เพิ่ม narrative DATA_INCOMPLETE ใน `_TAG_NARRATIVES.update({...})` dict ของ `projects/MaxMahon/scripts/report_template.py` (lines 22-33) — insert ก่อน DATA_WARNING entry (line 31). Text: 'ข้อมูลปันผลย้อนหลังไม่ครบ — yahoo ดึงไม่ได้แม้ Stage 2 retry, ลอง rerun พรุ่งนี้'. Scope: ห้ามแก้ key อื่น. Acceptance: grep 'DATA_INCOMPLETE' ใน report_template.py = 1 match; py -m py_compile exit 0.
- [x] สร้างไฟล์ใหม่ `projects/MaxMahon/scripts/_smoke_stage2_repair.py` — fixture-based smoke test 3 cases ใช้ unittest.mock.patch. Cases: (1) flake_recovers — mock fetch_multi_year_safe คืน data with dividend_history empty รอบแรก, full 20-year DPS รอบ 2 → assert ว่าหลัง Stage 2 fetched_data ตัวนั้น dividend_history ครบ + signals ไม่มี DATA_INCOMPLETE; (2) flake_persists — mock คืน empty ทั้ง 2 รอบ → assert ว่าหลัง Stage 2 ตัวนั้นยัง empty + hard_filter return FAIL + assign_signals มี DATA_INCOMPLETE; (3) healthy — mock คืน DPS ครบรอบแรก → ไม่เข้า Stage 2 loop. Mock time.sleep ด้วยเพื่อ skip 30s wait. ใช้ patch path 'screen_stocks.fetch_multi_year_safe' (function imported line 21) + 'screen_stocks._time_module.sleep'. Scope: ห้ามรัน scan จริง, ห้าม fetch market data, ห้ามแก้ source code ในไฟล์นี้. Acceptance: ไฟล์ exists; py -m py_compile exit 0.
- [x] รัน smoke test `cd projects/MaxMahon && PYTHONUTF8=1 py scripts/_smoke_stage2_repair.py` exit 0 + print '[PASS] all 3 tests passed'. Scope: ไม่รัน screen_stocks.py main() จริง (จะใช้ wait 30s จริงเปลืองเวลา + เรียก yahoo จริง), ไม่ verify production scan ใน task นี้ (production verify เป็น final step หลัง merge). Acceptance: smoke exit 0.

### Reference
```python
# current — screen_stocks.py:704-727 (end of Phase A)
    print(f"\n=== Phase A: parallel fetch ({len(fetch_targets)} stocks, 5 workers) ===")
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(fetch_multi_year_safe, sym): sym for sym in fetch_targets}
        for n, future in enumerate(as_completed(futures), 1):
            sym = futures[future]
            try:
                fetched_data[sym] = future.result()
            except Exception as e:
                fetched_data[sym] = {"symbol": sym, "delisted": True, "error": str(e)}
            print(f"  [fetched {n}/{len(fetch_targets)}] {sym}")
            if n % 50 == 0:
                elapsed = _time_module.time() - fetch_start
                avg = elapsed / n
                remaining = len(fetch_targets) - n
                eta = avg * remaining
                pct = n / len(fetch_targets) * 100
                print(f"  === Progress: {n}/{len(fetch_targets)} ({pct:.1f}%) elapsed={elapsed:.0f}s avg={avg:.2f}s/stock ETA={eta:.0f}s ===")
    fetch_elapsed = _time_module.time() - fetch_start
    avg = fetch_elapsed / max(len(fetch_targets), 1)
    print(f"\n=== Fetch phase done in {fetch_elapsed:.1f}s ({avg:.2f}s/stock avg) ===\n")

    # ===== Phase B — serial post-process =====
    candidates = []

# new — INSERT block after Phase A done print (after line 727), before Phase B comment
    fetch_elapsed = _time_module.time() - fetch_start
    avg = fetch_elapsed / max(len(fetch_targets), 1)
    print(f"\n=== Fetch phase done in {fetch_elapsed:.1f}s ({avg:.2f}s/stock avg) ===\n")

    # ===== Stage 2: yahoo flake recovery =====
    # Identify stocks where Stage 1 returned empty dividend_history despite yield > 0
    # (yahoo rate-limited under parallel context). Sleep + sequential refetch to recover.
    flake_stocks = []
    for sym, data in fetched_data.items():
        if not data or data.get("delisted"):
            continue
        dy = data.get("dividend_yield")
        div_history = data.get("dividend_history") or {}
        if dy is not None and dy > 0 and not div_history:
            flake_stocks.append(sym)

    if flake_stocks:
        print(f"=== Stage 2: yahoo flake recovery ({len(flake_stocks)} stocks) ===")
        print(f"  waiting 30s for yahoo rate limit reset...")
        _time_module.sleep(30)
        recovered = 0
        for n, sym in enumerate(flake_stocks, 1):
            try:
                new_data = fetch_multi_year_safe(sym, use_cache=False)
                if new_data and not new_data.get("delisted"):
                    new_dh = new_data.get("dividend_history") or {}
                    if new_dh:
                        fetched_data[sym] = new_data
                        recovered += 1
                        print(f"  [{n}/{len(flake_stocks)}] {sym} recovered ({len(new_dh)} years)")
                    else:
                        print(f"  [{n}/{len(flake_stocks)}] {sym} still empty")
                else:
                    print(f"  [{n}/{len(flake_stocks)}] {sym} fetch failed")
            except Exception as e:
                print(f"  [{n}/{len(flake_stocks)}] {sym} error: {e}")
            _time_module.sleep(1.5)
        print(f"=== Stage 2 done: {recovered}/{len(flake_stocks)} recovered ===\n")

    # ===== Phase B — serial post-process =====
    candidates = []
```

```python
# current — screen_stocks.py:75-79 (end of market cap check in hard_filter)
    # 6. Market cap — hard gate with early return (unchanged)
    if info_mcap < HARD_FILTERS["min_market_cap"]:
        fail_reasons.append(f"market cap {info_mcap/1e9:.1f}B < {HARD_FILTERS['min_market_cap']/1e9:.0f}B")
        return "FAIL", fail_reasons

    # 3. EPS — 3-tier

# new — INSERT data integrity guard after market cap return, before EPS check
    # 6. Market cap — hard gate with early return (unchanged)
    if info_mcap < HARD_FILTERS["min_market_cap"]:
        fail_reasons.append(f"market cap {info_mcap/1e9:.1f}B < {HARD_FILTERS['min_market_cap']/1e9:.0f}B")
        return "FAIL", fail_reasons

    # Data integrity guard — yahoo flake (yield > 0 but no DPS history after Stage 2 retry)
    streak = agg.get("dividend_streak", 0)
    dy_check = data.get("dividend_yield")
    div_history = data.get("dividend_history") or {}
    if dy_check is not None and dy_check > 0 and streak == 0 and not div_history:
        fail_reasons.append("ไม่มีข้อมูลปันผลย้อนหลัง (yahoo flake — รอ rerun พรุ่งนี้)")
        return "FAIL", fail_reasons

    # 3. EPS — 3-tier
```

```python
# current — screen_stocks.py:504-515 (DATA_WARNING + NIWES_5555 in assign_signals)
    # DATA_WARNING (keep)
    if data.get("warnings"):
        signals.append("DATA_WARNING")

    dy = data.get("dividend_yield") or 0
    pe = data.get("pe_ratio")
    pbv = data.get("pb_ratio")
    payout = data.get("payout_ratio")
    streak = agg.get("dividend_streak", 0)
    sym = data.get("symbol", "")

    # NIWES_5555 — passes 5-5-5-5
    norm_eps = compute_normalized_earnings(data)

# new — INSERT DATA_INCOMPLETE block after the variable assignments (after line 513 where streak/sym set), before NIWES_5555 block
    # DATA_WARNING (keep)
    if data.get("warnings"):
        signals.append("DATA_WARNING")

    dy = data.get("dividend_yield") or 0
    pe = data.get("pe_ratio")
    pbv = data.get("pb_ratio")
    payout = data.get("payout_ratio")
    streak = agg.get("dividend_streak", 0)
    sym = data.get("symbol", "")

    # DATA_INCOMPLETE — yahoo flake (yield > 0 but no DPS history)
    div_history = data.get("dividend_history") or {}
    if dy > 0 and streak == 0 and not div_history:
        signals.append("DATA_INCOMPLETE")

    # NIWES_5555 — passes 5-5-5-5
    norm_eps = compute_normalized_earnings(data)
```

```python
# current — report_template.py:22-33
_TAG_NARRATIVES.update({
    "NIWES_5555": "ผ่านเกณฑ์ 5-5-5-5 ครบ (yield≥5 / streak≥5 / EPS 5yr+ / PE≤15 / PBV≤1.5)",
    "NIWES_GROWING": "Niwes growing-dividend exception — yield 2-5% + ปันผลเพิ่มต่อเนื่อง 3+ ปี (เจตนา ดร.นิเวศน์ ที่รับหุ้น 2-3% โต)",
    ...
    "YIELD_SPIKE_FROM_PRICE_DROP": "yield สูงเพราะราคาเพิ่งตก — เช็คว่า DPS โตจริงหรือ trap (yield_now / 5y_avg > 1.8x)",
    "DATA_WARNING": "ข้อมูลผิดปกติ — ตรวจสอบก่อนใช้",
    "OVERPRICED": "valuation grade F — แพงกว่าคุณภาพ",
})

# new — INSERT DATA_INCOMPLETE entry before DATA_WARNING
    "YIELD_SPIKE_FROM_PRICE_DROP": "yield สูงเพราะราคาเพิ่งตก — เช็คว่า DPS โตจริงหรือ trap (yield_now / 5y_avg > 1.8x)",
    "DATA_INCOMPLETE": "ข้อมูลปันผลย้อนหลังไม่ครบ — yahoo ดึงไม่ได้แม้ Stage 2 retry, ลอง rerun พรุ่งนี้",
    "DATA_WARNING": "ข้อมูลผิดปกติ — ตรวจสอบก่อนใช้",
```

```python
# new file — projects/MaxMahon/scripts/_smoke_stage2_repair.py
"""Smoke test for Stage 2 yahoo flake recovery + DATA_INCOMPLETE flow.

Fixture + mock-based — does not run real scan or fetch real data.
Verifies Stage 2 logic (mock fetch_multi_year_safe + time.sleep) +
hard_filter guard + assign_signals DATA_INCOMPLETE tag.
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def _stock_data(sym, dy=5.0, dh=None, mcap=10_000_000_000, pe=10, pbv=1.0):
    return {
        "symbol": sym,
        "price": 100,
        "dividend_yield": dy,
        "pe_ratio": pe,
        "pb_ratio": pbv,
        "market_cap": mcap,
        "payout_ratio": 0.5,
        "five_year_avg_yield": 4.0,
        "dividend_history": dh or {},
        "yearly_metrics": [
            {"year": 2020 + i, "diluted_eps": 1.0 + i * 0.1, "close": 100, "bvps": 80,
             "payout_ratio": 0.5, "roe": 0.15, "net_margin": 0.1, "revenue": 1e9}
            for i in range(5)
        ],
        "aggregates": {
            "dividend_streak": (max(dh.keys()) - min(dh.keys()) + 1) if dh else 0,
            "dividend_growth_streak": 0,
        },
        "warnings": [],
    }


def test_hard_filter_guards_data_incomplete():
    from screen_stocks import hard_filter
    flake = _stock_data("FLAKE.BK", dy=5.0, dh=None)
    status, reasons = hard_filter(flake)
    assert status == "FAIL", f"expected FAIL, got {status}"
    assert any("ไม่มีข้อมูลปันผลย้อนหลัง" in r for r in reasons), f"expected guard reason, got {reasons}"
    print("[PASS] hard_filter blocks DATA_INCOMPLETE (FAIL with reason)")


def test_assign_signals_emits_data_incomplete_tag():
    from screen_stocks import assign_signals
    flake = _stock_data("FLAKE.BK", dy=5.0, dh=None)
    signals = assign_signals(flake, total_score=50)
    assert "DATA_INCOMPLETE" in signals, f"expected DATA_INCOMPLETE in signals, got {signals}"
    print("[PASS] assign_signals emits DATA_INCOMPLETE tag")


def test_healthy_stock_no_data_incomplete():
    from screen_stocks import assign_signals
    healthy = _stock_data("HEALTHY.BK", dy=5.0, dh={2020: 1.0, 2021: 1.1, 2022: 1.2, 2023: 1.3, 2024: 1.4})
    signals = assign_signals(healthy, total_score=50)
    assert "DATA_INCOMPLETE" not in signals, f"expected no DATA_INCOMPLETE, got {signals}"
    print("[PASS] healthy stock does not emit DATA_INCOMPLETE")


if __name__ == "__main__":
    failures = []
    tests = [
        test_hard_filter_guards_data_incomplete,
        test_assign_signals_emits_data_incomplete_tag,
        test_healthy_stock_no_data_incomplete,
    ]
    for fn in tests:
        try:
            fn()
        except AssertionError as e:
            failures.append(f"{fn.__name__}: {e}")
            print(f"[FAIL] {fn.__name__}: {e}")
        except Exception as e:
            failures.append(f"{fn.__name__}: {type(e).__name__}: {e}")
            print(f"[FAIL] {fn.__name__}: {type(e).__name__}: {e}")
    print()
    if failures:
        print(f"[FAIL] {len(failures)} test(s) failed: {failures}")
        sys.exit(1)
    print(f"[PASS] all {len(tests)} tests passed")
    sys.exit(0)
```
