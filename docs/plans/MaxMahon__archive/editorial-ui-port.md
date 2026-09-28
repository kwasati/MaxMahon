---
project: MaxMahon
created: 2026-04-18
last_updated: 2026-04-18
status: done
---

# Max UI → Editorial Design Port

> ยก UI ของ Max จาก dashboard style ปัจจุบัน → editorial magazine (Fraunces + IBM Plex Sans Thai + JetBrains Mono, paper/ink/forest/amber/burgundy) ตาม mockup/max-editorial.html ทำทีละ phase — ต้องไม่ให้ live app พัง (API binding, Chart.js, tab handlers, scheduler, #analysis-section async, state colors ยังทำงานครบ)

## Phase 1: Design Foundation
- [x] แก้ web/index.html: เปลี่ยน font import เป็น Fraunces + IBM Plex Sans Thai + JetBrains Mono (เก็บ Sarabun ไว้เป็น fallback ชั่วคราว จะลบใน P8)
- [x] แก้ web/style.css :root — เพิ่ม tokens: --paper, --paper-2, --paper-3, --ink, --ink-2, --ink-dim, --ink-soft, --line, --line-strong, --rule, --forest, --forest-soft, --burgundy, --burgundy-soft, --amber, --amber-soft, --gold, --navy, --navy-soft
- [x] ตั้ง body font-family = 'IBM Plex Sans Thai', Georgia, serif | bg = var(--paper) | color = var(--ink) | line-height 1.55
- [x] เพิ่ม utility class .mono (JetBrains Mono + font-variant-numeric: tabular-nums) และ .serif (Fraunces)
- [x] คง token เก่าไว้ก่อน (--bg, --surface, --text, --accent, --border เดิม) เป็น alias ชี้ token ใหม่ (--bg: var(--paper); --text: var(--ink); --accent: var(--forest); --border: var(--line))
- [x] CRITICAL — เพิ่ม legacy color alias ให้ครบ: --green: var(--forest); --blue: var(--navy); --red: var(--burgundy); --yellow: var(--amber); --orange: var(--amber); --purple: var(--gold) — เพราะ app.js บรรทัด 147/156/160 ใช้ inline style.color = 'var(--green)' / 'var(--blue)' / 'var(--red)' ถ้าไม่ alias summary stats จะเป็นสีเทาหมด
- [x] เช็คด้วย grep ใน web/app.js ว่ามี --green/--blue/--red/--yellow อีกกี่ที่ ที่อาจพลาด (inline style, className ไฮไลท์) — document ใน commit message
- [x] Test ใน browser: refresh live app ยังทำงานครบทุกปุ่ม สี+font เปลี่ยนเป็น paper tone แต่ layout เดิม — สีหมวด summary card ต้องยังถูก (forest/navy/burgundy ไม่เทา)

### Reference
```css
/* web/style.css */
:root {
  /* new editorial tokens */
  --paper: #f4f0e6; --paper-2: #ebe5d4; --paper-3: #ffffff;
  --ink: #121420; --ink-2: #2a2d3d; --ink-dim: #595c6b; --ink-soft: #8e8f9c;
  --line: #d6cfbd; --line-strong: #b0a98c; --rule: #1a1a22;
  --forest: #1d5b4f; --forest-soft: #e4ede8;
  --amber: #b45309; --amber-soft: #f7eadb;
  --burgundy: #a02143; --burgundy-soft: #f5e3e7;
  --gold: #c89b2c; --navy: #1f3f76; --navy-soft: #e5ebf5;

  /* legacy aliases — keep until P8 cleanup */
  --bg: var(--paper); --surface: var(--paper-3); --surface2: var(--paper-2);
  --text: var(--ink); --text2: var(--ink-2); --text3: var(--ink-soft);
  --accent: var(--forest); --border: var(--line); --border2: var(--line-strong);
  /* CRITICAL: inline style.color in app.js depends on these */
  --green: var(--forest); --blue: var(--navy); --red: var(--burgundy);
  --yellow: var(--amber); --orange: var(--amber); --purple: var(--gold);
  --green-light: var(--forest-soft); --blue-light: var(--navy-soft);
  --red-light: var(--burgundy-soft); --yellow-light: var(--amber-soft);
}
body { font-family: 'IBM Plex Sans Thai', Georgia, serif; background: var(--paper); color: var(--ink); line-height: 1.55; }
.mono { font-family: 'JetBrains Mono', monospace; font-variant-numeric: tabular-nums; }
.serif { font-family: 'Fraunces', Georgia, serif; }
```

## Phase 2: Masthead & Section Nav
- [x] แก้ web/index.html: ลบ .header เดิม ใส่ <header class='masthead'> 3-col — left=vol/issue/date+SET index, center=Max Mahon title+sub, right=scanned/passed/auto-schedule
- [x] เก็บ id='header-meta' ไว้บน .mast-meta container เพื่อ app.js renderHeaderMeta() ยัง getElementById ได้ — แต่เปลี่ยน inner HTML เป็น 3 div (vol+issue / weekday+date / SET index)
- [x] แก้ app.js renderHeaderMeta(): populate 3 slot ด้านใน #header-meta + 2 slot ใน .mast-right (scanned, passed) — ใช้ innerHTML rewrite หรือ querySelector target แต่ละ data-field
- [x] เพิ่ม <nav class='sec-nav'> ใต้ masthead ใช้ #tabs เป็น container ภายใน — เก็บ .tab + data-tab + data-type attrs ทุกปุ่ม
- [x] Sticky strategy (FIX — ห้าม hardcode top: 108px): ใช้ sticky container pattern — wrap <header class='masthead'> + <nav class='sec-nav'> ด้วย <div class='mast-sticky'> แล้วให้ wrapper สติก top:0 เดียว ไม่ต้องคำนวณ height (มือถือ/desktop ใช้ได้เหมือนกัน)
- [x] CSS: .mast-sticky { position: sticky; top: 0; z-index: 50; background: var(--paper); backdrop-filter: blur(16px); border-bottom: 1px solid var(--rule); } — ลบ sticky/top/z-index ออกจาก .masthead และ .sec-nav แต่ละตัว
- [x] CSS masthead border-bottom: 3px double var(--rule) ภายใน wrapper, sec-nav border-bottom 1px solid line
- [x] CSS .tab.active: border-bottom 2px solid var(--forest), color var(--ink); .tab: color var(--ink-dim), uppercase, Fraunces, letter-spacing 0.05em
- [x] Test: click tab ทุกปุ่ม → stock-section / page-panel สลับถูก, pipeline-bar show/hide ตาม type, sticky ตามเลื่อน scroll ไม่มี gap ทั้ง desktop + mobile 720px

### Reference
```html
<div class="mast-sticky">
  <header class="masthead">
    <div class="mast-inner">
      <div class="mast-meta" id="header-meta">
        <div>VOL. III · ISSUE <strong data-field="issue">№ 17</strong></div>
        <div><span data-field="weekday">SUN</span> · <strong data-field="date">18 APR 2026</strong></div>
        <div>SET <strong class="mono" data-field="set-index">1,412.08</strong></div>
      </div>
      <div class="mast-title"><h1 class="serif"><em>Max</em> Mahon</h1><div class="sub">The Weekly Dividend &amp; Quality Review</div></div>
      <div class="mast-right">
        <div class="issue">AUTO · <span data-field="next-run">พรุ่งนี้ 09:00</span></div>
        <div>SCANNED <strong class="mono" data-field="scanned">—</strong></div>
        <div>PASSED <strong class="mono" data-field="passed">—</strong></div>
      </div>
    </div>
  </header>
  <nav class="sec-nav">
    <div class="sec-nav-inner" id="tabs">
      <button class="tab active" data-tab="passed" data-type="stock">ผ่านเกณฑ์</button>
      <!-- ... ทุก tab เดิม -->
    </div>
  </nav>
</div>
```
```css
.mast-sticky { position: sticky; top: 0; z-index: 50; background: var(--paper); backdrop-filter: blur(16px) saturate(140%); }
.masthead { border-bottom: 3px double var(--rule); padding: 1.5rem 0 1.25rem; }
.sec-nav { border-bottom: 1px solid var(--rule); }
```

## Phase 3: Lede + Stats Panel
- [x] แก้ web/index.html: ลบ .summary-row 4-card — ใส่ <section class='lede'> 2-col = left(kicker+h2+lede-body+byline), right=<aside class='stats-panel'>
- [x] Headline h2 = Fraunces 900 clamp(2rem, 4.2vw, 3.5rem), มี em italic สี forest
- [x] lede-body = Fraunces serif 1.2rem + drop cap (::first-letter float, Fraunces 900 3.5em, forest color)
- [x] stats-panel = 5 rows: ผ่านเกณฑ์ (pos), คะแนนเฉลี่ย, yield เฉลี่ย watchlist (pos), ค้นพบใหม่, warnings (warn) — ใช้ .mono ค่าตัวเลข
- [x] แก้ app.js renderSummary(): เปลี่ยน selector จาก '#summary-row .summary-card' → document.querySelectorAll('.stats-panel [data-stat]') 5 slot (passed, avg-score, avg-yield, discoveries, warnings)
- [x] renderSummary ใส่ className .pos / .warn ตามเงื่อนไขเดิม (warnings > 0 → warn, passed > 0 → pos) แทนการเซ็ต inline style.color (ให้ CSS class จัดการสีแทน — อ่านง่ายกว่าและ theme ตามได้)
- [x] Handle empty state (API ยังไม่ response): default placeholder '—' ใน HTML แล้ว renderSummary override ทีหลัง
- [x] Test: refresh → ค่าสถิติ populate ถูก drop cap แสดง, warnings > 0 ขึ้นสี burgundy, mobile 1024px → stack 1-col

### Reference
```html
<section class="lede">
  <div>
    <div class="kicker">THIS WEEK'S THESIS · ISSUE 17</div>
    <h2 class="serif">เมื่อดอกเบี้ยลด<br/>คุณภาพ <em>คือราคาจริง</em><br/>ของการถือยาว.</h2>
    <div class="lede-body serif">SET ปิดที่ 1,412 จุด โมเมนตัมสัปดาห์นี้...</div>
    <div class="byline mono">ANALYSIS BY MAX · CLAUDE OPUS 4.7</div>
  </div>
  <aside class="stats-panel">
    <div class="stats-head serif">At a glance</div>
    <div class="stat-item"><span class="stat-label">หุ้นที่ผ่านเกณฑ์</span><span class="stat-value mono" data-stat="passed">—</span></div>
    <div class="stat-item"><span class="stat-label">คะแนนคุณภาพเฉลี่ย</span><span class="stat-value mono" data-stat="avg-score">—</span></div>
    <div class="stat-item"><span class="stat-label">Yield เฉลี่ย (watchlist)</span><span class="stat-value mono" data-stat="avg-yield">—</span></div>
    <div class="stat-item"><span class="stat-label">ค้นพบใหม่</span><span class="stat-value mono" data-stat="discoveries">—</span></div>
    <div class="stat-item"><span class="stat-label">ข้อมูลต้องตรวจสอบ</span><span class="stat-value mono" data-stat="warnings">—</span></div>
  </aside>
</section>
```
```js
// app.js renderSummary()
const slot = (k) => document.querySelector(`.stats-panel [data-stat="${k}"]`);
slot('passed').textContent = passedCount;
slot('passed').classList.toggle('pos', passedCount > 0);
slot('warnings').textContent = warnings;
slot('warnings').classList.toggle('warn', warnings > 0);
// ...
```

## Phase 4: Watchlist Editorial Table
- [x] แก้ HTML: เปลี่ยน .stock-list จาก grid-mode cards → <table class='watch'> thead + tbody — เก็บ id='stock-list' ไว้บน <tbody>
- [x] Columns: Stock (sym+name), Signal (tag pills), Score (bar+num), Yield, 5y Yield, P/E, D/E, ROE, Streak, Price
- [x] แก้ app.js render function (บรรทัด ~228-280): สร้าง <tr data-sym='X'> แทน div.stock-card — ใส่ 10 <td> ตาม column order
- [x] CRITICAL — แก้ app.js querySelectorAll('.stock-card') ทุกที่ (บรรทัด 284 + 368 + ที่อื่น) → querySelectorAll('tr[data-sym]') เพื่อ hover highlight + click handler ยังทำงาน
- [x] ใส่ .tag variants: .compounder (forest), .king (amber), .cow (navy), .contra (gold), .trap (burgundy — score <50 ใช้คู่กัน)
- [x] score-bar = div.score-bar > i ความกว้าง % inline style สี forest default; ถ้า score<50 → burgundy-soft bg + burgundy bar
- [x] States ใน tbody (CRITICAL):
- Loading: <tr class='state-row'><td colspan='10'><div class='loading-state'>กำลังโหลด…</div></td></tr>
- Empty: <tr class='state-row'><td colspan='10'><div class='empty-state'>ไม่มีหุ้นในรายการ</div></td></tr>
- Error: <tr class='state-row'><td colspan='10'><div class='error-state' style='color:var(--burgundy)'>โหลดข้อมูลไม่ได้ · <a href='#' onclick='location.reload()'>ลองใหม่</a></div></td></tr>
- เพิ่ม CSS: .state-row td { padding: 3rem; text-align: center; font-family: 'Fraunces', serif; font-style: italic; color: var(--ink-dim); }
- [x] Sort select ย้ายเป็น link editorial ใต้ section-head (SORTED BY · QUALITY ↓) — เก็บ logic #sort-select (hidden select + label click เปิด native dropdown หรือ custom dropdown)
- [x] Update section-head: .section-num (№ 01 / WATCHLIST) + h3 + .section-sort right
- [x] CSS responsive 720px: hide th/td:nth-child(n+6) (เหลือ Stock/Signal/Score/Yield/Price)
- [x] Test: scroll table, click row → detail เปิด, sort เปลี่ยน order, tab passed/watchlist/filtered ทำงานครบ, loading/empty/error state แสดงถูกตอนเรียก API มือ (ปิด network ทดลอง)

### Reference
```html
<div class="section-head">
  <span class="section-num mono">№ 01 / WATCHLIST</span>
  <h3 class="serif">หุ้นที่ผ่านเกณฑ์ <em>สัปดาห์นี้</em></h3>
  <span class="section-sort mono">SORTED BY · <a href="#" id="sort-toggle">QUALITY ↓</a></span>
</div>
<div class="watch-wrap">
  <table class="watch">
    <thead><tr><th>Stock</th><th>Signal</th><th>Score</th><th>Yield</th>...</tr></thead>
    <tbody id="stock-list">
      <tr class="state-row"><td colspan="10"><div class="loading-state">กำลังโหลด…</div></td></tr>
    </tbody>
  </table>
</div>
```
```js
// app.js — hover + click handlers update
document.querySelectorAll('tr[data-sym]').forEach(row => {
  row.addEventListener('click', () => selectStock(row.dataset.sym));
});
```
```css
.state-row td { padding: 3rem 1rem; text-align: center; font-family: 'Fraunces', serif; font-style: italic; color: var(--ink-dim); border-bottom: none; }
.state-row .error-state { color: var(--burgundy); }
.state-row .error-state a { color: var(--forest); border-bottom: 1px solid var(--forest); }
```

## Phase 5: Deep Dive Detail Panel
- [x] Refactor #detail: 2-col = left <div class='dive-body'> (kicker+h2+deck+prose+pull-quote+#analysis-section), right <aside class='dive-aside'> (fact-sheet + 2-3 mini-chart)
- [x] แก้ app.js renderDetail() (บรรทัด ~691): สร้าง fact-sheet 12 rows — Sector, Market cap, ROE 5y avg, Net margin, D/E, Payout, Dividend streak, FCF yield, Interest coverage, P/E trailing, P/E forward, Quality score
- [x] ใส่ <blockquote class='pull-quote'> render จาก analysis.insight field (ถ้ามีใน report JSON) — fallback ใช้ data คำนวณเช่น 'Score X ติดอันดับ top Y% ของ universe' ถ้าไม่มี insight
- [x] CRITICAL — #analysis-section preservation: renderDetail ต้องคง <div id='analysis-section' class='analysis-section'><div class='analysis-loading'>กำลังวิเคราะห์...</div></div> ใน dive-body (ใต้ pull-quote) เพราะ fetchAnalysis() บรรทัด 860 เรียก getElementById('analysis-section') ทันทีหลัง detail เปิด
- [x] Restyle .analysis-section / .analysis-card / .analysis-loading ให้ตรง editorial — .analysis-card bg=paper-3 border=line padding=1.25rem + border-left 2px forest, heading Fraunces serif, body Plex
- [x] CRITICAL — canvas sizing: .mini-chart canvas { width: 100%; height: 160px; } — Chart.js responsive ต้องมี wrapper dimension ชัด ไม่งั้นวาดเป็น 0
- [x] Update Chart.js global theme (Chart.defaults): backgroundColor transparent, scales.x/y.grid.color var(--line), ticks.color var(--ink-dim), font family 'JetBrains Mono' size 10
- [x] divChart: forest area fill (gradient 0.35→0 opacity) + forest line + last point highlight white stroke
- [x] roeChart: amber line + amber dots, baseline ROE 15% dashed line var(--burgundy)
- [x] revenueChart: navy bars + average line var(--amber)
- [x] CSS .mini-chart wrapper: paper-3 bg + rule border + shadow offset 4px 4px 0 paper-2 + padding 1.25rem
- [x] Test: click stock 5+ ตัว detail update ครบ, chart ทั้ง 3 วาดสี editorial + มีขนาด height 160px, #analysis-section โหลด + แสดงผล AI ถูกต้อง, responsive 1024px stack 1-col

### Reference
```html
<div id="detail" class="dive">
  <div class="dive-body">
    <div class="dive-kicker mono">DEEP DIVE · AOT</div>
    <h2 class="serif">AOT: <em>สนามบินที่พิมพ์เงินได้.</em></h2>
    <div class="dive-deck">คะแนน 91 ไม่ใช่โชค...</div>
    <p>ถ้ามีหุ้นที่ <strong>Buffett น่าจะรัก</strong>...</p>
    <blockquote class="pull-quote">"หุ้นดีไม่ต้อง yield สูง"<cite class="mono">— Max Analysis</cite></blockquote>
    <!-- CRITICAL: #analysis-section must stay for fetchAnalysis() -->
    <div id="analysis-section" class="analysis-section">
      <div class="analysis-loading serif">กำลังวิเคราะห์...</div>
    </div>
  </div>
  <aside class="dive-aside">
    <div class="fact-sheet">
      <div class="fact-head"><span class="mono">Fact sheet</span><span class="fact-symbol serif">AOT</span></div>
      <div class="fact-row"><span class="k">Sector</span><span class="v mono">Transportation</span></div>
      <!-- 12 rows -->
    </div>
    <div class="mini-chart"><div class="mini-head mono"><span>Dividend per share · 10Y</span><span>฿/share</span></div><canvas id="divChart"></canvas></div>
    <div class="mini-chart"><canvas id="roeChart"></canvas></div>
    <div class="mini-chart"><canvas id="revenueChart"></canvas></div>
  </aside>
</div>
```
```css
.mini-chart { background: var(--paper-3); border: 1px solid var(--rule); box-shadow: 4px 4px 0 var(--paper-2); padding: 1.25rem; }
.mini-chart canvas { width: 100% !important; height: 160px !important; display: block; }
.analysis-section { margin-top: 1.5rem; }
.analysis-card { background: var(--paper-3); border: 1px solid var(--line); border-left: 2px solid var(--forest); padding: 1.25rem; margin-bottom: 0.75rem; }
.analysis-card h4 { font-family: 'Fraunces', serif; font-weight: 700; }
```

## Phase 6: Discovery Strip + Signal Legend
- [x] Discoveries tab (data-tab='discoveries'): เปลี่ยน layout → <section class='discoveries'> bg=paper-2 + section head (№ 03 / DISCOVERY + disc-title+em) + 3-col .disc-grid
- [x] .disc-card: sym (Fraunces 900 1.8rem) + name + 4 metrics grid (Score/ROE/Yield/Streak mono) + tag pill ล่าง
- [x] Hover state: border forest + translateY(-2px)
- [x] แก้ app.js renderDiscoveries() สร้าง <article class='disc-card' data-sym='X'> markup (ไม่ใช่ .stock-card)
- [x] FIX — Signal Legend ตำแหน่ง: ย้าย <section class='legend-block'> ออกไปวางนอก #stock-section (หลัง page-panel ทั้งหมด ก่อน <footer>) เพื่อให้เห็นทุก tab — legend อธิบาย tag ที่ใช้ทั้งระบบ (watchlist, discovery, detail)
- [x] แต่ละ .leg = border-top 2px ink + .leg-head (mono uppercase สีตาม tag) + <p> Fraunces italic — 4 col desktop, 2 col 1024px, 1 col 720px
- [x] States สำหรับ discoveries-list: loading/empty/error เหมือน P4 (Fraunces italic, paper-3 bg card placeholder)
- [x] Test: สลับ tab discoveries เห็น editorial strip ถูก, legend อธิบาย tag ครบ, legend ปรากฏทุก tab (ไม่ซ่อนตอน tab อื่น)

### Reference
```html
<!-- ภายใน #stock-section -->
<section class="discoveries" data-subpage="discoveries">
  <div class="discoveries-inner">
    <div class="disc-head">
      <div>
        <div class="disc-title serif">ค้นพบใหม่ <em>สัปดาห์นี้</em></div>
        <div class="disc-dek serif">3 ตัวที่ Claude คัดจาก screener</div>
      </div>
      <span class="section-num mono">№ 03 / DISCOVERY</span>
    </div>
    <div class="disc-grid" id="discoveries-list">
      <!-- rendered by renderDiscoveries() -->
    </div>
  </div>
</section>

<!-- CRITICAL: legend วางนอก #stock-section / page-panel ทั้งหมด -->
<section class="legend-block">
  <div class="leg"><div class="leg-head forest mono">Compounder</div><p class="serif">ROE ≥20% + rev CAGR ≥10% + payout &lt;60%</p></div>
  <div class="leg"><div class="leg-head amber mono">Dividend King</div><p class="serif">yield ≥5% + payout 30-70% + streak ≥5 ปี</p></div>
  <div class="leg"><div class="leg-head navy mono">Cash Cow</div><p class="serif">FCF yield &gt;8% + payout &lt;70% + D/E &lt;0.5</p></div>
  <div class="leg"><div class="leg-head burgundy mono">Yield Trap</div><p class="serif">yield &gt;8% + ROE ลด + payout &gt;100%</p></div>
</section>

<footer>...</footer>
```

## Phase 7: Secondary Pages (Requests, DCA, Settings)
- [x] Requests page: wrap .search-section + .request-panel ด้วย editorial tokens (bg=paper-3, border=rule 1px, shadow offset 4px paper-2, padding 1.75rem)
- [x] Search presets = .tag pill style (border + uppercase mono + เปลี่ยนสีตาม preset — dividend=amber, growth=forest, value=burgundy, quality=navy)
- [x] Search input+select: bg=paper, border=line-strong, font-family JetBrains Mono, ink color
- [x] Search results card = mini fact-sheet style (paper-3 + shadow)
- [x] Search results loading/empty/error states: เหมือน P4 pattern (Fraunces italic placeholder)
- [x] DCA panel: heading Fraunces 1.8rem, labels JetBrains mono uppercase, dca-toggle ปรับ slider minimal ink+forest (off=line, on=forest)
- [x] DCA results Chart.js: ใช้ theme จาก P5 — forest area fill invested / amber portfolio value line
- [x] Settings: settings-section = .fact-sheet border+shadow, inputs mono, toggle forest, save button = ink pill (bg ink, color paper, uppercase mono, letter-spacing)
- [x] ห้ามแก้ logic app.js ใน phase นี้ — แค่ class + CSS override
- [x] Test: run search preset + custom filter, compute DCA, save schedule — ทุก function เหมือนเดิม, loading/empty/error state ปรากฏถูก

### Reference
```css
.search-section, .request-panel, .dca-panel, .settings-panel {
  background: var(--paper-3);
  border: 1px solid var(--rule);
  box-shadow: 4px 4px 0 var(--paper-2);
  padding: 1.75rem; margin-bottom: 2rem;
}
.search-section h3, .dca-panel h3, .settings-panel h3 {
  font-family: 'Fraunces', serif; font-weight: 900;
  font-size: 1.8rem; letter-spacing: -0.02em;
  border-bottom: 1px solid var(--line); padding-bottom: 0.75rem; margin-bottom: 1.25rem;
}
.search-section label, .dca-field label, .settings-field label {
  font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
  letter-spacing: 0.15em; text-transform: uppercase; color: var(--ink-dim);
}
.preset-btn {
  font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
  letter-spacing: 0.12em; text-transform: uppercase;
  border: 1px solid var(--ink); background: transparent; color: var(--ink);
  padding: 0.5rem 0.85rem; border-radius: 999px;
}
.preset-btn[data-preset="dividend"] { color: var(--amber); border-color: var(--amber); }
.preset-btn[data-preset="growth"] { color: var(--forest); border-color: var(--forest); }
.preset-btn[data-preset="value"] { color: var(--burgundy); border-color: var(--burgundy); }
.preset-btn[data-preset="quality"] { color: var(--navy); border-color: var(--navy); }
input[type=number], input[type=text], select {
  font-family: 'JetBrains Mono', monospace;
  background: var(--paper); border: 1px solid var(--line-strong);
  color: var(--ink); padding: 0.55rem 0.75rem; border-radius: 4px;
}
.settings-save { background: var(--ink); color: var(--paper); font-family: 'JetBrains Mono', monospace; text-transform: uppercase; letter-spacing: 0.15em; padding: 0.75rem 1.5rem; border: none; border-radius: 999px; }
```

## Phase 8: Polish & Ship
- [x] Mobile breakpoint 1024px: lede+dive stack 1-col, disc-grid 2-col, legend-block 2-col
- [x] Mobile breakpoint 720px: masthead 1-col center, sec-nav wrap + overflow-x: auto, watch table hide cols 6-10, disc-grid 1-col, legend 1-col, footer stack
- [x] ลบ legacy color alias token ทีละตัว (--green, --blue, --red, --yellow, --orange, --purple) หลัง grep ยืนยันว่าไม่มีที่ใช้แล้ว — ถ้ายังมีให้แก้ inline style/className ไปใช้ .pos/.warn/.info class ก่อน
- [x] ลบ CSS เก่าที่ไม่ใช้ออกจาก style.css: .summary-card, .stock-card, .grid-mode, .header เดิม, Sarabun font import (ถ้า migrate เสร็จ), legacy token อื่นๆ
- [x] cache bust __CB__ ใน index.html (ปรับ version) — หรือตรวจว่า server.py inject timestamp ยังทำงาน
- [x] เพิ่ม <footer> editorial: left=Max branding + schedule info, right=copyright + 'Designed with Claude Opus 4.7' + disclaimer 'Not investment advice'
- [x] เขียน CHANGELOG.md: version bump v3.3.0, สรุป editorial UI port (masthead, lede, watch table, deep dive, discovery, legend, secondary pages polish, responsive)
- [x] Smoke test ครบ flow: page load → watchlist scroll/sort → click stock 5 ตัว → detail + 3 charts + analysis-section โหลด → switch ทุก tab (passed/watchlist/discoveries/filtered/requests/DCA/settings) → pipeline button run (fetch/analyze/screen/weekly) → mobile 720px view → ปิด network ทดสอบ error state → refresh ตรวจ state row
- [x] Commit สุดท้าย + push

### Reference
```markdown
# CHANGELOG

## v3.3.0 — 2026-04-18 · Editorial UI Port
- UI overhauled to editorial magazine design
- Masthead (vol/issue/date + title + scanned/passed) with unified sticky wrapper
- Lede section with drop cap + stats panel sidebar
- Watchlist as editorial table (score bar, tag pills, loading/empty/error states)
- Deep dive 2-col: prose + fact sheet + 3 mini charts (editorial palette) + #analysis-section preserved
- Discovery strip + global signal legend block
- Secondary pages (Requests/DCA/Settings) retheme
- Typography: Fraunces + IBM Plex Sans Thai + JetBrains Mono
- Palette: paper / ink / forest / amber / burgundy / navy
- Removed legacy color aliases (--green/--blue/--red/--yellow/--orange/--purple) + old .summary-card/.stock-card/.header styles
- All functionality preserved (API bindings, Chart.js, scheduler, DCA compute, SSE events, analysis-section async)
```
