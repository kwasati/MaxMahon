---
project: 4-MaxMahon
created: 2026-06-24
last_updated: 2026-06-24
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: เปิดหน้าพอร์ตเว็บ เห็น 3 tab สลับได้ แต่ละ tab โหลดพอร์ตของตัวเอง (หุ้น+เป้า+holdings อิสระ) ดับเบิลคลิกชื่อ tab เปลี่ยนชื่อได้ และกดปุ่มดึงราคา ครอบ symbol ทุกพอร์ตทีเดียว

### รายละเอียด
- 3 พอร์ต fix id = A/B/C (ไม่มีปุ่มเพิ่ม/ลบ tab)
- พอร์ต A = พอร์ตเดิม (migrate data/portfolio.json -> data/portfolios/A.json ชื่อ 'พอร์ตหลัก')
- B/C seed โครง targets+meta เหมือน A แต่ holdings=0 cash=0 ชื่อ 'พอร์ต 2' / 'พอร์ต 3'
- ชื่อพอร์ตเก็บใน field 'name' ของแต่ละไฟล์ portfolios/{id}.json
- active tab จำใน localStorage ฝั่ง client (key 'mm_active_pf', default A)
- ปุ่มดึงราคา = POST /api/admin/price-refresh/trigger เดิม (ดึง symbol รวมทุกพอร์ต)
- เวลาดึงราคาล่าสุด = newest mtime ใน data/price_cache (field price_as_of เพิ่มใน build_state)
- backend ต้อง merge ก่อน frontend (frontend เรียก ?pf=, rename endpoint, price_as_of)

### Scope Boundary
**In scope:**
- scripts/portfolio_state.py
- server/app.py endpoints /api/portfolio/*
- scripts/daily_price_refresh.py
- scripts/migrate_portfolio_to_separate.py (ใหม่)
- data/portfolios/ (ใหม่)
- web/v6/static/js/pages/portfolio-home.js + portfolio-home.mobile.js
- web/v6/static/css/components.css

**Out of scope:**
- UI เพิ่ม/ลบหุ้นหรือตั้ง target ในพอร์ต (เฟสนี้แก้ผ่านไฟล์ JSON)
- เพิ่ม/ลบจำนวนพอร์ต (fix 3)
- scan pipeline / snapshot / screener

### Non-goals
- ไม่ทำ UI ตั้ง target/เพิ่มหุ้นใหม่ในพอร์ต B/C — เฟสนี้ใช้โครงหุ้นเดียวกับ A ก่อน
- ไม่ทำปุ่มเพิ่ม/ลบ tab (อาร์ทขอ fix 3)
- ไม่แตะ scan pipeline / snapshot / screener เก่า

# Multi-Portfolio 3 พอร์ต + ปุ่มดึงราคา — Index

> Multi-portfolio 3 tab + ปุ่มดึงราคา บนหน้าพอร์ตจริง MaxMahon. Index คุม build order: backend (data+api+price) ก่อน -> frontend (tab+ปุ่ม). mockup approve แล้ว: C:\WORKSPACE\.claude\artifacts\maxmahon-portfolio-3tab-mockup.html

## Phase 1: Backend (data + api + price refresh)
- [x] /build multi-portfolio-01-backend — migrate portfolio.json -> portfolios/A.json + seed B/C, portfolio_state รับ portfolio_id, endpoints รับ ?pf= + list + rename + price_as_of, daily_price_refresh รวม symbol ทุกพอร์ต — Acceptance: ดูใน plan ลูก multi-portfolio-01-backend

## Phase 2: Frontend (tab + ปุ่มดึงราคา) — รอ backend merge
- [x] /build multi-portfolio-02-frontend — tab strip 3 พอร์ต + double-click rename + ปุ่มดึงราคา + state per tab (desktop + mobile + css) ตาม mockup — Acceptance: ดูใน plan ลูก multi-portfolio-02-frontend
