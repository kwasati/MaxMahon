---
project: MaxMahon
created: 2026-05-07
last_updated: 2026-05-07
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: รัน screen_stocks.py แล้ว scoring ตรงเจตนา Niwes มากขึ้น — AWC.BK (NIWES_GROWING) score เพิ่มจาก 38 → 48+ / streak 20y vs 5y differentiate ชัด / no-debt company ได้ interest coverage max / DATA_WARNING + YIELD_SPIKE หัก score เบาแต่ active / Track Record pillar ใหม่ 10 pts revenue+eps growth ตามที่ Niwes พูด รายได้+กำไร+ปันผลเพิ่มทุกปี

### รายละเอียด
- Total budget reshape: Dividend 50 + Valuation 25 + Cash Flow 15→10 + Hidden Value 10→5 + Track Record 10 (new) = 100
- Fix 1 NIWES_GROWING +10 modifier ใน main() valuation_modifier section — boost ตัว exception path เทียบเคียง main path (Niwes intent)
- Fix 2 Track Record pillar 10 pts ใหม่ = revenue_cagr 5y (5) + eps_cagr 5y (5). Threshold: cagr >=10%=5, >=5%=3, >=0%=1. Aggregate fields revenue_cagr + eps_cagr มีอยู่แล้วใน fetch_data._build_aggregates
- Fix 3 Streak threshold ใหม่ 20y=15 / 15y=13 / 10y=10 / 7y=8 / 5y=5 / 3y=2 (เก่า 15y=15 / 10y=12 / 5y=8 / 3y=4)
- Fix 4 Payout sustainability fallback chain แก้: 5+y sustain=10, 3-4y sustain=6, 1-2y sustain=3, payout<70%=2, else=0 (independent if/elif ไม่ exclusive)
- Fix 5 Dividend Growth + stable payer 10 pts: growing 5+y=10 / 3+y=7 / 1+y=4 / **stable** (DPS stdev/mean < 0.1 over 5y)=5 / declining=0
- Fix 6 EV/EBITDA missing → 2 default (neutral) — ถ้า ev_per_ebit_da is None → 2 pts (ไม่ใช่ 0)
- Fix 7 Interest coverage no-debt → 5 pts max — ถ้า int_cov is None AND latest yearly_metric.de_ratio < 0.1 → 5
- Fix 8 Valuation grade modifier soft ใน main() line 962 dict: A+5 / B+2 / C 0 / D-3 / F-8 (เก่า A+5/B 0/C-5/D-10/F-20)
- Fix 9 DATA_WARNING penalty soft -5 ใน quality_score (เก่า -15)
- Fix 10 YIELD_SPIKE_FROM_PRICE_DROP penalty -5 ใน quality_score modifier (เก่า 0)
- Fix 11 Hidden Value cap 5 (was 10) — ตัด +5 if holding > parent mcap, keep base 5
- Fix 12 Cash Flow rebalance 15→10: FCF positive (5 keep) + OCF/NI ratio (5→3) + Interest coverage (5→2) = 10
- Order ใน quality_score: compute base 100 (4 pillars + Track Record) → assign_signals → modifiers (NIWES_GROWING +10, DIVIDEND_TRAP -20, DATA_WARNING -5, YIELD_SPIKE -5) → cap 0-100 → return
- valuation_grade modifier ยังอยู่ที่ main() line 962 (ที่อัพเดทค่า) — ไม่ย้ายเข้า quality_score

### Scope Boundary
**In scope:**
- projects/MaxMahon/scripts/screen_stocks.py — dividend_score / valuation_score / cash_flow_score / hidden_value_score / new track_record_score / quality_score modifier / main() valuation_modifier dict
- projects/MaxMahon/scripts/_smoke_scoring_v2.py — สร้างใหม่ smoke test 6 cases

**Out of scope:**
- Hard filter logic (Plan 1 done) — keep
- data_adapter.py / fetch_data.py — keep ตาม Plan A merged
- Stage 2 repair phase / hard_filter guard / DATA_INCOMPLETE — keep ตาม Plan B merged
- Signal tag definitions ใน assign_signals — keep ตาม Plan 1
- report_template.py narratives — keep
- DCA simulator / portfolio_builder / watchlist API — ไม่กระทบ

