# KTC deep dive — "ถือและซื้อตัวนี้ต่อไปทุกเดือนอีก 10 ปี เรามาถูกทางไหม?"

- Written 2026-10-28 · ordered by Art 2026-10-28 (deep-dive candidate from `research/niwes-keep-or-cut-2026-10-28.md` section 3) · Niwes leg · **candidate, not held — no cost basis**; all yield-on-cost tables use today's price and the cheap-ladder levels instead of a holding cost.
- Template: `docs/deep-dive.md` (steps, rules, pass criteria) · questions D1–D18 and flags T1–T6: `docs/niwes-principles.md` sections 4–5 · 10-section layout + "values for config" + acceptance copied from `research/bbl-deep-dive-2026-10-19.md` (format only; BBL's bank table becomes a consumer-finance lender table here).
- Starting data = fact sheet `reports/facts/KTC_2026-10-28.md` (FS), generated today with `--refresh`, close 35.00 on 2026-10-27, then re-generated after `data/manual_facts/KTC.json` was written (section 9).
- Owner's 7–12% yield-on-cost target is a direction, not a cut-off (deep-dive.md): section 4 reports the numbers, no pass/fail on the target. No buy/sell order (R6).
- **Q3/2026 results are out** (MD&A 3Q26, 20 Oct 2026): Q3 net profit 2,125 m +8.9% YoY, 9M 6,521 m +14.3% YoY (M3Q). FY2026 is not a complete fiscal year — FY2025 (DPS 1.77) is the base year everywhere.
- Language: English (worker rule); Thai headings copied from the template files.

## รหัสแหล่ง (ใช้ซ้ำทั้งไฟล์)

| code | source | data to | fetched |
|---|---|---|---|
| FS | `reports/facts/KTC_2026-10-28.md` — `fact_sheet.py KTC --refresh`: A1 DPS 2002–2025 (set.or.th 2021+, yahoo before), A2 cuts, A3 CAGR, A4 rule-based yield-on-cost (no config scenarios yet), A5 EPS/ROE/profit 2010–2025, A12 payout, A10 year-end PE/PBV/yield 2016–2025, flags | FY2025 · close 35.00 (2026-10-27) | 2026-10-28 |
| Y | yfinance `KTC.BK` (run inline, not saved): annual P&L/BS 2022–2025, quarterly 1Q25–2Q26, dividends 2003–2026, split 2018-07-13 10:1, real year-end / monthly closes 2010–2026 (`auto_adjust=False`), 52-week 24.80–40.50, market cap 90,242 m, shares 2,578.3 m, peer snapshot | 2Q26 · 2026-10-27 close | 2026-10-28 |
| PP | aio.panphol.com/stock/KTC/dividend (every XD row FY2545–FY2568, one payment per year, no special flag) · /sholder (top holders, record 5 Aug 2026) · /fin (2021–2025 equity, ROE, D/E, BVPS) | XD 10 Apr 2026 | 2026-10-28 |
| M25 | KTC MD&A FY2025 unaudited, 15 Jan 2026 — ktc.co.th/pub/media/sites/cs/assets/ir/financialinformation/document/05-MDA-TH-Y2025-Unaudited-Final.pdf (13 pages, pypdf): P&L table FY2024/FY2025, receivables by product, NPL by product, ECL movement, 4-year charts of NPL / coverage / credit cost / D/E / cost of funds / NIM / ROE / ROA / cost-to-income, borrowings, industry table (BOT data 9 Jan 2026), 2025 targets vs actual, BOT debt-relief programmes | 31 Dec 2025 | 2026-10-28 |
| M3Q25 · M1Q · M2Q · M3Q | KTC MD&A 3Q25 reviewed (…/05-MDA-3Q25-TH-Reviewed.pdf) · 1Q26 (upload/ir-financial-statement-mda/Q12026/05-MDA-TH-1Q2026-Unreviewed.pdf) · 2Q26 reviewed (Q22026/04-MDA-TH-2Q26-Reviewed.pdf) · 3Q26 unreviewed (Q32026/05-MDA-TH-3Q26-Unreviewed.pdf, 20 Oct 2026) — quarterly profit, NPL, coverage, credit cost, D/E, cost of funds, NIM, ROE, 2026 targets, WIN acquisition | 30 Sep 2026 | 2026-10-28 |
| F56 | KTC Form 56-1 FY2016 (ktc.co.th/sites/cs/assets/ir/resources/document/59_form56-1-311216.pdf, 271 pages, pypdf): founding 4 Dec 1996, listing 28 Oct 2002, dividend policy section 7.4 (verbatim) | FY2016 | 2026-10-28 |
| AB | ktc.co.th/en/about: registered 4 Dec 1996, listed 28 Oct 2002, 2,578,334,070 shares par 1, KTB 49.29%, TRIS rating AA, members 3,869,210 (30 Sep 2026) | 30 Sep 2026 | 2026-10-28 |
| AGM26 | ktc.co.th/en/news/corporate/agm-dividend2026 (3 Apr 2026): FY2025 net profit 7.78 bn +4.6%, DPS 1.77, total 4,563,651,304 baht, paid 30 Apr 2026 · ktc.co.th/news/corporate/ktc-agm-2022: FY2021 DPS 1.00 = 41.25% of net profit | AGM 2026 | 2026-10-28 |
| TRIS | TRIS Rating industry report "Credit card and personal loan", 26 Mar 2025 (media.settrade.com PDF, 8 pages): BOT system data 2020–2024, bank/non-bank shares, NPL by segment, BOT measure timeline 2020–2025, min-payment schedule 5% → 8% → 10% | end-2024 | 2026-10-28 |
| LHB | LH Bank research "Industry Outlook 2025 Credit Card", 12 Jun 2025 (lhbank.co.th PDF, 4 pages): issuer shares KBANK 20.6%, KCC 19.8%, KTC 16.3%, CardX 14.7% (metric not stated in the extracted text — likely card receivables, Mar 2025); bank 9.37 m vs non-bank 16.78 m card accounts | Mar 2025 | 2026-10-28 |
| BOTQ | bot.or.th news-20260818 (18 Aug 2026) — Q2/2026 banking brief: system loans +2.0% YoY, NPL 2.82% (534.8 bn), SME and consumer credit still contracting, stage-2 6.78% | 2Q26 | 2026-10-28 |
| BOTMP | BOT credit-card minimum payment: mitihoon 601802 (10 Dec 2025) — 8% extended to 31 Dec 2026, was to become 10% on 1 Jan 2026 · bangkokbiznews finance/1210721 (28 Oct 2026) — 8% through end-2026, 0.25% interest credit for paying ≥8%, conversion to term loan before NPL | Dec 2026 | 2026-10-28 |
| NCB | thaipost 1036037 (21 Jul 2026) — National Credit Bureau May 2026: NPL 1.33 tn = 9.75% of 13.64 tn tracked household debt, SM (pre-NPL) 4.3% from 3.1% in Q3/25, debt growth +0.6% | May 2026 | 2026-10-28 |
| HH | search summaries only (thaipublica.org/2026/07 SCB EIC · NESDC via mitihoon 13 Apr 2026): household debt 85.9% of GDP in Q1/2026, 16.41 tn, +0.5% YoY — original pages not opened; Q2/2026 figure not found | Q1/2026 | 2026-10-28 |
| TS · NW · TP | thansettakij 671870 (20 Oct 2026) + naewna 125663 (21 Oct 2026) + thaipost 1092598 (21 Oct 2026): Q3/9M26 figures, market shares first 8 months 2026 (card receivables 14.6%, spending 13.3%, PL 4.2%) · thaipost 931626 (15 Jan 2026): FY2025 figures + 2026 targets | Q3/26 | 2026-10-28 |
| IVX | innovestx.co.th ktc-earnings-20260116 (4Q25: credit cost 4.86%, LLR 420%, 2026 targets, NEUTRAL TP 31) · ktc-update-20260327 (2026F +4%, DPS 2026F 1.86 at 59% payout, TP 31, cost-to-income 36–37% in 2026 from core-system upgrade) · effective tax 27.7% FY2025 vs 20.26% FY2024 (search summary of IVX) | Mar 2026 | 2026-10-28 |
| HV | hoonvision 192147 (23 May 2026): Krungsri BUY TP 39 (2026F 8,194 m +5%), KGI Outperform TP 36, Phillip BUY TP 40 (2026F 8.1 bn, DPS 1.84) · settrade consensus (search summary, date not shown): 13 brokers, average TP 35.67, range 26–44 | May 2026 | 2026-10-28 |
| IQ25 · S2T | infoquest 507599 (25 Jun 2025): KTC statement on the share-price fall from 23 Jun 2025 — "no significant event", external factors · share2trade (search summary): 420,204,381 shares = 16.30% of the company pledged as margin collateral at the time | Jun 2025 | 2026-10-28 |
| MG12 | mgronline 9550000059446 (15 May 2012): Q1/2012 loss 155 m from provisioning after the floods; Q4/2011 bad-debt charge 2,288 m; CEO Rathian Srimongkol expects profit from Q2/2012 | Q1/2012 | 2026-10-28 |
| TR21 · BB19 | thairath 2015623 (19 Jan 2021): FY2020 profit 5,332 m, FY2019 5,524 m, receivables 90,149 m +4.3%, NPL 1.8% · brandbuffet (Feb 2019, search summary): FY2018 5,140 m +56%, FY2017 3,304 m, FY2016 2,495 m, NPL 1.1% | FY2020 | 2026-10-28 |
| KOC | `research/niwes-keep-or-cut-2026-10-28.md` section 3 — Q2/26 2,225 m vs 1,895 m, EPS-series doubt (2014 2.44 → 2015 0.80), profit 2022→2025 and ROE 24% → 18.5% | 2026-10-28 | — |

Unreachable or useless this round: ktc.co.th/en/investor-relations/dividend and /th/… (404) · ktc.co.th/en/investor-relations/financial-ratio (404) · Company-Highlight PDFs (server returns an XML error) · kaohoon 847444 (403; headline only: "Q2 profit +17% on lower provisions") · settrade news/consensus pages (JS) · 2Q26/FY2025 MD&A found under two different URL trees (`/pub/media/...` and `/upload/ir-financial-statement-mda/...`). Consequence: the dividend policy comes from the FY2016 Form 56-1 (verbatim) and payout ratios from AGM news + our own EPS; no company table of ROE/D/E before 2021.

---

## 1. คำตอบ 1 หน้า

**Answer (facts first, decision stays with Art and the head — R6):** KTC is a consumer-finance lender (credit cards 65% of receivables, personal loans 34%) that is **not growing its book**: receivables 107.7 bn, +0.8% YoY; the Thai card industry's receivables shrank 3.7% in 11M25 (M25, BOT data). What is growing is profit — 9M26 +14.3% — and it comes from lower credit losses (ECL −8.9%) and cheaper funding (−16.2%), not from revenue (+0.4%). The FY2025 dividend of 1.77 (yield 5.06% at 35.00) was a **payout jump from 46% to 59%**, not an earnings jump (EPS +4.6%). So the C1 yield passes today, but the question for a 10–20-year DCA is whether (a) the 59% payout is the new norm (policy only promises ≥40%) and (b) a lender whose industry is flat and whose prices are set by the BOT (16% ceiling, 8%/10% minimum payment) can compound EPS at all. Our answer: EPS growth of 0–6%/yr (bad/mid/good) on normal EPS 3.02, a dividend that is well covered (D/E 1.32, coverage 413%, 42% of profit retained) but regulator-exposed, and a share price that has been de-rated from PE 28 (2020) to 11.6 — cheap against its own past, but that past was a growth stock.

1. **Yield today 5.06% ≥5% (C1) — just.** DPS FY2025 1.77 ÷ 35.00 (FS A10) · 3-year average 4.2% (flag AVG_YIELD_3Y, 3-year window = ours) · FY2025 EPS 3.02 is normal — no one-off identified; ECL 5,906 m is a normal cost; bad-debt recoveries 4,038 m recur every year (section 2.3). Payout 58.6% on normal EPS.
2. **Year-5 (FY2030) DPS on an earnings-based rate: 1.77 / 2.15 / 2.37 baht at bad 0% / mid 4% / good 6%** → 5.1% / 6.2% / 6.8% of today's price (section 4). C2 (≥5% in year 5) holds in all three only if payout stays ≈59%; at the 40–46% payout of 2015–2024 the same EPS gives 1.21–1.39 → 3.5–4.0%.
3. **Dividend history has a hole, not a cut**: no dividend for FY2008, FY2009 and FY2011 (PP, Y pay-date list), with a net loss in 2011 (system cache 1,621 m; the Q4/2011 bad-debt charge of 2,288 m is sourced, MG12). Since FY2012: 14 straight years paid, never cut, flat once (FY2020, 0.88). The 2020 COVID year cost 3.5% of EPS and nothing of the dividend.
4. **Balance sheet is the strong part**: NPL 1.92% (cards 1.21% vs industry 2.6%), coverage 413%, allowance 8.5 bn = 4.1× the NPL stock of ≈2,051 m (8,481 ÷ 413.4%), D/E 1.32 vs a 10× covenant, 64% of borrowing in debentures at 2.62% cost, TRIS AA (M3Q, AB). ROE 19.3% with only 1.3× leverage.
5. **What does not hold up in the story**: "EPS grows 14%/yr" (FS A3 10-y window, base 2015 = the high-growth era, ROE 26–35%; the 2018→2025 rate is 6.1%, 2022→2025 3.2%) · "cheap at 90th-percentile yield" (the 2016–2022 yields of 1.5–2.9% were a PE-15–28 growth stock; today's 5% is a de-rating, section 7) · "1.77 is the floor" (policy ≥40%; 10 years of 40–46%).

**Confidence: medium-high on facts, low-medium on growth.** Profit, NPL, coverage, D/E, cost of funds and DPS agree across the company's own MD&As, the AGM news, panphol and yfinance. Low-confidence items: growth scenarios (judgement, section 4.1), the FY2025 tax rate (27.7% vs 20.3%, cause not stated in the MD&A — section 2.3), market-share ranking (LHB extract does not name the metric), household-debt Q2/2026 (not found).

**Items Art and the head must decide (not decided here):**
- Which scenario set goes into `holdings.growth_scenarios` (proposed bad 0 / mid 4 / good 6%) and whether normal EPS FY2025 = 3.02 (reported, nothing stripped) is accepted, or the tax-adjusted ≈3.3 (if the 27.7% tax rate proves a one-off) — section "ค่าที่ต้องจดลง config".
- Whether a payout-driven dividend (46% → 59%) counts as a "normal" base for C2/T2, or whether the bad case should be read on the 40% policy floor (DPS 1.21 at today's EPS).
- Whether a regulator-driven cut (interest ceiling or minimum payment) counts toward T1/T3 as "permanent" — the 2020 cap cut (18% → 16%) is the precedent.
- D17: whether a fourth finance name (after BBL, TCAP, TISCO off-plan) is wanted in the Niwes leg at all.

---

## 2. ใบข้อเท็จจริง

### 2.1 Dividend per share by fiscal year — three sources compared (FS A1 · PP · Y pay-date list) · all values on today's 2,578.3 m shares (par 10 → 1 split 2018-07-13, Y)

| FY | FS A1 | PP (XD · paid) | Y (pay date) | agree? |
|---|---:|---|---|---|
| 2012 | 0.040 | 0.40 par-10 (XD 4 Mar 2013) = 0.040 | 0.040 (2013-03-04) | ✓ |
| 2013 | 0.200 | 2.00 par-10 (XD 3 Mar 2014) = 0.200 | 0.200 (2014-03-03) | ✓ |
| 2014 | 0.275 | 2.75 (XD 26 Feb 2015) = 0.275 | 0.275 | ✓ |
| 2015 | 0.325 | 3.25 (XD 19 Feb 2016) = 0.325 | 0.325 | ✓ |
| 2016 | 0.400 | 4.00 (XD 21 Apr 2017, paid 16 May 2017) = 0.400 | 0.400 | ✓ |
| 2017 | 0.530 | 5.30 (XD 26 Apr 2018, paid 11 May 2018, pre-split) = 0.530 | 0.530 | ✓ |
| 2018 | 0.820 | 0.82 (XD 12 Apr 2019) | 0.820 | ✓ |
| 2019 | 0.880 | 0.88 (XD 16 Apr 2020) | 0.880 | ✓ |
| 2020 | 0.880 | 0.88 (XD 19 Apr 2021) | 0.880 | ✓ — flat, not cut |
| 2021 | 1.000 | 1.00 (XD 18 Apr 2022, paid 6 May 2022) · AGM26: 41.25% of profit | 1.000 | ✓ |
| 2022 | 1.150 | 1.15 (XD 18 Apr 2023) | 1.150 | ✓ |
| 2023 | 1.270 | 1.27 (XD 17 Apr 2024) | 1.270 | ✓ |
| 2024 | 1.320 | 1.32 (XD 17 Apr 2025, paid 2 May 2025) | 1.320 | ✓ |
| 2025 | 1.770 | 1.77 (XD 10 Apr 2026, paid 30 Apr 2026) · AGM26: 4,563,651,304 baht | 1.770 | ✓ |
| 2026 (open) | — | — (no interim; KTC pays once a year) | — | not a full year |

Earlier years: PP FY2545 0.55 · FY2546 0.70 · FY2547 1.30 · FY2548 1.50 · FY2550 1.20 (all par 10 → ÷10) · **no dividend FY2552 and FY2554** (PP rows "ไม่จ่ายเงินปันผล") · no FY2551 row at all, and Y shows no payment in 2009 → FY2008 unpaid (two sources, by absence). FS A1 rows 2002–2007 (0.0346 … 0.12) do **not** match PP per-share values year by year (yahoo tags by pay year and applies a different adjustment before 2008) — not used in this book; the FS statement "paid 14 years without a gap" (FY2012–2025) is correct. One payment per fiscal year, every PP row labelled "เงินปันผล" → **no special dividends** (nothing for `special_dividends`).

### 2.2 Lender table — the numbers that replace "cash" and "debt" for a consumer-finance company (D4 D10 D11) · consolidated group unless marked · entered in `data/manual_facts/KTC.json`

| year | net profit to parent (m) | receivables (m) | ECL (m) | credit cost | NPL | NPL cards / PL | coverage | allowance (m) | D/E | cost of funds | NIM | ROE | ROA | source |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2022 | 7,079 | — | — | 4.7% | 1.78% | — | 476.3% | 8,792 | 2.22 | 2.39% | 13.20% | 24.3% | 7.4% | M25 charts |
| 2023 | 7,295 | — | — | 5.2% | 2.19% | — | 400.3% | 9,763 | 2.15 | 2.64% | 13.22% | 21.8% | 6.8% | M25 charts |
| 2024 | 7,437 | 111,162 | 6,762 | 6.1% | 1.95% | 1.25% / 2.46% | 369.3% | 7,966 | 1.78 | 2.79% | 12.87% | 19.7% | 6.6% | M25 |
| 2025 | 7,782 (+4.6%) | 111,585 (+0.4%) | 5,906 (−12.7%) | 5.3% | 1.79% | 1.09% / 2.55% (lease 17.86%) | 425.0% | 8,424 | 1.51 | 2.84% | 13.07% | 18.5% | 7.0% | M25 |
| 1H26 | 4,397 (+17.1%) | — | 2,698 (−13.4%) | 5.0% | 1.86% | 1.14% / 2.55% | 426.3% | 8,494 | 1.43 | 2.62% | — | 20.0% (ann.) | 8.1% | M2Q |
| 9M26 | 6,521 (+14.3%) · Q3 2,125 (+8.9%) | 107,717 (+0.8%) | 4,155 (−8.9%) · Q3 1,457 (+0.9%) | 5.1% (Q3 5.4%) | 1.92% | 1.21% / 2.65% | 413.4% | 8,481 | 1.32 | 2.62% | 13.48% | 19.3% (ann.) | 8.0% | M3Q |

Earlier single-line facts (not entered as rows): NPL 1.1% end-2018 (BB19) · receivables 90,149 m +4.3%, NPL 1.8% end-2020 (TR21) · D/E 2.30, ROE 23.7% FY2021 (PP /fin).

Read: credit cost of 4.7–6.1% of receivables every year is **the normal cost of this book** (ECL 5.9–6.8 bn a year against 7.1–7.8 bn of profit — D1: provisions are not one-offs). Coverage was rebuilt from 369% to 425% in 2025 and is being drawn down slowly in 2026 (413%) while the NPL ratio ticks up (1.79% → 1.92%); lease NPL 18–29% is the KTB Leasing book, closed to new lending since Aug 2023 (M25). Leverage has fallen every year (2.30 → 1.32) because profits are retained while the book does not grow — this is also why ROE fell from 24% to 18–19%. Sensitivity (ours): each +1 point of credit cost ≈ 1.1 bn pre-tax ≈ 0.34/share after tax ≈ 11% of EPS.

### 2.3 EPS rebuilt on a constant share count — basis for normal EPS (D1, KOC doubt)

Net profit to parent ÷ 2,578.334 m shares (today's count; the 2018 split was 10:1 so the pre-2018 count of 257.8 m gives the same per-share figure). Net profit 2010–2021 = FS A5 (system cache, thaifin/SETSMART); 2016–2020 cross-checked with BB19/TR21; 2022–2025 with M25/AGM26.

| FY | net profit (m) | EPS rebuilt | FS A5 EPS | DPS | payout (ours) | note |
|---|---:|---:|---:|---:|---:|---|
| 2010 | 224 | 0.09 | n/a | 0.045 | 52% | |
| 2011 | −1,621 | −0.63 | n/a | none | — | loss; Q4/11 bad-debt charge 2,288 m (MG12); amount cache-only |
| 2012 | 255 | 0.10 | 0.10 | 0.04 | 40% | turnaround year |
| 2013 | 1,283 | 0.50 | 0.50 | 0.20 | 40% | |
| 2014 | 1,755 | **0.68** | **2.44 ⛔** | 0.275 | 40% | FS/cache value wrong (not a split artefact — the split was 2018); A3 windows that touch 2014 are polluted |
| 2015 | 2,073 | 0.80 | 0.80 | 0.325 | 40% | |
| 2016 | 2,495 | 0.97 | 0.98 | 0.40 | 41% | |
| 2017 | 3,304 | 1.28 | 1.29 | 0.53 | 41% | |
| 2018 | 5,140 | 1.99 | 1.99 | 0.82 | 41% | +56%: TFRS 9 / new provisioning + growth (BB19 "record 6th year") |
| 2019 | 5,524 | 2.14 | 2.14 | 0.88 | 41% | |
| 2020 | 5,333 | 2.07 | 2.08 | 0.88 | 43% | COVID: −3.5%; interest ceiling cut 18% → 16% (TRIS) |
| 2021 | 5,879 | 2.28 | 2.27 | 1.00 | 44% | revenue −5.6% (FS A5) |
| 2022 | 7,079 | 2.75 | 2.75 | 1.15 | 42% | |
| 2023 | 7,295 | 2.83 | 2.84 | 1.27 | 45% | |
| 2024 | 7,437 | 2.88 | 2.88 | 1.32 | 46% | effective tax 20.3% |
| 2025 | 7,782 | **3.02** | 3.02 | 1.77 | **58.6%** | effective tax 27.7% (ours: 1 − 7,559/10,456); FS A5 prints profit 7,668 ⛔ but EPS 3.02 ✓ |

EPS CAGR on the rebuilt series (base years all profitable, none a crisis year): 2015→2025 10 y **14.1%** (= FS A3 14.2%; base = start of the 2013–2018 high-growth era, ROE 26–35%, not repeatable) · 2017→2025 11.3% · **2018→2025 7 y 6.1%** · 2019→2025 6 y 5.9% (pre-COVID base) · 2020→2025 7.9% (COVID base — rejected) · **2022→2025 3 y 3.2%**. DPS CAGR 2015→2025 18.5% and 2020→2025 15.0% are above EPS growth only because payout moved 40% → 59% (GM-1 trap; A12).

**Normal EPS FY2025 = 3.02 (reported, nothing stripped).** Checked: ECL 5,906 m kept (normal cost) · bad-debt recoveries 4,038 m kept (4,110 m in 2024, 2,815 m in 9M26 — a recurring revenue line of this business) · KTB Leasing losses kept (real, ≈0.2/share by the gap between company-only profit 8,289 m and parent-attributable 7,782 m, M25; they fade as the 1.1 bn lease book runs off) · no asset sale, no revaluation, no equity-method gain found in M25 / M2Q / M3Q · **effective tax 27.7% vs 20.3% in 2024** — not explained in the MD&A (IVX also notes it); if it were a one-off, normal EPS would be ≈3.3 (10,456 × 0.797 − 223 NCI ÷ 2,578). Not added back (unproven); the direction is that 3.02 is conservative, not generous. FY2024 normal EPS = 2.88 (reported; nothing exceptional identified).

### 2.4 Peers — snapshot Y 2026-10-28 close (TTM ratios as yfinance computes them)

| | KTC | AEONTS (only other listed card/PL non-bank, TRIS) | KTB (parent) | KBANK | SCB |
|---|---:|---:|---:|---:|---:|
| price | 35.00 | 89.25 | 44.25 | 245.00 | 153.50 |
| PE trailing | 10.9 | 7.5 | 12.3 | 11.3 | 11.8 |
| PBV | 1.96 | 0.78 | 1.35 | 0.99 | 1.07 |
| dividend yield (Y) | 4.99% | 6.72% | 4.82% | 4.92% | 7.40% |
| ROE (Y TTM) | **19.3%** | 10.3% | 10.8% | 8.5% | 8.7% |
| payout (Y) | 54% | 46% | 58% | 56% | 87% |
| market cap (m) | 90,242 | 21,886 | 618,441 | 580,485 | 516,851 |

Read: KTC trades at twice AEONTS's PBV and the highest ROE of the group; the premium is ROE, not yield. AEONTS's profit fell 3,815 → 2,860 m 2023→2025 (KOC) while KTC's rose — same industry, different books. AEONTS D/E and NPL were not fetched this round (T6 peer line left open).

### 2.5 Crisis years — paid? how deep? how long to recover (PP · Y · FS A2 A5 · MG12 · TRIS)

| crisis | DPS before → during | paid? | back to prior level | cause |
|---|---|---|---|---|
| 2008–2011 | 0.12 (FY2007) → none FY2008 → none FY2009 → 0.045 FY2010 → none FY2011 → 0.04 FY2012 → 0.20 FY2013 | 3 of 4 years unpaid | above 0.12 again only in FY2013 = **6 years** | 2011 net loss (cache −1,621 m); Q4/2011 bad-debt charge 2,288 m + floods, provisioning overhaul under a new CEO from 1 Jan 2012 (MG12 and search summaries); the Q1/2012 loss of 155 m is sourced |
| 2020 COVID | 0.88 → 0.88 → 1.00 | normal, flat | no cut | EPS −3.5%; BOT cut the card interest ceiling 18% → 16% and the minimum payment 10% → 5% (TRIS); whether the BOT 2020 dividend order to commercial banks covered KTC (a non-bank in KTB's group) — not found |

Both the deep hole and the flat year were credit-cycle or regulator events; neither was a liquidity event (D/E was 2.2–2.3 even in 2021–22, PP /fin).

---

## 3. คำตอบ D1–D18 ทีละข้อ

| # | answer | evidence (FS section / source + date) | type | confidence |
|---|---|---|---|---|
| D1 | **Yield 5.06% ≥5% — passes C1 by 0.06 points.** DPS FY2025 1.77 ÷ 35.00 (close 2026-10-27); 3-year average 4.2% (flag AVG_YIELD_3Y; 3-year window = ours). Paid from normal profit: **yes — normal EPS FY2025 = 3.02 = reported** (section 2.3: ECL and bad-debt recoveries are recurring; no asset sale / revaluation / equity gain; the 27.7% tax rate is unexplained and would make normal EPS higher, not lower). Payout 58.6% < 100%, no LOSS flag. But the dividend rose 34% on EPS +4.6% — a payout shift from 46% to 59% (A12), which is not repeatable (deep-dive.md rule). A5 jump year 2018 (+56%) is 7 years old and was growth plus new provisioning rules, not a one-off. | FS A10 A5 A12 · M25 · AGM26 · section 2.3 | number + person | high (facts) / medium (tax item) |
| D2 | **Year-5 (FY2030) DPS: 1.77 / 2.15 / 2.37 baht at bad 0% / mid 4% / good 6% per year** → 5.1% / 6.2% / 6.8% of 35.00 (section 4). Rates are EPS-based on normal EPS (2.3): bad = flat EPS (revenue +0.4%, book +0.8%, industry −3.7%; credit cost back to 6% or a cap cut eats the cost savings); mid = 2022→2025 CAGR 3.2% rounded up for the 2026 run-rate (+14% 9M) and broker 2026F +4–5% (IVX, HV); good = 2018/2019→2025 CAGR 5.9–6.1%, within self-funded capacity ROE 19% × (1 − 59%) ≈ 7.8%. What supports it: card spending +4.7% vs industry ≈0% (M3Q), share gains in every product (M25: receivables 14.3 → 14.9%, spending 13.1 → 13.6%), cost of funds 2.93 → 2.62%, coverage 413%. Obstacles: receivables flat for 3 years (111.2 → 107.7 bn), industry card receivables −3.7% and cards −1.9% (M25), minimum payment scheduled 10% from 1 Jan 2027 (BOTMP), 16% interest ceiling with a 2020 precedent of cutting it, household debt 85.9% of GDP (HH) with NCB SM 4.3% rising (NCB), cost-to-income 36–37% in 2026 from the core-system upgrade (IVX). **All three scenarios assume payout stays ≈59%**; on the 40% policy floor year-5 DPS = 1.21 / 1.47 / 1.62 → 3.5% / 4.2% / 4.6%. C2 flag on FS today: not tripped (rule-based mid 8.9%); on proposed mid 4% still ≥5%; on bad 0% 5.06%. | FS A3 A4 · section 2.3 · 4.1 · M25 M3Q · BOTMP · HH · NCB · IVX · HV | number + person | medium |
| D3 | Not applicable as C3 exception (yield ≥5%). For the record: DPS up 5 straight years FY2021–2025 (FS A1), but FY2025's +34% is payout-driven (A12: 46% → 59%) and does not count as growth; underlying EPS growth 2022→2025 3.2%. | FS A1 A12 · 2.3 | number | high |
| D4 | **Can 1.77 hold if business falls?** On EPS 3.02, profit can fall 41.4% before payout hits 100% (FS A5, ours) — but the policy floor is 40% of profit (F56), so management may cut the dividend long before that: at 40% payout on today's EPS, DPS = 1.21. Worst EPS year: 2011 loss, no dividend (2.5); worst recent: 2020 −3.5%, dividend held. Lender buffers today (2.2): coverage 413%, allowance 8,481 m = 4.1× the NPL stock ≈2,051 m (8,481 ÷ 413.4%, ours), D/E 1.32 vs covenant 10×, undrawn lines 19,880 m vs 9,130 m of debt due in Q4/26 (M3Q); credit cost 5.1% vs a 6.1% peak in 2024. Stress (ours): credit cost back to 6.1% = −1.1 bn pre-tax ≈ −11% EPS → payout at 1.77 rises to ≈66%, still covered; a 2-point cut in the 16% card ceiling ≈ −0.9 bn of card interest income (7,800 m × 2/16, guess — mix of ceiling vs. actual rates not known) ≈ −9% EPS. Both together ≈ −20% EPS → payout 73% at 1.77. The regulator, not the balance sheet, is the binding constraint. | FS A2 A5 A12 · 2.2 · 2.5 · F56 · M25 M3Q · TRIS · `manual_facts/KTC.json` | number + person | high |
| D5 | Revenue up 13/15 years (FS A5; dips 2012 −2%, 2021 −5.6% COVID + cap cut), streak to latest year = 4 · EPS up 5 years (2021–2025; 2020 −3.5%) · DPS up 5 years (flat 2020). Stumbles: 2011 (loss, provisioning overhaul — permanent fix, temporary pain), 2020–21 (COVID + regulation — temporary), 2024 (credit cost 6.1%, EPS +1.9% — temporary, cost fell in 2025). 2026 in progress: 9M profit +14.3% but revenue +0.4% and receivables +0.8% — profit growth is from cost lines (ECL −8.9%, finance cost −16.2%), which has a floor. C7 "up every year" is roughly KTC's history since 2012 but not before. | FS A5 A1 · M3Q · 2.3 · 2.5 | number + person | high |
| D6 | Registered 4 Dec 1996, converted to public company 2 Jul 2002, listed on SET 28 Oct 2002 (F56, AB) — 30 years old, 24 years listed · paid 14 straight fiscal years FY2012–2025 (FS A1, PP); unpaid FY2008/09/11 (2.1) · market cap 90,242 m (Y) ≥ 5 bn (ours) · TRIS AA (AB) · SET50 since 2019 (AB). Passes C5 "old and large" with the 2008–11 gap on record. Recorded in `manual_facts`. | F56 · AB · FS A1 · PP · Y | number | high |
| D7 | **Policy (verbatim, F56 section 7.4):** "จากการประชุมสามัญผู้ถือหุ้น ครั้งที่ 1/2546 เมื่อวันที่ 25 มีนาคม 2546 มีมติให้จ่ายเงินปันผลในอัตราไม่ต่ำกว่าร้อยละ 40 ของกำไรสุทธิหลังหักภาษีและสำรองตามกฎหมาย ตั้งแต่ปี 2546 เป็นต้นไป" — a floor of 40%, no ceiling, no commitment above it. Actual: 40.4% FY2014–15 (F56), 41–46% FY2016–2024, 58.6% FY2025 (2.3); one payment a year, no interim. Brokers assume 59% continues (IVX DPS 2026F 1.86; Phillip 1.84) — assumption, not policy. Control: Krung Thai Bank 49.29% (AB, PP sholder 5 Aug 2026), Thai NVDR 8.72%, Mongkol Prakitchaivattana 3.53%, foreign nominees ≈5%; institutions 61% of the register (PP). Deals: KTC bought 75.05% of KTB Leasing from its parent (2021; search summary brandinside, not opened) — the lease book is now closed (Aug 2023), NPL 18–29%, and it dragged ≈0.5 bn off 2025 group profit (M25: company-only 8,289 m vs parent-attributable 7,782 m) — a related-party acquisition that cost minority holders; the 25 Aug 2026 purchase of collection partner WIN Performance (M3Q) is small and operational. SEC/enforcement search on KTC, KTB and the third-largest holder: nothing found (DC-4). Reading: a parent-controlled company that pays the policy floor plus a margin for 10 years and then lifted payout sharply in one year — shareholder-friendly in cash, parent-first in deals. | F56 · AGM26 · 2.3 · AB · PP · M25 M3Q · IVX HV | person | medium (deal details from a search summary) |
| D8 | **a. Industry declining?** Balances yes, spending no. BOT system data (M25 table, 9 Jan 2026): card receivables 522,784 m (+1.8%) in 2024 → 475,958 m (**−3.7%**) in 11M25; cards 26.69 m → 26.19 m (−1.9%); card spending 2,229 bn (+2.5%) → 2,003 bn 11M25 (+0.1%); personal loans 860 bn (−0.3%). Q1/2026: industry receivables 484,926 m (−0.1%), spending +0.7% (search summary of KTC 1Q26 news). TRIS (26 Mar 2025): card outstanding 497 bn end-2024 −0.3% after +3% in 2023; the 8% minimum payment since Jan 2024 raised repayments; card NPL 2.6% (2.5% in 2023), PL NPL 3.9%; 8 card issuers, 115 PL operators. BOT Q2/26: consumer credit "continued to contract" (BOTQ). Household debt 85.9% of GDP Q1/26, falling because credit is tighter (HH); NCB May 2026: NPL 9.75% of tracked debt, SM 4.3% and rising (NCB). KTC's own revenue (+0.4%) and receivables (+0.8%) echo this. **b. What disrupts it, and is it happening:** (1) BOT pricing rules — ceiling 18% → 16% (2020), PL 28% → 25%, minimum payment 5% → 8% (2024) → **10% scheduled 1 Jan 2027** (BOTMP; TRIS): happening · (2) debt-relief programmes that convert card debt to 5%-interest term loans, "คุณสู้ เราช่วย", NPL sales to SAM (M25; TRIS timeline): happening, KTC says no significant impact · (3) virtual banks and BNPL — NCB: PL +13.8% "partly BNPL"; KTB itself is in a virtual-bank consortium (BBL book VB, not re-verified): early · (4) a further ceiling cut (BOT's 2020 move is the precedent): not announced · (5) e-payment substitution of card spending: not measured here. | M25 · TRIS · BOTQ · BOTMP · HH · NCB · M3Q | person | medium |
| D9 | **Not number one.** LH Bank research (12 Jun 2025): KBANK 20.6%, Krungsri Card (KCC) 19.8%, **KTC 16.3%**, CardX 14.7% — third (metric not named in the extracted text; likely card receivables). KTC's own: 14.6% of industry card receivables, 13.3% of spending, 4.2% of personal loans, first 8 months 2026 (TS), up from 13–14% in prior years (M25). Edge that peers do not match on the numbers we have: lowest card NPL (1.21% vs industry 2.6%), coverage 413%, AA rating, parent funding (KTB lines 13.1 bn, M3Q), and a customer base skewed to civil servants and >25,000-baht earners (KGI via HV). Loses on scale to the KBANK/Krungsri groups and on cost of funds to deposit-taking banks (KTC borrows at 2.62%; banks fund cards from deposits). | LHB · TS · M25 M3Q · TRIS · HV | person (shares = number) | medium |
| D10 | Lender substitute for "cash": coverage 413.4%, allowance 8,481 m (7.9% of loans), D/E 1.32 (covenant 10×), borrowings 53,133 m of which debentures 63.9%, cost of funds 2.62%, undrawn lines 19,880 m vs 9,130 m due Q4/26 (M3Q) · bad-debt recoveries 2.8–4.1 bn a year are a cash inflow the P&L books as revenue (M25) · equity 44.0 bn (Y 2Q26) · TRIS AA (AB). Ample — the dividend (4.56 bn) is 10% of equity and 59% of profit. | 2.2 · M3Q · M25 · Y · AB | number + person | high |
| D11 | Debt vs industry: D/E 1.32 (9M26), down from 2.30 (2021), 2.22 (2022), 1.78 (2024), 1.51 (2025) — falling because the book is flat and profits are retained (M25, PP /fin). Covenant 10× (M25). Peer D/E (AEONTS) not fetched this round — T6 peer comparison left open. FS prints no A6 for `sector_profile: bank` (KTC is mapped to the bank profile); the cache-era ⛔ A6 problem does not arise here. | M25 M3Q · PP · FS A6 note | number | high (own) / open (peer) |
| D12 | Table 2.5: 2008–2011 three unpaid years + a loss year, 6 years back above the FY2007 level; 2020 flat, no cut; 2011 recovery was management-driven (provisioning overhaul), 2020 held by capital. The stock has never been through a 1997-type event (listed 2002). | PP · Y · FS A2 A5 · MG12 | number | medium (2011 loss amount cache-only) |
| D13 | No hidden asset found: no land, no listed subsidiary, no investment portfolio of note (Y BS: receivables and cash are 97% of assets). Two "hidden" items in the P&L sense, both ours: (1) excess allowance over NPL stock ≈ 6.4 bn pre-tax (8,481 − ≈2,051) — a buffer, releasable only if NPL falls, not an asset for sale · (2) KTB Leasing drag ≈ 0.2/share fading as the 1.1 bn lease book runs off (M25, M3Q) — guess on the per-share size. Market prices the equity at 1.96× book for a 19% ROE — nothing overlooked. | Y · M25 M3Q · 2.3 | number + person | low–medium |
| D14 | FS A10 label "cheap vs itself": yield 5.06% at the 90th percentile of 2016–2025 year-end yields (1.5–6.7%) — **but 2016–2022 were growth-stock years (PE 14–28, PBV 3.3–7.2 on the FS rows that are not glitched)**; the 90th-percentile reading measures the de-rating, not a bargain · PE 11.6 on FY2025 EPS, 10.9 trailing (Y) — not below the P3 "PE < 10" line (weak evidence, S2) · PBV 1.96 on 17.8 BVPS · 52-week 24.80–40.50 (Y) → 14% below the high, 41% above the low · brokers: TP 31 (IVX, Neutral, 1.65–1.7× PBV or 10× PE) to 39–40 (Krungsri/Phillip, May 2026), consensus average 35.67 (CONS, search summary) — today's price sits on the consensus · "another 20–30% down" (ours) = 28.0 / 24.5 → 6.3% / 7.2% on 1.77 (section 7 ladder). Price "appropriate" in Niwes' sense = person's call. | FS A10 · Y · IVX · HV · CONS | number + person | high |
| D15 | Belief table — section 5.1 (5 beliefs, counter-evidence with source + date, falsifier tied to a T flag). | section 5 | person | — |
| D16 | Flag table — section 6; every flag names the belief it watches, every belief has a flag. | section 6 | number + person | — |
| D17 | Art's call. Facts: Niwes leg today = AMATA (industrial estate) + BBL + TCAP (finance; TCAP ≈ 74% TTB per KOC) + TISCO off-plan (finance) — adding KTC makes finance 4 of 5 names and 3 of them (BBL, TTB via TCAP, KTC) are BOT-regulated consumer-credit exposures that move together on household-debt measures; KTB (KTC's parent) is not held. KTC's weight is not in the SSOT (no queue line) — not proposed here. Section 8 gives the arithmetic. | `roadmap/agreed-portfolio-framework.md` · KOC · section 8 | person | — |
| D18 | n/a — AMATA only. | — | — | — |

---

## 4. ปันผลเทียบต้นทุน (ปันผลปีนั้น ÷ ต้นทุน) — ก้อน + ถ้าซื้อทุกเดือน (DCA) · facts only, 7–12% is a direction (Art 2026-10-28)

Computed with the fact sheet's own functions (`scripts/fact_sheet.py` `yoc_table` / `dca_table` / `dca_yoc` / `required_growth`, imported inline on 2026-10-28) so the head can reproduce them by writing the scenarios into `config.json` and re-running `fact_sheet.py KTC --refresh`. Base DPS = FY2025 1.77 · price 35.00 (close 2026-10-27) · no holding cost (candidate) → cost levels = today's price + the three cheap-ladder levels of section 7 (29.50 / 27.00 / 24.50). Same rule as FS A4: DPS grows at the scenario rate from the last full-year dividend; DCA = equal money every month for 10 years, then hold; price grows with the dividend / price flat.

### 4.1 Three earnings-based growth scenarios (ours — not Niwes' words, not a forecast)

| scenario | DPS growth/yr | why this number | what must be true |
|---|---:|---|---|
| bad | 0.0% | revenue +0.4%, receivables +0.8% (M3Q); industry card receivables −3.7% (M25); the 2026 profit growth is cost-line driven (ECL −8.9%, finance cost −16.2%) and ends when credit cost normalises to 6% or the ceiling is cut; minimum payment 10% in 2027 shrinks revolving balances (BOTMP) | DPS held at 1.77 by keeping payout ≈59% of a flat EPS 3.0; no ceiling cut. **Below bad** (not a scenario, section 5): payout back to 40–46% → DPS 1.21–1.39 |
| mid | 4.0% | 2022→2025 rebuilt-EPS CAGR 3.2% (2.3); 2026 run-rate +14% (9M, M3Q) and broker 2026F +4–5% (IVX, HV); card spending +4.7% vs industry ≈0% with share gains (M25, TS); cost of funds 2.62% and falling | payout stays ≈59%; credit cost 5–5.5%; no ceiling cut; book grows 1–2% a year as targeted (M25) |
| good | 6.0% | 2018→2025 and 2019→2025 rebuilt-EPS CAGR 6.1% / 5.9% (through COVID and the 2020 cap cut); self-funded capacity ROE 19% × (1 − 0.59) ≈ 7.8%; KTB Leasing drag (≈0.2/share) fades | book growth returns to 4–5% (the 2025 target that was missed: +0.4% vs 4–5%, M25); NPL stays ≤2%; household-debt cycle turns |

The 10-year rate of 14.1% (FS A3 / 2.3) is rejected as a scenario: its base is the 2013–2018 era of 20–56% profit growth, ROE 26–35% and a growing industry; the industry has been flat since 2023 (TRIS, M25). FS A4 today uses rule-based 7.7 / 8.9 / 10.0% (cap 10%) because `config.json` has no KTC entry — superseded once Art decides.

### 4.2 ก. Lump: DPS in year N ÷ cost — cost = today's price and the three ladder levels (section 7)

| scenario | growth | year | DPS | @35.00 (today) | @29.50 (step 1) | @27.00 (step 2) | @24.50 (step 3) |
|---|---:|---:|---:|---:|---:|---:|---:|
| bad | 0.0% | 5 | 1.770 | 5.1% | 6.0% | 6.6% | 7.2% |
| bad | 0.0% | 10 | 1.770 | 5.1% | 6.0% | 6.6% | 7.2% |
| bad | 0.0% | 15 | 1.770 | 5.1% | 6.0% | 6.6% | 7.2% |
| bad | 0.0% | 20 | 1.770 | 5.1% | 6.0% | 6.6% | 7.2% |
| mid | 4.0% | 5 | 2.153 | 6.2% | 7.3% | 8.0% | 8.8% |
| mid | 4.0% | 10 | 2.620 | 7.5% | 8.9% | 9.7% | 10.7% |
| mid | 4.0% | 15 | 3.188 | 9.1% | 10.8% | 11.8% | 13.0% |
| mid | 4.0% | 20 | 3.878 | 11.1% | 13.1% | 14.4% | 15.8% |
| good | 6.0% | 5 | 2.369 | 6.8% | 8.0% | 8.8% | 9.7% |
| good | 6.0% | 10 | 3.170 | 9.1% | 10.7% | 11.7% | 12.9% |
| good | 6.0% | 15 | 4.242 | 12.1% | 14.4% | 15.7% | 17.3% |
| good | 6.0% | 20 | 5.677 | 16.2% | 19.2% | 21.0% | 23.2% |

Growth needed from 1.77 (FS A4 "required growth", facts): at 35.00 → 7% in year 5 = 6.7%/yr, year 10 = 3.3%/yr, year 20 = 1.6%/yr · 12% in year 10 = 9.0%/yr, year 20 = 4.4%/yr · at 27.00 → 7% in year 10 = 0.7%/yr; 12% in year 10 = 6.2%/yr.

### 4.3 ข. New money bought monthly for 10 years then held — dividend in year N ÷ all money invested (FS A4 DCA rule) · at today's price 35.00

| scenario | growth | year 5 grows / flat | year 10 grows / flat | year 15 grows / flat | year 20 grows / flat | avg buy yield needed for 7% / 12% in year 10 |
|---|---:|---|---|---|---|---|
| bad | 0.0% | 5.1% / 5.1% | 5.1% / 5.1% | 5.1% / 5.1% | 5.1% / 5.1% | 7.00% / 12.00% |
| mid | 4.0% | 5.6% / 6.2% | 6.2% / 7.5% | 7.5% / 9.1% | 9.2% / 11.1% | 4.73% / 8.11% |
| good | 6.0% | 5.9% / 6.8% | 6.9% / 9.1% | 9.2% / 12.1% | 12.3% / 16.2% | 3.91% / 6.70% |

Read (facts): new money at today's 5.06% yield stays at 5–7% for the first decade in every scenario except "good + flat price"; the second decade (years 15–20, no new buying) is where the mid/good cases move into double digits. "Price flat" is identical to the lump at 35.00.

### 4.4 ค. The case below "bad" — payout reverts to the 2015–2024 range (ours, for D4/D15 B1, not a scenario in config)

DPS = 45% × EPS 3.02 = **1.36** (−23%), then grows at the mid rate 4%: year 5 1.66 (4.7% of 35.00), year 10 2.01 (5.8%), year 20 2.98 (8.5%). On the policy floor of 40%: 1.21 (3.5%) today. This single decision by the board moves the year-10 number by more than the whole bad→good spread — it is the first thing to watch (section 6, T3-payout).

### 4.5 Numbers still unknown that would move the answer
- Why the FY2025 effective tax rate was 27.7% (vs 20.3%): a one-off would put normal EPS near 3.3 and payout near 54% — not found in M25/IVX.
- Whether the board intends 59% as the new payout (no statement found; brokers assume it). First evidence: FY2026 dividend, board ~Feb 2027, AGM ~Apr 2027.
- The BOT's decision on the 10% minimum payment for 2027 (due before 31 Dec 2026, BOTMP) and any move on the 16% ceiling.
- AEONTS D/E, NPL and credit cost for the T6 peer line.
- FY2026 Q4: KTC targets FY2026 profit > 7,782 m (M3Q); 9M is already 6,521 m, so FY2026 ≈ 8.5–8.7 bn (+9–12%) if Q4 ≈ 2.0–2.1 bn — ours, from the run-rate.

---

## 5. อะไรทำให้พัง — เรียงตาม โอกาสเกิด × ความเสียหายต่อปันผล

### 5.1 Belief table (D15 — C12 "avoid being fooled by the story") · "a guru holds it" is not among the reasons

| # | what we want to believe (1 sentence) | strongest counter-evidence + source + date | what proves it wrong (→ flag in section 6) |
|---|---|---|---|
| B1 | "1.77 is the new floor — KTC has moved to a 59% payout for good." | Policy says only "ไม่ต่ำกว่าร้อยละ 40" (F56 7.4, AGM 25 Mar 2003); payout was 40–46% for ten years FY2015–2024 (2.3); FY2025 EPS +4.6% vs DPS +34% (M25, AGM26 3 Apr 2026); no board statement on a new payout found; brokers' 59% is an assumption (IVX 27 Mar 2026) | T1: FY2026 DPS < 1.77 · T3-payout: DPS falls while normal EPS rises (= payout reverted) |
| B2 | "KTC is a growth lender — EPS compounds at 14%/yr (FS A3)." | Base year 2015 = start of the 2013–2018 boom (ROE 26–35%); 2018→2025 CAGR 6.1%, 2022→2025 3.2% (2.3); receivables 111.2 bn (2024) → 107.7 bn (9M26) (M25, M3Q); industry card receivables −3.7% 11M25, cards −1.9% (M25); 2026 profit growth is ECL −8.9% and finance cost −16.2%, revenue +0.4% (M3Q 20 Oct 2026); 2025 book-growth target 4–5% missed at +0.4% (M25) | T3: revenue growth < 2% for 3 fiscal years and credit cost back ≥ 6% · T2: year-10 mid-case yield < 7% |
| B3 | "NPL 1.9% and coverage 413% make the dividend crisis-proof." | KTC skipped the dividend three times in 2008–2011 and lost money in 2011 (PP; MG12 15 May 2012); group NPL rose 1.79% → 1.92% in 9M26 while coverage fell 425% → 413% (M25, M3Q); lease NPL 17.9–29.3% (M2Q, M25); NCB SM (pre-NPL) 4.3% and rising, NPL 9.75% of tracked household debt (NCB 21 Jul 2026); credit cost swung 4.7% → 6.1% → 5.3% in three years (M25) | T4-lender: coverage < 300% or allowance/NPL < 2.5× · T5: group NPL > 2.5% or credit cost > 7% |
| B4 | "Regulation is already in the price — the 16% ceiling and 8% minimum payment are old news." | 10% minimum payment is scheduled for 1 Jan 2027 and was only deferred, not cancelled (BOTMP 10 Dec 2025, 28 Oct 2026); the BOT cut the ceiling 18% → 16% and PL 28% → 25% in 2020 (TRIS 26 Mar 2025) — it has done it before; responsible-lending and persistent-debt rules extended to 7 years (TRIS timeline); IVX lists "BOT household-debt measures" as a key risk (27 Mar 2026) | T5: a ceiling cut or a minimum-payment step that cuts card interest income > 5% in a year (card interest 7,800 m, M25) |
| B5 | "A 49% state-bank parent makes KTC safe." | The parent sold KTC 75.05% of KTB Leasing (2021, search summary) → lending stopped Aug 2023, NPL 18–29%, ≈0.5 bn drag on 2025 group profit (M25); KTB funds 13.1 bn of KTC's borrowing (M3Q) — a dependency as well as a support; the parent decides the payout (49.29%, AB) | T3-payout as in B1 · a new related-party acquisition announced (person check) |

### 5.2 Non-belief risks — ranked by chance × damage to DPS (facts; judgement is ours)

| # | cause | chance (10 y) | damage to DPS | temporary / permanent | evidence |
|---|---|---|---|---|---|
| 1 | Board returns payout to 40–46% | medium — 10-year habit vs one year at 59%; no stated change | −23 to −32% in one year on flat EPS (4.4) | policy, reversible | F56 · 2.3 |
| 2 | BOT pricing: minimum payment 10% (2027) and/or ceiling cut below 16% | high for the 10% step (scheduled); medium for a ceiling cut | −5 to −10% EPS per step (D4 arithmetic, ours); revolving balances shrink | permanent while the rule stands | BOTMP · TRIS |
| 3 | Credit cycle: NPL > 2.5%, credit cost back to 6–7% | medium-high — SM 4.3% rising (NCB), stage-2 6.78% system (BOTQ), KTC NPL ticking up | −10 to −20% EPS for 1–2 years; DPS held only if payout is allowed to rise | temporary (coverage 413% absorbs first) | NCB · BOTQ · M3Q |
| 4 | Industry shrinks for years: household deleveraging, 8% → 10% repayment, debt consolidation into 5% term loans | high — happening: card receivables −3.7%, cards −1.9% (M25) | EPS flat → "bad" scenario | structural, slow | M25 · TRIS · HH |
| 5 | Funding shock: debenture market closes, cost of funds up 1–2 points | low–medium — AA rating, 64% debentures, 19.9 bn undrawn | +1 point on 53 bn ≈ −0.53 bn pre-tax ≈ −5% EPS | temporary | M3Q · AB |
| 6 | Digital/virtual-bank and BNPL competition for the same prime customers | low first 5 years, rising after | fee and spending share erosion; −5–10% EPS over a decade | permanent, slow | NCB (PL +13.8% partly BNPL) · BBL book VB |
| 7 | A 2008–2011-type cleanup (new management, provisioning overhaul, dividend skipped) | low — TFRS 9 provisioning in place since 2018, coverage 413% | −100% for 1–3 years | temporary but long | 2.5 · MG12 |
| 8 | Core-system upgrade overruns (cost-to-income 36–37% in 2026) | medium — in progress 2Q26 | −3–5% EPS for a year | temporary | IVX |

Summary: what breaks the dividend permanently (2, 4) is regulatory and slow and already partly in motion; what cuts it fast (1, 3) is a board decision or a credit cycle, both reversible. KTC's main risk to a 10–20-year DCA is "the dividend stalls at 1.4–1.8 while the industry is capped", not failure.

---

## 6. ธง "ผิดทาง" เฉพาะ KTC (T1–T6 ปรับให้ผู้ให้สินเชื่อรายย่อย — เลขเกณฑ์ กูตั้ง Art เคาะ)

| flag | lender measure | value today (source) | opens a review | points to "permanent" | watches belief (D16) | where to read |
|---|---|---|---|---|---|---|
| T1 | DPS of fiscal year below prior year | FY2025 1.77 (+34%) — not tripped (FS) · FY2026: board ~Feb 2027 | down 2 fiscal years (FY2026 + FY2027), or a single year below 1.32 (FY2024 level = the pre-jump base) | down 3 years, or any skipped year (2008–11 pattern) | B1, B5 | PP / set.or.th, Feb–Apr each year (one payment) |
| T2 | yield on today's price 35.00 in year 10, mid scenario | FS rule-based mid 8.9% → 11.8% (not tripped) · proposed mid 4% → 7.5%; bad 0% → 5.1% | mid-case projection < 7% ⇔ latest DPS × 1.04^10 < 2.45 ⇔ latest DPS < 1.655 | — | B2 | recompute after each final dividend (fact sheet A4) |
| T3 | why the dividend fell: normal EPS / payout / regulation | normal EPS FY2025 3.02; 9M26 EPS 2.53 (+14.3%, M3Q); payout 58.6% | **T3-payout**: DPS down while normal EPS up (= reversion, B1) · **T3-EPS**: normal EPS down 2 fiscal years with revenue growth < 2% | normal EPS down 3 years not caused by provisions (= pricing rules broke the model) | B1, B2, B5 | quarterly MD&A (ktc.co.th IR; two URL trees in the source table) |
| T4 (lender) | funding and reserves instead of cash flow: coverage, allowance/NPL, D/E, undrawn lines | coverage 413.4%, allowance 8,481 m = 4.1× NPL, D/E 1.32, undrawn 19,880 m vs 9,130 m due (M3Q) | coverage < 300% or allowance/NPL < 2.5× or D/E > 3.0 or undrawn lines < debt due in 12 months | coverage < 150% or a rights issue | B3 | quarterly MD&A |
| T5 | industry: system card receivables, BOT pricing rules, system NPL | industry card receivables −3.7% 11M25, −0.1% Q1/26 (M25, search); minimum payment 8% to 31 Dec 2026 then 10% (BOTMP); ceiling 16%; system NPL 2.82% (BOTQ) | a ceiling cut or minimum-payment step costing > 5% of card interest income (ours) · industry receivables down 3 straight years · KTC group NPL > 2.5% or credit cost > 7% | industry receivables down 5 years with KTC's share flat · ceiling ≤ 12% | B3, B4 | BOT quarterly briefs · BOT announcements (Dec each year) · KTC MD&A industry table |
| T6 (lender) | D/E and credit cost vs peer (AEONTS) | KTC D/E 1.32, credit cost 5.1% (M3Q) · AEONTS: not fetched this round | D/E rising 3 years and above AEONTS · credit cost > peer by 2 points 2 years running | D/E > 5 with coverage < 200% | B3 | half-year: both MD&As (AEONTS FY ends Feb) |

FS flags on 2026-10-28: T1 ✅ not tripped · T2 ✅ not tripped (rule-based mid 8.9%) · C2 ✅ not tripped (year-5 7.7% rule-based; 5.1% on proposed bad) · PAYOUT ✅ 59% · LOSS ✅ none in 10 years (2011 loss is 15 years old, outside the window) · T4/T6 not computed by the sheet for the bank profile (replaced here). Next data: FY2026 results ~mid Jan 2027 (KTC reports in the third week of January, M25) · final dividend board ~Feb 2027, XD ~Apr 2027 · BOT minimum-payment decision before 31 Dec 2026.

---

## 7. ราคาตอนนี้ — เทียบประวัติตัวเอง (ราคาปิดจริง) + เทียบคู่ · ข้อเท็จจริงให้คน DCA คิด ไม่ใช่คำสั่ง

- Close 35.00 on 2026-10-27 (FS, Y) · 52-week 24.80 (13 Jan 2026) – 40.50 (20 Jul 2026) (Y) → 14% below the high, 41% above the low · month-end closes (Y, real, not dividend-adjusted): 2024 Dec 50.00 · 2025 May 38.50 → **Jun 24.00** (the 23 Jun 2025 fall: company said no fundamental change, IQ25; 16.3% of shares were margin collateral, S2T) → Jul 28.50 · Sep 30.00 · Dec 26.25 · 2026 Feb 33.25 · Apr 29.25 · Jul 38.25 · Sep 34.50 · Oct 35.00.
- Own history (FS A10, year-end closes): 2016–2022 the stock was a growth stock — year-end PE 14–29, yields 1.5–2.9%, 2021 high 83.00 (Y); 2023 PE 15.3, 2024 17.4, 2025 **8.7** (26.25), today 11.6. The FS "cheap vs itself" label (yield at the 90th percentile) is therefore a de-rating signal: the market now prices KTC as a 5%-yield, low-growth lender, which is what sections 2–5 describe. PBV 1.96 (FS rows 2016–2017 of 0.36/0.41 are a cache artefact — section 10).
- Peers (2.4): highest ROE and PBV, mid-pack PE and yield; AEONTS is cheaper on every ratio with half the ROE.
- Brokers: TP 31 (IVX Neutral, Mar 2026) · 36 (KGI) · 39 (Krungsri) · 40 (Phillip) (HV, May 2026) · consensus average 35.67, range 26–44 (CONS). Today's price = consensus. No post-Q3/26 target found.
- "Another 20–30% down" (ours, D14): 28.0 / 24.5 → 6.3% / 7.2% on 1.77.

### Cheap levels (for the cash-ammo step if it enters the portfolio) — shaped like the F5 ladder in `roadmap/agreed-portfolio-framework.md` (yield on the last full-year dividend 1.77; real closes; levels = ours, Art decides)

| step | price | yield on 1.77 | PE on EPS 3.02 | PBV on 17.8 | where it sits in KTC's own history (Y real closes) |
|---|---:|---:|---:|---:|---|
| 1 | ≤ 29.50 | 6.0% | 9.8 | 1.66 | the Oct 2025 – May 2026 trading zone (month-ends 26.25–30.00); −16% from today; first level where PE < 10 (P3 line, weak evidence) |
| 2 | ≤ 27.00 | 6.6% | 8.9 | 1.52 | Aug/Nov/Dec 2025 month-ends (27.25 / 27.25 / 26.25); the 2025 year-end close 26.25 = PE 8.7 |
| 3 | ≤ 24.50 | 7.2% | 8.1 | 1.38 | the 2025–26 trough: 24.00 (30 Jun 2025 close), 24.80 (13 Jan 2026, 52-week low); never lower since 2020 (year low 23.80) |

Guards, same as F5: one third of the ammo per step · only when the fall is market/sentiment (23 Jun 2025 type), not when a review is open (T1/T3-payout/T5 in section 6) · monthly DCA continues regardless (F4). Yield levels assume DPS stays 1.77 — if FY2026 DPS changes, the price steps move with it (step 1 = DPS ÷ 6.0%, etc.).

---

## 8. น้ำหนักในพอร์ต — ถ้าเข้ามาแล้วโดนพร้อมกลุ่มการเงิน ปันผลรวมหายเท่าไร (facts only, no weight proposed — R5/R6)

- KTC is not in the SSOT and has no weight. For any weight W of the plan: a payout reversion to 45% (risk 5.2 #1) removes ≈ W × 23% of the portfolio's dividend; a 2008–2011-type skip removes W × 100% for the year(s), if every holding yields about the same (arithmetic, ours).
- Correlation fact: BBL, TCAP (via TTB), TISCO and KTC are all BOT-regulated lenders exposed to the same household-debt measures (TRIS timeline; BBL book section 8). In 2020 BBL cut 64% by BOT order while KTC held flat — the same shock did not hit the two the same way, because the 2020 order covered commercial banks (BOT20 in the BBL book) and KTC's hit came through the pricing rules instead.
- No proposal to add or size — Art's intent (D17). Facts only.

---

## 9. สิ่งที่ algo ควรเตรียมเพิ่มสำหรับหุ้นกลุ่มนี้ (รอบนี้ต้องหามือ)

- `data/manual_facts/KTC.json` written this round (founded/listed, dividend policy verbatim, `lender_table` 2022–9M26 with receivables / ECL / credit cost / NPL by product / coverage / allowance / D/E / cost of funds / NIM / ROE / ROA / tax rate, crisis years, 2026 regulation, Q3/26 status, holders) and the fact sheet re-run (`fact_sheet.py KTC --refresh`): the sheet now prints the keys as-is in "ต้องกรอกมือ" (`_manual`). Git-ignored (`.gitignore` line 5: `data/`).
- The sheet maps KTC to `sector_profile: bank` — correct for A6/A7/T4 suppression, but the manual slot is named `bank_table` in BBL's file and `lender_table` here; the sheet prints either (no computation). If the head wants one name, rename in the JSON only.
- Cache fixes to request (not done here — no script edits): FS A5 2014 EPS 2.44 (should be 0.68) · FS A5 2025 net profit 7,668 (company: 7,782) · A10 PBV 2016–2017 (0.36/0.41 impossible at those prices) · A1 rows 2002–2007 (yahoo pay-year tagging).
- Still manual every round: MD&A PDFs (two URL trees on ktc.co.th; Company-Highlight PDFs return XML errors) · BOT minimum-payment/ceiling announcements (December) · NCB and BOT quarterly briefs for T5 · AEONTS numbers for T6.
- Not done: AEONTS peer fetch · historical DCA backtest · Q2/2026 household-debt figure · the FY2025 tax-rate cause (needs the audited notes, not the MD&A).

## 10. จุดที่ของเดิมใน `research/` กับใบข้อเท็จจริง ผิด / เก่า

| # | file:line / section | says | actual (source) | type |
|---|---|---|---|---|
| 1 | FS A5 row 2014 · FS A3 "กำไรต่อหุ้นโต 10 ปี 14.2%" · KOC section 3 | EPS 2014 = 2.44; KOC: "EPS series has breaks … likely par split / share change — growth figure not trusted" | 2014 EPS = 1,755 m ÷ 2,578.3 m = **0.68**; the series is otherwise on a consistent post-split basis (the 10:1 split was 2018-07-13, Y) — the 2014 cell alone is a cache error. The 10-y CAGR 2015→2025 happens to be unaffected (base 2015 = 0.80 is right) and equals 14.1% on the rebuilt series — valid arithmetic, wrong base era (section 2.3, 4.1). KOC's doubt was right about the cell, wrong about the cause. | data error + corrected reading |
| 2 | FS A5 row 2025 | net profit 7,668 m | 7,782 m to parent, 7,559 m group (M25, AGM26); EPS 3.02 in the same row is correct | data error (one cell) |
| 3 | FS A10 rows 2016–2017 | PBV 0.36 / 0.41 | impossible at 13.80 / 18.60 (equity ≈ 10–12 bn ÷ 2,578 m shares ≈ 4–5/share → PBV ≈ 3–4); pre-split book value against a split-adjusted price — not used; 2018+ rows plausible | data error |
| 4 | FS A1 rows 2002–2007 | 0.0346 / 0.07 / 0.2144 / 0.20 / 0.15 / 0.12 | PP per-share (÷10): 0.055 / 0.07 / 0.13 / 0.15 / — / 0.12 — yahoo tags by pay year and adjusts differently before 2008; FS A2 "cuts in 2005–2007" are therefore not verified; the FS "paid 14 years" (FY2012–25) is right | unverified / not used |
| 5 | FS A4 scenarios bad 7.7 / mid 8.9 / good 10.0% | rule-based on cache EPS windows (5-y 7.7%, 10-y 14.2% capped) | superseded by earnings-based 0 / 4 / 6% (section 4.1) pending Art; T2/C2 flags on the FS use the rule-based set | superseded |
| 6 | KOC section 3 "DCA y10 mid (rule-based) 8.0% / 11.8%" | rule-based | 6.2% / 7.5% on the proposed mid 4% (4.3) — KOC's own caveat ("not apples-to-apples") applies | superseded |
| 7 | FS "จ่ายปันผลไม่ขาด 14 ปี" + A2 crisis table "2008 / 2009 / 2011 ไม่มีข้อมูล" | no data | no dividend FY2008, FY2009, FY2011 (PP; Y pay-date gaps) and a loss in 2011 — the "no data" cells are real gaps in payment, not missing data | corrected reading |
| 8 | KOC section 3 "ROE 24% → 18.5%" | — | confirmed (M25: 24.3% → 18.5%); 9M26 annualised 19.3% (M3Q) | confirmed |
| 9 | KOC "Q2/26 2,225 m vs 1,895 m (+17%)" | — | confirmed (M2Q: +17.4%); Q3/26 2,125 m +8.9% is new | confirmed + updated |

---

## ค่าที่ต้องจดลง config (NOT written — awaiting Art)

The head writes this into `config.json` (this job does not touch it). Form follows `docs/deep-dive.md` step 3 (value + `_source` + `_as_of`). After writing, re-run `fact_sheet.py KTC --refresh` so A3/A4/A12 and the T2/C2 flags pick the values up.

```json
{
  "normal_eps": {
    "KTC": {
      "2025": 3.02,
      "2024": 2.88,
      "_source": "research/ktc-deep-dive-2026-10-28.md section 2.3 — FY2025: reported EPS 3.02 (net profit to parent 7,782 m / 2,578.334 m shares, KTC MD&A FY2025 15 Jan 2026 + AGM news 3 Apr 2026); nothing stripped: ECL 5,906 m and bad-debt recoveries 4,038 m are recurring, KTB Leasing losses (~0.2/share) are real and fading, no asset sale / revaluation / equity gain found; effective tax 27.7% (vs 20.3% FY2024) unexplained in the MD&A — if a one-off, normal EPS ~3.3 (not applied). FY2024: reported EPS kept, nothing exceptional identified. Cache cell 2014 EPS 2.44 is wrong (0.68)",
      "_as_of": "2026-10-28"
    }
  },
  "holdings": {
    "growth_scenarios": {
      "KTC": {
        "bad": 0.0,
        "mid": 0.04,
        "good": 0.06,
        "source": "research/ktc-deep-dive-2026-10-28.md section 4.1 — earnings-based on rebuilt EPS (net profit / 2,578.334 m shares): 2022->2025 CAGR 3.2%, 2018->2025 6.1%, 2019->2025 5.9%; the 10-y 14.1% (base 2015 = 2013-2018 boom era) rejected; 2020 base (COVID + cap cut) rejected. bad = flat EPS while the industry shrinks (BOT card receivables -3.7% 11M25) and credit cost normalises; mid = recent CAGR + 2026 run-rate (+14% 9M) + broker 2026F +4-5%; good = post-2018 CAGR, within self-funded capacity ROE 19% x (1-0.59). ALL assume payout stays ~59%; on the 40-46% policy-era payout DPS falls to 1.21-1.39 first (section 4.4)",
        "as_of": "2026-10-28"
      }
    }
  }
}
```

`special_dividends`: none for KTC — one regular payment per fiscal year, every panphol row FY2545–FY2568 labelled "เงินปันผล" (section 2.1).

---

## acceptance (ไล่ทีละข้อ)

- every D1–D18 answered with fact-sheet section or external source + date → section 3, each row has an evidence column with FS section codes and source codes dated in the source table.
- D1 has normal EPS FY2025 with what was removed and why → section 3 D1 + 2.3 (removed: nothing; checked and kept: ECL, bad-debt recoveries, KTB Leasing losses; tax rate noted as unexplained and not adjusted).
- D2 has a numeric year-5 DPS from an earnings-based rate plus obstacles → section 3 D2 + 4.1/4.2 (1.77 / 2.15 / 2.37 at 0 / 4 / 6%), with the payout-floor variant.
- D4 uses A2 + crisis history + the lender table → section 3 D4 (FS A2 A5 A12, table 2.2/2.5, F56 policy floor, regulation arithmetic → `manual_facts`).
- D15 has ≥2 beliefs each with sourced counter-evidence and a falsifier tied to a T-flag → section 5.1 (B1–B5).
- D16 maps every flag to a D15 belief → section 6 column "watches belief"; every belief appears in at least one flag row.
- Non-belief risks (regulation: BOT minimum payment / interest ceiling / household debt) sit in section 5.2, not in the belief table.
- D18 = "n/a — AMATA only" → section 3 D18.
- Real closing prices used throughout (Y `auto_adjust=False`; FS A10 year-end closes); no dividend-adjusted prices.
- DPS cross-checked across ≥2 sources for every year used (2.1: FS, PP, Y agree FY2012–FY2025; earlier rows flagged and not used).
- Q3/2026 and 9M/2026 results checked and used (M3Q, TS, NW, TP — 20–21 Oct 2026).
- Section 4 reports y5/y10/y15/y20 for DCA at today's price in both price modes and the lump view at today's price (plus ladder levels), all 3 scenarios; no verdict on 7–12%.
- Cheap levels section present with three steps shaped like F5, on real closes, with guards.
- Values for config present (normal_eps with reasoning, growth_scenarios with reasoning, special_dividends = none); not written to `config.json`.
- `data/manual_facts/KTC.json` written in BBL's shape (founded/listed, policy, `lender_table`, crisis, regulation, book) — git-ignored; fact sheet re-run and prints it.
- No script, no `config.json`, no `rebalance.py` touched; no commit.
- Not met / open: AEONTS peer line for T6 (not fetched); FY2025 tax-rate cause; Q2/2026 household-debt figure; 2011 loss amount is cache-only; LHB market-share metric unnamed in the extract.
