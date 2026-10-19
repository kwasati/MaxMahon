# AMATA deep dive 2026-10-19 — "hold and keep buying this every month for 10 more years: still on the right track?"

- Created 2026-10-19 · job job-12-dd-amata (desk z79h) · Niwes leg, 35% plan weight · holding 32,400 shares at average cost 26.40 (config.json holdings)
- Reference price 32.25 baht = close of 2026-10-15 per the fact sheet FS (yahoo closes 9–19 Oct 2026: 31.50 / 31.50 / 32.00 / 32.25 / 32.25 intraday 19 Oct)
- Written under the corrected principles (docs/deep-dive.md 2026-10-19): growth rates are earnings-based (normal EPS), base years checked, C2 tested for every stock, D15 belief table with falsifiers · the owner's 7–12% yield-on-cost target is parked: A4 / DCA numbers are reported as facts, no conclusion on whether the target is reached
- Format follows the 10-section layout of research/amata-deep-dive-2026-10-09.md; no number or conclusion was carried over without re-checking (section 10 lists what changed)
- Every Niwes reference = docs/niwes-principles.md (codes C/Q/P/F/H/X · T1–T6 · D1–D18). Niwes never spoke about AMATA or industrial estates; every judgement on AMATA here is ours, standing on his general rules only
- Labels: `number` = answered from figures · `person` = our judgement · `guess:` = not proven · "not found" written where a source was unreachable

## Source codes (used throughout)

| Code | Source | Data as of | Fetched |
|---|---|---|---|
| FS | System fact sheet reports/holdings/AMATA_2026-10-19.md (`fact_sheet.py AMATA --cost AMATA=26.40`, price 32.25 close 2026-10-15) — A1–A12, flags | FY2025 + FY2026 interim | 2026-10-19 |
| FS2 | Same fact-sheet code re-rendered with the growth scenarios of this book (scratch `_desk/maxmahon/z79h/files/amata_scen.py 0.0 0.05 0.09` → `amata_scen_0.0_0.05_0.09.md`) — A4 lump + DCA tables, flags | FY2025 | 2026-10-19 |
| OR | 56-1 One Report 2025 (English) https://amata.listedcompany.com/misc/one-report/20260327-amata-one-report2025-en.pdf — 306 pages, text extracted with pypdf; page numbers = printed page numbers | FY2025 (31 Dec 2025) | 2026-10-19 |
| DK | 9M-2025 results deck hosted by SET https://api.lcp.setgroup.or.th/file/presentation/8951 — EPS chart 2019–2024, land bank 30 Sep 2025, backlog, transfers | 30 Sep 2025 | 2026-10-19 |
| DK17 | FY-2017 results deck (company) https://static.seekingalpha.com/uploads/sa_presentations/416/23416/original.pdf — net profit after MI FY2016 / FY2017 | FY2017 | 2026-10-19 |
| IR | investor.amata.com/en/shareholder-info/dividend-information — dividend policy (full text) + payment table FY2008–FY2026 interim | 26 Aug 2026 XD | 2026-10-19 |
| IRH | investor.amata.com/en/financial-info/financial-highlights — revenue / net profit / EPS 2022–2025 + 6M2026 | 6M2026 | 2026-10-19 |
| PP | aio.panphol.com/stock/AMATA/dividend (curl + table parse) — payment rows 2555–2569 | 26 Aug 2026 | 2026-10-19 |
| Y | yahoo via yfinance (`_desk/maxmahon/z79h/files/amata_probe.py` → `amata_probe_out.txt`) — annual 2022–2025, quarterly to Q2/2026, prices, dividends, AMATA / WHA / ROJNA / AMATAV | Q2/2026 (30 Jun 2026) | 2026-10-19 |
| SC | Screener cache data/screener_cache/2026-10-19/AMATA.BK.json (`yearly_metrics`, thaifin/SETSMART) — revenue, net profit, EPS, OCF, capex 2010–2025 | FY2025 | file 2026-10-19 |
| R1 | ryt9/InfoQuest 2026-08-14 https://www.ryt9.com/s/iq/12836783 — Q2/2026 and 6M2026 net profit + EPS (SET filing summary) | Q2/2026 | 2026-10-19 |
| PR | Company press release 2026-08-21 via thaipr.net/?p=3752779 — Q2/H1 2026 revenue by segment, transfers 288 / 594 rai, gain 366 million | Q2/2026 | 2026-10-19 |
| PI | Pi Securities via kaohooninternational.com/markets/589262 (2026-08-24) — normalized profit 2Q26 / 1H26, presale 378 rai, backlog >18 bn | Q2/2026 | 2026-10-19 |
| IVX | InnovestX notes 2026-05-20 and 2026-08-24 (innovestx.co.th cafeinvest) — presale, backlog split TH/VN, 2026 forecasts | Q2/2026 | 2026-10-19 |
| KB | Kasikorn Securities via news.trueid.net/detail/Xlo05ZzPmjPy (2026-07-21) — 2026 target split TH 1,650 / VN 550 / Laos 600 rai, 1H26 sales 378 rai | Q2/2026 preview | 2026-10-19 |
| HV | hoonvision.com (2026-05-21) — Q1/2026: backlog 19,704 million, presale 106 rai, transfers 306 rai, avg price 8.12 million/rai | Q1/2026 | 2026-10-19 |
| BB | bangkokbiznews.com/finance/stock/1247395 (2026-08-14) — Q2/H1 2026 segment revenue, Bualuang target 40 | Q2/2026 | 2026-10-19 |
| KR | Krungsri Research industrial-estate outlook 2026 (2026-04-27) — IEAT-basis land sales 2025, occupancy, forecast 2026–28, risks | 2025 | 2026-10-19 |
| KF | Knight Frank Thailand manufacturing property H2 2023 / H2 2024 PDFs — serviced industrial land sold/leased 2023 8,867 rai, 2024 12,340 rai | 2024 | 2026-10-19 |
| CO | Colliers via nationthailand.com/business/economy/40067129 (2026-06-07) — Q1/2026 absorption 1,914 rai | Q1/2026 | 2026-10-19 |
| BOI | InfoQuest 2026-07-23 (infoquest.co.th/?p=620662) — BOI applications H1 2026 | H1 2026 | 2026-10-19 |
| MH | mitihoon.com/?p=367276 (2023-03-01) — broker note: 2022 ordinary profit 1,177 million vs reported 2,341 million | FY2022 | 2026-10-19 |
| SH | Shareholder list: aio.panphol.com/stock/AMATA/sholder (27 Aug 2026) + OR p.58 (30 Dec 2025) | 2026-08-27 | 2026-10-19 |
| WS | Web search snippets only (not opened): CBRE 2026 outlook "WHA + Amata ~3,200 rai transfers in 2026, normalization" · US tariff 19% framework 26 Oct 2025, ART talks final stage Oct 2026 · 2022 gain on 8 RBF units 455 million | — | 2026-10-19 |

Unreachable this round (status): investor.amata.com annual-report / presentation / company-profile pages (HTTP 500 / 404) · 2015 Annual Report PDF (sustainabilityreports.com 403, no other mirror) · kaohoon.com, bangkokpost, cbre.co.th, colliers.com (403) · set.or.th API (Incapsula 403) · gurufocus / stockanalysis (history only from 2021) → FY2015 primary EPS not obtained (see D18)

---

## 1. One-page answer

**What the data says (no buy / sell order — R6; the 7–12% target is not judged — parked 2026-10-18):**

