---
project: 4-MaxMahon
created: 2026-05-12
last_updated: 2026-05-18
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: หุ้นที่ yahoo ดึงข้อมูลไม่ได้หลัง Stage 2 retry → ไม่ FAIL ทิ้ง แต่เก็บเข้า data/flake_queue.json + retry รายวันใน daily_price_refresh + ได้แล้วเอากลับเข้า candidates + ค้าง > 7 วัน แจ้ง telegram ให้คนดูเอง — ไม่มีหุ้นดีๆ ตกฟรีอีก

### รายละเอียด
- ปัจจุบัน scan pipeline 3 stages (after Plan B yahoo-fetch-resilience):
- - Stage 1: parallel fetch 5 workers
- - Stage 2: รอ 30s → retry sequential 1.5s/symbol
- - Phase B post-process: hard_filter ตัด → data integrity guard → FAIL 'ไม่มีข้อมูลปันผลย้อนหลัง' (screen_stocks.py:84-88)
- Bug: หุ้น quality ดีที่ yahoo block ชั่วคราว → ตกฟรี ต้องรอ scan สัปดาห์หน้า
- Approach: เปลี่ยน hard_filter response — ถ้า data integrity guard fail → ไม่ return FAIL แต่ return PENDING + push to flake_queue
- Flake queue schema (data/flake_queue.json): {version: 1, queue: [{symbol, first_flaked_at: ISO, last_retry_at: ISO, retry_count: int, reasons: [str], scan_date: YYYY-MM-DD}]}
- Daily retry logic: daily_price_refresh → อ่าน flake_queue → retry yahoo สำหรับทุก symbol → ได้ครบ = ลบจาก queue + push to candidates / ยังไม่ได้ = update retry_count + last_retry_at
- Age check: ถ้า age (now - first_flaked_at) > 7 วัน → ส่ง telegram alert ผ่าน scripts/telegram_alert.py + mark as 'STALE' ใน queue (ไม่ retry อีก แต่เก็บไว้ดู)
- ใหม่ status ใน hard_filter: PASS / REVIEW / FAIL / PENDING (PENDING = อยู่ใน flake_queue)
- screener output schema: เพิ่ม key 'pending_candidates' [] — list หุ้นที่อยู่ใน queue (สำหรับ frontend แสดง)

### Scope Boundary
**In scope:**
- data/flake_queue.json (ใหม่) — queue state file
- scripts/flake_queue.py (ใหม่) — helper functions (add, remove, list_all, age_check, retry_one)
- scripts/screen_stocks.py — เปลี่ยน data integrity guard เป็น PENDING (ไม่ FAIL)
- scripts/daily_price_refresh.py — เรียก flake retry หลัง EOD refresh
- scripts/telegram_alert.py — extend สำหรับ stale flake alert (reuse existing function)
- server/app.py /api/screener — return pending_candidates
- web/v6/static/js/pages/home.js + home.mobile.js — แสดง section 'รอข้อมูล' (pending)

**Out of scope:**
- Yahoo retry mechanism ใน data_adapter.py (เก็บ Stage 1/2 ตามเดิม)
- Cache integrity guard logic (เก็บไว้ — แค่ไม่ FAIL)
- Plan F daily refilter (parallel-safe with this plan)

### Non-goals
- ไม่ใช้ database สำหรับ queue — file-based JSON ง่ายและพอ
- ไม่ implement exponential backoff — daily retry คงที่
- ไม่ retry มากกว่า 1 ครั้งต่อวัน (กัน yahoo rate limit)
- ไม่ remove stale entries อัตโนมัติ — เก็บไว้ให้คนตัดสินใจ

# Plan G — Yahoo Flake Retry Queue (No More False FAIL)

> Part 7 of 7 — Flake retry queue. yahoo flake = ไม่ FAIL ปัดทิ้ง แต่ queue + retry รายวัน. หุ้นดีๆ ที่ yahoo block ชั่วคราวไม่ตกฟรี.
> Depends on: filter-01 (filter logic stable) + filter-03 (DPS yahoo source confirmed)
> Parallel-safe with: filter-04-review-pass-tag, filter-05-normalized-eps, filter-06-daily-refilter

