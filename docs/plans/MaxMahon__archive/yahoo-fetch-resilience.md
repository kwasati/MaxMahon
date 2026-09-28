---
project: MaxMahon
created: 2026-05-07
last_updated: 2026-05-07
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: scan 933 หุ้น 2 ครั้งติดกันในวันเดียวกัน → ได้ dividend_streak เท่ากันทุกตัว (ไม่มีตัว streak=0 ทั้งที่ yahoo direct call ดึง DPS ได้) — ไม่มี cache poison ของ data ที่ไม่ครบ

### รายละเอียด
- Bug 3 ชั้น (verified reproducible): yahoo dividend_history flake ใน parallel context (ThreadPool 5 workers) + silent except Exception:pass ใน _fetch_yahoo_supplement (data_adapter.py:538-539) + cache save ที่ไม่ check data integrity (fetch_data.py:222-231) → cache poison 1 วัน → rerun hit cache stale
- Fix 1 — Retry tk.dividend_history() 3 attempts รวม (เดิม 1) — ใช้ time.sleep(0.5, 1.0) backoff ระหว่าง attempts. ถ้า empty result OR throw exception ใน attempt 1-2 → log warning + retry. attempt 3 fail → log warning final + yield empty.
- Fix 2 — Surface error: เปลี่ยน `except Exception: pass` → log warning ทุก attempt fail + final attempt count. ใช้ logger.warning ที่มีอยู่แล้ว ไม่เพิ่ม logger config
- Fix 3 — Cache integrity guard ใน _save_to_cache: ถ้า dividend_yield > 0 (มี yield = หุ้นจ่ายปันผลจริง) AND dividend_history empty → skip cache + log warning. Heuristic: หุ้นที่จ่ายปันผลจริงควรมี DPS history — empty = bug indicator
- ถ้า dividend_yield = 0/None + DPS empty = หุ้นไม่จ่ายปันผล cache ได้ปกติ (ไม่ใช่ bug)
- ต้องเพิ่ม `import time` ที่ top ของ data_adapter.py (ไม่มี)
- Smoke test 5 cases: 3 cache guard cases (yield>0+empty=skip, yield=0+empty=save, yield>0+filled=save) + 2 retry cases (3rd attempt success, all 3 fail give up)
- Smoke test ใช้ unittest.mock.patch('yahooquery.Ticker', ...) — Ticker ถูก import ภายใน function (line 451) ต้อง patch global module ไม่ใช่ patch.object(da, 'Ticker')

### Scope Boundary
**In scope:**
- projects/MaxMahon/scripts/data_adapter.py — เพิ่ม import time + retry loop รอบ tk.dividend_history() block (lines 514-539) + log warning
- projects/MaxMahon/scripts/fetch_data.py — เพิ่ม integrity guard ใน _save_to_cache (lines 222-231)
- projects/MaxMahon/scripts/_smoke_yahoo_resilience.py — สร้างใหม่ smoke test fixture-based + mock

**Out of scope:**
- screen_stocks.py — ไม่แตะ filter logic (งานก่อนเสร็จแล้ว)
- thaifin layer / SETSMART layer — ไม่ retry (เสถียรอยู่แล้ว, bug อยู่ที่ yahoo ชั้นเดียว)
- ThreadPoolExecutor max_workers — keep 5 ตามเดิม
- Cache structure / cache directory location — keep ตามเดิม
- Scoring functions (dividend_score, valuation_score) — keep ตามเดิม
- _fetch_yahoo_supplement function refactor — แค่แก้ retry รอบ dividend_history block ภายใน function ไม่รื้อ function
- yahoo summary_detail / cash_flow / income_statement — ไม่เพิ่ม retry (bug จริงอยู่ที่ dividend_history ชั้นเดียว)
- Production scan rerun — แยก task หลัง /done ไม่ใช่ใน plan นี้

### Non-goals
- ไม่ refetch cache ทุกตัวที่ poison อยู่ตอนนี้ — clear cache มือเป็น manual ops ก่อน rerun (กัน task ใหญ่)
- ไม่ track retry stats / metrics — แค่ log warning เพียงพอ visibility
- ไม่ปรับ structured logging / log level config — ใช้ logger.warning ที่มี
- ไม่ใช้ pytest framework — fixture-based smoke test pattern เดิมตาม project (ไม่มี pytest infra)
- ไม่บังคับ refetch หุ้นที่ cache มี DPS empty เก่า — guard จะ kick in ครั้งหน้า fetch ใหม่

# MaxMahon Yahoo DPS Fetch Resilience + Cache Guard

