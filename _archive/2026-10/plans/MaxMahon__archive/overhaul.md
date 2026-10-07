---
project: MaxMahon
created: 2026-04-13
last_updated: 2026-04-23
status: done
---

# Max Mahon Overhaul — data + user control + score + UI

> ปรับ Max จาก 'Max ตัดสินทุกอย่าง' เป็น 'Max วิเคราะห์ user ตัดสินใจ' — เปลี่ยน data source เป็น thaifin, เพิ่ม user control เต็มรูปแบบ, ปรับ score เน้นปันผล, UI mobile-first + charts

## Phase 1: Data Foundation — thaifin + request fix
- [x] ติดตั้ง thaifin + test — ดึง PTT, SCB, ADVANC ดูว่าได้ revenue, net profit, EPS, dividend, ROE ย้อน 10 ปีจริงไหม ถ้าไม่ได้ต้องหาทางอื่น
- [x] สร้าง data adapter (scripts/data_adapter.py) — thaifin primary + yfinance fallback (price, 52w, forward PE, market cap) + normalize symbol auto (LH → thaifin:LH + yfinance:LH.BK)
- [x] แก้ fetch_data.py ให้ใช้ data adapter แทน yfinance ตรง — map ข้อมูลเข้า yearly_metrics schema เดิมให้ backward compatible
- [x] แก้ request system end-to-end — backend: auto-append .BK สำหรับ yfinance, handle errors return ข้อมูลที่ใช้ได้ | frontend: loading state + error message + ไม่ต้องใส่ .BK
- [x] ขยาย universe — ดึง list หุ้นจาก thaifin หรือ SET100+SET50+MAI แทน static 99 ตัว เก็บเป็น set_universe.json ใหม่

### Reference
```python
# current: fetch_data.py ใช้ yfinance ตรง
import yfinance as yf
def fetch_multi_year(symbol: str) -> dict:
    tk = yf.Ticker(symbol)
    info = tk.info or {}
    inc = tk.income_stmt
    ...

# new: data_adapter.py — thaifin primary + yfinance fallback
from thaifin import Stock
import yfinance as yf

def normalize_symbol(raw: str) -> tuple[str, str]:
    clean = raw.upper().replace('.BK', '')
    return clean, f'{clean}.BK'

def fetch_fundamentals(symbol: str) -> dict:
    tf_sym, yf_sym = normalize_symbol(symbol)
    stock = Stock(tf_sym)  # thaifin: financials 10+ years
    tk = yf.Ticker(yf_sym)  # yfinance: price, 52w, forward PE
    ...
```

## Phase 2: User Control Layer
- [x] สร้าง user_data.json schema + migration script — watchlist, blacklist, notes, custom_lists + migrate จาก watchlist.json เดิม (symbol → watchlist, reason → notes)
- [x] เพิ่ม API endpoints ใน app.py — GET /api/user, PUT /api/user/watchlist {add/remove}, PUT /api/user/blacklist {add/remove}, PUT /api/user/notes/{symbol} {note}, PUT+DELETE /api/user/lists/{name}
- [x] แก้ screen_stocks.py เก็บหุ้นที่ไม่ผ่าน hard filter ไว้ใน output — filtered_out_stocks: [{symbol, name, sector, reasons, basic_metrics}]
- [x] แก้ pipeline (fetch_data.py main, run_weekly.py) ใช้ user_data.json watchlist แทน watchlist.json เดิม + filter blacklist ออกจากผลลัพธ์

### Reference
```json
// user_data.json schema
{
  "watchlist": ["PTT.BK", "ADVANC.BK", "SCB.BK"],
  "blacklist": ["BANPU.BK"],
  "notes": {
    "PTT.BK": "รอราคาลงอีก",
    "ADVANC.BK": "ปันผลดีมาก สะสมต่อ"
  },
  "custom_lists": {
    "เก็บแล้ว": ["PTT.BK", "SCB.BK"],
    "จับตา": ["CPALL.BK"]
  },
  "updated_at": "2026-04-13T10:00:00"
}
```

```python
# current: หุ้นไม่ผ่านหายไปเลย
if not passed:
    filtered_out += 1
    continue

# new: เก็บไว้ใน output
if not passed:
    filtered_stocks.append({
        "symbol": sym, "name": data.get("name"),
        "sector": data.get("sector"),
        "reasons": filter_reasons,
        "basic_metrics": {"price": data.get("price"), "dividend_yield": data.get("dividend_yield"), "roe": data.get("roe")}
    })
```

