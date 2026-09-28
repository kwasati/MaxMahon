---
project: 4-MaxMahon
created: 2026-05-16
last_updated: 2026-05-18
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: ได้ formal spec ไฟล์ `projects/4-MaxMahon/docs/scoring-anchor-spec.md` ที่ระบุสูตรคะแนน anchor 100 pts ครบทุกตัวเลข (base per tier, bonus scale per metric, disqualify list, penalty amount) — โดยทุกตัวเลขผ่านการคุยกับอาร์ท + อาร์ท approve ก่อนเขียนลง spec — ไม่ใช่ AI ตัดสินใจฝ่ายเดียว

### รายละเอียด
- Plan นี้ = discussion checkpoint plan ไม่ใช่ agent implementation plan — main thread คุยกับอาร์ทใน chat ทีละด้าน
- แต่ละ phase = checkpoint discussion 1 ด้าน — เปิดประเด็น + ลิสต์ option ที่เป็นไปได้ (ไม่ใช่ AI ชี้ตัวเลข) + ถามอาร์ท + จดผลลง spec
- ทุกตัวเลขเริ่มเป็น TBD — base value, bonus scale, threshold ตัวเลข, disqualify list, penalty amount — AI ห้าม assume
- ลำดับ phase ตาม weight Niwes: ปันผล (35) -> Cash flow (25) -> Moat (25) -> ถือยาว (15) -> Disqualify list -> Verify -> Finalize
- Reference data ที่ใช้คุย: parent plan niwes-refactor-v2-design.md Stage 1-6 (tag rules + aggregates fields) + niwes book ch2-7 (quote หลัก) — เปิดให้ทั้งคู่อ่านก่อนคุย
- Output ต่อ phase: append section ลง docs/scoring-anchor-spec.md หลังอาร์ท approve
- Phase 5 disqualify list: ไม่ assume list ล่วงหน้า — ลิสต์ negative tag ทุกตัวจาก Stage 1-6 (มีเยอะกว่า 6 ตัว) แล้วคุยทีละป้ายว่า disqualify หรือ penalty
- Phase 6 verify: หลัง spec ครบ คำนวณคะแนน 5 หุ้น real (PTT/SCC/CPALL/ADVANC/BDMS) เทียบ Niwes intuition — ถ้า misalign กลับมาแก้ spec
- Plan นี้ใช้ /build ไม่ได้ตรงตัว (ไม่ใช่ agent task) — main thread เปิด phase แต่ละขั้น เป็น discussion checkpoint
- Reset state ของ session: ถ้าอาร์ทกลับมาวันใหม่ พูด 'ต่อ scoring discussion' -> เปิด plan ดู phase ที่ยังไม่ tick -> เริ่ม discussion ต่อ

### Scope Boundary
**In scope:**
- projects/4-MaxMahon/docs/scoring-anchor-spec.md (NEW) - formal spec ที่อาร์ท approve เนื้อหา
- Discussion + decision capture ทีละ phase ใน main thread chat
- Re-alignment กับ implementation plan scoring-redesign-config-refactor.md หลัง spec finalize

**Out of scope:**
- Code implementation (ทำต่อใน scoring-redesign-config-refactor.md)
- Agent dispatch (ไม่มี — main thread discussion ตลอด)
- Tail/supporting role score (anchor only)
- DCA signal logic (ขาที่ 2 designed in parent)
- Hidden value score (separate plan)

### Non-goals
- ไม่ AI ตัดสินใจตัวเลขให้อาร์ท — ทุกตัวเลขต้อง discuss + approve
- ไม่ assume disqualify list — ลิสต์ negative tag ทั้งหมดให้อาร์ทเลือก
- ไม่ verify universe เต็ม - 5 หุ้น sample พอ
- ไม่ใช้ linear interpolation - step function (ตรง Niwes language)
- ไม่ implement code ใน plan นี้

# Scoring Formula Discussion — ตกผลึกตัวเลข Anchor Score ทีละด้าน

> Discussion checkpoint plan — main thread คุยกับอาร์ทใน chat ทีละด้าน ตกผลึกตัวเลขสูตรคะแนน anchor ก่อนเขียนลง spec. ทุกตัวเลข TBD จนอาร์ท approve. Output = docs/scoring-anchor-spec.md ที่ implementation plan reference ได้

