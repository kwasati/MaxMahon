---
project: MaxMahon
created: 2026-04-12
last_updated: 2026-04-23
status: done
---

# Max Mahon v2 — Buffett + เซียนฮง Quality Analysis

> อัพเกรดจาก single-year snapshot เป็น multi-year quality analysis สไตล์ Buffett + เซียนฮง — ดึงข้อมูล 5 ปี, scoring 100 คะแนน 4 ด้าน, sanity check, เหมาะ DCA 10-20 ปี + ปันผลดี

## Phase 1: Multi-Year Data Pipeline
- [x] Rewrite fetch_data.py — ดึง income_stmt/balance_sheet/cashflow 4-5 ปี + dividends 10+ ปี จาก yfinance, คำนวณ yearly metrics (ROE, margins, D/E, interest coverage, OCF/NI ratio, capital intensity, FCF), aggregates (revenue CAGR, EPS CAGR, avg ROE, avg margins, dividend growth streak), sanity check flags (yield >20%, growth >300%, payout >150%, ROE >50% → DATA_WARNING)
- [x] ทดสอบ fetch ด้วย watchlist ปัจจุบัน 12 ตัว — ตรวจว่าข้อมูลครบถ้วน, handle NaN/missing data ได้, ธนาคาร (SCB/TISCO) ไม่พัง (ไม่มี Gross Profit), sector-aware D/E, dividend grouping by year ถูกต้อง

### Reference
```python
# fetch_data.py v2 — key structure
def fetch_multi_year(symbol: str) -> dict:
    tk = yf.Ticker(symbol)
    
    # 1. Raw financial statements (4-5 years)
    inc = tk.income_stmt  # Revenue, Gross Profit, Net Income, EPS, EBITDA, Interest Expense
    bs = tk.balance_sheet  # Total Debt, Stockholders Equity, Current Assets/Liabilities
    cf = tk.cashflow       # OCF, FCF, CapEx, Dividends Paid
    
    # 2. Compute yearly metrics
    yearly = []
    for year_col in inc.columns:
        year = str(year_col.date().year)
        revenue = safe_get(inc, 'Total Revenue', year_col)
        net_income = safe_get(inc, 'Net Income', year_col)
        equity = safe_get(bs, 'Stockholders Equity', year_col)
        # ROE, margins, D/E, interest coverage, etc.
        yearly.append({year: computed_metrics})
    
    # 3. Dividends — full history grouped by year
    divs = tk.dividends
    dps_by_year = divs.groupby(divs.index.year).sum()
    
    # 4. Aggregates
    revenue_cagr = compute_cagr(revenues)
    eps_cagr = compute_cagr(eps_list)
    div_streak = count_consecutive_years_no_cut(dps_by_year)
    
    # 5. Sanity check
    warnings = validate_metrics(info, yearly)
    
    return {**info_snapshot, 'yearly': yearly, 'dividends': dps_history,
            'aggregates': aggregates, 'warnings': warnings}

def validate_metrics(info, yearly) -> list[str]:
    warnings = []
    if dy and dy > 20: warnings.append('yield >20% — ตรวจสอบข้อมูล')
    if eg and abs(eg) > 3: warnings.append('earnings growth >300% — อาจเป็น base effect')
    if payout and payout > 1.5: warnings.append('payout >150% — จ่ายเกินกำไร')
    return warnings
```

## Phase 2: Quality Scoring Engine
- [x] Rewrite screen_stocks.py — (A) Hard Filters: ROE avg ≥15% 4 ปี (ไม่มีปีต่ำกว่า 12%), Net Margin avg ≥10%, D/E ≤1.5 (non-fin) / ≤10 (fin), EPS บวก ≥3/4 ปี, FCF บวก ≥3/4 ปี, Market Cap ≥5B (B) Quality Score 100 คะแนน: Profitability 30 (ROE consistency + gross margin + net margin trend), Growth 25 (revenue CAGR + EPS CAGR + revenue consistency), Dividend 25 (yield + payout sustainability + dividend streak 10yr), Strength 20 (D/E level + interest coverage + FCF consistency + OCF/NI ratio) (C) Signal Tags: COMPOUNDER (ROE ≥20% ทุกปี + rev CAGR ≥10% + payout <60%), CASH_COW (FCF yield >8% + payout <70% + D/E <0.5), DATA_WARNING (sanity flags), ปรับ CONTRARIAN/DIVIDEND_KING/YIELD_TRAP ให้ใช้ multi-year data
- [x] ทดสอบ screening SET universe 99 ตัว — ยืนยันว่า CHG ถูก filter หรือ score ต่ำ (revenue ลง 3 ปี), MTC ถูก flag DATA_WARNING (yield 95%), ตัว quality สูง (CPALL, ADVANC, BDMS) ได้ score สูง

