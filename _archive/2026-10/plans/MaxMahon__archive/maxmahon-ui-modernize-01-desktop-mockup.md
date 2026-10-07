---
project: MaxMahon
created: 2026-04-23
last_updated: 2026-04-23
status: done
---

# Desktop Mockup — Robinhood Sage (จัดพอร์ตสไตล์แมกซ์)

> Part 1 of 2 — สร้าง desktop mockup ของ feature จัดพอร์ตสไตล์แมกซ์ ในสไตล์ Robinhood muted sage (ปัจจุบันมีแค่ mobile mockup: projects/MaxMahon/mockup/portfolio-builder-robinhood.html 480px max-width). Desktop mockup = standalone HTML, 1200+ px viewport, multi-column layout, bigger cards, ใช้ token system เดียวกับ mobile mockup (สมมติ user approve วิธีการ design → ส่ง mockup เป็น input ให้ plan 02 port ไป production). | Index: maxmahon-ui-modernize-index | Depends on: none | Parallel-safe with: none

## Phase 1: Create desktop mockup HTML
- [x] สร้างไฟล์ `projects/MaxMahon/mockup/portfolio-builder-robinhood-desktop.html` — standalone HTML (inline CSS + inline JS optional) แสดง feature จัดพอร์ตสไตล์แมกซ์ layout desktop viewport 1200-1600px. Structure: (1) top app header — logo mark 'M' + brand 'Max Mahon' + subtitle 'จัดพอร์ตสไตล์ ดร.นิเวศน์' + nav tabs (WATCHLIST/SAVED/PORTFOLIO/จัดพอร์ต/SIMULATOR/SETTINGS) + settings icon right, (2) page headline section — h1 big sans-serif 'จัดพอร์ตสไตล์แมกซ์' + tagline '5 หุ้น · 5 sector · น้ำหนัก 80/20 · ตามแนว ดร.นิเวศน์', (3) 2-column layout below headline: LEFT column (350-400px fixed) = capital input card (gradient bg like mobile) + pin/exclude chip rows + submit button 'จัดพอร์ต' + algo explanation footer, RIGHT column (fluid) = summary strip 3-cell + ranked position cards LIST view (5 cards full-width with extra details per card: rank badge + symbol+th-name + SET sector pill + quality score + weight % LEFT, financial metrics + amount+shares RIGHT, full reason paragraph below) + diversification panel (bigger pie chart + legend with 5 sector rows), (4) subtle footer 'Niwes composite: yield + value + hidden + quality · Weighting 40/35/12/8/5'. Copy `:root` + `@media (prefers-color-scheme:dark)` blocks **จากไฟล์** `mockup/portfolio-builder-robinhood.html` (บรรทัด 11-175) — ใช้ token ชุดเดียวกันเพื่อความสอดคล้อง light+dark mode. Demo data เดียวกับ mobile: QH 40% / TCAP 35% / MC 12% / INTUCH 8% / PTT 5% (capital 1M THB, pinned QH, excluded BCP+HMPRO, 5 sectors total avg score 85). ทุก color ต้องใช้ var(--...) — ห้าม hardcoded hex นอก :root. — scope: ห้ามแตะไฟล์นอก mockup/, ห้ามใช้ external JS framework (vanilla only), ห้าม import stylesheet อื่น — Acceptance: เปิดไฟล์ใน browser (double-click) + viewport 1440px → ต้องเห็น 2-column layout ชัดเจน + dark mode (prefers-color-scheme:dark) toggle ทำงาน + `grep -nE '#[0-9A-Fa-f]{3,6}|rgba\(' projects/MaxMahon/mockup/portfolio-builder-robinhood-desktop.html | grep -v '^[0-9]*:.*:root\|--' | head` ว่าง (ไม่มี hardcoded color นอก :root)
- [x] Visual self-review — เปิดไฟล์ใน browser ที่ viewport 1440px เทียบ side-by-side กับ `mockup/portfolio-builder-robinhood.html` (mobile) ว่า: (a) token palette ตรงกัน (sage green accent, warm cream bg ใน light / slate bg ใน dark), (b) typography consistency (Inter sans-serif ทั่วไป, monospace สำหรับตัวเลข), (c) feature parity (ทุก element ที่ mobile มี desktop ก็มี + ขยาย spatial), (d) dark mode ทั้ง desktop + mobile mockups อ่านได้ชัดไม่มี contrast issue. บันทึก mismatches ถ้ามี (เช่น icon ขนาดผิด, sector color ไม่ตรง) ใน comment ของไฟล์ — scope: ไม่แก้ mobile mockup — Acceptance: ไฟล์ desktop mockup เปิดดูได้ + ไม่มี console error + visual feel ใกล้เคียง mobile mockup ยกเว้น layout (mobile stacked, desktop 2-column)

