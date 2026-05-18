# MaxMahon Anchor Score Spec — Niwes Refactor v2

**Status:** FINAL v1.1 — Thai-realistic threshold + bank exclusion (2026-05-18)
**Version:** 1.1
**Created:** 2026-05-16
**Last Updated:** 2026-05-18

## Table of Contents

1. ภาพรวม
2. ด้าน 1 — ปันผลต่อเนื่อง (35 คะแนน)
3. ด้าน 2 — Cash Flow จริง (25 คะแนน)
4. ด้าน 3 — Moat (25 คะแนน)
5. ด้าน 4 — ถือยาว + ทนวิกฤต (15 คะแนน)
6. Disqualify Rules (3 ป้าย)
7. Penalty Rules (5 ป้าย)
8. No-action Rules (3 ป้าย)
9. หลักการตัดสิน Disqualify vs Penalty vs No-action
10. Verification — 5 หุ้น Light Pass (Historical Reference)
11. Reference List
12. Re-alignment with Implementation Plan (DEFAULT_SCORING_CONFIG)
13. Change Log

---

## ภาพรวม

Anchor score **internal 0-100** / **display 0.0-10.0** (หาร 10, 1 decimal) — คุณภาพล้วน (ราคาแยก DCA signal ขาที่ 2)

**Display format:**
- Internal calc เก็บเต็ม 100 (integer / float ทั้งคู่ใช้ได้ — ไม่กระทบ algo)
- UI/report แสดง `score / 10` ที่ 1 decimal — เช่น 82 → 8.2 / 57 → 5.7 / 0 → 0.0
- Future granular: ถ้าอยากได้ 2 decimal (8.25, 8.21) = เปลี่ยน internal เป็น float แล้ว display หาร 10 ที่ 2 decimal — ไม่ต้องแก้ scale ใน spec

ตัวเลขทุกค่าในไฟล์นี้ (base / bonus / modifier / penalty / cap) = **internal scale 0-100** ทั้งหมด เพื่อง่ายต่อการคำนวณ.

**น้ำหนัก 4 ด้าน:**
- ด้าน 1 — ปันผลต่อเนื่อง: 35 คะแนน
- ด้าน 2 — Cash flow จริง: 25 คะแนน
- ด้าน 3 — Moat: 25 คะแนน
- ด้าน 4 — ถือยาว + ทนวิกฤต: 15 คะแนน
- รวม: 100 คะแนน (cap)

**ระบบ 2 ขา:** anchor score (คุณภาพ) + DCA signal (ราคา) แยกกัน

**ป้ายฝ่ายเสีย 2 ระดับ:**
- Disqualify (anchor=0)
- Penalty (หักคะแนน)

---

## ด้าน 1 — ปันผลต่อเนื่อง (35 คะแนน) — FINAL 2026-05-16

อ้างอิง: Niwes ch3 — หุ้นปันผลที่ดี ไม่ใช่หุ้นที่ปันผลสูงสุด

### Base — ติดป้ายได้คะแนน

| ป้าย | คะแนน | เงื่อนไข (จาก parent plan Stage 2) |
|------|-------|-----------------------------------|
| ปันผลโต (GROWING_DIVIDEND) | 14 | จ่ายต่อเนื่อง ≥10 ปี + rising_ratio ≥70% + avg_yoy_growth ≥3% |
| นิ่ง (STABLE_PAYER) | 6 | จ่ายต่อเนื่อง ≥10 ปี แต่ตก growth criteria |
| มือใหม่ (NEW_PAYER) | 2 | จ่ายต่อเนื่อง 3-9 ปี |
| จ่ายๆหยุดๆ (INTERMITTENT) | 0 | <3 ปีติด หรือ years_paid_in_10y <8 |

Base รวม max = 14 → เหลือ 21 คะแนนสำหรับ bonus + ROE modifier

### Bonus — โตทบ 5 ปี (dps_5y_cagr) — Step B

| โตทบ/ปี | คะแนน |
|---------|-------|
| 0% หรือต่ำกว่า | 0 |
| 3% | +5 |
| 6% | +9 |
| 10% | +12 |
| 15%+ | +13 |

Step function — interpolate ไม่ใช่ linear

**ทำไมตัวเดียว:** ปีต่อเนื่องถูก count ใน base แล้ว (ติด GROWING ต้อง ≥10 ปี) + rising% overlap กับ gate ติดป้าย — เอาแค่ "โตทบ" ที่ดูขนาดการโต cleaner กว่า

### ROE trend modifier (orthogonal)

| ROE trend | คะแนน |
|-----------|-------|
| ROE_IMPROVING | +3 |
| ROE_STABLE | 0 |
| ROE_DECLINING | −5 |

### Cap

ด้านปันผลรวม ≤ 35 (cap ที่ 35 ถ้าเกิน)

### ตัวอย่างคำนวณ (จาก SETSMART test 2026-05-14)

| หุ้น | ป้าย | base | โตทบ | ROE | รวม |
|------|------|------|------|-----|-----|
| CPALL | ปันผลโต (+13% cagr, ROE_IMPROVING) | 14 | +12 | +3 | **29** |
| PTT | นิ่ง (+2.8% cagr, ROE_DECLINING) | 6 | +2 | −5 | **3** |
| SCC | (DIVIDEND_SHRINKING — Phase 5 disqualify) | — | — | — | **0** (TBD Phase 5) |

### Decision log ด้าน 1

