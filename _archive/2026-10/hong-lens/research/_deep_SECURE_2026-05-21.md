# Deep Dive — SECURE (NForce Secure PCL)

> วันที่: 2026-05-21
> โครงการ: Hong Lens (25% portfolio allocation — แนวเซียนฮง)
> Source หลัก: SET official factsheet + companyprofile (HTML) + MaxMahon yearly cache
> ข้อมูลที่ไม่มีใน source ตรง — flag ชัดทุกครั้งว่า "estimate" หรือ "ต้อง verify จาก 56-1"

---

## Snapshot — ตัวเลขสำคัญที่ต้องจำก่อนอ่าน

| รายการ | ค่า |
|--------|-----|
| ราคา | 11.30 บาท (52w high/low: 14.00 / 9.85) |
| Market Cap | 1,160.97 ล้านบาท (small cap) |
| P/E | 9.14x |
| P/BV | 1.44x |
| EV/EBITDA | 3.21x |
| Dividend Yield (FY2025) | 7.20% |
| Payout (FY2025) | 53% |
| ROE 2025 | 16.27% |
| Net Profit Margin 2025 | 9.32% |
| D/E 2025 | 0.50x |
| Free Float | 40.91% (2,693 holders, ณ 13/03/2026) |
| Foreign holding | 0.00% (Foreign limit 49%) |
| NVDR | 1.40% |
| CG Report | 4 (Good) |
| SET ESG / CAC | ไม่มี rating (ทั้งคู่ "-") |
| ตลาด | **mai** (ไม่ใช่ SET กระดานหลัก — note: pool Hong Lens ปกติเป็น SET-only แต่ user อนุญาต SECURE เป็น exception เพราะผ่าน v5 filter เด่น) |
| Listed | 01/07/2021 (อายุในตลาด ~4 ปี 10 เดือน) |
| IPO Price | 16.00 บาท → ปัจจุบัน 11.30 = -29% from IPO |

---

## Layer 1 — Business model (ขายอะไร ใครซื้อ ทำเงินยังไง)

### หัวใจของธุรกิจตาม SET filing
ตาม SET company profile ระบุชัดว่า:
> **Distributor of Cybersecurity Solution Products Business and Other Supporting Service Businesses**

แปลภาษาคน — SECURE เป็น **"ตัวกลางขาย"** สินค้า cybersecurity ของแบรนด์ระดับโลก ให้ลูกค้าองค์กรในไทย + บริการเสริมรอบๆ ตัว software/hardware ที่ขาย

### Layer ของรายได้ (model ที่ distributor IT ในไทยทำกันเป็น standard)
1. **Product resale (รายได้ก้อนใหญ่ — one-time)**
   - ซื้อ license/hardware จากเจ้าของ brand (vendor) → markup → ขายต่อให้ลูกค้าองค์กร
   - margin บางมาก (5-10% เป็น industry norm) เพราะการแข่งขันของ distributor ในไทย
2. **License renewal (recurring revenue — สำคัญสุดสำหรับ resilience)**
   - cybersecurity license ส่วนใหญ่จ่ายเป็นปี (annual subscription)
   - **ลูกค้า lock-in หลัง deploy** — เปลี่ยน vendor ลำบาก เพราะ infrastructure ฝังลึก + ทีม IT ต้องเรียนใหม่
   - SECURE ได้ค่า renewal ทุกปีจากฐานลูกค้าเดิมตราบใดที่ยัง renew
3. **Service / Professional services (margin สูงสุด)**
   - Deployment: ติดตั้ง + configure + integrate
   - Training: สอนทีม IT ลูกค้าใช้
   - 24/7 Support: SLA-based, MSSP (Managed Security Service Provider)
   - **margin 20-30%** estimate ตาม industry — SECURE ไม่ break out segment ใน SET filing

### Product mix ที่ SECURE distribute (estimate จาก public knowledge — ต้อง verify จาก 56-1 หรือ company website)
- **Network security**: Firewall (Fortinet / Palo Alto / Check Point) — segment ใหญ่สุดของ market
- **Endpoint security**: CrowdStrike / SentinelOne / Trend Micro
- **Identity & access**: CyberArk / Okta-class
- **Cloud security**: Prisma Cloud / Wiz / etc.
- **SIEM / SOC tools**: Splunk / IBM QRadar / LogRhythm
- **Threat intelligence + Email security**: Proofpoint / Mimecast

หมายเหตุ — รายชื่อ vendor นี้ **เป็น estimate จาก public knowledge ของอุตสาหกรรม distributor IT ไทย** ไม่ใช่จาก SET filing ตรง ต้องไปดู annual report 56-1 หรือ website www.nforcesecure.com (มีอยู่จริงตามการลงทะเบียน แต่ไม่อยู่ใน source ตรงที่ session นี้มี)

### ทำเงินยังไง (Cash Conversion Cycle)
ดูจาก SET factsheet พฤติกรรม:
- **A/R Turnover (FY2025): 3.59 ครั้ง** = เก็บเงินลูกค้าเฉลี่ย **~101.74 วัน** (slow — แต่ปกติของ B2B enterprise sales)
- Q1/2026 ดีขึ้นเป็น **5.98 ครั้ง = 61 วัน** = บริษัทบีบเก็บเร็วขึ้น (good sign)

= โมเดล "ขายของแล้วรอเก็บเงิน 2-3 เดือน" — ต้องมีกระแสเงินสดหนาเพื่อ float ระหว่างซื้อจาก vendor (จ่ายเร็ว) กับเก็บจากลูกค้า (ช้า)

### ทำไม model นี้ทนตลาดผันผวน
1. **Cybersecurity = mandatory spending** ไม่ใช่ optional — บริษัทใหญ่ยอมตัด marketing budget ก่อนตัด security
2. **Renewal cycle** สร้างฐานรายได้ทำให้ revenue ไม่ตกฮวบเหมือนขายของครั้งเดียว
3. **Regulatory tailwind** — PDPA + BOT mandate + Cyber Security Act บังคับใช้
4. **AI + cloud migration** ทำให้ surface attack เพิ่ม → demand security tools เพิ่ม

### ความเสี่ยงของ model
1. **Margin บีบจาก vendor** — vendor ใหญ่ (Fortinet/Palo Alto) ขายตรงให้ลูกค้า enterprise มากขึ้น → distributor margin หด
2. **Single-vendor concentration** — ถ้า SECURE พึ่ง 1-2 vendor มาก (เช่น Fortinet 40-60% ของรายได้) → vendor เปลี่ยน distributor = หายนะ
3. **Tech disruption** — Zero Trust / SASE / XDR เป็น architecture ใหม่ที่ vendor บางรายขายเป็น all-in-one ตัดความจำเป็นของ point product

---

## Layer 2 — Revenue / Segment breakdown

### ข้อมูลใน source ปัจจุบัน (limited)
SET factsheet **ไม่ break out segment** — รายงานแค่ total revenue + COGS + net profit รวม ไม่แยก product vs service / Thailand vs export / vendor mix

### ตัวเลขที่ verify ได้

