---
project: MaxMahon
created: 2026-04-27
last_updated: 2026-04-27
status: done
---

## Target / Goal
ทำได้: รัน `py scripts/setsmart_adapter.py` ผ่าน 5 smoke test (BBL EOD by symbol / EOD all 1 day / Financial all 1 quarter / discover package history coverage / cache layer) + report ระบุ package start year ที่ console + cache file สร้างใน data/setsmart_cache/

# SETSMART Adapter Module + Cache

> Part 1 of 2 — Foundation | Index: setsmart-integration-index. สร้าง SETSMART API wrapper standalone (ยังไม่ wire เข้า MaxMahon pipeline). มี 4 fetch functions + cache layer + retry/timeout + smoke test ทดสอบ 4 หุ้น verify (BBL/METCO/QH/SAT) + bulk EOD + bulk Financial + discover package coverage (history start year). Depends on: none. Parallel-safe with: none.

## Phase 1: SETSMART Adapter
- [x] สร้างไฟล์ใหม่ `projects/MaxMahon/scripts/setsmart_adapter.py` ตาม reference snippet ข้างล่าง — wrapper 4 endpoints (fetch_eod_by_symbol, fetch_eod_all, fetch_financial_by_symbol, fetch_financial_all) + retry/timeout + load API key from root `.env` (SETSMART_API_KEY) + cache layer (cached_eod_bulk, cached_financial_bulk, cached_eod_history) + smoke test 5 cases ใน `if __name__ == '__main__'`. — Scope: ห้ามแก้ไฟล์อื่น (data_adapter.py, daily_price_refresh.py, fetch_data.py — Plan 02 จะ wire เข้า). ห้ามใช้ library อื่น — ใช้แค่ `requests` + `json` + `pathlib` + stdlib. — Acceptance: (a) ไฟล์ `projects/MaxMahon/scripts/setsmart_adapter.py` ถูกสร้าง, (b) รัน `cd projects/MaxMahon && py scripts/setsmart_adapter.py` ต้องเห็น 'ALL SMOKE TESTS PASSED' ที่จบ, (c) console output ต้องระบุ package start year ของ BBL (ปีที่ SETSMART เริ่ม cover), (d) ไฟล์ `projects/MaxMahon/data/setsmart_cache/eod_{YYYY-MM-DD}.json` (ของวันที่ test) ถูกสร้าง
- [x] เพิ่ม `data/setsmart_cache/` ที่ `projects/MaxMahon/.gitignore` (ไฟล์ cache ไม่ commit เข้า repo เพราะใหญ่ ~4MB/วัน). ถ้าไม่มี .gitignore ให้สร้าง. — Scope: แตะแค่ .gitignore. — Acceptance: รัน `cd projects/MaxMahon && git status` ไม่เห็น `data/setsmart_cache/` ใน untracked files หลังรัน smoke test สร้าง cache
- [x] อัพเดต `projects/MaxMahon/CLAUDE.md` ในส่วน 'Data Sources' เพิ่ม SETSMART layer description — ระบุว่า SETSMART จะเป็น primary source ของ aggregate data (yield, P/E, P/BV, market cap, ROE, ROA, EPS, ratios) หลัง Plan 02 wire เสร็จ. ส่วน DPS event-by-event ยังคงใช้ yahooquery (SETSMART ไม่มี). — Scope: แก้แค่ section 'Data Sources' + 'Data Source Invariants'. ห้ามแตะ section อื่น. — Acceptance: section 'Data Sources' มีบรรทัด '**Layer 0 (after Plan 02 merge):** SETSMART API — ...' + ระบุ endpoint ทั้ง 4 + cache strategy