## Phase 1: คุยตัวเลขด้านปันผลต่อเนื่อง (weight 35) — FINAL 2026-05-16
- [x] เปิด discussion ด้านปันผลต่อเนื่อง — ระบุ tier ป้ายที่ออกแบบใน Stage 2 (GROWING_DIVIDEND / STABLE_PAYER / NEW_PAYER / INTERMITTENT) + metric ตัวเลขที่ใช้ขยาย (consecutive_no_cut ปี / dps_rising_ratio / dps_avg_yoy_growth / dps_5y_cagr / yield_current) + ROE trend (IMPROVING/STABLE/DECLINING orthogonal). ถามอาร์ท 4 ประเด็น: (1) base per tier เท่าไหร่ (รวมไม่เกิน 35 - ที่เหลือเก็บไว้ bonus), (2) เลือก metric ไหนมาเป็น bonus (เลือก 2-3 ตัวจาก list ไม่ใช่ทุกตัว), (3) step threshold ของ metric ที่เลือก (เช่น streak 10/15/20 หรือ 10/20 หรือ 10/15), (4) ROE trend modifier น้ำหนัก (+/- เท่าไหร่). หลังอาร์ท approve ตัวเลขครบทุกข้อ -> append section 'ด้าน 1 - ปันผลต่อเนื่อง' ลง docs/scoring-anchor-spec.md ระบุค่าทั้งหมด. — scope: ไม่เปิด discussion ด้านอื่น + ไม่ implement code + ไม่ assume ตัวเลขก่อนอาร์ทตอบ — Acceptance: section ในไฟล์ spec มี base table + bonus table + modifier table ที่มีค่าตัวเลขจริง (ไม่มี TBD/placeholder)

### Reference
Tier ป้าย Stage 2 (จาก parent plan section 2.4):

```
GROWING_DIVIDEND: consecutive_no_cut >=10y + rising_ratio >=70% + avg_yoy_growth >=3%
STABLE_PAYER:    consecutive_no_cut >=10y + (rising 40-70% OR growth 0-3%)
NEW_PAYER:       consecutive_no_cut 3-9y
INTERMITTENT:    consecutive <3y OR years_paid_in_10y <8
```

Metric aggregates ที่มีให้เลือกเป็น bonus:
- consecutive_no_cut (ปี)
- dps_rising_ratio (% transitions ที่ DPS เพิ่ม)
- dps_avg_yoy_growth (%/year)
- dps_5y_cagr (%)
- yield_current (% absolute)

ROE trend tag (Stage 2 orthogonal):
- ROE_IMPROVING / ROE_STABLE / ROE_DECLINING

Niwes ch3 anchor quote: 'ความสม่ำเสมอ 20 ปี มีน้ำหนักกว่า 12% ของปีเดียว เสมอ' (sign ที่ Niwes ให้น้ำหนัก streak มากกว่า yield absolute)

Open questions for อาร์ท:
- Q1: Base per tier - เช่น GROWING 20/STABLE 15/NEW 8/INTERMITTENT 0? หรือกระจายต่าง?
- Q2: เลือก metric ไหนเป็น bonus (เลือก 2-3 ตัว จาก streak/rising/growth/cagr/yield)
- Q3: Step threshold ของแต่ละ metric (กี่ step / ตัวเลข cutoff)
- Q4: ROE trend modifier (IMPROVING +0 / STABLE +1 / DECLINING -2? หรือต่าง?)