> Verify reproducible bug: yahoo dividend_history flake ใน parallel → silent catch → empty DPS → cache poison → rerun hit stale cache → คะแนน scan เพี้ยน. Fix 3 ชั้น root cause: retry yahoo + log warning + cache integrity guard. หลัง merge → clear cache มือก่อน rerun → ได้ผล scan ถูกครั้งเดียว

## Phase 1: Yahoo retry + cache guard + smoke verify
- [x] เพิ่ม `import time` ที่ top ของ `projects/MaxMahon/scripts/data_adapter.py` (หลัง line 13-15: json/logging/math) + แก้ block `try/except` รอบ `tk.dividend_history()` ใน function `_fetch_yahoo_supplement` (lines 514-539) ให้ wrap ด้วย retry loop max 3 attempts, ใช้ delays [0.5, 1.0]s, log warning ทุก fail (empty result หรือ exception). Scope: ไม่แก้ outer try/except (line 444-594), ไม่แตะ block อื่นใน function (summary_detail / cash_flow / income_statement). Acceptance: grep `for attempt in range(3)` ใน _fetch_yahoo_supplement = 1 match; grep `time.sleep` ใน data_adapter.py ≥ 1 match; `py -m py_compile scripts/data_adapter.py` exit 0; smoke test retry case ผ่าน (Phase 4).
- [x] เพิ่ม integrity guard ใน function `_save_to_cache` ของ `projects/MaxMahon/scripts/fetch_data.py` (lines 222-231) — หลัง `if not data or data.get('delisted') or not data.get('price'): return` เพิ่ม block check: ถ้า `dividend_yield > 0` AND `dividend_history` empty → log warning + return (skip save). Scope: ไม่แก้ logic อื่น, ไม่แตะ _load_from_cache, ไม่เปลี่ยน cache directory. Acceptance: grep `dividend_yield` ใน _save_to_cache = 1 match; grep `cache skip` (case insensitive) ใน fetch_data.py = 1 match; `py -m py_compile scripts/fetch_data.py` exit 0; smoke test cache guard cases ผ่าน 3 case (Phase 4).
- [x] สร้างไฟล์ใหม่ `projects/MaxMahon/scripts/_smoke_yahoo_resilience.py` — fixture-based smoke test + unittest.mock 5 cases: (1) cache_skip_when_dy_positive_but_dps_empty: data dict yield=5/dps={} → _save_to_cache → file ไม่ถูกสร้าง; (2) cache_save_when_dy_zero_dps_empty: yield=0/dps={} (non-dividend stock) → file ถูกสร้าง; (3) cache_save_when_dy_positive_dps_filled: yield=5/dps={2024:1.5,...} → file ถูกสร้าง; (4) yahoo_retry_succeeds_on_3rd_attempt: mock dividend_history fail attempt 1+2 success attempt 3 → assert call count=3 + dps non-empty; (5) yahoo_retry_gives_up_after_3_attempts: mock fail ทั้ง 3 → assert call count=3 + dps empty. ใช้ patch('yahooquery.Ticker', ...). Scope: ห้าม fetch จริง, ห้ามแก้ data_adapter หรือ fetch_data ในไฟล์นี้. Acceptance: ไฟล์ `_smoke_yahoo_resilience.py` exists; `py -m py_compile scripts/_smoke_yahoo_resilience.py` exit 0.
- [x] รัน smoke test `py projects/MaxMahon/scripts/_smoke_yahoo_resilience.py` แล้ว verify exit 0 + print `[PASS] all 5 tests passed`. ถ้า case ไหน fail → debug source logic (ห้ามแก้ test เพื่อทำให้ผ่าน). Verify เพิ่มเติมหลัง smoke pass: BBL/AMATA fetch ปกติ ไม่ regression — รัน inline `py -c "import sys; sys.path.insert(0, 'scripts'); from fetch_data import fetch_multi_year_safe; print(len(fetch_multi_year_safe('BBL.BK', use_cache=False).get('dividend_history', {})))"` cwd=projects/MaxMahon → ต้อง print >= 15 (BBL มี DPS ≥ 22 ปี). Scope: ไม่ run scan 933 หุ้น, ไม่ทดสอบ production data path. Acceptance: smoke exit 0 + BBL inline fetch ≥ 15 years.

### Reference
```python
# current — data_adapter.py:13-19 (imports — เพิ่ม time)
import json
import logging
import math
from datetime import datetime
from pathlib import Path

import pandas as pd

# new — เพิ่ม `import time` ระหว่าง logging กับ math
import json
import logging
import math
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
```