## Phase 1: Flake queue file structure + helper functions
- [x] สร้าง scripts/flake_queue.py — helper module: (1) load_queue() → dict (2) save_queue(data) (3) add_to_queue(symbol, reasons, scan_date) → add entry หรือ update retry_count (4) remove_from_queue(symbol) → ลบเมื่อ retry success (5) list_pending() → list ของ symbols ปัจจุบัน (6) list_stale(days=7) → list ของ age > N days — Scope: ไม่ผูกกับ yahoo logic — pure file I/O helper — Acceptance: py -c 'from scripts.flake_queue import add_to_queue, list_pending; add_to_queue("BBL", ["yahoo flake"], "2026-05-12"); print(list_pending())' รัน สำเร็จ + flake_queue.json มี entry BBL
- [x] Initialize ไฟล์ data/flake_queue.json — content: {"version": 1, "queue": []} — Acceptance: ไฟล์มี + JSON parse ได้

### Reference
```python
# new file: scripts/flake_queue.py
"""Yahoo flake retry queue — file-based JSON queue.

Schema:
  {
    "version": 1,
    "queue": [
      {
        "symbol": "BBL",
        "first_flaked_at": "2026-05-12T10:00:00",
        "last_retry_at": "2026-05-12T19:00:00",
        "retry_count": 1,
        "reasons": ["ไม่มีข้อมูลปันผลย้อนหลัง (yahoo flake)"],
        "scan_date": "2026-05-12",
        "stale": false
      }
    ]
  }
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE_FILE = ROOT / "data" / "flake_queue.json"


def _ensure_queue():
    if not QUEUE_FILE.exists():
        QUEUE_FILE.write_text(json.dumps({"version": 1, "queue": []}), encoding="utf-8")


def load_queue() -> dict:
    _ensure_queue()
    return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))


def save_queue(data: dict):
    QUEUE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def add_to_queue(symbol: str, reasons: list[str], scan_date: str):
    data = load_queue()
    now = datetime.now().isoformat()
    for e in data["queue"]:
        if e["symbol"] == symbol:
            e["retry_count"] = e.get("retry_count", 0)  # don't bump here
            e["reasons"] = reasons
            e["scan_date"] = scan_date
            save_queue(data)
            return
    data["queue"].append({
        "symbol": symbol,
        "first_flaked_at": now,
        "last_retry_at": None,
        "retry_count": 0,
        "reasons": reasons,
        "scan_date": scan_date,
        "stale": False,
    })
    save_queue(data)


def remove_from_queue(symbol: str):
    data = load_queue()
    data["queue"] = [e for e in data["queue"] if e["symbol"] != symbol]
    save_queue(data)


def mark_retry(symbol: str, success: bool):
    data = load_queue()
    now = datetime.now().isoformat()
    for e in data["queue"]:
        if e["symbol"] == symbol:
            e["last_retry_at"] = now
            e["retry_count"] = e.get("retry_count", 0) + 1
            break
    save_queue(data)
    if success:
        remove_from_queue(symbol)


def list_pending() -> list[str]:
    return [e["symbol"] for e in load_queue()["queue"] if not e.get("stale")]


def list_stale(days: int = 7) -> list[dict]:
    threshold = datetime.now() - timedelta(days=days)
    result = []
    for e in load_queue()["queue"]:
        first = e.get("first_flaked_at")
        if first and datetime.fromisoformat(first) < threshold and not e.get("stale"):
            result.append(e)
    return result


def mark_stale(symbol: str):
    data = load_queue()
    for e in data["queue"]:
        if e["symbol"] == symbol:
            e["stale"] = True
            break
    save_queue(data)
```

## Phase 2: hard_filter เปลี่ยน flake guard เป็น PENDING + push to queue
- [x] แก้ scripts/screen_stocks.py hard_filter data integrity guard (บรรทัด 84-88) — เปลี่ยน return 'FAIL' เป็น return 'PENDING' + เก็บ reasons ใน 4th return value — Scope: ไม่กระทบ logic อื่น — Acceptance: hard_filter(data_with_yahoo_flake) คืน ('PENDING', ['ไม่มีข้อมูลปันผลย้อนหลัง (yahoo flake)'])
- [x] แก้ scripts/screen_stocks.py main() — รับ PENDING status: ไม่เข้า candidates + ไม่เข้า filtered_out + เรียก flake_queue.add_to_queue(sym, reasons, today) + เก็บใน pending_candidates list — Acceptance: รัน scan แล้ว screener output มี key 'pending_candidates' [] + flake_queue.json อัพเดท
- [x] Update output schema: เพิ่ม 'pending_candidates' [] + 'counts.pending' — Acceptance: screener_*.json มี keys: candidates, review_candidates (empty backward compat), pending_candidates, filtered_out_stocks, counts.{passed, review, pending, filtered_out}

