---
project: MaxMahon
created: 2026-04-19
last_updated: 2026-04-19
status: done
---

# v4 — UX + Flow Rework: Unified Scan + Home Feed + Real Watchlist

> รื้อ UX ครั้งใหญ่: ยุบ weekly+discovery เป็น scan เดียว, สร้าง Home feed แยกจาก list, ปุ่ม ★ watchlist ทำงานจริง persist, merge 'ค้นพบใหม่' เข้าผ่านเกณฑ์ด้วย NEW badge, เพิ่ม history menu + per-stock timeline, real-time refresh หลัง scan. Wipe 18 หุ้น seed ที่ Claude เก่าตั้งเอง (user ไม่ได้เลือก)

## Phase 1: Backend — Unified Scan + Data Model + Wipe Watchlist
- [x] สร้าง scripts/scan.py รวม logic จาก analyze.py + discover.py: screen 933 → quality score → Claude วิเคราะห์ 6 ด้าน top candidates + watchlist stocks พร้อมกัน → 1 markdown report มี 4 section (Top Picks / Watchlist Update / New In Batch / Watch Out) · sections จัด conditionally (watchlist empty = skip section)
- [x] สร้าง scripts/run_scan.py แทน run_weekly.py: fetch_data (watchlist) + update_universe (ถ้าเก่ากว่า 7 วัน) + screen_stocks + scan.py · update scheduler ใน server/app.py: ลบ get_week_of_month()+odd/even logic ใช้ cron weekly ตรงๆ (รันทุก sun 09:00) เรียก scan อย่างเดียว
- [x] สร้าง data/history.json index: เพิ่ม entry ทุกครั้งหลัง scan เสร็จ (scan_num, date, type='scan', counts: {scanned, passed, new, filtered}, summary_one_line, report_file) + endpoint /api/history return list · Wipe user_data.json: set watchlist=[] (backup user_data.json → user_data.backup.json ก่อน) + ลบ endpoint /api/reports/weekly + route GET /api/scan/trigger POST สำหรับ manual scan

### Reference
```python
# scripts/scan.py โครงสร้าง
# 1. load screener_*.json (จาก screen_stocks.py รันก่อน)
# 2. load user_data.json → watchlist symbols
# 3. จัด 3 groups:
#    - top_candidates = screener passed, ไม่อยู่ใน watchlist, score>=50
#    - watchlist_current = watchlist stocks ที่อยู่ใน screener (pass หรือ filtered_out)
#    - new_in_batch = top_candidates ที่ไม่เคยผ่านเกณฑ์ใน screener_*.json รอบก่อน
# 4. build prompt system (framework + rules) + user (data ทั้ง 3 groups)
# 5. call anthropic SDK (Opus 4.7) + prompt caching
# 6. save report.md + append history.json entry

# server/app.py — replace scheduled_run
def scheduled_run():
    if not config['schedule']['enabled']:
        return
    scripts = ['fetch_data.py', 'update_universe.py', 'screen_stocks.py', 'scan.py']
    _execute_sync(scripts, 'scheduled scan')

# data/history.json
{
  "scans": [
    {
      "num": 17,
      "date": "2026-04-19T09:32:00",
      "counts": {"scanned": 933, "passed": 21, "new": 3, "filtered": 912},
      "summary": "CPALL, BDMS, SCB เด่น · +3 ใหม่",
      "report": "scan_2026-04-19.md"
    }
  ]
}
```

## Phase 2: Home Feed Page (Desktop + Mobile)
- [x] Desktop: สร้างโครง page-home ใน web/index.html — ย้าย thesis + at-a-glance + latest report card ออกจาก layout ปัจจุบัน (ที่โผล่ทุก tab) มาอยู่ใน page-home · tab อื่น (หุ้น/ติดตาม/ประวัติ/ตั้งค่า) header บางลง แสดงแค่ masthead-slim + tab name · default landing = home · add new nav tab 'หน้าแรก' (◉) เป็น tab แรก · latest report card clickable → scroll/nav ไปหน้า full report
- [x] Mobile: rewrite web/mobile.html โครงหน้า Home ตาม mockup #01 (mockup-flow.html) — ใช้ editorial palette + fonts + masthead + bottom nav ตาม desktop pattern · rebuild page-stocks/page-history/page-watchlist ใหม่หมด · copy editorial chrome CSS จาก desktop style.css + adjust viewport · ไม่ต้องทำ detail/history/report viewer ใน phase นี้ (ไปทำต่อใน phase 4-5)

