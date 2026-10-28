# HMPRO deep dive 2026-10-28 — "can Art hold and DCA this every month for 10–20 years?"

- Created 2026-10-28 · ordered by Art 2026-10-28 (candidate from research/niwes-keep-or-cut-2026-10-28.md section 3) · Niwes leg · **not held — no cost basis**; all cost levels below are today's price and discounts to it
- Reference price **6.50 baht = close of 2026-10-27** (fact sheet FS; yahoo closes 9–27 Oct 2026: 6.40 / 6.40 / 6.35 / 6.35 / 6.35 / 6.30 / 6.35 / 6.35 / 6.45 / 6.50)
- Written under docs/deep-dive.md: forward growth is earnings-based on normal EPS, abnormal base years excluded, real closes only, every number has a source + date, the owner's 7–12% yield-on-cost target is a direction — section 4 reports the numbers and draws no conclusion on reaching it · no buy / sell order (R6)
- Format = research/amata-deep-dive-2026-10-19.md (10 sections + values for config + acceptance) · every Niwes reference = docs/niwes-principles.md (codes C/Q/P/F/H/X · T1–T6 · D1–D18). Niwes never spoke about HMPRO in any source we hold; every judgement here is ours on his general rules
- Labels: `number` = from figures · `person` = our judgement · `guess:` = not proven · "not found" where no source was reachable

## Source codes (used throughout)

| Code | Source | Data as of | Fetched |
|---|---|---|---|
| FS | System fact sheet reports/facts/HMPRO_2026-10-28.md (`fact_sheet.py HMPRO --refresh`, price 6.50 close 2026-10-27; re-issued after data/manual_facts/HMPRO.json was written) — A1–A12, flags | FY2025 + FY2026 interim | 2026-10-28 |
| FS2 | Same fact-sheet functions (`yoc_table`, `dca_table`, `required_growth` imported from scripts/fact_sheet.py) run with the three EPS-based scenarios of this book (−2 / +1 / +5%), years 5/10/15/20 — section 4 | FY2025 base | 2026-10-28 |
| OR | 56-1 One Report 2025 (English) https://hmpro.listedcompany.com/misc/one-report/20260309-hmpro-one-report-2025-en.pdf — 466 pages, text via pypdf (scratch C:\WORKSPACE\_desk\maxmahon\hmpro-dd-2026-10-28\files\or2025.txt); page numbers = PDF page index | FY2025 (31 Dec 2025) | 2026-10-28 |
| AGM | Notice of the 2026 AGM (10 Mar 2026) https://hmpro.listedcompany.com/misc/shareholderMTG/agm-2026/20260310-hmpro-agm-2026-notice-en.pdf — 100 pages incl. 2025 AGM minutes; dividend policy, FY2025 dividend, payout table, buyback, director biographies | 10 Mar 2026 | 2026-10-28 |
| SETS | SET Listed Company Snapshot https://lssmedia.setlink.set.or.th/2025/YE/HMPRO-YE68-ListedCompanySnapshot-EN.html and …/2026/6M/HMPRO-6M69-… — store counts, FY2025 / 1H2026 P&L, shareholders 23 Apr 2026 | 30 Jun 2026 | 2026-10-28 |
| PP | aio.panphol.com/stock/HMPRO/dividend (curl + table parse) — cash and stock dividends 2545–2569 with XD dates | 8 Sep 2026 XD | 2026-10-28 |
| SA | stockanalysis.com/quote/bkk/HMPRO/dividend — ex-dates and amounts Sep 2021 – Sep 2026 | 8 Sep 2026 | 2026-10-28 |
| Y | yahoo via yfinance (scratch hmpro_probe.py → hmpro_probe_out.txt) — annual 2022–2025, quarterly to Q2/2026, balance sheets, cash flows, dividends, splits, unadjusted closes 2015–2026, peers GLOBAL / DOHOME / CRC / ILM | 30 Jun 2026 · price 27 Oct 2026 | 2026-10-28 |
| SC | Screener cache data/screener_cache/2026-10-28/HMPRO.BK.json (`yearly_metrics`, thaifin/SETSMART) — revenue, net profit, EPS, OCF, capex 2010–2025 | FY2025 | 2026-10-28 |
| K1 | kaohooninternational.com/?p=577788 (2026-02-25) — FY2025 results, final DPS 0.22, XD 22 Apr 2026 | FY2025 | 2026-10-28 |
| K2 | kaohooninternational.com/?p=568681 (2025-10-28) — 3Q25 / 9M25 results, store count Sep 2025 | 3Q25 | 2026-10-28 |
| K3 | kaohooninternational.com/?p=581677 (2026-04-28) — 1Q26 results, Easy E-Receipt base effect | 1Q26 | 2026-10-28 |
| K4 | kaohooninternational.com/?p=587585 (2026-07-27, Finansia) — 2Q26 results, GPM 27.7%, SSS Jul 1–20 −1 to −2% | 2Q26 | 2026-10-28 |
| IX1 | InnovestX earnings note 2026-02-26 (innovestx.co.th cafeinvest, EN/TH) — 4Q25 SSS by format, payout 83%, buyback 2, TP 9.0 | 4Q25 | 2026-10-28 |
| IX2 | InnovestX 2026-04-29 — 1Q26 SSS HomePro −12.5% / Mega Home −4%, TP cut 9.0 → 8.0 | 1Q26 | 2026-10-28 |
| IX3 | InnovestX update 2026-10-14 — 3Q26 preview: profit ≈1.3 bn flat YoY, SSS HomePro −2.8% / Mega Home −0.5%, GPM 27.2%, TP 8.2 | 3Q26 preview | 2026-10-28 |
| IX4 | InnovestX 2025-03-06 (EN 2025-05-09) and 2024-03-06 — company guidance for 2025 (SSS +2–3%, 12 stores, capex 7–8 bn) and 2024 (SSS +3%, sales +7–8%) | guidance | 2026-10-28 |
| KS | Kasikorn Securities note 2026-08-05 via hoonvision.com/?p=215485 — 2026 guidance: revenue flat, SSSG ≈ −3%, GPM +70–100 bps, capex 6–7 bn, 1 new store + 6 renovations in 2H | 2026 | 2026-10-28 |
| IR | insideretail.asia 2026-04-01 "Why are Thailand's DIY giants losing momentum?" — 2025 revenue / SSS for HomePro, Thai Watsadu, Global House, MR DIY | FY2025 | 2026-10-28 |
| DIY | diyinternational.com 2025-02-28 and 2025-04-07 — 2024 revenue of HomePro / Global House / Dohome, household debt 90.8% of GDP | FY2024 | 2026-10-28 |
| KR | Krungsri Research: construction materials 2026–2028 (2026-07-09) and modern trade 2026–2028 (2026-04-30) | 2026 | 2026-10-28 |
| KEN | kenresearch.com Thailand home improvement market (Aug 2026) — USD 15.5 bn 2025, CAGR 4.8% — marketing estimate, low weight | 2025 | 2026-10-28 |
| WS | Web-search snippets only (page not opened): TRIS AA- Stable (trisrating.com 403); buyback program 2 (bangkokbiznews 2026-01-27); Thai Watsadu 2024 sales ≈40 bn, 103 stores; MR DIY 2025 revenue 20.1 bn +24%; Oct-2026 new billing +10% (IX3 snippet) | — | 2026-10-28 |

Unreachable this round: trisrating.com (403) · Krungsri PDF of the home-improvement sub-segment (page is qualitative only) · 56-1 One Report 2024 not opened (2025 edition carries the 5-year tables) · SET API (not attempted; FS already carries set_official dividends).

---

## 1. One-page answer

**What the data says (no buy / sell order — R6; the 7–12% target is a direction, not judged here):**

