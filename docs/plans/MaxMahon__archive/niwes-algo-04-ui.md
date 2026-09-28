---
project: MaxMahon
created: 2026-04-21
last_updated: 2026-04-21
status: done
---

# UI Port: Charts + Score Breakdown + Watchlist Exit + On-demand Claude Button

> Part 4 of 5 — port web/ UI: score breakdown stacked bar, price history + yield trend charts, dividend history table, watchlist exit status, case study/moat tags display, on-demand Claude button (target existing #analysis-section, keep 3-perspective schema), history v2 display ใน #history-list container (divs, not table) | Index: niwes-algo-index | Depends on: niwes-algo-02-scan-engine | Parallel-safe with: niwes-algo-03-server

## Phase 1: Score Breakdown + Case Study/Moat Tags Display
- [x] แก้ `projects/MaxMahon/web/app.js` function `rowTagClass(sig)` — เพิ่ม mapping สำหรับ case study tags (RETAIL_DEFENSIVE_MOAT/BANK_VALUE_PBV1/HOLDING_CO_HIDDEN/VIETNAM_GROWTH_EXPOSURE/ENERGY_CYCLICAL_EXIT = `tag-case-study`) + moat tags (BRAND_MOAT/STRUCTURAL_MOAT/GOVT_LOCKIN = `tag-moat`) — **ห้ามเปลี่ยน class ของ DIVIDEND_TRAP** (keep `tag-trap`) + DATA_WARNING (keep `tag-warning`) เพื่อไม่กระทบ style เดิม — scope: add-only — Acceptance: inspect CPALL.BK row → RETAIL_DEFENSIVE_MOAT span มี class `tag-case-study`
- [x] แก้ function `stockRowHTML(c)` (บรรทัด 513) — ใน signals cell เปลี่ยนจาก limit ≤3 เป็น render ทุก signal (wrap ด้วย flex-wrap CSS) — scope: ห้ามแก้ column structure — Acceptance: row stock ที่มี 6 tags → render ครบ 6
- [x] เพิ่ม CSS ใน `projects/MaxMahon/web/style.css`: `.tag-case-study` (bg #1d5b4f forest-green, fg #f4f0e6), `.tag-moat` (bg #a02143 burgundy, fg #f4f0e6), padding 1px 6px, font-size 0.75em, border-radius 2px — scope: เพิ่มเท่านั้น ห้ามแก้ classes เดิม — Acceptance: RETAIL_DEFENSIVE_MOAT แสดงสีเขียว, BRAND_MOAT แสดงสีแดง
- [x] เพิ่ม score breakdown stacked horizontal bar ใน detail panel aside — ใน `renderDetailCharts(stockData)` (บรรทัด 833) เพิ่ม Chart.js horizontal stacked bar `type:'bar'`, `indexAxis:'y'`, 4 datasets: Dividend (50) #1d5b4f, Valuation (25) #1f3f76, Cash Flow (15) #b45309, Hidden (10) #6b7280 — ข้อมูลจาก `stockData.breakdown` (existing field ใน screener output → detail API pass through); ถ้าไม่มี breakdown → skip chart — เพิ่ม `<canvas id="chart-score-breakdown">` ใน detail panel HTML template inside renderDetailCharts wrapper — scope: ไม่เปลี่ยน 3 mini-charts เดิม — Acceptance: เปิด detail CPALL.BK → เห็น stacked bar 4 สี + legend ขวา

### Reference
```javascript
// app.js — rowTagClass extension
const CASE_STUDY_TAGS = new Set(['RETAIL_DEFENSIVE_MOAT','BANK_VALUE_PBV1','HOLDING_CO_HIDDEN','VIETNAM_GROWTH_EXPOSURE','ENERGY_CYCLICAL_EXIT']);
const MOAT_TAGS = new Set(['BRAND_MOAT','STRUCTURAL_MOAT','GOVT_LOCKIN']);

function rowTagClass(sig) {
  if (sig === 'NIWES_5555') return 'tag-king';
  if (sig === 'HIDDEN_VALUE') return 'tag-hidden';
  if (sig === 'DEEP_VALUE') return 'tag-value';
  if (sig === 'QUALITY_DIVIDEND') return 'tag-compounder';
  if (sig === 'DIVIDEND_TRAP') return 'tag-trap';          // KEEP
  if (sig === 'DATA_WARNING') return 'tag-warning';        // KEEP
  if (CASE_STUDY_TAGS.has(sig)) return 'tag-case-study';
  if (MOAT_TAGS.has(sig)) return 'tag-moat';
  return 'tag-default';
}
```

```javascript
// score breakdown chart (inside renderDetailCharts)
function renderScoreBreakdown(canvasId, breakdown) {
  if (!breakdown) return null;
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  return new Chart(ctx.getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['Score'],
      datasets: [
        { label: 'Dividend (50)', data: [breakdown.dividend || 0], backgroundColor: '#1d5b4f' },
        { label: 'Valuation (25)', data: [breakdown.valuation || 0], backgroundColor: '#1f3f76' },
        { label: 'Cash Flow (15)', data: [breakdown.cash_flow || 0], backgroundColor: '#b45309' },
        { label: 'Hidden (10)', data: [breakdown.hidden_value || 0], backgroundColor: '#6b7280' },
      ]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      scales: { x: { stacked: true, max: 100 }, y: { stacked: true } },
      plugins: { legend: { position: 'right' } },
    },
  });
}

// In renderDetailCharts(d):
//   const bd = d.breakdown || (d.candidate || {}).breakdown;
//   renderScoreBreakdown('chart-score-breakdown', bd);
```

```css
/* style.css */
.tag-case-study { background: #1d5b4f; color: #f4f0e6; padding: 1px 6px; font-size: 0.75em; border-radius: 2px; }
.tag-moat { background: #a02143; color: #f4f0e6; padding: 1px 6px; font-size: 0.75em; border-radius: 2px; }
```

## Phase 2: Price History + Yield Trend Charts + Dividend Table
- [x] เพิ่ม price history line chart ใน detail panel — ใน renderDetailCharts() เพิ่ม async helper `loadPriceHistory(symbol, canvasId)` ที่เรียก `GET /api/stock/{sym}/price-history` (plan 03 Phase 3), ได้ `{data: [{date, close}, ...]}` แล้ว render Chart.js line chart (x = date labels, y = close, borderColor #1f3f76, tension 0.2, no fill) — ถ้า fetch fail/empty → แทน canvas ด้วย `<div class="chart-placeholder">ข้อมูลราคาย้อนหลังยังไม่พร้อม</div>` — scope: frontend-only fetch logic — Acceptance: CPALL.BK detail → เห็น line chart 120 จุด (10yr monthly)
- [x] เพิ่ม yield trend line chart ใน detail panel — compute annual yields จาก `d.dividend_history[year] / d.yearly_metrics[year].price_avg` (price_avg field ที่ plan 01 Phase 1 เพิ่มไว้ใน fetch_data.py) — ถ้าปีใด price_avg=null ให้ skip ปีนั้น (ไม่ใช้ current price เพราะจะได้ข้อมูลเท็จ) + rolling 5yr avg overlay — Chart.js 2 datasets (forest-green + amber dashed) — ถ้ามี <3 data points → hide chart + แสดง placeholder — scope: ไม่ mock ข้อมูล — Acceptance: CPALL.BK → yield trend chart แสดงจุดจริงจาก yearly_metrics 5-10 ปี + rolling avg
- [x] เพิ่ม dividend history table ใน detail panel aside (ใต้ mini-charts) — HTML table 4 cols (ปี / DPS / YoY Growth % / Payout %) — render จาก `d.dividend_history` (dict year→dps) + `d.yearly_metrics[year].payout_ratio` — latest 10 years sorted asc — growth สีแดงถ้าลบ — scope: pure render ไม่ fetch เพิ่ม — Acceptance: ตาราง 10 แถว + ปีที่ YoY ลบเป็นสีแดง

### Reference
```javascript
// app.js — inside renderDetailCharts or separate helper
async function loadPriceHistoryChart(symbol, canvasId) {
  try {
    const res = await fetch(`${API}/api/stock/${encodeURIComponent(symbol)}/price-history`);
    if (!res.ok) throw new Error('fetch fail');
    const { data } = await res.json();
    if (!data || !data.length) throw new Error('empty');
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    new Chart(ctx.getContext('2d'), {
      type: 'line',
      data: {
        labels: data.map(p => p.date),
        datasets: [{ label: 'ราคา', data: data.map(p => p.close), borderColor: '#1f3f76', tension: 0.2, fill: false, pointRadius: 0 }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { maxTicksLimit: 10 } } } },
    });
  } catch (e) {
    const ctx = document.getElementById(canvasId);
    if (ctx) ctx.replaceWith(Object.assign(document.createElement('div'), {
      className: 'chart-placeholder', textContent: 'ข้อมูลราคาย้อนหลังยังไม่พร้อม',
    }));
  }
}

function renderYieldTrend(canvasId, dividendHistory, yearlyMetrics) {
  const years = Object.keys(dividendHistory || {}).sort();
  const yearMap = new Map((yearlyMetrics || []).map(m => [String(m.year), m]));
  const points = years.map(y => {
    const dps = dividendHistory[y];
    const ym = yearMap.get(y) || {};
    const priceAvg = ym.price_avg;  // from plan 01 Phase 1
    if (!priceAvg || priceAvg <= 0) return null;
    return { y: y, value: (dps / priceAvg) * 100 };
  }).filter(Boolean);
  if (points.length < 3) {
    const el = document.getElementById(canvasId);
    if (el) el.replaceWith(Object.assign(document.createElement('div'), { className: 'chart-placeholder', textContent: 'ข้อมูลน้อยเกินไป' }));
    return;
  }
  const yields = points.map(p => p.value);
  const labels = points.map(p => p.y);
  const rolling = yields.map((_, i, arr) => {
    const slice = arr.slice(Math.max(0, i - 4), i + 1);
    return slice.reduce((a, b) => a + b, 0) / slice.length;
  });
  const ctx = document.getElementById(canvasId).getContext('2d');
  new Chart(ctx, {
    type: 'line', data: { labels, datasets: [
      { label: 'Yield %', data: yields, borderColor: '#1d5b4f', tension: 0.1 },
      { label: 'Rolling 5y', data: rolling, borderColor: '#b45309', borderDash: [4,4], tension: 0.1 },
    ]},
    options: { responsive: true, maintainAspectRatio: false },
  });
}

function renderDividendHistoryTable(containerId, dividendHistory, yearlyMetrics) {
  const years = Object.keys(dividendHistory || {}).sort().slice(-10);
  const ym = new Map((yearlyMetrics || []).map(m => [String(m.year), m]));
  const rows = years.map((y, i) => {
    const dps = dividendHistory[y];
    const prev = i > 0 ? dividendHistory[years[i-1]] : null;
    const growth = prev && prev > 0 ? ((dps - prev) / prev) * 100 : null;
    const payout = (ym.get(y) || {}).payout_ratio;
    const growthCls = growth != null && growth < 0 ? 'neg' : 'pos';
    const growthTxt = growth != null ? `${growth.toFixed(1)}%` : '-';
    const payoutTxt = payout != null ? `${(payout * 100).toFixed(0)}%` : '-';
    return `<tr><td>${y}</td><td>${dps.toFixed(2)}</td><td class="${growthCls}">${growthTxt}</td><td>${payoutTxt}</td></tr>`;
  });
  const el = document.getElementById(containerId);
  if (el) el.innerHTML = `<table class="div-history"><thead><tr><th>ปี</th><th>DPS</th><th>YoY</th><th>Payout</th></tr></thead><tbody>${rows.join('')}</tbody></table>`;
}
```

## Phase 3: Watchlist Exit Status Section
- [x] เพิ่ม HTML container ใน detail panel (สร้างใน loadDetail template string ใกล้ aside column) `<section id="exit-status-section" class="exit-status" hidden>` + `<h3>Watchlist Exit Status</h3>` + 3 inner divs (exit-baseline, exit-triggers, exit-summary) — scope: HTML-only — Acceptance: DOM มี section element แม้ stock ไม่ใน watchlist (hidden)
- [x] เพิ่ม function `renderExitStatus(symbol)` ใน app.js — fetch `/api/watchlist/{sym}/exit-status` → ถ้า `!in_watchlist` → section.hidden=true return; else show baseline (date_added + pe/pbv/dy baseline formatted) + triggers cards (1 card ต่อ trigger: severity-high|medium class + type + reason) + summary 'High: N · Medium: M'; ถ้าไม่มี baseline → แสดง 'ยังไม่มี baseline (scan ครั้งต่อไปจะสร้าง)'; ถ้าไม่มี triggers → 'ไม่มี trigger' — เรียก `renderExitStatus(fullSymbol)` ใน loadDetail() หลัง fetchAnalysis — scope: error-safe (fetch fail → section hidden) — Acceptance: CPALL.BK (in watchlist + baseline exists) → section visible + triggers cards; SAUCE.BK (not in watchlist) → section hidden
- [x] เพิ่ม CSS ใน style.css: `.exit-status` (border-top + padding), `.exit-status-card` (border + padding + radius), `.severity-high` (bg #fce7ec + border-left 4px #a02143), `.severity-medium` (bg #fff4e0 + border-left 4px #b45309), `.trigger-type` (JetBrains Mono 0.75em uppercase), `.exit-summary` (mono) — Acceptance: high trigger card มีขอบซ้ายสีแดง, type text เป็น mono uppercase

### Reference
```javascript
// app.js — renderExitStatus
async function renderExitStatus(symbol) {
  const section = document.getElementById('exit-status-section');
  if (!section) return;
  try {
    const res = await fetch(`${API}/api/watchlist/${encodeURIComponent(symbol)}/exit-status`);
    if (!res.ok) { section.hidden = true; return; }
    const data = await res.json();
    if (!data.in_watchlist) { section.hidden = true; return; }
    section.hidden = false;
    const b = data.baseline;
    document.getElementById('exit-baseline').innerHTML = b
      ? `<p>Passed 5-5-5-5: <strong>${b.date_added}</strong> · PE baseline <strong>${(b.pe_baseline ?? 0).toFixed ? b.pe_baseline.toFixed(2) : '-'}</strong> · PBV <strong>${b.pbv_baseline?.toFixed ? b.pbv_baseline.toFixed(2) : '-'}</strong> · Yield <strong>${b.dy_baseline?.toFixed ? b.dy_baseline.toFixed(2) + '%' : '-'}</strong></p>`
      : '<p class="muted">ยังไม่มี baseline (scan ครั้งต่อไปจะสร้าง)</p>';
    const triggersHtml = (data.triggers || []).map(t => `
      <div class="exit-status-card severity-${t.severity}">
        <span class="trigger-type">${escapeHtml(t.type || '')}</span>
        <p>${escapeHtml(t.reason || '')}</p>
      </div>`).join('');
    document.getElementById('exit-triggers').innerHTML = triggersHtml || '<p class="muted">ไม่มี trigger</p>';
    const s = data.severity_summary || { high: 0, medium: 0 };
    document.getElementById('exit-summary').textContent = `High: ${s.high} · Medium: ${s.medium}`;
  } catch (e) { section.hidden = true; }
}
// wire in loadDetail(): renderExitStatus(fullSymbol);
```

```html
<!-- inside detail panel aside HTML template -->
<section id="exit-status-section" class="exit-status" hidden>
  <h3>Watchlist Exit Status</h3>
  <div id="exit-baseline"></div>
  <div id="exit-triggers"></div>
  <div id="exit-summary" class="exit-summary"></div>
</section>
```

```css
.exit-status { border-top: 1px solid #d6cfbd; padding-top: 1rem; margin-top: 1rem; }
.exit-status-card { border: 1px solid #d6cfbd; padding: 0.5rem; margin: 0.3rem 0; border-radius: 2px; }
.severity-high { background: #fce7ec; border-left: 4px solid #a02143; }
.severity-medium { background: #fff4e0; border-left: 4px solid #b45309; }
.trigger-type { font-family: 'JetBrains Mono', monospace; font-size: 0.75em; text-transform: uppercase; color: #121420; }
.exit-summary { margin-top: 0.5rem; font-family: 'JetBrains Mono', monospace; color: #121420; }
```

## Phase 4: On-demand Claude Button + History v2 Display
- [x] แก้ `loadDetail(fullSymbol)` ใน app.js (ใกล้บรรทัด 1355-1359) — **ลบ** line `fetchAnalysis(fullSymbol);` ใน setTimeout — แทนด้วย `renderAnalysisStub(fullSymbol);` (new function) — เพื่อให้เปิด detail ไม่เรียก Claude อัตโนมัติ — scope: แก้จุดเดียว — Acceptance: เปิด detail panel → เปิด Network tab ใน browser devtools → ไม่มี request ไป `/api/stock/.../analysis`
- [x] เพิ่ม functions ใน app.js: `renderAnalysisStub(symbol)` แสดง placeholder + button ใน `#analysis-section` (existing ID line 1368 — ใช้ตรงนี้ ห้ามเปลี่ยน ID); `triggerAnalysis(symbol)` = flow: disable button + show spinner → GET /analysis (เช็ค cache) → ถ้า 404 → POST /analyze → render content (keep 3-perspective: `data.buffett / data.hong / data.max` ผ่าน escapeHtml + 3 cards เดิม) + cache badge `Cached · {analyzed_at}` — scope: schema ต้อง match server plan 03 Phase 1 (`{analyzed_at, model, buffett, hong, max}`) — Acceptance: ลบ cache file → เปิด detail ไม่มี Claude call → กด button → spinner 2-5 วินาที → 3 cards + cache badge; กดอีกครั้งหลัง refresh detail → return cached ทันที
- [x] เพิ่ม history v2 display — แก้ function ที่ fetch `/api/history` (ค้นใน app.js) เปลี่ยนเป็น `/api/history/v2?limit=30` — render เข้า `#history-list` container (existing div บรรทัด 160 ใน index.html — **ไม่ใช่ table**) เป็น list of `<div class="history-entry">` แต่ละอันมี: date / scanned / passed / review / new / top_3_symbols / scoring_version badge + click expand แสดง top_candidates list (symbol+score+tags) — scope: render as divs ไม่ใช่ table — Acceptance: History page load 30 entries เรียงล่าสุด + click expand แสดง top candidates list
- [x] เพิ่ม CSS ใน style.css: `.spinner` (border 2px cream top forest-green, keyframe spin 0.7s), `.cache-badge` (bg #1d5b4f + cream text + JetBrains Mono 0.7em), `.btn-primary` (bg #1d5b4f + cream + Plex Sans Thai), `.btn-primary:disabled` (opacity 0.6 + cursor wait), `.history-entry` (border + padding + grid row), `.history-entry.expanded` (bg #faf8f2), `.history-expand` (display none default, block when expanded) — Acceptance: click analyze button → spinner visible + disabled; done → spinner หาย + cache badge แสดง

### Reference
```javascript
// app.js — loadDetail (near line 1355) — CHANGE
  setTimeout(() => {
    renderDetailCharts(d);
    renderAnalysisStub(fullSymbol);  // was: fetchAnalysis(fullSymbol);
    renderExitStatus(fullSymbol);    // new (plan 4 Phase 3)
  }, 50);

// new functions
function renderAnalysisStub(symbol) {
  const section = document.getElementById('analysis-section');  // EXISTING ID, line 1368
  if (!section) return;
  section.innerHTML = `
    <div class="analysis-ondemand">
      <p class="muted">คลิก เพื่อให้ AI วิเคราะห์หุ้น ${escapeHtml(symbol)} (ใช้ API credit)</p>
      <button id="analyze-btn" class="btn-primary">วิเคราะห์เพิ่มเติม (ใช้ AI)</button>
    </div>`;
  document.getElementById('analyze-btn').addEventListener('click', () => triggerAnalysis(symbol));
}

async function triggerAnalysis(symbol) {
  const btn = document.getElementById('analyze-btn');
  const section = document.getElementById('analysis-section');
  if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> กำลังวิเคราะห์...'; }
  try {
    let res = await fetch(`${API}/api/stock/${encodeURIComponent(symbol)}/analysis`);
    let data;
    if (res.status === 404) {
      res = await fetch(`${API}/api/stock/${encodeURIComponent(symbol)}/analyze`, { method: 'POST' });
      if (!res.ok) throw new Error('analyze failed: ' + res.status);
      data = await res.json();
    } else if (res.ok) {
      data = await res.json();
    } else { throw new Error('fetch: ' + res.status); }
    renderAnalysisContent(data);
  } catch (e) {
    section.innerHTML = `<p class="error">วิเคราะห์ไม่สำเร็จ: ${escapeHtml(e.message)}</p>`;
  }
}

function renderAnalysisContent(payload) {
  // payload = {analyzed_at, model, buffett, hong, max}  (plan 03 Phase 1 schema)
  const section = document.getElementById('analysis-section');
  if (!section) return;
  section.innerHTML = `
    <div class="cache-badge">Cached · ${escapeHtml(payload.analyzed_at || '')}</div>
    <div class="analysis-card">
      <div class="analysis-header"><span class="analysis-icon">🎩</span><span class="analysis-name">มุมมอง Buffett</span></div>
      <p class="analysis-text">${escapeHtml(payload.buffett || '')}</p>
    </div>
    <div class="analysis-card">
      <div class="analysis-header"><span class="analysis-icon">💰</span><span class="analysis-name">มุมมองเซียนฮง</span></div>
      <p class="analysis-text">${escapeHtml(payload.hong || '')}</p>
    </div>
    <div class="analysis-card">
      <div class="analysis-header"><span class="analysis-icon">📊</span><span class="analysis-name">Max Mahon สรุป</span></div>
      <p class="analysis-text">${escapeHtml(payload.max || '')}</p>
    </div>`;
}

// history v2 display — render into #history-list (EXISTING container, index.html line 160)
async function loadHistoryV2() {
  const container = document.getElementById('history-list');
  if (!container) return;
  try {
    const res = await fetch(`${API}/api/history/v2?limit=30`);
    const { scans } = await res.json();
    const sorted = [...scans].reverse();  // latest first
    container.innerHTML = sorted.map(s => {
      const top3 = (s.top_candidates || []).slice(0, 3).map(c => c.symbol).join(' · ');
      const topList = (s.top_candidates || []).map(c =>
        `<div class="hist-cand"><strong>${escapeHtml(c.symbol)}</strong> score ${c.score} · Y ${c.yield?.toFixed?.(1) ?? '-'}% · PE ${c.pe?.toFixed?.(1) ?? '-'} · ${(c.tags || []).join(' ')}</div>`
      ).join('');
      return `
        <div class="history-entry" data-scan="${s.num}">
          <div class="history-row-main">
            <span class="mono">${s.date?.slice(0,10) || '-'}</span>
            <span>scan ${s.counts?.scanned ?? 0}</span>
            <span>pass ${s.counts?.passed ?? 0}</span>
            <span>review ${s.counts?.review ?? 0}</span>
            <span>new ${s.counts?.new ?? 0}</span>
            <span class="mono">${escapeHtml(top3)}</span>
            <span class="tag-default">${escapeHtml(s.scoring_version || '-')}</span>
          </div>
          <div class="history-expand" hidden>${topList}</div>
        </div>`;
    }).join('');
    container.querySelectorAll('.history-entry').forEach(el => {
      el.addEventListener('click', () => {
        el.classList.toggle('expanded');
        const exp = el.querySelector('.history-expand');
        if (exp) exp.hidden = !el.classList.contains('expanded');
      });
    });
  } catch (e) { container.innerHTML = '<p class="error">โหลดประวัติไม่สำเร็จ</p>'; }
}
```

```css
/* style.css */
.spinner { display: inline-block; width: 0.8em; height: 0.8em; border: 2px solid #f4f0e6; border-top-color: #1d5b4f; border-radius: 50%; animation: spin 0.7s linear infinite; vertical-align: middle; }
@keyframes spin { to { transform: rotate(360deg); } }
.cache-badge { display: inline-block; padding: 2px 8px; background: #1d5b4f; color: #f4f0e6; font-family: 'JetBrains Mono', monospace; font-size: 0.7em; border-radius: 2px; margin-bottom: 0.5rem; }
.analysis-ondemand .muted { color: #6b7280; margin-bottom: 0.5rem; }
.btn-primary { background: #1d5b4f; color: #f4f0e6; border: 0; padding: 0.5rem 1rem; font-family: 'IBM Plex Sans Thai', sans-serif; cursor: pointer; }
.btn-primary:disabled { opacity: 0.6; cursor: wait; }
.history-entry { border: 1px solid #d6cfbd; padding: 0.75rem; margin: 0.5rem 0; cursor: pointer; }
.history-entry.expanded { background: #faf8f2; }
.history-row-main { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }
.history-expand { margin-top: 0.5rem; }
.hist-cand { padding: 0.25rem 0; border-bottom: 1px solid #eee; font-size: 0.9em; }
```
