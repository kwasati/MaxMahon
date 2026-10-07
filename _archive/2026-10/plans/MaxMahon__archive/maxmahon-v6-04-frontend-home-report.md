---
project: maxmahon
created: 2026-04-22
last_updated: 2026-04-23
status: done
---

# MaxMahon v6 · Home & Full Report Pages

> Part 4 of 9 — home card grid + full report 10 sections, desktop + mobile | Index: maxmahon-v6-index
> Depends on: maxmahon-v6-03-frontend-foundation
> Parallel-safe with: 05, 06, 07, 08 (different page files)

## Phase 1: Home page (desktop)
- [x] Port `projects/MaxMahon/web-v6-mockup/desktop/01-home.html` to `projects/MaxMahon/web/v6/desktop/home.html` + `projects/MaxMahon/web/v6/static/js/pages/home.js`. The html file contains only content sections (masthead + nav rendered by shell); js module exports `mount(container)` that fetches and renders. Render sections: (a) lede block narrative, (b) summary strip with 7 cells (scanned/passed/review/avg yield/top score/new entrants/sectors) from `summary` block of /api/screener, (c) trend bar chart from /api/screener/trend?weeks=12 using Chart.js, (d) This Week's Leaders top 5 by score, (e) filter/sort chips (sort by Score/Yield/P/E/P/BV/Δ Score + signal chips All/Niwes 5555/Hidden Value/Deep Value/Quality Div), (f) card grid 15 cards initial + 'Load remaining N of M' button, (g) card click → `location.href = '/report/' + symbol`. Data: GET /api/screener + GET /api/screener/trend?weeks=12 + GET /api/status (for masthead next_scan). Date format: canonical '15 Feb 2025' (3-letter month). Scope: desktop layout only; mobile in Phase 3. Acceptance: visual match `web-v6-mockup/desktop/01-home.html` 100% (side-by-side diff); data populated from API; no hardcoded samples; no console errors.
- [x] Integrate Chart.js for trend bar chart in home.js: include `<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>` in desktop/index.html app shell (Plan 03 output) — verify present; if not, add. Configure trend chart: x = week_label, y = passed count, color = `var(--oxblood)`, no shadows, no legend (matches mockup minimalism). Scope: one chart. Acceptance: trend chart renders 12 bars with mockup styling.
- [x] Implement client-side sort + filter on card grid (no API re-call): sort chips toggle orders array in-place; signal chips filter by `tags` array membership; card count label updates 'X of Y'. Scope: pure JS, no state library. Acceptance: toggling chips re-renders grid instantly; count label always correct.

### Reference
```javascript
// web/v6/static/js/pages/home.js (skeleton)
export async function mount(container) {
  MMComponents.renderLoading(container);
  try {
    const [screener, trend, status] = await Promise.all([
      MMApi.get('/api/screener'),
      MMApi.get('/api/screener/trend?weeks=12'),
      MMApi.get('/api/status'),
    ]);
    // Render masthead with status.next_scan_at
    document.getElementById('masthead').innerHTML = MMComponents.renderMasthead({
      vol: 'VI', no: status.vol_no || '17',
      date: formatDateDisplay(status.date), // '22 Apr 2026'
      next_scan: status.next_run_display || 'Sat 09:00'
    });
    document.getElementById('mast-nav').innerHTML = MMComponents.renderMastNav('home');
    // Then render summary strip, trend chart, chips, grid
    container.innerHTML = buildHomeHtml(screener, trend);
    mountTrendChart(trend);
    wireChips(screener);
  } catch (e) {
    MMComponents.renderError(container, e.message);
  }
}
function formatDateDisplay(iso) {
  // '2026-04-22' → '22 Apr 2026'
  const [y,m,d] = iso.split('-');
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  return `${parseInt(d,10)} ${months[parseInt(m,10)-1]} ${y}`;
}
```

