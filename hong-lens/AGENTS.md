# Hong Lens — Claude Instructions

## Codex Adapter [AUTO]

- ไฟล์นี้ sync มาจาก `C:\WORKSPACE\projects\4-MaxMahon\hong-lens\CLAUDE.md` — CLAUDE.md คือกฎต้นฉบับ, AGENTS.md คือสำเนาสำหรับ Codex
- ก่อนทำงานจริง ต้องอ่าน Claude memory ตัวจริง: `C:\Users\kwasa\.claude\projects\C--WORKSPACE\memory\MEMORY.md`
- ถ้า memory ชี้ไปไฟล์ย่อย ให้ resolve จาก `C:\Users\kwasa\.claude\projects\C--WORKSPACE\memory`
- ถ้าระหว่างงานมีบทเรียน/กฎ/บริบทใหม่ ต้อง merge กลับเข้า CLAUDE.md + Claude MEMORY.md ตัวจริง ไม่เก็บไว้แค่ฝั่ง Codex
- ห้ามถือไฟล์ใต้ `C:\WORKSPACE\.claude\memory-backpack\` เป็นตัวจริง ถ้ายังไม่เทียบกับ path memory ด้านบน

## Purpose

Sub-project ใน MaxMahon สำหรับคัดหุ้นไทยแนว **เซียนฮง สถาพร งามเรืองพงศ์** (Hybrid Value/Growth) — ใช้สำหรับส่วน **25%** ของพอร์ตอาร์ท (Niwes 70 / Hong 25 / Cash 5)

**Goal:** หาหุ้นไทยที่ pattern ตรงสไตล์เซียนฮง (Sweet Spot growth + ROE สูง + valuation ถูก) — ไม่ใช่ลอกพอร์ตเซียนฮงตรงๆ (พอร์ตจริงของแก ส่วนใหญ่ fail filter เพราะแกตัดสินใจ holistic ไม่ mechanical)

## Position in MaxMahon

- **MaxMahon main pipeline** = Niwes Dividend-First (ปันผลเพิ่มทุกปี + 5-pillar score)
- **Hong Lens (sub-folder นี้)** = standalone tool — borrow data layer ของ MaxMahon มา scan
- **ห้ามแก้ Niwes scoring/ranking module** — Hong scanner standalone อยู่แค่ `scripts/hong_stage1_scanner.py`

## เซียนฮง Philosophy — 9 Criteria ที่ verified

Primary (Kaohoon source):
1. D/E ≤ 1x (ค้าปลีกเกินได้ถ้าเจ้าหนี้การค้า)
2. เงินสดในมือพอจ่ายหนี้ระยะสั้น + ปันผล
3. Gross + Net margin trend (เทียบ peer)
4. Cash flow ≈ Net profit
5. ROE relative to industry

Secondary (book):
6. กำไรสุทธิทำ all-time high ต่อเนื่อง
7. กำไรโต ~26%/ปี ต่อเนื่อง 3 ปี
8. Forward PE ≤ 15x
9. Dividend yield 4-7%/ปี

Concept: PEG growth/PE ≥ 1.5 (= PEG ≤ 0.67)

Research source: `C:\WORKSPACE\_shared\docs\research-sianhong-stock-picking.md`

## Pipeline — 2 Stage

### Stage 1: Auto Scan (script ทำเอง)
- Universe: SET only (mai ตัดออก — 703 ตัว via thaifin)
- **7 Hard Gates** (Gate 2 cash adequacy SKIP — data MaxMahon ไม่มี short-term debt แยก, ใช้ SET balance sheet manual แทน):
  1. D/E sector-aware (retail ≤ 2.5 / bank ROA ≥ 1% / default ≤ 1)
  2. ~~Cash adequacy~~ — SKIP (manual via SET factsheet)
  3. Margin slope (gm + nm 3y ≥ 0)
  4. CFO/NP ≥ 0.8
  5. ROE relative industry (≥ industry median OR floor 12%)
  6. กำไรทำ new high ใน 5y
  7. Forward PE ≤ 15
- **Sweet Spot Composite** (rank survivors): CAGR 40% + Yield 30% + PEG 30%
- Script: `C:\WORKSPACE\projects\4-MaxMahon\scripts\hong_stage1_scanner.py` (--version v5)

### Stage 2: Manual Review (in-chat กับ user)
- เซียนฮง 3 ข้อ ผู้บริหาร: **ซื่อสัตย์ + เก่ง + มีไฟ**
  - ซื่อสัตย์ → กลต./ตลท. enforcement history + related party + ค่าใช้จ่าย vs peer
  - เก่ง → ROE proxy + capital allocation + track record
  - มีไฟ → Opportunity Day video + investor presentation
- **Cash Adequacy manual check** (Gate 2 ที่ skip)
- Data source: SET official factsheet + companyprofile ที่อาร์ท download มา (`hong-lens/data/`)

## Critical Lessons — ห้ามลืม

### 1. MaxMahon data ไม่ trust 100% — ต้อง audit SET official ก่อน
- บางตัว latest year = 2024 (thaifin lag) → false positive เพราะ filter "กำไร new high" ผ่านโดย default
- **MASTER lesson:** ROE 2022 = 105% (early IPO equity ต่ำ → distort) + ไม่มี 2025 data → ผ่าน filter ของกำมือเปล่า / SET official ROE 2025 = 5.70% (กำไรปี 2025 ลดลง!)
- **TKN lesson:** เหมือน MASTER — MaxMahon 2024 = 836MB / SET 2025 = 409MB (ตก 51%) → ผ่าน filter เพราะ data หาย

### 2. Audit Workflow (สำคัญสุด)
ก่อนลง Stage 2 manual ของหุ้นใด → audit ก่อนเสมอ:
1. ดู MaxMahon `yearly_metrics[-1].year` = 2024 หรือ 2025?
2. ดู ROE ปี 2020-2022 มีค่า > 50% ไหม (distortion early IPO)
3. ขอ SET factsheet จากอาร์ท
4. เทียบ ROE 2025 + NP 2025 vs MaxMahon
5. ถ้า fail → ตัดทิ้ง flag "MASTER-like"

### 3. ห้ามเดา 100%
- ถ้า data ไม่มี → บอก user ว่าไม่มี + ขอ verify มือ (download SET factsheet)
- ห้ามใช้ proxy / fallback / rule of thumb
- ตัวอย่างผิด: 30% × total_debt = short-term debt → ผิด → 651 stocks fail filter เปล่าๆ

## Active Stock Lists

### Verified 12 — ผ่าน Hong filter จริง (SET 2025 confirmed)
NSL / KCG / MOSHI / PSP / TFM / COM7 / ICHI / OSP / TOA / SISB / KDH / TSC

### MaxMahon ล้าหลัง 1 ปี แต่ SET ยังโต = OK
KDH (NP +8% 2025) / TSC (NP +17% 2025)

### Cut — MASTER-like (MaxMahon data หาย 2025, ของจริง fail)
- **TKN**: NP 2024 = 836MB → 2025 = 409MB (ตก -51%) / ROE 36% → 18%
- **MASTER**: ROE 2022 distorted 105% / 2025 ROE = 5.70% / NP ลด

## Files

```
hong-lens/
├── CLAUDE.md             # ไฟล์นี้ — context for AI session
├── MEMORY.md             # decisions + lessons accumulated
├── README.md             # human-readable overview
├── set-factsheets/       # 14 ไฟล์ — factsheet จาก SET (HTML .xls)
├── set-companyprofiles/  # 14 ไฟล์ — companyprofile จาก SET
└── research/             # output ของ Stage 2 extraction + audit reports
```

Note: ไม่ใช้ subfolder `data/` ภายในเพราะ MaxMahon `.gitignore` rule `data/` จะ match recursive (ครอบทุก `data` directory ใน repo)

External:
- Scanner script: `../scripts/hong_stage1_scanner.py`
- Research master: `C:\WORKSPACE\_shared\docs\research-sianhong-stock-picking.md`

## Rules

1. **ห้ามเดา** — ทุก criterion ต้องใช้ data จริงจาก SET/MaxMahon cache
2. **Audit SET official ก่อน trust MaxMahon** — เฉพาะหุ้นใหม่ที่จะ deep dive
3. **mai = ตัดออก** — เซียนฮงเล่นได้แต่ user ขอ SET only (703 ตัว)
4. **ห้ามแก้ Niwes module** — Hong scanner standalone
5. **Pool target 30-50 ตัวก่อน manual** — ตอนนี้ 29 (SET-only after mai cut)
