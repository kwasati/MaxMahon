---
project: 4-MaxMahon
created: 2026-05-12
last_updated: 2026-05-18
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: รัน weekly scan ในปี 2026 แล้วทุกตัวนับ (streak ปันผล, streak ปันผลโต, EPS 5-year window, EPS+Revenue CAGR) ไม่นับปี 2026 ที่ยังไม่จบ + config.json override growing_yield_floor + growing_min_streak ได้ + hard_filter dividend logic อ่านง่ายขึ้น (streak ≥ 3 → ใช้เกณฑ์ 2% / else ใช้เกณฑ์ 5%)

### รายละเอียด
- fy_is_complete dict ถูก build ใน data_adapter.py _fetch_yahoo_supplement (line 513-541) แล้ว แต่ไม่ได้ forward ไปยัง streak functions
- count_dividend_streak (fetch_data.py:76-87) filter y < current_year แต่ไม่เช็ค fy_is_complete — bug: ปี 2025 ที่ยังไม่ครบงวดสุดท้ายจะถูกนับเป็น streak year ถ้ามี DPS > 0
- count_dividend_growth_streak (fetch_data.py:90-101) same bug — ถ้าปีปัจจุบันยังไม่จบ + DPS น้อยกว่าปีก่อนเต็มปี → ดู 'ตก' = streak พังทั้งเส้น
- EPS 5-year window (screen_stocks.py:93-94) sorted(norm_eps.keys())[-5:] — ถ้า thaifin emit partial 2026 row จะเข้า window
- compute_cagr ใน _build_aggregates (fetch_data.py:137-138) — ส่ง eps_list / revenues ครบทุกปีรวมปียังไม่จบ
- config.json filters: ขาด growing_yield_floor + growing_min_streak — DEFAULT_FILTERS ใน screen_stocks.py:31-42 only — tune ผ่าน UI ไม่ได้
- Dividend filter logic swap: เก่า = check yield≥5% ก่อน → exception (≥2% AND streak≥3) / ใหม่ = check streak≥3 ก่อน → ใช้เกณฑ์ 2% / else เกณฑ์ 5% — ผลลัพธ์เหมือนกันทุกเคส (verified ใน chat session)
- Year-completeness rule: ใช้ fy_is_complete dict สำหรับ DPS-based functions, ใช้ y < current_year สำหรับ EPS/revenue (thaifin ไม่มี is_complete equivalent)

### Scope Boundary
**In scope:**
- scripts/screen_stocks.py — hard_filter dividend logic + EPS window filter
- scripts/fetch_data.py — count_dividend_streak, count_dividend_growth_streak, _build_aggregates
- scripts/data_adapter.py — forward fy_is_complete จาก _fetch_yahoo_supplement → fetch_fundamentals → return dict
- config.json — เพิ่ม 2 keys (growing_yield_floor, growing_min_streak)

**Out of scope:**
- SETSMART migration (Plan B)
- DPS source change (Plan C)
- REVIEW handling (Plan D)
- Normalized EPS implement (Plan E)
- Streak threshold scoring changes (15/13/10/8/5/2) — แค่ fix bug ไม่เปลี่ยน threshold

### Non-goals
- ไม่ refactor streak functions architecture — แค่เพิ่ม fy_is_complete param
- ไม่ migrate config.json schema — แค่เพิ่ม 2 keys ใน filters block
- ไม่เปลี่ยนผลลัพธ์ dividend filter — swap order เพื่อ readability only
- ไม่ remove min_dividend_streak config key (เก่า ไม่ใช้แล้วแต่ keep backward compat)

# Plan A — Year-completeness + Config Externalization + Dividend Logic Swap

> Part 1 of 7 — Year-completeness foundation. ตัด 'ปียังไม่จบ' ออกจากทุกตัวนับ + externalize config + swap dividend logic order (อ่านง่ายขึ้น)
> Depends on: none (foundation)
> Parallel-safe with: filter-02-setsmart-migration (แตะคนละไฟล์เป็นส่วนใหญ่ — แต่ recommend sequential เพราะ Plan B จะ refactor fetch_fundamentals หนัก)

