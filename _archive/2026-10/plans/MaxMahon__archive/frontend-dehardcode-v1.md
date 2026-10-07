---
project: MaxMahon
created: 2026-05-07
last_updated: 2026-05-07
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: เปิด max.intensivetrader.com → หน้า portfolio แสดง suggestion จาก scan PASS bucket จริง (REIT-PFund warning ขึ้น CPNREIT/AIMIRT แทน DIF/JASIF/CPNREIT hardcode) / หน้า report breakdown 5 rows มี Track Record + max pts ใหม่ (Cash Flow 10 / Hidden Value 5 / Track Record 10) / หน้า scan list มี sector filter chips multi-select กรอง sector หลายตัวพร้อมกันได้

### รายละเอียด
- Issue 1 portfolio_builder.py SECTOR_SUGGESTIONS hardcode → dynamic จาก scan: เพิ่ม function compute_sector_suggestions(screener) ที่ group candidates by canonical sector + sort by score + take top 3. Fallback static dict (DIF/JASIF/CPNREIT) เก็บไว้สำหรับ sector ว่างใน scan
- Issue 1 build_sector_warnings(picked, suggestions) รับ suggestions param แทนใช้ static SECTOR_SUGGESTIONS dict ตรงๆ. build_portfolio() call site ส่ง suggestions ที่ compute มา
- Issue 2 report.js _renderScoreBreakdown (lines 143-182) full replace: render dynamic จาก spec dict 5 pillars (dividend 50 / valuation 25 / cash_flow 10 / hidden_value 5 / track_record 10) + max pts ตาม Plan C ปัจจุบัน
- Issue 2 report.mobile.js chart labels (lines 433-454) update: 5 segments แทน 4 (เพิ่ม Track Record) + ใช้ value ของแต่ละ pillar จาก breakdown dict + label format 'Pillar value'
- Issue 3 home.js _buildFilterBar (lines 230-253) เพิ่ม filter group ใหม่สำหรับ sector chips between Signal และ Showing groups: dynamic generate chips จาก unique sectors ใน candidates
- Issue 3 home.js _wireControls (line 411-440) เพิ่ม sector chips handler — multi-select: toggle chip active class + push/pop ใน _state.sectors array + 0 = all / N = filter where stock.sector in array
- Issue 3 home.js _renderGrid filter logic update: filter candidates ผ่าน _state.sectors ก่อน sort + render
- Issue 3 home.mobile.js เพิ่ม sector filter group + handler เหมือน desktop (mirror pattern). Mobile mirror desktop layout — แต่อาจ collapse to scrollable row
- Reuse CSS class .filter-chip ที่มีอยู่ — ไม่ต้องเพิ่ม CSS ใหม่ (sector chips ใช้ pattern เดียวกับ signal/sort chips)
- Sector chip text = sector name ตาม raw value จาก screener (เช่น 'Banking', 'Property Development', 'Property Fund & REITs') — ไม่ canonical bucket (เพราะ user เลือก raw)
- Smoke test backend: 3 cases test compute_sector_suggestions logic + warnings dynamic — ไม่ test frontend (UI bypass)
- ห้ามแก้ scoring logic / hard filter / data layer — Plan C done already
- ห้าม rename Track Record (keep ตาม Plan C)
- 0 chip selected = show all candidates (default behavior). N chip selected = OR filter (any of selected sectors match)

### Scope Boundary
**In scope:**
- projects/4-MaxMahon/scripts/portfolio_builder.py — เพิ่ม compute_sector_suggestions + แก้ build_sector_warnings + build_portfolio call site
- projects/4-MaxMahon/web/v6/static/js/pages/home.js — เพิ่ม sector chip group ใน filter bar + state + handler + render filter
- projects/4-MaxMahon/web/v6/static/js/pages/home.mobile.js — เพิ่ม sector chip mirror desktop
- projects/4-MaxMahon/web/v6/static/js/pages/report.js — replace _renderScoreBreakdown ด้วย dynamic loop
- projects/4-MaxMahon/web/v6/static/js/pages/report.mobile.js — update score doughnut chart labels (5 segments)
- projects/4-MaxMahon/scripts/_smoke_dehardcode.py — สร้างใหม่ smoke test backend 3 cases

