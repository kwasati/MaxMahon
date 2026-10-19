# TCAP deep dive — "ถือและซื้อตัวนี้ต่อไปทุกเดือนอีก 10 ปี เรามาถูกทางไหม?"

- Created 2026-10-19 · job job-14-dd-tcap (desk z79h) · reference price **82.50** = close 2026-10-15 used by the fact sheet FS · yahoo 2026-10-19 ~11:45 (intraday) = 81.25 (−1.5%, does not change any conclusion) · holding: 4,700 shares at average cost 59.80 (`config.json` holdings.costs)
- New book under the corrected principles (EPS-based growth, normal profit, C2 for every stock, D15 belief table). The old book `research/tcap-deep-dive-2026-10-09.md` (RS) was read for leads only; every number below was re-checked against a dated source. Where the old book was wrong, see section 10.
- knowledge: `knowledge/domain/data-cross-check.md` (DC-1..5) → every DPS year checked across yahoo + panphol + company IR table; FY2019 4.00 special separated; snippet-only numbers labelled; investor material (One Report, snapshot, MD&A) opened first; shareholders searched against SEC cases · `knowledge/domain/growth-metric-traps.md` (GM-1, GM-2) → every growth rate states its base year; TTM EPS checked from quarterly data · `knowledge/domain/thai-data-sources.md` (TD-1) → quarterly data from yfinance, IR PDFs via curl + pypdf (kaohoon/prachachat 403 as expected)
- Ruler: `docs/niwes-principles.md` (C/Q/P/F/H/X · T1–T6 section 4 · D1–D18 section 5). Niwes said nothing about TCAP that we can quote verbatim (C8/P1 are Investerest interpretations, label `คนอื่นตีความ`) — every opinion about TCAP in this file is ours.
- Language: this book is written in English by the worker tab (workspace rule); Thai headings/quotes are copied from the AMATA template and the principles file. The head translates for Art.
- Working files (desk z79h `files/`): `tcap_q.py` + `tcap_q_out.txt` (yahoo pull) · `or2568-ONEREPORTTCAPT.txt` (One Report 2568, 506 pages) · `tcap-ar2019-th.txt` (annual report 2562, 324 pages) · `q2-2026-FINANCIAL_STATEMENTS.xls` + `tcap-q2-2026-mdna.txt` (Q2/2026) · `tcap-snapshot-fy25.txt` · `ttb-pres-2q26.txt` `ttb-pres-4q23.txt`

## รหัสแหล่ง (ใช้ซ้ำทั้งไฟล์)

| Code | Source | Data as of | Fetched |
|---|---|---|---|
| FS | System fact sheet `reports/holdings/TCAP_2026-10-19.md` (`fact_sheet.py TCAP --cost TCAP=59.80`, built after the system changes) — A1 DPS by FY, A3 growth, A4 lump + DCA tables, A5 EPS/ROE, A10 year-end PE/PBV/yield, T-flags | FY2025 + close 2026-10-15 | 2026-10-19 |
| Y | yahoo via yfinance `files/tcap_q.py` → `files/tcap_q_out.txt` — unadjusted closes, annual/quarterly statements 2022–Q2/2026, raw ex-dividend dates 2018→ for TCAP TTB THANI MBK PRG, peer snapshot | 2026-10-19 intraday | 2026-10-19 |
| OR | 56-1 One Report 2568 (PDF from SEC zip 0083ONE240320261417300671T, published 24 Mar 2026) — p22 history, p66 dividend policy + 5-yr table, p145–150 consolidated statements, p149/p260 cash flow, p321 associates table | FY2025 | 2026-10-19 (pypdf) |
| AR19 | Annual report 2562 `tcap.listedcompany.com/misc/ar/20200312-tcap-ar2019-th.pdf` — p4 5-yr summary, p13–14 chairman letter (special dividend), p200–201 cash flow, p284 note 37, p289 related-party note | FY2019 | 2026-10-19 (pypdf) |
| Q2 | Q2/2026 reviewed statements XLS (SET package 0083FIN100820260947230109T: sheets BS/PL/CF, consolidated + **separate**) + MD&A PDF 0083NWS100820261859290850T (11 Aug 2026) | 30 Jun 2026 | 2026-10-19 |
| SN | Company snapshot FY2568 (company-made, published 9 Mar 2026) `thanachart.co.th/.../20251231-tcap-company-snapshot-fy25-th.pdf` — stakes, 4-yr financials, shareholders 15 Sep 2025, revenue mix | FY2025 | 2026-10-19 (curl + pypdf) |
| IR-DIV | thanachart.co.th dividend-information page — policy wording + table FY2008–2025 (net profit, shares, EPS, interim/final, payout) | FY2025 | 2026-10-19 |
| IR-SH | thanachart.co.th major-shareholders — top 10 as of **14 Sep 2026** | 14 Sep 2026 | 2026-10-19 |
| IR-HIS | thanachart.co.th about-us/our-history — founding 2523, bank licence 2545, holding 2548, BNS 2550, SCIB 2553, TMB merger 2562, TNS sale 2568 | 2025 | 2026-10-19 |
| PP | aio.panphol.com/stock/TCAP/dividend — per-XD rows FY2023–FY2026 (page also has 1986→ but tool returned recent rows) | 11 Sep 2026 | 2026-10-19 |
| TRIS | TRIS Rating 29 Sep 2026 via hoonsmart 440996 — A/Stable, double leverage 107%, triggers (ttb stake, DL >120%) | Jun 2026 | 2026-10-19 |
| TTB-IR | ttb press releases: 12M21 (20 Jan 2022), 12M23 (19 Jan 2024), 12M24 (20 Jan 2025), 12M25 (20 Jan 2026), 2Q26 via pptvhd36 279987 (21 Jul 2026) | FY2021–1H26 | 2026-10-19 |
| TTB-P | ttb investor presentations 2Q26 (20 Jul 2026, media.ttbbank.com 8157-th.pdf) p5 p30 p38 p39 p41 p42 · 4Q23 (19 Jan 2024, 6991-en.pdf) p4 p15 | 1H26 / FY2023 | 2026-10-19 (pypdf) |
| IVX | InnovestX ttb update 23 Jan 2026 — 2025A credit cost 1.06% (1.36% incl. overlay), NIM 3.04%, loans −7%, DPS 0.136 | FY2025 | 2026-10-19 |
| BOT | Bank of Thailand banking-system reports: Q2/2569 via isranews 148483 (18 Aug 2026) · Q4/2568 via posttoday 738147 (17 Feb 2026) | Q2/2026 | 2026-10-19 |
| BRK | Broker notes: Kasikorn Securities via hoonvision tcap-3 (4 Aug 2026) · Krungsri via mitihoon 672793 (2 Sep 2026) · Krungthai via share2trade 57729 (3 Aug 2026) · buyback approval via hoonsmart 430774 (30 Jul 2026) | Jul–Sep 2026 | 2026-10-19 |
| PR | TCAP press release Q2/2026 thaipr 3749096 (11 Aug 2026) — CEO name, buyback terms | Q2/2026 | 2026-10-19 |
| S2T | share2trade 54788 (24 Apr 2026) — Niwes family TCAP holdings at record date 17 Apr 2026 | 17 Apr 2026 | 2026-10-19 |
| THANI | THANI Q2/2026 — kaohoon 852655 **search snippet only** (site 403): NPL 2.4% Jun 2026 vs 2.6% Dec 2025, HP receivables 35,765 mn | Jun 2026 | 2026-10-19 |
| RS | Old book `research/tcap-deep-dive-2026-10-09.md` — leads only, checked in section 10 | 9 Oct 2026 | — |
| NP | `docs/niwes-principles.md` — principles, T1–T6, D1–D18 | 2026-10-09 | — |

Not reachable this round: kaohoon (403 — only search snippets) · settrade/set.or.th (JS) · SEC One Report zip failed on first curl (http 000) and worked with referer + TLS1.2 · the SET's own 2019 MD&A PDF found in search is the Stock Exchange's MD&A, not TCAP's (not used) · ttb Q3/2026 results not yet announced (scheduled 20 Oct 2026 per share2trade 60167) · TCAP Q3/2026 not yet announced.
Not found (searched): SET listing year of TCAP (One Report p22–23 and the history page give founding 2523 only) · THANI truck-HP market share as a number (company claims "ผู้นำในธุรกิจเช่าซื้อรถบรรทุก" OR p23) · ttb's rank by assets (commonly cited as 6th; not verified this round → `เดา:`) · any SEC enforcement against the top-10 shareholders (search 2026-10-19 returned nothing — absence of result, not proof of absence).

