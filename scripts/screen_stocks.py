"""Max Mahon v5 — Stock Screener: Niwes Dividend-First framework (5-5-5-5)."""

import argparse
import json
import logging
import sys
import time as _time_module
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
UNIVERSE = DATA_DIR / "set_universe.json"
USER_DATA = ROOT / "user_data.json"

sys.path.insert(0, str(ROOT / "scripts"))
from fetch_data import fetch_multi_year_safe
from data_adapter import compute_normalized_earnings, last_complete_fy, refresh_prices_bulk
from fact_sheet import dividend_series, dividend_cuts, load_cfg as load_fact_cfg

GATE_VERSION = "niwes-gate-2026-10"

DEFAULT_FILTERS = {
    "min_dividend_yield": 5.0,
    "growing_yield_floor": 2.0,
    "growing_min_streak": 3,
    "growing_growth_cap": 0.15,
    "min_market_cap": 5_000_000_000,
    "yield_abnormal_pct": 20.0,
}


def load_filters() -> dict:
    """Load filters from config.json, fallback to defaults."""
    config_path = ROOT / "config.json"
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            return {**DEFAULT_FILTERS, **config.get("filters", {})}
        except Exception:
            pass
    return dict(DEFAULT_FILTERS)


HARD_FILTERS = load_filters()


def _last_complete_dps(data: dict):
    """(fy, dps) of the latest complete dividend year, or (None, None)."""
    agg = data.get("aggregates") or {}
    hist = {int(k): v for k, v in (data.get("dividend_history") or {}).items() if v is not None}
    fy = agg.get("dividend_last_complete_fy")
    if fy is None:
        fy = last_complete_fy(hist)
    if fy is None or hist.get(int(fy)) is None:
        return None, None
    return int(fy), float(hist[int(fy)])


def projected_yield_5y(data: dict):
    """Niwes C2/C3: yield in year 5 vs today's price = last-complete-FY DPS x (1+g)^5 / price (%).

    g = lower of dps_cagr (5y) and dps_10y_cagr (one None -> use the other), capped at growing_growth_cap.
    Returns (projected_yield_pct, g) or (None, g) when it cannot be computed / g <= 0.
    """
    agg = data.get("aggregates") or {}
    cands = [g for g in (agg.get("dps_cagr"), agg.get("dps_10y_cagr")) if g is not None]
    if not cands:
        return None, None
    g = min(min(cands), HARD_FILTERS["growing_growth_cap"])
    _, dps = _last_complete_dps(data)
    price = data.get("price")
    if g <= 0 or not dps or not price or price <= 0:
        return None, g
    return dps * (1 + g) ** 5 / price * 100, g


def gate_flags(data: dict) -> list:
    """Warning flags for a stock (never change PASS/FAIL). Own thresholds, not Niwes quotes."""
    flags: list[str] = []
    agg = data.get("aggregates") or {}
    norm_eps = compute_normalized_earnings(data)
    current_year = datetime.now().year
    years = sorted((y for y in norm_eps if int(y) < current_year), key=lambda y: int(y))[-5:]
    eps = [norm_eps[y] for y in years]
    if eps and any(e is not None and e <= 0 for e in eps):
        flags.append(f"LOSS_YEARS:{sum(1 for e in eps if e is not None and e <= 0)}/5")
    if len(eps) < 5:
        flags.append(f"EPS_HISTORY_SHORT:{len(eps)}")
    payout = data.get("payout_ratio")
    if payout is not None and payout > 1.0:
        flags.append("PAYOUT_OVER_100")
    if "dividend_history_short" in (agg.get("data_gaps") or []):
        flags.append("DIVIDEND_HISTORY_SHORT")
    dy = data.get("dividend_yield")
    if dy is not None and dy < HARD_FILTERS["min_dividend_yield"] and _passes_growing(data)[0]:
        py, g = projected_yield_5y(data)
        flags.append(f"PASSED_VIA_GROWTH:g={g:.3f},yield5y={py:.1f}%")
    if dy is not None and dy > HARD_FILTERS["yield_abnormal_pct"]:
        flags.append(f"YIELD_ABNORMAL:{dy:.1f}%")
    return flags