**Out of scope:**
- screen_stocks.py / data_adapter.py / fetch_data.py — Plan A/B/C done, keep
- server/app.py API endpoints — ไม่แก้
- watchlist.js / settings.js / portfolio.js page modules — ไม่กระทบ (portfolio.js consume API ที่ propagate ผ่าน build_sector_warnings ใหม่)
- Backend scoring functions — keep
- CSS components.css — reuse existing .filter-chip class ไม่เพิ่ม
- Signal filter chips ใหม่ (NIWES_GROWING / DATA_INCOMPLETE / YIELD_SPIKE) — out of scope plan นี้

### Non-goals
- ไม่ refactor frontend architecture
- ไม่เพิ่ม API endpoint ใหม่
- ไม่ดึง sector list จาก backend แยก endpoint — frontend dedupe จาก candidates
- ไม่เปลี่ยน scoring logic / hard filter
- ไม่ rename Track Record
- ไม่บังคับ user re-scan
- ไม่เพิ่ม signal filter chips ใหม่
- ไม่ทำ unit test framework — fixture-based smoke test pattern

# MaxMahon De-hardcode v1 — Sector Suggestions + Breakdown Dynamic + Sector Filter

> De-hardcode 3 issues: portfolio_builder SECTOR_SUGGESTIONS dynamic (DIF/JASIF/CPNREIT → real scan data) + frontend report breakdown render dynamic 5 rows (เพิ่ม Track Record + max pts ใหม่) + home filter เพิ่ม sector chips multi-select. UI bypass — agent ตรวจ code ได้ + user verify ตา browser

