---
project: 4-MaxMahon
created: 2026-06-24
last_updated: 2026-06-24
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: หน้าพอร์ต (desktop + mobile) โชว์ tab 3 พอร์ตตาม mockup, คลิกสลับโหลดพอร์ตนั้น, ดับเบิลคลิกชื่อ tab แก้ชื่อแล้วบันทึก, ปุ่มดึงราคากดแล้วเรียก refresh + โชว์เวลาล่าสุด

### รายละเอียด
- ยึด mockup 100%: C:\WORKSPACE\.claude\artifacts\maxmahon-portfolio-3tab-mockup.html (สี/ขนาด/layout copy จาก mockup)
- tab strip 3 อัน id A/B/C จุดสี A=positive B=info C=purple, active = bg-surface ขอบ folder
- ชื่อ tab โหลดจาก GET /api/portfolios; double-click -> contentEditable -> blur/Enter -> PUT /api/portfolio/{id}/name
- คลิก tab -> set _currentPfId + localStorage 'mm_active_pf' -> _load ใหม่ด้วย ?pf=
- _load เรียก GET /api/portfolio/state?pf={_currentPfId}
- ปุ่มดึงราคา -> POST /api/admin/price-refresh/trigger, ระหว่างรอ disable+หมุน, เสร็จ reload state + โชว์ price_as_of
- เวลาดึงล่าสุด อ่านจาก state.price_as_of (toLocaleString th-TH)
- ใช้ MMApi.get/post/put เดิม + MMComponents toast เดิม
- desktop + mobile โครงเดียวกัน — แก้ทั้ง 2 ไฟล์ให้ตรงกัน

### Scope Boundary
**In scope:**
- web/v6/static/js/pages/portfolio-home.js
- web/v6/static/js/pages/portfolio-home.mobile.js
- web/v6/static/css/components.css (.pf-home block)

**Out of scope:**
- backend (เสร็จใน plan 01)
- router/index.html (route เดิมใช้ได้)
- api.js (helper เดิมพอ)

### Non-goals
- ไม่ทำ UI เพิ่ม/ลบหุ้นในพอร์ต
- ไม่ทำปุ่มเพิ่ม/ลบ tab
- ไม่เปลี่ยนตาราง holdings/เติมเงินเดิม

### Skill Flow
- /build -> /qc -> /done

### Stop Conditions
- backend endpoint ?pf=/rename/price_as_of ยังไม่มี
- mockup หาย
- ไฟล์ portfolio-home.js ต่างจาก reference

# Multi-Portfolio Frontend — 3 tab + double-click rename + ปุ่มดึงราคา

> Part 2 of 2 — Frontend | Index: multi-portfolio-index
> Depends on: multi-portfolio-01-backend (ต้อง merge ก่อน — เรียก ?pf=, rename, price_as_of)
> Parallel-safe with: none

## Phase 1: shell — tab strip + ปุ่มดึงราคา (desktop)
- [x] Pre-build Review: อ่าน plan + mockup (C:\WORKSPACE\.claude\artifacts\maxmahon-portfolio-3tab-mockup.html) + portfolio-home.js + components.css .pf-home จริงก่อนแก้; ยืนยัน backend plan 01 merge แล้ว (มี ?pf=, /api/portfolios, PUT name, price_as_of); สงสัย/ขัดกัน = หยุดถาม; ชัด = เริ่มต่อ
- [x] แก้ web/v6/static/js/pages/portfolio-home.js _renderShell(): เพิ่ม pf-header (ปุ่มดึงราคา + priceinfo) ก่อน/ในหัว + pf-tabbar (3 tab จุดสี + ชื่อ) + pf-hintbar ตาม mockup; ใส่ id ph-pricebtn, ph-priceinfo, class pf-tab + data-pf. scope: ไม่แตะตาราง pf-card เดิม. Acceptance: หน้าโหลดเห็น 3 tab + ปุ่มดึงราคา ตรง mockup (ยังไม่ต้อง functional)

### Reference
# current (portfolio-home.js:27-89) _renderShell คืน '<div class="pf-wrap">' + pf-total + pf-card...
# mockup markup (อ้าง .claude/artifacts/maxmahon-portfolio-3tab-mockup.html):
#   .pf-header > button.pf-pricebtn#ph-pricebtn + span.pf-priceinfo#ph-priceinfo
#   .pf-tabbar > .pf-tab[.pf-tab-active] data-pf=A/B/C > .pf-tab-dot + .pf-tab-nm
#   .pf-hintbar 'ดับเบิลคลิกที่ชื่อแท็บเพื่อเปลี่ยนชื่อพอร์ต ...'
# ปุ่ม mockup ใช้ &#x21bb; (↻) ico, spin class ตอนกำลังดึง

