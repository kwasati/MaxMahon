---
project: MaxMahon
created: 2026-04-20
last_updated: 2026-04-20
status: done
---

# How-to ลงทุนหุ้นนอก (DR/VN/US/Tax/Holding) — Karl Roadmap

> Part 5 of 8 — Index: niwes-master-index | Depends on: rename-master-index (paths อ้าง projects/MaxMahon/) | Parallel-safe with: niwes-03, niwes-04 — guide ครบจบ Karl ทำไม่เป็นเลย: Quick Win (US DR), Vietnam direct (ดร.นิเวศน์ style), US direct, Tax (ป.161/2566 + DTA), Holding (ตีแตก). บังคับ WebFetch raw legal text + DR list authoritative

## Phase 1: Research broker + tax landscape (with WebFetch verify)
- [x] สร้าง folder `projects/MaxMahon/docs/foreign-investment/` + ไฟล์ `00-sources.md` — Agent (researcher subagent_type) ค้น: (1) Broker ไทย VN — KKPS, Bualuang Vietnam, Phillip, InnovestX, Liberator, Yuanta — fee/min/feature/onboarding, (2) Broker offshore US — IBKR, Tiger, Webull, Moomoo, FUSE, Liberator — fee/spread/min/Thailand support/W-8BEN, (3) DR list ใน SET — settrade.com/en/markets/foreign-listed (authoritative source, ห้ามใช้ blog), (4) Tax: WebFetch raw text จาก rd.go.th: ป.161/2566 ฉบับเต็ม, มาตรา 50(2)(จ), มาตรา 40(4)(ข), DTA ไทย-เวียดนาม, DTA ไทย-สหรัฐ. ทุก source ต้อง: URL + วันที่ + WebFetch HTTP status + 1-2 บรรทัดสรุป. ห้ามอ้าง blog/secondary source สำหรับ legal text. — Acceptance: ≥30 sources, ≥80% verified HTTP 200, legal text section มี ≥4 raw rd.go.th links

## Phase 2: Quick Win — US ผ่าน DR
- [x] สร้าง `projects/MaxMahon/docs/foreign-investment/01-quickwin-us-dr.md` — DR คืออะไร (เข้าใจง่าย), ทำไม Karl ทำได้พรุ่งนี้ (ใช้บัญชี SET เดิม), DR list ใน SET ปัจจุบัน (verify จาก settrade authoritative, list ครบ Bualuang + KGI series — AAPL19, MSFT19, NVDA19, etc.), ขั้นตอนซื้อ (market hours 10-12 + 14:30-16:30, T+2), ภาษีปันผล DR (US WHT 15% + ไทย bracket 0-35%), ข้อจำกัด (liquidity, premium/discount, FX, conversion ratio). Karl Action: เปิด Bualuang/InnovestX (ถ้ายังไม่มี) → ซื้อ AAPL19 ทดสอบ. — Acceptance: ≥600 บรรทัด + DR list verified + Karl action plan ทำได้พรุ่งนี้

## Phase 3: Core Thesis — Vietnam direct (ดร.นิเวศน์ style)
- [x] สร้าง `projects/MaxMahon/docs/foreign-investment/02-vietnam-direct.md` — Why VN (demographic 100M+, GDP 6%+, FTSE upgrade 2-3y, FPT เบอร์ 1 VN ใน 10 ปี). Broker comparison table (KKPS/Bualuang/Phillip/InnovestX) — fee/min/onboarding time/USD or VND deposit. ขั้นตอนเปิดบัญชี (เอกสาร, FATCA, 1-2 อาทิตย์, deposit method), การซื้อขาย (HOSE/HNX hours, lot size, T+2, FX VND), VN stock list ที่ ดร.นิเวศน์ลง (FPT/MWG/ACV/VRE/REE) ข้อมูลแต่ละตัว, ภาษี VN (capital gain 0.1% on sell, dividend WHT 5% foreign individual). Karl Action: เลือก broker → เปิดบัญชี → deposit $5,000 → ทดสอบ FPT. — Acceptance: ≥800 บรรทัด + broker table + step-by-step onboarding

