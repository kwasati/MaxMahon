---
project: MaxMahon
created: 2026-04-29
last_updated: 2026-04-29
status: done
---

## Target / Goal
ทำได้: 2 user (อาร์ท admin + เมีย viewer) login ด้วย Google ผ่าน Supabase Hub → เห็น watchlist + portfolio ของตัวเอง / viewer ดู settings ได้แต่แก้ไม่ได้ / admin endpoint return 403 ถ้าไม่ใช่ admin

# User Login System — Master Plan

> Master plan สำหรับ user login + role + per-user data isolation. Mockup approved 7 scenes ที่ `projects/MaxMahon/web/v6/mockup/user-login-system.html`. แตก 4 sub-plans ตาม dependency: Foundation → Backend → Frontend → Polish. Sequential — frontend ต้องการ backend session verify ก่อน.
> Depends on: none
> Parallel-safe with: none (each sub-plan blocks the next)

## Phase 1: Foundation — Supabase OAuth + env
- [x] /build user-login-01-supabase — 5 tasks: configure Google OAuth provider in Supabase Hub Dashboard + add Site/Redirect URLs + add `SUPABASE_HUB_JWT_SECRET` + `MAXMAHON_ALLOWED_USERS` to `.env` + smoke-test HTML at `projects/MaxMahon/scripts/auth_smoke_test.html` + runbook `projects/MaxMahon/docs/auth-setup.md`. Acceptance: open smoke-test → click Sign in → return → console shows valid JWT + Karl email

## Phase 2: Backend — auth middleware + per-user data
- [x] /build user-login-02-backend — 8 tasks: create `server/auth.py` (JWT verify + role lookup) + add PyJWT dep + `/api/me` endpoint + `require_admin` dep on `POST /api/settings` + all `/api/admin/*` + create `scripts/user_data_io.py` (per-user JSON helper) + refactor `/api/watchlist*`, `/api/portfolio/builder*`, `/api/user` to use authenticated user_id + migration script `scripts/migrate_to_per_user.py` (move legacy `user_data.json` → `data/users/{karl-id}/user_data.json`) + update `scripts/daily_price_refresh.py` to aggregate watchlists across all user folders. Acceptance: viewer JWT → `POST /api/settings` returns 403; admin JWT → 200; `GET /api/me` returns `{user_id, email, name, role}`; per-user file isolated

## Phase 3: Frontend — login + role-based UI
- [x] /build user-login-03-frontend — 8 tasks: add Supabase JS client + wrapper `web/v6/static/js/supabase-client.js` + create `pages/login.js` + `pages/login.mobile.js` + add `/login` + `/m/login` HTML routes + update `api.js` (Supabase JWT Bearer instead of MAX_TOKEN) + auth guard in shell boot + update `components.js renderMastNav` (user badge + dropdown) + update `pages/settings.js` + `settings.mobile.js` (fetch `/api/me` → role banner + conditional wire + hide Save/Operations for viewer) + add CSS for user-badge + role-banner + read-only state. Acceptance: open `/` without session → redirect `/login`; admin sees full settings + Save; viewer sees read-only banner + no Save button + no Operations panel; UI matches mockup

## Phase 4: Polish — E2E test + docs
- [x] /build user-login-04-polish — 3 tasks: E2E test admin flow (Karl) + E2E test viewer flow (เมีย) + update `projects/MaxMahon/CLAUDE.md` Architecture section (auth flow + per-user data layout + role rules). Acceptance: both flows pass manual checklist; viewer curl POST /api/settings returns 403; viewer curl POST /api/admin/scan/trigger returns 403; CLAUDE.md updated