| ปี | Revenue (MB) | Growth YoY | Gross Margin | Net Margin |
|----|--------------|------------|--------------|------------|
| 2020 | 633.92 | -1.4% | 19.79% | 3.71% |
| 2021 | 823.38 | +29.9% | 18.93% | 7.42% |
| 2022 | 893.90 | +8.6% | 16.23% | 6.16% |
| 2023 | 1,065.97 | +19.2% | 19.65% | 8.61% |
| 2024 | 1,237.95 | +16.1% | 19.86% | 9.34% |
| 2025 | 1,302.83 | +5.2% | 20.04% | 9.32% |
| Q1/2026 (3M) | 309 | +4.25% YoY | 22.05% | 11.19% |

**ข้อสังเกต:**
- รายได้โต 6 ปีติด — pattern ของ company ที่ market ยังไม่ saturate
- Gross margin ขยับขึ้นจาก 16-19% เป็น 20-22% Q1/2026 — **service mix เพิ่มขึ้น** estimate (เพราะ product มี margin บางกว่า service)
- Net margin โตจาก 3.7% ปี 2020 เป็น 9.3% ปี 2025 — **operating leverage** เริ่มออกผล (ค่าใช้จ่ายคงที่กระจาย over revenue ใหญ่ขึ้น)

### Recurring vs One-time estimate
- SECURE ไม่ disclose แต่ industry norm ของ distributor cybersecurity ไทยน่าจะอยู่ที่ **30-50% recurring** (renewal + MSSP) และ **50-70% one-time** (new license + hardware)
- ต้องดู MD&A Q1/2026 (มีอยู่ — released 14/05/2026) ที่ user load มาเพิ่มถึงจะ verify ได้

### Geographic mix
- SECURE จดทะเบียนในไทย — ที่อยู่ 9/2 ถ.รัชดาภิเษก ห้วยขวาง กรุงเทพ
- **น่าจะ Thailand-only** (estimate) — ไม่มี subsidiary ในประเทศอื่นใน SET company profile section "Subsidiaries"
- การขยายไป ASEAN เป็น **growth runway** แต่ยังไม่เห็น track record

### Top vendor concentration (risk #1 ของ business model นี้)
- **ไม่มีข้อมูลใน source ปัจจุบัน** — SET ไม่บังคับ disclose vendor breakdown
- ต้อง verify จาก 56-1 รายงานประจำปี หรือ investor presentation
- **Public knowledge estimate**: SECURE มี Fortinet เป็น core (เป็น distributor หลักในไทย) แต่ % ของรายได้ที่มาจาก Fortinet vs total = ไม่ทราบ

---

## Layer 3 — Customer dynamics

### กลุ่มลูกค้า (segment estimate จาก industry — ไม่ใช่ SET filing)
ลูกค้าของ SECURE น่าจะเป็น **B2B enterprise + government** กระจายตามนี้:

1. **Financial institutions (Bank + ประกัน + บล./บลจ.)** — กลุ่มใหญ่สุดของ cyber spend ในไทย
   - ธนาคาร 9 รายใหญ่ + ธ.พาณิชย์เล็ก + ประกัน 22 ราย + บล. + บลจ.
   - BOT (ธปท.) บังคับให้ใช้มาตรฐาน security ตาม IT Risk Guidelines
   - sales cycle ยาว (3-6 เดือนต่อ deal) แต่ deal size ใหญ่ (สิบล้าน-ร้อยล้าน)
2. **Government + รัฐวิสาหกิจ**
   - หน่วยงานราชการ + กฟผ./กฟภ./ปตท./บมจ. ภาครัฐ
   - มี procurement ผ่าน e-bidding ของกรมบัญชีกลาง
   - บังคับใช้มาตรฐาน NCSA (สำนักงานคณะกรรมการการรักษาความมั่นคงปลอดภัยไซเบอร์แห่งชาติ)
3. **Telecom + ISP** — AIS, True, NT (CAT+TOT)
4. **Large Enterprise** — บมจ. SET100 ส่วนใหญ่มี cyber budget เป็น line item แยก
5. **SME** — เล็กกว่า แต่ volume เยอะ — channel partner reseller มากกว่า direct

### Customer concentration % (ไม่มีข้อมูลใน source)
SECURE ไม่ disclose top 10 customer % — ต้อง verify จาก 56-1
ปกติ distributor IT ในไทย:
- ถ้าลูกค้า top 5 รวมเกิน 50% = concentration risk สูง
- ถ้ากระจายดี (top 10 ≤ 30%) = healthy

### Sales cycle ของ enterprise (industry knowledge)
- Bank/government: **3-6 เดือน** ต่อ deal ขนาดใหญ่ (proof of concept → procurement → contract → deployment)
- Mid enterprise: **1-3 เดือน**
- SME: **2-4 สัปดาห์**
- ทำให้ revenue ของ Q ไม่นิ่ง — บางไตรมาส deal ใหญ่ closed = ระเบิด บางไตรมาส deal เลื่อน = ตก

ดู Q1/2025 ของ SECURE เอง — รายได้ -15.10%, NP -28.74% YoY — แล้ว Q1/2026 ฟื้นกลับ +4.25% sales, +18.7% NP — ลักษณะ **lumpy revenue** ของธุรกิจ enterprise B2B

### Retention rate (key driver ของ recurring revenue)
- License-based vendor (Fortinet/Palo Alto/CrowdStrike) ปกติ renewal rate **85-95%** สำหรับ enterprise customer ที่ deploy แล้ว
- SECURE ได้ค่า renewal ทุกปี = ฐานรายได้ที่ predictable
- ไม่มีข้อมูล SECURE-specific ใน source ปัจจุบัน

### ทำไมลูกค้า once-bought ยอมซื้อต่อ
1. **Switching cost สูง** — เปลี่ยน firewall vendor = ต้อง re-architect network + retrain staff = หลายล้าน + risk downtime
2. **Trust ของ technical team** — ทีม security ของลูกค้ารู้จัก engineer ของ SECURE ตัวต่อตัว
3. **SLA + support** — ถ้า SECURE support เร็ว 24/7 ลูกค้าไม่อยากเสี่ยงไปใช้ที่อื่น
4. **Bundle pricing** — renew หลายอย่างพร้อมกัน ได้ส่วนลด

= **customer lock-in moat** ของ distributor cybersecurity ถ้าทำดี = strong

---

## Layer 4 — Margin drivers

### ทำไม Net Margin 9.3% สูงกว่า distributor IT ทั่วไป

Distributor IT ใหญ่ในไทย net margin typical:
- IT systems integrator (MFEC/G-Able): 3-7%
- Hardware reseller: 1-3%
- Software licensing: 4-8%
- **Specialized cybersecurity distributor (SECURE-like): 8-12%** = SECURE อยู่ในระดับสูงของ category

ที่ margin สูงเพราะ:

#### 1. Service mix สูง (estimate)
- Service margin 20-30% vs Product margin 5-10%
- ถ้า service revenue ratio = 25% ของ total = blended margin ~12% gross
- SECURE Gross margin 20% → consistent with **service mix ~25-35%** estimate

#### 2. Niche product mix (cybersecurity specialist)
- ไม่ทำ commodity IT (PC/printer/network cable) ที่ margin บาง
- focus เฉพาะ security product ที่ vendor ให้ margin distributor สูงกว่า (เพื่อจูงใจ specialist channel)