1. **Yield today is below the 5% rule.** FY2025 DPS 1.10 ÷ 32.25 = 3.4% (FS A10) · 3-year average 2.6% · on the trailing 12 months (0.75 final + 0.60 interim = 1.35) 4.2% (Y). AMATA enters the Niwes frame only through the growth exception (C3), not through C1.
2. **The dividend is paid from normal profit.** FY2025 EPS 2.74 reported; normal EPS 2.73 after removing a 113 million non-recurring tax (+) and a 215 million one-time Vietnam cost reversal (−, our after-tax/minority estimate) (OR p.155–156). Payout 40% = exactly the policy floor approved 28 Feb 2024 (IR).
3. **Earnings growth is 2.5–10%/yr depending on the base year, not the 19% the fact sheet shows.** The FS 10-year EPS CAGR of 19.2% uses FY2015 EPS 0.47 from the cache; that figure is inconsistent with the cache's own attributable profit (1,216 million ÷ 1,067 million shares = 1.14) and with the company's FY2016/FY2017 deck (DK17). Corrected windows: FY2014→2025 2.5% (peak base) · FY2015→2025 9.2% (trough base) · FY2016→2025 10.4% · FY2019→2025 9.0%. We use 0% / 5% / 9% as bad / mid / good (section 4.1), all inside our 10% ceiling.
4. **Year-5 dividend (FY2030) under the mid case = 1.40 baht** → 4.4% of today's price (C2 flag stays on), 5.3% of the 26.40 cost. Good case 1.69 → 5.2% / 6.4%. Bad case 1.10 flat → 3.4% / 4.2% (FS2).
5. **The cycle has already turned down in the order book.** Presale 2024 3,019 rai → 2025 1,234 rai (−59%, OR p.6) → 1H2026 377–378 rai = 13% of the 2,800-rai target (PI, KB, IVX). Backlog 22,307 million (30 Sep 2025, DK) → 18,400 million (30 Jun 2026, IVX). Reported 1H2026 profit is a record (EPS 2.58, R1) because 2024's sales are being transferred now, plus a 366 million disposal gain (PR). Land ready for sale in Thailand was only 1,965 rai at 30 Sep 2025 (DK) against a Thai target of 1,650 rai/yr (KB) — the rest (15,334 rai) is raw land needing capex.
6. **Dividend history is cyclical, not a straight line:** 25 years paid without a gap, 6 cuts ≥10% in 2006–2020, the 2014 peak (0.70) was only regained in FY2024 (FS A1/A2). Management did protect the dividend in 2023 and 2025 when sales fell (DPS up while presale down).
7. **Balance sheet: mid-pack, drifting up.** Interest-bearing debt / parent equity 0.87 (FY2025) → 0.90 (Q2/2026); WHA 1.41, ROJNA ≈0.8 (Y). TRIS A- stable (OR). Free cash flow after land purchases went negative again in 1H2026 (−2,428 million, Y) — the pattern that preceded the 2018 and 2020 cuts (FS A7).