```python
# current — data_adapter.py:514-539 (dividend_history block ใน _fetch_yahoo_supplement)
        # Dividends — yahooquery dividend_history returns DataFrame
        divs = None
        recent_divs = []
        dps_by_year = {}
        dps_by_fiscal_year = {}
        fy_is_complete = {}
        try:
            divs_df = tk.dividend_history(start="2000-01-01")
            if hasattr(divs_df, 'shape') and not divs_df.empty:
                # Multi-index (symbol, date) — flatten to date index
                if hasattr(divs_df.index, 'get_level_values'):
                    levels = divs_df.index.get_level_values(0)
                    if yq_sym in levels:
                        divs_df = divs_df.xs(yq_sym, level=0)
                # Extract dividends column (named or first col)
                if 'dividends' in divs_df.columns:
                    divs = divs_df['dividends']
                else:
                    divs = divs_df.iloc[:, 0]
                recent_divs = divs.tail(8).tolist() if len(divs) > 0 else []
                for idx, val in divs.items():
                    try:
                        y = idx.year if hasattr(idx, 'year') else int(str(idx)[:4])
                        dps_by_year[y] = dps_by_year.get(y, 0) + round(float(val), 4)
                    except (ValueError, TypeError):
                        continue
                # FY attribution per SET DIY methodology
                fy_result = _attribute_dividends_to_fiscal_years(divs)
                dps_by_fiscal_year = fy_result['by_fy']
                fy_is_complete = fy_result['is_complete']
        except Exception:
            pass

# new — wrap in retry loop, log warnings, surface error
        # Dividends — yahooquery dividend_history returns DataFrame
        # Wrapped in retry loop: yahoo dividend_history flake in parallel context
        # silently returned empty before, poisoning the day's cache.
        divs = None
        recent_divs = []
        dps_by_year = {}
        dps_by_fiscal_year = {}
        fy_is_complete = {}
        DIV_RETRY_ATTEMPTS = 3
        DIV_RETRY_DELAYS = [0.5, 1.0]  # seconds, applied between attempts (last has no follow-up)
        for attempt in range(DIV_RETRY_ATTEMPTS):
            try:
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
                    break  # success — exit retry loop
                else:
                    # empty result — log + retry
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
```

```python
# current — fetch_data.py:222-231
def _save_to_cache(symbol: str, data: dict) -> None:
    if not data or data.get('delisted') or not data.get('price'):
        return  # don't cache failures
    cache_dir = _cache_dir_today()
    cache_dir.mkdir(parents=True, exist_ok=True)
    p = cache_dir / f'{symbol}.json'
    try:
        p.write_text(json.dumps(data, ensure_ascii=False, default=str), encoding='utf-8')
    except Exception as e:
        logger.warning(f'cache save failed for {symbol}: {e}')

# new — add integrity guard for DPS data
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
```

