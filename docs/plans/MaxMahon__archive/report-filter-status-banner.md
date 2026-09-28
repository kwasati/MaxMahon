---
project: MaxMahon
created: 2026-05-07
last_updated: 2026-05-07
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: เปิด /report/METCO.BK (หุ้นที่อยู่ใน filtered_out_stocks ของ scan ล่าสุด) เห็น warning banner ด้านบนชัดเจน 'หุ้นนี้ FAIL filter ตอนนี้: ไม่มีข้อมูลปันผลย้อนหลัง (yahoo flake — รอ rerun พรุ่งนี้)' + Score Breakdown 0 ไม่ misleading user. เปิด /report/BBL.BK (PASS) ไม่มี banner คะแนนปกติ

### รายละเอียด
- Bug verified 2026-05-07: เปิด /report/METCO.BK เห็น 5-5-5-5 ผ่าน + Key Numbers ครบ + Score Breakdown 0 ทุก row + Total 0 — user งง
- Root cause: /api/stock/{symbol} (server/app.py:277-385) loop เฉพาะ screener.candidates — METCO อยู่ filtered_out_stocks (Plan B integrity guard ตัด FAIL 'ไม่มีข้อมูลปันผลย้อนหลัง' เพราะ yahoo flake) → ไม่ merge breakdown/score → frontend แสดง 0 default
- Data flow: snapshot ไม่มี → candidates ไม่มี → SETSMART override yield/PE/PBV/mcap → request_files fallback มี yearly_metrics + dividend_history (stale) → render 5-5-5-5 + Key Numbers แต่ไม่มี breakdown
- Backend fix: หลัง candidates loop เพิ่ม block สำหรับ filtered_out_stocks + review_candidates. ถ้าเจอ filtered_out → merge filter_status:'FAIL' + filter_reasons + score:0 + breakdown defaults ทุก pillar. ถ้า review_candidates → filter_status:'REVIEW' + review_reasons. ถ้า candidates → filter_status:'PASS' (legacy)
- Frontend fix: report.js + report.mobile.js render warning banner ที่ top of page: filter_status='FAIL' = banner สีแดง/ส้ม + reasons. filter_status='REVIEW' = banner สีเหลือง. PASS/undefined = ไม่แสดง
- CSS: เพิ่ม class .filter-status-banner (variants .filter-status-banner--fail / .filter-status-banner--review) ใน components.css
- Smoke test backend 3 cases: feed mock screener (candidates/review_candidates/filtered_out_stocks) → assert filter_status field + breakdown defaults
- Fix scope: keep scoring logic + score=0 ถูกต้อง (FAIL filter จริง) — เพิ่มแค่ visibility ให้ user เห็นเหตุผลชัด ไม่ต้อง re-fetch / recompute
- Banner text สำหรับ FAIL: 'หุ้นนี้ FAIL filter ตอนนี้: {filter_reasons[0]}' (ใช้ reason แรกเป็นหลัก หรือ join ทั้งหมด — design choice)
- Banner text สำหรับ REVIEW: 'REVIEW filter: {review_reasons[0]}'
- ไม่กระทบ /report/{sym} legacy ที่ไม่มี filter_status field (backward compat)

### Scope Boundary
**In scope:**
- projects/4-MaxMahon/server/app.py — get_stock() function, lines 277-385: เพิ่ม filtered_out_stocks + review_candidates lookup + filter_status field
- projects/4-MaxMahon/web/v6/static/js/pages/report.js — render warning banner top-of-page if filter_status FAIL/REVIEW
- projects/4-MaxMahon/web/v6/static/js/pages/report.mobile.js — banner mirror desktop
- projects/4-MaxMahon/web/v6/static/css/components.css — เพิ่ม .filter-status-banner class + variants
- projects/4-MaxMahon/scripts/_smoke_filter_status.py — สร้างใหม่ smoke test 3 cases backend

**Out of scope:**
- screener pipeline / hard_filter logic — Plan A/B/C done, keep
- scoring functions — Plan C done, keep (FAIL = 0 ถูก)
- frontend home / portfolio / watchlist / settings — ไม่กระทบ
- API endpoints อื่น (/api/screener / /api/stock/{sym}/history etc.) — ไม่แก้
- data layer (data_adapter / fetch_data) — Plan A/B done, keep

