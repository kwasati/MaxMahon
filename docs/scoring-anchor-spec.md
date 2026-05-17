# MaxMahon Anchor Score Spec — Niwes Refactor v2

**Status:** Phase 1 (ด้านปันผล) ตกผลึก — Phase 2-7 ยังไม่เริ่ม
**Created:** 2026-05-16
**Last Updated:** 2026-05-16

## ภาพรวม

Anchor score 0-100 คะแนน — คุณภาพล้วน (ราคาแยก DCA signal ขาที่ 2)

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

## ด้าน 3 — Moat (25 คะแนน) — TBD Phase 3

(ยังไม่เริ่ม discussion)

---

## ด้าน 4 — ถือยาว + ทนวิกฤต (15 คะแนน) — TBD Phase 4

(ยังไม่เริ่ม discussion)

---

## Disqualify Rules — TBD Phase 5

(ยังไม่เริ่ม discussion)

---

## Penalty Rules — TBD Phase 5

(ยังไม่เริ่ม discussion)

---

## Verification — TBD Phase 6

(ยังไม่เริ่ม — 5 หุ้น sample PTT/SCC/CPALL/ADVANC/BDMS)

---

## Change Log

- 2026-05-16: Phase 1 ด้านปันผล FINAL (base + bonus + ROE modifier) — discussion checkpoint ครบ
