---
project: 4-MaxMahon
created: 2026-05-12
last_updated: 2026-05-12
status: active
---

## Target / Goal

### เป้าหมาย
ทำได้: รัน compute_normalized_earnings(data) แล้วได้ EPS ที่ตัดรายการพิเศษ (one-time gains/losses) ออกแล้ว — ใช้ yahoo NormalizedIncome ÷ diluted shares per year + fallback ไป diluted_eps ดิบเมื่อ yahoo flake + log warning + EPS filter Niwes 5-5-5-5 ใช้ normalized value จริง ไม่ใช่ raw ที่ชื่อ normalized

### รายละเอียด
- ปัจจุบัน compute_normalized_earnings (data_adapter.py:913-929) = misnomer — return raw thaifin diluted_eps {year: eps}
- EXTRAORDINARY_KEYWORDS constant ที่ data_adapter.py:909-910 — never used
- Yahoo income_statement มี fields ที่ใช้ได้:
- - TotalUnusualItems (รายการพิเศษรวม)
- - TotalUnusualItemsExcludingGoodwill
- - SpecialIncomeCharges (special income/charges)
- - TaxEffectOfUnusualItems
- - NormalizedIncome (yahoo คำนวณให้เลย — Net Income after stripping unusual items)
- - BasicEPS, DilutedEPS (raw)
- - DilutedAverageShares (jumlah hisse — for computing EPS from NormalizedIncome)
- Approach: ใช้ yahoo NormalizedIncome ÷ DilutedAverageShares = normalized EPS per year
- SETSMART งบไม่มี extraordinary field — ใช้ yahoo only
- thaifin ไม่มี — ใช้ yahoo only
- Yahoo income_statement = 5 years (2021-2025 per BBL test) — match กับ Niwes 5-year EPS window พอดี
- Fallback: ถ้า yahoo income_statement flake / ไม่มี NormalizedIncome → ใช้ thaifin diluted_eps (raw) + log warning
- ลบ EXTRAORDINARY_KEYWORDS constant ที่ไม่ใช้ (cleanup)
- หรือ keep ไว้สำหรับ future SETSMART/thaifin extension

### Scope Boundary
**In scope:**
- scripts/data_adapter.py — compute_normalized_earnings function (บรรทัด 913-929)
- scripts/data_adapter.py — _fetch_yahoo_supplement (บรรทัด 445-614) เพิ่ม extract NormalizedIncome + DilutedAverageShares per year

**Out of scope:**
- EPS filter logic ใน screen_stocks.py (Plan A เปลี่ยน window แล้ว — ไม่กระทบ)
- Quality Score EPS-related scoring
- SETSMART/thaifin extraordinary detection

### Non-goals
- ไม่ implement extraordinary detection จาก line-item keywords (เพราะ yahoo คำนวณ NormalizedIncome ให้แล้ว)
- ไม่เปลี่ยน Niwes 5/5 positive years rule
- ไม่ extend ไปยัง SETSMART (SETSMART ไม่มี field)

# Plan E — Implement Normalized EPS (Yahoo NormalizedIncome ÷ Diluted Shares)

> Part 5 of 7 — Normalized EPS implementation. เปลี่ยนชื่อหลอกเป็นของจริง — ใช้ yahoo NormalizedIncome ÷ shares ตัดรายการพิเศษ. EPS filter Niwes 5/5 บวก ใช้ normalized value จริง.
> Depends on: filter-02-setsmart-migration (ต้องมี yahoo income_statement integration ที่ Plan B ใช้)
> Parallel-safe with: filter-03-dps-yahoo-only, filter-04-review-pass-tag

## Phase 1: Extract NormalizedIncome + DilutedAverageShares จาก yahoo
- [ ] แก้ scripts/data_adapter.py _fetch_yahoo_supplement (บรรทัด 445-614) — เพิ่มการ extract `normalized_income_by_year` + `diluted_avg_shares_by_year` จาก yahoo income_statement(frequency='a') — Scope: ไม่กระทบ existing fetches (capex, interest_expense, dividends) — Acceptance: _fetch_yahoo_supplement('BBL') คืน dict มี keys 'normalized_income_by_year' (year:int → income:float) + 'diluted_avg_shares_by_year' (year:int → shares:float)
- [ ] Handle edge cases: ถ้า income_statement DataFrame ไม่มี 'NormalizedIncome' column หรือ 'DilutedAverageShares' column → log warning + return {} dict ว่าง — Acceptance: หุ้นที่ yahoo flake → keys อยู่ใน return แต่ value = {} + warning ใน log

