---
project: maxmahon
created: 2026-04-22
last_updated: 2026-04-23
status: done
---

# MaxMahon v6 Redesign — Master Plan

> Master index for MaxMahon v6 redesign. Backend cleanup + frontend rewrite to match vintage newspaper mockup 100%.
> Build order: 01 → 02 → 03 → (04, 05, 06, 07, 08 parallel-safe) → 09
> Depends on: none (orchestrator). Parallel-safe with: none.

## Phase 1: Foundation (sequential — must complete in order)
- [x] /build maxmahon-v6-01-cleanup — backend cleanup, archive legacy, unify pipeline, fresh scan. Scope: no frontend changes. Acceptance: v5 archive folder in place, dead code removed, fresh scan outputs new snapshot/screener/history files, 3 deprecated endpoints removed.
- [x] /build maxmahon-v6-02-api — modify 9 endpoints + add 6 new endpoints + align schemas + admin namespace. Scope: no frontend wiring. Acceptance: all endpoints return documented shape with new fields, /api/simulate/portfolio-backtest returns 7 result cards + 3-line timeline, static routing serves web/v6/ placeholder OK.
- [x] /build maxmahon-v6-03-frontend-foundation — scaffold web/v6/, tokens, base.css, shared components, device detect, API client. Scope: no page-specific logic. Acceptance: web/v6/desktop + mobile + shared + static folders exist, tokens match mockup, base.css matches mockup, device detection redirects correctly.

### Reference
```
Build order rule: each /build must complete (merge + QC pass) before the next is invoked. Index plan acts as the orchestrator — it invokes sub-plan /build commands automatically per the build skill spec.
```

## Phase 2: Page implementation (parallel-safe — any order)
- [x] /build maxmahon-v6-04-frontend-home-report — home card grid + full report 10 sections, desktop + mobile. Parallel-safe with 05, 06, 07, 08. Acceptance: /home and /report/{sym} visually match mockup 100%, data populated from API, no hardcoded samples, no console errors.
- [x] /build maxmahon-v6-05-frontend-watchlist — watchlist table + compare modal + add-by-symbol flow, desktop + mobile. Parallel-safe with 04, 06, 07, 08. Acceptance: /watchlist visually matches mockup, compare modal up to 3 symbols works, add-by-symbol flow works, inline note edit persists.
- [x] /build maxmahon-v6-06-frontend-portfolio — portfolio real + simulated sections, desktop + mobile. Parallel-safe with 04, 05, 07, 08. Acceptance: /portfolio matches mockup, add/delete transaction works, simulated allocation save/load works.
- [x] /build maxmahon-v6-07-frontend-simulator — 3 tabs (DCA single / DCA portfolio / portfolio backtest with TDEX benchmark), desktop + mobile. Parallel-safe with 04, 05, 06, 08. Acceptance: all 3 tabs visually match mockup Tab 3 portfolio backtest renders 7 cards + 3-line chart + yearly table + assumptions paragraph.
- [x] /build maxmahon-v6-08-frontend-settings — auto scan + Niwes thresholds + universe selector, desktop + mobile. Parallel-safe with 04, 05, 06, 07. Acceptance: /settings matches mockup, save POST /api/settings works, last-saved timestamp renders after save, universe radio switches set_only/set_mai.

## Phase 3: Integration & deploy (sequential — after all pages ship)
- [x] /build maxmahon-v6-09-integration — E2E smoke across 12 views, APScheduler verification, Cloudflare tunnel check, docs update, final tag v6.0.0. Depends on: 04, 05, 06, 07, 08. Acceptance: all 12 pages load without errors, schedule job registers, max.intensivetrader.com serves v6, CHANGELOG + CLAUDE.md + README updated, submodule pointer pushed.