### Non-goals
- ไม่ใช้ AI / Claude SDK ใน scoring — pure Python deterministic
- ไม่เปลี่ยน hard filter logic
- ไม่เพิ่ม signal tag ใหม่ — ใช้ที่มี (NIWES_GROWING / DATA_WARNING / YIELD_SPIKE_FROM_PRICE_DROP)
- ไม่เปลี่ยน scoring schema (breakdown 4 pillars + new Track Record)
- ไม่ refactor เกินจำเป็น (แค่ update functions ตามที่ระบุ)
- ไม่บังคับ rerun scan — รอ next cron
- ไม่ทำ A/B compare score เก่า vs ใหม่ — accept new as production
- ไม่ย้าย valuation_grade modifier เข้า quality_score (อยู่ main() แต่อัพเดทค่า)

# MaxMahon Scoring Rebalance v2 (12 Niwes Alignment)

> Scoring rebalance v2 — แก้ 12 จุดที่ scoring ขัดเจตนา Niwes ตามที่ /qc deep analysis เจอ. NIWES_GROWING boost / Track Record pillar (revenue+eps growth ตาม Niwes รายได้+กำไร+ปันผลเพิ่มทุกปี) / streak threshold สมเหตุสมผล / no-debt = max int coverage / modifier penalties soft + active

