---
project: MaxMahon
created: 2026-04-27
last_updated: 2026-04-27
status: done
---

## Target / Goal
ทำได้: รัน `py -c "from scripts.data_adapter import fetch_stock_data; print(fetch_stock_data('BBL.BK')['dividend_yield'])"` (ที่ `cd projects/MaxMahon`) แล้วได้ yield ระหว่าง 6.5-7.5% (ตรง SET DIY) ไม่ใช่ 10.41% เหมือนปัจจุบัน. Verify ครบ 4 หุ้น (BBL/METCO/QH/SAT) ห่าง SET Streaming ภายใน ±1%.

# Fix DPS Calc — Fiscal Year Attribution (DIY ตรง SET)

> Yahoo's `dividendRate` field คำนวณผิดสำหรับหุ้นไทยจ่ายปันผลปีละ 2 รอบ. Max trust Yahoo ตาบอดทำให้ score 50 คะแนน Dividend + signal NIWES_5555 (yield≥5%) + QUALITY_DIVIDEND ผิดหมด. แก้โดย compute DIY (fiscal year attribution ตาม SET Formula Glossary v3.9) จาก raw `divs` events ที่ดึงจาก yahooquery มาแล้ว.

## Phase 1: เพิ่ม FY attribution helper
- [x] เพิ่ม function `_attribute_dividends_to_fiscal_years(divs)` ใน `projects/MaxMahon/scripts/data_adapter.py` ก่อน function `_fetch_yahoo_supplement` (บรรทัด ~370). Heuristic: ex-date ใน Jan-Jun ของปี N+1 = final ของ FY N / ex-date ใน Jul-Dec ของปี N = interim ของ FY N. Output: dict `{fy_year: total_dps}` รวมเฉพาะ FY ที่ครบ. เพิ่ม flag `is_complete: bool` per FY เพื่อ skip FY ปัจจุบันที่ยังไม่ครบ. — Scope: ห้ามแก้ caller, ห้ามลบ `dps_by_year` calendar bin ของเดิม (เก็บไว้ debug). — Acceptance: เพิ่ม `if __name__ == '__main__':` smoke block ที่ท้ายไฟล์ data_adapter.py ที่: (1) สร้าง pandas Series mock ด้วย events `[(Timestamp('2025-09-15'), 2.0), (Timestamp('2026-04-22'), 10.0)]`, (2) call `_attribute_dividends_to_fiscal_years(mock_divs)`, (3) assert `result['by_fy'][2025] == 12.0`, (4) print 'FY attribution OK' ถ้า assert ผ่าน. รัน `py scripts/data_adapter.py` แล้วต้องเห็น 'FY attribution OK' (ไม่ raise AssertionError)

### Reference
```python
# current (data_adapter.py:367-370 — placeholder location ก่อน _fetch_yahoo_supplement)
def _fetch_yahoo_supplement(symbol: str) -> dict:
    """Fetch supplementary data from yahooquery (price, 52w, forward PE, etc.).
    ...
    """

# new (insert ก่อน _fetch_yahoo_supplement)
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

    # Detect completeness: FY is complete if has both interim+final, OR has only 1 payment but next FY already has payments (means the company paid annually)
    is_complete = {}
    sorted_fys = sorted(by_fy.keys())
    for i, fy in enumerate(sorted_fys):
        periods = {p for _, _, p in events_per_fy.get(fy, [])}
        has_both = 'interim' in periods and 'final' in periods
        has_next_fy = (i < len(sorted_fys) - 1) and (sorted_fys[i+1] in by_fy)
        is_complete[fy] = has_both or has_next_fy

    return {'by_fy': by_fy, 'is_complete': is_complete, 'events_per_fy': events_per_fy}

# smoke test (append ที่ท้ายไฟล์)
if __name__ == '__main__':
    import pandas as pd
    mock_divs = pd.Series(
        [2.0, 10.0],
        index=[pd.Timestamp('2025-09-15'), pd.Timestamp('2026-04-22')],
    )
    result = _attribute_dividends_to_fiscal_years(mock_divs)
    assert result['by_fy'][2025] == 12.0, f"Expected FY2025=12.0, got {result['by_fy'].get(2025)}"
    print('FY attribution OK')
```

## Phase 2: แทนที่ DPS calc ใน data_adapter.py
- [x] แก้ function `_fetch_yahoo_supplement` ใน `projects/MaxMahon/scripts/data_adapter.py` (บรรทัด 437-510). บรรทัด 451-454 ที่ bin DPS ตามปฏิทิน — เก็บไว้ (เป็น `dps_by_year` legacy debug ใน return dict) แต่เพิ่มเรียก `_attribute_dividends_to_fiscal_years(divs)` หลัง bin เสร็จ. เพิ่ม keys ใน return dict (บรรทัด 496-504): `dps_by_fiscal_year` (= result['by_fy']), `fy_is_complete` (= result['is_complete']). — Scope: ห้ามแก้ try/except boundary, ห้ามลบ `dps_by_year` ของเดิม (downstream อาจอ่าน), ห้ามแตะ capex/operating_income blocks (บรรทัด 461-494). — Acceptance: import data_adapter; call `_fetch_yahoo_supplement('BBL.BK')` return dict มี keys ใหม่ครบ + `dps_by_fiscal_year[2025]` = ~12.0 สำหรับ BBL
- [x] แก้ merge logic ใน `projects/MaxMahon/scripts/data_adapter.py` (บรรทัด 540-700) เปลี่ยน 4 ฟิลด์ที่อ่านจาก Yahoo ใช้ FY data แทน:

