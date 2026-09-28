---
project: maxmahon
created: 2026-04-22
last_updated: 2026-04-23
status: done
---

# MaxMahon v6 · Frontend Foundation

> Part 3 of 9 — scaffold web/v6/, shared tokens + base.css + components, device-detect redirect | Index: maxmahon-v6-index
> Depends on: maxmahon-v6-02-api
> Parallel-safe with: none (foundation for 04-08)

## Phase 1: Folder scaffold
- [x] Create folder structure under `projects/MaxMahon/web/v6/`: `desktop/`, `mobile/`, `shared/`, `static/`, `static/js/`, `static/js/pages/`, `static/css/`. Scope: empty dirs only. Acceptance: all 7 folders exist; `ls web/v6/` shows desktop, mobile, shared, static.

## Phase 2: Design tokens + base styles
- [x] Copy `projects/MaxMahon/web-v6-mockup/shared/tokens.css` to `projects/MaxMahon/web/v6/shared/tokens.css`. Scope: byte-for-byte copy; do not rename tokens. Acceptance: file exists; diff shows 0 differences vs mockup source.
- [x] Copy `projects/MaxMahon/web-v6-mockup/shared/base.css` to `projects/MaxMahon/web/v6/shared/base.css`. Scope: byte-for-byte copy (masthead, card, rule, pull-quote, drop-cap, table, button classes). Acceptance: file exists; 0 diff vs mockup source.
- [x] If `projects/MaxMahon/web-v6-mockup/shared/mobile.css` exists, copy to `projects/MaxMahon/web/v6/shared/mobile.css` (mobile-specific overrides: stacked, bottom nav, touch targets). Scope: byte-for-byte copy. Acceptance: file exists (or skip task if mockup has no mobile.css).

## Phase 3: Shared UI components (single JS module)
- [x] Create `projects/MaxMahon/web/v6/static/js/components.js` with reusable functions: `renderMasthead(ctx)` (vol/no, date, next scan time), `renderMastNav(activeRoute)` (top navigation strip), `renderSectionNum(num)` (No 01 marker), `renderPullQuote(text, attribution)`, `renderDropCap(paragraph)`, `renderSevBadge(severity)` (HOLD/REVIEW/CONSIDER_EXIT color-coded via class not color directly), `openModal(id, contentHtml)` (backdrop + sheet + close), `showToast(message, variant)`, `renderLoading(container)`, `renderError(container, message)`. Scope: pure functions returning HTML strings OR DOM manipulation; no framework. Acceptance: `components.js` exports all 10 functions via `window.MMComponents` namespace; each function JSDoc-documented with params + return type.
- [x] Verify components visually match mockup by opening `web-v6-mockup/desktop/01-home.html` in browser + inspecting masthead, mast-nav, section-num elements. Scope: visual audit only; if discrepancy, fix JS to match. Acceptance: rendering `renderMasthead({vol:'VI', no:'17', date:'22 Apr 2026', next_scan:'Sat 09:00'})` produces DOM identical to mockup masthead source HTML.

### Reference
```javascript
// web/v6/static/js/components.js
window.MMComponents = (function(){
  function renderMasthead(ctx) {
    return `<header class="masthead">
      <div class="masthead-vol">VOL.${ctx.vol} · NO.${ctx.no}</div>
      <h1 class="masthead-title">Max Mahon</h1>
      <div class="masthead-date">${ctx.date} · next scan ${ctx.next_scan}</div>
    </header>`;
  }
  function renderMastNav(active) {
    const items = [['home','Home'],['watchlist','Watchlist'],['portfolio','Portfolio'],['simulator','Simulator'],['settings','Settings']];
    return `<nav class="mast-nav">${items.map(([k,l]) => `<a href="/${k==='home'?'':k}" class="${k===active?'active':''}">${l}</a>`).join('')}</nav>`;
  }
  function renderSectionNum(num) { return `<div class="section-num">№ ${String(num).padStart(2,'0')}</div>`; }
  function renderPullQuote(text, attr) { return `<blockquote class="pull-quote">${text}<cite>— ${attr}</cite></blockquote>`; }
  function renderDropCap(p) { return `<p class="drop-cap">${p}</p>`; }
  function renderSevBadge(sev) {
    const label = {HOLD:'Hold', REVIEW:'Review', CONSIDER_EXIT:'Consider Exit'}[sev] || sev;
    return `<span class="sev-badge sev-${sev.toLowerCase()}">${label}</span>`;
  }
  function openModal(id, html) {
    // create backdrop + sheet + close button
  }
  function showToast(msg, variant='info') { /* ... */ }
  function renderLoading(container) { container.innerHTML = '<div class="loading-state">Loading…</div>'; }
  function renderError(container, msg) { container.innerHTML = `<div class="error-state">${msg}</div>`; }
  return { renderMasthead, renderMastNav, renderSectionNum, renderPullQuote, renderDropCap, renderSevBadge, openModal, showToast, renderLoading, renderError };
})();
```

## Phase 4: API client helper
- [x] Create `projects/MaxMahon/web/v6/static/js/api.js` with: `const MM_API = window.location.origin` (base URL), function `apiFetch(path, {method, body, retry})` that wraps fetch with `Authorization: Bearer ${localStorage.getItem('MAX_TOKEN') || ''}`, JSON serialization, error handling (4xx/5xx throw with status + message), retry logic (3 attempts with exponential backoff on 500/503 only). Also add helper `apiGet(path)`, `apiPost(path, body)`, `apiPut(path, body)`, `apiDelete(path)`. Scope: pure fetch wrapper; no framework. Acceptance: `window.MMApi` exposes 4 helpers + base `apiFetch`; failed auth (401) throws with clear message not retried.
- [x] Add token prompt flow: if `localStorage.getItem('MAX_TOKEN')` is null on any API call, show a modal via `MMComponents.openModal` asking for token; on submit save to localStorage + retry original call. Scope: one-time prompt per session. Acceptance: first API call without token opens prompt; after saving, subsequent calls use it automatically.

