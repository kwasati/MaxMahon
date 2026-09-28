---
project: maxmahon
created: 2026-04-22
last_updated: 2026-04-23
status: done
---

# MaxMahon v6 · Settings Page

> Part 8 of 9 — auto scan + Niwes thresholds + universe selector, desktop + mobile | Index: maxmahon-v6-index
> Depends on: maxmahon-v6-03-frontend-foundation
> Parallel-safe with: 04, 05, 06, 07

## Phase 1: Settings page (desktop)
- [x] Create `projects/MaxMahon/web/v6/desktop/settings.html` + `projects/MaxMahon/web/v6/static/js/pages/settings.js`. Fetch GET /api/settings on mount. Render 3 blocks per mockup: (a) Auto Scan — enabled switch (schedule.enabled), day-of-week chips (Sun-Sat, single select from schedule.day_of_week), time input (HH:MM from schedule.hour/minute), 'next run' label showing response.next_run_at formatted ('Sat 26 Apr 2026, 09:00'); (b) Niwes Thresholds — 5 sliders: Min Yield % (range 0-20 step 0.5, default 5.0), Min Streak years (1-20, default 5), Max P/E (5-30, default 15), Max P/BV (0.5-5.0 step 0.1, default 1.5), Min Mcap (฿B slider 1-50, default 5); each slider shows current numeric value next to label; (c) Stock Universe — radio card group: SET Only (704) / SET + mai (933, default) per response.universe. Save All Changes button at bottom + 'last saved' timestamp showing `last_saved_at` formatted. Scope: desktop layout. Acceptance: visual match `web-v6-mockup/desktop/06-settings.html` 100%; all fields populated from API; sliders show current values.
- [x] Implement Save action in settings.js: collect form state → POST /api/settings with body {schedule:{enabled, day_of_week, hour, minute}, filters:{min_dividend_yield, min_dividend_streak, max_pe, max_pbv, min_market_cap}, universe}. On success: show toast, update 'last saved' label to new timestamp, update 'next run' label to new next_run_at. On error: show error toast with server message; do not clear form. Scope: one submit handler. Acceptance: editing yield slider from 5.0 → 6.0 + Save → config.json reflects 6.0; last_saved_at updates to current time; next_run_at recalculates if schedule changed.

### Reference
```javascript
// pages/settings.js save
async function onSave() {
  const body = {
    schedule: {
      enabled: document.getElementById('sched-enabled').checked,
      day_of_week: document.querySelector('.day-chip.active').dataset.day,
      hour: parseInt(document.getElementById('sched-hour').value, 10),
      minute: parseInt(document.getElementById('sched-minute').value, 10),
    },
    filters: {
      min_dividend_yield: parseFloat(document.getElementById('f-yield').value),
      min_dividend_streak: parseInt(document.getElementById('f-streak').value, 10),
      max_pe: parseFloat(document.getElementById('f-pe').value),
      max_pbv: parseFloat(document.getElementById('f-pbv').value),
      min_market_cap: parseInt(document.getElementById('f-mcap').value, 10) * 1e9,
    },
    universe: document.querySelector('input[name="universe"]:checked').value,
  };
  try {
    const r = await MMApi.post('/api/settings', body);
    MMComponents.showToast('Saved', 'success');
    document.getElementById('last-saved').textContent = `Last saved: ${formatDate(r.last_saved_at)}`;
    document.getElementById('next-run').textContent = r.next_run_display;
    dirty = false;
  } catch (e) { MMComponents.showToast(e.message, 'error'); }
}
```

## Phase 2: Settings page (mobile)
- [x] Port `projects/MaxMahon/web-v6-mockup/mobile/06-settings.html` to `projects/MaxMahon/web/v6/mobile/settings.html` + extend `pages/settings.js` mobile branch. Mobile: stacked form (each block full-width), mobile-optimized sliders (larger touch targets per `shared/mobile.css`), universe radio as vertical stack. Scope: mobile variant. Acceptance: visual match mockup 100%; all fields render; Save button docked at viewport bottom (sticky).

## Phase 3: Client-side validation + unsaved-changes warning
- [x] Add unsaved-changes tracking in `projects/MaxMahon/web/v6/static/js/pages/settings.js`: maintain `dirty` flag, set true on any input change, reset to false after successful Save. On `beforeunload` window event, if dirty === true, trigger native browser 'unsaved changes' prompt (e.ReturnValue = true). Scope: one flag + one event listener. Acceptance: editing a slider then clicking nav link triggers browser confirm; Save then nav away does not trigger.
- [x] Add client-side validation in settings.js before Save: yield >= 0, streak >= 1, max_pe > 0, max_pbv > 0, min_market_cap > 0. If any invalid, highlight field with error class + show toast 'กรอกค่าให้ถูกต้อง' and abort POST. Scope: one validator function. Acceptance: setting yield to -1 + Save → does not POST; field highlighted red; toast shown.