## Phase 2: คุยตัวเลขด้าน Cash Flow (weight 25)
- [x] เปิด discussion ด้าน Cash Flow — ระบุ tier ป้ายจาก Stage 3 (CASHFLOW_HEALTHY / CASHFLOW_OK / CASHFLOW_BELOW_PROFIT / FAKE_PROFIT / CASHFLOW_DETERIORATING) + metric (ccr_avg_3y / ccr_avg_5y / ocf_negative_count_3y / ocf_yoy_decline_pct). **Formula resolved 2026-05-17 = OCF/EBITDA (CCR)** — bypass minority interest issue, threshold 0.7/0.5 ตรง CCR industry standard. ถามอาร์ท 3 ประเด็น: (1) base per tier (รวมไม่เกิน 25), (2) เลือก metric ไหนเป็น bonus, (3) step threshold. หลัง approve -> append section 'ด้าน 2 - Cash Flow' ลง spec. — scope: ไม่เปิดด้านอื่น — Acceptance: section spec มีตัวเลขครบ
- [x] เปิด discussion penalty/disqualify ของ Stage 3 ป้าย - คุยทีละป้าย: (a) CASHFLOW_BELOW_PROFIT (Niwes ch4 'เริ่มระวัง') อาร์ทเลือก disqualify หรือ penalty? amount? (b) FAKE_PROFIT (Niwes ch4 'red flag ขายตั้งแต่ปีที่ 2') disqualify หรือ penalty?, (c) CASHFLOW_DETERIORATING (ลด >=20% magnitude) disqualify หรือ penalty? -> ตัดสินใจตัวนี้สำคัญ เพราะ CPALL ติด + อื่นๆ ดีหมด อาจ misalign Niwes intuition. หลัง approve -> append section 'Cash flow disqualify/penalty rules' ลง spec. — Acceptance: section ระบุการตัดสินของแต่ละป้าย 3 ตัว + reason quote Niwes

### Reference
Tier ป้าย Stage 3 (จาก parent plan section 2.5 — formula resolved 2026-05-17 = CCR):

```
CASHFLOW_HEALTHY:       OCF บวก 3 ปีติด + ccr_avg_3y >=0.70
CASHFLOW_OK:            OCF บวก 3 ปีติด + ccr_avg_3y 0.50-0.70
CASHFLOW_BELOW_PROFIT:  ccr_avg_3y <0.50 (>=2 ใน 3 ปีตก)
FAKE_PROFIT:            OCF ติดลบ >=1 ใน 3 ปี + NP บวก
CASHFLOW_DETERIORATING: OCF ลด >=2 transitions + magnitude <=-20%
```

Metrics: ccr_avg_3y, ccr_avg_5y, ocf_negative_count_3y, ocf_yoy_decline_pct, ocf_consecutive_declining_years (ccr = OCF/EBITDA, EBITDA computed from thaifin gp - sga + da)

Test 5 หุ้น 3y avg CCR (2026-05-17): PTT 0.87 / SCC 0.80 / CPALL 0.67 / ADVANC 0.96 / BDMS 0.91 — 4/5 HEALTHY + 1/5 OK (CPALL)

Niwes ch4 quotes:
- 'กำไรเป็นความเห็น แต่กระแสเงินสดคือข้อเท็จจริง'
- 'ถ้า OCF น้อยกว่า 50% ของ Net Profit = เริ่มระวัง' (CASHFLOW_BELOW_PROFIT context)
- 'ถ้า OCF ติดลบทั้งที่กำไรบวก = red flag ขายตั้งแต่ปีที่ 2' (FAKE_PROFIT context)

Open questions:
- Q1: base per tier
- Q2: metric ไหนเป็น bonus + step threshold
- Q3: CASHFLOW_BELOW_PROFIT - disqualify หรือ penalty? amount?
- Q4: FAKE_PROFIT - disqualify? (ดู Niwes ตรงไหม)
- Q5: CASHFLOW_DETERIORATING - disqualify หรือ penalty? CPALL test case จะ flag ตรงนี้

## Phase 3: คุยตัวเลขด้าน Moat (weight 25)
- [x] เปิด discussion ด้าน Moat - ระบุ tier ป้ายจาก Stage 4 (STRONG_MOAT / MODERATE_MOAT / NO_MOAT / MOAT_ERODING / ROE_FUELED_BY_DEBT) + metric (roe_consecutive_15plus_years / gm_trend / gm_recent_3y_avg / interest_coverage_4y_avg / net_debt_history_5y / net_debt_increases_in_3y / de_current). ถามอาร์ท 3 ประเด็น: (1) base per tier, (2) เลือก metric เป็น bonus (2-3 ตัว), (3) step threshold. — scope: ไม่คุย disqualify (อยู่ Phase 5 รวม) + ไม่เปิดด้านอื่น — Acceptance: section spec มี base table + bonus table

### Reference
Tier ป้าย Stage 4 (จาก parent plan section 2.6):

