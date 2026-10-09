"""Data adapter — thaifin (primary) + yahooquery (supplement).

thaifin provides 10+ years of Thai stock financials.
yahooquery supplements with realtime price, 52w range, forward PE, payout ratio, etc.

Public API:
    normalize_symbol(raw) → (tf_sym, yf_sym)
    fetch_from_thaifin(symbol) → dict | None
    fetch_yahoo_supplement(symbol) → dict
    fetch_fundamentals(symbol) → dict | None  (combined thaifin + yahooquery)
"""

import json
import logging
import math
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent

# set.or.th official dividend adapter (Phase 2 — set.or.th primary, yahoo fallback).
# Playwright may not be installed in some envs → log warning + fallback to yahoo.
try:
    from set_official_adapter import dps_by_fiscal_year as _set_dps_by_fy, fy_is_complete_by_year as _set_fy_complete
    _SET_OFFICIAL_AVAILABLE = True
except ImportError as e:
    logger.warning(f"set_official_adapter not available (Playwright?): {e}; will use yahoo for DPS")
    _SET_OFFICIAL_AVAILABLE = False


# Cache for holding mcap lookups (symbol → int | None). Per-process memoization.
_HOLDING_MCAP_CACHE: dict[str, "int | None"] = {}


def _holding_mcap(sym: str) -> "int | None":
    if sym in _HOLDING_MCAP_CACHE:
        return _HOLDING_MCAP_CACHE[sym]
    v = None
    # Try thaifin first (primary source for Thai stocks)
    try:
        from thaifin import Stock
        tf_sym = sym.replace(".BK", "")
        tf_stock = Stock(tf_sym)
        df = tf_stock.yearly_dataframe
        if df is not None and not df.empty:
            latest_mkt_cap = _safe(df.iloc[-1].get("mkt_cap"))
            if latest_mkt_cap is not None and latest_mkt_cap > 0:
                v = int(latest_mkt_cap)
    except Exception:
        pass
    # Fallback to yahooquery (for non-Thai holdings or when thaifin fails)
    if v is None:
        try:
            from yahooquery import Ticker
            tk = Ticker(sym)
            px = tk.price.get(sym, {}) if isinstance(tk.price, dict) else {}
            sd = tk.summary_detail.get(sym, {}) if isinstance(tk.summary_detail, dict) else {}
            yq_v = None
            if isinstance(sd, dict):
                yq_v = sd.get("marketCap")
            if yq_v is None and isinstance(px, dict):
                yq_v = px.get("marketCap")
            if yq_v:
                v = int(yq_v)
        except Exception:
            pass
    _HOLDING_MCAP_CACHE[sym] = v
    return v


def normalize_symbol(raw: str) -> tuple[str, str]:
    """Normalize symbol: 'LH' or 'LH.BK' → ('LH', 'LH.BK')."""
    base = raw.replace(".BK", "")
    return (base, f"{base}.BK")


def _to_yf_symbol(symbol: str) -> str:
    """Normalize symbol for Yahoo (.BK suffix): 'PTT' or 'PTT.BK' → 'PTT.BK'."""
    _, yf_sym = normalize_symbol(symbol)
    return yf_sym


def _to_tf_symbol(symbol: str) -> str:
    """Normalize symbol for thaifin: 'PTT.BK' or 'PTT' → 'PTT'."""
    tf_sym, _ = normalize_symbol(symbol)
    return tf_sym


