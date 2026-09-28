---
project: MaxMahon
created: 2026-04-25
last_updated: 2026-04-25
status: done
---

# Cleanup Finalize — Watchlist split + Star action

> Part 2 of 3 — Clarify Home (latest scan) vs Watchlist (user-starred) confusion: rename desktop nav 'WATCHLIST' → 'LATEST SCAN' + add real WATCHLIST item linking /watchlist; rename mobile 'Screen' → 'WATCHLIST'; backend exposes user_in_watchlist boolean in /api/stock/{sym}; add ⭐ star button on home cards (desktop+mobile) + report hero (desktop+mobile) wired to PUT /api/user/watchlist for instant toggle. | Index: cleanup-finalize-index
> Depends on: cleanup-finalize-01-archive-features
> Parallel-safe with: none

## Phase 1: Nav clarity (components.js)
- [x] แก้ `web/v6/static/js/components.js` `renderMasthead()` items array — หลัง Plan 1 archive เหลือ 2 items: `['watchlist', '/', 'WATCHLIST']`, `['settings', '/settings', 'SETTINGS']`. เปลี่ยนเป็น 3 items: `['latest-scan', '/', 'LATEST SCAN']`, `['watchlist', '/watchlist', 'WATCHLIST']`, `['settings', '/settings', 'SETTINGS']`. แก้ legacy compat block (lines ~33-34) ลบ `if (active === 'home' || active === 'report') active = 'watchlist'` — replace ด้วย: `if (active === 'home' || active === 'report') active = 'latest-scan';`. Scope: **ห้ามแตะ** renderMobileNav (Task ถัดไป). Acceptance: desktop nav มี 3 items; '/' active = 'latest-scan'; '/watchlist' active = 'watchlist'
- [x] แก้ `web/v6/static/js/components.js` `renderMobileNav()` (หลัง Plan 1 เหลือ 3 items): เปลี่ยน label ของ saved item จาก 'Screen' → 'WATCHLIST'. แก้ `web/v6/mobile/index.html` (lines ~33-59) navigation routing — ใน `mappedActive` mapping (lines 54-57): เพิ่ม `'latest-scan': 'home'` mapping. Scope: ห้ามเปลี่ยน icon (⌕) หรือ route (/m/watchlist). Acceptance: mobile nav saved item label = 'WATCHLIST'
- [x] Verify nav rendering: open `/` → desktop active = 'latest-scan' (highlighted); open `/watchlist` → active = 'watchlist'. Console no error. Scope: verification only. Acceptance: visual check pass บน DevTools 1440px viewport (mock — Karl เปิด server เอง)

## Phase 2: Backend — expose user_in_watchlist on /api/stock/{sym}
- [x] แก้ `server/app.py` endpoint `GET /api/stock/{symbol}` (line ~285-345) — ก่อน return ให้เพิ่ม field: `stock_data['user_in_watchlist'] = (symbol in load_user_data().get('watchlist', []))`. Scope: **ห้ามแตะ** _load_cached_narrative, screener_metrics, yearly_metrics fields เดิม. Acceptance: curl GET http://localhost:50089/api/stock/QH.BK (auth Bearer MAX_TOKEN) → response มี field `user_in_watchlist: true|false`

### Reference
```python
# current (app.py around line 339)
    stock_data['narrative'] = _load_cached_narrative(symbol)
    return stock_data

# new
    stock_data['narrative'] = _load_cached_narrative(symbol)
    stock_data['user_in_watchlist'] = symbol in (load_user_data().get('watchlist') or [])
    return stock_data
```

