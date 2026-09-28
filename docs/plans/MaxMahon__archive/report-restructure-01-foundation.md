---
project: MaxMahon
created: 2026-04-24
last_updated: 2026-04-24
status: done
---

# Report Page Restructure — Foundation (Backend + CSS + SVG)

> Part 1 of 3 — Infrastructure for restructure: backend expose verdict+analyzed_at in narrative response, port mockup CSS classes to components.css (with light→dark token translation: --ink→--fg-primary, --rule→--border-strong, --accent→--c-positive-strong), SVG icon helper in utils.js. No UI rendering changes in this plan — only prepare classes + helpers that Plans 02 + 03 will use. | Index: report-restructure-index
> Depends on: none
> Parallel-safe with: none

## Phase 1: Backend — expose verdict + analyzed_at in narrative response
- [x] แก้ function `_load_cached_narrative(symbol)` ใน `projects/MaxMahon/server/app.py` (บรรทัด 348-372) เพิ่ม 2 field ใน return dict: `verdict` (string raw จาก cached.get('verdict')) และ `analyzed_at` (string ISO จาก cached.get('analyzed_at')) — ทั้ง cache-hit path และ empty path ต้อง include fields. Scope: **ห้ามแก้** prompt template / parse_analysis_response / POST /analyze endpoint — แค่ expose field เพิ่มในฝั่ง GET. Acceptance: curl GET http://localhost:50089/api/stock/QH.BK (auth Bearer MAX_TOKEN) → response JSON contains `narrative.verdict` และ `narrative.analyzed_at` (value = existing cache content, null ถ้าไม่มี cache)

### Reference
```python
# current (app.py:348-372)
def _load_cached_narrative(symbol: str) -> dict:
    cache_path = _ANALYSIS_CACHE_DIR / f"{symbol}.json"
    if cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            text = (cached.get("to_art") or "").strip()
            if not text:
                parts = [
                    cached.get("dividend"),
                    cached.get("hidden"),
                    cached.get("moat"),
                    cached.get("valuation"),
                ]
                text = "\n\n".join([p for p in parts if p])
            if text:
                lede = text.split("\n\n", 1)[0] if "\n\n" in text else text[:200]
                return {"case_text": text, "lede": lede}
        except Exception:
            pass
    return {"case_text": None, "lede": None}

# new
def _load_cached_narrative(symbol: str) -> dict:
    cache_path = _ANALYSIS_CACHE_DIR / f"{symbol}.json"
    if cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            text = (cached.get("to_art") or "").strip()
            if not text:
                parts = [
                    cached.get("dividend"),
                    cached.get("hidden"),
                    cached.get("moat"),
                    cached.get("valuation"),
                ]
                text = "\n\n".join([p for p in parts if p])
            if text:
                lede = text.split("\n\n", 1)[0] if "\n\n" in text else text[:200]
                return {
                    "case_text": text,
                    "lede": lede,
                    "verdict": cached.get("verdict"),
                    "analyzed_at": cached.get("analyzed_at"),
                }
        except Exception:
            pass
    return {"case_text": None, "lede": None, "verdict": None, "analyzed_at": None}
```

