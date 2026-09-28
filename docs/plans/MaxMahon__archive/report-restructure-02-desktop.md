---
project: MaxMahon
created: 2026-04-24
last_updated: 2026-04-24
status: done
---

# Report Page Restructure — Desktop (report.js)

> Part 2 of 3 — Desktop restructure: redesign hero (symbol+tags | price+verdict chip+score pill), move Deep Analyze to top as money-shot with 2x2 grid + full-width Max-to-อาร์ท panel, remove 3 duplicates (The Case / Reasons / Pattern section), merge Reasons into enriched 5-5-5-5 checklist (5-col), convert Pattern to <details> footnote, strip vintage newspaper (byline, 3px double borders, column-count, italic abuse, emoji icons → SVG), re-order sections (hero → Deep Analyze → Score → 5-5-5-5 → Key Numbers → Dividend → History → Exit → Pattern footnote). | Index: report-restructure-index
> Depends on: report-restructure-01-foundation
> Parallel-safe with: none

## Phase 1: Hero redesign + Deep Analyze money-shot
- [x] สร้าง function `_renderHero(stock, patterns)` ใน `projects/MaxMahon/web/v6/static/js/pages/report.js` (place before _renderTheCase, ~line 74) แทน `_renderArticleHead` + `_renderPriceHero` — horizontal hero ใช้ class `.report-hero`: left = symbol(big) + name(italic secondary) + sector + tags(.tag), right = price(mono big, id=`v6-hero-price`) + as-of(small mono dim) + score pill (id=`v6-hero-score`, format 'XX/100') + verdict chip (id=`v6-hero-verdict`, class `.v6-verdict-chip` + variant based on stock.narrative.verdict). Empty verdict → chip 'ยังไม่ได้วิเคราะห์' class .empty. Scope: **ห้ามลบ** `_renderArticleHead` ยัง — Task 2 phase 2 ค่อยลบ call site. Acceptance: DevTools Elements → `.report-hero` 2-col grid; verdict chip visible ถ้า stock.narrative.verdict มีค่า; empty state แสดง 'ยังไม่ได้วิเคราะห์' italic dim
- [x] แก้ `_renderDeepAnalyze` (report.js บรรทัด 473) + `_renderAnalyzeResult` (บรรทัด 510) + `_renderAnalyzeInitialInner` (บรรทัด 481) + `_renderAnalyzeLoadingInner` (บรรทัด 490) + `_renderAnalyzeErrorInner` (บรรทัด 500) ใช้ class `.v6-deep-analyze` + `.v6-deep-verdict-bar` + `.v6-deep-grid` (2x2) + `.v6-deep-section` + `.v6-deep-talk-panel`. ลบ `max-width:640px` + `margin-left:auto;margin-right:auto`. แทน emoji icons 5 ตัว (💵💎🏛️⚖️💬) ที่ใช้ใน `_section()` helper (บรรทัด 531) + art-talk span (บรรทัด 551) ด้วย `window.MMUtils.svg('banknote')` / `svg('gem')` / `svg('landmark')` / `svg('scale')` / `svg('message-circle')`. ลบ inline styles ที่ layout — keep inline เฉพาะ dynamic (verdict badge color ตาม BUY/HOLD/SELL). Scope: **ห้ามเปลี่ยน** logic `_wireDeepAnalyze` / `_pollAnalysis` / `_attachClick` — แค่ HTML structure + classes. Acceptance: Deep Analyze card full-width บน 1440px viewport; 2x2 grid แสดง 4 neutral sections; Max-to-อาร์ท panel full-width ด้านล่างพร้อม pillar-badge; icons เป็น SVG ไม่ใช่ emoji (verify ผ่าน DevTools Elements: `<svg>` not `<span>` with emoji char)
- [x] แก้ `_wireDeepAnalyze(sym)` (report.js บรรทัด 739-791) เพิ่ม call `_applyHeroVerdict(payload.verdict)` ทุกครั้งที่ได้ analyze result — (a) หลัง `_load_cached_narrative` return ใน initial load (`block.innerHTML = _renderAnalyzeResult(cached);` then call _applyHeroVerdict), (b) หลัง POST success (`block.innerHTML = _renderAnalyzeResult(payload);` then call), (c) หลัง poll success (`block.innerHTML = _renderAnalyzeResult(r);` then call). Helper `_applyHeroVerdict(verdict)` อยู่ใน Task 1 Phase 1 reference แล้ว. Scope: **ห้ามแตะ** polling interval / timeout / cache logic — แค่เพิ่ม DOM update call. Acceptance: หลังกด 'ขอวิเคราะห์เพิ่มเติม' → analysis คืนมา → hero verdict chip ขึ้น class + label ใหม่ทันที (no page refresh needed); verify via browser console: `document.getElementById('v6-hero-verdict').outerHTML` เปลี่ยนหลัง click

