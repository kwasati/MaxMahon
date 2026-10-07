---
project: MaxMahon
created: 2026-04-24
last_updated: 2026-04-24
status: done
---

# Report Page Restructure — Mobile (report.mobile.js)

> Part 3 of 3 — Mobile port: mirror desktop changes to report.mobile.js (function names DIFFER from desktop: mobile uses _renderScore, _renderPattern, NO _renderReasonsGrid — keep mobile-specific names, don't force rename). Same CSS classes + same section order + mobile-responsive 1-col layouts via CSS @media query + validate at 375px viewport + submodule commit workflow. | Index: report-restructure-index
> Depends on: report-restructure-02-desktop
> Parallel-safe with: none

## Phase 1: Mobile port — mirror desktop structural changes (function names differ)
- [x] **Function name mapping (mobile vs desktop — DIFFERENT):** mobile file ใช้ชื่อสั้นลง ไม่ต้อง rename ให้ตรง desktop — ใช้ชื่อเดิมของ mobile แต่อัพเดท implementation: (a) `_renderScore` (mobile:136) → อัพเดท implementation ใช้ class `.v6-score-block` + `.v6-score-display` + `.v6-score-huge` (ชื่อ function ยังเป็น `_renderScore`), (b) `_renderPattern` (mobile:182) → **rename เป็น `_renderPatternFootnote`** + เปลี่ยน implementation เป็น `<details class="v6-pattern-footnote">` (เพราะ semantic เปลี่ยน — หน้าที่เปลี่ยนจาก section หลัก → footnote), (c) **_renderReasonsGrid ไม่มีใน mobile** — skip การลบ, ไม่ต้องทำอะไร (reasons อยู่ใน `_renderChecklist` implicit แล้ว หรือไม่มีในมือถือ). **ตรวจสอบก่อนแก้:** agent ต้อง Read ไฟล์จริงที่ `projects/MaxMahon/web/v6/static/js/pages/report.mobile.js` แล้วรัน grep เช็ค function name ให้ตรง ก่อนแก้
- [x] แก้ `projects/MaxMahon/web/v6/static/js/pages/report.mobile.js` port changes จาก desktop ตาม mapping ข้อบน: (a) สร้าง function `_renderHero(stock, patterns)` ใหม่ แทน `_renderArticleHead` (mobile:74) + `_renderPriceHero` (mobile:95) — ใช้ class `.report-hero` (CSS @media max-width:900px จะ stack 1-col อัตโนมัติจาก components.css) + id=`v6-mhero-verdict` (mobile prefix, NOT v6-hero-verdict) + id=`v6-mhero-score` + id=`v6-mhero-price` + helper `_buildVerdictChip(v)` และ `_applyHeroVerdict(v)` (ใช้ id mobile prefix), (b) ลบ `_renderTheCase` (mobile:114) ทั้ง function — ซ้ำ duplicate เหมือน desktop, (c) ลบ `_renderArticleHead` (mobile:74) + `_renderPriceHero` (mobile:95) ทั้ง function — replaced by `_renderHero` แล้ว, (d) แก้ `_renderDeepAnalyze` (mobile:284) + `_renderAnalyzeResult` (mobile:321) + 3 inner helpers (mobile:292,301,311) — ใช้ class `.v6-deep-analyze` + `.v6-deep-grid` (CSS collapse 1-col mobile) + SVG icons 5 ตัว (mobile:362,381-384) ผ่าน `window.MMUtils.svg('banknote')` / `svg('gem')` / `svg('landmark')` / `svg('scale')` / `svg('message-circle')` แทน emoji, (e) แก้ `_renderChecklist` (mobile:148) — rename เป็น `_renderChecklistEnriched` + อัพเดท 5-col grid + reason matching logic เหมือน desktop (ใช้ class `.v6-checklist-item` — CSS mobile @media จะจัด grid-template-columns 1fr auto auto auto + check-reason full-width row 2 อัตโนมัติ), (f) แก้ `_renderPattern` (mobile:182) — rename เป็น `_renderPatternFootnote` + เปลี่ยน implementation เป็น `<details class="v6-pattern-footnote">` เหมือน desktop, (g) แก้ `_renderScore` (mobile:136), `_renderKeyNumbers` (mobile:205), `_renderDividendHistory` (mobile:236), `_renderScoreHistory` (mobile:245), `_renderExitBaseline` (mobile:254) — แทน old `.section-num` HTML ด้วย `.v6-section-head` + class layout (.v6-score-block / .v6-chart-pair / .v6-exit-panel / .v6-exit-grid / .v6-exit-cell). Scope: **ห้ามแก้** canvas ID prefix (`v6-m*` ทุก chart) / chart options / polling logic / API fetch / `_hasAnalysisData` / `_stopPoll`. **ห้ามสร้าง** CSS ใหม่ — ใช้ class ที่มีอยู่แล้วจาก Plan 01. Acceptance: grep `_renderTheCase|_renderArticleHead|_renderPriceHero|_renderReasonsGrid|_renderPatternSection` ใน report.mobile.js → 0 matches; grep `_renderHero|_renderChecklistEnriched|_renderPatternFootnote` → เจอทุกตัว; canvas IDs `v6-mscore-chart/v6-mdps-chart/v6-mscorehist-chart` ยังอยู่
- [x] แก้ `_buildMobileReportHtml(stock, patterns, history, exitStatus)` (mobile:390-402) set section order ใหม่: `_renderHero(stock, patterns)` + `_renderDeepAnalyze()` + `_renderScore(stock)` + `_renderChecklistEnriched(stock)` + `_renderKeyNumbers(stock)` + `_renderDividendHistory(stock)` + `_renderScoreHistory(history)` + `_renderExitBaseline(exitStatus)` + `_renderPatternFootnote(patterns)` + foot. **หมายเหตุ:** mobile ใช้ `_renderScore` (ไม่ใช่ `_renderScoreBreakdown`) — ให้ keep เดิม, ไม่ต้อง rename. Scope: **ห้ามเพิ่ม** section ใหม่. Acceptance: grep `_renderTheCase` `_renderPatternSection` ใน report.mobile.js ไม่เจอ; _buildMobileReportHtml call sequence ตรงตามที่กำหนด (9 section + foot); viewport 375px load `/m/report/QH.BK` → render ครบทุก section

### Reference
```javascript
// report.mobile.js — new _renderHero (mobile prefix IDs v6-mhero-*)
function _renderHero(stock, patterns) {
  var esc = window.MMUtils.escapeHtml;
  var sym = esc(stock.symbol || '');
  var name = esc(stock.name || '');
  var sector = esc(stock.sector || '');
  var signals = stock.signals || [];
  var tags = '';
  if (signals.indexOf('NIWES_5555') !== -1) tags += '<span class="tag primary">Niwes 5-5-5-5</span>';
  if (signals.indexOf('QUALITY_DIVIDEND') !== -1) tags += '<span class="tag">Quality Dividend</span>';
  if (signals.indexOf('HIDDEN_VALUE') !== -1) tags += '<span class="tag">Hidden Value</span>';
  if (signals.indexOf('DEEP_VALUE') !== -1) tags += '<span class="tag">Deep Value</span>';
  if (patterns && (patterns.case_study_tags || []).length) tags += '<span class="tag">' + esc(patterns.case_study_tags[0]) + '</span>';
  var metrics = stock.screener_metrics || stock.metrics || {};
  var price = metrics.current_price != null ? metrics.current_price : stock.price;
  var priceStr = price == null ? '—' : '฿' + window.MMUtils.fmtNum(price, 2);
  var asOf = stock.price_as_of ? ('ราคาวันที่ ' + window.MMUtils.fmtDateThaiShort(stock.price_as_of)) : '';
  var score = stock.quality_score != null ? stock.quality_score : (stock.score || 0);
  var narrative = stock.narrative || {};
  var verdictHtml = _buildVerdictChip(narrative.verdict);
  return (
    '<section class="report-hero">' +
      '<div class="report-hero-left">' +
        '<h1 style="font-family:var(--font-head);font-weight:900;font-size:clamp(1.6rem,8vw,2.4rem);letter-spacing:-0.02em;line-height:1;margin:0;color:var(--fg-primary)">' + sym + '</h1>' +
        '<div style="font-size:var(--fs-sm);color:var(--fg-secondary)">' + name + (sector ? ' · ' + sector : '') + '</div>' +
        '<div style="display:flex;gap:6px;flex-wrap:wrap">' + tags + '</div>' +
      '</div>' +
      '<div class="report-hero-right">' +
        '<div class="report-hero-price" id="v6-mhero-price">' + priceStr + '<span style="font-size:var(--fs-sm);color:var(--fg-dim);margin-left:6px">THB</span></div>' +
        (asOf ? '<div style="font-family:var(--font-mono);font-size:var(--fs-xs);color:var(--fg-dim);letter-spacing:0.08em;text-transform:uppercase">' + esc(asOf) + '</div>' : '') +
        '<div style="display:flex;gap:var(--sp-2);align-items:center">' +
          '<span style="font-family:var(--font-mono);font-size:var(--fs-sm);color:var(--fg-dim)">Score</span>' +
          '<span id="v6-mhero-score" style="font-family:var(--font-mono);font-size:var(--fs-md);font-weight:700;color:var(--fg-primary)">' + Math.round(score) + '/100</span>' +
        '</div>' +
        '<div id="v6-mhero-verdict">' + verdictHtml + '</div>' +
      '</div>' +
    '</section>'
  );
}
function _buildVerdictChip(verdictRaw) {
  if (!verdictRaw) return '<span class="v6-verdict-chip empty">ยังไม่ได้วิเคราะห์</span>';
  var v = String(verdictRaw).trim();
  var cls = 'hold', label = 'HOLD';
  if (/^\s*BUY\b/i.test(v)) { cls = 'buy'; label = 'BUY'; }
  else if (/^\s*SELL\b/i.test(v)) { cls = 'sell'; label = 'SELL'; }
  return '<span class="v6-verdict-chip ' + cls + '">' + label + '</span>';
}
function _applyHeroVerdict(verdict) {
  var el = document.getElementById('v6-mhero-verdict');
  if (el) el.innerHTML = _buildVerdictChip(verdict);
}

// new _buildMobileReportHtml (mobile keeps _renderScore, not _renderScoreBreakdown)
function _buildMobileReportHtml(stock, patterns, history, exitStatus) {
  var esc = window.MMUtils.escapeHtml;
  var foot = '<div class="page-foot" style="padding:var(--sp-5) 0;text-align:center;color:var(--fg-dim);font-size:var(--fs-xs);border-top:1px solid var(--border-subtle);margin-top:var(--sp-6)">End · ' + esc(stock.symbol || '') + '</div>';
  return (
    _renderHero(stock, patterns) +
    _renderDeepAnalyze() +
    _renderScore(stock) +
    _renderChecklistEnriched(stock) +
    _renderKeyNumbers(stock) +
    _renderDividendHistory(stock) +
    _renderScoreHistory(history) +
    _renderExitBaseline(exitStatus) +
    _renderPatternFootnote(patterns) +
    foot
  );
}
```

## Phase 2: Mobile responsive verification at 375px
- [x] เปิด DevTools → Device Toolbar → iPhone 12 Pro (390px) และ iPhone SE (375px) แล้วเปิด `http://localhost:50089/m/report/QH.BK` ตรวจ 6 จุด: (a) ไม่มี horizontal scroll (body width ≤ viewport width — verify: `document.body.scrollWidth <= window.innerWidth`), (b) Deep Analyze 4 sections stack 1-col (ไม่ใช่ 2x2) — verify `document.querySelector('.v6-deep-grid')` computed style `grid-template-columns` = `1fr`, (c) Score block stack: huge number ด้านบน + chart ด้านล่าง (grid 1-col), (d) 5-5-5-5 checklist — แต่ละ row show 2 rows (label+actual+threshold+mark แถวบน, reason full-width แถวล่าง — grid-template-rows: auto auto), (e) bottom of page เห็น Pattern footnote `<details>` + ไม่ถูก bottom-nav บัง (bottom-nav 88px + safe-area padding จาก mobile.css), (f) Deep Analyze CTA button min-height ≥ 48px (touch target). Scope: **ห้ามแก้** mobile.css โดยไม่จำเป็น — ถ้า responsive ยังพังต้องเพิ่ม rule ใน components.css @media query เท่านั้น (ไม่ใช่ mobile.css). Acceptance: screenshot viewport 375px แปะ Karl; ไม่มี horizontal scroll; bottom content มีระยะ safe-area-inset-bottom จาก bottom-nav

## Phase 3: Smoke test 3 scenarios + submodule commit + ship
- [x] Validation 3 scenarios ที่ **localhost:50089** บน mobile 375px viewport: (a) `/m/report/QH.BK` (cached analysis, in watchlist) → ทุก section มี + verdict chip ใน hero + Deep Analyze stack 1-col, (b) `/m/report/BBL.BK` → Exit Baseline state render, (c) `/m/report/{unanalyzed}` → CTA button visible + กดแล้วรอ 30-60s → verdict chip update ทั้งใน hero และ Deep Analyze card. Verify: console no error + no horizontal scroll + no broken chart rendering + ข้อความ to_art ไม่ปรากฏซ้ำ 2 ที่ (visual inspection). Scope: **ห้าม** commit ถ้ายังมี console error หรือ horizontal scroll. Acceptance: screenshot 3 scenarios แปะ Karl ให้ดู + Karl approve
- [x] **Submodule commit workflow (บังคับ)** — MaxMahon เป็น git submodule ของ parent WORKSPACE repo: (1) `cd projects/MaxMahon` → `git add web/v6/static/js/pages/report.mobile.js` (+ ไฟล์อื่นที่แก้) → `git commit -m 'ui(report): mobile port restructure — remove duplicates + migrate to Robinhood dark + verdict chip'`, (2) `cd ../..` (กลับไป WORKSPACE root) → `git add projects/MaxMahon` (update submodule pointer) → `git commit -m 'build(maxmahon-report-restructure): bump submodule — mobile port Plan 03'`, (3) push ทั้ง 2 repos: `cd projects/MaxMahon && git push origin main && cd ../.. && git push origin main`. Scope: **ห้ามใช้** `git commit --no-verify` (hooks ต้อง pass) + **ห้าม force push**. Acceptance: `git log -1 --oneline` ใน submodule แสดง commit ใหม่; `git log -1 --oneline` ใน parent แสดง commit pointer update; `git status` ทั้ง 2 repos = clean; notify ผ่าน telegram_alert ถ้า Karl setup