### Reference
```javascript
// web/v6/static/js/api.js
window.MMApi = (function(){
  const BASE = window.location.origin;
  async function apiFetch(path, opts={}) {
    const { method='GET', body=null, retry=3 } = opts;
    const token = localStorage.getItem('MAX_TOKEN') || '';
    const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };
    const init = { method, headers };
    if (body !== null) init.body = JSON.stringify(body);
    let lastErr = null;
    for (let i=0; i<retry; i++) {
      try {
        const r = await fetch(`${BASE}${path}`, init);
        if (r.status === 401) {
          // trigger token prompt, don't retry
          throw new Error('Auth required');
        }
        if (!r.ok && r.status >= 500 && i < retry-1) {
          await new Promise(res => setTimeout(res, 500 * (2**i)));
          continue;
        }
        if (!r.ok) throw new Error(`HTTP ${r.status}: ${await r.text()}`);
        return await r.json();
      } catch (e) { lastErr = e; if (i === retry-1) throw e; }
    }
    throw lastErr;
  }
  return {
    apiFetch,
    get: (p) => apiFetch(p),
    post: (p, b) => apiFetch(p, {method:'POST', body:b}),
    put: (p, b) => apiFetch(p, {method:'PUT', body:b}),
    delete: (p) => apiFetch(p, {method:'DELETE'}),
  };
})();
```

## Phase 5: Device detection + routing
- [x] Create `projects/MaxMahon/web/v6/static/js/device.js` with: function `isMobile()` returning `window.matchMedia('(pointer: coarse)').matches || window.innerWidth < 768`. On page load, if `isMobile() && !location.pathname.startsWith('/m')` redirect to `/m` + current path tail; if `!isMobile() && location.pathname.startsWith('/m')` redirect to desktop equivalent. Scope: redirect once on load; do not re-redirect during session. Acceptance: visiting `/` on mobile UA redirects to `/m`; visiting `/m/report/BBL.BK` on desktop redirects to `/report/BBL.BK`.

### Reference
```javascript
// web/v6/static/js/device.js
window.MMDevice = (function(){
  function isMobile() {
    return window.matchMedia('(pointer: coarse)').matches || window.innerWidth < 768;
  }
  function redirectIfMismatch() {
    const path = location.pathname;
    const onMobilePath = path === '/m' || path.startsWith('/m/');
    if (isMobile() && !onMobilePath) {
      const tail = path === '/' ? '' : path;
      location.replace('/m' + tail);
    } else if (!isMobile() && onMobilePath) {
      const tail = path === '/m' ? '/' : path.slice(2);
      location.replace(tail || '/');
    }
  }
  document.addEventListener('DOMContentLoaded', redirectIfMismatch);
  return { isMobile };
})();
```

## Phase 6: Layout skeletons (app shell HTML)
- [x] Create `projects/MaxMahon/web/v6/desktop/index.html` with app-shell template: `<head>` loads Google Fonts (Playfair Display, Lora, IBM Plex Serif Thai, JetBrains Mono), `shared/tokens.css`, `shared/base.css`, `static/js/api.js`, `static/js/components.js`, `static/js/device.js`. `<body>` contains `<div id="masthead"></div>` + `<div id="mast-nav"></div>` + `<main id="app"></main>`. Inline script: read URL path, dynamically import `pages/{route}.js` (e.g., `pages/home.js`), call its `mount(app)` export. Scope: shell only; pages load next plans. Acceptance: opening `/` serves this HTML (post Plan 02 routing fix); inspecting DOM shows masthead + nav + empty main; no console errors (pages stubbed in next plans).
- [x] Create `projects/MaxMahon/web/v6/mobile/index.html` with mobile shell template: similar to desktop but loads `shared/mobile.css` (if present) + uses bottom-nav layout (sticky bottom bar with Home/Watchlist/Portfolio/Simulator/Settings icons-free text labels per mockup). Scope: shell only. Acceptance: opening `/m` on mobile-sized browser serves this HTML; bottom nav visible at viewport bottom.
- [x] Match masthead HTML/CSS exactly against `web-v6-mockup/desktop/01-home.html` + `web-v6-mockup/mobile/01-home.html`. Scope: verify side-by-side; fix any class name/structural diff. Acceptance: rendered masthead (before any data injection) is pixel-identical to the mockup source.

### Reference
```html
<!-- web/v6/desktop/index.html -->
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Max Mahon</title>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lora&family=IBM+Plex+Serif+Thai&family=JetBrains+Mono&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/static/v6/css/../shared/tokens.css">
  <link rel="stylesheet" href="/static/v6/css/../shared/base.css">
  <script src="/static/v6/js/api.js?v={{CACHEBUST}}"></script>
  <script src="/static/v6/js/components.js?v={{CACHEBUST}}"></script>
  <script src="/static/v6/js/device.js?v={{CACHEBUST}}"></script>
</head>
<body>
  <div id="masthead"></div>
  <div id="mast-nav"></div>
  <main id="app"></main>
  <script>
    (async () => {
      const route = (location.pathname.replace(/^\//, '').split('/')[0]) || 'home';
      try {
        const mod = await import(`/static/v6/js/pages/${route}.js?v={{CACHEBUST}}`);
        mod.mount(document.getElementById('app'));
      } catch (e) {
        document.getElementById('app').innerHTML = `<div class="error-state">Page not found: ${route}</div>`;
      }
    })();
  </script>
</body>
</html>
```