## Phase 3: Score Rebalance — Dividend-First
- [x] ปรับน้ำหนักคะแนน — Dividend 35 (yield 10 + streak 10 + payout 7 + div_growth 8), Profitability 25 (ROE 12 + margins 8 + trend 5), Growth 20 (rev CAGR 8 + EPS CAGR 8 + consistency 4), Strength 20 (เท่าเดิม)
- [x] เพิ่ม Dividend Growth scoring ใน dividend_score() — ใช้ agg.dividend_growth_streak: >=5yr=8pts, >=3yr=5pts, >=1yr=3pts
- [x] เพิ่ม Valuation modifier ใน quality_score() — คำนวณ valuation_grade ก่อน แล้วปรับ total: Grade A:+5, B:0, C:-5, D:-10, F:-20
- [x] ปรับ signal adjustments — YIELD_TRAP:-20, DATA_WARNING:-15, COMPOUNDER:+5, CONTRARIAN:+5 + cap total ที่ 100 เสมอ
- [x] Soft zone สำหรับ hard filter — ROE avg 13-14.9% ผ่านแต่ -5 pts + tag NEAR_MISS_ROE, Net Margin 8-9.9% เช่นกัน

### Reference
```python
# current weights
# Profitability 30 + Growth 25 + Dividend 25 + Strength 20 = 100
# signals: COMPOUNDER +10, CONTRARIAN +10, YIELD_TRAP -15
# no cap! can exceed 100

# new: Dividend-First + capped
def quality_score(data, sector_medians):
    p_score, _ = profitability_score(data)   # max 25
    g_score, _ = growth_score(data)          # max 20
    d_score, _ = dividend_score(data)        # max 35
    s_score, _ = strength_score(data)        # max 20
    total = p_score + g_score + d_score + s_score
    # signals
    if 'YIELD_TRAP' in signals: total -= 20
    if 'DATA_WARNING' in signals: total -= 15
    if 'COMPOUNDER' in signals: total += 5
    if 'CONTRARIAN' in signals: total += 5
    # valuation modifier
    val = valuation_grade(data, sector_medians)
    total += {'A': 5, 'B': 0, 'C': -5, 'D': -10, 'F': -20}[val['grade']]
    return {'score': max(0, min(100, total))}

# new dividend_score (35 max)
def dividend_score(data):
    # yield (10) + streak (10) + payout (7) + div_growth (8 NEW)
    div_growth = agg.get('dividend_growth_streak', 0)
    if div_growth >= 5: score += 8
    elif div_growth >= 3: score += 5
    elif div_growth >= 1: score += 3
```

## Phase 4: UI Overhaul — Mobile-First + Charts + User Control
- [x] Mobile-first responsive layout — CSS Grid: mobile (<768px) single col + bottom tab bar 44px, tablet (768-1024) 2 col, desktop (>1024) sidebar 340px + main detail | stock card ปรับ min-width
- [x] User control UI — ปุ่ม +watchlist/-remove บนทุก stock card, ปุ่ม hide/blacklist, inline notes editor, custom list dropdown + สร้าง list ใหม่ | เรียก Phase 2 API
- [x] แก้ request UI + tab ไม่ผ่าน — input แค่พิมพ์ชื่อหุ้น ไม่ต้อง .BK + loading spinner + error toast | tab ไม่ผ่าน แสดง card เหตุผล + basic metrics ทุกตัว
- [x] Charts ใน detail panel — Chart.js CDN: dividend per share bar chart 10yr, ROE line chart 5yr, revenue vs NI dual bar | responsive ย่อบน mobile
- [x] Detail panel mobile-friendly — score circle SVG, signal badges สี, Buffett checklist icons, yearly table horizontal scroll, valuation grade badge, near-miss warning

### Reference
```css
/* current: fixed grid */
.stock-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); }

/* new: mobile-first */
@media (max-width: 767px) {
  .stock-grid { grid-template-columns: 1fr; }
  .detail-panel { position: fixed; inset: 0; z-index: 100; overflow-y: auto; }
  .tab-bar { position: fixed; bottom: 0; display: flex; }
  .tab-bar button { min-height: 44px; flex: 1; }
}
@media (min-width: 1024px) {
  .app-layout { display: grid; grid-template-columns: 340px 1fr; }
}
```

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

```javascript
// User control
async function toggleWatchlist(symbol, add) {
  await fetch('/api/user/watchlist', {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(add ? {add: [symbol]} : {remove: [symbol]})
  });
  await refreshData();
}
```