## Phase 2: state + load pf + tab switch + rename + ปุ่มดึงราคา (desktop)
- [x] แก้ portfolio-home.js: เพิ่ม module state let _currentPfId = localStorage.getItem('mm_active_pf') || 'A'; _load เรียก GET /api/portfolio/state?pf=_currentPfId; _renderFoot/priceinfo ใช้ state.price_as_of; ตอน mount โหลดชื่อ tab จาก GET /api/portfolios มาเซ็ต .pf-tab-nm + ไฮไลต์ tab ตาม _currentPfId. Acceptance: เปิดหน้าโหลดพอร์ต A, ชื่อ tab ตรง backend, เวลาล่าสุดโชว์จาก price_as_of
- [x] แก้ portfolio-home.js _bindEvents: (ก) คลิก .pf-tab (ไม่ใช่ที่ชื่อ) -> set _currentPfId + localStorage + toggle active + _load; (ข) double-click .pf-tab-nm -> contentEditable=true เลือกข้อความ, blur/Enter -> PUT /api/portfolio/{id}/name {name}; (ค) คลิก ph-pricebtn -> _refreshPrice(): disable+spin, POST /api/admin/price-refresh/trigger, เสร็จ _load ใหม่ + toast, finally เลิก spin. scope: ไม่แตะ handler save/topup เดิม. Acceptance: สลับ tab โหลดคนละพอร์ต; rename แล้ว reload ยังอยู่; ปุ่มดึงราคา -> ราคาอัปเดต + เวลาเปลี่ยน

### Reference
# current (portfolio-home.js:16, 93-108, 371-391)
let _state = null; const _REPORT_BASE = '/report/';
async function _load(root){ const state = await window.MMApi.get('/api/portfolio/state'); ...}
function _bindEvents(root){ root.addEventListener('click', e=>{...}); ...}

# api helper: window.MMApi.get(path) / .post(path,body) / .put(path,body) (api.js:101-108)
# toast: window.MMComponents.showToast(msg, 'info'|'error')  (เช็คชื่อจริงใน components.js — settings.js ใช้ _showOpsToast)
# price btn pattern (settings.js): MMApi.post('/api/admin/price-refresh/trigger', {}).then(...).catch(...)
# new state: let _currentPfId = localStorage.getItem('mm_active_pf') || 'A';
#   _load -> MMApi.get('/api/portfolio/state?pf=' + _currentPfId)

## Phase 3: CSS .pf-tabbar / .pf-tab / .pf-pricebtn
- [x] เพิ่ม CSS ใน web/v6/static/css/components.css ท้าย .pf-home block: .pf-header, .pf-pricebtn(+hover/disabled/spin/ico @keyframes pf-spin), .pf-priceinfo, .pf-tabbar, .pf-tab(+active/dot/nm[contenteditable]), .pf-hintbar — copy ค่าจาก mockup <style> (token เดิมทั้งหมด ห้าม hardcode hex). Acceptance: หน้าตา tab + ปุ่ม ตรง mockup ทั้ง light + dark; ไม่กระทบ .pf-card/.pf-table เดิม

### Reference
# ค่าจริง copy จาก mockup <style> (.claude/artifacts/maxmahon-portfolio-3tab-mockup.html):
# .pricebtn -> .pf-pricebtn (height 34, radius 999, border c-positive-border, color c-positive-strong, hover c-positive-soft)
# .tabbar -> .pf-tabbar (flex align-end gap 4, border-bottom border-strong)
# .tab -> .pf-tab (height 38, radius r-3 r-3 0 0, bg-surface-2, active=bg-surface) 
# .tab .nm[contenteditable=true] -> bg c-positive-tint + ring c-positive
# prefix ทุก selector ด้วย .pf-home (scoped) เหมือน CSS เดิมในไฟล์

## Phase 4: mirror ลง mobile
- [x] แก้ web/v6/static/js/pages/portfolio-home.mobile.js ให้ตรง desktop: shell tab+ปุ่มดึงราคา, _currentPfId+localStorage, _load ?pf=, tab switch, double-click rename, _refreshPrice — copy logic จาก portfolio-home.js (ปรับเฉพาะส่วน layout mobile ที่ต่าง). Acceptance: เปิด /m เห็น tab + ปุ่มดึงราคา ใช้งานได้เหมือน desktop (สลับ/rename/ดึงราคา)

### Reference
# portfolio-home.mobile.js โครง function เดียวกับ desktop (mount/_renderShell/_load/_bindEvents)
# CSS ใช้ .pf-home ร่วม + mobile.css override ถ้าจำเป็น — tab/ปุ่ม reuse class เดียวกัน
