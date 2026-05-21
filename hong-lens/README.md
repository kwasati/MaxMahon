# Hong Lens

> คัดหุ้นไทยแนวเซียนฮง สถาพร งามเรืองพงศ์ — สำหรับ 25% ของพอร์ตอาร์ท

## Position in Portfolio

| Allocation | Strategy |
|------------|----------|
| **70%** | Niwes 5-5-5-5 Dividend-First (= MaxMahon main pipeline) |
| **25%** | **Hong Lens** ← sub-project นี้ |
| **5%** | Cash |

## What is Hong Lens

เซียนฮง = Hybrid Value/Growth investor — ไม่ pure value (ไม่เน้นปันผลอย่างเดียวแบบ Niwes) ไม่ pure long-hold (ไม่ถือชาตินี้แบบ Buffett) — เน้น **Sweet Spot growth phase** ของบริษัท

= หาหุ้นที่ "กำลังเร่งตัว" ไม่ใช่ "อยู่ตัวแล้ว"

Pattern ที่เซียนฮงมอง:
- **กำไรโต 26%/ปี ต่อเนื่อง 3 ปี**
- **PE ต่ำกว่า 15** (ยังไม่ถูก market price in growth)
- **D/E < 1** (หนี้น้อย ไม่เปราะ)
- **ROE สูง** (ผู้บริหารเก่ง)
- **CFO ≈ Net Profit** (กำไรจริง ไม่ใช่กระดาษ)
- **ผู้บริหาร: ซื่อสัตย์ + เก่ง + มีไฟ**

## Workflow

```
SET universe (703 ตัว)
  ↓
[Stage 1] Auto Scan — 7 Hard Gates
  ↓
~29 ตัว pool
  ↓
SET Official Audit (เทียบ MaxMahon vs SET factsheet)
  ↓
12 ตัว verified
  ↓
[Stage 2] Manual Review — เซียนฮง 3 ข้อ + Cash Adequacy
  ↓
5-10 ตัวสุดท้าย → Watchlist
  ↓
Entry 30:30:30:10 → Cut loss -8% → Exit at thesis-break
```

## Folder Structure

```
hong-lens/
├── CLAUDE.md             ← AI session context
├── MEMORY.md             ← decisions + lessons accumulated
├── README.md             ← (this file)
├── set-factsheets/       ← 14 ไฟล์ factsheet จาก SET (HTML .xls)
├── set-companyprofiles/  ← 14 ไฟล์ companyprofile จาก SET
└── research/             ← Stage 2 extraction + audit reports
    └── stage2-12-stocks-2026-05-21.md  ← mini-cards 12 verified stocks
```

External files:
- **Scanner:** `../scripts/hong_stage1_scanner.py`
- **Cache:** `../data/screener_cache/{date}/{SYM}.BK.json`
- **Hong research:** `../../../_shared/docs/research-sianhong-stock-picking.md`

## Current Stock Lists (2026-05-21)

### Verified 12 ตัว (ผ่าน Hong filter + SET 2025 confirmed)

NSL · KCG · MOSHI · PSP · TFM · COM7 · ICHI · OSP · TOA · SISB · KDH · TSC

### Cut 2 ตัว (MASTER-like — MaxMahon data หาย, SET 2025 fail)

- **TKN** — กำไร 2025 ตก 51%
- **MASTER** — ROE 2025 = 5.7% (ลดลงจาก 15.66%)

## How to Continue (Future Sessions)

1. อ่าน `CLAUDE.md` → understand context
2. อ่าน `MEMORY.md` → ดู decisions + lessons ล่าสุด
3. Check active list ใน `MEMORY.md` → "Verified 12"
4. ถ้าจะ rerun scanner → `py ../scripts/hong_stage1_scanner.py --universe all --version v5`
5. ถ้า audit หุ้นใหม่ → ให้ user download SET factsheet + companyprofile มาเก็บที่ `data/`
6. Stage 2 manual review → คุยกับอาร์ทในแชท ทีละตัว

## Rules

- ห้ามเดา (ตัวเลข, sector, market)
- Audit SET official ก่อน trust MaxMahon ทุกครั้ง
- ห้ามแก้ Niwes scoring/ranking module
- mai stocks ตัดออก
- ผู้บริหาร 3 ข้อ = Stage 2 manual (กลต. enforcement / Opp Day / 56-1)