### Reference
```html
<!-- REFERENCE: mobile mockup section structure from portfolio-builder-robinhood.html -->
<!-- Copy :root + @media blocks from lines 11-175 of mobile mockup verbatim -->

<!-- Desktop layout pattern (new) -->
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <title>Portfolio Builder · Max Mahon (Desktop)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    /* Copy :root + @media (prefers-color-scheme:dark) blocks from mobile mockup lines 11-175 */
    :root { /* ... primitive + semantic tokens ... */ }
    @media (prefers-color-scheme:dark) { :root { /* ... dark overrides ... */ } }

    *,*::before,*::after { box-sizing: border-box; }
    html, body { margin:0; padding:0; background: var(--bg-base); color: var(--fg-primary); font-family: var(--font); font-size:16px; line-height:1.5; }
    body { min-height:100vh; }

    .app-desktop { max-width: 1440px; margin: 0 auto; padding: 0 32px; }

    /* === TOP APP HEADER === */
    .app-header { display:flex; align-items:center; justify-content:space-between; padding: 20px 0 16px; border-bottom: 1px solid var(--border-subtle); }
    .app-header .brand { display:flex; align-items:center; gap:14px; }
    .app-header .mark { width:40px; height:40px; border-radius:12px; background: linear-gradient(135deg, var(--c-positive), var(--c-positive-strong)); display:grid; place-items:center; color:#fff; font-weight:900; font-size:18px; box-shadow: var(--shadow-accent-positive); }
    .app-header .name { font-weight:800; font-size:18px; letter-spacing:-.01em; }
    .app-header .sub { font-size:13px; color: var(--fg-dim); }
    .app-header nav { display:flex; gap:28px; }
    .app-header nav a { color: var(--fg-secondary); text-decoration:none; font-size:14px; font-weight:600; padding:8px 0; border-bottom: 2px solid transparent; }
    .app-header nav a.active { color: var(--c-positive-strong); border-bottom-color: var(--c-positive); }

    /* === HEADLINE === */
    .headline { padding: 40px 0 28px; }
    .headline h1 { margin:0; font-size:48px; font-weight:900; letter-spacing:-.025em; line-height:1.05; }
    .headline p { margin:10px 0 0; color: var(--fg-dim); font-size:16px; }

    /* === 2-COLUMN LAYOUT === */
    .cols { display: grid; grid-template-columns: 380px 1fr; gap: 32px; padding-bottom: 60px; }
    @media (max-width: 1100px) { .cols { grid-template-columns: 1fr; } }

    /* LEFT column */
    .left-col { display: flex; flex-direction: column; gap: 20px; }
    .capital-card { padding:26px; border-radius: var(--radius-lg); background: linear-gradient(135deg, var(--bg-elevated-start), var(--bg-elevated-end)); color: var(--fg-primary); position:relative; overflow:hidden; box-shadow: var(--shadow-card); border: 1px solid var(--bg-elevated-border); }
    /* ... capital card contents, chip sections, submit button ... */

    /* RIGHT column */
    .right-col { display: flex; flex-direction: column; gap: 20px; }
    .summary-strip { display: grid; grid-template-columns: repeat(3, 1fr); gap:0; padding: 20px; background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius); box-shadow: var(--shadow-card); }
    .pos-list { display: flex; flex-direction: column; gap: 12px; }
    .pos-card { padding: 20px 24px; background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius); display: grid; grid-template-columns: auto 2fr auto; gap: 20px; align-items: center; box-shadow: var(--shadow-card); }
    /* ... rest of desktop layout ... */
  </style>
</head>
<body>
  <div class="app-desktop">
    <header class="app-header"><!-- brand + nav + settings --></header>
    <section class="headline"><h1>จัดพอร์ตสไตล์แมกซ์</h1><p>5 หุ้น · 5 sector · น้ำหนัก 80/20 · ตามแนว ดร.นิเวศน์</p></section>
    <div class="cols">
      <aside class="left-col">
        <div class="capital-card"><!-- เงินลงทุน + yield --></div>
        <div class="chip-section"><!-- ปักหมุด QH --></div>
        <div class="chip-section"><!-- ถอดออก BCP + HMPRO --></div>
        <button class="run-btn">จัดพอร์ต</button>
        <div class="algo-foot"><!-- composite + weighting explanation --></div>
      </aside>
      <main class="right-col">
        <div class="summary-strip"><!-- 5 หุ้น / 5 sector / 85 score --></div>
        <div class="pos-list"><!-- 5 cards QH/TCAP/MC/INTUCH/PTT --></div>
        <div class="diversify"><!-- pie + legend --></div>
      </main>
    </div>
  </div>
</body>
</html>
```