def dividend_source_counts(fetched: dict) -> dict:
    """Where each fetched stock's dividend history came from: set.or.th (alone or merged) / yahoo only / none."""
    c = {"set": 0, "yahoo_only": 0, "none": 0, "total": 0}
    for data in fetched.values():
        if not data or data.get("delisted"):
            continue
        c["total"] += 1
        src = data.get("dividend_source") or ""
        if src.startswith("set_official"):
            c["set"] += 1
        elif src == "yahoo" and data.get("dividend_history"):
            c["yahoo_only"] += 1
        else:
            c["none"] += 1
    return c


def _passes_growing(data: dict) -> tuple:
    """Niwes C3 exception path. Returns (ok, why_not)."""
    dy = data.get("dividend_yield")
    streak = (data.get("aggregates") or {}).get("dividend_growth_streak", 0) or 0
    if dy is None or dy < HARD_FILTERS["growing_yield_floor"]:
        return False, f"yield < {HARD_FILTERS['growing_yield_floor']:.0f}%"
    if streak < HARD_FILTERS["growing_min_streak"]:
        return False, f"growth_streak {streak}yr < {HARD_FILTERS['growing_min_streak']}"
    py, g = projected_yield_5y(data)
    if py is None:
        return False, "คำนวณ yield ปีที่ 5 ไม่ได้ (g ไม่มีหรือ <= 0)"
    if py < HARD_FILTERS["min_dividend_yield"]:
        return False, f"yield ปีที่ 5 {py:.1f}% (g={g:.3f}) < {HARD_FILTERS['min_dividend_yield']:.0f}%"
    return True, ""


def hard_filter(data: dict) -> tuple:
    """Gate = junk screen using only what Dr.Niwes said. Returns (status, reasons), status in PASS/FAIL/PENDING.

    Passes when all hold:
    1. market cap >= min_market_cap — our own number for C5 "large enough"
    2. data sane — yahoo flake (yield > 0, no DPS history) -> PENDING
    3. dividend, either path:
       - C1: dividend_yield >= min_dividend_yield (5%)
       - C3: yield >= growing_yield_floor, DPS rising >= growing_min_streak complete years,
         and projected year-5 yield (last complete DPS x (1+g)^5 / price) >= 5% (C2)
         growing_yield_floor / growing_min_streak / growing_growth_cap are our own numbers
       - no dividend data = FAIL
    PE, PBV, EPS-positive years are not gate conditions; see gate_flags() for warnings.
    """
    info_mcap = data.get("market_cap") or 0
    if info_mcap < HARD_FILTERS["min_market_cap"]:
        return "FAIL", [f"market cap {info_mcap/1e9:.1f}B < {HARD_FILTERS['min_market_cap']/1e9:.0f}B"]

    agg = data.get("aggregates") or {}
    dy = data.get("dividend_yield")
    if dy is not None and dy > 0 and agg.get("dividend_streak", 0) == 0 and not (data.get("dividend_history") or {}):
        return "PENDING", ["ไม่มีข้อมูลปันผลย้อนหลัง (yahoo flake — queued for retry)"]

    if dy is None:
        return "FAIL", ["ไม่มีข้อมูลปันผล"]
    if dy >= HARD_FILTERS["min_dividend_yield"]:
        return "PASS", []
    ok, why = _passes_growing(data)
    if ok:
        return "PASS", []
    return "FAIL", [f"dividend yield {dy:.1f}% < {HARD_FILTERS['min_dividend_yield']:.0f}% (growing exception not met: {why})"]


def material_cuts_10y(data: dict) -> int:
    """Count of DPS cuts >= cut_material_pct (fact sheet config) in the latest 10 complete FYs."""
    complete, _ = dividend_series(data)
    if not complete:
        return 0
    last_fy = max(complete)
    cuts = dividend_cuts(complete, load_fact_cfg()["cut_material_pct"])
    return sum(1 for c in cuts if c["material"] and c["fy"] > last_fy - 10)


