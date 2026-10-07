---
project: MaxMahon
created: 2026-04-13
last_updated: 2026-04-23
status: done
---

# Dashboard Redesign ตาม Mockup

> Redesign หน้า dashboard ให้ตรง mockup.html 100% — card ไม่ซ้อนกัน, grid slide transition, แต่ละ tab มี layout เฉพาะ, filtered กดดู detail ได้

## Phase 1: Layout & Navigation Overhaul
- [x] HTML+CSS: เพิ่ม #stock-section wrapper ครอบ stock-layout + pipeline-bar, ย้าย request/dca/settings panels ออกมาเป็น .page-panel แยกจาก stock section, เพิ่ม CSS .page-panel { display:none } + .page-panel.active { display:block } + fadeIn animation, ซ่อน scrollbar ทุกที่ด้วย *::-webkit-scrollbar { display:none } + scrollbar-width:none — อ้างอิง mockup.html structure
- [x] JS: rewrite bindTabs() — แยก tab เป็น 2 type: stock tabs (passed/watchlist/discoveries/filtered) แสดง #stock-section + #pipeline-bar, page tabs (requests/dca/settings) ซ่อน #stock-section + #pipeline-bar แล้วแสดง .page-panel#page-{tab} ตัวเดียว, ลบ logic เดิมที่ toggle reqPanel/dcaPanel/settingsPanel ใน bindTabs()

### Reference
```html
<!-- เดิม: panels อยู่ใน app-layout -->
<div class="app-layout" id="app-layout">
  <div class="stock-list">...</div>
  <div class="detail-panel">...</div>
</div>
<div class="request-panel">...</div>
<div class="dca-panel">...</div>
<div class="settings-panel">...</div>

<!-- ใหม่: stock-section wrapper + page-panels แยก -->
<div id="stock-section">
  <div class="pipeline-bar">...</div>
  <div class="stock-layout grid-mode" id="stock-layout">
    <div class="stock-list">...</div>
    <div class="detail-panel">...</div>
  </div>
</div>
<div class="page-panel" id="page-requests">...</div>
<div class="page-panel" id="page-dca">...</div>
<div class="page-panel" id="page-settings">...</div>
```

```js
// เดิม bindTabs:
if (state.activeTab === 'requests') {
  reqPanel.style.display = '';
  dcaPanel.style.display = 'none';
  ...
}

// ใหม่ bindTabs:
const type = btn.dataset.type; // 'stock' or 'page'
if (type === 'stock') {
  stockSection.style.display = '';
  pipelineBar.style.display = '';
  document.querySelectorAll('.page-panel').forEach(p => p.classList.remove('active'));
} else {
  stockSection.style.display = 'none';
  pipelineBar.style.display = 'none';
  document.getElementById('page-' + tab).classList.add('active');
}
```

## Phase 2: Card Redesign + Grid-Slide Interaction
- [x] CSS: card styles ใหม่ — .card-row (flex, gap:12px), .card-score-circle (48x48 ซ้าย, border-radius:50%), .card-actions (absolute top-right, opacity:0 → hover opacity:1), .card-metrics-row (flex, border-top), ลบ .card-top/.card-identity/.card-score เก่า — ดู mockup.html เป็นหลัก
- [x] CSS: grid-mode/split-mode system — .stock-layout (flex, transition 0.4s), .grid-mode .stock-grid (grid-template-columns: repeat(auto-fill, minmax(280px,1fr))), .split-mode .stock-list (width:380px, overflow-y:auto), .split-mode .detail-panel (flex:1, opacity:1), .grid-mode .detail-panel (width:0, opacity:0), override @media(min-width:1024px) desktop layout เดิมให้ใช้ grid/split system แทน
- [x] JS: แก้ renderStockList() — card template ใหม่ตาม mockup (card-row > score-circle + card-info, card-metrics-row, card-tags, card-actions hover only), แก้ loadDetail() เพิ่ม toggle layout.classList split-mode/grid-mode แทน detail.style.display, แก้ closeDetail() toggle กลับ grid-mode, เพิ่ม detail-close-btn ใน renderDetail()