### Reference
```python
# new file: projects/MaxMahon/scripts/setsmart_adapter.py
"""SETSMART API adapter — primary source of truth for MaxMahon aggregate data.

API key from .env: SETSMART_API_KEY
Header: api-key
Method: GET
Base URL: https://www.setsmart.com/api/listed-company-api/

4 endpoints:
  - eod-price-by-symbol         (per-symbol daily history, max 6 yrs/request)
  - eod-price-by-security-type  (1 day, all symbols by type, ~4000 rows)
  - financial-data-and-ratio-by-symbol (per-symbol quarterly history)
  - financial-data-and-ratio    (1 year+quarter, all companies, ~700 rows)

Cache strategy:
  - data/setsmart_cache/eod_{YYYY-MM-DD}.json         (bulk daily, ~4MB)
  - data/setsmart_cache/financial_{YYYY}_q{N}.json    (bulk quarterly, ~1MB)
  - data/setsmart_cache/eod_by_symbol_{SYM}_{start}_{end}.json  (lazy, per-stock history)
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "data" / "setsmart_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://www.setsmart.com/api/listed-company-api"

# Load API key from .env (root)
def _load_api_key() -> str:
    # Walk up to find .env at workspace root
    p = ROOT.parent.parent
    env_file = p / ".env"
    if not env_file.exists():
        raise RuntimeError(f"SETSMART_API_KEY: .env not found at {env_file}")
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("SETSMART_API_KEY="):
            key = line.split("=", 1)[1].strip().strip("'\"")
            if key:
                return key
    raise RuntimeError("SETSMART_API_KEY not found in .env")

_API_KEY = None  # lazy

def _api_key() -> str:
    global _API_KEY
    if _API_KEY is None:
        _API_KEY = _load_api_key()
    return _API_KEY


def _request(path: str, params: dict, timeout: int = 30, retries: int = 3) -> list[dict]:
    """GET helper with retry + timeout."""
    url = f"{BASE_URL}/{path}"
    headers = {"api-key": _api_key()}
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=timeout)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 503) and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise
    return []


def fetch_eod_by_symbol(symbol: str, start_date: str, end_date: str | None = None,
                         adjusted: str = "Y") -> list[dict]:
    """Per-symbol EOD history. Max 6 years per request."""
    params = {"symbol": symbol, "startDate": start_date, "adjustedPriceFlag": adjusted}
    if end_date:
        params["endDate"] = end_date
    return _request("eod-price-by-symbol", params)


def fetch_eod_all(date: str, security_type: str = "CS", adjusted: str = "Y") -> list[dict]:
    """All symbols on 1 day, by security type."""
    return _request("eod-price-by-security-type",
                    {"securityType": security_type, "date": date, "adjustedPriceFlag": adjusted})


def fetch_financial_by_symbol(symbol: str, start_year: str, start_quarter: str,
                               end_year: str | None = None, end_quarter: str | None = None) -> list[dict]:
    """Per-symbol quarterly financials."""
    params = {"symbol": symbol, "startYear": start_year, "startQuarter": start_quarter}
    if end_year and end_quarter:
        params["endYear"] = end_year
        params["endQuarter"] = end_quarter
    return _request("financial-data-and-ratio-by-symbol", params)


def fetch_financial_all(year: str, quarter: str, account_period: str = "C") -> list[dict]:
    """All companies, 1 year+quarter."""
    return _request("financial-data-and-ratio",
                    {"accountPeriod": account_period, "year": year, "quarter": quarter})


# ----- Cache layer -----

def cached_eod_bulk(date: str, security_type: str = "CS") -> list[dict]:
    """Cached bulk EOD. Reads from disk if exists, else fetch + cache."""
    cache_file = CACHE_DIR / f"eod_{date}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))
    data = fetch_eod_all(date, security_type=security_type)
    cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def cached_financial_bulk(year: str, quarter: str, account_period: str = "C") -> list[dict]:
    """Cached bulk Financial. Reads from disk if exists, else fetch + cache."""
    cache_file = CACHE_DIR / f"financial_{year}_q{quarter}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))
    data = fetch_financial_all(year, quarter, account_period=account_period)
    cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def cached_eod_history(symbol: str, start_date: str, end_date: str) -> list[dict]:
    """Cached per-symbol history (lazy, used for detail page)."""
    cache_file = CACHE_DIR / f"eod_by_symbol_{symbol}_{start_date}_{end_date}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))
    data = fetch_eod_by_symbol(symbol, start_date, end_date)
    cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


# ----- Smoke test -----

if __name__ == "__main__":
    from datetime import datetime, timedelta

    print("[smoke 1/4] fetch_eod_by_symbol BBL 2024-01-01..2024-01-15")
    bbl = fetch_eod_by_symbol("BBL", "2024-01-01", "2024-01-15")
    print(f"  rows: {len(bbl)}, first: {bbl[0] if bbl else 'EMPTY'}")
    assert len(bbl) > 0, "BBL EOD fetch returned empty"

    print("[smoke 2/4] fetch_eod_all on most recent trading day")
    # Try yesterday first, walk back if empty
    test_date = None
    for delta in range(1, 8):
        d = (datetime.now() - timedelta(days=delta)).strftime("%Y-%m-%d")
        eod_all = fetch_eod_all(d)
        if len(eod_all) > 0:
            test_date = d
            break
    print(f"  date: {test_date}, rows: {len(eod_all)}, types: {set(x.get(\'securityType\') for x in eod_all[:50])}")
    assert test_date is not None, "fetch_eod_all returned empty for last 7 days"

    print("[smoke 3/4] fetch_financial_all 2023 Q4")
    fin = fetch_financial_all("2023", "4")
    print(f"  rows: {len(fin)}, first: {fin[0].get(\'symbol\') if fin else \'EMPTY\'}")
    assert len(fin) > 0, "fetch_financial_all returned empty"

    print("[smoke 4/4] discover package history coverage (BBL)")
    # SETSMART API returns HTTP 500 (not empty list) for out-of-coverage date ranges,
    # so we treat 500 as 'not covered' and continue walking forward.
    def _safe_eod(sym, start, end):
        try:
            return fetch_eod_by_symbol(sym, start, end)
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 500:
                return []
            raise

    early = _safe_eod("BBL", "2010-01-01", "2010-12-31")
    if len(early) > 0:
        print(f"  BBL 2010 rows: {len(early)} — package COVERS 2010")
    else:
        for try_year in (2015, 2018, 2020, 2022):
            r = _safe_eod("BBL", f"{try_year}-01-01", f"{try_year}-01-31")
            if len(r) > 0:
                print(f"  BBL {try_year}: {len(r)} rows — earliest covered >= {try_year}")
                break
        else:
            print("  WARN: no BBL data found 2010-2022 — investigate")

    print("[smoke 5/5] cache layer test")
    d = cached_eod_bulk(test_date)
    print(f"  cache hit/miss + rows: {len(d)}")
    cache_file = CACHE_DIR / f"eod_{test_date}.json"
    assert cache_file.exists(), f"cache file not created: {cache_file}"

    print()
    print("ALL SMOKE TESTS PASSED")
```