### Reference
```python
# current (scripts/screen_stocks.py:82-88)
# Data integrity guard — yahoo flake
streak = agg.get("dividend_streak", 0)
dy_check = data.get("dividend_yield")
div_history = data.get("dividend_history") or {}
if dy_check is not None and dy_check > 0 and streak == 0 and not div_history:
    fail_reasons.append("ไม่มีข้อมูลปันผลย้อนหลัง (yahoo flake — รอ rerun พรุ่งนี้)")
    return "FAIL", fail_reasons

# new — return PENDING instead
streak = agg.get("dividend_streak", 0)
dy_check = data.get("dividend_yield")
div_history = data.get("dividend_history") or {}
if dy_check is not None and dy_check > 0 and streak == 0 and not div_history:
    pending_reasons = ["ไม่มีข้อมูลปันผลย้อนหลัง (yahoo flake — queued for retry)"]
    return "PENDING", pending_reasons

# main() flow — handle PENDING
from flake_queue import add_to_queue

status, filter_reasons = hard_filter(data)
if status == "FAIL":
    filtered_out += 1
    continue
if status == "PENDING":
    add_to_queue(sym, filter_reasons, datetime.now().strftime("%Y-%m-%d"))
    pending_candidates.append({
        "symbol": sym,
        "sector": data.get("sector"),
        "reasons": filter_reasons,
    })
    continue
# status == "PASS" or "REVIEW" → existing logic
```

## Phase 3: Daily retry — fetch yahoo สำหรับ flake queue
- [x] แก้ scripts/daily_price_refresh.py — เพิ่ม function _retry_flake_queue() ที่ (1) อ่าน list_pending() (2) สำหรับแต่ละ symbol → เรียก fetch_multi_year(sym) (3) ถ้าได้ DPS history → mark_retry(sym, success=True) + push to candidates (4) ถ้าไม่ได้ → mark_retry(sym, success=False) — เรียกหลัง EOD refresh + ก่อน refilter (Plan F) — Scope: ไม่กระทบ EOD refresh — Acceptance: queue ที่มี 3 symbols → retry 3 ตัว, ตัวที่ได้ DPS = ลบจาก queue, ตัวที่ไม่ได้ = update retry_count
- [x] เพิ่ม recovered_to_candidates handling: ถ้า retry success → re-run hard_filter + quality_score → push to current screener candidates — Acceptance: หุ้นที่ recover แล้ว → ปรากฏใน candidates ของ screener วันนั้น

### Reference
```python
# scripts/daily_price_refresh.py — add retry flake queue
from flake_queue import list_pending, mark_retry, mark_stale, list_stale
from fetch_data import fetch_multi_year
from screen_stocks import hard_filter, quality_score

def _retry_flake_queue():
    pending = list_pending()
    if not pending:
        logger.info("flake queue empty")
        return
    
    logger.info("retrying %d flake symbols", len(pending))
    recovered = []
    for sym in pending:
        try:
            data = fetch_multi_year(sym)
            if data and data.get("dividend_history"):
                mark_retry(sym, success=True)
                recovered.append(data)
                logger.info("recovered: %s", sym)
            else:
                mark_retry(sym, success=False)
        except Exception as e:
            logger.warning("retry failed for %s: %s", sym, e)
            mark_retry(sym, success=False)
    
    # Push recovered to current screener
    if recovered:
        # ... merge into latest screener_*.json ...
        pass
    
    # Check stale
    stale = list_stale(days=7)
    for entry in stale:
        from telegram_alert import send_alert
        send_alert(f"flake STALE: {entry['symbol']} ค้าง {entry['retry_count']} retries")
        mark_stale(entry["symbol"])


def refresh_prices():
    # ... existing EOD refresh + write price_cache ...
    
    # NEW: retry flake queue
    _retry_flake_queue()
    
    # NEW (from Plan F): refilter with latest prices
    from daily_refilter import refilter_from_latest_prices
    refilter_from_latest_prices()
```