1. **Base distribution (B2): 14/6/2/0** — gap GROWING-STABLE กว้าง = reward consistency ตรง Niwes "ความสม่ำเสมอ 20 ปี มีน้ำหนักกว่า 12% ปีเดียว"
2. **Bonus ตัวเดียว — โตทบ 5 ปี** — ปีต่อเนื่อง + rising% overlap กับ gate ติดป้าย (double count) — ตัด เหลือแค่ "โตทบ" ดูขนาดการโต
3. **Step B (รางวัลโตจริง)** — 3-6% ได้ +5/+9 แล้ว ไม่ต้องรอ 15%+ เพราะ Niwes ตัวอย่าง 5%/ปี ก็ถือว่าดี
4. **ROE modifier B: +3/0/−5** — ลงหนักกว่าขึ้น (Niwes ติด warning ตอน ROE ลง)
5. **Cap 35 — ตอนนี้ max ทำได้ ~30** — เก็บ headroom 5 คะแนน ไม่ต้อง force ให้ถึง 35

---

## ด้าน 2 — Cash Flow จริง (25 คะแนน) — Base + Bonus FINAL 2026-05-17

อ้างอิง: Niwes ch4 — กำไรเป็นความเห็น / Cash flow คือข้อเท็จจริง

**Formula:** CCR (Cash Conversion Ratio) = OCF ÷ EBITDA — เลือก 2026-05-17 หลัง test 2 formula (NI_total fail / OCF/EBITDA viable). Bypass minority interest issue + thaifin compute ได้ครบ 16 ปี (EBITDA = Gross Profit - SG&A + D&A)

**Threshold (CCR equivalent ของ Niwes OCF/NI 0.80/0.50):** ≥ 0.7 healthy / 0.5-0.7 acceptable / < 0.5 warning — EBITDA ใหญ่กว่า NI ~1.5-2x → CCR shift left

### Base — ติดป้ายได้คะแนน

| ป้าย | คะแนน | เงื่อนไข (จาก parent plan Stage 3) |
|------|-------|-----------------------------------|
| สบาย (CASHFLOW_HEALTHY) | 17 | OCF บวก 3 ปีติด + ccr_avg_3y ≥ 0.70 |
| พอใช้ (CASHFLOW_OK) | 9 | OCF บวก 3 ปีติด + ccr_avg_3y 0.50-0.70 |
| น่าระวัง (CASHFLOW_BELOW_PROFIT) | 0 | ccr_avg_3y < 0.50 — TBD Phase 5 (disqualify/penalty) |
| กำไรลม (FAKE_PROFIT) | 0 | OCF ติดลบ ≥ 1 ปี + NP บวก — TBD Phase 5 |
| กำลังเสื่อม (CASHFLOW_DETERIORATING) | 0 | OCF ลด magnitude ≤ -20% — TBD Phase 5 (trend orthogonal) |

Base รวม max = 17 → เหลือ 8 คะแนนสำหรับ bonus

### Bonus — CCR extend (ccr_avg_3y) — Step

| ccr_avg_3y | คะแนน |
|------------|-------|
| < 1.0 (baseline tier HEALTHY) | 0 |
| ≥ 1.0 | +3 |
| ≥ 1.5 | +6 |
| ≥ 2.0 | +8 |

Step function — interpolate ไม่ใช่ linear

**ทำไม metric ตัวเดียว:** Phase 1 pattern — window 3y ใช้ในทั้ง tier + bonus (cleaner ไม่ double-count)

### Cap

ด้าน Cash Flow รวม ≤ 25

### ตัวอย่างคำนวณ (Test 5 หุ้น 2026-05-17)

| หุ้น | ป้าย | CCR 3y | base | bonus | รวม |
|------|------|--------|------|-------|-----|
| PTT | สบาย | 0.87 | 17 | 0 | **17** |
| SCC | สบาย | 0.80 | 17 | 0 | **17** |
| CPALL | พอใช้ | 0.67 | 9 | 0 | **9** |
| ADVANC | สบาย | 0.96 | 17 | 0 | **17** |
| BDMS | สบาย | 0.91 | 17 | 0 | **17** |

(ยังไม่มีหุ้น CCR ≥ 1.0 ใน sample — bonus 0 ทั้งหมด)

### Decision log ด้าน 2

1. **Formula = OCF/EBITDA (CCR)** — เลือก 2026-05-17 หลัง test 2 ทางแก้ (Formula A NI_total fail / Formula B CCR viable). Root cause: thaifin OCF total (รวม minority) ÷ NI to parent (หัก minority) = ฐาน mismatch — ratio พุ่ง 3.4-5.7x systematic บน conglomerate
2. **Base distribution 17/9/0/0/0** — base กินใหญ่ (68% ของ cap) เพราะ ratio ไม่มี "ขนาด" กว้างให้ขยาย เก็บ bonus น้อย
3. **Bonus metric ตัวเดียว — ccr_avg_3y** — window เดียวกับ tier (Niwes ปักธง 3y) ตัด overlap
4. **Step 0/3/6/8** — reward CCR > 1.0 (เก็บเงินสดเกินกำไรในงบ) + cap ที่ 2.0 (outlier good — high CCR อาจมาจาก one-off working capital)
5. **Threshold 0.70/0.50** — CCR equivalent ของ Niwes OCF/NI 0.80/0.50 (EBITDA ~1.5-2x NI → CCR shift left ~0.1)
6. **Disqualify/penalty 3 ป้ายฝ่ายเสีย — FINAL 2026-05-17** — ดู section "Disqualify / Penalty rules" ด้านล่าง

