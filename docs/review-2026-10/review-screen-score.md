# review-screen-score — review ชั้นคัด + ให้คะแนน + ออกรายงาน (Max Mahon)

- job: job-03-review-screen-score · ทำเมื่อ 2026-10-09 · อ่านอย่างเดียว (ไม่แก้ไฟล์ใน `C:\WORKSPACE\projects\4-MaxMahon`)
- knowledge: ไม่มีใบ knowledge ที่ job ชี้ (ท่อน `## knowledge` มีแต่ `แนะนำ:` 3 บรรทัด) → ทำตามคำแนะนำ: อ่านอย่างเดียว · import จาก scripts ผ่านสคริปต์ใน `C:\WORKSPACE\_desk\maxmahon\krv3\files\` (an1–an12.py) · ไม่ตัดสินว่าเกณฑ์ดีไหม ตัดสินแค่ตรง spec/config ไหม
- ไม้บรรทัด: `docs\scoring-anchor-spec.md` (v1.2 อ่านครบรวม Change Log) · `config.json` · `docs\niwes\04-criteria.md` `13-threshold-adjustments.md` `15-exit-rules.md`
- ข้อมูลที่ใช้: `data\screener_2026-08-22.json` (ตัวหลัก) เทียบ `screener_2026-08-15.json` (สแกนปกติสัปดาห์ก่อน)
- ป้ายความมั่นใจ: ทุกตัวเลข/ค่าจริงในไฟล์นี้มาจาก output ที่รันเอง (สคริปต์ an*.py) · ที่ไม่ได้พิสูจน์ขึ้นต้น `เดา:`

## สรุปสั้น (อ่านอันนี้ก่อน)

1. **คะแนนสูงสุด 45 ไม่ได้เกิดจากสูตรผิดอย่างเดียว — เกิดจาก 3 ชั้นซ้อน:** (ก) สแกน 08-22 ได้ประวัติปันผลสั้นเหลือ 4–7 ปี ทั้ง 45 ตัวเลยเป็น `NEW_PAYER` หมด ไม่มี `STABLE_PAYER` / `GROWING_DIVIDEND` เลย ด้านปันผลตันที่ 18 · (ข) แม้สแกนปกติ 08-15 สูงสุดก็แค่ 48 เพราะด้าน moat เฉลี่ย 1.5/25 และ long_hold เฉลี่ย 2.7/15 (ด่าน 5-5-5-5 คัดหุ้น PE≤15 PBV≤1.5 ซึ่ง ROE ไม่ถึง 15% ต่อเนื่อง 10 ปี) · (ค) เพดานทางทฤษฎีของโค้ดคือ **93 ไม่ใช่ 100**
2. **จุดผิดที่แรงสุดคือระบบเตือนขาย:** `main()` ข้ามหุ้น FAIL (`continue` ก่อนเรียก `detect_exit_signal`) → `FILTER_DEGRADATION` ซึ่งเป็นสัญญาณหลักไม่มีทางทำงานกับหุ้นที่หลุดเกณฑ์จริง · LH.BK ใน watchlist เคยผ่านแล้วตอนนี้ FAIL (P/E 16.1) ไม่มีเตือน
3. **ป้าย/ด่านที่ไม่ตรง spec แล้วกระทบคะแนน:** FAKE_PROFIT ใช้ `>=2` ปี (spec ≥1) · ชื่อ sector `'Property Fund & REIT'` ในโค้ด ≠ `'Property Fund & REITs'` ในข้อมูล → REIT ไม่ถูกยกเว้นตาม v1.2 → 3 ใน 6 ตัวที่ได้ 0 ทันทีเป็น REIT · `CASHFLOW_DETERIORATING` สูตร sign พลิกเมื่อ OCF ช่วงก่อนหน้าติดลบ (OCF ดีขึ้นแต่ติดป้ายเสื่อม) · `DIVIDEND_SHRINKING` นับปันผลปีปัจจุบันที่ยังจ่ายไม่ครบ (25 ตัวติด ถ้าตัดปี 2026 ออกเหลือ 10)
4. **ตัวอย่างใน spec ไม่ตรงโค้ด 1 จุด:** PTT ด้านปันผล spec = 3 (+2 จาก cagr 2.8%) โค้ด = **1** (step function ให้ 0 ที่ต่ำกว่า 3%)

## 1. ตารางต่อไฟล์ (12 ไฟล์ใน `scripts\`)

| ไฟล์ | ทำอะไร | ใครเรียก | ยังใช้หลังเก็บ server | คำตัดสิน + เหตุผล | smoke |
|---|---|---|---|---|---|
| `screen_stocks.py` (1028 บรรทัด) | ด่าน `hard_filter` → ป้าย `assign_anchor_stage_tags` → คะแนน → เขียน `data\screener_<วันที่>.json` + เซฟ `exit_baselines.json` | เดิม server `PIPELINE_MAP["scan"]` (`_archive\2026-10\server\app.py:893`) ตอนเสาร์ 09:00 · ตอนนี้ไม่มีใครเรียกอัตโนมัติ | ใช้ได้เมื่อสั่งมือ (`py scripts\screen_stocks.py`) · **ไม่มี schedule แล้ว** (Task Scheduler `Max Mahon Weekly` = Disabled, log server ตัดที่ 2026-08-27) | **ต้องแก้** — มีจุดผิด 10 จุด (หมวด 3 ข้อ 1,3,4,6,7,8,10,18,19,20) รวมถึงข้าม exit signal ของหุ้น FAIL | `_smoke_niwes_filter` ผ่าน 5/5 |
| `anchor_scoring.py` (312) | คำนวณคะแนน 4 ด้าน + disqualify + penalty (pure function) | `screen_stocks.py:30,846` · `scan_anchor.py:25` | ใช้ | **ใช้ต่อ** (สูตรตรง spec ทุกตัวเลข) แก้แค่ตัวอย่าง PTT ใน spec หรือขั้น bonus ให้ตรงกัน (หมวด 3 ข้อ 12) | ไม่มี (คำนวณ sample CPALL ใน `__main__` ด้วยค่าเดียวกัน = 78) |
| `scan_anchor.py` (149) | อ่าน screener → คำนวณคะแนนซ้ำ → ออก `reports\anchor_scan_<วัน>.md` แบ่ง band 80/50/1/0 | ไม่มีใครเรียก (grep ไม่เจอ caller) · รันมือครั้งเดียว `anchor_scan_2026-05-18.md` | ไม่มี caller | **เก็บกวาด** — `scan.py` + report_template ทำงานเดียวกันแล้ว · band 80/50 ไม่เคยมีใครถึง (สูงสุด 45–51) · glob `screener_*.json` ไม่กรอง regex (`:26`) หยิบ `*_curated.json` ได้ | ไม่มี |
| `scan.py` (105) | อ่าน screener ล่าสุด → `reports\scan_<วัน>.md` + upsert `history.json` + ส่ง Telegram ถ้ามี trigger high | เดิม server pipeline ขั้นสุดท้าย | ใช้ได้เมื่อสั่งมือ (`import dotenv, requests` ผ่าน) | **ใช้ต่อ** (ตัวที่ใช้จริง) แต่ alert อ่านเฉพาะ `candidates` ไม่อ่าน `review_candidates` (`:90-99`) | ไม่มี |
| `report_template.py` (167) | สร้าง markdown รายงาน (Top 10 / Sector / Review / New / Exit Alerts / Watch Out) | `scan.py:66` | ใช้ | **ต้องแก้เล็ก** — พิมพ์ `**Reasons:**` ว่างทุกตัว (`:97` อ่าน key `reasons` ที่ screener ไม่มี) · ไม่แสดง `valuation` | ไม่มี |
| `history_manager.py` (115) | สร้าง/upsert entry ใน `data\history.json` (top 15, watchlist_status, entry_thesis) | `scan.py:67` · `report_template.py:164` | ใช้ | **ต้องแก้** — `yield` เป็น `None` ทุกแถว (`:50,:70` อ่าน key `dy` แต่ screener ใช้ `dividend_yield`) | ไม่มี |
| `case_study_detector.py` (117) | ป้ายชุดเก่า (case-study patterns + BRAND_MOAT/STRUCTURAL_MOAT/GOVT_LOCKIN) | `screen_stocks.py:27,405-406` | ใช้ (ผลอยู่ใน `signals` ไม่เข้าคะแนน) | **ใช้ต่อ** (ไม่กระทบคะแนน) | ไม่มี |
| `sector_taxonomy.py` (68) | จัดกลุ่ม sector STABLE/CYCLICAL สำหรับป้าย Stage 5 | `screen_stocks.py:29,567-568` | ใช้ | **ต้องแก้** — 8 sector ไม่อยู่ทั้งสองชุด รวม `Property Fund & REITs`; ธนาคาร/ประกันอยู่ CYCLICAL ทั้งหมด → โดน −3 ทุกตัว (13/13) | `__main__` มี assert (ไม่ได้รัน) |
| `telegram_alert.py` (64) | ส่งข้อความ Telegram (`send_alert`, `send_exit_alert`) | `scan.py:90` · `daily_price_refresh.py:224` | ใช้ได้ (.env มีทั้ง TOKEN+CHAT_ID — ตรวจแค่ชื่อ key ไม่พิมพ์ค่า) | **ใช้ต่อ** — แต่ไม่เคยมี trigger ให้ส่ง (หมวด 5) | ไม่มี |
| `_smoke_niwes_filter.py` (121) | fixture เทส `hard_filter` + `assign_signals` | รันมือ | — | **ใช้ต่อ** | **รันแล้วผ่าน 5/5** (case 4 ยืนยันว่า streak 2 ผ่านด่านโดยตั้งใจ) |
| `_smoke_scoring_v2.py` (146) | เทสสูตรคะแนนเก่า (`quality_score` `dividend_score` `cash_flow_score`) | รันมือ | — | **เก็บกวาด** — ฟังก์ชันที่เทสถูกลบจาก `screen_stocks.py` หมดแล้ว | **รันแล้วล้ม 6/6** (ImportError `quality_score` / `dividend_score` / `cash_flow_score`) |
| `_smoke_dehardcode.py` (64) | เทส `portfolio_builder.compute_sector_suggestions` | รันมือ | — | **ย้ายออกจากกองนี้** — ทดสอบ `portfolio_builder` ไม่เกี่ยวชั้นคัด | **รันแล้วผ่าน 3/3** |

หมายเหตุ: `git status` หลังรัน smoke 3 ตัวไม่เปลี่ยน (ยังมีแค่ 3 ไฟล์ที่เปลี่ยนมาก่อนแล้ว) — smoke ไม่เขียน `data\`

## 2. คำตอบข้อ 1–7

### ข้อ 1 — ด่าน `hard_filter` เทียบ `config.json` + docstring

ค่าใน `config.json` `filters` (10 ตัว) กับที่ `screen_stocks.py` ใช้จริง (นับ `HARD_FILTERS["<key>"]` ใน source):

| key (config) | ค่า | ใช้ใน `hard_filter`? | หลักฐาน |
|---|---|---|---|
| `min_dividend_yield` | 5 | ใช้ (`:122`) | นับ 2 จุด |
| `growing_yield_floor` / `growing_min_streak` | 2.0 / 3 | ใช้ (`:124-125`) | |
| `min_eps_positive_years` | 5 | ใช้แบบ `==` (`:108`) ไม่ใช่ `>=` | ตั้ง 4 แล้วรัน: SCB EPS 5/5 → `FAIL ['EPS positive 5/5 (FAIL)']` (ผลรัน an8.py) · ตัวเลข 5 ใน `total < 5` (`:106`) กับ `pos == 4` (`:110`) ก็ hardcode |
| `max_pe` / `max_pbv` / `min_market_cap` | 15 / 1.5 / 5e9 | ใช้ | |
| **`min_dividend_streak`** | 5 | **ไม่ใช้** (นับ 0 จุด) | SCB streak=4 ผ่านด่านเป็น `PASS` (`hard_filter → ('PASS', [])` ผลรัน an8.py) ติดอยู่ใน 45 ตัว · smoke case 4 ตั้งใจยืนยันว่า "streak 2 ผ่าน" |
| **`bonus_pe` (8.0)** | 8.0 | **ไม่ใช้เลยใน .py ทั้ง `scripts\`** | grep `bonus_pe|bonus_pbv|min_dividend_streak` → ไม่เจอที่ใช้ นอกจาก DEFAULT dict (`:34-45`) · `DEEP_VALUE` (`:394`) hardcode `8` กับ `1.0` เอง |
| **`bonus_pbv` (1.0)** | 1.0 | **ไม่ใช้** | เหมือนกัน |

จุดที่ docstring ไม่ตรงโค้ด: (ก) เลขข้อข้าม 2 (มี 1,3,4,5,6) · (ข) docstring ไม่กล่าวถึง PENDING guard ใน list แต่อยู่ในย่อหน้า Rule · (ค) `assign_signals` hardcode `dy>=5 / streak>=5 / pe<=15 / pbv<=1.5` (`:368-377`) ไม่อ่าน `HARD_FILTERS` → แก้ config แล้วป้าย `NIWES_5555` ไม่ตามด่าน · `doc 13` Adjustment 1 (ระดับ streak PASS≥5 / REVIEW 3-4 / FAIL<3) ยัง `PENDING KARL REVIEW` แต่โค้ดไม่มีด่าน streak เลย ต่างจากทั้ง "Current" และ "Recommended" ในเอกสาร

**ลำดับ early return ทำให้เหตุผลหายไหม — ใช่ 2 จุด:**
1. market cap `< 5B` return ทันที (`:82-84`) → หุ้นเล็กไม่เห็นเหตุผลอื่น · ข้อมูล 08-22: ตก market cap 662 ตัว ทั้ง 662 มีเหตุผลเดียว (นับ `len(reasons)==1` = 662 = จำนวนที่มี market cap เป็นเหตุผล) · ทดสอบ mcap 1e9 + PE None → `['market cap 1.0B < 5B']` เท่านั้น
2. `market_cap` เป็น `None` → `or 0` → แสดง `market cap 0.0B < 5B` (ผลรัน) แยกไม่ออกว่าข้อมูลขาดหรือเล็กจริง
- PENDING guard (`:88-93`) อยู่ก่อน EPS/PE → หุ้นที่มี yield>0 แต่ไม่มีประวัติปันผล ได้ PENDING ไม่ใช่ FAIL (ผลรัน: `('PENDING', [...])`) ถูกตาม filter-07

**หุ้นข้อมูลขาด (PE None / ลบ) ตกเพราะอะไร:** `pe is None or pe <= 0` → FAIL เหตุผล `ไม่มี P/E ที่ใช้ได้` (`:135-136`) · P/BV เหมือนกัน `ไม่มี P/BV ที่ใช้ได้` · yield None → `ไม่มีข้อมูลปันผล` · EPS ไม่มี → `ไม่มีข้อมูล EPS` · ผลรันกับข้อมูลจริง SCB: pe None / pe -3 / pb None / dy None → FAIL ตามนี้ทั้งหมด · ในข้อมูล 08-22 มี 16 ตัวที่ตกเพราะ P/E ไม่มี/ลบ · **ไม่แยก "ขาดข้อมูล" กับ "ขาดทุนจริง" (PE ลบ)** ทั้งคู่ขึ้นข้อความเดียวกัน

สรุปผลคัดจริง 08-22: scanned 930 → PASS 45 · REVIEW 2 · FAIL 866 (market cap 662, yield 78, EPS positive 42, EPS history 34 …) · PENDING 0

### ข้อ 2 — ป้ายใน `assign_anchor_stage_tags` เทียบ spec (ครบทุกป้าย)

หมายเหตุ: `docs\scoring-anchor-spec.md` ระบุเงื่อนไขเต็มเฉพาะบางป้าย (GROWING/STABLE/NEW/INTERMITTENT, CASHFLOW tier, FAKE_PROFIT (ตัวหนังสือ), STRONG/MODERATE/NO_MOAT (v1.1), STABLE/RESILIENT (v1.2)) ป้ายที่เหลือ spec ชี้ "จาก parent plan" → อ่านจาก `_archive\2026-10\plans\_archive\niwes-refactor-v2-design.md` (คอลัมน์ "ที่มาเงื่อนไข")

| ป้าย | ที่มาเงื่อนไข | เงื่อนไขใน spec/plan (ฉบับล่าสุด) | เงื่อนไขในโค้ด (บรรทัด) | ตรง? |
|---|---|---|---|---|
| GROWING_DIVIDEND | spec ด้าน1 | ≥10 ปี + rising_ratio ≥70% + avg_yoy ≥3% | `:466` เหมือนกัน | ตรง |
| STABLE_PAYER | spec ด้าน1 | ≥10 ปี แต่ไม่ถึง growth | `:468` | ตรง |
| NEW_PAYER | spec ด้าน1 | จ่าย 3–9 ปี | `:470` consecutive≥3 | ตรง (ไม่เช็ค years_paid_in_10y) |
| INTERMITTENT | spec + plan `:275` | <3 ปี **หรือ** years_paid_in_10y <8 **หรือ** มี miss ใน 5 ปีล่าสุด | `:472` เฉพาะ <3 ปี | **ไม่ตรง** (ขาด 2 เงื่อนไข) |
| DIVIDEND_SHRINKING | plan `:273` | จ่ายต่อเนื่อง ≥10 ปี **และ** dps_5y_cagr < −3% | `:476-484` ต่ำกว่า 70% ของยอดสูงสุดใน 5 key สุดท้ายของ `dividend_history` · **ไม่เช็ค ≥10 ปี** · key สุดท้ายรวมปีปัจจุบัน (2026) ที่จ่ายยังไม่ครบ | **ไม่ตรง** — ติด 25/45 ถ้าตัดปี 2026 ออกเหลือ 10 (an7.py) |
| YIELD_TRAP | plan `:281` | ตก ≥3 ใน 5 ข้อ (payout, fcf_cov, yield abs, net_debt/ebitda, 1y price) | `:487-489` yield>8 และ streak<5 | **ไม่ตรง** (ลดรูปเหลือ 2 ข้อ) — ติด 0/45 |
| ROE_IMPROVING / DECLINING / STABLE | plan `:294-296` | IMPROVING: recent3 > earlier3 **และ** ROE ปัจจุบัน ≥10% · DECLINING: recent3 < earlier3 | `fetch_data.py:_compute_roe_trend` ±0.02 (2 จุด%) ไม่เช็ค ≥10% · <6 จุดข้อมูล → STABLE | **ไม่ตรงเล็กน้อย** (มี dead-band 2pp ไม่มีใน plan) |
| CASHFLOW_HEALTHY | spec ด้าน2 | OCF บวก 3 ปีติด + ccr_avg_3y ≥0.70 | `:500-502` ccr≥0.70 และ `ocf_positive` | ตรง |
| CASHFLOW_OK | spec ด้าน2 | OCF บวก 3 ปี + ccr 0.50–0.70 | `:503` | ตรง |
| CASHFLOW_BELOW_PROFIT | spec + plan `:409` | ccr_avg_3y <0.50 (≥2 ปีจาก 3 ตก) | `:505` ccr<0.50 **และ** OCF บวก 3 ปีติด | **ไม่ตรง (ติดแทบไม่ได้)** — ติด 0/45; ccr<0.5 ที่ OCF ติดลบ 1 ปีไม่ได้ป้ายใดเลย |
| FAKE_PROFIT | spec ตัวหนังสือ vs plan `:410` | spec ด้าน2: "OCF ติดลบ **≥1** ปี + NP บวก" · plan: "OCF ติดลบ **≥2** ปีใน 3 ปี + NP บวก + ไม่ใช่ Banks/Finance/Insurance" · v1.2: ยกเว้น Property/REIT | `:507-514` `ocf_neg >= 2` + `eps_trailing>0` + sector ไม่อยู่ใน `LUMPY` | **spec ภายในขัดกันเอง** (≥1 vs ≥2) โค้ดตาม plan · **ยกเว้น REIT ไม่ทำงาน** (ชื่อ sector ไม่ตรง — ดูหมวด 3 ข้อ 3) |
| CASHFLOW_DETERIORATING | spec + plan `:416` | OCF ลดในทั้ง 2 transition (3 ปี) **และ** ocf_yoy_decline_pct ≤ −20% · v1.2 ยกเว้น Bank/Property/REIT | `:515` เฉพาะ `pct ≤ −0.20` + ไม่อยู่ใน LUMPY · ไม่ใช้ `ocf_consecutive_declining_years` ที่คำนวณไว้แล้ว | **ไม่ตรง** — ดูข้อ 4 |
| STRONG_MOAT | spec v1.1 | ROE ≥12% ติด ≥5 ปี (Bank ≥10%) + GM stable/improving | `:550` เหมือนกัน | ตรง |
| MODERATE_MOAT | spec v1.1 | ROE ≥8% 3 ปี (Bank ≥7%) + GM stable | `:553` GM stable **หรือ improving** + avg_roe≥ขั้นต่ำ | ตรงโดยประมาณ (เพิ่ม improving ตาม commit `2073ee1` spec ไม่ได้ตามแก้) |
| NO_MOAT | spec | ROE ผันผวน/<10% หรือ GM หดตัว | `:556-563` (เหลือทุกกรณีที่ไม่เข้า 3 ข้างบน) | ตรง |
| MOAT_ERODING | plan `:511` | ROE เคยสูงแต่**ลด** 3 ปีล่าสุด + GM หดตัว · disqualify | `:556-561` อยู่ในกิ่ง NO_MOAT เท่านั้น + `roe_consecutive_15plus_years ≥3` (นับ ROE≥15% ติดกัน**จากปีล่าสุด**) | **ไม่ตรง (ตรรกะกลับด้าน)** — ดูข้างล่าง |
| ROE_FUELED_BY_DEBT | plan `:517` | ROE≥15% + D/E>2.0 + Int cov 4y <3 + Net debt เพิ่ม ≥2 ใน 3 ปี · penalty −10 | `:548` avg_roe ≥12% (Bank 10%) + `de>2.0` + int_cov<3 + net_debt_inc≥2 | **ไม่ตรง** — ROE เกณฑ์ต่างและ **D/E เช็คผิดหน่วย** (ดูข้างล่าง) |
| STABLE_BUSINESS | spec v1.2 | sector STABLE/STABLE_UTILITY + eps_cv ≤40% | `:569` เหมือนกัน | ตรง |
| CYCLICAL_BUSINESS | spec / plan `:613` | sector ∈ CYCLICAL **หรือ** eps_cv >50% · penalty −3 | `:571` เหมือนกัน | ตรง (แต่ taxonomy ใส่ Banking/Finance/Insurance ใน CYCLICAL → 13/13 ตัวโดน −3) |
| MIXED_STABILITY | spec | ไม่ติดสองป้ายบวก/ไม่ cyclical (no-action) | `:573` else | ตรง |
| RESILIENT_THROUGH_CRISIS | spec v1.2 | drop 2011 ≥−55% + OCF2011>0 + drop 2020 ≥−55% + OCF2020>0 | `:583-585` เหมือนกัน (ต้องมีข้อมูลทั้งสองวิกฤต — หุ้น IPO หลัง 2011 ติดไม่ได้) | ตรง |

**จุดที่หัวสงสัยทีละข้อ (ผลรันจริง):**
- **FAKE_PROFIT `>=1` vs `>=2`:** spec ด้าน 2 บรรทัด "OCF ติดลบ ≥ 1 ปี" ขัดกับ plan ต้นทาง "≥2 ปีใน 3 ปี" · โค้ดตาม plan · สังเคราะห์: `ocf_neg=1` → ไม่ติดป้ายใด (`['NEW_PAYER','ROE_STABLE','NO_MOAT','STABLE_BUSINESS']`) · `ocf_neg=2` → ติด `FAKE_PROFIT` · Banking `ocf_neg=2` → ไม่ติด (ถูกตาม v1.1)
- **STRONG_MOAT ธนาคาร (10%) กับโบนัส 15%:** ยืนยัน — ธนาคารที่ติด STRONG_MOAT ได้โบนัส ROE-years = 0 เสมอ เพราะ `roe_consecutive_15plus_years` นับ ROE≥15% (`fetch_data.py:273`) · ทดสอบ Bank ROE 11%×6 ปี → `STRONG_MOAT` · `compute_moat(['STRONG_MOAT'], {roe15y:0})` = 10 · ข้อมูลจริง: ธนาคาร 8 ตัว `roe15y=0` ทุกตัว; SAK (STRONG) moat = 12 = 10 + GM improving 2, โบนัส 0 · ไม่ใช่แค่ธนาคาร: STRONG ทั่วไป (12%) ที่ ROE 12–14.9% ก็ได้โบนัส 0 เช่นกัน
- **MOAT_ERODING ติดได้เฉพาะกิ่ง NO_MOAT:** ยืนยัน และเงื่อนไขกลับด้านกับ plan: ROE 20%×10 ปี แล้วตกเหลือ 5/4/3% (counter 15%+ = 0) → `['NO_MOAT']` **ไม่ติด ERODING** · ROE ยัง 18%×6 ปี + GM หดตัว (counter=6) → `['NO_MOAT','MOAT_ERODING']` · คือติดเฉพาะ "ROE ยังสูงแต่ GM ลด" ไม่ใช่ "ROE ที่เคยสูงแล้วตก" · ข้อมูลจริง: ติด 1 ตัว (NER: roe15y=9 + GM declining)
- **DIVIDEND_SHRINKING ใช้ยอดสูงสุด 5 ปีปนปีปัจจุบัน:** ยืนยัน — `dividend_history` ของ 23/45 ตัวมีปี `2026` เป็นปีล่าสุด (ครึ่งปีแรก) · AMATA: `{2025: 1.1, 2026: 0.6}` → 0.6 < 0.77 → ติด SHRINKING (−10) ทั้งที่ 2026 ยังจ่ายไม่ครบ (cache AMATA มีงวด ม.ค.–มิ.ย. 2026 0.6 บาท) · ตัดปี 2026 ออก: 25 → 10 ตัว (หลุด 15 ตัว) · คะแนนที่จะเปลี่ยน (จากสคริปต์): AMATA 30→40, PTTEP 24→34, ILM 23→33, TU 18→28, GVREIT 16→26, SAT 14→24, UTP 7→17, AEONTS 6→16, SCCC 6→16, IMPACT 4→14 (อีก 5 ตัวยัง 0 เพราะ disqualify)
- **ป้าย cash flow ไม่ติดเมื่อ `ccr` เป็น None:** ยืนยัน (`:500` `ccr is not None and ocf_positive`) · สังเคราะห์ ccr=None → ไม่มีป้าย CF → ด้าน CF = 0 · ข้อมูลจริง 14/39 ตัวที่ไม่ถูก disqualify **ไม่มีป้าย CF tier เลย** (เพราะ OCF ติดลบ 1 ปี หรือ ccr=None): TNL KTB SAK PRG KKP SCB TTB TCAP AP IMPACT SIRI AYUD SC SPALI · ตัวอย่างที่เห็นชัด: KTB ccr 2.12 / PRG ccr 5.58 / KKP ccr 2.93 ได้ C=8 (ได้แค่โบนัส ccr ไม่มี base) และ SAK/TTB/TCAP/AP ได้ C=0
- **ROE_FUELED_BY_DEBT หน่วย D/E ผิด:** `data['debt_to_equity']` เป็น **เปอร์เซ็นต์** (`data_adapter.py:352` ตั้งใจ "percentage for downstream schema compat"; `main()` หาร 100 ก่อนออก `metrics.de`) แต่ `:548` เทียบ `de > 2.0` โดยตรง = D/E > 2% → เกือบทุกตัวผ่าน · ข้อมูลจริง 45/45 ตัวมี raw D/E (=metrics.de×100) > 2.0 ทุกตัว (min เท่ากับ 9.3) · ผล: เงื่อนไข D/E ไม่กรองอะไร — ป้ายตัดสินด้วย ROE + int_cov + net_debt เท่านั้น · ติด 1 ตัว (SSP, D/E จริง 2.40x)

### ข้อ 3 — `anchor_scoring.py` เทียบ spec

**น้ำหนัก / ขั้น / cap / ลำดับ — เทียบทีละตัว (รัน `DEFAULT_SCORING_CONFIG` เทียบ spec ข้อความ):**

| หมวด | spec | โค้ด | ตรง |
|---|---|---|---|
| ปันผล base 14/6/2/0 · cap 35 · ROE +3/0/−5 | ✓ | `:18-33` | ตรง |
| โบนัส dps cagr (0,0)(3%,5)(6%,9)(10%,12)(15%,13) | step | `:25` | ตรง |
| CF base 17/9/0 · โบนัส (1.0,3)(1.5,6)(2.0,8) · cap 25 | ✓ | `:37-46` | ตรง |
| Moat base 10/4/0 · โบนัส (10y,5)(15y,9)(20y,11) · GM +2/0/−3 · cap 25 | ✓ | `:50-64` | ตรง |
| Long_hold additive 4+6 · eps_cv (0.40,0)(0.30,1)(0.20,2) · drop (−40,0)(−29,1)(−14,2)(−4,3) · cap 15 | v1.2 | `:68-81` | ตรง |
| penalty: −15 / −10 / −10 / −5 / −3 · disqualify 3 ป้าย | ✓ | `:85-92` | ตรง |
| ลำดับ 8 ขั้น (disqualify → 4 ด้าน → รวม cap 100 → หัก penalty → floor 0) | ✓ | `:244-272` | ตรง |

**`bonus_lookup` 3 โหมด ทดสอบค่าขอบ (ผลรัน an4.py):**

| โหมด | input → output |
|---|---|
| ปกติ (ccr) | None→0 · −1→0 · 0.99→0 · **1.0→3** · 1.5→6 · 2.0→8 · 5→8 |
| ปกติ (dps cagr) | None→0 · −0.1→0 · 0→0 · 0.0299→0 · **0.03→5** · 0.06→9 · 0.10→12 · 0.15→13 · 0.9→13 |
| ปกติ (roe ปี) | None/0/9→0 · 10→5 · 14→5 · 15→9 · 19→9 · 20→11 |
| `lower_is_better` (eps_cv) | None→0 · −0.1→2 · 0.20→2 · 0.2001→1 · 0.30→1 · 0.3001→0 · 0.40→0 · 0.41→0 |
| `lower_magnitude_is_better` (drop) | None→0 · −0.6→0 · −0.40→0 · −0.30→0 · **−0.29→1** · −0.20→1 · −0.14→2 · −0.04→3 · 0→3 · +0.2→3 |

จุดสังเกตขอบ: (ก) ค่าตรง threshold ได้คะแนนขั้นนั้น (≥) ตรง spec ทุกตัว · (ข) eps_cv = 0.20 พอดีได้ +2 ทั้งที่ spec เขียน "<20%" (ขอบเอนไปทางให้คะแนน) · (ค) eps_cv ติดลบได้ +2 (ไม่ควรเกิด; cv เป็นค่าบวกเสมอ) · (ง) ไม่มี None/ติดลบที่คืนค่าผิด

**ตัวอย่างใน spec รันด้วย `compute_*` จริง (an4.py):**

| ตัวอย่างใน spec | spec ว่า | โค้ดได้ | ตรง |
|---|---|---|---|
| CPALL ด้านปันผล (GROWING, cagr 13%, ROE_IMPROVING) | 14+12+3 = **29** | **29** | ตรง |
| PTT ด้านปันผล (STABLE, cagr 2.8%, ROE_DECLINING) | 6+**2**−5 = **3** | **1** (cagr 0.028 < 0.03 → bonus 0) · ที่ cagr 0.03 พอดีได้ 6+5−5 = 6 | **ไม่ตรง** — spec เขียน "+2 จาก cagr 2.8%" ขัดกับ "step function ไม่ interpolate" ในข้อความเดียวกัน (ไม่มีขั้น +2 ในตารางขั้น) |
| ด้าน CF PTT/SCC/ADVANC/BDMS (สบาย, ccr 0.87/0.80/0.96/0.91) | 17 | 17 | ตรง |
| ด้าน CF CPALL (พอใช้, ccr 0.67) | 9 | 9 | ตรง |
| ตาราง Verification: ADVANC ~57 / BDMS ~52 | ประมาณ | ไม่ได้คำนวณ (ไม่มีข้อมูลดิบของ 2 ตัวนี้) | `เดา:` ตัวเลข "~" ในตารางเป็นค่าประมาณจากมือ ไม่ใช่ output โค้ด |
| SCC หลัง penalty (spec: −28 → anchor 0 ในหมวด Phase 5, −30 ในตารางตรวจ) | ขัดกันเอง: −28 vs −30 | โค้ดรวม −15−10−3 = **−28** | spec ภายในไม่ตรงกัน (ตารางตรวจเขียน −30 ซึ่งเป็นค่าก่อน v1.2) |
| `__main__` CPALL sample ใน `anchor_scoring.py:289-307` | — | **78** (D29+C17+M19+L13) | — |
| CPALL ตามกฎ DETERIORATING → 0 | 0 | `compute_anchor_score([... 'CASHFLOW_DETERIORATING'])` → 0 `disqualified=True` | ตรง |

**คะแนนสูงสุดที่เป็นไปได้จริง (รันด้วยค่าสุดทาง):** ปันผล **30** (14+13+3 — spec ว่า cap 35 "max ~30" ✓) · CF **25** (HEALTHY 17 + 8; ถ้า OK ได้แค่ 17) · Moat **23** (10+11+2) · Long_hold **15** · **รวม 93** (`TOTAL MAX 93`) ไม่ใช่ 100 — `total_cap` 100 (`anchor_scoring.py:83`) ไม่มีวันถูกใช้ — คะแนนหน้ารายงานสูงสุดทางทฤษฎีคือ 9.3/10.0 ไม่ใช่ 10.0

**ทำไมสูงสุดทั้งตลาด 08-22 ได้แค่ 45 — แจกแจง 45 ตัวที่ผ่าน (an1/an2/an5/an12):**

| ด้าน | max จริง / เพดาน | เฉลี่ย (39 ตัวที่ไม่โดน 0) | ทำไมต่ำ |
|---|---|---|---|
| ปันผล | **18** / 30 | 9.4 | ทั้ง 45 เป็น `NEW_PAYER` (base 2) เพราะ `dividend_streak` สูงสุด 6 — ไม่มีตัวไหนถึง 10 ปี → ไม่มี `STABLE_PAYER` (6) / `GROWING` (14) · 18 = 2+13+3 |
| CF | 25 / 25 | 12.7 | ปกติ (HEALTHY 15 ตัว, 3 ตัวได้ 25) · 8 ตัวได้ 0 |
| Moat | **12** / 23 | **1.6** | 24/39 ได้ 0 · STRONG ติดแค่ 1 (SAK), MODERATE 8 · โบนัส ROE-years ไม่มีตัวไหนได้เลย (สูงสุด `roe15y` = 9 และ 9 <10) |
| Long_hold | 11 / 15 | 2.7 | 13/39 ได้ 0 · STABLE_BUSINESS ติด 4, RESILIENT 11 |

สาเหตุ 3 ชั้น:
1. **ข้อมูลปันผลสั้น (เฉพาะสแกน 08-22):** `dividend_history` ลึกสุด 7 ปี (6–7 ปีใน 41/45 ตัว) vs สแกน 08-15 ลึก 28 ปี · ตัวเลขเทียบ: 08-15 → STABLE_PAYER 25 + GROWING 4 + NEW 17 · 08-22 → NEW 45 · สาเหตุที่พิสูจน์ได้: `data\set_dividend_cache\*.json` (fetched 2026-08-15T23:xx UTC = รีเฟรชอาทิตย์ 08-16) — **502 จาก 933 ไฟล์มี event เก่าสุดเป็นปี 2021**, อีก 140 ไฟล์ไม่มี event (ไม่ใช่ 20+ ปีแบบรอบก่อน) → `set_official_adapter` ดึงมาแค่หน้าต่าง ~5 ปี · **`เดา:`** สาเหตุที่ API set.or.th คืนหน้าต่างสั้นลง (ไม่ได้ตรวจฝั่ง API) · สแกนที่ประวัติปันผลสั้นเกิดซ้ำ: 07-18 (streak สูงสุด 10), 07-25 (6), 08-08 (6), 08-22 (6) เต็มรูปแบบ + 07-04 บางส่วน (streak สูงสุด 27 แต่ median ความลึกประวัติ 6 ปี) = 5 จาก 11 สแกน (ผล an3.py)
2. **ด่านเข้ม + ด้านที่ให้คะแนนยาก:** แม้สแกนปกติ 08-15 (ข้อมูล 28 ปี) สูงสุดก็ 48 และ **ถึง ≥50 แค่ครั้งเดียวในทั้ง 11 สแกน** (51 ที่ 2026-06-27 ตัวเดียว) · ไม่เคยมีตัวไหน ≥80 · moat เฉลี่ย 1.5/25, long_hold เฉลี่ย 2.7/15 ในสแกนปกติ · เหตุ: ด่าน P/E≤15 + P/BV≤1.5 คัดหุ้น ROE ไม่สูงมาก → โบนัส moat (ROE≥15% ติด 10+ ปี) แทบไม่มีใครได้
3. **เพดานโค้ด 93** (ข้างบน)

ตารางแจกแจง 45 ตัว (เรียงคะแนน · `D/C/M/L` = ปันผล/CF/moat/long_hold · `pen` = penalty · cagr = `dps_cagr` · ccr = `ccr_avg_3y` · roe15y = ปีที่ ROE≥15% ติดกัน · ป้าย: NEWP ตัดออก/ทุกตัวเป็น NEW_PAYER):
```
CIMBT.B Banking        45 D15 C25 M2 L6 pen -3 cagr 0.638 ccr 3.41 roe15y 0 | ROEst CFH NOMOAT CYC RES
CMR.BK  Health Care Se 45 D18 C20 M0 L7 pen 0 cagr 0.332 ccr 1.17 roe15y 1 | ROEup CFH NOMOAT MIX RES
STANLY. Automotive     42 D15 C17 M2 L8 pen 0 cagr 0.253 ccr 0.9 roe15y 0 | ROEst CFH NOMOAT MIX RES
ALUCON. Packaging      38 D11 C20 M0 L7 pen 0 cagr 0.099 ccr 1.06 roe15y 0 | ROEst CFH NOMOAT MIX RES
KBANK.B Banking        38 D15 C20 M4 L2 pen -3 cagr 0.411 ccr 1.22 roe15y 0 | ROEst CFH MOD CYC
BBL.BK  Banking        36 D18 C20 M0 L1 pen -3 cagr 0.32 ccr 1.45 roe15y 0 | ROEup CFH NOMOAT CYC
PTT.BK  Energy & Utili 36 D15 C17 M0 L7 pen -3 cagr 0.229 ccr 0.96 roe15y 0 | ROEst CFH NOMOAT CYC RES
AWC.BK  Property Devel 34 D18 C17 M2 L0 pen -3 cagr 0.65 ccr 0.89 roe15y 0 | ROEup CFH NOMOAT CYC
SUC.BK  Fashion        34 D5 C20 M2 L7 pen 0 cagr 0.0 ccr 1.36 roe15y 0 | ROEup CFH NOMOAT MIX RES
TNL.BK  Finance & Secu 31 D18 C8 M2 L6 pen -3 cagr 0.537 ccr 6.93 roe15y 0 | ROEup NOMOAT CYC RES
AMATA.B Property Devel 30 D18 C25 M0 L0 pen -13 cagr 0.201 ccr 2.31 roe15y 0 | SHR ROEup CFH NOMOAT CYC
KTB.BK  Banking        29 D18 C8 M6 L0 pen -3 cagr 0.576 ccr 2.12 roe15y 0 | ROEup MOD CYC
METCO.B Electronic Com 29 D15 C9 M2 L6 pen -3 cagr 0.246 ccr 0.59 roe15y 1 | ROEst CFO NOMOAT CYC RES
SAK.BK  Finance & Secu 25 D14 C0 M12 L2 pen -3 cagr 0.131 ccr -0.18 roe15y 0 | ROEst STR CYC
PTTEP.B Energy & Utili 24 D14 C17 M6 L0 pen -13 cagr 0.086 ccr 0.78 roe15y 0 | SHR ROEup CFH MOD CYC
ILM.BK  Commerce       23 D5 C17 M6 L5 pen -10 cagr -0.013 ccr 0.89 roe15y 0 | SHR ROEup CFH MOD STAB
PRG.BK  Food & Beverag 23 D9 C8 M0 L6 pen 0 cagr 0.137 ccr 5.58 roe15y 0 | ROEdn NOMOAT STAB
HTC.BK  Food & Beverag 19 D2 C17 M0 L10 pen -10 cagr -0.024 ccr 0.94 roe15y 0 | SHR ROEst CFH NOMOAT STAB RES
TU.BK   Food & Beverag 18 D0 C17 M0 L11 pen -10 cagr 0.0 ccr 0.75 roe15y 0 | SHR ROEdn CFH NOMOAT STAB RES
KKP.BK  Banking        17 D10 C8 M0 L2 pen -3 cagr 0.204 ccr 2.93 roe15y 0 | ROEdn NOMOAT CYC
SCB.BK  Banking        17 D15 C3 M0 L2 pen -3 cagr 0.19 ccr 1.0 roe15y 0 | ROEst NOMOAT CYC
SSP.BK  Energy & Utili 17 D10 C17 M2 L1 pen -13 cagr 0.965 ccr 0.86 roe15y 0 | ROEdn CFH DEBT CYC
GVREIT. Property Fund  16 D9 C17 M0 L0 pen -10 cagr 0.111 ccr 0.95 roe15y 0 | SHR ROEdn CFH NOMOAT MIX
TTB.BK  Banking        16 D18 C0 M0 L1 pen -3 cagr 0.244 ccr 0.65 roe15y 0 | ROEup NOMOAT CYC
QH.BK   Property Devel 15 D2 C25 M0 L1 pen -13 cagr -0.206 ccr 3.12 roe15y 0 | SHR ROEst CFH NOMOAT CYC
LANNA.B Energy & Utili 14 D10 C17 M0 L0 pen -13 cagr 0.272 ccr 0.73 roe15y 0 | SHR ROEdn CFH NOMOAT CYC
SAT.BK  Automotive     14 D2 C17 M4 L1 pen -10 cagr -0.03 ccr 0.92 roe15y 0 | SHR ROEst CFH MOD MIX
TCAP.BK Banking        13 D14 C0 M0 L2 pen -3 cagr 0.142 ccr 0.34 roe15y 0 | ROEst NOMOAT CYC
KGI.BK  Finance & Secu  9 D2 C20 M0 L0 pen -13 cagr 0.044 ccr 1.28 roe15y 0 | SHR ROEdn CFH NOMOAT CYC
UTP.BK  Paper & Printi  7 D0 C17 M0 L0 pen -10 cagr 0.004 ccr 0.94 roe15y 0 | SHR ROEdn CFH NOMOAT MIX
AEONTS. Finance & Secu  6 D0 C17 M0 L2 pen -13 cagr -0.105 ccr 0.85 roe15y 0 | SHR ROEdn CFH NOMOAT CYC
SCCC.BK Construction M  6 D2 C17 M0 L0 pen -13 cagr -0.126 ccr 0.91 roe15y 0 | SHR ROEst CFH NOMOAT CYC
AP.BK   Property Devel  4 D0 C0 M6 L1 pen -3 cagr 0.029 ccr -0.17 roe15y 0 | ROEdn MOD CYC
ASIAN.B Food & Beverag  4 D0 C17 M0 L0 pen -13 cagr -0.157 ccr 0.96 roe15y 0 | SHR ROEdn CFH NOMOAT CYC
IMPACT. Property Fund   4 D14 C0 M0 L0 pen -10 cagr 0.092 ccr None roe15y 0 | SHR ROEup NOMOAT MIX
SIRI.BK Property Devel  4 D10 C3 M4 L0 pen -13 cagr 0.038 ccr 1.44 roe15y 0 | SHR ROEup MOD CYC
AIMIRT. Property Fund   0 D0 C0 M0 L0 pen 0 cagr 0.111 ccr -4.47 roe15y 0 | SHR ROEst CFDET NOMOAT MIX
AYUD.BK Insurance       0 D5 C0 M0 L0 pen -13 cagr 0.026 ccr 0.07 roe15y 1 | SHR ROEup NOMOAT CYC
FTREIT. Property Fund   0 D0 C0 M0 L0 pen 0 cagr 0.151 ccr 0.12 roe15y 0 | SHR ROEup CFDET NOMOAT MIX
KYE.BK  Home & Office   0 D0 C0 M0 L0 pen 0 cagr -0.087 ccr 0.73 roe15y 0 | SHR ROEdn CFDET NOMOAT CYC RES
NER.BK  Agribusiness    0 D0 C0 M0 L0 pen 0 cagr -0.213 ccr 0.2 roe15y 9 | SHR ROEdn CFDET NOMOAT ERODE MIX
PROSPEC Property Fund   0 D0 C0 M0 L0 pen 0 cagr 0.074 ccr None roe15y 0 | SHR ROEup FAKE MOD MIX
RCL.BK  Transportation  0 D0 C0 M0 L0 pen 0 cagr 0.0 ccr 1.02 roe15y 2 | SHR ROEdn CFH CFDET NOMOAT CYC
SC.BK   Property Devel  0 D0 C0 M0 L1 pen -13 cagr -0.167 ccr 0.22 roe15y 0 | SHR ROEdn NOMOAT CYC
SPALI.B Property Devel  0 D0 C0 M0 L1 pen -13 cagr 0.016 ccr 0.05 roe15y 0 | SHR ROEdn NOMOAT CYC
```
คำย่อป้าย: CFH=CASHFLOW_HEALTHY · CFO=CASHFLOW_OK · CFDET=CASHFLOW_DETERIORATING · FAKE=FAKE_PROFIT · STR/MOD/NOMOAT=moat · ERODE=MOAT_ERODING · DEBT=ROE_FUELED_BY_DEBT · CYC/MIX/STAB/RES=ป้ายเสถียร · SHR=DIVIDEND_SHRINKING · ROEup/dn/st=ROE trend

**ป้ายที่ติดใน 45 ตัว:** NEW_PAYER 45 · NO_MOAT 35 · CYCLICAL 29 · CASHFLOW_HEALTHY 25 · DIVIDEND_SHRINKING 25 · ROE_DECLINING 16 · ROE_IMPROVING 15 · ROE_STABLE 14 · MIXED_STABILITY 12 · RESILIENT 11 · MODERATE_MOAT 8 · CASHFLOW_DETERIORATING 5 · STABLE_BUSINESS 4 · CASHFLOW_OK 1 · STRONG_MOAT 1 · ROE_FUELED_BY_DEBT 1 · MOAT_ERODING 1 · FAKE_PROFIT 1 · (STABLE_PAYER / GROWING_DIVIDEND / INTERMITTENT / YIELD_TRAP / CASHFLOW_BELOW_PROFIT = 0)
**penalty ที่ถูกหักจริง:** CYCLICAL −3 × 27 · DIVIDEND_SHRINKING −10 × 19 · ROE_FUELED_BY_DEBT −10 × 1

### ข้อ 4 — ผลกระทบของ "ได้ 0 ทันที" (ข้อมูล 08-22)

**โดน disqualify 6 ตัว จาก 45** (13%) — นับจาก `disqualified=True`:

| หุ้น | sector | ป้ายที่ทำให้ 0 | ถูกต้องตาม spec/สูตรไหม |
|---|---|---|---|
| AIMIRT | Property Fund & REITs | CASHFLOW_DETERIORATING (decline −90%) | **ไม่** — OCF 3 ปีล่าสุดเฉลี่ย −62.5M ดีกว่า 3 ปีก่อน −640M (sign พลิก) + REIT ต้องถูกยกเว้น v1.2 |
| FTREIT | Property Fund & REITs | CASHFLOW_DETERIORATING (decline −509%) | **ไม่** — OCF เฉลี่ยล่าสุด +1,684M vs ก่อนหน้า −412M (ดีขึ้น) + REIT ต้องยกเว้น |
| NER | Agribusiness | CASHFLOW_DETERIORATING (−461%) + MOAT_ERODING | CFDET **ไม่** (ล่าสุด +477M vs ก่อนหน้า −132M) แต่ยัง 0 อยู่ดีเพราะ MOAT_ERODING (roe15y=9 + GM declining) |
| PROSPECT | Property Fund & REITs | FAKE_PROFIT | **ไม่** — REIT ต้องยกเว้น v1.2 (ชื่อ sector ไม่ตรง) |
| KYE | Home & Office Products | CASHFLOW_DETERIORATING (−36%) | ถูกตามสูตร: OCF เฉลี่ย 3 ปีล่าสุด 333M vs 518M |
| RCL | Transportation & Logistics | CASHFLOW_DETERIORATING (−40%) (+CFH) | ถูกตามสูตร: เฉลี่ย 9,921M vs 16,467M (OCF ปี 2025 11,252M ยังเป็นบวกและ ccr 1.02) |

นับตามป้าย: `CASHFLOW_DETERIORATING` 5 (AIMIRT FTREIT KYE NER RCL) · `MOAT_ERODING` 1 (NER ซ้อน) · `FAKE_PROFIT` 1 (PROSPECT) · **จริง ๆ ถูกต้องตาม spec = 2 ตัว (KYE, RCL) + NER (ถูกจาก ERODING)** · อีก 3 ตัว (AIMIRT FTREIT PROSPECT = REIT) ควรไม่ถูก disqualify ตาม v1.2 → ได้ 0 ผิด

**ผลต่อคะแนน:** 6 ตัวนี้ได้ 0 และยังนับอยู่ใน "ผ่านด่าน 45" (ไม่ถูกตัดออกจากรายการ) · ตัวอย่างฝั่ง REIT ที่ไม่โดน DQ: IMPACT (ccr=None) ได้ D14 C0 M0 L0 −10 = 4 เพราะไม่มีป้าย CF · ไม่ได้คำนวณใหม่ว่า 3 REIT จะได้กี่คะแนนถ้าไม่โดน DQ (ต้องรัน pipeline เต็ม ซึ่งห้าม) → `เดา:` ได้ระดับ 4–15 เหมือน REIT อื่น

**CASHFLOW_DETERIORATING วัดจากกี่ปี — ไม่ใช่ปีเดียว:** `ocf_yoy_decline_pct` (`fetch_data.py:252-257`) = `เฉลี่ย OCF 3 ปีล่าสุด ÷ เฉลี่ย OCF 3 ปีก่อนหน้า − 1` ต้องมีข้อมูล ≥6 ปี (ไม่รวมปีปัจจุบัน) · ชื่อ `yoy` ทำให้เข้าใจผิด · plan ต้นทางให้ต้อง "ลดทั้ง 2 transition" ด้วย แต่โค้ดไม่ใช้ `ocf_consecutive_declining_years` (`:260-267` คำนวณไว้เฉย ๆ) · กรณี `earlier_avg < 0` สูตรให้ค่าเกินจริงและเครื่องหมายกลับ (ตัวอย่างข้างบน 3 ตัว) · ขอบ: `≤ −0.20` พอดี → ติด (ทดสอบ `-0.2` → ติด `CASHFLOW_DETERIORATING`)

**ข้อสังเกตผลกระทบเชิงระบบ:** disqualify เกิดจากป้ายที่คำนวณจากตัวเลข OCF เฉลี่ย 6 ปี จุดเดียว → หุ้นที่ OCF พลิกจากติดลบเป็นบวก (กิจการฟื้น) ถูกตัดคะแนนเป็น 0 ทั้งหมด ไม่มี penalty ระดับกลาง

### ข้อ 5 — ระบบเตือนขาย (`detect_exit_signal` + `exit_baselines.json` + `telegram_alert.py`)

| ประเด็น | ผลตรวจ |
|---|---|
| ใครเรียก | `screen_stocks.py:824` (หุ้น REVIEW ใน watchlist) · `:867` (หุ้น PASS ใน watchlist) · ไม่มีที่อื่น |
| รันตอนไหน | ในการสแกน `main()` เท่านั้น — เดิม server เสาร์ 09:00 · **ตอนนี้ไม่มี schedule** (ดูข้อ 7) |
| key ตรงกันไหม | ตรง: `save_exit_baseline` เขียน `passed_5555` / `pe_baseline` (`:302-303`) · `detect_exit_signal` อ่านชื่อเดียวกัน (`:182,:195`) · ทดสอบ: baseline LH.BK + P/E 16.1 → `FILTER_DEGRADATION`; P/E 11.7 vs baseline 3.7 → `VALUATION_BUBBLE high (3.2x)` (ผลรัน an11.py) → **ตัวฟังก์ชันทำงานถูก** |
| baseline เซฟเมื่อไร | `:853-863` เมื่อป้ายเก่า `NIWES_5555` ติดตอนผ่านด่าน · `exit_baselines.json` 62 รายการ, modified 2026-08-22 09:19 · date_added: 53 รายการ 2026-05-18 (สแกนแรก), ที่เหลือทยอยเพิ่ม · date_refreshed 39 รายการ = 08-22 · `thesis_change_flag` เป็น true: 0 รายการ · **ไม่มีโค้ดใดตั้ง flag นี้** (grep: อยู่แค่ใน `screen_stocks.py:164,213,309` — "Plan 07 manual" ไม่เคยทำ) |
| **ทำงานจริงไหม** | **ไม่ — ไม่เคยยิง trigger เลยทั้ง 11 สแกน** (นับ `exit_triggers` ในทุกไฟล์ = 0) |
| **ทำไมไม่ทำงาน (บั๊ก)** | `main()` ข้ามหุ้น FAIL ด้วย `continue` (`:789-807`) **ก่อนถึง** `detect_exit_signal` → `FILTER_DEGRADATION` ซึ่งต้อง `hard_filter != PASS` จึงเกิดได้เฉพาะหุ้น REVIEW (`:824`) · สำหรับหุ้น PASS (`:867`) เงื่อนไขนี้เป็นไปไม่ได้เลย · หุ้นที่ตกเป็น FAIL จริง = กรณีสำคัญสุด ไม่ถูกตรวจ |
| หลักฐานกรณีจริง | LH.BK อยู่ใน watchlist, มี baseline (`passed_5555`, pe_baseline 11.77, เพิ่ม 05-18), อยู่ใน PASS ครบ 10 สแกนแรก (05-18 → 08-15) → 08-22 ตก FAIL `['P/E 16.1 > 15']` → **ไม่มี trigger** (ไฟล์ screener ไม่มีที่เก็บ LH) · baseline 62 ตัว: 19 ตัวตอนนี้ FAIL ทั้งหมดไม่ถูกตรวจ |
| ขนาดการเตือน | แม้ได้ trigger: `FILTER_DEGRADATION` ที่มีเหตุผลเดียวให้ severity `medium` (ทดสอบ LH: `severity: 'medium'`) → `scan.py:90-99` ส่ง Telegram เฉพาะ `high` → ไม่ถูกส่ง · และ `scan.py` อ่าน `candidates` ไม่อ่าน `review_candidates` → trigger ของหุ้น REVIEW ไม่ส่งแม้เป็น high |
| กฎ `15-exit-rules.md` Rule 2 | ระบุ "streak ขาด" เป็นเหตุเข้าข่าย — `hard_filter` ไม่มีด่าน streak จึงตรวจไม่ได้ (ข้อ 1) · Rule 1 (thesis change) ไม่มีตัวตรวจอัตโนมัติ (flag ว่าง) · Rule 3 ทำงานได้ (VALUATION_BUBBLE 3×/2×) |
| Telegram | `.env` มีทั้ง `TELEGRAM_BOT_TOKEN` และ `TELEGRAM_CHAT_ID` (ตรวจแค่ชื่อ key) · `send_alert` ใช้โดย `daily_price_refresh.py:224` (ไม่ใช่ใน scope) · `send_exit_alert` ไม่เคยถูกเรียกจริงเพราะไม่มี high trigger |

**หุ้นที่ Art ถือจริง (AMATA BBL TCAP TOA SISB SECURE MOSHI TISCO) อยู่ใน watchlist ไหม — ใน `user_data.json` มีแค่ TISCO (จาก 8 ตัว):** watchlist ทั้งหมด = `LH.BK METCO.BK QH.BK SAT.BK TISCO.BK` (อัปเดตล่าสุด 2026-04-28) · AMATA/BBL/TCAP มี baseline และผ่านด่านอยู่ แต่ **ไม่ได้อยู่ใน watchlist → ไม่เคยถูกตรวจ exit** · TOA/SISB/SECURE/MOSHI/TISCO ตก FAIL ใน 08-22 (TOA yield 4.9% + P/BV 1.93 · SISB P/BV 2.29 · SECURE market cap 1.3B · MOSHI EPS 3 ปี + P/E 18.6 + P/BV 5.08 · TISCO P/BV 2.35) และ **ไม่มี baseline** (ไม่เคยผ่านด่าน) → ต่อให้ซ่อมบั๊ก FAIL ก็ตรวจ FILTER_DEGRADATION ไม่ได้เพราะ `passed_5555` ไม่เคยเป็น true · ระบบนี้ออกแบบมาจับ "หุ้นที่เคยผ่านแล้วหลุด" ไม่ใช่ "หุ้นที่ Art ถือ"

### ข้อ 6 — ป้ายชุดเก่า `assign_signals` กับชุดใหม่

| ป้ายเก่า (`screen_stocks.py:333-407`) | เงื่อนไข | ซ้ำ/ขัดกับป้ายใหม่ | ผลจริง |
|---|---|---|---|
| NIWES_5555 | yield≥5, **streak≥5**, EPS 5/5, PE 0–15, PBV 0–1.5 (hardcode `:368`) | ซ้ำกับ `hard_filter` ทุกข้อยกเว้น streak (ซึ่งด่านไม่เช็ค) | 39/45 ติด · SCB (streak 4) ไม่ติด (ผ่านด่านโดยไม่มีป้าย) · เป็นตัวสั่ง `save_exit_baseline` (`:853`) |
| NIWES_GROWING | yield 2–5 + growth_streak≥3 + EPS + PE/PBV | ซ้ำ exception ใน `hard_filter` | 5 ตัว |
| QUALITY_DIVIDEND | yield≥5, payout<70%, streak≥10 | **ซ้อน** STABLE/GROWING_DIVIDEND (streak≥10) | 0 ใน 08-22; 120 ครั้งรวมทุกสแกน |
| DIVIDEND_TRAP | yield>8 + ROE ลดลง**ทุกปีติดกันตลอดประวัติ** + payout>100% (`:399-403`) | **ขัด/ซ้ำ** YIELD_TRAP (ใหม่: yield>8 + streak<5) คนละนิยาม ชื่อใกล้กัน | **ไม่เคยติดเลย 0 ครั้งทั้ง 11 สแกน** (ROE ต้องลดทุกปีทั้ง 16 ปี) · หมวด "Watch Out" ของรายงานอาศัยป้ายนี้ → ว่างตลอด |
| YIELD_SPIKE_FROM_PRICE_DROP | yield ≥1.8× เฉลี่ย 5 ปี | ไม่ซ้ำ (ไม่มีป้ายใหม่เทียบ) | 5 ตัว |
| DEEP_VALUE | PE≤8 + PBV≤1.0 (hardcode แทน `bonus_pe/bonus_pbv`) | ไม่ซ้ำ | 10 ตัว |
| HIDDEN_VALUE / DATA_WARNING / DATA_INCOMPLETE | — | ไม่ซ้ำ | HIDDEN 2 · WARNING 3 |
| BRAND_MOAT / STRUCTURAL_MOAT / GOVT_LOCKIN (`case_study_detector.py:detect_moat_tags`) + RETAIL_DEFENSIVE_MOAT ฯลฯ (pattern file) | sector keyword + margin/mcap | **ขัด** กับ moat tier ใหม่ (ใช้ ROE/GM): 08-22 มี `RETAIL_DEFENSIVE_MOAT` 5 ตัว แต่ 4 ตัว (PRG HTC TU ASIAN) ได้ `NO_MOAT` · BANK_VALUE_PBV1 ติด CIMBT/BBL ที่ NO_MOAT | แสดงในรายงานเป็นคำอธิบายว่า moat ทั้งที่คะแนน moat = 0 |

**ใครยังใช้ชุดเก่า:** `report_template.py:_top_pick_md` (พิมพ์ `signals` + narrative) และ Watch Out · `history_manager.py` (`NIWES_5555` → `HELD`/entry_thesis, tags) · `save_exit_baseline` ผ่าน `NIWES_5555` · **ชุดใหม่ (`anchor_stage_tags`) ไม่ถูกพิมพ์ในรายงาน** (พิมพ์แค่ breakdown + penalty tags) — ใช้ในคะแนน + `scan_anchor.py` เท่านั้น → คนอ่านรายงานเห็นป้ายเก่าที่ไม่ตรงกับที่ให้คะแนน

**`valuation_grade` (`:590-674`):** คำนวณ A–F (PEG 20 + P/E vs median sector 35 + yield vs 5y avg 30 + ตำแหน่ง 52w 15) ทุก candidate เก็บใน `candidates[].valuation` · ใช้ทำอย่างเดียว: ถ้า grade F ใส่ `OVERPRICED` ใน `signals` (`:971-972`) · **ไม่เข้าคะแนน** (`:968-969` ระบุ "score modifier removed") · ออกในรายงานหรือไม่: **ไม่ออกเกรด** — รายงานมีเฉพาะบรรทัด narrative ของ `OVERPRICED` (`report_template.py:35`) ซึ่งไม่ปรากฏใน 08-22 (เกรด 08-22: C 21 · B 12 · D 9 · A 3 · F 0) · ผู้ใช้หลักเดิมคือ web (เก็บแล้ว) · ใน 11 สแกนเคยติด OVERPRICED รวม 9 ครั้ง

### ข้อ 7 — `scan_anchor.py` กับ `scan.py`, `report_template.py`, schedule

| | `scan.py` | `scan_anchor.py` |
|---|---|---|
| ทำอะไร | อ่าน screener ล่าสุด → รายงานหลัก `reports\scan_<วัน>.md` + `history.json` + Telegram | อ่าน screener → **คำนวณ `compute_anchor_score` ซ้ำ** → `reports\anchor_scan_<วัน>.md` แบ่ง band High≥80 / Mid≥50 / Low / DQ |
| ตัวที่ใช้จริง | **ใช่** (server pipeline เรียกทุกเสาร์) | **ไม่** — รันมือครั้งเดียว ไฟล์เดียวใน `reports\` คือ `anchor_scan_2026-05-18.md` · ไม่มี caller |
| ปัญหา | alert อ่านเฉพาะ `candidates` | band 80/50 ไม่เคยมีใครถึงเกณฑ์ (สูงสุด 51, ≥80 = 0) → เกือบทั้งหมดไป "Low" · glob ไม่กรอง regex (`:26`) · คำนวณซ้ำทั้งที่ screener เก็บ `score`+`breakdown` ไว้แล้ว |

**`report_template.py` พิมพ์อะไร/ตรง field ไหม:** อ่าน `candidates[].{symbol,name,sector,signals,metrics.dividend_yield,metrics.pe,metrics.pb_ratio,aggregates.dividend_streak,display_score,disqualified,disqualify_tags,breakdown,penalty,penalty_tags,exit_triggers}` + `review_candidates[].review_reasons` — ตรงกับ screener ทั้งหมด **ยกเว้น 1 field:** `c.get("reasons")` (`:97`) ไม่มีใน screener → พิมพ์ `**Reasons:** ` ว่างทุกตัว (รายงาน 08-22: 10 ตัวว่างทั้ง 10) · ไม่พิมพ์ `anchor_stage_tags`, `valuation`, `in_watchlist`, `previous_score`/`score_streak_weeks` ที่ screener เก็บไว้ · Top 10 เรียงตาม `score` (int) · อันดับ 1 ของ 08-22 คือ CIMBT yield 15.95% PBV 0.25 ติด `DATA_WARNING` — รายงานบอกเป็นบรรทัด signal เท่านั้น ไม่กันออก

**history_manager.py:** `yield` ในทุกแถว `top_candidates` / `entry_thesis` เป็น `None` (อ่าน `metrics.dy` — screener ใช้ `dividend_yield`; `history.json` สแกนล่าสุด `top_candidates[0].yield = None`) · `watchlist_status.status` = `HELD` ถ้ามี NIWES_5555 มิฉะนั้น `REVIEW` ไม่ได้อ้างผลตรวจ exit

**schedule ที่หายไปพร้อม server:**

| งานอัตโนมัติ | ตัวตั้ง | สถานะตอนนี้ |
|---|---|---|
| สแกนรายสัปดาห์ (fetch_data → update_universe → screen_stocks → scan) | `config.json` `schedule` เสาร์ 09:00 (`enabled: true`) → APScheduler ใน `_archive\2026-10\server\app.py:1190-1198` + PIPELINE_MAP `:893` | **หยุด** — สแกนล่าสุด 2026-08-22 · log server หยุดที่ 2026-08-27 19:00 · ไม่มีสแกนหลัง 08-22 (สแกน 08-29 และหลังจากนั้นไม่มี) · `config.json` ยังเขียน `enabled: true` แต่ไม่มีใครอ่าน (หลอกตา) |
| รีเฟรชปันผล set.or.th ทุกอาทิตย์ 06:00 (ป้อน cache ที่สแกนเสาร์อ่าน) | APScheduler `:1229-1241` | **หยุด** — cache รอบสุดท้าย 08-16 (TTL 7 วัน `set_official_adapter.py:37`) · `เดา:` สแกนใหม่จะดึงสดผ่าน Playwright หรือตก fallback yahoo (ไม่ได้ทดสอบ) |
| รีเฟรชราคารายวัน 19:00 (`daily_price_refresh.py`) | APScheduler `:1208-1222` | **หยุด** — log สุดท้าย 2026-08-27 19:00 |
| Task Scheduler `Max Mahon Weekly` | Windows | `Disabled` (ผล `Get-ScheduledTask`; `_archive\2026-10\README.md` ระบุว่า disable ไว้) |
| ข้อสังเกต | log server ไม่มีบรรทัดรีเฟรชปันผลรอบ 2026-08-09 เลย (08-02 แล้วข้ามไป 08-16) | `เดา:` server ดับช่วงต้น-กลาง ส.ค. แล้วหยุดจริงหลัง 08-27 (ไม่ได้ตรวจสาเหตุที่ server ดับ) |

ผลต่อการใช้งานปัจจุบัน (Art ใช้ผ่านแชทกับ Claude): ถ้าจะใช้ `screener_2026-08-22.json` ตอบ ต้องรู้ว่าข้อมูลอายุ ~48 วันและเป็นรอบที่ประวัติปันผลสั้นผิดปกติ (คะแนนปันผลต่ำกว่าจริง) · ถ้าจะรัน scan ใหม่ ต้องสั่งมือ `py scripts\screen_stocks.py` ตามด้วย `scan.py` (ใช้เวลา ~20 นาทีตาม log: 09:00→09:19) และรีเฟรช cache ปันผลก่อน

## 3. จุดผิด / ไม่ตรง spec เรียงตามความแรง

(ทุกข้อมีผลรันจริงจาก an*.py ในโฟลเดอร์ files ของ desk · `path:บรรทัด` อยู่ใน `C:\WORKSPACE\projects\4-MaxMahon\scripts\`)

| # | ระดับ | path:บรรทัด | ผิดยังไง | ค่าจริง | กระทบอะไร |
|---|---|---|---|---|---|
| 1 | สูง | `screen_stocks.py:789-807` (+`:824,:867`) | หุ้น FAIL `continue` ก่อนเรียก `detect_exit_signal` → `FILTER_DEGRADATION` เกิดได้เฉพาะ REVIEW; หุ้น PASS เป็นไปไม่ได้ | `exit_triggers` ไม่เคยมีของเลยใน 11 สแกน · LH.BK (watchlist+baseline) PASS 10 สแกน → FAIL 08-22 (P/E 16.1) ไม่มีเตือน · 19/62 baseline ตอนนี้ FAIL | ระบบเตือนขายไม่ทำงานในกรณีหลักที่ออกแบบไว้ |
| 2 | สูง | `fetch_data.py:252-257` | `ocf_yoy_decline_pct = avg(3 ปีล่าสุด)/avg(3 ปีก่อน) − 1` เมื่อฐานติดลบ เครื่องหมายพลิก → OCF ที่ดีขึ้นกลายเป็น "เสื่อม" · ชื่อ `yoy` ทั้งที่เทียบ 6 ปี · ไม่ใช้เงื่อนไข "ลดทั้ง 2 transition" ของ plan | AIMIRT −90% (ล่าสุด −62M vs ก่อน −640M) · FTREIT −509% (+1,684M vs −412M) · NER −461% (+477M vs −132M) | ติด `CASHFLOW_DETERIORATING` → disqualify 3 ตัว (ผิด) |
| 3 | สูง | `screen_stocks.py:414` | ใส่ชื่อ sector `Property Fund & REIT` แต่ข้อมูลจริงเป็น `Property Fund & REITs` → การยกเว้น REIT ใน FAKE_PROFIT / CFDET (v1.2) ไม่ทำงาน · `sector_taxonomy.py` ไม่มีชื่อนี้ทั้งสองชุด | REIT 5 ตัวใน 45 · 3 ตัว (AIMIRT FTREIT PROSPECT) โดน DQ=0 | 3/6 ของ disqualify ทั้งหมดผิด spec |
| 4 | สูง | `screen_stocks.py:476-484` | `DIVIDEND_SHRINKING` เทียบปีล่าสุดของ `dividend_history` (ปี 2026 ที่จ่ายยังไม่ครบ) กับยอดสูงสุด 5 key · ไม่เช็ค "จ่าย ≥10 ปี" ตาม plan | 23/45 มีปี 2026 เป็นล่าสุด · ติด SHRINKING 25 → 10 ถ้าตัดปี 2026 · AMATA {2025:1.1, 2026:0.6} ถูกหัก −10 | 15 ตัวโดน −10 ผิด (AMATA 30→40, PTTEP 24→34 …) · ในสแกน 08-15 ก็ติด 16 |
| 5 | สูง (ข้อมูล) | ผลใน `data\set_dividend_cache\` (สร้างโดย `set_official_adapter.py` — ไม่แก้ในงานนี้) | cache รอบ 08-16 ได้ event เก่าสุดแค่ปี 2021 (502 จาก 933 ไฟล์) → `dividend_streak` ≤6 | ทั้ง 45 = `NEW_PAYER` · ด้านปันผลสูงสุด 18/30 · `เดา:` สาเหตุที่ API คืนหน้าต่าง ~5 ปี | คะแนนสแกน 08-22 ต่ำกว่าปกติเป็นระบบ · ไม่มี guard เตือนว่าประวัติสั้นผิดปกติ (5/11 สแกนเป็นแบบนี้) |
| 6 | กลาง | `screen_stocks.py:500-506` | ป้าย CF tier ต้องมี `ccr` ไม่ None **และ** OCF บวกครบ 3 ปี; ถ้า OCF ติดลบ 1 ปี → ไม่ติดป้ายใด · `CASHFLOW_BELOW_PROFIT` ติดแทบไม่ได้ | ไม่มีป้าย CF 14/39 ตัว · BELOW_PROFIT = 0 ใน 45 และ 0 ใน 11 สแกน · SAK/TTB/TCAP/AP ได้ C=0 ไม่มีเหตุผลบนป้าย | ด้าน CF 0 โดยไม่มีป้ายอธิบายและไม่มี penalty |
| 7 | กลาง | `screen_stocks.py:556-561` | `MOAT_ERODING` ติดเฉพาะเมื่อ ROE 15%+ ยัง**ติดต่อเนื่องจากปีล่าสุด** (+GM หด) — plan คือ "เคยสูงแล้วตก" | ROE 20%×10 ปีแล้วตก 5/4/3% → ไม่ติด · ติดแค่ NER (roe15y=9) | disqualify ป้ายนี้แทบไม่จับ moat เสื่อมจริง |
| 8 | กลาง | `screen_stocks.py:548` | `de > 2.0` เทียบกับ `debt_to_equity` ที่เป็น **เปอร์เซ็นต์** (D/E>2%) | 45/45 ตัว raw D/E >2.0 (min 9.3) · ROE_FUELED ติด 1 (SSP, D/E จริง 2.40x) | เงื่อนไข D/E ไม่กรองอะไร |
| 9 | กลาง | `fetch_data.py:77-96` | `count_dividend_streak` ข้ามปีที่ขาดใน dict (ไม่ break เมื่อ gap) | CIMBT: ปี {2020,2021,2022,2024,2025} (ไม่มี 2023) → streak = 5; ฟังก์ชันสังเคราะห์ → 5 | streak/ป้าย/NIWES_5555 สูงเกินจริงเมื่อ gap |
| 10 | กลาง | `screen_stocks.py:63-145` | `min_dividend_streak`, `bonus_pe`, `bonus_pbv` ใน config ไม่ถูกใช้ · `min_eps_positive_years` ใช้ `==` · `assign_signals` hardcode 5/15/1.5 | SCB streak 4 PASS (ไม่มีป้าย NIWES_5555) · ตั้ง min_eps=4 → SCB 5/5 ตก FAIL `EPS positive 5/5` | แก้ config ไม่มีผลตามที่เข้าใจ · doc 13 Adj.1 (ระดับ streak) ค้าง PENDING ไม่ตรงโค้ด |
| 11 | กลาง | `fetch_data.py:273-290` vs `screen_stocks.py:550` | STRONG/MODERATE ใช้ ROE 12%/8% (ธนาคาร 10%/7%) แต่โบนัสนับเฉพาะ ROE≥15% | ธนาคาร 8 ตัว `roe15y=0` ทุกตัว · SAK STRONG moat = 12 (10 + GM 2, โบนัส 0) · STRONG ทั่วไป ROE 12–14.9% ได้โบนัส 0 | โบนัส moat (สูงสุด +11) เข้าไม่ถึงสำหรับธนาคาร/ROE ปานกลาง · moat เฉลี่ย 1.6/25 |
| 12 | กลาง | spec `docs\scoring-anchor-spec.md` ตัวอย่างด้านปันผล PTT | เขียน "+2 จาก cagr 2.8%" ขัดกับตารางขั้น (3% ถึงได้ +5) | โค้ด: 6+0−5 = **1** (spec = 3); ที่ cagr 3.0% = 6 | ตัวอย่างใน spec ผิด หรือขาดขั้น 0<x<3% — ต้องให้ Art เคาะ |
| 13 | กลาง | `anchor_scoring.py:207-226` | โบนัส eps_cv / crisis drop ให้แม้ไม่ติด STABLE_BUSINESS/RESILIENT (spec: "ขยาย" ป้ายนั้น) | long_hold>0 โดยไม่มีป้ายใด 14/39 (KBANK BBL SAK KKP SCB SSP TTB QH SAT TCAP AEONTS AP SC SPALI) | ได้ 1–3 คะแนนฟรี ไม่ตรง "extend" |
| 14 | กลาง | `fetch_data.py:530-541,625` | `dps_cagr`/`dps_5y_cagr` = CAGR ตั้งแต่ปีแรกถึงปีสุดท้ายของประวัติ (รวมปี 2026 ครึ่งเดียว) ไม่ใช่ 5 ปี | ใน 08-22 ประวัติ 5–7 ปีเริ่มจากปีโควิด (CIMBT 0.005→0.059 = +63.8%) · 16/39 ตัวมี cagr ≥15% (เพดานโบนัส +13) | โบนัสปันผลบวมจากฐานต่ำ · ในสแกนปกติ cagr คิดจาก ~27 ปี (ไม่ใช่ 5y ตามชื่อ) |
| 15 | กลาง | `sector_taxonomy.py:24-26` | Banking/Finance/Insurance อยู่ CYCLICAL → โดน −3 ทุกตัวทั้งที่ spec ถือเป็น sector พิเศษ (ROE/FAKE_PROFIT) | 13/13 ตัวติด CYCLICAL_BUSINESS และถูกหัก −3 · 8 sector ไม่อยู่ทั้งสองชุด | อคติเป็นระบบต่อธนาคาร/ประกัน |
| 16 | ต่ำ | `history_manager.py:50,70` | อ่าน `metrics.dy` (ไม่มี; จริงคือ `dividend_yield`) | `yield` = None ทุกแถวใน `history.json` ล่าสุด | ประวัติเก็บ yield ไม่ได้ |
| 17 | ต่ำ | `report_template.py:97` | อ่าน `c["reasons"]` ที่ screener ไม่มี | `**Reasons:**` ว่าง 10/10 ใน `scan_2026-08-22.md` | รายงานมีหัวข้อว่าง |
| 18 | ต่ำ | `screen_stocks.py:487-489, 397-403` | `YIELD_TRAP` ลดรูปจาก "ตก ≥3 ใน 5 ข้อ" เหลือ yield>8 & streak<5 · `DIVIDEND_TRAP` (เก่า) ต้อง ROE ลดทุกปีทั้งประวัติ | YIELD_TRAP ติด 5 ครั้งรวม 11 สแกน (0 ใน 08-22) · DIVIDEND_TRAP 0 ครั้ง | ป้ายกันกับดักแทบไม่ทำงาน · "Watch Out" ในรายงานว่างตลอด |
| 19 | ต่ำ | `screen_stocks.py:472` | `INTERMITTENT` ไม่เช็ค years_paid_in_10y<8 / miss ใน 5 ปีล่าสุด | ติด 0 ใน 45 | ป้ายนี้ไม่แยกหุ้นจ่ายๆหยุดๆ |
| 20 | ต่ำ | `screen_stocks.py:82-84` | market cap return ก่อน ซ่อนเหตุผลอื่น · market_cap None แสดงเป็น "0.0B" | 662 ตัวมีเหตุผลเดียว | วิเคราะห์ว่าทำไมหุ้นตกยากขึ้น |
| 21 | ต่ำ | `scan.py:90-99`, `screen_stocks.py:188` | Telegram ส่งเฉพาะ severity high ของ `candidates`; FILTER_DEGRADATION เหตุผลเดียวได้ `medium` | ทดสอบ LH: `severity: medium` | ต่อให้ซ่อม #1 ก็ไม่แจ้ง Telegram |
| 22 | ต่ำ | spec FAKE_PROFIT ด้าน 2 vs plan | spec ตัวหนังสือ "≥1 ปี" ขัดกับ plan/โค้ด "≥2 ปี" | โค้ด: ocf_neg=1 ไม่ติด, =2 ติด | เอกสารขัดกันเอง ต้องให้ Art เคาะว่าตัวไหนจริง |
| 23 | ต่ำ | `data\screener_2026-08-22.json` | อันดับ 1 = CIMBT yield 15.95% PBV 0.25 ติด `DATA_WARNING` ยังเป็น Top Pick | คะแนน 45 | `เดา:` ข้อมูลผิดปกติ (PBV 0.25 ของแบงก์) ไม่ถูกกันออกจาก Top Picks |
| 24 | ต่ำ | `_smoke_scoring_v2.py` | เทสฟังก์ชันที่ถูกลบ | ล้ม 6/6 ImportError | เทสเสีย ไม่ตรวจอะไร |
| 25 | ต่ำ | `anchor_scoring.py:83` | `total_cap` 100 ไม่เคยถูกใช้; เพดานจริง 93 | `TOTAL MAX 93` | คะแนนหน้ารายงานเต็มไม่เกิน 9.3 |

## 4. ไฟล์ที่ควรเก็บกวาด + เหตุผล

| ไฟล์ | ทำอะไร | เหตุผล |
|---|---|---|
| `scripts\scan_anchor.py` | เก็บเข้า `_archive` | ไม่มี caller · ซ้ำงานกับ `scan.py` + screener (`score`/`breakdown` เก็บอยู่แล้ว) · band 80/50 ไม่เคยถึง · รันมือครั้งเดียว (`reports\anchor_scan_2026-05-18.md`) |
| `reports\anchor_scan_2026-05-18.md` | เก็บคู่ `scan_anchor.py` | ผลของสคริปต์ที่เลิกใช้ |
| `scripts\_smoke_scoring_v2.py` | ลบ/เก็บ | เทสฟังก์ชันที่ไม่มีแล้ว ล้ม 6/6 |
| `scripts\_smoke_dehardcode.py` | ย้ายไปกอง portfolio | เทส `portfolio_builder` ไม่ใช่ชั้นคัด (ผ่าน 3/3) |
| `config.json` ค่า `bonus_pe` `bonus_pbv` `min_dividend_streak` | ลบออกจาก config หรือทำให้โค้ดใช้ | ค่าตาย — config บอกว่าปรับได้แต่ไม่มีผล · `schedule` ก็ค่าตาย (ไม่มี scheduler อ่านแล้ว) |
| `data\exit_baselines.json.legacy`, `data\history.json.legacy` | ตรวจแล้วเก็บ | ชื่อ `.legacy` ค้างข้างไฟล์จริง (ไม่ได้เปิดดูเนื้อ — `เดา:` สำเนาก่อน migrate) |
| ที่ต้องเก็บไว้ | `screen_stocks.py` `anchor_scoring.py` `scan.py` `report_template.py` `history_manager.py` `case_study_detector.py` `sector_taxonomy.py` `telegram_alert.py` `_smoke_niwes_filter.py` | ยังเป็นสายหลัก (ต้องแก้ตามหมวด 3 ไม่ใช่ทิ้ง) |

หมายเหตุ: ไม่ได้แตะ/ลบไฟล์ใด — รายการนี้เป็นข้อเสนอสำหรับหัวตัดสิน