1. **Yield clears the 5% rule today, for the first time in its listed history.** FY2025 DPS 0.38 ÷ 6.50 = **5.8%** (FS A10); 3-year average (0.40 / 0.43 / 0.38) 6.2%; trailing 12 months (0.22 final + 0.16 interim) 0.38 → 5.8%. Year-end yield was 2.2–2.6% in 2016–2022; it reached 5.7% at end-2025 because the price fell 58% from the 2022 close (15.50 → 6.65) while the dividend stayed roughly flat — the yield came from the price, not from dividend growth.
2. **The dividend is paid from normal profit, at a high payout.** FY2025 EPS 0.46 reported = **normal EPS 0.46** — no disposal gain, no write-off, FX/derivative items < 10 million baht (OR p.407). Payout 83% of consolidated EPS (81–85% every year since 2022, company's own table in AGM p.4) against a policy floor of 40%. The 40% floor is far below what is paid, so a profit fall would be absorbed by cutting the payout ratio only if the board chose to — it has instead cut the DPS with profit (2020 −21%, 2025 −12%).
3. **Earnings have been flat for six years.** EPS 0.47 (2019) → 0.46 (2025) = −0.4%/yr; net profit 6,177 → 6,011 million; sales revenue 65,253 → 67,888 (+0.7%/yr) while the store count went 114 → 133 (+17%) — so sales per store fell. 10-year window 2015 → 2025 shows 5.5%/yr only because 2015–2019 was the expansion era (EPS 0.27 → 0.47). The 2024 → 2025 step was −6% (revenue −2.8%, HomePro same-store sales ≈ −6.4%).
4. **The last four quarters: no growth, better margin.** 3Q25 −9.6% · 4Q25 −7% · 1Q26 **−17.8%** (Easy E-Receipt base) · 2Q26 **+14.0%** (GPM 27.7% vs 25.8%) · 1H26 −3.5% (2,998 vs 3,106 million) · 3Q26 due ~end-Oct 2026, brokers expect ≈1.3 bn flat YoY, SSS −2.8% (IX3) · company guides 2026 revenue flat, SSSG ≈ −3%, GPM +70–100 bps (KS). The FY2026 interim DPS was held at 0.16; the T1 question (two consecutive DPS cuts) is decided by the final dividend in Feb–Mar 2027.
5. **Growth levers are thin.** New stores 1–2 a year in 2026 (vs 10 in 2025, 12 planned); Malaysia frozen at 7 stores since 2014 ("profitable but on tax losses", expansion paused — OR p.318, AGM minutes); Vietnam online closed 2024; Mega Home is the only format with flat-to-positive SSS; online 8.25% of sales (OR p.67). The industry (HomePro + CRC hardline + Global House + Dohome ≈ 203 bn baht revenue in 2025) has contracted or stalled three years running; the one grower is MR DIY small-box (+24% to 20.1 bn, WS).
6. **Scenarios (ours, EPS-based, section 4.1): bad −2% / mid +1% / good +5%.** At today's price the mid case gives a lump yield on cost of 6.5% in year 10 and 7.1% in year 20; new monthly DCA money (price flat) 6.5% / 7.1%; bad case slides from 5.3% to 3.9% by year 20; good case reaches 9.5% (lump, year 10). The gap between bad and good is decided by whether same-store sales turn positive again — nothing in the 2023–2026 data shows that yet.
7. **Balance sheet: clean for a retailer, not debt-free.** Interest-bearing debt 25.6 bn = 0.98× equity including 7.1 bn of TFRS16 leases, 0.71× without (OR p.314); TRIS AA- (WS); total liabilities / equity 1.71 (FS A6, identity holds). But 2025 was the first year since 2022 in which OCF − capex (5,276 million) did not cover the dividend (5,363) plus the buyback (1,355): cash fell 5,554 → 4,488 million and net debt rose 11.1 → 14.0 bn (Y). 1H2026 repeats the pattern (FCF 2,538 vs dividend 2,850 + buyback 381; cash 1,700 million).

**Decisions left to Art + head:** (a) accept −2 / +1 / +5% as the scenarios (section 4.1) or set others; (b) whether a 5.8% yield on a flat-earnings business with an 83% payout is the kind of "ordinary business that pays 5%" Niwes describes (C1, C10) or a value trap — the data supports either reading, section 5A lists what would decide it; (c) if it enters, what it replaces or dilutes (section 8 — it would be the first consumer / retail name beside AMATA, BBL, TCAP); (d) the cheap-ladder levels in section 7 if the cash-ammo step (F5) is extended to it.

---

## 2. Fact sheet

### 2.1 Dividend per share by fiscal year — three sources compared (PP vs SA vs yahoo/set_official in FS A1)

Method: interim (XD Sep of year N) + final (XD Apr of N+1) = FY N. HMPRO pays twice a year; XD dates are the same in all three sources for 2021–2026.

| FY | DPS | YoY | Composition and agreement | EPS (consolidated) | Payout |
|---|---:|---:|---|---:|---:|
| 2015 | 0.25 | — | PP 0.10 (XD 7 Sep 15) + 0.15 (12 Apr 16) · yahoo 0.10 + 0.15 ✓ · FS A1 0.25 ✓ | 0.27 | 94% (first full-cash year after stock dividends — base is odd, see note) |
| 2016 | 0.27 | +8% | 0.12 + 0.15 ✓ PP / yahoo / FS | 0.32 | 85% |
| 2017 | 0.31 | +15% | 0.13 + 0.18 ✓ | 0.37 | 84% |
| 2018 | 0.35 | +13% | 0.15 + 0.20 ✓ | 0.42 | 83% |
| 2019 | 0.38 | +9% | 0.17 + 0.21 ✓ | 0.47 | 81% |
| 2020 | 0.30 | **−21%** | 0.10 (8 Sep 20) + 0.20 (22 Apr 21) ✓ — COVID interim cut | 0.39 | 76% |
| 2021 | 0.32 | +7% | 0.12 + 0.20 ✓ PP / SA / yahoo / FS (set_official) | 0.41 | 78% |
| 2022 | 0.38 | +19% | 0.17 + 0.21 ✓ · AGM p.4 prints 0.38, payout 82.99% | 0.47 | 81% |
| 2023 | 0.40 | +5% | 0.18 + 0.22 ✓ · AGM 0.40, payout 85.19% | 0.49 | 82% |
| 2024 | 0.43 | +7% | 0.18 (10 Sep 24) + 0.25 (22 Apr 25) ✓ · AGM 0.43, payout 81.55% | 0.49 | 88% |
| 2025 | **0.38** | **−12%** | 0.16 (10 Sep 25) + 0.22 (22 Apr 26, paid 7 May 26) ✓ PP / SA / yahoo / FS / K1 / IX1 · payout 83% (IX1) | 0.46 | 83% |
| 2026 interim | 0.16 | flat vs 0.16 | XD 8 Sep 26, paid 22 Sep 26 (PP, SA, yahoo) · **incomplete year, not compared with full years** | 1H 0.23 (vs 0.24) | — |

Note on FS A1 before 2015: FY2009–FY2014 dividends were paid mainly as **stock dividends** (ratios 10:1 to 15:1 per PP) with 0.01–0.02 baht cash for withholding tax; yahoo's split-adjusted cash series (cumulative factor 6.62× over the ten stock dividends 2009-10-12 … 2015-04-17, Y) therefore shows "−81%" in 2010 and "−70%" in 2012 that are not cash cuts, and the FS A2 lines for 2010 / 2012 and the A3 15-/20-year dividend CAGRs (24.6% / 16.9%) are artefacts of that series. **Usable cash-dividend history = FY2015–FY2025 (11 years).** Cash dividend paid in total (OR p.408): 2024 5,259.7 million · 2025 5,362.8 million.

Dividend CAGR by window (cash era): FY2015 → 2025 4.3%/yr (base = first full-cash year at 94% payout) · FY2019 → 2025 **0%** (0.38 → 0.38) · FY2020 → 2025 4.8% (COVID base, not usable). Forward rates in section 4 are earnings-based anyway.

### 2.2 Revenue, profit, cash (million baht)

Net profit = attributable to owners (no minorities — Y "Minority Interests" 0). EPS: SC `diluted_eps` matches OR p.406 for 2024–2025 (0.49 / 0.46); earlier years are SC, checked against net profit ÷ 13,151 million shares (e.g. 2019: 6,177 ÷ 13,151 = 0.470 ✓, 2015: 3,499 ÷ 13,151 = 0.266 ✓ — share count has been constant at 13,151 million since the last stock dividend in 2015).

| Year | Sales revenue (SC) | Total revenue (OR) | Net profit | EPS | OCF | capex | OCF − capex | Dividend paid | Buyback | Cash (yr-end) | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2015 | 53,990 | — | 3,499 | 0.27 | 6,893 | 4,886 | 2,007 | ~3,288 est | — | 2,698 | first full-cash dividend year |
| 2016 | 58,634 | — | 4,125 | 0.32 | 7,005 | 4,969 | 2,037 | ~3,551 est | — | 3,721 | |
| 2017 | 61,785 | — | 4,886 | 0.37 | 7,526 | 3,233 | 4,293 | ~4,077 est | — | 2,505 | |
| 2018 | 63,556 | — | 5,613 | 0.42 | 8,725 | 2,870 | 5,855 | ~4,603 est | — | 6,238 | |
| 2019 | 65,253 | — | 6,177 | 0.47 | 8,375 | 3,017 | 5,359 | ~4,997 est | — | 2,860 | peak EPS before COVID |
| 2020 | 59,874 | — | 5,155 | 0.39 | 8,363 | 3,145 | 5,218 | ~3,945 est | — | 3,283 | COVID: revenue −8%, EPS −16%, DPS −21% |
| 2021 | 61,791 | — | 5,441 | 0.41 | 7,825 | 1,673 | 6,152 | ~4,208 est | — | 4,546 | |
| 2022 | 66,811 | 69,389 | 6,217 | 0.47 | 9,952 | 5,587 | 4,365 | 4,866 | — | 5,420 | |
| 2023 | 70,166 | 72,822 | 6,442 | 0.49 | 9,792 | 5,231 | 4,562 | 5,129 | — | 6,429 | record revenue |
| 2024 | 69,806 | 72,577 | 6,504 | 0.49 | 10,153 | 3,711 | 6,442 | 5,260 | 0 | 5,554 | record profit; revenue −0.3% |
| 2025 | 67,888 | 70,570 | 6,011 | 0.46 | 9,337 (Y) / 9,055 (SC) | 4,061 | 5,276 (Y) / 4,994 (SC) | **5,363** | **1,355** | 4,488 | revenue −2.8%, profit −7.6%; net debt 11.1 → 14.0 bn |
| 1H2026 | 32,962 (contracts) | 35,213 | 2,998 (−3.5%) | 0.23 | 4,466 | 1,928 | 2,538 | 2,850 | 381 | 1,700 (30 Jun) | Q1 −17.8%, Q2 +14.0% (Y, SETS, K3, K4) |

"est" = DPS × 13,151 million shares (FS A7 method). Depreciation 3,583 million in 2025 (Y) — capex 4,061 is barely above depreciation, i.e. 2025 capex was mostly maintenance plus the 10 new (mostly small hybrid) stores. Gross margin 27.6% (2025), 28.0% (1H26), SG&A 19.6% of revenue (2025); operating margin 11.9% → 11.9%; interest expense 711 million (Y).

Quarterly net profit (Y, K2–K4): 3Q24 1,442 · 1Q25 1,707 · 2Q25 1,399 · 3Q25 1,304 · 4Q25 1,602 · 1Q26 1,404 · 2Q26 1,594 — 9M25 4,410 (−7.7%). **Correction to research/niwes-keep-or-cut-2026-10-28.md section 3:** the "Q2/26 1,594 vs 1,707 (−7%)" line compared Q2/26 with **Q1/25**; the true YoY is +14.0% (vs Q2/25 1,399) — section 10.

### 2.3 Stores, same-store sales, sales mix (the "is there growth left" table)

| | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 so far | Source |
|---|---:|---:|---:|---:|---:|---:|---|
| Stores (company count, hybrids counted once) | 114 | 116 | 126 | 129 | **133** | 134 (Jun) | OR p.14, p.19 · SETS |
| of which Malaysia | 7 | 7 | 7 | 7 | 7 | 7 | OR p.14 (no new store since 2014) |
| New stores opened | — | 2 | 10 | 8 (IX4 2025-03 "8 in 2024") | 10 (2 HomePro, 1 Mega Home, 7 hybrid), 1 closed | 1 + 6 renovations planned 2H (KS) | OR p.19 · KS |
| Company plan at start of year | — | — | — | 7–8 stores, SSS +3%, sales +7–8% (IX4 2024-03) | 12 stores, SSS +2–3%, sales +5–7%, capex 7–8 bn (IX4 2025-03) | revenue flat, SSSG ≈ −3%, capex 6–7 bn (KS) | — |
| Delivered | — | — | — | revenue −0.3%, profit +1% | revenue −2.8%, profit −7.6%, **SSS HomePro ≈ −6.4%** (IR) · 4Q25 HomePro −8% / Mega Home −7% (IX1) | 1Q26 HomePro −12.5% / Mega −4% (IX2) · 2Q26 slightly negative · 3Q26F −2.8% / −0.5% (IX3) | — |
| Sales per store (sales revenue ÷ stores, million) | 542 | 576 | 557 | 541 | **510** | — | computed (SC ÷ OR) |
| Online share of sales | — | — | — | — | 8.25% | — | OR p.67 |
| Mix 2025: HomePro ≈ 80% · Mega Home ≈ 17% · Malaysia ≈ 3% of sales | | | | | | | IX1 · guess: Malaysia residual |
| Other income 2025: 4,615 (6.5% of total) incl. rental (Market Village malls) 1,932 (+4.2%) | | | | | | | OR p.67, p.311 |

Reading: three straight years of plans for +3% same-store growth delivered −0.8% (2024, IX4 2025-03 snippet), ≈ −6% (2025) and ≈ −3% (2026 guide). The store count grew 17% in four years while sales grew 10% — the network is being filled with smaller hybrid boxes in secondary towns, and each new store now adds less than an average old one. Malaysia is a frozen 7-store business (non-current assets 148 million vs Thailand 47,648 million, OR p.450).

### 2.4 Debt vs peers (30 Jun 2026 unless noted, million baht, Y)

| | HMPRO | GLOBAL | DOHOME | CRC (parent of Thai Watsadu) | ILM | Source |
|---|---:|---:|---:|---:|---:|---|
| Total debt incl. leases | 23,953 | 8,384 | 16,754 | 115,176 | 4,213 | Y |
| of which lease liabilities | 7,059 | 1,102 | 920 | 37,792 | 3,349 | Y |
| Parent equity | 25,872 | 26,004 | 13,954 | 66,417 | 6,435 | Y |
| Debt / equity incl. leases | **0.93** | 0.32 | 1.20 | 1.73 | 0.65 | computed |
| Debt / equity ex leases | **0.65** | 0.28 | 1.13 | 1.17 | 0.13 | computed |
| Total liabilities / equity | 1.61 (SETS 1H26) · 1.71 (FY25, FS A6) | 0.48 | 1.49 | 2.64 | 1.10 | Y · FS |
| Cash | 1,700 | — | — | — | — | Y |
| Net debt | 15,194 (vs 9,883 end-2022) | — | — | — | — | Y |
| Company definition IBD/E ex-lease | 0.71 (2025) · 0.62 (2024) · 0.70 (2023) | | | | | OR p.314 |
| Credit rating | TRIS AA- Stable (WS, not opened) | | | | | |
| ROE 2025 · net margin | 22.7% · 8.5% | 9.9% (ROE, Y) · 6.2% | 5.6% · 2.1% | 12.4% · 3.2% | 12.1% · 7.6% | Y, SETS |

FS A6 identity: 44,551 liabilities + 26,097 equity = 70,648 = total assets (Y, OR) — no ⛔ row. Debt is mid-pack (above GLOBAL, below DOHOME / CRC), with 28% of it being store leases. Current debt 7,231 + debentures maturing (6,700 current at end-2025, OR p.403) vs cash 1,700 — the group refinances continuously (2025: issued 19.5 bn, repaid 18.6 bn, Y) — normal for an AA- issuer, but it means the dividend is not sitting in a cash pile (T4 / D10).

### 2.5 Crisis years — paid? cut how much? recovered when?

| Episode | What happened | DPS | Back to the old level | EPS path | Source |
|---|---|---|---|---|---|
| 1997 Asian crisis | Company founded Jun 1995, listed Oct 2001 — no listed history | — | — | — | OR p.65 |
| 2008–09 global crisis | Cash DPS 0.18 (FY2007) → 0.35 (FY2008) → 0.26 cash + 10:1 stock (FY2009) on the pre-stock-dividend share count; net profit before 2010 not in SC | no cash cut found (par-era numbers, not comparable) | — | EPS 2010 0.13 → 2011 0.16 (+23%) | PP · SC |
| 2011 flood | Revenue +18%, EPS +23% | stock dividends era | — | up | SC |
| 2020 COVID | Revenue −8%, EPS −16% (0.47 → 0.39) | **−21%** (0.38 → 0.30; interim cut 0.17 → 0.10) | FY2022 (2 years) | 0.47 → 0.39 → 0.41 → 0.47 | PP · SC |
| 2023–26 consumer slump | Revenue −0.3% / −2.8%, EPS 0.49 → 0.49 → 0.46 | **−12%** (0.43 → 0.38) FY2025 | not yet (FY2026 interim held at 0.16) | 2026 1H −3.5% | PP · K1 · SETS |

Cash dividends paid every year since listing (FS A1: 24 years incl. the token-cash stock-dividend years). Two real cuts in the cash era, both ≥10% (2020, 2025), neither two years running yet. T1 (two consecutive cuts) has **never** triggered in the cash era; it is live for FY2026.

---

## 3. D1–D18 one by one

Labels: `number` / `person` / `number+person` · confidence high = 2+ sources agree.

| # | Answer | Figures, evidence, source + date | Label | Conf. |
|---|---|---|---|---|
| D1 yield ≥5%? paid from normal profit? | **Yes: 5.8%** (0.38 ÷ 6.50) · 3-yr average 6.2% · TTM 0.38 → 5.8% · **Paid from normal profit**: FY2025 EPS 0.46 reported = normal 0.46 — P&L carries no disposal gain, no impairment, FX/derivative items < 10 million (OR p.407); 2025 earthquake / flood / stimulus-cut effects are ordinary retail conditions, not stripped · A5 jump years: none (EPS moved within −16% / +20% every year since 2015) · No LOSS year · payout 83% | FS A10 A12 · OR p.406–407 · AGM p.4 | number+person | high |
| D2 year-5 dividend ≥5% of today's price? | **Yes in all three cases.** Base FY2025 DPS 0.38, payout held at 83%, EPS growth −2 / +1 / +5% → FY2030 DPS **0.343 / 0.399 / 0.485** = 5.3% / 6.1% / 7.5% of 6.50 (FS2) · needs only −1.0%/yr to stay at 5% of 6.50 in year 5 · Confidence rests on: 133 stores, no.1 profit in the sector, 83% payout, AA- · Obstacles: SSS negative since 2024, store additions down to 1–2/yr, industry flat, MR DIY and CRC taking share in small-box and contractor segments · C2 flag ✅ off in the mid case | FS2 · section 2.3 | number+person | medium |
| D3 (yield 2–3%) rising dividends? | Not the entry route — yield is 5.8% (C1). For the record: DPS rose FY2015–19 and FY2020–24, fell 2020 and 2025; payout stable 81–88% so the rises were earnings, not payout widening (A12) — the opposite problem: there is almost no payout room left (section 4.1) | FS A1 A12 | number | high |
| D4 if business dips, can the dividend hold? | EPS can fall **17.4%** before payout hits 100% (FS A5 tail) · worst real EPS drops: 2020 −16%, 2025 −6%, 1Q26 −18% (quarter) — a 2020-size year would put payout at 99% · cash 4,488 million (end-2025) covers **0.8 year** of the dividend with zero profit (FS); 1,700 million at 30 Jun 2026 (Y) · the board cut DPS in both dips rather than run payout up · OCF 9.3 bn vs dividend 5.4 bn: the dividend is covered 1.7× by operating cash before capex, so a hold is possible if capex is cut (2025 capex ≈ depreciation) | FS A5 · Y · OR p.408 | number+person | high |
| D5 revenue / profit / dividend streaks, where they broke, why | Sales revenue up 12 of 15 years; broke 2020 (COVID) and 2024–25 (two years: −0.3%, −2.8%) · EPS up 2015–2019, broke 2020, up 2021–2023, flat 2024, down 2025 · DPS broke 2020 and 2025 · Cause 2024–25 = same-store sales (−0.8%, ≈ −6%) from household debt ≈ 90% of GDP (DIY), weak housing, stimulus threshold cut, floods · **temporary or permanent: not decidable yet** — three years of falling SSS with a growing store base is the longest soft patch in the cash era; 2026 guide is −3% again | SC · OR p.14 · IR · DIY · KS | number+person | high (facts) · low (temp/perm) |
| D6 how old, how big | Founded **27 Jun 1995** (LH + QH joint venture) · public company 29 May 2001 · listed SET **30 Oct 2001** (OR p.65) → 31 years / 25 listed · dividends every year since FY2002 (FS A1, 24 years) · market cap **85.5 bn** at 6.50 (SC) vs GLOBAL 38.9 bn, DOHOME 12.4 bn, CRC 200.5 bn, ILM 6.8 bn (Y) · written to manual_facts | OR · FS · Y | number | high |
| D7 does management look after shareholders? | Policy: "pay out at least 40% of its annual net profit" (OR p.331; AGM p.4 says "not less than 40%", measured on the separate statements) · paid 81–88% every year 2015–2025 (A12; company table 82.99 / 85.19 / 81.55% for 2022–24) — more than double the floor, consistently · buybacks: 1,355 million (1.37%) in 2025, up to 2,959 million (3%) Mar–Aug 2026 — funded while FCF < dividend, i.e. with debt (section 2.2) · control: Land and Houses 30.23% + Quality Houses 19.87% = **50.10%**; Chairman Anant Asavabhokhin (74, LH founder) absent from the 2026 AGM; Executive Chairman Khunawut Thumpomkul (director since 2001, 1.08%); MD Weerapun Ungsumalee, 63 (OR p.329, p.50; AGM p.35) · related-party flows: provident fund managed by LH Fund Management (OR p.450); store sites / malls with LH-QH not quantified here — not found · SEC search on Anant / Niti / Khunawut: nothing found (search-level, DC-4) · deals that hurt minorities: none found in the sources opened · dilution: none since the 2015 stock dividend (13,151 million shares constant) | OR · AGM · WS | person | medium |
| D8a is the industry declining? (industry numbers) | **Flat-to-down for three years, not collapsing.** Big-box revenue (million baht): HMPRO 66,811 (2022) → 67,888 (2025) +0.5%/yr · GLOBAL 35,270 → 31,601 **−3.6%/yr**, profit 3,487 → 1,964 · DOHOME 31,321 → 29,110 −2.4%/yr · CRC hardline (Thai Watsadu) ≈ 72 bn in 2025, SSS −5% (IR); Thai Watsadu 2024 ≈ 40 bn (WS) · MR DIY 2025 20.1 bn **+24%**, ~900 stores (IR, WS) · HomePro SSS 2025 ≈ −6.4%, Global House "mid-single-digit" decline (IR) · drivers named by all sources: household debt 90.8% of GDP (Q1 2024, DIY), weak housing, stimulus cuts, floods · forecasts: Krungsri construction-materials retail "flat or limited growth in 2026, gradual improvement 2027–28" (KR 2026-07-09); modern trade +1.5–2.5% (2026), +3–3.5% (2027–28) (KR 2026-04-30); Ken Research 4.8% CAGR 2025–32 (KEN, marketing estimate) · HMPRO's own revenue −2.8% is the first signal already in | Y · IR · DIY · KR · KEN | person | medium |
| D8b what disrupts it easily, already happening? | Small-box convenience hardware (MR DIY 900 stores, +24%) — **happening**, takes the low-ticket basket · CRC's capital behind Thai Watsadu (88 big stores, 3–5/yr) — happening, matched HMPRO's revenue in 2025 · online marketplaces (Shopee / Lazada) for appliances and soft line — happening; HMPRO online 8.25% of sales (OR) · contractor channel: Global House / Dohome / Mega Home price war on steel and cement — happening (steel price the one deflating line, IX3) · housing cycle: new-home completions feed appliance/fit-out demand; property "worst year in nearly a decade" (nationthailand snippet, unverified) · regulation: none found that targets the format · technology: none beyond online | IR · WS · OR · IX3 | person | medium |
| D9 market leader? why can't rivals catch up? | **No.1 by profit, tied no.1 by revenue.** OR p.71: "leadership with the highest market share in the industry" (company claim) · 2025 revenue 70.6 bn vs CRC hardline ≈ 72 bn (IR) — revenue lead is gone; profit 6,011 vs GLOBAL 1,964, DOHOME 601 (Y) — margin lead intact (net 8.5% vs 6.2% / 2.1%) · moat = 126 Thai sites incl. owned land (fixed assets 47.5 bn net, OR p.72), private brands (21% of sales targeted 25%, IX4), Chang HomePro service, vendor support income 4.6 bn/yr · not a Niwes Q2 monopoly — four national chains plus MR DIY | OR · IR · Y | person | medium |
| D10 cash ample? | **No — adequate only with continuous refinancing.** Cash 1,700 million vs current debt 7,231 million (30 Jun 2026, Y); end-2025 cash 4,488 vs current debt 12,730 incl. 6,700 debentures (OR p.403) · OCF − capex 2022–25 = 20,645 million vs dividends 20,618 million = **1.00×** (Y) — every baht of free cash goes to the dividend; the 1,355 million buyback and 2026 program 2 are debt-funded · OCF / net profit 1.55× (2025), inventory 15.2 bn = 113 days of COGS (Y) · TRIS AA- | Y · OR | number | high |
| D11 low debt vs industry? | Debt / equity incl. leases 0.93 vs GLOBAL 0.32, DOHOME 1.20, CRC 1.73, ILM 0.65 (Y) — mid-pack; ex-lease 0.65 (company 0.71) · total liabilities / equity 1.71 (FY25) not up 3 years running (1.69 → 1.70 → 1.60 → 1.71) · T6 ✅ (FS) · net debt +5.3 bn since end-2022 while profit flat — direction is up | Y · FS A6 · OR p.314 | number | high |
| D12 crises 2008 / 2020: paid? cut? recovered? | 2008–09: paid (cash 0.35 FY2008, then stock dividends — par-era, not comparable) · 2011 flood: no cut, EPS +23% · 2020: cut 21%, back in 2 years · 2025: cut 12%, not yet back · section 2.5 | PP · SC | number | high (2020) · low (2008) |
| D13 hidden assets? | Investment properties (Market Village malls, rented space): book 4,492 vs fair value **9,910** million (OR p.432) → ≈5.4 bn pre-tax ≈ **0.42 baht/share** (6% of price) · store land and buildings carried at cost 85.5 bn gross / 47.5 bn net (OR p.72) — 126 Thai sites bought over 30 years: **guess:** worth more than book, not quantified · OneStockHome 30% stake (OR p.65) — size not found · no listed subsidiary | OR | number+person | low |
| D14 is today's price reasonable? | PE **14.1** on FY2025 EPS 0.46 (FS) · 14.4 TTM (Y) · year-end PE 2016–25: 32.3 · 34.6 · 36.2 · 34.2 · 34.8 · 35.4 · 33.0 · 23.9 · 19.2 · 14.5 (FS A10) — lowest of its own decade, still not < 10 (P3, weak evidence) · PBV 3.44 on FY2025 BVPS 1.89 (FS) / 3.23 on 2.01 (Y) — lowest of own range 3.52–10.94 · yield 5.8% = 100th percentile of own year-end yields → FS label **cheap vs itself** · 52-week 5.80–7.50 → 41% of the range; 10-year low close 5.80 (2025) · peers: GLOBAL PE 14.8 / PBV 1.50 / yield 2.7%; DOHOME 16.8 / 0.89 / 0.1%; CRC 24.3 / 3.02 / 1.6%; ILM 8.9 / 1.06 / 7.5% (Y) · brokers (not Niwes): InnovestX 8.2 (Oct 26), Finansia 7.70, KS 7.30 · a 20–30% drop = 4.55–5.20 → yield 7.3–8.4%, PE 9.9–11.3 | FS A10 · Y · IX3 · K4 · KS | number+person | high |
| D15 what do we want to believe? | Table in section 5A (5 beliefs, each with counter-evidence + falsifier tied to a T flag) | — | person | — |
| D16 "wrong-track" flags for this stock | Section 6: T1–T6 defined for a big-box retailer, each mapped to a D15 belief; current state: T1 ⚠ 1 of 2 (FY2025 cut) · T2 ✅ at today's price in mid (6.5% < 7% → **⛔ by the system's 7% line**) · C2 ✅ · T3 ⚠ normal EPS down 1 year · T4 ⚠ 1 of 2 (2025 FCF < dividend + buyback, cash down) · T5 watch · T6 ✅ | FS2 · section 6 | number+person | — |
| D17 good enough to add? what concentration grows? | Not held. The Niwes leg today = AMATA 35% (industrial estate) + BBL + TCAP (banks). HMPRO would be the first consumer-retail name — a different earnings driver (household spending) from FDI (AMATA) and rates (banks). Overlap: LH / QH control = exposure to the Thai housing cycle, which also moves AMATA's land and the banks' mortgage books — same macro, different mechanism. Art does not use the 5-stock / 5-industry rule (2026-10-19) — reported as a fact, no recommendation. What it is **not**: a growth stock; the case rests on 5.8% today + a flat-to-slightly-rising dividend, which is exactly the C1 "ordinary business paying 5%" picture and exactly what a value trap looks like from the outside — section 5A says what tells them apart | config holdings · section 5A | person | — |
| D18 (AMATA-specific) | Not applicable. The HMPRO-specific hard question is "is same-store growth gone for good" — answered under D5 / D8 and tested by T3 / T5 in section 6; FS A3 5-/10-year EPS CAGRs (3.2% / 5.6%) were re-checked: both use normal bases (2020 COVID is **not** the 5-year base — FS 5-year window runs FY2020 → 2025 = 3.2%, flattered by the COVID base; FY2019 → 2025 = −0.4% is the honest 6-year figure) | SC · section 4.1 | number+person | high |