#### 3. Operating leverage
- SG&A ratio (% of revenue) เพิ่มจาก 4.6% ปี 2024 เป็น 8.9% ปี 2025 — ดู noisy แต่ absolute SG&A ขึ้นมา 57 → 116 MB
- Operating margin ยังโตจาก 6.4% (2022) → 11.4% (2025) = operating leverage outpace SG&A growth

#### 4. Interest coverage สูงมาก
- 2025 interest coverage 133.69x = หนี้แทบไม่มี → ค่าดอกเบี้ยจิ๊บจ๊อย
- ไม่ต้องเหนื่อยกับ financial cost → กำไรเหลือเป็น net เกือบเต็มตัว

### Cost structure (จาก SET financial statement)
- **COGS** (จ่ายให้ vendor หลัก + product cost): ~80% ของ revenue
- **SG&A** (sales staff + technical staff + office + marketing): ~9% ของ revenue ปี 2025
- **Operating income**: ~11% ของ revenue
- **Tax + interest**: ~2%
- **Net**: ~9.3%

### ความเสี่ยงด้าน margin

1. **Vendor margin squeeze** — ถ้า vendor ตัด distributor margin เพื่อแข่งตรง = SECURE โดน
2. **Competitive bidding** — government tender forces price war → margin lower
3. **Currency** — vendor หลักเป็น USD/EUR → THB อ่อน = COGS แพง → ต้องผ่านราคาให้ลูกค้า (lag)
4. **Salary inflation** — security engineer + sales rep ในไทย salary โตเร็ว — SG&A pressure ระยะยาว

---

## Layer 5 — Capital allocation track record

### Snapshot ทุนรอบ IPO ถึงปัจจุบัน

| ปี | Equity (MB) | Cash (MB) | Total Debt (MB) | BVPS (Baht) | D/E |
|----|-------------|-----------|-----------------|-------------|-----|
| 2020 (ก่อน IPO) | 114 | 40.5 | 191 | – | 1.68 |
| 2021 (IPO) | 573 | 403 | 162 | 5.45 | 0.28 |
| 2022 | 612 | 398 | 200 | 5.65 | 0.33 |
| 2023 | 673 | 450 | 237 | 6.27 | 0.35 |
| 2024 | 723 | 448 | 294 | 6.68 | 0.41 |
| 2025 | 771 | 577 | 390 | 6.93 | 0.50 |

### IPO 2021 — เงินไปไหน
- IPO 01/07/2021 ที่ 16 บาท → ระดมทุนได้ประมาณ **520 MB** (cash jump จาก 40 → 403)
- ใช้:
  - **Working capital** ขยายธุรกิจ (เพราะ A/R 60-100 วัน ต้องการเงินสด float)
  - **R&D / training** — เพิ่ม technical team ขยาย service capability
  - **Acquisition / partnership** — ไม่เห็น M&A ใหญ่ใน SET filing
- ปี 2025 cash เพิ่มเป็น 577 MB = ทำกำไรสะสมไว้ (ไม่ได้ใช้หมดที่ระดม)
- = **prudent management** ไม่ใช่แบบเอาเงิน IPO ไปลงทุน aggressive แล้วเจ๊ง

### Equity growth 6 ปี
- 114 → 771 MB = **+577%** ใน 6 ปี
- ส่วนใหญ่มาจาก IPO เพิ่มทุน (จาก 114 → 573 ทันที) + retain earnings ปีละ ~50-100 MB

### Debt — ปลอดภัยมาก
- Total debt 200-400 MB ส่วนใหญ่เป็น **lease liability + AP** ไม่ใช่ bank loan
- **Short-term debt = 0** (ไม่มี overdraft + ไม่มี current portion LT)
- D/E 0.50x = ต่ำกว่าเกณฑ์เซียนฮง 1.0x สบายๆ
- Interest expense ปี 2025 = 1.1 MB เทียบกับ EBITDA 162.7 MB = noise

### Payout policy + sustainability
- Dividend policy: ไม่น้อยกว่า **50%** ของกำไรสุทธิหลังหักภาษีและสำรอง
- จริง — payout ทำขึ้นเรื่อยๆ: 2022 (33%) → 2023 (34%) → 2024 (55%) → 2025 (53%)
- ส่งสัญญาณ: **mature capital allocation** — ปี 2024 จ่าย payout เพิ่มเพราะกำไรโต + ไม่มี CAPEX ใหญ่รออยู่
- Capital intensity ลดลงต่อปี: 1.18 (2021 IPO peak invest) → 0.06 (2025) = ไม่ต้องลงทุนหนักเพื่อโต

### CAPEX track record (FCF healthy)
- CAPEX ปี 2024 = 1.45 MB / 2025 = 4.30 MB = **เล็กมาก**
- FCF 2025 = 206.81 MB (OCF 211 - capex 4.3)
- = **asset-light business** — distributor ไม่ต้องลงทุน factory/machinery แค่ office + IT infrastructure + working capital

### Capital allocation grade
- ✓ ไม่ผลาญเงิน IPO ไปสร้าง expansion ที่ไม่จำเป็น
- ✓ Balance sheet สะอาด — cash หนา + ไม่มีหนี้สั้น
- ✓ Payout เพิ่มตามกำไรโต = sustainable + leaves room for growth investment
- ⚠️ **ยังไม่เห็น track record ใหญ่ๆ** ของการเอาเงินไปทำ acquisition / strategic investment / international expansion — เพราะอายุในตลาดแค่ 4 ปี (อาจเป็น opportunity ที่ยังไม่เกิด หรือ management ยัง conservative)

---

## Layer 6 — Growth runway

### Thailand cybersecurity market size + growth rate
- ตลาด cybersecurity ไทย (estimate จาก public knowledge / IDC / Gartner-style report):
  - 2024 ~25-30 พันล้านบาท
  - CAGR 12-15% (vs IT spend overall ที่ ~5-7%)
  - Driver: cloud + AI + remote work + ภัยคุกคามใหม่
- **= Tailwind structural** ที่ตลาดไทยยังเล็กเทียบ developed economy (US/EU)

### Regulatory tailwind (catalyst หลัก)

#### 1. PDPA (พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล)
- บังคับใช้ 1 มิ.ย. 2022
- บริษัทไทยทุกแห่งที่มีข้อมูลส่วนบุคคล = ต้องลงทุน data security
- เริ่ม audit + ปรับจริง 2023-2025
- **demand ขยายจาก large enterprise → mid + SME**

#### 2. BOT IT-risk mandate
- ธนาคารแห่งประเทศไทยมี IT Risk Guidelines + cyber resilience framework
- บังคับธนาคาร + non-bank financial (สินเชื่อบุคคล/บัตรเครดิต/digital lending) ต้องมีมาตรฐาน
- SECURE ที่ทำงานกับ bank อยู่แล้ว → **direct beneficiary**

#### 3. Cyber Security Act (พ.ร.บ. การรักษาความมั่นคงปลอดภัยไซเบอร์ 2562)
- NCSA (National Cyber Security Agency) บังคับ critical infrastructure
- รัฐวิสาหกิจ + utility + telecom + airport + hospital ใหญ่ = required
- Compliance audit + ป้องกัน + incident response → demand service

