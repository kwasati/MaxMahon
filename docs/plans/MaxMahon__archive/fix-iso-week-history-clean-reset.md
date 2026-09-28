---
project: MaxMahon
created: 2026-04-28
last_updated: 2026-04-28
status: done
---

## Target / Goal
ทำได้: scan ซ้ำในสัปดาห์ ISO เดียวกัน → history.json มี 1 entry ของ week นั้น (ทับ ไม่ append) + UI trend chart แสดง label W{ISO} + ข้อความ scanned_at timestamp ใต้ chart. ลบ algo output เก่าทั้งหมดทิ้ง clean ก่อน scan รอบใหม่

# Fix scan history → ISO week key + clean reset

> Bug: ทุก scan ใหม่ถูกนับเป็นสัปดาห์ใหม่ (W{scan_sequence_num}) ทั้งที่ปฏิทินจริงอาจเป็นสัปดาห์เดียวกัน (5 scans → W1..W5 แต่ ISO calendar 22-28 เม.ย. = 2 สัปดาห์ W17+W18). แก้ root cause: ใช้ ISO week (Mon-Sun) เป็น key, scan ซ้ำในสัปดาห์เดิม = ทับ entry, เก็บ scanned_at timestamp ของ scan ล่าสุด. ลบ output algo เก่าทั้งหมดเพื่อ scan ใหม่ด้วย algo ที่ update แล้วแบบ clean. v2 fix (qc round 1): ย้าย report_template signature change มาก่อน scan.py + เพิ่ม iso_week_key ใน import + ระบุ server pre-condition.

## Phase 1: Backend Core — history_manager + report_template + scan
- [x] เพิ่ม helper `iso_week_key(d: date) -> str` ใน `projects/MaxMahon/scripts/history_manager.py` คืน format `YYYY-Www` (ใช้ `d.isocalendar()`). แก้ `build_v2_entry()` (บรรทัด 29-95) เปลี่ยน signature เป็น `(screener_data, scanned_at: datetime, report_filename)` (ลบ scan_num) — entry ใหม่มี keys: iso_week (เช่น `"2026-W18"`), scanned_at (ISO `2026-04-28T10:20:00`), date (yyyy-mm-dd ของ scanned_at สำหรับ event derivation), counts/summary/report/scoring_version/top_candidates/watchlist_status/entry_thesis/dividend_paid_since_entry/price_snapshot คงเดิม — ลบ `num` field ออก. — scope: ไม่แตะ load_history() — Acceptance: `iso_week_key(date(2026,4,28))` == `"2026-W18"`; `build_v2_entry(data, datetime(2026,4,28,10,20), "scan_2026-04-28.md")` คืน dict มี iso_week='2026-W18', scanned_at='2026-04-28T10:20:00', date='2026-04-28', ไม่มี key 'num'
- [x] เพิ่ม `upsert_scan_v2(entry, history=None)` ใน `projects/MaxMahon/scripts/history_manager.py` — logic: load history → กรอง scans เหลือแค่ entry ที่ iso_week != entry['iso_week'] → append entry ใหม่ → atomic write. ลบ `append_scan_v2()` ทิ้ง (มี caller เดียวคือ scan.py — แก้ใน task 4). — scope: ไม่ยุ่งกับ build_v2_entry() — Acceptance: stub test: `upsert_scan_v2({'iso_week':'2026-W17','scanned_at':'A',...})` → 1 entry. `upsert_scan_v2({'iso_week':'2026-W17','scanned_at':'B',...})` → ยังมี 1 entry, scanned_at='B'. `upsert_scan_v2({'iso_week':'2026-W18',...})` → 2 entries
- [x] แก้ `projects/MaxMahon/scripts/report_template.py` (ทำก่อน scan.py เพราะ scan.py จะเรียก signature ใหม่): (1) `_fm()` (บรรทัด 36-37) signature เป็น `_fm(date, iso_week, scanned_at, version)` — frontmatter keys: agent, date, type, **iso_week, scanned_at**, scoring_version (ลบ scan_num) (2) `generate_report_md()` (บรรทัด 77) signature เป็น `(screener_data, iso_week: str, scanned_at: datetime, prev_scan)` (3) heading (บรรทัด 99) เป็น `f'# รายงานตรวจหุ้น Niwes 5-5-5-5 (สัปดาห์ {iso_week})'` (4) subtitle (บรรทัด 100) เป็น `f'_วันที่ {date} (ตรวจล่าสุด {scanned_at.strftime("%H:%M")}) · ผ่าน {len(cands)} · review {len(review)} · new {len(new_in)}_'` (5) แก้ `__main__` test fallback ให้ pass `iso_week_key(date.today())` + `datetime.now()` แทน `0` — ต้องเพิ่ม import `from history_manager import iso_week_key` + `from datetime import date` ใน `__main__` block (`if __name__ == "__main__":`) — scope: ไม่แตะ Top Picks/Sector Spread/Review/New In Batch/Watchlist Exit/Watch Out sections — Acceptance: `generate_report_md(data, '2026-W18', datetime(2026,4,28,10,20))` → frontmatter มี `iso_week: 2026-W18` + heading `(สัปดาห์ 2026-W18)` + subtitle มี `(ตรวจล่าสุด 10:20)`
- [x] แก้ `projects/MaxMahon/scripts/scan.py` `main()` (บรรทัด 56-95): (1) ลบ function `next_scan_num()` (บรรทัด 48-53) + การเรียกที่บรรทัด 70 (2) เพิ่ม `scanned_at = datetime.now()` แทน scan_num (3) เปลี่ยน import จาก `from history_manager import build_v2_entry, append_scan_v2` เป็น `from history_manager import build_v2_entry, upsert_scan_v2, iso_week_key` (ครบ 3 ตัว — ขาดตัวใดตัวหนึ่งจะ NameError) (4) เพิ่ม `iso_week = iso_week_key(scanned_at.date())` ก่อนเรียก generate_report_md (5) เปลี่ยน `report_md = generate_report_md(screener_data, iso_week, scanned_at, prev_scan)` (signature ใหม่จาก task 3) (6) เปลี่ยนการสร้าง entry: `history_entry = build_v2_entry(screener_data, scanned_at, report_path.name)` (7) เปลี่ยนการเขียน: `upsert_scan_v2(history_entry, history)` (8) แก้ print: `print(f'history upserted: iso_week={iso_week} scanned_at={scanned_at.isoformat(timespec="seconds")}')` — scope: ไม่แตะ telegram alert + load_history + get_latest_screener — Acceptance: `py -c "import sys; sys.path.insert(0, 'projects/MaxMahon/scripts'); import scan"` ไม่ ImportError + ไม่มี reference `next_scan_num` หรือ `append_scan_v2` ใน scan.py แล้ว (end-to-end run test ใน Phase 4 task 3)