## Phase 3: Star action — Home cards (desktop + mobile)
- [x] แก้ function `_renderCard()` ใน `web/v6/static/js/pages/home.js` (lines ~52-137) — เพิ่ม ⭐ star button ที่ top-right ของ card. ใช้ `card.in_watchlist` boolean (มาจาก /api/screener response แล้ว) determine initial state. HTML: `<span class="v6-star" data-mm-star data-sym="{sym}" data-watched="{true|false}">★</span>` (filled=watched, outlined=not). เพิ่ม CSS class `.v6-star` ใน components.css (Task 3.3): position absolute top-right, color var(--fg-mute) → var(--c-warn) when [data-watched="true"], cursor pointer, font-size 1.4rem, padding 4px. หลัง _wireControls() เพิ่มเรียก `_wireStarButtons(container)` function ใหม่ — handle click event delegation: prevent card navigation (event.stopPropagation), determine current state, PUT /api/user/watchlist with {add: [sym]} or {remove: [sym]}, toggle data-watched attribute on success, no page reload. Scope: **ห้ามแตะ** card click→navigate logic; ห้ามเปลี่ยน fetch /api/screener. Acceptance: ทุก card มี ★ ที่ top-right; click ★ → toggle visual + PUT request เห็นใน Network tab; refresh page → state persists
- [x] Mirror to `web/v6/static/js/pages/home.mobile.js` (lines ~53-114) — เพิ่ม ⭐ button ใน mobile card layout. ใช้ class เดียวกัน (.v6-star) แต่ size อาจปรับให้ touch target ≥ 44px. _wireStarButtons mobile version. Acceptance: mobile card มี ★ + click toggle works
- [x] เพิ่ม CSS class `.v6-star` ใน `web/v6/static/css/components.css` (append at end): position relative for parent + absolute positioning for star + state styling (default=outline, watched=filled gold). Mobile variant: ขนาดใหญ่ขึ้น (touch target). Scope: **ห้ามแตะ** classes อื่น. Acceptance: grep `.v6-star` ใน components.css → at least 2 selectors

## Phase 4: Star action — Report page hero (desktop + mobile)
- [x] แก้ `_renderHero()` ใน `web/v6/static/js/pages/report.js` (lines ~74-111) — เพิ่ม ⭐ button ใน `.report-hero-right` (next to verdict chip area). ใช้ stock.user_in_watchlist (จาก Phase 2). HTML: `<span class="v6-star" data-mm-star id="v6-hero-star" data-sym="{sym}" data-watched="{true|false}">★</span>`. หลัง mount + _wireDeepAnalyze เพิ่ม call `_wireHeroStar(stock.symbol)` function ใหม่ที่: handle click → toggle PUT /api/user/watchlist + toggle data-watched. Scope: **ห้ามแตะ** verdict chip / score pill / price logic. Acceptance: hero มี ★ ใต้/ข้าง verdict chip; click toggle works; user_in_watchlist=true → ★ filled gold; refresh persist
- [x] Mirror to `web/v6/static/js/pages/report.mobile.js` `_renderHero()` — id=`v6-mhero-star` (mobile prefix). Same wiring. Acceptance: mobile hero ★ works

### Reference
```javascript
// new helper in report.js (add near _applyHeroVerdict)
function _wireHeroStar(sym) {
  var el = document.getElementById('v6-hero-star');
  if (!el) return;
  el.addEventListener('click', function () {
    var watched = el.getAttribute('data-watched') === 'true';
    var body = watched ? { remove: [sym] } : { add: [sym] };
    window.MMApi.put('/api/user/watchlist', body).then(function () {
      el.setAttribute('data-watched', String(!watched));
    });
  });
}

// in _renderHero return — add inside report-hero-right after verdict div
'<div id="v6-hero-verdict">' + verdictHtml + '</div>' +
'<span class="v6-star" id="v6-hero-star" data-sym="' + sym + '" data-watched="' + !!stock.user_in_watchlist + '">★</span>' +
```

## Phase 5: Smoke test
- [x] Verify 3 scenarios บน localhost:50089: (a) `/` → desktop nav 3-item (LATEST SCAN highlighted) + ⭐ on each card → click toggle works, (b) `/watchlist` → nav active='watchlist', list shows previously-starred stocks, (c) `/report/QH.BK` → hero มี ★ next to verdict + click toggle works + refresh persist. Mobile 375px viewport: mobile nav 3-item, ⭐ on cards/hero ขนาด ≥ 44px touch target. Verify console no error + no horizontal scroll. Scope: verification only. Acceptance: ทุก scenarios pass + Karl approve via screenshot
