---
project: maxmahon
created: 2026-04-22
last_updated: 2026-04-23
status: done
---

# MaxMahon v6 · Integration, QA & Deploy

> Part 9 of 9 — E2E smoke, scheduler verification, docs, Cloudflare tunnel check, changelog | Index: maxmahon-v6-index
> Depends on: 04, 05, 06, 07, 08
> Parallel-safe with: none

## Phase 1: APScheduler verification
- [x] Via v6 Settings page: set schedule to Saturday 09:00 (toggle on + day=sat + hour=09 + minute=00) + Save. Scope: use UI, not direct config edit. Acceptance: POST /api/settings returns 200 with next_run_at containing next Saturday 09:00; config.json on disk reflects new schedule.
- [x] Confirm scheduler job registered: call GET /api/admin/scan/trigger OR inspect server logs to verify APScheduler has a cron job with trigger 'cron(day_of_week=sat, hour=9, minute=0)' AND next_run_time is future. Scope: read-only verification. Acceptance: server log or scheduler inspect confirms one active cron job matching settings.
- [x] Trigger scan manually via POST /api/admin/scan/trigger (admin namespace per Plan 02 Phase 4). Watch SSE /api/admin/events for pipeline progress. Scope: one manual run. Acceptance: pipeline completes; new snapshot_{today}.json + screener_{today}.json written; /api/history/v2 scan count increments by 1.

## Phase 2: E2E smoke across 12 views
- [x] Open and verify 5 desktop pages: GET / (home), /report/BBL.BK (full report), /watchlist, /portfolio, /simulator, /settings. For each: data populated from API (no 'undefined' / no placeholder text), Chart.js charts render, modals open + close, sort/filter chips work, no console errors. Scope: visual + console inspection on localhost:50089. Acceptance: all 6 desktop pages load + interact without errors.
- [x] Open and verify 5 mobile pages on mobile viewport (Chrome DevTools device emulation, iPhone 14 Pro profile): GET /m (home), /m/report/BBL.BK, /m/watchlist, /m/portfolio, /m/simulator, /m/settings. Verify: bottom nav visible + active state correct, content stacked single-column, modals render as bottom-sheet. Scope: visual + interaction. Acceptance: all 6 mobile pages load + interact without errors.
- [x] Verify device redirect: visit / on mobile viewport → redirects to /m; visit /m on desktop viewport → redirects to /. Scope: 2 redirect flows. Acceptance: both redirects fire once on load; no infinite loop.
- [x] Verify 12 total views pass zero-error criteria: 6 desktop + 6 mobile. Scope: consolidate checklist. Acceptance: checklist complete; all green.

## Phase 3: Cloudflare tunnel + production routing
- [x] Verify `max.intensivetrader.com` (public URL via Cloudflare Tunnel) serves v6 frontend: open in browser, confirm masthead shows 'Max Mahon' with vintage newspaper styling (cream bg + ink text + oxblood accents). Scope: smoke test on production URL. Acceptance: page loads, no 502, masthead visible; DevTools Network tab shows /static/v6/* assets with 200.
- [x] Test mobile redirect on production: open max.intensivetrader.com on actual phone OR via Chrome DevTools mobile emulation pointing at production → should redirect to max.intensivetrader.com/m. Scope: one redirect test. Acceptance: redirect works on production same as local.
- [x] Verify /api/* endpoints respond on production (GET /api/status, /api/screener, /api/history/v2 with MAX_TOKEN Bearer) return 200 with expected JSON. Scope: 3 curl calls. Acceptance: all 3 return 200.

## Phase 4: Documentation
- [x] Update `projects/MaxMahon/CHANGELOG.md` — prepend v6.0.0 entry (date 2026-04-22 or ship date). Include: major sections (Breaking: v5 archive, Added: vintage newspaper frontend, Added: 6 new endpoints, Modified: 9 existing endpoints with additive fields, Moved: 8 endpoints to /api/admin/*, Removed: /api/exit_check, /api/user/lists/*, ENERGY_CYCLICAL_EXIT anti-rule). Scope: one entry at top of file. Acceptance: CHANGELOG.md has v6.0.0 header with at least 5 sub-sections.
- [x] Update `projects/MaxMahon/CLAUDE.md` Architecture section: reference web/v6/desktop + web/v6/mobile instead of web/; remove run_scan.py from Key Files (already done in Plan 01 Phase 4 but verify); add admin.py to server structure note; update Scoring version + signal tag summary if any changed. Scope: additive + corrections only. Acceptance: CLAUDE.md reflects v6 structure accurately.
- [x] Update `projects/MaxMahon/README.md` quickstart: new URL + start commands, mention /m mobile route, link to CHANGELOG v6. Scope: quickstart section only. Acceptance: README quickstart gets a visitor from zero to running v6 server in under 2 minutes.

## Phase 5: Final commit + tag + submodule push
- [x] Commit all v6 work in MaxMahon submodule: `git -C projects/MaxMahon add -A && git -C projects/MaxMahon commit -m "v6.0.0 — vintage newspaper redesign: 6 new endpoints, 9 modified, admin namespace, web/v6 frontend"`. Scope: one final commit for any remaining staging. Acceptance: commit created; `git -C projects/MaxMahon status` clean.
- [x] Tag v6.0.0 in MaxMahon submodule: `git -C projects/MaxMahon tag -a v6.0.0 -m "v6.0.0 — vintage newspaper redesign"`. Scope: one annotated tag. Acceptance: `git -C projects/MaxMahon tag` shows v6.0.0.
- [x] Push MaxMahon submodule: `git -C projects/MaxMahon push origin main --tags`. Scope: push branch + tag. Acceptance: GitHub shows v6.0.0 tag + latest commit on main.
- [x] Update parent WORKSPACE submodule pointer: `git add projects/MaxMahon && git commit -m "submodule: MaxMahon v6.0.0 — vintage newspaper redesign" && git push`. Scope: bump submodule pointer in parent repo. Acceptance: `git -C . status` clean; `git log --oneline -1` shows submodule bump.
- [x] Verify production deploy: after Cloudflare cache warmup (within 5 min), `max.intensivetrader.com` serves v6 (check masthead). Scope: post-push smoke. Acceptance: production serves v6 — confirmed in Phase 3 already, re-verify post-push.
