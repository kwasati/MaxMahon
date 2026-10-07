---
project: 4-MaxMahon
created: 2026-05-12
last_updated: 2026-05-12
status: active
---

## Target / Goal

### เป้าหมาย
ทำได้: ทุกวัน 19:00 หลัง daily price refresh เสร็จ → ระบบ re-compute ratios (P/E, P/BV, yield%, market_cap) จากราคาใหม่ + cached fundamentals → re-run hard filter → update screener_*.json + track status change (หุ้นใหม่เข้า / หุ้นเดิมออก) — user เปิด app วันนั้นเห็น candidates list ที่อัพเดทตามราคาวันนี้

### รายละเอียด
- ปัจจุบัน weekly scan รัน Sunday 09:00 → ดึง fundamentals + filter + score → screener_*.json. ระหว่างสัปดาห์ราคาเปลี่ยนทุกวัน → P/E + P/BV + yield + mcap เปลี่ยน → status PASS/FAIL อาจเปลี่ยน แต่ระบบไม่ re-classify
- Daily price refresh (19:00) ดึง SETSMART EOD bulk + yahoo fallback → write data/price_cache/{sym}.json — แต่ไม่ re-run filter
- Gap: หุ้นที่ราคาตกหนัก (P/E จาก 16 → 13) ต้องรอ Sunday scan ใหม่ถึงจะเข้า candidates — เสีย opportunity 6 วัน
- Approach: เพิ่ม script daily_refilter.py — โหลด last screener + ราคาใหม่ + recompute ratios + re-run hard_filter ด้วย cached fundamentals → write screener_{today}.json (ใหม่)
- Architecture: แยก script (single responsibility) ไม่รวมใน daily_price_refresh.py — เรียก sequential หลัง price refresh เสร็จ
- Cached fundamentals (งบ + DPS events + ratios fundamental) อยู่ใน screener_cache + setsmart_cache แล้ว — ไม่ต้อง re-fetch
- Status change tracking: เพิ่ม field 'status_change_log' ใน screener output — list of {date, symbol, from, to} — frontend แสดง 'หุ้นเข้าใหม่วันนี้' / 'หุ้นออกวันนี้'
- Edge case: ถ้า cached fundamentals หาย/เก่า > 7 วัน → skip refilter (ใช้ weekly scan แทน) + log warning
- Refilter ต้องการ 4 field ใน candidate entry: eps_ttm, bvps, dps_latest, shares_outstanding — ปัจจุบัน screen_stocks.py main() candidates.append ที่ ~บรรทัด 989 ยังไม่มี 4 field นี้ → Phase 2 ต้องเพิ่มเข้าไป (ไม่ใช่ audit)
- Plan F ต้องรอ Plan D (REVIEW unified into candidates) — ใช้ candidates list ที่ unified

### Scope Boundary
**In scope:**
- scripts/daily_refilter.py (ใหม่) — main refilter logic
- scripts/daily_price_refresh.py — เรียก daily_refilter หลัง EOD refresh
- scripts/screen_stocks.py — เพิ่ม 4 field (eps_ttm, bvps, dps_latest, shares_outstanding) เข้า candidate entry
- server/app.py /api/screener — return status_change_log
- web/v6/static/js/pages/home.js + home.mobile.js — แสดง 'หุ้นเข้าใหม่' / 'หุ้นออก' badge

**Out of scope:**
- Re-score quality_score (เก็บคะแนนเก่า — เปลี่ยนแค่ filter status)
- Re-fetch fundamentals (เก็บ cache เก่า)
- Weekly scan logic (ไม่เปลี่ยน)
- Plan G flake queue (แยก plan)

### Non-goals
- ไม่ re-run quality_score รายวัน (heavy computation — keep weekly)
- ไม่ trigger Claude AI deep analyze รายวัน
- ไม่ re-fetch yahoo dividend events รายวัน (เก็บ weekly cycle)
- ไม่ alert telegram ทุก status change (อาจ noisy — แยก plan ถ้าจำเป็น)

