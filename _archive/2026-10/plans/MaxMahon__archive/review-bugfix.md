---
project: MaxMahon
created: 2026-04-12
last_updated: 2026-04-12
status: done
---

# Max Mahon — Bugfix รวม 9 จุดจาก Ultra Review

> แก้ 9 bugs จาก codebase review — DCA ตัวเลขผิด, คะแนนบิดเบือน, pipeline ชนกัน, path traversal

## Phase 1: DCA Simulator — แก้ตัวเลขผิด
- [x] แก้ forward projection ปันผล — ดึง base DPS จาก historical dividends (fallback ย้อน 3 ปี) แทน current_price * current_div_yield ที่เป็น 0 เมื่อ yfinance ไม่มีค่า dividendYield + ใช้ base_dps ใน loop projection แทน
- [x] แก้ CAGR ระเบิด + YoC fallback — clamp years_elapsed >= 1.0 กัน CAGR เป็นพันเปอร์เซ็นต์เมื่อ backtest สั้น + Yield on Cost fallback ย้อน 3 ปีถ้าปีสุดท้ายไม่มีข้อมูลปันผล

### Reference
```python
# server/app.py — current (broken)
current_div_yield = info.get("dividendYield") or 0
dps_this_year = current_price * current_div_yield * ((1 + div_growth_rate) ** yr)

# fix — derive base DPS from historical
base_dps = 0
if dividends is not None and not dividends.empty:
    for yr_check in [end_year, end_year - 1, end_year - 2]:
        yr_divs = dividends[dividends.index.year == yr_check].sum()
        if yr_divs > 0:
            base_dps = yr_divs
            break
if base_dps == 0:
    base_dps = current_price * current_div_yield
# projection loop:
dps_this_year = base_dps * ((1 + div_growth_rate) ** yr)

# CAGR fix
years_elapsed = max(years_elapsed, 1.0)

# YoC fallback
for yr_check in [end_year, end_year - 1, end_year - 2]:
    last_year_divs = dividends[dividends.index.year == yr_check].sum() if dividends is not None and not dividends.empty else 0
    if last_year_divs > 0:
        break
```

## Phase 2: Scoring + Data — แก้คะแนนบิดเบือน
- [x] แก้ fetch_data.py �� dividend streak ไม่นับปีปัจจุบัน (exclude current_year จาก sorted keys) + dividend_growth_streak เช่นกัน + EPS CAGR return None ถ้ามี negative value ในปีไหน (ป้องกันการข้ามปีขาดทุน) + interest_coverage cap ที่ 200 (ค่าเกินนี้ไม่มีความหมาย)
- [x] แก้ discover.py — div_hist key sort ใช้ safe int cast (int(x) if str(x).isdigit() else 0) ป้องกัน ValueError crash ทั้ง discovery pipeline

### Reference
```python
# fetch_data.py — dividend streak fix
from datetime import datetime
current_year = datetime.now().year
years = [y for y in sorted(dps_by_year.keys(), reverse=True) if y < current_year]

# EPS CAGR fix — return None if any negative
def compute_cagr(values):
    if any(v is not None and v < 0 for v in values):
        return None
    clean = [(i, v) for i, v in enumerate(values) if v is not None and v > 0]
    ...

# interest_coverage cap
if interest_coverage is not None and interest_coverage > 200:
    interest_coverage = None

# discover.py — safe key sort
key=lambda x: int(x) if str(x).isdigit() else 0
```

## Phase 3: Safety — กันระบบพัง
- [x] เพิ่ม threading.Lock กัน pipeline race condition — lock รอบ check+set pipeline_state['running'] ทั้งใน run_pipeline (HTTP) และ scheduled_run (APScheduler thread)
- [x] sanitize date param ใน /api/reports/{report_type} — strip path separators + validate path ไม่หลุดนอก REPORTS_DIR ด้วย resolve().is_relative_to()

### Reference
```python
# server/app.py — pipeline lock
import threading
_pipeline_lock = threading.Lock()

# in _execute_sync and scheduled_run:
with _pipeline_lock:
    if pipeline_state["running"]:
        return  # or raise 409
    pipeline_state["running"] = True

# report date sanitize
if date:
    safe_date = "".join(c for c in date if c.isalnum() or c == '-')
    path = REPORTS_DIR / f"{report_type}_{safe_date}.md"
    if not path.resolve().is_relative_to(REPORTS_DIR.resolve()):
        raise HTTPException(400, "Invalid date")
```
