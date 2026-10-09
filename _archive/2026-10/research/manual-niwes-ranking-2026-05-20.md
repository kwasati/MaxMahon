---
date: 2026-05-20
source: scan_2026-05-20.json (screener_2026-05-20.json)
method: re-rank with set.or.th source-aware snapshot DPS (v6.6.1 fix)
universe: 55 stocks ผ่าน 5-5-5-5 (algo screener, hard yield >=5%)
supersedes: manual-niwes-ranking-2026-05-19.md
---

# Manual Niwes Ranking — 2026-05-20 (Post Snapshot DPS Fix)

Re-rank ด้วย DPS ของจริงจาก set.or.th (ไม่ใช่ yahoo split-adjusted) — รอบนี้สำหรับหุ้นที่มี split (HTC/BBL/KBANK/AMATA) ⓓ check และ yield จะตรงกับความจริง

## Filter Chain

1. **Hard yield ≥ 5%** ปีล่าสุด (ตัด NIWES_GROWING exception) → 55 ตัวจาก 56
2. **5 binary checks (score max 5):**
   - ⓓ DPS ขึ้นทุกปี 3 ปี (2022→2023→2024) strict pairwise — **DPS source = set.or.th จริง** (ไม่ split-adjusted)
   - ⓡ รายได้ + กำไร ขึ้นทุกปี 3 ปี strict pairwise
   - OCF บวกทุกปี 3 ปี
   - FCF บวกทุกปี 3 ปี
   - OCF/NI 2024 ≥ 1.0 (กำไรกลายเป็นเงินสดจริง)

## Tier S — ผ่านครบ 5/5

| Sym | y% | PE | PBV | ⓓ | ⓡ | OCF+ | FCF+ | OCF/NI | Cash 24 | Sector | ⚠ |
|---|---:|---:|---:|:---:|:---:|:---:|:---:|---:|---:|---|:---:|
| BBL | 6.1 | 6.8 | 0.55 | ✓ | ✓ | ✓ | ✓ | 2.55 | 47.36B | Banking |  |

## Tier A — 4/5

| Sym | y% | PE | PBV | ⓓ | ⓡ | OCF+ | FCF+ | OCF/NI | Cash 24 | Sector | ⚠ |
|---|---:|---:|---:|:---:|:---:|:---:|:---:|---:|---:|---|:---:|
| ROJNA | 10.2 | 8.5 | 0.52 | ✓ | · | ✓ | ✓ | 1.34 | 4.73B | Property Development |  |
| ILM | 8.0 | 8.7 | 0.96 | · | ✓ | ✓ | ✓ | 2.34 | 0.21B | Commerce |  |
| HTC | 6.6 | 10.7 | 1.43 | · | ✓ | ✓ | ✓ | 1.81 | 0.09B | Food & Beverage |  |
| PTTEP | 5.8 | 10.8 | 1.13 | ✓ | · | ✓ | ✓ | 2.50 | 133.85B | Energy & Utilities |  |
| AMATA | 5.3 | 7.6 | 1.01 | ✓ | · | ✓ | ✓ | 2.73 | 2.52B | Property Development |  |

## Tier B — 3/5