### Reference
```javascript
// new _renderHero in report.js (replaces _renderArticleHead + _renderPriceHero)
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
        '<h1 style="font-family:var(--font-head);font-weight:900;font-size:clamp(2rem,4vw,3rem);letter-spacing:-0.02em;line-height:1;margin:0;color:var(--fg-primary)">' + sym + '</h1>' +
        '<div style="font-size:var(--fs-md);color:var(--fg-secondary)">' + name + (sector ? ' · ' + sector : '') + '</div>' +
        '<div style="display:flex;gap:6px;flex-wrap:wrap">' + tags + '</div>' +
      '</div>' +
      '<div class="report-hero-right">' +
        '<div class="report-hero-price">' + priceStr + '<span style="font-size:var(--fs-sm);color:var(--fg-dim);margin-left:6px">THB</span></div>' +
        (asOf ? '<div style="font-family:var(--font-mono);font-size:var(--fs-xs);color:var(--fg-dim);letter-spacing:0.08em;text-transform:uppercase">' + esc(asOf) + '</div>' : '') +
        '<div style="display:flex;gap:var(--sp-2);align-items:center">' +
          '<span style="font-family:var(--font-mono);font-size:var(--fs-sm);color:var(--fg-dim)">Score</span>' +
          '<span id="v6-hero-score" style="font-family:var(--font-mono);font-size:var(--fs-md);font-weight:700;color:var(--fg-primary)">' + Math.round(score) + '/100</span>' +
        '</div>' +
        '<div id="v6-hero-verdict">' + verdictHtml + '</div>' +
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
  var el = document.getElementById('v6-hero-verdict');
  if (el) el.innerHTML = _buildVerdictChip(verdict);
}

// new Deep Analyze block using classes
function _renderDeepAnalyze() {
  return '<section class="v6-deep-analyze" id="v6-deep-analyze">' + _renderAnalyzeInitialInner() + '</section>';
}
```

## Phase 2: Remove duplicates (The Case, Reasons, Pattern section)
- [x] ลบ function `_renderTheCase(stock)` (report.js บรรทัด 125-154) ทั้ง function + ลบ call site ใน `_buildReportHtml` (บรรทัด 590 `_renderTheCase(stock) +`). Scope: **ห้ามลบ** `narrative.case_text` ที่ใช้ใน backend — keep cache logic intact. Acceptance: grep `_renderTheCase` ใน report.js ไม่เจอ match เลย; open `/report/QH.BK` → ไม่มี section '01 · The Case' + ไม่มี byline 'By Max Mahon' + ไม่มี 2-column newspaper text
- [x] แก้ function `_renderChecklist(stock)` (report.js บรรทัด 197-241) เป็น `_renderChecklistEnriched(stock)` รองรับ 5-col grid: label | actual | threshold | mark | reason. Add helper `_matchReasonFor(keys)` ที่ match keyword (yield, streak, eps, P/E, P/BV, market cap) กับ item ใน stock.reasons_narrative. ใช้ class `.v6-checklist-item` + `.v6-check-label/actual/threshold/mark/reason`. Update section-head ใช้ `.v6-section-head` ใหม่: `<div class="v6-section-head"><h2>5-5-5-5 Test</h2><small>Hard Filters · Pass All or Fail</small></div>`. แล้วลบ `_renderReasonsGrid` (บรรทัด 243-267) + ลบ call site ใน `_buildReportHtml` (บรรทัด 593). Scope: **ห้ามเปลี่ยน** threshold logic (yld>=5, streak>=5, etc) — เฉพาะ HTML structure + new reason matching. Acceptance: checklist แสดง 5 cols บน 1440px; แต่ละ row มี reason text แนบข้าง ถ้า match keyword ได้; ไม่มี section 'Reasons' แยกอีก
- [x] สร้าง function `_renderPatternFootnote(patterns)` (ใหม่, report.js) render `<details class="v6-pattern-footnote">` — summary คือ 'Reference: {pattern_tag} pattern' / body คือ narrative text + source link. Handle empty case: return '' ถ้าไม่มี matched_patterns. ลบ function เก่า `_renderPatternSection` (บรรทัด 269-296). Update call site ใน `_buildReportHtml` (บรรทัด 594): replace `_renderPatternSection(patterns) +` ด้วย `_renderPatternFootnote(patterns) +` และย้าย call ไปก่อน `foot` (after _renderExitBaseline). Scope: ไม่ต้องแก้ `/api/stock/{sym}/patterns` endpoint. Acceptance: หุ้นที่ match pattern → ท้ายหน้ามี `<details>` collapsible; คลิกขยายเห็น narrative; หุ้นไม่มี pattern → ไม่มี footnote element (grep document.querySelector('.v6-pattern-footnote') → null)

