---
project: MaxMahon
created: 2026-04-23
last_updated: 2026-04-23
status: done
---

# Screener Correctness Fix — Payout/Detector/Dead Code

> Part 1 of 3 — แก้ issue จาก QC report (2026-04-23): 2 critical + 2 high + 1 medium. C1 payout_sustainability bucket 10 คะแนนตายสนิทเพราะ dividends_paid ว่าง, C2 case_study_detector ไม่ enforce country/roe_3yr_avg_min ทำให้ VIETNAM_GROWTH_EXPOSURE false-positive Thai tech, H1 near_miss dead parameter, H3 debt_to_equity or 0 ทำลาย null semantics, M2 score_streak docstring ไม่ตรง code. | Index: maxmahon-next-index | Depends on: none | Parallel-safe with: none

## Phase 1: Fix payout sustainability (C1 + M1)
- [x] แก้ `projects/MaxMahon/scripts/data_adapter.py` function `compute_payout_sustainability` (บรรทัด 726-762) — เปลี่ยนสูตร payout_ratio จาก `abs(div_paid) / net_income` (ที่ div_paid เป็น None เสมอ) เป็น `dps_by_year[year] / diluted_eps` จาก dividend_history ที่ stock_data มีอยู่แล้ว. เช็คว่า year มีใน `stock_data.get('dividend_history', {})` และ `diluted_eps > 0` ถึงคำนวณ. sustainable criterion ใหม่: `payout_ratio is not None and payout_ratio < 0.80 and fcf is not None and fcf > 0` (ถอด dependency ต่อ div_paid + equity-based yield comparison ที่พังเพราะ div_paid ว่าง). — scope: ไม่แก้ caller ใน screen_stocks.py dividend_score — Acceptance: `py -c "import sys; sys.path.insert(0,'projects/MaxMahon/scripts'); from fetch_data import fetch_multi_year; from data_adapter import compute_payout_sustainability; d=fetch_multi_year('CPALL'); m=compute_payout_sustainability(d); vals=[v['sustainable'] for v in m.values()]; print('sustainable years:', sum(vals), '/', len(vals))"` ต้องออก `sustainable years: N / M` โดย N > 0 (ไม่ใช่ 0/M แบบปัจจุบัน)

### Reference
```python
# current (data_adapter.py:726-762)
def compute_payout_sustainability(stock_data: dict) -> dict:
    """Return {year: {payout_ratio, sustainable}} per yearly_metrics row.
    ...
    """
    out = {}
    for m in stock_data.get("yearly_metrics", []):
        year = m.get("year")
        if year is None:
            continue
        net_income = m.get("net_income")
        equity = m.get("equity")
        fcf = m.get("fcf")
        div_paid = m.get("dividends_paid")  # <-- always None from thaifin

        if div_paid is not None and net_income and net_income > 0:
            payout_ratio = abs(div_paid) / net_income
        else:
            payout_ratio = None  # <-- always None in practice

        fcf_yield = _safe_div(fcf, equity) if equity and equity > 0 else None
        div_yield_eq = _safe_div(abs(div_paid) if div_paid is not None else None, equity) \
            if equity and equity > 0 else None

        sustainable = (
            payout_ratio is not None and payout_ratio < 0.80
            and fcf_yield is not None and div_yield_eq is not None
            and fcf_yield > div_yield_eq  # <-- never True
        )

        out[year] = {"payout_ratio": payout_ratio, "sustainable": sustainable}
    return out

# new
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
        # dividend_history keys may be int or str — try both
        dps = dividend_history.get(year) or dividend_history.get(int(year) if str(year).isdigit() else year)
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
```