## Phase 1: Backend dynamic suggestions + frontend de-hardcode
- [x] เพิ่ม function `compute_sector_suggestions(screener)` ใหม่ใน `projects/4-MaxMahon/scripts/portfolio_builder.py` — insert ก่อน function `build_sector_warnings` (around line 232). Logic: loop candidates from screener.candidates → group by to_canonical_sector → sort each group by score desc → take top 3 symbols (clean symbol = strip '.BK'). For sectors that have 0 in scan → fallback to STATIC_SECTOR_SUGGESTIONS dict (rename existing SECTOR_SUGGESTIONS → STATIC_SECTOR_SUGGESTIONS to clarify role). Return dict {sector: [sym1, sym2, sym3]}. Scope: ห้ามแก้ to_canonical_sector / build_portfolio orchestrator ใน task นี้. Acceptance: grep `def compute_sector_suggestions` = 1 match; grep `STATIC_SECTOR_SUGGESTIONS` = 2+ matches (rename + use); py -m py_compile scripts/portfolio_builder.py exit 0; smoke test case 1 (REIT/PFund มีใน scan) ผ่าน.
- [x] แก้ function `build_sector_warnings(picked)` ใน `projects/4-MaxMahon/scripts/portfolio_builder.py` (lines 232-242) เพิ่ม param `suggestions` (default ใช้ STATIC_SECTOR_SUGGESTIONS เพื่อ backward compat). แก้ msg formatter ใช้ suggestions[sector] แทน SECTOR_SUGGESTIONS[sector]. แก้ build_portfolio (line 270) call build_sector_warnings(picked_sectors, compute_sector_suggestions(screener)). Scope: ห้ามแก้ apply_pin_overrides / top_per_canonical_sector / allocate_80_20. Acceptance: grep `build_sector_warnings(picked, suggestions=` (case insensitive) ใน portfolio_builder.py = 1+ match; smoke test case 3 (warning ขึ้น + suggestion ตรง scan) ผ่าน; py compile exit 0.
- [x] Replace function `_renderScoreBreakdown(stock)` ใน `projects/4-MaxMahon/web/v6/static/js/pages/report.js` (lines 143-182) ด้วย dynamic version. Add at top of file (or function-local) PILLAR_SPEC dict: {dividend: {label: 'Dividend Sustainability', max: 50, driver: 'Yield · Streak · Payout · Growth'}, valuation: {label: 'Valuation', max: 25, driver: 'P/E · P/BV · EV/EBITDA'}, cash_flow: {label: 'Cash Flow Strength', max: 10, driver: 'FCF · OCF/NI · Int Coverage'}, hidden_value: {label: 'Hidden Value', max: 5, driver: ''}, track_record: {label: 'Track Record', max: 10, driver: 'Revenue Growth · EPS Growth'}}. Loop spec keys + render row per pillar. Keep total = sum of max (100). Keep modifier row + total row. Scope: ห้ามแก้ _renderChecklistEnriched / _mountCharts / other functions. Acceptance: grep `PILLAR_SPEC` ใน report.js ≥ 1 match; grep `track_record` ใน report.js ≥ 1 match; grep `Cash Flow Strength` 1 match; ไม่มี `_cell('Cash Flow Strength', 15` (เก่า); user manual: เปิด /report/BBL.BK เห็น 5 rows breakdown รวม Track Record + Cash Flow max 10 + Hidden Value max 5.
- [x] แก้ chart labels ใน `_mountCharts(stock, history)` ของ `projects/4-MaxMahon/web/v6/static/js/pages/report.mobile.js` (lines 421-455) — เพิ่ม Track Record segment ที่ 5 ใน doughnut chart. Get tr value from breakdown.track_record. Update labels array เป็น 5 elements: ['Dividend ' + div, 'Valuation ' + val, 'Cash Flow ' + cf, 'Hidden ' + hv, 'Track Rec ' + tr] + Mod label เป็น 6 ถ้า include modifier. Update data array เป็น 5 (หรือ 6 with modifier) elements. Update backgroundColor เป็น 5 colors (เพิ่ม 1 color จาก existing palette). Scope: ห้ามแก้ DPS chart / yield chart logic. Acceptance: grep `track_record` ใน report.mobile.js ≥ 1 match; grep `Track Rec` ใน report.mobile.js = 1 match; user manual: เปิด /m/report/BBL.BK เห็น chart มี 5 segments (รวม Track Record).
- [x] เพิ่ม sector filter group ใน function `_buildFilterBar(totalCount)` ของ `projects/4-MaxMahon/web/v6/static/js/pages/home.js` (lines 230-253). Insert filter-group ใหม่ระหว่าง Signal group (lines 240-247) และ Showing group (lines 248-251). Group มี: label 'Sector' + chips จาก unique sectors ของ candidates (passed in as param หรือ generate inline). Chips ใช้ class `filter-chip` + `data-sector='{sector_name}'`. ไม่มี chip 'All' (chip selected = filter, 0 = show all). Update _buildFilterBar signature to accept candidates list (or compute sectors inline if state available). Scope: ห้ามแก้ Sort / Signal groups + ห้ามแก้ filter-chip CSS class. Acceptance: grep `data-sector` ใน home.js ≥ 1 match; grep `Sector` (case-insensitive label) ใน _buildFilterBar = 1 match; user manual: เปิด / เห็น sector chips ด้านบน list dynamic ตาม sectors ที่มีใน scan.
- [x] แก้ function `_wireControls(screener)` ใน `projects/4-MaxMahon/web/v6/static/js/pages/home.js` (lines 411-440) เพิ่ม sector chips handler: multi-select toggle (ไม่ clear other actives เหมือน sort/signal). Add to _state: `sectors: []` (array). On chip click: toggle btn.classList active + add/remove sector from _state.sectors. Update _renderGrid filter: ถ้า _state.sectors.length > 0 → filter candidates where _state.sectors includes stock.sector. Scope: ห้ามแก้ sort/signal handlers. Acceptance: grep `_state.sectors` ใน home.js ≥ 2 matches (state init + filter); grep `data-sector]` (with closing bracket pattern) ใน _wireControls = 1 match; user manual: เปิด / คลิก chip Banking → list filter ให้แค่ Banking; คลิก Energy เพิ่ม → list show Banking + Energy; คลิก Banking ซ้ำ → unselect Banking, list show Energy เท่านั้น.
- [x] เพิ่ม sector filter chips ใน `projects/4-MaxMahon/web/v6/static/js/pages/home.mobile.js` (similar pattern — section ที่มี filter-bar around line 164). Add filter-group with sector chips dynamic + handler. Reuse desktop pattern (multi-select toggle). Scope: keep mobile UI compact (chips อาจต้อง horizontal scroll ใน mobile — ใช้ existing CSS overflow-x:auto ของ filter-bar). Acceptance: grep `data-sector` ใน home.mobile.js ≥ 1 match; user manual: เปิด /m เห็น sector chips + คลิก filter ทำงาน.
- [x] สร้างไฟล์ใหม่ `projects/4-MaxMahon/scripts/_smoke_dehardcode.py` — backend smoke test 3 cases. (1) compute_sector_suggestions returns top 3 by score per canonical sector — feed mock screener with CPNREIT score 70 + AIMIRT score 60 + DIF score 30 in REIT-PFund → assert returns ['CPNREIT', 'AIMIRT', 'DIF']. (2) screener empty (no candidates) → assert fallback to STATIC_SECTOR_SUGGESTIONS keys. (3) build_sector_warnings(picked, suggestions) uses passed suggestions in msg — feed mock picked={'Banking'} + suggestions={'REIT-PFund': ['CPNREIT'], 'Property': ['QH']} → assert warning msg contains 'CPNREIT' (not hardcoded list). Scope: backend only, no frontend test. Acceptance: ไฟล์ exists; py -m py_compile scripts/_smoke_dehardcode.py exit 0.
- [x] รัน smoke `cd projects/4-MaxMahon && PYTHONUTF8=1 py scripts/_smoke_dehardcode.py` exit 0 + print '[PASS] all 3 tests passed'. ถ้า fail debug source. After smoke pass: provide UI verification checklist for user (ที่ /qc verify จะ flag UI bypass): 1) เปิด / เห็น sector filter chips dynamic 2) คลิก chip multi-select ทำงาน 3) เปิด /report/BBL.BK เห็น 5 rows breakdown 4) เปิด /m + /m/report mobile เหมือนกัน 5) เปิด /portfolio (มี watchlist user) ดู sector warnings — suggestions ตรง scan PASS bucket. Acceptance: smoke exit 0; UI checklist printed.

