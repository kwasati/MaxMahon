---
project: MaxMahon
created: 2026-04-12
last_updated: 2026-04-12
status: done
---

# Max Mahon — Smart Valuation + UI Overhaul + DCA Simulator

> ปรับ Max ให้คัดหุ้นแม่นขึ้น (เพิ่มเกณฑ์ราคา ไม่ดูแค่คุณภาพ), UI ดูง่ายเป็นภาษาไทย (card grid + P/E + ปันผล 5 ปี), DCA simulator ใช้งานจริงได้ (smart defaults + ปรับเอง + เทียบทบต้น)

## Phase 1: Valuation Grade + Data Sanity
- [ ] เพิ่ม compute_valuation_grade() ใน screen_stocks.py — คำนวณ 5 ด้าน: PEG score (0-30 ใช้ EPS CAGR 4-5 ปี ไม่ใช่ earnings_growth TTM เพราะ 8/13 ตัว eg ติดลบใช้ไม่ได้), PE score (0-25), PB score (0-20), yield premium vs 5yr avg (0-15 + sanity check: ถ้า yield > 5yr_avg × 5 → ใช้ 5yr_avg แทน + flag DATA_WARNING), 52w position score (0-10) → รวม /100 → grade A-F (A≥80 B≥65 C≥50 D≥35 F<35)
- [ ] เพิ่ม valuation signals ใน assign_signals() — OVERVALUED (grade D/F + quality ≥50), FAIR_VALUE (grade B), UNDERVALUED (grade A + quality ≥65) | ลบ TURNAROUND signal (ซ้อนกับ valuation) | COMPOUNDER ไม่ให้ +10 bonus ถ้า valuation grade F (ของดีแต่แพงเกินไม่ควร boost) | เพิ่ม yield sanity check: yield > 5yr_avg × 5 → DATA_WARNING
- [ ] ส่ง valuation data ใน screener output — เพิ่ม valuation_score, valuation_grade, valuation_breakdown ใน candidate dict | normalize ใน server _normalize_stock() | re-run screen ดูว่า DELTA เป็น quality 82 (ลด 10 จาก COMPOUNDER blocked) + valuation F

### Reference
```python
# current: screen_stocks.py score_candidates()
def score_candidates(candidates, watchlist_symbols):
    for c in candidates:
        score, breakdown, reasons = compute_quality_score(c)
        signals = assign_signals(c, score)
        c['quality_score'] = score
        c['score'] = score
        c['breakdown'] = breakdown
        c['signals'] = signals
        c['reasons'] = reasons

# new: เพิ่ม valuation + sanity check
def compute_valuation_grade(c):
    """PEG(30) + PE(25) + PB(20) + YieldPremium(15) + 52wPos(10) = /100"""
    m = c.get('metrics', {})
    pe = m.get('pe') or c.get('pe_ratio')
    pb = m.get('pb_ratio') or c.get('pb_ratio')
    dy = m.get('dividend_yield') or c.get('dividend_yield')
    avg_dy = m.get('five_year_avg_yield') or c.get('five_year_avg_yield')
    # sanity check: yield anomaly
    if dy and avg_dy and avg_dy > 0 and dy > avg_dy * 5:
        dy = avg_dy  # ใช้ค่าเฉลี่ยแทน
    eps_cagr = c.get('aggregates', {}).get('eps_cagr')  # ใช้ CAGR ไม่ใช่ TTM growth
    # PEG = PE / (EPS CAGR % * 100)
    peg = pe / (eps_cagr * 100) if pe and eps_cagr and eps_cagr > 0 else 999
    # ... calculate sub-scores ...
    total = peg_score + pe_score + pb_score + yield_score + pos_score
    grade = 'A' if total >= 80 else 'B' if total >= 65 else 'C' if total >= 50 else 'D' if total >= 35 else 'F'
    return total, grade, {'peg': peg_score, 'pe': pe_score, 'pb': pb_score, 'yield_premium': yield_score, 'position_52w': pos_score}

def score_candidates(candidates, watchlist_symbols):
    for c in candidates:
        score, breakdown, reasons = compute_quality_score(c)
        val_score, val_grade, val_breakdown = compute_valuation_grade(c)
        signals = assign_signals(c, score, val_grade)
        # COMPOUNDER bonus blocked if valuation F
        if 'COMPOUNDER' in signals and val_grade == 'F':
            score -= 10  # undo bonus
        c['quality_score'] = score
        c['valuation_score'] = val_score
        c['valuation_grade'] = val_grade
        c['valuation_breakdown'] = val_breakdown
```

