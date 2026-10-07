---
project: 4-MaxMahon
created: 2026-05-18
last_updated: 2026-05-18
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: รัน fetch_multi_year(sym) แล้ว aggregates dict มี 21 fields ใหม่ครบ + รัน screen_stocks ได้ screener output ที่ทุกหุ้น PASS มี anchor_stage_tags assigned ครบทุก dimension (Stage 2 dividend / Stage 3 cash flow / Stage 4 moat / Stage 5 stability)

### รายละเอียด
- Phase 1 ปันผล (3 fields): rising_ratio (% transitions DPS เพิ่ม), avg_yoy_growth (%/year arithmetic mean), roe_trend tag (ROE_IMPROVING/ROE_STABLE/ROE_DECLINING)
- Phase 2 cash flow (5 fields): ccr_avg_3y (OCF/EBITDA 3y avg), ocf_negative_count_3y, ocf_yoy_decline_pct (magnitude %), ocf_consecutive_declining_years, ocf_positive_3y
- Phase 3 moat (7 fields): roe_consecutive_15plus_years, gm_trend (improving/stable/declining), gm_recent_3y_avg, gm_earlier_3y_avg, interest_coverage_4y_avg, net_debt_history_5y, net_debt_increases_in_3y
- Phase 4 long_hold (6 fields): eps_cv_10y (stdev/mean), eps_mean_10y, crisis_2011_drop_pct, crisis_2020_drop_pct, ocf_2011, ocf_2020
- Phase 5 Stage tag assignment: NEW function assign_anchor_stage_tags(data, agg) ใน screen_stocks.py — return list[str] ของ Stage 2-5 tags + integrate ใน main() loop + screener output schema เพิ่ม key anchor_stage_tags per candidate
- Phase 6 smoke test 5 หุ้น (BBL/PTT/CPALL/KBANK/SCB): verify aggregates ครบ + tags ตรง Niwes intuition
- EBITDA compute = (Gross Profit - SG&A) + D&A — มีอยู่ใน yearly_metrics แล้ว (ใช้ field ebitda)
- Crisis drop = (price_min_during_crisis / price_pre_crisis) - 1 — ใช้ yearly_metrics close field ปี 2010-2011 + 2019-2020
- ROE consecutive 15%+ = walk yearly_metrics ROE field, count consecutive years where ROE >= 0.15 (decimal, after Phase 3 SETSMART override)
- GM trend = compare gm_recent_3y_avg vs gm_earlier_3y_avg: diff > +1% = improving / diff < -1% = declining / else stable
- Tag thresholds ตรงตาม parent plan niwes-refactor-v2-design Stage 1-6: GROWING_DIVIDEND = consecutive_no_cut >= 10y + rising_ratio >= 70% + avg_yoy_growth >= 3% etc.
- ไม่แตะ existing quality_score() + assign_signals() — เก็บ pillar-based scoring คู่ขนาน
- Output dict ใหม่ schema: signals (existing tags) + anchor_stage_tags (new) — parallel co-exist
- ใช้ Sector field จาก thaifin (data.get('sector')) เป็น input ของ Stage 5 tag assignment ใน Phase 5 (Plan 02 จะแยก sector_taxonomy.py แต่ Plan 01 ใช้ inline list ก่อน)

### Scope Boundary
**In scope:**
- projects/4-MaxMahon/scripts/fetch_data.py — extend _build_aggregates() function (lines 143-230) เพิ่ม 21 fields ใหม่
- projects/4-MaxMahon/scripts/screen_stocks.py — add NEW function assign_anchor_stage_tags(data, agg) + integrate in main() loop
- projects/4-MaxMahon/data/screener_*.json output schema — เพิ่ม key anchor_stage_tags per candidate (parallel กับ signals)

**Out of scope:**
- scripts/anchor_scoring.py compute scoring (Plan 02)
- scripts/sector_taxonomy.py (Plan 02 — Plan 01 ใช้ inline sector list ก่อน)
- Existing quality_score() / assign_signals() — ไม่แตะ
- Existing scan.py / report.py / report.js / server endpoint — ไม่กระทบ (output dict เพิ่ม key เท่านั้น)