### Reference
```python
# current (history_manager.py:29-105)
def build_v2_entry(screener_data: dict, scan_num: int, report_filename: str) -> dict:
    cands = screener_data.get("candidates", [])
    review = screener_data.get("review_candidates", [])
    top = sorted(cands, key=lambda x: x.get("score", 0), reverse=True)[:15]
    # ... (top_candidates, watchlist_status, entry_thesis, price_snapshot)
    return {
        "num": scan_num,
        "date": datetime.now().isoformat(timespec="seconds"),
        "counts": {...},
        "summary": ...,
        "report": report_filename,
        "scoring_version": ...,
        "top_candidates": top_candidates,
        # ...
    }

def append_scan_v2(entry: dict, history: dict | None = None) -> dict:
    hist = history or load_history()
    hist.setdefault("scans", []).append(entry)
    _HISTORY_PATH.write_text(json.dumps(hist, indent=2, ensure_ascii=False), encoding="utf-8")
    return hist

# new
from datetime import datetime, date

def iso_week_key(d: date) -> str:
    """Return ISO week key like '2026-W17' (Mon-Sun, ISO 8601)."""
    iso = d.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"

def build_v2_entry(screener_data: dict, scanned_at: datetime, report_filename: str) -> dict:
    cands = screener_data.get("candidates", [])
    review = screener_data.get("review_candidates", [])
    top = sorted(cands, key=lambda x: x.get("score", 0), reverse=True)[:15]
    # ... (top_candidates, watchlist_status, entry_thesis, price_snapshot ตามเดิม)
    return {
        "iso_week": iso_week_key(scanned_at.date()),
        "scanned_at": scanned_at.isoformat(timespec="seconds"),
        "date": scanned_at.strftime("%Y-%m-%d"),
        "counts": {...},
        "summary": ...,
        "report": report_filename,
        "scoring_version": ...,
        "top_candidates": top_candidates,
    }

def upsert_scan_v2(entry: dict, history: dict | None = None) -> dict:
    """Replace entry of same iso_week, or append if new week."""
    hist = history or load_history()
    iso_wk = entry["iso_week"]
    scans = [s for s in hist.get("scans", []) if s.get("iso_week") != iso_wk]
    scans.append(entry)
    hist["scans"] = scans
    _HISTORY_PATH.write_text(json.dumps(hist, indent=2, ensure_ascii=False), encoding="utf-8")
    return hist
```