---

## 4. Dividend vs cost — facts only (target 7–12% is a direction; no verdict on reaching it)

### 4.1 Earnings-based growth scenarios (ours, not Niwes; for Art to confirm → `holdings.growth_scenarios`)

Rule applied (deep-dive.md): forward growth = normal EPS growth; payout held at today's 83% (room to raise is 17 points — one-off, not growth); abnormal base years excluded. Buybacks: 1.37% in 2025 + up to 3% in 2026 shrink the share count and add roughly +1–1.5%/yr to EPS while they last — included in the mid case, not in the bad case (they stop when cash is tight).

| Window (EPS, section 2.2) | Base → FY2025 | CAGR | Base year normal? |
|---|---|---:|---|
| FY2015 → FY2025 (10 y) | 0.27 → 0.46 | **5.5%** | normal, but the window contains the 2015–19 expansion (store count 114 only by 2021; EPS +15%/yr 2015–19) — upper bound |
| FY2016 → FY2025 (9 y) | 0.32 → 0.46 | 4.1% | normal |
| FY2018 → FY2025 (7 y) | 0.42 → 0.46 | 1.3% | normal |
| FY2019 → FY2025 (6 y) | 0.47 → 0.46 | **−0.4%** | normal peak; six years of no growth |
| FY2020 → FY2025 (5 y, FS A3) | 0.39 → 0.46 | 3.2% | COVID trough — not usable |
| FY2022 → FY2025 (3 y) | 0.47 → 0.46 | −0.7% | normal |
| FY2023 → FY2025 (2 y) | 0.49 → 0.46 | −3.1% | normal → latest direction |
| Revenue 2019 → 2025 | 65,253 → 67,888 | +0.7%/yr | stores +17% in the same period |
| Industry forecast | — | 2026 flat · 2027–28 +3–3.5% | KR (modern trade / construction-material retail) |