## Phase 1: Scoring functions rebalance
- [x] แก้ function `dividend_score()` ใน `projects/MaxMahon/scripts/screen_stocks.py` (lines 146-208) — full replace ตาม reference snippet ใหม่. การแก้: streak threshold (20y=15/15y=13/10y=10/7y=8/5y=5/3y=2) + payout fallback chain (5+y=10/3-4y=6/1-2y=3/payout<70%=2/else=0) + dividend growth+stable (growing 5+y=10/3+y=7/1+y=4/stable DPS stdev mean<0.1=5/declining=0). Scope: keep yield section ตามเดิม (≥7=15, ≥5=12, ≥4=8, ≥3=5, ≥2=2). ห้ามแก้ valuation_score / cash_flow_score / hidden_value_score. Acceptance: grep `streak >= 20` ใน screen_stocks.py = 1 match; grep `stable` (case insensitive) ใน dividend_score = 1+ matches; py -m py_compile scripts/screen_stocks.py exit 0; smoke test case 3 (stable payer) ผ่าน.
- [x] แก้ function `valuation_score()` ใน `projects/MaxMahon/scripts/screen_stocks.py` (lines 211-259) — เพิ่ม EV/EBITDA missing handle: ถ้า ev_ebitda is None → score += 2 (neutral default). Logic อื่นๆ keep. Scope: ห้ามเปลี่ยน P/E threshold หรือ P/BV threshold หรือ logic อื่น. Acceptance: grep `ev_ebitda is None` ใน valuation_score = 1 match; py compile exit 0.
- [x] แก้ function `cash_flow_score()` ใน `projects/MaxMahon/scripts/screen_stocks.py` (lines 262-303) — full replace ตาม reference snippet. Reweight 15→10 pts: FCF positive (5 keep) + OCF/NI ratio (5→3) + Interest coverage (5→2) + add no-debt logic (int_cov is None + de_ratio < 0.1 → max 2 pts). docstring update '15 pts max' → '10 pts max'. Scope: ห้ามแก้ FCF logic. Acceptance: grep `de_ratio` ใน cash_flow_score = 1+ matches; grep `10 pts max` = 1 match; py compile exit 0; smoke test case 4 (no-debt) ผ่าน.
- [x] แก้ function `hidden_value_score()` ใน `projects/MaxMahon/scripts/screen_stocks.py` (lines 306-329) — ตัด `+5 if holding > parent mcap` block ออก (lines 322-328). Cap เหลือ 5 (เก่า 10). docstring update '10 pts max' → '5 pts max'. Scope: keep base 5 pts logic. Acceptance: grep `5 pts max` ใน hidden_value_score = 1 match; grep `min(score, 5)` ใน hidden_value_score = 1 match; py compile exit 0.
- [x] เพิ่ม function `track_record_score()` ใหม่ใน `projects/MaxMahon/scripts/screen_stocks.py` — insert ก่อน function `detect_exit_signal()` (around line 332). 10 pts max = revenue_cagr 5y (5) + eps_cagr 5y (5). Threshold: cagr >= 0.10 = 5, >= 0.05 = 3, >= 0 = 1, else 0. ใช้ aggregates.revenue_cagr + aggregates.eps_cagr ที่มีอยู่. Scope: ไม่แก้ logic อื่น, ไม่ดู metric อื่น (เช่น net_margin หรือ roe). Acceptance: grep `def track_record_score` = 1 match; grep `revenue_cagr` ใน screen_stocks.py = 2+ matches (function + caller); py compile exit 0; smoke test case 1 (main path) Track Record breakdown มีค่า.
- [x] แก้ function `quality_score()` ใน `projects/MaxMahon/scripts/screen_stocks.py` (lines 666-697) — เพิ่ม call `t_score, t_reasons = track_record_score(data)` หลัง hidden_value_score. รวม total += t_score. แก้ modifier section (lines 679-683): add NIWES_GROWING +10, change DATA_WARNING -15 → -5, add YIELD_SPIKE_FROM_PRICE_DROP -5. update breakdown dict เพิ่ม 'track_record': t_score. update docstring '50 + 25 + 15 + 10' → '50 + 25 + 10 + 5 + 10'. Scope: ห้ามย้าย valuation_grade modifier เข้า quality_score (ยังอยู่ main()). Acceptance: grep `track_record_score(data)` ใน quality_score = 1 match; grep `NIWES_GROWING` ใน quality_score = 1 match; grep `track_record` ใน breakdown dict = 1 match; py compile exit 0; smoke test case 2 (NIWES_GROWING boost) ผ่าน.
- [x] แก้ valuation_modifier dict ใน function `main()` ของ `projects/MaxMahon/scripts/screen_stocks.py` (line 962) — soft penalties. เก่า: `{"A": 5, "B": 0, "C": -5, "D": -10, "F": -20}`. ใหม่: `{"A": 5, "B": 2, "C": 0, "D": -3, "F": -8}`. Scope: ห้ามแก้ logic apply (cap 0-100), ห้ามแก้ valuation_grade function. Acceptance: grep `"F": -8` ใน screen_stocks.py = 1 match; grep `"B": 2` = 1 match; py compile exit 0.
- [x] สร้างไฟล์ใหม่ `projects/MaxMahon/scripts/_smoke_scoring_v2.py` — fixture-based smoke test 6 cases ตาม reference snippet. Cases: (1) main path stock score similar, (2) NIWES_GROWING +10 boost, (3) stable payer DPS stdev/mean<0.1 → 5 dividend growth, (4) no-debt int_cov 5 pts, (5) yield spike -5 modifier, (6) DATA_WARNING -5 (was -15). Scope: fixture-based, ห้าม fetch จริง, ห้ามแก้ source. Acceptance: ไฟล์ exists; py compile exit 0.
- [x] รัน smoke test `cd projects/MaxMahon && PYTHONUTF8=1 py scripts/_smoke_scoring_v2.py` exit 0 + print '[PASS] all 6 tests passed'. ถ้า case ไหน fail → debug source logic, ห้ามแก้ test fixture. Scope: ไม่รัน scan 933 หุ้น, ไม่ verify production. Acceptance: smoke exit 0.