```python
# current (report_template.py:36-37, 77, 98-100, 118-122 __main__)
def _fm(date: str, scan_num: int, version: str) -> str:
    return f"---\nagent: Max Mahon v5\ndate: {date}\ntype: scan\nscan_num: {scan_num}\nscoring_version: {version}\n---\n"

def generate_report_md(screener_data: dict, scan_num: int, prev_scan: dict | None = None) -> str:
    # ...
    parts = [
        _fm(date, scan_num, version),
        f"# รายงานตรวจหุ้น Niwes 5-5-5-5 (รอบที่ {scan_num})\n",
        f"_วันที่ {date} · ผ่าน {len(cands)} · review {len(review)} · new {len(new_in)}_\n",
    ]

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3 and sys.argv[1] == "--test":
        data = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        print(generate_report_md(data, 0))

# new
from datetime import datetime

def _fm(date: str, iso_week: str, scanned_at: datetime, version: str) -> str:
    return (
        f"---\nagent: Max Mahon v5\ndate: {date}\ntype: scan\n"
        f"iso_week: {iso_week}\nscanned_at: {scanned_at.isoformat(timespec='seconds')}\n"
        f"scoring_version: {version}\n---\n"
    )

def generate_report_md(screener_data: dict, iso_week: str, scanned_at: datetime, prev_scan: dict | None = None) -> str:
    # ...
    parts = [
        _fm(date, iso_week, scanned_at, version),
        f"# รายงานตรวจหุ้น Niwes 5-5-5-5 (สัปดาห์ {iso_week})\n",
        f"_วันที่ {date} (ตรวจล่าสุด {scanned_at.strftime('%H:%M')}) · ผ่าน {len(cands)} · review {len(review)} · new {len(new_in)}_\n",
    ]

if __name__ == "__main__":
    import sys
    from datetime import date
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from history_manager import iso_week_key
    if len(sys.argv) >= 3 and sys.argv[1] == "--test":
        data = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        print(generate_report_md(data, iso_week_key(date.today()), datetime.now()))
```

```python
# current (scan.py:48-95)
def next_scan_num(history: dict) -> int:
    scans = history.get("scans", [])
    if not scans:
        return 1
    nums = [s.get("num", 0) for s in scans]
    return max(nums) + 1

def main():
    # ...
    history = load_history()
    scan_num = next_scan_num(history)
    today = datetime.now().strftime("%Y-%m-%d")
    # ...
    report_path = REPORTS_DIR / f"scan_{today}.md"
    report_md = generate_report_md(screener_data, scan_num, prev_scan)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"report written: {report_path}")

    from history_manager import build_v2_entry, append_scan_v2
    history_entry = build_v2_entry(screener_data, scan_num, report_path.name)
    append_scan_v2(history_entry, history)
    print(f"history entry appended: scan_num={scan_num}")

# new (scan.py:48-95)
# (ลบ next_scan_num ทั้ง function)

def main():
    # ...
    history = load_history()
    scanned_at = datetime.now()
    today = scanned_at.strftime("%Y-%m-%d")
    # ...
    from history_manager import build_v2_entry, upsert_scan_v2, iso_week_key
    iso_week = iso_week_key(scanned_at.date())
    report_path = REPORTS_DIR / f"scan_{today}.md"
    report_md = generate_report_md(screener_data, iso_week, scanned_at, prev_scan)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"report written: {report_path}")

    history_entry = build_v2_entry(screener_data, scanned_at, report_path.name)
    upsert_scan_v2(history_entry, history)
    print(f"history upserted: iso_week={iso_week} scanned_at={scanned_at.isoformat(timespec='seconds')}")
```

