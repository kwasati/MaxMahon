---
project: MaxMahon
created: 2026-04-19
last_updated: 2026-04-19
status: active
---

# Mobile Editorial Port — ย้าย editorial design จาก desktop → mobile.html

> Desktop ได้ editorial treatment ไปแล้ว (v3.3.0) แต่ mobile.html ยังเป็น design เดิม (white bg, sans-serif, generic) ทำ mockup editorial mobile ก่อนให้ผู้ใช้อนุมัติ แล้วค่อย port ไป production mobile.html (ตามกฎ Mockup First) คงทุก UX flow + JS wiring เดิม เปลี่ยนแค่ visual language

## Phase 1: Mockup Foundation — สร้างไฟล์ + design tokens + chrome
- [ ] สร้าง web/mockup-mobile-editorial.html copy โครงจาก web/mobile.html (HTML structure เดิม ลบ JS wiring ออก ใส่ static fake data แทน — ใช้ 3-4 หุ้นจริงเพื่อ realistic)
- [ ] โหลด fonts: Fraunces (serif 400,500,700,900) + IBM Plex Sans Thai (400,500,600) + JetBrains Mono (400,500,600) จาก Google Fonts ใน <head>
- [ ] แทน :root tokens ของเดิมด้วย editorial palette 21 ตัวจาก desktop style.css (--paper, --ink, --forest, --amber ฯลฯ) + map ชื่อเก่า (--bg, --surface, --text) ให้ชี้ค่าใหม่เพื่อไม่ให้ inline styles พัง
- [ ] เพิ่ม route /mockup-mobile-editorial ใน server/app.py อ่านไฟล์ serve HTML แบบ raw (pattern เดียวกับ /mobile)
- [ ] Restyle top-bar เป็น masthead pattern — 3-col layout (Vol/Issue ซ้าย / ชื่อ Max Mahon กลาง serif italic / วันที่ขวา mono uppercase) + double border bottom + cream bg + sticky
- [ ] Restyle bottom nav — cream bg, rule line border-top, active state = forest underline แทน teal, icon stroke = ink

### Reference
```css
/* :root ใหม่ — copy จาก desktop style.css line 1-21 */
:root {
  --paper: #f4f0e6;
  --paper-2: #ebe5d4;
  --paper-3: #ffffff;
  --ink: #121420;
  --ink-2: #2a2d3d;
  --ink-dim: #595c6b;
  --ink-soft: #8e8f9c;
  --line: #d6cfbd;
  --line-strong: #b0a98c;
  --rule: #1a1a22;
  --forest: #1d5b4f;
  --forest-soft: #e4ede8;
  --amber: #b45309;
  --amber-soft: #f7eadb;
  --burgundy: #a02143;
  --burgundy-soft: #f5e3e7;
  --gold: #c89b2c;
  --navy: #1f3f76;
  --navy-soft: #e5ebf5;
  /* backward compat — ชี้ชื่อเก่าไปค่าใหม่ */
  --bg: var(--paper);
  --surface: var(--paper-3);
  --surface2: var(--paper-2);
  --border: var(--line);
  --border2: var(--line-strong);
  --text: var(--ink);
  --text2: var(--ink-2);
  --text3: var(--ink-soft);
  --accent: var(--forest);
  --accent-light: var(--forest-soft);
  --bottom-nav-h: 60px;
}

/* masthead */
.top-bar {
  background: var(--paper);
  border-bottom: 3px double var(--rule);
  padding: 0.75rem 1rem calc(0.75rem + env(safe-area-inset-top));
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 0.75rem;
  backdrop-filter: blur(16px) saturate(140%);
}
.mast-title {
  font-family: 'Fraunces', Georgia, serif;
  font-style: italic;
  font-weight: 900;
  font-size: 1.4rem;
  color: var(--ink);
  text-align: center;
}
.mast-meta {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--ink-dim);
}

/* bottom nav editorial */
.bottom-nav {
  background: var(--paper);
  border-top: 1px solid var(--rule);
}
.nav-item.active {
  color: var(--forest);
}
.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: 4px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 2px;
  background: var(--forest);
}
```