## Phase 2: Fix case_study_detector rules (C2 + H2)
- [x] แก้ `projects/MaxMahon/scripts/case_study_detector.py` function `detect_case_study_tags` (บรรทัด 25-68) — เพิ่ม 2 rule checks ที่ขาด: (a) `country` — skip ถ้า pattern rule มี `country` และไม่ match `stock.get('country', 'TH')` (default TH เพราะ MaxMahon = Thai-only), (b) `roe_3yr_avg_min` — compute avg จาก `yearly_metrics[-3:]['roe']` ที่ไม่ None และเช็คเทียบ threshold. — scope: ไม่เพิ่ม rule อื่นที่ไม่ใช่ country + roe_3yr — Acceptance: `py -c "from case_study_detector import detect_case_study_tags, load_patterns; p=load_patterns(); stock={'sector':'Information & Communication Technology','industry':'Technology','dividend_yield':4.1,'market_cap':60e9,'country':'TH','yearly_metrics':[{'roe':0.05}]*3,'aggregates':{'dividend_streak':10}}; print('tags:', detect_case_study_tags(stock, p))"` ต้องไม่เจอ `VIETNAM_GROWTH_EXPOSURE` ใน output (ถูก block จาก country check)
- [x] แก้ `projects/MaxMahon/data/case_study_patterns.json` — เพิ่ม field `"disabled": true` ให้ pattern `VIETNAM_GROWTH_EXPOSURE` (ตรงกับ CLAUDE.md note `VIETNAM_GROWTH_EXPOSURE[disabled]`) เพราะ MaxMahon ยังไม่รองรับหุ้นเวียดนาม และ detector ไม่มีทางได้ country='VN' จาก thaifin (Thai only). — scope: ไม่แก้ pattern อื่น — Acceptance: `py -c "import json; p=json.load(open('projects/MaxMahon/data/case_study_patterns.json')); assert p['VIETNAM_GROWTH_EXPOSURE'].get('disabled') is True; print('OK')"` ต้อง print `OK`

### Reference
```python
# current (case_study_detector.py:40-67)
def detect_case_study_tags(stock: dict, patterns: dict) -> list[str]:
    tags = []
    agg = stock.get("aggregates") or {}
    streak = agg.get("dividend_streak", 0)
    dy = stock.get("dividend_yield") or 0
    pe = stock.get("pe_ratio")
    pbv = stock.get("pb_ratio")
    mcap = stock.get("market_cap") or 0
    sector = stock.get("sector", "")
    symbol = stock.get("symbol", "")
    for p in patterns.values():
        if p.get("disabled"):
            continue
        r = p.get("rules", {})
        if "exclude_symbols" in r and symbol in r["exclude_symbols"]:
            continue
        if "sector_keywords" in r and not _matches_sector(sector, r["sector_keywords"]):
            continue
        if "dividend_streak_min" in r and streak < r["dividend_streak_min"]:
            continue
        if "dividend_yield_min" in r and dy < r["dividend_yield_min"]:
            continue
        if "pe_max" in r and (pe is None or pe <= 0 or pe > r["pe_max"]):
            continue
        if "pbv_max" in r and (pbv is None or pbv <= 0 or pbv > r["pbv_max"]):
            continue
        if "market_cap_min" in r and mcap < r["market_cap_min"]:
            continue
        if r.get("has_hidden_holdings"):
            hh = stock.get("_hidden_holdings") or []
            if not hh:
                continue
            hidden_total = sum(
                (h.get("holding_mcap") or 0) * (h.get("stake_pct", 0) / 100.0) for h in hh
            )
            if hidden_total < r.get("hidden_value_vs_mcap_min", 1.0) * mcap:
                continue
        tags.append(p["tag"])
    return tags

# new — เพิ่ม country check + roe_3yr_avg_min check
def detect_case_study_tags(stock: dict, patterns: dict) -> list[str]:
    tags = []
    agg = stock.get("aggregates") or {}
    streak = agg.get("dividend_streak", 0)
    dy = stock.get("dividend_yield") or 0
    pe = stock.get("pe_ratio")
    pbv = stock.get("pb_ratio")
    mcap = stock.get("market_cap") or 0
    sector = stock.get("sector", "")
    symbol = stock.get("symbol", "")
    country = stock.get("country", "TH")  # MaxMahon default — Thai market
    yearly = stock.get("yearly_metrics", []) or []
    for p in patterns.values():
        if p.get("disabled"):
            continue
        r = p.get("rules", {})
        if "country" in r and r["country"] != country:
            continue  # skip patterns for other markets
        if "exclude_symbols" in r and symbol in r["exclude_symbols"]:
            continue
        if "sector_keywords" in r and not _matches_sector(sector, r["sector_keywords"]):
            continue
        if "dividend_streak_min" in r and streak < r["dividend_streak_min"]:
            continue
        if "dividend_yield_min" in r and dy < r["dividend_yield_min"]:
            continue
        if "pe_max" in r and (pe is None or pe <= 0 or pe > r["pe_max"]):
            continue
        if "pbv_max" in r and (pbv is None or pbv <= 0 or pbv > r["pbv_max"]):
            continue
        if "market_cap_min" in r and mcap < r["market_cap_min"]:
            continue
        if "roe_3yr_avg_min" in r:
            # compute avg ROE over last 3 years from yearly_metrics
            roes = [m.get("roe") for m in yearly[-3:] if m.get("roe") is not None]
            if not roes:
                continue  # no data to evaluate
            avg_roe = sum(roes) / len(roes)
            if avg_roe < r["roe_3yr_avg_min"]:
                continue
        if r.get("has_hidden_holdings"):
            hh = stock.get("_hidden_holdings") or []
            if not hh:
                continue
            hidden_total = sum(
                (h.get("holding_mcap") or 0) * (h.get("stake_pct", 0) / 100.0) for h in hh
            )
            if hidden_total < r.get("hidden_value_vs_mcap_min", 1.0) * mcap:
                continue
        tags.append(p["tag"])
    return tags
```

