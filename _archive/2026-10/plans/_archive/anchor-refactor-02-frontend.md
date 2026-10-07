---
project: 4-MaxMahon
created: 2026-05-18
last_updated: 2026-05-18
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: เปิด web/v6 page (https://max.intensivetrader.com หรือ localhost:50089) เห็นคะแนน anchor 0.0-10.0 (1 decimal) + 4-pillar breakdown chart (Dividend/Cashflow/Moat/Long Hold) + disqualified state ชัดเจน + คะแนน 5 pillar เก่าหายจาก UI

### รายละเอียด
- Update home.js + home.mobile.js: score chip แสดง display_score 0.0-10.0 (1 decimal) แทน 100 pts integer + show disqualified marker (DISQUALIFIED tag/badge)
- Update report.js + report.mobile.js: score breakdown chart 4 pillar (Dividend/Cashflow/Moat/Long_hold) แทน 5 pillar (Dividend/Valuation/Cash Flow/Hidden Value/Track Record) + show penalty tags + disqualify_tags ถ้ามี
- Update web/v6/static/css/components.css ถ้า pillar count change กระทบ layout (chart size, color count, etc.)
- PILLAR_SPEC array ใน report.js: เปลี่ยน 5 entries เป็น 4 entries — keys: dividend, cashflow, moat, long_hold + max points 35/25/25/15 + label Thai labels
- Mobile chart (report.mobile.js): doughnut 4 segments แทน 5 + modifier display (penalty if exists)
- Display score: ตอนนี้ data จาก /api/screener มี display_score field (Plan 01 backend) — JS อ่านตรง field นี้
- Disqualified candidates: home.js + report.js แสดงป้าย 'DISQUALIFIED' + reason tag (FAKE_PROFIT/CASHFLOW_DETERIORATING/MOAT_ERODING)
- Backward compat: ไม่ต้อง keep — old breakdown keys (valuation/hidden_value/track_record) หายจาก UI
- Old score 100 pts: ลบจาก display — แสดง 0.0-10.0 เท่านั้น
- UI verification: อาร์ทเปิดเว็บดูเองหลัง build (per /build skill rule)
- หน้าที่กระทบ: home (latest scan list) + report (per-stock detail) — desktop + mobile แยกไฟล์ตาม DESIGN.md split

### Scope Boundary
**In scope:**
- projects/4-MaxMahon/web/v6/static/js/pages/home.js
- projects/4-MaxMahon/web/v6/static/js/pages/home.mobile.js
- projects/4-MaxMahon/web/v6/static/js/pages/report.js
- projects/4-MaxMahon/web/v6/static/js/pages/report.mobile.js
- projects/4-MaxMahon/web/v6/static/css/components.css — ถ้าจำเป็น

**Out of scope:**
- Other JS pages: portfolio.js, settings.js, watchlist.js — preserve (separate concerns)
- shared/tokens.css + base.css — design tokens unchanged
- Python backend (Plan 01 done)
- Data cleanup + fresh scan (Plan 03)

### Non-goals
- ไม่ keep old pillar UI parallel — replace entirely
- ไม่ change navigation / page structure / routing
- ไม่ refactor portfolio/watchlist/settings pages (not score-display related)
- ไม่ redesign color tokens / themes

# Anchor Refactor — Frontend (4 JS + CSS)

> Part 2 of 3 — Frontend refactor. Update 4 JS pages + CSS เพื่อแสดง anchor 0.0-10.0 + 4-pillar breakdown แทน 5-pillar score เก่า. | Index: anchor-refactor-index
> Depends on: anchor-refactor-01-backend (API returns new schema)
> Parallel-safe with: none — must come after Plan 01

## Phase 1: home.js + home.mobile.js — score chip display
- [x] แก้ projects/4-MaxMahon/web/v6/static/js/pages/home.js — score chip in candidate card แสดง display_score (0.0-10.0, 1 decimal) แทน score integer + handle disqualified state (badge 'DISQUALIFIED' + reason tag) — scope: ไม่แตะ pending_candidates section (filter-07 done), ไม่แตะ filter chips, ไม่แตะ trend strip — Acceptance: เปิด /v6/desktop/ + scan candidates show '7.5' format + disqualified show 'DISQUALIFIED' badge clearly
- [x] แก้ projects/4-MaxMahon/web/v6/static/js/pages/home.mobile.js — same changes for mobile (smaller chip, layout adjusted for mobile) — scope: ไม่แตะ other sections — Acceptance: เปิด /v6/m/ + scan candidates show display format + disqualified marker

### Reference
```javascript
// current home.js — find score render (likely in _buildHomeHtml or candidate render)
// score = c.score (0-100 integer)
// example: '<div class="score-chip">' + c.score + '</div>'

// new
const displayScore = c.display_score ?? (c.score / 10).toFixed(1);
const disqualified = c.disqualified === true;
let chipHtml;
if (disqualified) {
    const dqTags = (c.disqualify_tags || []).join(', ');
    chipHtml = `<div class="score-chip disqualified" title="${dqTags}">DISQUALIFIED</div>`;
} else {
    chipHtml = `<div class="score-chip">${displayScore}</div>`;
}
```

**Note:** Adapt to actual existing markup pattern. Read home.js + home.mobile.js to find score chip render location.

## Phase 2: report.js + report.mobile.js — 4-pillar breakdown
- [x] แก้ projects/4-MaxMahon/web/v6/static/js/pages/report.js — PILLAR_SPEC array เปลี่ยน 5 entries -> 4 entries: dividend (35) + cashflow (25) + moat (25) + long_hold (15). Score breakdown section read stock.breakdown[key] (dividend/cashflow/moat/long_hold). Show penalty if exists. Show disqualify_tags if disqualified — scope: ไม่แตะ Max-to-Art conversational section, ไม่แตะ verdict, ไม่แตะ other report sections (metrics/dividend history/etc.) — Acceptance: เปิด /report/BBL หน้า desktop see 4-pillar breakdown + penalty tags + disqualified state if applicable
- [x] แก้ projects/4-MaxMahon/web/v6/static/js/pages/report.mobile.js — mobile chart doughnut 4 segments (was 5) + same 4-pillar display + mobile-adapted layout — scope: ไม่แตะ mobile-specific verdict/analysis sections — Acceptance: เปิด /m/report/BBL show 4-segment doughnut + breakdown

### Reference
```javascript
// current report.js around lines 151-176 _renderScoreBreakdown
const PILLAR_SPEC = [
    {key: 'dividend', label: 'ปันผล', max: 50},
    {key: 'valuation', label: 'ราคา', max: 25},
    {key: 'cash_flow', label: 'Cash Flow', max: 10},
    {key: 'hidden_value', label: 'Hidden Value', max: 5},
    {key: 'track_record', label: 'Track Record', max: 10},
];

// new (4 pillars anchor model)
const PILLAR_SPEC = [
    {key: 'dividend', label: 'ปันผล', max: 35},
    {key: 'cashflow', label: 'Cash Flow', max: 25},
    {key: 'moat', label: 'Moat', max: 25},
    {key: 'long_hold', label: 'ถือยาว+ทนวิกฤต', max: 15},
];

// Breakdown render — read from stock.breakdown[p.key]
PILLAR_SPEC.forEach(p => {
    const score = stock.breakdown?.[p.key] ?? 0;
    const percent = (score / p.max * 100).toFixed(0);
    // render bar / number
});

// Display score (0.0-10.0)
const displayScore = stock.display_score ?? (stock.score / 10).toFixed(1);

// Disqualified state
if (stock.disqualified) {
    const dqTags = (stock.disqualify_tags || []).join(', ');
    // show DISQUALIFIED banner with tags
}

// Penalty tags
const penaltyTags = stock.penalty_tags || [];
if (penaltyTags.length > 0) {
    // show penalty pills (e.g. CYCLICAL_BUSINESS -5)
}
```

**Mobile chart (report.mobile.js):** doughnut 4 segments. Colors: 4 distinct hues from existing palette. Center label = display_score.

## Phase 3: CSS layout adjustments (if needed)
- [x] Verify projects/4-MaxMahon/web/v6/static/css/components.css — check pillar grid layout (5 cols -> 4 cols?) + score chip styles (font size for 0.0-10.0 vs 100 pts) + disqualified state class (red border? grayscale?). ปรับ CSS เฉพาะที่จำเป็นจาก layout shift — scope: ไม่ redesign tokens, ไม่ touch shared/tokens.css — Acceptance: layout responsive ทั้ง desktop + mobile + disqualified state มี visual treatment ชัดเจน

### Reference
```css
/* Reference — actual changes depend on existing styles */
/* If 5-col grid: */
.pillar-grid { grid-template-columns: repeat(5, 1fr); }

/* Change to 4-col: */
.pillar-grid { grid-template-columns: repeat(4, 1fr); }

/* Add disqualified state: */
.score-chip.disqualified {
    background: var(--bg-danger, #dc2626);
    color: white;
    text-decoration: line-through;
    opacity: 0.7;
}
```

**Adapt to actual CSS structure.** Read components.css first to find pillar/score-related styles.