| Sym | y% | PE | PBV | ⓓ | ⓡ | OCF+ | FCF+ | OCF/NI | Cash 24 | Sector | ⚠ |
|---|---:|---:|---:|:---:|:---:|:---:|:---:|---:|---:|---|:---:|
| CMR | 16.8 | 2.2 | 1.18 | · | · | ✓ | ✓ | 7.06 | 0.27B | Health Care Services | ⚠ |
| GVREIT | 11.6 | 10.5 | 0.67 | ✓ | · | ✓ | · | 1.43 | 0.08B | Property Fund & REITs |  |
| SAT | 10.7 | 8.7 | 0.76 | · | · | ✓ | ✓ | 1.66 | 1.45B | Automotive |  |
| ASIAN | 9.8 | 9.3 | 0.87 | · | · | ✓ | ✓ | 1.56 | 0.85B | Food & Beverage |  |
| STANLY | 9.0 | 8.8 | 0.78 | · | · | ✓ | ✓ | 1.52 | 2.00B | Automotive |  |
| SCB | 8.5 | 9.9 | 0.89 | ✓ | · | ✓ | · | 2.56 | n/a | Banking |  |
| SCCC | 7.7 | 11.0 | 1.23 | · | · | ✓ | ✓ | 2.60 | 5.41B | Construction Materials |  |
| KGI | 7.3 | 8.5 | 1.00 | · | · | ✓ | ✓ | 1.07 | 1.72B | Finance & Securities |  |
| KBANK | 7.1 | 9.3 | 0.80 | ✓ | · | ✓ | · | 4.39 | 356.68B | Banking |  |
| LANNA | 6.9 | 12.0 | 0.91 | · | · | ✓ | ✓ | 2.50 | 0.78B | Energy & Utilities |  |
| ALUCON | 6.7 | 9.6 | 1.32 | · | · | ✓ | ✓ | 1.27 | 0.53B | Packaging |  |
| QH | 6.4 | 8.4 | 0.49 | · | · | ✓ | ✓ | 2.11 | 1.46B | Property Development |  |
| SAK | 6.4 | 7.4 | 0.93 | ✓ | ✓ | · | · | 1.41 | 0.20B | Finance & Securities |  |
| PTT | 6.2 | 11.7 | 0.94 | · | · | ✓ | ✓ | 3.32 | 405.14B | Energy & Utilities |  |
| AEONTS | 5.9 | 7.5 | 0.85 | · | · | ✓ | ✓ | 1.63 | 2.80B | Finance & Securities |  |
| RATCH | 5.3 | 10.5 | 0.66 | · | · | ✓ | ✓ | 1.99 | 8.93B | Energy & Utilities |  |

## Tier C — 2/5

| Sym | y% | PE | PBV | ⓓ | ⓡ | OCF+ | FCF+ | OCF/NI | Cash 24 | Sector | ⚠ |
|---|---:|---:|---:|:---:|:---:|:---:|:---:|---:|---:|---|:---:|
| CIMBT | 15.9 | 5.3 | 0.25 | · | · | ✓ | ✓ | 0.41 | 5.57B | Banking | ⚠ |
| TPIPP | 9.0 | 9.8 | 0.41 | · | · | ✓ | · | 1.86 | 2.99B | Energy & Utilities |  |
| MAJOR | 8.6 | 7.8 | 1.11 | · | · | ✓ | · | 2.10 | 0.58B | Media & Publishing |  |
| RCL | 7.9 | 3.4 | 0.46 | · | · | ✓ | · | 1.38 | 10.41B | Transportation & Logistics |  |
| KTB | 7.9 | 9.8 | 1.02 | ✓ | · | · | · | 4.15 | 435.14B | Banking | ⚠ |
| TU | 6.0 | 9.5 | 0.97 | · | · | ✓ | ✓ | 1.00 | 8.33B | Food & Beverage |  |
| TCAP | 6.0 | 7.5 | 0.75 | ✓ | · | · | · | 1.10 | 9.47B | Banking |  |
| TTB | 5.9 | 10.1 | 0.86 | ✓ | · | · | · | 5.44 | 247.39B | Banking |  |
| EGCO | 5.6 | 13.0 | 0.62 | · | · | ✓ | ✓ | 0.74 | 35.44B | Energy & Utilities |  |
| SUC | 5.5 | 4.6 | 0.33 | · | · | ✓ | ✓ | 0.72 | 5.46B | Fashion |  |
| LHFG | 5.4 | 7.4 | 0.56 | · | ✓ | · | · | 1.23 | 4.67B | Banking |  |
| FPT | 5.0 | 5.9 | 0.40 | · | · | ✓ | · | 2.35 | 1.23B | Property Development |  |

## Tier D — 1/5

