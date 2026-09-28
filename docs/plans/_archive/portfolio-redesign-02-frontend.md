---
project: 4-MaxMahon
created: 2026-06-08
last_updated: 2026-06-11
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: เปิด max ที่ / แล้วเห็นหน้าพอร์ตตาม mockup (hero สรุปรวม + calculator เติมเงิน + holdings 3 กลุ่ม + นอกแผน + แผน) ทั้ง desktop และ mobile ; กรอกจำนวนหุ้นได้ ; ใส่เงินกองกลางกดคำนวณได้แผนซื้อ ; กดการ์ดดู research เต็มได้

### รายละเอียด
- ยึด mockup C:/WORKSPACE/.claude/artifacts/maxmahon-portfolio-redesign-mockup.html 100% (layout/สี/spacing/font copy จาก mockup ห้ามเดา)
- ใช้ token เดิมจาก tokens.css ทุกจุด (ห้าม hardcode hex/px) — mockup ฝัง token ค่าเดียวกับ DESIGN.md แล้ว
- หน้าใหม่เป็น route '/' (home ใหม่ = พอร์ต) — desktop pages/portfolio-home.js + mobile pages/portfolio-home.mobile.js (ชื่อใหม่กันชนกับ home.js เดิมที่ยัง archive ไม่เสร็จใน plan 03)
- nav ใหม่: แทน 4-tab เดิม (LATEST SCAN/WATCHLIST/จัดพอร์ต/SETTINGS) — เหลือเท่าที่จำเป็น (พอร์ต + อาจมีลิงก์ research/scan เดิมถ้ายังอยากเข้า) ใน components.js
- page module ตาม pattern เดิม: export function mount(root) -> _renderShell() + _bindEvents() + _load() ; fetch ผ่าน window.MMApi.get/put/post
- calculator interaction: พิมพ์เงิน -> POST /api/portfolio/topup -> render ตารางแผนซื้อ
- edit holdings: ปุ่มแก้จำนวนหุ้น+เงินสด -> PUT /api/portfolio/holdings -> reload state
- ดู full research: ปุ่มในการ์ด -> เปิด report เดิม (/report/{sym}) หรือ modal แสดง research markdown
- desktop/mobile split ตาม DESIGN.md (2 module + mobile.css override) breakpoint 900px
- CSS ใหม่ไปที่ static/css/components.css (section ใหม่ท้ายไฟล์) + mobile override ใน shared/mobile.css ; ทุก token ต้องมี dark counterpart

### Scope Boundary
**In scope:**
- web/v6/static/js/pages/portfolio-home.js (สร้างใหม่ desktop)
- web/v6/static/js/pages/portfolio-home.mobile.js (สร้างใหม่ mobile)
- web/v6/static/js/components.js — nav ใหม่ (desktop 34-39 + mobile 175-180)
- web/v6/static/css/components.css — section พอร์ตใหม่
- web/v6/shared/mobile.css — override พอร์ตใหม่
- shell route mapping ถ้าต้อง map '/' -> portfolio-home (desktop/index.html:33-34,91 + mobile/index.html:35-40,115)

**Out of scope:**
- API (เสร็จใน plan 01 แล้ว — แค่เรียก)
- archive page module เดิม + ลบ login (plan 03)
- tokens.css (ไม่เพิ่ม token ใหม่ ถ้าไม่จำเป็น — ใช้ของเดิม)

### Non-goals
- ไม่ออกแบบ token/สีใหม่ (ธีมเดิม)
- ไม่แตะหน้า report/scan เดิม (แค่ลิงก์ไปได้)
- ไม่ทำ chart ถ้า mockup ไม่มี (mockup ใช้ bar+ตาราง ไม่มี Chart.js — ไม่ต้องเพิ่ม)

### Skill Flow
- /build -> /qc -> /done

### Stop Conditions
- mockup element ไหน map API field ไม่ได้ (data ไม่มีใน /api/portfolio/state) -> หยุดถาม
- nav เดิมถูก component อื่นเรียกใช้ -> เช็คก่อนแก้ ไม่ให้หน้าอื่นพัง (ยังไม่ archive จนถึง plan 03)
- route '/' ชนกับ home.js เดิม -> ยืนยันวิธี map ก่อนแก้ shell

### Report-Back Contract
- verdict
- files touched
- เทียบ mockup ตรงไหม (screenshot)
- desktop+mobile ทั้งคู่ render ได้ไหม
- unresolved

# Portfolio Redesign 02 — Frontend (หน้าพอร์ตใหม่ desktop+mobile)