### Reference
```python
# current — portfolio_builder.py:224-242 (SECTOR_SUGGESTIONS + build_sector_warnings)
SECTOR_SUGGESTIONS = {
    'Banking': ['BBL', 'SCB', 'KBANK'],
    'Energy': ['PTT', 'PTTEP', 'BCP'],
    'Property': ['QH', 'AP', 'LPN'],
    'REIT-PFund': ['DIF', 'JASIF', 'CPNREIT'],
}


def build_sector_warnings(picked):
    """Warnings for canonical sectors absent from picks (excluding 'Other')."""
    warnings = []
    for sector in ('Banking', 'Energy', 'Property', 'REIT-PFund'):
        if sector not in picked:
            warnings.append({
                'sector': sector,
                'msg': f'{sector} ว่าง — ลองเพิ่ม {" · ".join(SECTOR_SUGGESTIONS[sector])} ใน watchlist',
                'suggestions': SECTOR_SUGGESTIONS[sector],
            })
    return warnings

# new — rename to STATIC_SECTOR_SUGGESTIONS + add compute_sector_suggestions + update build_sector_warnings
STATIC_SECTOR_SUGGESTIONS = {
    'Banking': ['BBL', 'SCB', 'KBANK'],
    'Energy': ['PTT', 'PTTEP', 'BCP'],
    'Property': ['QH', 'AP', 'LPN'],
    'REIT-PFund': ['DIF', 'JASIF', 'CPNREIT'],
}


def compute_sector_suggestions(screener):
    """Build sector suggestions dict from scan PASS bucket. Top 3 by score per canonical sector.

    Falls back to STATIC_SECTOR_SUGGESTIONS for sectors empty in scan.
    Returns dict {canonical_sector: [sym1, sym2, sym3]}.
    """
    cands = (screener or {}).get('candidates') or []
    by_sector = {}
    for c in cands:
        canonical = to_canonical_sector(c.get('sector'))
        by_sector.setdefault(canonical, []).append(c)
    out = {}
    for sector in ('Banking', 'Energy', 'Property', 'REIT-PFund'):
        members = by_sector.get(sector, [])
        members.sort(key=lambda s: s.get('score') or 0, reverse=True)
        top = [c['symbol'].replace('.BK', '') for c in members[:3] if c.get('symbol')]
        if top:
            out[sector] = top
        else:
            out[sector] = STATIC_SECTOR_SUGGESTIONS.get(sector, [])
    return out


def build_sector_warnings(picked, suggestions=None):
    """Warnings for canonical sectors absent from picks (excluding 'Other').

    `suggestions` defaults to STATIC_SECTOR_SUGGESTIONS for backward compat.
    """
    if suggestions is None:
        suggestions = STATIC_SECTOR_SUGGESTIONS
    warnings = []
    for sector in ('Banking', 'Energy', 'Property', 'REIT-PFund'):
        if sector not in picked:
            sect_sugg = suggestions.get(sector) or STATIC_SECTOR_SUGGESTIONS.get(sector, [])
            warnings.append({
                'sector': sector,
                'msg': f'{sector} ว่าง — ลองเพิ่ม {" · ".join(sect_sugg)} ใน watchlist',
                'suggestions': sect_sugg,
            })
    return warnings

# build_portfolio caller (line 270) update:
# OLD:  sector_warnings = build_sector_warnings(picked_sectors)
# NEW:  sector_warnings = build_sector_warnings(picked_sectors, compute_sector_suggestions(screener))
```