### Reference
```html
<!-- เดิม card template -->
<div class="card-actions">...</div>
<div class="card-top">
  <div class="card-identity"><h3>SYM</h3></div>
  <div class="card-score"><div class="score-circle high">89</div></div>
</div>
<div class="card-metrics">...</div>

<!-- ใหม่ card template -->
<div class="card-actions">...</div> <!-- opacity:0, hover:1 -->
<div class="card-row">
  <div class="card-score-circle high">89</div>
  <div class="card-info">
    <h3>SYM</h3>
    <div class="sector">Sector</div>
  </div>
</div>
<div class="card-metrics-row">
  <div class="card-metric"><span class="label">Yield</span><span class="value">3.8%</span></div>
  <div class="card-metric"><span class="label">Avg 5y</span><span class="value">2.3%</span></div>
  <div class="card-metric"><span class="label">ระดับราคา</span><span class="val-badge val-b">B</span></div>
</div>
<div class="card-tags">...</div>
```

```js
// loadDetail ใหม่:
async function loadDetail(symbol) {
  state.currentStock = symbol;
  const layout = document.getElementById('stock-layout');
  layout.classList.remove('grid-mode');
  layout.classList.add('split-mode');
  renderStockList(); // highlight selected
  // ... fetch + render
}
function closeDetail() {
  state.currentStock = null;
  const layout = document.getElementById('stock-layout');
  layout.classList.remove('split-mode');
  layout.classList.add('grid-mode');
  renderStockList();
}
```

## Phase 3: Filtered Stocks — Full Detail
- [x] JS: แก้ filtered card rendering ใน renderStockList() — เพิ่ม onclick="loadDetail(sym)", เพิ่ม card-row layout, แสดง basic_metrics (yield, roe) ใน card-metrics-row, style ยังคง border-left สีแดง + แสดง reasons
- [x] JS+CSS: แก้ renderDetail() — เช็คว่า symbol อยู่ใน filtered_out_stocks หรือไม่ (เก็บ reasons ไว้ใน state), ถ้าใช่แสดง .filtered-banner สีแดงบอกเหตุผลที่ไม่ผ่านเกณฑ์, เพิ่ม CSS .filtered-banner (background:var(--red-light), border, color:var(--red)), handle loadDetail error gracefully ถ้า API ไม่มี data ให้แสดงข้อความ 'ไม่มีข้อมูลละเอียด'

### Reference
```js
// เดิม filtered rendering:
el.innerHTML = '<div class="stock-grid">' + filtered.map(s => {
  return `<div class="stock-card filtered-card">
    <div class="card-top">...</div>
    <div class="filtered-reasons">${reasons}</div>
    <div class="card-metrics">...</div>
  </div>`;
}).join('') + '</div>';

// ใหม่ filtered rendering:
return `<div class="stock-card filtered-card" onclick="loadDetail('${sym}')">
  <div class="card-row">
    <div class="card-info">
      <h3>${sym}</h3>
      <div class="sector">${sector}</div>
    </div>
  </div>
  <div class="filtered-reasons">${reasons}</div>
  <div class="card-metrics-row">
    <div class="card-metric"><span class="label">Yield</span><span class="value">${dy}</span></div>
    <div class="card-metric"><span class="label">ROE</span><span class="value">${roe}</span></div>
  </div>
</div>`;

// renderDetail เพิ่ม filtered banner:
const filteredStock = (state.screener?.filtered_out_stocks || []).find(s => s.symbol === d.symbol);
const filteredBanner = filteredStock
  ? `<div class="filtered-banner">ไม่ผ่านเกณฑ์: ${filteredStock.reasons.join(', ')}</div>`
  : '';
```