(a) บรรทัด 547: เพิ่ม `yf_dps_by_fy = yf_supp.get('dps_by_fiscal_year', {})` + `yf_fy_complete = yf_supp.get('fy_is_complete', {})`

(b) บรรทัด 553 `dividend_history` — เปลี่ยน source จาก `yf_dps_by_year` (calendar) → `yf_dps_by_fy` (fiscal). Key semantics เปลี่ยน แต่ schema เดิม dict[int → float] ไม่กระทบ downstream `_build_five_year_history` / `_build_dividend_history_10y` ใน server/app.py.

(c) บรรทัด 600-610 `dy` (dividend_yield) — แทน `dps_current = yf_info.get('dividendRate')` ด้วย: หา latest complete FY จาก `yf_fy_complete`, `dps_current = yf_dps_by_fy[latest_complete_fy]`. ถ้าไม่มี FY ครบเลย → fallback `tf_snap.get('dividend_yield')`. คำนวณ `dy = dps_current / price * 100` เหมือนเดิม.

(d) บรรทัด 614-619 `five_year_avg_yield` — แทน `recent_dps = [yf_dps_by_year[y] for y in ...]` ด้วย: avg DPS ของ 5 FY ครบล่าสุด (skip incomplete current FY) จาก `yf_dps_by_fy` filter โดย `yf_fy_complete[y] is True`. คำนวณ avg / current price * 100 เหมือนเดิม.

(e) บรรทัด 626 `payout_ratio` — แทน `yf_info.get('payoutRatio')` ด้วย: `dps_current` (จาก step c) / EPS ของ FY เดียวกัน. EPS หาจาก `yearly_metrics` row ที่ `m['year'] == latest_complete_fy` field `diluted_eps`. ถ้าไม่มี EPS ตรงปี → fallback `yf_info.get('payoutRatio')`.

— Scope: ห้ามแก้ price, market_cap, pe_ratio, pb_ratio, eps, revenue, cashflow blocks. ห้ามแก้ field อื่นใน return dict (บรรทัด 661-697). — Acceptance: รัน `py -c "import sys; sys.path.insert(0, 'scripts'); from data_adapter import fetch_stock_data; r = fetch_stock_data('BBL.BK'); print('yield=', r['dividend_yield'], 'dps=', r['dps'], 'payout=', r['payout_ratio'])"` (ที่ `cd projects/MaxMahon`) ส่งคืน `dividend_yield` ระหว่าง 6.5-7.5% (ที่ราคา ~158-176), `dps` = ~12.0, `payout_ratio` ~0.5

### Reference
```python
# current (data_adapter.py:445-454)
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

# new (data_adapter.py:445-460 — เพิ่ม FY attribution หลัง calendar bin)
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
        # ...
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

# current (data_adapter.py:546-553)
        # --- DPS fix: use Yahoo dividends as source of truth ---
        yf_dps_by_year = yf_supp.get("dps_by_year", {})
        yf_capex_by_year = yf_supp.get("capex_by_year", {})
        yf_oi_by_year = yf_supp.get("operating_income_by_year", {})
        yf_ie_by_year = yf_supp.get("interest_expense_by_year", {})

        # Build dividend_history from Yahoo DPS (source of truth)
        dividend_history = {y: round(dps, 4) for y, dps in yf_dps_by_year.items()}

# new (data_adapter.py:546-555)
        # --- DPS fix: use FY attribution per SET DIY methodology ---
        yf_dps_by_year = yf_supp.get("dps_by_year", {})  # legacy debug
        yf_dps_by_fy = yf_supp.get("dps_by_fiscal_year", {})
        yf_fy_complete = yf_supp.get("fy_is_complete", {})
        yf_capex_by_year = yf_supp.get("capex_by_year", {})
        yf_oi_by_year = yf_supp.get("operating_income_by_year", {})
        yf_ie_by_year = yf_supp.get("interest_expense_by_year", {})

        # Build dividend_history from FY-attributed DPS (semantics: FY year, not payment year)
        dividend_history = {y: round(dps, 4) for y, dps in yf_dps_by_fy.items()}

# current (data_adapter.py:598-626)
        # --- Dividend: DPS-first, yield = DPS/price ---
        # Current DPS from Yahoo (dividendRate = annual DPS)
        dps_current = yf_info.get("dividendRate")
        # Fallback: trailingAnnualDividendRate
        if dps_current is None:
            dps_current = yf_info.get("trailingAnnualDividendRate")

        # dividend_yield = DPS / price * 100 (percentage)
        if dps_current is not None and price is not None and price > 0:
            dy = dps_current / price * 100
        else:
            # Fallback to thaifin snapshot (may be unreliable)
            dy = tf_snap.get("dividend_yield")

        # five_year_avg_yield = avg DPS last 5 years / current price * 100
        current_year = datetime.now().year
        recent_dps = [yf_dps_by_year[y] for y in yf_dps_by_year
                      if y >= current_year - 5 and y < current_year
                      and yf_dps_by_year[y] is not None]
        if recent_dps and price is not None and price > 0:
            avg_dps = sum(recent_dps) / len(recent_dps)
            five_year_avg_yield = avg_dps / price * 100
        else:
            # Fallback: Yahoo fiveYearAvgDividendYield (already percentage)
            raw_5y = yf_info.get("fiveYearAvgDividendYield")
            five_year_avg_yield = raw_5y if raw_5y is not None else None

        dividend_rate = dps_current
        payout_ratio = yf_info.get("payoutRatio")

# new (data_adapter.py:598-635)
        # --- Dividend: DIY (Fiscal Year Attribution per SET methodology) ---
        # Find latest COMPLETE fiscal year (skip incomplete current FY)
        complete_fys = sorted([y for y, ok in yf_fy_complete.items() if ok])
        latest_complete_fy = complete_fys[-1] if complete_fys else None

        if latest_complete_fy is not None:
            dps_current = yf_dps_by_fy.get(latest_complete_fy)
        else:
            dps_current = None  # no complete FY data

        # dividend_yield = latest FY DPS / current price * 100
        if dps_current is not None and price is not None and price > 0:
            dy = dps_current / price * 100
        else:
            dy = tf_snap.get("dividend_yield")  # fallback thaifin

        # five_year_avg_yield = avg DPS of last 5 COMPLETE FYs / current price
        recent_complete_fys = complete_fys[-5:] if len(complete_fys) >= 5 else complete_fys
        recent_dps = [yf_dps_by_fy[y] for y in recent_complete_fys if yf_dps_by_fy.get(y) is not None]
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
```

