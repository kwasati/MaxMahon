---
project: MaxMahon
created: 2026-04-27
last_updated: 2026-04-27
status: done
---

## Target / Goal
ทำได้: รัน `py scripts/_verify_dps_fix.py` แล้ว METCO yield ≈ 11.36% (เดิม 3.03% — annual-pay marked incomplete bug). BBL/QH/SAT คงตรง SET ภายใน ±1% เหมือนเดิม.

# Fix FY Completeness Detection — Adaptive Pay Frequency

> Heuristic `is_complete` เดิมตัดสินจาก has_both (interim+final) OR has_next_fy → ผิดสำหรับหุ้นจ่ายปีละครั้ง (METCO: Feb 2026 = 30 บาท แต่ mark incomplete → fallback FY ก่อน 8 บาท → yield 3.03% แทน 11.36%). แก้โดย detect typical pay frequency จาก history ของบริษัทเอง (mode ของ event count/FY) → FY complete = event count ≥ typical. ทำให้ Yahoo/thaifin path คำนวณ history 20+ ปีถูกต้องสำหรับหุ้นทุก pay pattern (annual / semi / quarterly) — ส่วน edge case (new stock first year, pattern transition) จะถูก double-check ด้วย SETSMART layer (plan ถัดไป) ที่มี data ปัจจุบันตรงเป๊ะ.

## Phase 1: Adaptive frequency detection
- [x] แก้ function `_attribute_dividends_to_fiscal_years(divs)` ใน `projects/MaxMahon/scripts/data_adapter.py` (บรรทัด ~369-428). เปลี่ยน logic ของ `is_complete`: แทนที่ rule เดิม `has_both OR has_next_fy` ด้วย adaptive frequency detection:

(1) นับ event count ต่อ FY จาก `events_per_fy` ของ FY ก่อนๆ (sorted_fys[:-1] — exclude latest FY ที่อาจยังไม่ครบ)

(2) หา mode (จำนวนที่พบบ่อยสุด) → `typical_count`. ถ้า history ว่างเปล่า → default 2 (semi-annual common pattern Thai stocks)

(3) สำหรับแต่ละ FY: `is_complete[fy] = len(events_per_fy.get(fy, [])) >= typical_count`

เก็บ `events_per_fy` + `by_fy` logic เดิม (ไม่แตะ heuristic จัด FY ของ event). เพิ่ม `typical_count` ใน return dict เป็น metadata. — Scope: ห้ามแก้ logic จัด FY (Jan-Jun → final ปีก่อน / Jul-Dec → interim ปีนี้). ห้ามแตะ `_fetch_yahoo_supplement`, merge function, smoke test เดิม. — Acceptance: รัน `py scripts/data_adapter.py` (smoke test เดิม BBL semi-annual) ต้องผ่าน 'FY attribution OK'. รัน `py -c "..."` กับ METCO mock data (1 event/year ติดกัน 5 ปี + ปีล่าสุด 1 event) ต้องได้ `is_complete[latest_fy] = True`
- [x] Update smoke test ที่ `if __name__ == '__main__':` block ท้ายไฟล์ `data_adapter.py` (บรรทัด ~845-855) — เพิ่ม assertion case ที่ 2 สำหรับ annual-pay pattern: mock divs ของ METCO (5 ปี ปีละ 1 event ก.พ.) + assert `is_complete[2025]=True` แม้มี event เดียว. — Scope: ห้ามลบ assertion BBL เดิม (ต้องผ่านทั้งคู่). — Acceptance: รัน `py scripts/data_adapter.py` ต้องเห็น 'FY attribution OK' (assert ทั้ง BBL pattern + METCO pattern ผ่าน) ไม่ raise AssertionError

