---
project: MaxMahon
created: 2026-05-07
last_updated: 2026-05-07
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: รัน hard_filter() ใหม่ pass หุ้น growing dividend (yield 2-5% + DPS โต 3+ ปี) ที่เคย FAIL และ assign_signals() ใหม่ออก signal NIWES_GROWING / YIELD_SPIKE_FROM_PRICE_DROP ตามเงื่อนไข — ตรงเจตนา ดร.นิเวศน์ จาก docs/niwes/04-criteria.md ข้อ 1

### รายละเอียด
- Layer 1 hard filter ใหม่: yield ≥ 5% PASS (main) OR (2.0% ≤ yield < 5% AND dividend_growth_streak ≥ 3) PASS (exception) — else FAIL
- ตัด dividend_streak ออกจาก hard filter ทั้ง FAIL+REVIEW (เก่า: <3 FAIL / 3-4 REVIEW / 5+ PASS) — ย้ายไปอยู่ใน scoring (Streak 15 pts ที่มีอยู่แล้ว ไม่แก้)
- เหตุผล: Niwes พูด 5-5-5-5 = yield 5% + 5 ปีข้างหน้า + 5 sectors + ถือ 5 ปี — ไม่มี streak ≥ 5 ในตัวเลข แกพูดเรื่อง forward-looking ไม่ใช่ backward streak
- DEFAULT_FILTERS เพิ่ม 2 keys: growing_yield_floor (default 2.0) + growing_min_streak (default 3) — config.json override ได้
- Signal NIWES_5555 เก่า keep ตามเดิม (yield ≥ 5 + streak ≥ 5 + EPS 5/5 + PE ≤ 15 + PBV ≤ 1.5) — เป็น main path tag
- Signal NIWES_GROWING ใหม่: 2.0% ≤ yield < 5% AND growth_streak ≥ 3 AND EPS 5/5 AND PE ≤ 15 AND PBV ≤ 1.5 — exception path tag
- Signal YIELD_SPIKE_FROM_PRICE_DROP ใหม่: dy / five_year_avg_yield > 1.8 AND five_year_avg_yield > 0 — warning ราคาตกทำ yield ดีดไม่ใช่ DPS โต
- DIVIDEND_TRAP เก่า keep (dy > 8 + ROE declining + payout > 100) — เงื่อนไขคนละแบบ ไม่ทับซ้อน YIELD_SPIKE
- Smoke test fixture-based 5 cases — ไม่ refetch market data, ไม่ต้องรัน scan 933 หุ้นจริง

### Scope Boundary
**In scope:**
- projects/MaxMahon/scripts/screen_stocks.py — DEFAULT_FILTERS config + hard_filter() yield/streak logic + assign_signals() เพิ่ม 2 tags
- projects/MaxMahon/scripts/report_template.py — _TAG_NARRATIVES dict เพิ่ม 2 keys
- projects/MaxMahon/scripts/_smoke_niwes_filter.py — สร้างใหม่ (smoke test fixture-based 5 cases)

**Out of scope:**
- data_adapter.py / fetch_data.py — data schema ใช้ field เดิม (dividend_yield / dividend_streak / dividend_growth_streak / five_year_avg_yield) ไม่แตะ
- Quality Score scoring weights (dividend_score, valuation_score, etc.) — keep as is
- DCA simulator / portfolio_builder / watchlist API — ไม่กระทบ
- Frontend UI signal tag display — ใช้ระบบ tag เดิมที่ render dynamic อยู่แล้ว
- Full scan 933 หุ้นจริง — รอ weekly cron / manual trigger ปกติ ไม่บังคับ

### Non-goals
- ไม่บังคับ 5 ปีย้อนหลัง yield ทุกปี > 5% — ขัดเจตนา Niwes ที่เปิดทาง growing 2-3% (source: Share2Trade 27 พ.ค. 2568)
- ไม่ลบ dividend_streak ออกจาก aggregates หรือ scoring — ย้ายแค่ออกจาก hard filter
- ไม่เปลี่ยน data schema / ไม่ refetch / ไม่ rebuild history.json
- ไม่ทำ forward DPS projection จริง — Claude deep analyze ผ่าน /api/stock/{sym}/analyze ทำหน้าที่นั้นแล้ว
- ไม่แก้ scoring formula หรือ weights หลัก (Quality Score 100 pts โครงสร้างเดิม)

