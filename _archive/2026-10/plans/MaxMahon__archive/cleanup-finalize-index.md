---
project: MaxMahon
created: 2026-04-25
last_updated: 2026-04-25
status: done
---

# Cleanup + Finalize — Archive features / Watchlist split / Settings ops panel

> Index of 3 child plans to finalize MaxMahon job: (1) Archive Portfolio + Portfolio Builder + Simulator features (move to _archive/, remove from nav, cleanup endpoints + CSS + data fields). (2) Split Home (latest scan) vs Watchlist (user-starred) — rename nav, add user_in_watchlist field, add ⭐ button on home cards + report hero. (3) Settings — add Operations panel (server status grid + manual scan trigger + manual price refresh) on top of existing config form. NOTE: settings.js is NOT actually empty — มี config form ทำงานอยู่แล้ว (schedule + thresholds + universe + save). 'implement' interpreted as 'add operational controls' (admin actions + status). If interpretation wrong → revise Plan 3 before /build.
> Depends on: none
> Parallel-safe with: none

## Phase 1: Archive Portfolio + Builder + Simulator features
- [x] /build cleanup-finalize-01-archive-features — 8 tasks: move 11 frontend files to _archive/ + delete 7 backend endpoint blocks + delete 3 CSS sections (~700 lines) + clean nav (3 items removed desktop, 2 mobile) + cleanup user_data.json fields. Acceptance: nav has 2 desktop / 3 mobile items remaining; /api/portfolio* + /api/simulate/* return 404; components.css smaller by ~700 lines; no orphan refs in active code

## Phase 2: Watchlist split + Star action
- [x] /build cleanup-finalize-02-watchlist-split — 7 tasks: rename desktop nav 'WATCHLIST' → 'LATEST SCAN' + add real WATCHLIST item to /watchlist + rename mobile 'Screen' → 'WATCHLIST'; backend extends /api/stock/{sym} with user_in_watchlist bool; ⭐ button on home cards (desktop+mobile) wired to PUT /api/user/watchlist; ⭐ button on report hero (desktop+mobile) same wiring. Acceptance: 3-item nav (LATEST SCAN / WATCHLIST / SETTINGS); ⭐ click adds to watchlist + visual toggle without reload; watchlist page shows starred stocks

## Phase 3: Settings — Operations panel
- [x] /build cleanup-finalize-03-settings-ops — 5 tasks: add Operations section (server status 4-cell grid + 2 action buttons) on top of existing config form in settings.js + settings.mobile.js + new CSS classes (.v6-ops-*) in components.css + 5s polling /api/status. Acceptance: Settings page shows Operations panel above Auto Scan config; status grid populates (uptime/last data date/last scan time/pipeline state badge); manual scan button POST /api/admin/scan/trigger + disabled while pipeline_running; manual price refresh button works similarly