```
STRONG_MOAT:        ROE >=15% ติด >=7y + GM stable/improving
MODERATE_MOAT:      ROE 10-15% ติด >=5y + GM stable
NO_MOAT:            ROE ผันผวน/<10% + GM หดตัว
MOAT_ERODING:       ROE เคยสูง + ลด 3y + GM หดตัว
ROE_FUELED_BY_DEBT: ROE >=15% + D/E >2.0 + InterestCov <3 + Net Debt เพิ่ม >=2/3 trans
```

Metrics: roe_consecutive_15plus_years, gm_trend (improving/stable/declining), gm_recent_3y_avg, gm_earlier_3y_avg, interest_coverage_4y_avg, net_debt_history_5y, net_debt_increases_in_3y, de_current

Niwes ch5 quotes:
- 'ROE >=15% ติดต่อ 7-10 ปี = สัญญาณ moat ดีมาก'
- 'Gross Margin คงที่/ขยับขึ้น = pricing power ยัง intact'
- 'ROE สูงแต่หนี้ท่วมหัว นั่นไม่ใช่ moat แต่คือความเสี่ยง'

Open questions:
- Q1: base per tier
- Q2: ใช้ ROE consecutive years หรือ ROE level (15/20/25%) เป็น bonus?
- Q3: GM trend modifier - improving +X / stable +Y / declining -Z
- Q4: Interest coverage / net debt trend เป็น bonus หรือ informative tag

## Phase 4: คุยตัวเลขด้านถือยาว + ทนวิกฤต (weight 15)
- [x] เปิด discussion ด้านถือยาว - ระบุ tier ป้ายจาก Stage 5 (STABLE_BUSINESS / CYCLICAL_BUSINESS / MIXED_STABILITY / RESILIENT_THROUGH_CRISIS) + metric (eps_cv_10y / crisis_2011_drop_pct / crisis_2020_drop_pct). หมายเหตุ: aggregator NEAR_SELL/MULTIPLE_SELL ตัดทิ้งแล้วใน Phase 1 chat (อาร์ท ack ข้อ 2). ถามอาร์ท 3 ประเด็น: (1) base per tier (รวมไม่เกิน 15), (2) เลือก metric เป็น bonus, (3) step threshold + แยก base ของ RESILIENT vs STABLE_BUSINESS (ติดทั้ง 2 = base รวม). — scope: ไม่คุย sector mapping (parent plan Stage 5 FINAL แล้ว) — Acceptance: section spec มี base + bonus

### Reference
Tier ป้าย Stage 5 (จาก parent plan section 2.7):

```
STABLE_BUSINESS:           (sector in STABLE OR symbol in STABLE_UTILITY) + eps_cv_10y <=30%
CYCLICAL_BUSINESS:         sector in CYCLICAL OR eps_cv_10y >50%
MIXED_STABILITY:           ไม่อยู่ทั้ง 2
RESILIENT_THROUGH_CRISIS:  crisis_2011_drop >=-40% + ocf_2011 >0 + crisis_2020_drop >=-40% + ocf_2020 >0
```

[TRIMMED ใน Phase 1 chat]: NEAR_SELL_TRIGGER + MULTIPLE_SELL_TRIGGERS aggregator - overlap กับ disqualify รายป้าย ไม่ใช้ scoring

Metrics: eps_cv_10y, eps_mean_10y, crisis_2011_drop_pct, crisis_2020_drop_pct, ocf_2011, ocf_2020

Niwes ch6 quote: 'เวลา คือผลตอบแทนที่คุณได้ฟรี ตราบเท่าที่คุณไม่ขายทิ้ง'

Open questions:
- Q1: base STABLE_BUSINESS vs RESILIENT - แยกกันแบบไหน (เช่น 5+5 หรือ 6+4 หรือต่าง)
- Q2: CYCLICAL ได้คะแนนติดลบไหม หรือแค่ 0
- Q3: bonus eps_cv step threshold (30/20/15/10 หรือต่าง)
- Q4: bonus crisis drop magnitude step threshold (-40/-25/-10/0 หรือต่าง)