def build_entry(sym: str, data: dict, in_watchlist: bool) -> dict:
    """Entry of a stock that passed the gate: which path, flags, headline numbers. No scoring."""
    agg = data.get("aggregates") or {}
    dy = data.get("dividend_yield")
    main_path = dy is not None and dy >= HARD_FILTERS["min_dividend_yield"]
    last_fy, last_dps = _last_complete_dps(data)
    py, g = (None, None) if main_path else projected_yield_5y(data)
    return {
        "symbol": sym,
        "name": data.get("name", sym),
        "sector": data.get("sector", "N/A"),
        "sector_profile": data.get("sector_profile") or agg.get("sector_profile"),
        "in_watchlist": in_watchlist,
        "gate_path": "main" if main_path else "growth",
        "gate_flags": gate_flags(data),
        "price": data.get("price"),
        "price_as_of": data.get("price_as_of"),
        "dividend_yield": dy,
        "last_dps": last_dps,
        "last_dps_fy": last_fy,
        "projected_yield_5y": py,
        "growth_used": g,
        "dps_cagr_5y": agg.get("dps_cagr"),
        "dps_cagr_10y": agg.get("dps_10y_cagr"),
        "dividend_streak": agg.get("dividend_streak"),
        "material_cuts_10y": material_cuts_10y(data),
        "pe": data.get("pe_ratio"),
        "pbv": data.get("pb_ratio"),
        "market_cap": data.get("market_cap"),
        "data_gaps": list(agg.get("data_gaps") or []),
    }


def candidate_sort_key(c: dict) -> tuple:
    """Fixed order: main path before growth path, then yield high -> low, then symbol."""
    return (0 if c.get("gate_path") == "main" else 1, -(c.get("dividend_yield") or 0), c["symbol"])


def parse_symbols(text: str) -> list:
    """'amata,BBL.BK' -> ['AMATA.BK', 'BBL.BK'] (order kept, duplicates dropped)."""
    out: list[str] = []
    for part in text.split(","):
        part = part.strip().upper()
        if not part:
            continue
        sym = part if part.endswith(".BK") else part + ".BK"
        if sym not in out:
            out.append(sym)
    return out