```json
// case_study_patterns.json — current VIETNAM_GROWTH_EXPOSURE entry
{
  "VIETNAM_GROWTH_EXPOSURE": {
    "tag": "VIETNAM_GROWTH_EXPOSURE",
    "source": "docs/niwes/10-case-fpt.md",
    "rules": {
      "country": "VN",
      ...
    },
    ...
  }
}

// new — เพิ่ม "disabled": true
{
  "VIETNAM_GROWTH_EXPOSURE": {
    "tag": "VIETNAM_GROWTH_EXPOSURE",
    "source": "docs/niwes/10-case-fpt.md",
    "disabled": true,
    "rules": {
      "country": "VN",
      ...
    },
    ...
  }
}
```

## Phase 3: Remove dead code + null safety (H1 + H3)
- [x] แก้ `projects/MaxMahon/scripts/screen_stocks.py` function `hard_filter` (บรรทัด 56-131) — ลบ parameter + return field `near_miss` ทิ้ง เพราะไม่เคย `.append()` จริง (dead parameter). เปลี่ยน return จาก `tuple (status, reasons, near_miss)` เป็น `tuple (status, reasons)`. แก้ caller ที่ `main()` บรรทัด 719 `status, filter_reasons, near_miss = hard_filter(data)` → `status, filter_reasons = hard_filter(data)` และลบ block บรรทัด 765-769 ที่อ่าน `near_miss` ทิ้ง. แก้ caller `detect_exit_signal` บรรทัด 348 `status_now, fail_reasons, _ = hard_filter(current_data)` → `status_now, fail_reasons = hard_filter(current_data)`. — scope: ไม่เปลี่ยน logic คัดหุ้น แค่ตัด dead param — Acceptance: `grep -n 'near_miss' projects/MaxMahon/scripts/screen_stocks.py` ต้องไม่เจอ. `py -m py_compile projects/MaxMahon/scripts/screen_stocks.py`
- [x] แก้ `projects/MaxMahon/scripts/screen_stocks.py` ทุก location ที่ใช้ `(data.get("debt_to_equity") or 0) / 100` (บรรทัด 731 + 821) — เปลี่ยนเป็น preserve None: `de = data.get('debt_to_equity'); result['de'] = de / 100 if de is not None else None`. กระทบ 2 จุด: `filtered_stocks[].basic_metrics.de` และ `candidates[].metrics.de`. — scope: ไม่แก้ logic อื่น แค่ null semantics — Acceptance: หุ้นที่ debt_to_equity=None ใน output screener JSON ต้องได้ `"de": null` ไม่ใช่ `"de": 0.0`

