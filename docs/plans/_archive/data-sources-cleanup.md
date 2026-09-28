---
project: 4-MaxMahon
created: 2026-05-22
last_updated: 2026-05-22
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: รัน scan pipeline (py scripts/data_adapter.py BBL + HTC) ก่อน-หลัง cleanup ผลลัพธ์ snapshot fields (dps / dividend_yield / payout_ratio / five_year_avg_yield / fy_is_complete) เท่ากันเป๊ะ + 4 surprises ใน docs/data-sources-guide.md ขึ้น RESOLVED status + grep dead code keys = 0 hits

### รายละเอียด
- #1 ลบ data_adapter.py:294-301 (dividend_history dict computation ใน _fetch_thaifin) + ลบ key 'dividend_history' จาก return dict ที่ line 347 — local vars dividend_yields/closes/five_year_yields/five_year_avg_yield ห้ามลบ (ยังใช้ที่ line 289-292 + return five_year_avg_yield line 352)
- #2 rename key 'fcf' -> 'financing_cf' ที่ _setsmart_financial_to_yearly line 655 + update docstring line 641 — collision เกิดเพราะ key 'fcf' ใน SETSMART dict = financingCashFlow ไม่ใช่ free cash flow (จริงๆ FCF ใน yearly_metrics = OCF - abs(capex) ที่ line 828)
- #5a เพิ่ม function fy_is_complete_by_year(symbol: str) -> dict[int, bool] ใน set_official_adapter.py หลัง dps_by_fiscal_year (line 262) — logic: ดึง cached events + รวบ FYs + dict[fy] = True ทุก FY ยกเว้น fy == datetime.now().year = False (ยังไม่จบ)
- #5b Wire fy_is_complete source-resolved ใน data_adapter.py — import _set_fy_complete ใกล้ line 29, เรียก set_fy_complete หลัง set.or.th success ที่ line 807-810, สร้าง var fy_is_complete = set_fy_complete ถ้า dividend_source=='set_official' ไม่งั้น yf_fy_complete, เปลี่ยน line 902 + line 1024 ให้ใช้ fy_is_complete แทน yf_fy_complete
- #7a inline comment ที่ setsmart_adapter.py ก่อน fetch_eod_by_symbol (line 76) + fetch_eod_all (line 84) อธิบาย adjustedPriceFlag='Y' default intentional + compatible กับ set.or.th DPS (split-adjusted)
- #7b update docs/data-sources-guide.md section 'Surprises / Findings During Audit' (line 473+) — เพิ่ม [RESOLVED 2026-05-22] prefix หน้า #1 #2 #5 #7 + insert note ว่า cleanup done in plan data-sources-cleanup
- Smoke test ก่อน + หลัง cleanup เทียบ snapshot fields ของ BBL + HTC + อย่างน้อย 1 ตัวที่ dividend_source=='yahoo' (เผื่อ fallback path test) — ผลต้อง zero regression
- Backward compat: เก็บ key name 'fy_is_complete' เดิมใน return dict (downstream consumers ใน fetch_data.py:77-190 + data_adapter.py:1171 ใช้ key นี้)
- yf_fy_complete fallback เก็บไว้ — สำหรับ stocks ที่ set.or.th ไม่มี data หรือ exception

### Scope Boundary
**In scope:**
- scripts/data_adapter.py (block ลบ 294-301 + return key 347 + rename line 655 + docstring 641 + import line 29 + wire fy_is_complete หลัง line 817 + ปรับ line 902 + ปรับ return line 1024)
- scripts/set_official_adapter.py (เพิ่ม function fy_is_complete_by_year หลัง line 262 + update __main__ smoke test)
- scripts/setsmart_adapter.py (inline comment block ก่อน fetch_eod_by_symbol line 76 + fetch_eod_all line 84)
- docs/data-sources-guide.md (surprises section line 473-486 status update)

