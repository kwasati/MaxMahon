"""Daily price refresh for watchlist + PASS candidates.

Scheduled 19:00 Asia/Bangkok (post SET close 17:00 + 2h buffer).

Collects symbols from EVERY user's watchlist (set-union via
``scripts.user_data_io.aggregate_watchlists``) + latest screener_*.json
candidates, then writes ``data/price_cache/{symbol}.json`` with
``{symbol, price, fetched_at, source}``.

Pricing source priority (Rule 0 — SETSMART precedence):
  1. SETSMART EOD bulk — primary. 1 request covers ~933 CS symbols, reliable.
  2. yahooquery batch — fallback for symbols SETSMART does not return
     (rare for Thai CS), with sequential retry for transient flake.
"""
import json
import logging
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from yahooquery import Ticker

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CACHE_DIR = DATA_DIR / "price_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Make sibling helper importable when this script is run as __main__ via APScheduler.
_PROJECT_ROOT = str(ROOT)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
from scripts.user_data_io import aggregate_watchlists  # noqa: E402

logger = logging.getLogger(__name__)

_SCREENER_RE = re.compile(r"^screener_\d{4}-\d{2}-\d{2}\.json$")


def _load_symbols() -> list[str]:
    """Collect deduped, sorted symbol list from ALL users' watchlists + latest screener."""
    symbols: set[str] = set()

    # Plan 02 Phase 4 — union watchlists across every user folder under data/users/.
    try:
        symbols.update(aggregate_watchlists())
    except Exception as e:  # noqa: BLE001
        logger.warning(f"aggregate_watchlists failed: {e}")

    # Latest screener candidate list (filter lexical sort to canonical dated files)
    screeners = [p for p in DATA_DIR.glob("screener_*.json") if _SCREENER_RE.match(p.name)]
    screeners.sort(reverse=True)
    if screeners:
        try:
            scr = json.loads(screeners[0].read_text(encoding="utf-8"))
            for c in scr.get("candidates", []) or []:
                sym = c.get("symbol")
                if sym:
                    symbols.add(sym)
        except (OSError, json.JSONDecodeError) as e:
            logger.warning(f"could not read {screeners[0].name}: {e}")

    return sorted(symbols)