## Phase 2: Mockup Pages — Stocks + Detail + Secondary
- [ ] Stocks page: summary strip chips → kicker style (mono uppercase, amber accent, rule-before pseudo) + sub-tabs (filter) → mono uppercase + active underline forest
- [ ] Stock card editorial: card-sym เป็น Fraunces serif 1.1rem bold + card-sector mono uppercase 0.65rem + card-nums mono จัด label/value ผ่าน dotted divider + card-tags ใช้ .tag editorial (border 1px solid ข้าง + soft bg + mono uppercase 0.62rem)
- [ ] Score circle: เปลี่ยนเป็น rectangle chip border-forest/amber/burgundy + hard shadow 2px 2px 0 var(--paper-2) แทน circle soft — match editorial print feel
- [ ] Filtered card variant: left accent bar burgundy + burgundy-soft bg แทน red border เดิม
- [ ] Detail overlay nav-bar: section-num kicker style (№ 01 / STOCK DEEP DIVE) + serif title + 2 action buttons (star/block) ขวา — double border bottom
- [ ] Detail header: lede-style — serif headline 1.5rem bold + mono byline (sector · market cap) + score เป็น pull-quote ข้างขวา
- [ ] Quick-metrics 3x2 grid → stats-panel pattern: paper-3 bg + hard shadow 4px 4px 0 paper-2 + dotted divider ระหว่าง row + mono label / serif value
- [ ] Section titles (Buffett checklist / Yearly / Analysis): ใช้ .section-num pattern (№ 01 บนสุด mono + serif headline + rule underline forest)
- [ ] Checklist items: rule line dotted ระหว่าง item + checkmark forest pass / burgundy fail + mono label uppercase
- [ ] Yearly table: table.watch pattern — mono thead 0.68rem uppercase + thin rule + row hover paper-2
- [ ] Signal badges: .tag editorial (border 1px ข้าง + soft bg match signal type: compounder=forest / king=amber / cow=navy / trap=burgundy / warning=burgundy)
- [ ] DCA page form: mono labels uppercase + clean underline inputs (no border box, just bottom rule) + result cards = stats-panel pattern
- [ ] Requests page: input editorial + list items = hairline rule + mono timestamp + status chip editorial
- [ ] Settings page: 3 sections แยกด้วย rule line + mono labels + inputs underline style + primary button = .pipe-btn.primary (forest bg + hard shadow)

### Reference
```css
/* kicker pattern */
.kicker {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--amber);
  margin-bottom: 0.5rem;
}
.kicker::before {
  content: '';
  width: 20px;
  height: 2px;
  background: var(--amber);
}

/* editorial tag */
.tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  padding: 3px 7px;
  border: 1px solid var(--ink);
  border-radius: 2px;
  font-weight: 500;
  white-space: nowrap;
}
.tag.compounder { border-color: var(--forest); color: var(--forest); background: var(--forest-soft); }
.tag.king { border-color: var(--amber); color: var(--amber); background: var(--amber-soft); }
.tag.cow { border-color: var(--navy); color: var(--navy); background: var(--navy-soft); }
.tag.trap { border-color: var(--burgundy); color: var(--burgundy); background: var(--burgundy-soft); }

/* stats panel — hard shadow print feel */
.stats-panel {
  border: 1px solid var(--rule);
  padding: 1rem 1rem;
  background: var(--paper-3);
  box-shadow: 4px 4px 0 var(--paper-2);
}
.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 0.55rem 0;
  border-bottom: 1px dotted var(--line);
}
.stat-item:last-child { border-bottom: none; }
.stat-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--ink-dim);
}
.stat-value {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 1rem;
  font-weight: 700;
  color: var(--ink);
}

/* section number */
.section-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  letter-spacing: 0.2em;
  color: var(--forest);
  padding-bottom: 0.25rem;
  border-bottom: 1px solid var(--forest);
  display: inline-block;
  margin-bottom: 0.5rem;
}
```

## Phase 3: Port to Production mobile.html
- [ ] หลังมึง review mockup แล้วอนุมัติ — copy :root tokens + font loads + chrome CSS (masthead, bottom nav, FAB) จาก mockup ไปแทนใน mobile.html ส่วนที่ตรงกัน
- [ ] Port stock card + filter tabs + summary strip CSS — ตรวจว่า inline onclick handlers ยังทำงาน + renderCards() template ไม่ต้องแก้ class names
- [ ] Port detail overlay CSS — nav-bar, header, quick-metrics, section titles, checklist, yearly table, signal badges, analysis cards — ตรวจ renderDetail() ไม่ต้องแก้
- [ ] Port DCA + Requests + Settings CSS — ตรวจ form wiring (submitRequest, runDCA, saveSettings) ยัง work
- [ ] Polish pass: ดู contrast บน cream bg (red/green readable ไหม), touch targets ≥44px ทุกปุ่ม, safe-area insets (top+bottom) ยังคง, test iOS Safari + Chrome Android viewport จริง
- [ ] ลบ web/mockup-mobile-editorial.html + route ออก (ไม่ต้องคา production) + update CHANGELOG.md (bump v3.3.2) + update projects/MaxMahon/CLAUDE.md ว่า mobile ก็เป็น editorial แล้ว
