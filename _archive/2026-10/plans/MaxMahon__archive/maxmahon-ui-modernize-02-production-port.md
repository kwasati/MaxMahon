---
project: MaxMahon
created: 2026-04-23
last_updated: 2026-04-23
status: done
---

# Production UI Port — Retire Vintage, Apply Mockups

> Part 2 of 2 — port ทั้ง desktop mockup (plan 01 สร้าง) + mobile mockup (portfolio-builder-robinhood.html) ไปยัง production UI — เลิกใช้ vintage newspaper masthead ทั้งหมด: swap fonts เป็น Inter (Playfair Display + Lora → Inter), rewrite mast nav + mobile nav ให้เป็น modern app header pattern, ลบ 'VOL.VI·NO.17' + 'THURSDAY · APRIL' dateline + '№ 05 · PORTFOLIO BUILDER' section kickers + newspaper display headings ออกจาก page modules, restyle portfolio-builder pages ให้ตรงกับ mockups เป๊ะ. | Index: maxmahon-ui-modernize-index | Depends on: maxmahon-ui-modernize-01-desktop-mockup | Parallel-safe with: none

## Phase 1: Typography swap + editorial chrome removal
- [x] แก้ `projects/MaxMahon/web/v6/shared/tokens.css` บรรทัด 90-93 — swap fonts: `--font-head` จาก 'Playfair Display' → 'Inter', `--font-body` จาก 'Lora' → 'Inter', เก็บ `--font-mono` เดิม (JetBrains Mono). ต้องอัพเดท Google Fonts import link ใน shell HTMLs ด้วย (Task 1.2). — scope: แค่ tokens.css font tokens — Acceptance: `grep -n 'Playfair\|Lora' projects/MaxMahon/web/v6/shared/tokens.css` ว่าง + `grep -n 'Inter' projects/MaxMahon/web/v6/shared/tokens.css` มี 2 matches ขึ้นไป
- [x] แก้ Google Fonts link tag ใน 8 shell HTMLs (desktop: index/portfolio/watchlist/portfolio-builder + mobile: index/portfolio/watchlist/portfolio-builder ใน `projects/MaxMahon/web/v6/desktop/` และ `projects/MaxMahon/web/v6/mobile/`) — เปลี่ยน `<link href="https://fonts.googleapis.com/css2?family=Playfair+Display...&family=Lora...">` เป็น `<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=IBM+Plex+Serif+Thai:wght@400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap">` (IBM Plex Serif Thai ถือเป็น Thai fallback เอาไว้ — แต่ primary = Inter). — scope: เฉพาะ link tag — Acceptance: grep Playfair+Lora ใน desktop/ + mobile/ ไม่เจอ
- [x] แก้ `projects/MaxMahon/web/v6/shared/base.css` — ลบ/simplify rules ที่สร้าง editorial feel: rules ที่ใช้ `--rule-thick` สำหรับ border หนา, rules ที่ใช้ `font-size: var(--fs-disp)` (5.2rem display heading), rules เฉพาะ `.dateline` / `.kicker` / `.masthead` ถ้ามี, rules ที่ใช้ italic + small-caps styling สำหรับ editorial. เก็บ utility classes `.serif` / `.body` / `.mono` แต่เปลี่ยน `.serif` → map `--font-head` (ตอนนี้ Inter อยู่แล้ว). — scope: ไม่แก้ layout/spacing/responsive — Acceptance: เปิด `/` ใน browser → ไม่มี 5.2rem display heading ลอย + ไม่มี oxblood border thick + font ทั่วหน้าเป็น Inter sans-serif