# MaxMahon Niwes 5-5-5-5 Filter Alignment

> Hard filter ปัจจุบันบังคับ yield ≥ 5% strict + streak ≥ 5 ทำให้ตัด CPALL pre-COVID style (yield 2-3% แต่ปันผลโต) ที่ Niwes บอกชัดว่ารับ — แก้ filter logic ให้รับ exception path + ตัด streak ออกจาก hard filter (ไม่ใช่ตัวเลข 5-5-5-5 ของแก) + เพิ่ม signal warning yield-spike-from-price-drop

## Phase 1: Hard Filter Logic Update
- [x] อัปเดต DEFAULT_FILTERS dict ใน `projects/MaxMahon/scripts/screen_stocks.py` (บรรทัด 31-40) — เพิ่ม key `growing_yield_floor: 2.0` + `growing_min_streak: 3`, เก็บ `min_dividend_streak: 5` ไว้สำหรับ scoring (ไม่ถูกใช้ใน hard filter ใหม่). Scope: ห้ามแก้ key อื่น, ห้ามแก้ load_filters() function. Acceptance: grep `growing_yield_floor` ใน screen_stocks.py = 1 match (config), grep `growing_min_streak` = 1 match.
- [x] แทนที่ block streak (บรรทัด 81-86) + block yield (บรรทัด 106-111) ใน function `hard_filter()` ของ `projects/MaxMahon/scripts/screen_stocks.py` — ลบ streak block ทิ้งทั้งหมด + แทนที่ yield block ด้วย logic ใหม่ที่รับ exception path. Logic: dy >= 5 → pass, growing_yield_floor <= dy < 5 AND growth_streak >= growing_min_streak → pass, else fail_reasons. Scope: ห้ามแก้ EPS / mcap / PE / PBV blocks, ห้ามแก้ docstring เกินจำเป็น (อัปเดต docstring เฉพาะที่ rule 1+2 เปลี่ยนไป). Acceptance: หุ้น dy=3.0 + growth_streak=5 + EPS 5/5 + PE 12 + PBV 1.0 + mcap 10B → return ('PASS', []) (เคย FAIL เพราะ yield < 5%); หุ้น dy=3.0 + growth_streak=2 → return ('FAIL', [...]) เหตุผล growing exception not met; หุ้น dy=6 + streak=2 + EPS 5/5 + PE 12 + PBV 1.0 + mcap 10B → return ('PASS', []) (เคย FAIL เพราะ streak <3).

### Reference
```python
# current — screen_stocks.py:31-40
DEFAULT_FILTERS = {
    "min_dividend_yield": 5.0,
    "min_dividend_streak": 5,
    "min_eps_positive_years": 5,
    "max_pe": 15.0,
    "bonus_pe": 8.0,
    "max_pbv": 1.5,
    "bonus_pbv": 1.0,
    "min_market_cap": 5_000_000_000,
}

# new
DEFAULT_FILTERS = {
    "min_dividend_yield": 5.0,
    "min_dividend_streak": 5,
    "growing_yield_floor": 2.0,
    "growing_min_streak": 3,
    "min_eps_positive_years": 5,
    "max_pe": 15.0,
    "bonus_pe": 8.0,
    "max_pbv": 1.5,
    "bonus_pbv": 1.0,
    "min_market_cap": 5_000_000_000,
}
```