Scenarios (per year, FY2025 base, 5–20 years):

| Case | EPS growth | Why this number | What has to be true |
|---|---:|---|---|
| Bad | **−2%** | Latest 2-year direction is −3%/yr; SSS has been negative three years; 2026 guide −3% SSS with GPM gains that cannot repeat forever; MR DIY / CRC keep taking share; buybacks stop | SSS stays ≤ −2%/yr, store additions ≤ 2/yr, GPM plateaus at ~28%, DPS drifts down with EPS at 83% payout |
| Mid | **+1%** | Six-year history −0.4% + ~1–1.5%/yr from buybacks + industry 2027–28 at +3% with HMPRO holding share; no SSS recovery assumed | SSS ≈ 0 from 2027, 2–4 stores/yr, GPM ≈ 28%, buyback continues at ~1–3%/yr, payout held 83% |
| Good | **+5%** | The 10-year window (5.5%) rerun: SSS back to +2–3% as management has guided three years running, hybrid stores mature, Mega Home grows with contractors, private brand 25% lifts GPM to 29% | positive SSS for 2+ years, revenue +4–5%/yr, no new price war, household debt eases |

None of the three uses a payout change. The 10% ceiling (ours) is not binding here.

### 4.2 Lump bought today — yield on cost = DPS of that year ÷ purchase price (FS2; no holding exists, so "cost" = price levels)