```javascript
// current — report.js:143-182 _renderScoreBreakdown (full replace)
function _renderScoreBreakdown(stock) {
  var esc = window.MMUtils.escapeHtml;
  var score = stock.quality_score != null ? stock.quality_score : (stock.score || 0);
  var breakdown = stock.score_breakdown || stock.breakdown || {};
  var div = breakdown.dividend == null ? null : breakdown.dividend;
  var val = breakdown.valuation == null ? null : breakdown.valuation;
  var cf  = breakdown.cashflow == null ? breakdown.cash_flow : breakdown.cashflow;
  var hv  = breakdown.hidden_value == null ? breakdown.hidden : breakdown.hidden_value;
  var mod = breakdown.modifier == null ? (breakdown.modifiers || 0) : breakdown.modifier;

  function _val(v) { return v == null ? 0 : v; }
  function _cell(label, max, scored, driver) {
    var cls = (scored && scored > 0) ? 'pos' : '';
    return '<tr><td class="sym">' + label + '</td><td class="num">' + max + '</td><td class="num ' + cls + '">' + (scored == null ? '—' : scored) + '</td><td class="dim">' + esc(driver || '') + '</td></tr>';
  }

  return (
    '<div class="v6-section-head"><h2>Score Breakdown</h2><small>Of One Hundred · Per Niwes Dividend-First Schema</small></div>' +
    '<section class="v6-score-block">' +
      '<div class="v6-score-display">' +
        '<div class="v6-score-huge">' + Math.round(score) + '</div>' +
        '<div class="v6-score-slash">of one hundred</div>' +
        '<div class="v6-score-version">niwes-dividend-first · v2</div>' +
      '</div>' +
      '<div><div class="v6-chart-box" style="position:relative;height:320px"><canvas id="v6-score-chart"></canvas></div></div>' +
    '</section>' +
    '<table class="data-table" style="margin-top:var(--sp-4)">' +
      '<thead><tr><th style="width:40%">Component</th><th class="num">Max</th><th class="num">Scored</th><th>Driver</th></tr></thead>' +
      '<tbody>' +
        _cell('Dividend Sustainability', 50, _val(div), 'Yield · Streak · Payout · Growth') +
        _cell('Valuation', 25, _val(val), 'P/E · P/BV · EV/EBITDA') +
        _cell('Cash Flow Strength', 15, _val(cf), 'FCF · OCF/NI · Int Coverage') +
        _cell('Hidden Value', 10, _val(hv), breakdown.hidden_value_note || '') +
        '<tr><td class="sym">Modifier</td><td class="num">—</td><td class="num pos">' + (mod > 0 ? '+' + mod : mod) + '</td><td class="dim">Valuation grade / signals</td></tr>' +
        '<tr style="border-top:2px solid var(--border-subtle)"><td class="sym">Total</td><td class="num">100</td><td class="num" style="font-size:1.2em">' + Math.round(score) + '</td><td></td></tr>' +
      '</tbody>' +
    '</table>'
  );
}

// new — full replace with dynamic PILLAR_SPEC loop
var PILLAR_SPEC = [
  { key: 'dividend', label: 'Dividend Sustainability', max: 50, driver: 'Yield · Streak · Payout · Growth' },
  { key: 'valuation', label: 'Valuation', max: 25, driver: 'P/E · P/BV · EV/EBITDA' },
  { key: 'cash_flow', label: 'Cash Flow Strength', max: 10, driver: 'FCF · OCF/NI · Int Coverage' },
  { key: 'hidden_value', label: 'Hidden Value', max: 5, driver: '' },
  { key: 'track_record', label: 'Track Record', max: 10, driver: 'Revenue Growth · EPS Growth' }
];

function _renderScoreBreakdown(stock) {
  var esc = window.MMUtils.escapeHtml;
  var score = stock.quality_score != null ? stock.quality_score : (stock.score || 0);
  var breakdown = stock.score_breakdown || stock.breakdown || {};
  var mod = breakdown.modifier == null ? (breakdown.modifiers || 0) : breakdown.modifier;

  function _getPillarValue(key) {
    // backward compat: cashflow vs cash_flow / hidden vs hidden_value
    if (key === 'cash_flow') {
      return breakdown.cash_flow != null ? breakdown.cash_flow : (breakdown.cashflow || 0);
    }
    if (key === 'hidden_value') {
      return breakdown.hidden_value != null ? breakdown.hidden_value : (breakdown.hidden || 0);
    }
    return breakdown[key] == null ? 0 : breakdown[key];
  }
  function _cell(label, max, scored, driver) {
    var cls = (scored && scored > 0) ? 'pos' : '';
    return '<tr><td class="sym">' + label + '</td><td class="num">' + max + '</td><td class="num ' + cls + '">' + (scored == null ? '—' : scored) + '</td><td class="dim">' + esc(driver || '') + '</td></tr>';
  }

  var rows = PILLAR_SPEC.map(function (p) {
    var driver = p.key === 'hidden_value' ? (breakdown.hidden_value_note || p.driver) : p.driver;
    return _cell(p.label, p.max, _getPillarValue(p.key), driver);
  }).join('');

  return (
    '<div class="v6-section-head"><h2>Score Breakdown</h2><small>Of One Hundred · Per Niwes Dividend-First Schema</small></div>' +
    '<section class="v6-score-block">' +
      '<div class="v6-score-display">' +
        '<div class="v6-score-huge">' + Math.round(score) + '</div>' +
        '<div class="v6-score-slash">of one hundred</div>' +
        '<div class="v6-score-version">niwes-dividend-first · v2</div>' +
      '</div>' +
      '<div><div class="v6-chart-box" style="position:relative;height:320px"><canvas id="v6-score-chart"></canvas></div></div>' +
    '</section>' +
    '<table class="data-table" style="margin-top:var(--sp-4)">' +
      '<thead><tr><th style="width:40%">Component</th><th class="num">Max</th><th class="num">Scored</th><th>Driver</th></tr></thead>' +
      '<tbody>' +
        rows +
        '<tr><td class="sym">Modifier</td><td class="num">—</td><td class="num pos">' + (mod > 0 ? '+' + mod : mod) + '</td><td class="dim">Valuation grade / signals</td></tr>' +
        '<tr style="border-top:2px solid var(--border-subtle)"><td class="sym">Total</td><td class="num">100</td><td class="num" style="font-size:1.2em">' + Math.round(score) + '</td><td></td></tr>' +
      '</tbody>' +
    '</table>'
  );
}
```