```python
# current — screen_stocks.py:81-86 (DELETE entire block)
    # 2. Dividend streak — 3-tier
    streak = agg.get("dividend_streak", 0)
    if streak < 3:
        fail_reasons.append(f"dividend streak {streak}yr < 3 (FAIL)")
    elif streak < HARD_FILTERS["min_dividend_streak"]:
        review_reasons.append(f"dividend streak {streak}yr (3-4 = REVIEW)")

# current — screen_stocks.py:106-111 (REPLACE entire block)
    # 1. Dividend yield — hard
    dy = data.get("dividend_yield")
    if dy is None:
        fail_reasons.append("ไม่มีข้อมูลปันผล")
    elif dy < HARD_FILTERS["min_dividend_yield"]:
        fail_reasons.append(f"dividend yield {dy:.1f}% < {HARD_FILTERS['min_dividend_yield']:.0f}%")

# new — replacement for yield block (streak block removed entirely)
    # 1. Dividend yield — hard, with Niwes growing-dividend exception
    dy = data.get("dividend_yield")
    growth_streak = agg.get("dividend_growth_streak", 0)
    if dy is None:
        fail_reasons.append("ไม่มีข้อมูลปันผล")
    elif dy >= HARD_FILTERS["min_dividend_yield"]:
        pass
    elif (dy >= HARD_FILTERS["growing_yield_floor"]
          and growth_streak >= HARD_FILTERS["growing_min_streak"]):
        pass
    else:
        fail_reasons.append(
            f"dividend yield {dy:.1f}% < {HARD_FILTERS['min_dividend_yield']:.0f}% "
            f"(growing exception not met: growth_streak {growth_streak}yr < {HARD_FILTERS['growing_min_streak']})"
        )
```

Docstring ของ `hard_filter()` (บรรทัด 59-70) — แก้บรรทัดที่อ้าง rule streak/yield ให้ตรง logic ใหม่:
- บรรทัด "1. dividend_yield ≥ 5% (hard FAIL)" → "1. dividend_yield ≥ 5% (main path) OR 2.0%-5% AND growth_streak ≥ 3 (Niwes growing exception) — else FAIL"
- บรรทัด "2. dividend_streak: ≥5 PASS / 3-4 REVIEW / <3 FAIL" → ลบทิ้ง (streak ไม่อยู่ใน hard filter แล้ว — อยู่ใน scoring เท่านั้น)

## Phase 2: Signal Tags — NIWES_GROWING + YIELD_SPIKE_FROM_PRICE_DROP
- [x] เพิ่ม 2 signal blocks ใน function `assign_signals()` ของ `projects/MaxMahon/scripts/screen_stocks.py` — block แรก NIWES_GROWING ใส่ทันทีหลัง NIWES_5555 block (หลังบรรทัด 524), block ที่สอง YIELD_SPIKE_FROM_PRICE_DROP ใส่หลัง QUALITY_DIVIDEND block (หลังบรรทัด 532). NIWES_GROWING คือ exception path tag ที่ไม่ใส่ NIWES_5555 (yield < 5% แม้จะ pass filter), YIELD_SPIKE คือ warning tag ใส่คู่กับ tag อื่นได้. Scope: ห้ามแก้ block เก่า (NIWES_5555 / DIVIDEND_TRAP / DEEP_VALUE / QUALITY_DIVIDEND / HIDDEN_VALUE / DATA_WARNING) — keep ตามเดิมทั้งหมด. Acceptance: หุ้น dy=3 + growth_streak=5 + eps_5_pos + pe=10 + pbv=1.0 + streak=2 → signals มี 'NIWES_GROWING' (ไม่มี NIWES_5555); หุ้น dy=8 + yield_5y=4 → signals มี 'YIELD_SPIKE_FROM_PRICE_DROP'; หุ้น dy=7 + yield_5y=5 → ไม่มี YIELD_SPIKE (ratio 1.4 < 1.8).

### Reference
```python
# current — screen_stocks.py:515-524 (NIWES_5555 block — KEEP AS IS, do not modify)
    # NIWES_5555 — passes 5-5-5-5
    norm_eps = compute_normalized_earnings(data)
    sorted_years = sorted(norm_eps.keys())[-5:] if norm_eps else []
    eps_recent = [norm_eps[y] for y in sorted_years]
    eps_5_pos = len(eps_recent) >= 5 and all(e is not None and e > 0 for e in eps_recent)

    if (dy >= 5 and streak >= 5 and eps_5_pos
            and pe is not None and 0 < pe <= 15
            and pbv is not None and 0 < pbv <= 1.5):
        signals.append("NIWES_5555")

# new — INSERT after line 524 (after NIWES_5555 append)
    # NIWES_GROWING — Niwes growing-dividend exception (yield 2-5% + DPS growing 3+ yrs + EPS 5/5 + PE/PBV ok)
    growth_streak = agg.get("dividend_growth_streak", 0)
    if (2.0 <= dy < 5 and growth_streak >= 3 and eps_5_pos
            and pe is not None and 0 < pe <= 15
            and pbv is not None and 0 < pbv <= 1.5):
        signals.append("NIWES_GROWING")
```

