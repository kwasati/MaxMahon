---
title: Niwes Manual Deep-Dive — Master Summary
session_start: 2026-05-19
status: in-progress
purpose: resume doc — เปิดอ่านไฟล์เดียวรู้ทั้งหมดที่คุยกัน ทำอะไรไปแล้ว ค้างอะไร
---

# Niwes Manual Analysis — Master Doc

## Context

อาร์ทไม่เชื่อใจ Max algo current scoring 100% — มันให้ CIMBT/MTI/PTTEP เป็น top score (4.9) ทั้งที่ตัวเลข fundamental จริงไม่ค่อยตรง Niwes spirit อาร์ทอยากแกะมือเองว่า:

1. หุ้นไหนผ่าน 5-5-5-5 floor จริง
2. ในกลุ่มนั้น ตัวไหนใกล้ Niwes "spirit" จริงๆ
3. ทำไม Max algo ranking ต่างจาก manual analysis เยอะ
4. อะไรที่ Niwes ดู แต่ algo (และ chat session นี้) ยังไม่คลุม

**Long-term goal:** ปรับ Max algo ให้ใกล้ Niwes spirit จริง — โดยใช้ manual lens เป็น ground-truth

## Source Data

- **Universe:** scan 2026-05-18 (933 หุ้นไทย → screener_2026-05-18.json) → ผ่าน 5-5-5-5 floor = 56 ตัว
- **Data path:** `projects/4-MaxMahon/data/screener_2026-05-18.json`
- **Algo scoring:** `niwes-dividend-first-v2` (5 pillars 100 pts — Dividend 50 / Valuation 25 / Cash Flow 10 / Hidden Value 5 / Track Record 10)

## Filter Chain ที่เราสร้าง (Strict Niwes Lens)

```
56 ตัว (algo screener ผ่าน 5-5-5-5)
  ↓
  Filter 1: yield ปีล่าสุด ≥ 5% (ตัด Niwes growing exception)
  ↓
55 ตัว (ตัด AWC ที่ yield 3.7% ผ่านมาทาง NIWES_GROWING)
  ↓
  Score 5 binary checks (1 คะแนน/ข้อ):
    ⓓ DPS ขึ้นทุกปี 3 ปี (strict pairwise 2022→2023→2024)
    ⓡ รายได้ + กำไร ขึ้นทุกปี 3 ปี
    💰O OCF บวกทุกปี 3 ปี
    💰F FCF บวกทุกปี 3 ปี
    ✓N OCF/NI 2024 ≥ 1.0 (กำไรกลายเป็นเงินสดจริง)
  ↓
  Tier S (5/5) — 2 ตัว — ผ่านครบ
  Tier A (4/5) — 6 ตัว
  Tier B (3/5) — 18 ตัว
  Tier C (2/5) — 9 ตัว
  Tier D (1/5) — 13 ตัว
  Tier F (0/5) — 7 ตัว
  ↓
  Filter 2 (decision 2026-05-19): ตัวที่มีปีขาดทุน 10 ปี = ตก list
  ↓
  ตก list (7 ตัว — ไม่ลบจาก data แต่เอาออกจาก ranking):
    CIMBT(1) · MAJOR(1) · TU(1) · EGCO(1) · METCO(1) · RCL(3) · AIMIRT(1)
```

## ความตัดสินใจสำคัญใน session นี้

1. **yield hard floor 5%** (ไม่เอา NIWES_GROWING exception) — เพราะ Niwes design รอบ 5%
2. **Strict pairwise YoY** (ไม่ใช้ CAGR average) — ตามคำพูด Niwes "ขึ้นทุกปี" หมายความเช่นนั้นจริงๆ
3. **Cash flow ใน scoring** — Niwes "เงินสดเหลือเฟือ" + "จ่ายปันผลจาก op profit" — แปลเป็น OCF/FCF/OCF-NI 3 binary checks
4. **3 ปี window** สำหรับ track record (ไม่ใช่ 5y CAGR) — strict
5. **ROE 10y + ไม่ขาดทุน** = filter เพิ่ม Niwes #11 (decision 2026-05-19)
6. **Algo ของ Max ใช้ continuous scoring + CAGR average** — ของเรา binary strict = ranking ต่างเพราะ design ต่าง

## Current State — 55 Stocks Tiered (2026-05-20 — post snapshot DPS fix v6.6.1)