### Reference
```css
/* current (tokens.css:90-93) */
--font-head:  'Playfair Display', 'IBM Plex Serif Thai', Georgia, serif;
--font-body:  'Lora', 'IBM Plex Serif Thai', Georgia, serif;
--font-mono:  'JetBrains Mono', ui-monospace, 'Courier New', monospace;
--font-micro: 'JetBrains Mono', 'IBM Plex Serif Thai', monospace;

/* new */
--font-head:  'Inter', 'IBM Plex Serif Thai', -apple-system, system-ui, sans-serif;
--font-body:  'Inter', 'IBM Plex Serif Thai', -apple-system, system-ui, sans-serif;
--font-mono:  'JetBrains Mono', ui-monospace, 'Courier New', monospace;
--font-micro: 'JetBrains Mono', 'IBM Plex Serif Thai', monospace;
```

```html
<!-- current (desktop/index.html:10) -->
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,700;0,900;1,400;1,700&family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400;1,600&family=IBM+Plex+Serif+Thai:wght@400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap" rel="stylesheet">

<!-- new -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=IBM+Plex+Serif+Thai:wght@400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap" rel="stylesheet">
```

## Phase 2: Rewrite mast + mobile nav components
- [x] Rewrite `projects/MaxMahon/web/v6/static/js/components.js` function `MMComponents.renderMastNav(opts)` — จากเดิม output newspaper masthead ('VOL. VI · NO. 17' + 'Max Mahon / The Dividend Review' + 'BUILDER EDITION · AUTO · NEXT SCAN') เปลี่ยนเป็น modern app header pattern ตาม mockup: `<header class='app-header'><div class='brand'><div class='mark'>M</div><div><div class='name'>Max Mahon</div><div class='sub'>จัดพอร์ตสไตล์ ดร.นิเวศน์</div></div></div><nav><a href='/watchlist'>WATCHLIST</a>...</nav><button class='icon-btn'>⋮</button></header>`. Active link detection จาก current pathname (same as current impl). — scope: ไม่แก้ renderMobileNav ใน task นี้ — Acceptance: เปิด `/` → top ของหน้าเป็น logo mark sage + brand name + nav tabs + icon — ไม่มี 'VOL. VI' หรือ dateline ปรากฏ
- [x] Rewrite `MMComponents.renderMobileNav` ใน `components.js` — update ให้ตรงกับ mockup mobile bottom nav: 5 tabs สูงสุด (Home + Screen + Portfolio + Watch + Settings) หรือย้าย 'จัดพอร์ต' ออกจาก bottom nav (ใส่ใน primary nav ของ mobile header แทน) ถ้าพื้นที่ไม่พอ. Tab style: `.bn-item` width: 1fr of 5-col grid, icon + label, active color = var(--c-positive). — scope: ไม่แก้ bottom-nav fixed positioning — Acceptance: mobile view เปิด `/m/` → bottom nav 5 tabs ชัด icon + label, tab ที่ active ใช้ sage color
- [x] Update 4 desktop shell HTMLs (`desktop/index.html`, `portfolio.html`, `watchlist.html`, `portfolio-builder.html`) — ตรวจ `<div id='masthead'>` container ถ้ายังมี → ยังเก็บไว้ได้ (renderMastNav mount ที่นั่น) แต่ remove any inline newspaper-related HTML ใน shell. — scope: ไม่แก้ page module imports — Acceptance: `curl -s http://localhost:50089/ | grep -o 'masthead\|VOL.\|EDITION' | sort -u` — ต้องเห็นแค่ 'masthead' (container) ไม่เห็น 'VOL.' หรือ 'EDITION'
- [x] Update 4 mobile shell HTMLs (`mobile/index.html`, `portfolio.html`, `watchlist.html`, `portfolio-builder.html`) — เหมือน task ด้านบน — Acceptance: grep 'VOL.\|EDITION' ใน mobile shells ว่าง

