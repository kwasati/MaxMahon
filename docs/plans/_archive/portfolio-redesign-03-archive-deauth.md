---
project: 4-MaxMahon
created: 2026-06-08
last_updated: 2026-06-25
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: เว็บเหลือแต่หน้าพอร์ตใหม่ (หน้า scan/watchlist/จัดพอร์ตเดิม/settings เก็บเข้ากรุ ไม่โผล่ใน nav) ; login Google ยังกันคนนอกได้ แต่ไม่มี role เมีย เหลือ user เดียว ; backend pipeline หลังบ้านยังรันได้ตามเดิม

### รายละเอียด
- archive page module เดิม: home.js, watchlist.js, report.js(เก็บถ้ายังลิงก์ดู research), portfolio.js(จัดพอร์ตเดิม 80/20), settings.js + คู่ .mobile.js -> ย้ายไป web/v6/static/js/pages/_archive/ หรือ mark ไม่ใช้
- report เดิม: ถ้า plan 02 ใช้ /report/{sym} ดู research เต็ม = เก็บไว้ (ไม่ archive) ; ตัวอื่น archive
- routes เดิมใน app.py (/watchlist /portfolio /settings + /m/*) -> redirect ไป '/' หรือลบ — scope: เก็บ /report/{sym} ถ้า 02 ใช้
- single-user: ตัด role gate — require_admin (auth.py:174) ที่ /api/settings + /api/admin/* ไม่ต้องแยก role (user เดียว = admin โดยปริยาย) ; whitelist MAXMAHON_ALLOWED_USERS เหลือ 1 email (อาร์ท) ตัด role viewer
- เก็บ get_current_user (auth.py:97) + Supabase login ไว้ (กันคนนอก) — ไม่ rip auth
- ลบ/archive login เฉพาะถ้าตัด login จริง — แต่ default = เก็บ login ไว้ (ตาม goal กันคนนอก) เพราะงั้น login.js เก็บ
- nav cleanup: เอา tab ที่ชี้หน้า archived ออก (ทำใน plan 02 แล้วบางส่วน — plan นี้เก็บตกที่เหลือ)

### Scope Boundary
**In scope:**
- web/v6/static/js/pages/_archive/ (ย้าย module เดิมที่ไม่ใช้)
- server/app.py — routes เดิม redirect/ลบ (2930-2989) + ตัด require_admin role logic
- auth.py — simplify role (174) เหลือ single-user
- .env / config — MAXMAHON_ALLOWED_USERS เหลือ 1 email (doc instruction ไม่ commit secret)

**Out of scope:**
- หน้าพอร์ตใหม่ (plan 02 เสร็จแล้ว)
- backend pipeline (scan/price/dividend — ไม่แตะ ยังรัน)
- API /api/portfolio/* (plan 01)

### Non-goals
- ไม่ rip auth/Supabase ทิ้ง (เก็บ login กันคนนอก)
- ไม่ลบ backend script ที่ pipeline ใช้ (scan/screen/fetch ยังรัน weekly)
- ไม่ลบไฟล์ทิ้งถาวร (archive = ย้าย/mark กู้คืนได้)

### Skill Flow
- /build -> /qc -> /done

### Stop Conditions
- route เดิมถูกเรียกจากที่อื่น (deep link/bookmark) -> ยืนยัน redirect ปลายทางก่อนลบ
- require_admin ผูกกับ endpoint ที่ยังต้องใช้ -> ยืนยันว่า single-user ใช้ได้ ไม่พัง
- archive module แล้ว shell import ไม่เจอ -> ต้องแก้ route mapping ให้ไม่ชี้ module ที่ย้าย

### Report-Back Contract
- verdict
- files touched
- เว็บเหลือหน้าพอร์ตอย่างเดียวไหม
- login ยังกันคนนอกได้ไหม
- backend pipeline ยังรันได้ไหม
- unresolved

# Portfolio Redesign 03 — เก็บกวาดเว็บเดิม + single-user

> Part 3 of 4 — เก็บกวาด: archive เว็บเดิม + ตัด role เหลือ single-user (เก็บ login) | Index: portfolio-redesign-index
> Depends on: portfolio-redesign-02-frontend (หน้าใหม่ต้องใช้ได้ก่อน archive ของเดิม)
> Parallel-safe with: none

## Phase 1: Archive page modules เดิม
- [x] ย้าย web/v6/static/js/pages/{home,watchlist,portfolio,settings}.js + .mobile.js ไป pages/_archive/ — scope: เก็บ report.js + report.mobile.js ถ้า plan 02 ใช้ดู research ; เก็บ login.js — Acceptance: หน้าพอร์ตใหม่ยังโหลดได้, ไม่มี import ชี้ module ที่ย้าย (เช็ค shell route mapping)
- [x] ปรับ shell route mapping ให้ route ที่ archive แล้ว fallback ไป '/' (desktop/index.html + mobile/index.html) — Acceptance: เปิด /watchlist เดิม -> เด้ง/แสดงหน้าพอร์ต ไม่ error module not found

### Reference
# shell loader: desktop/index.html:91 import('/static/v6/js/pages/'+route+'.js')
# ถ้า route ไม่มี module -> ต้อง catch + fallback '/' (เช็ค error handling เดิมใน boot script)
# pages เดิม: home/watchlist/report/portfolio/settings/login (.js + .mobile.js) = 12 ไฟล์

## Phase 2: Routes redirect + nav cleanup
- [x] แก้ server/app.py routes เดิม (/watchlist /portfolio /settings + /m/*) ให้ redirect '/' หรือ serve shell แล้วให้ client fallback — scope: เก็บ /report/{sym} (2969-2971) ถ้า 02 ใช้ ; เก็บ / และ /m — Acceptance: route เดิมไม่ 404, ไม่โชว์หน้าตาย
- [x] เก็บตก nav ใน components.js ถ้ายังเหลือ tab ชี้ archived (plan 02 แก้หลักแล้ว) — Acceptance: nav ไม่มีลิงก์ไปหน้า archived

### Reference
# app.py HTML routes (2960-2989): GET / +/home +/watchlist +/settings +/login -> _V6_DESKTOP ; /report/{sym} 2969-2971 ; /portfolio 2930-2937 ; mobile /m/* 2977-2989
# redirect pattern: from fastapi.responses import RedirectResponse ; return RedirectResponse('/')

## Phase 3: Single-user (ตัด role, เก็บ login)
- [x] แก้ server/app.py + auth.py — ตัด role distinction (require_admin -> เทียบเท่า get_current_user สำหรับ single-user) — scope: เก็บ get_current_user + JWT verify + Supabase login (กันคนนอก) ห้าม rip auth — Acceptance: user เดียว login เข้าใช้ทุกหน้าได้ ไม่ติด 403 role ; คนนอก (ไม่อยู่ whitelist) ยังโดน 403
- [x] อัปเดต doc/instruction ว่า MAXMAHON_ALLOWED_USERS เหลือ 1 email ตัด role viewer — scope: ไม่ commit ค่า secret ลง git — Acceptance: doc ระบุ single-user setup ชัด

### Reference
# auth.py: get_current_user (97) verify JWT + whitelist (155-161) -> เก็บ ; require_admin (174) raise 403 if role!=admin -> single-user ไม่ต้อง raise (หรือ map ทุก whitelisted = admin)
# whitelist env MAXMAHON_ALLOWED_USERS (auth.py 54-91) = JSON [{email,name,role}] -> เหลือ 1 entry
# ห้าม rip JWT verify (public tunnel max.intensivetrader.com = ต้องกันคนนอก)