**Decisions left to Art + head:** (a) accept 0 / 5 / 9% as the earnings-based scenarios (or set others); (b) whether the C2 flag (year-5 dividend < 5% of today's price in the mid case) changes the DCA plan for new money; (c) whether a 35% single-name weight is still wanted for a stock whose normal cycle cuts the dividend 25–35% roughly once every 4–5 years (section 8); (d) the T2 line: at 5% growth the year-10 yield on the 26.40 cost is 6.8%, just under the system's 7% threshold (FS2 flag).

---

## 2. Fact sheet

### 2.1 Dividend per share by fiscal year — three sources compared (IR vs PP vs yahoo in FS A1)

Method: interim (XD Aug–Dec of year N) + final (XD Apr–May of N+1) = FY N. yahoo values in FS A1 are adjusted ×0.9919 (0.4464 = 0.45). PP rows before 2555 not parsed this round (FS A1 carries yahoo back to 2001).

| FY | DPS | YoY | Composition and agreement | EPS (attributable, see 2.2) | Payout |
|---|---:|---:|---|---:|---:|
| 2008 | 0.30 | — | IR 0.20 (27 Nov 08) + 0.10 (13 May 09) · yahoo 0.2976 ✓ | — | — |
| 2009 | 0.10 | −67% | IR 0.10 (20 Jan 10) + "No Dividend" Oct–Dec 09 · yahoo 0.0992 ✓ | — | — |
| 2010 | 0.30 | +200% | IR 0.07 + 0.08 (25 Nov 10) + 0.15 (29 Apr 11) · yahoo 0.2976 ✓ | — | — |
| 2011 | 0.40 | +33% | IR 0.04 + 0.11 (29 Dec 11) + 0.25 (30 Apr 12) · yahoo 0.3968 ✓ | 0.87 (932 ÷ 1,067) | 46% |
| 2012 | 0.55 | +38% | IR 0.25 (23 Nov 12) + 0.30 (29 Apr 13) · PP ✓ · yahoo 0.5456 ✓ | 1.35 | 41% |
| 2013 | 0.50 | −9% | PP 0.25 (25 Nov 13) + 0.25 (29 Apr 14) · IR lists only the final · yahoo 0.4960 ✓ | 1.42 | 35% |
| 2014 | 0.70 | +40% | PP 0.20 (25 Nov 14) + 0.50 (28/29 Apr 15) · IR lists only the final · yahoo 0.6943 ✓ | 2.08 | 34% |
| 2015 | 0.46 | −34% | IR 0.22 (26 Nov 15) + 0.24 (29 Apr 16) · PP ✓ · yahoo 0.4562 ✓ | 1.14 (derived, D18) | 40% |
| 2016 | 0.45 | −2% | PP 0.15 (26 Aug 16) + 0.30 (4 May 17) · IR shows the 0.15 with "period not specified" · yahoo 0.4464 ✓ | 1.12 | 40% |
| 2017 | 0.53 | +18% | IR / PP / yahoo 0.20 + 0.33 ✓ | 1.32 (1,409 ÷ 1,067; cache 1.52) | 40% |
| 2018 | 0.40 | −25% | IR / PP / yahoo 0.23 + 0.17 ✓ | 0.96 | 42% |
| 2019 | 0.45 | +13% | IR / PP / yahoo 0.20 + 0.25 ✓ | 1.63 (DK) | 28% |
| 2020 | 0.30 | −33% | PP / yahoo 0.10 (28 Aug 20) + 0.20 (22 Apr 21) · **IR table omits the Aug 2020 interim** | 1.02 (DK) | 29% |
| 2021 | 0.40 | +33% | PP / yahoo 0.10 + 0.30 · **IR prints the final as 0.03 (typo for 0.30)** · OR p.6 dividend paid 344.99 million = 0.30 × 1,150 | 1.22 (OR) | 33% |
| 2022 | 0.60 | +50% | IR / PP / yahoo 0.20 + 0.40 ✓ · OR dividend paid 575.00 million | 2.04 (OR) | 29% |
| 2023 | 0.65 | +8% | 0.25 + 0.40 ✓ all three · OR 747.49 million | 1.64 (OR) | 40% |
| 2024 | 0.80 | +23% | 0.25 + 0.55 ✓ all three (IR XD final 27 Feb 25, PP 13 May 25 — payment 29 May 25 both) · OR 747.43 million | 2.15 (OR) | 37% |
| 2025 | **1.10** | +38% | 0.35 (26 Aug 25) + 0.75 (5 May 26) ✓ all three · OR 1,034.92 million | 2.74 (OR) | 40% |
| 2026 interim | 0.60 | interim +71% vs 0.35 | XD 26 Aug 26, paid 10 Sep 26 (IR, PP, yahoo) · **incomplete year, not compared with full years** | 1H 2.58 reported / ≈2.21–2.34 normalized (R1, PI) | — |

Reading: 2 source errors found again (IR FY2021 final 0.03; IR missing FY2020 interim) — every year still agrees on at least two sources (DC-1). Dividend CAGR by window (FS A3): 5y 29.7% (base FY2020 = COVID trough, not usable) · 10y 9.2% (base FY2015 trough) · 15y 9.1% (base FY2010 post-crisis) · 20y 2.7% (base FY2005 normal) — the long window is the honest one for dividends; the forward rates in section 4 are earnings-based anyway.

### 2.2 Revenue, profit, cash (million baht)

Net profit = attributable to owners of the parent. SC `net_income` 2010–2021 is attributable (DK17 confirms 2016 = 1,198 and 2017 = 1,409 exactly); SC `diluted_eps` before 2021 is not reliable (see D18). EPS column below = OR/DK where available, otherwise net profit ÷ shares (1,067 million to 2019, 1,150 million from 2020 — OR p.38, Y).

| Year | Revenue (SC) | Net profit attrib. | EPS used | EPS in cache | OCF | capex | OCF − capex | Dividend paid | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2011 | 3,748 | 932 | 0.87 | 0.45 | 1,942 | 2,883 | −941 | ~427 | flood year — DPS not cut |
| 2014 | 7,406 | 2,224 | 2.08 | 2.08 | 2,867 | 1,577 | 1,290 | ~747 | peak of the previous cycle |
| 2015 | 5,170 | 1,216 | 1.14 derived | **0.47** | 1,160 | 2,388 (sign wrong in SC) | −1,228 | ~491 | revenue −30%, profit −45% |
| 2016 | 4,484 | 1,198 | 1.12 | 1.11 | 1,648 | 2,027 | −379 | ~480 | |
| 2017 | 4,491 | 1,409 | 1.32 | 1.52 | 1,185 | 2,826 | −1,641 | ~566 | |
| 2018 | 4,354 | 1,018 | 0.95 | 0.96 | 1,871 | 3,017 | −1,146 | ~427 | DPS −25% |
| 2019 | 5,914 | 1,742 | 1.63 | 1.63 | 2,400 | 3,308 | −909 | ~480 | |
| 2020 | 4,202 | 1,103 | 1.02 (DK) | 1.02 | 1,137 | 3,766 | −2,629 | ~345 | DPS −33% · capital 1,067 → 1,150 million shares |
| 2021 | 5,097 | 1,402 | 1.22 | 1.22 | 2,395 | 1,410 | 986 | 345 (OR) | |
| 2022 | 6,502 | 2,341 | 2.04 | 2.04 | 3,057 | 515 | 2,542 | 575 (OR) | includes one-off gains ≈1.16 bn (MH, WS) — normal ≈1,177 |
| 2023 | 9,517 | 1,885 | 1.64 | 1.64 | 8,609 | 1,481 | 7,129 | 747 (OR) | gain on investment property 72 million |
| 2024 | 14,724 | 2,467 | 2.15 | 2.16 | 10,167 (Y) / 9,870 (SC) | 642 | 9,525 | 747 (OR) | gain on investment property 44 million |
| 2025 | 14,281 (14,524 total, OR) | 3,149 | 2.74 | 2.74 | 8,735 (Y) / 8,593 (SC) | 903 | 7,832 | 1,035 (OR) | non-recurring tax 113 · VN cost reversal 215 · FX loss 131 |
| 1H2026 | 7,571 (Y: 3,945 + 3,627) · 8,064 total (PR) | 2,962 (R1) | 2.58 | — | 2,571 | 4,998 | **−2,428** | 862 (final FY2025) | gain 366 on Long Thanh 2 disposal (PR, Y) · normalized 2,541 (PI) |

Reading: 2015–2020 the group spent more on land than it generated after capex for six years in a row and still paid a dividend (cut in 2015, 2018, 2020). 2023–2025 cash was abundant because customers prepay (OCF/net profit 2.7–4.6×). 1H2026 the land-buying phase restarted (Q2 capex 4,786 million, Y) — the first half of the same pattern.

### 2.3 Recurring income vs land sales

| | FY2024 | FY2025 | Q2/2026 | 1H2026 | Source |
|---|---:|---:|---:|---:|---|
| Real estate (land) sales | 9,004 | 8,703 | 2,206 | 4,692 | OR p.155 · PR |
| Utilities | 4,779 | 4,545 (−4.9%, VN electricity) | 1,154 (+3.9%) | 2,355 | OR · PR |
| Rental (ready-built factories) | 940 | 1,034 (+9.9%) | 266 (+4%) | 525 | OR · PR |
| Recurring share of revenue | 38% | 40% (OR p.63 states 40%) | 35% | 36% | computed |
| Gross margin: land / utilities / rental | 38.2% / 16.9% / 77.0% | 54.4% / 18.2% / 77.9% | 66.2% land (PR) | 49.3% total (PR) | OR p.155 |

Recurring gross profit FY2025 ≈ 4,545 × 18.2% + 1,034 × 77.9% ≈ 1,634 million. The dividend paid in 2025 was 1,035 million, SG&A 1,756 million, finance cost 664 million (OR p.155). **Recurring gross profit alone does not cover opex + interest + dividend** — the dividend needs land sales every year; "recurring 40%" is a revenue share, not a dividend floor (feeds D4, D15 belief 2).

### 2.4 Debt vs peers

| | AMATA 31 Dec 2025 | AMATA 30 Jun 2026 | WHA 30 Jun 2026 | ROJNA 30 Jun 2026 | Source |
|---|---:|---:|---:|---:|---|
| Interest-bearing debt | 20,401 | **23,285** | 52,927 | 16,884 | Y |
| Net debt | 16,872 | 20,021 | 48,735 | — | Y |
| Parent equity | 23,531 | 25,874 | 37,437 | ≈21,011 (price ÷ P/B) | Y |
| Interest-bearing debt / parent equity | 0.87 | **0.90** | **1.41** | ≈0.80 (yahoo D/E 70.7%) | computed |
| Company definition (÷ total equity incl. minorities) | 0.63 | — | — | — | OR p.158 (2020–2025: 1.03 · 0.86 · 0.61 · 0.68 · 0.62 · 0.63) |
| Total liabilities / parent equity | 1.67 | 1.61 | — | — | FS A6, Y |
| Cash | 2,307 | 1,926 (+1,897 short-term investments) | 3,695 | — | Y |
| Current debt | 5,636 | **8,216** | 15,723 | — | Y |
| Credit rating | TRIS A- Stable (2025) | | | | OR p.65 |

FS A6 identity check: 39,233 liabilities + 23,531 parent equity + 6,891 minorities = 69,654 = total assets (Y) — no ⛔ row in A6.

### 2.5 Crisis years — paid? cut how much? recovered when? (IR, PP, FS A2)

| Episode | DPS before → low | Cut | Back to the old level | Years | EPS path |
|---|---|---:|---|---|---|
| 2008–09 global crisis | 0.55 (2007) → 0.10 (2009) | **−82% over 2 years** | 0.55 in FY2012 | 5 | not in SC |
| 2011 flood | 0.30 (2010) → 0.40 (2011) | no cut (payout 46%) | — | — | 0.87 |
| 2015 FDI slump | 0.70 (2014) → 0.46 | −34% | 0.80 in FY2024 | **10** | 2.08 → 1.14 (−45%) |
| 2018 | 0.53 → 0.40 | −25% | 0.60 in FY2022 | 4 | 1.32 → 0.95 (−28%) |
| 2020 COVID | 0.45 → 0.30 | −33% | 0.60 in FY2022 | 2 | 1.63 → 1.02 (−37%) |
| 2023 EPS −20% | 0.60 → 0.65 | no cut (payout 29% → 40%) | — | — | 2.04 → 1.64 |
| 2025 presale −59% | 0.80 → 1.10 | no cut (+38%) | — | — | 2.15 → 2.74 (transfers lag sales) |

Never a year without a dividend since at least FY2001 (FS A1: 25 years). Two consecutive cuts happened twice (2008–09, 2015–16) — that is the T1 condition, and both times the company kept paying and recovered.

---

## 3. D1–D18 one by one

Labels: `number` / `person` / `number+person` · confidence high = 2+ sources agree.

| # | Answer | Figures, evidence, source + date | Label | Conf. |
|---|---|---|---|---|
| D1 yield ≥5%? paid from normal profit? | **No: 3.4%** (1.10 ÷ 32.25) · 3-yr average 2.6% · TTM 1.35 → 4.2% · **Paid from normal profit**: FY2025 reported EPS 2.74; items removed → normal EPS **2.73**: (+) 113 million non-recurring income tax on a related-party share sale whose 564 million gain sits only in the separate statements (OR p.156) · (−) 215 million one-time reduction of Vietnam land cost after the government took over a road (OR p.155), taken after 20% tax and 72.84% parent share ≈ −125 million (our estimate) · FX loss 131 million left in (recurring in a USD-funded group) · No LOSS year in 10 years (FS flags) · A5 jump years: 2022 (EPS 2.04 incl. ≈1.16 bn one-offs → normal ≈1.02, MH) and 2015 (data error, D18) | FS A10 · OR p.155–156 · Y (2026-10-19) | number+person | high |
| D2 year-5 dividend ≥5% of today's price? | **Mid case: no.** Base FY2025 DPS 1.10, payout held at 40%, EPS growth 0 / 5 / 9% (section 4.1) → FY2030 DPS **1.10 / 1.40 / 1.69** = 3.4% / **4.4%** / 5.2% of 32.25 (FS2) · needs 7.9%/yr to reach 5% of 32.25; 3.7%/yr for 5% of 26.40 · Confidence rests on: 18,131 rai Thai land bank, EEC location, data-centre and electronics buyers (OR, IVX) · Obstacles: presale 2025 −59% and 1H2026 13% of target; only 1,965 rai ready to sell; backlog falling; US tariff / ART still unsigned (WS) · C2 flag ⛔ stays on in the mid case | FS2 · OR p.6 · DK · IVX 2026-08-24 | number+person | medium |
| D3 (yield 2–3%) rising dividends? can profit reach 5% of today's price in 5 years? | DPS up 5 years running (FY2021–25) and the 2026 interim 0.60 > 0.35 · but part of the rise is payout widening: FY2022 payout 29% → FY2025 40% (A12) — of the 0.60 → 1.10 increase, 0.50 total, about 0.29 came from EPS growth at a fixed 29% payout and 0.21 from the payout move (our split) · Earnings must compound 7.9%/yr from a cyclical-peak base to put FY2030 DPS at 1.61 (5% of 32.25) — above our mid case, inside the good case | FS A1 A12 · IR | number+person | medium |
| D4 if business dips, can the dividend hold? | EPS can fall **59.9%** before payout hits 100% (FS A5 tail) · worst real EPS drops: 2015 −45%, 2020 −37%, 2018 −28% (section 2.2) — all inside that headroom · cash at end-2025 covers 2.2 years of the FY2025 dividend with zero profit (FS) · but the dividend was cut in each of 2015/2018/2020 despite headroom — the board cuts with earnings, it does not run payout to 100% · recurring gross profit 1,634 million < opex + interest + dividend (section 2.3) | FS A5 · OR p.155 | number+person | high |
| D5 revenue / profit / dividend streaks, where they broke, why | Revenue up 10 of 15 years, broke in 2025 (−3%) · EPS streak 2 years (2024–25), broke 2023 (−20%: fewer Chonburi transfers, Vietnam mix) · dividend 5 years · breaks 2015 / 2018 / 2020 all = FDI / transfer troughs, each temporary (2–5 years), except the 2014 peak which took 10 years · 2025 revenue dip while EPS rose = margin (land 54% vs 38%), not volume | FS A5 A1 · OR p.155 | number+person | high |
| D6 how old, how big | Founded **6 Mar 1989** as Bangpakong Industrial Park 2 PCL · listed SET **1997** (OR p.4, p.38) → 37 years / 29 years listed · dividend paid 25 years without a gap (FS A1) · market cap 37,087 million at 32.25 (Y) vs WHA 73,538 and ROJNA 11,719 · written to manual_facts | OR · FS · Y | number | high |
| D7 does management look after shareholders? | Policy (full text in manual_facts): "not less than 40 percent of net profits … consolidated … after deducting taxes and … reserves", approved **28 Feb 2024**; earlier wording since 1995/96 "minimum 40% … from the operating performance … depending on economic atmosphere" (IR) · paid vs policy: DPS/EPS 2019–22 = 27–33% (below 40%, old wording), 2023–25 = 40 / 37 / 40% · company's own payout measure (÷ total profit incl. minorities) 30–61% (OR p.169) · dividend raised in 2023 and 2025 when sales fell · dilution: capital 1,067 → 1,150 million in 2020 (OR p.38) · Vikrom Kromadit, 73, is Chairman **and** Acting CEO (OR p.12, p.14) — the "outside chairman" statement in the 2026-10-09 book is not what the One Report shows for 2025 · related-party subsidiary share sale in Q2/2025 (OR p.156) — gain not in consolidated profit, tax was · SEC search on Vikrom / Varisara / Anucha / Chavalit: nothing found (search-level, DC-4) · deals that hurt minorities: none found in the sources opened | IR · OR · SH | person | medium |
| D8a is the industry declining? (industry numbers) | **Cyclical, not declining — but 2025 was down and 2026 is a normalization year.** Serviced industrial land sold/leased (KF basis): 2022 ≈4,456 · 2023 8,867 (+99%) · 2024 **12,340** record · IEAT basis (KR): 2025 6,531 rai (−18%), cumulative occupancy 76.6% · Q1/2026 1,914 rai (+16.7% YoY, five-quarter high, CO) · forecast 2026–28 7,000–7,300 rai/yr ≈ +3–4%/yr (KR); CBRE: WHA + Amata ≈3,200 rai transfers in 2026 "normalization", bigger plots from data centres (WS) · BOI applications 2025 1.88–1.9 trn baht (+67%), H1/2026 1.47 trn (+37%), FDI 1.37 trn (+80%) of which digital 1.12 trn and Singapore-sourced 1.12 trn (BOI) — the 2026 FDI number is dominated by data-centre filings · AMATA's own revenue (A5) fell 3% in 2025 and presale fell 59% — first signal already in | KF · KR 2026-04-27 · CO 2026-06-07 · BOI 2026-07-23 | person | medium |
| D8b what disrupts it easily, already happening? | US tariff: 19% framework (26 Oct 2025), ART talks in final stage Oct 2026, one source cites a 12.5% band (WS — conflicting, unverified) — **happening** · competing FDI destinations Vietnam / Malaysia / Singapore; Thailand IMD rank 30th from 25th (KR) — happening · scarcity of 50+ rai plots in the EEC (KR) — happening · OECD 15% minimum tax eroding BOI value — law-level, effect not yet in numbers · Thailand–Cambodia border (Sa Kaeo estate 7.7% occupancy, KR) — local · water in the East — no 2026 event found · China–US détente removing relocation demand — not happening now | KR · WS | person | medium |
| D9 market leader? why can't rivals catch up? | **No. 2 in Thailand by size** (WHA market cap 2× AMATA) · share of 2024 national sales 3,019 ÷ 12,340 = 24% (KF basis, AMATA presale incl. Vietnam — bases differ); 2025 1,234 ÷ 6,531 = 19% (IEAT basis) · moat = 46,935 rai designed area in Chonburi/Rayong at historical cost (OR p.37), land GPM 54–66%, 1,547 factories as captive utility customers, 72.84%-owned Vietnam platform since 1994 · not a Niwes Q2 monopoly | OR · KF · KR · Y | person | medium |
| D10 cash ample? | **Adequate, not ample.** Cash 1,926 + ST investments 1,897 million vs current debt 8,216 million (Q2/2026, Y) · OCF − capex 2023–25 = 24,486 million vs dividends 2,529 million = 9.7× (OR, Y) · **1H2026 −2,428 million** after 4,998 million of land/capex (Y) · investing outflow 2025 9,102 million vs capex 903 — the rest is land and investments (OR p.157) · TRIS A- | Y · OR | number | high |
| D11 low debt vs industry? | Interest-bearing / parent equity 0.90 (Q2/26) vs WHA 1.41, ROJNA ≈0.80 (Y) · company definition 0.63 (OR) · net debt +3,148 million in 6 months · A6 has no ⛔ row (identity holds) · T6 not flagged (FS) | Y · OR · FS A6 | number | high |
| D12 crises 2008 / 2020: paid? cut? recovered? | Paid every year · 2008–09 cut 82% in two steps, back in 5 years · 2020 cut 33%, back in 2 years · 2011 flood no cut · section 2.5 | IR · PP · FS A2 | number | high |
| D13 hidden assets? | Investment properties: book 7,110 million vs fair value **12,666 million** (OR p.302, p.~195) → ≈5.6 bn pre-tax, ≈4.8 baht/share · raw land 15,334 rai carried in "real estate development costs" 22,989 million at cost (OR p.37, p.~190) ≈1.5 million/rai vs developed Chonburi land quoted 11–14 million/rai (KF Jan 2025) and AMATA's Q1/2026 average selling price 8.12 million/rai (HV) — the gap is large but development cost, timing and tax are unknown: **guess:** sizeable, not quantified · AMATAV 72.84%: market value 1,630 million vs book share ≈4,182 million (Y) — the market prices the Vietnam arm **below** book, the opposite of hidden value · AMATAR stake fair value 411 million (OR) | OR · Y · KF · HV | number+person | low |
| D14 is today's price reasonable? | PE on FY2025 EPS 11.8 (normal 2.73 → 11.8); TTM EPS 4.47 → 7.2, normalized ≈4.24 → 7.6 (Y, PI) — the TTM PE is flattered by a transfer peak + 366 million gain · PBV 1.43 (BVPS 22.50 Q2/26, Y) / 1.64 on FY2025 BVPS (FS) · yield 3.4% below the 5% rule, but FS labels "cheap vs own history" (80th percentile of own year-end yields 2016–25) — that history is 1.8–2.8% in 2017–24, so "cheap vs itself" ≠ passing C1 · 52-week 14.00–34.50 → 89% of the range · a 20–30% drop = 22.6–25.8 baht ≈ the 26.40 cost · P3 "PE < 10" (weak evidence) fails on FY2025, passes on TTM | FS A10 · Y | number+person | high |
| D15 what do we want to believe? | Table in section 5A (4 beliefs, each with counter-evidence + falsifier tied to a T flag) | — | person | — |
| D16 "wrong-track" flags for this stock | Section 6: T1–T6 defined for an industrial-estate developer, each flag mapped to a D15 belief; current state: T1 ✅ · **T2 ⛔ (6.8% < 7% at 5% growth)** · C2 ⛔ · T3 watch · T4 ✅ (but 1H2026 negative) · T5 watch · T6 ✅ (FS2) | FS2 | number+person | — |
| D17 good enough to add? what concentration grows? | Only industrial-estate / cyclical-property name in the plan; the other Niwes-leg names are banks (BBL, TCAP) · 35% in one stock whose normal cycle cuts DPS 25–35% every 4–5 years (section 8) · Art does not use the 5-stock / 5-industry rule (2026-10-19) — reported as a fact, no recommendation | config holdings | person | — |
| D18 (AMATA) lumpy land revenue; is the FY2015 EPS −77% real? | **Data error, not a real −77%.** SC FY2015 EPS 0.4737 × 1,067 million shares = 505 million, but SC's own attributable profit is 1,216 million (= 1.14/share); DK17 proves the SC profit column is attributable (2016 1,198 / 2017 1,409 match the company deck); SC EPS is also off in 2011 (0.45 vs 0.87), 2012 (1.49 vs 1.35), 2017 (1.52 vs 1.32) → the thaifin EPS column before 2019 is unreliable, probably separate-statement EPS in some years · real FY2015 drop = **−45%** (profit) on revenue −30%, consistent with the 2015 presale slump · primary FY2015 statement not reachable this round (IR pages 500/404, SET API 403) — label "derived" · Consequence: FS `eps_10y_cagr` 19.2% (base 0.47) is wrong; base FY2015 1.14 gives **9.2%**, and FY2015 itself is a trough base, so even 9.2% flatters — see section 4.1 · lumpy revenue: land = 60% of 2025 revenue, 54–58% in 1H2026; D5 / D8 / D12 answered with that in mind | SC · DK17 · DK · OR | number+person | high (that it is an error) · medium (exact value) |

---

## 4. Dividend vs cost — facts only (target 7–12% parked; no verdict on reaching it)

### 4.1 Earnings-based growth scenarios (ours, not Niwes; for Art to confirm → `holdings.growth_scenarios`)

Rule applied (deep-dive.md): forward growth = normal EPS growth, payout held at the policy floor 40%; dividend growth from payout widening does not count; abnormal base years excluded.

| Window (reported attributable EPS, section 2.2) | Base → FY2025 | CAGR | Base year normal? |
|---|---|---:|---|
| FY2014 → FY2025 (11 y) | 2.08 → 2.74 | **2.5%** | peak of the previous cycle (revenue record 7,406) — peak-to-peak |
| FY2015 → FY2025 (10 y) | 1.14 → 2.74 | 9.2% | trough (revenue −30%) — flatters |
| FY2016 → FY2025 (9 y) | 1.12 → 2.74 | 10.4% | trough |
| FY2019 → FY2025 (6 y) | 1.63 → 2.74 | 9.0% | normal year, but FY2025 end point is a transfer peak |
| FY2021 → FY2025 (4 y) | 1.22 → 2.74 | 22.4% | COVID trough base — not usable |
| FS as printed (cache base 0.47) | 0.47 → 2.74 | 19.2% | **data error** (D18) |
| Revenue 2010 → 2025 (15 y) | 3,693 → 14,281 | 9.4% | FS A5 |
| Recurring revenue 2023 → 2025 | 4,713 → 5,579 | 8.8%/yr | utilities fell 4.9% in 2025 |

Scenarios (per year, FY2025 base, 5–15 years):

| Case | EPS growth | Why this number | What has to be true |
|---|---:|---|---|
| Bad | **0%** | Peak-to-peak history is 2.5%; the next trough (2027–28 after the 2025–26 presale slump) offsets 2024–26 margins; dividend held at 1.10 | presale stays ≤1,500 rai/yr, land GPM back to ~40%, utilities flat |
| Mid | **5%** | Between peak-to-peak 2.5% and trough-based 9–10%; ≈ industry volume +3–4%/yr (KR) + price (+10%/yr 2025–26, KB) + recurring +5–9% | presale ≈2,000 rai/yr average, raw land developed on time, debt stays <1.0× |
| Good | **9%** | Trough-based history 9–10%, capped under our 10% ceiling; data-centre / Vietnam / Laos deliver | presale ≥2,500 rai/yr for several years, Laos first sales, no tariff shock |

The 2026-10-09 book used 3 / 7 / 11% from dividend history — replaced; the 11% case exceeded the 10% ceiling and the 7% mid rested on a 5-year dividend window with a COVID base.

### 4.2 Lump held — 32,400 shares, cost 26.40 (FS2 A4; yield = DPS of that year ÷ cost)

| Case | g | Year 5 (FY2030) DPS | @26.40 | @32.25 (today) | @25.80 (−20%) | @19.35 (−40%) | Year 10 DPS | @26.40 | @32.25 | Year 15 DPS | @26.40 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Bad | 0% | 1.100 | 4.2% | 3.4% | 4.3% | 5.7% | 1.100 | 4.2% | 3.4% | 1.100 | 4.2% |
| Mid | 5% | 1.404 | 5.3% | 4.4% | 5.4% | 7.3% | 1.792 | 6.8% | 5.6% | 2.287 | 8.7% |
| Good | 9% | 1.692 | 6.4% | 5.2% | 6.6% | 8.7% | 2.604 | 9.9% | 8.1% | 4.007 | 15.2% |

Growth needed to reach 7% / 12% of cost (FS2): at 26.40 — year 5: 10.9% / 23.6% · year 10: 5.3% / 11.2% · year 15: 3.5% / 7.3% · at 32.25 — year 10: 7.5% / 13.4%. Baht on the lump: FY2025 dividend = 32,400 × 1.10 = 35,640; at the mid year-10 DPS 1.792 = 58,061; cost 855,360; market value at 32.25 = 1,044,900.

### 4.3 Monthly DCA — equal money every month for 10 years, then hold (FS2 A4 DCA; yield = dividend received in year N ÷ all money put in by then)

| Case | g | Year 5: price grows with DPS / price flat | Year 10 | Year 15 |
|---|---:|---|---|---|
| Bad | 0% | 3.4% / 3.4% | 3.4% / 3.4% | 3.4% / 3.4% |
| Mid | 5% | 3.9% / 4.4% | 4.4% / 5.6% | 5.6% / 7.1% |
| Good | 9% | 4.3% / 5.2% | 5.4% / 8.1% | 8.4% / 12.4% |

Average purchase yield needed for the year-10 dividend to reach 7% / 12% of money invested (FS2): bad 7.00% / 12.00% · mid 4.30% / 7.37% · good 2.96% / 5.07% — against 3.4% at today's price.

### 4.4 Numbers still unknown that would move the answer
- FY2026 presale full year (target 2,800; 1H 377–378) and year-end backlog — decide whether 2027–28 is a "bad" or "mid" year · due with Q3/2026 results (mid-Nov 2026, date not verified) and FY results (late Feb / early Mar 2027)
- Normal EPS FY2026: reported 1H 2.58 includes the 366 million gain (≈0.23/share after the 72.84% share) → normalized ≈2.3; if 2H repeats, FY2026 ≈4.3–4.6 reported and the FY2026 DPS at 40% ≈1.7–1.8 — this would be the new base and would make the FY2025-based tables above conservative for year 1, but it is a transfer peak (section 5 item 1)
- FY2015 primary EPS (annual report 2015 not reachable)

---

## 5. What breaks it — ordered by likelihood × damage to the dividend (all odds = `guess:`; "temporary" = dividend back within ≤3 years as AMATA has done; "permanent" = X1)

| # | Cause | 5-yr odds | Damage to DPS | Temp / perm | Evidence today |
|---|---|---|---|---|---|
| 1 | Transfer cliff 2027–28: presale 2025 1,234 rai and 1H2026 378 rai feed 2027–28 revenue; backlog 22.3 bn (Sep 25) → 18.4 bn (Jun 26); CBRE "normalization" | guess: high (50%) | DPS −20–35% for 1–2 years (as 2015 / 2018 / 2020) | temporary if 2026–27 presale recovers | OR p.6 · DK · IVX · WS |
| 2 | Land-buying cycle squeezes cash: 3,948 rai bought in 2025, capex 4,998 million in 1H2026, FCF −2,428, net debt +3.1 bn in 6 months; only 1,965 rai ready to sell so development capex must continue | guess: 40% | board holds DPS flat 2–3 years | temporary | OR p.37 · Y |
| 3 | US tariff / ART outcome worse than peers; FDI "wait-and-see"; Vietnam / Malaysia win the electronics wave | guess: 30% | presale down 2–3 years → turns #1 from 1 year into 3 | risk of permanent if structural | WS · KR |
| 4 | Data-centre demand concentration: 2026 FDI filings dominated by digital (1.12 trn of 1.37 trn, BOI); a few 300–800 rai deals decide the year; power / water availability is the gate | guess: 30% | lumpier years, not a lower base | temporary | BOI · IVX |
| 5 | Vietnam utilities and transfers: utilities revenue −4.9% (2025) and −15% (9M25) from a customer's lower output; VN transfers 469 → 152 rai; ODI approvals delayed (HV) | guess: 35% | recurring floor erodes 5–10% | temporary | OR p.155 · DK · HV |
| 6 | Governance / key person: founder 73 is Chairman and Acting CEO; family 27.1%; a related-party subsidiary sale in 2025 | guess: 15% | price more than dividend | — | OR p.12, p.58, p.156 |
| 7 | Water / power in the East, OECD minimum tax on BOI, politics / EEC policy | guess: 15% | 10–25% of recurring if it happens | temporary 1–3 y | KR |
| 8 | Scarcity of large EEC plots turns into AMATA's advantage or into cost inflation on new raw land (bought at today's prices, margins below 54–66%) | guess: slow, 10–15 y | margin drift down | permanent, gradual | KR · OR p.37 |