| Sym | y% | PE | PBV | ⓓ | ⓡ | OCF+ | FCF+ | OCF/NI | Cash 24 | Sector | ⚠ |
|---|---:|---:|---:|:---:|:---:|:---:|:---:|---:|---:|---|:---:|
| PROSPECT | 10.8 | 11.7 | 1.00 | · | ✓ | · | · | -6.14 | 0.02B | Property Fund & REITs |  |
| METCO | 10.8 | 5.2 | 0.77 | · | · | ✓ | · | 0.43 | 1.99B | Electronic Components | ⚠ |
| SIRI | 9.2 | 5.5 | 0.50 | · | · | · | · | 2.41 | 4.91B | Property Development |  |
| SC | 8.1 | 5.2 | 0.32 | · | · | · | · | 1.58 | 1.32B | Property Development |  |
| BAM | 7.5 | 11.9 | 0.48 | · | · | · | · | 4.51 | 1.75B | Finance & Securities |  |
| JMT | 7.1 | 13.4 | 0.51 | · | · | · | · | 2.95 | 1.10B | Finance & Securities |  |
| KKP | 7.0 | 10.0 | 1.00 | · | · | · | · | 3.98 | 1.34B | Banking |  |
| LH | 6.8 | 11.8 | 0.84 | · | · | · | · | 1.71 | 3.93B | Property Development |  |
| AIMIRT | 6.8 | 10.4 | 0.94 | · | ✓ | · | · | -0.45 | 0.60B | Property Fund & REITs |  |
| THANI | 6.7 | 8.2 | 0.70 | · | · | · | · | 8.57 | 3.69B | Finance & Securities |  |
| FTREIT | 6.4 | 13.6 | 1.04 | ✓ | · | · | · | 0.94 | 0.35B | Property Fund & REITs |  |
| SCAP | 6.4 | 8.4 | 0.66 | · | · | · | · | 5.21 | 2.45B | Finance & Securities |  |
| IMPACT | 5.8 | 14.8 | 1.03 | · | · | ✓ | · | 0.99 | 0.00B | Property Fund & REITs |  |
| KYE | 5.7 | 9.4 | 0.59 | · | · | · | · | 1.27 | 0.22B | Home & Office Products | ⚠ |

## Tier F — 0/5

| Sym | y% | PE | PBV | ⓓ | ⓡ | OCF+ | FCF+ | OCF/NI | Cash 24 | Sector | ⚠ |
|---|---:|---:|---:|:---:|:---:|:---:|:---:|---:|---:|---|:---:|
| PRG | 8.4 | 11.4 | 0.73 | · | · | · | · | 0.07 | 0.04B | Food & Beverage |  |
| SPALI | 8.1 | 7.2 | 0.52 | · | · | · | · | 0.21 | 5.12B | Property Development |  |
| NER | 7.0 | 5.3 | 0.82 | · | · | · | · | 0.60 | 0.22B | Agribusiness |  |
| AP | 6.9 | 5.4 | 0.50 | · | · | · | · | 0.43 | 2.57B | Property Development |  |
| AYUD | 6.3 | 5.5 | 0.98 | · | · | · | · | — | 3.09B | Insurance |  |
| MTI | 5.3 | 8.7 | 1.06 | · | · | · | · | — | 0.78B | Insurance |  |
| BPP | 5.2 | 4.2 | 0.63 | · | · | · | · | 0.23 | 7.59B | Energy & Utilities |  |

## ส่วนที่เปลี่ยนจาก 2026-05-19 (impact ของ snapshot DPS source-aware fix)

| Sym | Tier เก่า | Tier ใหม่ | ทิศ | y% ใหม่ | Score ใหม่ | เหตุผล |
|---|:---:|:---:|:---:|---:|:---:|---|
| HTC | S | A | DOWN | 6.6 | 4/5 | other check flip |
| PTTEP | B | A | UP | 5.8 | 4/5 | other check flip |
| KBANK | A | B | DOWN | 7.1 | 3/5 | other check flip |
| PTT | A | B | DOWN | 6.2 | 3/5 | other check flip |
| MAJOR | B | C | DOWN | 8.6 | 2/5 | other check flip |
| TU | B | C | DOWN | 6.0 | 2/5 | other check flip |
| TCAP | B | C | DOWN | 6.0 | 2/5 | other check flip |
| LHFG | D | C | UP | 5.4 | 2/5 | other check flip |
| KKP | C | D | DOWN | 7.0 | 1/5 | other check flip |
| AIMIRT | F | D | UP | 6.8 | 1/5 | other check flip |
| THANI | A | D | DOWN | 6.7 | 1/5 | other check flip |
| NER | D | F | DOWN | 7.0 | 0/5 | other check flip |

## Loss-year tagged OUT (ปีขาดทุนใน 10y → ตก list)

| Sym | Tier | y% | ปีขาดทุน | Sector |
|---|:---:|---:|:---:|---|
| CIMBT | C | 15.9 | 1 | Banking |
| METCO | D | 10.8 | 1 | Electronic Components |
| MAJOR | C | 8.6 | 1 | Media & Publishing |
| RCL | C | 7.9 | 3 | Transportation & Logistics |
| AIMIRT | D | 6.8 | 1 | Property Fund & REITs |
| TU | C | 6.0 | 1 | Food & Beverage |
| EGCO | C | 5.6 | 1 | Energy & Utilities |

