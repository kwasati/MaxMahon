"""set_official_adapter.py — set.or.th public JSON dividend adapter for MaxMahon.

Primary source for Thai stock dividend history (replaces Yahoo split-adjusted DPS).

Hits set.or.th public JSON endpoint:
    https://www.set.or.th/api/set/stock/{SYMBOL}/corporate-action?lang=en

Cloudflare blocks direct requests (403). Workaround: Playwright Chromium headless
visits any set.or.th page first to obtain Cloudflare cookies, then uses
APIRequestContext (cookies + headers persisted) for subsequent API calls.

Returns DPS events with explicit fiscal-year period (beginOperation, endOperation)
so callers can group by FY without heuristics. Cache local JSON, 7-day TTL.

Public API:
    fetch_dividends(symbol)        -> list[dict]   raw events from set.or.th
    cached_dividends(symbol, ...)  -> list[dict]   cache-aware read
    dps_by_fiscal_year(symbol)     -> dict[int,float]  {FY: sum_dps}
"""

from __future__ import annotations


def fetch_dividends(symbol: str) -> list[dict]:
    """Fetch raw Cash Dividend events for symbol from set.or.th API.

    Returns list of {xdate, payment_date, begin_operation, end_operation, dps,
    dividend_type, source_of_dividend}. Filters caType=='XD' AND
    dividendType=='Cash Dividend'. Skips events with null endOperation.
    """
    raise NotImplementedError


def cached_dividends(symbol: str, max_age_days: int = 7) -> list[dict]:
    """Cache-aware dividend events read.

    Reads CACHE_DIR/{symbol}.json. If file exists and age < max_age_days,
    returns cached events. Otherwise calls fetch_dividends() and writes cache
    atomically (temp file + os.replace). Corrupt/missing keys -> re-fetch.
    """
    raise NotImplementedError


def dps_by_fiscal_year(symbol: str) -> dict[int, float]:
    """Group cached dividend events by fiscal year (= int(end_operation[:4])).

    Returns {FY: total_dps_rounded_4} like {2022: 1.52, 2023: 1.52, ...}.
    Events whose end_operation year cannot be parsed to int are skipped.
    """
    raise NotImplementedError
