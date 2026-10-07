# MaxMahon Niwes Refactor v2 — Design Spec

**Status:** Phase 1 (Spec) — Stage 1-6 ออกแบบเสร็จครบ (Stage 7 ตัดทิ้ง 2026-05-15)
**Created:** 2026-05-14
**Anchor:** `C:\WORKSPACE\reMarkable\scripts\tmp\niwes-book\chapters\ch01-ch08.md` (Niwes 8-chapter — first principle)

---

## 1. เป้าหมาย (Target)

**ทำได้:** รื้อ MaxMahon pipeline ใหม่ตาม Niwes 8 บท — ทุก 933 หุ้นได้ analysis report ครบ + ป้ายตามมิติ Niwes + score ที่สื่อ portfolio role + Claude วิเคราะห์ลึก on-demand

**Observable end-state:**
- ทุกตัวมี profile + ป้ายครบทุก stage (ไม่ตัดทิ้ง)
- Display: home filter ตามคะแนน / search ได้ทุกตัวรวม FAIL
- Score ใหม่ตอบโจทย์ "หุ้นคะแนนสูง แต่จัดเข้าพอร์ตได้จริง"
- Dictionary หน้าคำศัพท์ — ป้าย+ศัพท์เฉพาะทุกตัวเปิดดูคำอธิบายได้

---

## 2. รายละเอียด (Details)

### 2.1 Architecture ใหม่ — 4 Layer

```
[933 หุ้น]
   |
   v
L1: Hard Filter 5-5-5-5  ->  PASS / REVIEW / FAIL (สถานะ — ไม่ตัด)
   |
   v
L2: 6 Stage Tag Classification  ->  ทุกตัวได้ป้าย + raw data ครบ
   |
   v
L3: Scoring (redesign — TBD)
   |
   v
L4: Display
   - Home list = filter เฉพาะ PASS+REVIEW
   - Search = เปิดดูได้ทุกตัวรวม FAIL
   |
   v
L5: Claude Opus deep analyze (on-demand, prompt redesign)
```

**หลักการ:**
- ทุก stage ไม่มี "ตัดทิ้ง" — ทุก signal เป็น tag/flag ให้ user filter เอง
- Niwes red flag (OCF negative, ปันผลก้อนเดียว, D/E พุ่ง, GM erosion, ROE ผันผวน, CEO ใหม่นอก industry) = tag warning ไม่ใช่ hard FAIL

### 2.2 6 Stage Framework (จาก Niwes 8 บท)

| Stage | บท Niwes | คำถาม | สถานะ design |
|-------|----------|-------|--------------|
| 1 | ch2 | ราคาถูกพอ? (Margin of Safety) | ✅ เสร็จ |
| 2 | ch3 | ปันผลจ่ายต่อเนื่อง? | ✅ เสร็จ |
| 3 | ch4 | Cash flow จริง? | ✅ เสร็จ |
| 4 | ch5 | มี moat? | ✅ เสร็จ |
| 5 | ch6-7 | ถือยาวได้? | ✅ เสร็จ |
| 6 | ch3+existing | Hidden value? | ✅ เสร็จ |

### 2.3 Stage 1 — ราคาถูกพอ (FINAL — approved + backfilled 2026-05-14)

**Source:** Niwes ch2 — Margin of Safety + 3 สัญญาณของถูก

#### Raw data ที่เก็บให้ทุกหุ้น

**Snapshot fields (top-level dict — unit ตามใน data_adapter.py):**

| Field (output) | data_adapter source field | Unit | คำอธิบาย |
|---|---|---|---|
| `pe_current` | `pe_ratio` | ratio (12.5) | P/E ปัจจุบัน |
| `pb_current` | `pb_ratio` | ratio | P/B ปัจจุบัน |
| `eps_current` | `eps_trailing` | THB/share | กำไรต่อหุ้น |
| `yield_current` | `dividend_yield` | **percent (4.5)** | ปันผล % ปัจจุบัน |
| `yield_5y_avg` | `five_year_avg_yield` | **percent** | ปันผล % เฉลี่ย 5 ปี |
| `sector` | `sector` (thaifin string) | string | เช่น "Energy & Utilities" |
| `industry` | `industry` (thaifin string) | string | เช่น "Resources" |
| `price` | `price` | THB | ราคาปัจจุบัน |

**Yearly + computed fields:**

| Field (output) | Source | คำอธิบาย |
|---|---|---|
| `pe_history_5y` | `yearly_metrics[].close / .diluted_eps` | P/E รายปี 5 ปี (คำนวณ) |
| `pe_5y_median` | คำนวณจาก `pe_history_5y` | **ใช้ median ไม่ใช่ mean** (กัน COVID 2020-22 skew) |
| `pe_5y_min`, `pe_5y_max` | คำนวณ | สำหรับ context display |
| **`sector_pe_median`** | precompute table (universe scan per industry) | **ไม่มีใน data_adapter ปัจจุบัน — ต้องสร้างใหม่** |
| **`fair_value`** | `eps_current × sector_pe_median` | คำนวณ |
| **`mos_pct`** | `(fair_value - price) / fair_value × 100` | คำนวณ |

#### Sector mapping (industry-based — real thaifin string)

**ASSET_HEAVY (P/B ใช้ได้):**
```
industry ∈ {
  'Financials',
  'Property & Construction',
  'Resources',           # Energy & Utilities, Mining
  'Industrials',
  'Agro & Food Industry'
}
```

**ASSET_LIGHT (P/B ใช้ไม่ได้):**
```
industry ∈ {
  'Technology',
  'Services',
  'Consumer Products'
}
```

**Override symbols** (infrastructure ใน Services parent):
```
ASSET_HEAVY_EXCEPTIONS = {'AOT', 'BTS', 'BEM'}  # toll/airport/mass transit
```

**Unknown sector** (`sector == '-'`, ~24% ของ universe): default ASSET_LIGHT + `UNKNOWN_SECTOR` warning tag

#### ป้ายที่แปะ (8 ป้าย — เพิ่ม UNKNOWN_SECTOR + DATA_INCOMPLETE_PE)

| Tag | เงื่อนไข | ที่มา Niwes |
|-----|---------|-------------|
| `MOS_30PLUS` | mos_pct ≥ 30% **AND** sector_pe_median available | ch2 EPS×PE method |
| `MOS_50PLUS` | mos_pct ≥ 50% **AND** sector_pe_median available | ของถูกชัด |
| `MR_MARKET_DISCOUNT` | pe_current < **pe_5y_median** × 0.7 (median ไม่ใช่ mean) | ch2 สัญญาณ 1 |
| `OVERVALUED_VS_SELF` | pe_current > pe_5y_median × 2.0 | inverse signal |
| `ASSET_HEAVY` | industry ∈ HEAVY set OR symbol ∈ ASSET_HEAVY_EXCEPTIONS | ch2 สัญญาณ 2 gate |
| `ASSET_LIGHT` | industry ∈ LIGHT set AND symbol ∉ exceptions | ch2 exclusion |
| `PB_DISCOUNT` | pb_current < 1.0 **AND** ASSET_HEAVY **AND** roe_current ≥ 5% | ch2 สัญญาณ 2 + quality gate |
| `YIELD_ABOVE_SELF` | yield_current > yield_5y_avg × 1.3 | ch2 สัญญาณ 3 (self history) |
| `UNKNOWN_SECTOR` (warning) | sector == '-' หรือไม่อยู่ใน mapping | data quality flag |
| `DATA_INCOMPLETE_PE` (warning) | sector_pe_median == None OR years_of_data < 5 | data quality flag |

#### Real-world test (SETSMART Layer 0 chain — 2026-05-14)

**Source:** `fetch_fundamentals(symbol)` chain SETSMART (snapshot Q4 audit) → thaifin (history) → yahoo (events)

| หุ้น | PE | EPS (Q4 audit) | sector_pe_median | fair_value | MoS% | PB | ROE% | industry | dy% | y5avg | Tags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **PTT** | 11.23 | 3.15 | 15.0 (default) | 47.25 | 24.3% | 0.90 | 7.93 | Resources | 6.43 | 5.66 | `ASSET_HEAVY`, `PB_DISCOUNT` (ROE ผ่าน gate) |
| **SCC** | 19.95 | **5.28** | 15.0 (default) | **79.20** | **-195%** (premium มหาศาล) | 0.83 | **1.77** | Property & Construction | 2.14 | 3.68 | `ASSET_HEAVY`, **NO `PB_DISCOUNT`** (ROE 1.77% ตก 5% gate) |
| **CPALL** | 14.06 | **2.77** | 15.0 (default) | **41.55** | -7% (เกือบ fair) | 2.87 | 21.31 | Services | 3.71 | 2.31 | `MR_MARKET_DISCOUNT`, `ASSET_LIGHT`, `YIELD_ABOVE_SELF` |

**Verified:**
- ✓ Sector mapping (PTT=Resources, SCC=Property & Construction, CPALL=Services)
- ✓ MR_MARKET_DISCOUNT trigger ตาม PE history (CPALL 14 < median 5y × 0.7)
- ✓ ROE gate ช่วย — SCC PB 0.83 + ROE 1.77% (Q4 audit ลดจาก thaifin 4%) → ไม่ติด PB_DISCOUNT (กัน value trap) **— ROE Q4 finalised ทำให้ rule strong กว่าเดิม**
- ✓ CPALL MoS -7% (เดิม +4% ใน thaifin) → SS audit EPS 2.77 < TF 3.10 → ไม่ติด MOS_30PLUS = ตรงเจตนา Niwes (ราคาใกล้ fair ไม่ใช่ของถูก)
- ⚠ Sector P/E median ใช้ default 15 → ต้อง precompute จริง (Phase A3)

**SETSMART vs thaifin (key flips):**
- SCC EPS 11.73 (TF YTD noisy) → **5.28** (SS Q4 audit) — fair value 175→79, MoS -33% → **-195%** (ราคาแพงกว่ามูลค่าจริงเยอะ)
- CPALL EPS 3.10 → **2.77** → MoS 4.3% → -7% (เดิม MOS_30PLUS ก็ไม่ติด, ปัจจุบันยังไม่ติด)
- SCC ROE 4% → **1.77%** → strong reject PB_DISCOUNT

#### Edge cases (must handle)

| Case | Behavior |
|---|---|
| **IPO < 5 ปี** (years_of_data < 5) | skip pe_5y_median tags + flag `DATA_INCOMPLETE_PE` |
| **ไม่จ่ายปันผล** (yield_current == 0) | skip YIELD_ABOVE_SELF |
| **NP ติดลบ** ใน eps_current | mos_pct = N/A (fair_value ติดลบ ไม่ใช้) + flag `EPS_NEGATIVE` |
| **sector == '-'** | default ASSET_LIGHT + flag UNKNOWN_SECTOR |
| **sector_pe_median == None** (sector ใหม่/หุ้นเดียวในกลุ่ม) | skip MOS tags + flag DATA_INCOMPLETE_PE |
| **PE_5y_median พังจาก COVID outliers** | trim outlier ก่อน median (95th/5th percentile) — fallback: ใช้ pe_5y_min × 2 + pe_5y_max × 0.5 → mid range |

#### Code reference (implementation roadmap)

**Files ต้องแตะ:**
1. `scripts/data_adapter.py` — เพิ่ม `pe_history_5y` คำนวณจาก `yearly_metrics[].close / .diluted_eps` (existing fields)
2. `scripts/fetch_data.py::_build_aggregates` (lines 127-194) — เพิ่ม `pe_5y_median`, `sector_pe_median_lookup`
3. **NEW file:** `scripts/sector_pe_precompute.py` — universe scan compute median ต่อ industry → save `data/sector_pe_median.json` (refresh weekly)
4. `scripts/screen_stocks.py::assign_signals` (lines 565-632) — เพิ่ม 8 tag ใหม่
5. `scripts/screen_stocks.py::quality_score` (replace existing valuation_score lines 234-284)