## Phase 2: UI Overhaul + ภาษาไทย
- [ ] เปลี่ยน stock list จาก row → card grid — CSS: grid-template-columns repeat(3, 1fr) responsive 900px→2col 480px→1col | card content: symbol+sector top, quality score วงกลม + valuation grade badge (A-F สี), P/E ratio, ราคา, yield ล่าสุด + 5yr avg, tags ล่าง | เอา 'Buffett + เซียนฮง v2' เปลี่ยนเป็น 'Buffett + เซียนฮง' (เอา v2 ออก)
- [ ] เปลี่ยนภาษาไทยทั้ง dashboard — tags: COMPOUNDER→ทบต้นเก่ง, DIVIDEND_KING→ปันผลเด่น, CASH_COW→เงินสดเยอะ, CONTRARIAN→ราคาลงน่าสน, OVERVALUED→ราคาสูง, FAIR_VALUE→ราคาเหมาะ, UNDERVALUED→ราคาน่าสน, YIELD_TRAP→ระวังปันผลหลอก, DATA_WARNING→ข้อมูลผิดปกติ | ปุ่ม pipeline: ลดเหลือ 2 ปุ่มหลัก 'อัพเดทข้อมูล' (fetch+analyze) + 'คัดกรองใหม่' (full pipeline) ซ่อน advanced ไว้ | tabs: ผ่านเกณฑ์, ติดตาม, ค้นพบใหม่, ไม่ผ่าน, ขอวิเคราะห์, DCA

### Reference
```javascript
// current: renderStockList() — single row
el.innerHTML = candidates.map(c => {
  return `<div class="stock-row" data-symbol="${sym}">
    <div class="stock-identity"><h3>${sym}</h3><div class="sector">${sector}</div></div>
    <div class="stock-score"><div class="score-circle ${scoreClass(score)}">${score}</div></div>
    <div class="stock-tags">${signals.map(...)}</div>
    <div class="stock-price"><div class="current">${price}</div><div class="yield">Yield ${yld}%</div></div>
  </div>`;
});

// new: card grid + P/E + valuation + 5yr yield
const tagMapTH = {
  'COMPOUNDER': 'ทบต้นเก่ง', 'DIVIDEND_KING': 'ปันผลเด่น',
  'CASH_COW': 'เงินสดเยอะ', 'CONTRARIAN': 'ราคาลงน่าสน',
  'OVERVALUED': 'ราคาสูง', 'FAIR_VALUE': 'ราคาเหมาะ',
  'UNDERVALUED': 'ราคาน่าสน', 'YIELD_TRAP': 'ระวังปันผลหลอก',
  'DATA_WARNING': 'ข้อมูลผิดปกติ'
};
function tagLabelTH(tag) { return tagMapTH[tag] || tag; }

el.innerHTML = candidates.map(c => {
  const valGrade = c.valuation_grade || '-';
  const pe = c.pe_ratio || c.metrics?.pe;
  const fiveYrYld = c.five_year_avg_yield || c.metrics?.five_year_avg_yield;
  return `<div class="stock-card" data-symbol="${sym}">
    <div class="card-header">
      <div><h3>${sym}</h3><span class="sector">${sector}</span></div>
      <div class="card-scores">
        <div class="score-circle ${scoreClass(score)}">${score}</div>
        <div class="val-badge ${valGradeClass(valGrade)}">${valGrade}</div>
      </div>
    </div>
    <div class="card-body">
      <div class="card-price">฿${price} <span class="pe">P/E ${safe(pe,'1d')}</span></div>
      <div class="card-yields">
        <span>ปันผล ${yld}%</span>
        <span class="dim">5ปี ${safe(fiveYrYld,'1d')}%</span>
      </div>
    </div>
    <div class="card-tags">${signals.map(s => `<span class="tag ${tagClass(s)}">${tagLabelTH(s)}</span>`).join('')}</div>
  </div>`;
}).join('');

// CSS
.stock-list { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
@media (max-width: 900px) { .stock-list { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .stock-list { grid-template-columns: 1fr; } }

// pipeline: 2 main + advanced
<button class="pipe-btn" data-action="weekly" title="ดึงข้อมูลล่าสุด + วิเคราะห์">อัพเดทข้อมูล</button>
<button class="pipe-btn primary" data-action="discovery" title="ดึงข้อมูล + คัดกรอง SET 99 ตัว + ค้นหาตัวใหม่">คัดกรองใหม่</button>
```