```python
# current — screen_stocks.py:530-532 (QUALITY_DIVIDEND block — KEEP AS IS)
    # QUALITY_DIVIDEND — yield≥5 + payout<70 + streak≥10
    if dy >= 5 and payout is not None and payout < 0.70 and streak >= 10:
        signals.append("QUALITY_DIVIDEND")

# new — INSERT after line 532 (after QUALITY_DIVIDEND append)
    # YIELD_SPIKE_FROM_PRICE_DROP — yield ดีดเพราะราคาตก ไม่ใช่ DPS โต (warning, not exclusion)
    yield_5y = data.get("five_year_avg_yield") or 0
    if yield_5y > 0 and dy / yield_5y > 1.8:
        signals.append("YIELD_SPIKE_FROM_PRICE_DROP")
```

## Phase 3: Report Narratives
- [x] เพิ่ม 2 entries ใน `_TAG_NARRATIVES.update({...})` ของ `projects/MaxMahon/scripts/report_template.py` (บรรทัด 22-33) — key `NIWES_GROWING` + `YIELD_SPIKE_FROM_PRICE_DROP` พร้อม narrative ภาษาไทยที่อธิบายเงื่อนไขชัด. Scope: ห้ามแก้ key เก่า, ห้ามแก้ _PATTERNS_PATH หรือ load logic. Acceptance: grep `NIWES_GROWING` ใน report_template.py = 1 match, grep `YIELD_SPIKE_FROM_PRICE_DROP` = 1 match; รัน `py scripts/report_template.py` ไม่ error syntax.

### Reference
```python
# current — report_template.py:22-33
_TAG_NARRATIVES.update({
    "NIWES_5555": "ผ่านเกณฑ์ 5-5-5-5 ครบ (yield≥5 / streak≥5 / EPS 5yr+ / PE≤15 / PBV≤1.5)",
    "BRAND_MOAT": "Brand moat — margin สูง + dividend streak ยาว",
    "STRUCTURAL_MOAT": "Structural moat — utility/transport/telecom scale ใหญ่",
    "GOVT_LOCKIN": "Government lock-in — recurring revenue จากภาครัฐ",
    "HIDDEN_VALUE": "มี holding ที่ตลาดไม่ได้ pricing in",
    "DEEP_VALUE": "PE ≤8 + PBV ≤1.0 — ถูกกว่าค่าเฉลี่ย",
    "QUALITY_DIVIDEND": "yield ≥5% + payout <70% + streak ≥10 ปี",
    "DIVIDEND_TRAP": "ระวัง — yield >8% + ROE declining + payout >100%",
    "DATA_WARNING": "ข้อมูลผิดปกติ — ตรวจสอบก่อนใช้",
    "OVERPRICED": "valuation grade F — แพงกว่าคุณภาพ",
})

# new — เพิ่ม 2 entries ใน update() dict (insert ก่อน closing brace)
_TAG_NARRATIVES.update({
    "NIWES_5555": "ผ่านเกณฑ์ 5-5-5-5 ครบ (yield≥5 / streak≥5 / EPS 5yr+ / PE≤15 / PBV≤1.5)",
    "NIWES_GROWING": "Niwes growing-dividend exception — yield 2-5% + ปันผลเพิ่มต่อเนื่อง 3+ ปี (เจตนา ดร.นิเวศน์ ที่รับหุ้น 2-3% โต)",
    "BRAND_MOAT": "Brand moat — margin สูง + dividend streak ยาว",
    "STRUCTURAL_MOAT": "Structural moat — utility/transport/telecom scale ใหญ่",
    "GOVT_LOCKIN": "Government lock-in — recurring revenue จากภาครัฐ",
    "HIDDEN_VALUE": "มี holding ที่ตลาดไม่ได้ pricing in",
    "DEEP_VALUE": "PE ≤8 + PBV ≤1.0 — ถูกกว่าค่าเฉลี่ย",
    "QUALITY_DIVIDEND": "yield ≥5% + payout <70% + streak ≥10 ปี",
    "DIVIDEND_TRAP": "ระวัง — yield >8% + ROE declining + payout >100%",
    "YIELD_SPIKE_FROM_PRICE_DROP": "yield สูงเพราะราคาเพิ่งตก — เช็คว่า DPS โตจริงหรือ trap (yield_now / 5y_avg > 1.8x)",
    "DATA_WARNING": "ข้อมูลผิดปกติ — ตรวจสอบก่อนใช้",
    "OVERPRICED": "valuation grade F — แพงกว่าคุณภาพ",
})
```