**Sector mapping constants:** add ที่ `scripts/sector_taxonomy.py` (NEW file)

#### Decision log (Stage 1)

1. **Fair Value + MOS%** — Niwes ch2 หัวใจ (EPS × industry P/E = fair, MOS = ส่วนลด)
2. **Industry-based mapping** ไม่ใช่ sector name — ใช้ 8 industry value จริงจาก thaifin (PTT=Resources, SCC=Property & Construction) — generic name {FIN/ENERG/...} ที่เสนอตอนแรกผิด
3. **PE_5y_median ไม่ใช่ mean** — COVID 2020-22 ทำให้ mean skew (CPALL mean PE 29.6 vs median ~16) — median ทนต่อ outlier
4. **PB_DISCOUNT + ROE gate ≥ 5%** — SCC PB 0.83 + ROE 4% เคยติด tag ผิด (PB ต่ำเพราะ business เสื่อม ไม่ใช่ของถูก) — เพิ่ม gate quality check
5. **YIELD self history** ไม่ใช่ bond spread — Niwes ตัวอย่างเทียบ "ปีก่อน 4% ปีนี้ 6.7%"
6. **Symbol override exceptions** — AOT/BTS/BEM ใน Services parent แต่ infrastructure asset-heavy → manual whitelist
7. **กลุ่มสินทรัพย์เบาไม่ "ข้าม"** — ข้ามแค่ PB_DISCOUNT (Niwes บอกห้ามใช้กับ tech/IP) — ป้ายอื่นได้ครบ

### 2.4 Stage 2 — ปันผลต่อเนื่อง (FINAL — approved + backfilled 2026-05-14)

**Source:** Niwes ch3 — หุ้นปันผลที่ดี ไม่ใช่หุ้นที่ปันผลสูงสุด

**Niwes ปักธง:**
- จ่ายต่อเนื่อง ≥10 ปีไม่ขาด + ค่อยๆ เพิ่มขึ้น
- 3 คำถาม: กี่ปีต่อเนื่อง / มี miss ไหม / ROE คงที่หรือดีขึ้น
- Yield Trap = yield สูงเพราะราคาตก ไม่ใช่ปันผลขึ้น

#### Raw data ที่เก็บให้ทุกหุ้น

**Snapshot:**

| Field (output) | data_adapter source | Unit | คำอธิบาย |
|---|---|---|---|
| `yield_current` | `dividend_yield` | percent | ปันผล ปัจจุบัน |
| `yield_5y_avg` | `five_year_avg_yield` | percent | ปันผล 5y avg |
| `payout_ratio_current` | `payout_ratio` | decimal (0-1) | DPS/EPS |
| `fcf_current` | `free_cashflow` | THB | FCF |
| `roe_current` | `roe` | decimal | ROE |
| `de_current` | `debt_to_equity` ÷ 100 | ratio | snapshot ต้อง ÷ 100 (unit gotcha) |
| `interest_coverage` | `latest_interest_coverage` (aggregates) | ratio | EBIT/Interest |
| `price_1y_return` | computed จาก yahoo price history | percent | -20% trigger |

**Yearly history (re-use across stages):**

| Field (output) | data_adapter source | คำอธิบาย |
|---|---|---|
| `dps_history_10y` | `dividend_history` dict → array | DPS รายปี 10y |
| `eps_history_10y` | `yearly_metrics[].diluted_eps` | EPS รายปี 10y |
| `roe_history_6y` | `yearly_metrics[].roe` × 100 (decimal→percent) | ROE 6y |
| `ocf_history_10y` | `yearly_metrics[].ocf` | สำหรับ Stage 3 link |

**Computed signals (เพิ่มใน `_build_aggregates`):**