### Disqualify / Penalty rules (Cash Flow tags) — FINAL 2026-05-17

3 ป้ายฝ่ายเสียของ Stage 3 — รวมเข้า Phase 5 disqualify/penalty list (รวมทุก stage)

**หลัก:** penalty หัก total anchor score (cross-ด้าน, cap floor 0) — disqualify ทำให้ anchor = 0 ทั้งหมด

| ป้าย | Verdict | จำนวน | Reason (Niwes ch4) |
|------|---------|-------|-------------------|
| CASHFLOW_BELOW_PROFIT | **penalty** | -5 | "ถ้า OCF น้อยกว่า 50% ของกำไร = เริ่มระวัง" — warning ไม่ใช่ขาย, scale เดียวกับ Phase 1 ROE_DECLINING |
| FAKE_PROFIT | **disqualify** | anchor = 0 | "ถ้า OCF ติดลบทั้งที่กำไรบวก = red flag ขายตั้งแต่ปีที่ 2" — strong sell trigger |
| CASHFLOW_DETERIORATING | **disqualify** | anchor = 0 | Niwes "ต้องไม่ลดลง" + precursor ของ FAKE_PROFIT (บทอสังหาฯ: OCF ลดต่อเนื่อง → ปีที่ 4 หยุดจ่ายปันผล + ราคาตก 80%) |

**Note: CPALL implication** — ใน test 2026-05-17 CPALL ติด HEALTHY + DETERIORATING (trend orthogonal) → ตามกฎใหม่ disqualify ที่ระดับ total anchor (anchor = 0). ตัวอย่างคำนวณด้าน 2 (CPALL = 9) แสดง score ของ ด้าน 2 เท่านั้น — total anchor ของ CPALL = 0 (Phase 6 verify จะ recompute เต็มอีกที)

---

## ด้าน 3 — Moat (25 คะแนน) — FINAL 2026-05-18

อ้างอิง: Niwes ch5 — moat คือ pricing power + structural advantage ที่ยืนนาน

### Base — ติดป้ายได้คะแนน

| ป้าย | คะแนน | เงื่อนไข (จาก parent plan Stage 4) |
|------|-------|-----------------------------------|
| moat แข็ง (STRONG_MOAT) | 10 | ROE ≥15% ติด ≥7 ปี + GM stable/improving |
| moat กลาง (MODERATE_MOAT) | 4 | ROE 10-15% ติด ≥5 ปี + GM stable |
| ไม่มี moat (NO_MOAT) | 0 | ROE ผันผวน/<10% หรือ GM หดตัว |
| moat กำลังเสื่อม (MOAT_ERODING) | 0 | TBD Phase 5 (disqualify/penalty) |
| ROE สูงเพราะกู้ (ROE_FUELED_BY_DEBT) | 0 | TBD Phase 5 (disqualify/penalty) |

Base รวม max = 10 → เหลือ 15 คะแนนสำหรับ bonus + modifier

### Bonus — ROE ≥15% ติดต่อกี่ปี (consecutive years) — Step

| ปี | คะแนน |
|----|-------|
| 7-9 | 0 (base only) |
| 10 | +5 |
| 15 | +9 |
| 20+ | +11 |

Step function — interpolate ไม่ใช่ linear

**ทำไม metric ตัวเดียว:** Phase 1+2 pattern — tier ใช้ ROE level + min duration อยู่แล้ว → bonus ขยายที่ "ติดได้ยาวแค่ไหน" ไม่ double-count

**ทำไม reward เร็วที่ 10y:** ตรง Niwes "ROE ≥15% ติดต่อ 7-10 ปี = สัญญาณ moat ดีมาก" — 10 ปีคือ sweet spot ที่ Niwes ปักธง

### Gross Margin trend modifier (orthogonal)

| GM trend | คะแนน |
|----------|-------|
| GM_IMPROVING | +2 |
| GM_STABLE | 0 |
| GM_DECLINING | −3 (rarely used — ตก moat แข็ง/กลาง ไปแล้ว) |

### Interest coverage + Net debt — informative tag (ไม่ scoring)

- ฝั่งลบ (D/E >2.0 + Interest cov <3 + Net debt เพิ่ม) → ROE_FUELED_BY_DEBT ป้ายฝ่ายเสีย → Phase 5 disqualify/penalty
- ฝั่งบวก (Interest cov สูง / Net debt ลด) → ไม่ scoring (กัน double-bonus + Niwes ไม่ reward หนี้น้อยเป็น moat indicator)

### Cap

ด้าน Moat รวม ≤ 25 (max realistic = 10 + 11 + 2 = 23, เหลือ headroom 2)

### ตัวอย่างคำนวณ (qualitative — actual ROE consecutive years pending Phase 6 verify)

| หุ้น | ป้าย | base | ROE years | GM trend | รวม |
|------|------|------|-----------|----------|-----|
| CPALL | moat แข็ง | 10 | TBD Phase 6 | TBD | TBD ≤ 23 |
| PTT | moat กำลังเสื่อม | — | — | — | 0 (Phase 5 ตัดสิน penalty/disqualify) |
| SCC | ไม่มี moat | 0 | — | — | 0 |
| ADVANC | moat แข็ง (partial data) | 10 | TBD Phase 6 | TBD | TBD ≤ 23 |
| BDMS | partial data | TBD | TBD | TBD | TBD |

### Decision log ด้าน 3

