---
project: maxmahon
created: 2026-04-22
last_updated: 2026-04-23
status: done
---

# MaxMahon v6 · Watchlist Page & Compare Modal

> Part 5 of 9 — watchlist table + compare modal overlay + add-by-symbol flow, desktop + mobile | Index: maxmahon-v6-index
> Depends on: maxmahon-v6-03-frontend-foundation
> Parallel-safe with: 04, 06, 07, 08

## Phase 1: Watchlist page (desktop)
- [x] Port `projects/MaxMahon/web-v6-mockup/desktop/03-watchlist.html` to `projects/MaxMahon/web/v6/desktop/watchlist.html` + `projects/MaxMahon/web/v6/static/js/pages/watchlist.js`. Fetch: GET /api/watchlist/enriched. Render: (a) summary strip (Tracked/Hold/Review/Consider Exit/Avg Δ Entry/Oldest Position days), (b) table with rows per position containing: star (filled), symbol + name, current_score, Δ Entry ('+14 vs 60' format), entry_date ('15 Feb 2025'), exit_signal via `MMComponents.renderSevBadge`, notes (inline `<input class="notes-input">`), compare checkbox. On notes blur: PUT /api/user/notes/{symbol} with new value, show toast on success. On star click: PUT /api/user/watchlist {remove:[sym]} + optimistically remove row. Scope: desktop layout + CRUD wiring. Acceptance: visual match mockup 100%; notes save on blur; star remove works; no console errors.

### Reference
```javascript
// pages/watchlist.js (sketch)
async function onNoteBlur(sym, input) {
  const newNote = input.value;
  try {
    await MMApi.put(`/api/user/notes/${sym}`, { note: newNote });
    MMComponents.showToast('บันทึก note แล้ว', 'success');
  } catch (e) { MMComponents.showToast('Save failed: ' + e.message, 'error'); }
}
async function onStarRemove(sym, rowEl) {
  try {
    await MMApi.put('/api/user/watchlist', { remove: [sym] });
    rowEl.remove();
  } catch (e) { MMComponents.showToast(e.message, 'error'); }
}
```

## Phase 2: Compare modal (desktop)
- [x] Implement compare flow in `projects/MaxMahon/web/v6/static/js/pages/watchlist.js`: footer 'Compare N/3' button is disabled unless 2-3 checkboxes checked (Karl decision: up to 3). Click → call GET /api/watchlist/compare?symbols=A,B,C, then `MMComponents.openModal('compare', html)` rendering: column headers (symbols), row rows (Score, Yield, P/E, P/BV, Streak, Payout, ROE, Exit Signal, Mcap (B THB), Signals), cell best-value highlighted (accent `--oxblood` background on `best_index` column), delta column rightmost. Footer narrative paragraph at bottom. Scope: modal open/close + rendering; no save. Acceptance: with 2 boxes checked, button enables + clicks opens modal with 2 columns; with 3 checked, 3 columns; best-value cells highlighted; close button works.
- [x] Match compare modal styling exactly to mockup (if mockup shows embedded inline compare, instead render as backdrop + sheet overlay with slide-in per README note 'Compare view is embedded on the watchlist page (not a separate modal). If it needs to be a real overlay with backdrop, needs different treatment'). Karl decision: use real modal overlay with backdrop + close. Scope: modal component styling. Acceptance: backdrop darkens page; sheet centered; close button + Esc key both dismiss.

## Phase 3: Add-by-symbol modal
- [x] Implement 'Add by Symbol' flow in `projects/MaxMahon/web/v6/static/js/pages/watchlist.js`: footer '+ Add by Symbol' button → `MMComponents.openModal('add-sym', html)` with simple text input (Karl decision: text input, upgrade to autocomplete later) + submit button. On submit: trim + uppercase + auto-append '.BK' if missing suffix; call PUT /api/user/watchlist {add:[sym]}; on success close modal + refetch /api/watchlist/enriched + re-render table; show toast. Scope: one modal + submit flow. Acceptance: entering 'CPALL' → add call uses 'CPALL.BK'; entering 'CPALL.BK' → unchanged; watchlist refreshes with new row.

### Reference
```javascript
function normalizeSymbol(raw) {
  const s = raw.trim().toUpperCase();
  return s.endsWith('.BK') ? s : s + '.BK';
}
```

## Phase 4: Watchlist page (mobile)
- [x] Port `projects/MaxMahon/web-v6-mockup/mobile/03-watchlist.html` to `projects/MaxMahon/web/v6/mobile/watchlist.html` + extend `pages/watchlist.js` with mobile branch. Mobile: table rows → stacked cards (symbol + score top, metrics below, exit badge right, notes as textarea, star + compare checkbox footer). Modals render as bottom-sheet full-screen with slide-up animation (matching mockup). Scope: mobile variant. Acceptance: visual match mockup 100%; add-by-symbol modal slides up from bottom; compare modal full-screen with close bar at top.
