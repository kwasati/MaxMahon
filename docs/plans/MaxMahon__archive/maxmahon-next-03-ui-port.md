---
project: MaxMahon
created: 2026-04-23
last_updated: 2026-04-23
status: done
---

# UI Port — Robinhood Muted Sage Tokens → Production

> Part 3 of 3 — แทนที่ vintage newspaper design system (cream + ink + oxblood) ใน production UI ด้วย Robinhood muted sage token system จาก mockup ที่ user เลือกแล้ว (portfolio-builder-robinhood.html). Port 2-layer token (primitive + semantic) เข้า web/v6/shared/tokens.css + update base.css/mobile.css + redesign 6 existing page modules (home/report/watchlist/portfolio/simulator/settings) + wire portfolio-builder page (สร้างใน plan 02) ให้ใช้ design system ใหม่. | Index: maxmahon-next-index | Depends on: maxmahon-next-02-portfolio-builder | Parallel-safe with: none

## Phase 1: Token foundation — tokens.css + base/mobile.css
- [x] แก้ `projects/MaxMahon/web/v6/shared/tokens.css` — แทนที่ทั้งไฟล์ด้วย Robinhood muted sage token system จาก mockup (`projects/MaxMahon/mockup/portfolio-builder-robinhood.html` :root block บรรทัด 11-175): 2-layer system (primitive swatches: sage/rose/wheat/lavender/slate-blue — semantic: bg/fg/border/accent/rank/shadow), light mode default + @media (prefers-color-scheme:dark) override ทุก token ที่ต้อง swap. เก็บ --font-head/--font-body/--font-mono/--font-micro เดิมไว้ (typography ไม่เปลี่ยน). เก็บ --sp-1..--sp-8, --fs-*, --col-max, --rule-thin/med/thick เดิม (spacing/type scale + layout ไม่เปลี่ยน). เพิ่ม legacy aliases เผื่อ component CSS เก่าอ้าง --paper/--ink/--accent: --paper=var(--bg-base), --paper-2=var(--bg-surface), --ink=var(--fg-primary), --accent=var(--c-positive-strong). — scope: ห้ามแก้ base.css/mobile.css/components.css — Acceptance: เปิดหน้า `/` ใน browser ดู — bg ไม่ใช่สี cream อีก แต่เป็น warm off-white muted (#f5f5f0), dark mode เปลี่ยนเป็น slate-900 (#1c1f25) ไม่ใช่ pure black
- [x] แก้ `projects/MaxMahon/web/v6/shared/base.css` — scan ไฟล์ทั้งหมด หาที่ใช้ hex/rgb ตรงๆ (ไม่ใช่ var()) แล้วแทนด้วย semantic tokens ใหม่: `#F4EFE6` → `var(--bg-base)`, `#1A1814` → `var(--fg-primary)`, `#7A1F2B` → `var(--c-positive-strong)` (accent = sage instead of oxblood), etc. เก็บ rule-thin/rule-hair ที่เป็น token ไว้. — scope: ไม่เปลี่ยน layout/spacing/typography — Acceptance: `grep -nE '#[0-9A-Fa-f]{3,6}|rgba\(|rgb\(' projects/MaxMahon/web/v6/shared/base.css` ควรไม่เหลือ hardcoded color นอก :root/comments
- [x] แก้ `projects/MaxMahon/web/v6/shared/mobile.css` — เหมือน base.css task ข้างบน — แทนที่ hardcoded colors ด้วย var() references. — scope: ไม่เปลี่ยน layout — Acceptance: `grep -nE '#[0-9A-Fa-f]{3,6}|rgba\(|rgb\(' projects/MaxMahon/web/v6/shared/mobile.css` ควรเหลือแค่ใน comments
- [x] แก้ `projects/MaxMahon/web/v6/static/css/components.css` — แทนที่ hardcoded colors ในทุก component rule ด้วย semantic tokens. — scope: ไม่เปลี่ยน layout — Acceptance: `grep -nE '#[0-9A-Fa-f]{3,6}|rgba\(|rgb\(' projects/MaxMahon/web/v6/static/css/components.css` ว่าง (นอก comment)

### Reference
```css
/* current (tokens.css:1-80) — vintage newspaper */
:root {
  --paper:        #F4EFE6;   /* cream base */
  --paper-2:      #EDE6D6;
  --ink:          #1A1814;
  --accent:       #7A1F2B;   /* oxblood */
  /* ... */
}

/* new — copy from mockup/portfolio-builder-robinhood.html :root (lines 11-175) */
:root {
  /* PRIMITIVE (raw swatches) */
  --sage-500:#7ba688;  --sage-600:#5d8c69;
  --rose-500:#c98b85;
  --wheat-500:#caa673;
  --lavender-500:#9d90c7;
  --slate-blue-500:#84a8c9;

  /* SEMANTIC — light mode */
  --bg-base:#f5f5f0;
  --bg-outside:#e8e6dd;
  --bg-surface:#ffffff;
  --bg-surface-2:#ebebe4;
  --bg-elevated-start:#f1eee3;
  --bg-elevated-end:#e6e2d4;
  --bg-elevated-border:#d9d4c4;
  --btn-on-elevated:rgba(255,255,255,.75);

  --fg-primary:#3b4050;
  --fg-secondary:#5a6072;
  --fg-dim:#878d9a;
  --fg-mute:#b2b6c0;

  --border-subtle:#e6e4db;
  --border-strong:#d1cec1;

  --c-positive:var(--sage-500);
  --c-positive-strong:var(--sage-600);
  --c-positive-soft:#e9f1eb;
  --c-positive-tint:#f3f8f4;
  --c-positive-border:rgba(123,166,136,.35);

  --c-negative:var(--rose-500);
  --c-negative-soft:#f4eae8;
  --c-negative-border:rgba(201,139,133,.35);

  --c-warn:var(--wheat-500);
  --c-warn-soft:#f5eed8;
  --c-warn-fg:#8a6d3a;
  --c-warn-border:rgba(202,166,115,.3);

  --c-info:var(--slate-blue-500);
  --c-info-soft:#e6eef5;
  --c-info-fg:#456a8c;

  --c-purple:var(--lavender-500);
  --c-purple-soft:#ebe7f4;
  --c-purple-fg:#6a5c9e;

  --rank-gold-start:#f2e5ba;
  --rank-gold-end:#d9c08a;
  --rank-gold-fg:#6d5524;
  --rank-silver-start:#e7eaf0;
  --rank-silver-end:#c9cfdb;
  --rank-silver-fg:#4a5264;

  --shadow-card:0 2px 10px rgba(60,66,82,.06);
  --shadow-elevated:0 8px 24px rgba(60,66,82,.08);
  --shadow-accent-positive:0 4px 12px rgba(123,166,136,.22);
  --shadow-toggle:0 2px 6px rgba(60,66,82,.12);

  /* keep typography + spacing + radius + layout from old tokens.css */
  --font-head:'Playfair Display','IBM Plex Serif Thai',Georgia,serif;
  --font-body:'Lora','IBM Plex Serif Thai',Georgia,serif;
  --font-mono:'JetBrains Mono',ui-monospace,'Courier New',monospace;
  /* ... keep fs-*, sp-*, rule-*, col-max, r-* unchanged ... */

  /* Legacy aliases for component CSS not yet refactored */
  --paper:var(--bg-base);
  --paper-2:var(--bg-surface-2);
  --paper-3:var(--bg-surface);
  --ink:var(--fg-primary);
  --ink-soft:var(--fg-secondary);
  --ink-dim:var(--fg-dim);
  --ink-faint:var(--fg-mute);
  --rule:var(--border-strong);
  --rule-hair:var(--border-subtle);
  --rule-fade:var(--border-subtle);
  --accent:var(--c-positive-strong);
  --accent-ink:var(--c-positive);
  --accent-soft:var(--c-positive-soft);
}

@media (prefers-color-scheme:dark) {
  :root {
    /* flip all semantic bg/fg/border/soft — keep primitive swatches */
    --bg-base:#1c1f25;
    --bg-outside:#0f1115;
    --bg-surface:#262a32;
    --bg-surface-2:#2f343d;
    --bg-elevated-start:#2a2f38;
    --bg-elevated-end:#353b45;
    --bg-elevated-border:#3d434e;
    --btn-on-elevated:rgba(255,255,255,.08);
    --fg-primary:#e4e6eb;
    --fg-secondary:#b3b7c1;
    --fg-dim:#838896;
    --fg-mute:#5b606c;
    --border-subtle:#373c46;
    --border-strong:#4b5160;
    --c-positive-soft:rgba(123,166,136,.14);
    --c-positive-tint:rgba(123,166,136,.07);
    --c-positive-border:rgba(123,166,136,.4);
    --c-negative-soft:rgba(201,139,133,.14);
    --c-negative-border:rgba(201,139,133,.4);
    --c-warn-soft:rgba(202,166,115,.16);
    --c-warn-fg:#d9b87f;
    --c-warn-border:rgba(202,166,115,.35);
    --c-info-soft:rgba(132,168,201,.14);
    --c-info-fg:#a8c2d9;
    --c-purple-soft:rgba(157,144,199,.14);
    --c-purple-fg:#c1b6e0;
    --rank-gold-start:#4d421e;
    --rank-gold-end:#6a5a2e;
    --rank-gold-fg:#e8d49a;
    --rank-silver-start:#363c4a;
    --rank-silver-end:#474e5f;
    --rank-silver-fg:#c9cfdb;
    --shadow-card:0 2px 10px rgba(0,0,0,.28);
    --shadow-elevated:0 8px 24px rgba(0,0,0,.38);
    --shadow-accent-positive:0 4px 12px rgba(123,166,136,.28);
    --shadow-toggle:0 2px 6px rgba(0,0,0,.35);
  }
}
```

## Phase 2: Shell HTML updates (desktop + mobile)
- [x] แก้ 3 desktop shells: `projects/MaxMahon/web/v6/desktop/index.html`, `portfolio.html`, `watchlist.html` — scan แต่ละไฟล์หา inline `style="..."` + inline `<style>` blocks ที่ใช้ hardcoded hex/rgb colors → แทนด้วย var() references. เปลี่ยน body/page chrome จาก vintage newspaper feel (serif header + oxblood rule) เป็น modern soft (sans-serif header + sage accent). เก็บ structural HTML เดิม (grid / sections / IDs / data-attributes) — แตะแค่ visual chrome. — scope: ห้ามแก้ไฟล์ JS modules หรือเปลี่ยน layout structure — Acceptance: `grep -nE '#[0-9A-Fa-f]{3,6}' projects/MaxMahon/web/v6/desktop/*.html` returns empty (นอก comments), visual: เปิด 3 หน้า bg เป็น soft cream ไม่ใช่ vintage paper
- [x] แก้ 3 mobile shells: `projects/MaxMahon/web/v6/mobile/index.html`, `portfolio.html`, `watchlist.html` — same as desktop task — scope: ไม่แก้ responsive breakpoints — Acceptance: `grep -nE '#[0-9A-Fa-f]{3,6}' projects/MaxMahon/web/v6/mobile/*.html` returns empty

## Phase 3: Desktop page modules — 6 pages redesign
- [x] แก้ `projects/MaxMahon/web/v6/static/js/pages/home.js` + `report.js` + `watchlist.js` + `portfolio.js` + `simulator.js` + `settings.js` — scan each สำหรับ inline color strings ใน template literal / createElement หรือ setAttribute แล้วเปลี่ยนเป็น CSS class references (ให้ styling มาจาก tokens.css/components.css). ถ้าจำเป็น add utility classes ไปใน components.css (เช่น `.sage-fg`, `.positive-bg`, etc.). — scope: ห้ามเปลี่ยน data fetching / API calls / event handlers — Acceptance: 6 pages โหลดใน browser ได้ + visual screenshots เทียบกับ mockup palette (sage/cream) + dark mode ก็ work
- [x] แก้ `projects/MaxMahon/web/v6/static/js/pages/portfolio-builder.js` (ที่สร้างใน plan 02) — update styling ให้ตรง design system ใหม่. เอา layout + UX pattern จาก mockup `mockup/portfolio-builder-robinhood.html` — capital card, chip rows, summary strip, position cards with weight %, diversification panel, bottom nav accent. ลบ style เดิมที่เป็น vintage. — scope: ไม่เปลี่ยน data flow ที่สร้างใน plan 02 — Acceptance: เปิด `/portfolio-builder` ดู visual ต้องใกล้เคียงกับ mockup (sage accent, muted palette, card-based layout)

## Phase 4: Mobile page modules — 6 pages redesign
- [x] แก้ 6 mobile page modules: `home.mobile.js`, `report.mobile.js`, `watchlist.mobile.js`, `portfolio.mobile.js`, `simulator.mobile.js`, `settings.mobile.js` — เหมือน desktop task แต่ mobile-first responsive styling. ใช้ utility classes ที่เพิ่มใน components.css. — scope: เหมือน desktop — Acceptance: 6 pages โหลดใน `/m/*` ได้ + visual screenshots
- [x] แก้ `projects/MaxMahon/web/v6/static/js/pages/portfolio-builder.mobile.js` — port mobile layout จาก mockup (480px max-width + bottom nav + stacked position cards). — Acceptance: `/m/portfolio-builder` visual ใกล้เคียง mockup mobile layout

## Phase 5: Visual verify + deploy
- [x] เปิด browser screenshot 14 pages (6 desktop + 6 mobile + 1 portfolio-builder desktop + 1 mobile): `/`, `/report/*`, `/watchlist`, `/portfolio`, `/simulator`, `/settings`, `/portfolio-builder`, `/m/`, `/m/report/*`, `/m/watchlist`, `/m/portfolio`, `/m/simulator`, `/m/settings`, `/m/portfolio-builder`. เก็บไว้ที่ `projects/MaxMahon/docs/ui-port-screenshots/YYYY-MM-DD/`. ตรวจทั้ง light + dark mode. — scope: manual visual QA — Acceptance: 14 screenshots saved + dark mode ก็เช็คแล้ว ไม่มี cream-on-dark contrast issue (ตาม bug ที่เคยพบ)
- [x] เช็คและลบ hardcoded colors ที่ตกค้าง: `grep -rnE '#[0-9A-Fa-f]{3,6}|rgba\(|rgb\(' projects/MaxMahon/web/v6/ --include='*.css' --include='*.html' --include='*.js'` — เอาเฉพาะบรรทัดที่ไม่ใช่ comment. ถ้าเจอ → แก้เป็น var() ref. — Acceptance: grep ผลลัพธ์ไม่เหลือ hardcoded color นอก tokens.css + comments
- [x] Commit ทุก task ตาม commit format + push MaxMahon main + bump superproject submodule pointer — Acceptance: `git log --oneline origin/main..HEAD` บน submodule ว่าง (pushed), superproject main ชี้ submodule SHA ใหม่แล้ว