| Field (output) | Formula | คำอธิบาย |
|---|---|---|
| `consecutive_years_paid` | count consecutive years จาก newest ที่ DPS > 0 **AND** DPS_yoy_drop < 30% | นับต่อเนื่อง + ไม่ลดเกิน 30% |
| `consecutive_no_cut` | count consecutive years ไม่มี cut > 30% YoY | strict variant |
| `years_paid_in_10y` | count year ที่ DPS > 0 ใน 10 ปี | sparsity check |
| `dps_rising_ratio` | (# transitions DPS_i ≥ DPS_i-1) / 9 transitions × 100 | % ปีที่ DPS เพิ่ม |
| `dps_avg_yoy_growth` | arithmetic mean ของ (DPS_i - DPS_i-1) / DPS_i-1 ปี-ต่อ-ปี | growth ปีละ % เฉลี่ย |
| `dps_5y_cagr` | (DPS[-1]/DPS[-5])^(1/4) - 1 | CAGR 5y (สำหรับ DIVIDEND_SHRINKING) |
| `roe_recent_3y_avg` | mean(roe_history_6y[-3:]) | 3 ปีล่าสุด |
| `roe_earlier_3y_avg` | mean(roe_history_6y[-6:-3]) | 3 ปีก่อนหน้า |
| `roe_6y_spread` | max(roe_6y) - min(roe_6y) | สำหรับ ROE_STABLE |
| `fcf_coverage` | fcf_current / sum(dividends_paid 1y) | ratio (gotcha: thaifin no dividends_paid field — ต้องคำนวณจาก DPS × shares) |
| `net_debt` | `total_debt` - `cash` (yearly_metrics ล่าสุด) | THB |
| `net_debt_ebitda` | net_debt / `ebitda` (yearly_metrics ล่าสุด) | ratio |

#### Industry-based payout threshold (replace generic name)

```python
PAYOUT_THRESHOLD_BY_INDUSTRY = {
    'Technology': 0.70,            # Tech
    'Services': 0.80,              # default (Commerce/Health/Tourism/Trans/etc.)
    'Financials': 0.75,            # Finance/Bank/Insurance
    'Resources': 1.00,             # Energy & Utilities (Utility-like)
    'Industrials': 0.80,
    'Property & Construction': 1.00,  # REIT-like + property
    'Consumer Products': 0.70,
    'Agro & Food Industry': 0.80,
    'default': 0.80,               # fallback
}
```

#### Net Debt/EBITDA threshold (split by ASSET class)

```python
NET_DEBT_EBITDA_THRESHOLD = {
    'ASSET_HEAVY': 6.0,   # HEAVY ปกติ leverage สูง (PTT 4x, CPALL 6x ปกติ)
    'ASSET_LIGHT': 3.0,   # LIGHT ปกติ leverage ต่ำ
}
```
*Reason:* Test เจอ PTT 4.01x / SCC 15.4x / CPALL 6.6x — threshold เดิม 4.0x ทำให้ HEAVY industry false positive

#### ป้ายที่แปะ (10 ป้าย — เพิ่ม DIVIDEND_SHRINKING)

**Dividend continuity tier (mutually exclusive):**

| Tag | เงื่อนไข | ที่มา |
|-----|---------|------|
| `GROWING_DIVIDEND` | consecutive_no_cut ≥10y + rising_ratio ≥70% + avg_yoy_growth ≥3% | ch3 บริษัท A |
| `STABLE_PAYER` | consecutive_no_cut ≥10y + ตก growth criteria (rising 40-70% OR growth 0-3%) | ch3 |
| `DIVIDEND_SHRINKING` (NEW) | consecutive_paid ≥10y **แต่** dps_5y_cagr < -3% | SCC pattern — กัน "stable" misnomer |
| `NEW_PAYER` | consecutive_no_cut 3-9 ปี | ch3 |
| `INTERMITTENT` | consecutive < 3 ปี OR years_paid_in_10y < 8 OR มี miss ใน 5 ปีล่าสุด | ch3 บริษัท B/Y |

**Yield Trap (3-of-5 rule — standard practitioner):**

| Tag | เงื่อนไข |
|-----|---------|
| `YIELD_TRAP` | ตก ≥3 ใน 5 ข้อ |

5 ข้อเช็ค:
1. `payout_ratio_current > PAYOUT_THRESHOLD_BY_INDUSTRY[industry]`
2. `fcf_coverage < 1.0` (FCF/dividends paid)
3. `yield_current > sector_yield_median × 2` OR `> 8%` absolute
4. `net_debt_ebitda > NET_DEBT_EBITDA_THRESHOLD[asset_class]` (split HEAVY 6 / LIGHT 3)
5. `price_1y_return < -20%`

**ROE trend (orthogonal):**

| Tag | เงื่อนไข |
|-----|---------|
| `ROE_IMPROVING` | roe_recent_3y_avg > roe_earlier_3y_avg + roe_current ≥ 10% |
| `ROE_STABLE` | roe_6y_spread < **10%** (เดิม 5% เข้มเกิน) + roe_6y avg ≥ 10% |
| `ROE_DECLINING` | roe_recent_3y_avg < roe_earlier_3y_avg |

#### Real-world test (SETSMART chain — 2026-05-14)

**Source:** SETSMART snapshot + thaifin DPS history + yahoo special dividend events

| หุ้น | DPS 10y (last 5) | consecutive_no_cut | rising% | avg_yoy% | dps_5y_cagr | Continuity tag |
|---|---|---|---|---|---|---|
| **PTT** | 1.0, 2.0, 2.0, 2.1, 2.3 | partial (cut 2020) | 44% | 9.95% | +2.8% | `STABLE_PAYER` (rising < 70%) |
| **SCC** | 18.5, 8, 6, 5, 5 | partial | 11% | **-10.4%** | **-22%** | `DIVIDEND_SHRINKING` ✓ (เดิมติด STABLE_PAYER ผิด) |
| **CPALL** | 0.6, 0.75, 1.0, 1.35, 1.65 | partial (cut 2020) | 78% | 8.6% | +13% | `GROWING_DIVIDEND` (rising 78% + growth ผ่าน) |

**Yield Trap check (5 conditions):**

| หุ้น | payout% (SS audit) | fcf_cov | yield abs (SS) | net_debt/ebitda (threshold) | 1y price | YIELD_TRAP score |
|---|---|---|---|---|---|---|
| **PTT** | 73% (≤100% Resources) ✓ | 1.95x ✓ | 6.43% ✓ | 4.01x (HEAVY 6.0) ✓ | +5% ✓ | **0/5** ผ่าน |
| **SCC** | **95%** (SS EPS 5.28 → DPS 5/5.28) ✗ | -1.25 ✗ | 2.14% ✓ | 15.4x ✗ | +9% ✓ | **3/5 ✗ YIELD_TRAP** ⚠ (flip จาก thaifin EPS 11.73 → payout 42% เคยผ่าน) |
| **CPALL** | 60% (SS EPS 2.77 → 1.65/2.77) ✓ | 1.73x ✓ | 3.71% ✓ | 6.6x (LIGHT 3.0) ✗ | -19.8% (-20% threshold) ⚠ | 1-2/5 ผ่าน |

| หุ้น | roe_recent_3y | roe_earlier_3y | spread 6y | ROE tag |
|---|---|---|---|---|
| **PTT** | 8.7% | 10.8% | wide | `ROE_DECLINING` |
| **SCC** | **1.77% (SS Q4)** | 10.3% | wide | `ROE_DECLINING` (strong) |
| **CPALL** | 21.31% (SS) | 14.3% | wide | `ROE_IMPROVING` |

**Verified:**
- ✓ `DIVIDEND_SHRINKING` กัน SCC false positive `STABLE_PAYER` (DPS ตก 19→5)
- ✓ `consecutive_no_cut` (cut ≥30% = break) แทน raw count กิน history ทั้งหมด
- ✓ **SCC flip:** SETSMART EPS 5.28 (Q4 audit ลดจาก TF 11.73 YTD) → payout 95% ตก gate 1 → **กลายเป็น YIELD_TRAP 3/5** — Niwes intuition ตรง (SCC ปันผลไม่ปลอดภัย)
- ✓ Sector payout threshold (industry-based) — Resources 100% / Services 80% — ใช้แล้วเทียบได้
- ✓ Net Debt/EBITDA split — PTT 4x ผ่าน HEAVY (6 threshold) / CPALL 6.6x ตก LIGHT (3 threshold) — แต่ CPALL ใน ASSET_HEAVY_EXCEPTIONS = ใช้ threshold HEAVY 6.0 → CPALL 6.6x ตกผ่าน (borderline)
- ⚠ `ROE_STABLE` ขยับ 5%→10% spread — เดิม spread 5% Thai cyclical ไม่ trigger เลย

**SETSMART vs thaifin (key flips):**
- SCC payout 42% (TF) → **95%** (SS Q4 audit) → ติด YIELD_TRAP 3/5
- SCC ROE 4% → 1.77% → ROE_DECLINING strong
- ADVANC yield 4.05% (TF) → **9.80%** (SS includes TT&T special div) → จะติด YIELD_ABOVE_SELF เพิ่ม (อยู่ใน Stage 5 5 หุ้น set)

#### Edge cases (must handle)

| Case | Behavior |
|---|---|
| **ไม่จ่ายปันผล** (DPS history empty) | tags ทั้งหมด N/A + flag `NO_DIVIDEND` (warning) |
| **History < 3y** (IPO ใหม่) | flag `DATA_INCOMPLETE_DIVIDEND` + skip continuity tier |
| **History 3-9y** | NEW_PAYER tier — skip GROWING_DIVIDEND (ต้อง 10y) |
| **DPS = 0 ในปีล่าสุด แต่ history ≥10y** | flag `RECENT_DIVIDEND_HALT` (warning ก่อน confirm) |
| **EBITDA ≤ 0** (loss year) | net_debt_ebitda = N/A → skip yield_trap rule 4 |
| **dividends_paid field ไม่มีใน thaifin** | คำนวณ fcf_coverage = `fcf / (dps × shares_outstanding)` |
| **payout > 100%** (จ่ายเกินกำไร) | ติด yield_trap rule 1 ทันที (ไม่ต้องเทียบ threshold) |
| **ROE history < 6y** | skip ROE_STABLE (ต้อง 6y window) + ใช้ ROE_IMPROVING/DECLINING ด้วย 3y avg available |

#### Code reference (implementation roadmap)

**Files ต้องแตะ:**
1. `scripts/fetch_data.py::_build_aggregates` (lines 127-194) — เพิ่ม `consecutive_no_cut`, `dps_rising_ratio`, `dps_avg_yoy_growth`, `dps_5y_cagr`, `roe_recent_3y_avg`, `roe_earlier_3y_avg`, `roe_6y_spread`, `fcf_coverage`, `net_debt`, `net_debt_ebitda`
2. `scripts/sector_taxonomy.py` (NEW) — `PAYOUT_THRESHOLD_BY_INDUSTRY`, `NET_DEBT_EBITDA_THRESHOLD`, `ASSET_HEAVY_INDUSTRIES`, etc.
3. `scripts/screen_stocks.py::assign_signals` (lines 565-632) — เพิ่ม 10 tag ใหม่ (replace existing `NIWES_GROWING`, `YIELD_SPIKE_FROM_PRICE_DROP`, `DIVIDEND_TRAP`)
4. `scripts/screen_stocks.py::dividend_score` (lines 146-231) — rewrite ตาม Niwes 5-pillar (50pts → ค่อย redesign Stage 2.8)

#### Decision log (Stage 2)

1. **consecutive_no_cut แทน consecutive_paid** — SCC จ่าย 25 ปีแต่ DPS ลด 19→5 ใน 8 ปี = ผิดเจตนา Niwes "ค่อยๆ เพิ่ม" — เพิ่ม cut ≥30% = break streak
2. **DIVIDEND_SHRINKING tag ใหม่** — SCC pattern (consecutive ≥10y แต่ shrinking) ไม่ควรเรียก "STABLE" — ป้ายแยก
3. **Industry-based payout threshold** — replace generic name (Tech/Finance/Utility) → real industry 8 ค่า
4. **Net Debt/EBITDA split HEAVY/LIGHT** — test เจอ PTT 4x ปกติ heavy industry ไม่ใช่ red flag — threshold ต้อง sector-aware
5. **ROE_STABLE spread 5%→10%** — Thai cyclical wide → 5% ไม่ trigger เลย — 10% reasonable
6. **fcf_coverage calculation** — thaifin ไม่มี `dividends_paid` field → คำนวณจาก `DPS × shares_outstanding` (verify availability)
7. **Threshold 3%/ปี** — Niwes ตัวอย่างใช้ 5% แต่ไม่ปักธง — ใช้ 3% เพื่อ inclusive (อาร์ทตัดสิน 2026-05-14)
8. **Yield Trap = 3-of-5** — research มาตรฐาน (Benzinga / CFA L2 / Sahm Capital)
9. **ROE แยก orthogonal** ไม่ใช่ gate GROWING_DIVIDEND — informative อยู่ตัวเอง

### 2.5 Stage 3 — Cash flow จริง (FINAL — approved + backfilled 2026-05-14)

**Source:** Niwes ch4 — กำไรเป็นความเห็น / Cash flow คือข้อเท็จจริง

**Niwes ปักธงชัด:**
- OCF (เงินสดดำเนินงาน) < 50% ของ Net Profit = "เริ่มระวัง"
- OCF ติดลบทั้งที่ Net Profit บวก = "red flag เดินหนี"
- ดู 3 ปีย้อนหลัง — ต้องบวก + ไม่ลดลง
- ตัวอย่างอสังหาฯ: NP 200→250→300 ล้าน vs OCF -100→-300→-500 ล้าน → ปีที่ 4 หยุดจ่ายปันผล + ราคาตก 80%

#### Raw data ที่เก็บให้ทุกหุ้น

| Field (output) | data_adapter source | Unit | คำอธิบาย |
|---|---|---|---|
| `net_profit_history_5y` | `yearly_metrics[].net_income` | THB | NP 5 ปี (extend จาก 3 → fallback 3 ถ้า data ไม่ครบ) |
| `ocf_history_5y` | `yearly_metrics[].ocf` | THB | OCF 5 ปี |
| `ocf_to_np_ratio_5y` | คำนวณ each year | ratio | OCF/NP รายปี |
| `ocf_to_np_avg_3y` | mean(ocf_to_np[-3:]) | ratio | เฉลี่ย 3 ปีล่าสุด (primary) |
| `ocf_to_np_avg_5y` | mean(ocf_to_np) | ratio | เฉลี่ย 5 ปี (secondary verify) |
| `ocf_negative_count_3y` | count(ocf < 0) ใน 3 ปีล่าสุด | int | สำหรับ FAKE_PROFIT |
| `ocf_yoy_decline_pct` | (ocf[-1] - ocf[-3]) / ocf[-3] | percent | magnitude ของการลด 3 ปี |
| `ocf_consecutive_declining_years` | count consecutive YoY drops จาก newest | int | สำหรับ DETERIORATING |

**Formula RESOLVED 2026-05-17** — เปลี่ยนเป็น **OCF ÷ EBITDA (Cash Conversion Ratio)**

Root cause ของ OCF/NP ratio 3.4-3.6x: OCF total (รวม subsidiary) ÷ NI to parent (หัก minority) = ฐานไม่ match. Tested both fix paths (agent A + B 2026-05-17):
- ❌ Formula A — compute NI_total (parent + minority): ratio ยังพุ่ง 3.00 avg (minority = equity accounting ไม่ใช่ cash scaling) — NOT VIABLE
- ✅ Formula B — OCF/EBITDA (CCR): ratio 0.67-0.96 บน 5 หุ้น — VIABLE + matches industry CCR normal range

**Compute:** EBITDA = (Gross Profit - SG&A) + D&A — fields: thaifin `gp`, `sga`, `da` ครบ (16 ปี coverage)

**Threshold ใหม่** (เปลี่ยนจาก Niwes 0.80/0.50 บน OCF/NP): ≥0.7 healthy / 0.5-0.7 acceptable / <0.5 warning — EBITDA ใหญ่กว่า NI ~1.5-2x → ratio shift left, CCR 0.7 ≈ OCF/NI 0.8-0.9 healthiness intent

#### ป้ายที่แปะ (5 ป้าย — 4 Level + 1 Trend orthogonal)

**Level tier (mutually exclusive):**

| Tag | เงื่อนไข | ที่มา Niwes |
|-----|---------|-------------|
| `CASHFLOW_HEALTHY` | OCF บวก 3 ปีติด **AND** ccr_avg_3y ≥ 0.70 | ch4 บริษัท A (CCR 0.7 ≈ Niwes OCF/NI 0.8) |
| `CASHFLOW_OK` | OCF บวก 3 ปีติด **AND** ccr_avg_3y 0.50-0.70 | interpolate |
| `CASHFLOW_BELOW_PROFIT` | ccr_avg_3y < 0.50 (≥ 2 ปีจาก 3 ตก) | ch4 "เริ่มระวัง" (CCR 0.5 ≈ OCF/NI 0.5) |
| `FAKE_PROFIT` | OCF ติดลบ ≥ 2 ปีใน 3 ปี **AND** NP บวก **AND** sector NOT in {Banking, Finance & Securities, Insurance} | ch4 red flag "ขายตั้งแต่ปีที่ 2" — banks excluded: bank cash flow accounting (loan disbursements drive OCF) ไม่ตรง Niwes context (industrial/retail/property). revised 2026-05-18 v1.1: bank exclusion |

**Trend (orthogonal — แปะคู่กับ Level ได้):**

| Tag | เงื่อนไข |
|-----|---------|
| `CASHFLOW_DETERIORATING` | OCF ลด ≥2 ใน 2 transitions (3 ปี) **AND** ocf_yoy_decline_pct ≤ -20% (magnitude gate) |

**Decline magnitude gate** = ป้ายไม่ trigger แค่ stable downward drift — ต้องลดเกิน 20% จาก peak 3 ปี

#### Real-world test (SETSMART chain — 2026-05-14)

**Source:** thaifin yearly_metrics (OCF + NP history — SETSMART chain uses thaifin for history > 1y)

| หุ้น | NP 3y (B THB) | OCF 3y (B THB) | OCF/NP avg | OCF neg count | OCF 3y decline | Tags |
|---|---|---|---|---|---|---|
| **PTT** | 112, 90, 90 | 382, 373, 299 | 3.62x ⚠ | 0 | -22% | `CASHFLOW_HEALTHY` + `CASHFLOW_DETERIORATING` (magnitude -22% ผ่าน gate) |
| **SCC** | 26, 6.3, 14 | 44, 36, 43 | 3.48x ⚠ | 0 | -2% | `CASHFLOW_HEALTHY` (no DETERIORATING — magnitude ผ่าน gate) |
| **CPALL** | 18, 25, 28 | 87, 76, 74 | 3.45x ⚠ | 0 | **-38%** (recent 2y avg vs earlier 3y avg per SS re-test) | `CASHFLOW_HEALTHY` + `CASHFLOW_DETERIORATING` (flip จาก thaifin -15% — SS sees deeper deceleration) |

⚠ **OCF/NP ratio 3.4-3.6x ทั้ง 3 ตัว = สงสัย definition mismatch** — ต้อง verify ก่อน implement (อาจต้องเปลี่ยน formula เป็น OCF/EBITDA — Phase A2 verify field meaning)

**Verified after magnitude gate:**
- ✓ PTT ติด DETERIORATING (decline -22%) — แสดงสัญญาณ OCF เริ่มถดถอย
- ✓ SCC ไม่ติด — decline เล็ก ไม่ใช่ true trend reversal
- ✓ **CPALL flip:** SETSMART re-test (recent 2y OCF/NI avg 2.82 vs earlier 3y avg 4.52 = drop 38%) → ติด DETERIORATING (thaifin window 3y เห็น -15% เฉพาะ raw trend, SS recent vs earlier comparison สะท้อนกว่า)

**SETSMART vs thaifin (Stage 3 flips):**
- CPALL OCF/NI: -15% raw 3y decline (TF) → **-38%** recent vs earlier comparison (SS lens) → ติด DETERIORATING
- NP definition mismatch (3.4-3.6x ratio) ยืนยันใน SS data → ต้อง switch formula เป็น `OCF/EBITDA` หรือ `OCF/pretax_income` ก่อน implement

#### Edge cases (must handle)

| Case | Behavior |
|---|---|
| **NP ติดลบ** ในปีใดปีหนึ่ง | ratio ปีนั้น = N/A (skip จาก ocf_to_np_avg) + flag `NP_NEGATIVE_YEAR` |
| **NP ติดลบ 2+ ปี ใน 3 ปี** | tags Stage 3 ทั้งหมด N/A + flag `CHRONIC_LOSS` (จัด Stage 5 ถือยาว) |
| **OCF ติดลบทุกปี** | ติด `FAKE_PROFIT` strong (เกินกว่า 1 ปี) |
| **OCF ติดลบ + NP ติดลบ ปีเดียวกัน** | ไม่ใช่ FAKE_PROFIT (NP ก็ติดลบจริง) — flag แยก `BUSINESS_LOSS_YEAR` |
| **History < 3y** | flag `DATA_INCOMPLETE_CASHFLOW` + skip Level tier |
| **EBITDA ≤ 0** (ถ้าใช้ OCF/EBITDA) | fallback OCF/NP ถ้า NP บวก |
| **CCR ratio > 2.0x** (กรณีผิดปกติ) | flag `CCR_OUTLIER` (debug) — review field meaning |

#### Code reference (implementation roadmap)

**Files ต้องแตะ:**
1. `scripts/fetch_data.py::_build_aggregates` — เพิ่ม `ocf_to_np_avg_3y`, `ocf_to_np_avg_5y`, `ocf_negative_count_3y`, `ocf_yoy_decline_pct`, `ocf_consecutive_declining_years`
2. `scripts/data_adapter.py` — verify `net_income` vs `ocf` definition (test ก่อน implement — อาจต้องเปลี่ยน NP source เป็น `pretax_income` หรือ `ebitda`)
3. `scripts/screen_stocks.py::cash_flow_score` (lines 287-331) — rewrite 10pts pillar ตาม Stage 3 framework
4. `scripts/screen_stocks.py::assign_signals` — เพิ่ม 5 tag ใหม่

#### Decision log (Stage 3)

1. **Threshold 50% + 0%** — Niwes ปักธงในบท (50% = "เริ่มระวัง" / 0% = "red flag") — ไม่ตั้งเอง
2. **80% layer** เพิ่ม — แยก "ดี" จาก "พอใช้" — standard practitioner
3. **OCF ≠ FCF** — Stage 2 yield_trap ใช้ FCF/dividends, Stage 3 ใช้ CCR (OCF/EBITDA) — คนละมุม Niwes ch4 พูด OCF ตรง
4. **Trend orthogonal** — แปะคู่ Level ได้ (เช่น "พอใช้ + แย่ลง")
5. **Formula = OCF/EBITDA (CCR)** — เลือก 2026-05-17 หลัง test 2 ทางแก้ (NI_total vs EBITDA): OCF/EBITDA viable + bypass minority issue + thaifin compute ได้ครบ. Threshold เลื่อนเป็น 0.7/0.5 (CCR equivalent ของ Niwes OCF/NI 0.8/0.5)
5. **Magnitude gate -20%** สำหรับ DETERIORATING — test เจอว่า PTT OCF ลด 382→373→299 ติด tag เกิน intention (mostly stable) — เพิ่ม magnitude gate กัน false positive
6. **5y history** (เดิม 3y) — เพิ่ม secondary verify + fallback 3y ถ้า data ไม่ครบ
7. **NP definition mismatch** — test เจอ OCF/NP 3.4-3.6x ผิดปกติ — verify field ก่อน implement (อาจ switch เป็น OCF/EBITDA หรือ pretax)

### 2.6 Stage 4 — Moat (FINAL — approved 2026-05-14)

**Source:** Niwes ch5 — Moat: หาบริษัทที่คู่แข่งทำลายไม่ได้

**Niwes ปักธงเชิงตัวเลข:**
- ROE ≥ 15% ติดต่อ 7-10 ปี = สัญญาณ moat ดีมาก
- Gross Margin คงที่/ขยับขึ้น = pricing power ยัง intact
- ระวัง ROE สูงเพราะกู้หนี้เยอะ = ไม่ใช่ moat แต่คือ risk
- Moat erosion (Kodak) — ROE เคยสูงแล้วลด = moat กำลังบางลง

**Niwes 5 ประเภท Moat (qualitative):** Brand / Cost / Network / Regulatory / Switching — ไม่ tag อัตโนมัติใน Stage 4 (qualitative) — Claude Opus L4 deep analyze จะ classify

#### Raw data ที่เก็บให้ทุกหุ้น

| Field | คำอธิบาย | Source |
|-------|---------|--------|
| `roe_history_10y` | ROE รายปี 10 ปี (extend จาก Stage 2 ที่ 6y) | thaifin (มี 16y) |
| `roe_consecutive_15plus_years` | จำนวนปีติดต่อ ROE ≥ 15% (from newest) | คำนวณ |
| `de_current` | D/E ปัจจุบัน | thaifin |
| `de_5y_avg` | D/E เฉลี่ย 5 ปี | คำนวณ |
| `gm_history_10y` | Gross Margin รายปี 10 ปี | thaifin |
| `gm_recent_3y_avg` | GM เฉลี่ย 3 ปีล่าสุด | คำนวณ |
| `gm_earlier_3y_avg` | GM เฉลี่ย 3 ปีก่อนหน้า (4-6 ย้อนหลัง) | คำนวณ |
| `gm_trend` | recent vs earlier (improving/stable/declining) | คำนวณ |
| `interest_expense_4y` | Interest Expense 4 ปี (yahoo limit) | yahoo `InterestExpense` |
| `ebit_4y` | EBIT 4 ปี — ใช้ field ตรง ไม่ใช่ OperatingIncome | yahoo `EBIT` |
| `interest_coverage_4y_avg` | EBIT / Interest Expense เฉลี่ย 4 ปี | คำนวณ |
| `net_debt_history_5y` | Total Debt - Cash & Equivalents | thaifin (มี 5-16y) |
| `net_debt_increases_in_3y` | จำนวน transitions ที่ Net Debt เพิ่ม (max 2) | คำนวณ |

#### ป้ายที่แปะ (5 ป้าย — 4 Moat tier + 1 Warning)

**Moat tier (mutually exclusive):**

| Tag | เงื่อนไข | ที่มา Niwes |
|-----|---------|-------------|
| `STRONG_MOAT` | ROE ≥ 15% ติดต่อ ≥ 7 ปี + GM คงที่/ขยับขึ้น | ch5 ปักธง |
| `MODERATE_MOAT` | ROE 10-15% ติดต่อ ≥ 5 ปี + GM คงที่ | (interpolate) |
| `NO_MOAT` | ROE ผันผวน หรือ < 10% + GM หดตัว | ch5 บริษัทสิ่งทอ |
| `MOAT_ERODING` | ROE เคยสูง แต่ลด 3 ปีล่าสุด + GM หดตัว | ch5 Kodak warning |

**Warning tag (orthogonal — แปะคู่ Moat tier ได้):**

| Tag | เงื่อนไข (AND ทั้ง 4) | ที่มา |
|-----|---------|------|
| `ROE_FUELED_BY_DEBT` | ROE ≥ 15% + D/E > 2.0 + Interest Coverage avg 4y < 3.0 + Net Debt เพิ่ม ≥ 2 ใน 3 transitions | ch5 Niwes warning + อาร์ท insight |

#### Real-world test (SETSMART chain — 2026-05-14)

**Source:** SETSMART snapshot (ROE/D/E latest Q4 audit) + thaifin history (ROE/GM 16y) + yahoo (Interest Exp + EBIT 4y)

| หุ้น | ROE Q4 audit | D/E (ratio) | Int. Cov | Net Debt 5y trend | Tag |
|---|---|---|---|---|---|
| **CPALL** | 21.31% (5y stable high) | 1.95 | 3.6x | +9% (mild) | `STRONG_MOAT` (ไม่ติด FUELED_BY_DEBT เพราะ Int.Cov > 3) |
| **PTT** | 7.93% (ลดต่อ 5y) | 1.08 | 5.5x | -18% (จ่ายคืน) | `MOAT_ERODING` (ROE+GM ลด) |
| **SCC** | **1.77%** (Q4 audit — เทรนด์ดิ่ง) | 1.05 | 2.8x | sideways | `NO_MOAT` (strong, ROE ดิ่งกว่าเดิมที่เห็นใน thaifin 4%) |

→ CPALL test สำคัญ — Niwes ในบทยกเป็น moat ตัวอย่าง, rule ใหม่ผ่าน ✓

**SETSMART vs thaifin (Stage 4 verdict ไม่ flip แต่ value strong กว่า):**
- SCC ROE 4% (TF) → 1.77% (SS Q4 audit) — NO_MOAT verdict เดิมยังถูก แต่ signal strong กว่า
- CPALL ROE 21% (TF) → 21.31% (SS) — เหมือนกัน, STRONG_MOAT verdict ผ่าน
- D/E percent vs ratio gotcha: SS snapshot `debt_to_equity` = 108 (percent) ↔ yearly_metrics `de_ratio` = 1.08 — Phase A1 normalize

#### Edge cases (must handle)

| Case | Behavior |
|---|---|
| **ROE history < 7y** (IPO ใหม่) | skip STRONG_MOAT (ต้อง 7y) — fallback MODERATE_MOAT ถ้ามี 5y |
| **EBIT ติดลบบางปี** | SCC pattern — Interest Coverage = N/A ปีนั้น → skip rule, ใช้ Net Debt trend อย่างเดียว |
| **Interest Expense = 0** (no debt) | Interest Coverage = inf → ผ่าน rule (จริง = ดี ไม่มีหนี้) |
| **Net Debt ติดลบ** (cash > debt) | net_debt_increases_in_3y = 0 → ผ่าน rule (cash-rich = ปลอดภัย) |
| **GM history < 6y** | skip MOAT_ERODING (ต้องเทียบ 3y recent vs 3y earlier) |
| **Yahoo InterestExpense missing pre-2022** | ใช้ 4y window — flag `DATA_LIMITED_INT_COV` |

#### Decision log (Stage 4)

1. **ตัด D/E ออกจาก "STRONG_MOAT"** — Moat = business advantage ไม่ใช่ balance sheet structure. CPALL D/E 2.0 (retail business มี inventory + lease structural) ROE 21% คงที่ + GM ขยาย = moat แท้ตาม Niwes
2. **Net Debt/EBITDA → Interest Coverage + Net Debt trend** — Net Debt/EBITDA = ทฤษฎี (สมมติเอากำไรทั้งหมดไปคืนหนี้) ไม่จริง. Interest Coverage = "กำไรพอจ่ายดอกไหม" + Net Debt trend = "เอากำไรไปคืนหนี้จริงไหม" (refinance vs repay) — ตรงกว่า (อาร์ท insight 2026-05-14)
3. **Moat type 5 ประเภท → Claude L4** — Brand/Cost/Network/Regulatory/Switching = qualitative ต้อง business context ไม่ tag อัตโนมัติ
4. **ROE threshold ≥ 15% + ≥ 7 ปี** — Niwes บอก 7-10 ปี, เลือก 7 (Thai data context — บริษัท listed history limited)
5. **EBIT field ตรง ไม่ใช่ OperatingIncome** — SCC `OperatingIncome` ติดลบบางปี → ratio พัง. Yahoo มี `EBIT` แยก ใช้ตัวนี้
6. **Interest Coverage 4y window** — Yahoo `InterestExpense` มีแค่ 4 ปี (2022-2025) ไม่ครบ 5y — accept limitation

#### Code reference (implementation roadmap)

**Files ต้องแตะ:**
1. `scripts/fetch_data.py::_build_aggregates` — เพิ่ม `roe_consecutive_15plus_years`, `gm_recent_3y_avg`, `gm_earlier_3y_avg`, `gm_trend`, `interest_coverage_4y_avg`, `net_debt_history_5y`, `net_debt_increases_in_3y`
2. `scripts/data_adapter.py` — verify EBIT field (`EBIT` direct vs `OperatingIncome`) จาก yahoo income_statement — SCC OperatingIncome บางปีติดลบ ต้องใช้ EBIT
3. `scripts/screen_stocks.py::assign_signals` — เพิ่ม 5 tag (STRONG_MOAT / MODERATE_MOAT / NO_MOAT / MOAT_ERODING / ROE_FUELED_BY_DEBT)
4. `scripts/screen_stocks.py::quality_score` — moat tier weight in scoring redesign (Stage 2.8)

### 2.7 Stage 5 — ถือยาวได้ (FINAL — approved + backfilled 2026-05-14)

**Source:** Niwes ch6 (ถือยาว 10 ปี) + ch7 (5 สัญญาณขาย)

**Niwes ปักธง:**
- ch6: "เวลา คือผลตอบแทนที่คุณได้ฟรี ตราบเท่าที่คุณไม่ขายทิ้ง" — ระบุก่อนซื้อว่าจะขายเมื่อไหร่
- ch7 5 sell signals: Moat หาย / Management เปลี่ยน / D/E > 100% เพิ่ม / OCF ติดลบ 2y / P/E > 3x historic
- 4 ใน 5 sell signals จับโดย Stage 1/3/4 อยู่แล้ว → Stage 5 = aggregator + business stability mode

#### Raw data ที่เก็บให้ทุกหุ้น

| Field (output) | Source | คำอธิบาย |
|---|---|---|
| `eps_history_10y` | `yearly_metrics[].diluted_eps` (re-use Stage 2) | EPS 10y (2015-2024 — exclude 2025 YTD) |
| `eps_cv_10y` | `std(eps) / abs(mean(eps)) × 100` | coefficient of variation (%) |
| `eps_mean_10y` | mean(eps_history_10y) | สำหรับ CHRONIC_LOSS detection |
| `dps_2011`, `dps_2010` | `dividend_history['2011']` / `'2010'` | crisis check 2011 |
| `dps_2020`, `dps_2019` | `dividend_history['2020']` / `'2019'` | crisis check 2020 |
| `ocf_2011`, `ocf_2020` | `yearly_metrics[year=='2011'].ocf` / `'2020'` | OCF ช่วง crisis |
| `crisis_2011_drop_pct` | `(dps_2011 - dps_2010) / dps_2010 × 100` | % drop crisis 2011 |
| `crisis_2020_drop_pct` | `(dps_2020 - dps_2019) / dps_2019 × 100` | % drop crisis 2020 |
| `sell_signal_count` | count tags trigger จาก Stage 1/2/3/4 (5 signals) | aggregator |

#### Sector mapping (updated ใน sector_taxonomy.py — Section 7 ปรับแล้ว)

```python
# เพิ่มเข้า STABLE_SECTORS (จาก 4 → 8):
STABLE_SECTORS = {
    'Health Care Services', 'Food & Beverage',
    'Personal Products & Pharmaceuticals',
    'Information & Communication Technology',
    'Commerce',                # NEW — Niwes ch7 retail daily-use
    'Banking',                 # NEW — predictable rate-driven
    'Finance & Securities',    # NEW
    'Insurance',               # NEW
}

# เพิ่มเข้า CYCLICAL_SECTORS:
# + 'Tourism & Leisure' (airline/hotel ch6)
# + 'Transportation & Logistics' (ยกเว้น AOT/BTS/BEM ที่อยู่ใน ASSET_HEAVY_EXCEPTIONS)
```

#### ป้ายที่แปะ (6 ป้าย — 3 Stability + 1 Crisis + 2 Sell aggregator)

**Business Stability (mutually exclusive):**

| Tag | เงื่อนไข |
|---|---|
| `STABLE_BUSINESS` | (sector ∈ STABLE_SECTORS OR symbol ∈ STABLE_UTILITY_SYMBOLS) **AND** eps_cv_10y ≤ 30% |
| `CYCLICAL_BUSINESS` | sector ∈ CYCLICAL_SECTORS **OR** eps_cv_10y > 50% |
| `MIXED_STABILITY` | ไม่อยู่ทั้ง 2 (EPS CV 30-50% + sector ไม่ชัด) |

**Crisis Resilience:**

| Tag | เงื่อนไข |
|---|---|
| `RESILIENT_THROUGH_CRISIS` | crisis_2011_drop_pct ≥ -40% **AND** ocf_2011 > 0 **AND** crisis_2020_drop_pct ≥ -40% **AND** ocf_2020 > 0 |

**Sell Signal Aggregator** (count 5 signals จาก Stage 1-4):
- `MOAT_ERODING` (Stage 4)
- `ROE_FUELED_BY_DEBT` (Stage 4)
- `FAKE_PROFIT` (Stage 3)
- `OVERVALUED_VS_SELF` (Stage 1)
- `DIVIDEND_SHRINKING` (Stage 2)

| Tag | เงื่อนไข |
|---|---|
| `MULTIPLE_SELL_TRIGGERS` | sell_signal_count ≥ 2 |
| `NEAR_SELL_TRIGGER` | sell_signal_count == 1 |

#### Real-world test (SETSMART Layer 0 — 2026-05-14)

| หุ้น | EPS CV% | sector | Stability | DPS 2011 drop | DPS 2020 drop | OCF crisis | Sell count | Final tags |
|---|---|---|---|---|---|---|---|---|
| **PTT** | 33.6% | Energy & Utilities (non-utility) | CYCLICAL | +17% ✓ | **-50%** ✗ | both ✓ | 1-2 | `CYCLICAL_BUSINESS` + `NEAR_SELL` |
| **SCC** | 42.7% | Construction Materials | CYCLICAL | 0% ✓ | 0% ✓ | both ✓ | 1 | `CYCLICAL_BUSINESS` + `RESILIENT` + `NEAR_SELL` |
| **CPALL** | 23.9% | Commerce | **STABLE** ✓ | -10.7% ✓ | -28% ✓ | both ✓ | 1 | `STABLE_BUSINESS` + `RESILIENT` + `NEAR_SELL` |
| **ADVANC** | 13.3% | ICT | STABLE | -34.8% ✓ | -5.7% ✓ | both ✓ | 0 | `STABLE_BUSINESS` + `RESILIENT` |
| **BDMS** | 28.5% | Health Care | STABLE | +37.5% ✓ | 0% ✓ | both ✓ | 0 | `STABLE_BUSINESS` + `RESILIENT` |

**Verified:**
- ✓ CPALL ติด `STABLE_BUSINESS` (Commerce ใน STABLE_SECTORS — fix จาก MIXED ผิด)
- ✓ PTT 2020 DPS drop -50% **ไม่ติด** `RESILIENT` (threshold -40% strict ตรงเจตนา Niwes)
- ✓ ADVANC/BDMS EPS CV ต่ำ + sector stable → STABLE ทั้งคู่
- ✓ SCC ติด NEAR_SELL (เพราะ NO_MOAT จาก Stage 4)

#### Edge cases (must handle)

| Case | Behavior |
|---|---|
| **History < 5y** (IPO ใหม่) | skip stability tag + flag `INSUFFICIENT_EPS_HISTORY` |
| **IPO หลัง 2017** | skip crisis 2011 + ใช้ crisis 2020 อย่างเดียว — RESILIENT ถ้าผ่าน 2020 |
| **IPO หลัง 2020** | skip crisis resilience ทั้งหมด + flag `DATA_LIMITED_CRISIS` |
| **2008 Hamburger** | ไม่ครอบ (thaifin start 2010) — accept limitation |
| **EPS mean ≤ 0** (chronic loss) | CV ใหญ่ noise → ใช้ `abs(mean)` + flag CHRONIC_LOSS แทน stability tag |
| **DPS = 0 ในปี crisis** | drop = -100% → ไม่ติด RESILIENT |
| **DPS = None (ไม่จ่าย)** | resilience N/A + flag NO_DIVIDEND |
| **OCF year missing** | resilience N/A + flag DATA_INCOMPLETE_CRISIS |

#### Code reference (implementation roadmap)

**Files ต้องแตะ:**
1. `scripts/sector_taxonomy.py` (NEW) — เพิ่ม `STABLE_SECTORS` (8 sectors) + `CYCLICAL_SECTORS` (12 sectors)
2. `scripts/fetch_data.py::_build_aggregates` — เพิ่ม `eps_cv_10y`, `eps_mean_10y`, `crisis_*_drop_pct`, `ocf_*` (per crisis year)
3. `scripts/screen_stocks.py::assign_signals` — เพิ่ม 6 tag + sequencing: Stage 5 ต้อง run **หลัง** Stage 1-4 (depend trigger results)

#### Decision log (Stage 5)

1. **Commerce → STABLE_SECTORS** — Niwes ch7 retail daily-use = stable. CPALL EPS CV 24% + ติด MIXED ผิด ใน thaifin test → fix sector mapping
2. **Crisis threshold -40%** (เดิม -50%) — PTT 2020 DPS drop exactly -50% เฉียดฉิวผ่าน gate Niwes คงไม่ถือว่า "ทน" → tighten
3. **Crisis years 2011 + 2020** (ไม่ใช่ 2008) — thaifin start 2010 ไม่ครอบ 2008 — accept
4. **EPS CV ใช้ 10y window** — exclude 2025 YTD (ปียังไม่ครบ) → ใช้ 2015-2024
5. **Sell aggregator = 5 signals จาก Stage 1-4** — ไม่ duplicate logic, reuse trigger results (sequencing: Stage 5 ต้อง run หลัง)
6. **เพิ่ม sector mapping 6 sectors** — Commerce/Banking/Finance/Insurance (STABLE) + Tourism/Transport (CYCLICAL except AOT/BTS/BEM)

### 2.7c Stage 6 — Hidden value (FINAL — approved + backfilled 2026-05-14)

**Source:** Niwes ch3 + 04-criteria section 8 ("Hidden Asset / Sum-of-Parts > Market Cap") + case study `08-case-qh.md`

**Niwes ปักธง (qualitative — ไม่มีสูตรตายตัว):**
- Holding company มี cross-holding ที่มูลค่าเกินราคาตลาด (sum-of-parts > mcap) — case QH ถือ HMPRO 19.87%
- Asset-rich + P/BV ต่ำมาก + sector property/banking
- ตัวอย่าง Niwes: QH, MBK, TCAP, INTUCH (classic), CPN (land bank), SCB group (cross-holding)

#### Raw data ที่เก็บให้ทุกหุ้น

| Field (output) | Source | คำอธิบาย |
|---|---|---|
| `holdings_list` | `data/hidden_value_holdings.json` (manual, Claude-curated) | array of {holding, stake_pct, type, note} |
| `holding_mcap_total` | `_holding_mcap()` (yahooquery) × stake_pct → sum | THB |
| `parent_mcap` | re-use Stage 1 (`market_cap`) | THB |
| `sop_ratio` | `holding_mcap_total / parent_mcap` | ratio (≥1.0 = ของถูกชัด) |
| `pb_current`, `sector` | re-use Stage 1 | — |

#### ป้ายที่แปะ (3 ป้าย + 1 default)

| Tag | เงื่อนไข | ที่มา |
|-----|---------|------|
| `HIDDEN_HOLDING` | อยู่ใน manual list (classic_holding type) | Niwes case study (QH/MBK/TCAP/INTUCH) |
| `HOLDING_VALUE_DEEP` | sop_ratio ≥ 1.0 | Niwes section 8 + QH model |
| `ASSET_RICH_PBV_LOW` | P/BV ≤ 0.7 **AND** sector ∈ {Property Development, Property Fund & REITs, Banking, Finance & Securities} | Niwes section 8 (asset-rich proxy) |
| `NONE` (default) | ไม่ match ทั้ง 3 | majority of stocks |

**Scoring contribution:**
- `HIDDEN_HOLDING` → +3 pts (classic, manual whitelist)
- `HOLDING_VALUE_DEEP` → +2 pts (sum-of-parts verified) — cap pillar รวม 5 pts
- `ASSET_RICH_PBV_LOW` → **0 pts (tag เฉย ๆ)** — กัน overlap Valuation pillar Stage 1

#### Manual list governance — **Option B (Claude curate)** [CRITICAL]

**Source of truth:** `projects/4-MaxMahon/data/hidden_value_holdings.json`

**ใครแก้:** Claude (กู) เท่านั้น — อาร์ทไม่แก้ JSON ตรง

**Workflow:**
1. **Initial seed (Phase B Day 7):** กู research Niwes 8 บท + 04-criteria + case study + SET news → propose ~20-30 entries → อาร์ท approve list → commit
2. **Audit existing 5 entries:**
   - **Remove DELTA** ทันที (Taiwan parent ≠ undervalued holding — wrong context)
   - Verify QH/MBK/TCAP/INTUCH ตรง Niwes case study
   - Expand: SCC group (cross-holding), CPN (land bank), SCB (financial holding), AIS group, etc.
3. **Schema เพิ่ม `type` field:**
   ```json
   {
     "QH": [{"holding": "HMPRO", "stake_pct": 19.87, "type": "classic_holding", "note": "Niwes case study reference"}],
     "CPN": [{"type": "land_bank", "note": "Central group land assets > book"}]
   }
   ```
   type values: `classic_holding` / `land_bank` / `cross_holding` / `parent_co`
4. **Refresh cadence:** ทุก 3-6 เดือน กูสแกน Niwes blog / SET news → propose update → อาร์ท approve
5. **Ad-hoc:** อาร์ทเจอเอง → บอก Claude → Claude update

#### Real-world test (5 หุ้น — SETSMART chain — 2026-05-14)

| หุ้น | P/BV | In list (post-audit) | sop_ratio | Sector | Tags |
|---|---|---|---|---|---|
| **QH** | 0.50 | YES (HMPRO 19.87%) | ≥1.0 ✓ | Property Development | `HIDDEN_HOLDING` + `HOLDING_VALUE_DEEP` + `ASSET_RICH_PBV_LOW` |
| **MBK** | 1.22 | YES (subsidiary) | TBD (verify) | Property Development | `HIDDEN_HOLDING` (+ DEEP if sop_ratio ≥1) |
| CPN | 2.65 | TBD (add land_bank) | — | Property Development | (TBD post-audit) |
| **DELTA** | 36.89 | **REMOVE** | — | Electronics | `NONE` (after fix) |
| HMPRO | 2.88 | NO | — | Commerce | `NONE` |

**Verified:**
- ✓ QH = classic Niwes case — ติด 3 tags (overlap intentional)
- ✓ DELTA removal — fix false positive
- ⚠ CPN ต้อง audit + add land_bank entry
- ⚠ MBK sop_ratio ต้อง verify ด้วย holding_mcap จริง

#### Edge cases (must handle)

| Case | Behavior |
|---|---|
| **Holdings list empty for symbol** | `NONE` default |
| **Yahoo flake ดึง holding_mcap ไม่ได้** | `HIDDEN_HOLDING` ติด (manual list) แต่ skip `HOLDING_VALUE_DEEP` + flag `DATA_INCOMPLETE_HOLDING` |
| **sop_ratio บางส่วนเท่านั้น** (1 holding ดึงได้ / อีก 1 fail) | คำนวณบางส่วน + flag DATA_PARTIAL_HOLDING |
| **Recursive holding** (holding ของ holding) | limit depth 1 — ไม่ traverse ลึก |
| **P/BV ติดลบ** (equity ติดลบ) | skip `ASSET_RICH_PBV_LOW` |
| **Type missing ใน JSON entry** | default `classic_holding` (backward compat) |

#### Code reference (implementation roadmap)

**Files ต้องแตะ:**
1. `data/hidden_value_holdings.json` — **audit + re-seed** (remove DELTA / add SCC/CPN/SCB groups / add `type` schema)
2. `scripts/data_adapter.py::check_hidden_value` (lines 967-989) — เพิ่ม `type` field handling
3. `scripts/screen_stocks.py::hidden_value_score` (lines 334-349) — wire `HOLDING_CO_HIDDEN` pattern + sop_ratio threshold
4. `scripts/screen_stocks.py::assign_signals` — เพิ่ม 3 tag (HIDDEN_HOLDING / HOLDING_VALUE_DEEP / ASSET_RICH_PBV_LOW)
5. **NEW process** — Claude curate workflow (initial seed + refresh quarterly)

#### Decision log (Stage 6)

1. **3-layer approach** (manual + sum-of-parts + asset-rich proxy) — Niwes qualitative ต้องใช้ judgment, ไม่ algorithmic ทั้งหมด
2. **Manual list = Claude curate (Option B)** — อาร์ทไม่ยุ่ง JSON / Claude propose → approve → commit
3. **Audit 5 existing entries** — DELTA wrong context (Taiwan parent ≠ hidden value) ต้องลบ
4. **`ASSET_RICH_PBV_LOW` ไม่บวก score** — กัน overlap Valuation pillar Stage 1 (P/B ใช้ใน MOS calc แล้ว)
5. **Sum-of-parts cap depth 1** — ไม่ traverse holding ของ holding (false positive risk)
6. **Schema `type` field** — แยกประเภท classic_holding / land_bank / cross_holding / parent_co

### 2.7d Stage 7 — ตัดทิ้ง (Decision 2026-05-15)

**Reason:**
- Stage 1-6 ครอบ quality + dividend resilience + crisis test ครบแล้ว
- Stage 7 candidate tag (PILLAR_STOCK 4 เงื่อนไข SET50 + mcap >=100B + listed >=15y + dividend 10y unbroken):
  - [d] dividend 10y unbroken ทับซ้อน Stage 2 (consecutive_no_cut + streak)
  - [a]+[b]+[c] ใหม่จริง แต่ value-add น้อย — `STRONG_MOAT` (Stage 4) + `RESILIENT_THROUGH_CRISIS` (Stage 5) บอกเรื่องเดียวกันใกล้เคียง
- DELTA case ที่กังวล (ใหญ่+เก่าแต่ผันผวน) — Stage 4 (ROE swing) + Stage 5 (CYCLICAL_BUSINESS) จับได้แล้ว
- Cost ที่ตัดได้: scrape SET50 semi-annual list + IPO listing date factsheet + 6-month refresh maintenance

**Research artifact (kept for reference):** `C:\WORKSPACE\.claude\plans\4-MaxMahon\stage7-research.md` — 391-line synthesis (Niwes book + SET50 + Graham defensive + global investor criteria)

**Framework final = 6 stages** (no Stage 7)

### 2.8 Scoring Redesign (TBD)

**โจทย์สำคัญ:** ตอบ "score vs portfolio role mismatch"
- เก่า: คะแนน 100 weighted (50/25/10/5/10) → หุ้นคะแนนสูงบางตัวไม่เหมาะเป็น anchor
- ทางเลือก: multi-axis (anchor fit / supporting fit / tail fit) แทน single score
- หรือ tag-based selector (filter tag combo → role) แทน scoring

### 2.9 Claude Opus Prompt Redesign (TBD)

- Input ใหม่ตาม Niwes framework (raw data + tag จาก 6 stage)
- Output: deep analysis ตาม Niwes mental model (ไม่ใช่ generic value investor)

### 2.10 Dictionary หน้าคำศัพท์ — NEW Requirement

**ทำไม:** ป้าย+ศัพท์เฉพาะที่โผล่ใน report ผู้ใช้ต้องเปิดดูคำอธิบายได้

**Scope:**
- ทุก tag ที่ design (6 stage รวม ~37 tags) → มี definition + ตัวอย่าง
- ศัพท์เฉพาะ: hidden value, deep value, payout ratio, moat, margin of safety, OCF, FCF, ROE, P/E, P/B, yield trap, ฯลฯ
- UX: hover tooltip (compact) / คลิกเปิดหน้าเต็ม (detail)
- Source: tag dictionary แยก lib file → render ได้ทั้ง report + standalone page

**Deliverable:** Library file (JSON/MD) + UI component + page route

---

## 3. Scope Boundary

### In Scope
- Refactor pipeline 4 layer ใหม่ (Hard Filter → 6 Stage Tag → Scoring → Display → Claude Analyze)
- Design + implement 6 Stage tag (Niwes ch2-ch7)
- Scoring redesign (multi-axis or tag-based)
- Claude Opus prompt redesign
- Dictionary หน้าคำศัพท์ (lib + UI)
- Plan archive: `filter-04/05/06/08` (framework-tied old design)

### Out of Scope
- Hard Filter 5-5-5-5 logic redesign (คงเดิม — แค่เปลี่ยน semantics จาก "ตัด" เป็น "set status")
- UI overhaul ที่ไม่เกี่ยวกับ tag/score display
- Data source change (คงเดิม: Layer 0 SETSMART / Layer 1 thaifin / Layer 2 yahooquery)
- Plan archive ของ infrastructure plans: `filter-01/02/03/07` (keep — ไม่ผูก framework)

---

## 4. Non-goals

- **ไม่ทำ retroactive migration** — หุ้นที่มีอยู่ใน DB จะ recompute ตาม framework ใหม่ ไม่ migrate historic tag
- **ไม่บังคับ user เลือก single score** — multi-axis เผยให้ user เลือกเอง
- **ไม่ส่ง alert/notification** — refactor focus pipeline + display ไม่ใช่ engagement layer
- **ไม่ output ใน real-time** — weekly scan ปกติ (อ่าน existing schedule)
- **ไม่แก้ Hard Filter 5-5-5-5 threshold** — คง threshold เดิม แค่เปลี่ยน behavior (PASS/REVIEW/FAIL = status ไม่ใช่ filter)

---

## 5. Plan Files Decision

| File | Action | Reason |
|------|--------|--------|
| `filter-01-year-completeness.md` | Keep | Infrastructure (ปียังไม่จบ bug) — ไม่ผูก framework |
| `filter-02-setsmart-migration.md` | Keep | Data source — คุ้ม subscription |
| `filter-03-dps-yahoo-only.md` | Keep | DPS accuracy — independent |
| `filter-04-review-pass-tag.md` | Archive | REVIEW concept เก่า — framework เปลี่ยน |
| `filter-05-normalized-eps.md` | Archive | Filter เก่า — pipeline เปลี่ยน |
| `filter-06-daily-refilter.md` | Archive | Pipeline เก่า |
| `filter-07-flake-retry-queue.md` | Keep | Resilience — independent |
| `filter-08-integration-verify.md` | Archive | จะใหม่ตาม framework |
| `filter-index.md` | Regenerate | Index ตาม plan ใหม่ |

---

## 6. Code Reference Map (full pipeline)

### Layer 1 — Hard Filter 5-5-5-5
- **File:** `projects/4-MaxMahon/scripts/screen_stocks.py`
- **Function:** `hard_filter(data)` lines 60-143 → returns `(status, reasons)` status ∈ `PASS/REVIEW/FAIL`
- **Threshold dict:** `DEFAULT_FILTERS` lines 31-42 + `HARD_FILTERS` line 57, overridable via `config.json`
- **Values:** `min_dividend_yield=5.0`, `min_dividend_streak=5`, `growing_yield_floor=2.0`, `growing_min_streak=3`, `min_eps_positive_years=5`, `max_pe=15`, `bonus_pe=8`, `max_pbv=1.5`, `bonus_pbv=1.0`, `min_market_cap=5_000_000_000`
- **Niwes refactor:** เปลี่ยน semantics จาก "filter cut" → "status assign" (PASS/REVIEW/FAIL คงเดิม แต่ display แสดงทั้งหมด search ได้)

### Layer 2 — Tag Classification (existing → replace)
- **File:** `projects/4-MaxMahon/scripts/screen_stocks.py`
- **Function:** `assign_signals(data, total_score)` lines 565-632
- **Existing tags (replace ทั้งหมด):** `DATA_WARNING`, `DATA_INCOMPLETE`, `NIWES_5555`, `NIWES_GROWING`, `HIDDEN_VALUE`, `QUALITY_DIVIDEND`, `YIELD_SPIKE_FROM_PRICE_DROP`, `DEEP_VALUE`, `DIVIDEND_TRAP`, `OVERPRICED`
- **Plus:** `detect_case_study_tags` + `detect_moat_tags` from `scripts/case_study_detector.py` (loads `data/case_study_patterns.json`)
- **Tag narratives:** `_TAG_NARRATIVES` dict in `scripts/report_template.py` lines 22-36 — Thai descriptions per tag (becomes glossary seed)

### Layer 3 — Scoring (quality_score 100 → redesign Stage 2.8)
- **File:** `projects/4-MaxMahon/scripts/screen_stocks.py`
- **Main aggregator:** `quality_score(data)` lines 722-760 — calls 5 sub-functions then applies signal modifiers
- **5 pillar functions (existing — แต่ละจะ redesign):**
  - `dividend_score` lines 146-231 — **50 pts** (yield 15 + streak 15 + payout sust 10 + growth/stable 10)
  - `valuation_score` lines 234-284 — **25 pts** (P/E 10 + P/BV 10 + EV/EBITDA 5)
  - `cash_flow_score` lines 287-331 — **10 pts** (FCF 5 + OCF/NI 3 + interest cov 2)
  - `hidden_value_score` lines 334-349 — **5 pts**
  - `track_record_score` lines 352-385 — **10 pts** (revenue_cagr 5 + eps_cagr 5)
- **Signal modifiers** lines 738-745: NIWES_GROWING +10, DIVIDEND_TRAP -20, DATA_WARNING -5, YIELD_SPIKE -5
- **Valuation grade modifier** lines 1024-1026 (main): A:+5/B:+2/C:0/D:-3/F:-8
- **Function `valuation_grade`** lines 635-719 — PEG + sector median + yield ratio + 52w position

### Layer 4 — Display
- **Home list:** `projects/4-MaxMahon/web/v6/static/js/pages/home.js` + `home.mobile.js`
- **Filter state:** `_state` lines 343-351 (`sort`, `signal`, `sectors[]`, `page`, `pageSize=15`)
- **Filter logic:** `_applyFilterSort()` lines 353-382
- **Sector chips dynamic** lines 231-244
- **Signal chips hardcoded** lines 262-267 — currently expose แค่ 4 tags (NIWES_5555 / HIDDEN_VALUE / DEEP_VALUE / QUALITY_DIVIDEND)
- **Search:** `projects/4-MaxMahon/server/app.py` `POST /api/search` line 1815, helper `_extract_search_result` line 1783
- **Report page:** `projects/4-MaxMahon/web/v6/static/js/pages/report.js` (+ `.mobile.js`) — fetch `/api/stock/{sym}` + `/patterns` + `/history` + `/exit-status`

### Layer 5 — Claude Opus Analyze
- **Prompt builder:** `projects/4-MaxMahon/server/app.py` `_build_analysis_prompt(stock)` lines 1873-1955 (Max-to-Art persona, JSON 6-key schema `{dividend, hidden, moat, valuation, to_art, verdict}`)
- **Wrapper:** `build_analysis_prompt(symbol)` line 1961
- **Response parser:** `parse_analysis_response(raw)` lines 1977-2002
- **API endpoint:** `POST /api/stock/{symbol}/analyze` line 2032
- **Model:** `claude-opus-4-7` lines 2047 + 2062, `max_tokens=4000`, `timeout=90.0`
- **Cache:** `_ANALYSIS_CACHE_DIR / {symbol}.json`, TTL 7 days
- **Second invoke:** `POST /api/portfolio/builder/explain` line 2764 — `_build_portfolio_explain_prompt`

### Data Adapter Schema (`scripts/data_adapter.py` + `scripts/fetch_data.py`)

**Snapshot top-level fields:**
- `symbol`, `name`, `sector` (string), `industry` (string), `currency`
- `price` (THB), `market_cap` (THB absolute)
- `pe_ratio` (ratio), `forward_pe`, `pb_ratio` (ratio)
- `dividend_yield` (**percent**), `dps` (THB/share), `five_year_avg_yield` (**percent**)
- `eps_trailing`, `eps_forward` (THB/share)
- `revenue` (THB), `revenue_growth` (decimal), `earnings_growth` (decimal)
- `profit_margin`, `gross_margins`, `operating_margins` (decimal)
- `roe`, `roa` (decimal)
- `debt_to_equity` — **percent (×100)** ⚠ ต่างจาก yearly_metrics
- `current_ratio`, `free_cashflow`, `operating_cashflow` (THB)
- `recent_dividends[]`, `52w_high`, `52w_low`, `50d_avg`, `200d_avg`
- `yearly_metrics[]`, `dividend_history{year: dps}`

**`yearly_metrics` per-year dict** (lines 222-262):
- `year` (str), `revenue`, `gross_profit`, `operating_income`, `net_income`, `ebitda`, `interest_expense`, `diluted_eps`, `sga`, `equity`, `total_debt`, `total_assets`
- `ocf`, `fcf`, `capex` (negative=spend), `dividends_paid` (**None** — thaifin doesn't have)
- `roe`, `gross_margin`, `net_margin`, `operating_margin`, `sga_ratio` — **decimal**
- `de_ratio` — **ratio** ⚠ (NOT percent, opposite of snapshot)
- `interest_coverage`, `ocf_ni_ratio`, `capital_intensity`
- `close`, `dividend_yield` (percent), `mkt_cap`, `bvps`, `payout_ratio` (decimal)
- `cash`, `roa_year`, `revenue_yoy`, `net_profit_yoy`, `eps_yoy`, `cash_cycle`, `financing_activities`, `ev_per_ebit_da`

**`aggregates`** (`fetch_data.py::_build_aggregates` lines 127-194):
- `revenue_cagr`, `eps_cagr`, `dps_cagr` (decimal)
- `avg_roe`, `min_roe`, `avg_net_margin`, `avg_gross_margin`, `avg_operating_margin` (decimal)
- `revenue_growth_years`, `revenue_growth_total_comparisons`, `eps_positive_years`, `eps_total_years`, `fcf_positive_years`, `fcf_total_years`
- `dividend_streak`, `dividend_growth_streak`, `years_of_data`
- `latest_interest_coverage`, `latest_ocf_ni_ratio`, `latest_capital_intensity`

**Unit gotchas (อย่าพลาด):**
1. `debt_to_equity` (snapshot) = **percent** / `de_ratio` (yearly) = **ratio** — ต่างกัน
2. `dividend_yield` (snapshot) = **percent** / margins, roe = **decimal** — ผสมกันใน snapshot
3. `dividends_paid` ใน yearly_metrics = **None** — thaifin ไม่มี — ต้องคำนวณ `dps × shares_outstanding`

### Report Renderer
- **Markdown scan:** `projects/4-MaxMahon/scripts/report_template.py::generate_report_md` line 84 → `reports/scan_*.md`
- **Per-stock HTML:** rendered client-side `web/v6/static/js/pages/report.js` consume `GET /api/stock/{sym}`
- **Tag chips:** hardcoded ใน `home.js` lines 64-75 + Thai narrative dict ใน `report_template.py` lines 22-36

### Dictionary / Glossary (NEW required)
- **ไม่มีไฟล์ glossary เฉพาะ** — `_TAG_NARRATIVES` + `case_study_patterns.json` คือใกล้ที่สุด
- **NEW file:** `projects/4-MaxMahon/data/niwes_glossary.json` — Niwes term-to-Thai dictionary

### Files ที่ Niwes refactor v2 ต้องแตะ

| # | File | สิ่งที่ทำ |
|---|------|---------|
| 1 | `scripts/data_adapter.py` | unit normalization + verify EBIT field + dividends_paid fallback |
| 2 | `scripts/fetch_data.py::_build_aggregates` | เพิ่ม fields ทุก Stage (consecutive_no_cut / dps_rising_ratio / ocf_to_np / roe metrics / GM trend / interest_coverage_4y / net_debt) |
| 3 | `scripts/sector_taxonomy.py` (NEW) | mapping tables (industry → ASSET class / payout threshold / Net Debt cap / stable-cyclical) |
| 4 | `scripts/sector_pe_precompute.py` (NEW) | universe scan compute median P/E per industry → `data/sector_pe_median.json` |
| 5 | `scripts/screen_stocks.py::assign_signals` (lines 565-632) | replace existing tags ด้วย Stage 1-6 tags (design ครบแล้ว) |
| 6 | `scripts/screen_stocks.py::*_score` (lines 146-385) | rewrite 5 pillars ตาม Stage 2.8 scoring redesign |
| 7 | `scripts/case_study_detector.py` + `data/case_study_patterns.json` | align กับ Stage 4/5 tag definitions |
| 8 | `scripts/report_template.py::_TAG_NARRATIVES` | expand ทุก tag ใหม่ + becomes glossary seed |
| 9 | `server/app.py::_build_analysis_prompt` (lines 1873-1955) | Claude prompt redesign ตาม Stage 2.9 |
| 10 | `web/v6/static/js/pages/home.js` lines 64-75, 262-267 | expand signal chips list (currently 4 → all new tags) |
| 11 | `web/v6/static/js/pages/report.js` | per-stock tag display + dictionary tooltip |
| 12 | `data/niwes_glossary.json` (NEW) | Niwes term dictionary (Stage 2.10) |
| 13 | `config.json` | filter threshold overrides |

---

## 7. Sector Mapping Table (real thaifin values)

### Source
- Field: `sector` (string) + `industry` (string) ที่ top-level
- Library: thaifin (`getattr(stock, "sector", "N/A")` / `"industry"`)
- File: `scripts/data_adapter.py` lines 127-128 + 750-751 + 870-871
- **No SET 4-6 letter codes** — only English long names เช่น "Banking", "Energy & Utilities"
- Mapper (existing): `scripts/portfolio_builder.py:9` `to_canonical_sector` — substring match (`'bank' in r`)

### 8 Industries (SET standard — เป๊ะ)
1. **Agro & Food Industry**
2. **Consumer Products**
3. **Financials**
4. **Industrials**
5. **Property & Construction**
6. **Resources**
7. **Services**
8. **Technology**

### 28 Sectors (string ภาษาอังกฤษ จริงจาก thaifin)

| Industry | Sectors |
|---|---|
| Agro & Food Industry | Agribusiness, Food & Beverage |
| Consumer Products | Fashion, Home & Office Products, Personal Products & Pharmaceuticals |
| Financials | Banking, Finance & Securities, Insurance |
| Industrials | Automotive, Industrial Materials & Machinery, Packaging, Paper & Printing Materials, Petrochemicals & Chemicals, Steel and Metal Products |
| Property & Construction | Construction Materials, Construction Services, Property Development, Property Fund & REITs |
| Resources | Energy & Utilities |
| Services | Commerce, Health Care Services, Media & Publishing, Professional Services, Tourism & Leisure, Transportation & Logistics |
| Technology | Electronic Components, Information & Communication Technology |

**Coverage gaps:**
- "Mining" (SET code MINE) ไม่มีใน real data — LANNA (ถ่านหิน) อยู่ Energy & Utilities
- 223/912 entries (~24%) มี `sector = '-'` — หุ้นเล็ก/warrants/PFund บางตัว → default ASSET_LIGHT + flag UNKNOWN_SECTOR

### Mapping `sector_taxonomy.py` (NEW file)

```python
# Stage 1: ASSET_HEAVY / ASSET_LIGHT (P/B usability)
ASSET_HEAVY_INDUSTRIES = {
    'Financials', 'Property & Construction', 'Resources',
    'Industrials', 'Agro & Food Industry',
}
ASSET_LIGHT_INDUSTRIES = {
    'Technology', 'Services', 'Consumer Products',
}
ASSET_HEAVY_EXCEPTIONS = {
    'AOT', 'BTS', 'BEM',  # transport infrastructure (Services parent)
    'CPALL', 'BJC', 'MAKRO', 'GLOBAL', 'CPAXT',  # daily essentials retail
}

# Stage 2: Industry payout threshold
PAYOUT_THRESHOLD_BY_INDUSTRY = {
    'Technology': 0.70,
    'Services': 0.80,
    'Financials': 0.75,
    'Resources': 1.00,
    'Industrials': 0.80,
    'Property & Construction': 1.00,
    'Consumer Products': 0.70,
    'Agro & Food Industry': 0.80,
    'default': 0.80,
}

# Stage 2: Net Debt/EBITDA threshold (split HEAVY/LIGHT)
NET_DEBT_EBITDA_THRESHOLD = {
    'ASSET_HEAVY': 6.0,
    'ASSET_LIGHT': 3.0,
}

# Stage 5: Stable / Cyclical (sector + symbol override — updated 2026-05-14)
STABLE_SECTORS = {
    'Health Care Services',
    'Food & Beverage',
    'Personal Products & Pharmaceuticals',
    'Information & Communication Technology',
    'Commerce',                # NEW — retail daily-use (Niwes ch7)
    'Banking',                 # NEW — predictable rate-driven
    'Finance & Securities',    # NEW
    'Insurance',               # NEW
}
CYCLICAL_SECTORS = {
    'Construction Materials', 'Construction Services', 'Property Development',
    'Automotive', 'Steel and Metal Products', 'Petrochemicals & Chemicals',
    'Industrial Materials & Machinery', 'Packaging', 'Paper & Printing Materials',
    'Agribusiness',
    'Tourism & Leisure',                  # NEW — airline/hotel (Niwes ch6)
    'Transportation & Logistics',         # NEW (ยกเว้น AOT/BTS/BEM ใน ASSET_HEAVY_EXCEPTIONS)
}
STABLE_UTILITY_SYMBOLS = {'EGCO', 'RATCH', 'GULF', 'GPSC', 'BGRIM', 'BPP', 'CKP'}
# Rest of Energy & Utilities = CYCLICAL (PTT/BCP/BANPU/TOP/OR/IRPC/etc.)

# Special bucket: exclude from ASSET taxonomy
REIT_PFUND_BUCKET = {'Property Fund & REITs'}
```

### Edge cases for sector taxonomy

| Case | Resolution |
|---|---|
| Energy & Utilities ก้อนรวม (energy cyclical + utility stable) | symbol whitelist STABLE_UTILITY_SYMBOLS |
| Commerce ก้อนรวม (staples + discretionary retail) | symbol whitelist ASSET_HEAVY_EXCEPTIONS |
| Transportation & Logistics (infrastructure vs asset-lite ops) | symbol whitelist {AOT, BTS, BEM} |
| Property Fund & REITs | separate bucket — exclude from ASSET taxonomy |
| Banking + Insurance + Finance | ASSET_HEAVY + STABLE (Niwes ch2 P/B applicable) |
| sector = '-' | default ASSET_LIGHT + UNKNOWN_SECTOR warning |

---

## 8. Implementation Order + Dependency

### Test Data Source (verified 2026-05-14)

**ใช้ SETSMART (Layer 0) เป็น primary** ผ่าน orchestrator `fetch_fundamentals(symbol)` ที่ chain:
1. **L0 SETSMART** — snapshot + Q4 audited financial (override snapshot fields)
2. **L1 thaifin** — yearly history 16y (2010-2025) — primary สำหรับ time series
3. **L2 yahooquery** — DPS events (special dividends) + Interest Expense + EBIT (4y)

**Credentials:** `SETSMART_API_KEY` ใน `.env` (header `api-key`) — verified working

**Test verified กับ 5 หุ้น:** PTT, SCC, CPALL, ADVANC, BDMS (Stage 1-5 ทั้งหมด tag trigger ถูก)

**Caveats:**
- SETSMART = snapshot + Q4 ปีล่าสุด finalised audit — ตัวเลขสะอาดกว่า thaifin YTD noisy
- History > 1 ปี ยังพึ่ง thaifin (chain design intentional)
- EOD cache stale 2026-05-08 — `daily_price_refresh.py` cron ไม่รัน → ต้อง refresh manual ก่อน scan
- thaifin = test convenience only — production = SETSMART chain เสมอ

**สำคัญสำหรับ build agent:**
- ใช้ `fetch_fundamentals(symbol)` ใน `data_adapter.py:676` (full chain) — **ไม่ใช่ `_fetch_thaifin` หรือ `_fetch_setsmart` ตรง**
- Snapshot fields (pe_ratio / pb_ratio / etc.) จะถูก SETSMART override ตอนล่าสุด audited
- Yearly history (yearly_metrics) มาจาก thaifin
- ถ้า SETSMART unavailable → chain fallback เอง

### Phase A: Infrastructure (Day 1-3)
ต้องทำก่อน Stage tag implement

1. **A1: Unit normalization** — `data_adapter.py` resolve `debt_to_equity` (percent vs ratio) + verify EBIT vs OperatingIncome
2. **A2: Sector taxonomy module** — NEW file `scripts/sector_taxonomy.py` (mapping tables)
3. **A3: Sector P/E precompute** — NEW file `scripts/sector_pe_precompute.py` + `data/sector_pe_median.json` (weekly refresh job)
4. **A4: Extend `_build_aggregates`** — เพิ่ม Stage 1-4 computed fields (consecutive_no_cut / dps_rising_ratio / etc.)

### Phase B: Stage tag implementation (Day 4-8 — parallel after A)

| Day | Stage | Dependency |
|---|---|---|
| Day 4 | Stage 1 (ราคาถูกพอ) | A1, A2, A3 |
| Day 4 | Stage 3 (Cash flow) | A4 |
| Day 5 | Stage 2 (ปันผล) | A2, A4 |
| Day 5 | Stage 4 (Moat) | A4 |
| Day 6 | Stage 5 (ถือยาว) | Stage 1, 3, 4 results (aggregator) |
| Day 7 | Stage 6 (Hidden value) | existing (minor align) |


### Phase C: Scoring + Display (Day 9-11)
1. **C1:** Scoring redesign (Stage 2.8) — multi-axis vs tag-based
2. **C2:** Claude prompt redesign (Stage 2.9) — รับ input ตาม 6 stage
3. **C3:** Glossary JSON (Stage 2.10) — `data/niwes_glossary.json` + report renderer + UI tooltip
4. **C4:** Frontend chips expansion (`home.js`) — expose tags ใหม่ทั้งหมด

### Phase D: QC + cutover (Day 12-13)
1. **D1:** End-to-end test universe scan + verify tags ออกตาม spec
2. **D2:** Backfill report cache
3. **D3:** Documentation update (`CLAUDE.md` MaxMahon)
4. **D4:** Cutover — disable old tag set + enable new

### Critical Path
A1 → A4 → Stage 1/3 (parallel) → Stage 2/4 (parallel) → Stage 5/6 (parallel) → C1 (Scoring) → C2 (Claude) → C3/C4 (Glossary + UI) → D

### Parallel opportunities
- Stage 1 + Stage 3 (independent — different data)
- Stage 2 + Stage 4 (share roe history fields แต่ logic แยก)
- C2 + C3 + C4 (independent after Stage tags complete)

---

## 9. Edge Cases Master List (all stages)

| Category | Case | Resolution |
|---|---|---|
| **Data completeness** | History < 5y | flag `DATA_INCOMPLETE_*` + skip year-dependent tags |
| | IPO < 3y | hard filter REVIEW status (not FAIL) |
| | sector = '-' | default ASSET_LIGHT + UNKNOWN_SECTOR warning |
| | sector_pe_median = None | skip MOS tags + flag DATA_INCOMPLETE_PE |
| | yahoo InterestExpense pre-2022 missing | 4y window — flag DATA_LIMITED_INT_COV |
| | thaifin dividends_paid = None | calc `dps × shares_outstanding` |
| **Negative values** | EPS ติดลบ | mos_pct = N/A + flag EPS_NEGATIVE |
| | NP ติดลบ 1 ปี | OCF/NP ratio = N/A ปีนั้น + flag NP_NEGATIVE_YEAR |
| | NP ติดลบ 2+ ปี ใน 3 | Stage 3 N/A + flag CHRONIC_LOSS (Stage 5 handles) |
| | EBITDA ≤ 0 | net_debt_ebitda = N/A → skip yield_trap rule 4 |
| | EBIT ติดลบ | Interest Coverage = N/A → skip MOAT rule, ใช้ Net Debt trend |
| | Net Debt ติดลบ (cash > debt) | net_debt_increases = 0 → pass rule (cash-rich = safe) |
| **No dividend** | DPS history empty | all dividend tags N/A + flag NO_DIVIDEND |
| | DPS = 0 ปีล่าสุด แต่ history ≥ 10y | flag RECENT_DIVIDEND_HALT (warning) |
| | DPS cut > 30% YoY | break consecutive_no_cut streak |
| **Definition mismatch** | OCF/NP ratio > 5x | flag OCF_NP_DEFINITION_MISMATCH (debug field meaning) |
| | snapshot vs yearly unit (D/E) | normalize ใน `data_adapter.py` |
| **Sector edge cases** | Energy & Utilities (energy vs utility) | symbol whitelist STABLE_UTILITY_SYMBOLS |
| | Commerce (staples vs discretionary) | symbol whitelist ASSET_HEAVY_EXCEPTIONS |
| | REIT / PFund | separate bucket — exclude from ASSET taxonomy |
| **Outlier** | PE_5y_avg skewed by COVID (mean) | ใช้ median แทน mean (trim outliers) |
| **Magnitude** | OCF ลด 2 ปีติด แต่ magnitude เล็ก | gate -20% decline ก่อนติด DETERIORATING |

---

## 10. Resume Checkpoint — ต่อ Section 2.8+

**Status (2026-05-15):** Stage 1-6 design ครบ + Stage 7 ตัดทิ้ง (decision logged section 2.7d)

**Stage ที่เสร็จแล้ว (6/6):**
- Stage 1 — ราคาถูกพอ (2026-05-14)
- Stage 2 — ปันผลต่อเนื่อง (2026-05-14)
- Stage 3 — Cash flow จริง (2026-05-14)
- Stage 4 — Moat (2026-05-14)
- Stage 5 — ถือยาวได้ (2026-05-14)
- Stage 6 — Hidden value (2026-05-14)

**ที่ค้าง (6 ก้อน — Stage 7 ตัดออก จาก 7 เดิม):**
1. **Section 2.8** — Scoring redesign (multi-axis vs tag-based)
2. **Section 2.9** — Claude Opus prompt redesign (input 6 stage tags → output Niwes mental model)
3. **Section 2.10** — Dictionary (`data/niwes_glossary.json` + UI hover + page route)
4. **Stage 6 initial seed** — Claude propose ~20-30 entries `hidden_value_holdings.json` → อาร์ท approve → commit
5. **Phase A pre-implementation tasks (A1-A4):**
   - A1: `data_adapter.py` unit normalization (D/E percent vs ratio)
   - A2: verify OCF/NP definition (อาจ switch เป็น OCF/EBITDA)
   - A3: `sector_pe_precompute.py` + `data/sector_pe_median.json` (weekly refresh)
   - A4: extend `_build_aggregates` ทุก Stage 1-5 fields
6. **Archive obsolete plans** — `filter-04/05/06/08` + regen `filter-index.md`

**Test data source:** SETSMART (Layer 0) verified 5 หุ้น (PTT/SCC/CPALL/ADVANC/BDMS)

**Manual list governance (Stage 6):** Claude curate เท่านั้น — initial seed Phase B Day 7 + refresh ทุก 3-6 เดือน