## By-Sector Pick (top per sector by tier+yield)

| Sector | Pick | รอง | สำรอง |
|---|---|---|---|
| Agribusiness | **NER (7.0% · 0/5)** | — | — |
| Automotive | **SAT (10.7% · 3/5)** | STANLY (9.0% · 3/5) | — |
| Banking | **BBL (6.1% · 5/5)** | SCB (8.5% · 3/5) | KBANK (7.1% · 3/5) |
| Commerce | **ILM (8.0% · 4/5)** | — | — |
| Construction Materials | **SCCC (7.7% · 3/5)** | — | — |
| Electronic Components | **METCO⚠ (10.8% · 1/5)** | — | — |
| Energy & Utilities | **PTTEP (5.8% · 4/5)** | LANNA (6.9% · 3/5) | PTT (6.2% · 3/5) |
| Fashion | **SUC (5.5% · 2/5)** | — | — |
| Finance & Securities | **KGI (7.3% · 3/5)** | SAK (6.4% · 3/5) | AEONTS (5.9% · 3/5) |
| Food & Beverage | **HTC (6.6% · 4/5)** | ASIAN (9.8% · 3/5) | TU (6.0% · 2/5) |
| Health Care Services | **CMR⚠ (16.8% · 3/5)** | — | — |
| Home & Office Products | **KYE⚠ (5.7% · 1/5)** | — | — |
| Insurance | **AYUD (6.3% · 0/5)** | MTI (5.3% · 0/5) | — |
| Media & Publishing | **MAJOR (8.6% · 2/5)** | — | — |
| Packaging | **ALUCON (6.7% · 3/5)** | — | — |
| Property Development | **ROJNA (10.2% · 4/5)** | AMATA (5.3% · 4/5) | QH (6.4% · 3/5) |
| Property Fund & REITs | **GVREIT (11.6% · 3/5)** | PROSPECT (10.8% · 1/5) | AIMIRT (6.8% · 1/5) |
| Transportation & Logistics | **RCL (7.9% · 2/5)** | — | — |

## Full Ranking

