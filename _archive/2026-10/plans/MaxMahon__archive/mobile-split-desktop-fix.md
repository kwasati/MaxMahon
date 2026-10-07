---
project: MaxMahon
created: 2026-04-19
last_updated: 2026-04-19
status: done
---

# Mobile route + touch detect + fix desktop slide

> Editorial redesign ทำให้ desktop slide พัง (CSS เก่ายังไม่ลบ ชนกับของใหม่) + mobile.html เป็น mockup ไม่ได้ serve จริง ต้อง fix desktop slide, route /mobile, touch detect, แล้ว wire mobile ให้ใช้ API จริงครบทุกหน้า

## Phase 1: Fix desktop slide — restore split-mode layout
- [x] ลบ CSS เก่าใน web/style.css ~line 610-689 ที่ชน: `.stock-layout{display:flex}`, `.stock-layout.grid-mode .stock-list/.detail-panel`, `.stock-layout.split-mode .stock-list/.detail-panel`, `.grid-mode .stock-grid`, `.split-mode .stock-grid`
- [x] เพิ่ม slide rules ใหม่ใน editorial section (~line 298 ต่อจาก `.stock-layout{display:block}`): เมื่อมี `.split-mode` → flex row, `.watch-wrap` fixed 420px sticky left, `.detail-panel` flex-1 right, ซ่อนคอลัมน์ 5-10 (5Y Yield, P/E, D/E, ROE, Streak, Price) ในตารางฝั่ง split
- [x] Override `.detail-panel#detail.open` ใน split-mode → เปลี่ยนเป็น block (ไม่ใช่ 2-col grid) เพราะ pane แคบแล้ว ให้ section ต่างๆ stack กัน + เพิ่ม transition smooth
- [x] ตรวจ JS (`app.js` closeDetail ~line 63, loadDetail ~line 585) ยังคงใช้ `.split-mode`/`.grid-mode` + `.open` ถูก — ไม่ต้องแก้ JS ถ้า class names ยังตรงกับ CSS ใหม่

### Reference
```css
/* REMOVE — style.css line ~610-689 (OLD conflict) */
.stock-layout {
  display: flex;
  gap: 0;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: calc(100vh - 280px);
}
.stock-layout.grid-mode .stock-list { width: 100%; flex-shrink: 0; }
.stock-layout.grid-mode .detail-panel { width: 0; opacity: 0; overflow: hidden; padding: 0; border: none; }
.stock-layout.split-mode .stock-list { width: 380px; min-width: 380px; flex-shrink: 0; overflow-y: auto; height: calc(100vh - 200px); position: sticky; top: 12px; border-right: 1px solid var(--border); padding-right: 12px; }
.stock-layout.split-mode .detail-panel { flex: 1; opacity: 1; padding: 20px 24px 24px 24px; min-width: 0; }
.stock-grid { display: grid; gap: 10px; transition: grid-template-columns 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
.grid-mode .stock-grid { grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); }
.split-mode .stock-grid { grid-template-columns: 1fr; }

/* ADD — near editorial .stock-layout (~line 298) */
.stock-layout {
  max-width: 1400px; margin: 0 auto;
  padding: 0 2.5rem 3rem;
  display: block;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}
.stock-layout.split-mode {
  display: flex;
  gap: 2.5rem;
  align-items: flex-start;
}
.stock-layout.split-mode .watch-wrap {
  flex: 0 0 420px;
  position: sticky;
  top: 12px;
  max-height: calc(100vh - 120px);
  overflow-y: auto;
  border-right: 1px solid var(--rule);
  padding-right: 1.5rem;
}
/* shrink table: show Stock | Signal | Score | Yield only */
.stock-layout.split-mode table.watch thead th:nth-child(n+5),
.stock-layout.split-mode table.watch tbody td:nth-child(n+5) { display: none; }
/* detail panel override — no internal 2-col grid in split */
.stock-layout.split-mode .detail-panel#detail.open {
  display: block;
  flex: 1;
  min-width: 0;
  margin-top: 0;
  padding-top: 0;
  border-top: none;
}

/* responsive: fall back to stacked below 1024 */
@media (max-width: 1024px) {
  .stock-layout.split-mode { display: block; }
  .stock-layout.split-mode .watch-wrap { flex: none; position: static; max-height: none; border-right: none; padding-right: 0; }
  .stock-layout.split-mode table.watch thead th:nth-child(n+5),
  .stock-layout.split-mode table.watch tbody td:nth-child(n+5) { display: table-cell; }
}
```