## Phase 4: Stale alert + frontend display
- [x] Verify scripts/telegram_alert.py — function send_alert(message) อยู่แล้ว — ไม่ต้องแก้ — Acceptance: cat scripts/telegram_alert.py | grep 'def send' → confirm function exists
- [x] แก้ server/app.py /api/screener — เพิ่ม 'pending_candidates' ใน response + 'flake_stale' count (จาก list_stale()) — Acceptance: GET /api/screener คืน pending_candidates[] + summary มี pending_count + flake_stale_count
- [x] แก้ web/v6/static/js/pages/home.js — เพิ่ม section 'รอข้อมูล (ถ้ามี)' แสดง pending_candidates พร้อม age (วันที่ถูก flake) — Acceptance: ถ้ามี pending → แสดง section + รายชื่อ + age, ถ้าไม่มี → ซ่อน
- [x] แก้ web/v6/static/js/pages/home.mobile.js — same — Acceptance: มือถือเห็น section เหมือน desktop

### Reference
```python
# server/app.py /api/screener — add pending
from scripts.flake_queue import load_queue, list_stale

@app.get("/api/screener")
async def get_screener(user: dict = Depends(get_current_user)):
    data = read_json(path)
    # ... existing enrichment ...
    
    queue_data = load_queue()
    data["pending_candidates"] = queue_data["queue"]
    data["summary"]["pending_count"] = len([e for e in queue_data["queue"] if not e.get("stale")])
    data["summary"]["flake_stale_count"] = len(list_stale(days=7))
    
    return data
```

```javascript
// home.js — render pending section
function _renderPending(pending) {
    if (!pending || pending.length === 0) return '';
    return '<section class="pending-candidates">' +
        '<h3>รอข้อมูล (' + pending.length + ')</h3>' +
        '<ul>' + pending.map(p => 
            '<li>' + p.symbol + ' — ' + p.reasons.join('; ') + ' (' + p.retry_count + ' retries)</li>'
        ).join('') + '</ul>' +
    '</section>';
}
```

## Phase 5: Smoke test + simulate flake
- [x] Simulate flake: เพิ่มเข้า queue manual: py -c 'from scripts.flake_queue import add_to_queue; add_to_queue("BBL", ["test flake"], "2026-05-12")' — Acceptance: data/flake_queue.json มี entry BBL
- [x] Trigger retry: py scripts/daily_price_refresh.py — Acceptance: log แสดง 'retrying 1 flake symbols' + 'recovered: BBL' (เพราะ BBL ดึง yahoo ได้จริง) + flake_queue.json queue ว่าง
- [x] Simulate stale: เพิ่มเข้า queue ด้วย first_flaked_at = 10 วันก่อน → trigger retry → Acceptance: telegram alert ถูกส่ง + entry stale=True ใน queue
- [x] Edge case: queue ว่าง → refresh_prices ทำงานปกติ ไม่ error

### Reference
Verify commands:
```bash
# Test 1: add to queue
py -c "from scripts.flake_queue import add_to_queue; add_to_queue('BBL', ['test'], '2026-05-12')"
cat data/flake_queue.json

# Test 2: trigger retry
py scripts/daily_price_refresh.py
cat data/flake_queue.json  # Should show BBL removed

# Test 3: simulate stale (manual)
py -c "
import json
from pathlib import Path
from datetime import datetime, timedelta
p = Path('data/flake_queue.json')
d = json.loads(p.read_text())
d['queue'].append({
    'symbol': 'TESTSTALE',
    'first_flaked_at': (datetime.now() - timedelta(days=10)).isoformat(),
    'last_retry_at': None,
    'retry_count': 7,
    'reasons': ['stale test'],
    'scan_date': '2026-05-02',
    'stale': False,
})
p.write_text(json.dumps(d, indent=2))
"
py scripts/daily_price_refresh.py  # Should send telegram alert
```