## Phase 5: ลิสต์ป้ายฝ่ายเสีย + คุยทีละป้ายว่า disqualify หรือ penalty
- [x] ลิสต์ป้าย negative ทั้งหมดจาก Stage 1-6 (จาก parent plan) - ครอบทุกตัวที่ยังไม่ได้ตัดสินใน Phase 1-4. ลิสต์ประมาณ 10-12 ป้าย: DIVIDEND_SHRINKING (Stage 2), YIELD_TRAP (Stage 2), ROE_DECLINING (Stage 2 orthogonal), FAKE_PROFIT (Stage 3), CASHFLOW_BELOW_PROFIT (Stage 3 - Phase 2 ตัดสินแล้ว), CASHFLOW_DETERIORATING (Stage 3 - Phase 2 ตัดสินแล้ว), MOAT_ERODING (Stage 4), ROE_FUELED_BY_DEBT (Stage 4), NO_MOAT (Stage 4), CYCLICAL_BUSINESS (Stage 4 - Phase 4 base 0), OVERVALUED_VS_SELF (Stage 1 - แต่ราคา อยู่ขาที่ 2 ไม่ใช่ anchor). คุยทีละป้ายที่**ยังไม่ตัดสิน**: เลือก disqualify (anchor=0) หรือ penalty (หักคะแนน) หรือ no-action (ใช้แค่ filter ขา 2). ใช้ Niwes quote เป็น guide. — scope: ไม่แก้เงื่อนไข trigger (FINAL ที่ parent) — Acceptance: section 'Disqualify Rules' + 'Penalty Rules' มีรายการป้ายครบ + reason + Niwes quote ต่อป้าย

### Reference
Niwes severity hint (from agent research):

- DIVIDEND_SHRINKING - Niwes ch3 strong (ขาด core criterion)
- YIELD_TRAP - Niwes ch3 'ป้ายเตือน'
- FAKE_PROFIT - Niwes ch4 'red flag ขายตั้งแต่ปีที่ 2'
- CASHFLOW_BELOW_PROFIT - Niwes ch4 'เริ่มระวัง' (Phase 2 ตัดสินแล้ว)
- CASHFLOW_DETERIORATING - Phase 2 ตัดสินแล้ว (อาจ flag เพราะ CPALL case)
- MOAT_ERODING - Niwes ch7 sell trigger #1
- ROE_FUELED_BY_DEBT - Niwes ch5 warning (compound 4 condition = strong)
- ROE_DECLINING - orthogonal modifier (Phase 1 ตัดสินแล้ว -2)
- NO_MOAT - base 0 (Phase 3 ตัดสินแล้ว)
- CYCLICAL_BUSINESS - base 0 (Phase 4 ตัดสินแล้ว)
- OVERVALUED_VS_SELF - ขาที่ 2 ไม่ใช่ scoring

Open questions (เฉพาะที่ยังไม่ตัดสิน):
- DIVIDEND_SHRINKING - disqualify หรือ penalty? amount?
- YIELD_TRAP - disqualify หรือ penalty? amount?
- FAKE_PROFIT - disqualify? (น่าเป็น disqualify ตาม Niwes แต่ confirm)
- MOAT_ERODING - disqualify (ch7 sell trigger) หรือ penalty?
- ROE_FUELED_BY_DEBT - disqualify หรือ penalty? (compound 4 condition)
- มีป้าย negative อื่นใน Stage 1-6 ที่ลืม list ไหม - ตรวจ parent plan ก่อนคุย

## Phase 6: Verify spec กับ 5 หุ้น real + adjust ถ้า misalign
- [x] หลัง spec ครบ (Phase 1-5 approve หมด) - คำนวณ anchor score 5 หุ้น Niwes test sample ทีละหุ้น (PTT/SCC/CPALL/ADVANC/BDMS) ตาม spec ที่เพิ่งทำ. ใช้ verified data จาก parent plan SETSMART test (ป้ายติดทุก stage มีอยู่แล้ว). แสดง: disqualify check + ถ้าผ่าน คำนวณ 4 ด้าน + cap + รวม + verdict vs Niwes intuition. ถ้าหุ้นใด misalign กับ intuition (เช่น CPALL ที่คาดว่าเป็น textbook anchor แต่กลับโดน disqualify) - ระบุ root cause + ถามอาร์ทว่าจะปรับ spec ไหม. หลัง verify ครบ + อาร์ท approve adjustment (ถ้ามี) -> append section 'Verification' + apply adjustment ลง spec. — scope: ไม่ run script จริง (calc by hand) + ไม่ verify universe เต็ม — Acceptance: 5 หุ้นมี score + verdict + Niwes intuition comparison; misalign cases มี root cause + spec adjustment approved