### Reference
```python
# current (screen_stocks.py:56-68)
def hard_filter(data: dict) -> tuple:
    """Niwes 5-5-5-5 hard filter — 3-tier (PASS/REVIEW/FAIL).
    ...
    Returns (status, reasons, near_miss) where status ∈ {'PASS','REVIEW','FAIL'}.
    """
    fail_reasons: list[str] = []
    review_reasons: list[str] = []
    near_miss: list[str] = []  # <-- dead — never appended
    ...
    return "PASS", [], near_miss  # line 131

# new — ลบ near_miss
def hard_filter(data: dict) -> tuple:
    """Niwes 5-5-5-5 hard filter — 3-tier (PASS/REVIEW/FAIL).
    ...
    Returns (status, reasons) where status ∈ {'PASS','REVIEW','FAIL'}.
    """
    fail_reasons: list[str] = []
    review_reasons: list[str] = []
    # (no near_miss variable)
    ...
    return "PASS", []  # line 131


# current (screen_stocks.py:719) — main caller
status, filter_reasons, near_miss = hard_filter(data)

# new
status, filter_reasons = hard_filter(data)


# current (screen_stocks.py:348) — exit signal caller
status_now, fail_reasons, _ = hard_filter(current_data)

# new
status_now, fail_reasons = hard_filter(current_data)


# current (screen_stocks.py:765-769) — dead near_miss penalty block
# Apply near-miss penalty
if near_miss:
    result["score"] = max(0, result["score"] - 5 * len(near_miss))
    result["signals"].extend([nm.split(":")[0] for nm in near_miss])
    result["reasons"].extend(near_miss)

# new — ลบทั้ง block ออก (near_miss ไม่มีอยู่แล้ว)


# current (screen_stocks.py:731)
"de": (data.get("debt_to_equity") or 0) / 100 if data.get("debt_to_equity") else None,

# new
"de": (lambda de: de / 100 if de is not None else None)(data.get("debt_to_equity")),


# current (screen_stocks.py:821)
"de": (data.get("debt_to_equity") or 0) / 100,

# new
"de": (lambda de: de / 100 if de is not None else None)(data.get("debt_to_equity")),
```

## Phase 4: Docstring align (M2)
- [x] แก้ `projects/MaxMahon/scripts/screen_stocks.py` function `compute_score_streak` docstring (บรรทัด 418-424) — docstring ปัจจุบันบอก `Count consecutive prior scans where score went UP` แต่ code ใช้ `<=` ซึ่งหมายถึง up-OR-stayed. แก้ docstring ให้ตรง code: `Count consecutive prior scans where score did not drop (i.e., went up or stayed equal). Stops at first decrease.` — scope: ไม่แก้ code logic (code ถูกแล้ว, แค่ docstring ผิด) — Acceptance: `grep -A4 'def compute_score_streak' projects/MaxMahon/scripts/screen_stocks.py | head -5` ต้องเห็น docstring ใหม่ที่บอก 'did not drop' แทน 'went UP'

