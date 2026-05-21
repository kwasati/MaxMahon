"""Hong Stage 1 Auto Scanner — Hong full philosophy.

Reference research: _shared/docs/research-sianhong-stock-picking.md

Versions:
  v1 — legacy: D/E ≤ 1.0 for all sectors, 6 criteria all-or-nothing
  v2 — sector-aware solvency, 6 criteria all-or-nothing
  v3 — alias for v2 logic + full SET+mai universe
  v4 — Full philosophy: 7 hard gates + Sweet Spot composite score
  v5 — **Same as v4 minus Gate 2 (cash adequacy). 6 hard gates only.**
        Cash adequacy needs short_term_debt + annual dividends paid per FY which
        are NOT in cache. v4 used proxies (0.3 * total_debt + dps * shares) which
        we no longer trust. v5 simply skips this gate and emits
        "MANUAL_CHECK_NEEDED: cash_adequacy" for every survivor so the analyst
        knows it is still pending verification.

v4 — 7 Hard Gates (all must pass to enter pool):
  1. Solvency (sector-aware):
       default → D/E ≤ 1.0
       retail  → D/E ≤ 2.5
       bank    → ROA 3y avg ≥ 1%
  2. Cash adequacy — cash ≥ (short-term debt proxy + estimated annual dividend)
  3. Margin slope — gm 3y slope ≥ 0 AND nm 3y slope ≥ 0 (strict both)
  4. CFO / Net profit (3y avg) ≥ 0.8
  5. ROE relative — ROE 3y avg ≥ max(industry_median, 12%)
  6. กำไร new high — latest profit = max of last 5y
  7. Forward PE ≤ 15 (trailing fallback ok)

v5 — 6 Hard Gates (skip Gate 2 — manual review needed):
  1. Solvency (same as v4)
  3. Margin slope
  4. CFO / NP
  5. ROE relative
  6. New high profit
  7. Forward PE
  (Gate 2 cash adequacy removed — flagged for manual review in Stage 2)

v4 — Sweet Spot Composite Score (rank survivors):
  8. Earnings CAGR 3y     — linear 0%→0, 26%→100 (capped)
  9. Dividend yield       — linear 0%→0, 4%→70, 7%+→100
  10. PEG (growth/PE)     — linear ratio 1→50, 1.5+→100, <1→from 0
  Composite = CAGR×0.4 + Yield×0.3 + PEG×0.3

Data source: data/screener_cache/{date}/{SYM}.json (output of fetch_fundamentals).
Universe options:
  - SET100   → SET100 2025-H2 hardcoded list (97 syms)
  - all      → all common stocks in cache (SET + mai), filter out
               Property Fund & REITs + Infrastructure Fund + ETF (~840 syms)
  - {file}   → custom file with one symbol per line (no .BK suffix)

Usage:
    py scripts/hong_stage1_scanner.py [--cache-date YYYY-MM-DD] [--out-prefix path/prefix]
                                      [--universe SET100|all|file.txt]
                                      [--version v1|v2|v3|v4]   (default v2)

Outputs (v1-v3):
    research/hong-stage1-scan-{today}-{version}.csv
    research/hong-stage1-scan-{today}-{version}.md
Outputs (v4):
    research/hong-v4-scan-{today}.csv
    research/hong-v4-scan-{today}.md
    stdout: top 30 + gate failure breakdown + niwes regression
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


# ----------------------------------------------------------------------------
# SET100 universe (effective 1 Jul 2025 - 31 Dec 2025, official SET index page).
# Source: SET index publication "SET50 SET100 รอบบ่ายของวันที่ 17 ธ.ค. 2567 / 2H2025".
# ----------------------------------------------------------------------------
SET100_2025_H2 = [
    "ADVANC", "AOT", "AP", "AWC", "BANPU", "BBL", "BCP", "BCPG", "BDMS", "BEM",
    "BGRIM", "BH", "BJC", "BLA", "BTS", "CBG", "CCET", "CENTEL", "CK", "CKP",
    "COM7", "CPALL", "CPF", "CPN", "CRC", "DELTA", "EA", "EGCO", "ERW", "GLOBAL",
    "GPSC", "GULF", "GUNKUL", "HANA", "HMPRO", "ICHI", "IRPC", "ITC", "IVL", "JMART",
    "JMT", "KBANK", "KCE", "KKP", "KTB", "KTC", "LH", "M", "MAJOR", "MEGA",
    "MINT", "MTC", "OR", "OSP", "PLANB", "PSL", "PTG", "PTT", "PTTEP", "PTTGC",
    "QH", "RATCH", "RBF", "SAPPE", "SAWAD", "SCB", "SCC", "SCGP", "SHR", "SIRI",
    "SISB", "SPALI", "SPRC", "STA", "STGT", "STECON", "SUPER", "TASCO", "TCAP",
    "THCOM", "TIDLOR", "TISCO", "TOA", "TOP", "TRUE", "TTB", "TU", "VGI", "WHA",
    "WHAUP", "BSRC", "BLAND", "TLI", "INTUCH", "MOSHI", "BTG", "CHG", "BCH",
    "TNP", "TIPH", "PR9",
]


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def _safe(v):
    if v is None:
        return None
    try:
        f = float(v)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


def _last_n_years(yearly_metrics: list[dict], n: int) -> list[dict]:
    """Return the last n yearly_metrics rows, sorted oldest→newest."""
    if not yearly_metrics:
        return []
    rows = sorted(yearly_metrics, key=lambda r: str(r.get("year", "")))
    return rows[-n:]


def _drop_partial_latest(yearly_metrics: list[dict]) -> list[dict]:
    """If the latest year row has all-zero or near-zero revenue/net_income, drop it (partial-year data)."""
    if not yearly_metrics:
        return yearly_metrics
    rows = sorted(yearly_metrics, key=lambda r: str(r.get("year", "")))
    last = rows[-1]
    rev = _safe(last.get("revenue"))
    ni = _safe(last.get("net_income"))
    # Drop only if both look uninitialised/zero. Real loss years (ni<0) kept.
    if (rev is None or rev == 0) and (ni is None or ni == 0):
        return rows[:-1]
    return rows


# ----------------------------------------------------------------------------
# Sector classification (sector-aware solvency)
# ----------------------------------------------------------------------------

# SET sector strings we expect (from data_adapter.py / thaifin):
#   - Banking
#   - Finance & Securities
#   - Insurance
#   - Commerce              (retail / wholesale — heavy trade payables)
#   - Food & Beverage       (some have retail-like AP — kept as default; can revisit)
#   - Professional Services, Construction Services, etc. → default
def classify_sector(sector_name: str | None) -> str:
    """Return one of: 'retail' | 'bank' | 'default'.

    'bank' = banking / finance & securities (deposits/customer-funding inflate D/E).
    'retail' = commerce sector (trade payables inflate D/E above 1.0 legitimately).
    Everything else = 'default' (industrial, services, healthcare, tech ...).
    """
    if not sector_name:
        return "default"
    s = sector_name.strip().lower()
    if "bank" in s or "finance & securities" in s or s in ("financial", "financials"):
        return "bank"
    if "commerce" in s or "retail" in s:
        return "retail"
    return "default"


# ----------------------------------------------------------------------------
# Criteria
# ----------------------------------------------------------------------------

def _latest_de_raw(stock: dict) -> float | None:
    """Latest D/E as raw ratio. Prefer yearly_metrics[-1].de_ratio, fallback to
    top-level debt_to_equity which is stored as percentage (data_adapter.py:316)."""
    ym = _drop_partial_latest(stock.get("yearly_metrics") or [])
    if ym:
        de = _safe(ym[-1].get("de_ratio"))
        if de is not None:
            return de
    de_pct = _safe(stock.get("debt_to_equity"))
    if de_pct is not None:
        return de_pct / 100.0
    return None


def _roa_3y_avg(stock: dict) -> tuple[float | None, list[float | None]]:
    """ROA 3y avg (decimal). Returns (avg, per-year list)."""
    ym = _drop_partial_latest(stock.get("yearly_metrics") or [])
    last3 = _last_n_years(ym, 3)
    if len(last3) < 3:
        return (None, [])
    roas = [_safe(r.get("roa")) for r in last3]
    if any(r is None for r in roas):
        return (None, roas)
    return (sum(roas) / 3, roas)


def criterion_1_solvency(stock: dict, sector_class: str, version: str = "v2"
                         ) -> tuple[bool | None, dict]:
    """Sector-aware solvency check.

    v1: always D/E ≤ 1.0 (legacy).
    v2:
      - default → D/E ≤ 1.0
      - retail  → D/E ≤ 2.5    (trade payables tolerance)
      - bank    → ROA 3y avg ≥ 0.01 (1%) — D/E swap

    Returns (passed, info_dict). info_dict keys:
      - rule: "de<=1.0" | "de<=2.5" | "roa3y>=0.01"
      - de_ratio:  latest D/E raw (always populated when available, even for banks
                    — for the audit columns)
      - roa_3y_avg: only populated for bank rule
    """
    de_raw = _latest_de_raw(stock)
    roa_avg, _ = _roa_3y_avg(stock)

    info: dict = {
        "rule": None,
        "de_ratio": de_raw,
        "roa_3y_avg": roa_avg,
        "sector_class": sector_class,
    }

    if version == "v1" or sector_class == "default":
        info["rule"] = "de<=1.0"
        if de_raw is None:
            return (None, info)
        return (de_raw <= 1.0, info)

    if sector_class == "retail":
        info["rule"] = "de<=2.5"
        if de_raw is None:
            return (None, info)
        return (de_raw <= 2.5, info)

    if sector_class == "bank":
        info["rule"] = "roa3y>=0.01"
        if roa_avg is None:
            return (None, info)
        return (roa_avg >= 0.01, info)

    # Fallback shouldn't happen
    info["rule"] = "de<=1.0"
    if de_raw is None:
        return (None, info)
    return (de_raw <= 1.0, info)


# v1-compatible alias kept for any external caller
def criterion_1_de(stock: dict) -> tuple[bool | None, float | None]:
    """Legacy v1: D/E ≤ 1.0 across all sectors. Kept for backward compatibility."""
    de_raw = _latest_de_raw(stock)
    if de_raw is None:
        return (None, None)
    return (de_raw <= 1.0, de_raw)


def criterion_2_roe(stock: dict, industry_median_3y_avg: float | None = None) -> tuple[bool | None, dict]:
    """ROE ≥ 15% for 3 consecutive recent years (or ≥ industry median if median > 15%).

    industry_median_3y_avg: ROE 3y avg median of stocks in the same sector (decimal).

    Returns ROE 3y values + 3y avg.
    """
    ym = _drop_partial_latest(stock.get("yearly_metrics") or [])
    last3 = _last_n_years(ym, 3)
    if len(last3) < 3:
        return (None, {"roe_3y": [], "roe_3y_avg": None, "threshold": 0.15})

    roes = [_safe(r.get("roe")) for r in last3]
    if any(r is None for r in roes):
        return (None, {"roe_3y": roes, "roe_3y_avg": None, "threshold": 0.15})

    avg = sum(roes) / 3
    threshold = 0.15
    if industry_median_3y_avg is not None and industry_median_3y_avg > 0.15:
        threshold = industry_median_3y_avg

    passed = all(r >= threshold for r in roes)
    return (passed, {"roe_3y": roes, "roe_3y_avg": avg, "threshold": threshold})


def criterion_3_profit_new_high(stock: dict) -> tuple[bool | None, dict]:
    """Latest net profit = all-time high within last 5 years."""
    ym = _drop_partial_latest(stock.get("yearly_metrics") or [])
    last5 = _last_n_years(ym, 5)
    if len(last5) < 3:
        return (None, {"net_profits_5y": [], "latest": None, "max_prior": None})

    profits = [(r.get("year"), _safe(r.get("net_income"))) for r in last5]
    if any(p[1] is None for p in profits):
        return (None, {"net_profits_5y": profits, "latest": None, "max_prior": None})

    latest_year, latest = profits[-1]
    prior = [p[1] for p in profits[:-1]]
    if not prior:
        return (None, {"net_profits_5y": profits, "latest": latest, "max_prior": None})
    max_prior = max(prior)
    # Strict: latest > max_prior (or equal — call equal as "new high" too)
    return (latest >= max_prior and latest > 0, {
        "net_profits_5y": profits,
        "latest": latest,
        "max_prior": max_prior,
    })


def criterion_4_cfo_np(stock: dict) -> tuple[bool | None, dict]:
    """CFO / Net profit (avg of last 3y) ≥ 0.8.

    Compute ratio per year (when both positive), then take simple mean of the
    last 3 fiscal years.
    """
    ym = _drop_partial_latest(stock.get("yearly_metrics") or [])
    last3 = _last_n_years(ym, 3)
    if len(last3) < 3:
        return (None, {"per_year": [], "avg": None})

    ratios = []
    per_year = []
    for r in last3:
        ocf = _safe(r.get("ocf"))
        ni = _safe(r.get("net_income"))
        if ocf is None or ni is None or ni <= 0:
            # If net profit ≤ 0, ratio is meaningless. Mark as None per year.
            per_year.append({"year": r.get("year"), "ocf": ocf, "ni": ni, "ratio": None})
            continue
        ratio = ocf / ni
        ratios.append(ratio)
        per_year.append({"year": r.get("year"), "ocf": ocf, "ni": ni, "ratio": ratio})

    if len(ratios) < 3:
        return (None, {"per_year": per_year, "avg": None})

    avg = sum(ratios) / len(ratios)
    return (avg >= 0.8, {"per_year": per_year, "avg": avg})


def criterion_5_fwd_pe(stock: dict) -> tuple[bool | None, float | None, str]:
    """Forward PE ≤ 15.

    Source preference: forward_pe (from yfinance summary_detail.forwardPE).
    Fallback: trailing pe_ratio when forward is missing (frequent for Thai stocks
    with no analyst coverage). The label tells which source was used.

    Returns (pass_bool|None, pe_value, source_label).
    """
    fwd_pe = _safe(stock.get("forward_pe"))
    if fwd_pe is not None and fwd_pe > 0:
        return (fwd_pe <= 15.0, fwd_pe, "forward")
    # Fallback: trailing PE
    pe = _safe(stock.get("pe_ratio"))
    if pe is not None and pe > 0:
        return (pe <= 15.0, pe, "trailing_fallback")
    return (None, None, "missing")


# ----------------------------------------------------------------------------
# v4 — additional criteria
# ----------------------------------------------------------------------------

def cash_adequacy_check(stock: dict) -> tuple[bool | None, dict]:
    """Gate 2 (v4) — cash ≥ (short-term debt proxy + estimated annual dividend).

    Proxy rules (data we don't have direct from cache):
      - short_term_debt ≈ total_debt × 0.3 (heuristic: ~30% of total typically <1y)
      - annual_dividend ≈ dps × shares_outstanding where shares = market_cap / price

    Returns (passed, info_dict) with cash, st_debt_proxy, est_annual_div, ratio.
    """
    ym = _drop_partial_latest(stock.get("yearly_metrics") or [])
    if not ym:
        return (None, {"reason": "no yearly_metrics"})
    last = ym[-1]
    cash = _safe(last.get("cash"))
    total_debt = _safe(last.get("total_debt"))

    if cash is None:
        return (None, {"reason": "cash missing"})
    if total_debt is None or total_debt < 0:
        total_debt = 0.0

    st_debt_proxy = total_debt * 0.30

    # Estimate annual dividend payout
    dps = _safe(stock.get("dps"))
    mcap = _safe(stock.get("market_cap"))
    price = _safe(stock.get("price"))
    est_annual_div = 0.0
    if dps is not None and dps > 0 and mcap is not None and price is not None and price > 0:
        shares = mcap / price
        est_annual_div = dps * shares

    required = st_debt_proxy + est_annual_div
    info = {
        "cash": cash,
        "total_debt": total_debt,
        "st_debt_proxy": st_debt_proxy,
        "est_annual_div": est_annual_div,
        "required": required,
        "ratio": (cash / required) if required > 0 else None,
    }
    # If required is 0 (no debt + no div), trivially pass
    if required <= 0:
        return (True, info)
    return (cash >= required, info)


def industry_median_roe(sector: str | None, all_stocks: dict[str, dict]) -> float | None:
    """Industry-median ROE 3y avg for a sector. Same as compute_industry_roe_medians
    but returns single value. Used by v4 gate 5."""
    if not sector:
        return None
    medians = compute_industry_roe_medians(all_stocks)
    return medians.get(sector)


def earnings_cagr_3y(stock: dict) -> float | None:
    """3y CAGR of net_income from latest 4 yearly_metrics rows (3 intervals).

    CAGR = (end/start)^(1/3) - 1. Returns None if start ≤ 0 or data missing.
    """
    ym = _drop_partial_latest(stock.get("yearly_metrics") or [])
    last4 = _last_n_years(ym, 4)
    if len(last4) < 4:
        return None
    start = _safe(last4[0].get("net_income"))
    end = _safe(last4[-1].get("net_income"))
    if start is None or end is None:
        return None
    if start <= 0:
        return None
    if end <= 0:
        return -1.0  # collapsed earnings → very negative growth
    return (end / start) ** (1.0 / 3.0) - 1.0


def dividend_yield_pct(stock: dict) -> float | None:
    """Latest dividend yield as percentage (e.g. 5.0 = 5%).

    Prefer top-level `dividend_yield` (computed dps/price * 100 by data_adapter).
    Fallback: compute from dps + price directly.
    """
    y = _safe(stock.get("dividend_yield"))
    if y is not None and y >= 0:
        return y
    dps = _safe(stock.get("dps"))
    price = _safe(stock.get("price"))
    if dps is not None and price is not None and price > 0:
        return (dps / price) * 100
    return None


def peg_ratio(growth_pct: float | None, fwd_pe: float | None) -> float | None:
    """PEG = PE / earnings_growth_pct.

    growth_pct in percent points (e.g. 20 = 20%). fwd_pe positive.
    Returns None if either missing or growth <= 0 (PEG undefined for negative growth).
    """
    if growth_pct is None or fwd_pe is None:
        return None
    if growth_pct <= 0 or fwd_pe <= 0:
        return None
    return fwd_pe / growth_pct


# ----------------------------------------------------------------------------
# v4 — Sweet Spot Component Scores
# ----------------------------------------------------------------------------

def cagr_score(cagr: float | None) -> float:
    """0%→0, 26%→100, >26%→100 capped. Negative→0."""
    if cagr is None:
        return 0.0
    if cagr <= 0:
        return 0.0
    pct = cagr * 100
    if pct >= 26:
        return 100.0
    return (pct / 26.0) * 100.0


def yield_score(y_pct: float | None) -> float:
    """0%→0, 4%→70, 7%+→100. Linear in between."""
    if y_pct is None or y_pct <= 0:
        return 0.0
    if y_pct >= 7.0:
        return 100.0
    if y_pct <= 4.0:
        # 0 → 0, 4 → 70 linear
        return (y_pct / 4.0) * 70.0
    # 4 → 70, 7 → 100 linear
    return 70.0 + ((y_pct - 4.0) / 3.0) * 30.0


def peg_score(peg: float | None) -> float:
    """
    Lower PEG = better growth-per-PE.
    Spec: ratio 1 → 50, 1.5+ → 100, <1 → linear from 0.

    Interpretation (per task):
      peg = 0    → 0
      peg = 1.0  → 50
      peg = 1.5+ → 100
    Above 1.5: capped at 100.
    """
    if peg is None:
        return 0.0
    if peg <= 0:
        return 0.0
    if peg >= 1.5:
        return 100.0
    if peg <= 1.0:
        return peg * 50.0  # 0 → 0, 1 → 50
    # 1.0 → 50, 1.5 → 100
    return 50.0 + ((peg - 1.0) / 0.5) * 50.0


def composite_score(cagr_s: float, yield_s: float, peg_s: float) -> float:
    """Weighted: CAGR 40 + Yield 30 + PEG 30."""
    return cagr_s * 0.4 + yield_s * 0.3 + peg_s * 0.3


def criterion_6_margin_trend(stock: dict) -> tuple[bool | None, dict]:
    """Gross + Net margin non-decreasing over last 3y (linear slope ≥ 0 for both).

    Using slope of margin vs year-index (0,1,2). Both gross_margin and net_margin
    must have slope ≥ 0 (we allow tiny negative slope as 'noise' threshold but
    Hong's intent is "นิ่งหรือเพิ่ม" = stable-or-rising → strict ≥ 0).
    """
    ym = _drop_partial_latest(stock.get("yearly_metrics") or [])
    last3 = _last_n_years(ym, 3)
    if len(last3) < 3:
        return (None, {"gm": [], "nm": [], "gm_slope": None, "nm_slope": None})

    gms = [_safe(r.get("gross_margin")) for r in last3]
    nms = [_safe(r.get("net_margin")) for r in last3]
    if any(v is None for v in gms) or any(v is None for v in nms):
        return (None, {"gm": gms, "nm": nms, "gm_slope": None, "nm_slope": None})

    # Simple linear slope: (y2 - y0) / 2 — covers monotone enough for 3 pts
    def _slope(vals):
        # least squares slope for x = [0,1,2]
        x_mean = 1.0
        y_mean = sum(vals) / 3
        num = sum((i - x_mean) * (vals[i] - y_mean) for i in range(3))
        den = sum((i - x_mean) ** 2 for i in range(3))
        return num / den if den else 0.0

    gm_slope = _slope(gms)
    nm_slope = _slope(nms)

    # Allow tiny numerical noise tolerance (-0.005 = -0.5% slope per year — basically flat)
    tol = -0.005
    passed = (gm_slope >= tol) and (nm_slope >= tol)
    return (passed, {"gm": gms, "nm": nms, "gm_slope": gm_slope, "nm_slope": nm_slope})


# ----------------------------------------------------------------------------
# Industry median ROE (3y avg) computed across the universe.
# Only stocks with enough data are included. Sectors with < 3 valid samples
# fall back to global threshold 0.15.
# ----------------------------------------------------------------------------

def compute_industry_roe_medians(all_stocks: dict[str, dict]) -> dict[str, float]:
    by_sector = defaultdict(list)
    for sym, st in all_stocks.items():
        sec = st.get("sector") or "N/A"
        ym = _drop_partial_latest(st.get("yearly_metrics") or [])
        last3 = _last_n_years(ym, 3)
        if len(last3) < 3:
            continue
        roes = [_safe(r.get("roe")) for r in last3]
        if any(r is None for r in roes):
            continue
        by_sector[sec].append(sum(roes) / 3)

    out = {}
    for sec, vals in by_sector.items():
        if len(vals) >= 3:
            out[sec] = median(vals)
    return out


# ----------------------------------------------------------------------------
# Universe loader (v3 — all SET + mai common stocks from cache)
# ----------------------------------------------------------------------------

# Sectors / industries to exclude — non-common-stock instruments.
EXCLUDE_SECTORS = {
    "Property Fund & REITs",
    "Infrastructure Fund",
    "ETF",
}


def _is_non_common_by_name(name: str) -> bool:
    """Fallback name-based filter for instruments that slipped past sector filter."""
    if not name:
        return False
    n = name.lower()
    keywords = (
        "real estate investment trust",
        "leasehold property fund",
        "infrastructure fund",
        "depositary receipt",
        " etf",
    )
    for kw in keywords:
        if kw in n:
            return True
    return False


def load_universe_from_cache(cache_date: str) -> tuple[list[str], dict[str, int]]:
    """Return (symbols, filter_stats) for all common stocks in cache_date.

    Filters out:
      - Property Fund & REITs (sector)
      - Infrastructure Fund (sector)
      - ETF (sector or name pattern)
      - REIT / leasehold property fund (by name fallback when sector missing)

    filter_stats:
      - total_cache: total files scanned
      - filtered_by_sector_<sector_name>: per-reason count
      - kept: final kept count
    """
    cache_dir = ROOT / "data" / "screener_cache" / cache_date
    if not cache_dir.exists():
        return [], {"total_cache": 0, "kept": 0}

    kept: list[str] = []
    stats = defaultdict(int)
    for p in sorted(cache_dir.glob("*.BK.json")):
        stats["total_cache"] += 1
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            stats["parse_error"] += 1
            continue
        sym = (data.get("symbol") or p.stem).replace(".BK", "")
        sec = (data.get("sector") or "").strip()
        name = data.get("name") or ""
        if sec in EXCLUDE_SECTORS:
            stats[f"excluded_sector_{sec}"] += 1
            continue
        if _is_non_common_by_name(name):
            stats["excluded_by_name"] += 1
            continue
        kept.append(sym)

    stats["kept"] = len(kept)
    return kept, dict(stats)


# ----------------------------------------------------------------------------
# Main scanner
# ----------------------------------------------------------------------------

def load_stock(sym: str, cache_date: str) -> dict | None:
    cache_path = ROOT / "data" / "screener_cache" / cache_date / f"{sym}.BK.json"
    if not cache_path.exists():
        return None
    try:
        return json.loads(cache_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def fetch_fresh(sym: str) -> dict | None:
    """Fetch via data_adapter if not cached. Slow — keep as fallback."""
    try:
        from data_adapter import fetch_fundamentals  # type: ignore
        return fetch_fundamentals(sym + ".BK")
    except Exception as e:
        print(f"  [WARN] fresh fetch failed for {sym}: {e}", file=sys.stderr)
        return None


def latest_cache_date() -> str:
    cache_root = ROOT / "data" / "screener_cache"
    if not cache_root.exists():
        return ""
    dates = sorted([p.name for p in cache_root.iterdir() if p.is_dir()])
    return dates[-1] if dates else ""


def scan(universe: list[str], cache_date: str, allow_fresh: bool = False,
         version: str = "v2") -> dict:
    """Run Hong Stage 1 on universe. Returns dict of results.

    version: 'v1' (legacy D/E<=1.0 for all) or 'v2' (sector-aware solvency).
    """
    print(f"[scan] universe size = {len(universe)}")
    print(f"[scan] cache date    = {cache_date}")
    print(f"[scan] allow_fresh   = {allow_fresh}")
    print(f"[scan] version       = {version}")

    # Phase 1: load all stocks from cache (incl. those NOT in target universe — needed for industry median)
    all_stocks: dict[str, dict] = {}
    cache_dir = ROOT / "data" / "screener_cache" / cache_date
    if cache_dir.exists():
        for p in cache_dir.glob("*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                sym_clean = (data.get("symbol") or p.stem).replace(".BK", "")
                all_stocks[sym_clean] = data
            except Exception:
                continue
    print(f"[scan] loaded {len(all_stocks)} stocks from cache for industry-median calc")

    # Compute industry medians
    industry_medians = compute_industry_roe_medians(all_stocks)
    print(f"[scan] industry-median ROE computed for {len(industry_medians)} sectors")

    # Phase 2: process target universe
    results = []
    missing = []
    fetch_errors = []
    t0 = time.time()

    for i, sym in enumerate(universe, 1):
        stock = all_stocks.get(sym)
        if stock is None:
            if allow_fresh:
                print(f"[{i}/{len(universe)}] {sym} cache miss — fetching fresh ...")
                stock = fetch_fresh(sym)
                time.sleep(0.5)
            if stock is None:
                missing.append(sym)
                results.append({
                    "symbol": sym,
                    "status": "missing",
                })
                continue

        sec = stock.get("sector") or "N/A"
        industry_roe = industry_medians.get(sec)
        sector_class = classify_sector(sec)

        c1_pass, c1_info = criterion_1_solvency(stock, sector_class, version=version)
        c2_pass, c2_info = criterion_2_roe(stock, industry_roe)
        c3_pass, c3_info = criterion_3_profit_new_high(stock)
        c4_pass, c4_info = criterion_4_cfo_np(stock)
        c5_pass, fwd_pe, fwd_pe_source = criterion_5_fwd_pe(stock)
        c6_pass, c6_info = criterion_6_margin_trend(stock)

        # Pass-count for ranking
        flags = [c1_pass, c2_pass, c3_pass, c4_pass, c5_pass, c6_pass]
        passes = sum(1 for f in flags if f is True)
        nones = sum(1 for f in flags if f is None)
        overall_pass = passes == 6

        results.append({
            "symbol": sym,
            "name": stock.get("name", ""),
            "sector": sec,
            "industry": stock.get("industry", "N/A"),
            "sector_class": sector_class,
            "solvency_rule": c1_info.get("rule"),
            "price": _safe(stock.get("price")),
            "mcap": _safe(stock.get("market_cap")),
            "status": "scanned",
            # Criterion values
            "de_ratio": c1_info.get("de_ratio"),
            "roa_3y_avg": c1_info.get("roa_3y_avg"),
            "roe_3y_avg": c2_info.get("roe_3y_avg"),
            "roe_y0": c2_info["roe_3y"][0] if len(c2_info.get("roe_3y", [])) == 3 else None,
            "roe_y1": c2_info["roe_3y"][1] if len(c2_info.get("roe_3y", [])) == 3 else None,
            "roe_y2": c2_info["roe_3y"][2] if len(c2_info.get("roe_3y", [])) == 3 else None,
            "roe_threshold": c2_info.get("threshold"),
            "profit_latest": c3_info.get("latest"),
            "profit_max_prior_5y": c3_info.get("max_prior"),
            "cfo_np_avg_3y": c4_info.get("avg"),
            "fwd_pe": fwd_pe,
            "fwd_pe_source": fwd_pe_source,
            "gm_slope": c6_info.get("gm_slope"),
            "nm_slope": c6_info.get("nm_slope"),
            # Pass flags (c1 = sector-aware solvency in v2)
            "c1_de_pass": c1_pass,
            "c2_roe_pass": c2_pass,
            "c3_new_high_pass": c3_pass,
            "c4_cfo_pass": c4_pass,
            "c5_fwd_pe_pass": c5_pass,
            "c6_margin_pass": c6_pass,
            "passes_count": passes,
            "nones_count": nones,
            "overall_pass": overall_pass,
        })

    elapsed = time.time() - t0
    print(f"[scan] done in {elapsed:.1f}s")
    return {
        "results": results,
        "missing": missing,
        "fetch_errors": fetch_errors,
        "industry_medians": industry_medians,
        "elapsed_sec": elapsed,
        "cache_date": cache_date,
        "scan_date": datetime.now().strftime("%Y-%m-%d"),
        "universe_size": len(universe),
        "version": version,
    }


# ----------------------------------------------------------------------------
# v4 — Hong Full Philosophy scanner
# ----------------------------------------------------------------------------

def evaluate_v4(stock: dict, sector_class: str, industry_roe_med: float | None) -> dict:
    """Run all 7 hard gates + 3 sweet spot scores for one stock.

    industry_roe_med = ROE 3y avg median of stocks in same sector (decimal),
                       used by gate 5 (relative ROE).
    """
    # Gate 1 — solvency (reuse v2)
    c1_pass, c1_info = criterion_1_solvency(stock, sector_class, version="v2")

    # Gate 2 — cash adequacy (new v4)
    c2_pass, c2_info = cash_adequacy_check(stock)

    # Gate 3 — margin slope (reuse criterion_6_margin_trend, but stricter ≥0)
    ym = _drop_partial_latest(stock.get("yearly_metrics") or [])
    last3 = _last_n_years(ym, 3)
    g3_info = {"gm_slope": None, "nm_slope": None}
    if len(last3) < 3:
        c3_pass = None
    else:
        gms = [_safe(r.get("gross_margin")) for r in last3]
        nms = [_safe(r.get("net_margin")) for r in last3]
        if any(v is None for v in gms) or any(v is None for v in nms):
            c3_pass = None
        else:
            def _slope(vals):
                x_mean = 1.0
                num = sum((i - x_mean) * (vals[i] - sum(vals) / 3) for i in range(3))
                den = sum((i - x_mean) ** 2 for i in range(3))
                return num / den if den else 0.0
            g3_info["gm_slope"] = _slope(gms)
            g3_info["nm_slope"] = _slope(nms)
            # Strict ≥ 0 (tiny tolerance for numerical noise)
            tol = -0.001
            c3_pass = g3_info["gm_slope"] >= tol and g3_info["nm_slope"] >= tol

    # Gate 4 — CFO/NP (reuse v2)
    c4_pass, c4_info = criterion_4_cfo_np(stock)

    # Gate 5 — ROE relative (v4: ROE 3y avg ≥ max(industry_median, 12%))
    last3_roe = _last_n_years(_drop_partial_latest(stock.get("yearly_metrics") or []), 3)
    if len(last3_roe) < 3:
        c5_pass = None
        c5_info = {"roe_3y_avg": None, "threshold": None}
    else:
        roes = [_safe(r.get("roe")) for r in last3_roe]
        if any(r is None for r in roes):
            c5_pass = None
            c5_info = {"roe_3y_avg": None, "threshold": None}
        else:
            roe_avg = sum(roes) / 3
            threshold = max(industry_roe_med or 0.0, 0.12)
            c5_pass = roe_avg >= threshold
            c5_info = {"roe_3y_avg": roe_avg, "threshold": threshold,
                       "industry_median": industry_roe_med}

    # Gate 6 — new high profit (reuse v2)
    c6_pass, c6_info = criterion_3_profit_new_high(stock)

    # Gate 7 — Forward PE ≤ 15 (reuse v2 with trailing fallback)
    c7_pass, fwd_pe, fwd_pe_source = criterion_5_fwd_pe(stock)

    # Hard gate all-pass
    gates = [c1_pass, c2_pass, c3_pass, c4_pass, c5_pass, c6_pass, c7_pass]
    all_pass = all(g is True for g in gates)

    # Sweet spot scores
    cagr = earnings_cagr_3y(stock)
    div_y = dividend_yield_pct(stock)

    # PEG: use earnings_growth (decimal in cache → convert to percent points for peg_ratio)
    growth_dec = _safe(stock.get("earnings_growth"))
    # Prefer 3y CAGR for PEG when earnings_growth missing or non-positive
    if growth_dec is None or growth_dec <= 0:
        growth_dec = cagr if (cagr is not None and cagr > 0) else None
    growth_pct = (growth_dec * 100.0) if growth_dec is not None else None

    peg = peg_ratio(growth_pct, fwd_pe)

    s_cagr = cagr_score(cagr)
    s_yield = yield_score(div_y)
    s_peg = peg_score(peg)
    s_comp = composite_score(s_cagr, s_yield, s_peg)

    return {
        "all_pass": all_pass,
        "gate_pass": {
            "g1_solvency": c1_pass,
            "g2_cash_adequacy": c2_pass,
            "g3_margin_slope": c3_pass,
            "g4_cfo_np": c4_pass,
            "g5_roe_relative": c5_pass,
            "g6_new_high": c6_pass,
            "g7_fwd_pe": c7_pass,
        },
        "gate_info": {
            "g1": c1_info,
            "g2": c2_info,
            "g3": g3_info,
            "g4": c4_info,
            "g5": c5_info,
            "g6": c6_info,
            "g7": {"fwd_pe": fwd_pe, "source": fwd_pe_source},
        },
        "metrics": {
            "cagr_3y": cagr,
            "dividend_yield_pct": div_y,
            "peg": peg,
            "growth_used_pct": growth_pct,
            "fwd_pe": fwd_pe,
            "roe_3y_avg": c5_info.get("roe_3y_avg"),
        },
        "scores": {
            "cagr_score": s_cagr,
            "yield_score": s_yield,
            "peg_score": s_peg,
            "composite": s_comp,
        },
    }


def evaluate_v5(stock: dict, sector_class: str, industry_roe_med: float | None) -> dict:
    """v5 — Same as v4 but Gate 2 (cash adequacy) is REMOVED.

    Cache has no `short_term_debt` and no `dividends_paid` per FY — v4 used proxies
    (0.3 * total_debt + dps * shares) which we no longer trust. v5 skips this
    gate entirely. Every survivor is flagged `manual_cash_check = "PENDING"` so
    Stage 2 manual review still happens.

    Returns dict with the same shape as evaluate_v4() except:
      - `gate_pass` has 6 keys (no `g2_cash_adequacy`)
      - `gate_info` has 6 keys (no `g2`)
      - `manual_cash_check` = "PENDING" (literal string for every result)
    """
    # Gate 1 — solvency
    c1_pass, c1_info = criterion_1_solvency(stock, sector_class, version="v2")

    # Gate 3 — margin slope (strict ≥ 0)
    ym = _drop_partial_latest(stock.get("yearly_metrics") or [])
    last3 = _last_n_years(ym, 3)
    g3_info = {"gm_slope": None, "nm_slope": None}
    if len(last3) < 3:
        c3_pass = None
    else:
        gms = [_safe(r.get("gross_margin")) for r in last3]
        nms = [_safe(r.get("net_margin")) for r in last3]
        if any(v is None for v in gms) or any(v is None for v in nms):
            c3_pass = None
        else:
            def _slope(vals):
                x_mean = 1.0
                num = sum((i - x_mean) * (vals[i] - sum(vals) / 3) for i in range(3))
                den = sum((i - x_mean) ** 2 for i in range(3))
                return num / den if den else 0.0
            g3_info["gm_slope"] = _slope(gms)
            g3_info["nm_slope"] = _slope(nms)
            tol = -0.001
            c3_pass = g3_info["gm_slope"] >= tol and g3_info["nm_slope"] >= tol

    # Gate 4 — CFO/NP
    c4_pass, c4_info = criterion_4_cfo_np(stock)

    # Gate 5 — ROE relative
    last3_roe = _last_n_years(_drop_partial_latest(stock.get("yearly_metrics") or []), 3)
    if len(last3_roe) < 3:
        c5_pass = None
        c5_info = {"roe_3y_avg": None, "threshold": None}
    else:
        roes = [_safe(r.get("roe")) for r in last3_roe]
        if any(r is None for r in roes):
            c5_pass = None
            c5_info = {"roe_3y_avg": None, "threshold": None}
        else:
            roe_avg = sum(roes) / 3
            threshold = max(industry_roe_med or 0.0, 0.12)
            c5_pass = roe_avg >= threshold
            c5_info = {"roe_3y_avg": roe_avg, "threshold": threshold,
                       "industry_median": industry_roe_med}

    # Gate 6 — new high profit
    c6_pass, c6_info = criterion_3_profit_new_high(stock)

    # Gate 7 — Forward PE ≤ 15
    c7_pass, fwd_pe, fwd_pe_source = criterion_5_fwd_pe(stock)

    # 6 hard gates — Gate 2 removed
    gates = [c1_pass, c3_pass, c4_pass, c5_pass, c6_pass, c7_pass]
    all_pass = all(g is True for g in gates)

    # Sweet spot scores (unchanged from v4)
    cagr = earnings_cagr_3y(stock)
    div_y = dividend_yield_pct(stock)

    growth_dec = _safe(stock.get("earnings_growth"))
    if growth_dec is None or growth_dec <= 0:
        growth_dec = cagr if (cagr is not None and cagr > 0) else None
    growth_pct = (growth_dec * 100.0) if growth_dec is not None else None

    peg = peg_ratio(growth_pct, fwd_pe)

    s_cagr = cagr_score(cagr)
    s_yield = yield_score(div_y)
    s_peg = peg_score(peg)
    s_comp = composite_score(s_cagr, s_yield, s_peg)

    return {
        "all_pass": all_pass,
        "manual_cash_check": "PENDING",  # Gate 2 removed — always pending Stage 2
        "gate_pass": {
            "g1_solvency": c1_pass,
            "g3_margin_slope": c3_pass,
            "g4_cfo_np": c4_pass,
            "g5_roe_relative": c5_pass,
            "g6_new_high": c6_pass,
            "g7_fwd_pe": c7_pass,
        },
        "gate_info": {
            "g1": c1_info,
            "g3": g3_info,
            "g4": c4_info,
            "g5": c5_info,
            "g6": c6_info,
            "g7": {"fwd_pe": fwd_pe, "source": fwd_pe_source},
        },
        "metrics": {
            "cagr_3y": cagr,
            "dividend_yield_pct": div_y,
            "peg": peg,
            "growth_used_pct": growth_pct,
            "fwd_pe": fwd_pe,
            "roe_3y_avg": c5_info.get("roe_3y_avg"),
        },
        "scores": {
            "cagr_score": s_cagr,
            "yield_score": s_yield,
            "peg_score": s_peg,
            "composite": s_comp,
        },
    }


def scan_v5(universe: list[str], cache_date: str) -> dict:
    """v5 scan — 6 hard gates (no cash adequacy) + composite score ranking."""
    print(f"[v5 scan] universe size = {len(universe)}")
    print(f"[v5 scan] cache date    = {cache_date}")

    all_stocks: dict[str, dict] = {}
    cache_dir = ROOT / "data" / "screener_cache" / cache_date
    if cache_dir.exists():
        for p in cache_dir.glob("*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                sym_clean = (data.get("symbol") or p.stem).replace(".BK", "")
                all_stocks[sym_clean] = data
            except Exception:
                continue
    print(f"[v5 scan] loaded {len(all_stocks)} stocks from cache")

    industry_medians = compute_industry_roe_medians(all_stocks)
    print(f"[v5 scan] industry-median ROE computed for {len(industry_medians)} sectors")

    results = []
    missing = []
    gate_fail_counts = defaultdict(int)
    t0 = time.time()

    for i, sym in enumerate(universe, 1):
        stock = all_stocks.get(sym)
        if stock is None:
            missing.append(sym)
            results.append({"symbol": sym, "status": "missing"})
            continue

        sec = stock.get("sector") or "N/A"
        sector_class = classify_sector(sec)
        ind_med = industry_medians.get(sec)

        ev = evaluate_v5(stock, sector_class, ind_med)
        for g, v in ev["gate_pass"].items():
            if v is False:
                gate_fail_counts[g] += 1
            elif v is None:
                gate_fail_counts[g + "_na"] += 1

        results.append({
            "symbol": sym,
            "name": stock.get("name", ""),
            "sector": sec,
            "sector_class": sector_class,
            "status": "scanned",
            "all_pass": ev["all_pass"],
            "manual_cash_check": ev["manual_cash_check"],
            "gate_pass": ev["gate_pass"],
            "gate_info": ev["gate_info"],
            "metrics": ev["metrics"],
            "scores": ev["scores"],
            "price": _safe(stock.get("price")),
            "mcap": _safe(stock.get("market_cap")),
        })

    elapsed = time.time() - t0
    print(f"[v5 scan] done in {elapsed:.1f}s")

    return {
        "results": results,
        "missing": missing,
        "industry_medians": industry_medians,
        "gate_fail_counts": dict(gate_fail_counts),
        "elapsed_sec": elapsed,
        "cache_date": cache_date,
        "scan_date": datetime.now().strftime("%Y-%m-%d"),
        "universe_size": len(universe),
        "version": "v5",
    }


def print_v5_report(result: dict, top_n: int = 30) -> None:
    """Print v5 report to stdout — 6 gates + manual cash check warning."""
    rows = result["results"]
    scanned = [r for r in rows if r.get("status") == "scanned"]
    passed = [r for r in scanned if r.get("all_pass") is True]
    passed_sorted = sorted(passed, key=lambda r: -(r["scores"]["composite"]))

    print()
    print("=" * 80)
    print("Hong Scanner v5 (Skip Gate 2 — Cash Adequacy needs Manual Review)")
    print("=" * 80)
    print()
    print(f"Universe: {result['universe_size']} stocks")
    print(f"Scanned with data: {len(scanned)}")
    print(f"Passed 6 hard gates: {len(passed)} stocks")
    print()
    print("Gate failure breakdown (6 gates):")
    gate_labels = {
        "g1_solvency": "Gate 1 (Solvency D/E or bank ROA)",
        "g3_margin_slope": "Gate 3 (Margin slope GM+NM)",
        "g4_cfo_np": "Gate 4 (CFO/NP >= 0.8)",
        "g5_roe_relative": "Gate 5 (ROE >= max(industry, 12%))",
        "g6_new_high": "Gate 6 (Profit new high 5y)",
        "g7_fwd_pe": "Gate 7 (Fwd PE <= 15)",
    }
    gfc = result["gate_fail_counts"]
    for k, label in gate_labels.items():
        failed = gfc.get(k, 0)
        na = gfc.get(k + "_na", 0)
        print(f"- {label}: {failed} failed, {na} no-data")
    print("(Gate 2 removed — manual review needed for cash adequacy)")
    print()
    print(f"Top {top_n} by Composite Score:")
    print("=" * 80)
    print()
    print(f"{'Rank':>4} | {'Symbol':<8} | {'Name':<28} | {'Sector':<22} | {'Comp':>5} | {'CAGR':>6} | {'Yield':>6} | {'PEG':>5} | {'ROE':>6} | {'FwdPE':>6} | {'Cash':<8}")
    print("-" * 140)
    for i, r in enumerate(passed_sorted[:top_n], 1):
        m = r["metrics"]
        s = r["scores"]
        cagr_str = f"{m['cagr_3y']*100:.1f}%" if m['cagr_3y'] is not None else "n/a"
        y_str = f"{m['dividend_yield_pct']:.1f}%" if m['dividend_yield_pct'] is not None else "n/a"
        peg_str = f"{m['peg']:.2f}" if m['peg'] is not None else "n/a"
        roe_str = f"{m['roe_3y_avg']*100:.1f}%" if m['roe_3y_avg'] is not None else "n/a"
        fpe_str = f"{m['fwd_pe']:.1f}" if m['fwd_pe'] is not None else "n/a"
        name = (r['name'] or '')[:28]
        sector = (r['sector'] or '')[:22]
        cash_str = r.get("manual_cash_check", "PENDING")
        print(f"{i:>4} | {r['symbol']:<8} | {name:<28} | {sector:<22} | {s['composite']:>5.1f} | {cagr_str:>6} | {y_str:>6} | {peg_str:>5} | {roe_str:>6} | {fpe_str:>6} | {cash_str:<8}")
    print()
    print("NOTE: 'Cash' column = MANUAL_CHECK_NEEDED for cash adequacy (Stage 2).")
    print()


def write_v5_csv(result: dict, out_path: Path) -> None:
    """Write v5 CSV with 6 gates + manual_cash_check column."""
    rows = result["results"]
    if not rows:
        out_path.write_text("", encoding="utf-8")
        return

    columns = [
        "symbol", "name", "sector", "sector_class", "status",
        "all_pass", "manual_cash_check",
        "g1_solvency", "g3_margin_slope", "g4_cfo_np",
        "g5_roe_relative", "g6_new_high", "g7_fwd_pe",
        "composite", "cagr_score", "yield_score", "peg_score",
        "cagr_3y_pct", "dividend_yield_pct", "peg",
        "roe_3y_avg_pct", "fwd_pe",
        "price", "mcap",
    ]

    def _bool_str(v):
        if v is True: return "YES"
        if v is False: return "NO"
        return "NA"

    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            if r.get("status") != "scanned":
                w.writerow({"symbol": r.get("symbol"), "status": r.get("status")})
                continue
            gp = r["gate_pass"]
            m = r["metrics"]
            s = r["scores"]
            row = {
                "symbol": r["symbol"],
                "name": r.get("name", ""),
                "sector": r.get("sector", ""),
                "sector_class": r.get("sector_class", ""),
                "status": "scanned",
                "all_pass": _bool_str(r.get("all_pass")),
                "manual_cash_check": r.get("manual_cash_check", "PENDING") if r.get("all_pass") is True else "N/A",
                "g1_solvency": _bool_str(gp.get("g1_solvency")),
                "g3_margin_slope": _bool_str(gp.get("g3_margin_slope")),
                "g4_cfo_np": _bool_str(gp.get("g4_cfo_np")),
                "g5_roe_relative": _bool_str(gp.get("g5_roe_relative")),
                "g6_new_high": _bool_str(gp.get("g6_new_high")),
                "g7_fwd_pe": _bool_str(gp.get("g7_fwd_pe")),
                "composite": round(s["composite"], 2),
                "cagr_score": round(s["cagr_score"], 2),
                "yield_score": round(s["yield_score"], 2),
                "peg_score": round(s["peg_score"], 2),
                "cagr_3y_pct": round(m["cagr_3y"] * 100, 2) if m.get("cagr_3y") is not None else None,
                "dividend_yield_pct": round(m["dividend_yield_pct"], 2) if m.get("dividend_yield_pct") is not None else None,
                "peg": round(m["peg"], 3) if m.get("peg") is not None else None,
                "roe_3y_avg_pct": round(m["roe_3y_avg"] * 100, 2) if m.get("roe_3y_avg") is not None else None,
                "fwd_pe": round(m["fwd_pe"], 2) if m.get("fwd_pe") is not None else None,
                "price": r.get("price"),
                "mcap": r.get("mcap"),
            }
            w.writerow(row)


def write_v5_md(result: dict, out_path: Path) -> None:
    """Write v5 markdown report."""
    rows = result["results"]
    scanned = [r for r in rows if r.get("status") == "scanned"]
    passed = [r for r in scanned if r.get("all_pass") is True]
    passed_sorted = sorted(passed, key=lambda r: -(r["scores"]["composite"]))

    lines = []
    lines.append(f"# Hong Stage 1 Scan — v5 (Skip Gate 2) — {result['scan_date']}\n")
    lines.append(f"> **Scan date:** {result['scan_date']}  ")
    lines.append(f"> **Data cache date:** {result['cache_date']}  ")
    lines.append(f"> **Universe:** {result['universe_size']}  ")
    lines.append(f"> **Scanned:** {len(scanned)}  ")
    lines.append(f"> **Passed 6 hard gates:** **{len(passed)}**  ")
    lines.append(f"> **Elapsed:** {result['elapsed_sec']:.1f}s  ")
    lines.append("")
    lines.append("> **WARNING:** Gate 2 (Cash Adequacy) removed in v5 because cache has no")
    lines.append("> `short_term_debt` and no `dividends_paid` per FY — v4 proxies were unreliable.")
    lines.append("> Every survivor below is flagged `MANUAL_CHECK_NEEDED: cash_adequacy` and must be")
    lines.append("> verified in Stage 2 manual review (annual report — short-term debt + dividends paid).")
    lines.append("")
    lines.append("## 6 Hard Gates\n")
    lines.append("| # | Gate | Threshold |")
    lines.append("|---|------|-----------|")
    lines.append("| 1 | Solvency (sector-aware) | default D/E ≤ 1.0, retail ≤ 2.5, bank ROA 3y ≥ 1% |")
    lines.append("| 3 | Margin slope | gm 3y slope ≥ 0 AND nm 3y slope ≥ 0 |")
    lines.append("| 4 | CFO / Net profit | 3y avg ≥ 0.8 |")
    lines.append("| 5 | ROE relative | 3y avg ≥ max(industry median, 12%) |")
    lines.append("| 6 | Profit new high | latest = max of last 5y |")
    lines.append("| 7 | Forward PE | ≤ 15 (trailing fallback) |")
    lines.append("")
    lines.append("**Gate 2 (Cash adequacy) REMOVED** — manual review required.")
    lines.append("")
    lines.append("## Sweet Spot Composite (rank survivors)\n")
    lines.append("Composite = CAGR_score × 0.4 + Yield_score × 0.3 + PEG_score × 0.3\n")
    lines.append("- **CAGR 3y:** 0%→0, 26%+→100 capped")
    lines.append("- **Dividend yield:** 0→0, 4%→70, 7%+→100")
    lines.append("- **PEG (Fwd PE / growth%):** 0→0, 1.0→50, 1.5+→100")
    lines.append("")

    # Gate failure breakdown
    lines.append("## Gate failure breakdown (6 gates)\n")
    gate_labels = {
        "g1_solvency": "Gate 1 Solvency",
        "g3_margin_slope": "Gate 3 Margin slope",
        "g4_cfo_np": "Gate 4 CFO/NP",
        "g5_roe_relative": "Gate 5 ROE relative",
        "g6_new_high": "Gate 6 New high",
        "g7_fwd_pe": "Gate 7 Fwd PE",
    }
    gfc = result["gate_fail_counts"]
    lines.append("| Gate | Failed | No-data |")
    lines.append("|------|--------|---------|")
    for k, label in gate_labels.items():
        lines.append(f"| {label} | {gfc.get(k, 0)} | {gfc.get(k + '_na', 0)} |")
    lines.append("")

    # Top 30
    lines.append(f"## Top 30 by Composite Score ({len(passed_sorted)} survivors)\n")
    if passed_sorted:
        lines.append("| Rank | Sym | Name | Sector | Composite | CAGR3y | Yield | PEG | ROE | FwdPE | Manual_Cash_Check |")
        lines.append("|------|-----|------|--------|-----------|--------|-------|-----|-----|-------|-------------------|")
        for i, r in enumerate(passed_sorted[:30], 1):
            m = r["metrics"]
            s = r["scores"]
            cagr_str = f"{m['cagr_3y']*100:.1f}%" if m['cagr_3y'] is not None else "n/a"
            y_str = f"{m['dividend_yield_pct']:.1f}%" if m['dividend_yield_pct'] is not None else "n/a"
            peg_str = f"{m['peg']:.2f}" if m['peg'] is not None else "n/a"
            roe_str = f"{m['roe_3y_avg']*100:.1f}%" if m['roe_3y_avg'] is not None else "n/a"
            fpe_str = f"{m['fwd_pe']:.1f}" if m['fwd_pe'] is not None else "n/a"
            name = (r.get('name') or '')[:25]
            sector = (r.get('sector') or '')[:18]
            cash_str = r.get("manual_cash_check", "PENDING")
            lines.append(
                f"| {i} | {r['symbol']} | {name} | {sector} | {s['composite']:.1f} | "
                f"{cagr_str} | {y_str} | {peg_str} | {roe_str} | {fpe_str} | {cash_str} |"
            )
    else:
        lines.append("_No stocks passed all 6 hard gates._")
    lines.append("")

    lines.append("## Limitations & Notes\n")
    lines.append("- **Gate 2 removed:** Cache has no `short_term_debt` (only `total_debt`) and no `dividends_paid` per FY. v4 proxies (0.3 * total_debt + dps * shares) were unreliable. Every survivor is flagged `MANUAL_CHECK_NEEDED: cash_adequacy` — Stage 2 must verify from annual report.")
    lines.append("- **CAGR 3y:** computed from net_income series (3 intervals → 4 data points). Returns -100% if latest year unprofitable, None if 3y-ago year ≤ 0.")
    lines.append("- **PEG growth source:** prefers `earnings_growth` (yfinance fwd), falls back to 3y CAGR.")
    lines.append("- **Bank gate 1:** banks evaluated by ROA 3y ≥ 1% instead of D/E.")
    lines.append("- **Industry-median ROE:** only sectors with ≥3 valid samples; otherwise gate 5 threshold = 12% absolute floor.")
    lines.append("- **Stage 1 only:** quantitative pass — Stage 2 manual (management, moat, governance, **cash adequacy**) still required.")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def scan_v4(universe: list[str], cache_date: str) -> dict:
    """v4 scan — 7 hard gates + composite score ranking."""
    print(f"[v4 scan] universe size = {len(universe)}")
    print(f"[v4 scan] cache date    = {cache_date}")

    # Phase 1 — load all stocks (for industry median)
    all_stocks: dict[str, dict] = {}
    cache_dir = ROOT / "data" / "screener_cache" / cache_date
    if cache_dir.exists():
        for p in cache_dir.glob("*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                sym_clean = (data.get("symbol") or p.stem).replace(".BK", "")
                all_stocks[sym_clean] = data
            except Exception:
                continue
    print(f"[v4 scan] loaded {len(all_stocks)} stocks from cache")

    industry_medians = compute_industry_roe_medians(all_stocks)
    print(f"[v4 scan] industry-median ROE computed for {len(industry_medians)} sectors")

    results = []
    missing = []
    gate_fail_counts = defaultdict(int)
    t0 = time.time()

    for i, sym in enumerate(universe, 1):
        stock = all_stocks.get(sym)
        if stock is None:
            missing.append(sym)
            results.append({"symbol": sym, "status": "missing"})
            continue

        sec = stock.get("sector") or "N/A"
        sector_class = classify_sector(sec)
        ind_med = industry_medians.get(sec)

        ev = evaluate_v4(stock, sector_class, ind_med)
        # Count gate failures (only count is False — None = data missing, count separately)
        for g, v in ev["gate_pass"].items():
            if v is False:
                gate_fail_counts[g] += 1
            elif v is None:
                gate_fail_counts[g + "_na"] += 1

        results.append({
            "symbol": sym,
            "name": stock.get("name", ""),
            "sector": sec,
            "sector_class": sector_class,
            "status": "scanned",
            "all_pass": ev["all_pass"],
            "gate_pass": ev["gate_pass"],
            "gate_info": ev["gate_info"],
            "metrics": ev["metrics"],
            "scores": ev["scores"],
            "price": _safe(stock.get("price")),
            "mcap": _safe(stock.get("market_cap")),
        })

    elapsed = time.time() - t0
    print(f"[v4 scan] done in {elapsed:.1f}s")

    return {
        "results": results,
        "missing": missing,
        "industry_medians": industry_medians,
        "gate_fail_counts": dict(gate_fail_counts),
        "elapsed_sec": elapsed,
        "cache_date": cache_date,
        "scan_date": datetime.now().strftime("%Y-%m-%d"),
        "universe_size": len(universe),
        "version": "v4",
    }


def print_v4_report(result: dict, top_n: int = 30) -> None:
    """Print v4 report to stdout in the requested format."""
    rows = result["results"]
    scanned = [r for r in rows if r.get("status") == "scanned"]
    passed = [r for r in scanned if r.get("all_pass") is True]
    passed_sorted = sorted(passed, key=lambda r: -(r["scores"]["composite"]))

    print()
    print("=" * 60)
    print("Hong Scanner v4 (Reset - Full Philosophy)")
    print("=" * 60)
    print()
    print(f"Universe: {result['universe_size']} stocks")
    print(f"Scanned with data: {len(scanned)}")
    print(f"Passed all 7 hard gates: {len(passed)} stocks")
    print()
    print("Gate failure breakdown:")
    gate_labels = {
        "g1_solvency": "Gate 1 (Solvency D/E or bank ROA)",
        "g2_cash_adequacy": "Gate 2 (Cash adequacy)",
        "g3_margin_slope": "Gate 3 (Margin slope GM+NM)",
        "g4_cfo_np": "Gate 4 (CFO/NP >= 0.8)",
        "g5_roe_relative": "Gate 5 (ROE >= max(industry, 12%))",
        "g6_new_high": "Gate 6 (Profit new high 5y)",
        "g7_fwd_pe": "Gate 7 (Fwd PE <= 15)",
    }
    gfc = result["gate_fail_counts"]
    for k, label in gate_labels.items():
        failed = gfc.get(k, 0)
        na = gfc.get(k + "_na", 0)
        print(f"- {label}: {failed} failed, {na} no-data")
    print()
    print(f"Top {top_n} by Composite Score:")
    print("=" * 60)
    print()
    print(f"{'Rank':>4} | {'Symbol':<8} | {'Name':<28} | {'Sector':<24} | {'Comp':>5} | {'CAGR':>6} | {'Yield':>6} | {'PEG':>5} | {'ROE':>6} | {'FwdPE':>6}")
    print("-" * 130)
    for i, r in enumerate(passed_sorted[:top_n], 1):
        m = r["metrics"]
        s = r["scores"]
        cagr_str = f"{m['cagr_3y']*100:.1f}%" if m['cagr_3y'] is not None else "n/a"
        y_str = f"{m['dividend_yield_pct']:.1f}%" if m['dividend_yield_pct'] is not None else "n/a"
        peg_str = f"{m['peg']:.2f}" if m['peg'] is not None else "n/a"
        roe_str = f"{m['roe_3y_avg']*100:.1f}%" if m['roe_3y_avg'] is not None else "n/a"
        fpe_str = f"{m['fwd_pe']:.1f}" if m['fwd_pe'] is not None else "n/a"
        name = (r['name'] or '')[:28]
        sector = (r['sector'] or '')[:24]
        print(f"{i:>4} | {r['symbol']:<8} | {name:<28} | {sector:<24} | {s['composite']:>5.1f} | {cagr_str:>6} | {y_str:>6} | {peg_str:>5} | {roe_str:>6} | {fpe_str:>6}")
    print()


def write_v4_csv(result: dict, out_path: Path) -> None:
    """Write v4 CSV with full per-stock detail."""
    rows = result["results"]
    if not rows:
        out_path.write_text("", encoding="utf-8")
        return

    columns = [
        "symbol", "name", "sector", "sector_class", "status",
        "all_pass",
        "g1_solvency", "g2_cash_adequacy", "g3_margin_slope", "g4_cfo_np",
        "g5_roe_relative", "g6_new_high", "g7_fwd_pe",
        "composite", "cagr_score", "yield_score", "peg_score",
        "cagr_3y_pct", "dividend_yield_pct", "peg",
        "roe_3y_avg_pct", "fwd_pe",
        "price", "mcap",
    ]

    def _bool_str(v):
        if v is True: return "YES"
        if v is False: return "NO"
        return "NA"

    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            if r.get("status") != "scanned":
                w.writerow({"symbol": r.get("symbol"), "status": r.get("status")})
                continue
            gp = r["gate_pass"]
            m = r["metrics"]
            s = r["scores"]
            row = {
                "symbol": r["symbol"],
                "name": r.get("name", ""),
                "sector": r.get("sector", ""),
                "sector_class": r.get("sector_class", ""),
                "status": "scanned",
                "all_pass": _bool_str(r.get("all_pass")),
                "g1_solvency": _bool_str(gp.get("g1_solvency")),
                "g2_cash_adequacy": _bool_str(gp.get("g2_cash_adequacy")),
                "g3_margin_slope": _bool_str(gp.get("g3_margin_slope")),
                "g4_cfo_np": _bool_str(gp.get("g4_cfo_np")),
                "g5_roe_relative": _bool_str(gp.get("g5_roe_relative")),
                "g6_new_high": _bool_str(gp.get("g6_new_high")),
                "g7_fwd_pe": _bool_str(gp.get("g7_fwd_pe")),
                "composite": round(s["composite"], 2),
                "cagr_score": round(s["cagr_score"], 2),
                "yield_score": round(s["yield_score"], 2),
                "peg_score": round(s["peg_score"], 2),
                "cagr_3y_pct": round(m["cagr_3y"] * 100, 2) if m.get("cagr_3y") is not None else None,
                "dividend_yield_pct": round(m["dividend_yield_pct"], 2) if m.get("dividend_yield_pct") is not None else None,
                "peg": round(m["peg"], 3) if m.get("peg") is not None else None,
                "roe_3y_avg_pct": round(m["roe_3y_avg"] * 100, 2) if m.get("roe_3y_avg") is not None else None,
                "fwd_pe": round(m["fwd_pe"], 2) if m.get("fwd_pe") is not None else None,
                "price": r.get("price"),
                "mcap": r.get("mcap"),
            }
            w.writerow(row)


def write_v4_md(result: dict, out_path: Path) -> None:
    """Write v4 markdown report."""
    rows = result["results"]
    scanned = [r for r in rows if r.get("status") == "scanned"]
    passed = [r for r in scanned if r.get("all_pass") is True]
    passed_sorted = sorted(passed, key=lambda r: -(r["scores"]["composite"]))

    lines = []
    lines.append(f"# Hong Stage 1 Scan — v4 Full Philosophy — {result['scan_date']}\n")
    lines.append(f"> **Scan date:** {result['scan_date']}  ")
    lines.append(f"> **Data cache date:** {result['cache_date']}  ")
    lines.append(f"> **Universe:** {result['universe_size']}  ")
    lines.append(f"> **Scanned:** {len(scanned)}  ")
    lines.append(f"> **Passed 7 hard gates:** **{len(passed)}**  ")
    lines.append(f"> **Elapsed:** {result['elapsed_sec']:.1f}s  ")
    lines.append("")
    lines.append("## 7 Hard Gates\n")
    lines.append("| # | Gate | Threshold |")
    lines.append("|---|------|-----------|")
    lines.append("| 1 | Solvency (sector-aware) | default D/E ≤ 1.0, retail ≤ 2.5, bank ROA 3y ≥ 1% |")
    lines.append("| 2 | Cash adequacy | cash ≥ (0.3×total_debt + est annual div) |")
    lines.append("| 3 | Margin slope | gm 3y slope ≥ 0 AND nm 3y slope ≥ 0 |")
    lines.append("| 4 | CFO / Net profit | 3y avg ≥ 0.8 |")
    lines.append("| 5 | ROE relative | 3y avg ≥ max(industry median, 12%) |")
    lines.append("| 6 | Profit new high | latest = max of last 5y |")
    lines.append("| 7 | Forward PE | ≤ 15 (trailing fallback) |")
    lines.append("")
    lines.append("## Sweet Spot Composite (rank survivors)\n")
    lines.append("Composite = CAGR_score × 0.4 + Yield_score × 0.3 + PEG_score × 0.3\n")
    lines.append("- **CAGR 3y:** 0%→0, 26%+→100 capped")
    lines.append("- **Dividend yield:** 0→0, 4%→70, 7%+→100")
    lines.append("- **PEG (Fwd PE / growth%):** 0→0, 1.0→50, 1.5+→100")
    lines.append("")

    # Gate failure breakdown
    lines.append("## Gate failure breakdown\n")
    gate_labels = {
        "g1_solvency": "Gate 1 Solvency",
        "g2_cash_adequacy": "Gate 2 Cash adequacy",
        "g3_margin_slope": "Gate 3 Margin slope",
        "g4_cfo_np": "Gate 4 CFO/NP",
        "g5_roe_relative": "Gate 5 ROE relative",
        "g6_new_high": "Gate 6 New high",
        "g7_fwd_pe": "Gate 7 Fwd PE",
    }
    gfc = result["gate_fail_counts"]
    lines.append("| Gate | Failed | No-data |")
    lines.append("|------|--------|---------|")
    for k, label in gate_labels.items():
        lines.append(f"| {label} | {gfc.get(k, 0)} | {gfc.get(k + '_na', 0)} |")
    lines.append("")

    # Top 30
    lines.append(f"## Top 30 by Composite Score ({len(passed_sorted)} survivors)\n")
    if passed_sorted:
        lines.append("| Rank | Sym | Name | Sector | Composite | CAGR3y | Yield | PEG | ROE | FwdPE |")
        lines.append("|------|-----|------|--------|-----------|--------|-------|-----|-----|-------|")
        for i, r in enumerate(passed_sorted[:30], 1):
            m = r["metrics"]
            s = r["scores"]
            cagr_str = f"{m['cagr_3y']*100:.1f}%" if m['cagr_3y'] is not None else "n/a"
            y_str = f"{m['dividend_yield_pct']:.1f}%" if m['dividend_yield_pct'] is not None else "n/a"
            peg_str = f"{m['peg']:.2f}" if m['peg'] is not None else "n/a"
            roe_str = f"{m['roe_3y_avg']*100:.1f}%" if m['roe_3y_avg'] is not None else "n/a"
            fpe_str = f"{m['fwd_pe']:.1f}" if m['fwd_pe'] is not None else "n/a"
            name = (r.get('name') or '')[:25]
            sector = (r.get('sector') or '')[:18]
            lines.append(
                f"| {i} | {r['symbol']} | {name} | {sector} | {s['composite']:.1f} | "
                f"{cagr_str} | {y_str} | {peg_str} | {roe_str} | {fpe_str} |"
            )
    else:
        lines.append("_No stocks passed all 7 hard gates._")
    lines.append("")

    # Limitations
    lines.append("## Limitations & Notes\n")
    lines.append("- **Short-term debt proxy:** 30% of total_debt (cache has no st_debt breakdown). May over/under-estimate cash adequacy.")
    lines.append("- **Annual dividend estimate:** dps × (market_cap / price). Approximate.")
    lines.append("- **CAGR 3y:** computed from net_income series (3 intervals → 4 data points). Returns -100% if latest year unprofitable, None if 3y-ago year ≤ 0.")
    lines.append("- **PEG growth source:** prefers `earnings_growth` (yfinance fwd), falls back to 3y CAGR.")
    lines.append("- **Bank gate 1:** banks evaluated by ROA 3y ≥ 1% instead of D/E.")
    lines.append("- **Industry-median ROE:** only sectors with ≥3 valid samples; otherwise gate 5 threshold = 12% absolute floor.")
    lines.append("- **Stage 1 only:** quantitative pass — Stage 2 manual (management, moat, governance) still required.")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_csv(scan_result: dict, out_path: Path) -> None:
    rows = scan_result["results"]
    if not rows:
        out_path.write_text("", encoding="utf-8")
        return

    columns = [
        "symbol", "name", "sector", "industry", "sector_class", "solvency_rule", "status",
        "overall_pass", "passes_count", "nones_count",
        "c1_de_pass", "de_ratio", "roa_3y_avg",
        "c2_roe_pass", "roe_3y_avg", "roe_y0", "roe_y1", "roe_y2", "roe_threshold",
        "c3_new_high_pass", "profit_latest", "profit_max_prior_5y",
        "c4_cfo_pass", "cfo_np_avg_3y",
        "c5_fwd_pe_pass", "fwd_pe", "fwd_pe_source",
        "c6_margin_pass", "gm_slope", "nm_slope",
        "price", "mcap",
    ]

    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            row = dict(r)
            # Bools to YES/NO for readability
            for k in ["overall_pass", "c1_de_pass", "c2_roe_pass", "c3_new_high_pass",
                      "c4_cfo_pass", "c5_fwd_pe_pass", "c6_margin_pass"]:
                v = row.get(k)
                if v is True:
                    row[k] = "YES"
                elif v is False:
                    row[k] = "NO"
                else:
                    row[k] = "NA"
            # Round floats
            for k in ["de_ratio", "roa_3y_avg", "roe_3y_avg", "roe_y0", "roe_y1", "roe_y2", "roe_threshold",
                      "cfo_np_avg_3y", "fwd_pe", "gm_slope", "nm_slope"]:
                v = row.get(k)
                if isinstance(v, float):
                    row[k] = round(v, 4)
            w.writerow(row)


def write_md(scan_result: dict, out_path: Path) -> None:
    rows = scan_result["results"]
    passed = [r for r in rows if r.get("overall_pass") is True]
    near_miss = [r for r in rows if r.get("passes_count") == 5 and r.get("status") == "scanned"]
    missing = scan_result["missing"]
    scanned = [r for r in rows if r.get("status") == "scanned"]

    # Rank passed stocks by ROE 3y avg desc; tie-break by lowest fwd PE
    def _rank_key(r):
        roe = r.get("roe_3y_avg") or -1
        fpe = r.get("fwd_pe") or 9999
        return (-roe, fpe)

    passed_sorted = sorted(passed, key=_rank_key)
    near_miss_sorted = sorted(near_miss, key=_rank_key)

    version = scan_result.get("version", "v2")
    universe_label = scan_result.get("universe_label", "SET100")
    universe_size = scan_result["universe_size"]
    if universe_label == "SET100":
        universe_desc = f"SET100 effective 1 Jul 2025 - 31 Dec 2025 ({universe_size} symbols targeted)"
        title_suffix = "SET100 (2025-H2)"
    elif universe_label.startswith("all"):
        universe_desc = f"All SET + mai common stocks ({universe_size} symbols targeted; filtered Property Fund & REITs + Infrastructure Fund)"
        title_suffix = "All SET + mai"
    else:
        universe_desc = f"{universe_label} ({universe_size} symbols targeted)"
        title_suffix = universe_label

    lines = []
    lines.append(f"# Hong Stage 1 Scan — {title_suffix} — {version}\n")
    lines.append(f"> **Scan date:** {scan_result['scan_date']}  ")
    lines.append(f"> **Data cache date:** {scan_result['cache_date']}  ")
    lines.append(f"> **Universe:** {universe_desc}  ")
    lines.append(f"> **Elapsed:** {scan_result['elapsed_sec']:.1f}s  ")
    if version in ("v2", "v3"):
        lines.append(f"> **Solvency mode:** sector-aware (retail D/E ≤ 2.5, bank ROA 3y ≥ 1%, default D/E ≤ 1.0)  ")
    else:
        lines.append(f"> **Solvency mode:** v1 legacy — D/E ≤ 1.0 for all sectors  ")
    lines.append("")

    # Sector-class breakdown of scanned
    sec_class_count = defaultdict(int)
    for r in scanned:
        sec_class_count[r.get("sector_class", "?")] += 1

    lines.append("## Summary\n")
    lines.append(f"- **Scanned with data:** {len(scanned)} / {scan_result['universe_size']}")
    lines.append(f"- **Passed 6/6 criteria:** **{len(passed)} stocks**")
    lines.append(f"- **Near-miss (5/6):** {len(near_miss)} stocks")
    lines.append(f"- **Missing from cache (skipped):** {len(missing)} symbols")
    if sec_class_count:
        cls_str = ", ".join(f"{k}={v}" for k, v in sorted(sec_class_count.items()))
        lines.append(f"- **Sector class breakdown (scanned):** {cls_str}")
    lines.append("")
    lines.append("## Hong Stage 1 Criteria (reference)\n")
    lines.append("| # | Criterion | Threshold |")
    lines.append("|---|-----------|-----------|")
    if version in ("v2", "v3"):
        lines.append("| 1 | Solvency (sector-aware) | default: D/E ≤ 1.0 / retail: D/E ≤ 2.5 / bank: ROA 3y avg ≥ 1% |")
    else:
        lines.append("| 1 | D/E (debt to equity) | ≤ 1.0 |")
    lines.append("| 2 | ROE 3 consecutive years | ≥ 15% (or industry median if > 15%) |")
    lines.append("| 3 | Latest net profit | = all-time high in last 5y |")
    lines.append("| 4 | CFO / Net profit (3y avg) | ≥ 0.8 |")
    lines.append("| 5 | Forward PE | ≤ 15 |")
    lines.append("| 6 | Gross + Net margin trend | slope ≥ 0 over last 3y |")
    lines.append("")

    # PASSED TABLE
    lines.append(f"## Passed 6/6 ({len(passed)} stocks) — ranked by ROE 3y avg desc\n")
    if passed_sorted:
        lines.append("| Rank | Symbol | Name | Sector | Class | ROE 3y | Solvency | CFO/NP | Fwd PE | GM | NM |")
        lines.append("|------|--------|------|--------|-------|--------|----------|--------|--------|----|----|")
        for i, r in enumerate(passed_sorted, 1):
            roe_pct = (r["roe_3y_avg"] * 100) if r["roe_3y_avg"] else 0
            cls = r.get("sector_class", "?")
            de = r.get("de_ratio")
            roa = r.get("roa_3y_avg")
            if cls == "bank":
                solvency_str = f"ROA {roa*100:.2f}%" if roa is not None else "ROA n/a"
            else:
                solvency_str = f"D/E {de:.2f}" if de is not None else "D/E n/a"
            lines.append(
                f"| {i} | {r['symbol']} | {(r['name'] or '')[:30]} | {(r['sector'] or '')[:16]} | {cls} | "
                f"{roe_pct:.1f}% | {solvency_str} | "
                f"{(r['cfo_np_avg_3y'] or 0):.2f} | {(r['fwd_pe'] or 0):.1f} | "
                f"{(r['gm_slope'] or 0):.3f} | {(r['nm_slope'] or 0):.3f} |"
            )
    else:
        lines.append("_None_")
    lines.append("")

    # NEAR-MISS TABLE
    lines.append(f"## Near-miss 5/6 ({len(near_miss)} stocks) — which one failed\n")
    if near_miss_sorted:
        lines.append("| Symbol | Name | Sector | ROE 3y | D/E | NewHi | CFO/NP | FwdPE | Margin | Failed |")
        lines.append("|--------|------|--------|--------|-----|-------|--------|-------|--------|--------|")
        flag_keys = [
            ("c1_de_pass", "D/E"),
            ("c2_roe_pass", "ROE"),
            ("c3_new_high_pass", "NewHi"),
            ("c4_cfo_pass", "CFO/NP"),
            ("c5_fwd_pe_pass", "FwdPE"),
            ("c6_margin_pass", "Margin"),
        ]
        for r in near_miss_sorted:
            roe_pct = (r["roe_3y_avg"] * 100) if r["roe_3y_avg"] else 0
            failed = [label for k, label in flag_keys if r.get(k) is False]
            failed_str = ", ".join(failed) if failed else "—"
            def _mark(k):
                v = r.get(k)
                return "Y" if v is True else ("N" if v is False else "?")
            lines.append(
                f"| {r['symbol']} | {(r['name'] or '')[:30]} | {(r['sector'] or '')[:14]} | "
                f"{roe_pct:.1f}% | {(r['de_ratio'] if r['de_ratio'] is not None else 0):.2f} | "
                f"{_mark('c3_new_high_pass')} | {(r['cfo_np_avg_3y'] if r['cfo_np_avg_3y'] is not None else 0):.2f} | "
                f"{(r['fwd_pe'] if r['fwd_pe'] is not None else 0):.1f} | "
                f"{_mark('c6_margin_pass')} | {failed_str} |"
            )
    else:
        lines.append("_None_")
    lines.append("")

    # Top 10 ranked by ROE 3y avg (combined passed + best near-miss for selection guide)
    top10 = passed_sorted[:10]
    lines.append("## Top 10 (from passed, ranked by ROE 3y avg)\n")
    if top10:
        for i, r in enumerate(top10, 1):
            roe_pct = (r["roe_3y_avg"] * 100) if r["roe_3y_avg"] else 0
            lines.append(
                f"{i}. **{r['symbol']}** — {r['name']} ({r['sector']})  "
            )
            lines.append(
                f"   ROE 3y {roe_pct:.1f}% / D/E {(r['de_ratio'] or 0):.2f} / "
                f"Earnings new high YES / Fwd PE {(r['fwd_pe'] or 0):.1f} / CFO/NP {(r['cfo_np_avg_3y'] or 0):.2f}"
            )
    else:
        lines.append("_None passed all 6 criteria._")
    lines.append("")

    # Data quality section
    lines.append("## Data Quality\n")
    nones_breakdown = defaultdict(int)
    for r in scanned:
        for k in ["c1_de_pass", "c2_roe_pass", "c3_new_high_pass",
                  "c4_cfo_pass", "c5_fwd_pe_pass", "c6_margin_pass"]:
            if r.get(k) is None:
                nones_breakdown[k] += 1
    lines.append("Missing-data count per criterion (None = could not evaluate):")
    label_map = {
        "c1_de_pass": "D/E",
        "c2_roe_pass": "ROE 3y",
        "c3_new_high_pass": "New-high",
        "c4_cfo_pass": "CFO/NP",
        "c5_fwd_pe_pass": "Forward PE",
        "c6_margin_pass": "Margin trend",
    }
    for k, label in label_map.items():
        lines.append(f"- {label}: {nones_breakdown.get(k, 0)} / {len(scanned)}")
    lines.append("")
    if missing:
        lines.append(f"Symbols missing from cache (not scanned): {', '.join(missing)}")
        lines.append("")

    # Industry medians
    lines.append("## Industry-median ROE 3y avg (used as ROE threshold when > 15%)\n")
    sec_items = sorted(scan_result["industry_medians"].items(), key=lambda kv: -kv[1])
    if sec_items:
        lines.append("| Sector | Median ROE 3y avg | Used? |")
        lines.append("|--------|-------------------|-------|")
        for sec, med in sec_items:
            used = "YES" if med > 0.15 else "(15% default)"
            lines.append(f"| {sec} | {med*100:.1f}% | {used} |")
    else:
        lines.append("_No sector has ≥ 3 valid samples._")
    lines.append("")

    # Limitations
    lines.append("## Limitations & Notes\n")
    lines.append("- **Source data:** `data/screener_cache/" + scan_result["cache_date"] + "/` — output of `fetch_fundamentals` (SETSMART + thaifin + yahooquery).")
    lines.append("- **Latest fiscal year:** yearly data covers up to most-recent reported FY (typically 2024, some have 2025 partial). Latest row dropped only if revenue+net_income both null/zero.")
    lines.append("- **D/E source:** raw ratio from `yearly_metrics[-1].de_ratio` (thaifin, with SETSMART 5y override). Banks/financial sectors have inherent high D/E (deposits) — will fail D/E test by design.")
    lines.append("- **Forward PE:** from `yfinance.summary_detail.forwardPE`. When missing (no analyst coverage — frequent for Thai mid/small caps), falls back to trailing P/E. CSV `fwd_pe_source` column shows which was used (`forward` / `trailing_fallback` / `missing`).")
    lines.append("- **ROE threshold:** 15% baseline; replaced by sector median when sector median > 15% (only sectors with ≥ 3 valid samples).")
    lines.append("- **Margin trend:** linear slope on 3 data points, tolerance -0.005 / year (treat tiny dips as 'flat').")
    lines.append("- **'New high':** latest net profit ≥ max of prior 4 years AND latest > 0. Equal-to-max also counts.")
    lines.append("- **Stage 1 only:** quantitative pass — Stage 2 manual (management quality, business moat, governance) still required before any buy decision.")
    lines.append("- **Hong's actual portfolio history** (PTL/KTC/OR/DITTO etc.) — see `_shared/docs/research-sianhong-stock-picking.md`. Hong does NOT mechanically apply filters; criteria here are codification of patterns extracted from interviews/books.")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-date", default=None,
                        help="Date folder under data/screener_cache/ (YYYY-MM-DD). Default: latest.")
    parser.add_argument("--out-prefix", default=None,
                        help="Output prefix. Default: research/hong-stage1-scan-{today}.")
    parser.add_argument("--allow-fresh", action="store_true",
                        help="Allow fresh API fetch for symbols missing from cache (slow).")
    parser.add_argument("--universe", default="SET100",
                        help="Universe: SET100 (default 97 syms) | all (~840 SET+mai common stocks from cache) | "
                             "path to .txt file with symbols (one per line, no .BK suffix).")
    parser.add_argument("--version", default="v2", choices=["v1", "v2", "v3", "v4", "v5"],
                        help="Scoring version: v1 (legacy D/E≤1 all) | v2 (sector-aware, SET100 default) | "
                             "v3 (alias for v2 logic — used with --universe all for full SET+mai) | "
                             "v4 (Hong full philosophy: 7 hard gates + Sweet Spot composite score) | "
                             "v5 (v4 minus Gate 2 cash adequacy — flag survivors for manual review).")
    args = parser.parse_args()

    # Resolve cache date
    cache_date = args.cache_date or latest_cache_date()
    if not cache_date:
        print("ERROR: no cache directory found under data/screener_cache/", file=sys.stderr)
        sys.exit(1)

    # v3 = sector-aware logic (same as v2) but applied to full SET+mai universe.
    # Map v3 → v2 internally for criterion logic; keep version label for outputs.
    # v4 = different scanner (scan_v4) — handled separately below.
    scan_version = "v2" if args.version == "v3" else args.version
    output_version = args.version

    universe_filter_stats: dict = {}

    # Resolve universe
    if args.universe == "SET100":
        universe = list(SET100_2025_H2)
        universe_label = "SET100"
    elif args.universe == "all":
        universe, universe_filter_stats = load_universe_from_cache(cache_date)
        universe_label = "all-SET+mai-common"
        if not universe:
            print(f"ERROR: no symbols loaded from cache {cache_date}", file=sys.stderr)
            sys.exit(1)
        print(f"[universe] loaded {len(universe)} common stocks from cache (filtered {universe_filter_stats.get('total_cache', 0) - len(universe)} non-common instruments)")
    else:
        p = Path(args.universe)
        if not p.exists():
            print(f"ERROR: universe file not found: {p}", file=sys.stderr)
            sys.exit(1)
        universe = [ln.strip().replace(".BK", "").upper() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]
        universe_label = f"file:{p.name}"

    # Run — v4 uses different scanner (7 hard gates + composite score)
    if output_version == "v4":
        result = scan_v4(universe, cache_date)
        result["universe_label"] = universe_label
        result["universe_filter_stats"] = universe_filter_stats

        today = result["scan_date"]
        out_prefix = args.out_prefix or str(ROOT / "research" / f"hong-v4-scan-{today}")
        csv_path = Path(out_prefix + ".csv")
        md_path = Path(out_prefix + ".md")
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        write_v4_csv(result, csv_path)
        write_v4_md(result, md_path)

        # Stdout report (Top 30 + gate breakdown)
        print_v4_report(result, top_n=30)
        print(f"CSV: {csv_path}")
        print(f"MD:  {md_path}")
        return

    # v5 — same as v4 but skip Gate 2 (cash adequacy needs manual review)
    if output_version == "v5":
        result = scan_v5(universe, cache_date)
        result["universe_label"] = universe_label
        result["universe_filter_stats"] = universe_filter_stats

        today = result["scan_date"]
        out_prefix = args.out_prefix or str(ROOT / "research" / f"hong-v5-scan-{today}")
        csv_path = Path(out_prefix + ".csv")
        md_path = Path(out_prefix + ".md")
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        write_v5_csv(result, csv_path)
        write_v5_md(result, md_path)

        # Stdout report (Top 30 + gate breakdown)
        print_v5_report(result, top_n=30)
        print(f"CSV: {csv_path}")
        print(f"MD:  {md_path}")
        return

    # v1/v2/v3 path
    result = scan(universe, cache_date, allow_fresh=args.allow_fresh, version=scan_version)
    result["universe_label"] = universe_label
    result["universe_filter_stats"] = universe_filter_stats
    # Override label with original user-requested version (v3 preserved in outputs)
    result["version"] = output_version

    # Output paths
    today = result["scan_date"]
    default_suffix = f"-{output_version}" if output_version != "v1" else ""
    out_prefix = args.out_prefix or str(ROOT / "research" / f"hong-stage1-scan-{today}{default_suffix}")
    csv_path = Path(out_prefix + ".csv")
    md_path = Path(out_prefix + ".md")
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    write_csv(result, csv_path)
    write_md(result, md_path)

    # Console summary
    passed = sum(1 for r in result["results"] if r.get("overall_pass") is True)
    near = sum(1 for r in result["results"] if r.get("passes_count") == 5 and r.get("status") == "scanned")
    missing = len(result["missing"])
    print(f"\n=== Hong Stage 1 Scan ===")
    print(f"Universe:    {result['universe_size']} (SET100 2025-H2)")
    print(f"Passed 6/6:  {passed}")
    print(f"Near-miss:   {near}")
    print(f"Missing:     {missing}")
    print(f"CSV:         {csv_path}")
    print(f"MD:          {md_path}")


if __name__ == "__main__":
    main()