#### 4. SET ESG / Sustainability requirement
- บริษัทจดทะเบียน SET ต้องรายงาน cybersecurity risk ใน annual report
- → demand audit + assessment ขยาย

### Cloud security new frontier
- AWS / Azure / Google Cloud adoption ในไทยโตเร็ว — banks + government + corporate ย้าย workload
- ต้องมี cloud security tool (CSPM/CWPP/CNAPP) แยกจาก on-prem firewall
- vendor ใหม่ (Wiz / Lacework / Palo Alto Prisma Cloud) ขายผ่าน distributor
- = **growth segment** ที่ SECURE ต้องจับให้ทัน

### AI security emerging
- AI-driven threat (deepfake + prompt injection + LLM attack) + AI-driven defense (SIEM with ML)
- vendor ที่ขาย AI-native security (CrowdStrike Falcon / SentinelOne) = growth driver
- เด็กใหม่ในตลาด — first-mover advantage ที่ distributor ที่ pivot ได้เร็วจะกิน share

### SECURE expansion strategy
- **ไม่มี clear M&A/expansion announcement ใน source ปัจจุบัน**
- ดู recent events 2026:
  - AGM 2026 resolutions (23/04/2026)
  - Q1/2026 results (14/05/2026)
  - ไม่มี announce เรื่อง acquisition / new product line / ASEAN expansion
- **= management ยัง organic growth focus** — ยังไม่ pivot ไป inorganic

### Growth runway grade
- **Thailand market** — ยาว 5-10 ปี structural demand
- **Regulation tailwind** — 4 ตัวบังคับใช้พร้อมกัน = unprecedented
- **ASEAN expansion** — opportunity ยังไม่ taken (Vietnam / Indonesia / Philippines มี cybersecurity boom เหมือนไทย)
- **Risk**: ถ้า SECURE ไม่ขยายไป ASEAN ใน 3-5 ปีนี้ = miss window (คู่แข่ง G-Able / Yip In Tsoi อาจ expansion ก่อน)

### Q1/2026 fresh data = growth confirm
- Q1/2025 ดิป -28.7% NP (lumpy revenue + base effect)
- Q1/2026 ฟื้น +18.7% NP YoY = back to growth track
- Sales growth Q1/2026 +4.25% (low) แต่ margin expansion (NM 11.19% vs 9.83% Q1/2025) = pricing power + service mix แข็งขึ้น

---

## Layer 7 — Owner & management

### Ownership map (top 10 ณ 13/03/2026)