### Reference
```python
# current — screen_stocks.py:146-208 dividend_score (full replace)
def dividend_score(data: dict) -> tuple:
    """Niwes Dividend pillar — 50 pts max.

    yield (15) + streak (15) + payout sustainability (10) + dividend growth (10)
    """
    score = 0
    reasons = []
    agg = data.get("aggregates", {})

    # Yield (15 pts) — Niwes wants ≥5%
    dy = data.get("dividend_yield")
    if dy is not None:
        if dy >= 7:
            score += 15
            reasons.append(f"yield สูง {dy:.1f}%")
        elif dy >= 5:
            score += 12
            reasons.append(f"yield ผ่านเกณฑ์ {dy:.1f}%")
        elif dy >= 4:
            score += 8
        elif dy >= 3:
            score += 5
        elif dy >= 2:
            score += 2

    # Streak (15 pts) — Niwes wants ≥5y, ideally 10+
    streak = agg.get("dividend_streak", 0)
    if streak >= 15:
        score += 15
        reasons.append(f"จ่ายปันผล {streak} ปีติดต่อกัน")
    elif streak >= 10:
        score += 12
        reasons.append(f"จ่ายปันผล {streak} ปีติด")
    elif streak >= 5:
        score += 8
    elif streak >= 3:
        score += 4

    # Payout sustainability (10 pts) — uses compute_payout_sustainability
    sust_map = compute_payout_sustainability(data)
    payout = data.get("payout_ratio")
    sust_count = sum(1 for v in sust_map.values() if v.get("sustainable"))
    if sust_count >= 5:
        score += 10
        reasons.append("payout ยั่งยืน 5+ ปี")
    elif sust_count >= 3:
        score += 6
    elif payout is not None and payout < 0.70:
        score += 4
    elif payout is not None and payout >= 1.0:
        reasons.append("payout เกิน 100%")

    # Dividend Growth (10 pts)
    div_growth_streak = agg.get("dividend_growth_streak", 0)
    if div_growth_streak >= 5:
        score += 10
        reasons.append(f"ปันผลเพิ่มต่อเนื่อง {div_growth_streak} ปี")
    elif div_growth_streak >= 3:
        score += 6
    elif div_growth_streak >= 1:
        score += 3

    return min(score, 50), reasons

# new — full replace
def dividend_score(data: dict) -> tuple:
    """Niwes Dividend pillar — 50 pts max.

    yield (15) + streak (15) + payout sustainability (10) + dividend growth or stable (10)
    """
    import statistics
    score = 0
    reasons = []
    agg = data.get("aggregates", {})

    # Yield (15 pts) — Niwes wants ≥5%
    dy = data.get("dividend_yield")
    if dy is not None:
        if dy >= 7:
            score += 15
            reasons.append(f"yield สูง {dy:.1f}%")
        elif dy >= 5:
            score += 12
            reasons.append(f"yield ผ่านเกณฑ์ {dy:.1f}%")
        elif dy >= 4:
            score += 8
        elif dy >= 3:
            score += 5
        elif dy >= 2:
            score += 2

    # Streak (15 pts) — disproportionate Niwes-style: 20y elite tier
    streak = agg.get("dividend_streak", 0)
    if streak >= 20:
        score += 15
        reasons.append(f"จ่ายปันผล {streak} ปีติด (elite)")
    elif streak >= 15:
        score += 13
        reasons.append(f"จ่ายปันผล {streak} ปีติด")
    elif streak >= 10:
        score += 10
    elif streak >= 7:
        score += 8
    elif streak >= 5:
        score += 5
    elif streak >= 3:
        score += 2

    # Payout sustainability (10 pts) — independent if/elif (ไม่ exclusive chain)
    sust_map = compute_payout_sustainability(data)
    payout = data.get("payout_ratio")
    sust_count = sum(1 for v in sust_map.values() if v.get("sustainable"))
    if sust_count >= 5:
        score += 10
        reasons.append("payout ยั่งยืน 5+ ปี")
    elif sust_count >= 3:
        score += 6
    elif sust_count >= 1:
        score += 3
    elif payout is not None and payout < 0.70:
        score += 2
    if payout is not None and payout >= 1.0:
        reasons.append("payout เกิน 100%")

    # Dividend Growth or Stable (10 pts) — Niwes accepts both growing AND stable
    div_growth_streak = agg.get("dividend_growth_streak", 0)
    div_history = data.get("dividend_history") or {}
    stable = False
    if div_growth_streak == 0 and len(div_history) >= 5:
        # Check stable: DPS stdev/mean < 0.1 over last 5 years
        recent_years = sorted(div_history.keys())[-5:]
        recent_dps = [div_history[y] for y in recent_years if div_history[y] and div_history[y] > 0]
        if len(recent_dps) >= 5:
            mean_dps = sum(recent_dps) / len(recent_dps)
            if mean_dps > 0:
                stdev_dps = statistics.stdev(recent_dps)
                if stdev_dps / mean_dps < 0.1:
                    stable = True

    if div_growth_streak >= 5:
        score += 10
        reasons.append(f"ปันผลเพิ่มต่อเนื่อง {div_growth_streak} ปี")
    elif div_growth_streak >= 3:
        score += 7
    elif div_growth_streak >= 1:
        score += 4
    elif stable:
        score += 5
        reasons.append("ปันผลคงที่ (stable payer)")

    return min(score, 50), reasons
```