## Phase 2: CSS — append report-page classes to components.css
- [x] เพิ่ม CSS block ท้ายไฟล์ `projects/MaxMahon/web/v6/static/css/components.css` (append only — ห้ามแก้ existing rules) ประกอบด้วย 12 sections: (a) comment header 'Report page token map' อธิบาย mapping --ink→--fg-primary, --ink-soft→--fg-secondary, --ink-dim→--fg-dim, --ink-faint→--fg-mute, --rule→--border-strong, --rule-hair→--border-subtle, --accent→--c-positive-strong, (b) `.report-hero` + `.report-hero-left` + `.report-hero-right` + `.report-hero-price` — horizontal hero grid 1.4fr 1fr desktop, stack mobile, (c) `.v6-verdict-chip` + `.v6-verdict-chip.buy` + `.hold` + `.sell` + `.empty` — pill chip with colored background, (d) `.v6-section-head` (replaces .section-num) — h2 flex baseline + small subtitle, (e) `.v6-checklist` + `.v6-checklist-item` (grid 5-col desktop: 1fr auto auto auto 1.2fr; mobile: 2-row block) + `.v6-check-label` + `.v6-check-actual` (mono) + `.v6-check-threshold` (fg-dim small) + `.v6-check-mark.pass` (c-positive) + `.fail` (c-negative) + `.v6-check-reason` (fg-secondary fs-xs), (f) `.v6-score-block` (grid 1fr 1.4fr desktop, 1fr mobile) + `.v6-score-huge` (clamp(6rem, 10vw, 11rem) font-size), (g) `.v6-chart-pair` (grid 1.6fr 1fr desktop, 1fr mobile), (h) `.v6-exit-panel` (border 1px border-subtle rounded 16) + `.v6-exit-grid` (grid 4-col desktop, 2-col mobile), (i) `.v6-deep-analyze` (full-width card) + `.v6-deep-verdict-bar` (horizontal strip) + `.v6-deep-grid` (grid 2x2 desktop 1fr mobile) + `.v6-deep-section` + `.v6-deep-talk-panel` (full-width sage-tinted bg), (j) `.v6-pattern-footnote` (details/summary subtle styling, fg-dim, small), (k) `.v6-empty-state` (centered muted text utility), (l) media query @media (max-width: 900px) for stacking rules. Scope: **ห้ามแตะ** .card, .tag, .data-table, .btn, .mm-pb-*, .bottom-nav classes เดิม. Use var(--*) tokens only — ห้ามใช้ hardcoded hex. Acceptance: DevTools Elements tab → ตรวจ .v6-verdict-chip.buy มี background: var(--c-positive) + color white + padding 6px 14px + border-radius 8px; .v6-checklist-item มี display: grid + grid-template-columns: 1fr auto auto auto 1.2fr ที่ viewport 1440px; @media max-width: 900px → ทุก grid-template-columns ตกเหลือ 1fr