ดู `manual-niwes-ranking-2026-05-20.md` สำหรับตารางเต็ม + diff section
(ของเก่าก่อน fix: `manual-niwes-ranking-2026-05-19.md` — yahoo split-adjusted DPS)

**Tier S (5/5) — ผ่านครบ:**
- BBL (Banking · y 6.1% · DPS 2.5→3.5→4.5→7.0→8.5→10.0 จาก set.or.th ขึ้นทุกปี)

**Tier A (4/5):**
- HTC (F&B · y 6.6% · DPS 1.52→1.52→1.05 ตก → ⓓ fail) — เคย S
- AMATA (Prop Dev · y 5.3% · DPS 0.2→0.4→0.6→0.65→0.8→1.1 ขึ้นทุกปี)
- ILM (Commerce · y 8.0%) · ROJNA ⚠ (Prop Dev · y 10.2%)
- PTTEP (Energy · y 5.8%) — UP จาก B

**Tier B-F:** ดูในไฟล์ ranking 2026-05-20

**Key tier changes vs 2026-05-19 (impact ของ snapshot DPS source-aware fix + data refresh):**
- **HTC** S → A — set.or.th DPS แสดงค่าจริง (yahoo split-adjusted ทำให้ดูโตจอม) → ⓓ fail
- **BBL** S → S — DPS ขึ้นจริงทุกปี (set.or.th confirm)
- **KBANK** A → B — DPS ขึ้น ✓ แต่ ⓡ revenue dip 22→23
- **PTT** A → B — DPS 2.0→2.0→2.1 (strict pairwise flat = fail)
- **PTTEP** B → A — ⓓ ขึ้น
- **THANI** A → D — multi-check fail (data refresh)
- รวม 12 ตัวเปลี่ยน — ดูตารางเต็มใน ranking 2026-05-20

**Loss-year tagged OUT (7 ตัว):**
| Sym | Tier | y% | ปีขาดทุน | ROE min | หมายเหตุ |
|---|:---:|---:|:---:|---:|---|
| CIMBT | C | 15.9 | 1 | -2.3% | Banking — yield สูงสุด list แต่ขาดทุน |
| MAJOR | B | 8.6 | 1 | -8.4% | Media — COVID hit |
| TU | B | 6.0 | 1 | -20.0% | F&B — write-off Red Lobster |
| EGCO | C | 5.6 | 1 | -7.4% | Energy — IPP cyclical |
| METCO | D | 10.8 | 1 | -2.7% | Electronic — semiconductor cycle |
| RCL | C | 7.9 | **3** | -13.8% | Transport — container shipping cycle ขาด 3/10 |
| AIMIRT | F | 6.8 | 1 | -0.3% | REIT — pandemic property hit |

## 13 Niwes Criteria — Coverage Status

(ดู `niwes-criteria-coverage-map.md` เต็ม)

**คลุมแล้ว ✅ (6 ข้อ):**
- #1 yield ≥5% ตอนนี้
- #3 PE ≤15 (algo floor)
- #4 PBV <1.5 (algo floor)
- #5 ปันผลจาก operating profit (OCF/FCF/Cash)
- #6 รายได้/กำไร/ปันผล ขึ้นทุกปี (strict YoY)
- #12 กระจาย 5+ sector (algo floor)

**ยังไม่คลุม ⏳ (7 ข้อ):**

| # | เกณฑ์ | Quant/Qual | สถานะ |
|---|---|:---:|:---:|
| #2 | yield ≥5% อีก 5 ปี | Quant | ⟳ จะทำต่อ (forward projection) |
| #8 | Hidden Value | Quant | ⟳ จะทำต่อ (pull algo cache) |
| #11 | ROE consistent 10y + ไม่ขาดทุน | Quant | ✅ ทำแล้ว 2026-05-19 |
| #7 | ธุรกิจอยู่กับเรา 3+ ปี | Qual | ⏳ ค้าง (คน) |
| #9 | Moat / mid-tier | Qual | ⏳ ค้าง (คน) |
| #10 | Daily-use + ไม่ sexy | Qual | ⏳ ค้าง (คน) |
| #13 | Geographic 30/30/30 | Qual | ⏳ ค้าง (คน) |

## Anomalies / ต้องคิด