1. **Base 10/4/0/0/0** (option A — gap กว้าง) — gap moat แข็ง vs moat กลาง = 6 คะแนน ตรง Niwes "ROE ≥15% เกณฑ์ตัด moat แข็ง" + เก็บ bonus headroom 11 ให้ขยายตามขนาด "ติดได้ยาวแค่ไหน"
2. **Bonus metric ตัวเดียว = ROE consecutive years** (option B) — tier ใช้ ROE level + min duration อยู่แล้ว, bonus ขยายที่ duration ดู gap หุ้น 10y vs 20y ชัดกว่าใช้ ROE level
3. **Step 0/+5/+9/+11** (option A reward เร็ว) — pattern Phase 1 cagr reward เร็ว + ตรง Niwes "7-10 ปี = สัญญาณดีมาก" (10 ปีควรได้ค่อนข้างเยอะ ไม่ต้องรอ 20 ปี)
4. **GM modifier mild +2/0/−3** (option A) — GM trend อยู่ใน tier criteria แล้ว, modifier เลยเบากว่า Phase 1 ROE (+3/0/−5) + Niwes ไม่ "warning" GM declining แรงเท่า ROE declining
5. **Interest coverage / Net debt = informative tag (ไม่ scoring)** (option A) — กัน double-bonus + Phase 1+2 pattern bonus ตัวเดียว + Niwes ไม่ reward หนี้น้อยเป็น moat indicator + ฝั่งลบครอบ Phase 5 (ROE_FUELED_BY_DEBT)
6. **Disqualify/penalty 3 ป้ายฝ่ายเสีย (MOAT_ERODING, ROE_FUELED_BY_DEBT, NO_MOAT)** — TBD Phase 5 รวมที่หลัง

---

## ด้าน 4 — ถือยาว + ทนวิกฤต (15 คะแนน) — FINAL 2026-05-18

อ้างอิง: Niwes ch6 — "เวลา คือผลตอบแทนที่คุณได้ฟรี ตราบเท่าที่คุณไม่ขายทิ้ง"

**ลักษณะพิเศษ:** ป้ายฝ่ายบวก 2 ตัวเป็น orthogonal (ติดได้พร้อมกัน) — ใช้โครงสร้าง **additive** (ติดป้ายไหนได้คะแนนของป้ายนั้น รวมกัน)

### Base — ติดป้ายได้คะแนน (additive)

| ป้าย | คะแนน | เงื่อนไข (จาก parent plan Stage 5) |
|------|-------|-----------------------------------|
| ธุรกิจนิ่ง (STABLE_BUSINESS) | 4 | sector ใน STABLE/STABLE_UTILITY + eps_cv_10y ≤30% |
| ผ่านวิกฤตได้ (RESILIENT_THROUGH_CRISIS) | 6 | crisis_2011_drop ≥−40% + ocf_2011 >0 + crisis_2020_drop ≥−40% + ocf_2020 >0 |
| ผสม (MIXED_STABILITY) | 0 | ไม่ติดทั้ง 2 ป้ายฝ่ายบวก — TBD Phase 5 (penalty?) |
| วัฏจักร (CYCLICAL_BUSINESS) | 0 | sector ใน CYCLICAL หรือ eps_cv_10y >50% — TBD Phase 5 (penalty?) |

Base รวม max (ติดทั้ง 2) = 10 → เหลือ 5 คะแนนสำหรับ bonus

**ทำไม RESILIENT > STABLE:** RESILIENT เงื่อนไข 4 conditions (ต้องผ่าน 2 crisis + OCF บวกทั้งคู่) = proof แท้ พิสูจน์แล้ว / STABLE เงื่อนไข soft (sector + cv) = prediction — reward proof มากกว่า prediction

### Bonus 1 — EPS swing extend (ขยาย STABLE)

EPS swing = ความแกว่งของกำไรเทียบค่าเฉลี่ย 10 ปี (eps_cv_10y) — ต่ำ = สม่ำเสมอ

| EPS swing | คะแนน |
|-----------|-------|
| 25-30% | 0 (base only) |
| 15-24% | +1 |
| <15% | +2 |

**ทำไม +2 max:** EPS swing ต่ำเป็น "ความปกติ" — บางเซคเตอร์ swing ต่ำเป็นธรรมชาติ (utility/F&B) ไม่ใช่ signal แรงเท่า crisis tolerance ที่พิสูจน์มาแล้ว → reward เบากว่า

### Bonus 2 — Crisis drop magnitude extend (ขยาย RESILIENT)

วัด drop เฉลี่ย 2 crisis (2011 + 2020) — น้อย = ทนแรง

| avg drop 2 crisis | คะแนน |
|------------------|-------|
| −30 ถึง −40% | 0 (base only) |
| −15 ถึง −29% | +1 |
| −5 ถึง −14% | +2 |
| 0 ถึง −4% (หรือบวก) | +3 |

**ทำไม +3 max:** drop น้อยตอน crisis = signal pricing power + balance sheet แข็ง (ของจริงพิสูจน์มาแล้ว) — Niwes ch6 ยก "หุ้นที่ผ่านต้มยำกุ้ง + subprime/covid โดยกระทบน้อย = ของจริง"

### ไม่มี modifier ใน Phase 4

orthogonal axis ใช้ครบที่ bonus 2 ตัว (Phase 1 ROE trend modifier นอก tier / Phase 3 GM อยู่ใน tier — Phase 4 ใช้ orthogonal เป็น 2 base + 2 bonus แทน)

### Cap

ด้าน Phase 4 รวม ≤ 15 (max realistic = 4 + 6 + 2 + 3 = 15 เต็ม cap)

