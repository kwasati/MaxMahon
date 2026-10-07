---
project: 4-MaxMahon
created: 2026-06-08
last_updated: 2026-06-25
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: เปิด max แล้วเห็นพอร์ตจริง 7 ตัว + เงินสด + นอกแผน (LH/TISCO) สัดส่วนจริงเทียบเป้า ใส่เงินกองกลางแล้วได้แผนซื้อแบบดึงกลับเป้า ทุกอย่างที่เดียวจบ ไม่ต้องเปิด sheet

### รายละเอียด
- แปลง max จากเว็บสแกนหุ้น เป็นเว็บพอร์ตจริง (pillar 1 ปันผล)
- mockup เคาะแล้ว: C:/WORKSPACE/.claude/artifacts/maxmahon-portfolio-redesign-mockup.html (desktop) = source of truth ของ layout
- backend pipeline เดิม (setsmart price refresh 19:00 / set.or.th dividend / weekly scan) ยังรันหลังบ้านตามเดิม ไม่แตะ
- calculator = ดึงกลับเป้า (rebalance) เติมเฉพาะตัวขาดเป้า ไม่ใช่หารตามสัดส่วนตรงๆ
- ราคา auto จาก price_cache (setsmart) / จำนวนหุ้นกรอกเอง
- เก็บ login Google ไว้กันคนนอก แต่ single-user ตัด role เมีย (viewer)
- ธีมเดิม 100% (DESIGN.md tokens) layout ใหม่
- build order sequential: 01-backend -> 02-frontend -> 03-archive-deauth (collision app.py + shell ทำ parallel ไม่ได้)

### Scope Boundary
**In scope:**
- 01: data/portfolio.json + scripts/portfolio_state.py + API ใหม่ใน server/app.py
- 02: web/v6 หน้าพอร์ตใหม่ (desktop+mobile) + components.js nav + components.css
- 03: archive page modules เดิม + ตัด role gate + simplify whitelist

**Out of scope:**
- scan / screener / data_adapter / daily_price_refresh pipeline (รันหลังบ้านตามเดิม ไม่แตะ logic)
- Claude Opus analyze endpoint (ไม่เกี่ยวพอร์ต)

### Non-goals
- ไม่ทำ real-time sync กับพอร์ตโบรกจริง (จำนวนหุ้นกรอกเอง)
- ไม่ rip auth ทิ้งทั้งหมด (เก็บ login กันคนนอก เพราะ public tunnel + เงินจริง)
- ไม่ทำ multi-user/role (เหลือ user เดียว)

### Skill Flow
- /build portfolio-redesign-01-backend -> 02-frontend -> 03-archive-deauth -> /qc -> /done

# MaxMahon Portfolio Redesign — Index (build order)

> Part 0 of 4 — Index กำหนด build order | benefit: 4-MaxMahon. แปลง max เป็นเว็บพอร์ตจริง pillar 1 ที่เดียวจบ ตาม mockup ที่เคาะแล้ว

## Phase 1: Foundation (backend)
- [x] /build portfolio-redesign-01-backend — data schema + calculator + API (no deps)

## Phase 2: Frontend (หน้าพอร์ตใหม่)
- [x] /build portfolio-redesign-02-frontend — page module + nav + CSS ตาม mockup (depends 01)

## Phase 3: เก็บกวาดของเดิม + de-auth
- [x] /build portfolio-redesign-03-archive-deauth — archive เว็บเดิม + single-user (depends 02)