### Reference
```css
/* ========== Report page token map ========== */
/*
  mockup --ink       → --fg-primary
  mockup --ink-soft  → --fg-secondary
  mockup --ink-dim   → --fg-dim
  mockup --ink-faint → --fg-mute
  mockup --rule      → --border-strong
  mockup --rule-hair → --border-subtle
  mockup --accent    → --c-positive-strong
*/

/* ========== Report hero ========== */
.report-hero {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: var(--sp-5);
  align-items: center;
  padding: var(--sp-6) var(--sp-5);
  background: linear-gradient(135deg, var(--bg-elevated-start), var(--bg-elevated-end));
  border: 1px solid var(--bg-elevated-border);
  border-radius: 20px;
  margin: var(--sp-5) 0;
  box-shadow: var(--shadow-card);
}
.report-hero-left { display: flex; flex-direction: column; gap: var(--sp-3); }
.report-hero-right { display: flex; flex-direction: column; gap: var(--sp-3); align-items: flex-end; }
.report-hero-price {
  font-family: var(--font-mono);
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 900;
  color: var(--fg-primary);
  letter-spacing: -0.02em;
}

/* ========== Verdict chip ========== */
.v6-verdict-chip {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-2);
  padding: 6px 14px;
  border-radius: 999px;
  font-family: var(--font-mono);
  font-size: var(--fs-sm);
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.v6-verdict-chip.buy { background: var(--c-positive); color: #fff; }
.v6-verdict-chip.hold { background: var(--c-warn); color: #fff; }
.v6-verdict-chip.sell { background: var(--c-negative); color: #fff; }
.v6-verdict-chip.empty { background: var(--bg-surface-2); color: var(--fg-dim); font-style: italic; }

/* ========== Section head (replaces .section-num) ========== */
.v6-section-head {
  display: flex;
  align-items: baseline;
  gap: var(--sp-3);
  flex-wrap: wrap;
  margin: var(--sp-6) 0 var(--sp-4);
  padding-bottom: var(--sp-3);
  border-bottom: 1px solid var(--border-subtle);
}
.v6-section-head h2 {
  font-family: var(--font-head);
  font-weight: 700;
  font-size: var(--fs-xl);
  color: var(--fg-primary);
  margin: 0;
}
.v6-section-head small {
  font-family: var(--font-mono);
  font-size: var(--fs-xs);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--fg-dim);
  font-weight: 400;
}

/* ========== Enriched 5-5-5-5 checklist ========== */
.v6-checklist { margin: var(--sp-4) 0; }
.v6-checklist-item {
  display: grid;
  grid-template-columns: 1fr auto auto auto 1.2fr;
  gap: var(--sp-4);
  padding: var(--sp-3) 0;
  border-bottom: 1px solid var(--border-subtle);
  align-items: baseline;
}
.v6-check-label { font-family: var(--font-head); font-size: var(--fs-md); font-weight: 500; color: var(--fg-primary); }
.v6-check-actual { font-family: var(--font-mono); font-weight: 500; font-size: var(--fs-md); color: var(--fg-primary); }
.v6-check-threshold { font-family: var(--font-mono); font-size: var(--fs-sm); color: var(--fg-dim); }
.v6-check-mark { font-family: var(--font-head); font-weight: 700; font-size: var(--fs-lg); width: 20px; text-align: center; }
.v6-check-mark.pass { color: var(--c-positive); }
.v6-check-mark.fail { color: var(--c-negative); }
.v6-check-reason { font-size: var(--fs-xs); color: var(--fg-secondary); line-height: 1.4; }

/* ========== Score block ========== */
.v6-score-block { display: grid; grid-template-columns: 1fr 1.4fr; gap: var(--sp-6); align-items: center; padding: var(--sp-5) 0; }
.v6-score-display { text-align: center; }
.v6-score-huge { font-family: var(--font-mono); font-weight: 300; font-size: clamp(6rem, 10vw, 11rem); line-height: 0.8; letter-spacing: -0.05em; color: var(--fg-primary); }
.v6-score-slash { font-family: var(--font-head); color: var(--fg-dim); font-size: var(--fs-lg); margin-top: var(--sp-3); }
.v6-score-version { font-family: var(--font-mono); font-size: var(--fs-xs); letter-spacing: 0.14em; text-transform: uppercase; color: var(--fg-mute); margin-top: var(--sp-4); }

/* ========== Chart pair ========== */
.v6-chart-pair { display: grid; grid-template-columns: 1.6fr 1fr; gap: var(--sp-5); margin: var(--sp-4) 0; align-items: flex-start; }
.v6-chart-box { position: relative; height: 260px; }
.v6-chart-caption { font-family: var(--font-head); font-size: var(--fs-sm); color: var(--fg-dim); text-align: center; margin-top: var(--sp-3); }

/* ========== Exit panel ========== */
.v6-exit-panel { border: 1px solid var(--border-subtle); border-radius: 16px; padding: var(--sp-5); margin: var(--sp-4) 0; background: var(--bg-surface); }
.v6-exit-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--sp-4); padding: var(--sp-4) 0; border-top: 1px solid var(--border-subtle); border-bottom: 1px solid var(--border-subtle); margin: var(--sp-4) 0; }
.v6-exit-cell .lbl { font-family: var(--font-mono); font-size: 0.65rem; letter-spacing: 0.16em; text-transform: uppercase; color: var(--fg-dim); }
.v6-exit-cell .v { font-family: var(--font-mono); font-size: var(--fs-lg); font-weight: 500; display: block; margin-top: 4px; color: var(--fg-primary); }
.v6-exit-cell .sub { font-family: var(--font-body); font-size: var(--fs-xs); color: var(--fg-dim); display: block; margin-top: 2px; }

/* ========== Deep Analyze ========== */
.v6-deep-analyze { background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 20px; padding: var(--sp-5); margin: var(--sp-5) 0; }
.v6-deep-verdict-bar { display: flex; align-items: center; gap: var(--sp-3); padding: var(--sp-4); border-radius: 12px; background: var(--c-positive-soft); border: 1px solid var(--c-positive-border); margin-bottom: var(--sp-5); }
.v6-deep-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--sp-5); }
.v6-deep-section { padding: var(--sp-4); border-radius: 12px; background: var(--bg-surface-2, var(--bg-base)); border: 1px solid var(--border-subtle); }
.v6-deep-section h4 { display: flex; align-items: center; gap: var(--sp-2); font-size: var(--fs-md); font-weight: 700; color: var(--c-positive-strong); margin: 0 0 var(--sp-3); }
.v6-deep-section h4 svg { width: 18px; height: 18px; color: var(--c-positive); }
.v6-deep-section p { font-size: var(--fs-sm); color: var(--fg-secondary); line-height: 1.65; margin: 0; }
.v6-deep-talk-panel { background: var(--c-positive-tint); border: 1px solid var(--c-positive-border); border-radius: 16px; padding: var(--sp-5); margin-top: var(--sp-5); }
.v6-deep-talk-panel h4 { display: flex; align-items: center; gap: var(--sp-2); font-size: var(--fs-md); font-weight: 700; color: var(--c-positive-strong); margin: 0 0 var(--sp-3); flex-wrap: wrap; }
.v6-deep-talk-panel .pillar-badge { font-family: var(--font-mono); font-size: var(--fs-xs); padding: 3px 10px; border-radius: 999px; background: var(--bg-surface); color: var(--fg-secondary); border: 1px solid var(--border-subtle); text-transform: none; }
.v6-deep-talk-panel p { font-size: var(--fs-sm); color: var(--fg-primary); line-height: 1.7; margin: 0 0 var(--sp-3); }
.v6-deep-talk-panel p:last-child { margin-bottom: 0; }

/* ========== Pattern footnote ========== */
.v6-pattern-footnote { margin: var(--sp-6) 0 var(--sp-5); padding: var(--sp-4); border-top: 1px solid var(--border-subtle); font-size: var(--fs-sm); color: var(--fg-secondary); }
.v6-pattern-footnote summary { font-family: var(--font-mono); font-size: var(--fs-xs); letter-spacing: 0.12em; text-transform: uppercase; color: var(--fg-dim); cursor: pointer; padding: var(--sp-2) 0; }
.v6-pattern-footnote summary:hover { color: var(--fg-primary); }
.v6-pattern-footnote[open] summary { margin-bottom: var(--sp-3); }
.v6-pattern-footnote p { line-height: 1.6; margin: 0 0 var(--sp-3); }
.v6-pattern-footnote .src { font-family: var(--font-mono); font-size: var(--fs-xs); color: var(--fg-mute); }

/* ========== Empty state utility ========== */
.v6-empty-state { text-align: center; padding: var(--sp-5); font-family: var(--font-body); color: var(--fg-dim); font-size: var(--fs-sm); }

/* ========== Responsive: 900px ========== */
@media (max-width: 900px) {
  .report-hero { grid-template-columns: 1fr; gap: var(--sp-4); padding: var(--sp-5) var(--sp-4); }
  .report-hero-right { align-items: flex-start; }
  .v6-score-block { grid-template-columns: 1fr; gap: var(--sp-4); }
  .v6-chart-pair { grid-template-columns: 1fr; gap: var(--sp-4); }
  .v6-exit-grid { grid-template-columns: repeat(2, 1fr); }
  .v6-deep-grid { grid-template-columns: 1fr; gap: var(--sp-4); }
  .v6-checklist-item { grid-template-columns: 1fr auto auto auto; grid-template-rows: auto auto; }
  .v6-check-reason { grid-column: 1 / -1; grid-row: 2; margin-top: 4px; }
}
```