### ตัวอย่างคำนวณ (qualitative — actual eps_cv + crisis drop pending Phase 6 verify)

| หุ้น | STABLE | RESILIENT | EPS swing | crisis drop | รวม |
|------|--------|-----------|-----------|-------------|-----|
| CPALL | 4 (ติด) | 6 (ติด) | TBD | TBD | TBD ≤ 15 |
| SCC | 0 (cyclical) | 6 (ติด resilient) | — | TBD | 6-9 |
| ADVANC | 4 (ติด) | 6 (ติด) | TBD | TBD | TBD ≤ 15 |
| BDMS | 4 (ติด) | 6 (ติด) | TBD | TBD | TBD ≤ 15 |
| PTT | 0 (cyclical) | 0 (ไม่ทน) | — | — | 0 |

### Decision log ด้าน 4

1. **โครงสร้าง additive** (option A) — STABLE กับ RESILIENT orthogonal ติดได้พร้อมกัน — additive reflect คุณสมบัติจริงดีกว่า combined tier ที่บังคับ trade-off artificial
2. **Base 4 + 6 (เน้น RESILIENT)** (option C) — RESILIENT เงื่อนไขยากกว่า (4 conditions ต้องผ่าน 2 crisis) + proof แท้ > prediction — SCC ทน crisis แม้ cyclical = signal แท้ ควรได้ 6
3. **Bonus EPS swing 0/+1/+2 (25-30/15-24/<15%)** — reward stability เร็วที่ 15% (ตรง pattern Phase 1 cagr reward เร็ว) — max +2 เพราะ swing ต่ำเป็นธรรมชาติ sector
4. **Bonus crisis drop 0/+1/+2/+3 (−30/−15/−5/0%)** — 4 step ละเอียดกว่า EPS swing เพราะ drop pattern หุ้น crisis-resilient มี variance สูง (ADVANC drop น้อย vs SCC drop เกือบ gate) — max +3 reward elite "drop เกือบไม่กระทบ"
5. **ไม่มี modifier** — Phase 1/3 ใช้ modifier เพราะ orthogonal axis (ROE trend / GM trend) ไม่ได้รวมใน base/bonus — Phase 4 ใช้ orthogonal เป็น base 2 ตัว + bonus 2 ตัวครบแกนแล้ว ไม่ต้อง modifier เพิ่ม
6. **CYCLICAL + MIXED ฝ่ายเสีย — TBD Phase 5** รวมที่หลัง (น่าจะ no-action หรือ penalty เบา — Phase 5 ตัดสิน)

---

## Disqualify Rules — FINAL 2026-05-18

ใช้กับป้ายที่ Niwes flag เป็น sell trigger explicit หรือ red flag level (anchor = 0)

| ป้าย | ที่มา | Niwes evidence |
|------|------|---------------|
| FAKE_PROFIT | Stage 3 | ch4 "red flag ขายตั้งแต่ปีที่ 2" — explicit sell trigger (Phase 2) |
| CASHFLOW_DETERIORATING | Stage 3 | ch4 "ต้องไม่ลดลง" + precursor ของ FAKE_PROFIT (Phase 2) |
| MOAT_ERODING | Stage 4 | ch7 sell trigger #1 + "Disruption risk" explicit (EV กับน้ำมัน, e-commerce กับ retail) — Phase 5 |

3 ป้ายทั้งหมด — Niwes พูด "ขาย" / sell trigger explicit ใน text

---

## Penalty Rules — FINAL 2026-05-18

ใช้กับป้ายที่ Niwes flag เป็น warning ไม่ใช่ sell trigger — หักจาก total anchor score (cap floor 0)

| ป้าย | Amount | ที่มา | Niwes evidence |
|------|--------|------|---------------|
| YIELD_TRAP | −15 | Stage 2 | ch3 "เลี่ยง 'หุ้นปันผลสูง' ที่จ่ายชั่วคราว" — explicit warning strong |
| DIVIDEND_SHRINKING | −10 | Stage 2 | implicit fail Niwes 5-5-5-5 ("ปันผลเพิ่มทุกปี") + SCC case study (DPS 19→5) |
| ROE_FUELED_BY_DEBT | −10 | Stage 4 | implicit "หุ้นมั่นคง แข็งแกร่ง" + compound 4 conditions (D/E + Int cov + Net debt) strong signal |
| CASHFLOW_BELOW_PROFIT | −5 | Stage 3 | ch4 "เริ่มระวัง" — soft warning (Phase 2) |
| CYCLICAL_BUSINESS | −5 | Stage 5 | ch6 daily-use vs disruption — sector วัฏจักรไม่เหมาะ DCA 10-20 ปี แต่ไม่ห้าม |

Plus ROE_DECLINING −5 (Phase 1 modifier orthogonal — แยก scoring จาก penalty list)

---

## No-action Rules — FINAL 2026-05-18

ป้ายที่ Niwes ไม่ flag เป็น red flag — score ปกติทำงานเอง (base 0 sufficient)

| ป้าย | ที่มา | เหตุผล |
|------|------|--------|
| MIXED_STABILITY | Stage 5 | Niwes ไม่ flag + Phase 4 base 0 อยู่แล้ว score ปกติทำงาน |
| NO_MOAT | Stage 4 | Phase 3 base 0 อยู่แล้ว — ไม่มี moat = ไม่ได้คะแนน แต่ไม่ใช่ red flag |
| INTERMITTENT | Stage 2 | Phase 1 base 0 อยู่แล้ว — จ่ายๆหยุดๆ ไม่ใช่ "ปันผลที่ดี" แต่ไม่ใช่ sell trigger |