## Phase 4: US Direct (advanced)
- [x] สร้าง `projects/MaxMahon/docs/foreign-investment/03-us-direct.md` — Why US Direct (5,000+ stocks vs DR ~30, fractional, options, ETF universe), Broker comparison (IBKR/Tiger/Webull/Moomoo/FUSE/Liberator), ขั้นตอนเปิดบัญชี (W-8BEN ลด WHT 30%→15%, ID/proof, deposit Wise/SWIFT), การซื้อขาย (NYSE/NASDAQ hours, T+1 ใหม่ 2024), ภาษี US (WHT 15% หลัง W-8BEN, เครดิตได้ในไทย), **US Estate Tax >$60K assets** (non-resident เสีย 18-40% มรดก, วิธีเลี่ยง: ETF non-US registered, holding company, joint account). Karl Action: ถ้า <$60K ใช้ DR ก่อน, ถ้าใหญ่ขึ้น IBKR + W-8BEN. — Acceptance: ≥800 บรรทัด + broker table + estate tax section ชัด

## Phase 5: Tax — Comprehensive (with WebFetch raw legal)
- [x] สร้าง `projects/MaxMahon/docs/foreign-investment/04-tax-comprehensive.md` — section 1: ทำไม final tax 10% หุ้นไทยใช้ไม่ได้ (มาตรา 50(2)(จ) บังคับ บจ.ไทยเท่านั้น) — quote raw text จาก rd.go.th, section 2: ป.161/2566 ฉบับเต็ม (ก่อน vs หลัง 1 ม.ค.2567 — loophole remittance ปิด) — quote raw text, section 3: DTA ไทย-VN + ไทย-US (อัตรา WHT, foreign tax credit) — quote raw text + ระบุข้อ, section 4: อัตราภาษีก้าวหน้าไทย bracket, section 5: ตัวอย่างคำนวณจริง ≥3 case (VN dividend / US dividend / capital gain), section 6: การยื่นภาษี (ภงด.90/91 + แบบ 95 ภาษีหัก ณ ที่จ่ายต่างประเทศ), section 7: เคล็ดลับลด tax. **บังคับ disclaimer:** 'ผู้เขียนไม่ใช่นักภาษี — ตัวเลขอ้างอิงราชกิจจาเท่านั้น ถ้าจะใช้จริงต้อง consult tax pro หรือ rd.go.th hotline 1161'. ทุก legal claim ต้องมี source URL + ข้อมาตรา. — Acceptance: ≥1,000 บรรทัด + ≥3 ตัวอย่าง + disclaimer top + ทุก legal claim มี citation

## Phase 6: Scale-up — Holding Company (ตีแตก จำกัด style)
- [x] สร้าง `projects/MaxMahon/docs/foreign-investment/05-holding-company.md` — เคส ตีแตก จำกัด ของ ดร.นิเวศน์ (ภาษีนิติ 20% < บุคคล 35%). Break-even calculation table (ปันผล/ปี → tax saved → vs accounting cost), ขั้นตอนจดบริษัท (ทุน 1M+, กรรมการ 3, สำนักงาน, accounting+audit), ข้อจำกัด (paperwork, transfer pricing risk, dividend distribution หลังคุ้ม), Hybrid model (holding ถือ foreign + ส่วนตัวถือไทย). Karl Roadmap: ปัจจุบันพอร์ตเล็ก อย่ายุ่ง, >3M ปันผล/ปี consider, >10M ตั้งเลย. — Acceptance: ≥600 บรรทัด + break-even table + Karl roadmap ชัด

## Phase 7: Action Plan + Index
- [x] สร้าง `projects/MaxMahon/docs/foreign-investment/00-action-plan.md` — Karl Personal Roadmap: Phase 1 (Q2 2026) DR US บน Bualuang เดิม ($1,000 test), Phase 2 (Q3 2026) KKPS Vietnam FPT ($5,000), Phase 3 (2027) IBKR W-8BEN US direct ($10,000+), Phase 4 (2028+) Holding company เมื่อปันผล >3M/ปี. แต่ละ phase: checklist, KPI, escalation criteria. — Acceptance: roadmap ชัด actionable + KPI วัดได้
- [x] สร้าง `projects/MaxMahon/docs/foreign-investment/00-index.md` — TOC (00-action-plan/01-quickwin/02-vietnam/03-us-direct/04-tax/05-holding) + Quick Start (00→01→04) + Decision Tree (เริ่มเลย→01 / ตามแนว ดร.นิเวศน์→02 / พอร์ตใหญ่→05). — Acceptance: TOC ครบ + decision tree ชัด