| Case | g | Year 5 (FY2030) DPS | @6.50 (today) | @5.80 (10-y low) | @5.20 (−20%) | @4.75 (ladder 3) | @3.90 (−40%) | Year 10 DPS | @6.50 | @5.20 | Year 15 DPS | @6.50 | Year 20 DPS | @6.50 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Bad | −2% | 0.343 | 5.3% | 5.9% | 6.6% | 7.2% | 8.8% | 0.310 | 4.8% | 6.0% | 0.281 | 4.3% | 0.254 | 3.9% |
| Mid | +1% | 0.399 | 6.1% | 6.9% | 7.7% | 8.4% | 10.2% | 0.420 | **6.5%** | 8.1% | 0.441 | 6.8% | 0.464 | **7.1%** |
| Good | +5% | 0.485 | 7.5% | 8.4% | 9.3% | 10.2% | 12.4% | 0.619 | 9.5% | 11.9% | 0.790 | 12.2% | 1.008 | 15.5% |

Growth needed to reach 7% / 12% of cost (FS2, base 0.38): at 6.50 — year 5: 3.7% / 15.5% · year 10: **1.8%** / 7.5% · year 15: 1.2% / 4.9% · year 20: 0.9% / 3.7% · at 5.20 — year 10: −0.4% / 5.1% · year 20: −0.2% / 2.5%. Reading: at today's price the 7% line in year 10 needs 1.8%/yr — above the mid case (1%) and below the good case; at 5.20 the 7% line needs no growth at all.