---

## หลักการตัดสิน Disqualify vs Penalty vs No-action

1. **Disqualify (anchor=0)** = Niwes พูด "ขาย" / "red flag" / "sell trigger" explicit ใน text
2. **Penalty heavy (−10 to −15)** = Niwes warning strong (explicit "เลี่ยง" หรือ implicit fail core criterion)
3. **Penalty medium (−5)** = Niwes "เริ่มระวัง" / warning soft
4. **No-action** = Niwes ไม่ได้ flag + base 0 ทำงานเองได้

---

## Decision log Phase 5

1. **MOAT_ERODING = disqualify** — Niwes ch7 sell trigger #1 explicit + disruption risk warning (level เดียวกับ FAKE_PROFIT)
2. **YIELD_TRAP = penalty −15** — Niwes explicit "เลี่ยง" — heavy warning ที่ไม่ถึง sell trigger
3. **DIVIDEND_SHRINKING = penalty −10** — implicit fail core criterion 5-5-5-5 + SCC case study (severity strong แต่ไม่ explicit sell)
4. **ROE_FUELED_BY_DEBT = penalty −10** — compound 4 conditions strong signal + Niwes implicit "หุ้นมั่นคง" (severity strong แต่ Niwes ไม่ explicit sell)
5. **CYCLICAL_BUSINESS = penalty −5** — Niwes ch6 daily-use vs disrupt + Phase 4 base 0 อยู่แล้ว (ไม่ disqualify เพราะ cyclical ปกติ ≠ disrupted)
6. **MIXED_STABILITY = no-action** — Niwes ไม่ flag + base 0 ทำงานเองได้

**สรุป count:**
- 3 ป้าย disqualify (FAKE_PROFIT + CASHFLOW_DETERIORATING + MOAT_ERODING) — ทั้งหมด Niwes sell trigger explicit
- 5 ป้าย penalty (−15 to −5)
- 3 ป้าย no-action (MIXED_STABILITY + NO_MOAT + INTERMITTENT — base 0 อยู่แล้ว)

**Test impact (5 หุ้น sample):**
- SCC (DIVIDEND_SHRINKING + YIELD_TRAP + CYCLICAL): penalty rolls = −10 − 15 − 5 = −30 → anchor = max(0, ~23 − 30) = **0**
- PTT (MOAT_ERODING + CYCLICAL): disqualify → **anchor = 0**
- CPALL (CASHFLOW_DETERIORATING Phase 2): disqualify → **anchor = 0** (Phase 6 verify จะดูต่อ — ถ้า misalign Niwes intuition จะ revisit)
- ADVANC / BDMS: partial data — Phase 6 verify

---

## Verification — FINAL 2026-05-18 (Light Pass — Historical Reference)

**Scope note:** Niwes 5 หุ้น sample = historical reference จากยุค 2000s ที่ Niwes สะสม — ไม่ใช่ ground truth ของ spec วันนี้ (ดู `feedback_niwes_5_stocks_historical_reference.md`). Verify นี้ดู context drift narrative ไม่ adjust spec ตามผล

**ใช้ verified tag data:** parent plan SETSMART test 2026-05-14 + Phase 2 CCR test 2026-05-17 + Phase 1 spec example (CPALL/PTT)

### Anchor Score 5 หุ้น

| หุ้น | ด้าน 1 | ด้าน 2 | ด้าน 3 | ด้าน 4 | Penalty | Anchor |
|------|--------|--------|--------|--------|---------|--------|
| PTT | 3 | disqualify (CASHFLOW_DETERIORATING) | — | — | — | **0** |
| SCC | 0 | 17 | 0 | 6 | −30 (DIVIDEND_SHRINKING + YIELD_TRAP + CYCLICAL) | **0** |
| CPALL | 29 | disqualify (CASHFLOW_DETERIORATING) | — | — | — | **0** |
| ADVANC | ~9 | 17 | ~19 | ~12 | 0 | **~57** ✓ |
| BDMS | ~8 | 17 | ~15 | ~12 | 0 | **~52** ✓ |

ADVANC/BDMS = partial data (dps_5y_cagr / ROE consecutive years approximate) — scan implementation จะ verify ตัวเลขจริง

### Narrative Drift (ทำไม 3/5 ตก)

| หุ้น | Niwes ยุค (2000s context) | ตอนนี้ (spec result) | สาเหตุ drift |
|------|---------------------------|----------------------|------------|
| PTT | blue chip energy stable | anchor=0 (disqualify) | EV disrupting + cash flow declining + minority structure |
| SCC | cement growth + DPS story | anchor=0 (penalty −30) | overcapacity Asia + property slowdown + DPS shrink 19→5 |
| CPALL | 7-11 hyper-growth | anchor=0 (disqualify) | retail saturated + e-commerce + cash flow erratic |
| ADVANC | telecom moat | ~57 anchor ✓ | infrastructure moat ยัง intact + 5G barriers |
| BDMS | hospital aging | ~52 anchor ✓ | aging demographic structural |

### Validation Insight