### Reference
```html
<!-- web/index.html — ADD new page-home -->
<section class="page" data-page="home" style="display:block">
  <!-- existing thesis + at-a-glance + latest report -->
</section>
<section class="page" data-page="stocks" style="display:none">
  <!-- filter tabs + stock list (WITHOUT thesis/at-a-glance) -->
</section>

<!-- masthead slim variant -->
<header class="masthead slim">
  <div class="mast-meta">SCAN #17</div>
  <div class="mast-title">หุ้น</div>
  <div class="scan-chip">21/933</div>
</header>
```

## Phase 3: Unified Stock List + Watchlist Fix (Desktop + Mobile)
- [x] Desktop + Mobile: ลบ tab 'ค้นพบใหม่' + data-tab='discovery' logic ใน app.js/mobile.html · merge candidates ทั้งหมดเข้า tab 'ผ่านเกณฑ์' · เพิ่ม NEW badge บน card ถ้า stock.is_new_in_batch=true (cross-check กับ screener_*.json ก่อนหน้า — ไม่เคยผ่าน = ใหม่)
- [x] Desktop + Mobile: ซ่อม tab 'ติดตาม' — เปลี่ยนตรรกะจาก candidates.filter(c => c.in_watchlist) เป็น load user_data.watchlist → overlay status จาก screener (pass = แสดง card ปกติ + score, fail = แสดง card + fail-badge 'หลุดรอบนี้' + reason จาก screener.filtered_out_stocks) · ตัวที่ไม่อยู่ใน screener เลย = แสดง card เหลือ static info ไม่มี score
- [x] Desktop + Mobile: ปุ่ม ★ บน card + detail panel header: toggle follow/unfollow · on click → PUT /api/user/watchlist ด้วย watchlist list ใหม่ (add หรือ remove symbol) · optimistic UI (update star ทันที revert ถ้า fail) · star bright amber เมื่อ on · test end-to-end กด + บน card → ไปที่ tab ติดตาม เห็นตัวที่เพิ่ง follow · reload page ยังอยู่

### Reference
```javascript
// app.js — replace watchlist filter logic
async function renderWatchlistTab() {
  const watchSyms = new Set((userData.watchlist || []).map(s => _normSym(s)));
  const scr = state.screener || {};
  const passed = (scr.candidates || []).filter(c => watchSyms.has(_normSym(c.symbol)));
  const failed = (scr.filtered_out_stocks || []).filter(c => watchSyms.has(_normSym(c.symbol)));
  // cards to render:
  const cards = [...passed.map(c => ({...c, status:'pass'})), ...failed.map(c => ({...c, status:'fail'}))];
  // symbols in watchlist but not in screener at all = show static card
  const seenSyms = new Set(cards.map(c => _normSym(c.symbol)));
  const missingSyms = [...watchSyms].filter(s => !seenSyms.has(s));
  missingSyms.forEach(s => cards.push({symbol: s, status: 'unknown'}));
  renderCards(cards);
}

// star toggle handler
async function toggleStar(sym) {
  const list = new Set(userData.watchlist || []);
  if (list.has(sym)) list.delete(sym);
  else list.add(sym);
  userData.watchlist = [...list];
  await fetch(API + '/api/user/watchlist', {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({stocks: userData.watchlist})
  });
  renderCards();
}
```

## Phase 4: History Page + Report Viewer (Desktop + Mobile)
- [x] Desktop + Mobile: สร้าง page-history — GET /api/history + render list เรียงใหม่→เก่า · แต่ละ item แสดง scan number, date, summary 1 line, stats (passed/new/filtered) · tap → navigate to report viewer ด้วย scan_num
- [x] Desktop + Mobile: สร้าง page-report (report viewer) — fetch /api/reports/scan?num=17 (new endpoint) หรือ /api/reports/scan/latest · render markdown เป็น HTML ด้วย editorial CSS (serif h2 with § prefix, pick boxes, hard shadow) · back arrow ที่ top กลับไปหน้าก่อน (Home หรือ History, ใช้ browser history.back()) · page แสดง masthead slim + content flow ไม่ใช่ overlay