## Phase 4: Smoke Test
- [x] สร้างไฟล์ใหม่ `projects/MaxMahon/scripts/_smoke_niwes_filter.py` — fixture-based smoke test ที่ import `hard_filter` + `assign_signals` จาก screen_stocks แล้วทดสอบ 5 cases. Cases: (1) main path PASS — dy=7.5/streak=10/growth_streak=2/eps_5_pos=True/pe=10/pbv=1.0/mcap=10B → expect ('PASS', []) + signal มี NIWES_5555 + ไม่มี NIWES_GROWING; (2) exception PASS — dy=3.0/streak=8/growth_streak=5/eps_5_pos/pe=12/pbv=1.2/mcap=10B → expect ('PASS', []) + signal มี NIWES_GROWING + ไม่มี NIWES_5555; (3) exception FAIL — dy=3.0/streak=8/growth_streak=2 → expect ('FAIL', [...]) เหตุผลมีคำว่า 'growing exception not met'; (4) low-streak regression — dy=6.0/streak=2/growth_streak=1/eps_5_pos/pe=10/pbv=1.0/mcap=10B → expect ('PASS', []) (เคย FAIL ก่อนแก้); (5) yield-spike — dy=8.0/yield_5y=4.0 → expect signal มี 'YIELD_SPIKE_FROM_PRICE_DROP'. Helper function `compute_normalized_earnings` ต้อง mock ผ่าน yearly_metrics ที่มี diluted_eps positive 5 ปี + close + bvps + payout_ratio + roe เพียงพอให้ compute return non-empty. Scope: ห้าม import market data, ห้าม fetch จริง, ห้ามแก้ screen_stocks.py ใน task นี้ (แก้แล้วใน Phase 1+2). Acceptance: รัน `py projects/MaxMahon/scripts/_smoke_niwes_filter.py` exit 0 + print 5 cases ผ่านครบ + แต่ละ case มี [PASS] หรือ [FAIL] label ชัดเจน.
- [x] รัน smoke test `py projects/MaxMahon/scripts/_smoke_niwes_filter.py` แล้ว verify output. ถ้า case ไหน fail → debug ที่ source ของ logic ผิด (ห้ามแก้ fixture เพื่อทำให้ pass — fixture สะท้อนเจตนา). Verify เพิ่มเติม: import screen_stocks ไม่ error (`py -c "from scripts.screen_stocks import hard_filter, assign_signals"` cwd=projects/MaxMahon). Scope: ไม่รัน scan 933 หุ้นจริง, ไม่ต้อง verify API endpoint. Acceptance: smoke test exit 0; import verify exit 0; ถ้ามี case fail ต้อง root-cause + แก้ source logic ใน screen_stocks.py แล้ว rerun pass.