## Phase 1: Forward fy_is_complete ลงไปถึง streak functions
- [x] แก้ scripts/fetch_data.py function count_dividend_streak (บรรทัด 76-87) — เพิ่ม param fy_is_complete: dict | None = None และ filter year ที่ y in fy_is_complete + fy_is_complete[y] == True เท่านั้น — Scope: ไม่แก้ caller signature ใน Phase 1 (default None = backward compat), ใช้ year < current_year ถ้า fy_is_complete=None — Acceptance: count_dividend_streak({2024:5, 2025:3, 2026:1}, fy_is_complete={2024:True, 2025:True, 2026:False}) คืน 2 (ไม่นับ 2026), call เก่า count_dividend_streak({2024:5, 2025:3}) คืน 2 (เหมือนเดิม)
- [x] แก้ scripts/fetch_data.py function count_dividend_growth_streak (บรรทัด 90-101) — เพิ่ม param fy_is_complete: dict | None = None แบบเดียวกัน + filter year ก่อนนับ growth — Acceptance: count_dividend_growth_streak({2023:5, 2024:7, 2025:9, 2026:2}, fy_is_complete={2023:True, 2024:True, 2025:True, 2026:False}) คืน 2 (โต 2 ปีติด, ไม่นับ 2026 ที่ DPS น้อย), call เก่าไม่มี fy_is_complete คืน 0 (เพราะ 2026 มาแล้วทำให้พัง — confirm bug)
- [x] แก้ scripts/data_adapter.py function fetch_fundamentals (บรรทัด 676-904) — return dict เพิ่ม key 'fy_is_complete' (จาก yf_fy_complete ที่ build ใน _fetch_yahoo_supplement บรรทัด 513-541) — Scope: ไม่แก้ schema downstream consumers ใน Phase 1 — Acceptance: fetch_fundamentals('BBL') return dict มี key 'fy_is_complete' ที่ value = {year:bool} dict
- [x] แก้ scripts/fetch_data.py function _build_aggregates (บรรทัด 127-194) — รับ fy_is_complete จาก fundamentals dict + ส่งต่อไป count_dividend_streak (บรรทัด 152) + count_dividend_growth_streak (บรรทัด 153) — Acceptance: _build_aggregates(fundamentals) ใช้ fy_is_complete ที่ส่งมา + คืน dict มี dividend_streak + dividend_growth_streak ที่นับเฉพาะ FY ที่ complete

### Reference
```python
# current (scripts/fetch_data.py:76-87)
def count_dividend_streak(dps_by_year):
    if not dps_by_year:
        return 0
    current_year = datetime.now().year
    years = [y for y in sorted(dps_by_year.keys(), reverse=True) if y < current_year]
    streak = 0
    for y in years:
        if dps_by_year[y] > 0:
            streak += 1
        else:
            break
    return streak

# new
def count_dividend_streak(dps_by_year, fy_is_complete=None):
    """Streak นับเฉพาะ FY ที่ is_complete=True เท่านั้น.
    
    ถ้า fy_is_complete=None (backward compat) → filter y < current_year แบบเดิม.
    """
    if not dps_by_year:
        return 0
    if fy_is_complete is not None:
        years = [y for y in sorted(dps_by_year.keys(), reverse=True)
                 if fy_is_complete.get(y) is True]
    else:
        current_year = datetime.now().year
        years = [y for y in sorted(dps_by_year.keys(), reverse=True) if y < current_year]
    streak = 0
    for y in years:
        if dps_by_year[y] > 0:
            streak += 1
        else:
            break
    return streak

# current (scripts/fetch_data.py:90-101)
def count_dividend_growth_streak(dps_by_year):
    if not dps_by_year:
        return 0
    current_year = datetime.now().year
    years = [y for y in sorted(dps_by_year.keys(), reverse=True) if y < current_year]
    streak = 0
    for i in range(len(years) - 1):
        if dps_by_year[years[i]] > dps_by_year[years[i + 1]] and dps_by_year[years[i + 1]] > 0:
            streak += 1
        else:
            break
    return streak

# new
def count_dividend_growth_streak(dps_by_year, fy_is_complete=None):
    if not dps_by_year:
        return 0
    if fy_is_complete is not None:
        years = [y for y in sorted(dps_by_year.keys(), reverse=True)
                 if fy_is_complete.get(y) is True]
    else:
        current_year = datetime.now().year
        years = [y for y in sorted(dps_by_year.keys(), reverse=True) if y < current_year]
    streak = 0
    for i in range(len(years) - 1):
        if dps_by_year[years[i]] > dps_by_year[years[i + 1]] and dps_by_year[years[i + 1]] > 0:
            streak += 1
        else:
            break
    return streak
```

