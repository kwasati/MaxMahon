---
project: maxmahon
created: 2026-04-22
last_updated: 2026-04-23
status: done
---

# MaxMahon v6 · Portfolio (Real + Simulated)

> Part 6 of 9 — portfolio real holdings + simulated allocation stacked sections, desktop + mobile | Index: maxmahon-v6-index
> Depends on: maxmahon-v6-03-frontend-foundation
> Parallel-safe with: 04, 05, 07, 08

## Phase 1: Portfolio page — Real section (desktop)
- [x] Create `projects/MaxMahon/web/v6/desktop/portfolio.html` + `projects/MaxMahon/web/v6/static/js/pages/portfolio.js`. Section 04a Real Holdings: fetch GET /api/portfolio/pnl. Render: (a) donut pie chart of positions by market value (Chart.js doughnut, segment colors derived from position symbol hash mapped to grayscale + oxblood accent for largest position), (b) totals strip (total MV, unrealized P&L %, total dividends_received, cash_reserve), (c) table columns: Position (sym + name), Qty, Avg Cost, Current Price, Market Value, P&L %, Dividends Received per position, (d) footer 'Total positions N · cash reserve ฿X' + '+ เพิ่ม Transaction' button. Scope: real holdings only; simulated in Phase 2. Acceptance: visual match mockup 04a section 100%; pie renders; table populated.
- [x] Implement add-transaction modal in portfolio.js: button click → `MMComponents.openModal('add-tx', html)` with fields: symbol (text input with .BK auto-append), date (date picker default today), type (radio BUY/SELL), price (number), qty (number), note (text). Submit → POST /api/portfolio/transactions with body; on success refetch /api/portfolio/pnl + re-render; show toast. Scope: one modal; one submit. Acceptance: submit with BBL.BK + 2025-02-15 + BUY + 150 + 100 creates transaction; PnL table updates with new row.
- [x] Implement delete-transaction flow: each table row has a delete button (or transactions history view) → DELETE /api/portfolio/transactions/{tx_id} → refetch + re-render. Scope: one button + confirm prompt. Acceptance: clicking delete removes row; undo toast offered for 5s (optional — if mockup doesn't show undo, skip).

## Phase 2: Portfolio page — Simulated section (desktop)
- [x] Extend `projects/MaxMahon/web/v6/static/js/pages/portfolio.js` with Section 04b Simulated: fetch GET /api/portfolio/simulated. Render: (a) donut pie of target weights, (b) totals strip (total_weight_pct, projected_yoc_pct, cash_reserve_pct, concentration_profile '30/30/30/10' — free text from response), (c) table: Position (sym + label free-text), Weight % + inline bar visual, Current Price, Target Yield, Score, Signal tag, (d) footer '+ เพิ่มหุ้น' button. Inline edit weight_pct on blur → validate sum = 100% (or show warning if not). Scope: simulated section. Acceptance: visual match mockup 04b section 100%; editing weights updates live bar; sum warning visible if not 100%.
- [x] Implement add-row modal (simulated): button click → modal with fields symbol, label (free-text per Karl decision), weight_pct. On submit: PUT /api/portfolio/simulated with full positions array (existing + new); on success refetch + re-render. Scope: one modal; PUT replaces entire list. Acceptance: adding row appends to list; save persists (refresh page → row still present).

### Reference
```javascript
// pages/portfolio.js simulated save
async function saveSimulated(positions, cashPct) {
  try {
    await MMApi.put('/api/portfolio/simulated', {
      positions: positions.map(p => ({ symbol: p.symbol, label: p.label, weight_pct: p.weight_pct })),
      cash_reserve_pct: cashPct,
    });
    MMComponents.showToast('Saved', 'success');
    await refetchAndRender();
  } catch (e) { MMComponents.showToast(e.message, 'error'); }
}
```

## Phase 3: Portfolio page (mobile)
- [x] Port `projects/MaxMahon/web-v6-mockup/mobile/04-portfolio.html` to `projects/MaxMahon/web/v6/mobile/portfolio.html` + extend `pages/portfolio.js` mobile branch. Mobile: stacked sections 04a then 04b, tables → card list (Position card with qty/cost/MV/P&L/Div stacked), donuts smaller (200x200px), modals bottom-sheet. Scope: mobile variant of both sections. Acceptance: visual match mockup 100%; both sections render; add modals slide up from bottom.