## Phase 2: Server API
- [x] แก้ `/api/screener/trend` ใน `projects/MaxMahon/server/app.py` (บรรทัด 2404-2432): (1) เปลี่ยน `week_label` จาก `f'W{num}'` เป็น `s.get('iso_week','').split('-W')[-1]` แล้ว prepend 'W' เช่น `'W18'` (fallback `scan_date` ถ้าไม่มี iso_week) (2) เพิ่ม field `iso_week` (full key) + `scanned_at` (ISO timestamp) ใน week dict — scope: ไม่แตะ counts derivation, ไม่แตะ /api/history/v2, ไม่แตะ avg_yield/top_score logic — Acceptance: GET `/api/screener/trend?weeks=4` คืน `{weeks:[{week_label:'W18', iso_week:'2026-W18', scanned_at:'2026-04-28T10:20:00', scan_date:'2026-04-28', passed, review, avg_yield, top_score}, ...]}`
- [x] แก้ `/api/stock/{symbol}/history` ใน `projects/MaxMahon/server/app.py` (บรรทัด 599-738): (1) เปลี่ยน `scan_nums: dict[str, int]` (บรรทัด 614) เป็น `iso_weeks: dict[str, str]` + `iso_weeks[date_key] = s.get('iso_week')` (บรรทัด 623) (2) ใน timeline build (บรรทัด 632-657): `scan_num = scan_nums.get(date)` → `iso_week = iso_weeks.get(date)`, field `'scan_num': scan_num` → `'iso_week': iso_week` (ทุก timeline.append + events.append ทั้ง 7 จุด: บรรทัด 638, 652, 688, 697, 705, 715, 729) (3) docstring (บรรทัด 604-605) แก้ `scan_num` → `iso_week` — scope: ไม่แตะ watchlist_events handling, ไม่แตะ derive events logic — Acceptance: GET `/api/stock/BBL/history` → timeline + events มี field `iso_week` (เช่น `'2026-W18'`), ไม่มี field `scan_num` แล้ว

### Reference
```python
# current (server/app.py:2404-2432) /api/screener/trend
@app.get("/api/screener/trend")
async def screener_trend(weeks: int = 12):
    # ...
    scans = (hist.get("scans") or [])[-weeks:]
    weeks_out = []
    for s in scans:
        counts = s.get("counts") or {}
        top = s.get("top_candidates") or []
        yields = [c.get("yield") for c in top if c.get("yield") is not None]
        scan_date = (s.get("date") or "")[:10]
        num = s.get("num")
        weeks_out.append({
            "week_label": f"W{num}" if num else scan_date,
            "scan_date": scan_date,
            "passed": counts.get("passed", 0),
            "review": counts.get("review", 0),
            "avg_yield": ...,
            "top_score": ...,
        })
    return {"weeks": weeks_out}

# new
@app.get("/api/screener/trend")
async def screener_trend(weeks: int = 12):
    # ...
    scans = (hist.get("scans") or [])[-weeks:]
    weeks_out = []
    for s in scans:
        counts = s.get("counts") or {}
        top = s.get("top_candidates") or []
        yields = [c.get("yield") for c in top if c.get("yield") is not None]
        scan_date = (s.get("date") or "")[:10]
        iso_week = s.get("iso_week") or ""
        week_label = ("W" + iso_week.split("-W")[-1]) if iso_week else scan_date
        weeks_out.append({
            "week_label": week_label,
            "iso_week": iso_week,
            "scanned_at": s.get("scanned_at"),
            "scan_date": scan_date,
            "passed": counts.get("passed", 0),
            "review": counts.get("review", 0),
            "avg_yield": counts.get("avg_yield") if counts.get("avg_yield") is not None
                else (round(sum(yields) / len(yields), 2) if yields else 0),
            "top_score": counts.get("top_score") if counts.get("top_score") is not None
                else max((c.get("score", 0) for c in top), default=0),
        })
    return {"weeks": weeks_out}
```