### Reference
```python
# screen_stocks.py v2 — scoring framework

HARD_FILTERS = {
    'min_roe_avg': 0.15,      # Buffett: ROE ≥15% sustained
    'min_roe_floor': 0.12,    # ไม่มีปีต่ำกว่า 12%
    'min_net_margin': 0.10,   # Net Margin ≥10% avg
    'max_de_non_fin': 1.5,    # เซียนฮง: D/E ≤1.0 (เราผ่อนเป็น 1.5)
    'max_de_financial': 10,   # ธนาคาร/ประกัน
    'min_eps_positive_years': 3,  # จาก 4 ปี
    'min_fcf_positive_years': 3,
    'min_market_cap': 5_000_000_000,
}

def quality_score(data: dict) -> dict:
    score = 0
    breakdown = {}
    
    # A. Profitability & Returns (30 pts)
    # ROE consistency: 15 pts (ปีละ ~4 pts ถ้า ≥15%)
    # Gross Margin level: 10 pts (≥40%=10, ≥30%=7, ≥20%=4)
    # Net Margin trend: 5 pts (เพิ่มทุกปี=5, mixed=2)
    
    # B. Growth Consistency (25 pts)
    # Revenue CAGR: 10 pts (≥15%=10, ≥10%=7, ≥5%=4)
    # EPS CAGR: 10 pts (same scale)
    # Revenue positive years: 5 pts (4/4=5, 3/4=3)
    
    # C. Dividend Quality (25 pts)
    # Yield: 8 pts (≥6%=8, ≥4%=6, ≥3%=4)
    # Payout 30-70%: 7 pts (sweet spot=7, 70-85%=4)
    # Dividend streak no-cut: 10 pts (≥10yr=10, ≥7yr=7, ≥5yr=5)
    
    # D. Financial Strength (20 pts)
    # D/E level: 5 pts (<0.5=5, <1.0=3)
    # Interest Coverage: 5 pts (>10x=5, >5x=3)
    # FCF consistency: 5 pts (4/4=5, 3/4=3)
    # OCF/NI ratio 0.8-1.2: 5 pts (clean accounting)
    
    return {'score': score, 'breakdown': breakdown,
            'signals': signals, 'reasons': reasons}
```

## Phase 3: Analysis & Discovery Upgrade
- [x] อัพเดท analyze.py — prompt ใหม่ส่ง multi-year data (revenue/NI/EPS/ROE 4 ปี + DPS history 10 ปี + quality score + warnings) ให้ Claude วิเคราะห์ 6 ด้าน: Business Quality (moat, competitive position), Financial Health (debt, cash flow, interest coverage), Growth Consistency (trend ไม่ใช่แค่ปีเดียว), Dividend Sustainability (จ่ายจาก cash จริงหรือหนี้ track record กี่ปี), Valuation (P/E vs quality, เทียบ historical), DCA Suitability (เหมาะสะสมระยะยาว 10-20 ปีไหม)
- [x] อัพเดท discover.py — prompt quality-first ส่ง quality score + multi-year data, สไตล์ Buffett+เซียนฮง, เน้นหาตัว COMPOUNDER/CASH_COW สำหรับ DCA 10-20 ปี, flag DATA_WARNING ชัดเจน, เปรียบเทียบกับ watchlist ปัจจุบัน
- [x] อัพเดท CLAUDE.md — document: architecture ใหม่ (multi-year pipeline), scoring criteria (hard filters + quality score 100), analysis framework (6 ด้าน), signal tags (เก่า+ใหม่), data sources (yfinance now + SETSMART planned), references (Buffett/เซียนฮง criteria)

### Reference
```python
# analyze.py v2 — prompt structure (key sections)
prompt = f"""
คุณคือ Max Mahon — นักวิเคราะห์หุ้นไทย
สไตล์: Warren Buffett (คุณภาพธุรกิจ + moat) + เซียนฮง สถาพร (ปันผล + growth)
เป้าหมาย: คัดหุ้นสำหรับ DCA ระยะยาว 10-20 ปี ปันผลดี

## ข้อมูลหุ้น {symbol}
- Quality Score: {score}/100 ({breakdown})
- Signals: {signals}
- Warnings: {warnings}

### Yearly Financials (4 ปี)
| ปี | Revenue | Net Income | EPS | ROE | Net Margin | D/E |
{yearly_table}

### Dividend History (10 ปี)
| ปี | DPS | Yield at year-end |
{dividend_table}

### Aggregates
- Revenue CAGR: {rev_cagr}% | EPS CAGR: {eps_cagr}%
- Avg ROE: {avg_roe}% | Avg Net Margin: {avg_nm}%
- Dividend Streak (ไม่เคยตัด): {streak} ปี
- Interest Coverage: {int_cov}x | OCF/NI: {ocf_ni}x

## วิเคราะห์ 6 ด้าน:
1. Business Quality — ธุรกิจแข็งไหม มี moat ไหม
2. Financial Health — หนี้ กระแสเงินสด ความแข็งแกร่ง
3. Growth Consistency — โตสม่ำเสมอหรือแค่ปีเดียวกระโดด
4. Dividend Sustainability — ปันผลยั่งยืน จ่ายจาก cash จริงไหม
5. Valuation — แพงหรือถูกเมื่อเทียบคุณภาพ
6. DCA Suitability — เหมาะ DCA 10-20 ปีไหม ทำไม
"""
```