Normal cycle vs wrong track (D18 restated): normal = DPS cut 25–35% for one year with EPS still positive, backlog > 12 months of land revenue, recurring revenue still growing → Niwes "temporary, do nothing" · wrong track = DPS cut 2 years running or > 50%, presale < 1,000 rai 2 years running, recurring revenue falling, net debt rising at the same time → X1 "adjust the portfolio". A 2027 cut from cause #1 alone would be the normal cycle.

### 5A. D15 — what we want to believe, the strongest counter-evidence, and what would prove it wrong

| # | Belief (1 sentence) | Strongest counter-evidence + source + date | Falsifier (number / event → flag in section 6) |
|---|---|---|---|
| B1 | "Data-centre and electronics relocation make FY2024–26 earnings (EPS ≥2.7) the new normal" | Presale 2025 1,234 rai −59% (OR p.6, 2026-03-27); 1H2026 377–378 rai = 13% of target (PI, KB, Jul–Aug 2026); backlog 22.3 → 18.4 bn in 9 months (DK, IVX); industry 2025 −18% IEAT basis (KR 2026-04-27); CBRE 2026 "normalization" (WS) | FY2026 presale < 1,500 rai **and** year-end backlog < 12 bn → normal EPS falls in 2027 and 2028 (**T3**) · industry sales < 6,000 rai two years (**T5**) |
| B2 | "Recurring income (40% of revenue) is a floor under the 1.10 dividend" | Recurring gross profit ≈1,634 million < SG&A 1,756 + finance 664 + dividend 1,035 (OR p.155, 2026-03-27); utilities revenue −4.9% in 2025 and −15% in 9M25 (OR, DK) | Utilities + rental revenue down two years running while DPS is cut (**T3**, cause = recurring, not payout) · dividends paid > OCF − capex two years with cash falling (**T4**) |
| B3 | "Management protects the dividend (raised it in 2023 and 2025 when sales fell; policy ≥40%)" | The 40% floor was only formalised 28 Feb 2024 (IR); payout 27–33% in 2019–22; six cuts ≥10% in 2006–2020 incl. −33% in 2020 and two back-to-back cuts twice (FS A1/A2); founder is Chairman and Acting CEO at 73 (OR p.14) | DPS cut two years running (**T1**) · payout < 40% in a year when EPS rose (policy breach) · year-10 yield on the 26.40 cost < 7% in the mid case (**T2**, already ⛔ at 5%) |
| B4 | "18k rai of land bank = 12 years of sales, so growth is secured" | Only 1,965 rai ready for sale at 30 Sep 2025; 15,334 rai raw (DK); 2025 raw-land purchases 3,948 rai pushed interest-bearing debt to 23.3 bn and 1H2026 FCF to −2,428 million (OR p.37, Y) | OCF − capex < dividends two years with net debt rising (**T4**) · interest-bearing debt / parent equity > 1.2 and above the peer median (**T6**) |
| B5 | "Niwes-style: yield will reach 5% on its own as the dividend grows" | Needs 7.9%/yr from a cyclical-peak base to reach 5% of 32.25 by FY2030; mid case gives 4.4% (FS2) | C2 flag still on at the next deep dive with the FY2026 base (**T2 / C2**) |

