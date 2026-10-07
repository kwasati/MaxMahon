---
project: maxmahon
created: 2026-04-22
last_updated: 2026-04-23
status: done
---

# MaxMahon v6 · Simulator (DCA + Backtest)

> Part 7 of 9 — 3 tabs DCA single / DCA portfolio / portfolio backtest with SET benchmark, desktop + mobile | Index: maxmahon-v6-index
> Depends on: maxmahon-v6-03-frontend-foundation
> Parallel-safe with: 04, 05, 06, 08

## Phase 1: Tab 1 — DCA รายตัว (Single-stock DCA) desktop
- [x] Create `projects/MaxMahon/web/v6/desktop/simulator.html` + `projects/MaxMahon/web/v6/static/js/pages/simulator.js` with 3 tab structure (Tab 1 / 2 / 3 header strip). Tab 1 inputs: stock dropdown (populated from GET /api/screener candidates — 54+ passed), monthly amount (฿ number input, default 20000), duration years (1-30, default 10), reinvest dividends toggle (default ON). Submit triggers GET `/api/dca/{symbol}?amount={monthly}&backtest_years={duration}&forward_years=0&reinvest={bool}`. Render 4 result cards: Invested (total), Accumulated Value, Shares Held (+ avg cost), Dividends Paid Lifetime (+ YoC %). Render line chart (Chart.js line): x = months, y = accumulated value (filled oxblood area) + invested (dashed ink line). Render narrative paragraph (generated from result figures). Scope: Tab 1 only. Acceptance: visual match `web-v6-mockup/desktop/05-simulator.html` Tab 1 100%; selecting BBL.BK + ฿20k + 15yr + reinvest ON produces chart + 4 cards with non-zero values.

## Phase 2: Tab 2 — DCA ทั้งพอร์ต (Multi-stock DCA) desktop
- [x] Extend `projects/MaxMahon/web/v6/static/js/pages/simulator.js` Tab 2: portfolio row editor (add/remove rows with symbol dropdown + weight % input), must sum to 100% (show error badge if not), monthly amount total input, duration years. Submit → POST /api/simulate/dca-portfolio with body {positions:[{symbol, weight_pct}], monthly_amount, duration_years, reinvest_dividends}. Render 4 result cards (Invested / Ending Value / CAGR / Dividends Lifetime) + line chart (Portfolio Value vs Invested dashed) + per-position table (Position / Weight / Invested / Ending Value / Return % / Div Paid). Scope: Tab 2 only. Acceptance: visual match mockup Tab 2 100%; 5-position portfolio with weights summing to 100 produces results + table with 5 rows + line chart with 2 lines.

## Phase 3: Tab 3 — Portfolio Backtest desktop (CRITICAL — Karl-emphasized)
- [x] Extend `projects/MaxMahon/web/v6/static/js/pages/simulator.js` Tab 3 per mockup: portfolio textarea (SYMBOL WEIGHT per line format, default BBL 20 / TCAP 15 / INTUCH 15 / ADVANC 14 / LH 12 / QH 12 / SCB 8 / Cash 4), start date picker (default 'Jan 2015' display = '2015-01-01' ISO), monthly DCA amount (default ฿10,000), reinvest dividends toggle. Parse textarea → positions[]. On submit: POST /api/simulate/portfolio-backtest with body {positions, start_date, monthly_amount, reinvest_dividends, benchmark:'SET'}. Render 7 result cards per mockup (Row 1: Total Invested / Portfolio Value Today / Total Return % / CAGR %; Row 2: Dividends Received / Max Drawdown % / TDEX Benchmark Value). Render Chart.js line chart with 3 lines: Portfolio (oxblood `var(--oxblood)` solid, filled area), TDEX Benchmark (ink dashed), Cumulative Invested (gray solid). Render yearly breakdown table (Year / Invested YTD / Port Value YTD / Dividends YTD / TDEX YTD). Render assumptions paragraph from response.assumptions block (include benchmark_proxy, costs not modeled, cash_return_rate_pct 0). Scope: Tab 3 — this is the Karl-emphasized critical deliverable. Acceptance: visual match `web-v6-mockup/desktop/05-simulator.html` Tab 3 exactly (side-by-side diff); running with default config shows populated 7 cards + 3-line chart + yearly table + assumptions; benchmark line uses TDEX proxy (fallback ^SET per Plan 02 Phase 3).

### Reference
```javascript
// pages/simulator.js Tab 3 portfolio parse
function parsePortfolioText(text) {
  return text.split('\n').map(line => line.trim()).filter(Boolean).map(line => {
    const parts = line.split(/\s+/);
    const symbol = parts[0];
    const weight_pct = parseFloat(parts[1]);
    if (symbol.toUpperCase() === 'CASH') return { symbol: 'Cash', weight_pct };
    return { symbol: symbol.endsWith('.BK') || symbol === 'Cash' ? symbol : symbol + '.BK', weight_pct };
  });
}

// Chart.js 3-line config
const cfg = {
  type: 'line',
  data: {
    labels: timeline.map(t => t.date),
    datasets: [
      { label: 'Portfolio', data: timeline.map(t => t.portfolio_value), borderColor: 'var(--oxblood)', fill: true, backgroundColor: 'rgba(122,31,43,0.15)' },
      { label: 'TDEX Benchmark', data: timeline.map(t => t.benchmark_value), borderColor: 'var(--ink)', borderDash: [6,4], fill: false },
      { label: 'Cumulative Invested', data: timeline.map(t => t.invested_cumulative), borderColor: '#888', fill: false },
    ],
  },
  options: { plugins: { legend: { display: true, position: 'bottom' } }, scales: { x: { ticks: { maxRotation: 0 } } } },
};
```

## Phase 4: Simulator page (mobile)
- [x] Port `projects/MaxMahon/web-v6-mockup/mobile/05-simulator.html` to `projects/MaxMahon/web/v6/mobile/simulator.html` + extend `pages/simulator.js` mobile branch. Mobile: tab header → dropdown `<select>` mode selector (Karl decision: keep dropdown per mockup), stacked inputs, result cards stacked full-width, chart reduced height, per-position table → stacked cards. Scope: mobile variant of all 3 tabs. Acceptance: visual match mockup 100%; dropdown switches between 3 modes; all 3 modes render correctly on mobile viewport.