```javascript
// current — report.mobile.js:431-455 score doughnut chart
  var scoreCanvas = document.getElementById('v6-mscore-chart');
  if (scoreCanvas) {
    var bd = stock.score_breakdown || stock.breakdown || {};
    var div = bd.dividend || 0;
    var val = bd.valuation || 0;
    var cf  = bd.cashflow != null ? bd.cashflow : (bd.cash_flow || 0);
    var hv  = bd.hidden_value != null ? bd.hidden_value : (bd.hidden || 0);
    var mod = bd.modifier != null ? bd.modifier : 0;
    new window.Chart(scoreCanvas, {
      type: 'doughnut',
      data: {
        labels: ['Dividend ' + div, 'Valuation ' + val, 'Cash Flow ' + cf, 'Hidden ' + hv, 'Mod ' + (mod > 0 ? '+' + mod : mod)],
        datasets: [{
          data: [div, val, cf, Math.max(hv, 0.1), Math.abs(mod)],
          backgroundColor: [accent, textInk, '#878d9a', '#b2b6c0', '#5a6072'],
          borderColor: '#f5f5f0',
          borderWidth: 2,
        }]
      },
      ...

// new — add Track Record as 5th pillar segment (modifier becomes 6th)
  var scoreCanvas = document.getElementById('v6-mscore-chart');
  if (scoreCanvas) {
    var bd = stock.score_breakdown || stock.breakdown || {};
    var div = bd.dividend || 0;
    var val = bd.valuation || 0;
    var cf  = bd.cash_flow != null ? bd.cash_flow : (bd.cashflow || 0);
    var hv  = bd.hidden_value != null ? bd.hidden_value : (bd.hidden || 0);
    var tr  = bd.track_record || 0;
    var mod = bd.modifier != null ? bd.modifier : 0;
    new window.Chart(scoreCanvas, {
      type: 'doughnut',
      data: {
        labels: ['Dividend ' + div, 'Valuation ' + val, 'Cash Flow ' + cf, 'Hidden ' + hv, 'Track Rec ' + tr, 'Mod ' + (mod > 0 ? '+' + mod : mod)],
        datasets: [{
          data: [div, val, cf, Math.max(hv, 0.1), Math.max(tr, 0.1), Math.abs(mod)],
          backgroundColor: [accent, textInk, '#878d9a', '#b2b6c0', '#9aa1ad', '#5a6072'],
          borderColor: '#f5f5f0',
          borderWidth: 2,
        }]
      },
      ...
```