**Out of scope:**
- ไม่แก้ scoring/screener logic ใน scripts/screen_stocks.py (cleanup ไม่กระทบ business rules)
- ไม่แก้ FCF correction logic ที่ data_adapter.py:828 (m['fcf'] = m['ocf'] - abs(capex)) — fcf ใน yearly_metrics ไม่เกี่ยวกับ #2 collision
- ไม่ refactor _fetch_thaifin function structure (เพียงลบ dead block + return key)
- ไม่ rename existing 'fy_is_complete' return key (เก็บชื่อเดิม backward compat กับ fetch_data.py + data_adapter.py:1171)
- ไม่ bump v6.6.1 -> v6.6.2 ที่นี่ (cleanup ไม่ใช่ feature change — version bump ทำตอน /done ถ้าจำเป็น)
- ไม่ add pytest unit tests (Niwes = analyst tool ไม่มี test suite, smoke test ผ่าน scan pipeline ก็พอ)

### Non-goals
- ไม่ deprecate yf_fy_complete fallback — กรณี set.or.th ไม่มี data ยังต้องใช้ yahoo
- ไม่ make set.or.th synthesis เป็น primary unconditionally — เก็บ source-resolve pattern (dividend_source decides)
- ไม่แตะ scoring weights / valuation grade modifiers (ไม่เกี่ยวกับ cleanup)
- ไม่ทำ migration script สำหรับ cache เก่า (cache schema ไม่เปลี่ยน — fy_is_complete สร้างใหม่ทุกครั้ง fetch_fundamentals call)

# MaxMahon Data Sources Cleanup — 4 Surprises Resolution

> Post-audit cleanup ของ 4 surprises ใน MaxMahon data layer — #1 ลบ thaifin dead code / #2 rename SETSMART fcf key collision / #5 synthesize fy_is_complete จาก set.or.th (เปลี่ยนจาก doc-only เป็น code fix หลัง audit) / #7 doc inline comment + guide status update. Cosmetic + safety improvement ไม่กระทบ business logic ไม่ block production