1. **NER (Tier D, score 1/5)** ROE avg 10y = **26.7%** ดีสุดทั้ง list + ไม่เคยขาดทุน + D/E 1.06 — สูงสุดทุก quality metric แต่ score ต่ำเพราะ DPS+rev YoY ไม่ขึ้น strict. ต้องเจาะ
2. **LANNA / AEONTS** ROE 18-19% + D/E ต่ำ + ไม่ขาดทุน — anomaly เทียบ tier B ตัวเอง
3. **BBL D/E 7.00 vs HTC 0.77** — Tier S ทั้งคู่ profile ตรงข้าม: HTC compounder low-leverage / BBL bank leverage ปกติ
4. **Banking D/E 5-9 = ปกติ** ของธุรกิจกู้-ปล่อยกู้ — เทียบกันเองในกลุ่ม
5. **NER ROE 26.7%** ขัดกับ algo score ต่ำ — Niwes น่าจะเลือก NER มากกว่า KKP (algo 3.8) → algo มี bias ทาง streak weight
6. **ขัดแย้ง Niwes spirit:** algo top = mature payer (CIMBT/MTI/PTTEP — long streak high yield) vs manual top = compounder (HTC/BBL — DPS+rev+กำไร ขึ้นทุกปี)

## Files ใน Session

| File | Purpose |
|---|---|
| `niwes-analysis-master.md` (this) | resume doc — เปิดอ่านไฟล์เดียว |
| `manual-niwes-ranking-2026-05-19.md` | ranking 55 stocks + ROE+D/E full data |
| `niwes-criteria-coverage-map.md` | 13 criteria + matrix coverage status |

## Extended Score (Niwes #8 + #2 + #11 included)

**คะแนนใหม่ max 7:**
- 5 base (DPS↑ / rev+กำไร↑ / OCF+ / FCF+ / OCF/NI≥1)
- + 1 ROE avg10y ≥ 10%
- + 1 D/E reasonable (bank ≤10 / non-bank ≤2)

**Filter:** loss years ≥1 ใน 10 ปี → **OUT** (ไม่ลบจาก data)

### Re-ranked Master Tier

