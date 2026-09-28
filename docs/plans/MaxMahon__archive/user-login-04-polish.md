---
project: MaxMahon
created: 2026-04-29
last_updated: 2026-04-29
status: done
---

## Target / Goal
ทำได้: admin (อาร์ท) ทำงานครบ flow (login → home → watchlist → settings edit + save → logout). Viewer (เมีย) ทำงานครบ flow (login → home → watchlist เปล่า → settings ดูได้แก้ไม่ได้ → logout). curl POST `/api/settings` + admin endpoints ด้วย viewer JWT → 403. CLAUDE.md ของ MaxMahon updated.

# User Login — End-to-end Test + Docs

> Part 4 of 4 — End-to-end manual test ทั้ง 2 user role + update project CLAUDE.md ให้สะท้อน auth flow + per-user data layout. ใช้ checklist verify ก่อน close งาน. **Scope:** ห้ามแก้ code ใหม่ — ทั้ง plan = test + docs only.
> Index: user-login-index
> Depends on: user-login-03-frontend (frontend + backend ครบแล้ว)
> Parallel-safe with: none (final gate)

## Phase 1: E2E manual test
- [x] Test admin (อาร์ท) flow end-to-end. Steps: (1) เปิด `https://max.intensivetrader.com/` (or localhost:50089) ไม่มี session → ควร redirect `/login`. (2) Click Sign in with Google → Google consent → return → ควร redirect `/`. (3) Header แสดง user badge สีเขียว 'อาร์ท Admin'. (4) คลิก Latest Scan → screener load. (5) คลิก Watchlist → ของอาร์ท (after migration ของ Plan 02). (6) คลิก Settings → role banner 'Admin mode' + Operations panel เห็น + ปรับ slider Min Yield → Save → toast 'Saved'. (7) คลิก user badge → dropdown → Logout → redirect `/login`. Scope: test only — ห้ามแก้ code. Acceptance: ทุก step pass; ไม่มี error ใน console; settings save → reload settings → ค่าใหม่ persist.
- [x] Test viewer (เมีย) flow end-to-end. Steps: (1) เปิด browser private window `https://max.intensivetrader.com/` → redirect `/login`. (2) Sign in ด้วย Google account ของเมีย → return → redirect `/`. (3) Header แสดง user badge สีม่วง 'น้องเมีย Viewer'. (4) คลิก Latest Scan → screener load (เห็นเหมือน admin). (5) คลิก Watchlist → เปล่า (เมียยังไม่ได้เพิ่มหุ้น). กดดาว ⭐ บนหุ้น → เพิ่ม watchlist ของเมียได้. (6) คลิก Settings → banner สีน้ำเงิน 'Viewer mode' + Operations panel ซ่อน + slider drag ไม่ได้ + Save button หาย. (7) ดึง viewer JWT จาก browser: F12 → Application → Local Storage → key `sb-zmscqylztzvzeyxwamzp-auth-token` → copy value field `access_token`. (8) curl test ใน terminal: `curl -H "Authorization: Bearer <viewer-jwt>" -X POST https://max.intensivetrader.com/api/settings -d '{}' -H 'Content-Type: application/json'` → 403; `curl -H "Authorization: Bearer <viewer-jwt>" -X POST https://max.intensivetrader.com/api/admin/scan/trigger` → 403. (9) Logout. Scope: test only. Acceptance: ทุก step pass; viewer watchlist isolated จาก admin; curl ทั้ง 2 endpoint return HTTP 403.
- [x] Cross-isolation check + cron aggregate. Steps: (1) admin login → add 'PTT.BK' ลง watchlist. (2) Logout. (3) viewer login → ตรวจ watchlist → ห้ามเห็น PTT.BK. (4) viewer add 'BBL.BK'. (5) Logout. (6) admin login → ตรวจ watchlist → ห้ามเห็น BBL.BK. (7) ตรวจไฟล์ filesystem: `ls projects/MaxMahon/data/users/` ควรมี 2 folders (UUID admin + viewer) — แต่ละ folder มี `user_data.json` แยก. (8) Trigger daily price refresh: เปิด server log (stdout ของ `max-server.bat` หรือ uvicorn output) → กดปุ่ม 'รีเฟรชราคาตอนนี้' ใน admin settings → log ควร print 'refreshing N symbols' โดย N รวม PTT.BK + BBL.BK + duplicates removed. Scope: test + filesystem inspection only. Acceptance: per-user isolation ครบ; 2 folders ใน data/users/; cron log แสดง count = union (no dup).

## Phase 2: Update project docs
- [x] Update `projects/MaxMahon/CLAUDE.md` Architecture section. เพิ่ม sub-section 'Auth + User System': Supabase Hub Google OAuth, JWT verify ผ่าน `server/auth.py` + PyJWT HS256, whitelist email→role จาก env `MAXMAHON_ALLOWED_USERS`, `/api/me` endpoint, `require_admin` dep on settings + admin endpoints. เพิ่ม sub-section 'Per-User Data': layout `data/users/{user_id}/user_data.json`, helper `scripts/user_data_io.py`, cron aggregate via `aggregate_watchlists()`. Update 'Server' section: ลบ MAX_TOKEN reference (legacy), เพิ่ม `SUPABASE_HUB_JWT_SECRET` + `SUPABASE_HUB_ANON_KEY` + `MAXMAHON_ALLOWED_USERS`. เพิ่ม HTML routes `/login` + `/m/login`. Update 'User Data' section path. **Scope:** เฉพาะ `projects/MaxMahon/CLAUDE.md` — **ห้ามแตะ root `C:/WORKSPACE/.claude/CLAUDE.md` หรือ `MEMORY.md`** (ส่วนนั้น /done จัดการ). Acceptance: ไฟล์ updated; section auth + per-user data ครบ; old `MAX_TOKEN` mention หายหมด.
