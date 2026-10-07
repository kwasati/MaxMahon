---
project: 4-MaxMahon
created: 2026-05-12
last_updated: 2026-05-18
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: รัน fetch_fundamentals('BBL') แล้ว DPS ทุกปีตรงกับ yahoo dividend events จริง — BBL ปี 2010 DPS = 5.00 (ไม่ใช่ 0.06 ที่ derive จาก thaifin yield × close), BBL ปี 2024 DPS = 8.50, ปี 2025 DPS = 10.0 + dividend_streak + dividend_growth_streak คำนวณจาก yahoo events เท่านั้น

### รายละเอียด
- Live test confirmed (data/research/source_coverage_test_2026-05-12.json): thaifin ไม่มี DPS field — ระบบ derive จาก dividend_yield × close = approximate
- Cross-check BBL: thaifin DPS 2010 = 0.06 vs yahoo events = 5.00 → diff 99%
- Cross-check BBL: thaifin DPS 2017-2025 → underestimate 14-33% consistently
- Root cause: dividend_yield จาก thaifin คือ yield ของช่วงเวลาหนึ่ง (อาจเป็น point-in-time จาก SET หรือ Yahoo) คูณ close ณ end of year → ไม่สะท้อน DPS ที่จ่ายจริงในงวด
- data_adapter.py line 762-774 มี logic ใช้ yahoo อยู่แล้ว (yf_dps_by_fy = adapter_result['dps_by_fiscal_year']) แต่ fallback ที่ line 774 = tf_snap.get('dividend_yield') = derive จาก thaifin
- ต้องลบ fallback ทั้งหมด — ถ้า yahoo flake → FAIL hard (existing Stage 2 retry handle อยู่แล้ว)
- yearly_metrics[*]['dividend_yield'] (จาก thaifin yearly) — ใช้สำหรับ HISTORY display ได้ (ไม่กระทบ DPS) — แต่ DPS per year ต้องใช้ yahoo events เท่านั้น
- _attribute_dividends_to_fiscal_years (data_adapter.py:374-442) ใช้ yahoo events อยู่แล้ว — ไม่ต้องแก้
- Plan C ต้องรอ Plan B เพราะ Plan B refactor fetch_fundamentals control flow

### Scope Boundary
**In scope:**
- scripts/data_adapter.py — fetch_fundamentals DPS fallback removal (บรรทัด 762-774)
- scripts/data_adapter.py — ลบ logic ที่ derive DPS จาก thaifin yield (ถ้ามีตำแหน่งอื่น)
- scripts/fetch_data.py — verify _build_aggregates ไม่ derive DPS จาก thaifin

**Out of scope:**
- thaifin yearly dividend_yield field — keep สำหรับ history display
- yahoo retry mechanism (Stage 2 + integrity guard)
- DPS event-by-event API endpoint (frontend ไม่ต้องเปลี่ยน)

### Non-goals
- ไม่ migrate ออกจาก yahoo — ไม่มี source อื่นมี DPS event-by-event
- ไม่เปลี่ยน fiscal year attribution logic (_attribute_dividends_to_fiscal_years)
- ไม่เปลี่ยน Stage 2 retry หรือ integrity guard

# Plan C — DPS Source-of-Truth = Yahoo Events Only

> Part 3 of 7 — DPS yahoo-only. ลบ thaifin DPS derived (พลาด 14-99%) ใช้ yahoo events ที่แม่นจริง เป็น source of truth.
> Depends on: filter-02-setsmart-migration (Plan B refactor fetch_fundamentals — ต้องเสร็จก่อน)
> Parallel-safe with: none