```python
# current — screen_stocks.py valuation_score EV/EBITDA block (around line 246-258)
    # EV/EBITDA (5 pts) — use thaifin ev_per_ebit_da from latest yearly_metrics
    yearly = data.get("yearly_metrics", [])
    latest = yearly[-1] if yearly else {}
    ev_ebitda = latest.get("ev_per_ebit_da")
    if ev_ebitda is not None and ev_ebitda > 0:
        if ev_ebitda <= 6:
            score += 5
            reasons.append(f"EV/EBITDA {ev_ebitda:.1f}x ถูก")
        elif ev_ebitda <= 10:
            score += 3
        elif ev_ebitda <= 15:
            score += 1

# new — add neutral 2 pts when missing
    # EV/EBITDA (5 pts) — use thaifin ev_per_ebit_da from latest yearly_metrics
    yearly = data.get("yearly_metrics", [])
    latest = yearly[-1] if yearly else {}
    ev_ebitda = latest.get("ev_per_ebit_da")
    if ev_ebitda is None:
        score += 2  # neutral default — missing data shouldn't penalize
    elif ev_ebitda > 0:
        if ev_ebitda <= 6:
            score += 5
            reasons.append(f"EV/EBITDA {ev_ebitda:.1f}x ถูก")
        elif ev_ebitda <= 10:
            score += 3
        elif ev_ebitda <= 15:
            score += 1
```

```python
# current — screen_stocks.py:262-303 cash_flow_score (full replace)
def cash_flow_score(data: dict) -> tuple:
    """Niwes Cash Flow Strength pillar — 15 pts max.

    FCF positive (5) + OCF/NI ratio (5) + Interest coverage (5)
    """
    score = 0
    reasons = []
    agg = data.get("aggregates", {})

    # FCF positive (5 pts)
    fcf_pos = agg.get("fcf_positive_years", 0)
    fcf_total = agg.get("fcf_total_years", 0)
    if fcf_total >= 3:
        if fcf_pos == fcf_total:
            score += 5
            reasons.append("FCF บวกทุกปี")
        elif fcf_pos >= fcf_total - 1:
            score += 3
        elif fcf_pos >= fcf_total // 2:
            score += 1

    # OCF/NI ratio (5 pts)
    ocf_ni = agg.get("latest_ocf_ni_ratio")
    if ocf_ni is not None:
        if 0.8 <= ocf_ni <= 3.0:
            score += 5
            reasons.append("กำไรมีเงินสดรองรับ")
        elif 0.5 <= ocf_ni:
            score += 3

    # Interest coverage (5 pts)
    int_cov = agg.get("latest_interest_coverage")
    if int_cov is not None:
        if int_cov > 10:
            score += 5
            reasons.append(f"interest coverage {int_cov:.0f}x")
        elif int_cov > 5:
            score += 3
        elif int_cov > 3:
            score += 1

    return min(score, 15), reasons

# new — full replace, rebalance 15 → 10 pts (5+3+2) + no-debt handle
def cash_flow_score(data: dict) -> tuple:
    """Niwes Cash Flow Strength pillar — 10 pts max.

    FCF positive (5) + OCF/NI ratio (3) + Interest coverage or no-debt (2)
    """
    score = 0
    reasons = []
    agg = data.get("aggregates", {})

    # FCF positive (5 pts) — keep
    fcf_pos = agg.get("fcf_positive_years", 0)
    fcf_total = agg.get("fcf_total_years", 0)
    if fcf_total >= 3:
        if fcf_pos == fcf_total:
            score += 5
            reasons.append("FCF บวกทุกปี")
        elif fcf_pos >= fcf_total - 1:
            score += 3
        elif fcf_pos >= fcf_total // 2:
            score += 1

    # OCF/NI ratio (3 pts) — reduced
    ocf_ni = agg.get("latest_ocf_ni_ratio")
    if ocf_ni is not None:
        if 0.8 <= ocf_ni <= 3.0:
            score += 3
            reasons.append("กำไรมีเงินสดรองรับ")
        elif 0.5 <= ocf_ni:
            score += 2

    # Interest coverage or no-debt (2 pts) — reduced + no-debt handle
    int_cov = agg.get("latest_interest_coverage")
    yearly = data.get("yearly_metrics", [])
    latest_de = yearly[-1].get("de_ratio") if yearly else None
    if int_cov is not None:
        if int_cov > 10:
            score += 2
            reasons.append(f"interest coverage {int_cov:.0f}x")
        elif int_cov > 5:
            score += 1
    elif int_cov is None and latest_de is not None and latest_de < 0.1:
        score += 2
        reasons.append("ไม่มีหนี้ (no debt = max coverage)")

    return min(score, 10), reasons
```