| Tier | Score | Sym | y% | ROE10 | D/E | DPS CAGR | Proj y29 | Sector |
|:---:|:---:|---|---:|---:|---:|---:|---:|---|
| **S+** | 7/7 | **HTC** | 6.6 | 12.6% | 0.77 | +2.5% | 7.9% ✓ | F&B |
| S | 6/7 | ILM | 8.0 | 11.3% | 1.07 | +16.1% | 16.9% ✓ | Commerce |
| S | 6/7 | THANI | 6.7 | 16.6% | 1.91 | -8.1% | 4.4% ⚠ | Finance |
| S | 6/7 | PTT | 6.2 | 10.6% | 0.98 | +3.6% | 7.4% ✓ | Energy |
| S | 6/7 | BBL | 6.1 | 7.4% | 7.00 | +30.0% | 22.6% ✓ | Banking |
| S | 6/7 | AMATA | 5.3 | 10.6% | 1.29 | +28.8% | 18.8% ✓ | Prop Dev |
| A | 5/7 | SAT | 10.7 | 11.0% | 0.20 | +1.6% | 11.6% ✓ | Automotive |
| A | 5/7 | ROJNA ⚠ | 10.2 | 9.6% | 1.05 | +25.7% | 32.2% ✓ | Prop Dev |
| A | 5/7 | ASIAN ⚠ | 9.8 | 14.3% | 0.15 | +15.8% | 29.9% ✓ | F&B |
| A | 5/7 | SCB | 8.5 | 10.6% | 6.05 | n/a | n/a | Banking |
| A | 5/7 | SCCC | 7.7 | 10.6% | 0.94 | +5.1% | 10.0% ✓ | Cement |
| A | 5/7 | KGI | 7.3 | 15.4% | 0.90 | +5.5% | 9.6% ✓ | Finance |
| A | 5/7 | KBANK | 7.1 | 9.2% | 5.77 | +44.1% | 44.1% ✓ | Banking |
| A | 5/7 | LANNA | 6.9 | **19.6%** | 0.33 | +50.4% | 121.9% ✓ | Energy |
| A | 5/7 | ALUCON | 6.7 | 13.1% | 0.13 | +4.7% | 6.3% ✓ | Packaging |
| A | 5/7 | SAK | 6.4 | 13.7% | 1.28 | +14.6% | 12.6% ✓ | Finance |
| A | 5/7 | AEONTS | 5.9 | 18.4% | 2.38 | +1.7% | 6.4% ✓ | Finance |
| A | 5/7 | PTTEP | 5.8 | 10.6% | 0.80 | +15.0% | 11.7% ✓ | Energy |
| B | 4/7 | CMR ⚠ | 16.8 | 9.5% | 0.87 | -1.0% | 3.7% ⚠ | Health |
| B | 4/7 | GVREIT | 11.6 | 7.6% | 0.36 | +0.9% | 12.1% ✓ | REIT |
| B | 4/7 | STANLY | 9.0 | 9.4% | 0.12 | +38.1% | 45.4% ✓ | Automotive |
| B | 4/7 | TPIPP | 9.0 | 13.6% | 0.89 | -27.3% | 0.8% ⚠ | Energy |
| B | 4/7 | KKP | 7.0 | 12.1% | 6.49 | +17.9% | 15.9% ✓ | Banking |
| B | 4/7 | QH 💎 | 6.4 | 9.9% | 0.39 | -2.6% | 5.6% ✓ | Prop Dev |
| B | 4/7 | TCAP 💎 | 6.0 | 9.6% | 0.80 | +3.9% | 7.2% ✓ | Banking |
| B | 4/7 | RATCH | 5.3 | 8.6% | 1.21 | -8.8% | 3.4% ⚠ | Energy |
| C | 3/7 | SC | 8.1 | 10.4% | 1.58 | -6.9% | 5.6% ✓ | Prop Dev |
| C | 3/7 | KTB ⚠ | 7.9 | 9.0% | 7.08 | +59.0% | 80.3% ✓ | Banking |
| C | 3/7 | JMT | 7.1 | 13.3% | 0.36 | -4.7% | 5.6% ✓ | Finance |
| C | 3/7 | NER | 7.0 | **26.7%** | 1.06 | -7.9% | 4.7% ⚠ | Agribusiness |
| C | 3/7 | LH | 6.8 | 15.7% | 1.68 | -15.9% | 2.9% ⚠ | Prop Dev |
| C | 3/7 | SCAP | 6.4 | 10.0% | 2.32 | -69.6% | 0.0% ⚠ | Finance |
| C | 3/7 | TTB | 5.9 | 8.0% | 5.97 | +37.0% | 28.4% ✓ | Banking |
| C | 3/7 | KYE ⚠ | 5.7 | 11.3% | 0.19 | +17.4% | 21.2% ✓ | Home Prod |
| C | 3/7 | SUC | 5.5 | 5.6% | 0.09 | +1.6% | 6.4% ✓ | Fashion |
| C | 3/7 | FPT | 5.0 | 5.0% | 1.59 | -1.5% | 4.6% ⚠ | Prop Dev |
| D | 2/7 | PROSPECT | 10.8 | 8.5% | 0.82 | -14.9% | 2.7% ⚠ | REIT |
| D | 2/7 | SIRI | 9.2 | 9.1% | 1.90 | +21.3% | 24.1% ✓ | Prop Dev |
| D | 2/7 | SPALI | 8.1 | 16.0% | 0.81 | +0.0% | 8.1% ✓ | Prop Dev |
| D | 2/7 | BAM | 7.5 | 8.1% | 2.03 | -2.4% | 6.7% ✓ | Finance |
| D | 2/7 | AP | 6.9 | 14.3% | 0.86 | +1.0% | 7.3% ✓ | Prop Dev |
| D | 2/7 | FTREIT | 6.4 | 6.2% | 0.43 | +2.9% | 7.4% ✓ | REIT |
| D | 2/7 | IMPACT | 5.8 | 5.9% | 0.27 | +55.9% | 46.8% ✓ | REIT |
| D | 2/7 | LHFG | 5.4 | 7.0% | 8.34 | +10.7% | 9.0% ✓ | Banking |
| D | 2/7 | MTI | 5.3 | 13.4% | 4.00 | +15.4% | 10.6% ✓ | Insurance |
| E | 1/7 | PRG | 8.4 | 5.1% | 0.24 | n/a | n/a | F&B |
| E | 1/7 | AYUD | 6.3 | 6.6% | 0.77 | +14.0% | 13.4% ✓ | Insurance |
| E | 1/7 | BPP | 5.2 | 9.4% | 0.77 | -2.0% | 4.7% ⚠ | Energy |
| **OUT** | 5/7 | MAJOR | 8.6 | 13.4% | 1.59 | -37.1% | 0.3% ⚠ | Media |
| **OUT** | 4/7 | RCL | 7.9 | 20.2% | 0.38 | +49.5% | 59.3% ✓ | Transport |
| **OUT** | 3/7 | CIMBT ⚠ | 15.9 | 3.2% | 9.02 | n/a | n/a | Banking |
| **OUT** | 3/7 | TU | 6.0 | 7.7% | 2.04 | -7.4% | 4.1% ⚠ | F&B |
| **OUT** | 3/7 | EGCO | 5.6 | 7.7% | 1.22 | -8.8% | 5.6% ✓ | Energy |
| **OUT** | 2/7 | METCO ⚠ | 10.8 | 6.1% | 0.43 | -5.4% | 2.2% ⚠ | Electronic |
| **OUT** | 1/7 | AIMIRT | 6.8 | 6.9% | 0.58 | -8.7% | 3.4% ⚠ | REIT |