---

## 6. "Wrong-track" flags T1–T6 for an industrial-estate developer (each flag → the D15 belief it watches)

| Flag | Measure | Where to read it | Value today | Open a review when | Points to "permanent" when | Watches |
|---|---|---|---|---|---|---|
| T1 DPS down how many years | Full-year DPS vs prior year (never interim vs full year) | IR / set.or.th after the final (~Mar) | FY2025 1.10 up; 2026 interim 0.60 up (✅ FS2) | FY down 1 year > 25% | down 2 years running (happened 2008–09, 2015–16) | B3 |
| T2 yield on cost year 10 (mid case) | DPS FY2035 ÷ 26.40 with the agreed mid growth | FS A4 | **6.8% < 7% at 5% → ⛔ (FS2)**; 8.2% at the old 7% | < 7% in the mid case (system threshold; target parked) | < 5% even in the good case | B3, B5 |
| C2 year-5 yield on today's price | DPS FY2030 ÷ 32.25, mid case | FS A4 | **4.4% → ⛔ (FS2)** | < 5% in the mid case | < 5% in the good case (today 5.2% — barely clear) | B1, B5 |
| T3 why did the dividend fall | (a) normal EPS two years down (b) payout cut (c) recurring revenue YoY (d) presale rai/yr | MD&A, OR segment table, company deck | normal EPS 2.73 (2025) · payout 40% · recurring +8.8%/yr 2023–25 · presale 1,234 (2025), 378 (1H26) | normal EPS down 1 year > 30% · recurring < 0 · presale < 1,500 rai/yr | normal EPS down 2 years · presale < 1,000 rai 2 years · recurring down 2 years · payout > 80% to hold DPS | B1, B2 |
| T4 paid from real cash | dividends vs OCF − capex (full year) and net debt | Y annual / quarterly cash flow | 2025 1,035 vs 7,832 ✅ · **1H2026 862 vs −2,428** | OCF − capex < dividends for a full year with net debt up | 2 years running (2018–20 pattern before cuts) | B2, B4 |
| T5 industry | national land sales (KF / IEAT), BOI applications, backlog in months of land revenue | KR annual, KF semi-annual, BOI, company deck | 2025 −18% (IEAT) · Q1/26 +16.7% · BOI H1/26 +37% · backlog 18.4 bn ≈ 25 months of 2025 land revenue 8,703 | national sales < 6,000 rai · backlog < 12 months | 2 years of falling national sales with Thailand's tariff clearly above Vietnam / Malaysia | B1 |
| T6 debt vs peers | interest-bearing debt / parent equity (Y) vs WHA, ROJNA | Y quarterly balance sheet | 0.90 vs WHA 1.41, ROJNA ≈0.80 (✅) | > 1.2 and rising 2 quarters | > 1.5 together with T4 | B4 |