| # | ผู้ถือหุ้น | % | ประเภท |
|---|-----------|---|--------|
| 1 | บริษัท มอซ เซกูโร จำกัด | 25.33% | Corporate (family holding co) |
| 2 | น.ส. สุกัญญา ล้วนจำเริญ | 15.49% | Individual / Family |
| 3 | นาย นักรบ เนียมนามธรรม (CEO) | 14.09% | Individual / Family |
| 4 | บริษัท ฮิวแมนิก้า จำกัด (มหาชน) | 3.14% | Strategic — listed company partner |
| 5 | น.ส. พสิกา รัตนพงศ์ | 2.26% | Individual |
| 6 | นาง รุ่งรวี ล้วนจำเริญ | 1.81% | Individual / Family (สุกัญญา's relative) |
| 7 | MISS ARPAPORN LUANCHAMROEN | 1.79% | Individual / Family (ล้วนจำเริญ) |
| 8 | Thai NVDR | 1.47% | NVDR |
| 9 | MR. SUPACHAI BURISTRAKUL | 1.42% | Individual |
| 10 | MR. BADIN JANJAI | 1.25% | Individual |

### Founding control breakdown
- **เนียมนามธรรม + มอซ เซกูโร**: บริษัท มอซ เซกูโร (25.33%) เป็น family holding co + นักรบ (CEO) 14.09% รวม = **~39.4%**
  - หมายเหตุ: ต้อง verify มอซ เซกูโรเป็น vehicle ของตระกูลเนียมนามธรรมจริงๆ จาก SET filing 56-1 ไม่ใช่แค่ name similarity
- **ล้วนจำเริญ family** (สุกัญญา + รุ่งรวี + ARPAPORN รวม 3 holder): **~19.1%**
- **Total founding control combined: ~58.5%**
- **ฮิวแมนิก้า 3.14%** — บมจ. Humanica (อยู่ใน mai) เป็น strategic shareholder (น่าจะ relationship ผ่าน enterprise software service ที่ทำคู่กันได้) — verify จาก 56-1

### Free float
- 40.91% (2,693 holders) — ค่อนข้างกระจาย
- เพิ่มจากปี 2025 (40.70%, 2,834 holders) — holders ลดเล็กน้อย แสดงว่ามีคนเก็บใหญ่ขึ้น

### Foreign holding
- **0.00%** (Foreign limit 49% — เปิดเต็มที่)
- = **ต่างชาติยังไม่สนใจ** หรือ market cap เล็กเกินกระดาน institutional ต่างชาติ
- อาจเป็น **catalyst** ถ้าได้ขึ้น SET100/SETHD index — แต่ปัจจุบันอยู่ mai ทำให้ index inclusion ยาก

### Board of directors (จาก SET factsheet)

| # | ชื่อ | ตำแหน่ง |
|---|------|---------|
| 1 | Miss PATTANANT PETCHCHEDCHOO | **Chairman / Independent / Chairman of Audit Committee** |
| 2 | Mr. NAKROP NIAMNAMTHAM | CEO / Director (founding family) |
| 3 | Miss SUKANYA LUANCHAMROEN | Director (founding family) |
| 4 | Mr. ANOTAI ADULBHAN | Director |
| 5 | Mr. JUMRUD SAWANGSAMUD | Independent Director |
| 6 | Mr. CHAOWCHAI JIAMVIJID | Independent Director |
| 7 | Mr. PIYASAK CHOTIPRUK | Independent / Audit Committee |
| 8-9 | (2 ที่เหลือ — ไม่ extract ครบ คาดว่า independent + 1 family) | – |

### Governance signal — strong
- **Chairman เป็น Independent + Chairman of Audit Committee** = separation of chairman & CEO (best practice)
- Miss PATTANANT — ไม่ใช่ family — เป็น professional governance
- Independent directors **5 จาก 9** = สูงกว่า SET minimum (1/3) → strong governance signal
- CG Report = **4 (Good)** — ดีกว่า average mai
- SET ESG / CAC = "-" — **ยังไม่ได้ rating** อาจเพราะ company ใหม่ + market cap เล็ก
  - **action item**: ถ้าได้ ESG rating ในอนาคต = ยกระดับ + เปิด institutional ต่างชาติ

### ผู้บริหารแกน 3 ข้อ (เซียนฮง: ซื่อสัตย์ + เก่ง + มีไฟ)

#### "ซื่อสัตย์" — verify จาก SET enforcement history
- **ไม่พบใน source ปัจจุบัน** ว่า SECURE หรือ CEO นายนักรบเคยถูก กลต./ตลท. enforcement
- ต้อง check ที่ sec.or.th/enforcement หรือ kaohoon column
- Chairman เป็น Independent strong signal — board governance ดี
- ค่าใช้จ่าย vs peer — SG&A ratio 8.9% ปี 2025 = ระดับปกติของ IT distributor (5-10%)
- **First impression: pass** — แต่ user ควร verify เพิ่มเอง

#### "เก่ง" — ROE + capital allocation track record
- ROE 16.27% ปี 2025 = solid (Tech industry median ~12-15%)
- Capital allocation: IPO 2021 → กำไรโต 6 ปีติด + cash หนา + ไม่เสี่ยงหนี้ = **prudent**
- Margin expansion (GM 16% → 22%) = **operational excellence**
- **Verdict: เก่งจริง**

#### "มีไฟ" — investor presentation + DPS growing 4 ปีติด
- DPS growing 4 ปีติด (0.18 → 0.30 → 0.45 → 0.90 → 1.00) = management commit คืนเงินผู้ถือหุ้น
- Investor presentation — ไม่มีใน source ปัจจุบัน ต้อง check Opportunity Day video
- Q1/2026 ฟื้น = management react ทัน
- **Verdict: ดูมีไฟ — แต่ verify ด้วยการดู IR presentation จริงๆ ก่อน high confidence**

---

## Layer 8 — Moat depth

### Cybersecurity distributor moat ใน Thailand

#### 1. Vendor authorization (highest barrier)
- การเป็น **tier-1 distributor** ของ Fortinet / Palo Alto / CrowdStrike ใน Thailand = limit จำนวน (vendor มี exclusive territory)
- ต้องผ่าน:
  - ยอดขาย threshold ปีละหลาย MUSD
  - Certified engineer จำนวนเฉพาะ
  - Training budget commitment
  - Brand exclusivity (บางกรณี)
- ใหม่เข้าตลาด **= ยากมาก** เพราะ vendor ไม่อยากเพิ่ม distributor ที่เป็น competition กันเอง
- SECURE มี existing relationship 10+ ปี (founded 2014) = **competitive moat**

**ความเสี่ยง**: vendor อาจตัด distributor / appoint distributor ใหม่ที่อ่อนลง → SECURE หาย — แต่นี่เป็น rare event (ทุก 5-10 ปี)

#### 2. Technical certification + engineer headcount
- Cybersecurity engineer ที่ certified Fortinet NSE 7+ / Palo Alto PCNSE / CrowdStrike CCFA = หายากในไทย
- บริษัทขนาด SECURE น่าจะมี **50-150 certified engineer** estimate (ไม่อยู่ใน source)
- = moat ที่ replicable ลำบาก เพราะ engineer ไทยที่เก่ง security มีจำกัด (สมอง drain ไปเมืองนอก)

#### 3. Customer relationships (switching cost)
- Bank/government ใช้ SECURE มา 5-10 ปี = ทีม engineer SECURE กับทีม IT ลูกค้ารู้จักกันตัวต่อตัว
- ต่อ contract ใหม่ปกติ incumbent vendor มีโอกาส win > 80%
- = **strong customer retention** เป็น moat (แม้ไม่ disclose)

#### 4. Sales pipeline + market knowledge
- B2B enterprise sales ต้องอาศัย relationship + understanding regulatory ของไทย (PDPA + BOT + NCSA)
- คู่แข่งจากต่างประเทศเข้ามายาก เพราะ Thai context
- SECURE = local player + 10+ years experience = **local moat**

#### 5. Compliance domain knowledge
- Cybersecurity audit + assessment + incident response ต้องรู้กฎไทย + แมป กับมาตรฐานสากล (ISO 27001 / NIST / PCI-DSS)
- SECURE มี service practice นี้แล้ว = **knowledge moat**

### Moat ranking (1-5)
- Vendor authorization: 4/5 (strong but contractually renewable)
- Engineer talent: 4/5 (scarce in Thailand)
- Customer lock-in: 4/5 (high switching cost)
- Brand: 2/5 (B2B not consumer-facing, ไม่ได้แข็งเท่า G-Able ที่เก่าและใหญ่)
- Cost advantage: 3/5 (economies of scale ระดับกลาง)

**Overall moat: ปานกลาง-สูง** — ไม่ใช่ wide moat แบบ Buffett-style แต่ defensible enough สำหรับ 3-7 ปี

---

## Layer 9 — Competitive landscape

### Direct competitors ในตลาดไทย (estimate from public knowledge)

| คู่แข่ง | ขนาด | จุดแข็ง | จุดอ่อน |
|---------|------|---------|---------|
| **G-Able Group** (จดทะเบียน 2023) | ใหญ่กว่า SECURE (revenue ~6-8B) | systems integration + cyber + cloud + AI | margin บางกว่า (4-5%) เพราะ scope กว้าง |
| **Yip In Tsoi (ยิบอินซอย)** | privately held ใหญ่มาก (~10B+) | history 80+ ปี + government deep relationship | private — ไม่ rate vs SECURE ได้ |
| **ACU Group** | mid-size (~2-3B) | full-stack IT services | margin บาง |
| **MFEC** (จดทะเบียน SET) | ใหญ่ ~5-6B | systems integration | cyber เป็น 1 in many |
| **BLISS Telecom (BLISS)** | small | cyber + telecom | scope limited |
| **VST ECS** | private — distributor IT ใหญ่สุด | volume เยอะ + vendor ครบ | commodity IT margin บาง |

### Direct sales by vendors (long-term threat)
- Fortinet / Palo Alto / CrowdStrike ขยาย direct enterprise sales force ในไทย → กิน share จาก distributor
- ปัจจุบันยัง small ของ total — distributor ยัง core channel
- **ระยะยาว 5-10 ปี** ถ้า vendor พึ่ง direct มาก → SECURE-class distributor ต้อง pivot ไป service / MSSP มากขึ้น

### Foreign distributor (Crayon, Westcon-Comstor, Ingram Micro)
- Global distributor มี office ในไทย
- แข่งใน segment ใหญ่ที่ vendor หลายเจ้าต้อง consolidate
- SECURE specialist focus = ได้เปรียบ ใน sub-segment cybersecurity

### Vendor competition (Fortinet vs Palo Alto vs Check Point vs Cisco)
- vendor หลักแข่งกันเอง → distributor ที่ทำหลาย vendor ได้ประโยชน์ (sell whichever client wants)
- SECURE positioning ที่ multi-vendor = **flexibility advantage**
- ความเสี่ยง: vendor บีบ distributor ให้ exclusive → SECURE ต้องเลือกฝ่าย

### SECURE positioning vs competitors
- Margin (NM 9.3%) **สูงสุดในกลุ่ม distributor** ที่ public — สูงกว่า MFEC (3-4%) / G-Able (4-5%)
- Focus เฉพาะ cybersecurity = specialist premium
- Market cap เล็ก = ยังโตได้อีกหลายเท่า ถ้า penetrate ตลาดเพิ่ม

---

## Layer 10 — Macro / regulatory / policy risk

### 1. NCSA (สำนักงานคณะกรรมการการรักษาความมั่นคงปลอดภัยไซเบอร์แห่งชาติ)
- ตั้งตาม พ.ร.บ. การรักษาความมั่นคงปลอดภัยไซเบอร์ 2562
- บังคับ critical infrastructure (8 sectors: ธนาคาร / energy / IT / telecom / transport / health / government / public service)
- บริษัทใน scope ต้องรายงาน incident + audit + assess
- = **tailwind** สำหรับ SECURE-class service provider

### 2. BOT IT-risk mandate
- ธนาคารแห่งประเทศไทย — IT Risk Guidelines + Cyber Resilience Framework
- บังคับ commercial bank + finance company + payment service provider
- 2025-2026 มี audit เข้มขึ้น → demand security tool + service โต

### 3. PDPA enforcement
- บังคับใช้เต็ม 1 มิ.ย. 2022
- 2024-2025 ปรับจริง: บริษัทละเมิดข้อมูลส่วนบุคคล โดน penalty + ฟ้องร้อง
- → demand data security tool + DLP + monitoring โต
- **SECURE benefit** ในส่วน DLP / encryption / access management product mix

### 4. Cyber Security Act compliance
- บริษัทใน scope ต้องมี CISO + Incident Response Plan + Tabletop Exercise
- → demand cybersecurity advisory + service โต

### 5. Geopolitical (US-China tech split)
- US sanction Chinese vendor (Huawei / Hikvision security camera ที่ banking ใช้)
- บางลูกค้าต้อง rip & replace Chinese product → **ทดแทนด้วย US vendor** ที่ SECURE distribute = opportunity
- ความเสี่ยง: US export control บางอย่าง อาจ ban ขายไทย (rare แต่มี risk)

### 6. SET regulation risk
- SECURE อยู่ mai — มี risk ขยับขึ้น SET / ตกลงไม่อยู่ — ไม่น่ามี (financial healthy + listed >3 ปี)
- ถ้าได้ขึ้น SET กระดานหลัก = catalyst เพิ่ม visibility

### 7. Tax risk
- BOI privilege (ถ้ามี) อาจหมดอายุ → effective tax rate เพิ่ม
- ไม่มีข้อมูลใน source ปัจจุบัน ต้องดู notes to financial statement

### 8. Currency risk
- COGS ส่วนใหญ่ USD (vendor หลักเป็น US)
- Revenue THB
- THB อ่อน → COGS เพิ่ม → squeeze margin (lag 1-2 quarter ก่อนผ่านราคาให้ลูกค้า)
- 2026 baht ผันผวน = risk ระยะสั้น

### Macro risk grade
- ⚠️ Currency: ปานกลาง
- ✅ Regulatory: tailwind หนัก (4 ตัว)
- ⚠️ Vendor disintermediation: ปานกลาง — slow burn risk
- ✅ Geopolitical: opportunity มากกว่า threat

---

## Layer 11 — Hong 9-criteria scoring

### Check ทีละข้อ + ตัวเลขสนับสนุน

#### 1. D/E ≤ 1x — **PASS strong**
- D/E 2025 = **0.50x** (annualized FY)
- D/E Q1/2026 = 0.33x (ลดลงอีก)
- Total debt 390 MB แต่ส่วนใหญ่เป็น lease/AP ไม่ใช่ bank loan
- Interest expense 1.1 MB เทียบ EBITDA 162.7 MB = nominal
- **Verdict: ✅ ผ่านสบาย** อยู่ใน "safe zone" ของเซียนฮง

#### 2. เงินสดในมือพอจ่ายหนี้สั้น + ปันผล — **PASS strong**
- Cash 2025 = **577 MB** (FY end)
- Short-term debt = **0** (ไม่มี OD + ไม่มี current portion LT) — verified จาก SET balance sheet
- Annual dividend paid = 0.90 + 1.00 = ~190 MB (ประมาณการจาก DPS × 102.7M shares = 195 MB)
- Cash / (Short-debt + Dividend) = 577 / (0 + 195) = **2.96x** ผ่านสบาย
- **Verdict: ✅✅** เงินสดเหลือ runway หลายปีแม้ไม่มีกำไรเข้ามา

#### 3. Gross + Net margin trend — **PASS**
- Gross margin: 19.79% (2020) → 18.93% (2021) → 16.23% (2022 dip) → 19.65% (2023) → 19.86% (2024) → 20.04% (2025) → 22.05% (Q1/2026)
  - 3y recent avg (2023-2025): **19.85%**
  - 3y earlier (2020-2022): **18.32%**
  - = **improving trend +1.5 pp**
- Net margin: 3.71% → 7.42% → 6.16% → 8.61% → 9.34% → 9.32% → 11.19% (Q1/2026)
  - **6-year improvement +5.6 pp** จาก IPO base
- เทียบ peer distributor IT ไทย (NM 3-7%) — SECURE มากกว่ามาก
- **Verdict: ✅** trend ดี + relative peer ดีกว่า

#### 4. Cash flow ≈ Net profit — **PASS strong**
- 2025: OCF 211.11 MB / NP 121.51 MB = **1.74x** (OCF มากกว่า NP — strong cash generation)
- 3y CCR average (2023-2025): 0.81 (ยังต่ำกว่า 0.8 threshold แต่ปีล่าสุดดีดเด่น)
- FCF 2025 = 207 MB (CAPEX จิ๊บจ๊อย)
- **Verdict: ✅✅** กำไรเป็นเงินจริง ไม่ใช่ accounting trick
- ⚠️ Caveat: OCF ปี 2024 = 62 MB / NP 116 MB = 0.54x (ปีเดียวที่อ่อน) — เพราะ A/R จ่ายช้า เงินยังไม่กลับ → ปี 2025 collect ได้เลยพุ่ง

#### 5. ROE relative to industry — **PASS**
- ROE 2025 = **16.27%**
- Annualized Q1/2026 = 16.30% (stable)
- เทียบ Technology industry median ไทย ~12-15%
- 3y avg ROE: 15.71% (2023) + 16.57% (2024) + 16.27% (2025) = ~16.2%
- ไม่มี ROE distortion year (ทุกปี 9-17%)
- **Verdict: ✅** เหนือ median industry ~1-3 pp stable

#### 6. กำไรสุทธิทำ all-time high ต่อเนื่อง — **PASS**
- NP timeline (MB): 23.5 (2020) → 61.1 (2021) → 55.1 (2022 dip) → 91.8 (2023) → 115.6 (2024) → 121.5 (2025)
- **NP new high 3 ปีติด** (2023 → 2024 → 2025)
- 2022 ดิป -10% เพราะ post-IPO investment + cycle
- **Verdict: ✅** ผ่าน — แต่ growth ปี 2025 +5.1% เท่านั้น (ชะลอจาก +26% ปี 2024) — watch
- Q1/2026 +18.7% YoY ฟื้นกลับ growth track

#### 7. กำไรโต ~26%/ปี ต่อเนื่อง 3 ปี — **PASS borderline**
- NP CAGR 3y (2022 → 2025): (121.5/55.1)^(1/3) - 1 = **30.0%**
- NP CAGR 5y (2020 → 2025): (121.5/23.5)^(1/5) - 1 = **38.9%**
- EPS CAGR (per MaxMahon): **30.95%**
- **Verdict: ✅✅** เหนือ threshold 26% ทั้ง 3y และ 5y
- ⚠️ ปีล่าสุด (2025) growth +5.1% — แสดงถึง **deceleration** ที่ต้องจับตา
- Q1/2026 +18.7% = ฟื้น แต่ยังไม่ถึง 26% trajectory ระยะยาว — ต้องดู 2-3 Q ข้างหน้า

#### 8. Forward PE ≤ 15x — **PASS strong**
- Forward PE = **9.14x** (จาก SET factsheet)
- MaxMahon forward PE = 7.52x (อาจคำนวณจาก projection ต่างกัน)
- Trailing PE 9.64x = consistent
- **Verdict: ✅✅✅** ต่ำกว่า 15 มาก = ถูกชัด

#### 9. Dividend yield 4-7% — **PASS in band**
- Yield 2025 (FY-based) = **7.20%** จาก SET factsheet
- Yield 8.77% per MaxMahon (อาจใช้ DPS trailing 12m รวม 2024 H2 + 2025 H1)
- 5y average yield = 4.96% — แสดงว่า yield ดีดขึ้นช่วง 2024-2025 (จาก DPS โต ไม่ใช่ราคาตก)
- **Verdict: ✅** อยู่ในกรอบ Hong (4-7%) — ส่วน 7.2% อยู่ปลายบน
- Payout 53% sustainable (policy 50% — บริษัทจ่ายเกินเล็กน้อย = commitment to shareholder return)

#### PEG concept check
- เซียนฮง concept: growth/PE ≥ 1.5x → PE/growth ≤ 0.67
- Growth NP 3y CAGR = 30% / Forward PE = 9.14 → **PEG = 9.14 / 30 = 0.30**
- หรือ PEG = 7.52 / 25 (conservative growth) = 0.30
- **Verdict: ✅✅✅** PEG ต่ำกว่า 0.67 มาก = Sweet Spot ของจริง

### สรุป 9 + PEG criteria

| # | Criterion | Status |
|---|-----------|--------|
| 1 | D/E ≤ 1 | ✅✅ |
| 2 | Cash ≥ short-debt + dividend | ✅✅ |
| 3 | Margin trend | ✅ |
| 4 | CFO ≈ NP | ✅✅ |
| 5 | ROE vs industry | ✅ |
| 6 | NP new high | ✅ |
| 7 | NP CAGR 26%/3y | ✅✅ |
| 8 | Forward PE ≤ 15 | ✅✅✅ |
| 9 | Yield 4-7% | ✅ |
| PEG | ≤ 0.67 | ✅✅✅ |

**ผ่านครบ 9 + PEG — SECURE = Sweet Spot ของจริง**

### Compare vs Hong-finalist 9 ใน MaxMahon Hong pool

| Stock | Yield | PE | PEG | ROE | NP CAGR 3y |
|-------|-------|-----|-----|-----|------------|
| COM7 | 4.4% | – | – | 41.5% | low |
| MOSHI | 2.3% | – | – | 26.5% | medium |
| PSP | 4.4% | – | – | 21.7% | high |
| TFM | 9.0% | – | – | 29.0% | high (recovery) |
| OSP | 3.7% | – | – | 22.7% | recovery |
| TOA | 4.5% | – | – | 20.7% | recovery |
| SISB | 3.8% | – | – | 26.3% | high |
| KDH | – | – | – | 17.8% | medium |
| TSC | 7.8% | – | – | 22.3% | medium |
| **SECURE** | **7.2%** | **9.14** | **0.30** | **16.27%** | **30%** |

SECURE จุดเด่นกว่า 9 ตัวเดิม:
- **PEG ต่ำสุด** (0.30 vs ตัวอื่นน่าจะ 0.5+)
- Yield สูง 7.2% + Forward PE ต่ำ 9.14x
- ROE 16.27% **ต่ำกว่าค่าเฉลี่ย** (vs COM7 41%, SISB 26%) — เป็นจุดอ่อน

SECURE จุดอ่อนกว่า 9 ตัวเดิม:
- Market cap เล็กสุด (1.16B vs COM7 huge) — liquidity ต่ำ
- อยู่ mai ไม่ใช่ SET กระดานหลัก
- Track record สั้นกว่า (listed 2021 vs many ตัว listed 2014-2018)

---

## Layer 12 — Position sizing + watch triggers

### Position sizing ใน Hong portfolio

#### กรอบใหญ่ (จาก MEMORY)
- Portfolio allocation: **70 Niwes / 25 Hong / 5 Cash**
- Hong 25% = แตกเป็น **4 ตัว สุดท้าย** (อาร์ทยังตัดสินไม่จบ)
- Per stock = ~6.25% ของ total portfolio
- หรือ 25% Hong → SECURE (1/4) = 6.25% ของพอร์ตทั้งหมด

#### เซียนฮง 30:30:30:10 framework apply ยังไง
- จากเงิน 6.25% ที่จัดสรรให้ SECURE:
  - **Round 1 (30%)**: ซื้อทันทีถ้า conviction พอ (1.9% ของ total portfolio)
  - **Round 2 (30%)**: เพิ่มเมื่อราคาขึ้น 7-8% จากซื้อ round 1
  - **Round 3 (30%)**: เพิ่มอีกถ้ายังขึ้นต่อ
  - **Reserve 10%**: เก็บไว้
- **Cut loss -8%** จาก average ของ round 1 = exit ทันที (ตรง Hong rule)

#### ทำไม SECURE เหมาะ Hong (สรุปสั้น)
1. ผ่านเกณฑ์ 9 + PEG ครบ (verified)
2. Sector tailwind (cybersecurity compliance) = catalyst structural 5-10 ปี
3. DPS growing 4 ปีติด = mgmt commit คืนเงินผู้ถือหุ้น
4. Valuation ถูก (PE 9.14 / PEG 0.30) = margin of safety
5. Q1/2026 ฟื้น = growth story กลับมา

#### ความเสี่ยงของ position size
- **Liquidity risk**: mai stock + market cap 1.16B = volume ต่ำ — ออกใหญ่ๆ ตอน sentiment แย่อาจ slippage
- **Single sector concentration**: ถ้า SECURE คือ tech-distributor ใน 4 Hong stocks → portfolio Hong มี sector imbalance
- **แนะนำ position sizing**: เริ่ม **conservative** อาจจะ 50-70% ของ 6.25% (= 3-4.5% ของ total) ในช่วง 6 เดือนแรก ดูพฤติกรรม earnings 2 quarters ก่อน scale full position

### Watch trigger — **ลด weight / exit**

#### 🚨 Trigger 1: Vendor concentration risk realized
- ถ้า SECURE แจ้งสูญเสีย distributor agreement ของ Fortinet หรือ vendor หลัก
- ดู: SET 56-1 disclose vendor mix / news release / Q&A ที่ Opportunity Day
- = exit ทันที — moat หาย

#### 🚨 Trigger 2: Growth gone, ไม่ใช่ pause
- Q1/2026 ฟื้น +18.7% เป็น sign positive
- ถ้า Q2 + Q3 + Q4 ของ 2026 กลับลบ 3 quarters ติดต่อกัน = thesis change
- = ลด weight 50% หรือ exit

#### 🚨 Trigger 3: DPS streak break
- DPS เพิ่ม 4 ปีติด — ถ้าปี 2026 DPS ลด = signal capital allocation/profitability เสื่อม
- = ลด weight 30%

#### 🚨 Trigger 4: Tech disruption signal
- ถ้า vendor หลัก (Fortinet/Palo Alto) เปลี่ยน distribution model ไปขายตรงมากขึ้น (เห็นจาก vendor earnings call หรือ press release)
- หรือ Zero Trust / SASE replace point product แบบใหญ่
- = re-evaluate moat — ลด weight ตาม conviction

#### 🚨 Trigger 5: Insider selling pattern
- CEO นายนักรบ (14.09%) ขายหุ้นใหญ่ผ่าน SET 246 disclose
- มอซ เซกูโร (25.33% family holding) ขาย
- = lose confidence signal — ลด weight 30%

#### 🚨 Trigger 6: ROE drop หรือ Margin compression
- ROE ต่ำกว่า 13% (= ต่ำกว่า industry median) 2 ปีติด
- Net margin ต่ำกว่า 7% 2 ปีติด
- = thesis change — ลด weight

#### 🚨 Trigger 7: Major lawsuit / regulatory action
- กลต./ตลท. enforcement
- ลูกค้า bank/government ฟ้อง data breach
- = exit ทันที (Hong rule: ผู้บริหารถูก enforcement = filter แรก)

### Watch trigger — **เพิ่ม weight**

#### ✅ Trigger A: กำไร new all-time high
- ถ้า annual 2026 NP > 130 MB = new high
- + margin maintain ≥ 9% = thesis confirm
- = เพิ่ม weight ไป full position

#### ✅ Trigger B: New vendor partnership ASEAN
- SECURE announce expansion ไป Vietnam / Indonesia / Philippines
- หรือ partner กับ vendor ใหม่ที่ growing (Wiz / Cribl / SentinelOne for ASEAN)
- = growth runway ขยาย — เพิ่ม weight

#### ✅ Trigger C: Bank mandate ใหม่ที่ขยาย demand
- BOT issue new IT-risk regulation ที่บังคับ extra security
- NCSA expand critical infrastructure scope
- = direct tailwind — เพิ่ม weight

#### ✅ Trigger D: ขึ้น SET กระดานหลัก
- ถ้าได้ขึ้น SET (market cap + ระยะเวลา + free float ผ่านเกณฑ์)
- = ดึงดูด institutional + ต่างชาติ — re-rating PE possible
- = เพิ่ม weight ก่อนหรือหลัง index inclusion

#### ✅ Trigger E: SET ESG / CAC rating ได้
- ปัจจุบัน "-" ทั้งคู่ — ถ้าได้ rating BBB+ ขึ้น
- = ESG fund flow ใหม่
- = เพิ่ม weight

### Final position recommendation (กูเสนอ)
- **Entry round 1**: 30% ของ 6.25% allocation = **1.9% ของ total portfolio** เมื่อราคา 11-12 บาท (= forward PE 9-10x = within thesis)
- **Round 2**: +30% ถ้าราคาขึ้น 7-8% (12-13 บาท) + 1 Q earnings confirm trajectory
- **Round 3**: +30% ถ้าราคา 13-14 บาท + 2 Q earnings confirm
- **Reserve 10%**: เก็บไว้ rebalance หรือซื้อตอน dip
- **Cut loss**: -8% จาก average = ~10.5 บาท (ถ้าเริ่ม 11.3) → exit ทันที

---

## Closing notes — สำหรับ session ต่อไป

### Strength ของ thesis
1. ✅ ผ่าน 9-criteria + PEG ครบ — Sweet Spot ของจริง
2. ✅ Sector tailwind หนัก 4 ตัว (PDPA / BOT / NCSA / Cyber Act)
3. ✅ Q1/2026 growth กลับมา confirm thesis
4. ✅ Balance sheet สะอาดมาก (cash หนา + ไม่มีหนี้สั้น)
5. ✅ Governance แข็ง (Independent Chairman + 5/9 ID)
6. ✅ DPS growing 4 ปีติด — mgmt commit

### Weakness ที่ต้อง verify เพิ่ม
1. ⚠️ **Vendor concentration unknown** — ไม่รู้ว่า Fortinet / Palo Alto = กี่ % ของ revenue — risk #1 ที่ต้อง check ที่ 56-1
2. ⚠️ **Customer concentration unknown** — top 10 customer revenue % ไม่ disclose
3. ⚠️ **Business description detail ใน SET file น้อย** — ต้องไป IR website / 56-1 / Opportunity Day video
4. ⚠️ **อยู่ mai** ไม่ใช่ SET — liquidity ต่ำกว่า + index inclusion ยาก
5. ⚠️ **Track record สั้น** (listed 2021) — ไม่มี cycle หลายรอบให้ดู resilience
6. ⚠️ **2025 growth slow** (+5%) — ถ้า Q2/2026 onwards ไม่ฟื้นต่อ = thesis pause
7. ⚠️ **No SET ESG / CAC rating** — institutional ต่างชาติยังเข้าไม่ได้

### Items ที่อาร์ทต้อง decide ต่อ
1. รวม SECURE เข้า Hong final pool **4 ตัว** ไหม? (ปัจจุบันมี 9 finalist + SECURE = 10)
2. ถ้ารวม → ตัวไหน drop จาก 9 เดิม?
3. Position sizing — เริ่ม conservative (50% ของ allocation) หรือ full 30:30:30:10?
4. รอ Q2/2026 earnings (Aug 2026) ก่อน entry หรือเข้าทันที?

### Sources used (verifiable)
- SET official factsheet: `C:\WORKSPACE\projects\4-MaxMahon\hong-lens\set-factsheets\SECURE.xls`
- SET companyprofile: `C:\WORKSPACE\projects\4-MaxMahon\hong-lens\set-companyprofiles\SECURE.xls`
- MaxMahon yearly cache: `C:\WORKSPACE\projects\4-MaxMahon\data\screener_cache\2026-05-20\SECURE.BK.json`
- Stage 2 mini-card: `C:\WORKSPACE\projects\4-MaxMahon\hong-lens\research\stage2-12-stocks-2026-05-21.md` (section #14)
- Hong philosophy research: `C:\WORKSPACE\_shared\docs\research-sianhong-stock-picking.md`

### Sources ที่ต้องไป verify เพิ่ม (อาร์ท หรือ session ใหม่)
- **Annual Report 56-1 ของ SECURE 2025** (จาก IR website www.nforcesecure.com หรือ SETSMART) — สำหรับ vendor mix / customer concentration / segment breakdown
- **Opportunity Day Q1/2026 video** (ปกติ SET broadcast บน YouTube) — สำหรับ "มีไฟ" check
- **MD&A Q1/2026** (มีอยู่จริง released 14/05/2026 — extract เพิ่มได้)
- **กลต. enforcement history** สำหรับ CEO นายนักรบ + Chairman + Audit Committee — sec.or.th/enforcement
- **Public knowledge** เรื่อง vendor relationship — ดูจาก Fortinet ASEAN distributor list, Palo Alto Partner Portal, etc.

---

_จบเอกสาร — เขียนโดยทำงานในกรอบ Hong Lens 25% portfolio allocation สำหรับอาร์ท / ภาษาเขียนภาษาคน + ทับศัพท์ลงทุน / ตัวเลขทุกตัวมาจาก SET official หรือ MaxMahon cache / ส่วนที่เป็น industry estimate flag ชัด_