### Reference
Niwes intuition (jam-as-reference for verification):
- CPALL = textbook anchor (Niwes ch5 STRONG_MOAT + ch7 retail daily-use stable)
- ADVANC = telecom moat strong + dividend consistent
- BDMS = healthcare stable defensive
- PTT = cyclical (Niwes ch6 ตัวอย่าง cyclical - ROE_DECLINING)
- SCC = ปันผลเสื่อม (DIVIDEND_SHRINKING strong)

Verified tag data from parent plan SETSMART test (2026-05-14):
```
PTT: STABLE_PAYER, MOAT_ERODING, CYCLICAL_BUSINESS, ROE_DECLINING, CASHFLOW_HEALTHY+DETERIORATING
SCC: DIVIDEND_SHRINKING, YIELD_TRAP 3/5, NO_MOAT, CYCLICAL_BUSINESS, RESILIENT
CPALL: GROWING_DIVIDEND, STRONG_MOAT, STABLE_BUSINESS, RESILIENT, CASHFLOW_HEALTHY+DETERIORATING, ROE_IMPROVING
ADVANC: STABLE_BUSINESS, RESILIENT, partial data (need full)
BDMS: STABLE_BUSINESS, RESILIENT, partial data (need full)
```

Key verification questions:
- ADVANC/BDMS - คะแนนตรง intuition?
- CPALL - ติด CASHFLOW_DETERIORATING (Phase 2 อาจตัดสินไปแล้วว่า disqualify/penalty)
- ถ้า CPALL anchor=0 แต่ Niwes intuition = textbook anchor -> ปรับ spec ไหม?
- PTT - มี MOAT_ERODING + CYCLICAL - คาด anchor=0 ตรงไหม

## Phase 7: Finalize spec file + re-alignment dict
- [x] หลัง verify ผ่าน + adjustment apply ครบ - finalize docs/scoring-anchor-spec.md: เพิ่ม table of contents บนสุด + spec version 1.0 + created/last_updated date + change log (initial creation) + reference list (parent plan path + niwes ch). - Acceptance: ไฟล์ spec มี TOC + version metadata + change log + reference list ที่ implementation plan อ้างถึงได้
- [x] เขียน section 'Re-alignment with implementation plan' ท้าย spec - convert ค่าทั้งหมดที่อาร์ท approve เป็น DEFAULT_SCORING_CONFIG dict format (Python nested dict) ที่ scoring-redesign-config-refactor.md Phase 1 load_scoring_config() อ่านได้. - scope: ไม่แก้ implementation plan ตรง (caller จะ backfill หลัง) - Acceptance: section มี dict structure ครบ (anchor.dividend + anchor.cashflow + anchor.moat + anchor.long_hold + disqualify_tags + penalty_dict + total_cap) ตามค่าที่ approve

### Reference
Dict format target ที่ implementation plan ใช้:

```python
DEFAULT_SCORING_CONFIG = {
    'anchor': {
        'dividend': {
            'base': {...},  # ค่าจาก Phase 1 approve
            'bonus_metrics': {...},  # ค่าจาก Phase 1
            'cap': 35
        },
        'cashflow': {
            'base': {...},  # ค่าจาก Phase 2
            'penalty': {...},  # ค่าจาก Phase 2
            'cap': 25
        },
        'moat': {
            'base': {...},  # ค่าจาก Phase 3
            'bonus_metrics': {...},
            'cap': 25
        },
        'long_hold': {
            'base': {...},  # ค่าจาก Phase 4
            'bonus_metrics': {...},
            'cap': 15
        },
        'disqualify_tags': [...],  # ค่าจาก Phase 5
        'penalty_tags': {...},  # tag -> amount จาก Phase 5
        'total_cap': 100
    }
}
```

File target: docs/scoring-anchor-spec.md เป็น human-readable spec + machine-translatable to dict (translation = implementation task)