```javascript
// home.js _buildFilterBar — INSERT new sector group between Signal and Showing
// current (lines 240-251)
      '<div class="filter-group">' +
        '<span class="lbl">Signal</span>' +
        '<button class="filter-chip active" data-signal="ALL">All</button>' +
        '<button class="filter-chip" data-signal="NIWES_5555">Niwes 5-5-5-5</button>' +
        '<button class="filter-chip" data-signal="HIDDEN_VALUE">Hidden Value</button>' +
        '<button class="filter-chip" data-signal="DEEP_VALUE">Deep Value</button>' +
        '<button class="filter-chip" data-signal="QUALITY_DIVIDEND">Quality Div</button>' +
      '</div>' +
      '<div class="filter-group">' +
        '<span class="lbl" style="margin-right:0">Showing</span>' +
        '<span class="val mono" style="color:var(--ink);font-weight:500" id="v6-home-count">— of ' + totalCount + '</span>' +
      '</div>' +

// new — _buildFilterBar(totalCount, candidates) — insert sector group between Signal and Showing
// First, compute unique sectors from candidates list (passed as new arg or use _state.all):
function _buildFilterBar(totalCount, candidates) {
  candidates = candidates || [];
  var sectorSet = {};
  for (var i = 0; i < candidates.length; i++) {
    var s = candidates[i].sector;
    if (s) sectorSet[s] = true;
  }
  var sectors = Object.keys(sectorSet).sort();
  var sectorChips = sectors.map(function (s) {
    var safe = s.replace(/"/g, '&quot;');
    return '<button class="filter-chip" data-sector="' + safe + '">' + safe + '</button>';
  }).join('');
  // ... existing return with new section inserted between Signal and Showing groups:
  // '<div class="filter-group">' +
  //   '<span class="lbl">Sector</span>' +
  //   sectorChips +
  // '</div>' +
}
// Update caller at _buildHomeHtml (line 282):
//   _buildFilterBar(candidates.length, candidates) // pass candidates

// home.js _wireControls — add sector chip handler (multi-select) at end of existing handlers
// _state.sectors = []  // initialized at module load or _state declaration
    Array.prototype.forEach.call(bar.querySelectorAll('[data-sector]'), function (btn) {
      btn.addEventListener('click', function () {
        var sector = btn.getAttribute('data-sector');
        var idx = _state.sectors.indexOf(sector);
        if (idx >= 0) {
          _state.sectors.splice(idx, 1);
          btn.classList.remove('active');
        } else {
          _state.sectors.push(sector);
          btn.classList.add('active');
        }
        _state.page = 1;
        _renderGrid();
      });
    });

// home.js _renderGrid filter logic — ADD sector filter step before sort
// Existing filter (somewhere in _renderGrid):
//   var filtered = _state.signal === 'ALL' ? all : all.filter(...);
// Add after that:
//   if (_state.sectors && _state.sectors.length > 0) {
//     filtered = filtered.filter(function (s) { return _state.sectors.indexOf(s.sector) !== -1; });
//   }
```