## Phase 1: Cleanup 4 surprises
- [x] [#1] ลบ dead code thaifin dividend_history — แก้ `scripts/data_adapter.py` ลบ block lines 294-301 (dividend_history dict computation ใน _fetch_thaifin) + ลบ key 'dividend_history' จาก return dict ที่ line 347 — scope: ห้ามลบ local vars dividend_yields/closes/five_year_yields/five_year_avg_yield (ยังใช้ที่ line 289-292 + return five_year_avg_yield line 352) — Acceptance: grep 'dividend_history' ใน _fetch_thaifin scope (line 121-380) = 0 hits ทั้ง compute + return, py -c 'from scripts.data_adapter import _fetch_thaifin' import success no NameError
- [x] [#2] rename fcf collision ใน SETSMART aggregation — แก้ `scripts/data_adapter.py` line 655 เปลี่ยน key 'fcf' -> 'financing_cf' ใน `_setsmart_financial_to_yearly` + update docstring line 641 (`eps, ocf, icf, fcf, roe, roa, de` -> `eps, ocf, icf, financing_cf, roe, roa, de`) — scope: ไม่แก้ caller ที่ line 862-869 (ไม่ได้อ่าน fcf key อยู่แล้ว) — Acceptance: grep 'ss_y["fcf"]|ss_y.get("fcf")' = 0 hits ใน data_adapter.py, grep 'financing_cf' = 2 hits (definition line 655 + docstring line 641)
- [x] [#5a] เพิ่ม fy_is_complete_by_year function ใน set_official_adapter — แก้ `scripts/set_official_adapter.py` เพิ่ม function `fy_is_complete_by_year(symbol: str) -> dict[int, bool]` หลัง `dps_by_fiscal_year` (line 262) + update `__main__` smoke test (line 265+) ให้ print ผลลัพธ์ — logic: ดึง events ผ่าน cached_dividends + extract FYs ผ่าน end_operation[:4] + dict[fy] = True เสมอ ยกเว้น fy == datetime.now().year = False (ยังไม่จบ) — Acceptance: py -m scripts.set_official_adapter (รัน smoke test) แสดง fy_is_complete dict ของ HTC non-empty + ถ้า HTC มี FY 2025 = False (current year), FY 2024 ลงไป = True
- [x] [#5b] Wire fy_is_complete source-resolved ใน fetch_fundamentals — แก้ `scripts/data_adapter.py`: (1) เพิ่ม import `fy_is_complete_by_year as _set_fy_complete` ในกลุ่ม set_official_adapter import line 29-30, (2) หลัง set.or.th success block (หลัง line 810) เรียก `set_fy_complete_dict = _set_fy_complete(sym_clean)` + ใน except branch line 813-817 ตั้ง `set_fy_complete_dict = {}`, (3) หลัง try/except (หลัง line 817) สร้าง var `fy_is_complete = set_fy_complete_dict if dividend_source == 'set_official' and set_fy_complete_dict else yf_fy_complete`, (4) เปลี่ยน line 902 `yf_fy_complete.items()` -> `fy_is_complete.items()`, (5) เปลี่ยน return line 1024 `"fy_is_complete": yf_fy_complete` -> `"fy_is_complete": fy_is_complete` — scope: ไม่แตะ yf_fy_complete extraction line 795 (fallback ยังต้องมี) — Acceptance: smoke test BBL (dividend_source=set_official) แสดง fy_is_complete dict ครอบ FY ของ set.or.th, smoke test ตัวที่ set.or.th fail (e.g. mai stock บางตัว) แสดง dividend_source=yahoo + fy_is_complete = yf_fy_complete (fallback path)
- [x] [#7a] inline comment ที่ SETSMART EOD functions — แก้ `scripts/setsmart_adapter.py` เพิ่ม comment block 3-4 บรรทัดก่อน `fetch_eod_by_symbol` (line 76) + ก่อน `fetch_eod_all` (line 84) อธิบาย `adjustedPriceFlag='Y'` default intentional + compatible กับ set.or.th DPS (split-adjusted) สำหรับ DPS x price calculation — scope: ไม่แก้ function signature/body — Acceptance: comment ครอบทั้ง 2 functions, py -c 'import scripts.setsmart_adapter' import success
- [x] [#7b] update data-sources-guide.md surprises status — แก้ `docs/data-sources-guide.md` section 'Surprises / Findings During Audit' (line 473+) เพิ่ม `**[RESOLVED 2026-05-22]**` prefix หน้า items #1 #2 #5 #7 + insert note line ใต้แต่ละ item ว่า `Fix applied in plan: data-sources-cleanup` + เก็บ content เดิมทั้งหมด (เพิ่ม metadata ไม่ใช่แทน) — scope: ไม่แก้ items #0 #3 #3a #4 #6 #8 #9 #10 — Acceptance: grep '[RESOLVED 2026-05-22]' = 4 hits, content เดิมยังคงอยู่ word-for-word
- [x] Smoke test zero regression — รัน 2 commands: (1) `py -c "from scripts.data_adapter import fetch_fundamentals; import json; d=fetch_fundamentals('BBL.BK'); print(json.dumps({'dps':d['dps'],'dividend_yield':d['dividend_yield'],'payout_ratio':d['payout_ratio'],'five_year_avg_yield':d['five_year_avg_yield'],'fy_is_complete':d['fy_is_complete'],'dividend_source':d['dividend_source']},default=str))"` ก่อน cleanup (capture output), (2) เรียกเดิมหลัง cleanup เทียบ — dps + yield + payout + five_year_avg_yield ต้องเท่ากันเป๊ะ, fy_is_complete อาจเปลี่ยน (source-resolved) แต่ต้องมี keys ครอบ FY ของ dividend_history, ทำซ้ำกับ HTC + 1 stock ที่ dividend_source=='yahoo' (fallback path test) — Acceptance: 3 stocks zero regression numeric fields, warnings list เหมือนเดิม

### Reference
```python
# === #1 — current: data_adapter.py:294-301 (DELETE this block) ===
        # Dividend history: DPS per year (dy% * close / 100)
        dividend_history = {}
        for y in dividend_yields:
            dy_val = dividend_yields[y]
            close_val = closes.get(y)
            if dy_val is not None and close_val is not None and close_val > 0:
                dps = dy_val * close_val / 100.0
                dividend_history[y] = round(dps, 4)

# === #1 — current: data_adapter.py:344-347 (DELETE 'dividend_history' key) ===
        return {
            "info": info,
            "yearly_metrics": yearly_metrics,
            "dividend_history": dividend_history,  # <- DELETE this line
            "snapshot": {

# === #1 — new: data_adapter.py:344-347 (after) ===
        return {
            "info": info,
            "yearly_metrics": yearly_metrics,
            "snapshot": {


# === #2 — current: data_adapter.py:638-662 (docstring + dict) ===
def _setsmart_financial_to_yearly(records: list[dict]) -> dict:
    """Group 4 quarters into yearly aggregate. Use Q4 accumulated fields.

    Returns: {year: {revenue, net_profit, eps, ocf, icf, fcf, roe, roa, de,
                      total_assets, shareholder_equity}}
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
                'fcf': r.get('financingCashFlow'),  # <- rename key to 'financing_cf'
                'roe': r.get('roe'),
                'roa': r.get('roa'),
                'de': r.get('de'),
                'total_assets': r.get('totalAssets'),
                'shareholder_equity': r.get('shareholderEquity'),
            }
    return by_year_q4

# === #2 — new: data_adapter.py:638-662 ===
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


# === #5a — current: set_official_adapter.py:247-263 (dps_by_fiscal_year) ===
def dps_by_fiscal_year(symbol: str) -> dict[int, float]:
    """Group cached dividend events by fiscal year (= int(end_operation[:4])).

    Returns {FY: total_dps_rounded_4} like {2022: 1.52, 2023: 1.52, ...}.
    Events whose end_operation year cannot be parsed to int are skipped.
    """
    events = cached_dividends(symbol)
    totals: dict[int, float] = {}
    for ev in events:
        end_op = ev.get('end_operation') or ''
        try:
            fy = int(end_op[:4])
        except (ValueError, TypeError):
            continue
        totals[fy] = totals.get(fy, 0.0) + float(ev.get('dps') or 0)
    return {fy: round(v, 4) for fy, v in totals.items()}

# === #5a — new: ADD function after line 262 (set_official_adapter.py) ===
def fy_is_complete_by_year(symbol: str) -> dict[int, bool]:
    """Synthesize fy_is_complete dict from set.or.th events.

    Logic: every FY present in cached events is marked complete (True),
    except the current calendar year (False — fiscal year not yet closed).
    This mirrors yahoo's yf_fy_complete dict so downstream count_dividend_streak
    and snapshot DPS picker work uniformly when dividend_source='set_official'.

    Returns {FY: True/False} like {2022: True, 2023: True, 2024: True, 2025: False}.
    Empty dict if no events cached.
    """
    events = cached_dividends(symbol)
    current_year = datetime.now().year
    fys = set()
    for ev in events:
        end_op = ev.get('end_operation') or ''
        try:
            fy = int(end_op[:4])
            fys.add(fy)
        except (ValueError, TypeError):
            continue
    return {fy: (fy < current_year) for fy in fys}


# === #5b — current: data_adapter.py:29 (import) + 800-817 (try/except) + 902 + 1024 ===
# line 29
from set_official_adapter import dps_by_fiscal_year as _set_dps_by_fy

# line 800-817
        # Build dividend_history — set.or.th primary, yahoo fallback
        sym_clean = symbol.replace('.BK', '').upper()
        dividend_source = 'unknown'
        _dps_fallback_to_yahoo = False
        try:
            if not _SET_OFFICIAL_AVAILABLE:
                raise RuntimeError('set_official_adapter import failed at module load')
            set_fy_dps = _set_dps_by_fy(sym_clean)
            if set_fy_dps:
                dividend_history = {y: round(dps, 4) for y, dps in set_fy_dps.items()}
                dividend_source = 'set_official'
            else:
                raise ValueError('set.or.th returned empty')
        except Exception as e:
            logger.warning(f'set.or.th DPS fetch failed for {symbol}: {e}; falling back to yahoo')
            dividend_history = {y: round(dps, 4) for y, dps in yf_dps_by_fy.items()}
            dividend_source = 'yahoo'
            _dps_fallback_to_yahoo = True

# line 902
        complete_fys = sorted([y for y, ok in yf_fy_complete.items() if ok])

# line 1024
        "fy_is_complete": yf_fy_complete,

# === #5b — new ===
# line 29 (replace)
from set_official_adapter import dps_by_fiscal_year as _set_dps_by_fy, fy_is_complete_by_year as _set_fy_complete

# line 800-817 (replace whole try/except + add set_fy_complete_dict)
        # Build dividend_history + fy_is_complete — set.or.th primary, yahoo fallback
        sym_clean = symbol.replace('.BK', '').upper()
        dividend_source = 'unknown'
        _dps_fallback_to_yahoo = False
        set_fy_complete_dict: dict = {}
        try:
            if not _SET_OFFICIAL_AVAILABLE:
                raise RuntimeError('set_official_adapter import failed at module load')
            set_fy_dps = _set_dps_by_fy(sym_clean)
            if set_fy_dps:
                dividend_history = {y: round(dps, 4) for y, dps in set_fy_dps.items()}
                dividend_source = 'set_official'
                set_fy_complete_dict = _set_fy_complete(sym_clean)
            else:
                raise ValueError('set.or.th returned empty')
        except Exception as e:
            logger.warning(f'set.or.th DPS fetch failed for {symbol}: {e}; falling back to yahoo')
            dividend_history = {y: round(dps, 4) for y, dps in yf_dps_by_fy.items()}
            dividend_source = 'yahoo'
            _dps_fallback_to_yahoo = True

        # Source-resolved fy_is_complete: use set.or.th synthesis when set_official wins,
        # fall back to yahoo's calendar-based dict otherwise.
        fy_is_complete = set_fy_complete_dict if (dividend_source == 'set_official' and set_fy_complete_dict) else yf_fy_complete

# line 902 (replace yf_fy_complete -> fy_is_complete)
        complete_fys = sorted([y for y, ok in fy_is_complete.items() if ok])

# line 1024 (replace yf_fy_complete -> fy_is_complete)
        "fy_is_complete": fy_is_complete,


# === #7a — current: setsmart_adapter.py:76-86 ===
def fetch_eod_by_symbol(symbol: str, start_date: str, end_date: str | None = None,
                         adjusted: str = "Y") -> list[dict]:
    params = {"symbol": symbol, "startDate": start_date, "adjustedPriceFlag": adjusted}
    if end_date:
        params["endDate"] = end_date
    return _request("eod-price-by-symbol", params)


def fetch_eod_all(date: str, security_type: str = "CS", adjusted: str = "Y") -> list[dict]:
    return _request("eod-price-by-security-type",
                    {"securityType": security_type, "date": date, "adjustedPriceFlag": adjusted})

# === #7a — new: setsmart_adapter.py:76-86 (with comment) ===
# NOTE: adjustedPriceFlag='Y' default is intentional. SETSMART adjusted close is
# compatible with set.or.th DPS (which is also split-adjusted) — yield = DPS/price
# and DPS x price calculations work consistently across both sources. For raw
# historical price comparisons (back-testing), pass adjusted='N' explicitly.
def fetch_eod_by_symbol(symbol: str, start_date: str, end_date: str | None = None,
                         adjusted: str = "Y") -> list[dict]:
    params = {"symbol": symbol, "startDate": start_date, "adjustedPriceFlag": adjusted}
    if end_date:
        params["endDate"] = end_date
    return _request("eod-price-by-symbol", params)


# NOTE: adjustedPriceFlag='Y' default is intentional — see fetch_eod_by_symbol above.
def fetch_eod_all(date: str, security_type: str = "CS", adjusted: str = "Y") -> list[dict]:
    return _request("eod-price-by-security-type",
                    {"securityType": security_type, "date": date, "adjustedPriceFlag": adjusted})


# === #7b — docs/data-sources-guide.md (line 473+) ===
# current (example, line 476):
1. **Dead code in thaifin branch:** `_fetch_thaifin` computes a `dividend_history` dict ...

# new (example):
1. **[RESOLVED 2026-05-22]** **Dead code in thaifin branch:** `_fetch_thaifin` computes a `dividend_history` dict ...
   *Fix applied in plan: data-sources-cleanup*

# Apply same pattern (prepend [RESOLVED 2026-05-22] + append fix note) to items #1, #2, #5, #7.
# Do NOT modify items #0, #3, #3a, #4, #6, #8, #9, #10.
```
