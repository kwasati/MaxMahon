"""Max Mahon v4 — fetch multi-year Thai stock fundamentals.

Primary: thaifin (10+ years Thai financials)
Supplement: yahooquery (realtime price, DPS events, capex + interest_expense per year)
No fallback: if thaifin fails the stock is treated as delisted/missing.
"""

import json
import logging
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# Ensure project root is in sys.path for `from scripts.xxx` imports
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from scripts.data_adapter import fetch_fundamentals as _adapter_fetch
from scripts.data_adapter import fetch_from_thaifin
from scripts.data_adapter import (
    classify_sector_profile,
    complete_dividend_by_year,
    dividend_crisis_facts,
    last_complete_fy,
    load_crisis_bars,
)

ROOT = Path(__file__).resolve().parent.parent
USER_DATA = ROOT / "user_data.json"
DATA_DIR = ROOT / "data"

FINANCIAL_SECTORS = {"Financial Services", "Banking", "Insurance"}


def safe_get(df, row_name, col):
    try:
        val = df.loc[row_name, col]
        if pd.isna(val):
            return None
        return float(val)
    except (KeyError, TypeError):
        return None


def safe_div(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


def normalize_yield(val):
    if val is None:
        return None
    if val < 1:
        return val * 100
    return val


def compute_cagr(values, reject_negatives=False):
    # If reject_negatives, return None if any value is negative (e.g. EPS with loss years)
    if reject_negatives and any(v is not None and v < 0 for v in values):
        return None
    clean = [(i, v) for i, v in enumerate(values) if v is not None and v > 0]
    if len(clean) < 2:
        return None
    first_i, first_v = clean[0]
    last_i, last_v = clean[-1]
    years = last_i - first_i
    if years <= 0:
        return None
    try:
        return (last_v / first_v) ** (1 / years) - 1
    except (ValueError, ZeroDivisionError):
        return None


def count_dividend_streak(dps_by_year, fy_is_complete=None):
    """Consecutive complete FYs with DPS > 0, counted back from the latest complete FY.

    Stops at the first missing year (a gap) or a zero-DPS year. Incomplete FYs are
    excluded via complete_dividend_by_year. fy_is_complete=None → every FY before
    the current calendar year counts as complete.
    """
    complete = complete_dividend_by_year(dps_by_year, fy_is_complete)
    if not complete:
        return 0
    y = max(complete)
    streak = 0
    while complete.get(y) is not None and complete[y] > 0:
        streak += 1
        y -= 1
    return streak


def count_dividend_growth_streak(dps_by_year, fy_is_complete=None):
    """Consecutive complete FYs (from the latest) where DPS rose vs the previous FY.

    Stops at a gap in the years, a non-increase, or a zero base year.
    """
    complete = complete_dividend_by_year(dps_by_year, fy_is_complete)
    if not complete:
        return 0
    y = max(complete)
    streak = 0
    while (y - 1) in complete and complete[y - 1] > 0 and complete[y] > complete[y - 1]:
        streak += 1
        y -= 1
    return streak


def compute_dps_cagr(dps_by_year, fy_is_complete=None, years=5):
    """CAGR of DPS over exactly `years` complete years: (DPS[L] / DPS[L-years])^(1/years) - 1.

    L = latest complete FY. None if either end is missing or not > 0.
    """
    complete = complete_dividend_by_year(dps_by_year, fy_is_complete)
    if not complete:
        return None
    last = max(complete)
    first_v, last_v = complete.get(last - years), complete[last]
    if first_v is None or first_v <= 0 or last_v is None or last_v <= 0:
        return None
    return (last_v / first_v) ** (1 / years) - 1


def validate_metrics(info, yearly_metrics):
    warnings = []
    dy = normalize_yield(info.get("dividendYield"))
    if dy is not None and dy > 15:
        warnings.append(f"yield {dy:.0f}% ผิดปกติ — ตรวจสอบข้อมูล")

    eg = info.get("earningsGrowth")
    if eg is not None and abs(eg) > 3:
        warnings.append(f"earnings growth {eg*100:.0f}% — อาจเป็น base effect หรือข้อมูลผิด")

    payout = info.get("payoutRatio")
    if payout is not None and payout > 1.5:
        warnings.append(f"payout {payout*100:.0f}% — จ่ายเกินกำไร")

    for ym in yearly_metrics:
        roe = ym.get("roe")
        if roe is not None and abs(roe) > 1.5:
            warnings.append(f"ROE {roe*100:.0f}% ปี {ym['year']} — สูงผิดปกติ")
            break

    return warnings


def _year_int(m):
    """Safely convert yearly_metric's 'year' field (str) → int. None if invalid."""
    y = m.get("year")
    if y is None:
        return None
    try:
        return int(y)
    except (TypeError, ValueError):
        return None


# --- Anchor scoring helpers (Phases 1-4) ---
# All helpers return None gracefully when source data is missing in yearly_metrics.
# Field name notes (verified against data_adapter._fetch_thaifin yearly_metrics dict):
#   - cash_and_equivalents → use field 'cash' (thaifin column)
#   - payout_ratio_year → use field 'payout_ratio'
#   - All other plan-referenced fields match actual schema.

def _dps_transitions(dps_by_year: dict, fy_is_complete) -> list:
    """(prev, curr) DPS pairs for consecutive complete FYs with prev > 0."""
    complete = complete_dividend_by_year(dps_by_year, fy_is_complete)
    return [(complete[y - 1], complete[y]) for y in sorted(complete)
            if (y - 1) in complete and complete[y - 1] > 0]


def _compute_rising_ratio(dps_by_year: dict, fy_is_complete) -> "float | None":
    """Ratio of YoY transitions where DPS increased (complete, consecutive FYs only)."""
    pairs = _dps_transitions(dps_by_year, fy_is_complete)
    if not pairs:
        return None
    return sum(1 for prev, curr in pairs if curr > prev) / len(pairs)


def _compute_avg_yoy_growth(dps_by_year: dict, fy_is_complete) -> "float | None":
    """Arithmetic mean of YoY DPS % changes (complete, consecutive FYs only)."""
    pairs = _dps_transitions(dps_by_year, fy_is_complete)
    if not pairs:
        return None
    return sum(curr / prev - 1 for prev, curr in pairs) / len(pairs)


def _compute_roe_trend(yearly_metrics: list) -> str:
    """Compare recent 3y ROE avg vs earlier 3y ROE avg. Needs >=6 non-None ROE points."""
    roes = [m.get("roe") for m in yearly_metrics if m.get("roe") is not None]
    if len(roes) < 6:
        return "ROE_STABLE"
    recent = sum(roes[-3:]) / 3
    earlier = sum(roes[-6:-3]) / 3
    if recent > earlier + 0.02:
        return "ROE_IMPROVING"
    if recent < earlier - 0.02:
        return "ROE_DECLINING"
    return "ROE_STABLE"


def _compute_ccr_avg_3y(yearly_metrics: list, current_year: int) -> "float | None":
    """3y average of OCF / EBITDA (excluding current calendar year)."""
    valid = []
    for m in yearly_metrics:
        y = _year_int(m)
        if y is None or y >= current_year:
            continue
        ocf = m.get("ocf")
        ebitda = m.get("ebitda")
        if ocf is None or ebitda is None or ebitda == 0:
            continue
        valid.append((y, ocf, ebitda))
    valid.sort(key=lambda t: t[0], reverse=True)
    valid = valid[:3]
    if len(valid) < 3:
        return None
    ratios = [ocf / ebitda for _, ocf, ebitda in valid]
    return sum(ratios) / len(ratios)


def _compute_ocf_stats_3y(yearly_metrics: list, current_year: int) -> dict:
    """Return {negative_count_3y, yoy_decline_pct, consecutive_declining, positive_3y}."""
    valid = []
    for m in yearly_metrics:
        y = _year_int(m)
        if y is None or y >= current_year:
            continue
        ocf = m.get("ocf")
        if ocf is None:
            continue
        valid.append((y, ocf))
    valid.sort(key=lambda t: t[0], reverse=True)
    recent_3 = valid[:3]
    negative_count_3y = sum(1 for _, ocf in recent_3 if ocf < 0)
    positive_3y = len(recent_3) == 3 and all(ocf > 0 for _, ocf in recent_3)
    yoy_decline_pct = None
    if len(valid) >= 6:
        recent_avg = sum(ocf for _, ocf in valid[:3]) / 3
        earlier_avg = sum(ocf for _, ocf in valid[3:6]) / 3
        if earlier_avg != 0:
            yoy_decline_pct = (recent_avg / earlier_avg) - 1
    # Consecutive declining count (newest going back; each step requires ocf < prev)
    consecutive = 0
    for i in range(len(valid) - 1):
        if valid[i][1] < valid[i + 1][1]:
            consecutive += 1
        else:
            break
    return {
        "negative_count_3y": negative_count_3y,
        "yoy_decline_pct": yoy_decline_pct,
        "consecutive_declining": consecutive,
        "positive_3y": positive_3y,
    }


def _compute_roe_consecutive_15plus(yearly_metrics: list, current_year: int) -> int:
    """Consecutive years (from newest, excluding current year) with ROE >= 0.15."""
    valid = []
    for m in yearly_metrics:
        y = _year_int(m)
        if y is None or y >= current_year:
            continue
        roe = m.get("roe")
        if roe is None:
            continue
        valid.append((y, roe))
    valid.sort(key=lambda t: t[0], reverse=True)
    count = 0
    for _, roe in valid:
        if roe >= 0.15:
            count += 1
        else:
            break
    return count


def _compute_gm_trend_stats(yearly_metrics: list, current_year: int) -> dict:
    """Gross margin trend: recent 3y avg vs earlier 3y avg. Returns dict."""
    valid = []
    for m in yearly_metrics:
        y = _year_int(m)
        if y is None or y >= current_year:
            continue
        gm = m.get("gross_margin")
        if gm is None:
            continue
        valid.append((y, gm))
    valid.sort(key=lambda t: t[0], reverse=True)
    if len(valid) < 6:
        return {"trend": "stable", "recent_3y_avg": None, "earlier_3y_avg": None}
    recent = sum(gm for _, gm in valid[:3]) / 3
    earlier = sum(gm for _, gm in valid[3:6]) / 3
    if recent > earlier + 0.01:
        trend = "improving"
    elif recent < earlier - 0.01:
        trend = "declining"
    else:
        trend = "stable"
    return {"trend": trend, "recent_3y_avg": recent, "earlier_3y_avg": earlier}


def _compute_net_debt_stats(yearly_metrics: list, current_year: int) -> dict:
    """Net debt (total_debt - cash) history over last 5 prior years + count of YoY increases in recent 3 transitions.

    Note: data_adapter exposes field 'cash' (not 'cash_and_equivalents').
    """
    valid = []
    for m in yearly_metrics:
        y = _year_int(m)
        if y is None or y >= current_year:
            continue
        td = m.get("total_debt")
        cash = m.get("cash")
        if td is None or cash is None:
            continue
        valid.append((y, td - cash))
    valid.sort(key=lambda t: t[0], reverse=True)
    if len(valid) < 5:
        return {"history_5y": None, "increases_in_3y": 0}
    history = [nd for _, nd in valid[:5]]  # index 0 = newest
    increases = 0
    # Compare newest vs older (3 transitions max): history[i] vs history[i+1]
    for i in range(min(3, len(history) - 1)):
        if history[i] > history[i + 1]:
            increases += 1
    return {"history_5y": history, "increases_in_3y": increases}


def _compute_interest_coverage_4y_avg(yearly_metrics: list, current_year: int) -> "float | None":
    """4y average of interest_coverage (excluding current calendar year)."""
    valid = []
    for m in yearly_metrics:
        y = _year_int(m)
        if y is None or y >= current_year:
            continue
        ic = m.get("interest_coverage")
        if ic is None:
            continue
        valid.append((y, ic))
    valid.sort(key=lambda t: t[0], reverse=True)
    valid = valid[:4]
    if len(valid) < 4:
        return None
    return sum(ic for _, ic in valid) / 4


def _compute_eps_cv_10y(yearly_metrics: list, current_year: int) -> dict:
    """Coefficient of variation (CV) of diluted_eps over up to 10 prior years.

    CV = stdev / |mean|. Uses population stdev (pstdev) because:
    - The 10y EPS series is the full population of observations for this period
      (not a sample drawn from a larger population)
    - Difference vs sample stdev is small (factor of sqrt(N/(N-1)) ~= 1.05 for N=10)
    - Intentional choice for descriptive measure of historical stability

    Lower CV = more stable earnings = STABLE_BUSINESS qualifier.
    """
    valid = []
    for m in yearly_metrics:
        y = _year_int(m)
        if y is None or y >= current_year:
            continue
        eps = m.get("diluted_eps")
        if eps is None:
            continue
        valid.append((y, eps))
    valid.sort(key=lambda t: t[0], reverse=True)
    valid = valid[:10]
    if len(valid) < 5:
        return {"eps_cv_10y": None, "eps_mean_10y": None}
    eps_values = [eps for _, eps in valid]
    mean = sum(eps_values) / len(eps_values)
    if mean == 0:
        return {"eps_cv_10y": None, "eps_mean_10y": 0}
    stdev = statistics.pstdev(eps_values)
    return {"eps_cv_10y": stdev / abs(mean), "eps_mean_10y": mean}


def _crisis_drop_from_bars(bars: list, pre_year: int, crisis_year: int) -> "float | None":
    """Peak-to-trough drawdown from cached monthly bars (one formula, no network, no fallback).

    drop = min(low in crisis_year) / max(high in pre_year) - 1  (negative = drawdown).
    Uses 'close' for a month only when its high/low is missing. None if either year has no data.
    """
    def _vals(year, primary, secondary):
        out = []
        for b in bars or []:
            if str(b.get("date", ""))[:4] != str(year):
                continue
            v = b.get(primary)
            if v is None:
                v = b.get(secondary)
            if v is not None:
                out.append(v)
        return out

    peaks = _vals(pre_year, "high", "close")
    troughs = _vals(crisis_year, "low", "close")
    if not peaks or not troughs:
        return None
    peak = max(peaks)
    if peak == 0:
        return None
    return float((min(troughs) - peak) / peak)


def _get_ocf_for_year(yearly_metrics: list, year: int) -> "float | None":
    for m in yearly_metrics:
        if _year_int(m) == year:
            return m.get("ocf")
    return None


def _compute_data_gaps(yearly_metrics, aggregates, dps_by_year, fy_is_complete, current_year) -> list:
    """Names of aggregates that silently fell to a default because the data was too short.

    Only flags — never changes a value. Scoring still sees the same defaults as before.
    """
    def _prior(field):
        return [m for m in yearly_metrics
                if (_year_int(m) or current_year) < current_year and m.get(field) is not None]

    gaps = []
    if len([m for m in yearly_metrics if m.get("roe") is not None]) < 6:
        gaps.append("roe_trend")            # default ROE_STABLE
    if len(_prior("gross_margin")) < 6:
        gaps.append("gm_trend")             # default "stable"
    if aggregates.get("net_debt_history_5y") is None:
        gaps.append("net_debt_increases_in_3y")  # default 0
    n_ocf = len(_prior("ocf"))
    if n_ocf < 3:
        gaps.append("ocf_positive_3y")      # default False
    if n_ocf == 0:
        gaps.append("ocf_negative_count_3y")  # default 0
    if not _prior("roe"):
        gaps.append("roe_consecutive_15plus_years")  # default 0
    if aggregates.get("avg_roe") is None:
        gaps.append("avg_roe")              # screen reads None as 0
    complete = complete_dividend_by_year(dps_by_year, fy_is_complete)
    if aggregates.get("rising_ratio") is None:
        gaps.append("rising_ratio")         # screen reads None as 0
    if aggregates.get("avg_yoy_growth") is None:
        gaps.append("avg_yoy_growth")       # screen reads None as 0
    if not complete:
        gaps.append("dividend_growth_streak")  # default 0
    if len(complete) < 10:
        gaps.append("dividend_history_short")  # <10 complete FYs
    return gaps


def _build_aggregates(yearly_metrics, dps_by_year, fy_is_complete=None, symbol=None):
    """Compute aggregates from yearly_metrics and dividend history.

    fy_is_complete: optional dict {year: bool} — every DPS aggregate (streaks, rising_ratio,
    avg_yoy_growth, dps_cagr, crisis facts) reads dividends through
    data_adapter.complete_dividend_by_year, so incomplete FYs never enter. Revenue/EPS
    CAGR excludes the current calendar year (thaifin has no is_complete flag).

    symbol: optional ticker (e.g. 'BBL') — when provided, crisis_drop is computed from
    the monthly bars cached on disk by data_adapter.ensure_crisis_bars (no network;
    no cache → None).
    """
    revenues = [m["revenue"] for m in yearly_metrics]
    eps_list = [m["diluted_eps"] for m in yearly_metrics]
    roe_list = [m["roe"] for m in yearly_metrics if m["roe"] is not None]
    nm_list = [m["net_margin"] for m in yearly_metrics if m["net_margin"] is not None]
    gm_list = [m["gross_margin"] for m in yearly_metrics if m["gross_margin"] is not None]
    om_list = [m["operating_margin"] for m in yearly_metrics if m["operating_margin"] is not None]
    fcf_list = [m["fcf"] for m in yearly_metrics if m["fcf"] is not None]

    # CAGR: exclude current calendar year (thaifin may emit partial-year row;
    # no is_complete flag exists for thaifin → use year-based filter).
    current_year = datetime.now().year

    def _year_lt_current(m):
        y = m.get("year")
        if y is None:
            return False
        try:
            return int(y) < current_year
        except (ValueError, TypeError):
            return False

    cagr_revenues = [m.get("revenue") for m in yearly_metrics if _year_lt_current(m)]
    cagr_eps_list = [m.get("diluted_eps") for m in yearly_metrics if _year_lt_current(m)]
    revenue_cagr = compute_cagr(cagr_revenues)
    eps_cagr = compute_cagr(cagr_eps_list, reject_negatives=True)
    avg_roe = sum(roe_list) / len(roe_list) if roe_list else None
    avg_net_margin = sum(nm_list) / len(nm_list) if nm_list else None
    min_roe = min(roe_list) if roe_list else None

    revenue_positive_years = sum(1 for i in range(1, len(revenues))
                                  if revenues[i] is not None and revenues[i - 1] is not None
                                  and revenues[i] > revenues[i - 1])
    total_revenue_comparisons = sum(1 for i in range(1, len(revenues))
                                     if revenues[i] is not None and revenues[i - 1] is not None)

    eps_positive_years = sum(1 for e in eps_list if e is not None and e > 0)
    fcf_positive_years = sum(1 for f in fcf_list if f > 0)

    div_streak = count_dividend_streak(dps_by_year, fy_is_complete=fy_is_complete)
    div_growth_streak = count_dividend_growth_streak(dps_by_year, fy_is_complete=fy_is_complete)

    # dps_cagr: exactly 5 complete years (L-5 → L); dps_10y_cagr likewise over 10
    dps_cagr = compute_dps_cagr(dps_by_year, fy_is_complete, years=5)
    dps_10y_cagr = compute_dps_cagr(dps_by_year, fy_is_complete, years=10)

    latest = yearly_metrics[-1] if yearly_metrics else {}

    avg_gross_margin = sum(gm_list) / len(gm_list) if gm_list else None
    avg_operating_margin = sum(om_list) / len(om_list) if om_list else None

    aggregates = {
        "revenue_cagr": revenue_cagr,
        "eps_cagr": eps_cagr,
        "dps_cagr": dps_cagr,
        "dps_10y_cagr": dps_10y_cagr,
        "avg_roe": avg_roe,
        "min_roe": min_roe,
        "avg_net_margin": avg_net_margin,
        "avg_gross_margin": avg_gross_margin,
        "avg_operating_margin": avg_operating_margin,
        "revenue_growth_years": revenue_positive_years,
        "revenue_growth_total_comparisons": total_revenue_comparisons,
        "eps_positive_years": eps_positive_years,
        "eps_total_years": len([e for e in eps_list if e is not None]),
        "fcf_positive_years": fcf_positive_years,
        "fcf_total_years": len(fcf_list),
        "dividend_streak": div_streak,
        "dividend_growth_streak": div_growth_streak,
        "years_of_data": len(yearly_metrics),
        "latest_interest_coverage": latest.get("interest_coverage"),
        "latest_ocf_ni_ratio": latest.get("ocf_ni_ratio"),
        "latest_capital_intensity": latest.get("capital_intensity"),
    }

    # --- Anchor scoring v1.0 — 21 new fields across 4 dimensions ---
    # Phase 1 dividend (3)
    aggregates["rising_ratio"] = _compute_rising_ratio(dps_by_year, fy_is_complete)
    aggregates["avg_yoy_growth"] = _compute_avg_yoy_growth(dps_by_year, fy_is_complete)
    aggregates["roe_trend"] = _compute_roe_trend(yearly_metrics)

    # Phase 2 cash flow (5)
    aggregates["ccr_avg_3y"] = _compute_ccr_avg_3y(yearly_metrics, current_year)
    ocf_stats = _compute_ocf_stats_3y(yearly_metrics, current_year)
    aggregates["ocf_negative_count_3y"] = ocf_stats["negative_count_3y"]
    aggregates["ocf_yoy_decline_pct"] = ocf_stats["yoy_decline_pct"]
    aggregates["ocf_consecutive_declining_years"] = ocf_stats["consecutive_declining"]
    aggregates["ocf_positive_3y"] = ocf_stats["positive_3y"]

    # Phase 3 moat (7)
    aggregates["roe_consecutive_15plus_years"] = _compute_roe_consecutive_15plus(
        yearly_metrics, current_year
    )
    gm_stats = _compute_gm_trend_stats(yearly_metrics, current_year)
    aggregates["gm_trend"] = gm_stats["trend"]
    aggregates["gm_recent_3y_avg"] = gm_stats["recent_3y_avg"]
    aggregates["gm_earlier_3y_avg"] = gm_stats["earlier_3y_avg"]
    aggregates["interest_coverage_4y_avg"] = _compute_interest_coverage_4y_avg(
        yearly_metrics, current_year
    )
    debt_stats = _compute_net_debt_stats(yearly_metrics, current_year)
    aggregates["net_debt_history_5y"] = debt_stats["history_5y"]
    aggregates["net_debt_increases_in_3y"] = debt_stats["increases_in_3y"]

    # Phase 4 long_hold (6)
    eps_stats = _compute_eps_cv_10y(yearly_metrics, current_year)
    aggregates["eps_cv_10y"] = eps_stats["eps_cv_10y"]
    aggregates["eps_mean_10y"] = eps_stats["eps_mean_10y"]

    # crisis_drop: one formula over the monthly bars cached on disk by data_adapter
    # (no network here). No bars → None; running twice gives the same value.
    bars = load_crisis_bars(symbol) if symbol else []
    aggregates["crisis_2011_drop_pct"] = _crisis_drop_from_bars(bars, 2010, 2011)
    aggregates["crisis_2020_drop_pct"] = _crisis_drop_from_bars(bars, 2019, 2020)

    # Dividend facts for crisis years + last complete FY (all read through complete_dividend_by_year)
    aggregates.update(dividend_crisis_facts(dps_by_year, fy_is_complete))
    aggregates["dividend_last_complete_fy"] = last_complete_fy(dps_by_year, fy_is_complete)

    aggregates["ocf_2011"] = _get_ocf_for_year(yearly_metrics, 2011)
    aggregates["ocf_2020"] = _get_ocf_for_year(yearly_metrics, 2020)

    # dps_5y_cagr alias — same value as dps_cagr (both are the true 5-complete-year CAGR)
    aggregates["dps_5y_cagr"] = aggregates.get("dps_cagr")

    aggregates["data_gaps"] = _compute_data_gaps(yearly_metrics, aggregates, dps_by_year,
                                                 fy_is_complete, current_year)

    return aggregates




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
    # Integrity guard: stock has dividend_yield > 0 (SETSMART/thaifin confirms it pays dividends)
    # but dividend_history is empty = yahoo fetch flake; don't poison the day's cache
    dy = data.get('dividend_yield')
    div_history = data.get('dividend_history') or {}
    if dy is not None and dy > 0 and not div_history:
        logger.warning("cache skip for %s: dividend_yield=%.2f%% but dividend_history empty (suspected yahoo flake)",
                       symbol, dy)
        return
    cache_dir = _cache_dir_today()
    cache_dir.mkdir(parents=True, exist_ok=True)
    p = cache_dir / f'{symbol}.json'
    try:
        p.write_text(json.dumps(data, ensure_ascii=False, default=str), encoding='utf-8')
    except Exception as e:
        logger.warning(f'cache save failed for {symbol}: {e}')


def fetch_multi_year(symbol: str) -> dict:
    """Fetch multi-year fundamentals. thaifin primary, yahooquery supplement, no fallback."""
    # Try thaifin + yahooquery supplement via adapter
    adapter_result = _adapter_fetch(symbol)

    if adapter_result is not None and "error" not in adapter_result:
        # Adapter succeeded — compute aggregates and finalize
        yearly_metrics = adapter_result["yearly_metrics"]
        dividend_history = adapter_result["dividend_history"]
        fy_is_complete = adapter_result.get("fy_is_complete")

        aggregates = _build_aggregates(yearly_metrics, dividend_history,
                                       fy_is_complete=fy_is_complete,
                                       symbol=symbol)

        # Validate
        # Build a minimal info-like dict for validate_metrics
        info_for_validate = {
            "dividendYield": adapter_result.get("dividend_yield"),
            "earningsGrowth": adapter_result.get("earnings_growth"),
            "payoutRatio": adapter_result.get("payout_ratio"),
        }
        warnings = validate_metrics(info_for_validate, yearly_metrics)

        aggregates["sector_profile"] = (adapter_result.get("sector_profile")
                                        or classify_sector_profile(adapter_result.get("sector")))
        adapter_result["aggregates"] = aggregates
        # keep the adapter's own flags (DPS_SOURCE_YAHOO / DPS_SOURCE_MISMATCH) next to validate's
        adapter_result["warnings"] = list(adapter_result.get("warnings") or []) + warnings
        adapter_result["fetched_at"] = datetime.now().isoformat()
        return adapter_result

    if adapter_result is not None and "error" in adapter_result:
        return adapter_result

    # No legacy fallback — thaifin is single source of truth for fundamentals
    return {"symbol": symbol, "delisted": True, "error": "thaifin fetch returned no data"}


def fetch_multi_year_safe(symbol: str, use_cache: bool = True) -> dict:
    """Wrap fetch_multi_year with try/except + day-scoped cache.

    Returns cached data if same-day cache hit (instant). Otherwise fetches
    + caches successful results. Failures (delisted, no price) NOT cached.
    """
    if use_cache:
        cached = _load_from_cache(symbol)
        if cached is not None:
            return cached
    try:
        result = fetch_multi_year(symbol)
    except Exception as e:
        logger.warning(f"fetch failed for {symbol}: {e}")
        return {"symbol": symbol, "delisted": True, "error": str(e)}
    if isinstance(result, dict) and "error" in result and not result.get("price"):
        err = result.get("error", "unknown")
        logger.warning(f"fetch returned error for {symbol}: {err}")
        return {"symbol": symbol, "delisted": True, "error": str(err)}
    if use_cache:
        _save_to_cache(symbol, result)
    return result


def main():
    # Read from user_data.json (new format)
    user_data = json.loads(USER_DATA.read_text(encoding="utf-8"))
    symbols = user_data.get("watchlist", [])

    print(f"Max Mahon v4 fetching {len(symbols)} stocks (multi-year, parallel)...")

    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(fetch_multi_year_safe, sym): sym for sym in symbols}
        for n, future in enumerate(as_completed(futures), 1):
            sym = futures[future]
            try:
                data = future.result()
            except Exception as e:
                print(f"  [{n}/{len(symbols)}] {sym} ERROR: {e}")
                results.append({"symbol": sym, "error": str(e)})
                continue
            # Ensure symbol field is set (defensive — for deterministic sort below)
            if not data.get("symbol"):
                data["symbol"] = sym
            results.append(data)
            if data.get("delisted"):
                print(f"  [{n}/{len(symbols)}] {sym} DELISTED/ERROR: {data.get('error', 'unknown')}")
                continue
            if "error" in data:
                print(f"  [{n}/{len(symbols)}] {sym} ERROR: {data['error']}")
                continue
            price = data.get("price") or "N/A"
            dy = data.get("dividend_yield")
            dy_str = f"{dy:.1f}%" if dy else "N/A"
            years = data["aggregates"]["years_of_data"]
            streak = data["aggregates"]["dividend_streak"]
            warns = len(data.get("warnings", []))
            warn_str = f" ⚠{warns}" if warns > 0 else ""
            print(f"  [{n}/{len(symbols)}] {sym} ฿{price} yield={dy_str} | {years}yr | streak={streak}yr{warn_str}")

    # Sort results to match original symbol order (deterministic output)
    sym_order = {s: i for i, s in enumerate(symbols)}
    results.sort(key=lambda d: sym_order.get(d.get("symbol"), 999999))

    today = datetime.now().strftime("%Y-%m-%d")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / f"snapshot_{today}.json"
    out_path.write_text(
        json.dumps(
            {"date": today, "agent": "Max Mahon v4", "stocks": results},
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    print(f"\nSaved → {out_path}")
    return out_path


if __name__ == "__main__":
    main()