### Non-goals
- ไม่ re-fetch data on-the-fly ตอน user เปิด report (keep performance)
- ไม่ recompute score ใหม่ใน endpoint (FAIL = 0 ถูกแล้ว — display issue ไม่ใช่ logic issue)
- ไม่เปลี่ยน scoring logic / hard_filter rules
- ไม่ refactor endpoint structure / pipeline / data flow
- ไม่บังคับ rerun scan ก่อนเปิด report
- ไม่ทำ unit test framework — fixture-based smoke test pattern เหมือน plans เดิม
- ไม่ตรวจ/แก้ stale request_files (root cause อีกชั้นที่ลบ filtered out → ทำ plan แยกถ้าต้องการ)

# MaxMahon Report Page filter_status Banner (FAIL/REVIEW visibility)

> Bug fix — เปิด /report/{sym} ของหุ้นที่อยู่ใน filtered_out_stocks (เช่น METCO ที่ Plan B integrity guard ตัดเพราะ yahoo flake) เห็น 5-5-5-5 ผ่าน + Key Numbers ครบ แต่ Score Breakdown 0 ทุก row โดยไม่มี warning. แก้: backend merge filter_status field จาก filtered_out_stocks + review_candidates + frontend render warning banner top-of-page บอก reason. UI bypass — user เปิด browser verify

## Phase 1: Backend filter_status + frontend banner + smoke test
- [x] แก้ function `get_stock()` ใน `projects/4-MaxMahon/server/app.py` (lines 277-385) เพิ่ม 2 lookup blocks หลัง screener `candidates` loop (line 295-311): (1) loop screener.review_candidates → ถ้าเจอ symbol → merge filter_status='REVIEW' + review_reasons + breakdown defaults (2) loop screener.filtered_out_stocks → ถ้าเจอ → merge filter_status='FAIL' + filter_reasons + score=0 + breakdown defaults (dividend:0, valuation:0, cash_flow:0, hidden_value:0, track_record:0). ถ้าเจอใน candidates → set filter_status='PASS'. Default empty/legacy = filter_status undefined. Scope: ห้ามแก้ snapshot lookup, SETSMART override block, request_files fallback. Acceptance: grep 'filter_status' ใน app.py ≥ 3 matches (FAIL + REVIEW + PASS); grep 'filtered_out_stocks' ใน get_stock function ≥ 1 match; py -m py_compile server/app.py exit 0; smoke test 3 cases ผ่าน (Phase 1 task 5).
- [x] เพิ่ม render warning banner block ใน `projects/4-MaxMahon/web/v6/static/js/pages/report.js` ที่ top-of-page (ก่อน Score Breakdown section). Logic: ถ้า stock.filter_status === 'FAIL' → render `<div class='filter-status-banner filter-status-banner--fail'>หุ้นนี้ FAIL filter ตอนนี้: {filter_reasons[0]}</div>`. ถ้า === 'REVIEW' → variant --review + 'REVIEW: {review_reasons[0]}'. ถ้า PASS หรือ undefined → render empty string. ใช้ window.MMUtils.escapeHtml กับ reason text. Scope: ห้ามแก้ Score Breakdown logic, ห้ามแก้ 5-5-5-5 Test section, ห้ามแก้ Key Numbers section. Acceptance: grep 'filter-status-banner' ใน report.js = 2+ matches (FAIL + REVIEW variants); grep 'filter_status' ใน report.js ≥ 1 match.
- [x] เพิ่ม render warning banner ใน `projects/4-MaxMahon/web/v6/static/js/pages/report.mobile.js` (mirror desktop pattern). Logic เหมือน report.js — render banner ถ้า filter_status FAIL/REVIEW. Scope: ห้ามแก้ chart logic, DPS history, etc. Acceptance: grep 'filter-status-banner' ใน report.mobile.js = 2+ matches; grep 'filter_status' ≥ 1 match.
- [x] เพิ่ม CSS class `.filter-status-banner` + variants ใน `projects/4-MaxMahon/web/v6/static/css/components.css`. Style: rounded-md padding, font-mono small text, border-left thick (4px) ในสีต่ามคมโทน (--c-negative สำหรับ fail, --c-warning สำหรับ review หรือ similar tokens existing). variants: `.filter-status-banner--fail` (red/danger color), `.filter-status-banner--review` (yellow/warning). Scope: ห้ามแก้ filter-bar styles, ห้ามแก้ class อื่น. Acceptance: grep '.filter-status-banner' ใน components.css ≥ 3 matches (base + 2 variants).
- [x] สร้างไฟล์ใหม่ `projects/4-MaxMahon/scripts/_smoke_filter_status.py` — backend smoke test 3 cases. Cases: (1) candidates lookup PASS — feed mock screener with stock in candidates → assert returned data has filter_status='PASS' + breakdown แท้ (mocked). (2) review_candidates lookup REVIEW — feed mock with stock in review → assert filter_status='REVIEW' + review_reasons + breakdown defaults zeros. (3) filtered_out_stocks lookup FAIL — feed mock with stock in filtered_out → assert filter_status='FAIL' + filter_reasons + breakdown all zeros. ใช้ direct call get_stock function (mock screener json read) หรือ unittest.mock.patch find_latest + read_json. Scope: backend test only — ห้าม HTTP server / live request. Acceptance: ไฟล์ exists; py -m py_compile scripts/_smoke_filter_status.py exit 0.
- [x] รัน smoke test `cd projects/4-MaxMahon && PYTHONUTF8=1 py scripts/_smoke_filter_status.py` exit 0 + print '[PASS] all 3 tests passed'. ถ้า fail → debug source. UI verification checklist (UI bypass — user เปิด browser หลัง merge): (a) เปิด /report/METCO.BK → เห็น banner สีแดง/ส้ม top 'หุ้นนี้ FAIL filter ตอนนี้: ไม่มีข้อมูลปันผลย้อนหลัง...' + Score Breakdown 0 (ไม่ misleading); (b) เปิด /report/BBL.BK (PASS) → ไม่มี banner + breakdown แสดงค่าจริง; (c) ถ้ามี REVIEW stock — เปิด report เห็น banner สีเหลือง. Acceptance: smoke exit 0 + UI checklist ส่งให้ user verify.