## Phase 3: SVG icon helper in utils.js (wrapped IIFE)
- [x] เพิ่ม function `svg(name, opts)` ใน `projects/MaxMahon/web/v6/static/js/utils.js` — คืน inline SVG string ขนาด default 18px stroke 2 color currentColor รองรับ 5 icons: 'banknote', 'gem', 'landmark', 'scale', 'message-circle' (path data จาก Lucide icons). **ห้าม leak global variables** — ต้อง wrap ใน IIFE ใหม่ `(function(){ ... })();` วางต่อท้ายไฟล์ (หลัง existing IIFE ที่ปิดด้วย `})();` ที่บรรทัด 124). ภายใน IIFE: declare `var _SVG_PATHS = {...}`, `function svg(...)`, แล้ว assign `window.MMUtils.svg = svg;` — MMUtils object มีอยู่แล้วจาก IIFE แรก. Scope: **ห้ามลบ/แก้** functions เดิม (fmtNum, escapeHtml, fmtDate*, fmtPercent, fmtCompact) + **ห้ามแก้ IIFE แรก** — append only. Acceptance: (a) ใน browser console พิมพ์ `MMUtils.svg('banknote')` คืน string starting with `<svg` ที่มี path data valid, (b) `MMUtils.svg('unknown')` คืน empty string, (c) พิมพ์ `_SVG_PATHS` หรือ `svg` ที่ console → `ReferenceError: is not defined` (confirms no global leak)