## Phase 3: DCA Simulator — Smart + Comparison
- [ ] Backend: smart defaults + custom params + เทียบ reinvest — params ใหม่: backtest_years (default 10), price_growth (empty=auto), div_growth (empty=auto) | smart defaults: price_growth = median(eps_cagr, revenue_cagr) cap 20% floor 3% + source explanation | div_growth = actual DPS CAGR จาก dividend_history 5 ปี cap 15% floor 0% | **เปลี่ยนจาก toggle เป็นคำนวณทั้ง 2 แบบเสมอ** (reinvest + no-reinvest) ส่งคู่กันใน response ให้ frontend เทียบ | return smart_defaults พร้อม source text
- [ ] Frontend: DCA form ใหม่ + แสดงเทียบ reinvest vs ไม่ทบต้น — เพิ่ม inputs: ย้อนหลังกี่ปี, ราคาโต %/ปี, ปันผลโต %/ปี (placeholder=auto จาก smart defaults) | เมื่อเลือกหุ้น → fetch smart defaults แสดง placeholder + ที่มา | ลบ reinvest toggle → แสดงผลทั้ง 2 แบบเทียบกันเสมอ: summary cards แถวบน 'ไม่ทบต้น: 1.2M → 3.5M' แถวล่าง 'ทบต้น: 1.2M → 5.2M' ให้เห็นพลัง compound ทันที

### Reference
```python
# current: hardcoded growth
price_growth_rate = stock_agg.get('eps_cagr') or stock_agg.get('revenue_cagr') or 0.08
div_growth_rate = 0.05

# new: smart defaults + always compute both
import statistics

def compute_smart_defaults(stock_agg, dividend_history):
    rates = [v for v in [stock_agg.get('eps_cagr'), stock_agg.get('revenue_cagr')] if v and v > 0]
    price_gr = statistics.median(rates) if rates else 0.08
    price_gr = max(0.03, min(0.20, price_gr))
    price_src = f"median(EPS CAGR {stock_agg.get('eps_cagr',0)*100:.1f}%, Revenue CAGR {stock_agg.get('revenue_cagr',0)*100:.1f}%)"

    years = sorted(k for k in dividend_history.keys() if dividend_history[k] > 0)
    div_gr = 0.03
    div_src = 'default 3%'
    if len(years) >= 3:
        first_dps, last_dps = dividend_history[years[-5]] if len(years)>=5 else dividend_history[years[0]], dividend_history[years[-1]]
        if first_dps > 0 and last_dps > 0:
            n = min(5, len(years) - 1)
            div_gr = (last_dps / first_dps) ** (1/n) - 1
            div_src = f"DPS CAGR {n}yr ({first_dps:.2f}→{last_dps:.2f})"
    div_gr = max(0.0, min(0.15, div_gr))
    return {'price_growth': price_gr, 'price_growth_source': price_src,
            'div_growth': div_gr, 'div_growth_source': div_src}

@app.get('/api/dca/{symbol}')
async def dca_simulate(symbol, days='1,15', amount=5000,
                       backtest_years: int = 10,
                       projection_years: int = 10,
                       price_growth: Optional[float] = None,
                       div_growth: Optional[float] = None):
    # Always compute both reinvest + no-reinvest
    defaults = compute_smart_defaults(stock_agg, div_hist)
    # ... run backtest twice (reinvest=True, reinvest=False)
    return {
        'smart_defaults': defaults,
        'backtest_reinvest': {...},
        'backtest_no_reinvest': {...},
        'projection_reinvest': {...},
        'projection_no_reinvest': {...},
    }
```
