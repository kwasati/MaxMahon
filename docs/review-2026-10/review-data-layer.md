# review-data-layer — ชั้นดึงข้อมูล Max Mahon (read-only review)

วันที่ตรวจ 2026-10-09 · หลักฐานจาก `data\screener_2026-08-22.json` + `data\set_dividend_cache\` + เรียกฟังก์ชันอ่านอย่างเดียว (สคริปต์ตรวจอยู่ในโต๊ะ krv3 (ไม่ได้ย้ายเข้า project): `recompute.py` `shrink.py` `probe_live.py` `yprobe.py`)
knowledge: ใบแนะนำ 3 ข้อในใบงาน (ตรวจแบบอ่านอย่างเดียว / อ่านไฟล์ยาวเป็นท่อน / ดึงเน็ตทีละไม่กี่ตัว) → ใช้ครบ: เรียกเฉพาะ `_build_aggregates(symbol=None)` กับ `set_official_adapter.fetch_dividends('BBL')` + yahoo `dividend_history` 3 ตัว (BBL TCAP AMATA) ไม่เขียนอะไรลง `data\`

## สรุปบรรทัดเดียว

ปัญหาใหญ่สุด = **ประวัติปันผลถูกตัดที่ ~6 ปี (FY2020–2025) เพราะ API set.or.th คืนข้อมูลย้อนหลังแค่ ~5 ปี** → `dividend_streak` ไม่เคยเกิน 6 → ป้าย `STABLE_PAYER`/`GROWING_DIVIDEND` (ต้อง ≥10) **เป็นไปไม่ได้เลย** · ผ่านด่าน 45/45 ตัวได้ `NEW_PAYER` · FY2020 ของแต่ละตัวมีแค่ final (interim ตกหน้าต่าง) → CAGR/growth เพี้ยน · ปี FY2026 ที่ยังไม่ครบถูกปนเข้า `dps_cagr` กับ `DIVIDEND_SHRINKING` (false positive 15 จาก 25 ตัว)

## 1. ตารางต่อไฟล์ (12 ไฟล์)

| ไฟล์ (scripts\) | ทำอะไร | ใครเรียก | ใช้หลังเก็บ server? | ข้อมูลมาจาก | คำตัดสิน |
|---|---|---|---|---|---|
| `data_adapter.py` (1176 บ.) | `fetch_fundamentals` รวม SETSMART (snapshot+ROE/EPS 5 ปี) + thaifin (งบรายปี 10–16 ปี) + yahoo (52w, capex, OI, interest, DPS สำรอง) + set.or.th (DPS) → `yearly_metrics` + `dividend_history` | `fetch_data.py:20-21` · `screen_stocks.py:22` · `hong_stage1_scanner.py:672` (fallback) | ใช้ (แกนของสาย scan) | thaifin / SETSMART cache / yahooquery / set_official | **ต้องแก้** — จุดผิด #1 #3 #5 #6 (ข้อ 3 ล่าง) |
| `fetch_data.py` (793 บ.) | คำนวณ aggregate ทุกตัว (`_build_aggregates` :478) + cache รายวัน `data\screener_cache\<วัน>\` + `fetch_multi_year_safe` | `screen_stocks.py:21` · `daily_price_refresh.py:190` | ใช้ | จาก `data_adapter` + yahoo รายเดือน (crisis drop) | **ต้องแก้** — จุดผิด #2 #4 #7 #8 #9 |
| `setsmart_adapter.py` (218) | client SETSMART 4 endpoint + cache `data\setsmart_cache\` | `data_adapter.py:699` (lazy) · `daily_price_refresh.py:113,262` | ใช้ (ต้องมี `SETSMART_API_KEY`) | SETSMART API (จ่ายเงิน) | ใช้ต่อ — แต่ cache EOD ช้า 1 วันทำการ (จุด #10) |
| `set_official_adapter.py` (304) | ดึง corporate-action XD จาก set.or.th ผ่าน Playwright + cache 7 วัน `data\set_dividend_cache\` | `data_adapter.py:29` (try-import) · `_verify_dps_set_fix.py:20` | ใช้ | set.or.th JSON (Cloudflare bootstrap) | **ต้องแก้** — คืนแค่ ~5 ปี (จุด #1) + `fy_is_complete_by_year` :286 หยาบ (จุด #6) |
| `daily_price_refresh.py` (374) | รีเฟรชราคา → `data\price_cache\<SYM>.json` + retry flake queue + prefetch SETSMART EOD/financial | **ไม่มีใครเรียกในโค้ดปัจจุบัน** — เดิม scheduler ใน `_archive\2026-10\server\app.py` (APScheduler 19:00) | ครึ่งตาย: ไม่มี scheduler แล้ว แต่ `rebalance.py`/`portfolio_state.py:136` อ่าน `price_cache` + `data_adapter._fetch_setsmart` พึ่ง `setsmart_cache` ที่มันเติม | SETSMART EOD bulk → yahoo สำรอง | **ใช้ต่อ แต่ต้องมีคนสั่งรัน** (cron/Task Scheduler/มือ) — `price_cache` ล่าสุด mtime 2026-08-27 19:00 (74 ไฟล์) แปลว่าหยุดรันหลังเก็บ server |
| `update_universe.py` (38) | ดึงรายชื่อ SET+mai จาก thaifin → `data\set_universe.json` (930 ตัว) | ไม่มี import · อยู่แค่ใน README:126 + `_archive\...\server\app.py:893` (ลิสต์สคริปต์ "scan") | ใช้แบบรันมือ (screen_stocks อ่าน `set_universe.json` :17) | thaifin `Stocks()` | ใช้ต่อ — ไม่มีใครรันให้ ต้องใส่ขั้นตอนใน docs |
| `flake_queue.py` (107) | คิวหุ้นที่ yahoo flake `data\flake_queue.json` | `screen_stocks.py:28,834` (add) · `daily_price_refresh.py:189` (retry) | ใช้ทางเทคนิคแต่ว่างเปล่า (`queue: []`) | ไฟล์ JSON ในเครื่อง | ใช้ต่อ (เบา) |
| `user_data_io.py` (124) | อ่าน/เขียน `data\users\<uid>\` per-user (watchlist) + `aggregate_watchlists` | `daily_price_refresh.py:39` · archive server `app.py:1682` | **เกือบตาย** — ผู้ใช้เดียวตอนนี้ (`user_data.json` ที่ root) แต่ `data\users\` ยังมี 2 โฟลเดอร์ | ไฟล์ในเครื่อง | **เก็บกวาด** (หรือตัด import ใน daily_price_refresh) หลังตัดสินใจเรื่อง multi-user |
| `_verify_dps_fix.py` (114) | สคริปต์ยืนยันครั้งเดียว: ดึง BBL METCO QH SAT เทียบ "ก่อนแก้" (baseline เม.ย.) | ไม่มี (อ้างแค่แผนใน archive) | ตาย — ฮาร์ดโค้ด baseline เก่า | `fetch_fundamentals` (ยิงเน็ต) | **เก็บกวาด** |
| `_verify_dps_set_fix.py` (165) | เทียบ DPS set.or.th กับ ground truth ฮาร์ดโค้ด (HTC…) เขียนรายงานลง docs | ไม่มี (อ้างใน CHANGELOG:209) | ตาย — one-off ของ 2026-05-19 · ยิง Playwright | set_official + ground truth ฮาร์ดโค้ด | **เก็บกวาด** (ผลอยู่ `docs\dps-set-fix-verification-2026-05-19.md`) |
| `_smoke_yahoo_resilience.py` (147) | smoke mock: retry yahoo DPS + guard `_save_to_cache` | ไม่มี · ไม่อยู่ใน `tests\` | ยังรันได้ แต่**เขียน `data\screener_cache\<วันนี้>\_SMOKETEST_*.json`** (บรรทัด ~20) | mock + fixture | ย้ายเข้า `tests\` ให้ pytest ครอบ หรือเก็บกวาด (ตอนนี้ไม่มี guard ใน CI) |
| `_smoke_stage2_repair.py` (84) | smoke mock: hard_filter guard + tag `DATA_INCOMPLETE` | ไม่มี | ใช้ได้ (ไม่เขียนไฟล์ ถ้าอ่านจาก 22 บรรทัดแรก) | fixture | ย้ายเข้า `tests\` หรือเก็บกวาด |

หมายเหตุ: `CLAUDE.md` project สั่ง "smoke test: `py scripts\_smoke_*.py`" — ดังนั้น 2 ไฟล์ smoke ถูกอ้างเป็นคำสั่งทางการ แต่ `_smoke_dehardcode` `_smoke_niwes_filter` `_smoke_scoring_v2` (นอกกองนี้) ก็อยู่ใน pattern เดียวกัน

## 2. คำตอบข้อ 1 — ทำไมแบงก์ทุกตัว (และผ่านด่านทั้ง 45 ตัว) เป็น `NEW_PAYER`

**ต้นเหตุ: ข้อมูลปันผลมีแค่ ~5 ปีหลังสุด ไม่ใช่ว่าแบงก์เพิ่งเริ่มจ่าย**

สายคำนวณ (ตามโค้ดจริง):
1. `data_adapter.py` (บล็อก "Build dividend_history", ~บรรทัด 800-817) เรียก `set_official_adapter.dps_by_fiscal_year(sym)` → รวม DPS ตาม `int(end_operation[:4])` → `dividend_history = {FY: DPS}`; ถ้าว่างค่อย fallback yahoo (tag `DPS_SOURCE_YAHOO`)
2. `fetch_data.py:77` `count_dividend_streak` นับปีต่อเนื่องจากปีล่าสุดย้อนหลัง เฉพาะ FY ที่ `fy_is_complete` = True และ DPS > 0
3. `screen_stocks.py:466-473`: streak ≥10 → STABLE/GROWING · ≥3 → `NEW_PAYER` · อื่นๆ → `INTERMITTENT`

หลักฐาน — API set.or.th ตัดที่ ~5 ปี:
- ดึงสด `fetch_dividends('BBL')` (probe_live.py) → ได้ 18 รายการ (XD 12 + XM 6) **xdate เก่าสุด 2021-03-08** (ไม่มีก่อนหน้านี้) ใหม่สุด 2026-09-09
- ทั้ง cache `data\set_dividend_cache\` 933 ไฟล์: ว่าง 141 ไฟล์; ที่เหลือ 792 ไฟล์ **xdate เก่าสุดปี 2021 = 504 ไฟล์ (64%)** · 2022=83 · 2023=71 · 2024=56 · 2025=54 · 2026=24 (คือหุ้นที่เพิ่ง IPO/เพิ่งเริ่มจ่าย)
- ผล: `dividend_history` ของผู้ผ่านด่าน 45 ตัว ช่วงปี = (2020–2025) 20 ตัว · (2020–2026) 20 ตัว · (2021–2026) 3 · (2021–2025) 1 · (2022–2025) 1 → `dividend_streak` กระจาย 4→1 ตัว · 5→6 ตัว · **6→38 ตัว · ไม่มีตัวไหนเกิน 6**
- tag ของ 45 ตัว: `NEW_PAYER` 45 · `GROWING_DIVIDEND` 0 · `STABLE_PAYER` 0 · `INTERMITTENT` 0 (นับจาก `anchor_stage_tags`) — กฎ ≥10 ปีไม่มีวันถึงด้วยข้อมูลชุดนี้
- เทียบความจริง (yahoo `dividend_history` ดึงสดทีละตัว, yprobe.py จัด FY ด้วยกฎ ม.ค.–มิ.ย.=ปีก่อน): **BBL จ่ายทุก FY ตั้งแต่ 2007** (2.0, 3.0, 4.0, 5.0, 6.0, 6.5×7 ปี, 7.0 …) = 19 ปี · **TCAP จ่ายทุก FY 2007–2025** · **AMATA จ่ายทุก FY 2007–2025** (ไม่มีปี 0) → ถ้าใช้ข้อมูลนี้ทั้งหมดจะได้ STABLE/GROWING ตามจริง
- ถึง "ปีไหนหาย": FY ≤2019 ทั้งหมด (นอกหน้าต่าง API) และ **FY2020 หายครึ่ง**: ex-date ครึ่งปีหลัง 2020 ตกนอกหน้าต่าง เหลือแต่ final ที่ XD เม.ย. 2021 · TCAP FY2020 ระบบเก็บ 1.8 แต่ yahoo 3.0 (ขาด interim 1.2) · AMATA เก็บ 0.2 vs yahoo 0.2992 · BBL เก็บ 2.5 = yahoo 2.5 (ตรง เพราะปี 2020 จ่ายครั้งเดียว) → FY2020 ของหุ้นที่จ่ายสองงวดจะต่ำกว่าจริง ทำให้ปี 2021 ดู "โต" เกินจริง (TCAP 1.8→3.0 = +67% แต่ความจริง 3.0→3.0 = 0%)
- เอกสารรู้เรื่องนี้ (`docs\data-sources-guide.md` "Coverage limit ~6 years") แต่ไม่ได้ส่งต่อเข้ากฎคะแนน → ไม่มี guard ว่า "streak ถูก cap ด้วยหน้าต่างข้อมูล"

ผลกับแบงก์: ทุกตัว (BBL KBANK KTB SCB TCAP …) streak 6 (SCB 4: `dividend_history` มีแค่ 2022–2025; เดา: เป็นเพราะเปลี่ยนเป็น holding company ปี 2022 ทำให้ symbol/ประวัติ corporate-action เริ่มใหม่ — ยังไม่ได้พิสูจน์) → `NEW_PAYER` base 2 คะแนน (แทน 6 หรือ 14) · เป็น **ทุกหุ้น ไม่ใช่เฉพาะแบงก์** (45/45)

ข้อผิดแถม (นับ streak ข้ามปีที่ไม่มีค่า): `count_dividend_streak` วนเฉพาะ key ที่มีใน dict ไม่ตรวจปีที่ขาดตรงกลาง → CIMBT `dividend_history` keys = [2020, 2021, 2022, 2024, 2025] (ไม่มี 2023) ได้ streak 5 (ควรหยุดที่ 2 ปี) · PRG [2020, 2022–2025] ได้ 5 (ควร 4) — เจอ 2 จาก 45 ตัว (recompute.py)

## 3. คำตอบข้อ 2 — `ccr_avg_3y` กับแบงก์

สูตร (`fetch_data.py:217-234`): เฉลี่ย `ocf / ebitda` ของ 3 ปีล่าสุดที่ปี < ปีปัจจุบัน และมีทั้งสองค่า (ขาด ebitda หรือ ebitda=0 → ข้ามปีนั้น; ได้ไม่ครบ 3 ปี → None)

ค่าจริง (คำนวณซ้ำจาก `yearly_metrics` ใน screener = ตรงกับ stored ทุกตัว):

| ตัว | ocf 2023 / 2024 / 2025 (พันล้าน) | ebitda 2023 / 2024 / 2025 | ratio แต่ละปี | `ccr_avg_3y` | `ocf_positive_3y` | CF score |
|---|---|---|---|---|---|---|
| BBL | 112.07 / 33.67 / 65.63 | 46.57 / 50.85 / 51.73 | 2.406 / 0.662 / 1.269 | **1.446** | True | **20** (HEALTHY 17 + ccr≥1.0 โบนัส 3) |
| TCAP | −0.884 / 2.524 / 6.124 | 6.834 / 6.878 / 7.919 | −0.129 / 0.367 / 0.773 | **0.337** | **False** (ปี 2023 ติดลบ) | **0** |
| CIMBT | — | — | — | 3.406 | True | 25 |

เหตุที่ TCAP ได้ 0: `screen_stocks.py` (บล็อก Stage 3, `screen_stocks.py:500`) ให้ tag `CASHFLOW_*` เฉพาะเมื่อ `ccr is not None and ocf_positive_3y` — OCF ปี 2023 ของ TCAP = −0.88 พันล้านทำให้ไม่ได้ tag ใดเลย → base 0 + bonus 0. ไม่ใช่เพราะ ccr ต่ำ (ต่อให้ ccr ผ่าน 0.70 ก็ไม่ได้ถ้า ocf_positive False)

EBITDA ของแบงก์คำนวณยังไง: `data_adapter.py` (ใน `_fetch_thaifin`) `ebitda = net_profit + da` (thaifin `da`); ถ้า yahoo มี `OperatingIncome` ของปีนั้น จะแทนด้วย `OI + (ebitda − net_income)` (data_adapter.py:843-846). ผลคือ EBITDA แบงก์ ≈ กำไรสุทธิ + ค่าเสื่อม (BBL 2025: NI 46.0 พันล้าน, EBITDA 51.7) — ไม่มี interest expense เพราะนิยามแบงก์ต่างจากอุตสาหกรรม
OCF ที่ใช้คือ thaifin `operating_activities` ซึ่งในงบแบงก์รวมการเปลี่ยนแปลงเงินให้กู้/เงินรับฝาก → **สัญญาณสลับสุ่ม**: BBL OCF รายปี 2010 −101.8, 2011 +30.6, 2012 −32.8, 2015 +146.2, 2020 +216.5, 2021 +0.54 (พันล้านบาท)

**ค่านี้ไม่มีความหมายกับแบงก์**: แบงก์ใน candidates ได้ CF score ตั้งแต่ 0 ถึง 25 ตามเครื่องหมายของงบกระแสเงินสดล้วนๆ — CIMBT 25 · KBANK 20 · BBL 20 · KTB 8 · KKP 8 · SCB 3 · TTB 0 · TCAP 0 (จาก `breakdown.cashflow`) ทั้งที่เป็นกลุ่มธุรกิจเดียวกัน โค้ดยกเว้นแบงก์แล้วเฉพาะ `FAKE_PROFIT`/`CASHFLOW_DETERIORATING` (`LUMPY_CASHFLOW_SECTORS`) แต่ **ไม่ยกเว้น `CASHFLOW_HEALTHY/OK` และ ccr bonus** → ช่องว่างตกที่ฝั่งให้คะแนน

## 4. คำตอบข้อ 3 — aggregate ทุกตัวที่สูตรคะแนนใช้

อ่านตาราง: "ปีปัจจุบัน" = ปนปี 2026 ที่ยังไม่ครบไหม · "ขาด" = ค่าที่ได้เมื่อข้อมูลไม่พอ · ค่า BBL/TCAP/AMATA คัดจาก `recompute.py` (คำนวณซ้ำจาก yearly_metrics ใน screener แล้วตรงกับค่า stored ทุกตัว ยกเว้น crisis_* ซึ่งต้องยิง yahoo)

| aggregate | คำนวณที่ (`fetch_data.py`) | สูตรจริง | ถูกไหม | ปีปัจจุบัน | ขาดข้อมูล → ค่า | ค่าที่เห็น BBL / TCAP / AMATA |
|---|---|---|---|---|---|---|
| `dps_cagr` (+alias `dps_5y_cagr` :625) | :531-541 | `(DPS ปีสุดท้าย / DPS ปีแรก)^(1/(ปีท้าย−ปีแรก)) − 1` จาก key ทั้งหมดใน `dividend_history` ที่ DPS>0 | **ผิด 2 ทาง**: (ก) ไม่กรอง `fy_is_complete` (ข) ไม่ใช่ 5 ปี — span คือ (ปีท้าย−ปีแรก) = 5 หรือ 6 ปี ขึ้นกับว่ามี FY2026 ไหม · คอมเมนต์ :622 "same 5-year CAGR" ไม่จริง | **ปนเต็มๆ**: AMATA ใช้ FY2026=0.6 (ครึ่งเดียว) | <2 ปี → `None`; ปีแรก 0 → None | 0.3195 / 0.1422 / **0.2009** (ถ้าเอาเฉพาะปีครบ: AMATA **0.4063**) |
| `rising_ratio` | :162-181 | ปีที่ DPS เพิ่ม ÷ จำนวน transition (เฉพาะ FY complete; prev>0) | สูตรถูก · ข้อมูลฐานเพี้ยน: FY2020 ขาด interim → transition 2020→2021 "เพิ่ม" เกินจริง · ปีที่ขาดตรงกลาง (CIMBT 2023) ถูกมองเป็นปีติดกัน | ตัดปีไม่ครบออกแล้ว (ใช้ `fy_is_complete`) | <2 ปี → `None` (tag ใช้ `or 0`) | 1.0 / 1.0 / 1.0 |
| `avg_yoy_growth` | :184-200 | ค่าเฉลี่ย (arithmetic) ของ `curr/prev − 1` (FY complete) | ถูกตามสูตร แต่ arithmetic mean เกินจริงเมื่อมีปีกระโดด + FY2020 base ต่ำ (TCAP 1.8→3.0) | ตัดแล้ว | ไม่มีคู่ปีที่ prev>0 → `None` | 0.3264 / 0.1648 / 0.4378 · CIMBT 1.026 (+103%/ปี) |
| `dividend_growth_streak` | :99-118 | นับ FY complete ย้อนหลัง: DPS ปีใหม่ > ปีเก่า (และปีเก่า>0) จนขาด | ถูก แต่ถูก cap ที่ 5 ด้วยหน้าต่าง 6 ปี และข้ามปีที่ขาดตรงกลาง | ตัดแล้ว | ไม่มีข้อมูล → `0` | 5 / 5 / 5 (ใช้ที่ `screen_stocks.py:119,374`) |
| `roe_trend` | :203-214 | เฉลี่ย ROE 3 ปีท้าย vs 3 ปีก่อนหน้า (±0.02) จาก `roe` ที่ไม่ None ทุกแถว | สูตรโอเค แต่**ไม่กรองปีปัจจุบัน** และ ROE ผสมสองแหล่ง (SETSMART ทับปี 2021–2025 `data_adapter.py:~862`, thaifin ก่อนหน้า) | ไม่กรอง — ถ้า thaifin มีแถว 2026 จะปน (เดา: ยังไม่มีแถว 2026 ในข้อมูล 2026-08-22) | <6 จุด → `"ROE_STABLE"` (เดาให้ว่าเสถียร) | IMPROVING / STABLE / IMPROVING |
| `avg_roe` | :491,514 | ค่าเฉลี่ยของ ROE **ทุกปีที่มี (สูงสุด ~16 ปี)** | ไม่ใช่ค่าล่าสุด — ปี 2010–2020 ที่เก่ามากปนกับ 2021+ (คนละแหล่ง) · ใช้ตัดสิน NO_MOAT (`screen_stocks.py:556`) | **ปนทุกแถว** ไม่กรองปีปัจจุบัน | ไม่มี → `None` (tag ใช้ `or 0`) | 0.0894 / 0.1189 / 0.1311 |
| `roe_consecutive_15plus_years` | :273-290 | ปี ROE ≥0.15 ติดกันจากปีล่าสุด (ปี<2026) หยุดเมื่อต่ำกว่า | ถูก · ปีที่ ROE เป็น None "ข้าม" ไม่ตัดสาย | กรองแล้ว | ไม่มี → `0` | 0 / 0 / 0 (แบงก์ ROE ไม่ถึง 15% — ปกติ) |
| `gm_trend` | :294-316 | GM เฉลี่ย 3 ปีท้าย vs 3 ปีก่อน (±0.01) → improving/declining/stable | สูตรถูก · **ข้อมูลแบงก์เพี้ยน**: BBL gross_margin 2020=0.60 → 2021=**1.04** → 2022=**1.05** → 2023=0.63 (นิยาม revenue/gross profit ของ thaifin เปลี่ยน; CIMBT gm>1 ทุกปี) → BBL ได้ `declining` (earlier avg 0.897 vs recent 0.62) → `NO_MOAT` · ผลคือ moat ของ BBL = 0 | กรองแล้ว | <6 ปี → `"stable"` (ผ่านเกต moat ได้ — ขาดข้อมูลกลับได้เปรียบ) | declining / declining / declining |
| `eps_cv_10y` | :364-393 | `pstdev(EPS)/|mean|` ของ `diluted_eps` สูงสุด 10 ปีก่อนปีนี้ | ถูก (ใช้ pstdev ตั้งใจ) · EPS เป็นต่อหุ้นจาก thaifin — เดา: ไม่ปรับ split ย้อนหลัง (AMATA EPS 2011=0.45, 2012=1.492 กระโดดจริงๆ ผิดปกติ) แต่หน้าต่าง 2016–2025 ที่ใช้อยู่ไม่โดน | กรองแล้ว | <5 ปี → `None`; mean=0 → `None` | 0.2446 / 0.1298 / 0.3384 |
| `crisis_2011_drop_pct` | :396-468 + เรียก :610 | หลัก: yahoo รายเดือน `min(low ปี 2011)/max(high ปี 2010) − 1`; สำรอง: `close` ปลายปี 2011 / `close` ปลายปี 2010 − 1 | สูตรหลักถูก · **ไม่ deterministic**: ผลขึ้นกับว่ายิง yahoo สำเร็จไหม (ค่าสองทางต่างกันมาก) · ยิงเน็ต 2 ครั้ง/หุ้น/วันใน aggregator | ไม่เกี่ยว (ปีอดีต) | fetch ล้ม+ไม่มี close → `None` | stored −0.2377 / −0.4438 / −0.5349 · ทางสำรอง (offline) +0.0791 / −0.2256 / −0.1111 |
| `crisis_2020_drop_pct` | เดียวกัน :611 | ปี 2019→2020 | เดียวกัน | — | เดียวกัน | stored −0.5926 / −0.5630 / −0.7063 · สำรอง −0.2269 / −0.2981 / −0.1603 |
| `ocf_2011` | :471-475 | OCF ของปี 2011 ตรงๆ (thaifin `operating_activities`) | ถูกตามสูตร · แบงก์ค่าเครื่องหมายสุ่ม (TCAP −76.9 พันล้าน) | — | ไม่มีแถวปี 2011 → `None` | 30.6 / −76.9 / 1.94 พันล้าน |
| `ocf_2020` | เดียวกัน | OCF ปี 2020 | เดียวกัน | — | เดียวกัน | 216.5 / 13.3 / 1.14 พันล้าน |
| `ocf_positive_3y` | :237-270 | 3 ปีล่าสุด (ปี<2026) OCF ทั้งหมด >0 | สูตรถูก | กรองแล้ว | ข้อมูล <3 ปี → `False` (ไม่ใช่ None — แยก "ไม่มีข้อมูล" กับ "ติดลบ" ไม่ได้) | True / **False** / True |
| `ocf_negative_count_3y` | เดียวกัน | จำนวนปีติดลบใน 3 ปีล่าสุด ที่มีข้อมูล | ถูก | กรองแล้ว | ไม่มีข้อมูลเลย → `0` (ดูเหมือน "ไม่ติดลบ") | 0 / 1 / 0 |
| `ocf_yoy_decline_pct` | เดียวกัน | **ไม่ใช่ YoY** — `avg(OCF 3 ปีท้าย) / avg(OCF 3 ปีก่อน) − 1` | สูตรทำงานตามโค้ด แต่ชื่อหลอก · ฐานติดลบ/ใกล้ศูนย์ให้เลขมหาศาล (AMATA +311%, CIMBT +220%) · ใช้ตัดสิน `CASHFLOW_DETERIORATING` ≤−0.20 (ไม่ใช้กับแบงก์/พร็อพ) | กรองแล้ว | <6 ปี หรือ earlier_avg=0 → `None` | −0.2692 / −0.5076 / +3.108 |
| `interest_coverage_4y_avg` | :346-361 | ค่าเฉลี่ย `interest_coverage` (=yahoo OI/IE, ตัดเกิน 200) 4 ปีล่าสุด | ถูก แต่ yahoo ให้ IE ได้แค่ ~2022+ → มีพอดี 4 ปี ขาดปีเดียว = None; แบงก์ไม่มี OI → None | กรองแล้ว | <4 ปี → `None` (เกต `ROE_FUELED_BY_DEBT` ต้อง not None → ไม่ทำงาน) | None / None / 5.197 |
| `net_debt_increases_in_3y` | :319-343 | `total_debt − cash` ต่อปี; นับครั้งที่ปีใหม่ > ปีเก่า ใน 3 transition จาก 5 ปีล่าสุด | สูตรถูก · **ข้อมูลแบงก์เพี้ยน**: BBL `total_debt` 2018=2.70e12 → 2019=2.81e11 → 2022=3.91e12 (นิยามเปลี่ยน; รวมเงินรับฝากหรือไม่ไม่แน่นอน) · `net_debt` ของแบงก์ไม่มีความหมาย | กรองแล้ว | <5 ปี → **`0`** (ควรเป็น None; 0 = "หนี้ไม่เพิ่ม" ดีกว่าจริง) | 3 / 1 / 3 |

## 5. คำตอบข้อ 4 — ค่าตลาด/ปันผลที่ป้อนด่านคัด (หน่วย + แหล่ง + ความสด)

| ฟิลด์ | หน่วย | แหล่ง (primary → fallback) | ที่ | ตรวจกับของจริง (BBL, screener 2026-08-22) |
|---|---|---|---|---|
| `dividend_yield` | **เปอร์เซ็นต์** (5.25 = 5.25%) | `DPS ของ FY ครบล่าสุด ÷ ราคา × 100` (DPS จาก set.or.th) → SETSMART EOD `dividendYield` (%) → None | `data_adapter.py:917` | 10.0 ÷ 190.5 × 100 = 5.2493 ✓ ตรง stored · SETSMART เองให้ 5.25 |
| `pe_ratio` | เท่า (x) | SETSMART EOD `pe` → thaifin snapshot (ใช้ `or` ⇒ ค่า 0 ก็ตกไป thaifin) | `data_adapter.py` snapshot block | 8.19 = ค่า EOD 2026-08-20 ✓ |
| `pb_ratio` | เท่า (x) | SETSMART EOD `pbv` → thaifin | เดียวกัน | 0.63 ✓ |
| `market_cap` | **บาทเต็ม** (ไม่ใช่ล้านบาท) | SETSMART EOD `marketCap` → thaifin → yahoo | เดียวกัน | 363,634,571,307 ✓ · ด่านขั้นต่ำ `min_market_cap` = 5,000,000,000 ในหน่วยบาท ตรงกัน |
| `payout_ratio` | ทศนิยม (0.415 = 41.5%) | `DPS FY ครบล่าสุด ÷ diluted_eps ของ FY เดียวกัน` (thaifin EPS) → yahoo `payoutRatio` | `data_adapter.py:948` | 10.0 ÷ 24.09 = 0.4151 ✓ |
| `five_year_avg_yield` | เปอร์เซ็นต์ | `เฉลี่ย DPS ของ ≤5 FY ครบล่าสุด ÷ **ราคาปัจจุบัน** × 100` → yahoo `fiveYearAvgDividendYield` | `data_adapter.py:935` | (3.5+4.5+7.0+8.5+10.0)/5 = 6.7 ÷ 190.5 = 3.517 ✓ |

ข้อสังเกต:
- `five_year_avg_yield` **ไม่ใช่ค่าเฉลี่ยของ yield ในอดีต** แต่เป็น DPS เฉลี่ยหารราคาวันนี้ → ถ้าปันผลโตเร็ว/ราคาขึ้น ค่านี้บอกอะไรไม่ตรงชื่อ (ชื่อหลอก ไม่ใช่บั๊กตัวเลข)
- ความสด: ราคา/PE/PBV/mcap/dy-snapshot มาจากไฟล์ EOD ล่าสุดใน `data\setsmart_cache\eod_<วัน>.json` ณ ตอนรัน · งาน 19:00 สร้างไฟล์ของ "วันทำการก่อนหน้า" (`eod_2026-08-20` สร้าง 2026-08-21 19:00; `eod_2026-08-21` สร้าง 2026-08-24 09:51 — หลัง screener รอบ 2026-08-22 09:19) → screener เสาร์ 08-22 ใช้ราคาปิด **พฤหัส 08-20 = 190.5** ทั้งที่ศุกร์ 08-21 ปิด 190.0 (ช้า 1 วันทำการ) · ตอนนี้ไม่มี scheduler (ดูตารางไฟล์) ราคาจะค้างตามวันที่มีคนรันเอง
- yield ใช้ DPS ของ "FY ครบล่าสุด" (FY2025) ÷ ราคาวันนี้ ไม่ใช่ trailing-12-month → ปันผลงวดใหม่ของปีปัจจุบัน (เช่น BBL interim ก.ย. 2026) ไม่เข้าจนกว่า FY2026 ปิด
- ราคา SETSMART เป็น `adjustedPriceFlag='Y'` (ปรับ split/ปันผลหุ้น) — เอกสารบันทึกว่าแก้แล้ว 2026-05-22 (`docs\data-sources-guide.md:486`) ไม่ได้ตรวจซ้ำ

## 6. คำตอบข้อ 5 — ตรวจมือ AMATA · BBL · TCAP

### BBL — `set_dividend_cache\BBL.json` (11 event) เทียบ `dividend_history` ใน screener
FY2020 = 2.5 (final xd 2021-04-21) · FY2021 = 1.0 + 2.5 = 3.5 · FY2022 = 1.5 + 3.0 = 4.5 · FY2023 = 2.0 + 5.0 = 7.0 · FY2024 = 2.0 + 6.5 = 8.5 · FY2025 = 2.0 + 8.0 = 10.0 → **ตรง `dividend_history` ทุกปี**
aggregate คำนวณมือ: `dps_cagr` = (10/2.5)^(1/5) − 1 = **0.3195 ✓** · `avg_yoy_growth` = mean(0.400, 0.286, 0.556, 0.214, 0.176) = **0.3264 ✓** · streak 6 ✓ (2020–2025) · EPS 21.82 / 23.69 / 24.09 (2023–25) · ROE 0.0805 / 0.0834 / 0.0815 (SETSMART) · `avg_roe` 0.0894 ✓ (เฉลี่ยทุก 16 ปี)
yahoo: BBL จ่ายทุก FY ตั้งแต่ 2007 → ระบบเห็น 6 ปีจาก 19 (ข้อ 1) · `gm_trend=declining` เป็นผลจาก gross_margin 1.04–1.05 ของปี 2021–22 (ข้อ 3) → moat 0

### TCAP — event 11 รายการ
FY2020 = 1.8 · 2021 = 1.2 + 1.8 = 3.0 · 2022 = 1.2 + 1.9 = 3.1 · 2023 = 1.2 + 2.0 = 3.2 · 2024 = 1.25 + 2.05 = 3.3 · 2025 = 1.3 + 2.2 = 3.5 → **ตรง `dividend_history`**
แต่ **ค่าที่เก็บ FY2020 = 1.8 ขาด interim 1.2** (yahoo 3.0; ex-date ปี 2020 ตกนอกหน้าต่าง set.or.th) → `dps_cagr` stored **0.1422** = (3.5/1.8)^(1/5) − 1 ✓ ตรงสูตร แต่สูตรกินข้อมูลผิด · ถ้า FY2020 = 3.0 จะได้ (3.5/3.0)^(1/5) − 1 = **0.031**
ผลต่อคะแนน (`anchor_scoring.py:~28` steps `dps_5y_cagr` (0.03→5, 0.06→9, 0.10→12, 0.15→13)): TCAP ได้ bonus 12 (breakdown.dividend = 14 = NEW_PAYER 2 + 12) แต่ค่าจริง 0.031 ได้แค่ 5 → **ปันผลสูงเกินจริง ~7 คะแนน** (จาก 100 · display 0.7)
CF score 0 → ดูข้อ 2 (OCF 2023 ติดลบ) · ROE 0.0792–0.1000 (2022–2025) เฉลี่ย 16 ปี 0.1189

### AMATA — event 12 รายการ
FY2020 = 0.2 (final xd 2021-04-22; **interim 2020 หาย** yahoo 0.2992) · 2021 = 0.1 + 0.3 = 0.4 · 2022 = 0.2 + 0.4 = 0.6 · 2023 = 0.25 + 0.4 = 0.65 · 2024 = 0.25 + 0.55 = 0.8 · 2025 = 0.35 + 0.75 = 1.1 · **2026 = 0.6** (ex-date 2026-08-26 งวด 1 ม.ค.–30 มิ.ย. 2026 เท่านั้น) → ตรง `dividend_history` ทุกปี
**ที่มาของ `DIVIDEND_SHRINKING`**: `screen_stocks.py:475-484` ดู `dividend_history` 5 ปีท้ายที่เรียง key = {2022: 0.6, 2023: 0.65, 2024: 0.8, 2025: 1.1, **2026: 0.6**}; peak = 1.1; ปีท้าย 0.6 < 1.1 × 0.70 = 0.77 → ติดป้าย · โค้ดนี้ **ไม่กรอง `fy_is_complete`** จึงเทียบ "ครึ่งปีแรก FY2026" กับ "ทั้งปี FY2025" → **false positive** (ถ้าเทียบ interim ต่อ interim: 0.35 → 0.6 โตขึ้น) · ex-date 2026-08-26 ยังไม่เกิดตอน screener รัน (2026-08-22) — cache ดึง 2026-08-15 เป็นรายการประกาศล่วงหน้า
ผลคะแนน: penalty −10 (`anchor_scoring.py:88`) → AMATA score **30** (43 − 13) ทั้งที่ควร **40** (43 − 3)
`dps_cagr` stored 0.2009 = (0.6/0.2)^(1/6) − 1 ✓ ตามสูตร แต่ปนปี FY2026 ครึ่งเดียว (ปีครบ 2020–2025: (1.1/0.2)^(1/5) − 1 = **0.4063**) · bonus เท่าเดิม (13) เพราะทั้งสองค่า ≥0.15 · EPS 1.64 / 2.16 / 2.74 (2023–25) · ROE 0.0945 / 0.1169 / 0.1389 · `interest_coverage_4y_avg` 5.197 ✓

## 7. รายการจุดผิด (เรียงตามความแรง)

| # | path:บรรทัด | ผิดยังไง | ค่าจริงที่เห็น | กระทบอะไร |
|---|---|---|---|---|
| 1 | `data_adapter.py` บล็อก dividend (~800-817) + `set_official_adapter.py:100-173,248` | ใช้ set.or.th เป็นแหล่งเดียวของ DPS ทั้งที่ API คืนแค่ ~5 ปี (ตั้งแต่ 2021-03) และ yahoo ใช้เฉพาะตอน set ว่าง → ประวัติสั้น 6 ปีเสมอ | BBL xdate เก่าสุด 2021-03-08 · streak 45 ตัว: 4→1, 5→6, 6→38 · tag 45/45 `NEW_PAYER` · yahoo เห็น BBL/TCAP/AMATA จ่ายทุก FY 2007–2025 | **ด่านคะแนนด้านปันผล (base 2 แทน 6/14)** ทุกตัว ทั้งตลาด · `STABLE_PAYER`/`GROWING_DIVIDEND` ใช้ไม่ได้เลย · ป้าย ≥10 ปีของ Niwes ใช้การไม่ได้ |
| 2 | `set_official_adapter.py:248-262` (`dps_by_fiscal_year`) + `:286` (`fy_is_complete_by_year`) | FY แรกในหน้าต่าง (FY2020) มีแค่ final (interim ตกนอกหน้าต่าง) แต่ถูกมองเป็นปีครบ (`fy < ปีปัจจุบัน`) | TCAP FY2020 เก็บ 1.8 vs yahoo 3.0 · AMATA 0.2 vs 0.2992 | `dps_cagr`/`rising_ratio`/`avg_yoy_growth` ฐานต่ำ → TCAP `dps_cagr` 0.1422 (จริง ≈0.031) → **ปันผลเกิน ~7 คะแนน** · กระทบทุกหุ้นที่จ่ายสองงวด |
| 3 | `screen_stocks.py:475-484` | `DIVIDEND_SHRINKING` เทียบ DPS ปีท้ายกับ peak โดยไม่กรอง FY ที่ยังไม่ครบ | ติด 25 ตัว · ถ้าตัด FY2026 เหลือ 10 → **false positive 15**: AMATA PTTEP ILM TU GVREIT SAT UTP AEONTS SCCC IMPACT AIMIRT FTREIT NER PROSPECT SPALI | penalty −10 ต่อตัว (`anchor_scoring.py:88`) · AMATA 30 แทน 40 |
| 4 | `fetch_data.py:531-541` (+alias :625, คอมเมนต์ :622) | `dps_cagr` ไม่กรอง `fy_is_complete`, span 5 หรือ 6 ปี แต่ alias ชื่อ `dps_5y_cagr` | AMATA 0.2009 (ปีครบ 0.4063) · 23/45 ตัวมี key 2026 | bonus ปันผลของหุ้นที่มี FY ครึ่งปีท้าย (บางตัวขั้นเปลี่ยน) · ชื่อ metric ไม่ตรงนิยาม |
| 5 | `fetch_data.py:77-97,99-118` | streak ไม่ตรวจปีที่ขาดตรงกลาง (วนเฉพาะ key ที่มี) | CIMBT keys [2020,2021,2022,2024,2025] ได้ 5 (ควร 2) · PRG [2020,2022–2025] ได้ 5 (ควร 4) | streak สูงเกินจริง · ด่านขั้นต่ำ `min_dividend_streak`=5 ผ่านทั้งที่ขาดปี (ผ่านด่าน 2 ตัว — เดา: ปี 2023 ของ CIMBT ไม่จ่ายจริง ยังไม่พิสูจน์) |
| 6 | `fetch_data.py:217-234` + `screen_stocks.py` Stage 3 (:500) + `data_adapter.py` ebitda (:843-846) | ccr = OCF/EBITDA ใช้กับแบงก์ซึ่ง OCF รวมการเคลื่อนไหวเงินให้กู้/รับฝาก → เครื่องหมายสุ่ม · `ocf_positive_3y` False ตัด tag ทิ้ง | CF score: CIMBT 25 · KBANK 20 · BBL 20 · KTB 8 · KKP 8 · SCB 3 · TTB 0 · TCAP 0 · ocf BBL 2010 −101.8 / 2020 +216.5 พันล้าน | **ด้านกระแสเงินสด (0–25) ของแบงก์ทั้งกลุ่มคือเสียงรบกวน** — ยกเว้นเฉพาะ FAKE_PROFIT/DETERIORATING ไม่ยก HEALTHY/OK |
| 7 | `fetch_data.py:294-316,319-343` (ต้นเหตุข้อมูล: thaifin `gpm`/`total_debt` ในงบแบงก์) | `gm_trend` และ `net_debt` ของแบงก์ใช้ตัวเลขที่นิยามเปลี่ยนกลางทาง | BBL gm 0.60→1.04→1.05→0.63 (2020–23) ⇒ `declining` ⇒ `NO_MOAT` (moat=0) · BBL total_debt 2.70e12→2.81e11→3.91e12 (2018/19/22) · CIMBT gm=1.0 ทุกปี | **ด้านโมท (0–25)** ของแบงก์ · `ROE_FUELED_BY_DEBT` ประเมินบนหนี้แบงก์ไม่ได้ |
| 8 | `fetch_data.py:610-611` (+ :396-468) | `crisis_2011/2020_drop_pct` ยิง yahoo ในตัว aggregator และถ้าล้มจะเปลี่ยนสูตรเป็น close ปลายปี → ผลไม่ deterministic ขัดกฎ project ("scan pipeline ต้อง deterministic") | BBL 2011: yahoo −0.2377 vs ทางสำรอง +0.0791 · TCAP 2020: −0.5630 vs −0.2981 | **ด้าน long_hold (0–15)** ตัวชี้ "ทนวิกฤต" ขึ้นกับว่าเน็ตติดไหมในวันรัน |
| 9 | `fetch_data.py:207,214` · `:307` · `:336` · `screen_stocks.py:464-465` | ค่า default ที่ดูเหมือนข้อมูลจริง: ROE_STABLE (<6 จุด), gm_trend `stable` (<6 ปี) ผ่านเกต moat, `net_debt_increases_in_3y=0` (<5 ปี), `ocf_negative_count_3y=0`, `None→0` ใน `rising/growth` | หุ้นข้อมูลสั้นได้เปรียบ/เสียเปรียบโดยไม่มีธง | หุ้น IPO ใหม่ / ข้อมูล thaifin ขาด — แยก "ไม่มีข้อมูล" กับ "ดี" ไม่ได้ |
| 10 | `fetch_data.py:491,514,516,524-525` · `:203-214` | `avg_roe`/`min_roe`/`eps_positive_years`/`fcf_*` นับทุกแถว (ไม่กรองปีปัจจุบัน, ผสม ROE thaifin + SETSMART) · `roe_trend` ไม่กรองปีปัจจุบัน | `avg_roe` BBL 0.0894 = เฉลี่ย 16 ปี · ตอนนี้ไม่มีแถว 2026 จึงยังไม่เพี้ยน | เดา: ถ้า thaifin เริ่มส่งแถวปีปัจจุบัน (บางส่วน) ค่าเหล่านี้จะปนทันที |
| 11 | `data_adapter.py` `_fetch_setsmart` (~680-693) + `daily_price_refresh.py` (ไม่มีผู้เรียก) | EOD cache ช้า 1 วันทำการ + ไม่มี scheduler หลังเก็บ server | screener 08-22 ใช้ราคา 08-20 (190.5) ขณะ 08-21 ปิด 190.0 · `price_cache` อัปเดตล่าสุด 2026-08-27 19:00 | ราคา/yield/PE ที่ผ่านด่านคัดและ `rebalance.py` ค้างตามวันที่มีคนรัน |
| 12 | `data_adapter.py:935` · `fetch_data.py` (ชื่อ `ocf_yoy_decline_pct`) · `:622` | ชื่อไม่ตรงนิยาม: `five_year_avg_yield` = DPS เฉลี่ย÷ราคาวันนี้ · `ocf_yoy_decline_pct` = เฉลี่ย 3 ปี vs 3 ปีก่อน (ไม่ใช่ YoY) | AMATA +3.108 (+311%) | ตัวเลขถูกตามสูตร แต่คนอ่านรายงานตีความผิด · `CASHFLOW_DETERIORATING` ฐานต่ำให้ค่าแปลก |
| 13 | `_smoke_yahoo_resilience.py:21,35,50` | smoke "ไม่ยิงตลาดจริง" แต่เขียนไฟล์ `_SMOKETEST_*.json` ลง `data\screener_cache\<วันนี้>\` จริง | (อ่านโค้ด ยังไม่ได้รัน) | เดา: ถ้าไฟล์ทดสอบไม่ถูกลบ จะปนใน `screener_cache` ที่ screen อ่านรายวัน |

ข้อควรรู้ ไม่ใช่บั๊ก: `data\screener_2026-08-22.json` คำนวณซ้ำจาก `yearly_metrics`+`dividend_history` ที่เก็บไว้ได้ค่า aggregate ตรง stored ทุก key ที่ไม่ต้องใช้เน็ต (18 key × 3 หุ้น ไม่รวม crisis_*) → โค้ดคำนวณ "ตรงสูตรที่เขียน"; ปัญหาอยู่ที่ข้อมูลที่ป้อนกับกฎที่ไม่กัน FY ไม่ครบ ไม่ใช่เลขคณิต

## 8. ไฟล์ที่ควรเก็บกวาด

| ไฟล์ | เหตุผล | ความเสี่ยงถ้าลบ |
|---|---|---|
| `scripts\_verify_dps_fix.py` | one-off ของ 2026-05 · baseline ฮาร์ดโค้ด "ก่อนแก้" (BBL yield 10.41 …) ล้าสมัย · ไม่มีใครเรียก · ยิงเน็ตจริง | ต่ำ (ผลอยู่ใน plan ที่ archive แล้ว) |
| `scripts\_verify_dps_set_fix.py` | one-off ของ 2026-05-19 · ground truth ฮาร์ดโค้ด (HTC …) · ผลเก็บแล้วที่ `docs\dps-set-fix-verification-2026-05-19.md` | ต่ำ · **แต่** ถ้าจะแก้ข้อ 1–2 อาจเก็บไว้ใช้เป็นแม่แบบเทียบ SETSMART ground truth |
| `scripts\_smoke_yahoo_resilience.py` + `scripts\_smoke_stage2_repair.py` | ไม่อยู่ใน `tests\` (pytest/unittest ไม่เก็บ) · ตัวแรกมี side-effect เขียน `data\` | ปานกลาง: `CLAUDE.md` project อ้าง "smoke test: `py scripts\_smoke_*.py`" → ถ้าลบต้องแก้บรรทัดนั้น · ทางที่ดีกว่า = ย้ายเข้า `tests\` + ให้ใช้ tmp dir |
| `scripts\user_data_io.py` + import ใน `daily_price_refresh.py:39` + โฟลเดอร์ `data\users\` (2 uid) | multi-user ตายพร้อม server (ตอนนี้ user เดียว `user_data.json`) · ตัวเดียวที่เรียกคือ `daily_price_refresh._load_symbols` | ปานกลาง: ต้องตัดสินใจว่า watchlist ยังจะมาจาก `data\users\` หรือ `user_data.json` ก่อน (ยังไม่พิสูจน์ว่าไฟล์ใน `data\users\` มีข้อมูลที่ต้องเก็บ) |
| `data_adapter.py:734-737` alias `fetch_yfinance_supplement` (DEPRECATED) + `fetch_data.py:26` `import fetch_from_thaifin` (ไม่ได้ใช้ใน fetch_data) | alias/นำเข้าที่ไม่มีผู้ใช้ (grep ไม่พบ) | ต่ำ |

**ไม่ควรเก็บกวาด** (ยังใช้): `data_adapter.py` `fetch_data.py` `setsmart_adapter.py` `set_official_adapter.py` `update_universe.py` (ขั้นรันมือ) `flake_queue.py` (เบา, `screen_stocks.py:28`) · `daily_price_refresh.py` = **ต้องมี scheduler/ขั้นรันมือกำกับ** แทนการลบ (rebalance พึ่ง price_cache)