## Phase 2: Server /mobile route + touch detect redirect
- [x] เพิ่ม `@app.get("/mobile", response_class=HTMLResponse)` ใน `server/app.py` — อ่าน `web/mobile.html` serve พร้อมกัน (mobile.html มี inline CSS/JS ไม่ต้อง cache-bust)
- [x] เพิ่ม touch detection script ใน `<head>` ของ `web/index.html` — ถ้าเป็น touch + viewport < 768 + ไม่มี `?desktop=1` → `location.replace('/mobile')` (script ต้องรันก่อน body render เพื่อไม่ flash UI)
- [x] เพิ่ม "ดูบน Desktop" link ด้านบน mobile.html (ในส่วน header หรือ bottom nav) → navigate ไป `/?desktop=1`
- [x] Test: desktop Chrome → /, mobile Chrome emulator → / redirect to /mobile, กด Desktop link → /?desktop=1 อยู่ที่ desktop

### Reference
```python
# server/app.py — ADD route before static mount (line ~1555)
@app.get("/mobile", response_class=HTMLResponse)
async def serve_mobile():
    mobile_path = WEB_DIR / "mobile.html"
    html = mobile_path.read_text(encoding="utf-8")
    return HTMLResponse(html)

# CURRENT at line 1555 — existing /, keep as-is
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = WEB_DIR / "index.html"
    html = index_path.read_text(encoding="utf-8")
    css_mtime = int((WEB_DIR / "style.css").stat().st_mtime)
    js_mtime = int((WEB_DIR / "app.js").stat().st_mtime)
    html = html.replace("style.css?v=__CB__", f"style.css?v={css_mtime}")
    html = html.replace("app.js?v=__CB__", f"app.js?v={js_mtime}")
    return HTMLResponse(html)
```

```html
<!-- web/index.html — ADD inline before </head> or at very top of <body> -->
<script>
(function(){
  var url = new URL(window.location.href);
  if (url.searchParams.has('desktop')) return;  // escape hatch
  var isTouch = ('ontouchstart' in window) || navigator.maxTouchPoints > 0;
  var isNarrow = window.innerWidth < 768;
  if (isTouch && isNarrow) {
    window.location.replace('/mobile');
  }
})();
</script>
```

```html
<!-- web/mobile.html — ADD link to desktop (e.g. in top nav area near line ~660) -->
<a href="/?desktop=1" class="desktop-link">ดูบน Desktop</a>
<style>
.desktop-link { position: absolute; top: 12px; right: 12px; font-size: 0.72rem; color: var(--text3); text-decoration: none; padding: 4px 8px; }
.desktop-link:active { color: var(--accent); }
</style>
```

## Phase 3: Mobile — wire stock list + detail with real API
- [x] แทนที่ mock arrays `STOCKS`/`FILTERED` ใน mobile.html (~line 875-894) — init async: `fetch('/api/watchlist')` + `fetch('/api/screener')` → normalize เป็น card shape (sym, sector, score, yield, avg5y, grade, tags) — copy pattern จาก `app.js` renderStockList + ใช้ TAG_TH mapping จาก app.js
- [x] แยก list ตาม `currentFilter`: passed = screener.candidates score>=50, watchlist = watchlist.stocks, new = screener discoveries, filtered = screener.filtered_out_stocks (~40+ รายการ)
- [x] Rewire `openDetail(sym)` (~line 964) → `fetch('/api/stock/' + sym)` → ดึงข้อมูลจริง (price, pe, dividend_yield, payout_ratio, debt_to_equity, roe) แทน hardcoded ใน quick-metrics grid
- [x] Render Buffett checklist จาก breakdown/aggregates จริง (ROE>=15, GM>=30, D/E<1.0, FCF+, streak>=5, EPS trend) — map agg.avg_roe, agg.avg_gross_margin, m.de, agg.fcf_positive_years, agg.dividend_streak, agg.eps_cagr > 0
- [x] Render yearly table จาก `stock.yearly_metrics` (array ปี revenue/net_income/roe/de/dps) แทน hardcoded 2020-2025