Combination rule (niwes-principles section 4): T1 or T2 triggered **and** T3 / T4 / T5 pointing to permanent → open a "adjust portfolio" review · triggered but T3–T5 say temporary → hold ("do nothing" — H2) · no auto-sell · every belief has a flag and every flag a belief (B1 ← T3 T5 C2 · B2 ← T3 T4 · B3 ← T1 T2 · B4 ← T4 T6 · B5 ← C2/T2).

Next dates: Q3/2026 results and 9M presale (mid-Nov 2026, not verified) · FY2026 presale, backlog and final dividend (Feb–Mar 2027) · Krungsri / Knight Frank 2026 industry totals (Q1–Q2 2027).

---

## 7. Is today's price cheap or expensive (for the cash-for-bargains plan — not a quality judgement)

All history = actual year-end closes, not dividend-adjusted (FS A10).

| Measure | Today 32.25 (close 2026-10-15) | Own history | Reading |
|---|---:|---|---|
| PE on FY2025 EPS 2.74 | 11.8 | year-end PE 2016–25: 10.2 · 17.0 · 21.3 · 12.2 · 16.0 · 17.2 · 10.4 · 16.3 · 13.3 · 6.1 (FS A10) | lower half of own range; not < 10 (P3, weak evidence) |
| PE on TTM EPS 4.47 / normalized ≈4.24 | 7.2 / 7.6 | 2025 year-end 6.1 was the only year < 10 besides 2016 | passes P3 only because 1H2026 is a transfer peak + 366 million gain |
| PBV | 1.43 (BVPS 22.50 Q2/26, Y) · 1.64 on FY2025 BVPS 19.71 (FS) | 0.84–2.23 (2016–25) | middle of own range |
| Yield on FY2025 DPS | 3.4% | 1.8–2.8% in 2017–24 · 3.9% 2016 · 6.6% 2025 | FS label "cheap vs itself" (80th percentile) — but below the 5% rule every year since 2009 except 2025 |
| Yield on TTM DPS 1.35 | 4.2% | — | interim 0.60 counts half a year that may not repeat |
| Yield if FY2026 DPS = 40% × EPS 4.3–4.6 (guess) | 5.3–5.7% | — | would clear 5% once; depends on 2H2026 transfers |
| 52-week position | 14.00–34.50 → 89% | January 2026 ≈15.7 → +105% in 9 months | top of the range |
| Peers (Y) | PE TTM 7.2 · PBV 1.43 · yield 4.2% | WHA PE 17.6 · PBV 1.96 · yield 4.2% · ROJNA PE 3.2 · PBV 0.56 · yield 8.9% (loss year 2025) | cheaper than WHA, dearer than ROJNA |
| Broker targets (not Niwes) | — | Bualuang 40 (BB) · Pi 36 (PI) · InnovestX 44 mid-2027 (IVX) · KBank 35 (KB) | all "buy" after the price doubled |

