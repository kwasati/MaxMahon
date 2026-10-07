---
project: MaxMahon
created: 2026-04-13
last_updated: 2026-04-23
status: done
---

# Pipeline Overhaul — Data Integrity + Scoring + Sort/Search

> แก้ pipeline ให้ข้อมูลถูกต้องแม่นยำ (DPS source of truth, FCF, scoring) + เพิ่ม sort/filter + custom search บน dashboard

## Phase 1: Data Integrity
- [x] data_adapter.py: DPS เป็น source of truth — ตรวจ thaifin API ว่ามี DPS โดยตรงไหม (ถ้ามีใช้เลย ถ้าไม่มีใช้ yfinance dividendRate), ลบการคำนวณ DPS จาก yield×price, yield% คำนวณจาก DPS/current_price×100, five_year_avg_yield คำนวณจาก avg DPS 5y / current_price × 100, ทำให้ทุก path (thaifin/yfinance) output หน่วยเดียวกัน
- [x] data_adapter.py: FCF = OCF - capex (ตรวจ thaifin ว่ามี capex แยกไหม ถ้าไม่มีใช้ yfinance capitalExpenditures เสริม ถ้าไม่มีทั้งคู่ fallback investing_activities แต่ flag DATA_WARNING), interest_coverage ใช้ operating_profit/interest_expense (ตรวจ thaifin fields, supplement จาก yfinance ถ้าไม่มี ถ้าไม่มีทั้งคู่ set None)
- [x] fetch_data.py: validate_metrics ROE threshold เปลี่ยน abs(roe) > 0.5 → abs(roe) > 1.5 (ไม่ลงโทษหุ้น ROE สูงจริง), dividend_growth_streak เปลี่ยน >= เป็น > strictly increasing (flat ไม่นับเป็น growth)
- [x] fetch_data.py: เพิ่ม dps_cagr ใน _build_aggregates — คำนวณ CAGR จาก DPS first/last year ที่มีข้อมูล, เพิ่ม DATA_DIR.mkdir(exist_ok=True) + REPORTS_DIR.mkdir(exist_ok=True) ก่อนเขียนไฟล์ทุกจุด

### Reference
```python
# เดิม — DPS คำนวณจาก yield × price (ไม่แม่น)
# data_adapter.py line 211-217:
dps = dividend_yield * close_price / 100  # WRONG: yield varies by price

# ใหม่ — DPS จาก thaifin/yfinance โดยตรง
dps = thaifin_dps or yfinance_dividend_rate  # actual declared amount
yield_pct = (dps / current_price) * 100  # calculated from DPS

# เดิม — FCF = OCF + investing (รวม M&A, asset sales)
fcf = ocf + investing_activities  # WRONG

# ใหม่ — FCF = OCF - capex
capex = abs(capital_expenditures)  # from yfinance supplement
fcf = ocf - capex  # correct free cash flow

# เดิม — ROE > 50% = DATA_WARNING
if abs(roe) > 0.5:  # too aggressive

# ใหม่
if abs(roe) > 1.5:  # only truly anomalous

# เดิม — flat counts as growth
if dps_by_year[years[i]] >= dps_by_year[years[i+1]]:  # >= includes flat

# ใหม่ — strictly increasing
if dps_by_year[years[i]] > dps_by_year[years[i+1]]:  # > only
```

## Phase 2: Scoring & Prompts
- [x] screen_stocks.py: interest_coverage scoring — ถ้ามีค่า (not None) ให้คิดคะแนน strength ปกติ (5 แต้ม), ถ้า None ให้ redistribute 5 แต้มไป D/E (7.5), FCF (7.5), OCF/NI (5) โดย scale proportional ไม่ใช่ให้ 0 แต้มฟรี
- [x] screen_stocks.py: CASH_COW signal ใช้ FCF จาก yearly_metrics ล่าสุดแทน data.get('free_cashflow'), แก้ valuation modifier ให้ apply ก่อน signal modifiers เพื่อ consistency
- [x] discover.py: แก้ prompt Quality Score description ให้ตรง spec — Dividend 35 (Yield 10+Streak 10+Payout 7+Growth 8), Profitability 25, Growth 20, Strength 20, ขยาย new_finds limit จาก 15 → 30
- [x] analyze.py + discover.py: เปลี่ยนจากอ่าน watchlist.json เป็น user_data.json — watchlist ใช้ userData['watchlist'], notes ใช้ userData['notes'], ลบ dependency กับ watchlist.json