### Reference
```javascript
// mobile.html — REPLACE mock data section (~line 873+)
const API = window.location.origin;
let state = { watchlist: null, screener: null, userData: null };
let currentFilter = 'passed';

async function init() {
  try {
    const [wl, sc] = await Promise.all([
      fetch(API + '/api/watchlist').then(r => r.ok ? r.json() : null),
      fetch(API + '/api/screener').then(r => r.ok ? r.json() : null)
    ]);
    state.watchlist = wl;
    state.screener = sc;
    renderCards();
  } catch (e) {
    document.getElementById('card-list').innerHTML = '<div class="error">โหลดข้อมูลไม่ได้</div>';
  }
}

const TAG_TH = { COMPOUNDER:'หุ้นเติบโต', DIVIDEND_KING:'ปันผลเด่น', CASH_COW:'เงินสดดี', CONTRARIAN:'สวนกระแส', TURNAROUND:'กำลังฟื้น', YIELD_TRAP:'ปันผลหลอก', DATA_WARNING:'ตรวจสอบข้อมูล' };
const TAG_COLOR = { COMPOUNDER:'green', DIVIDEND_KING:'yellow', CASH_COW:'purple', CONTRARIAN:'blue', TURNAROUND:'blue', YIELD_TRAP:'red', DATA_WARNING:'red' };

function normalizeStock(s) {
  const m = s.metrics || {};
  const agg = s.aggregates || {};
  return {
    sym: (s.symbol || '').replace('.BK',''),
    sector: s.sector || '',
    score: s.score || s.quality_score || 0,
    yield: (s.dividend_yield ?? m.dividend_yield ?? 0),
    avg5y: (s.five_year_avg_yield ?? m.five_year_avg_yield ?? 0),
    grade: (s.valuation && s.valuation.grade) || '-',
    tags: (s.signals || []).map(t => TAG_TH[t] || t),
    tagColors: (s.signals || []).map(t => TAG_COLOR[t] || 'blue')
  };
}

function getListForFilter() {
  if (currentFilter === 'filtered') return (state.screener?.filtered_out_stocks || []).map(normalizeStock);
  if (currentFilter === 'watchlist') return (state.watchlist?.stocks || []).map(normalizeStock);
  if (currentFilter === 'new') return ((state.screener?.candidates || []).filter(c => c.score >= 50 && !(state.watchlist?.stocks || []).find(w => w.symbol === c.symbol))).map(normalizeStock);
  // passed = candidates that passed filters sorted by score
  return (state.screener?.candidates || []).filter(c => c.score >= 50).map(normalizeStock);
}

async function openDetail(sym) {
  const dp = document.getElementById('detail-page');
  document.getElementById('detail-nav-title').textContent = sym;
  document.getElementById('detail-content').innerHTML = '<div class="loading">กำลังโหลด...</div>';
  dp.classList.add('open');
  try {
    const data = await fetch(API + '/api/stock/' + encodeURIComponent(sym)).then(r => r.json());
    renderDetail(sym, data);
  } catch (e) {
    document.getElementById('detail-content').innerHTML = '<div class="error">ไม่มีข้อมูลหุ้นนี้</div>';
  }
}

function renderDetail(sym, d) {
  const m = d.metrics || {};
  const agg = d.aggregates || {};
  const yearly = d.yearly_metrics || [];
  const price = d.price ?? m.current_price ?? '-';
  const pe = d.pe_ratio ?? m.pe ?? '-';
  const yld = d.dividend_yield ?? m.dividend_yield ?? 0;
  const payout = d.payout_ratio ?? m.payout ?? 0;
  const de = d.debt_to_equity ?? m.de ?? '-';
  const roe = d.roe ?? m.roe ?? agg.avg_roe ?? 0;
  // build checklist from real aggregates
  const checks = [
    { label: 'ROE ≥15% สม่ำเสมอ', pass: (agg.avg_roe || 0) >= 0.15 },
    { label: 'Gross Margin ≥30%', pass: (agg.avg_gross_margin || 0) >= 0.30 },
    { label: 'หนี้ต่ำ (D/E < 1.0)', pass: (m.de ?? 9) < 1.0 },
    { label: 'FCF บวก ≥3/4 ปี', pass: (agg.fcf_positive_years || 0) >= 3 },
    { label: 'ปันผล ≥5 ปีติด', pass: (agg.dividend_streak || 0) >= 5 },
    { label: 'EPS โตสม่ำเสมอ', pass: (agg.eps_cagr || 0) > 0 }
  ];
  // render innerHTML with real values + yearly table from yearly_metrics
  document.getElementById('detail-content').innerHTML = /* template with real values */;
}

// replace `renderCards()` on init at bottom
init();
```

