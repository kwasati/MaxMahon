---
project: MaxMahon
created: 2026-04-24
last_updated: 2026-04-24
status: done
---

# Report Page Restructure — Index

> Index of 3 child plans — restructure /report/{sym} page: remove 3 duplicates (The Case vs Max-to-อาร์ท, Reasons vs 5-5-5-5, Pattern vs Hidden Audit), migrate vintage newspaper → Robinhood dark, desktop layout for Deep Analyze (2x2 grid + full-width Max-to-อาร์ท panel), fix broken CSS (.section-num + .checklist-item), re-order sections (hero → Deep Analyze money-shot → Score → enriched checklist → Key Numbers → Dividend → History → Exit → Pattern footnote).
> Depends on: none
> Parallel-safe with: none

## Phase 1: Foundation (infrastructure, no UI change)
- [x] /build report-restructure-01-foundation — backend expose verdict+analyzed_at, port mockup CSS classes to components.css, SVG icon helper — Acceptance: /api/stock/QH.BK returns narrative.verdict field, new CSS classes available in DevTools, MMUtils.svg('banknote') returns valid SVG

## Phase 2: Desktop Restructure (report.js)
- [x] /build report-restructure-02-desktop — 8 tasks in 4 phases: (a) hero redesign + move Deep Analyze up, (b) remove duplicates (The Case, Reasons, Pattern section), (c) vintage cleanup + section reorder, (d) smoke test — Acceptance: no duplicate content on page, Deep Analyze full-width desktop, verdict chip in hero, 5-5-5-5 rendered as 5-col grid, no emoji icons, no 'By Max Mahon' byline, Pattern as <details> footnote at end

## Phase 3: Mobile Port (report.mobile.js)
- [x] /build report-restructure-03-mobile — 5 tasks in 3 phases: mirror desktop changes to report.mobile.js + mobile 1-col responsive + smoke test at 375px — Acceptance: mobile report matches desktop structure + no horizontal scroll at 375px + Deep Analyze stacks 1-col + bottom-nav clearance preserved