A 20–30% drop = 22.6–25.8 baht: PBV ≈1.0–1.15, FY2025 yield 4.3–4.9%, roughly the 26.40 average cost. The monthly DCA continues under F4 regardless; the separate "cash for bargains" pocket has no trigger today by the FS rule (yield 3.4% is "cheap vs itself" only because the history is low-yield).

---

## 8. 35% in one name

Base: 32,400 shares × 26.40 = 855,360 cost · 1,044,900 at 32.25 (+22%) · FY2025 dividend 35,640 baht · plan weight 35% (job brief; no fresh total-portfolio value available this round).

| If AMATA … | Effect on the holding | Happened before? |
|---|---|---|
| price −58% (as 2025: 25.68 → 10.90, FS A10 / old book) | 1,044,900 → 439,000; −49% below cost; plan value −20% if AMATA is 35% | yes — 2025 and 2008 (−80%) |
| DPS −33% (as 2020) | 35,640 → 23,760/yr | yes — 2015 / 2018 / 2020 |
| DPS −82% over two years (as 2008–09) | 35,640 → 6,400/yr for 1–2 years | once |
| both at once | year-5 yield on cost 2.8–3.5% in the mid case for the cut years | 2008–09 |

Niwes F1 asks for ≥5 stocks in 5 industries (Art does not apply it, 2026-10-19); his own two largest positions were 42% + 38% (F2, behaviour not rule) but in companies with stable earnings. AMATA's recorded cycle: a dividend cut of 25–35% roughly every 4–5 years, paid back within 2–5 years (once 10). The 35% weight therefore carries "timing risk on a third of the plan", not "business-failure risk" (A- rating, 1,547 captive customers). Written for Art to weigh — no new weight proposed.

---

## 9. What the system should prepare next time (found by hand this round)