### Reference
```python
# เดิม — interest_coverage None → 0 แต้ม
ic_score = 0 if ic is None  # loses 5 pts

# ใหม่ — redistribute
if ic is not None:
    strength_ic = min(5, ...)
else:
    # redistribute 5 pts: D/E gets +2.5, FCF gets +2.5
    de_score = min(7.5, ...)  # was max 5
    fcf_score = min(7.5, ...)  # was max 5

# เดิม discover.py prompt (WRONG weights):
# Profitability (30), Growth (25), Dividend (25), Strength (20)

# ใหม่ (correct weights):
# Dividend (35), Profitability (25), Growth (20), Strength (20)

# เดิม — อ่าน watchlist.json
watchlist = json.loads(WATCHLIST.read_text())
reasons = {s['symbol']: s['reason'] for s in watchlist['stocks']}

# ใหม่ — อ่าน user_data.json
user_data = json.loads(USER_DATA.read_text())
watched = user_data.get('watchlist', [])
notes = user_data.get('notes', {})
```

## Phase 3: Server Stability
- [x] server/app.py: /api/request endpoint — ย้าย sync blocking calls (fetch_multi_year) ไป run_in_executor เพื่อไม่ block event loop, ใช้ loop.run_in_executor(None, blocking_func) แทน asyncio.create_task กับ sync code
- [x] server/app.py: scheduled_run ให้เรียก _execute_sync(scripts) แทนเขียน pipeline logic ซ้ำ — single source of truth สำหรับ pipeline execution
- [x] server/app.py: request_status dict เพิ่ม timestamp per entry, เพิ่ม cleanup function ลบ entries > 24 ชม., เรียก cleanup ทุกครั้งที่มี request ใหม่เข้า

### Reference
```python
# เดิม — blocks event loop
async def _run():
    sys.path.insert(0, str(SCRIPTS_DIR))
    from fetch_data import fetch_multi_year  # sync blocking!
    data = fetch_multi_year(sym)  # blocks entire server

# ใหม่ — run in executor
async def _run():
    loop = asyncio.get_event_loop()
    for sym in symbols:
        data = await loop.run_in_executor(None, _fetch_one, sym)

def _fetch_one(sym):
    sys.path.insert(0, str(SCRIPTS_DIR))
    from fetch_data import fetch_multi_year
    return fetch_multi_year(sym)

# เดิม — scheduled_run reimplements pipeline
async def scheduled_run():
    scripts = [...]  # duplicated logic
    result = subprocess.run(...)  # reimplemented

# ใหม่ — delegates to _execute_sync
async def scheduled_run():
    scripts = _get_scripts_for_schedule(config)
    await asyncio.get_event_loop().run_in_executor(None, _execute_sync, scripts)
```

## Phase 4: Sort & Custom Search
- [x] Frontend (app.js + style.css): เพิ่ม sort dropdown ถัดจาก sub-tabs ใน stock page — ตัวเลือก: คะแนน (default), Yield สูงสุด, Avg 5y Yield, DPS, P/E ต่ำสุด, D/E ต่ำสุด — frontend sort ใน renderStockList() ก่อน render, เก็บ state.sortBy, ใช้ได้ทุก sub-tab (ผ่าน/ติดตาม/ใหม่/ไม่ผ่าน)
- [x] Backend (app.py): เพิ่ม /api/search endpoint — รับ JSON body { criteria: [{metric, operator, value, year?}], sort_by, limit }, scan data/ files หรือ screener results, filter ตามเงื่อนไข, sort, return results — metrics ที่รองรับ: dividend_yield, dps, avg_5y_yield, roe, net_margin, de_ratio, pe_ratio, quality_score, payout_ratio, fcf, market_cap, dividend_streak
- [x] Frontend (app.js + index.html): เพิ่ม search UI ในหน้าคำขอ — preset buttons: ปันผลดี (yield>4% + streak>5), เติบโตสม่ำเสมอ (ROE>15% + EPS CAGR>5%), ราคาถูก (valuation A/B) + custom form: dropdown metric + operator + value + optional ปี/ช่วง, กด search → เรียก /api/search → แสดงผลเป็น stock card list (กดดูรายละเอียดได้)

### Reference
```js
// Sort dropdown ใน renderStockList:
const sortFns = {
  score: (a,b) => (b.quality_score||0) - (a.quality_score||0),
  yield: (a,b) => (b.dividend_yield||0) - (a.dividend_yield||0),
  avg5y: (a,b) => (b.five_year_avg_yield||0) - (a.five_year_avg_yield||0),
  pe_asc: (a,b) => (a.pe_ratio||999) - (b.pe_ratio||999),
  de_asc: (a,b) => (a.de_ratio||999) - (b.de_ratio||999),
};
candidates.sort(sortFns[state.sortBy] || sortFns.score);

// Search API:
// POST /api/search
// Body: { criteria: [{metric:'dividend_yield', op:'>=', value:4}, {metric:'dividend_streak', op:'>=', value:5}], sort_by:'dividend_yield', limit:50 }
// Response: { results: [{symbol, name, sector, metrics...}], total: 42 }
```