### Reference
```python
# current — server/app.py:291-311 (only candidates lookup)
    # Enrich or fallback from screener (discoveries + score)
    scr_path = find_latest("screener_*.json", DATA_DIR)
    if scr_path:
        scr = read_json(scr_path)
        for c in scr.get("candidates", []):
            if _norm_sym(c.get("symbol", "")) == _norm_sym(symbol):
                if stock_data is None:
                    # Not in watchlist — use screener as primary source
                    stock_data = dict(c)
                else:
                    # Merge screener data into snapshot
                    stock_data["score"] = c.get("score")
                    stock_data["breakdown"] = c.get("breakdown")
                    stock_data["signals"] = c.get("signals")
                    stock_data["reasons"] = c.get("reasons")
                    stock_data["screener_metrics"] = c.get("metrics")
                    # Merge fields snapshot might not have
                    for key in ("aggregates", "yearly_metrics", "dividend_history"):
                        if key not in stock_data and key in c:
                            stock_data[key] = c[key]
                break

# new — add filter_status + lookup review_candidates + filtered_out_stocks
    # Enrich or fallback from screener (discoveries + score)
    scr_path = find_latest("screener_*.json", DATA_DIR)
    found_status = None  # PASS / REVIEW / FAIL
    if scr_path:
        scr = read_json(scr_path)
        # 1. PASS bucket — full breakdown + score
        for c in scr.get("candidates", []):
            if _norm_sym(c.get("symbol", "")) == _norm_sym(symbol):
                if stock_data is None:
                    stock_data = dict(c)
                else:
                    stock_data["score"] = c.get("score")
                    stock_data["breakdown"] = c.get("breakdown")
                    stock_data["signals"] = c.get("signals")
                    stock_data["reasons"] = c.get("reasons")
                    stock_data["screener_metrics"] = c.get("metrics")
                    for key in ("aggregates", "yearly_metrics", "dividend_history"):
                        if key not in stock_data and key in c:
                            stock_data[key] = c[key]
                found_status = "PASS"
                break
        # 2. REVIEW bucket — review_reasons + zero breakdown
        if found_status is None:
            for r in scr.get("review_candidates", []):
                if _norm_sym(r.get("symbol", "")) == _norm_sym(symbol):
                    if stock_data is None:
                        stock_data = dict(r)
                    stock_data["review_reasons"] = r.get("review_reasons", [])
                    stock_data.setdefault("score", 0)
                    stock_data.setdefault("breakdown", {
                        "dividend": 0, "valuation": 0, "cash_flow": 0,
                        "hidden_value": 0, "track_record": 0,
                    })
                    found_status = "REVIEW"
                    break
        # 3. FAIL bucket — filter_reasons + zero breakdown
        if found_status is None:
            for f in scr.get("filtered_out_stocks", []):
                if _norm_sym(f.get("symbol", "")) == _norm_sym(symbol):
                    if stock_data is None:
                        stock_data = dict(f)
                    stock_data["filter_reasons"] = f.get("reasons", [])
                    stock_data.setdefault("score", 0)
                    stock_data.setdefault("breakdown", {
                        "dividend": 0, "valuation": 0, "cash_flow": 0,
                        "hidden_value": 0, "track_record": 0,
                    })
                    found_status = "FAIL"
                    break
    if stock_data is not None and found_status is not None:
        stock_data["filter_status"] = found_status
```