## Phase 4: Mobile — wire Request / DCA / Settings pages
- [x] Wire Request form (page-requests, ~line 751) — input symbols → POST `/api/request` → poll `/api/request/status` ทุก 3 วินาที → แสดง list รายการ + สถานะ (processing/done/error), แสดงประวัติจาก `/api/requests`
- [x] Wire DCA form (page-dca, ~line 693) — fields (symbol, amount, days, backtest_years, forward_years, reinvest) → GET `/api/dca/{sym}?params` → render backtest summary cards (total_invested, current_value, cagr, total_dividends) + projection cards
- [x] Wire Settings page (page-settings, ~line 774) — init `fetch('/api/settings')` populate form (schedule enabled/day/hour, pipeline odd_weeks/even_weeks, filters) → POST `/api/settings` on save

### Reference
```javascript
// REQUEST page wire (mobile.html page-requests)
async function submitRequest() {
  const input = document.getElementById('req-symbols-input');
  const symbols = input.value.split(',').map(s => s.trim().toUpperCase()).filter(Boolean);
  if (!symbols.length) return;
  await fetch(API + '/api/request', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({symbols}) });
  input.value = '';
  pollRequestStatus();
}

async function pollRequestStatus() {
  const s = await fetch(API + '/api/request/status').then(r => r.json());
  const list = Object.entries(s).map(([sym, st]) => `<div class="req-item"><span class="sym">${sym.replace('.BK','')}</span><span class="status ${st}">${st}</span></div>`).join('');
  document.getElementById('req-status-list').innerHTML = list;
  if (Object.values(s).some(st => st === 'processing')) setTimeout(pollRequestStatus, 3000);
  else loadRequestHistory();
}

async function loadRequestHistory() {
  const data = await fetch(API + '/api/requests').then(r => r.json());
  // render data.requests grouped by date
}

// DCA page wire
async function runDCA() {
  const sym = document.getElementById('dca-symbol').value.trim().toUpperCase();
  const amount = document.getElementById('dca-amount').value;
  const days = Array.from(document.querySelectorAll('#dca-days input:checked')).map(x => x.value).join(',');
  const backtest = document.getElementById('dca-backtest-years').value;
  const forward = document.getElementById('dca-forward-years').value;
  const reinvest = document.getElementById('dca-reinvest').checked;
  const q = new URLSearchParams({ days, amount, backtest_years: backtest, forward_years: forward, reinvest });
  const data = await fetch(API + `/api/dca/${sym}?${q}`).then(r => r.json());
  // render data.backtest + data.projection into result cards
}

// SETTINGS page wire
async function loadSettings() {
  const cfg = await fetch(API + '/api/settings').then(r => r.json());
  document.getElementById('sch-enabled').checked = cfg.schedule.enabled;
  document.getElementById('sch-day').value = cfg.schedule.day_of_week;
  document.getElementById('sch-hour').value = cfg.schedule.hour;
  // ... populate other fields
}

async function saveSettings() {
  const body = {
    schedule: {
      enabled: document.getElementById('sch-enabled').checked,
      day_of_week: document.getElementById('sch-day').value,
      hour: parseInt(document.getElementById('sch-hour').value),
      minute: parseInt(document.getElementById('sch-minute').value)
    },
    pipeline: { odd_weeks: document.getElementById('pipe-odd').value, even_weeks: document.getElementById('pipe-even').value },
    filters: { /* ... */ }
  };
  await fetch(API + '/api/settings', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
}
```