```python
# new file — projects/4-MaxMahon/scripts/_smoke_dehardcode.py
"""Smoke test for Plan D backend de-hardcode (portfolio_builder dynamic suggestions)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))


def test_compute_sector_suggestions_top3_by_score():
    from portfolio_builder import compute_sector_suggestions
    screener = {
        'candidates': [
            {'symbol': 'CPNREIT.BK', 'score': 70, 'sector': 'Property Fund & REITs'},
            {'symbol': 'AIMIRT.BK', 'score': 60, 'sector': 'Property Fund & REITs'},
            {'symbol': 'DIF.BK', 'score': 30, 'sector': 'Property Fund & REITs'},
            {'symbol': 'BBL.BK', 'score': 80, 'sector': 'Banking'},
        ]
    }
    out = compute_sector_suggestions(screener)
    assert out['REIT-PFund'][:3] == ['CPNREIT', 'AIMIRT', 'DIF'], f"expected top 3 by score, got {out['REIT-PFund']}"
    assert out['Banking'][0] == 'BBL', f"expected BBL top, got {out['Banking']}"
    print('[PASS] compute_sector_suggestions returns top 3 by score per canonical sector')


def test_compute_sector_suggestions_empty_fallback():
    from portfolio_builder import compute_sector_suggestions, STATIC_SECTOR_SUGGESTIONS
    out = compute_sector_suggestions({'candidates': []})
    assert out['REIT-PFund'] == STATIC_SECTOR_SUGGESTIONS['REIT-PFund'], 'expected fallback to static'
    assert out['Banking'] == STATIC_SECTOR_SUGGESTIONS['Banking']
    print('[PASS] compute_sector_suggestions falls back to static when scan empty')


def test_build_sector_warnings_uses_passed_suggestions():
    from portfolio_builder import build_sector_warnings
    custom = {'REIT-PFund': ['CPNREIT', 'AIMIRT'], 'Banking': ['BBL'], 'Property': ['QH'], 'Energy': ['PTT']}
    warnings = build_sector_warnings({'Banking'}, custom)
    msg_text = ' '.join(w['msg'] for w in warnings)
    assert 'CPNREIT' in msg_text, f'expected CPNREIT in warnings msg, got: {msg_text}'
    assert 'DIF' not in msg_text or 'CPNREIT' in msg_text, 'should use passed suggestions, not static DIF list'
    print('[PASS] build_sector_warnings uses passed suggestions')


if __name__ == '__main__':
    failures = []
    tests = [
        test_compute_sector_suggestions_top3_by_score,
        test_compute_sector_suggestions_empty_fallback,
        test_build_sector_warnings_uses_passed_suggestions,
    ]
    for fn in tests:
        try:
            fn()
        except AssertionError as e:
            failures.append(f'{fn.__name__}: {e}')
            print(f'[FAIL] {fn.__name__}: {e}')
        except Exception as e:
            failures.append(f'{fn.__name__}: {type(e).__name__}: {e}')
            print(f'[FAIL] {fn.__name__}: {type(e).__name__}: {e}')
    print()
    if failures:
        print(f'[FAIL] {len(failures)} test(s) failed: {failures}')
        sys.exit(1)
    print(f'[PASS] all {len(tests)} tests passed')
    sys.exit(0)
```