### Reference
```javascript
// new _renderChecklistEnriched in report.js
function _renderChecklistEnriched(stock) {
  var metrics = stock.screener_metrics || {};
  var fallback = stock;
  function _get(key) { return metrics[key] != null ? metrics[key] : fallback[key]; }
  var yld = _get('dividend_yield');
  var pe = _get('pe') == null ? fallback.pe_ratio : _get('pe');
  var pb = _get('pb_ratio') == null ? fallback.pb_ratio : _get('pb_ratio');
  var mcap = _get('mcap') == null ? fallback.market_cap : _get('mcap');
  var streak = stock.dividend_streak_years || metrics.dividend_streak_years || metrics.div_streak;
  var epsPos = stock.eps_positive_count != null ? stock.eps_positive_count : metrics.eps_positive_count;
  var reasons = stock.reasons_narrative || stock.reasons || [];
  function _matchReasonFor(keys) {
    for (var i = 0; i < reasons.length; i++) {
      var r = typeof reasons[i] === 'string' ? reasons[i] : (reasons[i].text || '');
      var low = r.toLowerCase();
      for (var k = 0; k < keys.length; k++) { if (low.indexOf(keys[k]) !== -1) return r; }
    }
    return '';
  }
  function _item(label, actual, threshold, pass, keys) {
    var reason = _matchReasonFor(keys);
    var markCls = pass ? 'pass' : 'fail';
    var markIcon = pass ? '✓' : '✗';
    return (
      '<div class="v6-checklist-item">' +
        '<div class="v6-check-label">' + label + '</div>' +
        '<div class="v6-check-actual">' + actual + '</div>' +
        '<div class="v6-check-threshold">' + threshold + '</div>' +
        '<div class="v6-check-mark ' + markCls + '">' + markIcon + '</div>' +
        '<div class="v6-check-reason">' + window.MMUtils.escapeHtml(reason) + '</div>' +
      '</div>'
    );
  }
  return (
    '<div class="v6-section-head"><h2>5-5-5-5 Test</h2><small>Hard Filters · Pass All or Fail</small></div>' +
    '<div class="v6-checklist">' +
      _item('Dividend Yield', (yld == null ? '—' : window.MMUtils.fmtPercent(yld)), '≥ 5.00%', yld != null && yld >= 5, ['yield', 'ปันผล']) +
      _item('Dividend Streak', (streak == null ? '—' : (streak + ' yrs')), '≥ 5 yrs', streak != null && streak >= 5, ['streak', 'ติดต่อกัน', 'จ่ายปันผล']) +
      _item('EPS Positive (5y)', (epsPos == null ? '—' : (epsPos + ' / 5')), 'No loss years', epsPos != null && epsPos >= 5, ['eps', 'ขาดทุน']) +
      _item('P/E', (pe == null ? '—' : (window.MMUtils.fmtNum(pe, 1) + '×')), '≤ 15×', pe != null && pe <= 15, ['p/e', 'pe', 'earnings']) +
      _item('P/BV', (pb == null ? '—' : (window.MMUtils.fmtNum(pb, 2) + '×')), '≤ 1.5×', pb != null && pb <= 1.5, ['p/bv', 'pbv', 'book']) +
      _item('Market Cap', (mcap == null ? '—' : window.MMUtils.fmtCompact(mcap) + ' THB'), '≥ 5B THB', mcap != null && mcap >= 5e9, ['mcap', 'market cap']) +
    '</div>'
  );
}

// new _renderPatternFootnote
function _renderPatternFootnote(patterns) {
  var matched = (patterns && patterns.matched_patterns) || [];
  if (!matched.length) return '';
  var esc = window.MMUtils.escapeHtml;
  var blocks = matched.map(function (p) {
    var src = p.source ? '<div class="src">Source: ' + esc(p.source) + '</div>' : '';
    return '<details class="v6-pattern-footnote"><summary>Reference: ' + esc(p.tag) + ' pattern</summary><p>' + esc(p.narrative || '') + '</p>' + src + '</details>';
  }).join('');
  return blocks;
}
```