```python
# current (server/app.py:614-623) — only the mapping snippet
scan_nums: dict[str, int] = {}
if history_file.exists():
    try:
        hist = read_json(history_file)
        for s in hist.get("scans", []):
            rep = s.get("report", "") or ""
            date_key = rep.replace("scan_", "").replace(".md", "") if rep else None
            if date_key:
                scan_nums[date_key] = s.get("num")
    except Exception as e:
        ...

# new
iso_weeks: dict[str, str] = {}
if history_file.exists():
    try:
        hist = read_json(history_file)
        for s in hist.get("scans", []):
            rep = s.get("report", "") or ""
            date_key = rep.replace("scan_", "").replace(".md", "") if rep else None
            if date_key:
                iso_weeks[date_key] = s.get("iso_week")
    except Exception as e:
        ...
# (then in loop — replace `scan_num = scan_nums.get(date)` with `iso_week = iso_weeks.get(date)`,
#  and every `"scan_num": scan_num` with `"iso_week": iso_week` in the 7 dict literals
#  at lines 638, 652, 688, 697, 705, 715, 729)
```

## Phase 3: Frontend UI — render scanned_at timestamp
- [x] แก้ `projects/MaxMahon/web/v6/static/js/pages/home.js` `_buildTrendStrip()` (บรรทัด 185-216): หลัง `<div class='micro'>Pass Count · Trailing 12 Weeks</div>` (บรรทัด 207) เพิ่ม element แสดง `อัพเดตล่าสุด {dd/mm HH:mm}` ของ week ล่าสุด (`trend.weeks[trend.weeks.length-1].scanned_at`) format inline ด้วย `new Date(iso).toLocaleString('th-TH', {day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'})`. ถ้าไม่มี scanned_at = ไม่แสดง — scope: ไม่แตะ chart logic, ไม่แตะ leaders strip, ไม่แตะ summary/lede — Acceptance: เปิด `/` desktop → ใต้ 'Pass Count · Trailing 12 Weeks' มีข้อความ 'อัพเดตล่าสุด: 28/04 10:20' (เมื่อ scan ล่าสุด 28 เม.ย. 10:20)
- [x] แก้ `projects/MaxMahon/web/v6/static/js/pages/home.mobile.js` `trendBox` (บรรทัด 145-149): หลัง `<div class='micro'>Pass Count · Trailing 12 Weeks</div>` (บรรทัด 147) เพิ่ม element แสดง `อัพเดตล่าสุด {dd/mm HH:mm}` แบบเดียวกับ desktop. ใช้ `var lastScanned = (weeks[weeks.length-1] || {}).scanned_at;` — scope: ไม่แตะ chart logic, ไม่แตะ summary/lede — Acceptance: เปิด `/m` mobile → ใต้ 'Pass Count · Trailing 12 Weeks' มีข้อความ 'อัพเดตล่าสุด: 28/04 10:20'

### Reference
```javascript
// current (home.js:204-215) _buildTrendStrip
return (
  '<section class="mini-chart-strip" style="display:grid;grid-template-columns:2fr 1fr;gap:var(--sp-6);padding:var(--sp-5) 0;border-bottom:1px solid var(--rule);align-items:center">' +
    '<div>' +
      '<div class="micro" style="margin-bottom:var(--sp-2)">Pass Count · Trailing 12 Weeks</div>' +
      '<div class="mini-chart-box" style="height:140px"><canvas id="v6-home-trend"></canvas></div>' +
    '</div>' +
    // ... leaders strip
);

// new — เพิ่ม scanLine ใต้ micro label
var weeks = (trend && trend.weeks) || [];
var lastScanned = weeks.length ? weeks[weeks.length - 1].scanned_at : null;
var scanLine = '';
if (lastScanned) {
  var d = new Date(lastScanned);
  var fmt = d.toLocaleString('th-TH', {day:'2-digit', month:'2-digit', hour:'2-digit', minute:'2-digit'});
  scanLine = '<div class="micro" style="color:var(--fg-dim);margin-bottom:var(--sp-2)">อัพเดตล่าสุด: ' + fmt + '</div>';
}
return (
  '<section class="mini-chart-strip" ...>' +
    '<div>' +
      '<div class="micro" style="margin-bottom:var(--sp-2)">Pass Count · Trailing 12 Weeks</div>' +
      scanLine +
      '<div class="mini-chart-box" style="height:140px"><canvas id="v6-home-trend"></canvas></div>' +
    '</div>' +
    // ... leaders strip
);
```