| Tier | # | Sym | y% | PE | PBV | Score | ⓓ | ⓡ | OCF+ | FCF+ | OCF/NI | Cash24 | Loss10y | Sector | ⚠ |
|:---:|---:|---|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|---:|---:|:---:|---|:---:|
| S | 1 | BBL | 6.1 | 6.8 | 0.55 | 5/5 | ✓ | ✓ | ✓ | ✓ | 2.55 | 47.36B | 0 | Banking |  |
| A | 2 | ROJNA | 10.2 | 8.5 | 0.52 | 4/5 | ✓ | · | ✓ | ✓ | 1.34 | 4.73B | 0 | Property Development |  |
| A | 3 | ILM | 8.0 | 8.7 | 0.96 | 4/5 | · | ✓ | ✓ | ✓ | 2.34 | 0.21B | 0 | Commerce |  |
| A | 4 | HTC | 6.6 | 10.7 | 1.43 | 4/5 | · | ✓ | ✓ | ✓ | 1.81 | 0.09B | 0 | Food & Beverage |  |
| A | 5 | PTTEP | 5.8 | 10.8 | 1.13 | 4/5 | ✓ | · | ✓ | ✓ | 2.50 | 133.85B | 0 | Energy & Utilities |  |
| A | 6 | AMATA | 5.3 | 7.6 | 1.01 | 4/5 | ✓ | · | ✓ | ✓ | 2.73 | 2.52B | 0 | Property Development |  |
| B | 7 | CMR | 16.8 | 2.2 | 1.18 | 3/5 | · | · | ✓ | ✓ | 7.06 | 0.27B | 0 | Health Care Services | ⚠ |
| B | 8 | GVREIT | 11.6 | 10.5 | 0.67 | 3/5 | ✓ | · | ✓ | · | 1.43 | 0.08B | 0 | Property Fund & REITs |  |
| B | 9 | SAT | 10.7 | 8.7 | 0.76 | 3/5 | · | · | ✓ | ✓ | 1.66 | 1.45B | 0 | Automotive |  |
| B | 10 | ASIAN | 9.8 | 9.3 | 0.87 | 3/5 | · | · | ✓ | ✓ | 1.56 | 0.85B | 0 | Food & Beverage |  |
| B | 11 | STANLY | 9.0 | 8.8 | 0.78 | 3/5 | · | · | ✓ | ✓ | 1.52 | 2.00B | 0 | Automotive |  |
| B | 12 | SCB | 8.5 | 9.9 | 0.89 | 3/5 | ✓ | · | ✓ | · | 2.56 | n/a | 0 | Banking |  |
| B | 13 | SCCC | 7.7 | 11.0 | 1.23 | 3/5 | · | · | ✓ | ✓ | 2.60 | 5.41B | 0 | Construction Materials |  |
| B | 14 | KGI | 7.3 | 8.5 | 1.00 | 3/5 | · | · | ✓ | ✓ | 1.07 | 1.72B | 0 | Finance & Securities |  |
| B | 15 | KBANK | 7.1 | 9.3 | 0.80 | 3/5 | ✓ | · | ✓ | · | 4.39 | 356.68B | 0 | Banking |  |
| B | 16 | LANNA | 6.9 | 12.0 | 0.91 | 3/5 | · | · | ✓ | ✓ | 2.50 | 0.78B | 0 | Energy & Utilities |  |
| B | 17 | ALUCON | 6.7 | 9.6 | 1.32 | 3/5 | · | · | ✓ | ✓ | 1.27 | 0.53B | 0 | Packaging |  |
| B | 18 | QH | 6.4 | 8.4 | 0.49 | 3/5 | · | · | ✓ | ✓ | 2.11 | 1.46B | 0 | Property Development |  |
| B | 19 | SAK | 6.4 | 7.4 | 0.93 | 3/5 | ✓ | ✓ | · | · | 1.41 | 0.20B | 0 | Finance & Securities |  |
| B | 20 | PTT | 6.2 | 11.7 | 0.94 | 3/5 | · | · | ✓ | ✓ | 3.32 | 405.14B | 0 | Energy & Utilities |  |
| B | 21 | AEONTS | 5.9 | 7.5 | 0.85 | 3/5 | · | · | ✓ | ✓ | 1.63 | 2.80B | 0 | Finance & Securities |  |
| B | 22 | RATCH | 5.3 | 10.5 | 0.66 | 3/5 | · | · | ✓ | ✓ | 1.99 | 8.93B | 0 | Energy & Utilities |  |
| C | 23 | CIMBT | 15.9 | 5.3 | 0.25 | 2/5 | · | · | ✓ | ✓ | 0.41 | 5.57B | **1** | Banking | ⚠ |
| C | 24 | TPIPP | 9.0 | 9.8 | 0.41 | 2/5 | · | · | ✓ | · | 1.86 | 2.99B | 0 | Energy & Utilities |  |
| C | 25 | MAJOR | 8.6 | 7.8 | 1.11 | 2/5 | · | · | ✓ | · | 2.10 | 0.58B | **1** | Media & Publishing |  |
| C | 26 | RCL | 7.9 | 3.4 | 0.46 | 2/5 | · | · | ✓ | · | 1.38 | 10.41B | **3** | Transportation & Logistics |  |
| C | 27 | KTB | 7.9 | 9.8 | 1.02 | 2/5 | ✓ | · | · | · | 4.15 | 435.14B | 0 | Banking | ⚠ |
| C | 28 | TU | 6.0 | 9.5 | 0.97 | 2/5 | · | · | ✓ | ✓ | 1.00 | 8.33B | **1** | Food & Beverage |  |
| C | 29 | TCAP | 6.0 | 7.5 | 0.75 | 2/5 | ✓ | · | · | · | 1.10 | 9.47B | 0 | Banking |  |
| C | 30 | TTB | 5.9 | 10.1 | 0.86 | 2/5 | ✓ | · | · | · | 5.44 | 247.39B | 0 | Banking |  |
| C | 31 | EGCO | 5.6 | 13.0 | 0.62 | 2/5 | · | · | ✓ | ✓ | 0.74 | 35.44B | **1** | Energy & Utilities |  |
| C | 32 | SUC | 5.5 | 4.6 | 0.33 | 2/5 | · | · | ✓ | ✓ | 0.72 | 5.46B | 0 | Fashion |  |
| C | 33 | LHFG | 5.4 | 7.4 | 0.56 | 2/5 | · | ✓ | · | · | 1.23 | 4.67B | 0 | Banking |  |
| C | 34 | FPT | 5.0 | 5.9 | 0.40 | 2/5 | · | · | ✓ | · | 2.35 | 1.23B | 0 | Property Development |  |
| D | 35 | PROSPECT | 10.8 | 11.7 | 1.00 | 1/5 | · | ✓ | · | · | -6.14 | 0.02B | 0 | Property Fund & REITs |  |
| D | 36 | METCO | 10.8 | 5.2 | 0.77 | 1/5 | · | · | ✓ | · | 0.43 | 1.99B | **1** | Electronic Components | ⚠ |
| D | 37 | SIRI | 9.2 | 5.5 | 0.50 | 1/5 | · | · | · | · | 2.41 | 4.91B | 0 | Property Development |  |
| D | 38 | SC | 8.1 | 5.2 | 0.32 | 1/5 | · | · | · | · | 1.58 | 1.32B | 0 | Property Development |  |
| D | 39 | BAM | 7.5 | 11.9 | 0.48 | 1/5 | · | · | · | · | 4.51 | 1.75B | 0 | Finance & Securities |  |
| D | 40 | JMT | 7.1 | 13.4 | 0.51 | 1/5 | · | · | · | · | 2.95 | 1.10B | 0 | Finance & Securities |  |
| D | 41 | KKP | 7.0 | 10.0 | 1.00 | 1/5 | · | · | · | · | 3.98 | 1.34B | 0 | Banking |  |
| D | 42 | LH | 6.8 | 11.8 | 0.84 | 1/5 | · | · | · | · | 1.71 | 3.93B | 0 | Property Development |  |
| D | 43 | AIMIRT | 6.8 | 10.4 | 0.94 | 1/5 | · | ✓ | · | · | -0.45 | 0.60B | **1** | Property Fund & REITs |  |
| D | 44 | THANI | 6.7 | 8.2 | 0.70 | 1/5 | · | · | · | · | 8.57 | 3.69B | 0 | Finance & Securities |  |
| D | 45 | FTREIT | 6.4 | 13.6 | 1.04 | 1/5 | ✓ | · | · | · | 0.94 | 0.35B | 0 | Property Fund & REITs |  |
| D | 46 | SCAP | 6.4 | 8.4 | 0.66 | 1/5 | · | · | · | · | 5.21 | 2.45B | 0 | Finance & Securities |  |
| D | 47 | IMPACT | 5.8 | 14.8 | 1.03 | 1/5 | · | · | ✓ | · | 0.99 | 0.00B | 0 | Property Fund & REITs |  |
| D | 48 | KYE | 5.7 | 9.4 | 0.59 | 1/5 | · | · | · | · | 1.27 | 0.22B | 0 | Home & Office Products | ⚠ |
| F | 49 | PRG | 8.4 | 11.4 | 0.73 | 0/5 | · | · | · | · | 0.07 | 0.04B | 0 | Food & Beverage |  |
| F | 50 | SPALI | 8.1 | 7.2 | 0.52 | 0/5 | · | · | · | · | 0.21 | 5.12B | 0 | Property Development |  |
| F | 51 | NER | 7.0 | 5.3 | 0.82 | 0/5 | · | · | · | · | 0.60 | 0.22B | 0 | Agribusiness |  |
| F | 52 | AP | 6.9 | 5.4 | 0.50 | 0/5 | · | · | · | · | 0.43 | 2.57B | 0 | Property Development |  |
| F | 53 | AYUD | 6.3 | 5.5 | 0.98 | 0/5 | · | · | · | · | — | 3.09B | 0 | Insurance |  |
| F | 54 | MTI | 5.3 | 8.7 | 1.06 | 0/5 | · | · | · | · | — | 0.78B | 0 | Insurance |  |
| F | 55 | BPP | 5.2 | 4.2 | 0.63 | 0/5 | · | · | · | · | 0.23 | 7.59B | 0 | Energy & Utilities |  |

## Notes

- DPS ในรอบนี้ทุกตัว = source-of-truth set.or.th (non-split-adjusted) ไม่ใช่ yahoo อีกแล้ว
- ก่อนหน้านี้ 2026-05-19 ranking ใช้ yahoo split-adjusted → split stocks (HTC/BBL/KBANK/AMATA) ⓓ check ผิด
- รายการ ⚠ = `DATA_WARNING` หรือ `YIELD_SPIKE_FROM_PRICE_DROP` จาก algo screener
- ROE bar visualization + D/E table ใน 2026-05-19 ไม่ขึ้นในรอบนี้ (data ROE ไม่เปลี่ยนจาก fix นี้ — ดู `manual-niwes-ranking-2026-05-19.md` section ROE 10y)
