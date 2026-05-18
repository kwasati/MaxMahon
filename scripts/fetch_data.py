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


def count_dividend_growth_streak(dps_by_year, fy_is_complete=None):
    """Growth streak นับเฉพาะ FY ที่ is_complete=True เท่านั้น.

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
    for i in range(len(years) - 1):
        if dps_by_year[years[i]] > dps_by_year[years[i + 1]] and dps_by_year[years[i + 1]] > 0:
            streak += 1
        else:
            break
    return streak


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

def _compute_rising_ratio(dps_by_year: dict, fy_is_complete) -> "float | None":
    """Ratio of YoY transitions where DPS increased (complete FY only)."""
    if not dps_by_year:
        return None
    if fy_is_complete is not None:
        years = sorted(y for y in dps_by_year if fy_is_complete.get(y) is True)
    else:
        years = sorted(dps_by_year.keys())
    if len(years) < 2:
        return None
    transitions = 0
    rising = 0
    for i in range(1, len(years)):
        prev = dps_by_year[years[i - 1]]
        curr = dps_by_year[years[i]]
        if prev is not None and prev > 0 and curr is not None:
            transitions += 1
            if curr > prev:
                rising += 1
    return rising / transitions if transitions > 0 else None


def _compute_avg_yoy_growth(dps_by_year: dict, fy_is_complete) -> "float | None":
    """Arithmetic mean of YoY DPS % changes (complete FY only)."""
    if not dps_by_year:
        return None
    if fy_is_complete is not None:
        years = sorted(y for y in dps_by_year if fy_is_complete.get(y) is True)
    else:
        years = sorted(dps_by_year.keys())
    if len(years) < 2:
        return None
    growths = []
    for i in range(1, len(years)):
        prev = dps_by_year[years[i - 1]]
        curr = dps_by_year[years[i]]
        if prev is not None and prev > 0 and curr is not None:
            growths.append((curr / prev) - 1)
    return sum(growths) / len(growths) if growths else None


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


def _compute_crisis_drop(yearly_metrics: list, pre_year: int, crisis_year: int,
                         field: str = "close") -> "float | None":
    """Fallback: yearly close-to-close % change of `field` from pre_year to crisis_year.

    Less precise than monthly drawdown (misses intra-year low). Used as fallback
    when monthly yahoo fetch fails.
    """
    by_year = {}
    for m in yearly_metrics:
        y = _year_int(m)
        if y in (pre_year, crisis_year):
            by_year[y] = m
    pre = (by_year.get(pre_year) or {}).get(field)
    crisis = (by_year.get(crisis_year) or {}).get(field)
    if pre is None or crisis is None or pre == 0:
        return None
    return (crisis - pre) / pre


def _fetch_crisis_drop_monthly(symbol: str, pre_year: int, crisis_year: int) -> "float | None":
    """Compute max peak-to-trough drawdown using monthly history.

    drop = (min(low) during crisis_year) / (max(close) during pre_year) - 1

    Returns a negative value (e.g. -0.45 = 45% drawdown peak-to-trough).
    Uses yahooquery monthly history. Returns None on fetch failure or missing data
    so the caller can fall back to yearly close-to-close.
    """
    try:
        from yahooquery import Ticker
        sym_yf = symbol if symbol.endswith('.BK') else f'{symbol}.BK'
        t = Ticker(sym_yf)
        hist = t.history(
            start=f'{pre_year}-01-01',
            end=f'{crisis_year}-12-31',
            interval='1mo',
        )
        if hist is None:
            return None
        # yahooquery may return a string error message on failure
        if not hasattr(hist, 'empty') or hist.empty:
            return None
        hist = hist.reset_index()
        if 'date' not in hist.columns:
            return None
        hist['year'] = pd.to_datetime(hist['date']).dt.year
        pre_data = hist[hist['year'] == pre_year]
        crisis_data = hist[hist['year'] == crisis_year]
        if pre_data.empty or crisis_data.empty:
            return None
        # Peak during pre_year: prefer 'high' if available, else 'close'
        if 'high' in pre_data.columns and pre_data['high'].notna().any():
            pre_peak = pre_data['high'].max()
        elif 'close' in pre_data.columns and pre_data['close'].notna().any():
            pre_peak = pre_data['close'].max()
        else:
            return None
        # Trough during crisis_year: prefer 'low' if available, else 'close'
        if 'low' in crisis_data.columns and crisis_data['low'].notna().any():
            crisis_trough = crisis_data['low'].min()
        elif 'close' in crisis_data.columns and crisis_data['close'].notna().any():
            crisis_trough = crisis_data['close'].min()
        else:
            return None
        if pre_peak is None or pre_peak == 0 or crisis_trough is None:
            return None
        try:
            return float((crisis_trough - pre_peak) / pre_peak)
        except (TypeError, ZeroDivisionError):
            return None
    except Exception as e:
        logger.warning(f"crisis_drop monthly fetch failed for {symbol} {pre_year}-{crisis_year}: {e}")
        return None


def _get_ocf_for_year(yearly_metrics: list, year: int) -> "float | None":
    for m in yearly_metrics:
        if _year_int(m) == year:
            return m.get("ocf")
    return None


def _build_aggregates(yearly_metrics, dps_by_year, fy_is_complete=None, symbol=None):
    """Compute aggregates from yearly_metrics and dividend history.

    fy_is_complete: optional dict {year: bool} — when provided, streak functions
    use it to exclude incomplete fiscal years. CAGR excludes current calendar
    year regardless (thaifin has no is_complete equivalent for EPS/revenue).

    symbol: optional ticker (e.g. 'BBL') — when provided, crisis_drop computation
    uses monthly yahoo history (intra-year peak-to-trough) for higher precision,
    falling back to yearly close-to-close on fetch failure.
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

    # dps_cagr from dividend_history
    dps_years = sorted([y for y in dps_by_year if dps_by_year[y] and dps_by_year[y] > 0])
    if len(dps_years) >= 2:
        first_dps = dps_by_year[dps_years[0]]
        last_dps = dps_by_year[dps_years[-1]]
        n_years = dps_years[-1] - dps_years[0]
        if first_dps > 0 and n_years > 0:
            dps_cagr = (last_dps / first_dps) ** (1 / n_years) - 1
        else:
            dps_cagr = None
    else:
        dps_cagr = None

    latest = yearly_metrics[-1] if yearly_metrics else {}

    avg_gross_margin = sum(gm_list) / len(gm_list) if gm_list else None
    avg_operating_margin = sum(om_list) / len(om_list) if om_list else None

    aggregates = {
        "revenue_cagr": revenue_cagr,
        "eps_cagr": eps_cagr,
        "dps_cagr": dps_cagr,
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

    # crisis_drop: prefer monthly intra-year peak-to-trough (more precise).
    # Falls back to yearly close-to-close when monthly fetch fails or symbol is unknown.
    crisis_2011 = None
    crisis_2020 = None
    if symbol:
        crisis_2011 = _fetch_crisis_drop_monthly(symbol, 2010, 2011)
        crisis_2020 = _fetch_crisis_drop_monthly(symbol, 2019, 2020)
    if crisis_2011 is None:
        crisis_2011 = _compute_crisis_drop(yearly_metrics, 2010, 2011, "close")
    if crisis_2020 is None:
        crisis_2020 = _compute_crisis_drop(yearly_metrics, 2019, 2020, "close")
    aggregates["crisis_2011_drop_pct"] = crisis_2011
    aggregates["crisis_2020_drop_pct"] = crisis_2020

    aggregates["ocf_2011"] = _get_ocf_for_year(yearly_metrics, 2011)
    aggregates["ocf_2020"] = _get_ocf_for_year(yearly_metrics, 2020)

    # FIX 3: dps_5y_cagr alias for spec consistency
    # Spec uses 'dps_5y_cagr' in DEFAULT_SCORING_CONFIG bonus_metrics;
    # existing data key is 'dps_cagr'. Both point to the same 5-year CAGR value.
    aggregates["dps_5y_cagr"] = aggregates.get("dps_cagr")

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

        adapter_result["aggregates"] = aggregates
        adapter_result["warnings"] = warnings
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