# Plan F — Daily Re-filter (Price Update → Re-classify PASS/REVIEW/FAIL)

> Part 6 of 7 — Daily re-filter. ราคาเปลี่ยนทุกวัน = ratio เปลี่ยน = status filter เปลี่ยนได้. re-classify รายวันด้วย cache เดิม + ราคาใหม่ ไม่ต้องรอ scan รายสัปดาห์.
> Depends on: filter-01 (filter logic stable) + filter-02 (SETSMART warm) + filter-04 (REVIEW unified candidates)
> Parallel-safe with: filter-07-flake-retry-queue

## Phase 1: สร้าง daily_refilter.py — core logic
- [ ] สร้าง scripts/daily_refilter.py — function refilter_from_latest_prices() → (1) โหลด last screener_*.json (newest in data/) (2) โหลด data/price_cache/{sym}.json สำหรับทุก symbol ใน candidates (3) re-compute ratios: pe = price / eps_ttm, pb = price / bvps, yield% = dps_latest / price * 100, mcap = price * shares_outstanding (4) แทน snapshot fields ใน data dict (5) เรียก hard_filter(data) ใหม่ (6) บันทึก status change ใน status_change_log[] — Scope: ไม่ re-fetch fundamentals, ไม่ re-score, ไม่ re-tag — Acceptance: py scripts/daily_refilter.py รัน standalone สำเร็จ + output screener_{today}.json มี candidates ที่ filter_status update ตามราคาวันนี้ + status_change_log[] มี entries สำหรับหุ้นที่เปลี่ยน status
- [ ] Edge case handling ใน daily_refilter.py: ถ้า cached fundamentals (eps_ttm, bvps, dps_latest, shares) ขาด → skip stock + log warning 'fundamentals stale for {sym}' — Acceptance: ทดสอบกับ 5 หุ้นที่ cache สมบูรณ์ + 1 หุ้นที่ cache ขาดบาง field → 5 หุ้น re-filter, 1 หุ้น skip warning

### Reference
```python
# new file: scripts/daily_refilter.py
"""Daily re-filter — re-classify PASS/REVIEW/FAIL using latest prices + cached fundamentals.

Flow:
  1. Load latest screener_*.json
  2. Load data/price_cache/{sym}.json for each candidate
  3. Re-compute ratios (P/E, P/BV, yield, mcap) from new price + cached fundamentals
  4. Re-run hard_filter() with updated data dict
  5. Track status changes -> status_change_log[]
  6. Write new screener_{today}.json
"""
import json
import logging
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PRICE_CACHE = DATA_DIR / "price_cache"

sys.path.insert(0, str(ROOT / "scripts"))
from screen_stocks import hard_filter

logger = logging.getLogger(__name__)


def _latest_screener():
    files = sorted(DATA_DIR.glob("screener_*.json"))
    if not files:
        return None
    return files[-1]


def refilter_from_latest_prices():
    src = _latest_screener()
    if src is None:
        logger.warning("no screener_*.json found — skip refilter")
        return
    
    screener = json.loads(src.read_text(encoding="utf-8"))
    candidates = screener.get("candidates", [])
    status_change_log = []
    refilter_skip = []
    
    for c in candidates:
        sym = c.get("symbol")
        price_file = PRICE_CACHE / f"{sym}.json"
        if not price_file.exists():
            refilter_skip.append({"symbol": sym, "reason": "no price cache"})
            continue
        
        price_data = json.loads(price_file.read_text(encoding="utf-8"))
        new_price = price_data.get("price")
        if not new_price or new_price <= 0:
            refilter_skip.append({"symbol": sym, "reason": "invalid price"})
            continue
        
        # Rebuild data dict from candidate + cached fundamentals
        eps_ttm = c.get("eps_ttm")
        bvps = c.get("bvps")
        dps_latest = c.get("dps_latest")
        shares = c.get("shares_outstanding")
        
        if None in (eps_ttm, bvps, dps_latest, shares):
            refilter_skip.append({"symbol": sym, "reason": "fundamentals stale"})
            continue
        
        # Recompute ratios with new price
        data = dict(c)  # shallow copy
        data["pe_ratio"] = new_price / eps_ttm if eps_ttm > 0 else None
        data["pb_ratio"] = new_price / bvps if bvps > 0 else None
        data["dividend_yield"] = (dps_latest / new_price * 100) if new_price > 0 else None
        data["market_cap"] = new_price * shares
        
        # Re-run filter
        new_status, reasons = hard_filter(data)
        old_status = c.get("filter_status", "PASS")
        
        if new_status != old_status:
            status_change_log.append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "symbol": sym,
                "from": old_status,
                "to": new_status,
                "reasons": reasons,
            })
        
        c["filter_status"] = new_status
        c["pe_ratio"] = data["pe_ratio"]
        c["pb_ratio"] = data["pb_ratio"]
        c["dividend_yield"] = data["dividend_yield"]
        c["market_cap"] = data["market_cap"]
        c["refilter_at"] = datetime.now().isoformat()
    
    # Filter out new FAIL stocks
    candidates = [c for c in candidates if c.get("filter_status") != "FAIL"]
    
    screener["candidates"] = candidates
    screener["status_change_log"] = status_change_log
    screener["refilter_skip"] = refilter_skip
    screener["refilter_at"] = datetime.now().isoformat()
    
    out = DATA_DIR / f"screener_{datetime.now().strftime('%Y-%m-%d')}.json"
    out.write_text(json.dumps(screener, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("refilter complete: %d candidates, %d status changes, %d skipped",
                len(candidates), len(status_change_log), len(refilter_skip))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    refilter_from_latest_prices()
```