| # | Item | Found in | What the script should do | Trap |
|---|---|---|---|---|
| 1 | EPS 2011–2018 in `yearly_metrics` | SC vs DK17 / OR | recompute EPS = attributable profit ÷ shares (1,067 million to 2019, 1,150 from 2020) or verify against company decks; drop `eps_10y_cagr` when the base-year EPS × shares ≠ net profit ±10% | FY2015 0.47 produced the "19%" headline and the −77% worst-drop line |
| 2 | Normal EPS | OR p.155–156 | `normal_eps` entries below; A3/A4 then use 2.73 (change is tiny for 2025, large for 2022) | 2022 one-offs ≈1.16 bn only from a broker snippet |
| 3 | Presale / transfer / backlog / land ready for sale | OR p.6, p.37, DK, PR | manual yearly fields (no API): presale 2021–25 = 913 / 692 / 1,853 / 3,019 / 1,234 · transfers 2024–25 = 1,912 / 1,645 · backlog 31 Dec 2025 21,833 · land ready 1,965 rai (30 Sep 2025) | 594 rai (1H2026) is transfers, not presale (378) — the 2026-10-09 book mixed them |
| 4 | Recurring gross profit vs dividend + opex + interest | OR p.155 | add a line to A7: (utilities + rental gross profit) ÷ (SG&A + finance cost + dividend) | "40% recurring" is revenue share only |
| 5 | FCF for the latest half-year | Y quarterly | T4 should also print the YTD figure (1H2026 −2,428) | annual T4 looks fine while the half-year has turned |
| 6 | Dividend policy + approval date + previous wording | IR | manual_facts (done) | policy wording changed 28 Feb 2024 — payout comparisons before that use the old wording |
| 7 | Chairman / CEO / age / family stake | OR p.12, p.14, p.58 | manual_facts (done); refresh yearly | 2026-10-09 book said an outside chairman was appointed — OR 2025 shows Vikrom as Chairman and Acting CEO; the press-release claim was never verified (page 403) |
| 8 | Peer D/E | Y | A6 could print WHA / ROJNA interest-bearing debt / equity next to AMATA | three D/E definitions in circulation (0.63 / 0.90 / 1.67) |

---

## 10. Where the 2026-10-09 book was wrong or has been replaced

| # | 2026-10-09 book | This book | Type |
|---|---|---|---|
| 1 | Growth scenarios 3 / 7 / 11% from dividend history (section 4.1) | 0 / 5 / 9% from earnings; 11% was above the 10% ceiling; the 7% mid rested on a dividend window with a COVID base | method |
| 2 | 2.1 table: EPS 2015 = 0.47, payout 97% | data error; EPS ≈1.14 derived, payout 40% | data |
| 3 | 2.1 / 3 D1: "interim paid from BOI 0.25 + non-BOI 0.35 (snippet)" | not in IR table ("no BOI designation shown") — dropped | unverified |
| 4 | D7: "appointed an outside chairman (Dr Panpree), Vikrom still CEO (headline)" | OR 2025: Vikrom Kromadit = Chairman and Acting CEO, age 73 | wrong / outdated |
| 5 | D7: paying below 40% in 2019–22 "contradicts policy or policy came later" | policy text approved 28 Feb 2024; earlier wording "minimum 40% … depending on economic atmosphere" since 1995/96 (IR) | resolved |
| 6 | D8: land bank 18,212 rai (Bangkok Post snippet) → 11–15 years | official 18,131 rai Thailand at 30 Sep 2025, of which only 1,965 rai ready for sale, 15,334 raw (DK) | replaced |
| 7 | 5 / 6: "H1/26 presale 594 rai = 21% of target" | 594 = transfers (PR); presale 1H2026 = 377–378 rai = 13% (PI, KB) | mixed definitions |
| 8 | 2.3: recurring annualized ≈5,680 million = 4.5× dividend "at revenue level" | FY2025 recurring 5,579 million revenue, ≈1,634 million gross profit — below opex + interest + dividend | reframed |
| 9 | D6: "IPO 18 baht 1997 (PP)" | listing year 1997 confirmed (OR); IPO price not re-verified | partial |
| 10 | D13: "DBS P/NAV 0.4 at 15.70 → ≈0.8 today" | replaced by OR figures: investment-property fair value 12,666 vs book 7,110; AMATAV at 0.39× book in the market | replaced |
| 11 | 2.2: "2025 revenue 14,281 (Y) / 14,524 (KHI)" | both right: 14,281 = operating revenue, 14,524 = total incl. other income (OR) | clarified |
| 12 | 2.1 note: FY2020 set cache = 0.20 | FS A1 (set_official + yahoo) now shows 0.2992 — fixed in the system since | fixed |
| 13 | Section 1: conclusions about reaching 7–12% ("medium chance" / "low chance") | removed — target parked; tables reported as facts only | scope |

Still valid from the old book and reused after re-check: DPS table FY2008–2025 (3 sources), crisis table, peer D/E picture, risk list structure, the "594 rai" number (as transfers).

---

## ค่าที่ต้องจดลง config

Head writes these into config.json (`normal_eps` and `holdings.growth_scenarios`); this job did not edit config.json. After entry run `fact_sheet.py AMATA --refresh --cost AMATA=26.40` so A3/A4/A12 pick them up.

```json
{
  "normal_eps": {
    "AMATA": {
      "2025": 2.73,
      "2024": 2.11,
      "2023": 1.59,
      "2022": 1.02,
      "_source": "research/amata-deep-dive-2026-10-19.md D1 + section 2.2: FY2025 reported 2.74 (3,148.66 M / 1,150 M sh, One Report 2025 p.154) + 113 M non-recurring income tax (p.156) - 215 M one-time Vietnam land-cost reversal after 20% tax and 72.84% parent share = -125 M (p.155, our estimate) -> 3,137 M = 2.727 · FY2024 2,467.12 M - 44.2 M gain on investment property x0.8 = 2,431.7 M / 1,150 = 2.11 (p.155) · FY2023 1,884.76 M - 72.2 M gain x0.8 = 1,827 M / 1,150 = 1.59 (p.~165 six-year table) · FY2022 ordinary profit 1,177 M / 1,150 = 1.02 per broker note quoted by mitihoon 2023-03-01 (snippet-level; head may exclude) — reported 2,341.35 M = 2.04",
      "_as_of": "2026-10-19"
    }
  },
  "holdings": {
    "growth_scenarios": {
      "AMATA": {
        "bad": 0.0,
        "mid": 0.05,
        "good": 0.09,
        "source": "research/amata-deep-dive-2026-10-19.md section 4.1 — earnings-based: peak-to-peak FY2014-25 EPS CAGR 2.5%, trough-based FY2015/16-25 9.2-10.4%, FY2019-25 9.0%; payout held at the 40% policy floor; 10% ceiling",
        "as_of": "2026-10-19"
      }
    }
  }
}
```

`special_dividends`: none identified for AMATA (IR table shows only ordinary cash dividends; no special designation).

---

## acceptance (checked line by line)
- D1–D18 all answered with fact-sheet section or external source + date: section 3, 18 rows, every row has a source column with codes dated in the source table
- D1 normal EPS FY2025 with what was removed and why: 2.73 — +113 million non-recurring tax, −215 million Vietnam cost reversal (after-tax, parent share estimate); config block above
- D2 numeric year-5 DPS from an earnings-based rate + obstacles: 1.10 / 1.40 / 1.69 (FY2030) at 0 / 5 / 9%; obstacles listed in D2 and section 5
- D15 ≥2 beliefs with sourced counter-evidence and a falsifier tied to a T flag: 5 beliefs in 5A, each with source + date and a T / C2 flag
- D16 every flag maps to a D15 belief and every belief has a flag: section 6 table + combination line
- D18 FY2015 −77% checked: data error (SC EPS 0.47 vs attributable 1,216 million ÷ 1,067 million shares = 1.14; cache EPS column unreliable 2011–2018); real drop −45%; primary FY2015 statement not reachable (labelled derived)
- Fact-sheet `eps_10y_cagr` ≈19% with base FY2015: base is both a data error and a trough year; rates used instead 2.5% (peak-to-peak) · 9.2% (corrected trough base) → scenarios 0 / 5 / 9%
- Owner's 7–12% target: section 4 reports A4 / DCA numbers only; no sentence concludes whether the target is reached (section 10 item 13 removed the old conclusions)
- Files written: research/amata-deep-dive-2026-10-19.md (this file) · data/manual_facts/AMATA.json (git-ignored via `data/` rule in .gitignore, not committed) · config JSON block: this section
