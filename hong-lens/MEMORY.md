# Hong Lens — Memory (decisions + lessons)

> Accumulated state for continuation across sessions

## Timeline

### 2026-05-21 — Session Day 1 (Hong Lens setup)

**Direction:**
- อาร์ทแบ่งพอร์ต **70 / 25 / 5** = Niwes / Hong / Cash
- Hong lens 25% = sub-project ใน MaxMahon ใช้ data layer ที่มี

**Hong Philosophy verified** (research file `_shared/docs/research-sianhong-stock-picking.md`):
- 9 criteria (5 primary Kaohoon + 4 secondary book)
- Entry: 30:30:30:10
- Cut loss: -8%
- ผู้บริหาร 3 ข้อ: ซื่อสัตย์ + เก่ง + มีไฟ
- พอร์ตจริงเซียนฮง ≠ filter mechanical (case study: KTC, OR, DITTO, PTL)

**Scanner iterations:**
- v1: SET100 strict — 4 ตัว (เข้มไป)
- v2: sector-aware D/E (retail ≤ 2.5 / bank ROA ≥ 1%) — 6 ตัว
- v3: all SET+mai universe (841) — 18 ตัว
- v4: full 7 hard gates + composite — 10 ตัว (cash adequacy proxy 30% เข้มไป)
- **v5 (current):** Gate 2 cash adequacy SKIP → 39 ตัว (SET+mai) → 29 ตัว (SET only)

**Composite weight:** CAGR 40% + Yield 30% + PEG 30% — เน้น growth ตามสไตล์เซียนฮง

**Universe decision:** SET only (mai ตัด 229 ตัว) — อาร์ทเลือกเอง

## Verified Stock Lists

### ✅ TRUST 10 — MaxMahon data ตรง SET เป๊ะ (audit ผ่าน)
NSL / KCG / MOSHI / PSP / TFM / COM7 / ICHI / OSP / TOA / SISB

### ⚠️ NEEDS_2025_OK 2 — MaxMahon ล้าหลัง 1 ปี แต่ SET 2025 ยังโต
KDH (NP +8%) / TSC (NP +17%)

### 🚨 CUT batch 1 — MASTER-like (MaxMahon data หาย 2025, ของจริง fail)
- **TKN** — MaxMahon 2024 NP 836MB → SET 2025 NP 409MB (-51%) / ROE 36% → 18%
- **MASTER** — MaxMahon ROE 2022 distort 105% / SET 2025 ROE 5.70% / กำไรลด

### 🚨 CUT batch 2 — Real red flags (Stage 2 review 2026-05-21)
- **ICHI** — PEG 7.72 (analyst forward expect growth ชะลอ — ตรงข้าม Hong sweet spot)
- **NSL** — Family concentration 72.7% (control extreme — too risky for minority)
- **KCG** — Cash 0.07x (liquidity weak ผิดปกติแม้สำหรับ F&B retailer)

### ✅ FINAL 9 — Verified pass Stage 1+2 ของ Hong Lens (2026-05-21)
**COM7 / MOSHI / PSP / TFM / OSP / TOA / SISB / KDH / TSC**

### Stage 3 — คัดเหลือ 4 ตัว (อาร์ทตัดสินใจ 2026-05-21)
จาก 9 ตัว → คัดให้เหลือ **4 ตัวสุดท้าย** สำหรับ 25% portfolio allocation
Position sizing Hong 30:30:30:10 ต่อตัว ในกรอบ 25% (= ~6.25% ต่อตัว)

## Critical Lessons

### Lesson 1 — MaxMahon thaifin data lag
ตัวที่ thaifin ยังไม่ load 2025 → `yearly_metrics[-1].year = 2024` → filter "กำไร new high" ผ่านโดย default เพราะไม่เห็นปี 2025 ที่กำไรลด

**Mitigation:** ก่อน trust filter ของ stock ใด → audit `yearly_metrics[-1].year` ต้อง = 2025 ถ้า 2024 → ต้องดู SET official ก่อน

### Lesson 2 — ROE Early-IPO distortion
บริษัทที่ IPO ใหม่ equity ต่ำมาก → ROE ปี 2020-2022 อาจ > 50-100% (distorted)
ถ้าค่าผิดอยู่ใน 3y window ที่ใช้คำนวณ avg → score เพี้ยน

**Mitigation:** ดู ROE per year — ถ้ามีปี > 50% → flag distorted

### Lesson 3 — Cash Adequacy ห้ามใช้ proxy
MaxMahon cache ไม่มี `short_term_debt` แยก → agent เดิมเดา "30% × total_debt" → 651 stocks fail เปล่าๆ
**Decision:** Gate 2 SKIP ใน auto scan + manual check ผ่าน SET balance sheet ใน Stage 2

### Lesson 4 — ห้ามเดาเด็ดขาด (กฎ workspace)
อาร์ทย้ำหลายรอบ — ถ้า data ไม่มี = report + ขอ manual ไม่ใช่ใช้ proxy/rule of thumb