## Phase 2: เพิ่ม 4 field เข้า candidate entry ใน screen_stocks.py
- [ ] แก้ scripts/screen_stocks.py main() — ที่ candidates.append ประมาณบรรทัด 989 — เพิ่ม 4 field เข้า entry dict: eps_ttm (จาก data.get('eps_ttm') หรือ data['yearly_metrics'][-1].get('diluted_eps')), bvps (จาก data.get('bvps') หรือ data['yearly_metrics'][-1].get('book_value_per_share')), dps_latest (จาก data.get('dps_latest') หรือ data['dividend_history'][latest_complete_fy]), shares_outstanding (จาก data.get('shares_outstanding') หรือ data.get('market_cap') / data.get('price')) — Scope: ไม่กระทบ existing fields, แค่เพิ่ม 4 field — Acceptance: หลังรัน scan, screener_*.json candidates[0] มี keys: 'eps_ttm', 'bvps', 'dps_latest', 'shares_outstanding' พร้อม value (ไม่ใช่ None)

### Reference
```python
# current (scripts/screen_stocks.py around line 989 — candidates.append)
entry = {
    'symbol': sym,
    'sector': data.get('sector'),
    'score': result['score'],
    'signals': result['signals'],
    'filter_status': status,
    # ... existing fields ...
}
candidates.append(entry)

# new — add 4 fields needed for daily refilter
yearly = data.get('yearly_metrics') or []
latest_yearly = yearly[-1] if yearly else {}

div_history = data.get('dividend_history') or {}
fy_complete = data.get('fy_is_complete') or {}
complete_fys = sorted([y for y, ok in fy_complete.items() if ok])
latest_complete_fy = complete_fys[-1] if complete_fys else None
dps_latest = div_history.get(latest_complete_fy) if latest_complete_fy else None

shares = data.get('shares_outstanding')
if shares is None and data.get('market_cap') and data.get('price'):
    shares = data['market_cap'] / data['price']

entry = {
    'symbol': sym,
    'sector': data.get('sector'),
    'score': result['score'],
    'signals': result['signals'],
    'filter_status': status,
    # ... existing fields ...
    # NEW for daily refilter:
    'eps_ttm': data.get('eps_ttm') or latest_yearly.get('diluted_eps'),
    'bvps': data.get('bvps') or latest_yearly.get('book_value_per_share'),
    'dps_latest': dps_latest,
    'shares_outstanding': shares,
}
candidates.append(entry)
```