## Phase 3: Vintage cleanup + section re-order
- [x] แก้ functions ที่เหลือใน report.js — `_renderScoreBreakdown` (บรรทัด 156-195), `_renderKeyNumbers` (298-336), `_renderDividendHistory` (338-367), `_renderScoreHistory` (369-414), `_renderExitBaseline` (416-471) — ทั้งหมดทำ 4 อย่าง: (a) แทน 2-line section-num HTML `<div class="section-num"><span class="no">...</span><span>...</span></div>` ด้วย `<div class="v6-section-head"><h2>Title</h2><small>Subtitle</small></div>`, (b) แทน inline grid template styles (score-block, chart-pair, exit-grid, exit-panel) ด้วย class names `.v6-score-block` + `.v6-score-display` + `.v6-score-huge` + `.v6-score-slash` + `.v6-score-version` + `.v6-chart-pair` + `.v6-chart-box` + `.v6-chart-caption` + `.v6-exit-panel` + `.v6-exit-grid` + `.v6-exit-cell`, (c) ลบทุก `border:3px double` + `font-style:italic` ที่ไม่ใช่ chart-caption, (d) ลบ `_renderArticleHead` (บรรทัด 74-104) + `_renderPriceHero` (บรรทัด 106-123) เก่าทิ้งทั้ง function (Task phase 1 replace ด้วย `_renderHero` แล้ว). Scope: **ห้ามแก้** `_mountCharts` / `_ensureChartJs` / `_wireDeepAnalyze` / chart options. Acceptance: grep `3px double` ใน report.js ไม่เจอ; grep `column-count` ใน report.js ไม่เจอ; grep `font-style:italic` ใน report.js ไม่เกิน 1 แห่ง (chart-caption เท่านั้น); ทุก section-num class replaced ด้วย v6-section-head
- [x] แก้ `_buildReportHtml(stock, patterns, history, exitStatus)` (report.js บรรทัด 581-602) จัด section order ใหม่ตาม sequence: `_renderHero(stock, patterns)` + `_renderDeepAnalyze()` + `_renderScoreBreakdown(stock)` + `_renderChecklistEnriched(stock)` + `_renderKeyNumbers(stock)` + `_renderDividendHistory(stock)` + `_renderScoreHistory(history)` + `_renderExitBaseline(exitStatus)` + `_renderPatternFootnote(patterns)` + foot. ลบ call `_renderArticleHead`, `_renderTheCase`, `_renderReasonsGrid`, `_renderPatternSection` ออกทั้งหมด. ลบ inline style ของ `foot` ที่มี `3px double` ใน template var — เปลี่ยนเป็น simple border-top 1px border-subtle. Scope: **ห้ามเพิ่ม** section ใหม่ — เอาแค่ที่ list. Acceptance: open `/report/QH.BK` → order จริง: hero (symbol+price+verdict), Deep Analyze result (BUY + 4 sections + Max-to-อาร์ท), Score 69/100 + donut, 5-5-5-5 enriched, Key Numbers table, Dividend History, Score History, Exit Baseline (ถ้าใน watchlist), Pattern footnote `<details>` ท้ายสุด

## Phase 4: Smoke test + validate desktop
- [x] Validation 3 scenarios ที่ **localhost:50089** (production max.intensivetrader.com ทดสอบเมื่อ Karl approve) บน browser 1440px viewport: (a) `/report/QH.BK` (cached analysis, in-watchlist) → ทุก section render ครบ + verdict=BUY chip ใน hero + Max-to-อาร์ท panel full-width + 5-5-5-5 grid 5-col + Pattern footnote collapsed ท้ายหน้า + Exit Baseline visible, (b) `/report/BBL.BK` (cached analysis, might not be in watchlist) → Exit Baseline แสดง 'Not in Watchlist' state หรือ hide; ส่วนอื่นปกติ, (c) `/report/PTT.BK` หรือหุ้นที่ยังไม่ได้ analyze → Deep Analyze section แสดง CTA button 'ขอวิเคราะห์เพิ่มเติม' + hero verdict chip = 'ยังไม่ได้วิเคราะห์' empty state + หลังกดปุ่มรอ 30-60s → result ปรากฏใน Deep Analyze + hero verdict chip update เป็น BUY/HOLD/SELL. Verify: (i) console ไม่มี error, (ii) **no duplicate content — visual inspection**: ข้อความ to_art (Max คุยกับอาร์ท) ไม่ปรากฏซ้ำ 2 ที่บนหน้า; verify ด้วยตา scroll ทั้งหน้า + count `document.querySelectorAll('.v6-deep-talk-panel').length === 1` + count `document.querySelectorAll('.case-body,.case-cols').length === 0` (old class หายแล้ว), (iii) responsive 900px breakpoint → Deep Analyze grid collapse 1-col (DevTools resize viewport ดู). Scope: **ห้ามแก้** report.mobile.js ใน plan นี้ (Plan 03 ค่อยทำ). Acceptance: screenshot 3 scenarios แปะ Karl ให้ดู; ถ้า Karl approve → merge + mark plan done