### Reference
```python
# new file — projects/MaxMahon/scripts/_smoke_niwes_filter.py
"""Smoke test for Niwes 5-5-5-5 filter alignment changes.

Fixture-based — does not fetch market data. Verifies hard_filter() + assign_signals()
behavior across 5 critical cases (main path, exception path, regression, signals).
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from screen_stocks import hard_filter, assign_signals


def _make_fixture(*, dy, streak, growth_streak, eps_5_pos=True, pe=10, pbv=1.0,
                  mcap=10_000_000_000, payout=0.5, yield_5y=None, roe_trend=None):
    """Build a data dict shaped like fetch_data output for filter/signal testing."""
    eps_list = [1.0, 1.1, 1.2, 1.3, 1.5] if eps_5_pos else [1.0, -0.5, 1.2, 1.3, 1.5]
    yearly = []
    for i, e in enumerate(eps_list):
        yearly.append({
            "year": 2020 + i,
            "diluted_eps": e,
            "close": 100.0,
            "bvps": 80.0,
            "payout_ratio": payout,
            "roe": (roe_trend[i] if roe_trend else 0.15),
            "net_margin": 0.10,
            "revenue": 1e9,
        })
    return {
        "symbol": "TEST.BK",
        "dividend_yield": dy,
        "pe_ratio": pe,
        "pb_ratio": pbv,
        "market_cap": mcap,
        "payout_ratio": payout,
        "five_year_avg_yield": yield_5y,
        "yearly_metrics": yearly,
        "aggregates": {
            "dividend_streak": streak,
            "dividend_growth_streak": growth_streak,
        },
        "warnings": [],
    }


CASES = [
    {
        "name": "1. Main path PASS (yield 7.5, streak 10)",
        "data": _make_fixture(dy=7.5, streak=10, growth_streak=2),
        "expect_status": "PASS",
        "expect_signals_in": ["NIWES_5555"],
        "expect_signals_not_in": ["NIWES_GROWING"],
    },
    {
        "name": "2. Exception PASS (yield 3.0, growth_streak 5)",
        "data": _make_fixture(dy=3.0, streak=8, growth_streak=5),
        "expect_status": "PASS",
        "expect_signals_in": ["NIWES_GROWING"],
        "expect_signals_not_in": ["NIWES_5555"],
    },
    {
        "name": "3. Exception FAIL (yield 3.0, growth_streak 2 — not enough)",
        "data": _make_fixture(dy=3.0, streak=8, growth_streak=2),
        "expect_status": "FAIL",
        "expect_reason_contains": "growing exception not met",
    },
    {
        "name": "4. Low-streak regression PASS (yield 6.0, streak 2 — was FAIL before)",
        "data": _make_fixture(dy=6.0, streak=2, growth_streak=1),
        "expect_status": "PASS",
    },
    {
        "name": "5. Yield-spike signal (yield 8.0, 5y_avg 4.0)",
        "data": _make_fixture(dy=8.0, streak=10, growth_streak=2, yield_5y=4.0),
        "expect_signals_in": ["YIELD_SPIKE_FROM_PRICE_DROP"],
    },
]


def _run():
    failures = []
    for case in CASES:
        data = case["data"]
        status, reasons = hard_filter(data)
        signals = assign_signals(data, total_score=70)
        ok = True
        notes = []
        if "expect_status" in case and status != case["expect_status"]:
            ok = False
            notes.append(f"status={status} expected={case['expect_status']}")
        if "expect_reason_contains" in case:
            joined = " | ".join(reasons)
            if case["expect_reason_contains"] not in joined:
                ok = False
                notes.append(f"reasons={joined!r} missing {case['expect_reason_contains']!r}")
        for sig in case.get("expect_signals_in", []):
            if sig not in signals:
                ok = False
                notes.append(f"signal {sig!r} missing (signals={signals})")
        for sig in case.get("expect_signals_not_in", []):
            if sig in signals:
                ok = False
                notes.append(f"signal {sig!r} should NOT be present (signals={signals})")
        label = "[PASS]" if ok else "[FAIL]"
        print(f"{label} {case['name']}")
        if notes:
            for n in notes:
                print(f"       - {n}")
        if not ok:
            failures.append(case["name"])
    print()
    if failures:
        print(f"[FAIL] {len(failures)} case(s) failed: {failures}")
        sys.exit(1)
    print(f"[PASS] all {len(CASES)} cases passed")
    sys.exit(0)


if __name__ == "__main__":
    _run()
```