## Phase 2: EPS window + CAGR exclude current year
- [x] แก้ scripts/screen_stocks.py function hard_filter (บรรทัด 90-106) — EPS 5-year window: filter sorted_years exclude current calendar year ก่อน slice [-5:] — Acceptance: ถ้า norm_eps มีปี 2020-2026 → sorted_years = [2021,2022,2023,2024,2025] (5 ปี ไม่รวม 2026)
- [x] แก้ scripts/fetch_data.py function _build_aggregates (บรรทัด 137-138) — compute_cagr รับ eps_list และ revenues ที่ exclude current calendar year ก่อนคำนวณ — Acceptance: ถ้า yearly_metrics มีปี 2010-2026 → compute_cagr ใช้ values ถึงปี 2025 เท่านั้น

### Reference
```python
# current (scripts/screen_stocks.py:90-106)
norm_eps = compute_normalized_earnings(data)
if norm_eps:
    sorted_years = sorted(norm_eps.keys())[-5:]
    eps_recent = [norm_eps[y] for y in sorted_years]
    pos = sum(1 for e in eps_recent if e is not None and e > 0)
    total = len(eps_recent)
    if total < 5:
        fail_reasons.append(f"EPS history {total}yr (need 5)")
    elif pos == HARD_FILTERS["min_eps_positive_years"]:
        pass
    elif pos == 4 and all(e is not None and e > 0 for e in eps_recent[-3:]):
        review_reasons.append("EPS 4/5 & last 3 positive (COVID exception = REVIEW)")
    else:
        fail_reasons.append(f"EPS positive {pos}/5 (FAIL)")
else:
    fail_reasons.append("ไม่มีข้อมูล EPS")

# new
norm_eps = compute_normalized_earnings(data)
if norm_eps:
    current_year = datetime.now().year
    sorted_years = sorted(y for y in norm_eps.keys() if y < current_year)[-5:]
    eps_recent = [norm_eps[y] for y in sorted_years]
    pos = sum(1 for e in eps_recent if e is not None and e > 0)
    total = len(eps_recent)
    if total < 5:
        fail_reasons.append(f"EPS history {total}yr (need 5)")
    elif pos == HARD_FILTERS["min_eps_positive_years"]:
        pass
    elif pos == 4 and all(e is not None and e > 0 for e in eps_recent[-3:]):
        review_reasons.append("EPS 4/5 & last 3 positive (COVID exception = REVIEW)")
    else:
        fail_reasons.append(f"EPS positive {pos}/5 (FAIL)")
else:
    fail_reasons.append("ไม่มีข้อมูล EPS")

# Note: ต้อง import datetime ที่หัวไฟล์ (น่าจะ import แล้ว — verify ตอน build)

# current (scripts/fetch_data.py:137-138 area)
eps_list = [m.get("diluted_eps") for m in yearly_metrics if m.get("diluted_eps") is not None]
revenues = [m.get("revenue") for m in yearly_metrics if m.get("revenue") is not None]
eps_cagr = compute_cagr(eps_list, reject_negatives=True)
rev_cagr = compute_cagr(revenues)

# new
current_year = datetime.now().year
eps_list = [m.get("diluted_eps") for m in yearly_metrics
            if m.get("diluted_eps") is not None and m.get("year") and m.get("year") < current_year]
revenues = [m.get("revenue") for m in yearly_metrics
            if m.get("revenue") is not None and m.get("year") and m.get("year") < current_year]
eps_cagr = compute_cagr(eps_list, reject_negatives=True)
rev_cagr = compute_cagr(revenues)
```

