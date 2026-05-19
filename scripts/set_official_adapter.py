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

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import BrowserContext, sync_playwright

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / 'data' / 'set_dividend_cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)
BASE_URL = 'https://www.set.or.th/api/set/stock'
CACHE_TTL_DAYS = 7
REQUEST_DELAY_SEC = 1.5

# Module-level singletons — reused across calls so the Cloudflare cookie
# bootstrap (page.goto) happens only once per process.
_playwright = None
_browser = None
_context: BrowserContext | None = None


def _get_browser_context() -> BrowserContext:
    """Lazy-init Playwright Chromium + bootstrap Cloudflare cookies.

    On first call: start Playwright, launch headless Chromium, create a
    context with a desktop UA, then visit https://www.set.or.th/en/market
    once so Cloudflare drops its clearance cookies into the context. The
    same context is reused for every subsequent API call (its cookie jar
    is shared with APIRequestContext via ctx.request).
    """
    global _playwright, _browser, _context
    if _context is not None:
        return _context
    _playwright = sync_playwright().start()
    _browser = _playwright.chromium.launch(headless=True)
    _context = _browser.new_context(
        user_agent=(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        ),
    )
    page = _context.new_page()
    page.goto(
        'https://www.set.or.th/en/market',
        wait_until='domcontentloaded',
        timeout=30000,
    )
    page.wait_for_timeout(2000)
    page.close()
    return _context


def _close_browser() -> None:
    """Tear down Playwright resources. Safe to call multiple times."""
    global _playwright, _browser, _context
    if _context is not None:
        try:
            _context.close()
        except Exception:
            pass
        _context = None
    if _browser is not None:
        try:
            _browser.close()
        except Exception:
            pass
        _browser = None
    if _playwright is not None:
        try:
            _playwright.stop()
        except Exception:
            pass
        _playwright = None


def fetch_dividends(symbol: str) -> list[dict]:
    """Fetch raw Cash Dividend events for symbol from set.or.th API.

    Returns list of {xdate, payment_date, begin_operation, end_operation, dps,
    dividend_type, source_of_dividend}. Filters caType=='XD' AND
    dividendType=='Cash Dividend'. Skips events with null endOperation.
    Raises RuntimeError on non-200 status.
    """
    ctx = _get_browser_context()
    url = f'{BASE_URL}/{symbol}/corporate-action?lang=en'
    resp = ctx.request.get(
        url,
        headers={
            'Referer': (
                f'https://www.set.or.th/en/market/product/stock/quote/'
                f'{symbol}/rights-benefits'
            ),
            'Accept': 'application/json',
        },
    )
    if resp.status != 200:
        raise RuntimeError(
            f'set.or.th API returned {resp.status} for {symbol}'
        )
    try:
        data = json.loads(resp.body().decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise RuntimeError(
            f'set.or.th API returned invalid JSON for {symbol}: {e}'
        )
    if not isinstance(data, list):
        raise RuntimeError(
            f'set.or.th API returned unexpected payload type '
            f'{type(data).__name__} for {symbol} (expected list)'
        )
    events: list[dict] = []
    for ev in data:
        if not isinstance(ev, dict):
            continue
        if ev.get('caType') != 'XD':
            continue
        if ev.get('dividendType') != 'Cash Dividend':
            continue
        end_op = ev.get('endOperation')
        if not end_op:
            continue
        events.append({
            'xdate': (ev.get('xdate') or '')[:10],
            'payment_date': (ev.get('paymentDate') or '')[:10],
            'begin_operation': (ev.get('beginOperation') or '')[:10],
            'end_operation': end_op[:10],
            'dps': float(ev.get('dividend') or 0),
            'dividend_type': ev.get('dividendType'),
            'source_of_dividend': ev.get('sourceOfDividend'),
        })
    return events


def _read_cache(cache_path: Path, max_age_days: int) -> list[dict] | None:
    """Return cached events if file exists, parses OK, and is fresh."""
    if not cache_path.exists():
        return None
    try:
        with cache_path.open('r', encoding='utf-8') as f:
            payload = json.load(f)
        fetched_at_raw = payload['fetched_at']
        events = payload['events']
        if not isinstance(events, list):
            return None
        fetched_at = datetime.fromisoformat(fetched_at_raw)
        if fetched_at.tzinfo is None:
            fetched_at = fetched_at.replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - fetched_at
        if age.total_seconds() >= max_age_days * 86400:
            return None
        return events
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def _write_cache_atomic(cache_path: Path, symbol: str, events: list[dict]) -> None:
    """Write cache JSON atomically (temp file in same dir + os.replace)."""
    payload = {
        'symbol': symbol,
        'fetched_at': datetime.now(timezone.utc).isoformat(),
        'events': events,
    }
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        prefix=f'.{symbol}.', suffix='.json.tmp', dir=str(cache_path.parent)
    )
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, cache_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def cached_dividends(symbol: str, max_age_days: int = 7) -> list[dict]:
    """Cache-aware dividend events read.

    Reads CACHE_DIR/{symbol}.json. If file exists and age < max_age_days,
    returns cached events. Otherwise calls fetch_dividends() and writes cache
    atomically (temp file + os.replace). Corrupt/missing keys -> re-fetch.
    """
    cache_path = CACHE_DIR / f'{symbol}.json'
    cached = _read_cache(cache_path, max_age_days)
    if cached is not None:
        return cached
    events = fetch_dividends(symbol)
    _write_cache_atomic(cache_path, symbol, events)
    return events


def dps_by_fiscal_year(symbol: str) -> dict[int, float]:
    """Group cached dividend events by fiscal year (= int(end_operation[:4])).

    Returns {FY: total_dps_rounded_4} like {2022: 1.52, 2023: 1.52, ...}.
    Events whose end_operation year cannot be parsed to int are skipped.
    """
    raise NotImplementedError