### Reference
```python
# server/app.py — new endpoint
@app.get('/api/reports/scan')
async def get_scan_report(num: Optional[int] = None):
    history = read_json(DATA_DIR / 'history.json')
    entry = None
    if num is None:
        entry = history['scans'][0] if history.get('scans') else None
    else:
        entry = next((s for s in history['scans'] if s['num'] == num), None)
    if not entry:
        raise HTTPException(404)
    path = REPORTS_DIR / entry['report']
    if not path.exists():
        raise HTTPException(404)
    html = markdown.markdown(path.read_text(encoding='utf-8'), extensions=['tables','fenced_code'])
    return {'num': entry['num'], 'date': entry['date'], 'html': html, 'stats': entry['counts']}
```

## Phase 5: Stock Detail + History Tab (Desktop + Mobile)
- [x] Desktop + Mobile: เพิ่ม tab row บน detail panel: 'ภาพรวม' (ปัจจุบัน), 'ประวัติ', 'เปรียบเทียบ' (placeholder) · overview tab = ของเดิม · history tab = ใหม่
- [x] Desktop + Mobile: History tab content — SVG score timeline chart (read จาก /api/stock/{sym}/history) + events log (entered watchlist, exited, signal change, passed, failed) · backend endpoint aggregates จาก screener_*.json ทุกไฟล์ย้อนหลัง + user_data.json history (ต้อง track watchlist mutations — เพิ่ม log entries ลง data/watchlist_events.jsonl ทุกครั้งที่ PUT /api/user/watchlist)

### Reference
```python
# server/app.py
@app.get('/api/stock/{symbol}/history')
async def get_stock_history(symbol: str):
    sym = _norm_sym(symbol)
    timeline = []
    for scr_file in sorted(DATA_DIR.glob('screener_*.json')):
        data = read_json(scr_file)
        date = data.get('date', scr_file.stem.replace('screener_', ''))
        for c in data.get('candidates', []):
            if _norm_sym(c.get('symbol','')) == sym:
                timeline.append({
                    'scan_date': date,
                    'scan_num': data.get('scan_num'),
                    'score': c.get('score'),
                    'signals': c.get('signals', []),
                    'passed': True,
                })
                break
        else:
            for c in data.get('filtered_out_stocks', []):
                if _norm_sym(c.get('symbol','')) == sym:
                    timeline.append({
                        'scan_date': date,
                        'score': None,
                        'passed': False,
                        'reasons': c.get('filter_reasons', [])
                    })
                    break
    # events = compute from timeline diffs + watchlist_events.jsonl filtered by symbol
    events = _compute_events(timeline, sym)
    return {'timeline': timeline, 'events': events}
```

## Phase 6: Real-time SSE Banner + Auto-refresh
- [x] Desktop + Mobile: SSE listener ใน frontend app.js/mobile.html — subscribe /api/events (EventSource) · เมื่อ pipeline_running=true → แสดง running-banner amber + 'กำลังวิเคราะห์...' + dot-pulse animation · เมื่อ pipeline_running เปลี่ยนจาก true→false + last_result ใหม่ → แสดง toast 'รายงาน #N พร้อม' + auto reload home feed + history list · toast tap = navigate to report viewer

### Reference
```javascript
// app.js
let lastRunningState = false;
const es = new EventSource(API + '/api/events');
es.addEventListener('status', (evt) => {
  const s = JSON.parse(evt.data);
  const banner = document.getElementById('running-banner');
  if (s.pipeline_running) {
    banner.style.display = 'flex';
    banner.textContent = 'กำลังวิเคราะห์ · ' + (s.current_task || 'กำลังทำงาน');
  } else {
    banner.style.display = 'none';
  }
  // detect completion
  if (lastRunningState && !s.pipeline_running && s.last_result) {
    showToast('รายงาน #' + s.last_result.scan_num + ' พร้อม', () => goToReport(s.last_result.scan_num));
    refreshFeed();
  }
  lastRunningState = s.pipeline_running;
});
```

## Phase 7: Cleanup + v4.0 Release
- [x] ลบไฟล์ deprecated: scripts/analyze.py, scripts/run_weekly.py, /api/reports/weekly endpoint, DEFAULT_CONFIG.pipeline.odd_weeks/even_weeks fields · update pipeline action buttons ใน UI: ลบปุ่ม 'Weekly'/'Discovery' เหลือ 'Scan' เดียว · กด 'Scan' = POST /api/scan/trigger
- [x] Update CHANGELOG.md v4.0.0 (breaking change) — อธิบาย flow rework · update projects/MaxMahon/CLAUDE.md Architecture section · update mockup-flow.html add 'status: approved' comment · commit + push submodule + parent sync · tag v4.0.0