### 4.3 Monthly DCA — equal money every month for 10 years, then hold (FS2 `dca_table`; yield = dividend received in year N ÷ all money put in by then)

Two price paths as in FS A4: (a) price grows with the dividend (yield at purchase stays 5.8%) · (b) price flat at 6.50 (yield at purchase rises as DPS rises, falls as it falls).

| Case | g | Year 5: price grows / flat | Year 10 | Year 15 | Year 20 |
|---|---:|---|---|---|---|
| Bad | −2% | 5.6% / 5.3% | 5.3% / 4.8% | 4.8% / 4.3% | 4.3% / 3.9% |
| Mid | +1% | 6.0% / 6.1% | **6.1% / 6.5%** | 6.5% / 6.8% | **6.8% / 7.1%** |
| Good | +5% | 6.6% / 7.5% | 7.6% / 9.5% | 9.6% / 12.2% | 12.3% / 15.5% |

Average purchase yield needed for the year-10 dividend to reach 7% / 12% of money invested (FS2): bad 8.57% / 14.69% · mid 6.34% / 10.86% · good 4.30% / 7.37% — against 5.85% at today's price. In the bad case "price grows with the dividend" means the price **falls** 2%/yr, which is why (a) is above (b) there.

### 4.4 Numbers still unknown that would move the answer
- 3Q26 result (due ~end-Oct 2026; 3Q25 was released 28 Oct 2025) and whether 4Q26 is the "best quarter of the year" brokers expect (IX3) — decides if FY2026 EPS lands above or below 0.46 (T3)
- FY2026 final dividend (Feb–Mar 2027): ≥ 0.22 keeps DPS at 0.38 (T1 stays at one cut); < 0.22 = two consecutive cuts (T1 lit)
- 2027 store plan and the result of buyback program 2 (how many of the 394.5 million shares were bought by 31 Aug 2026 — treasury was 242.9 million at 30 Jun, Y)
- Full-year 2025 SSS by format from the company (only broker / press figures found: ≈ −6.4% HomePro, −8% / −7% in 4Q)
- Related-party dealings with LH / QH (site leases, services) — One Report section "Internal Control and Related Party Transactions" p.386 not read this round

---

## 5. What breaks it — ordered by likelihood × damage to the dividend (all odds = `guess:`; "temporary" = dividend back within ≤3 years as in 2020; "permanent" = X1)

| # | Cause | 5-yr odds | Damage to DPS | Temp / perm | Evidence today |
|---|---|---|---|---|---|
| 1 | Same-store sales never turn positive: household debt, weak housing, ageing core customer; stores added in smaller towns dilute sales per store (542 → 510 million) | guess: 45% | DPS drifts −2 to −3%/yr with EPS (bad case) — no single cut, a slow slide | permanent if SSS < 0 for 5 years | SSS −0.8 / ≈−6 / ≈−3% 2024–26 (IX4, IR, KS); sales per store (section 2.3) |
| 2 | Share loss to MR DIY (small basket) and CRC / Thai Watsadu (big-box, deep pockets) — revenue parity reached in 2025 | guess: 40% | margin pressure once GPM gains (private brand, pricing) are used up; EPS −5–10% in a price-war year | permanent, gradual | IR · WS · IX3 (GPM is the only line improving) |
| 3 | Debt-funded dividend + buyback: FCF 1.00× dividends 2022–25, buybacks 1.4 + up to 3.0 bn on top, net debt +5.3 bn since 2022, cash 1.7 bn vs 7.2 bn current debt | guess: 35% | board trims payout from 83% toward 60–70% to protect AA- → DPS −15–25% once | temporary if earnings hold; it is the 2025 pattern plus buyback | Y · OR p.314 · section 2.2 |
| 4 | Consumer shock (COVID-type, flood, stimulus withdrawal) | guess: 30% in any 5 years | EPS −15–20% and DPS −20% for a year, as 2020 | temporary (2020: 2 years) | section 2.5 |
| 5 | Majority owners' interests (LH 30% + QH 20%): HMPRO dividends are a cash source for two property developers in a weak housing market — pressure to keep payout high even when FCF is short (#3), or to transact with the parents | guess: 25% | keeps DPS high short-term, raises #3 | — | OR p.329 · D7 |
| 6 | Malaysia / new ventures: Malaysia frozen, Vietnam online closed — expansion abroad is not a growth lever; if restarted it costs capex with no track record | guess: 20% | capex up, FCF down, no DPS effect unless large | — | OR p.65, p.318 · AGM minutes |
| 7 | Lease / rent inflation on the 28% of debt that is leases and on mall-based HomePro S units (one closed 2025 on lease expiry) | guess: 15% | margin −20–50 bps | gradual | OR p.19 · Y |
| 8 | Online disintermediation of appliances / soft line (25% of sales are soft line + appliances-heavy hard line) by marketplaces | guess: 15% beyond #2 | GPM mix worsens | permanent, slow | OR p.67 (online 8.25%) |

Normal cycle vs wrong track: normal = one DPS cut ≤ 25% with EPS still ≥ 0.40, SSS back to ≥ 0 within two years, payout ≤ 90% → Niwes "temporary, do nothing" · wrong track = DPS down two years running **and** normal EPS down two years **and** SSS still negative → X1 "adjust the portfolio". FY2026 is the test year for all three at once.

### 5A. D15 — what we want to believe, the strongest counter-evidence, and what would prove it wrong

| # | Belief (1 sentence) | Strongest counter-evidence + source + date | Falsifier (number / event → flag in section 6) |
|---|---|---|---|
| B1 | "People always fix their homes — HomePro is the everyday business Niwes means (C10), and 5.8% is a real 5% yield" | The 5.8% exists because the price fell 58% from 2022 while DPS went 0.38 → 0.38 (FS A10, 2026-10-28); the dividend itself has not grown in six years (section 2.1) | FY2026 DPS < 0.38 (**T1** two cuts) with normal EPS also down 2 years (**T3**) |
| B2 | "Same-store sales are cyclically depressed (debt, floods, stimulus) and will revert — management has guided +2–3% every year" | Three years of +3% guidance delivered −0.8% / ≈−6% / ≈−3% (IX4 2024-03, 2025-03; IR 2026-04-01; KS 2026-08-05); sales per store down 12% since 2022 while the industry's big four shrank or stalled 2022–25 (Y) | SSS (HomePro format) negative for a 4th year in FY2027 (**T3** cause = volume, **T5** industry) · industry big-four revenue down again in 2026 (**T5**) |
| B3 | "An 83% payout on 9 bn of operating cash is safe; the 40% policy floor is irrelevant" | OCF − capex covered dividends only 1.00× over 2022–25; 2025 FCF 5,276 < dividend 5,363 + buyback 1,355; cash 5,554 → 4,488 → 1,700 (Jun 26); net debt 9.9 → 15.2 bn (Y, 2026-10-28) | OCF − capex < dividends two full years with net debt rising (**T4**) · debt / equity incl. leases > 1.2 (**T6**) · payout cut below 60% in a year EPS did not fall (policy use) |
| B4 | "Leadership + private brands + Chang HomePro give a margin moat nobody can copy" | CRC hardline matched HMPRO's revenue in 2025 (≈72 vs 70.6 bn, IR); MR DIY +24% to 20.1 bn (WS); GLOBAL's profit fell 44% 2022–25 — the sector is already in a margin fight; HMPRO's GPM gain in 2026 comes partly from "elevated product prices" (IX3) that reverse | GPM below 27% for two quarters while SSS is negative (**T3** cause = margin) · revenue rank falls to no.2 for a full year (**T5**) |
| B5 | "Buybacks + 83% payout show a board that returns everything to shareholders" | Buybacks were funded with debt in a year FCF < dividend (section 2.2); LH + QH (50.1%) are the main recipients of that cash (OR p.329); Chairman absent from the AGM (AGM minutes) | buyback program 3 announced while **T4** is lit · related-party transaction with LH / QH above 1% of assets (**T6** proxy: debt rises for a non-operating reason) |

---

## 6. "Wrong-track" flags T1–T6 for a big-box home-improvement retailer (each flag → the D15 belief it watches)