### Lesson 5 — Hong portfolio ≠ filter mechanical
เซียนฮง portfolio จริง (TISCO/JMT/IVL/MALEE/SINGER) ส่วนใหญ่ fail Hong filter ของเรา 2-4 criteria
= filter เราคือ "pattern matching" ไม่ใช่ "ลอกพอร์ต"

### Lesson 6 — เปลี่ยน weight ดู rerun ก่อนตัดสิน
COM7 ROE 39% สูงสุดในกลุ่ม แต่ rank #34 เพราะ CAGR 10% ต่ำ + composite weight CAGR 40%
= ปรัชญาเซียนฮง "Sweet Spot growth" ทำให้ mature ROE-high stock ตก rank ถูกแล้ว

## Data Issues & Workarounds

| Issue | Workaround |
|-------|-----------|
| MaxMahon `yearly_metrics` lag 1 ปี (some stocks) | Audit SET official ก่อน |
| ROE early IPO distortion | Check per-year, flag > 50% |
| `short_term_debt` ไม่อยู่ใน cache | SET factsheet balance sheet manual |
| `dividends_paid` per year = null | ใช้ DPS × outstanding shares หรือ companyprofile |
| `current_ratio` per year = null (banks) | Snapshot only (yahoo top-level field) |
| `forward_pe` หายในบาง mid/small cap | Fallback trailing PE (track via `fwd_pe_source` column) |

## Stage 2 Extraction (2026-05-21) — Done

12 mini-cards extracted from SET official factsheet + companyprofile → `research/stage2-12-stocks-2026-05-21.md`

**Fields ที่ extract ได้:**
- A Identity (name/sector/listed/IPO/fiscal year/dividend policy)
- B Top 5 shareholders + categorize + family-combined detection (same surname heuristic)
- C Board (Chairman/CEO/Independent count/Full list)
- D Cash Adequacy 2025 (cash / short-debt / current liab)
- E Recent Events (top 5 news + capital movement)
- F Performance Trend (Revenue/NP/ROE/Margin 2023-2025)
- Bonus: Dividend history

**Fields ที่ extract ไม่ได้ (N/A across all):**
- Business description — `companyprofile.xls` ไม่มี field นี้ (มีแต่ metadata + securities info) — ต้อง manual ดู
- Annual dividend paid — SET CF table มีแค่ Operating/Investing/Financing aggregate ไม่แยก dividend row → ratio `Cash / (Short-debt + Dividend)` คำนวณไม่ได้

**Cash Adequacy ผลตาม Hong rule (cash ≥ short-debt):**
- ✅ PASS: NSL (1.96x), TFM (3.19x), TOA (19.62x), OSP (29.08x)
- ✅ Trivial PASS (short-debt = 0): ICHI, SISB, TSC, MOSHI, KDH
- ❌ FAIL: KCG (0.07x), PSP (0.30x), COM7 (0.30x)

**Family-combined ownership detected (same surname top 1 + relatives):**
- ICHI: ภาสกรนที 41.60% (4 holders)
- NSL: อัศวปิยานนท์ 72.71% (concentration risk สูงมาก)
- TSC: จุฬางกูร 40.44%
- OSP: โอสถานุเคราะห์ 29.93%
- PSP: KRONGPHANICH 25.74%

**Special:**
- TSC fiscal year = 30/09 (ต่างจากตัวอื่น 31/12) — "2025" = Oct 2024-Sep 2025
- TFM = controlled by Thai Union Group 51% (institutional, not family)

## Open Decisions

- [ ] Stage 2 user review — กูประมวลผล mini-cards ใน chat ทีละตัว user score 3 ข้อ
- [ ] Cash Adequacy reconcile — agent ใช้ `cash / short-debt` (ไม่รวม dividend) แต่ Hong original = `cash / (short-debt + dividend)`. Dividend paid annual extract ไม่ได้จาก SET CF aggregate → ต้องหา source อื่น (DPS × shares outstanding?) หรือยอมรับ proxy
- [ ] Position sizing — เซียนฮง 30:30:30:10 จะ apply ใน 25% Hong allocation ยังไง
- [ ] Business description manual lookup — companyprofile.xls ไม่มี → ต้องไปอ่าน 56-1 annual report หรือ company website

## Cross-references

- **CLAUDE.md** — context for AI session resume
- **README.md** — human-readable overview
- **Hong philosophy research:** `C:\WORKSPACE\_shared\docs\research-sianhong-stock-picking.md`
- **Scanner script:** `../scripts/hong_stage1_scanner.py`
- **MaxMahon main:** `../CLAUDE.md` + `../DESIGN.md`
- **Workspace global:** `C:\WORKSPACE\.claude\CLAUDE.md` + `C:\Users\kwasa\.claude\projects\C--WORKSPACE\memory\MEMORY.md`