### Reference
```python
# current (scripts/data_adapter.py:589-591 — interest expense extract pattern)
income_df = tk.income_statement(frequency='a', trailing=False)
if income_df is not None and not income_df.empty and 'InterestExpense' in income_df.columns:
    for _, row in income_df.iterrows():
        # ... extract per year ...

# new — extend to NormalizedIncome + DilutedAverageShares
normalized_income_by_year = {}
diluted_avg_shares_by_year = {}
try:
    income_df = tk.income_statement(frequency='a', trailing=False)
    if income_df is not None and not income_df.empty:
        for _, row in income_df.iterrows():
            as_of = row.get('asOfDate')
            if as_of is None:
                continue
            year = pd.to_datetime(as_of).year
            if 'NormalizedIncome' in row.index and pd.notna(row['NormalizedIncome']):
                normalized_income_by_year[year] = float(row['NormalizedIncome'])
            if 'DilutedAverageShares' in row.index and pd.notna(row['DilutedAverageShares']):
                diluted_avg_shares_by_year[year] = float(row['DilutedAverageShares'])
except Exception as e:
    logger.warning("yahoo income_statement fetch failed for %s: %s", symbol, e)

# Return dict — add new keys
return {
    # ... existing keys ...
    'normalized_income_by_year': normalized_income_by_year,
    'diluted_avg_shares_by_year': diluted_avg_shares_by_year,
}
```

## Phase 2: compute_normalized_earnings — ใช้ yahoo NormalizedIncome
- [ ] แก้ scripts/data_adapter.py compute_normalized_earnings (บรรทัด 913-929) — เปลี่ยน logic: รับ data dict, ถ้ามี normalized_income_by_year + diluted_avg_shares_by_year (จาก yahoo) → compute normalized_eps = income / shares per year, fallback ไป raw diluted_eps จาก yearly_metrics เมื่อ yahoo flake — Acceptance: compute_normalized_earnings({yearly_metrics: [...], normalized_income_by_year: {2024: 50000000}, diluted_avg_shares_by_year: {2024: 1908000}}) คืน {2024: 26.2} (normalized EPS) ไม่ใช่ thaifin diluted_eps
- [ ] ลบ EXTRAORDINARY_KEYWORDS constant (บรรทัด 909-910) — Scope: cleanup unused code — Acceptance: grep 'EXTRAORDINARY_KEYWORDS' scripts/ ไม่เจอ result

### Reference
```python
# current (scripts/data_adapter.py:909-929)
EXTRAORDINARY_KEYWORDS = (
    "extraordinary", "one-time", "gain on sale", "impairment",
)

def compute_normalized_earnings(data: dict) -> dict:
    """thaifin yearly_dataframe does not expose line-item names for extraordinary items,
    so this falls back to using diluted_eps as-is."""
    yearly = data.get('yearly_metrics') or []
    result = {}
    for ym in yearly:
        year = ym.get('year')
        eps = ym.get('diluted_eps')
        if year is None or eps is None:
            continue
        result[year] = eps
    return result

# new — use yahoo NormalizedIncome
def compute_normalized_earnings(data: dict) -> dict:
    """Normalized EPS = yahoo NormalizedIncome ÷ DilutedAverageShares per year.
    
    Yahoo computes NormalizedIncome by stripping TotalUnusualItems from NetIncome —
    we use it directly. Fallback to thaifin raw diluted_eps when yahoo flake.
    """
    yearly = data.get('yearly_metrics') or []
    norm_income = data.get('normalized_income_by_year') or {}
    diluted_shares = data.get('diluted_avg_shares_by_year') or {}
    
    result = {}
    for ym in yearly:
        year = ym.get('year')
        if year is None:
            continue
        
        # Try yahoo normalized first
        ni = norm_income.get(year)
        shares = diluted_shares.get(year)
        if ni is not None and shares is not None and shares > 0:
            result[year] = ni / shares
        else:
            # Fallback: raw diluted_eps from thaifin
            eps_raw = ym.get('diluted_eps')
            if eps_raw is not None:
                result[year] = eps_raw
                logger.warning(
                    "normalized_eps fallback to raw diluted_eps for year %s (yahoo flake)",
                    year
                )
    return result
```

## Phase 3: Smoke test + verify
- [ ] py -c 'from scripts.data_adapter import fetch_fundamentals, compute_normalized_earnings; r=fetch_fundamentals("BBL"); norm=compute_normalized_earnings(r); print("normalized EPS:", norm); print("raw diluted:", {y: m.get("diluted_eps") for m in r["yearly_metrics"] for y in [m.get("year")] if y})' — Acceptance: BBL ปี 2024 normalized EPS ≠ raw diluted_eps (มี TotalUnusualItems ตัดออก) สำหรับปี 2021-2025 (yahoo coverage)
- [ ] Smoke 5 หุ้น: py scripts/scan.py --symbols BBL,PTT,CPALL,KBANK,SCB --no-write + verify EPS hard filter ใช้ normalized value — Acceptance: scan สำเร็จ + log แสดง normalized EPS ใช้งานจริง ไม่ใช่ raw

### Reference
Verify commands:
```bash
cd C:\WORKSPACE\projects\4-MaxMahon

py -c "
from scripts.data_adapter import fetch_fundamentals, compute_normalized_earnings
r = fetch_fundamentals('BBL')
norm = compute_normalized_earnings(r)
raw = {m['year']: m.get('diluted_eps') for m in r['yearly_metrics'] if m.get('year')}
for y in sorted(set(list(norm.keys()) + list(raw.keys())))[-5:]:
    print(f'{y}: normalized={norm.get(y, \"?\")} | raw={raw.get(y, \"?\")}')
"
# Expected: normalized และ raw แตกต่างกันสำหรับปีที่มี extraordinary items
```