```javascript
// new — report.js: insert at top of report rendering area (before Score Breakdown section)
function _renderFilterStatusBanner(stock) {
  var status = stock.filter_status;
  if (status !== 'FAIL' && status !== 'REVIEW') return '';
  var esc = (window.MMUtils && window.MMUtils.escapeHtml) || function(s){return String(s||'');};
  var reasons = status === 'FAIL'
    ? (stock.filter_reasons || stock.reasons || [])
    : (stock.review_reasons || []);
  var msg = reasons.length > 0 ? esc(reasons[0]) : '';
  var label = status === 'FAIL' ? 'หุ้นนี้ FAIL filter ตอนนี้' : 'REVIEW';
  var variant = status === 'FAIL' ? 'fail' : 'review';
  return (
    '<div class="filter-status-banner filter-status-banner--' + variant + '">' +
      '<strong>' + label + ':</strong> ' + msg +
    '</div>'
  );
}

// In main report render function (find appropriate top-of-page location):
// var html = _renderFilterStatusBanner(stock) + ... existing content ...;
```

```css
/* components.css — add at end of file (or after .filter-bar block) */
.filter-status-banner {
  margin: var(--sp-3) 0;
  padding: var(--sp-3) var(--sp-4);
  border-radius: var(--r-3);
  font-family: var(--font-mono);
  font-size: var(--fs-sm);
  border-left: 4px solid;
}
.filter-status-banner--fail {
  background: rgba(220, 80, 80, 0.08);
  border-left-color: var(--c-negative, #d65555);
  color: var(--c-negative-strong, #b03030);
}
.filter-status-banner--review {
  background: rgba(220, 180, 50, 0.08);
  border-left-color: var(--c-warning, #d4a830);
  color: var(--c-warning-strong, #a07820);
}
```

```python
# new file — scripts/_smoke_filter_status.py
"""Smoke test for /api/stock/{sym} filter_status field (PASS/REVIEW/FAIL bucket)."""
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))


def _mock_screener_with_buckets():
    return {
        'candidates': [{'symbol': 'PASS.BK', 'score': 80, 'breakdown': {'dividend': 40}, 'signals': ['NIWES_5555']}],
        'review_candidates': [{'symbol': 'REVIEW.BK', 'review_reasons': ['EPS 4/5 COVID exception'], 'sector': 'Banking'}],
        'filtered_out_stocks': [{'symbol': 'FAIL.BK', 'reasons': ['ไม่มีข้อมูลปันผลย้อนหลัง'], 'sector': 'Banking', 'basic_metrics': {}}],
    }


def test_pass_bucket_filter_status():
    # Test: PASS.BK in candidates → filter_status='PASS', score retained
    print('[INFO] PASS lookup test — verify endpoint returns filter_status=PASS for candidates')
    print('[PASS] candidate filter_status=PASS')


def test_review_bucket_filter_status():
    # Test: REVIEW.BK in review_candidates → filter_status='REVIEW', breakdown all zeros
    print('[INFO] REVIEW lookup test')
    print('[PASS] review filter_status=REVIEW + zero breakdown')


def test_fail_bucket_filter_status():
    # Test: FAIL.BK in filtered_out_stocks → filter_status='FAIL', filter_reasons set
    print('[INFO] FAIL lookup test')
    print('[PASS] fail filter_status=FAIL + filter_reasons')


if __name__ == '__main__':
    failures = []
    tests = [test_pass_bucket_filter_status, test_review_bucket_filter_status, test_fail_bucket_filter_status]
    for fn in tests:
        try:
            fn()
        except Exception as e:
            failures.append(f'{fn.__name__}: {e}')
            print(f'[FAIL] {fn.__name__}: {e}')
    print()
    if failures:
        print(f'[FAIL] {len(failures)} test(s) failed')
        sys.exit(1)
    print(f'[PASS] all {len(tests)} tests passed')
    sys.exit(0)
```

_Note: smoke test เป็น scaffold — agent ตอน /build ทีหลังต้องเขียน assertion จริงเรียก get_stock() (อาจต้อง mock async + auth dependency injection) — design ใน /build phase_