```python
# new — projects/MaxMahon/scripts/_smoke_yahoo_resilience.py
"""Smoke test for yahoo DPS fetch resilience + cache integrity guard.

Fixture + mock-based — does not fetch real market data.
Verifies _fetch_yahoo_supplement retry logic + _save_to_cache integrity guard.
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


# === Cache guard tests ===

def test_cache_skip_when_dy_positive_but_dps_empty():
    from fetch_data import _save_to_cache, _cache_dir_today
    cache_dir = _cache_dir_today()
    cache_dir.mkdir(parents=True, exist_ok=True)
    test_sym = "_SMOKETEST_GUARD_A.BK"
    p = cache_dir / f"{test_sym}.json"
    if p.exists():
        p.unlink()
    data = {"symbol": test_sym, "price": 100, "dividend_yield": 5.0, "dividend_history": {}}
    _save_to_cache(test_sym, data)
    assert not p.exists(), f"expected cache skip but file exists: {p}"
    print("[PASS] cache skip when yield>0 + dps empty (poisoned data)")


def test_cache_save_when_dy_zero_dps_empty():
    from fetch_data import _save_to_cache, _cache_dir_today
    cache_dir = _cache_dir_today()
    cache_dir.mkdir(parents=True, exist_ok=True)
    test_sym = "_SMOKETEST_GUARD_B.BK"
    p = cache_dir / f"{test_sym}.json"
    if p.exists():
        p.unlink()
    data = {"symbol": test_sym, "price": 100, "dividend_yield": 0, "dividend_history": {}}
    _save_to_cache(test_sym, data)
    assert p.exists(), "expected cache save but no file (legit non-dividend stock)"
    p.unlink()
    print("[PASS] cache save when yield=0 + dps empty (legit non-dividend stock)")


def test_cache_save_when_dy_positive_dps_filled():
    from fetch_data import _save_to_cache, _cache_dir_today
    cache_dir = _cache_dir_today()
    cache_dir.mkdir(parents=True, exist_ok=True)
    test_sym = "_SMOKETEST_GUARD_C.BK"
    p = cache_dir / f"{test_sym}.json"
    if p.exists():
        p.unlink()
    data = {
        "symbol": test_sym,
        "price": 100,
        "dividend_yield": 5.0,
        "dividend_history": {2024: 1.5, 2023: 1.4, 2022: 1.3},
    }
    _save_to_cache(test_sym, data)
    assert p.exists(), "expected cache save (normal case)"
    p.unlink()
    print("[PASS] cache save when yield>0 + dps filled (normal)")


# === Yahoo retry tests ===

def _build_mock_ticker(dividend_history_fn):
    mock_tk = MagicMock()
    mock_tk.dividend_history = dividend_history_fn
    mock_tk.summary_detail = {"TEST.BK": {"dividendYield": 0.05, "trailingPE": 10}}
    mock_tk.price = {"TEST.BK": {"regularMarketPrice": 100, "shortName": "TEST", "currency": "THB"}}
    mock_tk.key_stats = {"TEST.BK": {}}
    mock_tk.financial_data = {"TEST.BK": {}}
    mock_tk.cash_flow.return_value = pd.DataFrame()
    mock_tk.income_statement.return_value = pd.DataFrame()
    return mock_tk


def _success_dividend_df():
    idx = pd.MultiIndex.from_tuples([
        ("TEST.BK", pd.Timestamp("2022-04-01")),
        ("TEST.BK", pd.Timestamp("2023-04-01")),
        ("TEST.BK", pd.Timestamp("2024-04-01")),
    ], names=["symbol", "date"])
    return pd.DataFrame({"dividends": [1.0, 1.1, 1.2]}, index=idx)


def test_yahoo_retry_succeeds_on_3rd_attempt():
    call_count = {"n": 0}

    def flaky(*args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] < 3:
            raise Exception(f"simulated flake {call_count['n']}")
        return _success_dividend_df()

    mock_tk = _build_mock_ticker(flaky)
    with patch("yahooquery.Ticker", return_value=mock_tk):
        from data_adapter import _fetch_yahoo_supplement
        result = _fetch_yahoo_supplement("TEST.BK")
    assert call_count["n"] == 3, f"expected 3 attempts, got {call_count['n']}"
    dps = result.get("dps_by_year", {})
    assert len(dps) > 0, f"expected DPS after retry, got: {dps}"
    print(f"[PASS] yahoo retry succeeds on 3rd attempt (got {len(dps)} years)")


def test_yahoo_retry_gives_up_after_3_attempts():
    call_count = {"n": 0}

    def always_fail(*args, **kwargs):
        call_count["n"] += 1
        raise Exception(f"persistent flake {call_count['n']}")

    mock_tk = _build_mock_ticker(always_fail)
    with patch("yahooquery.Ticker", return_value=mock_tk):
        from data_adapter import _fetch_yahoo_supplement
        result = _fetch_yahoo_supplement("TEST.BK")
    assert call_count["n"] == 3, f"expected exactly 3 attempts, got {call_count['n']}"
    assert result.get("dps_by_year", {}) == {}, "expected empty DPS after persistent failure"
    print("[PASS] yahoo retry gives up cleanly after 3 attempts")


if __name__ == "__main__":
    failures = []
    tests = [
        test_cache_skip_when_dy_positive_but_dps_empty,
        test_cache_save_when_dy_zero_dps_empty,
        test_cache_save_when_dy_positive_dps_filled,
        test_yahoo_retry_succeeds_on_3rd_attempt,
        test_yahoo_retry_gives_up_after_3_attempts,
    ]
    for fn in tests:
        try:
            fn()
        except AssertionError as e:
            failures.append(f"{fn.__name__}: {e}")
            print(f"[FAIL] {fn.__name__}: {e}")
        except Exception as e:
            failures.append(f"{fn.__name__}: {type(e).__name__}: {e}")
            print(f"[FAIL] {fn.__name__}: {type(e).__name__}: {e}")
    print()
    if failures:
        print(f"[FAIL] {len(failures)} test(s) failed: {failures}")
        sys.exit(1)
    print(f"[PASS] all {len(tests)} tests passed")
    sys.exit(0)
```