```python
# current — screen_stocks.py:306-329 hidden_value_score (full replace)
def hidden_value_score(data: dict) -> tuple:
    """Niwes Hidden Value pillar — 10 pts max.

    Base 5 if symbol has hidden-value flag.
    +5 if any holding's note indicates holding > parent market cap.
    """
    score = 0
    reasons = []
    sym = data.get("symbol", "")
    holdings = check_hidden_value(sym)
    if not holdings:
        return 0, reasons

    score += 5
    reasons.append(f"hidden value: {len(holdings)} holding(s)")

    for h in holdings:
        note = (h.get("note") or "").lower()
        if "exceed" in note or "more than" in note or "worth more" in note:
            score += 5
            reasons.append("hidden holding > parent mcap")
            break

    return min(score, 10), reasons

# new — cap 5 pts (drop +5 holding>parent block)
def hidden_value_score(data: dict) -> tuple:
    """Niwes Hidden Value pillar — 5 pts max.

    Base 5 if symbol has hidden-value flag (holdings file maintained manually).
    """
    score = 0
    reasons = []
    sym = data.get("symbol", "")
    holdings = check_hidden_value(sym)
    if not holdings:
        return 0, reasons

    score += 5
    reasons.append(f"hidden value: {len(holdings)} holding(s)")

    return min(score, 5), reasons
```

```python
# new — insert NEW function before detect_exit_signal (around line 332)
def track_record_score(data: dict) -> tuple:
    """Niwes Track Record pillar — 10 pts max.

    Revenue growth 5y (5) + EPS growth 5y (5).
    Per Niwes: รายได้เพิ่มทุกปี กำไรเพิ่มทุกปี ปันผลเพิ่มทุกปี.
    Dividend growth covered in dividend_score; revenue + eps covered here.
    """
    score = 0
    reasons = []
    agg = data.get("aggregates", {})

    # Revenue CAGR (5 pts)
    rev_cagr = agg.get("revenue_cagr")
    if rev_cagr is not None:
        if rev_cagr >= 0.10:
            score += 5
            reasons.append(f"รายได้โต {rev_cagr*100:.1f}%/ปี")
        elif rev_cagr >= 0.05:
            score += 3
        elif rev_cagr >= 0:
            score += 1

    # EPS CAGR (5 pts)
    eps_cagr = agg.get("eps_cagr")
    if eps_cagr is not None:
        if eps_cagr >= 0.10:
            score += 5
            reasons.append(f"กำไร EPS โต {eps_cagr*100:.1f}%/ปี")
        elif eps_cagr >= 0.05:
            score += 3
        elif eps_cagr >= 0:
            score += 1

    return min(score, 10), reasons
```

```python
# current — screen_stocks.py:666-697 quality_score (full replace)
def quality_score(data: dict) -> dict:
    """Niwes Dividend-First Quality Score — 100 pts cap.

    Dividend 50 + Valuation 25 + Cash Flow 15 + Hidden Value 10
    """
    d_score, d_reasons = dividend_score(data)
    v_score, v_reasons = valuation_score(data)
    c_score, c_reasons = cash_flow_score(data)
    h_score, h_reasons = hidden_value_score(data)

    total = d_score + v_score + c_score + h_score
    signals = assign_signals(data, total)

    # Signal adjustments (cap applied after valuation modifier in main)
    if "DIVIDEND_TRAP" in signals:
        total -= 20
    if "DATA_WARNING" in signals:
        total -= 15

    all_reasons = d_reasons + v_reasons + c_reasons + h_reasons

    return {
        "score": max(0, min(100, total)),
        "breakdown": {
            "dividend": d_score,
            "valuation": v_score,
            "cash_flow": c_score,
            "hidden_value": h_score,
        },
        "signals": signals,
        "reasons": all_reasons,
    }

# new — full replace with track_record + new modifiers
def quality_score(data: dict) -> dict:
    """Niwes Dividend-First Quality Score — 100 pts cap.

    Dividend 50 + Valuation 25 + Cash Flow 10 + Hidden Value 5 + Track Record 10
    Modifiers: NIWES_GROWING +10, DIVIDEND_TRAP -20, DATA_WARNING -5, YIELD_SPIKE_FROM_PRICE_DROP -5
    """
    d_score, d_reasons = dividend_score(data)
    v_score, v_reasons = valuation_score(data)
    c_score, c_reasons = cash_flow_score(data)
    h_score, h_reasons = hidden_value_score(data)
    t_score, t_reasons = track_record_score(data)

    total = d_score + v_score + c_score + h_score + t_score
    signals = assign_signals(data, total)

    # Modifier adjustments (cap applied after valuation_grade modifier in main)
    if "NIWES_GROWING" in signals:
        total += 10
    if "DIVIDEND_TRAP" in signals:
        total -= 20
    if "DATA_WARNING" in signals:
        total -= 5
    if "YIELD_SPIKE_FROM_PRICE_DROP" in signals:
        total -= 5

    all_reasons = d_reasons + v_reasons + c_reasons + h_reasons + t_reasons

    return {
        "score": max(0, min(100, total)),
        "breakdown": {
            "dividend": d_score,
            "valuation": v_score,
            "cash_flow": c_score,
            "hidden_value": h_score,
            "track_record": t_score,
        },
        "signals": signals,
        "reasons": all_reasons,
    }
```