### Non-goals
- ไม่ replace pillar-based quality_score — parallel co-exist ระหว่าง transition
- ไม่ refactor _build_aggregates structure — เพิ่ม fields ใน existing dict
- ไม่ break backward compat ของ screener output schema (เก่า keys + new keys)
- ไม่ทำ /api endpoint เพิ่ม — frontend ยังใช้ existing fields
- ไม่ทำ scoring computation — Plan 02 จัดการ

# Anchor Scoring — Aggregates Extension + Stage 1-6 Tags

> Part 1 of 2 — Aggregates extension + Stage 1-6 tag assignment. Foundation for Plan 02 scoring computation. | Index: anchor-scoring-index
> Depends on: none (filter-02/03/07 infra done 2026-05-18 = data quality stable)
> Parallel-safe with: none — Plan 02 depends on output ของ Plan 01

## Phase 1: ด้านปันผล — 3 new aggregate fields
- [x] แก้ scripts/fetch_data.py _build_aggregates() (lines 143-230) เพิ่ม 3 fields: (1) rising_ratio = (# transitions ที่ DPS เพิ่ม) / (total transitions) ใน dividend_history excluding current year FY — float 0.0-1.0 (2) avg_yoy_growth = mean ของ (DPS[y] / DPS[y-1] - 1) ใน transitions ที่ DPS[y-1] > 0 — float (e.g. 0.045 = 4.5%/year mean) (3) roe_trend = orthogonal tag จาก yearly_metrics ROE values: ROE_IMPROVING ถ้า recent 3y avg > earlier 3y avg + 0.02 / ROE_DECLINING ถ้า recent 3y avg < earlier 3y avg - 0.02 / ROE_STABLE else — string — scope: ไม่แตะ existing fields (revenue_cagr, eps_cagr, dps_cagr, etc.) เพิ่มเฉพาะ 3 keys ใหม่ — Acceptance: BBL aggregates มี rising_ratio (e.g. 0.62), avg_yoy_growth (e.g. 0.087), roe_trend (e.g. 'ROE_STABLE')

### Reference
```python
# current (scripts/fetch_data.py:143-230 area, end of _build_aggregates)
# dict construction at end — has these keys: revenue_cagr, eps_cagr, dps_cagr,
# avg_roe, min_roe, avg_net_margin, avg_gross_margin, avg_operating_margin,
# revenue_growth_years, eps_positive_years, fcf_positive_years,
# dividend_streak, dividend_growth_streak, years_of_data,
# latest_interest_coverage, latest_ocf_ni_ratio, latest_capital_intensity

# new — append 3 fields to existing aggregates dict
# Helper functions to compute (place above _build_aggregates or use inline):

def _compute_rising_ratio(dps_by_year: dict, fy_is_complete: dict) -> float | None:
    """Ratio of transitions where DPS increased.
    
    Iterates completed FY years (fy_is_complete[y]=True), counts transitions 
    where dps_by_year[y] > dps_by_year[y-1] AND dps_by_year[y-1] > 0.
    Returns None if < 2 complete years.
    """
    years = sorted(y for y in dps_by_year if fy_is_complete.get(y) is True)
    if len(years) < 2:
        return None
    transitions = 0
    rising = 0
    for i in range(1, len(years)):
        prev = dps_by_year[years[i-1]]
        curr = dps_by_year[years[i]]
        if prev > 0:
            transitions += 1
            if curr > prev:
                rising += 1
    return rising / transitions if transitions > 0 else None


def _compute_avg_yoy_growth(dps_by_year: dict, fy_is_complete: dict) -> float | None:
    """Arithmetic mean of YoY DPS % changes."""
    years = sorted(y for y in dps_by_year if fy_is_complete.get(y) is True)
    if len(years) < 2:
        return None
    growths = []
    for i in range(1, len(years)):
        prev = dps_by_year[years[i-1]]
        curr = dps_by_year[years[i]]
        if prev > 0:
            growths.append((curr / prev) - 1)
    return sum(growths) / len(growths) if growths else None


def _compute_roe_trend(yearly_metrics: list[dict]) -> str:
    """Compare recent 3y ROE avg vs earlier 3y ROE avg.
    
    Returns 'ROE_IMPROVING' / 'ROE_STABLE' / 'ROE_DECLINING'.
    Needs >= 6 years of ROE data; else returns 'ROE_STABLE' default.
    """
    roes = [m.get('roe') for m in yearly_metrics if m.get('roe') is not None]
    if len(roes) < 6:
        return 'ROE_STABLE'
    recent = sum(roes[-3:]) / 3
    earlier = sum(roes[-6:-3]) / 3
    if recent > earlier + 0.02:
        return 'ROE_IMPROVING'
    if recent < earlier - 0.02:
        return 'ROE_DECLINING'
    return 'ROE_STABLE'


# In _build_aggregates, after existing dict build:
aggregates = {
    ...existing keys...,
    'rising_ratio': _compute_rising_ratio(dps_by_year, fy_is_complete),
    'avg_yoy_growth': _compute_avg_yoy_growth(dps_by_year, fy_is_complete),
    'roe_trend': _compute_roe_trend(yearly_metrics),
}
```

## Phase 2: ด้าน Cash Flow — 5 new fields + CCR helper
- [x] แก้ scripts/fetch_data.py _build_aggregates() เพิ่ม 5 cash flow fields: (1) ccr_avg_3y = mean ของ OCF/EBITDA 3 ปีล่าสุด (exclude current year) — float (2) ocf_negative_count_3y = count ของปีที่ OCF < 0 ใน 3 ปีล่าสุด — int 0-3 (3) ocf_yoy_decline_pct = magnitude % ของ OCF decline (recent vs earlier 3y avg) — float negative (4) ocf_consecutive_declining_years = max consecutive years ที่ OCF ลดลง — int (5) ocf_positive_3y = bool ว่า OCF บวกครบ 3 ปีติด — scope: ใช้ yearly_metrics ที่มี ebitda + ocf (operating_cash_flow) field — Acceptance: BBL aggregates มี ccr_avg_3y (e.g. 0.85 จาก spec example), ocf_negative_count_3y (0 สำหรับ BBL), ocf_positive_3y True

### Reference
```python
# Helper functions:

def _compute_ccr_avg_3y(yearly_metrics: list[dict], current_year: int) -> float | None:
    """3y average of OCF / EBITDA.
    
    Uses yearly_metrics ocf + ebitda fields.
    Excludes current year (incomplete FY).
    Returns None if < 3 complete years with both fields.
    """
    valid = [
        m for m in yearly_metrics
        if m.get('year') and m['year'] < current_year
        and m.get('ocf') is not None and m.get('ebitda') is not None and m['ebitda'] != 0
    ]
    valid_sorted = sorted(valid, key=lambda m: m['year'], reverse=True)[:3]
    if len(valid_sorted) < 3:
        return None
    ratios = [m['ocf'] / m['ebitda'] for m in valid_sorted]
    return sum(ratios) / len(ratios)


def _compute_ocf_stats_3y(yearly_metrics: list[dict], current_year: int) -> dict:
    """Returns dict with negative_count_3y, yoy_decline_pct, consecutive_declining, positive_3y."""
    valid = [
        m for m in yearly_metrics
        if m.get('year') and m['year'] < current_year and m.get('ocf') is not None
    ]
    valid_sorted = sorted(valid, key=lambda m: m['year'], reverse=True)
    recent_3 = valid_sorted[:3]
    negative_count_3y = sum(1 for m in recent_3 if m['ocf'] < 0)
    positive_3y = len(recent_3) == 3 and all(m['ocf'] > 0 for m in recent_3)
    
    # yoy_decline_pct: compare recent 3y mean vs earlier 3y mean
    yoy_decline_pct = None
    if len(valid_sorted) >= 6:
        recent_avg = sum(m['ocf'] for m in valid_sorted[:3]) / 3
        earlier_avg = sum(m['ocf'] for m in valid_sorted[3:6]) / 3
        if earlier_avg != 0:
            yoy_decline_pct = (recent_avg / earlier_avg) - 1
    
    # Consecutive declining (newest to oldest)
    consecutive = 0
    asc = list(reversed(valid_sorted))
    for i in range(len(asc) - 1, 0, -1):
        if asc[i]['ocf'] < asc[i-1]['ocf']:
            consecutive += 1
        else:
            break
    
    return {
        'negative_count_3y': negative_count_3y,
        'yoy_decline_pct': yoy_decline_pct,
        'consecutive_declining': consecutive,
        'positive_3y': positive_3y,
    }


# In _build_aggregates dict:
ccr = _compute_ccr_avg_3y(yearly_metrics, current_year)
ocf_stats = _compute_ocf_stats_3y(yearly_metrics, current_year)
aggregates = {
    ...existing + Phase 1 keys...,
    'ccr_avg_3y': ccr,
    'ocf_negative_count_3y': ocf_stats['negative_count_3y'],
    'ocf_yoy_decline_pct': ocf_stats['yoy_decline_pct'],
    'ocf_consecutive_declining_years': ocf_stats['consecutive_declining'],
    'ocf_positive_3y': ocf_stats['positive_3y'],
}
```

## Phase 3: ด้าน Moat — 7 new fields + ROE/GM/Debt helpers
- [x] แก้ scripts/fetch_data.py _build_aggregates() เพิ่ม 7 moat fields: (1) roe_consecutive_15plus_years = max consecutive years ที่ ROE >= 0.15 — int (2) gm_trend = 'improving' / 'stable' / 'declining' — string (3) gm_recent_3y_avg = mean GM 3 ปีล่าสุด — float (4) gm_earlier_3y_avg = mean GM ปี 4-6 จากปัจจุบัน — float (5) interest_coverage_4y_avg = mean ของ interest_coverage 4 ปีล่าสุด — float | None (6) net_debt_history_5y = list[float] ของ net_debt 5 ปี (total_debt - cash_and_equivalents per year) — list | None (7) net_debt_increases_in_3y = count ปีที่ net_debt เพิ่ม ใน 3 transitions — int 0-3 — scope: ใช้ yearly_metrics roe + gross_margin + interest_coverage + total_debt + cash_and_equivalents fields ที่มีอยู่ — Acceptance: CPALL roe_consecutive_15plus_years >= 15 (Niwes textbook anchor), CPALL gm_trend = 'stable' หรือ 'improving'

### Reference
```python
def _compute_roe_consecutive_15plus(yearly_metrics: list[dict], current_year: int) -> int:
    """Max consecutive years where ROE >= 0.15 (15%), counting from most recent."""
    valid = sorted(
        [m for m in yearly_metrics if m.get('year') and m['year'] < current_year and m.get('roe') is not None],
        key=lambda m: m['year'], reverse=True
    )
    count = 0
    for m in valid:
        if m['roe'] >= 0.15:
            count += 1
        else:
            break
    return count


def _compute_gm_trend(yearly_metrics: list[dict], current_year: int) -> dict:
    """Returns {trend: str, recent_3y_avg: float|None, earlier_3y_avg: float|None}."""
    valid = sorted(
        [m for m in yearly_metrics if m.get('year') and m['year'] < current_year and m.get('gross_margin') is not None],
        key=lambda m: m['year'], reverse=True
    )
    if len(valid) < 6:
        return {'trend': 'stable', 'recent_3y_avg': None, 'earlier_3y_avg': None}
    recent = sum(m['gross_margin'] for m in valid[:3]) / 3
    earlier = sum(m['gross_margin'] for m in valid[3:6]) / 3
    if recent > earlier + 0.01:
        trend = 'improving'
    elif recent < earlier - 0.01:
        trend = 'declining'
    else:
        trend = 'stable'
    return {'trend': trend, 'recent_3y_avg': recent, 'earlier_3y_avg': earlier}


def _compute_net_debt_stats(yearly_metrics: list[dict], current_year: int) -> dict:
    """net_debt history 5y + count of increases in last 3 transitions."""
    valid = sorted(
        [m for m in yearly_metrics if m.get('year') and m['year'] < current_year
         and m.get('total_debt') is not None and m.get('cash_and_equivalents') is not None],
        key=lambda m: m['year'], reverse=True
    )
    if len(valid) < 5:
        return {'history_5y': None, 'increases_in_3y': 0}
    history = [m['total_debt'] - m['cash_and_equivalents'] for m in valid[:5]]
    increases = 0
    for i in range(min(3, len(history) - 1)):
        if history[i] > history[i + 1]:  # newest > older = increase
            increases += 1
    return {'history_5y': history, 'increases_in_3y': increases}


def _compute_interest_coverage_4y_avg(yearly_metrics: list[dict], current_year: int) -> float | None:
    valid = sorted(
        [m for m in yearly_metrics if m.get('year') and m['year'] < current_year
         and m.get('interest_coverage') is not None],
        key=lambda m: m['year'], reverse=True
    )[:4]
    if len(valid) < 4:
        return None
    return sum(m['interest_coverage'] for m in valid) / 4


# In _build_aggregates dict:
gm_stats = _compute_gm_trend(yearly_metrics, current_year)
debt_stats = _compute_net_debt_stats(yearly_metrics, current_year)
aggregates = {
    ...existing + Phase 1+2 keys...,
    'roe_consecutive_15plus_years': _compute_roe_consecutive_15plus(yearly_metrics, current_year),
    'gm_trend': gm_stats['trend'],
    'gm_recent_3y_avg': gm_stats['recent_3y_avg'],
    'gm_earlier_3y_avg': gm_stats['earlier_3y_avg'],
    'interest_coverage_4y_avg': _compute_interest_coverage_4y_avg(yearly_metrics, current_year),
    'net_debt_history_5y': debt_stats['history_5y'],
    'net_debt_increases_in_3y': debt_stats['increases_in_3y'],
}
```

**Note on field names**: ตรวจ yearly_metrics actual key names ก่อน (อาจเป็น 'gross_margin' or 'gm' or 'gross_margin_pct'). อ่าน _fetch_thaifin() output structure ก่อน.

## Phase 4: ด้าน Long Hold — 6 new fields (EPS CV + Crisis Drop)
- [x] แก้ scripts/fetch_data.py _build_aggregates() เพิ่ม 6 long_hold fields: (1) eps_cv_10y = stdev / mean ของ EPS 10 ปี — float (2) eps_mean_10y = mean EPS 10 ปี — float (3) crisis_2011_drop_pct = max drawdown ปี 2010-2011 (negative %) — float | None (4) crisis_2020_drop_pct = max drawdown ปี 2019-2020 — float | None (5) ocf_2011 = OCF ปี 2011 — float | None (6) ocf_2020 = OCF ปี 2020 — float | None — scope: ใช้ yearly_metrics close + diluted_eps + ocf — Acceptance: CPALL eps_cv_10y < 0.30 (stable), BDMS crisis drop ปี 2020 > -40% (resilient), PTT ocf_2020 > 0

### Reference
```python
import statistics

def _compute_eps_cv_10y(yearly_metrics: list[dict], current_year: int) -> dict:
    """Coefficient of variation (stdev/mean) of EPS over 10y excluding current year."""
    valid = sorted(
        [m for m in yearly_metrics if m.get('year') and m['year'] < current_year
         and m.get('diluted_eps') is not None],
        key=lambda m: m['year'], reverse=True
    )[:10]
    if len(valid) < 5:
        return {'eps_cv_10y': None, 'eps_mean_10y': None}
    eps_values = [m['diluted_eps'] for m in valid]
    mean = sum(eps_values) / len(eps_values)
    if mean == 0:
        return {'eps_cv_10y': None, 'eps_mean_10y': 0}
    stdev = statistics.pstdev(eps_values)
    return {'eps_cv_10y': stdev / abs(mean), 'eps_mean_10y': mean}


def _compute_crisis_drop(yearly_metrics: list[dict], pre_year: int, crisis_year: int, field: str = 'close') -> float | None:
    """Max drawdown from pre_year to crisis_year using close (or specified field).
    
    Returns negative percent (e.g. -0.45 = dropped 45%).
    """
    by_year = {m['year']: m for m in yearly_metrics if m.get('year') in (pre_year, crisis_year)}
    pre = by_year.get(pre_year, {}).get(field)
    crisis = by_year.get(crisis_year, {}).get(field)
    if pre is None or crisis is None or pre == 0:
        return None
    return (crisis - pre) / pre


def _get_ocf_for_year(yearly_metrics: list[dict], year: int) -> float | None:
    for m in yearly_metrics:
        if m.get('year') == year:
            return m.get('ocf')
    return None


# In _build_aggregates dict:
eps_stats = _compute_eps_cv_10y(yearly_metrics, current_year)
aggregates = {
    ...existing + Phase 1+2+3 keys...,
    'eps_cv_10y': eps_stats['eps_cv_10y'],
    'eps_mean_10y': eps_stats['eps_mean_10y'],
    'crisis_2011_drop_pct': _compute_crisis_drop(yearly_metrics, 2010, 2011, 'close'),
    'crisis_2020_drop_pct': _compute_crisis_drop(yearly_metrics, 2019, 2020, 'close'),
    'ocf_2011': _get_ocf_for_year(yearly_metrics, 2011),
    'ocf_2020': _get_ocf_for_year(yearly_metrics, 2020),
}
```

## Phase 5: Stage 1-6 Tag Assignment — assign_anchor_stage_tags
- [x] สร้าง NEW function assign_anchor_stage_tags(data, agg) ใน scripts/screen_stocks.py — return list[str] ของ Stage 2-5 tags ตาม parent plan rules — input: data dict + agg dict (from Plan 01 Phase 1-4) — output: list of strings เช่น ['GROWING_DIVIDEND', 'CASHFLOW_HEALTHY', 'STRONG_MOAT', 'STABLE_BUSINESS', 'RESILIENT_THROUGH_CRISIS', 'ROE_STABLE'] — scope: ไม่แก้ existing assign_signals() — Acceptance: assign_anchor_stage_tags บน CPALL data return tags ที่มี GROWING_DIVIDEND + STRONG_MOAT + STABLE_BUSINESS / SCC return DIVIDEND_SHRINKING + NO_MOAT + CYCLICAL_BUSINESS
- [x] integrate assign_anchor_stage_tags() ใน scripts/screen_stocks.py main() loop — เรียกหลัง assign_signals() + เก็บลง output dict key anchor_stage_tags — scope: ไม่แก้ output schema อื่น — Acceptance: รัน screen_stocks.py แล้ว screener_*.json ทุกหุ้น PASS มี anchor_stage_tags array

### Reference
```python
# Inline sector lists (Plan 01 ใช้ ก่อน Plan 02 แยกเป็น module):
STABLE_SECTORS_TEMP = {
    'Commerce', 'Food & Beverage', 'Healthcare', 'Information & Communication Technology',
    'Media & Publishing', 'Tourism & Leisure', 'Transportation & Logistics'
}
CYCLICAL_SECTORS_TEMP = {
    'Energy & Utilities', 'Petrochemicals & Chemicals', 'Steel',
    'Construction Materials', 'Property Development', 'Mining'
}
STABLE_UTILITY_SYMBOLS_TEMP = {'EGCO', 'GPSC', 'RATCH', 'BPP', 'BCPG'}


def assign_anchor_stage_tags(data: dict, agg: dict) -> list[str]:
    """Assign Stage 2-5 anchor tags per parent plan niwes-refactor-v2-design.
    
    Returns list of tag strings (e.g. 'GROWING_DIVIDEND', 'STRONG_MOAT').
    Side-by-side with existing assign_signals() — doesn't replace.
    """
    tags = []
    sector = data.get('sector', '')
    symbol = data.get('symbol', '').replace('.BK', '')
    
    # Stage 2: Dividend tier (mutually exclusive)
    consecutive = agg.get('dividend_streak', 0)
    rising = agg.get('rising_ratio') or 0
    growth = agg.get('avg_yoy_growth') or 0
    if consecutive >= 10 and rising >= 0.70 and growth >= 0.03:
        tags.append('GROWING_DIVIDEND')
    elif consecutive >= 10:
        tags.append('STABLE_PAYER')
    elif consecutive >= 3:
        tags.append('NEW_PAYER')
    else:
        tags.append('INTERMITTENT')
    
    # Stage 2: DIVIDEND_SHRINKING (orthogonal)
    dividend_history = data.get('dividend_history') or {}
    if dividend_history:
        sorted_years = sorted(dividend_history.keys())
        if len(sorted_years) >= 2:
            recent_dps = [dividend_history[y] for y in sorted_years[-5:]]
            peak = max(recent_dps) if recent_dps else 0
            current_dps = recent_dps[-1] if recent_dps else 0
            if peak > 0 and current_dps < peak * 0.70:
                tags.append('DIVIDEND_SHRINKING')
    
    # Stage 2: YIELD_TRAP (orthogonal)
    dy = data.get('dividend_yield') or 0
    if dy > 8 and consecutive < 5:
        tags.append('YIELD_TRAP')
    
    # Stage 2: ROE trend (orthogonal — from Phase 1 aggregate)
    roe_trend = agg.get('roe_trend', 'ROE_STABLE')
    tags.append(roe_trend)
    
    # Stage 3: Cash flow tier
    ccr = agg.get('ccr_avg_3y')
    ocf_positive = agg.get('ocf_positive_3y', False)
    ocf_neg = agg.get('ocf_negative_count_3y', 0)
    ocf_decline = agg.get('ocf_yoy_decline_pct')
    if ccr is not None and ocf_positive:
        if ccr >= 0.70:
            tags.append('CASHFLOW_HEALTHY')
        elif ccr >= 0.50:
            tags.append('CASHFLOW_OK')
        else:
            tags.append('CASHFLOW_BELOW_PROFIT')
    if ocf_neg >= 1:
        # If has positive NP but OCF negative -> FAKE_PROFIT
        latest_eps = data.get('eps_trailing') or 0
        if latest_eps > 0:
            tags.append('FAKE_PROFIT')
    if ocf_decline is not None and ocf_decline <= -0.20:
        tags.append('CASHFLOW_DETERIORATING')
    
    # Stage 4: Moat tier (mutually exclusive)
    roe_15plus = agg.get('roe_consecutive_15plus_years', 0)
    gm_trend = agg.get('gm_trend', 'stable')
    avg_roe = agg.get('avg_roe', 0) or 0
    de = data.get('debt_to_equity') or data.get('de_ratio')
    int_cov = agg.get('interest_coverage_4y_avg')
    net_debt_inc = agg.get('net_debt_increases_in_3y', 0)
    
    if avg_roe >= 0.15 and de and de > 2.0 and int_cov is not None and int_cov < 3 and net_debt_inc >= 2:
        tags.append('ROE_FUELED_BY_DEBT')
    elif roe_15plus >= 7 and gm_trend in ('stable', 'improving'):
        tags.append('STRONG_MOAT')
    elif roe_15plus >= 5 and gm_trend == 'stable' and avg_roe >= 0.10:
        tags.append('MODERATE_MOAT')
    elif gm_trend == 'declining' or avg_roe < 0.10:
        tags.append('NO_MOAT')
        if roe_15plus >= 3:
            tags.append('MOAT_ERODING')  # was strong, now declining
    else:
        tags.append('NO_MOAT')
    
    # Stage 5: Stability tier
    eps_cv = agg.get('eps_cv_10y')
    is_stable_sector = (sector in STABLE_SECTORS_TEMP) or (symbol in STABLE_UTILITY_SYMBOLS_TEMP)
    is_cyclical_sector = sector in CYCLICAL_SECTORS_TEMP
    if is_stable_sector and eps_cv is not None and eps_cv <= 0.30:
        tags.append('STABLE_BUSINESS')
    elif is_cyclical_sector or (eps_cv is not None and eps_cv > 0.50):
        tags.append('CYCLICAL_BUSINESS')
    else:
        tags.append('MIXED_STABILITY')
    
    # Stage 5: RESILIENT_THROUGH_CRISIS (orthogonal — additive)
    drop2011 = agg.get('crisis_2011_drop_pct')
    drop2020 = agg.get('crisis_2020_drop_pct')
    ocf2011 = agg.get('ocf_2011')
    ocf2020 = agg.get('ocf_2020')
    if (drop2011 is not None and drop2011 >= -0.40 and (ocf2011 or 0) > 0 and
        drop2020 is not None and drop2020 >= -0.40 and (ocf2020 or 0) > 0):
        tags.append('RESILIENT_THROUGH_CRISIS')
    
    return tags


# Integration in main() loop — after assign_signals(), before scoring:
# signals = assign_signals(data, score_result, sector_pe_median)
# anchor_stage_tags = assign_anchor_stage_tags(data, agg)
# result_entry['signals'] = signals
# result_entry['anchor_stage_tags'] = anchor_stage_tags  # NEW key
```

**Note**: Threshold values from parent plan niwes-refactor-v2-design Stage 2-5. Verify against parent plan when implementing — may need slight adjustment for actual yearly_metrics field name conventions.

## Phase 6: Smoke Test — 5 stocks verification
- [x] Smoke test py -c that fetches 5 stocks (BBL/PTT/CPALL/KBANK/SCB) + verify aggregates 21 fields + assign_anchor_stage_tags ออก tags ที่ตรง Niwes intuition: CPALL -> GROWING_DIVIDEND + STRONG_MOAT + STABLE_BUSINESS / SCC -> DIVIDEND_SHRINKING + NO_MOAT + CYCLICAL_BUSINESS / PTT -> CYCLICAL_BUSINESS + (MOAT_ERODING if applicable) / BBL -> STABLE_PAYER + healthy / KBANK -> STABLE_PAYER + healthy — scope: smoke only ไม่ replace pipeline — Acceptance: 5 stocks ผ่าน fetch + assign_anchor_stage_tags + tags ตรง Niwes expectation อย่างน้อย 80% (4/5 หุ้น)

### Reference
```bash
# Verify command pattern:
cd C:\WORKSPACE\projects\4-MaxMahon
SETSMART_API_KEY=... py -c "
import sys
sys.path.insert(0, 'scripts')
from fetch_data import fetch_multi_year
from screen_stocks import assign_anchor_stage_tags
for sym in ['BBL', 'PTT', 'CPALL', 'KBANK', 'SCB']:
    r = fetch_multi_year(sym)
    agg = r['aggregates']
    print(f'{sym}: ccr_avg_3y={agg.get(\"ccr_avg_3y\")}, roe_15plus={agg.get(\"roe_consecutive_15plus_years\")}, eps_cv_10y={agg.get(\"eps_cv_10y\")}')
    tags = assign_anchor_stage_tags(r, agg)
    print(f'  tags: {tags}')
"
```

Expected output pattern (qualitative — actual values from data):
- CPALL: GROWING_DIVIDEND + STRONG_MOAT + STABLE_BUSINESS + RESILIENT_THROUGH_CRISIS + ROE_IMPROVING
- SCC: DIVIDEND_SHRINKING + YIELD_TRAP (if dy high) + NO_MOAT + CYCLICAL_BUSINESS + ROE_DECLINING
- PTT: STABLE_PAYER + ROE_DECLINING + CYCLICAL_BUSINESS + MOAT_ERODING (if ROE was >=15% in earlier years)
- BBL: STABLE_PAYER + CASHFLOW_HEALTHY + ROE_STABLE
- KBANK: STABLE_PAYER + CASHFLOW_HEALTHY + ROE_STABLE

Note: หากผลตัวเลขไม่ตรง intuition 100% — ก็ OK เป็น Plan 02 / TEST GATE 3 จะ deeper verify
