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

## ด้าน 2 — Cash Flow จริง (25 คะแนน) — TBD Phase 2

(ยังไม่เริ่ม discussion)

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