- **3/5 ตก** — spec ทำงานตาม Niwes invariant ("ปันผลต้องไม่ลด" / "cash flow ต้องไม่เสื่อม" / "moat ต้องไม่เสื่อม") — Niwes สมัยถือคือ snapshot ผ่านมาแล้ว (10-20 ปี)
- **2/5 ยังเป็น anchor** — daily-use + structural moat ที่ยัง intact (telecom infrastructure + hospital aging)
- **spec = strict Niwes pure form** — ไม่ใช่ "Niwes สะสม yug 2000s" — match ความตั้งใจของ Niwes ปรัชญา ไม่ใช่ portfolio holding history

### Adjustment

**ไม่ปรับ spec** — drift narrative อธิบายได้ตาม Niwes ปรัชญา. หุ้น 3 ตัวที่ตกเป็นเพราะ context ตลาดเปลี่ยน ไม่ใช่ spec ผิด

**Pending validation** — scan universe 933 หุ้น ใน implementation (Phase 7+) จะดู TOP anchor candidates ปัจจุบัน เป็น verification หลัก

---

## Reference List

**Plan files:**
- Parent design: `C:\WORKSPACE\.claude\plans\4-MaxMahon\niwes-refactor-v2-design.md` — Stage 1-6 tag rules + aggregates fields
- Discussion plan: `C:\WORKSPACE\.claude\plans\4-MaxMahon\scoring-formula-discussion.md` — Phase 1-7 discussion checkpoints
- Master index: `C:\WORKSPACE\.claude\plans\4-MaxMahon\maxmahon-index.md` — MaxMahon build order
- Implementation plan: `C:\WORKSPACE\.claude\plans\4-MaxMahon\scoring-redesign-config-refactor.md` — STALE, awaiting rewrite based on this spec

**Niwes references (verbatim quotes used in decision logs):**
- `C:\WORKSPACE\projects\4-MaxMahon\docs\niwes\00-index.md` — Niwes research master index
- `C:\WORKSPACE\projects\4-MaxMahon\docs\niwes\03-philosophy.md` — 8 ปรัชญาหลัก
- `C:\WORKSPACE\projects\4-MaxMahon\docs\niwes\04-criteria.md` — 5-5-5-5 + 11 เกณฑ์
- `C:\WORKSPACE\projects\4-MaxMahon\docs\niwes\06-case-cpall.md` — CPALL case study
- `C:\WORKSPACE\projects\4-MaxMahon\docs\niwes\09-case-or-exit.md` — sell + disruption examples
- `C:\WORKSPACE\projects\4-MaxMahon\docs\niwes\12-recent-views-2025-2026.md` — recent context
- `C:\WORKSPACE\projects\4-MaxMahon\docs\niwes\15-exit-rules.md` — sell trigger rules

**Chapter mapping (Niwes book → spec section):**
- ch3 (ปันผล) → ด้าน 1 + DIVIDEND_SHRINKING + YIELD_TRAP
- ch4 (cash flow) → ด้าน 2 + FAKE_PROFIT + CASHFLOW_DETERIORATING + CASHFLOW_BELOW_PROFIT
- ch5 (moat) → ด้าน 3 + ROE_FUELED_BY_DEBT
- ch6 (ถือยาว) → ด้าน 4 STABLE_BUSINESS + CYCLICAL_BUSINESS
- ch7 (sell trigger) → MOAT_ERODING + ด้าน 4 RESILIENT_THROUGH_CRISIS

**Memory references:**
- `feedback_niwes_5_stocks_historical_reference.md` — Phase 6 verify principle (Niwes 5 หุ้น = historical reference ไม่ใช่ ground truth)
- `project_maxmahon_niwes_refactor.md` — main project memory

---

## Re-alignment with Implementation Plan (DEFAULT_SCORING_CONFIG)

Python nested dict format สำหรับ implementation plan (`scoring-redesign-config-refactor.md` Phase 1 `load_scoring_config()`):

```python
DEFAULT_SCORING_CONFIG = {
    'anchor': {
        'dividend': {
            'base': {
                'GROWING_DIVIDEND': 14,
                'STABLE_PAYER': 6,
                'NEW_PAYER': 2,
                'INTERMITTENT': 0,
            },
            'bonus_metrics': {
                'dps_5y_cagr': {
                    # step function — discrete floor lookup at threshold
                    'steps': [
                        (0.00, 0),
                        (0.03, 5),
                        (0.06, 9),
                        (0.10, 12),
                        (0.15, 13),
                    ],
                },
            },
            'modifiers': {
                'ROE_IMPROVING': 3,
                'ROE_STABLE': 0,
                'ROE_DECLINING': -5,
            },
            'cap': 35,
        },
        'cashflow': {
            'base': {
                'CASHFLOW_HEALTHY': 17,
                'CASHFLOW_OK': 9,
                'CASHFLOW_BELOW_PROFIT': 0,
                'FAKE_PROFIT': 0,
                'CASHFLOW_DETERIORATING': 0,
            },
            'bonus_metrics': {
                'ccr_avg_3y': {
                    'steps': [
                        (1.0, 3),
                        (1.5, 6),
                        (2.0, 8),
                    ],
                },
            },
            'cap': 25,
        },
        'moat': {
            'base': {
                'STRONG_MOAT': 10,
                'MODERATE_MOAT': 4,
                'NO_MOAT': 0,
                'MOAT_ERODING': 0,
                'ROE_FUELED_BY_DEBT': 0,
            },
            'bonus_metrics': {
                'roe_consecutive_15plus_years': {
                    'steps': [
                        (10, 5),
                        (15, 9),
                        (20, 11),
                    ],
                },
            },
            'modifiers': {
                'GM_IMPROVING': 2,
                'GM_STABLE': 0,
                'GM_DECLINING': -3,
            },
            'cap': 25,
        },
        'long_hold': {
            'base_additive': {
                # additive — ติดได้พร้อมกัน (orthogonal)
                'STABLE_BUSINESS': 4,
                'RESILIENT_THROUGH_CRISIS': 6,
            },
            'bonus_metrics': {
                'eps_cv_10y': {
                    'steps': [
                        (0.30, 0),  # base only — gate threshold
                        (0.24, 1),
                        (0.15, 2),
                    ],
                    'lower_is_better': True,
                },
                'crisis_drop_avg_pct': {
                    'steps': [
                        (-0.40, 0),  # base only — gate threshold
                        (-0.29, 1),
                        (-0.14, 2),
                        (-0.04, 3),
                    ],
                    'lower_magnitude_is_better': True,
                },
            },
            'cap': 15,
        },
        'total_cap': 100,
    },
    'disqualify_tags': [
        'FAKE_PROFIT',
        'CASHFLOW_DETERIORATING',
        'MOAT_ERODING',
    ],
    'penalty_tags': {
        'YIELD_TRAP': -15,
        'DIVIDEND_SHRINKING': -10,
        'ROE_FUELED_BY_DEBT': -10,
        'CASHFLOW_BELOW_PROFIT': -5,
        'CYCLICAL_BUSINESS': -5,
    },
    'no_action_tags': [
        'MIXED_STABILITY',
        'NO_MOAT',
        'INTERMITTENT',
    ],
    'display_scale': 10,  # internal 0-100 → display หาร 10 ที่ 1 decimal (82 → 8.2)
}
```