def _safe(val):
    """Return None for NaN/inf, else float."""
    if val is None:
        return None
    try:
        f = float(val)
        if pd.isna(f) or not math.isfinite(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


def _safe_pct(val):
    """Convert thaifin percentage (e.g. 15.0) → decimal (0.15). None-safe."""
    f = _safe(val)
    if f is None:
        return None
    return f / 100.0


def _safe_div(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


def _fetch_thaifin(symbol: str) -> dict | None:
    """Fetch data from thaifin. Returns dict or None on failure."""
    try:
        from thaifin import Stock
        tf_sym = _to_tf_symbol(symbol)
        stock = Stock(tf_sym)
        df = stock.yearly_dataframe

        if df is None or df.empty:
            logger.warning("thaifin: empty data for %s", tf_sym)
            return None

        # Company info
        info = {
            "name": getattr(stock, "company_name", tf_sym),
            "sector": getattr(stock, "sector", "N/A"),
            "industry": getattr(stock, "industry", "N/A"),
        }

        # Build yearly_metrics from dataframe
        yearly_metrics = []
        dividend_yields = {}  # year → yield percentage
        closes = {}  # year → close price

        for year in df.index:
            # Index can be Period or int
            year_int = year.year if hasattr(year, 'year') else int(year)
            year_str = str(year_int)

            revenue = _safe(df.loc[year].get("revenue"))
            gross_profit = _safe(df.loc[year].get("gross_profit"))
            net_income = _safe(df.loc[year].get("net_profit"))
            diluted_eps = _safe(df.loc[year].get("earning_per_share"))
            sga = _safe(df.loc[year].get("sga"))
            equity = _safe(df.loc[year].get("equity"))
            total_debt = _safe(df.loc[year].get("total_debt"))
            total_assets = _safe(df.loc[year].get("asset"))
            ocf = _safe(df.loc[year].get("operating_activities"))
            investing = _safe(df.loc[year].get("investing_activities"))
            close = _safe(df.loc[year].get("close"))
            mkt_cap = _safe(df.loc[year].get("mkt_cap"))
            dy = _safe(df.loc[year].get("dividend_yield"))
            bvps = _safe(df.loc[year].get("book_value_per_share"))
            da = _safe(df.loc[year].get("da"))

            # Store for later use
            if dy is not None:
                dividend_yields[year_int] = dy  # percentage
            if close is not None:
                closes[year_int] = close

            # Skip rows with no meaningful data
            if revenue is None and net_income is None and diluted_eps is None:
                continue

            # Computed fields
            fcf = (ocf + investing) if ocf is not None and investing is not None else None
            roe = _safe_pct(df.loc[year].get("roe"))
            gross_margin = _safe_pct(df.loc[year].get("gpm"))
            net_margin = _safe_pct(df.loc[year].get("npm"))
            sga_ratio = _safe_pct(df.loc[year].get("sga_per_revenue"))
            de_ratio = _safe(df.loc[year].get("debt_to_equity"))  # already ratio

            # Operating income: revenue - cost of goods - sga (approximate)
            operating_income = None
            if gross_profit is not None and sga is not None:
                operating_income = gross_profit - sga
            elif revenue is not None and gross_margin is not None and sga is not None:
                operating_income = revenue * gross_margin - sga

            operating_margin = _safe_div(operating_income, revenue)

            # EBITDA: approximate from ev_per_ebit_da if available, else net_income + da
            ebitda = None
            if net_income is not None and da is not None:
                ebitda = net_income + da

            # Interest expense: not directly available, skip
            interest_expense = None

            # Current ratio: not in thaifin yearly data
            current_ratio = None

            # Interest coverage
            interest_coverage = None  # no interest expense data

            # OCF/NI ratio
            ocf_ni_ratio = _safe_div(ocf, net_income) if net_income and net_income > 0 else None

            # Capital intensity
            capex_abs = abs(investing) if investing is not None else None
            capital_intensity = _safe_div(capex_abs, ocf) if ocf and ocf > 0 else None

            # Payout ratio per year — thaifin doesn't provide directly; compute
            payout_ratio_year = None
            if dy is not None and close is not None and diluted_eps is not None and diluted_eps > 0:
                # dy is percentage (e.g. 5.2), close is THB, diluted_eps is THB
                dps_approx = (dy / 100.0) * close  # THB
                payout_ratio_year = dps_approx / diluted_eps  # decimal (0-1+)

            # Additional thaifin columns exposed (previously unused)
            cash_val = _safe(df.loc[year].get("cash"))
            roa_year = _safe_pct(df.loc[year].get("roa"))
            revenue_yoy = _safe_pct(df.loc[year].get("revenue_yoy"))
            net_profit_yoy = _safe_pct(df.loc[year].get("net_profit_yoy"))
            eps_yoy = _safe_pct(df.loc[year].get("earning_per_share_yoy"))
            cash_cycle = _safe(df.loc[year].get("cash_cycle"))
            financing_activities = _safe(df.loc[year].get("financing_activities"))
            ev_per_ebit_da = _safe(df.loc[year].get("ev_per_ebit_da"))

            yearly_metrics.append({
                "year": year_str,
                "revenue": revenue,
                "gross_profit": gross_profit,
                "operating_income": operating_income,
                "net_income": net_income,
                "ebitda": ebitda,
                "interest_expense": interest_expense,
                "diluted_eps": diluted_eps,
                "sga": sga,
                "equity": equity,
                "total_debt": total_debt,
                "total_assets": total_assets,
                "ocf": ocf,
                "fcf": fcf,
                "capex": investing,  # negative = spending
                "dividends_paid": None,  # not in thaifin
                "roe": roe,
                "gross_margin": gross_margin,
                "net_margin": net_margin,
                "operating_margin": operating_margin,
                "sga_ratio": sga_ratio,
                "de_ratio": de_ratio,
                "current_ratio": current_ratio,
                "interest_coverage": interest_coverage,
                "ocf_ni_ratio": ocf_ni_ratio,
                "capital_intensity": capital_intensity,
                "close": close,
                "dividend_yield": dy,
                "mkt_cap": mkt_cap,
                "bvps": bvps,
                "payout_ratio": payout_ratio_year,
                "cash": cash_val,
                "roa_year": roa_year,
                "revenue_yoy": revenue_yoy,
                "net_profit_yoy": net_profit_yoy,
                "eps_yoy": eps_yoy,
                "cash_cycle": cash_cycle,
                "financing_activities": financing_activities,
                "ev_per_ebit_da": ev_per_ebit_da,
            })

        yearly_metrics.sort(key=lambda x: x["year"])

        # Latest year snapshot for top-level fields
        latest_idx = max(df.index) if len(df.index) > 0 else None
        latest_row = df.loc[latest_idx] if latest_idx is not None else {}
        latest_year = latest_idx.year if hasattr(latest_idx, 'year') else (int(latest_idx) if latest_idx is not None else None)

        # PE ratio from thaifin
        pe_ratio = _safe(latest_row.get("price_earning_ratio")) if latest_year else None
        pb_ratio = _safe(latest_row.get("price_book_value")) if latest_year else None

        # Dividend yield (latest year, percentage)
        latest_dy = _safe(latest_row.get("dividend_yield")) if latest_year else None

        # Five year avg yield from thaifin
        current_year = datetime.now().year
        recent_years = sorted([y for y in dividend_yields.keys()
                               if y >= current_year - 5 and y < current_year])
        five_year_yields = [dividend_yields[y] for y in recent_years if dividend_yields[y] is not None]
        five_year_avg_yield = (sum(five_year_yields) / len(five_year_yields)) if five_year_yields else None

        # EPS trailing from latest year
        eps_trailing = _safe(latest_row.get("earning_per_share")) if latest_year else None

        # Revenue/earnings from latest
        latest_revenue = _safe(latest_row.get("revenue")) if latest_year else None
        latest_net_profit = _safe(latest_row.get("net_profit")) if latest_year else None

        # ROE/ROA from latest (decimal)
        latest_roe = _safe_pct(latest_row.get("roe")) if latest_year else None
        latest_roa = _safe_pct(latest_row.get("roa")) if latest_year else None

        # D/E from latest — thaifin is ratio, downstream expects percentage (*100)
        latest_de = _safe(latest_row.get("debt_to_equity"))
        de_for_output = latest_de * 100 if latest_de is not None else None

        # Margins from latest (decimal)
        latest_npm = _safe_pct(latest_row.get("npm")) if latest_year else None
        latest_gpm = _safe_pct(latest_row.get("gpm")) if latest_year else None

        # OCF from latest
        latest_ocf = _safe(latest_row.get("operating_activities")) if latest_year else None
        latest_investing = _safe(latest_row.get("investing_activities")) if latest_year else None
        latest_fcf = (latest_ocf + latest_investing) if latest_ocf is not None and latest_investing is not None else None

        # Market cap from latest
        latest_mkt_cap = _safe(latest_row.get("mkt_cap")) if latest_year else None

        # Revenue/earnings growth YoY from latest
        revenue_growth = _safe_pct(latest_row.get("revenue_yoy")) if latest_year else None
        earnings_growth = _safe_pct(latest_row.get("net_profit_yoy")) if latest_year else None

        # Additional latest-year values (mirroring new yearly_metrics fields)
        latest_cash = _safe(latest_row.get("cash")) if latest_year else None
        latest_roa_year = _safe_pct(latest_row.get("roa")) if latest_year else None
        latest_revenue_yoy = _safe_pct(latest_row.get("revenue_yoy")) if latest_year else None
        latest_net_profit_yoy = _safe_pct(latest_row.get("net_profit_yoy")) if latest_year else None
        latest_eps_yoy = _safe_pct(latest_row.get("earning_per_share_yoy")) if latest_year else None
        latest_cash_cycle = _safe(latest_row.get("cash_cycle")) if latest_year else None
        latest_financing_activities = _safe(latest_row.get("financing_activities")) if latest_year else None
        latest_ev_per_ebit_da = _safe(latest_row.get("ev_per_ebit_da")) if latest_year else None

        return {
            "info": info,
            "yearly_metrics": yearly_metrics,
            "snapshot": {
                "pe_ratio": pe_ratio,
                "pb_ratio": pb_ratio,
                "dividend_yield": latest_dy,  # percentage
                "five_year_avg_yield": five_year_avg_yield,  # percentage
                "eps_trailing": eps_trailing,
                "revenue": latest_revenue,
                "revenue_growth": revenue_growth,
                "earnings_growth": earnings_growth,
                "profit_margin": latest_npm,
                "gross_margins": latest_gpm,
                "operating_margins": None,  # not directly available
                "roe": latest_roe,
                "roa": latest_roa,
                "debt_to_equity": de_for_output,  # percentage for downstream schema compat
                "current_ratio": None,
                "free_cashflow": latest_fcf,
                "operating_cashflow": latest_ocf,
                "market_cap": latest_mkt_cap,
                "cash": latest_cash,
                "roa_year": latest_roa_year,
                "revenue_yoy": latest_revenue_yoy,
                "net_profit_yoy": latest_net_profit_yoy,
                "eps_yoy": latest_eps_yoy,
                "cash_cycle": latest_cash_cycle,
                "financing_activities": latest_financing_activities,
                "ev_per_ebit_da": latest_ev_per_ebit_da,
            },
        }

    except Exception as e:
        logger.warning("thaifin failed for %s: %s", symbol, e)
        return None


def _attribute_dividends_to_fiscal_years(divs) -> dict:
    """Group dividends by fiscal year per SET methodology.

    SET DIY uses 'latest annual operating period' which = fiscal year.
    For Thai stocks (FY = calendar year):
      - ex-date Jan-Jun of year N+1 → final of FY N
      - ex-date Jul-Dec of year N → interim of FY N

    Args:
        divs: pandas Series with timestamp index, DPS values

    Returns:
        {
            'by_fy': {fy_year: total_dps},
            'is_complete': {fy_year: bool},  # True if both interim+final detected, or single payment + no recent payment expected
            'events_per_fy': {fy_year: [(date, amount, period), ...]},  # for debug
        }

    Example:
        >>> # BBL events: Sep 2025=2.0, Apr 2026=10.0
        >>> result = _attribute_dividends_to_fiscal_years(divs)
        >>> result['by_fy'][2025]
        12.0
    """
    if divs is None or (hasattr(divs, 'empty') and divs.empty):
        return {'by_fy': {}, 'is_complete': {}, 'events_per_fy': {}}

    by_fy = {}
    events_per_fy = {}
    for idx, val in divs.items():
        try:
            ts = idx if hasattr(idx, 'month') else None
            if ts is None:
                continue
            month = ts.month
            cal_year = ts.year
            amount = float(val)
            if month <= 6:
                fy = cal_year - 1  # H1 next year = final of last FY
                period = 'final'
            else:
                fy = cal_year       # H2 same year = interim of this FY
                period = 'interim'
            by_fy[fy] = by_fy.get(fy, 0) + round(amount, 4)
            events_per_fy.setdefault(fy, []).append((ts, amount, period))
        except (ValueError, TypeError, AttributeError):
            continue

    # Detect completeness: adaptive per company's typical pay frequency
    # 1. Count events per FY for older FYs (skip latest 1 — may still be in-progress)
    # 2. Find mode (most common count) → typical_count for this company
    # 3. FY complete = event count >= typical_count
    sorted_fys = sorted(by_fy.keys())
    is_complete = {}
    typical_count = 2  # default semi-annual (common Thai pattern)
    if len(sorted_fys) >= 2:
        # Use older FYs (exclude latest) to detect pattern
        older_counts = [len(events_per_fy.get(fy, [])) for fy in sorted_fys[:-1]]
        if older_counts:
            from collections import Counter
            typical_count = Counter(older_counts).most_common(1)[0][0]
            if typical_count < 1:
                typical_count = 1  # safety floor

    for fy in sorted_fys:
        actual_count = len(events_per_fy.get(fy, []))
        is_complete[fy] = actual_count >= typical_count

    return {'by_fy': by_fy, 'is_complete': is_complete, 'events_per_fy': events_per_fy, 'typical_count': typical_count}


# --- Disk caches for yahoo data (so a re-run gives the same numbers) ---
YAHOO_DIV_CACHE_DIR = ROOT / "data" / "yahoo_dividend_cache"
YAHOO_DIV_CACHE_TTL_DAYS = 7
PRICE_HISTORY_DIR = ROOT / "data" / "price_history"
CRISIS_BARS_START = "2010-01-01"
CRISIS_BARS_END = "2020-12-31"


def _atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def _read_yahoo_div_cache(yq_sym: str, max_age_days: int = YAHOO_DIV_CACHE_TTL_DAYS):
    """Return yahoo dividend Series from disk cache, or None if missing/stale/corrupt."""
    p = YAHOO_DIV_CACHE_DIR / f"{yq_sym}.json"
    if not p.exists():
        return None
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
        fetched_at = datetime.fromisoformat(payload["fetched_at"])
        if (datetime.now() - fetched_at).total_seconds() >= max_age_days * 86400:
            return None
        events = payload["events"]
        if not events:
            return None
        idx = pd.to_datetime([e[0] for e in events])
        return pd.Series([float(e[1]) for e in events], index=idx, name="dividends")
    except (OSError, ValueError, KeyError, TypeError, IndexError):
        return None


def _write_yahoo_div_cache(yq_sym: str, divs) -> None:
    try:
        events = [[str(idx)[:10], float(val)] for idx, val in divs.items()]
        _atomic_write_json(
            YAHOO_DIV_CACHE_DIR / f"{yq_sym}.json",
            {"symbol": yq_sym, "fetched_at": datetime.now().isoformat(), "events": events},
        )
    except Exception as e:  # cache is best-effort
        logger.warning("yahoo dividend cache write failed for %s: %s", yq_sym, e)


def _crisis_bars_path(symbol: str) -> Path:
    sym = symbol.upper()
    if not sym.endswith(".BK"):
        sym += ".BK"
    return PRICE_HISTORY_DIR / f"{sym}_monthly_crisis.json"


def load_crisis_bars(symbol: str) -> list:
    """Read cached monthly bars [{date, high, low, close}] 2010-2020. No network. [] if absent."""
    p = _crisis_bars_path(symbol)
    if not p.exists():
        return []
    try:
        bars = json.loads(p.read_text(encoding="utf-8")).get("bars") or []
        return bars if isinstance(bars, list) else []
    except (OSError, ValueError, AttributeError):
        return []


def ensure_crisis_bars(symbol: str) -> list:
    """Return cached monthly bars, fetching from yahoo once if the cache is absent.

    Past prices never change, so the cache has no TTL. A failed fetch writes
    nothing (next run retries) and returns [].
    """
    bars = load_crisis_bars(symbol)
    if bars:
        return bars
    try:
        from yahooquery import Ticker
        yq_sym = _to_yf_symbol(symbol)
        hist = Ticker(yq_sym).history(start=CRISIS_BARS_START, end=CRISIS_BARS_END, interval="1mo")
        if hist is None or not hasattr(hist, "empty") or hist.empty:
            return []
        hist = hist.reset_index()
        if "date" not in hist.columns:
            return []
        bars = []
        for _, row in hist.iterrows():
            def _num(k):
                v = row.get(k)
                return None if v is None or pd.isna(v) else float(v)
            bars.append({"date": str(row["date"])[:10], "high": _num("high"),
                         "low": _num("low"), "close": _num("close")})
        if bars:
            _atomic_write_json(_crisis_bars_path(symbol),
                               {"symbol": yq_sym, "fetched_at": datetime.now().isoformat(), "bars": bars})
        return bars
    except Exception as e:
        logger.warning("crisis bars fetch failed for %s: %s", symbol, e)
        return []


def _yq_cache_path(symbol: str, suffix: str) -> Path:
    sym = symbol.upper()
    if not sym.endswith(".BK"):
        sym += ".BK"
    return PRICE_HISTORY_DIR / f"{sym}_{suffix}.json"


def load_yearend_closes(symbol: str) -> dict:
    """Cached {year: last close of December} (yahoo, split-adjusted). No network. {} if absent."""
    p = _yq_cache_path(symbol, "yearend")
    if not p.exists():
        return {}
    try:
        raw = json.loads(p.read_text(encoding="utf-8")).get("closes") or {}
        return {int(k): float(v) for k, v in raw.items() if v is not None}
    except (OSError, ValueError, AttributeError, TypeError):
        return {}


def ensure_yearend_closes(symbol: str) -> dict:
    """{year: December close} for every complete calendar year; fetched once from yahoo.

    Past closes never change, so the cache only refreshes when it lacks last year's close.
    A failed fetch writes nothing and returns whatever the cache already had.
    """
    cached = load_yearend_closes(symbol)
    if cached and max(cached) >= datetime.now().year - 1:
        return cached
    try:
        from yahooquery import Ticker
        yq_sym = _to_yf_symbol(symbol)
        hist = Ticker(yq_sym).history(start="2000-01-01", interval="1mo")
        if hist is None or not hasattr(hist, "empty") or hist.empty:
            return cached
        hist = hist.reset_index()
        if "date" not in hist.columns or "close" not in hist.columns:
            return cached
        closes = {}
        for _, row in hist.iterrows():
            d = str(row["date"])
            if d[5:7] == "12" and not pd.isna(row["close"]) and int(d[:4]) < datetime.now().year:
                closes[int(d[:4])] = float(row["close"])
        if closes:
            _atomic_write_json(_yq_cache_path(symbol, "yearend"),
                               {"symbol": yq_sym, "fetched_at": datetime.now().isoformat(),
                                "closes": {str(k): v for k, v in sorted(closes.items())}})
            return closes
    except Exception as e:
        logger.warning("year-end closes fetch failed for %s: %s", symbol, e)
    return cached


def ensure_interest_bearing_debt(symbol: str) -> dict:
    """{year: {'total_debt', 'equity'}} interest-bearing debt (yahoo TotalDebt) per FY, ~4y. {} if none.

    Cached 7 days like the yahoo dividend cache; a failed fetch returns the stale cache or {}.
    """
    p = _yq_cache_path(symbol, "debt")
    stale = {}
    if p.exists():
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
            stale = {int(k): v for k, v in (payload.get("years") or {}).items()}
            age = datetime.now() - datetime.fromisoformat(payload["fetched_at"])
            if age.total_seconds() < YAHOO_DIV_CACHE_TTL_DAYS * 86400:
                return stale
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            stale = {}
    try:
        from yahooquery import Ticker
        bs = Ticker(_to_yf_symbol(symbol)).balance_sheet(frequency="a")
        if bs is None or not hasattr(bs, "empty") or bs.empty or "TotalDebt" not in bs.columns:
            return stale
        years = {}
        for _, row in bs.reset_index().iterrows():
            debt = row.get("TotalDebt")
            if debt is None or pd.isna(debt):
                continue
            eq = row.get("StockholdersEquity")
            years[int(str(row["asOfDate"])[:4])] = {
                "total_debt": float(debt),
                "equity": None if eq is None or pd.isna(eq) else float(eq),
            }
        if years:
            _atomic_write_json(p, {"fetched_at": datetime.now().isoformat(),
                                   "years": {str(k): v for k, v in sorted(years.items())}})
            return years
    except Exception as e:
        logger.warning("interest-bearing debt fetch failed for %s: %s", symbol, e)
    return stale


# --- Dividend history: merge set.or.th + yahoo, completeness, crisis facts ---
DPS_MISMATCH_REL_TOL = 0.10   # |set - yahoo| / max(set, yahoo) above this → flag
DPS_MISMATCH_ABS_TOL = 0.005  # ignore sub-satang rounding noise

BANK_PROFILE_SECTORS = {"Banking", "Finance & Securities", "Insurance"}
REIT_PROFILE_SECTORS = {"Property Fund & REIT", "Property Fund & REITs"}


def classify_sector_profile(sector) -> str:
    """Label only (no scoring change): 'bank' | 'reit' | 'general'."""
    if sector in BANK_PROFILE_SECTORS:
        return "bank"
    if sector in REIT_PROFILE_SECTORS:
        return "reit"
    return "general"


def _int_keys(d) -> dict:
    out = {}
    for k, v in (d or {}).items():
        try:
            out[int(k)] = v
        except (TypeError, ValueError):
            continue
    return out


def complete_dividend_by_year(dps_by_year, fy_is_complete=None, current_year=None) -> dict:
    """The one place that decides which FYs count: {FY: DPS} for COMPLETE years only.

    A year is complete when fy_is_complete[fy] is True; with no flags given
    (legacy callers) every FY before the current calendar year is complete.
    Every year-over-year dividend aggregate must read through this function.
    """
    dps = _int_keys(dps_by_year)
    if fy_is_complete is not None:
        flags = _int_keys(fy_is_complete)
        return {y: v for y, v in dps.items() if flags.get(y) is True and v is not None}
    cy = current_year or datetime.now().year
    return {y: v for y, v in dps.items() if y < cy and v is not None}


def last_complete_fy(dps_by_year, fy_is_complete=None, current_year=None):
    complete = complete_dividend_by_year(dps_by_year, fy_is_complete, current_year)
    return max(complete) if complete else None


def merge_dividend_sources(set_by_fy: dict, yahoo_by_fy: dict) -> dict:
    """Merge DPS-by-FY from set.or.th (raw, ~5y window) and yahoo (split-adjusted, long).

    - FY after the first FY of the set window → set.or.th (full year).
    - first FY of the window (interim fell outside it) and older → yahoo.
      If yahoo lacks the first window FY, keep set's partial value, source 'set_partial'.
    - Overlapping years are compared; a difference above tolerance is NOT merged
      silently: it is returned in `mismatches` {fy: {'set': x, 'yahoo': y}}.
    Returns {'history', 'source_by_fy', 'mismatches', 'overlap_years', 'overlap_matches'}.
    """
    set_d = {int(k): float(v) for k, v in (set_by_fy or {}).items() if v is not None}
    yh_d = {int(k): float(v) for k, v in (yahoo_by_fy or {}).items() if v is not None}
    history, source, mismatches = {}, {}, {}
    overlap_years = overlap_matches = 0

    def _differs(a, b):
        return abs(a - b) > DPS_MISMATCH_ABS_TOL and abs(a - b) / max(abs(a), abs(b)) > DPS_MISMATCH_REL_TOL

    if not set_d:
        return {"history": dict(sorted(yh_d.items())), "source_by_fy": {y: "yahoo" for y in sorted(yh_d)},
                "mismatches": {}, "overlap_years": 0, "overlap_matches": 0}

    f0 = min(set_d)
    for fy in sorted(set(set_d) | set(yh_d)):
        s_val, y_val = set_d.get(fy), yh_d.get(fy)
        if fy > f0:
            if s_val is not None:
                history[fy], source[fy] = s_val, "set"
                if y_val is not None:
                    overlap_years += 1
                    if _differs(s_val, y_val):
                        mismatches[fy] = {"set": s_val, "yahoo": y_val}
                    else:
                        overlap_matches += 1
            elif y_val is not None and y_val > 0:
                # inside the set window but set has no payment: not merged, flagged
                mismatches[fy] = {"set": None, "yahoo": y_val}
        elif y_val is not None:
            history[fy], source[fy] = y_val, "yahoo"
            if fy == f0 and s_val is not None:
                overlap_years += 1
                # set only has part of FY0, so yahoo must be >= set; yahoo below set is a conflict
                if y_val < s_val and _differs(s_val, y_val):
                    mismatches[fy] = {"set": s_val, "yahoo": y_val}
                else:
                    overlap_matches += 1
        elif s_val is not None:
            history[fy], source[fy] = s_val, "set_partial"
    return {"history": history, "source_by_fy": source, "mismatches": mismatches,
            "overlap_years": overlap_years, "overlap_matches": overlap_matches}


def dividend_crisis_facts(dps_by_year, fy_is_complete=None, current_year=None) -> dict:
    """DPS change vs previous FY in 2008/2009/2011/2020 + years to regain the pre-cut level.

    `dps_change_<Y>` is a fraction (-0.25 = -25%), None if either year is missing.
    `dps_recovery_years_<Y>`: 0 if no cut, k = first later complete FY (Y+k) whose DPS
    >= DPS(Y-1), None if not yet recovered / no data.
    """
    complete = complete_dividend_by_year(dps_by_year, fy_is_complete, current_year)
    facts = {}
    for y in (2008, 2009, 2011, 2020):
        pre, cur = complete.get(y - 1), complete.get(y)
        change = recovery = None
        if pre is not None and pre > 0 and cur is not None:
            change = cur / pre - 1
            if cur >= pre:
                recovery = 0
            else:
                for later in sorted(k for k in complete if k > y):
                    if complete[later] >= pre:
                        recovery = later - y
                        break
        facts[f"dps_change_{y}"] = change
        facts[f"dps_recovery_years_{y}"] = recovery
    return facts


def _fetch_yahoo_supplement(symbol: str, snapshot: bool = True) -> dict:
    """Fetch supplementary data from yahooquery (price, 52w, forward PE, etc.).

    Also fetches: dividends history (DPS by year), capex, operating income,
    interest expense — used to supplement thaifin data.

    Args:
        symbol: stock symbol (with or without .BK suffix)
        snapshot: when True (default), populate info dict with realtime snapshot
            fields (price, PE, PBV, marketCap, dividendYield) and early-return on
            empty info. When False (SETSMART has primary snapshot), skip the
            currentPrice gate so dividends/52w/capex/IE still fetch even if
            yahoo summary endpoints flake — info dict still populated as fallback
            for fields SETSMART doesn't provide (52w range, payoutRatio, etc.).
    """
    try:
        from yahooquery import Ticker
        yq_sym = _to_yf_symbol(symbol)
        tk = Ticker(yq_sym)

        # Build info dict from multiple yahooquery endpoints — maintain legacy schema keys
        sd = tk.summary_detail.get(yq_sym, {}) if isinstance(tk.summary_detail, dict) else {}
        px = tk.price.get(yq_sym, {}) if isinstance(tk.price, dict) else {}
        ks = tk.key_stats.get(yq_sym, {}) if isinstance(tk.key_stats, dict) else {}
        fd = tk.financial_data.get(yq_sym, {}) if isinstance(tk.financial_data, dict) else {}

        # yahooquery returns strings like "Quote not found" when symbol fails — normalize to dict
        if not isinstance(sd, dict):
            sd = {}
        if not isinstance(px, dict):
            px = {}
        if not isinstance(ks, dict):
            ks = {}
        if not isinstance(fd, dict):
            fd = {}

        info = {
            "currentPrice": px.get("regularMarketPrice") or fd.get("currentPrice"),
            "regularMarketPrice": px.get("regularMarketPrice"),
            "marketCap": sd.get("marketCap") or px.get("marketCap"),
            "trailingPE": sd.get("trailingPE"),
            "forwardPE": sd.get("forwardPE") or ks.get("forwardPE"),
            "priceToBook": ks.get("priceToBook"),
            "dividendRate": sd.get("dividendRate"),
            "trailingAnnualDividendRate": sd.get("trailingAnnualDividendRate"),
            "payoutRatio": sd.get("payoutRatio"),
            "fiveYearAvgDividendYield": sd.get("fiveYearAvgDividendYield"),
            "fiftyTwoWeekHigh": sd.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekLow": sd.get("fiftyTwoWeekLow"),
            "fiftyDayAverage": sd.get("fiftyDayAverage"),
            "twoHundredDayAverage": sd.get("twoHundredDayAverage"),
            "freeCashflow": ks.get("freeCashflow") or fd.get("freeCashflow"),
            "operatingCashflow": fd.get("operatingCashflow"),
            "trailingEps": ks.get("trailingEps"),
            "forwardEps": ks.get("forwardEps"),
            "dividendYield": sd.get("dividendYield"),
            "revenueGrowth": fd.get("revenueGrowth"),
            "earningsGrowth": fd.get("earningsGrowth"),
            "profitMargins": fd.get("profitMargins"),
            "grossMargins": fd.get("grossMargins"),
            "operatingMargins": fd.get("operatingMargins"),
            "returnOnEquity": fd.get("returnOnEquity"),
            "returnOnAssets": fd.get("returnOnAssets"),
            "debtToEquity": fd.get("debtToEquity"),
            "currentRatio": fd.get("currentRatio"),
            "totalRevenue": fd.get("totalRevenue"),
            "shortName": px.get("shortName"),
            "currency": px.get("currency"),
        }

        # When snapshot=True (legacy default), early-return if yahoo has no price.
        # When snapshot=False (SETSMART warm), continue to fetch dividends/capex/IE
        # even if summary endpoints flake — those are the irreplaceable bits.
        if snapshot and info.get("currentPrice") is None:
            return {"info": info, "divs": None, "error": "near-empty info (no price)"}

        # Dividends — yahooquery dividend_history returns DataFrame
        divs = None
        recent_divs = []
        dps_by_year = {}
        dps_by_fiscal_year = {}
        fy_is_complete = {}
        # Dividends — yahooquery dividend_history returns DataFrame
        # Wrapped in retry loop: yahoo dividend_history flake in parallel context
        # silently returned empty before, poisoning the day's cache.
        DIV_RETRY_ATTEMPTS = 3
        DIV_RETRY_DELAYS = [0.5, 1.0]  # seconds, applied between attempts (last has no follow-up)
        _cached_divs = _read_yahoo_div_cache(yq_sym)  # disk cache → re-runs give identical DPS
        for attempt in range(DIV_RETRY_ATTEMPTS):
            try:
                if _cached_divs is not None:
                    divs_df = _cached_divs.to_frame("dividends")
                else:
                    divs_df = tk.dividend_history(start="2000-01-01")
                if hasattr(divs_df, 'shape') and not divs_df.empty:
                    if hasattr(divs_df.index, 'get_level_values'):
                        levels = divs_df.index.get_level_values(0)
                        if yq_sym in levels:
                            divs_df = divs_df.xs(yq_sym, level=0)
                    if 'dividends' in divs_df.columns:
                        divs = divs_df['dividends']
                    else:
                        divs = divs_df.iloc[:, 0]
                    if _cached_divs is None and len(divs) > 0:
                        _write_yahoo_div_cache(yq_sym, divs)
                    recent_divs = divs.tail(8).tolist() if len(divs) > 0 else []
                    for idx, val in divs.items():
                        try:
                            y = idx.year if hasattr(idx, 'year') else int(str(idx)[:4])
                            dps_by_year[y] = dps_by_year.get(y, 0) + round(float(val), 4)
                        except (ValueError, TypeError):
                            continue
                    fy_result = _attribute_dividends_to_fiscal_years(divs)
                    dps_by_fiscal_year = fy_result['by_fy']
                    fy_is_complete = fy_result['is_complete']
                    break  # success - exit retry loop
                else:
                    # empty result - log + retry
                    if attempt < DIV_RETRY_ATTEMPTS - 1:
                        logger.warning("yahoo dividend_history empty for %s (attempt %d/%d), retrying",
                                       yq_sym, attempt + 1, DIV_RETRY_ATTEMPTS)
                        time.sleep(DIV_RETRY_DELAYS[attempt])
                    else:
                        logger.warning("yahoo dividend_history empty for %s after %d attempts",
                                       yq_sym, DIV_RETRY_ATTEMPTS)
            except Exception as e:
                if attempt < DIV_RETRY_ATTEMPTS - 1:
                    logger.warning("yahoo dividend_history failed for %s (attempt %d/%d): %s, retrying",
                                   yq_sym, attempt + 1, DIV_RETRY_ATTEMPTS, e)
                    time.sleep(DIV_RETRY_DELAYS[attempt])
                else:
                    logger.warning("yahoo dividend_history failed for %s after %d attempts: %s",
                                   yq_sym, DIV_RETRY_ATTEMPTS, e)

        # Capex + Operating Income + Interest Expense — annual cash_flow + income_statement
        capex_by_year = {}
        operating_income_by_year = {}
        interest_expense_by_year = {}

        try:
            cf = tk.cash_flow(frequency='a')
            if hasattr(cf, 'shape') and not cf.empty and 'CapitalExpenditure' in cf.columns:
                for _, row in cf.iterrows():
                    as_of = row.get('asOfDate')
                    if as_of is None:
                        continue
                    y = as_of.year if hasattr(as_of, 'year') else int(str(as_of)[:4])
                    val = _safe(row.get('CapitalExpenditure'))
                    if val is not None:
                        capex_by_year[y] = val  # negative = spending
        except Exception:
            pass

        try:
            inc = tk.income_statement(frequency='a')
            if hasattr(inc, 'shape') and not inc.empty:
                for _, row in inc.iterrows():
                    as_of = row.get('asOfDate')
                    if as_of is None:
                        continue
                    y = as_of.year if hasattr(as_of, 'year') else int(str(as_of)[:4])
                    oi = _safe(row.get('OperatingIncome'))
                    ie = _safe(row.get('InterestExpense'))
                    if oi is not None:
                        operating_income_by_year[y] = oi
                    if ie is not None:
                        interest_expense_by_year[y] = ie
        except Exception:
            pass

        return {
            "info": info,
            "divs": divs,
            "recent_dividends": recent_divs,
            "dps_by_year": dps_by_year,                  # legacy calendar bin (debug)
            "dps_by_fiscal_year": dps_by_fiscal_year,    # NEW — SET DIY source of truth
            "fy_is_complete": fy_is_complete,            # NEW — flag complete FYs
            "capex_by_year": capex_by_year,
            "operating_income_by_year": operating_income_by_year,
            "interest_expense_by_year": interest_expense_by_year,
        }

    except Exception as e:
        logger.warning("yahooquery failed for %s: %s", symbol, e)
        return {"info": {}, "divs": None, "recent_dividends": [],
                "dps_by_year": {}, "dps_by_fiscal_year": {}, "fy_is_complete": {},
                "capex_by_year": {},
                "operating_income_by_year": {}, "interest_expense_by_year": {}}


def _setsmart_financial_to_yearly(records: list[dict]) -> dict:
    """Group 4 quarters into yearly aggregate. Use Q4 accumulated fields.

    Returns: {year: {revenue, net_profit, eps, ocf, icf, financing_cf, roe, roa, de,
                      total_assets, shareholder_equity}}

    Note: 'financing_cf' = financingCashFlow (debt/equity activity), NOT free cash flow.
    True FCF = OCF - abs(capex) computed in fetch_fundamentals (line 828).
    """
    by_year_q4: dict = {}
    for r in records:
        y = r.get('year')
        q = r.get('quarter')
        if y and q is not None and int(q) == 4:
            by_year_q4[int(y)] = {
                'revenue': r.get('totalRevenueAccum'),
                'net_profit': r.get('netProfitAccum'),
                'eps': r.get('epsAccum'),
                'ocf': r.get('operatingCashFlow'),
                'icf': r.get('investingCashFlow'),
                'financing_cf': r.get('financingCashFlow'),
                'roe': r.get('roe'),
                'roa': r.get('roa'),
                'de': r.get('de'),
                'total_assets': r.get('totalAssets'),
                'shareholder_equity': r.get('shareholderEquity'),
            }
    return by_year_q4


def _fetch_setsmart(symbol: str) -> dict | None:
    """Fetch aggregate data from SETSMART (cached bulk endpoints).

    Returns dict with EOD snapshot (latest day) + financial 5y quarterly range, or None on failure.
    Reads from data/setsmart_cache/ — populated by daily_price_refresh + weekly scan.
    Lazy import of setsmart_adapter to avoid circular import at module load.

    Return shape:
        {
            "eod": dict | None,                           # latest EOD row for symbol
            "financial": list[dict],                      # 5y × 4q = up to 20 quarterly records
            "financial_quarterly": dict[(year, q), dict], # indexed lookup
            "financial_yearly": dict[year, dict],         # Q4 accumulated aggregate per year
        }
    """
    try:
        sym_no_bk = _to_tf_symbol(symbol)  # 'BBL.BK' → 'BBL' (SETSMART uses no .BK suffix)

        cache_dir = ROOT / "data" / "setsmart_cache"
        if not cache_dir.exists():
            return None

        # EOD walk logic — unchanged (newest→older bulk cache files)
        eod_files = sorted(cache_dir.glob("eod_*.json"), reverse=True)
        # Filter out per-symbol files (eod_by_symbol_*.json) — only bulk files (eod_YYYY-MM-DD.json)
        eod_files = [f for f in eod_files if not f.name.startswith("eod_by_symbol_")]
        # Walk newest→older: skip empty cache files (weekend/holiday) until we find symbol
        eod_row = None
        for f in eod_files:
            rows = json.loads(f.read_text(encoding="utf-8"))
            if not rows:
                continue
            for r in rows:
                if r.get("symbol") == sym_no_bk:
                    eod_row = r
                    break
            if eod_row is not None:
                break

        # NEW: financial 5y quarterly range via cached_financial_by_symbol_range
        # Lazy import to avoid circular import at module load (per existing pattern)
        from setsmart_adapter import cached_financial_by_symbol_range

        current_year = datetime.now().year
        start_y = str(current_year - 5)
        end_y = str(current_year - 1)
        try:
            financial_records = cached_financial_by_symbol_range(
                sym_no_bk, start_y, '1', end_y, '4'
            )
        except Exception as e:
            logger.warning("SETSMART financial fetch failed for %s: %s", symbol, e)
            financial_records = []

        financial_quarterly: dict = {}
        for r in financial_records:
            y = r.get('year')
            q = r.get('quarter')
            if y and q:
                financial_quarterly[(int(y), int(q))] = r

        if eod_row is None and not financial_records:
            return None

        return {
            "eod": eod_row,
            "financial": financial_records,
            "financial_quarterly": financial_quarterly,
            "financial_yearly": _setsmart_financial_to_yearly(financial_records),
        }
    except Exception as e:
        logger.warning("SETSMART fetch failed for %s: %s", symbol, e)
        return None


# Public API aliases
fetch_from_thaifin = _fetch_thaifin
fetch_yahoo_supplement = _fetch_yahoo_supplement
# DEPRECATED: keep for any external caller — prefer _fetch_yahoo_supplement
fetch_yfinance_supplement = _fetch_yahoo_supplement


def fetch_fundamentals(symbol: str) -> dict:
    """Fetch fundamentals — SETSMART (primary aggregate) + thaifin (history) + yahooquery (DPS events + 52w + capex/oi/ie).

    Flow (Phase 3 — SETSMART primary):
      1. SETSMART first → use EOD as primary snapshot (price, dy, pe, pbv, mcap)
         + financial_yearly as primary ROE/ROA/D/E/EPS for last 5y
      2. thaifin → yearly history (10-16y) for years outside SETSMART range
      3. yahoo → irreplaceable only (DPS events for fiscal-year attribution,
         52w range, capex, operating_income, interest_expense). When SETSMART
         snapshot is warm, yahoo info is consulted only as fallback for
         fields SETSMART doesn't provide (52w, payoutRatio, etc.).

    Returns schema identical to fetch_multi_year() output.
    """
    yf_sym = _to_yf_symbol(symbol)
    tf_sym = _to_tf_symbol(symbol)

    # 0. SETSMART primary layer — realtime aggregate + 5y yearly ratios
    ss_data = _fetch_setsmart(symbol)
    ss_eod = (ss_data or {}).get("eod") or {}
    ss_fin_yearly = (ss_data or {}).get("financial_yearly") or {}
    use_ss_snapshot = bool(ss_eod and ss_eod.get("close") is not None)

    # 1. thaifin yearly history (10-16y full)
    tf_data = _fetch_thaifin(symbol)

    # 2. yahoo supplement — pass snapshot flag so dividends/capex/IE still fetch
    #    even if yahoo summary endpoints flake (when SETSMART has primary snapshot)
    yf_supp = _fetch_yahoo_supplement(symbol, snapshot=not use_ss_snapshot)
    yf_info = yf_supp.get("info", {})

    # If Yahoo + thaifin + SETSMART all empty → delisted/missing
    # Only treat yahoo "error" as fatal when SETSMART has no snapshot either.
    yf_err = yf_supp.get("error")
    if yf_err and not use_ss_snapshot and tf_data is None and ss_data is None:
        return {"symbol": yf_sym, "error": yf_err}

    # 3. If thaifin failed → return delisted marker (no fallback)
    use_thaifin = tf_data is not None and len(tf_data.get("yearly_metrics", [])) > 0

    if use_thaifin:
        tf_info = tf_data["info"]
        tf_snap = tf_data["snapshot"]
        yearly_metrics = tf_data["yearly_metrics"]

        # --- DPS fix: use Yahoo dividends as source of truth ---
        yf_dps_by_year = yf_supp.get("dps_by_year", {})
        yf_dps_by_fy = yf_supp.get("dps_by_fiscal_year", {})
        yf_fy_complete = yf_supp.get("fy_is_complete", {})
        yf_capex_by_year = yf_supp.get("capex_by_year", {})
        yf_oi_by_year = yf_supp.get("operating_income_by_year", {})
        yf_ie_by_year = yf_supp.get("interest_expense_by_year", {})

        # Build dividend_history + fy_is_complete — set.or.th for the full years inside its
        # ~5y window, yahoo for the first (partial) window year and everything older.
        sym_clean = symbol.replace('.BK', '').upper()
        dividend_source = 'unknown'
        _dps_fallback_to_yahoo = False
        set_fy_dps: dict = {}
        try:
            if not _SET_OFFICIAL_AVAILABLE:
                raise RuntimeError('set_official_adapter import failed at module load')
            set_fy_dps = _set_dps_by_fy(sym_clean)
            if not set_fy_dps:
                raise ValueError('set.or.th returned empty')
        except Exception as e:
            logger.warning(f'set.or.th DPS fetch failed for {symbol}: {e}; falling back to yahoo')
            set_fy_dps = {}
            _dps_fallback_to_yahoo = True

        merged = merge_dividend_sources(set_fy_dps, yf_dps_by_fy)
        dividend_history = {y: round(dps, 4) for y, dps in merged['history'].items()}
        dividend_history_source = merged['source_by_fy']
        dps_mismatches = merged['mismatches']
        dividend_warnings = ['DPS_SOURCE_YAHOO'] if _dps_fallback_to_yahoo else []
        if dps_mismatches:
            parts = [f"FY{y} set={m['set']} yahoo={m['yahoo']}" for y, m in sorted(dps_mismatches.items())]
            dividend_warnings.append('DPS_SOURCE_MISMATCH ' + '; '.join(parts))

        if set_fy_dps:
            dividend_source = ('set_official+yahoo'
                               if any(v == 'yahoo' for v in dividend_history_source.values())
                               else 'set_official')
            _cy = datetime.now().year
            # past years are complete; the first set-window year kept as set_partial is not
            fy_is_complete = {y: (y < _cy and dividend_history_source.get(y) != 'set_partial')
                              for y in dividend_history}
        else:
            dividend_source = 'yahoo'
            fy_is_complete = yf_fy_complete

        crisis_bars = ensure_crisis_bars(symbol)  # disk-cached yahoo monthly bars for crisis_* drops

        # Patch yearly_metrics with capex, operating_income, interest data from Yahoo
        for m in yearly_metrics:
            y = int(m["year"])

            # FCF: OCF - capex (not OCF + investing_activities)
            capex_val = yf_capex_by_year.get(y)
            if capex_val is not None:
                m["capex"] = capex_val  # negative = spending
                if m["ocf"] is not None:
                    m["fcf"] = m["ocf"] - abs(capex_val)
            # else: keep original fcf (OCF + investing) as fallback

            # Interest coverage: operating_income / interest_expense
            oi_val = yf_oi_by_year.get(y)
            ie_val = yf_ie_by_year.get(y)
            if oi_val is not None:
                m["operating_income"] = oi_val
                m["operating_margin"] = _safe_div(oi_val, m.get("revenue"))
            if ie_val is not None:
                m["interest_expense"] = ie_val
            if oi_val is not None and ie_val is not None and ie_val > 0:
                cov = oi_val / ie_val
                m["interest_coverage"] = cov if cov <= 200 else None
            # Also fix EBITDA: use operating_income + DA instead of net_income + DA
            if oi_val is not None and m.get("ebitda") is not None:
                da_approx = m["ebitda"] - (m.get("net_income") or 0)  # DA from old calc
                if da_approx > 0:
                    m["ebitda"] = oi_val + da_approx

        # SETSMART yearly override (5y range) — overlay ROE/ROA/D/E/EPS from
        # financial_yearly onto thaifin yearly_metrics where year matches.
        # thaifin schema: m["roe"], m["roa"] (decimal), m["de_ratio"] (raw ratio),
        # m["diluted_eps"] (THB). SETSMART roe/roa come as percentage → /100.
        # EPS stored as separate field eps_setsmart to preserve thaifin diluted_eps.
        if ss_fin_yearly:
            for m in yearly_metrics:
                try:
                    y_int = int(m.get("year"))
                except (TypeError, ValueError):
                    continue
                ss_y = ss_fin_yearly.get(y_int)
                if not ss_y:
                    continue
                if ss_y.get("roe") is not None:
                    m["roe"] = ss_y["roe"] / 100.0
                if ss_y.get("roa") is not None:
                    m["roa"] = ss_y["roa"] / 100.0
                if ss_y.get("de") is not None:
                    m["de_ratio"] = ss_y["de"]
                if ss_y.get("eps") is not None:
                    m["eps_setsmart"] = ss_y["eps"]

        # Merge: thaifin base + Yahoo supplement
        name = tf_info.get("name") or yf_info.get("shortName", yf_sym)
        sector = tf_info.get("sector", "N/A")
        industry = tf_info.get("industry", "N/A")

        # --- SNAPSHOT FIELDS — SETSMART primary, yahoo/thaifin fallback ---
        if use_ss_snapshot:
            price = ss_eod.get("close")
            price_as_of = ss_eod.get("date")
            pe_ratio = ss_eod.get("pe") or tf_snap.get("pe_ratio")
            pb_ratio = ss_eod.get("pbv") or tf_snap.get("pb_ratio")
            market_cap = ss_eod.get("marketCap") or tf_snap.get("market_cap")
            # dy from SETSMART EOD — DPS-based override may follow below
            dy_snapshot = ss_eod.get("dividendYield")
            logger.info(
                "SETSMART snapshot primary for %s (price=%s pe=%s pbv=%s mcap=%s dy=%s)",
                symbol, price, pe_ratio, pb_ratio, market_cap, dy_snapshot,
            )
        else:
            # SETSMART cold → fall back to yahoo + thaifin
            price = yf_info.get("currentPrice") or yf_info.get("regularMarketPrice")
            price_as_of = datetime.now().strftime("%Y-%m-%d")
            market_cap = yf_info.get("marketCap") or tf_snap.get("market_cap")
            pe_ratio = yf_info.get("trailingPE") or tf_snap.get("pe_ratio")
            pb_ratio = yf_info.get("priceToBook") or tf_snap.get("pb_ratio")
            dy_snapshot = None
            logger.info("SETSMART snapshot cold for %s — using yahoo+thaifin fallback", symbol)

        forward_pe = yf_info.get("forwardPE")

        # --- Dividend: DPS-first, yield = DPS/price (Fiscal Year Attribution per SET methodology) ---
        # Source-resolved: read from dividend_history (set.or.th primary, yahoo fallback)
        # — fy_is_complete is source-resolved (set.or.th synthesis primary, yahoo calendar fallback)
        complete_fys = sorted([y for y, ok in fy_is_complete.items() if ok])
        latest_complete_fy = complete_fys[-1] if complete_fys else None

        if latest_complete_fy is not None:
            dps_current = dividend_history.get(latest_complete_fy)
            snapshot_dps_source = dividend_source if dps_current is not None else None
        else:
            dps_current = None
            snapshot_dps_source = None

        logger.info(
            "snapshot DPS for %s: dps_current=%s snapshot_dps_source=%s (dividend_source=%s, latest_complete_fy=%s)",
            symbol, dps_current, snapshot_dps_source, dividend_source, latest_complete_fy,
        )

        if dps_current is not None and price is not None and price > 0:
            dy = dps_current / price * 100
        elif dy_snapshot is not None:
            dy = dy_snapshot  # SETSMART EOD dividendYield
        else:
            dy = None
            logger.warning(
                "no DPS for %s (latest_complete_fy=%s, dps_current=%s, price=%s, dps_source=%s) — "
                "dy unset (no DPS in dividend_history for latest complete FY; thaifin DPS approximation NOT used)",
                symbol, latest_complete_fy, dps_current, price, snapshot_dps_source,
            )

        # five_year_avg_yield = avg DPS of last 5 COMPLETE FYs / current price
        # Source-resolved: read from dividend_history (matches dps_current source)
        current_year = datetime.now().year
        recent_complete_fys = complete_fys[-5:] if len(complete_fys) >= 5 else complete_fys
        recent_dps = [dividend_history.get(y) for y in recent_complete_fys if dividend_history.get(y) is not None]
        if recent_dps and price is not None and price > 0:
            avg_dps = sum(recent_dps) / len(recent_dps)
            five_year_avg_yield = avg_dps / price * 100
        else:
            raw_5y = yf_info.get("fiveYearAvgDividendYield")
            five_year_avg_yield = raw_5y if raw_5y is not None else None

        dividend_rate = dps_current
        # payout_ratio = latest FY DPS / latest FY EPS (same period match)
        payout_ratio = None
        if latest_complete_fy is not None and dps_current is not None:
            for m in yearly_metrics:
                if int(m.get("year", 0)) == latest_complete_fy:
                    eps_fy = m.get("diluted_eps")
                    if eps_fy and eps_fy > 0:
                        payout_ratio = dps_current / eps_fy
                    break
        if payout_ratio is None:
            payout_ratio = yf_info.get("payoutRatio")  # fallback Yahoo

        # EPS
        eps_trailing = tf_snap.get("eps_trailing") or yf_info.get("trailingEps")
        eps_forward = yf_info.get("forwardEps")

        # Financials: prefer thaifin
        revenue = tf_snap.get("revenue") or yf_info.get("totalRevenue")
        revenue_growth = tf_snap.get("revenue_growth") or yf_info.get("revenueGrowth")
        earnings_growth = tf_snap.get("earnings_growth") or yf_info.get("earningsGrowth")
        profit_margin = tf_snap.get("profit_margin") or yf_info.get("profitMargins")
        gross_margins = tf_snap.get("gross_margins") or yf_info.get("grossMargins")
        operating_margins = tf_snap.get("operating_margins") or yf_info.get("operatingMargins")
        roe = tf_snap.get("roe") or yf_info.get("returnOnEquity")
        roa = tf_snap.get("roa") or yf_info.get("returnOnAssets")
        debt_to_equity = tf_snap.get("debt_to_equity") or yf_info.get("debtToEquity")
        current_ratio = tf_snap.get("current_ratio") or yf_info.get("currentRatio")

        # FCF: prefer Yahoo (uses proper capex), fallback thaifin
        free_cashflow = yf_info.get("freeCashflow") or tf_snap.get("free_cashflow")
        operating_cashflow = yf_info.get("operatingCashflow") or tf_snap.get("operating_cashflow")

        # Recent dividends from Yahoo
        recent_divs = yf_supp.get("recent_dividends", [])

        # Price technicals from Yahoo (irreplaceable — SETSMART doesn't provide)
        w52_high = yf_info.get("fiftyTwoWeekHigh")
        w52_low = yf_info.get("fiftyTwoWeekLow")
        d50_avg = yf_info.get("fiftyDayAverage")
        d200_avg = yf_info.get("twoHundredDayAverage")

    else:
        # thaifin failed — return None to signal delisted/missing
        return None

    return {
        "symbol": yf_sym,
        "name": name,
        "sector": sector,
        "industry": industry,
        "currency": yf_info.get("currency", "THB"),
        "price": price,
        "price_as_of": price_as_of,
        "market_cap": market_cap,
        "pe_ratio": pe_ratio,
        "forward_pe": forward_pe,
        "pb_ratio": pb_ratio,
        "dividend_yield": dy,  # percentage (e.g. 4.5 = 4.5%)
        "dps": dps_current,  # actual dividend per share amount
        "dividend_rate": dividend_rate,
        "payout_ratio": payout_ratio,
        "five_year_avg_yield": five_year_avg_yield,  # percentage
        "eps_trailing": eps_trailing,
        "eps_forward": eps_forward,
        "revenue": revenue,
        "revenue_growth": revenue_growth,
        "earnings_growth": earnings_growth,
        "profit_margin": profit_margin,
        "gross_margins": gross_margins,
        "operating_margins": operating_margins,
        "roe": roe,
        "roa": roa,
        "debt_to_equity": debt_to_equity,
        "current_ratio": current_ratio,
        "free_cashflow": free_cashflow,
        "operating_cashflow": operating_cashflow,
        "recent_dividends": recent_divs,
        "52w_high": w52_high,
        "52w_low": w52_low,
        "50d_avg": d50_avg,
        "200d_avg": d200_avg,
        "yearly_metrics": yearly_metrics,
        "dividend_history": dividend_history,
        "fy_is_complete": fy_is_complete,
        "dividend_source": dividend_source,
        "dividend_history_source": dividend_history_source,  # {FY: 'set'|'yahoo'|'set_partial'}
        "dividend_last_complete_fy": last_complete_fy(dividend_history, fy_is_complete),
        "dividend_source_mismatch": dps_mismatches,  # {FY: {'set': x, 'yahoo': y}}
        "dividend_overlap_years": merged['overlap_years'],
        "dividend_overlap_matches": merged['overlap_matches'],
        "crisis_bars_available": bool(crisis_bars),
        "sector_profile": classify_sector_profile(sector),
        "warnings": dividend_warnings,
    }


# --- Niwes extensions (append-only — do not modify fetch_fundamentals) ---

EXTRAORDINARY_KEYWORDS = ("extraordinary", "one-time", "one time", "gain on sale",
                         "loss on sale", "impairment", "restructuring", "non-recurring")


def compute_normalized_earnings(stock_data: dict) -> dict:
    """Return {year: normalized_eps} after stripping extraordinary items.

    thaifin yearly_dataframe does not expose line-item names for extraordinary
    items, so this falls back to using diluted_eps as-is. When richer income
    statement data becomes available (item-name keyword match against
    EXTRAORDINARY_KEYWORDS), this function will exclude those items from
    net_income before recomputing EPS.
    """
    out = {}
    for m in stock_data.get("yearly_metrics", []):
        year = m.get("year")
        eps = m.get("diluted_eps")
        if year is None or eps is None:
            continue
        out[year] = eps
    return out


def compute_payout_sustainability(stock_data: dict) -> dict:
    """Return {year: {payout_ratio, sustainable}} per yearly_metrics row.

    payout_ratio = DPS / diluted_eps (both known fields).
    sustainable = payout < 0.80 AND fcf positive (dividends paid from real cash).

    Replaces old formula that depended on dividends_paid which is always None from thaifin.
    """
    out = {}
    dividend_history = stock_data.get("dividend_history", {}) or {}
    for m in stock_data.get("yearly_metrics", []):
        year = m.get("year")
        if year is None:
            continue
        eps = m.get("diluted_eps")
        fcf = m.get("fcf")
        # dividend_history keys are int (from fetch), yearly_metrics.year is str — try both
        dps = dividend_history.get(year)
        if dps is None:
            try:
                dps = dividend_history.get(int(year))
            except (TypeError, ValueError):
                dps = None
        if dps is not None and eps is not None and eps > 0:
            payout_ratio = dps / eps
        else:
            payout_ratio = None
        sustainable = (
            payout_ratio is not None and payout_ratio < 0.80
            and fcf is not None and fcf > 0
        )
        out[year] = {"payout_ratio": payout_ratio, "sustainable": sustainable}
    return out


def check_hidden_value(symbol: str) -> list:
    """Return list of hidden-value holdings for symbol, or [] if none.

    Reads bootstrap data from data/hidden_value_holdings.json.
    Symbol normalized to .BK form for lookup.
    """
    import json
    from pathlib import Path

    _, yf_sym = normalize_symbol(symbol)
    json_path = Path(__file__).resolve().parent.parent / "data" / "hidden_value_holdings.json"
    if not json_path.exists():
        return []
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    holdings = data.get(yf_sym, [])
    # Enrich holdings with holding_mcap (error-safe, memoized)
    for h in holdings:
        if "holding_mcap" not in h:  # don't overwrite if caller pre-set
            h["holding_mcap"] = _holding_mcap(h.get("holding"))
    return holdings


if __name__ == '__main__':
    import pandas as pd

    # Test 1: Semi-annual pattern (BBL-like) — 2 events จัดเป็น FY2025
    bbl_divs = pd.Series(
        [2.0, 10.0],
        index=[pd.Timestamp('2025-09-15'), pd.Timestamp('2026-04-22')],
    )
    r1 = _attribute_dividends_to_fiscal_years(bbl_divs)
    assert r1['by_fy'][2025] == 12.0, f"BBL: Expected FY2025=12.0, got {r1['by_fy'].get(2025)}"
    # sorted_fys = [2025] → typical_count = 2 default → actual_count for FY2025 = 2 → is_complete = True
    assert r1['is_complete'][2025] is True, "BBL FY2025 should be complete"

    # Test 2: Annual-pay pattern (METCO-like) — pays once per year in February
    metco_divs = pd.Series(
        [10.0, 14.0, 18.0, 10.0, 8.0, 30.0],
        index=[
            pd.Timestamp('2021-02-10'),  # FY2020 final
            pd.Timestamp('2022-02-09'),  # FY2021 final
            pd.Timestamp('2023-02-08'),  # FY2022 final
            pd.Timestamp('2024-02-07'),  # FY2023 final
            pd.Timestamp('2025-02-06'),  # FY2024 final
            pd.Timestamp('2026-02-05'),  # FY2025 final (single event = whole year for annual-pay)
        ],
    )
    r2 = _attribute_dividends_to_fiscal_years(metco_divs)
    assert r2['typical_count'] == 1, f"METCO typical should be 1 (annual), got {r2.get('typical_count')}"
    assert r2['by_fy'][2025] == 30.0, f"METCO FY2025 should be 30.0, got {r2['by_fy'].get(2025)}"
    assert r2['is_complete'][2025] is True, "METCO FY2025 should be complete (annual-pay, 1 event = full year)"

    print('FY attribution OK')

    # Smoke test: snapshot DPS source-aware fix (2026-05-20)
    # Runs real fetch — verifies snapshot dps matches dividend_history[latest_complete_fy]
    import json
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    for sym in ('HTC.BK', 'BBL.BK'):
        print(f'\n=== smoke test: {sym} ===')
        data = fetch_fundamentals(sym)
        if data is None:
            print(f'  fetch_fundamentals returned None (delisted or fetch failure)')
            continue
        if 'error' in data:
            print(f'  error: {data["error"]}')
            continue
        snapshot = {
            'dps': data.get('dps'),
            'dividend_rate': data.get('dividend_rate'),
            'dividend_yield': data.get('dividend_yield'),
            'five_year_avg_yield': data.get('five_year_avg_yield'),
            'payout_ratio': data.get('payout_ratio'),
        }
        print(f'  dividend_source: {data.get("dividend_source")}')
        print(f'  dividend_history: {json.dumps(data.get("dividend_history", {}), sort_keys=True)}')
        print(f'  snapshot (5 fields): {json.dumps(snapshot, indent=2, default=str)}')
        # Sanity: dps should match dividend_history[latest_complete_fy]
        fy_complete = data.get('fy_is_complete', {})
        complete_fys = sorted([int(y) for y, ok in fy_complete.items() if ok])
        if complete_fys:
            latest_fy = complete_fys[-1]
            div_hist = data.get('dividend_history', {})
            hist_dps = div_hist.get(latest_fy) or div_hist.get(str(latest_fy))
            print(f'  cross-check: dps={snapshot["dps"]} vs dividend_history[{latest_fy}]={hist_dps} -> {"MATCH" if snapshot["dps"] == hist_dps else "MISMATCH"}')