> Part 2 of 4 — Frontend: หน้าพอร์ตใหม่ desktop+mobile + nav + CSS ตาม mockup | Index: portfolio-redesign-index
> Depends on: portfolio-redesign-01-backend (ต้องมี API /api/portfolio/*)
> Parallel-safe with: none (03 แตะ components.js + shell เหมือนกัน)

## Phase 1: CSS (components.css + mobile.css)
- [x] เพิ่ม CSS section พอร์ตใหม่ใน web/v6/static/css/components.css — copy ค่าจาก mockup (hero/summary-strip/calc/holding/alloc-bar/offplan/plan-card) ใช้ var(--xxx) ทุกจุด — scope: ไม่แก้ section เดิม (watchlist/report/portfolio builder) — Acceptance: class ครบตาม mockup, ไม่มี hardcode hex/px, มี dark counterpart
- [x] เพิ่ม mobile override ใน web/v6/shared/mobile.css — holdings grid 1-col, summary-strip 2-col, calc stack — scope: เฉพาะ class พอร์ตใหม่ — Acceptance: ≤900px layout ไม่ overflow

### Reference
# mockup = source of truth: C:/WORKSPACE/.claude/artifacts/maxmahon-portfolio-redesign-mockup.html
# <style> block ใน mockup มี class ครบ (.hero/.calc/.holding/.alloc-bar/.offplan/.plan-card) + token values
# components.css ปัจจุบัน 1298 บรรทัด — portfolio builder section อยู่ 717-976 (อย่าทับ) เพิ่ม section ใหม่ท้ายไฟล์
# DESIGN.md section 15 กฎเหล็ก: var(--xxx) เท่านั้น + dark counterpart + card var(--r-4)

## Phase 2: Page module desktop
- [x] สร้าง web/v6/static/js/pages/portfolio-home.js — export mount(root); _renderShell() ตาม mockup (hero+calc+holdings 3 กลุ่ม+offplan+plan); _load() เรียก MMApi.get('/api/portfolio/state'); render การ์ดจาก state — scope: ตาม pattern portfolio.js เดิม — Acceptance: เปิดหน้าเห็นพอร์ตครบตาม mockup, ราคา/สัดส่วนจาก API จริง
- [x] เพิ่ม calculator interaction ใน portfolio-home.js — input เงิน + ปุ่มคำนวณ -> MMApi.post('/api/portfolio/topup',{new_money}) -> render ตารางแผนซื้อ — Acceptance: ใส่ 100000 กดคำนวณ เห็นตัวขาดได้ shares_to_buy ตัวเกินขึ้น —
- [x] เพิ่ม edit holdings + ดู research ใน portfolio-home.js — ปุ่มแก้จำนวนหุ้น -> PUT holdings -> reload ; ปุ่มดูเหตุผลเต็ม -> /report/{sym} — Acceptance: แก้หุ้นแล้ว state อัปเดต, กดดู research เปิดหน้า report

### Reference
# page module pattern (portfolio.js:12-15):
# export function mount(root){ root.innerHTML=_renderShell(); _bindEvents(root); _load(root); }
# fetch: window.MMApi.get(url) / .put(url,body) / .post(url,body) — wrapper + Bearer + 403 redirect
# helper: window.MMComponents.renderLoading/renderError ; window.MMUtils.escapeHtml
# render = vanilla DOM string concat เข้า root (<main id=app class=container>)

## Phase 3: Page module mobile + nav + route
- [x] สร้าง web/v6/static/js/pages/portfolio-home.mobile.js — port desktop logic, layout mobile (1-col) ตาม mobile.css — Acceptance: เปิด /m เห็นพอร์ตครบ ไม่ overflow
- [x] แก้ nav ใน web/v6/static/js/components.js — desktop renderMastNav items (34-39) + mobile renderMobileNav (175-180) เป็น nav ใหม่ (พอร์ตเป็นหลัก) — scope: ไม่ลบ function อื่น — Acceptance: nav ชี้หน้าพอร์ต, ไม่มี tab ตาย
- [x] map route '/' -> portfolio-home ใน shell (desktop/index.html:91 + mobile/index.html:115 import path) — scope: ไม่แตะ auth guard (plan 03) — Acceptance: เปิด / โหลด portfolio-home.js, /m โหลด .mobile.js

### Reference
# components.js desktop nav (34-39): items=[['latest-scan','/','LATEST SCAN'],['watchlist','/watchlist','WATCHLIST'],['portfolio','/portfolio','จัดพอร์ต'],['settings','/settings','SETTINGS']]
# components.js mobile nav (175-180): [['home','/m','...'],['saved','/m/watchlist',...],['portfolio','/m/portfolio',...],['settings','/m/settings',...]]
# shell route loader: desktop/index.html:91 import('/static/v6/js/pages/'+route+'.js') ; mobile:115 +'.mobile.js'
# route = pathname segment แรก (desktop:33-34 currentRoute) — '/' -> route='' หรือ 'home' (เช็ค default mapping ในไฟล์)