---

## 1. คำตอบ 1 หน้า

**Answer: holding is on track by the T-flags (none lit); buying more every month at ~82 is a different question — today's yield 4.2% is below Niwes' 5% (C1) and TCAP passes only through C3 (yield growing, reaches 5% of today's price within 5 years if EPS grows ≥3.3%/yr).** Owner's 7–12% target is parked: the A4/DCA numbers are reported in section 4 as facts, no verdict on the target.

What TCAP is today (OR p145, p321 · SN · Q2):
1. **A holding company whose profit is ~74% ttb**: share of profit from associates 5,707 mn of 7,750 mn company profit in FY2025 (ttb ≈ 24.93%, MBK 24.69%, PRG 24.80%); THANI (66.94%) 1,148 mn and Thanachart Insurance (TNI, 100%) 1,077 mn are the operating subsidiaries. Kasikorn Securities puts ttb at ~70% of profit (BRK). Listed stakes alone are worth ~89.6 bn at 19 Oct prices vs TCAP market cap 86.5 bn at 82.50 (section 3 D13) — the market pays nothing for TNI/T-Life/AMCs and charges nothing for parent debt.
2. **Dividend record**: regular DPS never cut in 24 fiscal years (FY2002–FY2025, FS A1; IR-DIV FY2008–2025 agrees to the satang), flat in 2008, 2011, 2014, 2020, 2021; up 4 years in a row to 3.50 (FY2025); FY2026 interim 1.50 (+15% vs 1.30). Payout 47% of FY2025 EPS 7.39. FY2019's 7.00 contains a 4.00 special from the TBANK sale — confirmed in the chairman's letter (AR19 p14) and already in `config.json` special_dividends.
3. **Growth is slow and comes from ttb**: EPS 2020→2025 grew 3.4%/yr (IR 6.26→7.39; FS cache 6.12 gives 3.8%), DPS 3.1%/yr; 10-year EPS 4.8%/yr (2015 base 4.61). H1/2026 EPS 4.54 (+26% YoY) is inflated by dividend income +140% and provisions −80%; the recurring part (share of associates +13%) is the number to trust (Q2 MD&A p4, p7). TTM EPS 8.33 > FY2025 7.39 (Y) — GM-2 check passes.
4. **Price is at the top of its own range**: PE 11.2 on FY2025 EPS (9.9 on TTM), PBV 1.03–1.10 vs 10-year year-end range 0.58–1.09, yield 4.2% at the 10th percentile of its own history (FS A10 label `แพงเทียบตัวเอง`). The 2026 rally (+42% YTD: 58.25 → 82.50) rode ttb (+45%: 2.02 → 2.92, Y) and the buyback announcement.
5. **The 7,500 mn buyback (17 Aug 2026–16 Feb 2027) shows no evidence of execution**: no treasury shares at 30 Jun 2026 (Q2 BS), no SET buyback report found (search 2026-10-19), Kasikorn (4 Aug) says the budget is expected to go to dividends instead after the price crossed 1.0x PBV, Krungsri (2 Sep) says "มีโอกาสจ่ายเงินปันผลพิเศษหาก TCAP ไม่ได้ทำการซื้อหุ้น" (BRK). Treat the +11% EPS from a full buyback as unproven.

Confidence: high that the dividend history, FY2025 normal profit and the ttb bank numbers are right (2–3 sources agree) · medium on the growth scenarios (depend on ttb profit and on whether ttb's share cancellations lift TCAP's stake) · what would change the answer fastest: ttb's Q3/2026 (20 Oct 2026) and TCAP's buyback report by 16 Feb 2027.

Decisions for Art and the head (not taken here): (a) accept "TCAP = ttb ~74%" and therefore watch ttb's T-flags as TCAP's lead flags (section 6); (b) whether DCA continues at yield <5% under C3 or pauses (section 7 gives the price ladder); (c) write `normal_eps` 7.32 (FY2025) and 5.36 (FY2019) and the 1.5/4/7% scenarios into `config.json` (section "ค่าที่ต้องจดลง config").

---

## 2. ใบข้อเท็จจริง

### 2.1 ปันผลต่อหุ้นรายปีบัญชี (ยาวสุดที่หาได้ — 3 แหล่งเทียบกัน)

FY rule: interim XD Aug–Oct of year N + final XD Apr of N+1 = FY N (IR-DIV columns "interim Jan–Jun / final Jul–Dec" confirm the split). Y raw ex-dates agree with PP for every row FY2023–FY2026; IR-DIV agrees with FS for every FY2008–FY2025.

| FY | Interim | Final | Regular DPS | Special | EPS (IR-DIV) | Payout (IR-DIV) | Year-end close (Y, unadjusted) | Yield on regular DPS | Sources |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2008 | 0.30 | 0.60 | 0.90 | — | 2.08 | 42% | — | — | IR-DIV FS |
| 2009 | 0.35 | 0.60 | 0.95 | — | 3.99 | 24% | 22.10 | 4.3% | IR-DIV FS Y |
| 2010 | 0.50 | 0.70 | 1.20 | — | 4.41 | 27% | 36.00 | 3.3% | IR-DIV FS Y |
| 2011 | 0.50 | 0.70 | 1.20 | — | 3.91 | 31% | 26.75 | 4.5% | IR-DIV FS Y |
| 2012 | 0.50 | 0.90 | 1.40 | — | 4.31 | 32% | 37.75 | 3.7% | IR-DIV FS Y |
| 2013 | 0.60 | 1.00 | 1.60 | — | 7.49 (abnormal year, see D1) | 21% | 32.25 | 5.0% | IR-DIV FS Y |
| 2014 | 0.60 | 1.00 | 1.60 | — | 4.24 | 38% | 31.75 | 5.0% | IR-DIV FS Y |
| 2015 | 0.70 | 1.10 | 1.80 | — | 4.61 | 39% | 36.50 | 4.9% | IR-DIV FS Y |
| 2016 | 0.80 | 1.20 | 2.00 | — | 5.16 | 39% | 44.00 | 4.5% | IR-DIV FS Y |
| 2017 | 0.90 | 1.30 | 2.20 | — | 6.01 | 37% | 56.25 | 3.9% | IR-DIV FS Y |
| 2018 | 1.00 | 1.60 | 2.60 | — | 6.74 | 38% | 49.75 | 5.2% | IR-DIV FS Y |
| 2019 | 1.20 (XD 3 Oct 2019) | 1.80 (XD 13 Apr 2020) | **3.00** | **4.00** (XD 27 Dec 2019, paid Jan 2020 — AR19 p14) | 9.43 (abnormal, see D1) | 73% on 7.00 | 53.50 | 5.6% | IR-DIV AR19 Y PP |
| 2020 | 1.20 | 1.80 | 3.00 | — | 6.26 (FS cache 6.12 — flag) | 47% | 34.50 | 8.7% | IR-DIV OR p66 FS Y |
| 2021 | 1.20 | 1.80 | 3.00 | — | 5.04 | 60% | 37.75 | 7.9% | IR-DIV OR p66 Y |
| 2022 | 1.20 | 1.90 | 3.10 | — | 4.98 | 62% | 42.50 | 7.3% | IR-DIV OR p66 Y |
| 2023 | 1.20 | 2.00 | 3.20 | — | 6.30 | 51% | 49.50 | 6.5% | IR-DIV OR p66 Y PP |
| 2024 | 1.25 | 2.05 | 3.30 | — | 6.35 | 52% | 50.50 | 6.5% | IR-DIV OR p66 Y PP |
| 2025 | 1.30 (XD 12 Sep 2025) | 2.20 (XD 16 Apr 2026) | **3.50** | — | 7.39 | 47% | 58.25 | 6.0% | IR-DIV SN Y PP |
| 2026 (open) | **1.50** (board 31 Aug 2026, XD 11 Sep, paid 30 Sep) | — | — | — | H1 EPS 4.54 | — | 82.50 (15 Oct) | trailing 12m 3.70 / 82.50 = 4.5% | PP Y Q2 |

- Regular-DPS cuts in 24 years: **0** (FS A2 "ลดทุกขนาด 0 ครั้ง") · flat years 2006 2008 2011 2014 2020 2021 (FS A1 "+0%") · FY2019 special 4.00 confirmed verbatim in AR19 p14: "เงินปันผลจากผลประกอบการตามปกติปี 2562 ในอัตราหุ้นละ 3.00 บาท และเงินปันผลพิเศษหุ้นละ 4.00 บาท รวมเป็นเงินปันผลจ่ายหุ้นละ 7.00 บาท" → `config.json` special_dividends TCAP 2019 = 4.0 is **correct**.
- Growth with base year stated (FS A3 + table): DPS 5y 2020→25 3.1% · 10y 2015→25 6.9% · 15y 2010→25 7.4% · 20y 2005→25 7.7% — the long windows include the era when TCAP consolidated Thanachart Bank (until 3 Dec 2019); the structure since 2020 is different, so the post-merger window is the honest base.
- IR-DIV cell check (DC-1): the tool read FY2020 net profit as "3,124" — inconsistent with EPS 6.26 × 1,049 mn shares ≈ 6,567 mn; treated as a misread/typo and not used. FS cache FY2019 EPS 7.03 and FY2020 6.12 disagree with the company's 9.43 and 6.26 (OR p66, AR19 p13) — flagged for the head (section 9).

### 2.2 รายได้ กำไร เงินสด (ล้านบาท) — where FY2025 profit comes from (OR p145 consolidated P&L · SN · Q2 MD&A)

| Line (consolidated, mn baht) | 2023 | 2024 (restated) | 2025 | H1/2026 | Note |
|---|---:|---:|---:|---:|---|
| Share of profit from associates (ttb, MBK, PRG) | 4,663 | 5,565 | **5,707** | 3,109 (+13.1% YoY) | = 74% of company profit 2025 · ttb ≈ 70% of TCAP profit (BRK Kasikorn) |
| Net interest income (THANI hire-purchase + parent) | 3,374 | 2,809 | 2,622 | 1,185 (−11.4%) | THANI lends cautiously, loan book shrinking (Q2 MD&A p6) |
| Insurance income net of insurance expense (TNI, T Life) | 2,345 | 590 | 1,118 | 810 (+83%) | TNI profit 1,077 (2025), 889 (H1/26) |
| Dividend income (investment portfolio) | 218 | 293 | 497 | 864 (+140%) | lumpy — "ตามนโยบายการลงทุนในธุรกิจการเงิน" (SN) |
| Gains: FVTPL + investments + debt settlement + foreclosed assets | 548 | 54 | 499 | 142 | volatile; foreclosed assets swung −165 → +171 |
| Expected credit loss (ECL) | 1,016 | 1,003 | 738 | 83 (−82%) | THANI asset quality improving (NPL 2.4% Jun 2026, THANI snippet) |
| Profit from continuing operations (group) | 7,207 | 7,043 | 8,189 | 5,089 | |
| Discontinued operations (TNS, sold to ttb 1 Jul 2025) | — | −21 | **+75** | — | one-off line, removed in normal EPS |
| **Profit attributable to TCAP** | 6,603 | 6,655 | **7,750** | **4,765** | EPS 6.30 / 6.35 / 7.39 / 4.54 |
| Revenue mix (SN, FY2025) | | | HP & leasing 23.84% · insurance 17.79% · investment & other 58.37% | | |

Group structure at 31 Dec 2025 (OR p23, p321 · SN): ttb **24.93%** (associate; book value of the stake 60,859 mn; ttb's own treasury shares 5,105 mn at year-end) · MBK **24.69%** (up from 22.64% in 2024) · PRG **24.80%** (since 19 May 2025) · THANI **66.94%** (up from 63.24% during 2025) · TNI 100% · T Life, T Broker, T Plus, TS AMC/NFS AMC/MAX AMC 100% (OR p22 structure chart) · TNS sold to ttb 1 Jul 2025 (SN).

### 2.3 เงินสดจริงที่ระดับบริษัทแม่ — dividends received vs paid (separate statements: OR p260 · Q2 CF/BS separate columns · TRIS)

| | FY2024 | FY2025 | H1/2026 | Source |
|---|---:|---:|---:|---|
| Dividends received by the parent (separate cash flow) | 4,090 | **4,384** | **3,082** | OR p260 · Q2 CF |
| Dividends paid to TCAP shareholders | 3,406 | **3,511** | **2,307** (final FY2025 2.20) | OR p150 · Q2 CF |
| Interest paid on debt securities & borrowings (consolidated) | 1,651 | 1,536 | 814 (expense) | OR p150 · Q2 MD&A |
| Parent interbank deposits + investments + FVTPL (cash-like) | — | 3,078 + 2,237 + 1,358 = **6,673** | 2,255 + 7,070 + 0 = **9,325** | Q2 BS separate (31 Dec 2025 audited column / 30 Jun 2026) |
| Parent debt securities issued & borrowings (+ FI borrowings) | — | 26,442 + 200 = **26,642** | 27,664 + 300 = **27,964** | Q2 BS separate |
| Parent total liabilities / equity | — | 27,751 / 80,514 (0.34x) | 28,753 / 83,766 (0.34x) | Q2 BS separate |
| Parent investments in subsidiaries / associates (equity method) | — | 21,062 / 65,439 | 22,798 / 66,784 | Q2 BS separate |
| Loans from parent to group companies | — | 12,367 | 10,842 | Q2 BS separate ("เงินให้สินเชื่อ") |
| TRIS double leverage (investments in subs+associates ÷ parent equity) | — | — | **107%** (trigger for downgrade >120%) | TRIS 29 Sep 2026 |

- Estimated ttb cash dividend to TCAP: ~24.3 bn ttb shares (fair value 49,138 mn ÷ ttb close 2.02 at 30 Dec 2025, OR p322 · Y) × FY2025 DPS 0.134 (Y; TTB-P p38) ≈ **3.26 bn** (calc) → ttb alone covers ~93% of what TCAP pays; THANI (0.17/share FY2025, Y) + MBK (1.00) + PRG (0.76) + TNI (unlisted) fill the rest. Parent received 4,384 mn in 2025 = 1.25x dividends paid.
- The parent carries ~28 bn of debt securities against ~9 bn cash-like assets and 10.8 bn loans to group companies; the debt funds THANI/T Plus lending through the parent and the ttb stake (TRIS: "2.6 เท่า" investments to interest-bearing debt). Not a cash-rich holding; a leveraged one at a modest 107% double leverage.

### 2.4 หนี้ · ทุน · ซื้อหุ้นคืน (OR p25 p144 · SN · Q2 · PR · BRK)

| Item | 2022 | 2023 | 2024 | 2025 | 30 Jun 2026 | Note |
|---|---:|---:|---:|---:|---:|---|
| Total assets (consolidated) | 156,978 | 158,138 | 160,791 | 154,674 | 157,380 | SN · Q2 |
| Total liabilities | 84,553 | 80,783 | 80,309 | 68,662 | 68,069 | of which debt securities & borrowings 45,824 (2025), insurance contract liabilities 13,523 (OR p144) |
| Equity attributable to TCAP | 66,673 | 71,290 | 74,506 | 80,514 | 83,766 | BVPS 79.88 (Y) · hoonsmart 78.84 (Mar 2026) |
| D/E (SN) | 1.17 | 1.04 | 1.00 | 0.80 | — | falling 3 years; bank-style D/E not comparable to industrials (A6 not printed for banks, FS) |
| ROE (SN) | 7.93% | 9.64% | 9.11% | 10.06% | 12.81% (Q2 annualised, MD&A p4) | |
| Shares outstanding (mn) | 1,048.6 | 1,048.6 | 1,048.6 | 1,048.6 | 1,048.6 | treasury 116.5 mn (2021) → 97.0 mn (2022) → cancelled 2 May 2023 (OR p25: paid-up 11,456.6 → 10,486.2 mn baht) |

- **Buyback 2026**: board 30 Jul 2026 approved ≤7,500 mn baht, ≤104,861,673 shares (10%), 17 Aug 2026–16 Feb 2027, AOM method (PR · hoonsmart 430774). Status 19 Oct 2026: no treasury shares at 30 Jun 2026 (program not started yet, Q2 BS), **no SET buyback report found in search**, Kasikorn (4 Aug) expects the budget redirected to dividends after price > 1.0x PBV, Krungsri (2 Sep) sees a special dividend "หาก TCAP ไม่ได้ทำการซื้อหุ้น" (BRK). → the +11% DPS/EPS from a full 10% buyback is **not** in the base case.
- Credit: TRIS "A" / Stable reaffirmed 29 Sep 2026; downgrade triggers: weaker subsidiary ratings, double leverage >120%, a significant fall in the ttb stake (TRIS).

### 2.5 ตัวเลขแบงก์ของ ttb (ไม่ใช่คำนิเวศน์ — เราเลือกแทน "เงินสดเหลือเฟือ") — copied into `data/manual_facts/TCAP.json`

| ttb | 2021 | 2022 | 2023 | 2024 | 2025 | 1H/2026 | Source |
|---|---:|---:|---:|---:|---:|---:|---|
| Net profit (mn) | 10,474 | 14,195 | 18,462 | 21,031 | **20,639** (−1.9%) | 10,683 (+5.8%) | TTB-IR · TTB-P 4Q23 p4 ("THB 14.2 bn") |
| NPL (Stage 3) ratio | 2.81% | 2.7% | 2.62% | 2.59% | **2.87%** (39.1 bn) | **2.93%** (38.9 bn) | TTB-IR · TTB-P 2Q26 p5 |
| Coverage (LLR/NPL) | 124% (1Q21) | 138% | 155% | 151% | **152%** | **157%** | TTB-P 2Q26 p31, 4Q23 p22 · TTB-IR |
| Credit cost (bps) normal / total | not in release | 133 / — | 128 / 164 | ≈150 total (calc: provisions 19,852 mn ÷ ~1.3 trn loans — not stated by ttb) | **106 / 136** | **91 / 136** | TTB-P 4Q23 p4 p15 · 2Q26 p5 · IVX |
| Tier 1 / CAR (BIS) | 15.3% / 19.3% | n/a | 17.0% / 20.7% | 16.9% / 19.3% | **17.5% / 19.5%** | **17.0% / 19.0%** | TTB-IR · TTB-P 2Q26 p38 |
| CET1 | n/a | n/a | n/a | n/a | 17.5% (1Q26, IVX via search) | **17.7%** (TTB-P 2Q26 p42; p39 says "17%") | internal comfort level ~16% |
| NIM | n/a | 2.95% | 3.24% | n/a | 3.04% | 3.02% | TTB-P 4Q23 p4 · 2Q26 p5 |
| Loan growth | −1.5% | +0.4% | −3.5% | −6.6% | **−2.9%** (1,205 bn) | −1.8% YTD (1,184 bn) | TTB-IR · TTB-P |
| DPS (FY) / payout | 0.038 + warrants (BoT cap) | 0.073 / 50% | 0.105 / 55% | 0.130 / 60% | **0.134** / 60% | interim 0.081 | TTB-P 2Q26 p38 · Y |
| Share buyback | — | — | — | — | 21 bn programme 2025–27 | **21 bn done = 10.29% of paid-up**, raised to 35 bn through 2028 (14 bn left) | TTB-P 2Q26 p39 p42 · TTB-IR |

- ttb shareholders 12 Jun 2026 (TTB-P p41, % of total paid-up incl. 10.3% treasury): TCAP 24.4% · ING 17.5% (→ ~11.6% after the 18 Aug 2026 placement, infoquest 633930 via search) · Ministry of Finance 11.7% · Vayupak 3.6% · ttb (treasury) 10.3%. panphol 8 Sep 2026: TCAP 24.11% (search snippet). TCAP's own figure 24.93% (OR, Dec 2025). If ttb cancels the treasury shares, TCAP's economic share rises toward ~27% without buying a share (calc) — this is the only "free" EPS growth in the system and it is not yet booked.
- Sector backdrop for D8 (BOT): system loans −1.1% YoY in Q4/2025 (6 consecutive quarters of contraction, SME 14 quarters), NPL 2.84% (536 bn), Stage 2 7.07%; Q2/2026 loans **+2.0%** YoY (large corporates +6.6%, SME −4.6%, hire-purchase −7.0%), NPL **2.82%** (534.8 bn), Stage 2 6.78%, system net profit 83 bn (+6.8% YoY); policy rate 1.00% after 150 bps of cuts since late 2024 (Q2 MD&A p2 · TTB-P p29).

---

## 3. คำตอบ D1–D18 ทีละข้อ

Labels: `เลข` = from numbers · `คน` = our judgement · confidence high = 2+ sources agree.

| # | Answer | Evidence + source | Label | Conf. |
|---|---|---|---|---|
| D1 yield ≥5%? paid from normal profit? | **No at today's price**: FY2025 DPS 3.50 ÷ 82.50 = **4.24%** (FS A10 4.2%); 3-year average yield **4.0%** (FS A10, 3 years = our number). On cost 59.80: 5.85%. **Normal profit FY2025**: company profit 7,750 mn includes +75 mn from discontinued TNS (sold 1 Jul 2025) → remove → **normal EPS 7.32** (7,675 ÷ 1,048.6). Also inside continuing profit: FVTPL 179 + investment gains 76 + debt-settlement gains 74 + foreclosed-asset gains 171 = 499 mn pre-tax (volatile but recurring every year: 548 in 2023, 54 in 2024) — a stricter normal EPS removing ~400 mn after tax/NCI would be ~6.94; we propose **7.32** and list 6.94 as the stricter alternative. Bank-type provisions (ECL 738 mn) are a normal cost, not removed (NP D1). Payout on normal EPS = 3.50 ÷ 7.32 = **48%** → the dividend is paid from normal profit. **Abnormal years in A5**: FY2019 EPS 9.43 (company) / 7.03 (FS cache) includes the TBANK sale — consolidated gain on disposal of subsidiaries 4,664 mn (AR19 p200 cash-flow adjustment; separate-FS gain 53,647 mn, AR19 p284 note 37) → **normal EPS 2019 ≈ (10,807 − 4,664) ÷ 1,146 mn weighted shares = 5.36** (`เดา:` pre-tax gain used; tax effect on the gain not disclosed per share — the head should check against the discontinued-operations note before writing it). FY2013 EPS 7.49 (profit 9,231) is also a spike year (RS attributes it to the Thanachart Life sale to Prudential — not verified this round, left out of config). | FS A10 A12 · OR p145 · AR19 p4 p13 p200 p284 · Y | เลข+คน | high (yield, FY2025) · medium (2019 normal) |
| D2 in 5 years DPS ≥5% of today's price? | Needs DPS ≥ 4.125 by FY2030 = **3.3%/yr** from 3.50 at constant payout. Earnings-based scenarios (section 4.1): bad 1.5% → FY2030 DPS **3.77** (4.6% of 82.50) ✗ · mid 4.0% → **4.26** (5.2%) ✓ · good 7.0% → **4.91** (6.0%) ✓. Fact-sheet C2 flag with the current config (2/4/5.4%) is ✅ "ไม่ติด" at 5.2% (FS). What we trust: ttb share of profit growing +13% H1/26 (Q2 MD&A), ttb's buyback lifting TCAP's stake toward ~27% (TTB-P), THANI provisions normalising. Obstacles: ttb profit −1.9% in 2025 and guidance "ทรงตัว" for 2026 (IVX), NIM 3.02% under a 1.00% policy rate, system loans barely positive, TCAP's own buyback not executing, holding-level debt 28 bn. | section 4.1 · FS A4 · TTB-P p5 · IVX · Q2 | เลข+คน | medium |
| D3 (yield 2–3%… here 4.2%) DPS rising? reaches 5% in 5 years without obstacles? | Regular DPS **up 4 consecutive FYs** 2022–2025 (FS A1) after 3 flat years 2019–2021; FY2026 interim +15%. Growth 2020→2025: DPS 3.1%/yr vs EPS 3.4%/yr (IR) — payout 48% → 47%, so the DPS growth was **not** payout expansion (GM-1 passes for this window). The 2019→2025 window is distorted by the abnormal 2019 EPS. Reaching 5% needs 3.3%/yr — the mid scenario clears it, the bad one does not. "No obstacles" is false: see D2 list. | FS A1 A3 A12 · IR-DIV · section 4 | เลข+คน | high |
| D4 if business falls, can the dividend hold? | Payout 47% → EPS can fall **52.6%** before payout hits 100% (FS A5, our number). Worst EPS drop in A5: 2014 **−44%** — but the base 2013 was a spike year (D1), so the real worst normal-year drop is 2020→2021 −19% (6.26 → 5.04, IR) and 2010→2011 −11%. Crisis test 2020: ttb's dividend was capped by the BoT (TTB-P p38 note "In 2021, banks' dividend payment was capped by the BoT's guidance") yet TCAP paid 3.00 flat (D12). Bank cushion today (2.5): ttb CET1 17.7%, CAR 19.0%, coverage 157%, NPL 2.93%, credit cost 136 bps vs long-term aspiration 125–135 (TTB-P p6). Holding cushion: parent received 4,384 mn vs paid 3,511 mn in 2025 (1.25x); cash-like 9.3 bn vs debt 28.0 bn — a second year of ttb dividend cap would be paid from reserves/borrowing, as in 2020. | FS A5 · section 2.3, 2.5 · TTB-P | เลข+คน | medium (no ttb Q3 yet) |
| D5 revenue / profit / dividend streaks, stumbles, temporary or permanent? | FS A5: revenue up 3 years, EPS up 3 years (both stumbled 2022), DPS up 4 years. Stumbles: EPS 2020–2022 (6.26 → 5.04 → 4.98) = post-merger structure + COVID provisions at THANI + ttb's low 2020–21 dividend — recovered by 2023 (6.30) → **temporary**. Caveat on "revenue": the FS cache series (18,718 for 2025) is not the company's revenue (24,809, SN) — different definition; and TCAP revenue is interest + insurance premiums + equity-method profit, so C7 "revenue up every year" is a weak test for a holding. C7 itself is `ยังไม่ยืนยันซ้ำ` (NP) → supporting fact, not a criterion. | FS A5 · SN · IR-DIV | เลข+คน | high |
| D6 how old, how big? | Founded **2523 (1980)** as บริษัทเงินทุนหลักทรัพย์ ธนชาติ จำกัด (OR p22 · IR-HIS) · became a holding company 2548 (IR-HIS) · **SET listing year not found** in One Report or history page (searched; left blank in manual_facts) · dividends paid without a gap for 24 FYs in data (FS A1, since 2002; IR-DIV table from 2008) · market cap **86.5 bn** at 82.50 (85.1 bn intraday 19 Oct, Y) vs our size floor ≥5 bn (our number) · peers (Y, 19 Oct): BBL 354 bn · ttb 256 bn · TISCO 100 bn · KKP 98 bn. | OR p22 · IR-HIS · FS · Y | เลข | high (except listing year) |
| D7 does management look after shareholders? | **Announced policy (no %)**, verbatim OR p66 / IR-DIV: "ในการพิจารณาจ่ายเงินปันผล บริษัทฯ จะพิจารณาถึงผลประกอบการและผลตอบแทนของผู้ถือหุ้นในระยะยาว" + board may pay interim dividends when profit allows. Actual payout 2008–2025: 21%–73%, 47–62% since 2020 (IR-DIV) — consistent, twice a year, never cut. Capital returns: 2019–21 buyback (97 mn shares cancelled 2023), 4.00 special 2019, 2026 buyback approved (execution unproven). **Points to know**: cross-holding — MBK owns 24.90% of TCAP, TCAP owns 24.69% of MBK, same chairman บันเทิง ตันติวิท at both (OR p36 board list · IR-SH); ตันติวิท family members hold 1.67% + 1.35% (IR-SH ranks 7, 9); the 2025 PRG investment (24.80%, MBK-group company, 1,674 mn fair value OR p322) is money kept inside the family group rather than returned. CEO since 1 Jan 2025 พีระพัฒน์ เมฆสิงห์วี (PR). SEC check on top-10 holders (DC-4): search 2026-10-19 found no enforcement news for MBK / ลิ้มถิรคุณ / ตันติวิท — nothing found, not proof. | OR p66 p36 · IR-DIV · IR-SH · PR | คน | medium |
| D8 a. industry in decline? b. what disrupts it? | **a. Not in decline, but ex-growth**: Thai bank loans contracted 6 straight quarters to Q4/2025 (−1.1%), turned +2.0% YoY in Q2/2026 on large corporates while SME −4.6% and hire-purchase −7.0%; NPL 2.82%; policy rate 1.00% (BOT · Q2 MD&A). ttb: loans −6.6% (2024), −2.9% (2025), −1.8% YTD; NIM 3.24% (2023) → 3.02% (1H26); profit −1.9% in 2025 (TTB-IR). Truck hire-purchase (THANI): receivables 35.8 bn shrinking, NPL 2.4% improving (THANI snippet); TCAP's own NII −11% YoY (Q2 MD&A). Insurance (TNI): profit 1,077 mn, H1/26 889 mn — the one growing piece. **b. Disruption**: virtual banks — ttb itself positions "humanized digital banking (vs. a pure virtual bank)" and targets "<40% competitive C/I ratio compared to those of virtual banks" (TTB-P p6), i.e. ttb sees it as live competition; low rates compress NIM (already happening); EV trucks hitting used-truck prices — no dated source found this round (RS had none either). | BOT · TTB-IR · TTB-P p6 · Q2 MD&A · THANI | คน | medium |
| D9 market leader? | **No**. ttb is a mid-sized bank (assets 1,702 bn, OR p321) — `เดา:` 6th by assets (not verified this round); its own aspiration is "Top-quartile ROE of >10%" (TTB-P p6), not leadership. THANI: company says "ผู้นำในธุรกิจเช่าซื้อรถบรรทุก" (OR p23) — no market-share number found. TNI: premiums >10 bn/yr (RS, not re-verified). TCAP's edge is structural (cheap access to ttb + cross-holding control), not a moat. Q2 is `ยังไม่ยืนยัน` as a Niwes quote (NP). | OR p23 p321 · TTB-P p6 | คน | low |
| D10 cash abundant? (bank table + TCAP-level cash/debt) | **ttb** (2.5): CET1 17.7%, CAR 19.0%, NPL 2.93%, coverage 157%, credit cost 136 bps, 21 bn bought back — strong by every ratio. **TCAP parent** (2.3): cash-like 9.3 bn vs debt 28.0 bn (30 Jun 2026); dividends received 4,384 mn vs paid 3,511 mn (2025); double leverage 107% (TRIS). Verdict: the bank is over-capitalised; the holding is **not** cash-rich — it is a modestly leveraged owner of a cash-rich bank. Niwes' "เงินสดเหลือเฟือ" (Q1) is met at ttb, not at TCAP itself. | section 2.3 2.5 · TRIS · Q2 BS | เลข+คน | high (numbers) |
| D11 debt low vs industry? | Consolidated D/E 0.80, down from 1.17 in 2022 (SN) — most of the 45.8 bn debt securities fund THANI's hire-purchase book (normal for a lender). Parent-only liabilities 27.8 bn vs equity 80.5 bn = **0.34x** (Q2 BS separate); TRIS A/Stable. A6 not printed for banks and T6 not computed (FS) — for a holding we propose T6 = double leverage (section 6). No ⛔ rows to check (A6 absent). | SN · Q2 BS · TRIS · FS A6 | เลข | high |
| D12 crises 2551 / 2563: paid? cut? recovery? | 2008: DPS 0.90 **flat** (2007 0.90), 0.95 in 2009 (IR-DIV). 2020: 3.00 **flat**, flat again 2021, growth resumed 2022 (IR-DIV) while ttb's own DPS fell 0.04 → 0.045 → 0.038 (TTB-P p38) under the BoT cap. Price: 2019 close 53.50 → 2020 34.50 (**−36%**) → back above 53.50 only at end-2025 (58.25) = 5 years (Y, unadjusted). Never a cut, but a 5-year price drawdown. | IR-DIV · TTB-P p38 · Y | เลข | high |
| D13 hidden assets the market ignores? | Sum of listed stakes at 19 Oct 2026 intraday prices (Y): ttb ~24.3 bn sh × 2.92 = **71.0 bn** · MBK 24.69% × 28.1 bn = 6.9 bn · THANI 66.94% × 14.3 bn = 9.6 bn · PRG 24.80% × 8.1 bn = 2.0 bn → **89.6 bn = 85.4 baht/share**, vs market cap 86.5 bn at 82.50 (**listed parts = 104% of market cap**). Subtract parent net debt (28.0 − 9.3 = 18.6 bn) → 70.9 bn = 67.6/share. Unlisted: TNI (profit 1,077 mn → `เดา:` 8.6–10.8 bn at PE 8–10 = 8–10 baht/share), T Life, AMCs, T Plus loans 10.8 bn. **Reading**: at 82.50 you pay roughly the listed stakes and get TNI + the rest against the parent's 18.6 bn net debt — the holding discount that existed at 35–50 baht (RS: 30–40%) is **gone**. Not a hidden-value case any more (C11 is `คนอื่นตีความ`). | Y · OR p321 p322 · Q2 BS | เลข+คน | medium |
| D14 price reasonable? | PE **11.2** on FY2025 EPS 7.39, 11.3 on normal 7.32, **9.9** on TTM 8.33 (Y) — PE <10 (P3, weak evidence) passes only on TTM. PBV **1.03** (BV 79.88, Y) / 1.10 (FS formula) vs own 10-year year-end range 0.58–1.09 → above every year-end since 2017 (FS A10). Yield 4.2% at the 10th percentile of its own history; FS label **แพงเทียบตัวเอง** (our 25% rule). Our "fall 20–30%" ladder: 66.00 → yield 5.3% (back above C1), 57.75 → 6.1% (≈ end-2025 level). SN: at 30 Dec 2025 TCAP PE 8.49 / PBV 0.78 / yield 5.67% vs bank sector 8.32 / 0.75 / 5.93% — TCAP was priced like a bank then; today it trades above the bank sector on PBV (BBL 0.61, KBANK 0.98, SCB 1.03, Y). | FS A10 · Y · SN | เลข+คน | high |
| D15 what we want to believe | See the table in section 5 — five beliefs, each with counter-evidence and a falsifier tied to a T-flag; includes "Niwes holds TCAP". | section 5 | คน | — |
| D16 "wrong-way" flags for this stock | See section 6 — T1–T6 adapted to a bank holding, each mapped to a D15 belief. | section 6 | เลข+คน | — |
| D17 fit to add? concentration? | TCAP is 12.5% of the plan, Niwes leg = AMATA 35 / BBL 22.5 / TCAP 12.5 (`scripts/rebalance.py` TARGETS); TISCO off-plan. Financials in plan = BBL + TCAP = **35%**, more with TISCO. TCAP adds ttb (retail/auto bank), truck HP and non-life insurance — overlapping BBL only at the "Thai bank" macro level (rates, loan growth, BoT dividend caps). Art does not use the 5-stocks/5-industries rule (NP F1, 2026-10-19) — this row only states the overlap. | rebalance.py · NP F1 | เลข+คน | high |
| D18 | n/a — AMATA only | — | — | — |

---

## 4. ปันผลเทียบต้นทุน — ก้อนที่ถือ · เงิน DCA ใหม่ (facts only; the 7–12% target is parked — no verdict here)

### 4.1 สมมติฐานอัตราโต 3 ฉาก — earnings-based (EPS), base FY2025 DPS 3.50 at constant payout ~47%

| Scenario | EPS growth/yr | Why (base year stated) | Who set it |
|---|---:|---|---|
| bad | **1.5%** | ttb profit flat-to-down (2025 −1.9%, 2026 guidance "ทรงตัว" IVX; NIM 3.02% at policy rate 1.00%; system loans +2% with SME/HP shrinking); THANI book shrinking; TCAP buyback not executed; only ttb's share-count shrink adds anything. Below the long windows (EPS 2018→2025 1.3%/yr is the only lower one, and 2018 was a pre-merger structure). | us |
| mid | **4.0%** | = EPS CAGR 2020→2025 **3.4%** (IR 6.26 → 7.39) / 3.8% (FS cache 6.12), post-merger structure, normal base year; FS A3 10y EPS 4.8% (2015 base). DPS grew 3.1% in the same window with payout flat → repeatable. Same mid as the current config (4.0%). | us |
| good | **7.0%** | ttb cancels its 10.3% treasury shares → TCAP's share of ttb profit +~11% spread over ~3 years (+3.5%/yr) + ttb profit +3%/yr + THANI/TNI growth; TTM EPS 8.33 already +13% over FY2025 (Y). Excludes TCAP's own buyback and special dividends. Below our 10% ceiling (FS rule). The 2021→2025 CAGR of 10% is a COVID-base trap (GM-1) and is **not** used. | us |

### 4.2 ก้อนที่ถืออยู่ 4,700 หุ้น ต้นทุน 59.80 — DPS of year N ÷ cost (calc from 3.50; same arithmetic as FS A4)

| Scenario | g | FY2030 (yr 5) DPS → @59.80 · @82.50 · @66.00 | FY2035 (yr 10) | FY2040 (yr 15) |
|---|---:|---|---|---|
| bad | 1.5% | 3.77 → **6.3%** · 4.6% · 5.7% | 4.06 → 6.8% · 4.9% · 6.2% | 4.38 → 7.3% · 5.3% · 6.6% |
| mid | 4.0% | 4.26 → **7.1%** · 5.2% · 6.5% | 5.18 → 8.7% · 6.3% · 7.8% | 6.30 → 10.5% · 7.6% · 9.6% |
| good | 7.0% | 4.91 → **8.2%** · 6.0% · 7.4% | 6.89 → 11.5% · 8.3% · 10.4% | 9.66 → 16.1% · 11.7% · 14.6% |

- Today: 3.50 ÷ 59.80 = **5.85%** on cost (4,700 × 3.50 = 16,450 baht/yr); trailing 12 months 3.70 → 6.19%.
- FS A4 with the **current** config (2.0 / 4.0 / 5.4%) prints yr-10 @59.80 = 7.1% / 8.7% / 9.9% and the "required growth to 7% / 12%" table (59.80 yr 10: 1.8% / 7.4%) — reported as facts; whether that is "enough" is parked.
- C2 (Niwes, 5% of today's price in year 5): needs **3.3%/yr** → bad ✗ (4.6%) · mid ✓ (5.2%) · good ✓ (6.0%).

### 4.3 เงิน DCA ใหม่ ซื้อเท่ากันทุกเดือน 10 ปี — FS A4 DCA table (config scenarios 2 / 4 / 5.4%, price 82.50), copied as facts

| Scenario | g | yr 10: price grows with DPS / price flat | yr 15 |
|---|---:|---|---|
| แย่ (FS) | 2.0% | 4.7% / 5.2% | 5.2% / 5.7% |
| กลาง (FS) | 4.0% | 5.2% / 6.3% | 6.3% / 7.6% |
| ดี (FS) | 5.4% | 5.6% / 7.2% | 7.3% / 9.3% |

- FS also prints the average purchase yield needed for 7% / 12% at year 10: 5.74 / 9.84% (แย่) · 4.73 / 8.11% (กลาง) · 4.14 / 7.09% (ดี) — at DPS 3.50 that is an average price of 61–74 baht for 7% (vs 82.50 today). After the head writes the 1.5 / 4 / 7% scenarios into config, `fact_sheet.py TCAP --refresh --cost TCAP=59.80` regenerates this table — the mid row will not change (same 4%).

### 4.4 ตัวเลขที่ยังไม่รู้แล้วพลิกคำตอบได้
1. ttb Q3/2026 (due 20 Oct 2026): profit trend, credit cost, any change to the 60% payout or the 35 bn buyback → drives D2/D4.
2. Whether ttb **cancels** the repurchased 10.3% (TCAP's stake 24.4% → ~27% of a smaller base) — the single biggest lever in the good scenario; not yet announced.
3. TCAP's buyback execution by 16 Feb 2027 (treasury shares in Q3/Q4 balance sheets) — or a special dividend instead (BRK); either way not in the base case.
4. FY2026 final dividend (board ~Feb 2027): interim 1.50 + a final ≥2.20 would make FY2026 ≥3.70 (+5.7%).
5. The tax effect on the FY2019 disposal gain (normal EPS 2019 could be 5.4–6.2).

---

## 5. อะไรทำให้พัง — D15 belief table first, then risks that are nobody's belief

### 5.1 D15 — เรื่องที่เราอยากเชื่อ (≥2, each with counter-evidence + falsifier → T-flag in section 6)

| # | What we want to believe (1 sentence) | Strongest counter-evidence + source + date | What proves it wrong (falsifier → flag) |
|---|---|---|---|
| B1 | "Niwes holds TCAP, so holding it is on track." | He bought in 2557 at PE 7–8, PBV <1, yield ~5% (Investerest S6 — interpretation, NP C8); today PE 11.2 / PBV 1.03 / yield 4.2% (D14). His visible stake is **14.0 mn shares = 1.335%**, unchanged from 17 Apr 2026 (S2T) to 14 Sep 2026 (IR-SH rank 10); his wife and daughter's 8 mn each (S2T) are **below the top-10 cutoff** and cannot be confirmed as still held. TCAP pays him ~49 mn/yr of a reported ~220–230 mn family dividend income (S2T) — one of several holdings, and he cut Thai equities to 30% of his portfolio (S8, NP F3). His holding is a fact about his cost base, not about ours. | Niwes drops out of the top-10 at the next record date (Apr 2027) **or** his stake is cut while TCAP's T1/T2 are clean → our thesis must stand without him (→ **T2** on our own cost 59.80, not his). |
| B2 | "Regular DPS never cut in 24 years, so it will not be cut." | 2020 was held only because the **parent** paid 3.00 while ttb's dividend was capped by the BoT (TTB-P p38 note) — that cushion now sits on 28 bn of parent debt vs 9.3 bn cash-like (Q2 BS); ttb already pays 60% and buys back shares, so ttb's room to raise is smaller than in 2021–24; ttb profit fell in 2025 (TTB-IR). Payout at TCAP 47% is the real buffer. | **T1**: FY2026 DPS < 3.50 (final < 2.00) · **T3**: ttb FY DPS cut or BoT cap for a 2nd year · T4-holding: dividends received < dividends paid for a full year. |
| B3 | "The 10% buyback will lift DPS/EPS by ~11%." | No treasury shares at 30 Jun 2026; no SET buyback report found (19 Oct 2026); Kasikorn (4 Aug) and Krungsri (2 Sep) both expect the budget to go to dividends instead because the price is above book (BRK). RS's +11% was written before this was known. | Treasury shares = 0 in the Q3/Q4 2026 balance sheets and no report by **16 Feb 2027** → drop the lever from every scenario (→ **T2** recompute). |
| B4 | "TCAP is still the cheap way to own ttb (holding discount)." | Listed stakes = **104%** of market cap at 82.50; after parent net debt 18.6 bn the listed-only value is 67.6/share (D13). At 35–50 baht (2020–24) the discount was 30–40% (RS); it is gone at 82.50. PBV 1.03 is above every year-end since 2017 (FS A10). | Price ÷ SOTP (listed stakes) stays ≥1.0 for 4 quarters while yield <5% → new money fails C1 and only passes via C3 (→ **T2** at purchase price 82.50; section 7 ladder). |
| B5 | "H1/2026 profit +26% means TCAP has entered a growth phase." | Of the +988 mn YoY: dividend income +504 (lumpy portfolio dividends), ECL −379, share of associates +360, insurance +367, NII −153 (Q2 MD&A p4–p7). The repeatable part is the +13% share of associates; the rest is timing and the credit cycle. | **T3**: FY2026 profit ex-dividend-income-and-gains grows <5% while headline grows >15% → the growth is not normal profit. |

### 5.2 ความเสี่ยงที่ไม่ใช่ความเชื่อของใคร — ranked by probability × damage to the dividend

| # | Risk | Probability (10 yrs) | Damage to TCAP DPS | Temporary / permanent | Evidence |
|---|---|---|---|---|---|
| 1 | ttb profit stagnates: NIM 3.0% at policy rate 1.00%, loans −2.9% (2025), −1.8% YTD; 2025 profit −1.9% | high (happening) | medium: DPS flat, not cut (2020–21 precedent) | temporary if rate cycle; **permanent if Thai bank loans stop growing for a decade** (SME −4.6%, HP −7.0% BOT Q2/26) | TTB-IR · BOT · IVX |
| 2 | BoT caps bank dividends in a crisis (2020–21 precedent) → ttb dividend to TCAP falls for 1–2 years | medium | low–medium: parent paid from reserves in 2020; today 28 bn debt vs 9.3 bn cash-like | temporary | TTB-P p38 · Q2 BS |
| 3 | Capital kept inside the MBK family group (PRG 24.8% in 2025, MBK stake raised 22.6% → 24.7%) instead of returned | medium | medium: DPS does not grow; holding discount returns | permanent (governance) | OR p321 p322 · IR-SH |
| 4 | Holding-level refinancing: 27.7 bn debt securities at the parent; TRIS A/Stable, trigger DL >120% | low | medium if downgraded (funding cost up) | temporary | Q2 BS · TRIS |
| 5 | THANI truck cycle / used-truck prices (EV trucks — no dated source found) | medium | low: THANI ≈ 15% of profit, NPL 2.4% improving | temporary | THANI snippet · BRK |
| 6 | ttb shareholder churn: ING 23.1% → 11.6% in 2026 (search); "Super Bank" KTB–ttb merger talk appeared in search results (unverified — `เดา:` rumour) | low–medium | unknown: a merger could dilute or cash out TCAP's 24.9% | permanent | search 2026-10-19 (not verified) |
| 7 | Key person: chairman บันเทิง ตันติวิท at both TCAP and MBK; succession (CEO since 2025) visible, chairman age/plan not found | low | low | permanent | OR p36 · PR |

---

## 6. ธง "ผิดทาง" เฉพาะ TCAP (T1–T6 adapted to a bank holding) — every flag watches a D15 belief, every belief has a flag

| Flag | Measure | Where to read | Value today | Open a review when | Points to "permanent" when | Watches |
|---|---|---|---|---|---|---|
| T1 DPS cut | regular DPS per FY vs prior FY (never compare interim to full year; specials excluded) | IR-DIV / PP after final (~Apr) | FY2025 3.50 ↑ · FY2026 interim 1.50 ↑ | FY2026 total < 3.50 | 2 consecutive FY cuts (FS rule) | B2 |
| T2 yield on cost year 5 | DPS FY2030 ÷ 59.80 (lump) · ÷ purchase price for new money | section 4.2 · FS A4 | bad/mid/good = 6.3 / 7.1 / 8.2% on 59.80 · 4.6 / 5.2 / 6.0% on 82.50 | mid scenario <5% of purchase price (C2) | <5% even in good | B1 B3 B4 |
| T3 why the dividend moves | (a) ttb FY net profit and DPS (b) TCAP normal profit ex dividend income & gains (c) payout | ttb press release Jan · OR/MD&A | ttb 2025 −1.9%, DPS 0.134 ↑ · TCAP normal EPS 7.32 ↑ · payout 47% | ttb profit −10% in a year **or** TCAP normal profit down 1 year **or** payout >70% to hold DPS | ttb DPS cut 2 years · TCAP normal profit down 2 years (FS/NP rule) | B2 B5 |
| T4 paid from real cash (holding version — FS skips T4 for banks) | parent dividends received ÷ dividends paid (separate CF) · parent cash-like vs debt | OR separate CF · Q2 CF/BS | 2025: 4,384 / 3,511 = **1.25x** · H1/26 3,082 / 2,307 · cash-like 9.3 bn vs debt 28.0 bn | ratio <1.0 for a full year · parent debt up to pay dividends | 2 years <1.0 with rising parent debt | B2 |
| T5 industry | BOT system loan growth + NPL · ttb NIM + loan growth · THANI NPL | BOT quarterly · ttb deck · THANI MD&A | loans +2.0% (Q2/26), NPL 2.82% · ttb NIM 3.02%, loans −1.8% · THANI NPL 2.4% | system loans negative 4 quarters again · ttb NIM <2.8% · THANI NPL >5% | 8 quarters of system contraction with ttb profit falling | risk 1, 5 |
| T6 debt vs group (holding version) | TRIS double leverage · parent liabilities/equity · ttb CET1 | TRIS annual · Q2 BS · ttb deck | DL 107% · 0.34x · CET1 17.7% | DL >115% · ttb CET1 <15% | DL >120% (TRIS trigger) or TRIS downgrade | risk 4 |

Rule (NP section 4): T1 or T2 lit **and** T3/T4/T5 say permanent → open a "ปรับพอร์ต" review · lit but temporary → hold (H2) · no auto-sell (R6). Next dates: ttb Q3/26 **20 Oct 2026** · TCAP Q3/26 ~mid-Nov 2026 · buyback deadline **16 Feb 2027** · FY2026 final DPS ~Feb–Mar 2027 · ttb FY2026 results ~20 Jan 2027.

---

## 7. ราคาตอนนี้ถูกหรือแพง (for the cash plan — not a quality judgement)

| Price | Yield on FY2025 DPS 3.50 | PE on FY2025 7.39 / TTM 8.33 | PBV (BV 79.88, Y) | vs own history (FS A10) |
|---:|---:|---|---:|---|
| 82.50 (close 15 Oct 2026) | 4.2% | 11.2 / 9.9 | 1.03 | yield at 10th percentile of 10 yrs; PBV above every year-end 2016–2025 (max 1.09 in 2017) → **แพงเทียบตัวเอง** |
| 70.00 (= 5.0% yield, Niwes C1 line) | 5.0% | 9.5 / 8.4 | 0.88 | ≈ Jul 2026 level before the buyback news (71.25 on 30 Jul, hoonsmart) |
| 66.00 (−20%) | 5.3% | 8.9 / 7.9 | 0.83 | ≈ year-end 2016–2017 yields |
| 57.75 (−30%) | 6.1% | 7.8 / 6.9 | 0.72 | ≈ end-2025 (58.25, yield 6.0%) |
| 50.00 | 7.0% | 6.8 / 6.0 | 0.63 | ≈ end-2023/2024 |

- Niwes' only price numbers: PE <10 (P3, weak evidence) — passes on TTM, fails on FY2025; "ราคาเหมาะสม" (P4) has no number. Our 25% rule says expensive. ttb itself trades at PBV 1.10 / yield 5.1% (0.149 ÷ 2.92, Y) — the bank is **not** cheaper than its holding today.

## 8. น้ำหนัก 12.5% ตัวเดียว

- TCAP 12.5% of plan + BBL 22.5% = 35% in Thai-bank-linked earnings (rebalance.py TARGETS), plus TISCO off-plan. The two banks share the macro (rates, loan growth, BoT caps) but not the business: BBL = corporate/international, ttb = retail/auto, THANI = trucks, TNI = non-life. Art keeps the weights (NP F1 note 2026-10-19) — nothing here changes that; D17 only states the overlap.

## 9. สิ่งที่ algo ควรเตรียมให้ครั้งหน้า / data issues found

| # | Item | Found this round | Fix / note for the head |
|---|---|---|---|
| 1 | FS cache EPS FY2019 **7.03** vs company **9.43** (AR19 p13) · FY2020 **6.12** vs **6.26** (OR p66) | yearly_metrics (thaifin/SETSMART) | affects A5/A12/A3 5-yr window (3.8% vs 3.4%); cache cell check per DC-3 |
| 2 | FS "revenue" 18,718 (2025) ≠ company revenue 24,809 (SN) | different definition in cache | label the A5 column for holdings/banks or map to "รายได้จากการดำเนินงาน" |
| 3 | `data/manual_facts/TCAP.json` written (bank table, policy, founding year, parent cash/debt) — **data/ is git-ignored** (`.gitignore` line 5), so it lives only on this machine | FS prints it under "ต้องกรอกมือ" once present | re-run `fact_sheet.py TCAP --refresh --cost TCAP=59.80` after config changes |
| 4 | normal_eps + growth_scenarios proposed below — not written to config.json (head's job) | — | after writing, `--refresh` so the day-cache is rebuilt (fetch_data checks normal_eps_applied) |
| 5 | SET listing year not found | OR p22, history page | leave null; ask IR if needed |
| 6 | FS A4 DCA table only covers the config scenarios — new 1.5 / 7% rows appear after config update | — | — |

## 10. จุดที่ของเดิมใน `research/tcap-deep-dive-2026-10-09.md` ผิด / เก่า

| Old book (RS) said | Now | Source |
|---|---|---|
| Buyback "ถ้าทำครบ ... DPS +11%" treated as likely; thesis point 3 | No execution evidence 2.5 months into the window; two brokers expect redirection to dividends | Q2 BS · BRK 4 Aug / 2 Sep 2026 |
| ttb dividend to TCAP ≈ 21.8 bn shares × DPS → 2,859 mn (2025) | TCAP holds ~24.3 bn ttb shares (fair value 49,138 mn ÷ 2.02) → ~3,260 mn; actual parent dividends received (all sources) 4,384 mn | OR p322 p260 |
| "งบเฉพาะกิจการหาไม่ได้" — D10/D11 answered indirectly | Separate statements found (Q2 XLS + OR p260): parent cash-like 9.3 bn, debt 28.0 bn, dividends received 1.25x paid, DL 107% | Q2 · TRIS |
| Founding year 2523 "ยังไม่ยืนยัน" | Verified: OR p22 + company history page | OR · IR-HIS |
| "นโยบายปันผลเป็นตัวเลข: หาไม่ได้" | Policy found — deliberately has no %, wording recorded in manual_facts | OR p66 · IR-DIV |
| D13: discount ~20–25% at 77 | Listed stakes = 104% of market cap at 82.50; discount gone | Y · OR p321 |
| ttb DPS 2024 "0.120" | 0.130 (0.065 + 0.065) | Y · TTB-P p38 |
| FY2019 EPS used 7.03 (FS) | Company EPS 9.43; normal ≈ 5.36 after the 4,664 mn disposal gain | AR19 p13 p200 |
| Niwes family 30 mn shares (2.86%) | Only Niwes' 14.0 mn (1.335%) visible at 14 Sep 2026; family 8 + 8 mn below the top-10 cutoff → unconfirmed | IR-SH · S2T |
| Scenarios 2 / 4 / 5.4% set from DPS history | 1.5 / 4 / 7% set from EPS history + ttb share-count effect (section 4.1) | — |

---

## ค่าที่ต้องจดลง config

The head writes these into `config.json` (worker did not touch config.json). `special_dividends` TCAP 2019 = 4.0 stays as is (confirmed, AR19 p14).

```json
{
  "normal_eps": {
    "TCAP": {
      "2025": 7.32,
      "2019": 5.36,
      "_source": "research/tcap-deep-dive-2026-10-19.md section 3 D1 — FY2025: profit attributable 7,750 mn minus discontinued TNS operations +75 mn (One Report 2568 p145) = 7,675 / 1,048.6 mn shares; stricter alternative 6.94 also removes ~400 mn after-tax of FVTPL/investment/foreclosed-asset gains. FY2019: (10,807 − 4,664 consolidated gain on disposal of subsidiaries, annual report 2562 p200) / 1,146 mn weighted shares — pre-tax gain, tax effect not disclosed: check before use. FY2013 (EPS 7.49) also abnormal, not quantified.",
      "_as_of": "2026-10-19"
    }
  },
  "holdings.growth_scenarios": {
    "TCAP": {
      "bad": 0.015,
      "mid": 0.04,
      "good": 0.07,
      "source": "research/tcap-deep-dive-2026-10-19.md section 4.1 — EPS-based: bad = ttb profit flat/declining (2025 −1.9%, NIM 3.02%, loans −1.8% YTD), no TCAP buyback, only ttb share-count effect; mid = EPS CAGR 2020→2025 3.4% (IR 6.26→7.39) / 3.8% (FS cache), post-merger base, matches FS A3 5y 3.8% and 10y 4.8%; good = ttb cancels 10.3% treasury shares (+~11% to TCAP's share of ttb profit over ~3 yrs) + ttb profit +3%/yr + THANI/TNI growth, below the 10% ceiling. 2021→2025 10%/yr not used (COVID base, GM-1).",
      "as_of": "2026-10-19"
    }
  }
}
```

## acceptance (ไล่ทีละข้อ)
- D1–D18 all answered with fact-sheet section or external source + date: section 3 has 18 rows; every row names FS sections (A1/A3/A4/A5/A10/A12) or coded sources dated in the source table.
- D1 normal EPS FY2025 = 7.32 with what was removed (TNS discontinued +75 mn) and why; FY2019 one-off 4,664 mn identified and marked to check.
- D2 numeric year-5 DPS 3.77 / 4.26 / 4.91 from EPS-based 1.5 / 4 / 7% + obstacles listed.
- D4 / D10 use the ttb bank table (2.5) + TCAP-level cash 9.3 bn / debt 28.0 bn (2.3).
- D15 five beliefs incl. "Niwes holds TCAP", each with sourced counter-evidence and a falsifier tied to T1/T2/T3/T4.
- D16 section 6 maps every flag to a belief or a section-5.2 risk; D18 = n/a — AMATA only.
- FY2019 special 4.00 confirmed verbatim (AR19 p14) → `config.json` special_dividends unchanged.
- Owner's 7–12% target: section 4 reports numbers only, no verdict.