## Phase 3: เรียก daily_refilter หลัง daily_price_refresh
- [ ] แก้ scripts/daily_price_refresh.py refresh_prices() — เรียก refilter_from_latest_prices() ตอนท้าย — Scope: ไม่กระทบ existing EOD refresh — Acceptance: รัน py scripts/daily_price_refresh.py → ทำ EOD refresh จบ → refilter รันต่ออัตโนมัติ → screener_{today}.json อัพเดท
- [ ] Verify server/app.py scheduled_price_refresh_job (บรรทัด 1048-1055) → trigger ใหม่อัตโนมัติ (เพราะแก้ใน daily_price_refresh.py ที่ scheduler import) — Acceptance: trigger manual via /api/admin/price-refresh/trigger → log แสดงทั้ง 'price refresh complete' + 'refilter complete' sequential

### Reference
```python
# current (scripts/daily_price_refresh.py refresh_prices function)
def refresh_prices():
    symbols = _load_symbols()
    # ... EOD refresh ...
    # ... write price_cache/{sym}.json ...

# new — add refilter at end
from daily_refilter import refilter_from_latest_prices

def refresh_prices():
    symbols = _load_symbols()
    # ... existing EOD refresh ...
    # ... write price_cache/{sym}.json ...
    
    # NEW: re-classify candidates with latest prices
    try:
        refilter_from_latest_prices()
    except Exception as e:
        logger.error("daily refilter failed: %s", e)
```

## Phase 4: Frontend — แสดง status change (เข้าใหม่/ออก)
- [ ] แก้ server/app.py /api/screener (บรรทัด 200-273) — เพิ่ม status_change_log + refilter_at ใน response — Acceptance: GET /api/screener คืน fields status_change_log[] + refilter_at
- [ ] แก้ web/v6/static/js/pages/home.js — เพิ่ม section 'หุ้นเข้าใหม่วันนี้' / 'หุ้นออกวันนี้' (จาก status_change_log) ที่ด้านบนของ candidates list — Acceptance: ถ้ามี status_change_log → แสดง section, ถ้าไม่มี → ซ่อน
- [ ] แก้ web/v6/static/js/pages/home.mobile.js — same — Acceptance: มือถือเห็น section เหมือน desktop

### Reference
```javascript
// new — at top of home.js renderCandidates
function _renderStatusChanges(changes) {
    if (!changes || changes.length === 0) return '';
    var entered = changes.filter(c => c.to === 'PASS' || c.to === 'REVIEW');
    var exited = changes.filter(c => c.from === 'PASS' || c.from === 'REVIEW');
    if (entered.length === 0 && exited.length === 0) return '';
    return '<section class="status-changes">' +
        '<h3>หุ้นเข้าใหม่ ' + entered.length + ' / ออก ' + exited.length + '</h3>' +
    '</section>';
}
```

## Phase 5: Smoke test + verify
- [ ] Manual trigger: py scripts/daily_price_refresh.py — Acceptance: log แสดง 'price refresh complete' + 'refilter complete' + data/screener_{today}.json updated + มี status_change_log
- [ ] Edge case test: ลบ price_cache ของ 1 หุ้น (เช่น BBL) แล้ว refilter — Acceptance: refilter_skip[] มี BBL + reason='no price cache', candidates อื่นยัง refilter ปกติ
- [ ] Visual verify: เปิด home page → เห็น 'หุ้นเข้าใหม่วันนี้' / 'หุ้นออกวันนี้' section (ถ้ามี)

### Reference
Verify commands:
```bash
py scripts/daily_price_refresh.py
py -c "
import json
from pathlib import Path
latest = sorted(Path('data').glob('screener_*.json'))[-1]
d = json.loads(latest.read_text(encoding='utf-8'))
print('refilter_at:', d.get('refilter_at'))
print('status_change_log:', len(d.get('status_change_log', [])))
print('candidates:', len(d.get('candidates', [])))
"
```