## Phase 3: Verify against SET reality
- [x] สร้างไฟล์ verify script `projects/MaxMahon/scripts/_verify_dps_fix.py` ที่ทำ: (1) import `fetch_stock_data` จาก data_adapter, (2) เรียก fetch สำหรับ 4 หุ้น ['BBL.BK', 'METCO.BK', 'QH.BK', 'SAT.BK'], (3) print ตาราง `symbol, price, dividend_yield, dps, payout_ratio, five_year_avg_yield` แต่ละหุ้น, (4) write report markdown ที่ `projects/MaxMahon/docs/dps-fix-verification-2026-04-27.md` ระบุ: (a) ตาราง before (จาก git log/screener_2026-04-25.json) vs after, (b) ค่า SET Streaming reference ที่อาร์ทต้องเปิดดูเอง (placeholder รอกรอก), (c) PASS/FAIL ต่อหุ้น tolerance ±1%. จากนั้นรัน `cd projects/MaxMahon && py scripts/_verify_dps_fix.py`. — Scope: ห้ามแก้ data_adapter.py เพิ่มจาก Phase 2 (verify only). ห้าม commit screener output ใหม่. — Acceptance: ไฟล์ `docs/dps-fix-verification-2026-04-27.md` ถูกสร้าง + มีตาราง 4 หุ้น (yield ใหม่) + script รันแล้วไม่ raise exception. อาร์ทเปิด report เห็นตัวเลขก่อนกรอก SET Streaming reference manually

### Reference
```python
# scripts/_verify_dps_fix.py — verify script template
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from data_adapter import fetch_stock_data

SYMBOLS = ['BBL.BK', 'METCO.BK', 'QH.BK', 'SAT.BK']

print('Fetching 4 stocks for DPS fix verification...')
results = {}
for sym in SYMBOLS:
    try:
        data = fetch_stock_data(sym)
        results[sym] = {
            'price': data.get('price'),
            'yield': data.get('dividend_yield'),
            'dps': data.get('dps'),
            'payout': data.get('payout_ratio'),
            'yield_5y': data.get('five_year_avg_yield'),
        }
        print(f"{sym}: price={results[sym]['price']}, yield={results[sym]['yield']:.2f}%, dps={results[sym]['dps']}, payout={results[sym]['payout']}, yield_5y={results[sym]['yield_5y']:.2f}%")
    except Exception as e:
        print(f"{sym}: ERROR {e}")
        results[sym] = None

# Write report
report_path = ROOT / 'docs' / f"dps-fix-verification-{datetime.now().strftime('%Y-%m-%d')}.md"
report_path.parent.mkdir(exist_ok=True)
# ... build markdown table ...

# Verification target — SET DIY values to match
# BBL.BK at price ~158-176: SET DIY = ~6.8% (FY2025 DPS=12)
# METCO.BK at price ~264: เช็ค SET (อาจมี special dividend, expect 5-12%)
# QH.BK at price ~1.42: เช็ค SET (expect 7-10%)
# SAT.BK at price ~14.7: เช็ค SET (expect 8-12%)
# Tolerance: ±1.0% absolute
```