```javascript
// current (home.mobile.js:145-149) trendBox
var trendBox =
  '<div style="padding:12px 0;border-bottom:1px solid var(--border-subtle)">' +
    '<div class="micro" style="margin-bottom:6px">Pass Count · Trailing 12 Weeks</div>' +
    '<div style="height:120px"><canvas id="v6-mhome-trend"></canvas></div>' +
  '</div>';

// new
var tWeeks = (trend && trend.weeks) || [];
var tLast = tWeeks.length ? tWeeks[tWeeks.length - 1].scanned_at : null;
var tLine = '';
if (tLast) {
  var td = new Date(tLast);
  var tf = td.toLocaleString('th-TH', {day:'2-digit', month:'2-digit', hour:'2-digit', minute:'2-digit'});
  tLine = '<div class="micro" style="color:var(--fg-dim);margin-bottom:4px">อัพเดตล่าสุด: ' + tf + '</div>';
}
var trendBox =
  '<div style="padding:12px 0;border-bottom:1px solid var(--border-subtle)">' +
    '<div class="micro" style="margin-bottom:6px">Pass Count · Trailing 12 Weeks</div>' +
    tLine +
    '<div style="height:120px"><canvas id="v6-mhome-trend"></canvas></div>' +
  '</div>';
```

## Phase 4: Cleanup + Verify
- [x] สร้าง `projects/MaxMahon/scripts/clean_reset.py` — ลบ algo output + raw cache ทั้งหมด. รับ flag `--confirm` (ถ้าไม่มี = dry run print เฉยๆ). targets ที่ต้องลบ (list เป๊ะ): files = `data/history.json`, `data/history.json.v1.bak`, `data/screener_*.json` (glob), `data/snapshot_*.json` (glob), `data/analysis_cache.json`, `data/niwes_diff_history.json`, `data/niwes_diff_latest.json`, `data/niwes_news_*.json` (glob), `data/niwes_alert_sent.json`, `data/niwes_news_seen.json`, `data/request_*.json` (glob), `data/monitor_log_*.log` (glob), `reports/scan_*.md` (glob); folders = `data/screener_cache/`, `data/analysis_cache/`, `data/portfolio_opus_cache/`, `data/setsmart_cache/`, `data/price_cache/`, `data/price_history/`. ใช้ `Path.unlink(missing_ok=True)` + `shutil.rmtree(folder, ignore_errors=True)`. Print แต่ละไฟล์/folder ที่ลบ + summary count `Deleted X files, Y folders`. — scope: ห้ามลบ `case_study_patterns.json`, `exit_baselines.json`, `hidden_value_holdings.json`, `set_universe.json`, `user_data.json`, `config.json` (ใส่ assertion guard ตรวจไฟล์เหล่านี้ยังอยู่ตอนจบ) — Acceptance: รัน `py projects/MaxMahon/scripts/clean_reset.py` (no flag) → print 'DRY RUN: would delete N items' + list. รัน `py projects/MaxMahon/scripts/clean_reset.py --confirm` → ลบจริง + print summary. หลังลบ: `data/case_study_patterns.json` + `data/exit_baselines.json` + `data/hidden_value_holdings.json` + `data/set_universe.json` ยังอยู่ครบ
- [x] รัน cleanup จริง: `py projects/MaxMahon/scripts/clean_reset.py --confirm` — Acceptance: ออก 0, ตรวจ `ls projects/MaxMahon/data/` เหลือแค่ {case_study_patterns, exit_baselines, hidden_value_holdings, set_universe}.json + (อาจมี config.json/user_data.json ถ้าอยู่ใน data/ — ปกติอยู่ root project), niwes_diff_*.json/niwes_news_seen.json ลบหมด, ไม่มี history.json, ไม่มี screener_*.json, ไม่มี setsmart_cache/, ไม่มี price_cache/, ไม่มี price_history/, ไม่มี snapshot_*.json. `ls projects/MaxMahon/reports/` ไม่มี scan_*.md เหลือ (อาจมี non-scan reports ของ niwes ก็ปล่อยไว้)
- [x] Verify end-to-end ด้วย scan สด — **Pre-condition (สำคัญ — ก่อนเริ่ม Step ใดๆ):** ตรวจ MaxMahon server รันอยู่ที่ port 50089 ด้วย `curl -s http://localhost:50089/api/status` (ถ้าไม่ตอบ → start ด้วย `cd projects/MaxMahon && max-server.bat` ที่ terminal แยก หรือใช้ public URL `https://max.intensivetrader.com` ผ่าน Cloudflare Tunnel). — Step 1: รัน `py projects/MaxMahon/scripts/screen_stocks.py` (จะ trigger SETSMART bulk fetch ใหม่หลัง cache โดน clean) → Step 2: รัน `py projects/MaxMahon/scripts/scan.py` → ตรวจ `data/history.json` มี 1 entry มี `iso_week='2026-W18'` (หรือสัปดาห์ปัจจุบัน) + `scanned_at` ISO + `date` + ไม่มี `num` → Step 3: รัน `py projects/MaxMahon/scripts/scan.py` ซ้ำใน 1-2 นาที → `data/history.json` ยังมี 1 entry, `scanned_at` อัพเดตเป็นเวลาล่าสุด → Step 4: เปิด UI `http://localhost:50089/` (desktop) + `http://localhost:50089/m` (mobile) ใน browser ดู: trend chart label = `W{ISO}` (เช่น `W18`) + ใต้ 'Pass Count · Trailing 12 Weeks' มี 'อัพเดตล่าสุด: ...' — scope: verify อย่างเดียว ไม่แก้ code — Acceptance: history.json schema ตรงตามที่ออกแบบ + scan ซ้ำ = upsert + UI render ถูกต้อง 100%

