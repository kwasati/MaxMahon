---
project: MaxMahon
created: 2026-04-29
last_updated: 2026-04-29
status: done
---

## Target / Goal
ทำได้: เปิด `projects/MaxMahon/scripts/auth_smoke_test.html` → กด Sign in with Google → กลับมา → console พิมพ์ valid JWT (3 segments) + decoded payload (อ่าน `aud`, `sub`, `email` ได้). `.env` มี `SUPABASE_HUB_JWT_SECRET` + `SUPABASE_HUB_ANON_KEY` + `MAXMAHON_ALLOWED_USERS` ครบ.

# User Login — Supabase OAuth + Env Setup

> Part 1 of 4 — Supabase Google OAuth + JWT secret + email whitelist. ไม่แตะ code ของ MaxMahon backend/frontend เลย — แค่ infra setup ก่อน Plan 02 + 03 จะเริ่ม.
> Index: user-login-index
> Depends on: none
> Parallel-safe with: none (foundation gate — Plans 02-04 ต้องรอ)

## Phase 1: Supabase Dashboard config
- [x] Configure Google OAuth provider in Supabase Hub Dashboard. Path: Supabase Dashboard (project `zmscqylztzvzeyxwamzp`) → Authentication → Providers → Google → toggle Enable. ใส่ Google Cloud Console OAuth 2.0 Client ID + Secret (สร้างใหม่ที่ Google Cloud Console → APIs & Services → Credentials → Create OAuth client ID → Web application; Authorized redirect URIs: `https://zmscqylztzvzeyxwamzp.supabase.co/auth/v1/callback`). Save provider config. Scope: ห้ามแตะ provider อื่น. Acceptance: provider toggle = Enabled in dashboard, ไม่มี warning banner.
- [x] Configure Site URL + Redirect URLs in Supabase Dashboard. Path: Supabase Dashboard → Authentication → URL Configuration. Site URL: `https://max.intensivetrader.com`. Additional Redirect URLs (4 entries): `https://max.intensivetrader.com/login`, `https://max.intensivetrader.com/m/login`, `http://localhost:50089/login`, `http://localhost:50089/m/login`. Scope: ห้ามแตะ JWT settings. Acceptance: ทั้ง 4 URL ปรากฏใน Redirect URLs list.

## Phase 2: Env vars
- [x] Add `SUPABASE_HUB_JWT_SECRET` to root `.env` (`C:/WORKSPACE/.env`). Path ดึง: Supabase Dashboard → Settings → API → JWT Settings → JWT Secret (HS256 key). Scope: ห้ามแตะ key อื่นใน `.env`. Acceptance: `py -c "import os, dotenv; dotenv.load_dotenv(); print(len(os.environ['SUPABASE_HUB_JWT_SECRET']) > 30)"` → True.
- [x] Add `SUPABASE_HUB_ANON_KEY` to root `.env` (ถ้ายังไม่มี). Path ดึง: Supabase Dashboard → Settings → API → Project API keys → `anon` `public` key (long JWT-looking string). Public-safe (ฝัง client ได้). Scope: เฉพาะ key นี้. Acceptance: `py -c "import os, dotenv; dotenv.load_dotenv(); print(os.environ['SUPABASE_HUB_ANON_KEY'].startswith('eyJ'))"` → True.
- [x] Add `MAXMAHON_ALLOWED_USERS` JSON env to `.env`. Value = JSON array ของ 2 users: `[{"email":"kwasati@gmail.com","role":"admin","name":"อาร์ท"},{"email":"<wife-email-อาร์ทกรอกเอง>","role":"viewer","name":"น้องเมีย"}]`. NOTE: ก่อน build Plan 02 อาร์ทต้องใส่ email เมียจริงแทน placeholder. Scope: ใส่ใน `.env` เท่านั้น (ห้าม commit). Acceptance: `py -c "import os, json, dotenv; dotenv.load_dotenv(); u=json.loads(os.environ['MAXMAHON_ALLOWED_USERS']); print(len(u)==2 and u[0]['role']=='admin')"` → True.

## Phase 3: Smoke test + runbook
- [x] สร้าง `projects/MaxMahon/scripts/auth_smoke_test.html` — standalone HTML ที่ใช้ Supabase JS client (CDN `@supabase/supabase-js@2.45.0` — pin version) + ปุ่ม Sign in with Google + แสดง JWT + decoded payload ใน console หลัง redirect กลับ. ใส่ Supabase URL + ANON_KEY hardcoded จาก Plan 01 Phase 2 Task 2 (anon key public-safe). Decode payload: `JSON.parse(atob(token.split('.')[1]))` → console.log `{aud, sub, email, exp}`. Scope: ไฟล์เดียว ไม่แตะ web/v6/. Acceptance: เปิดไฟล์ใน browser → click Sign in → Google consent → return → console แสดง: (1) `access_token` length > 100, (2) decoded payload object ที่มี `aud='authenticated'`, `sub=<uuid>`, `email='kwasati@gmail.com'`. ถ้า `aud` ไม่ใช่ 'authenticated' → flag ให้แก้ Plan 02 ก่อน build.
- [x] สร้าง runbook `projects/MaxMahon/docs/auth-setup.md` — บันทึก step-by-step: (1) Google Cloud Console OAuth client setup, (2) Supabase Dashboard provider + URL config, (3) JWT secret extraction (Settings → API → JWT Settings → JWT Secret), (4) Anon key extraction (Settings → API → Project API keys → anon public), (5) `MAXMAHON_ALLOWED_USERS` format + how to add new user, (6) JWT secret rotation procedure, (7) วิธีหา user UUID ของอาร์ทหลัง login ครั้งแรก (Dashboard → Authentication → Users → click email → copy UUID — สำหรับ Plan 02 migration). Scope: markdown only. Acceptance: ไฟล์ exist + step ครบ 7 ข้อ + ทดสอบตามได้จริง.