def _write_cache(sym: str, price: float, fetched_at: str, source: str) -> None:
    payload = {
        "symbol": sym,
        "price": price,
        "fetched_at": fetched_at,
        "source": source,
    }
    (CACHE_DIR / f"{sym}.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _load_setsmart_eod_map() -> tuple[dict[str, float], str | None]:
    """Find latest SETSMART EOD payload, return ({symbol_no_bk: close}, date).

    Walks today → 7 days back; first non-empty response wins. Returns ({}, None) on failure.
    """
    try:
        from setsmart_adapter import cached_eod_bulk
    except Exception as e:
        logger.warning("SETSMART adapter import failed: %s", e)
        return {}, None

    for delta in range(0, 8):
        d = (datetime.now() - timedelta(days=delta)).strftime("%Y-%m-%d")
        try:
            data = cached_eod_bulk(d)
        except Exception as e:
            logger.warning("SETSMART fetch failed for %s: %s", d, e)
            continue
        if not data:
            continue
        price_map: dict[str, float] = {}
        for row in data:
            sym = row.get("symbol")
            close = row.get("close")
            if sym and close is not None:
                price_map[sym] = float(close)
        if price_map:
            logger.info("SETSMART EOD bulk: %d symbols for %s", len(price_map), d)
            return price_map, d

    logger.warning("SETSMART EOD bulk: no data in last 8 days")
    return {}, None


def _yahoo_fetch_batch(chunk: list[str]) -> dict[str, float]:
    """Fetch one chunk via yahooquery batch. Returns {symbol: price} for hits."""
    out: dict[str, float] = {}
    try:
        tk = Ticker(chunk)
        prices = tk.price
        if not isinstance(prices, dict):
            logger.warning("yahoo batch returned non-dict: %s", type(prices).__name__)
            return out
        for sym in chunk:
            info = prices.get(sym)
            if not isinstance(info, dict):
                continue
            price = info.get("regularMarketPrice")
            if price is None:
                continue
            out[sym] = float(price)
    except Exception as e:
        logger.warning("yahoo batch failed: %s", e)
    return out


def _refresh_setsmart_financial(symbols: list[str]) -> None:
    """Refresh SETSMART per-symbol financial cache (5y quarterly).

    Calls ``cached_financial_by_symbol_range`` for each symbol so the next
    scan/report read can hit warm cache (avoid per-request SETSMART round-trip).

    Strips ``.BK`` suffix to match SETSMART API expectation (consistent with EOD
    bulk lookup convention in ``refresh_prices``). Handles per-symbol failures
    gracefully so one bad symbol does not abort the batch.
    """
    try:
        from setsmart_adapter import cached_financial_by_symbol_range
    except Exception as e:
        logger.warning("SETSMART adapter import failed (financial refresh): %s", e)
        return

    current_year = datetime.now().year
    start_y = str(current_year - 5)
    end_y = str(current_year - 1)
    success_count = 0
    for sym in symbols:
        sym_no_bk = sym[:-3] if sym.endswith(".BK") else sym
        try:
            records = cached_financial_by_symbol_range(sym_no_bk, start_y, "1", end_y, "4")
            if records:
                success_count += 1
        except Exception as e:
            logger.warning("SETSMART financial refresh failed for %s: %s", sym, e)
    logger.info("SETSMART financial refresh: %d/%d success", success_count, len(symbols))


def refresh_prices() -> dict:
    """Refresh prices for watchlist + PASS candidates.

    Strategy:
      1. SETSMART EOD bulk (primary) — covers all Thai CS symbols in one request.
         Strip ".BK" suffix on lookup since SETSMART uses raw symbol.
      2. yahoo batch fallback — only for symbols SETSMART did not return.
      3. yahoo sequential retry — for symbols still missing after batch, with
         30s wait + 1.5s/sym delay (mirrors scan pipeline Stage 2 repair).

    Returns {symbol: price} for symbols successfully written to cache.
    """
    symbols = _load_symbols()
    logger.info("refreshing %d symbols", len(symbols))
    fetched: dict[str, float] = {}

    # 1. SETSMART primary
    ss_map, ss_date = _load_setsmart_eod_map()
    ss_fetched_at = (
        datetime.strptime(ss_date, "%Y-%m-%d").replace(hour=17, minute=0).isoformat(timespec="seconds")
        if ss_date else datetime.now().isoformat(timespec="seconds")
    )
    missing: list[str] = []
    for sym in symbols:
        base = sym[:-3] if sym.endswith(".BK") else sym
        price = ss_map.get(base)
        if price is not None:
            _write_cache(sym, price, ss_fetched_at, "setsmart")
            fetched[sym] = price
        else:
            missing.append(sym)
    logger.info("SETSMART covered %d/%d, missing %d", len(fetched), len(symbols), len(missing))

    # 2. yahoo batch fallback for missing
    still_missing: list[str] = []
    if missing:
        for i in range(0, len(missing), 20):
            chunk = missing[i:i + 20]
            yh = _yahoo_fetch_batch(chunk)
            for sym in chunk:
                price = yh.get(sym)
                if price is not None:
                    _write_cache(sym, price, datetime.now().isoformat(timespec="seconds"), "yahoo")
                    fetched[sym] = price
                else:
                    still_missing.append(sym)
            time.sleep(0.2)
        logger.info("yahoo batch recovered %d, still missing %d", len(missing) - len(still_missing), len(still_missing))

    # 3. yahoo sequential retry for stubborn flakes
    if still_missing:
        logger.info("yahoo retry sequential: %d symbols (sleep 30s first)", len(still_missing))
        time.sleep(30)
        recovered = 0
        for sym in still_missing:
            yh = _yahoo_fetch_batch([sym])
            price = yh.get(sym)
            if price is not None:
                _write_cache(sym, price, datetime.now().isoformat(timespec="seconds"), "yahoo")
                fetched[sym] = price
                recovered += 1
            time.sleep(1.5)
        logger.warning("yahoo retry recovered %d/%d (still stale: %s)",
                       recovered, len(still_missing),
                       [s for s in still_missing if s not in fetched])

    logger.info("refreshed %d/%d prices total", len(fetched), len(symbols))

    # 4. SETSMART per-symbol financial refresh (Plan filter-02 Phase 4)
    # Warm cache for 5y quarterly financial-data-and-ratio-by-symbol so next
    # scan/report can read locally. Runs after EOD refresh completes.
    _refresh_setsmart_financial(symbols)

    return fetched


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    result = refresh_prices()
    print(f"OK — {len(result)} prices refreshed")