### Reference
```python
# new file: projects/MaxMahon/scripts/clean_reset.py
"""Clean reset: ลบ algo output + raw cache ทั้งหมด ก่อน scan รอบใหม่.
Usage:
  py projects/MaxMahon/scripts/clean_reset.py           # dry run
  py projects/MaxMahon/scripts/clean_reset.py --confirm # ลบจริง
"""
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REPORTS = ROOT / "reports"

KEEP_FILES = {"case_study_patterns.json", "exit_baselines.json", 
              "hidden_value_holdings.json", "set_universe.json"}

FILE_TARGETS = [
    DATA / "history.json",
    DATA / "history.json.v1.bak",
    DATA / "analysis_cache.json",
    DATA / "niwes_diff_history.json",
    DATA / "niwes_diff_latest.json",
    DATA / "niwes_alert_sent.json",
    DATA / "niwes_news_seen.json",
]
GLOB_TARGETS = [
    (DATA, "screener_*.json"),
    (DATA, "snapshot_*.json"),
    (DATA, "niwes_news_*.json"),
    (DATA, "request_*.json"),
    (DATA, "monitor_log_*.log"),
    (REPORTS, "scan_*.md"),
]
FOLDER_TARGETS = [
    DATA / "screener_cache",
    DATA / "analysis_cache",
    DATA / "portfolio_opus_cache",
    DATA / "setsmart_cache",
    DATA / "price_cache",
    DATA / "price_history",
]

def collect():
    files = [f for f in FILE_TARGETS if f.exists()]
    for base, pat in GLOB_TARGETS:
        files.extend(sorted(base.glob(pat)))
    folders = [f for f in FOLDER_TARGETS if f.exists()]
    return files, folders

def main():
    confirm = "--confirm" in sys.argv
    files, folders = collect()
    print(f"Targets: {len(files)} files, {len(folders)} folders")
    for f in files:
        print(f"  FILE   {f.relative_to(ROOT)}")
    for d in folders:
        print(f"  FOLDER {d.relative_to(ROOT)}")
    if not confirm:
        print("\nDRY RUN — no changes. Use --confirm to delete.")
        return
    for f in files:
        f.unlink(missing_ok=True)
    for d in folders:
        shutil.rmtree(d, ignore_errors=True)
    for keep in KEEP_FILES:
        assert (DATA / keep).exists(), f"PROTECTED file missing: {keep}"
    print(f"\nDeleted {len(files)} files, {len(folders)} folders.")
    print("Reference files preserved:", ", ".join(sorted(KEEP_FILES)))

if __name__ == "__main__":
    main()
```