def refresh_market_prices(symbols=None, refresher=None) -> dict:
    """Refresh prices before the scan (whole market = one bulk call) and print what was and wasn't refreshed."""
    if refresher is None:
        refresher = refresh_prices_bulk
    res = refresher(symbols)
    ok, failed = res.get("ok") or {}, res.get("failed") or {}
    dates = sorted(set(ok.values()))
    print(f"price refresh: {len(ok)} refreshed, {len(failed)} failed · price date "
          f"{dates[0] if len(dates) == 1 else (dates[0] + '..' + dates[-1] if dates else '-')} · bulk calls {res.get('bulk_calls')}")
    for s, why in sorted(failed.items())[:20]:
        print(f"  refresh failed {s}: {why}")
    if len(failed) > 20:
        print(f"  ... and {len(failed) - 20} more")
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description="Max Mahon gate screener")
    ap.add_argument("--symbols", help="comma-separated symbols to scan instead of the whole universe")
    ap.add_argument("--out-dir", help="write the screener json here instead of data/ (also skips the flake queue)")
    ap.add_argument("--no-refresh", action="store_true", help="skip the price refresh and use the SETSMART cache as is")
    args = ap.parse_args(argv)
    out_dir = Path(args.out_dir) if args.out_dir else None

    user_data = json.loads(USER_DATA.read_text(encoding="utf-8"))
    watched = set(user_data.get("watchlist", []))
    blacklisted = set(user_data.get("blacklist", []))

    if args.symbols:
        symbols = parse_symbols(args.symbols)
    else:
        symbols = json.loads(UNIVERSE.read_text(encoding="utf-8"))["symbols"]
    print(f"Max Mahon gate screening {len(symbols)} stocks ({GATE_VERSION})...")

    if args.no_refresh:
        print("price refresh: skipped (--no-refresh) — using the SETSMART cache as is")
    else:
        if args.symbols:
            refresh_market_prices(symbols)
        else:  # whole market: one bulk call, no per-symbol fallback (the dead/fund tickers just get listed as failed)
            refresh_market_prices([s for s in symbols if s not in blacklisted],
                                  refresher=lambda syms: refresh_prices_bulk(syms, max_per_symbol_fallback=0))

    # ===== Phase A — parallel fetch =====
    fetch_targets = [s for s in symbols if s not in blacklisted]
    fetched_data: dict[str, dict] = {}
    fetch_start = _time_module.time()
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
    pending_candidates: list[dict] = []
    filtered_stocks = []
    error_count = 0
    today = datetime.now().strftime("%Y-%m-%d")

    for i, sym in enumerate(symbols):
        if sym in blacklisted:
            print(f"  [{i+1}/{len(symbols)}] {sym} — blacklisted, skipping")
            continue

        try:
            data = fetched_data.get(sym)

            if data is None:
                print(f"  [{i+1}/{len(symbols)}] {sym} — skipped: no data")
                continue

            if data.get("delisted"):
                logger.info(f"skip delisted {sym}: {data.get('error', 'unknown')}")
                print(f"  [{i+1}/{len(symbols)}] {sym} — delisted/error: {data.get('error', 'unknown')}")
                error_count += 1
                continue

            if "error" in data and not data.get("price"):
                print(f"  [{i+1}/{len(symbols)}] {sym} — error: {data['error']}")
                continue

            status, filter_reasons = hard_filter(data)
            if status == "FAIL":
                filtered_stocks.append({
                    "symbol": sym,
                    "name": data.get("name", sym),
                    "sector": data.get("sector", "N/A"),
                    "in_watchlist": sym in watched,
                    "reasons": filter_reasons,
                    "basic_metrics": {
                        "price": data.get("price"),
                        "dividend_yield": data.get("dividend_yield"),
                        "roe": data.get("roe"),
                        "de": (lambda de: de / 100 if de is not None else None)(data.get("debt_to_equity")),
                        "mcap": data.get("market_cap"),
                        "pe": data.get("pe_ratio"),
                        "eps": data.get("eps_trailing"),
                    }
                })
                print(f"  [{i+1}/{len(symbols)}] {sym} — filtered: {', '.join(filter_reasons[:2])}")
                continue

            if status == "PENDING":
                pending_candidates.append({
                    "symbol": sym,
                    "sector": data.get("sector", "N/A"),
                    "in_watchlist": sym in watched,
                    "reasons": filter_reasons,
                })
                print(f"  [{i+1}/{len(symbols)}] {sym} — pending: {', '.join(filter_reasons[:2])}")
                continue

            entry = build_entry(sym, data, sym in watched)
            candidates.append(entry)
            marker = "★" if entry["in_watchlist"] else "✦"
            print(f"  [{i+1}/{len(symbols)}] {marker} {sym} — pass ({entry['gate_path']}) yield {entry['dividend_yield']}"
                  + (f" flags={entry['gate_flags']}" if entry["gate_flags"] else ""))

        except Exception as e:
            error_count += 1
            print(f"  [{i+1}/{len(symbols)}] {sym} — error: {e}")

    candidates.sort(key=candidate_sort_key)
    src_counts = dividend_source_counts(fetched_data)
    print(f"dividend source: set.or.th {src_counts['set']} · yahoo only {src_counts['yahoo_only']} · "
          f"none {src_counts['none']} (of {src_counts['total']} fetched)")
    n_main = sum(1 for c in candidates if c["gate_path"] == "main")
    new_finds = [c for c in candidates if not c["in_watchlist"]]

    out = {
        "date": today,
        "agent": "Max Mahon v5",
        "gate_version": GATE_VERSION,
        "total_scanned": len(symbols),
        "passed_filter": len(candidates),
        "filtered_out": len(filtered_stocks),
        "pending_count": len(pending_candidates),
        "new_discoveries": len(new_finds),
        "counts": {
            "passed": len(candidates),
            "passed_main": n_main,
            "passed_growth": len(candidates) - n_main,
            "filtered_out": len(filtered_stocks),
            "pending": len(pending_candidates),
        },
        "hard_filters": HARD_FILTERS,
        "dividend_sources": src_counts,
        "candidates": candidates,
        "pending_candidates": pending_candidates,
        "filtered_out_stocks": filtered_stocks,
    }

    target_dir = out_dir or DATA_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    out_path = target_dir / f"screener_{today}.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Scanned: {len(symbols)} | Passed: {len(candidates)} (main {n_main} / growth {len(candidates) - n_main}) | "
          f"Pending: {len(pending_candidates)} | Filtered: {len(filtered_stocks)} | Errors: {error_count} | New: {len(new_finds)}")
    print(f"\nSaved → {out_path}")

    return out_path


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"screen_stocks fatal: {e}", file=sys.stderr)
        sys.exit(1)