### Implementation notes

1. **Tier base** (Phase 1-3): mutually exclusive ป้ายต่อด้าน — assign ป้ายเดียวต่อด้าน → base lookup
2. **Long_hold base_additive** (Phase 4): orthogonal — ติดป้าย STABLE + RESILIENT ทั้งคู่ได้ → sum
3. **Bonus step function**: discrete floor — หา threshold ที่ใหญ่ที่สุดที่ value >= threshold (สำหรับ "higher is better") หรือ value <= threshold (สำหรับ "lower is better"/"lower magnitude is better")
4. **Disqualify**: ถ้ามี tag ใน `disqualify_tags` ติด → anchor = 0 ทันที (ไม่ต้องคำนวณ 4 ด้าน)
5. **Penalty**: หักจาก total anchor score หลังคำนวณ 4 ด้าน + cap → cap floor 0 (penalty ไม่ทำให้ negative)
6. **ROE_DECLINING** อยู่ใน `modifiers` ของ dividend (orthogonal กับ tier) — แยก scoring กับ `penalty_tags`
7. **No-action tags**: informational only — ไม่ส่งผลต่อ score (base 0 อยู่แล้ว)
8. **Display conversion**: `display_score = round(anchor_score / display_scale, 1)` — แสดง 1 decimal place (82 → 8.2). Future granular: เปลี่ยน internal เป็น float → `round(score / scale, 2)` ได้ 8.25

### Calculation order

```
1. Check disqualify_tags → if any matches: return anchor_score = 0
2. Compute dividend  (base + bonus + modifier + cap 35)
3. Compute cashflow  (base + bonus + cap 25)
4. Compute moat      (base + bonus + modifier + cap 25)
5. Compute long_hold (base_additive + bonus + cap 15)
6. Sum 4 ด้าน → total (cap 100)
7. Subtract penalty (sum of penalty_tags ที่ match)
8. anchor_score = max(0, total - penalty)
```

---

## Change Log

- 2026-05-16: Phase 1 ด้านปันผล FINAL (base + bonus + ROE modifier) — discussion checkpoint ครบ
- 2026-05-17: Phase 2 ด้าน Cash Flow FINAL (CCR formula resolved + base/bonus + disqualify/penalty 3 ป้าย) — discussion checkpoint ครบ
- 2026-05-18: Phase 3 ด้าน Moat FINAL (base + bonus ROE consecutive years + GM modifier mild + interest cov informative-only) — discussion checkpoint ครบ
- 2026-05-18: Phase 4 ด้านถือยาว + ทนวิกฤต FINAL (additive structure + STABLE 4 / RESILIENT 6 + bonus EPS swing 0-2 + bonus crisis drop 0-3) — discussion checkpoint ครบ
- 2026-05-18: Phase 5 disqualify/penalty list FINAL (3 disqualify + 5 penalty + 3 no-action — อิง Niwes quote audit verbatim) — discussion checkpoint ครบ
- 2026-05-18: Phase 6 verification light pass FINAL (5 หุ้น Niwes sample = historical reference, 3/5 ตกตาม Niwes invariant + 2/5 anchor ที่ยัง intact — ไม่ปรับ spec) — discussion checkpoint ครบ
- 2026-05-18: Phase 7 spec finalize FINAL (TOC + Version 1.0 + Reference List + DEFAULT_SCORING_CONFIG dict + Implementation notes + Calculation order + display_scale 10 for UI 0.0-10.0 format) — Spec v1.0 RELEASE
- 2026-05-18 v1.1: Thai-realistic threshold revision — STRONG_MOAT ROE ≥12% (was 15%) ติด ≥5y (was 7y) for general / ≥10% 5y for Banks-Finance-Insurance. MODERATE_MOAT ROE ≥8% 3y general / ≥7% 3y Banks. RESILIENT crisis drop ≤−50% (was −40%). FAKE_PROFIT exclude Banks/Finance/Insurance sectors (Niwes ch4 context = industrial not banking).