**💎 = Hidden Value (Niwes #8) — algo flag confirmed**
**⚠ next to symbol = data warning · ⚠ next to proj yield = forward yield <5%**

## Hidden Value Result (Niwes #8)

Algo cache มี 5 ตัวรวม `data/hidden_value_holdings.json`:
- **QH** (อยู่ใน 55-list, Tier B 4/7) — ถือ HMPRO 19.87%, market value HMPRO > QH market cap
- **TCAP** (อยู่ใน 55-list, Tier B 4/7) — ถือ TMB 6.5% — hidden financial sector value
- MBK / INTUCH / DELTA — ไม่ผ่าน 5-5-5-5 filter (ไม่อยู่ใน 55-list)

**ข้อจำกัด:** algo cache มีแค่ 5 ตัวที่ hardcoded ไว้ — ไม่ได้ scan ทุกบริษัทอัตโนมัติว่าถือลูกใครเท่าไหร่ ต้อง manual research เพิ่มเอง

## Forward Yield Projection (Niwes #2)

**Method:** DPS 5y CAGR (2020-2024) × current price assume price flat → projected yield ปี 2029

**ตัวที่ project yield 2029 ≥ 5% (ผ่าน Niwes #2) จาก non-OUT tier:**
- Tier S+: HTC (7.9%)
- Tier S: ILM (16.9%) · PTT (7.4%) · BBL (22.6%) · AMATA (18.8%) — THANI fail (4.4%)
- Tier A: ส่วนใหญ่ผ่าน — ยกเว้น SCB (n/a)
- Tier B: หลายตัว forward yield ดิ่ง — CMR (3.7%) · TPIPP (0.8%) · RATCH (3.4%) — Niwes #2 fail

**Forward yield projection caveat:**
- DPS CAGR +50% ของ LANNA = coal price spike unsustainable → projection สูงผิดจริง
- CAGR +40-60% ของ KBANK / KTB / STANLY = recovery จาก COVID → projection อาจ overstate
- ใช้เป็น **direction signal** (โต/ทรง/ดิ่ง) ดีกว่าตัวเลข absolute

## Key Findings (2026-05-19)

1. **HTC = ตัวเดียวที่ได้ 7/7** ผ่านครบทุกข้อ Niwes ที่วัดเป็นเลขได้ — small-cap F&B (โค้กใต้) cash buffer แค่ 90M
2. **6 ตัว Tier S (6/7):** ILM · THANI · PTT · BBL · AMATA + HTC (7/7) — 6 sector ต่างกัน ครบ Niwes #12 diversification
3. **ROE 10% threshold หนักสำหรับ banks** — BBL ROE 7.4% ตก ROE filter แต่ Niwes รับ TCAP ROE 7-10% — ต้องคิด carve-out
4. **THANI Tier S แต่ Forward yield 4.4%** — DPS 3y strict ขึ้น แต่ 5y CAGR ลบ = pre-COVID DPS สูงกว่านี้ ตอนนี้ recovering แต่ยังไม่ถึง — strict 3y filter จับไม่ทัน
5. **NER ROE 26.7% (สูงสุด list) แต่ Tier C (3/7)** — quality ดีสุด แต่ rev/dps strict YoY ไม่ขึ้น + DPS CAGR ลบ = Niwes spirit ผ่าน แต่ recent growth fail
6. **Hidden Value cache จำกัด** — algo รู้แค่ 5 ตัว manual research ต่อได้
7. **7 ตัว tagged OUT** เพราะปีขาดทุน — บางตัวคะแนนสูงก่อนตัด (MAJOR 5/7, RCL 4/7)

## Anomalies / ต้องคิดต่อ

1. **NER (Tier C, 3/7)** ROE avg 10y = **26.7%** ดีสุดทั้ง list + ไม่เคยขาดทุน + D/E 1.06 — สูงสุดทุก quality metric แต่ score ต่ำเพราะ DPS+rev YoY ไม่ขึ้น strict + DPS CAGR ลบ. คุยกันต่อ
2. **LANNA / AEONTS** ROE 18-19% + D/E ต่ำ + ไม่ขาดทุน — anomaly เทียบ tier ตัวเอง
3. **BBL D/E 7.00 vs HTC 0.77** — Tier S ทั้งคู่ profile ตรงข้าม
4. **Banking ROE threshold 10% เกินไป** — TCAP/BBL ตก แต่ Niwes เคยซื้อ TCAP ROE 7-10% ตอนนั้น
5. **NER algo score ต่ำ vs ROE สูง** — algo มี bias ทาง streak weight
6. **MAJOR ขาดทุน 1/10 ปี COVID — แต่ pre/post COVID ROE 12-13%** — Niwes คงรอ recovery จริงไหม?

## Files ใน Session

| File | Purpose |
|---|---|
| `niwes-analysis-master.md` (this) | resume doc — เปิดอ่านไฟล์เดียว |
| `manual-niwes-ranking-2026-05-19.md` | ranking 55 stocks + ROE+D/E full data |
| `niwes-criteria-coverage-map.md` | 13 criteria + matrix coverage status |

## Backlog (priority order)

1. ✅ Hidden Value pull (done — limited cache 2 ตัวใน list)
2. ✅ Forward yield projection (done — DPS 5y CAGR method)
3. ✅ Re-rank with ROE + D/E (done — ext_score max 7)
4. ⏳ **ROE threshold carve-out** — bank vs non-bank (Niwes รับ bank ROE 7-10%)
5. ⏳ **NER anomaly investigation** — ROE 26.7% สูงสุด แต่ score ต่ำ ทำไม?
6. ⏳ **DPS 5y CAGR projection refinement** — strip out cyclical spike (LANNA coal / KBANK COVID recovery)
7. ⏳ **Manual hidden value research** — beyond algo cache 5 ตัว
8. ⏳ Moat tag manual review ตัว Tier S+ (qualitative)
9. ⏳ Daily-use tagging (qualitative)
10. ⏳ Cycle position (banking trough? energy peak?)
11. ⏳ Geographic diversification — portfolio construction
12. ⏳ ปรับ Max algo (long-term) — port manual filter chain เข้า algo

## How to Resume This Work

**Keyword to trigger:** "ต่อ niwes analysis" หรือ "ต่อ manual ranking"

**First step on resume:** เปิดไฟล์นี้ + `manual-niwes-ranking-2026-05-19.md` + `niwes-criteria-coverage-map.md`

**Source data:** `data/screener_2026-05-18.json` — ถ้ามี scan ใหม่ ใช้ตัวล่าสุด (`scan_*.md` + `screener_*.json`)

**ห้ามทำ:** อย่า rebuild algo Max ก่อนที่ manual lens stable — ใช้ manual เป็น ground-truth ก่อน

## Notes for Future Sessions

- อาร์ทไม่ชอบให้ AI "case-match" จาก case studies เก่า (CPALL/TCAP/QH) — ชอบให้ดูจาก fundamental จริง
- อาร์ทคิดว่า "เพิ่มทุกปี" (Niwes #6) สำคัญกว่า case-match
- อาร์ทตัดสินใจเรื่อง yield 5% floor strict (ไม่เอา growing exception) — เพราะ AWC 3.7% ผ่อนปลนเกินไป
- พูดภาษาคน ไม่พ่นศัพท์โปรแกรมเมอร์/stat
- ⚠ marker = data warning (yield spike / data anomaly) — Niwes ต้องเช็คก่อนเข้า