### Reference
```python
# current (data_adapter.py:~419-428 — completeness logic ใน _attribute_dividends_to_fiscal_years)
    # Detect completeness: FY is complete if has both interim+final, OR has only 1 payment but next FY already has payments (means the company paid annually)
    is_complete = {}
    sorted_fys = sorted(by_fy.keys())
    for i, fy in enumerate(sorted_fys):
        periods = {p for _, _, p in events_per_fy.get(fy, [])}
        has_both = 'interim' in periods and 'final' in periods
        has_next_fy = (i < len(sorted_fys) - 1) and (sorted_fys[i+1] in by_fy)
        is_complete[fy] = has_both or has_next_fy

    return {'by_fy': by_fy, 'is_complete': is_complete, 'events_per_fy': events_per_fy}

# new (data_adapter.py:~419-435 — adaptive frequency detection)
    # Detect completeness: adaptive per company's typical pay frequency
    # 1. Count events per FY for older FYs (skip latest 1 — may still be in-progress)
    # 2. Find mode (most common count) → typical_count for this company
    # 3. FY complete = event count >= typical_count
    sorted_fys = sorted(by_fy.keys())
    is_complete = {}
    typical_count = 2  # default semi-annual (common Thai pattern)
    if len(sorted_fys) >= 2:
        # Use older FYs (exclude latest) to detect pattern
        older_counts = [len(events_per_fy.get(fy, [])) for fy in sorted_fys[:-1]]
        if older_counts:
            # Mode: most common count
            from collections import Counter
            typical_count = Counter(older_counts).most_common(1)[0][0]
            if typical_count < 1:
                typical_count = 1  # safety floor

    for fy in sorted_fys:
        actual_count = len(events_per_fy.get(fy, []))
        is_complete[fy] = actual_count >= typical_count

    return {'by_fy': by_fy, 'is_complete': is_complete, 'events_per_fy': events_per_fy, 'typical_count': typical_count}

# current smoke test (data_adapter.py:~845-855)
if __name__ == '__main__':
    import pandas as pd
    mock_divs = pd.Series(
        [2.0, 10.0],
        index=[pd.Timestamp('2025-09-15'), pd.Timestamp('2026-04-22')],
    )
    result = _attribute_dividends_to_fiscal_years(mock_divs)
    assert result['by_fy'][2025] == 12.0, f"Expected FY2025=12.0, got {result['by_fy'].get(2025)}"
    print('FY attribution OK')

# new smoke test (add 2nd assertion for annual-pay pattern)
if __name__ == '__main__':
    import pandas as pd

    # Test 1: Semi-annual pattern (BBL-like)
    bbl_divs = pd.Series(
        [2.0, 10.0],
        index=[pd.Timestamp('2025-09-15'), pd.Timestamp('2026-04-22')],
    )
    r1 = _attribute_dividends_to_fiscal_years(bbl_divs)
    assert r1['by_fy'][2025] == 12.0, f"BBL: Expected FY2025=12.0, got {r1['by_fy'].get(2025)}"
    # Note: BBL test has only 1 FY in history → typical_count=2 default → FY2025 (1 event so far before final)... actually has 2 events so complete=True
    # Re-check: bbl_divs has 2 events both attributed to FY2025 → events_per_fy[2025] = 2 events
    # But sorted_fys = [2025] → older_counts = [] (excluded) → typical_count = 2 default
    # actual_count for FY2025 = 2 → is_complete[2025] = True
    assert r1['is_complete'][2025] is True, f"BBL FY2025 should be complete"

    # Test 2: Annual-pay pattern (METCO-like) — pays once per year in February
    metco_divs = pd.Series(
        [10.0, 14.0, 18.0, 10.0, 8.0, 30.0],
        index=[
            pd.Timestamp('2021-02-10'),  # FY2020 final
            pd.Timestamp('2022-02-09'),  # FY2021 final
            pd.Timestamp('2023-02-08'),  # FY2022 final
            pd.Timestamp('2024-02-07'),  # FY2023 final
            pd.Timestamp('2025-02-06'),  # FY2024 final
            pd.Timestamp('2026-02-05'),  # FY2025 final (single event = whole year for annual-pay)
        ],
    )
    r2 = _attribute_dividends_to_fiscal_years(metco_divs)
    assert r2['typical_count'] == 1, f"METCO typical should be 1 (annual), got {r2.get('typical_count')}"
    assert r2['by_fy'][2025] == 30.0, f"METCO FY2025 should be 30.0, got {r2['by_fy'].get(2025)}"
    assert r2['is_complete'][2025] is True, f"METCO FY2025 should be complete (annual-pay, 1 event = full year)"

    print('FY attribution OK')
```

## Phase 2: Re-verify against SET
- [x] รัน `py scripts/_verify_dps_fix.py` (script เดิมไม่ต้องแก้) ที่ `cd projects/MaxMahon` — script จะ fetch 4 หุ้น (BBL/METCO/QH/SAT) ผ่าน fetch_fundamentals + write report `docs/dps-fix-verification-{YYYY-MM-DD}.md` (วันที่รัน — script ใช้ `datetime.now()`). ก่อนรัน: ลบไฟล์ `docs/dps-fix-verification-*.md` เก่าทั้งหมด (กัน orphan stale report). ตรวจ output ของ METCO ใหม่ — yield ต้อง ≈ 11-12% (เดิม 3.03%). อัพเดต report บน main branch ให้ตรง output ใหม่. — Scope: ห้ามแก้ verify script. ห้ามแก้ data_adapter (เสร็จไปแล้วใน Phase 1). — Acceptance: ไฟล์ `docs/dps-fix-verification-{YYYY-MM-DD}.md` ระบุ METCO yield 11-12% range + ทุกหุ้นยังมี structure ถูกต้อง + ไม่มี dps-fix-verification เก่าค้างใน docs/ + commit message ระบุว่า re-verified after frequency fix

### Reference
```
# Verification expected (SET reference):
#   BBL.BK   ≈ 6.8%   (semi-annual, ตรงเหมือนเดิม)
#   METCO.BK ≈ 11.4%  (NEW — fix annual-pay)
#   QH.BK    ≈ 6-7%   (ตรงเหมือนเดิม)
#   SAT.BK   ≈ 11%    (annual-pay เหมือน METCO — ต้อง verify pattern)
#
# Tolerance: ±1.0% absolute
```