| Flag | Measure | Where to read it | Value today | Open a review when | Points to "permanent" when | Watches |
|---|---|---|---|---|---|---|
| T1 DPS down how many years | Full-year DPS vs prior year (interim + final; never interim vs full year) | PP / set.or.th after the final (~Feb–Mar) | FY2025 0.38 **down 12%** (1 year) · 2026 interim 0.16 flat (⚠ FS: 1 of 2) | FY2026 < 0.38 | down 2 years running (never happened in the cash era) | B1 |
| T2 yield on cost year 10 (mid case) | DPS FY2035 ÷ purchase price with the agreed mid growth | FS A4 / FS2 | **6.5% at 6.50 < 7% → ⛔ by the system line** (target itself parked); 8.1% at 5.20 | < 7% in the mid case | < 5% even in the good case (today 9.5% — clear) | B1 |
| C2 year-5 yield on today's price | DPS FY2030 ÷ 6.50, mid case | FS A4 / FS2 | 6.1% ✅ (bad 5.3% also ≥ 5%) | < 5% in the mid case | < 5% in the good case | B1, B2 |
| T3 why did the dividend fall | (a) normal EPS two years down (b) payout cut (c) SSS by format (d) GPM | MD&A / One Report / broker notes | normal EPS 0.49 → 0.46 (**1 year down**); payout 88% → 83% (not the cause); SSS ≈ −6% (2025), −3% guide (2026); GPM 27.6% → 28.0% | normal EPS down 1 year > 10% · SSS < −3% for a year · GPM < 27% | normal EPS down 2 years · SSS negative 4 years · payout > 90% to hold DPS | B2, B4 |
| T4 paid from real cash | dividends + buybacks vs OCF − capex (full year) and net debt | Y annual / quarterly cash flow · OR p.408 | 2025: 5,276 vs 5,363 + 1,355, cash −1,066, net debt +2.9 bn (**⚠ 1 of 2**; FS A7 prints 0.9× for 2022, 2023, 2025) · 1H26 2,538 vs 2,850 + 381 | OCF − capex < dividends for a full year with net debt up (**2025 qualifies**) | 2 years running | B3, B5 |
| T5 industry | revenue of HMPRO + CRC hardline + GLOBAL + DOHOME; MR DIY growth; Krungsri retail outlook | Y annual (Feb–Mar), IR / DIY press, KR | big four flat-to-down 2022–25; MR DIY +24%; KR 2026 flat | big-four revenue down 2 years running · MR DIY > 30 bn while HMPRO flat | 3 years of falling big-four revenue with HMPRO's share falling | B2, B4 |
| T6 debt vs peers | debt / equity incl. leases vs GLOBAL, DOHOME, CRC, ILM; net debt trend | Y quarterly balance sheet | 0.93 (mid-pack) ✅ · net debt 9.9 → 15.2 bn 2022 → Jun 26 | > 1.2 and rising 2 quarters, or net debt > 2× annual FCF | > 1.5 together with T4 | B3, B5 |

Combination rule (niwes-principles section 4): T1 or T2 triggered **and** T3 / T4 / T5 pointing to permanent → open an "adjust portfolio" review · triggered but T3–T5 say temporary → hold ("do nothing" — H2) · no auto-sell · every belief has a flag and every flag a belief (B1 ← T1 T2 C2 · B2 ← T3 T5 C2 · B3 ← T4 T6 · B4 ← T3 T5 · B5 ← T4 T6).