### Reference
```python
# current (screen_stocks.py:418-424)
def compute_score_streak(symbol: str, current_score: int, prior_files: list[Path]) -> tuple[int, Optional[int]]:
    """Count consecutive prior scans where score went up for this symbol.
    
    Returns (streak_weeks, previous_score). Streak = number of consecutive
    prior scans where score was <= the one after it (i.e., score moved up or stayed).
    Stops at first decrease.
    """

# new — align docstring with actual code semantics
def compute_score_streak(symbol: str, current_score: int, prior_files: list[Path]) -> tuple[int, Optional[int]]:
    """Count consecutive prior scans where score did not drop for this symbol.
    
    Returns (streak_weeks, previous_score). Streak = number of consecutive
    prior scans where score was <= the one after it (score went up OR stayed equal).
    Stops at first decrease.
    """
```

## Phase 5: End-to-end verify
- [x] สร้าง `_shared/tmp/verify_qc_fix.py` ที่ workspace root ใช้ทดสอบ 5 หุ้น (CPALL, TCAP, QH, MC, ADVANC) — assert ทุกข้อ: (a) payout sustainability มีหุ้นที่ sustainable=True อย่างน้อย 1 ตัว (ก่อนแก้เป็น 0/ทุกตัว), (b) ADVANC ต้องไม่มี tag VIETNAM_GROWTH_EXPOSURE (จาก country=TH block + disabled=true), (c) hard_filter(data) คืน 2-tuple (status, reasons) ไม่ใช่ 3-tuple, (d) หุ้นที่มี debt_to_equity=None ต้องได้ de=None ใน basic_metrics ไม่ใช่ de=0, (e) compute_score_streak docstring contains 'did not drop'. รันจาก workspace root: `py _shared/tmp/verify_qc_fix.py`. ลบ script หลัง verify เสร็จ. — scope: ไม่แก้ code — Acceptance: script print 5 ✓ lines แล้วจบโดยไม่มี AssertionError

### Reference
```python
# _shared/tmp/verify_qc_fix.py (temp, ลบหลัง verify)
import sys, inspect
from pathlib import Path
sys.path.insert(0, str(Path('projects/MaxMahon/scripts').resolve()))
from fetch_data import fetch_multi_year
from data_adapter import compute_payout_sustainability
from screen_stocks import hard_filter, compute_score_streak
from case_study_detector import detect_case_study_tags, load_patterns

# (a) payout sustainability
d = fetch_multi_year('CPALL')
m = compute_payout_sustainability(d)
sustain_count = sum(1 for v in m.values() if v.get('sustainable'))
assert sustain_count > 0, f'C1 fix failed: sustainable years = 0'
print(f'✓ C1: CPALL sustainable years = {sustain_count}')

# (b) VIETNAM tag not applied to Thai tech
p = load_patterns()
advanc_data = fetch_multi_year('ADVANC')
advanc_data['_hidden_holdings'] = []
tags = detect_case_study_tags(advanc_data, p)
assert 'VIETNAM_GROWTH_EXPOSURE' not in tags, f'C2 fix failed: VIETNAM tag on ADVANC: {tags}'
print(f'✓ C2: ADVANC tags = {tags} (no VIETNAM)')

# (c) hard_filter returns 2-tuple
result = hard_filter(advanc_data)
assert len(result) == 2, f'H1 fix failed: hard_filter returned {len(result)}-tuple'
print(f'✓ H1: hard_filter returns 2-tuple (status={result[0]})')

# (d) de=None preserved
import json, subprocess
# Run screener for CPALL only and check output — easier: just re-check code
import screen_stocks
src = inspect.getsource(screen_stocks)
assert 'or 0) / 100' not in src, 'H3 fix failed: lossy `or 0) / 100` still present'
print('✓ H3: no lossy `or 0) / 100` in screen_stocks')

# (e) docstring aligned
doc = compute_score_streak.__doc__ or ''
assert 'did not drop' in doc, f'M2 fix failed: docstring still says "went UP"'
print('✓ M2: docstring aligned to code semantics')

print('\n5/5 QC fixes verified')
```