## Phase 2: Full Report page (desktop)
- [x] Port `projects/MaxMahon/web-v6-mockup/desktop/02-report.html` to `projects/MaxMahon/web/v6/desktop/report.html` + `projects/MaxMahon/web/v6/static/js/pages/report.js` with route param (symbol from URL `/report/BBL.BK`). Module exports `mount(container)` that reads symbol from URL. Fetch in parallel: GET /api/stock/{sym}, GET /api/stock/{sym}/patterns, GET /api/stock/{sym}/history, GET /api/watchlist/{sym}/exit-status (swallow 404 if not in watchlist). Render all 10 sections per mockup: (1) Article head with symbol + name + sector + signal chips, (2) The Case narrative placeholder (filled only when analysis endpoint returns data; show 'Generate' state otherwise), (3) Score breakdown donut chart (Chart.js doughnut) + table, (4) Niwes 5-5-5-5 checklist 6 rows, (5) Reasons grid 9 numbered bullets from `reasons_narrative`, (6) Case study pattern narrative from patterns endpoint, (7) Key numbers 5y table from `five_year_history`, (8) Dividend history 10y bar chart (Chart.js bar) + table from `dividend_history_10y`, (9) Score history 12w line chart (Chart.js line) from /api/stock/{sym}/history + table with Δ column, (10) Exit baseline 5-trigger table from `/exit-status.trigger_rules` + narrative + entry_context cells. Then Deep Analyze button. Data format: dates display as '15 Feb 2025'. Scope: desktop layout. Acceptance: visual match mockup 100%; all data fields populated from API; no hardcoded samples; no console errors.
- [x] Implement Deep Analyze button + polling logic in report.js: button click → POST /api/stock/{sym}/analyze (fire-and-forget, show 'Pending · est. 45 seconds' pulse state). Start polling every 5s via GET /api/stock/{sym}/analysis (Karl decision). On first successful response with narrative, render into section 2 'The Case' block (4-paragraph byline + pull quote) + stop polling. If poll reaches 90s without result, show error + retry button. Scope: one button with state machine (idle → pending → done/error). Acceptance: clicking button triggers POST, polls GET every 5s, swaps content on success, times out at 90s.

### Reference
```javascript
// pages/report.js polling logic
function startDeepAnalyze(sym) {
  const btn = document.getElementById('deep-analyze-btn');
  btn.textContent = 'Pending · est. 45 seconds';
  btn.disabled = true;
  MMApi.post(`/api/stock/${sym}/analyze`, {}).catch(console.error);
  let elapsed = 0;
  const handle = setInterval(async () => {
    elapsed += 5;
    try {
      const r = await MMApi.get(`/api/stock/${sym}/analysis`);
      if (r && r.narrative) {
        clearInterval(handle);
        renderTheCase(r.narrative);
        btn.textContent = 'Deep Analyzed ✓';
      }
    } catch (e) { /* 404 = still pending */ }
    if (elapsed >= 90) {
      clearInterval(handle);
      btn.textContent = 'Retry Deep Analyze';
      btn.disabled = false;
    }
  }, 5000);
}
```

## Phase 3: Home page (mobile)
- [x] Port `projects/MaxMahon/web-v6-mockup/mobile/01-home.html` to `projects/MaxMahon/web/v6/mobile/home.html` + use shared `pages/home.js` logic. Mobile layout: single column, bottom nav instead of top nav (rendered via mobile index.html shell from Plan 03), cards stacked full-width, summary strip reduced to 4 cells (scanned/passed/avg yield/top score per mockup), trend chart smaller height. Scope: mobile variant; reuse home.js mount() which detects viewport via `MMDevice.isMobile()` and branches HTML accordingly. Acceptance: visual match `web-v6-mockup/mobile/01-home.html` 100%; data populated; bottom nav visible + active state correct.

## Phase 4: Full Report page (mobile)
- [x] Port `projects/MaxMahon/web-v6-mockup/mobile/02-report.html` to `projects/MaxMahon/web/v6/mobile/report.html` + extend `pages/report.js` with mobile branch. Mobile layout: single column, charts sized for portrait (smaller height, horizontal scroll for wide tables OR stacked key-value lists instead of tables), section numbers smaller. Scope: mobile variant of all 10 sections. Acceptance: visual match `web-v6-mockup/mobile/02-report.html` 100%; all 10 sections render; Deep Analyze button works same as desktop.