## Phase 3: Config externalize + dividend logic swap
- [x] แก้ config.json — เพิ่ม 2 keys ใน filters block: growing_yield_floor (2.0), growing_min_streak (3) — Acceptance: cat config.json | grep growing_yield_floor returns line
- [x] แก้ scripts/screen_stocks.py DEFAULT_FILTERS (บรรทัด 31-42) — ไม่ต้องแก้ (มีอยู่แล้ว) + verify load_filters() merge config override correctly (บรรทัด 45-54) — Acceptance: ถ้าตั้ง config growing_yield_floor=2.5 → HARD_FILTERS["growing_yield_floor"] = 2.5 (assert ด้วย print หรือ test)
- [x] แก้ scripts/screen_stocks.py hard_filter dividend yield check (บรรทัด 108-122) — swap order: เช็ค growth_streak ≥ growing_min_streak ก่อน → ใช้เกณฑ์ growing_yield_floor / else ใช้เกณฑ์ min_dividend_yield — Acceptance: ผลลัพธ์เหมือนเดิมทุกเคส (5 test cases: yield=6 streak=2 PASS / yield=6 streak=5 PASS / yield=3 streak=5 PASS / yield=3 streak=2 FAIL / yield=1 streak=5 FAIL) + error message ใหม่อ่านง่ายขึ้น

### Reference
```json
// current config.json filters
{
  "filters": {
    "min_dividend_yield": 5,
    "min_dividend_streak": 5,
    "min_eps_positive_years": 5,
    "max_pe": 15,
    "bonus_pe": 8.0,
    "max_pbv": 1.5,
    "bonus_pbv": 1.0,
    "min_market_cap": 5000000000
  }
}

// new config.json filters (เพิ่ม 2 keys)
{
  "filters": {
    "min_dividend_yield": 5,
    "min_dividend_streak": 5,
    "min_eps_positive_years": 5,
    "max_pe": 15,
    "bonus_pe": 8.0,
    "max_pbv": 1.5,
    "bonus_pbv": 1.0,
    "min_market_cap": 5000000000,
    "growing_yield_floor": 2.0,
    "growing_min_streak": 3
  }
}
```

```python
# current (scripts/screen_stocks.py:108-122)
dy = data.get("dividend_yield")
growth_streak = agg.get("dividend_growth_streak", 0)
if dy is None:
    fail_reasons.append("ไม่มีข้อมูลปันผล")
elif dy >= HARD_FILTERS["min_dividend_yield"]:
    pass
elif (dy >= HARD_FILTERS["growing_yield_floor"]
      and growth_streak >= HARD_FILTERS["growing_min_streak"]):
    pass
else:
    fail_reasons.append(
        f"dividend yield {dy:.1f}% < {HARD_FILTERS['min_dividend_yield']:.0f}% "
        f"(growing exception not met: growth_streak {growth_streak}yr < {HARD_FILTERS['growing_min_streak']})"
    )

# new (swap order — streak first, then pick threshold)
dy = data.get("dividend_yield")
growth_streak = agg.get("dividend_growth_streak", 0)
if dy is None:
    fail_reasons.append("ไม่มีข้อมูลปันผล")
else:
    if growth_streak >= HARD_FILTERS["growing_min_streak"]:
        yield_threshold = HARD_FILTERS["growing_yield_floor"]
        threshold_reason = f"growing exception (streak {growth_streak}yr) → threshold {yield_threshold:.1f}%"
    else:
        yield_threshold = HARD_FILTERS["min_dividend_yield"]
        threshold_reason = f"main path → threshold {yield_threshold:.1f}%"
    if dy < yield_threshold:
        fail_reasons.append(
            f"dividend yield {dy:.1f}% < {yield_threshold:.1f}% ({threshold_reason})"
        )
```

## Phase 4: Verify end-to-end + pytest
- [x] รัน pytest บน MaxMahon tests (ถ้ามี) + manual smoke test: รัน py scripts/scan.py --limit 5 หุ้น (BBL, PTT, CPALL, KBANK, SCB) แล้ว verify ใน screener_*.json: dividend_streak + dividend_growth_streak ไม่นับปี 2026 + EPS check ผ่านตามที่ Niwes คาด — Acceptance: 5/5 หุ้น ผ่าน hard filter ถูกต้อง + count_dividend_growth_streak BBL ≥ 3 (5 ปีโต DPS — ตามที่ฝัง yahoo test แสดง: 2020 2.5 → 2021 3.5 → 2022 4.5 → 2023 7.0 → 2024 8.5 → 2025 10.0)

### Reference
Verify command:
```bash
cd C:\WORKSPACE\projects\4-MaxMahon
py scripts/scan.py --symbols BBL,PTT,CPALL,KBANK,SCB --no-write
# หรือ
py -c "from scripts.fetch_data import fetch_multi_year; print(fetch_multi_year('BBL'))"
```
Expected output: dividend_growth_streak BBL ≥ 3 (currently may be 0 due to bug)