## Phase 3: Page module editorial cleanup
- [x] แก้ 6 desktop page modules (`home.js`, `report.js`, `watchlist.js`, `portfolio.js`, `simulator.js`, `settings.js` ที่ `projects/MaxMahon/web/v6/static/js/pages/`) — ลบ section kicker pattern '№ XX · PAGE NAME' (ค้นด้วย grep `№` หรือ `\\u2116`) ทั้งหมด. ลบ `.dateline` / `.section-kicker` / `.masthead-display` HTML output ใน render functions. เปลี่ยน big display heading (ถ้ามี `<h1>` ใช้ `--fs-disp`) เป็น `<h1>` normal ที่ใช้ Inter sans-serif — scope: ไม่แก้ data fetching / API calls — Acceptance: `grep -nE '№|section-kicker|fs-disp' projects/MaxMahon/web/v6/static/js/pages/*.js` ว่าง (ยกเว้น .mobile.js ที่ task ถัดไปทำ)
- [x] แก้ 6 mobile page modules (`*.mobile.js` same 6 names) — เหมือน desktop task — Acceptance: grep same ใน *.mobile.js ว่าง

## Phase 4: Portfolio-builder restyle to mockups
- [x] Rewrite `projects/MaxMahon/web/v6/static/js/pages/portfolio-builder.js` (desktop) — ใช้ `mockup/portfolio-builder-robinhood-desktop.html` (สร้างจาก plan 01) เป็น source of truth ของ DOM structure + CSS class names. Structure: `.app-desktop > .headline + .cols ( .left-col + .right-col )` — left has capital-card + chip-section × 2 + run-btn + algo-foot, right has summary-strip + pos-list + diversify. แสดง **capital input + chip rows default เสมอ** (ไม่รอ submit) + result section แสดง empty state แรก 'กดจัดพอร์ตเพื่อดูผล' และอัพเดทหลัง API response. styling ใช้ `.mm-pb-*` classes ใน components.css (เพิ่ม desktop variant ถ้ายังไม่มี). — scope: ไม่แก้ API call logic — Acceptance: เปิด `/portfolio-builder` viewport 1440px → 2-column layout ชัด, form inputs + chips แสดงทันทีโดยไม่ต้อง submit, feel ใกล้เคียง mockup desktop
- [x] Rewrite `projects/MaxMahon/web/v6/static/js/pages/portfolio-builder.mobile.js` — ใช้ `mockup/portfolio-builder-robinhood.html` เป็น source of truth: `.app > .topbar + .headline + .capital-card + .quick-row + .chip-section × 2 + .summary-strip + .pos-list + .bottom-nav`. Capital card + chips visible default. Position cards ranked list ใต้ summary. Diversification panel ท้ายก่อน bottom-nav. — scope: ไม่แก้ API — Acceptance: เปิด `/m/portfolio-builder` mobile viewport → เห็น capital card prominent top + chip rows default + bottom-nav 5 tabs, feel ตรง mockup mobile

## Phase 5: Visual verify + sweep
- [x] Visual check — รัน server (`py -m uvicorn server.app:app --port 50089` background) + เปิด 4 pages สุ่มใน 2 viewports: `/` + `/portfolio-builder` ที่ viewport 1440px (desktop) และ `/m/` + `/m/portfolio-builder` ที่ viewport 375px (mobile iPhone). ถ่าย screenshot ทั้ง light + dark mode (8 screenshots รวม) เก็บที่ `projects/MaxMahon/docs/ui-modernize-screenshots/YYYY-MM-DD/`. เช็คกับ mockups ทั้ง desktop + mobile — ต้องใกล้เคียง. — scope: manual QA — Acceptance: 8 screenshots saved + visual match notes
- [x] Final sweep: `grep -rnE '#[0-9A-Fa-f]{3,6}|rgba\(|rgb\(|Playfair|Lora|№|masthead-display|dateline|section-kicker|fs-disp' projects/MaxMahon/web/v6/ --include='*.css' --include='*.html' --include='*.js'` — ควรเหลือเฉพาะ tokens.css :root + _comments. ถ้าเจอที่อื่น → แก้ — Acceptance: grep output สะอาด