State on 2026-10-28: T2 ⛔ (system 7% line, mid case at today's price) · T1 / T3 / T4 each at "one of two" · nothing at "permanent" yet · FY2026 results (Feb–Mar 2027) can light T1 + T3 + T4 together.

Next dates: 3Q26 results ≈ 28 Oct – early Nov 2026 (3Q25 was 28 Oct 2025) · FY2026 results + final dividend late Feb 2027 · 2027 store plan at the Feb–Mar analyst meeting · Krungsri retail outlook Q2 2027.

---

## 7. Is today's price cheap or expensive (for the cash-ammo plan — not a quality judgement)

All history = actual year-end closes, not dividend-adjusted (FS A10, Y).

| Measure | Today 6.50 (close 2026-10-27) | Own history | Reading |
|---|---:|---|---|
| PE on FY2025 EPS 0.46 | 14.1 | year-end PE 2016–25: 32.3 · 34.6 · 36.2 · 34.2 · 34.8 · 35.4 · 33.0 · 23.9 · 19.2 · 14.5 (FS A10) | lowest of own decade; not < 10 (P3, weak evidence) |
| PE on 1H26 annualized EPS ≈0.45–0.46 | ≈14 | — | no quarter-level distortion |
| PBV | 3.44 on FY2025 BVPS 1.89 (FS) · 3.23 on 2.01 (Y, Jun 26) | 3.52–10.94 (2016–25) | below the whole range — ROE 22.7% still high for PBV 3.4 |
| Yield on FY2025 DPS 0.38 | **5.8%** | 2.2–2.6% (2016–22) · 3.4% (2023) · 4.6% (2024) · 5.7% (2025) | 100th percentile → FS "cheap vs itself"; the first time above the 5% rule |
| 52-week position | 5.80–7.50 → 41% | 10-year low close 5.80 (2025); 2026 low 5.90 | lower half |
| Closes by year (low / high / Dec) | — | 2022 12.60 / 16.50 / 15.50 · 2023 11.60 / 15.80 / 11.70 · 2024 7.90 / 12.20 / 9.40 · 2025 5.80 / 9.70 / 6.65 · 2026 5.90 / 7.50 / 6.50 (27 Oct) | −58% from the 2022 close in three years |
| Peers (Y) | PE 14.4 · PBV 3.23 · yield 5.9% | GLOBAL 14.8 / 1.50 / 2.7% · DOHOME 16.8 / 0.89 / 0.1% · CRC 24.3 / 3.02 / 1.6% · ILM 8.9 / 1.06 / 7.5% | same PE as GLOBAL with 2× its yield and 2.3× its ROE |
| Broker targets (not Niwes) | — | InnovestX 8.2 (14 Oct 26) · Finansia 7.70 (27 Jul 26) · KS 7.30 (5 Aug 26) · InnovestX was 13 → 10.5 → 9.0 → 8.0 → 8.2 over 18 months | targets have followed the price down |

### Cheap levels (for the cash-ammo step if it enters the portfolio) — shaped like the F5 ladder in roadmap/agreed-portfolio-framework.md (ours, not Niwes; yields on FY2025 DPS 0.38; real closes)

| Step | Price | Yield on 0.38 | PE on 0.46 | Why this level |
|---|---:|---:|---:|---|
| 1 | **≤ 5.80** | 6.6% | 12.6 | = lowest close of the last 10 years (2025 low; 2026 low was 5.90) — "below everything the market has paid since the 2015 stock-dividend era" |
| 2 | **≤ 5.40** | 7.0% | 11.7 | yield reaches the lower edge of Art's 7–12% direction on the current dividend, with no growth needed (section 4.2: at 5.20 the 7% line needs −0.4%/yr) |
| 3 | **≤ 4.75** | 8.0% | 10.3 | PE ≈ 10 (P3 line, weak evidence) · 27% below today — the "falls another 20–30%" level we use (D14, ours) |

Guards, same as F5: shoot only when the fall is market / sentiment (SET down, peers down with it), **never** while T1 is lit (FY2026 DPS < 0.38) together with T3 pointing to permanent — a 7% yield on a dividend that is being cut is not a bargain. Each step 1/3 of the ammo. The monthly DCA (F4) is unaffected either way.

---

## 8. Fit in the plan (not held — facts for D17)

| | AMATA | BBL | TCAP | HMPRO (candidate) |
|---|---|---|---|---|
| Earnings driver | FDI land sales + utilities | NIM, loan growth, provisions | ttb dividends, buyback | household spending on home goods |
| Yield on FY2025 DPS at today's price | 3.4% (19 Oct) | ≈5.4% (keep-or-cut) | 4.4% | **5.8%** |
| Payout | 40% (floor) | ≈30–40% | — | **83%** |
| Growth case (mid) | 5% | low | low | **1%** |
| Dividend cuts ≥10% in the cash era | 6 (2006–2020) | — | — | 2 (2020, 2025) |
| Controlling holder | Kromadit 27% | — | — | LH + QH 50.1% |
| Common macro | Thai economy, property cycle | rates, credit | rates, credit | consumer debt, housing |

What HMPRO adds: a third earnings driver and the highest current yield of the four; what it does not add: growth — in the mid case the dividend is the same 0.42–0.46 baht in 10–20 years as it is now, and the result depends on the purchase price more than on the business (section 4.2: 6.5% at 6.50 vs 8.1% at 5.20 in year 10). The 83% payout means every profit dip reaches the dividend within a year; the 40% policy floor protects nothing in practice. Written for Art to weigh — no weight proposed.

---

## 9. What the system should prepare next time (found by hand this round)

| # | Item | Found in | What the script should do | Trap |
|---|---|---|---|---|
| 1 | Stock-dividend years in yahoo's series | PP vs FS A1 | mark years with `splits` events as "stock dividend — cash not comparable" and start the cash-era CAGR / A2 cut table after the last split (2015 for HMPRO) | A2 shows "−81% in 2010 / −70% in 2012" and A3 15-/20-year DPS CAGR 24.6% / 16.9% — all artefacts |
| 2 | Quarterly YoY in the keep-or-cut scan | Y quarterly | compare Q with the same quarter last year, not the previous row | "Q2/26 −7%" was Q2/26 vs Q1/25; real +14% |
| 3 | Buybacks in T4 | Y `Repurchase Of Capital Stock` | add buybacks to the dividend side of A7 / T4 (cash returned vs FCF) | 2025 looks 0.98× without the 1,355 million buyback, 0.78× with it |
| 4 | Lease split in A6 | Y `Capital Lease Obligations` | print debt / equity with and without leases and the same for peers | HMPRO 0.93 vs 0.65; DOHOME / CRC comparison changes rank |
| 5 | Total revenue vs sales revenue | OR p.67 vs SC | A5 revenue = sales (SC 67,888) while press / SET print total revenue 70,570 — label the column | −2.8% (total) vs −2.7% (sales) — small here, large for AMATA |
| 6 | SSS by format and sales per store | OR p.14 store table, broker notes | manual yearly fields: stores, SSS HomePro / Mega Home, sales per store | the single number that answers "growth left?" is not in any cache |
| 7 | Store count definitions | OR vs IX | company counts hybrids once (133); brokers count both banners (145–150) | +8% YoY store growth in IX3 is a counting artefact |
| 8 | Dividend policy + payout table + owners | AGM notice p.4, p.35; OR p.329–331 | manual_facts (done) — refresh after each AGM notice (March) | policy is on the **separate** statements' net profit |

---

## 10. Corrections to earlier notes

| # | Earlier note | This book | Type |
|---|---|---|---|
| 1 | research/niwes-keep-or-cut-2026-10-28.md section 3: "Q2/26 1,594 m vs 1,707 m (−7%)" | 1,707 is Q1/25; Q2/25 = 1,399 → Q2/26 **+14.0%**; 1H26 −3.5%, 1Q26 −17.8% | data (quarter mismatch) |
| 2 | Same table: "EPS growth 10 y (FS A3) 5.6%" and DCA y10 mid 8.0% / 10.6% (rule-based 6.1%) | 10-year 5.5% is the expansion-era upper bound; 6-year −0.4%; deep-dive mid 1% → DCA y10 6.1% / 6.5% | method |
| 3 | FS A2: 4 cuts ≥10% incl. 2010 (−81%) and 2012 (−70%) | 2 real cuts in the cash era (2020 −21%, 2025 −12%); 2010 / 2012 are stock-dividend artefacts | data |
| 4 | FS A3: DPS CAGR 15 y 24.6%, 20 y 16.9% | not meaningful (stock-dividend era); cash-era 10 y 4.3%, 6 y 0% | data |
| 5 | FS T4 "✅ not lit — 2025: 4,994 vs 5,363" | FS already shows 2025 below 1× (0.9×); with the buyback it is 0.78×; flag needs 2 years — one of two | reading |
| 6 | Keep-or-cut: "DPS down FY2025" listed as a weakness without the interim | FY2026 interim held at 0.16 (= FY2025 interim) — T1 decided by the Feb-2027 final | update |

---

## Values for config (NOT written — awaiting Art)

Head writes these into config.json (`normal_eps`, `holdings.growth_scenarios`, `special_dividends`); this job did not edit config.json. After entry run `fact_sheet.py HMPRO --refresh` so A3 / A4 / A12 pick them up.

```json
{
  "normal_eps": {
    "HMPRO": {
      "2025": 0.46,
      "2024": 0.49,
      "2023": 0.49,
      "_source": "research/hmpro-deep-dive-2026-10-28.md D1 + section 2.2: FY2025 reported EPS 0.46 (net profit 6,011.39 M, One Report 2025 p.406) with nothing stripped — no disposal gain, no impairment, FX/derivative items < 10 M (p.407); 2025 earthquake / flood / stimulus-cut effects are ordinary retail conditions, left in · FY2024 0.49 (6,503.55 M) and FY2023 0.49 (6,441.56 M) likewise clean (One Report 2025 p.14, p.406; yahoo annual income statement) · pre-2015 EPS in the cache is per the post-stock-dividend share count (13,151 M) and is consistent (net profit ÷ shares)",
      "_as_of": "2026-10-28"
    }
  },
  "holdings": {
    "growth_scenarios": {
      "HMPRO": {
        "bad": -0.02,
        "mid": 0.01,
        "good": 0.05,
        "source": "research/hmpro-deep-dive-2026-10-28.md section 4.1 — earnings-based: FY2019-25 EPS CAGR -0.4% (six flat years), FY2023-25 -3.1% (latest direction), FY2015-25 +5.5% (expansion-era upper bound); payout held at 83%; buyback ~1-1.5%/yr in the mid case only; industry forecast flat 2026, +3-3.5% 2027-28 (Krungsri)",
        "as_of": "2026-10-28"
      }
    }
  }
}
```

`special_dividends`: none identified for HMPRO — PP lists only ordinary cash dividends from FY2015 (stock dividends FY2009–14 are a form, not a special); no "พิเศษ" row.

---

## acceptance (checked line by line against docs/deep-dive.md)
- D1–D18 all answered with fact-sheet section or external source + date: section 3, 18 rows, every row has a source column with codes dated in the source table (D18 marked not applicable with the HMPRO-specific question answered instead)
- D1 normal EPS FY2025 recorded with what was removed and why: 0.46 — nothing removed, reason given (no one-offs in the consolidated P&L, OR p.406–407); config block above (not written to config.json per the brief)
- D2 numeric year-5 DPS from an earnings-based rate + obstacles: 0.343 / 0.399 / 0.485 (FY2030) at −2 / +1 / +5%; obstacles in D2 and section 5
- D15 ≥2 beliefs with sourced counter-evidence and a falsifier tied to a T flag: 5 beliefs in 5A, each with source + date and a T / C2 flag
- D16 every flag maps to a D15 belief and every belief has a flag: section 6 table + combination line; risks that are nobody's belief sit in section 5
- Numbers and quotes all carry source + date; unproven items prefixed `guess:`; "not found" written for related-party detail, OneStockHome size, 2008 net profit, company full-year SSS by format
- Forward growth is EPS-based on normal earnings; dividend growth and payout shifts not used; COVID 2020 not a base (FS 5-year window flagged as COVID-based in D18 / 4.1)
- Real closing prices only (Y unadjusted closes; FS A10)
- DPS cross-checked on ≥2 sources every year FY2015–2026 interim (PP, SA, yahoo, FS set_official, AGM, K1, IX1); interim / final assigned to the fiscal year of the profit (interim XD Sep N + final XD Apr N+1 = FY N)
- Q3/2026: searched — not published on 2026-10-28 (broker previews only, IX3); 9M/2026 therefore not available; 1H26 and SSS by quarter reported instead
- Debt: FS A6 has no ⛔; identity verified against OR / Y; leases split out (7,097 million)
- data/manual_facts/HMPRO.json written (founded / listed / policy / payout table / owners / board / stores / SSS / Malaysia / debt / buyback / one-offs / quarterly profits) and `fact_sheet.py HMPRO --refresh` re-run — the refreshed FS prints the manual facts under "ต้องกรอกมือ"
- Section 4 DCA / lump tables computed with `yoc_table` / `dca_table` / `required_growth` from scripts/fact_sheet.py for years 5/10/15/20, both price modes, three scenarios, lump at today's price and discounts; no sentence concludes whether 7–12% is reached
- Cheap-levels section written as a three-step ladder with guards (section 7)
- No buy / sell order (R6); no verdict on the 7–12% target
- Files written: research/hmpro-deep-dive-2026-10-28.md (this file) · data/manual_facts/HMPRO.json (git-ignored) · reports/facts/HMPRO_2026-10-28.md (re-generated by the script) · scratch: C:\WORKSPACE\_desk\maxmahon\hmpro-dd-2026-10-28\files\ (hmpro_probe.py, hmpro_probe_out.txt, or2025.pdf/.txt, agm2026.pdf/.txt, panphol_hmpro_div.html) · config.json and all scripts untouched · nothing committed