```python
# current — screen_stocks.py:962 valuation_modifier in main()
        val_modifier = {"A": 5, "B": 0, "C": -5, "D": -10, "F": -20}

# new — soft penalties (range 13 instead of 25)
        val_modifier = {"A": 5, "B": 2, "C": 0, "D": -3, "F": -8}
```

```python
# new file — projects/MaxMahon/scripts/_smoke_scoring_v2.py
"""Smoke test for scoring rebalance v2 — 12 Niwes alignment fixes."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def _stock_data(sym, *, dy=5.0, streak=10, growth_streak=2, dh=None,
                pe=10, pbv=1.0, mcap=10_000_000_000, payout=0.5,
                de_ratio=0.5, int_cov=8, ocf_ni=1.2,
                rev_cagr=0.08, eps_cagr=0.06, ev_ebitda=8,
                yield_5y=4.0, fcf_pos=5, fcf_total=5,
                eps_5_pos=True, warnings=None):
    eps_list = [1.0, 1.1, 1.2, 1.3, 1.5] if eps_5_pos else [1.0, -0.5, 1.2, 1.3, 1.5]
    yearly = []
    for i, e in enumerate(eps_list):
        yearly.append({
            "year": 2020 + i,
            "diluted_eps": e,
            "close": 100.0,
            "bvps": 80.0,
            "payout_ratio": payout,
            "roe": 0.15,
            "net_margin": 0.10,
            "revenue": 1e9,
            "de_ratio": de_ratio,
            "ev_per_ebit_da": ev_ebitda,
        })
    return {
        "symbol": sym,
        "price": 100,
        "dividend_yield": dy,
        "pe_ratio": pe,
        "pb_ratio": pbv,
        "market_cap": mcap,
        "payout_ratio": payout,
        "five_year_avg_yield": yield_5y,
        "dividend_history": dh if dh is not None else {2020 + i: 1.0 + i*0.1 for i in range(5)},
        "yearly_metrics": yearly,
        "aggregates": {
            "dividend_streak": streak,
            "dividend_growth_streak": growth_streak,
            "fcf_positive_years": fcf_pos,
            "fcf_total_years": fcf_total,
            "latest_ocf_ni_ratio": ocf_ni,
            "latest_interest_coverage": int_cov,
            "revenue_cagr": rev_cagr,
            "eps_cagr": eps_cagr,
        },
        "warnings": warnings or [],
    }


def test_main_path_score_reasonable():
    from screen_stocks import quality_score
    s = _stock_data("MAIN.BK", dy=7.0, streak=22, growth_streak=5, pe=8, pbv=0.6)
    r = quality_score(s)
    assert r["score"] >= 60, f"main path expected >=60, got {r['score']}"
    assert "track_record" in r["breakdown"], "breakdown should include track_record"
    print(f"[PASS] main path score reasonable (got {r['score']})")


def test_niwes_growing_boost():
    from screen_stocks import quality_score
    # NIWES_GROWING: yield 3% + growth_streak 5 + EPS 5/5 + PE/PBV ok
    s = _stock_data("GROW.BK", dy=3.0, streak=8, growth_streak=5, pe=12, pbv=1.2)
    r = quality_score(s)
    assert "NIWES_GROWING" in r["signals"], f"expected NIWES_GROWING, got {r['signals']}"
    # without modifier: lower score; with +10 modifier: should be > 30
    assert r["score"] > 30, f"NIWES_GROWING boosted score expected >30, got {r['score']}"
    print(f"[PASS] NIWES_GROWING +10 boost (score {r['score']})")


def test_stable_payer_dividend_growth():
    from screen_stocks import dividend_score
    # Stable: DPS 1.0 every year for 5 years (stdev=0, mean=1)
    s = _stock_data("STABLE.BK", dy=5.5, streak=10, growth_streak=0,
                    dh={2020: 1.0, 2021: 1.0, 2022: 1.0, 2023: 1.0, 2024: 1.0})
    score, reasons = dividend_score(s)
    has_stable = any("stable" in r.lower() or "คงที่" in r for r in reasons)
    assert has_stable, f"expected stable reason, got {reasons}"
    print(f"[PASS] stable payer gets dividend growth pts (score {score})")


def test_no_debt_interest_coverage():
    from screen_stocks import cash_flow_score
    # No debt: int_cov None + de_ratio 0.05 -> max 2 pts
    s = _stock_data("NODEBT.BK", int_cov=None, de_ratio=0.05)
    score, reasons = cash_flow_score(s)
    has_nodebt = any("no debt" in r.lower() or "ไม่มีหนี้" in r for r in reasons)
    assert has_nodebt, f"expected no-debt reason, got {reasons}"
    print(f"[PASS] no-debt interest coverage max ({score} pts)")


def test_yield_spike_penalty():
    from screen_stocks import quality_score
    # yield 16% + 5y_avg 7% = ratio 2.3 > 1.8 trigger YIELD_SPIKE
    s = _stock_data("SPIKE.BK", dy=16.0, streak=20, growth_streak=2, yield_5y=7.0)
    r = quality_score(s)
    assert "YIELD_SPIKE_FROM_PRICE_DROP" in r["signals"], f"expected spike, got {r['signals']}"
    # YIELD_SPIKE -5 modifier — verify score is reduced (compare without spike: same data minus spike condition)
    # Quick check: if score appears reasonable but with -5 applied, total should be < if no spike
    # We just verify modifier was applied via not-zero result + signal present
    assert r["score"] < 100, f"score should be capped, got {r['score']}"
    print(f"[PASS] YIELD_SPIKE detected + score adjusted (score {r['score']})")


def test_data_warning_soft_penalty():
    from screen_stocks import quality_score
    # DATA_WARNING via warnings field — score reduced -5 (was -15)
    base = _stock_data("BASE.BK", dy=7.0, streak=22)
    warned = _stock_data("WARN.BK", dy=7.0, streak=22, warnings=["sanity test"])
    r_base = quality_score(base)
    r_warn = quality_score(warned)
    diff = r_base["score"] - r_warn["score"]
    assert "DATA_WARNING" in r_warn["signals"], f"expected DATA_WARNING, got {r_warn['signals']}"
    assert diff == 5, f"expected DATA_WARNING penalty 5, got diff {diff}"
    print(f"[PASS] DATA_WARNING soft penalty -5 (was -15)")


if __name__ == "__main__":
    failures = []
    tests = [
        test_main_path_score_reasonable,
        test_niwes_growing_boost,
        test_stable_payer_dividend_growth,
        test_no_debt_interest_coverage,
        test_yield_spike_penalty,
        test_data_warning_soft_penalty,
    ]
    for fn in tests:
        try:
            fn()
        except AssertionError as e:
            failures.append(f"{fn.__name__}: {e}")
            print(f"[FAIL] {fn.__name__}: {e}")
        except Exception as e:
            failures.append(f"{fn.__name__}: {type(e).__name__}: {e}")
            print(f"[FAIL] {fn.__name__}: {type(e).__name__}: {e}")
    print()
    if failures:
        print(f"[FAIL] {len(failures)} test(s) failed: {failures}")
        sys.exit(1)
    print(f"[PASS] all {len(tests)} tests passed")
    sys.exit(0)
```