### Reference
```javascript
// append to utils.js — wrapped IIFE to avoid global leaks
(function () {
  var _SVG_PATHS = {
    'banknote': '<rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/>',
    'gem': '<path d="M6 3h12l4 6-10 13L2 9Z"/><path d="M11 3 8 9l4 13 4-13-3-6"/><path d="M2 9h20"/>',
    'landmark': '<line x1="3" x2="21" y1="22" y2="22"/><line x1="6" x2="6" y1="18" y2="11"/><line x1="10" x2="10" y1="18" y2="11"/><line x1="14" x2="14" y1="18" y2="11"/><line x1="18" x2="18" y1="18" y2="11"/><polygon points="12 2 20 7 4 7"/>',
    'scale': '<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
    'message-circle': '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
  };
  function svg(name, opts) {
    var paths = _SVG_PATHS[name];
    if (!paths) return '';
    var size = (opts && opts.size) || 18;
    var stroke = (opts && opts.stroke) || 2;
    return '<svg xmlns="http://www.w3.org/2000/svg" width="' + size + '" height="' + size + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="' + stroke + '" stroke-linecap="round" stroke-linejoin="round">' + paths + '</svg>';
  }
  window.MMUtils.svg = svg;
})();
```

## Phase 4: Smoke test — no UI change verification
- [x] เปิด `http://localhost:50089/report/QH.BK` (local dev เท่านั้น — production max.intensivetrader.com ทดสอบเมื่อ Karl approve) ใน browser แล้วตรวจ 3 จุด: (a) console ไม่มี error, (b) 11 sections เดิม still render (article head + The Case + Score Breakdown + 5-5-5-5 + Reasons + Pattern + Key Numbers + Dividend History + Score History + Exit Baseline + Deep Analyze) — ก่อน desktop restructure ยังเห็นทุก section เก่า, (c) DevTools → network tab → `/api/stock/QH.BK` response JSON มี field `narrative.verdict` + `narrative.analyzed_at` (check via console: `await fetch('/api/stock/QH.BK',{headers:{'Authorization':'Bearer '+MAX_TOKEN}}).then(r=>r.json()).then(j=>j.narrative)`). Scope: **ห้ามเปิด** report.js / report.mobile.js / components.css / utils.js แก้อะไร — นี่ verification phase เท่านั้น. Acceptance: page loads + 11 sections visible + verdict field exists in API response