## Phase 1: Audit + remove thaifin DPS fallback
- [x] Grep audit: grep -rn 'dividend_yield' scripts/ | grep -v '.pyc' — list ทุก location ที่ใช้ dividend_yield — Acceptance: เห็น list ครบ ระบุได้ว่าตำแหน่งไหน derive DPS vs ตำแหน่งไหน read yield สำหรับ display
- [x] แก้ scripts/data_adapter.py fetch_fundamentals (บรรทัด 762-774) — ลบ fallback `dy = tf_snap.get('dividend_yield')` ที่ใช้เมื่อไม่มี yahoo DPS — แทนด้วย `dy = None` + log warning — Scope: dy snapshot ยัง override ได้จาก SETSMART (Plan B) — แค่ลบ thaifin path ที่ derive DPS — Acceptance: เมื่อ yahoo events ว่าง + SETSMART cold → dy = None (ไม่ใช่ thaifin yield) + log warning 'no yahoo DPS, dy unset'
- [x] Grep: grep -rn 'dps' scripts/data_adapter.py — list ทุกที่ที่ derive DPS — Acceptance: ทุก derived DPS location ใช้ yahoo events (jf_dps_by_fy หรือ dps_by_year) ไม่มี thaifin yield × close path

### Reference
```python
# current (scripts/data_adapter.py:762-774)
complete_fys = sorted([y for y, ok in yf_fy_complete.items() if ok])
latest_complete_fy = complete_fys[-1] if complete_fys else None
if latest_complete_fy is not None:
    dps_current = yf_dps_by_fy.get(latest_complete_fy)
else:
    dps_current = None
if dps_current is not None and price is not None and price > 0:
    dy = dps_current / price * 100
else:
    dy = tf_snap.get("dividend_yield")  # fallback thaifin — REMOVE THIS

# new
complete_fys = sorted([y for y, ok in yf_fy_complete.items() if ok])
latest_complete_fy = complete_fys[-1] if complete_fys else None
if latest_complete_fy is not None:
    dps_current = yf_dps_by_fy.get(latest_complete_fy)
else:
    dps_current = None

if dps_current is not None and price is not None and price > 0:
    dy = dps_current / price * 100
else:
    dy = None  # no yahoo DPS — let SETSMART override (Plan B) or stay None
    logger.warning(
        "no yahoo DPS for %s (latest_complete_fy=%s, dps_current=%s, price=%s) — "
        "dy unset (will use SETSMART if cache warm, else None)",
        symbol, latest_complete_fy, dps_current, price
    )
```

## Phase 2: Verify + smoke test
- [x] py -c 'from scripts.data_adapter import fetch_fundamentals; r=fetch_fundamentals("BBL"); dh=r["dividend_history"]; print("2010 DPS:", dh.get(2010)); print("2024 DPS:", dh.get(2024)); print("2025 DPS:", dh.get(2025))' — Acceptance: 2010 DPS ≈ 5.0 (ไม่ใช่ 0.06), 2024 DPS ≈ 8.5, 2025 DPS ≈ 10.0
- [x] py -c 'from scripts.fetch_data import fetch_multi_year; r=fetch_multi_year("BBL"); agg=r["aggregates"]; print("streak:", agg["dividend_streak"]); print("growth_streak:", agg["dividend_growth_streak"])' — Acceptance: dividend_streak ≥ 20 (BBL จ่ายตั้งแต่ 2004 = 22 ปี), dividend_growth_streak ≥ 3 (Plan A bug fix + Plan C accurate DPS = streak พ้น threshold)
- [x] Smoke 5 หุ้น: รัน py scripts/scan.py --symbols BBL,PTT,CPALL,KBANK,SCB --no-write + verify ไม่มี crash + DPS ตรงกับ yahoo events — Acceptance: scan สำเร็จ + screener output dividend_streak ของ BBL/PTT/CPALL/KBANK/SCB ตรงกับที่ verify manual

### Reference
Verify commands:
```bash
cd C:\WORKSPACE\projects\4-MaxMahon

# Test 1: DPS history accurate
py -c "
from scripts.data_adapter import fetch_fundamentals
r = fetch_fundamentals('BBL')
import json
print(json.dumps(r['dividend_history'], indent=2, default=str))
"

# Expected (from yahoo events):
# 2010: ~5.0
# 2020: ~2.5
# 2024: ~8.5
# 2025: ~10.0

# Test 2: streak with Plan A fix + Plan C accurate DPS
py -c "
from scripts.fetch_data import fetch_multi_year
r = fetch_multi_year('BBL')
print('streak:', r['aggregates']['dividend_streak'])
print('growth_streak:', r['aggregates']['dividend_growth_streak'])
"
# Expected: streak ≥ 20, growth_streak ≥ 3 (5+ ปีโตติด: 2020→2025)
```
