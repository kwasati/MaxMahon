# KBANK deep dive — "ถือและซื้อตัวนี้ต่อไปทุกเดือนอีก 10 ปี เรามาถูกทางไหม?" (candidate — not held)

- Written 2026-10-28 · ordered by Art 2026-10-28 (after `research/niwes-keep-or-cut-2026-10-28.md` section 3 named KBANK a deep-dive candidate vs BBL) · Niwes leg · **not held, no cost basis, no weight** — every "on cost" figure below uses today's price 245.00 (close 2026-10-27).
- Template: `docs/deep-dive.md` (steps + pass criteria) · questions D1–D18 and flags T1–T6: `docs/niwes-principles.md` sections 4–5 · 10-section layout copied from `research/bbl-deep-dive-2026-10-19.md` (bank model).
- Starting data = fact sheet `reports/facts/KBANK_2026-10-28.md` (FS; `fact_sheet.py KBANK --refresh`, re-run after `data/manual_facts/KBANK.json` was written). `config.json` has no KBANK `normal_eps` / `growth_scenarios` / `special_dividends` yet, so the sheet's A3/A4 use the mechanical rule (bad 2.3% / mid 6.1% / good 10%) on base DPS 14.00 — superseded by section 4 of this book once Art decides.
- Owner's 7–12% yield-on-cost target is a direction, not a cut-off (`docs/deep-dive.md`, Art 2026-10-18/28): A4 / DCA numbers are reported, no conclusion on whether the direction is reached.
- **Q3/2026 results published 21 Oct 2026** (net profit 12,720 m, −2.1% YoY) — included (table 2.2).
- Core question from Art: can he hold and DCA this every month for 10–20 years. Answer in section 1; facts only; no buy/sell order (R6).
- Language: English (worker rule); Thai headings copied from the template files.

## รหัสแหล่ง (ใช้ซ้ำทั้งไฟล์)

| code | source | data to | fetched |
|---|---|---|---|
| FS | `reports/facts/KBANK_2026-10-28.md` — A1 DPS 2004–2025 (set.or.th 2021+, yahoo before), A2 cuts, A3 CAGR, A4 yield-on-cost (mechanical scenarios), A5 EPS/ROE/net profit 2010–2025, A12 payout, A10 year-end PE/PBV/yield 2016–2025, flags | FY2025 · close 245.00 on 2026-10-27 | 2026-10-28 |
| Y | yahoo via yfinance (`C:/WORKSPACE/_desk/_scratch/kbank-dd/kbank_yf.py` → `kbank_yf_out.json`): annual P&L/BS 2022–2025, quarterly 2Q25–2Q26, dividends 2015–2026, year-end closes and yearly low/high 2014–2026 (not dividend-adjusted, `auto_adjust=False`), last close 245.00 on 2026-10-27, 52-week 178–261, market cap 580,485 m, shares 2,369.3 m, book value/share 247.76, earnings dates; peer snapshot BBL SCB KTB TTB (info call 2026-10-28 ~10:15, may be intraday) | 2Q26 · 2026-10-27 | 2026-10-28 |
| PP | aio.panphol.com/stock/KBANK/dividend (every XD row FY2560–2569 + FY2539–2540 rows) · /sholder (top holders, record 10 Sep 2569) | XD 9 Sep 2026 | 2026-10-28 |
| PR21–PR25 | KBANK full-year press releases via mirrors: FY2021 thestandard.co/kbank-profit-2564 (21 Jan 2022) · FY2022 thebangkokinsight 1030516 (20 Jan 2023) · FY2023 thestandard kbank-profits-in-2023 + brandinside ?p=161951 (19 Jan 2024) · FY2024 thaipr.net ?p=3563289 (21 Jan 2025) · FY2025 thansettakij 649460 + brandinside ?p=248226 (21–22 Jan 2026) — profit, NII, NIM, ECL, NPL, coverage, Tier 1 / BIS, assets | FY2025 | 2026-10-28 |
| H1 | KBANK 1H2026 release via brandbuffet ?p=300967 + thaipost 1035973 (21 Jul 2026) — profit, one-time item, NIM, ECL, credit cost, NPL, coverage, BIS | 30 Jun 2026 | 2026-10-28 |
| Q3 | KBANK Q3/2026 release via thansettakij 671899 + pptvhd36 285604 (21 Oct 2026) — profit, 9M, one-time item, NII, NIM, non-II, ECL ratio, NPL, coverage, BIS, assets | 30 Sep 2026 | 2026-10-28 |
| Q126 | KBANK Q1/2026 release via brandinside ?p=266065 / wealthythai 47247 search summary (Apr 2026) — one-time "investment-value compensation" 1,455 m | 31 Mar 2026 | 2026-10-28 |
| TRI | Trinity Securities notes (PDF → pypdf, `_scratch/kbank-dd/KBANKT_*.txt`): 22 Jan 2026 (4Q25 result, FY26F/27F, TP 186, PBV 0.7x, quarterly P&L 2Q24–4Q25, Stage 2 8.6%, write-offs) · 21 Jan 2025 (4Q24, FY2025 credit-cost guidance 140–160 bp, JV AMC with BAM) · 22 Jul 2025 (2Q25, TP 172, annual balance sheet 2022A–2024A: net loans, deposits, equity) | 4Q25 | 2026-10-28 |
| INVX | innovestx.co.th cafeinvest: kbank-news-20261021 (21 Oct 2026, Q3/26: loans +6.3% YoY, credit cost 1.6%, coverage 168%, TP 280 OUTPERFORM) · kbank-news-20260721-1 (21 Jul 2025, FY2025 guidance NIM 2.75–2.95%, credit cost 1.4–1.6%, BOT-regulation hit 2–3%) | Q3/26 | 2026-10-28 |
| KHI | kaohooninternational.com ?p=562585 (4 Aug 2025: payout floor raised 25% → ≥50%, target 50–60%, FY2024 payout 58.5% incl. special, regular 46.3%, CEO ROE target double digit) · ?p=578052 (27 Feb 2026: FY25 final 12 = regular 10 + special 2, payout 67%, CGSI FV 190 Hold) · ?p=577056 (16 Feb 2026: Gulf 10.0298% on SEC count, below 10% on BOT count) | Feb 2026 | 2026-10-28 |
| DIV | mitihoon.com/2026/02/26/620894 (26 Feb 2026: FY2025 total 14.00 = regular 12.00 + special 2.00 one-time; final 12.00 XD 21 Apr 2569, paid 8 May 2569) · share2trade.com/news/40990 + kaohoon.com/news/741441 (Apr 2025: special 2.50, XD 15 May 2568, paid 6 Jun 2568) | — | 2026-10-28 |
| BB | buyback: innovestx kbank-news-20251030 + infoquest 2025/542511 + thairath 2893507 (Oct–Nov 2025): programme ≤8,800 m / ≤47,386,552 shares (2%), 14 Nov 2025 – 13 May 2026 | — | 2026-10-28 |
| BOTQ | bot.or.th news-20260818 (18 Aug 2026) — Q2/2026 banking sector: system loans +2.0% YoY, SME + consumer contracting, NPL 2.82% (534.8 bn), Stage 2 6.78% | 2Q26 | 2026-10-28 |
| KR | thansettakij 672038 (22 Oct 2026, K-Research on 8 banks Q3/26): NIM 3.00%, loans +3.9% YoY, NPL 3.11%, coverage 199.0%, FY26 NPL 3.00–3.20% | 3Q26 | 2026-10-28 |
| MPC | thairath 2902537 / thaipbs 502608 (25 Feb 2026: cut to 1.00%, vote 4–2) · 28 Oct 2026 meeting: decision not found at the time of writing (K-Research expected hold, bangkokbiznews 872579) · earlier holds 29 Apr / 24 Jun / 26 Aug 2026 per `research/bbl-deep-dive-2026-10-19.md` (MPC), not re-opened | 28 Oct 2026 | 2026-10-28 |
| VB | kaohoon pr/831898 + pptvhd36 275997 + brandbuffet (May–Jun 2026): CLICX (KTB+AIS+OR) licensed 18 May 2026, launched 27 May, first service 19 Jun 2026, 4% deposit promo | Jun 2026 | 2026-10-28 |
| SH | PP sholder record 10 Sep 2569: Thai NVDR 18.21%, Gulf Development 9.99%, State Street Europe 6.13%, SEA UK (Type C) Nominees 4.10%, Social Security Office 2.81% · thairath 2889348 (16 Oct 2024: Gulf 3.25% Mar 2024 → 5.03% Oct 2024, "trading and dividend income") · hoonvision (2026): Gulf "no intervention in policy/management" | Sep 2026 | 2026-10-28 |
| WK | en.wikipedia.org/wiki/Kasikornbank — founded 8 Jun 1945 (Thai Farmers Bank, Choti Lamsam), listed on SET 1976, CEO Kattiya Indaravijaya since Apr 2020 | — | 2026-10-28 |
| MTL | search summary (kasikornbank.com financial-conglomerate page + wealthythai 3320): KBANK net beneficial interest in Muang Thai Life 38.25%; 10-year bancassurance contract 12,700 m (2020) — page itself not opened | — | 2026-10-28 |
| BOT20/21 | BOT dividend restriction 2020–21 — source codes of `research/bbl-deep-dive-2026-10-19.md` (thaipublica 19 Jun 2020; BOT press release 82/2564, 11 Nov 2021); not re-opened this round | 2020–21 | — |
| KOC | `research/niwes-keep-or-cut-2026-10-28.md` section 3 — why KBANK is a candidate (rule-based DCA numbers there are superseded here) | 2026-10-28 | — |

Unreachable this round: kasikornbank.com (news pages and IR deck PDFs 2Q26/3Q26 return an HTML stub; WebFetch blank) · wealthythai (403) · prachachat (403) · set.or.th. Consequence: Tier 1 / CET1 for FY2024–9M2026 not found (press mirrors print only the total BIS ratio); the bank's own gain-on-investment table not opened (normal EPS uses yfinance line items, as the BBL book did).

---

## 1. คำตอบ 1 หน้า

**Answer (facts first; the decision is Art's and the head's — R6):** KBANK is the biggest earner among Thai banks (net profit #1 in 2024 and 2025, thairath) with capital and provisions well above 2020, and a management that in 2025 switched from paying out 20–30% of profit to a stated 50–60% plus specials and a buyback. That switch — not earnings growth — is what turned a 2–3% yield stock into today's 5.7%. The question for "DCA every month for 10–20 years" is therefore whether the dividend can grow once payout expansion is spent: on the numbers, earnings have been flat for a decade and 2026 is flat again.

1. **Yield today 5.7% on FY2025 DPS 14.00 — but 2.00 of it is a one-time special** (DIV). On the regular 12.00 the yield is **4.9%**, a hair under the 5% line (C1); 3-year average yield 4.4% on total / 3.8% on regular (FS A10 + ours). FY2025 EPS 20.63 (FS) includes ~5.1 bn more gains on securities than 2024 (Y); **normal EPS FY2025 = 18.9** (section 2.3). Regular payout 58% of reported / 63% of normal EPS — already at the top of the 50–60% band (KHI).
2. **Year-5 (FY2030) regular DPS at bad 0% / mid 2.5% / good 5% = 12.00 / 13.58 / 15.32 → 4.9% / 5.5% / 6.3% of 245** (section 4). The bad case misses C2 (≥5% in 5 years) by 0.1 point; mid and good pass. Growth rates are earnings-based (EPS CAGR 10 y 2.3%, 15 y 6.4%, 2014→2025 0.6%; net profit 2014→2025 +0.65%/yr — FS A3/A5), not the 41%/yr dividend CAGR of A3 (base 2020 = BOT-cut year, payout-driven).
3. **Dividend cut twice in the FS window's memory, both with a regulator or a system crisis**: FY2020 −50% (5.00 → 2.50, BOT order, back above 5.00 in FY2023 = 3 years — FS A2, PP, BOT20/21); FY1997 interim 3.00 then no panphol rows until the FS window starts in 2004 (section 2.5 — treat as "suspended for years", exact path not verified). Capital today: BIS 19.77%, coverage 177.9%, NPL 3.18% (Q3) vs BIS 18.45% / coverage 161% / NPL 3.95% in Q3 2020.
4. **2026 so far: reported 9M profit +3.4%, but ex the 1,455 m one-time item it is −0.3%** (Q3, Q126). NIM 2.89% (from 3.23% FY2025 and 3.66% FY2023) while NPL is flat and coverage is rising. The bank is defending profit with lower provisions (credit cost 1.6% vs 2.2% in 2022–23) and lower costs (cost/income 40.8%) — both have limits.
5. **What does not hold up in the story**: "dividend grew 85% + 17%" (payout 37% → 68% with two specials — FS A12, DIV); "KBANK beats BBL because its profit grows" (KOC section 3 — ex one-off it is flat; the difference vs BBL in 2026 is that KBANK cut provisions and costs while BBL's market gains reversed); "yield 5.7%" (4.9% regular).

**Confidence: medium.** DPS agrees across three sources per year (2.1); bank table from the bank's own releases via mirrors (2.2); Q3/2026 actual included. Low-confidence: normal EPS (yfinance "gain on sale of security" line, bank's own table not opened), the split between recurring and one-time in non-interest income (wealth/insurance income is growing +21% in 9M26 and partly market-driven), Tier 1 / CET1 after 2023 (not found).

**Items Art and the head must decide (not decided here):**
- Which base dividend counts for KBANK: regular 12.00 (yield 4.9%, this book's primary tables) or total 14.00 (5.7%, what the sheet prints). Entering `special_dividends` (values at the end) makes the sheet use 12.00.
- Growth scenarios proposed: bad 0% / mid 2.5% / good 5% (section 4.1) and normal EPS FY2025 = 18.9 (or the harsher 18.0).
- Whether a bank yielding 4.9% regular / 5.7% with special, PBV 1.0, is the right third bank next to BBL and TCAP (D17, section 8) — this is the concentration question, not a KBANK question.

---

## 2. ใบข้อเท็จจริง

### 2.1 Dividend per share by fiscal year — three sources compared (FS A1 · PP · Y XD list) · regular vs special split

| FY | FS A1 (set.or.th / yahoo) | PP (interim + final [+ special]) | Y XD list | regular | special | agree? |
|---|---:|---|---|---:|---:|---|
| 2017 | 4.00 | 0.50 (XD 12 Sep 2017) + 3.50 (XD 11 Apr 2018) | 0.5 + 3.5 | 4.00 | — | ✓ |
| 2018 | 4.00 | 0.50 + 3.50 (XD 11 Apr 2019) | 0.5 + 3.5 | 4.00 | — | ✓ |
| 2019 | 5.00 | 0.50 (XD 11 Sep 2019) + 4.50 (XD 9 Apr 2020) | 0.5 + 4.5 | 5.00 | — | ✓ |
| 2020 | 2.50 | 2.50 (XD 20 Apr 2021) — no interim (BOT order) | 2.5 | 2.50 | — | ✓ |
| 2021 | 3.25 | 0.50 (XD 8 Sep 2021) + 2.75 (XD 18 Apr 2022) | 0.5 + 2.75 | 3.25 | — | ✓ |
| 2022 | 4.00 | 0.50 + 3.50 (XD 17 Apr 2023) | 0.5 + 3.5 | 4.00 | — | ✓ |
| 2023 | 6.50 | 0.50 + 6.00 (XD 22 Apr 2024) | 0.5 + 6.0 | 6.50 | — | ✓ |
| 2024 | 12.00 | 1.50 (XD 11 Sep 2024) + 8.00 (XD 17 Apr 2025) + **2.50 (XD 15 May 2025)** | 1.5 + 8.0 + 2.5 | **9.50** | **2.50** (DIV: "ปันผลพิเศษ", from retained earnings) | ✓ |
| 2025 | 14.00 | 2.00 (XD 10 Sep 2025) + 12.00 (XD 21 Apr 2026, paid 8 May 2026) | 2.0 + 12.0 | **12.00** | **2.00** (DIV/KHI: final 12 = regular 10 + special 2, one-time) | ✓ |
| 2026 (open) | 2 (FS "ปีที่ยังไม่ครบ") | 2.00 interim (XD 9 Sep 2026, paid 25 Sep 2026) | 2.0 | — | — | ✓ — not a full year, not counted |

Panphol labels every row "เงินปันผล" (no special flag) — the special status comes from the bank's announcements as reported by mitihoon / kaohoon / share2trade (DIV), which satisfies DC-2 (special identified from company announcement, not from the XD list). Before 2004 (PP rows returned): FY1996 = 3.00 + 3.00 (XD Aug 1996, Mar 1997) · FY1997 = 3.00 interim (XD 8 Aug 1997) · no PP rows between FY1997 and the FS window (2004 = 1.00 yahoo-adjusted). The 1998–99 recapitalisation is not re-verified; "no dividend for ~6 years" is the reading of the gap, not a verified per-share path (same caveat as BBL).

Regular-DPS history (ours, for growth reading): 4.00 flat 2014–2018 → 5.00 (2019) → 2.50 (2020, BOT) → 3.25 → 4.00 → 6.50 → 9.50 → 12.00. Regular DPS 2019→2025 = 15.7%/yr, EPS over the same years 4.1%/yr (FS A5) — the gap is payout (31% → 58%, FS A12 on regular).

### 2.2 Bank table — the numbers that replace "cash" and "debt" for a bank (D4 D10 D11) · from the bank's own year-end releases via mirrors unless marked

| year | net profit (m) | NIM | ECL (m) | credit cost | NPL ratio | coverage | Tier 1 | BIS | net loans (m) | source |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2020 | 29,487 (FS) | — | — | — | 3.93% | 149.2% | 15.74% (30 Sep 2020) | 18.45% (30 Sep 2020) | — | PR21 comparatives · thestandard 21 Oct 2020 |
| 2021 | 38,053 (+29.1%) | 3.21% | 40,332 | — | 3.76% | 159.1% | 16.49% | 18.77% | — | PR21 |
| 2022 | 35,770 (−6.0%) | 3.33% | 51,919 | 2.18% (ours: ECL ÷ year-end loans) | 3.19% | 154.3% | 16.84% | 18.81% | 2,377,774 (TRI) | PR22 · TRI |
| 2023 | 42,405 (+18.6%) | 3.66% | 51,840 | 2.19% (ours) | 3.19% | 152.3% | 17.44% | 19.41% | 2,371,492 (TRI) | PR23 · TRI |
| 2024 | 48,598 (+14.6%) · restated 49,603 (Y) | 3.64% | 47,251 (TRI) | 1.98% (ours) | 3.18% | 153.3% | not found | 20.25% | 2,390,187 | PR24 · TRI |
| 2025 | 49,565 (−0.08% vs restated) | 3.23% | 40,312 (−14.7%) | 1.67% (ours, loans ≈2,411,825 TRI — column label uncertain) · 1H25 bank-reported 1.62% (KHI) | 3.20% (93,533 m) | 162.8% | not found | 20.35% | ≈2,411,825 | PR25 · TRI · thairath 2909569 |
| 1H26 | 27,915 (+6.2%; ex one-off 26,609, +1.3%) | 2.91% | 19,842 | 1.58% (bank, avg loans) | 3.18% | 173.9% | not found | 19.24% | — | H1 |
| 9M26 | 40,635 (+3.4%; ex one-off 39,180, −0.3%) · Q3 12,720 (−2.1% YoY) | 2.89% | 30,171 | 1.60% (bank) | 3.18% | 177.9% (INVX: 168%) | not found | 19.77% | +6.3% YoY, +0.3% QoQ (INVX) | Q3 · INVX |

Read: KBANK's credit cost is structurally higher than BBL's (2.0–2.2% in 2022–24 vs BBL 1.2–1.3%; `data/manual_facts/BBL.json`) because its book is heavier in SME and retail — this is a **normal cost** of KBANK (D1: not stripped). What changed in 2025–26 is that ECL fell from 51.9 bn to a 40 bn run-rate while coverage rose from 152% to 178% — provisions were cut and reserves still grew, consistent with slower new NPL formation (Trinity: Stage 2 8.6% at 4Q25, write-offs 6.0 bn in 4Q25 — "asset quality still to watch"). NIM fell 77 bp in 21 months (3.66% → 2.89%). BIS ≈ 20% is far above the regulatory floor (D-SIB floor from the BBL book, not re-verified). Tier 1 / CET1 after 2023: the press mirrors print only the total ratio; KBANK has no AT1 that I found, so Tier 1 ≈ CET1 (guess).

### 2.3 Where FY2025 profit came from — basis for normal EPS (Y annual lines + PR25; bank's own gain table not opened)

| line (m baht) | 2022 | 2023 | 2024 | 2025 | note |
|---|---:|---:|---:|---:|---|
| net interest income (PR) | 132,998 (TRI) | 148,444 | 149,376 | 137,152 | −7.33% in 2025 (NIM 3.64% → 3.23%) |
| non-interest income (PR) | 40,259 (TRI) | 44,210 | 48,570 · restated 50,240 | 57,648 | +7,408 (+14.75%) in 2025 on the restated base — wealth, insurance, investment (PR25) |
| of which gain on sale of securities (Y line) | −2,161 | 821 | 3,647 | **8,717** | +5,070 vs 2024; +7,948 vs 2022–24 average 769 |
| pre-provision profit (PR25 / TRI) | 98,505 | 107,685 | 113,994 | 109,951 | −3.55% in 2025 |
| ECL (PR) | 51,919 | 51,840 | 47,251 | 40,312 | normal bank cost — kept |
| net profit (PR = FS) | 35,770 | 42,405 | 48,598 (restated 49,603) | 49,565 | −0.08% vs restated |
| EPS (FS A5) | 14.78 | 17.58 | 20.21 (restated 20.63, Y) | 20.63 | Trinity prints 20.92 on 2,369 m shares; FS/Y implied shares 2,402.6 m — basis difference, both used as-is |
| one-time items disclosed by the bank | — | — | — | none found | 2026: Q1 "investment-value compensation" 1,455 m (Q126) |

Normal EPS FY2025 (our number): the bank disclosed no one-time item for 2025, but the Y line "gain on sale of security" is 8,717 m vs 3,647 m in 2024 and ≈0 in 2022–23. Strip the excess over 2024: 5,070 m × (1 − 19.9% effective tax, Y 13,871/69,640) = 4,060 m = 1.69/share on 2,402.6 m → **20.63 − 1.69 = 18.9**. Harsher variant (excess over the 2022–24 average 769 m): 7,948 × 0.801 = 6,365 m = 2.65/share → 18.0. Cross-checks: 9M26 ex one-off 39,180 m annualised ≈ 52 bn would say reported earnings are holding (EPS ≈ 21.7 on 2,402 m) — but 9M26 non-II is +21.5% YoY (Q3), i.e. the market-income component kept growing in 2026, so "normal" may be closer to reported than 18.9 if that income is recurring (wealth/insurance fees) and lower if it is mark-to-market. Trinity FY26F EPS 20.27 (−5%). 18.9 is proposed for `normal_eps` (section "ค่าที่ต้องจดลง config"); ECL and the restatement are not adjusted. The restatement of 2024 (48,598 → 49,603) is in the FY2025 comparatives (Y, thairath −0.08%); cause not stated in the mirrors (guess: TFRS 17 insurance adoption 2025).

### 2.4 Big-bank peers — snapshot Y 2026-10-28 (info call, may be intraday) + latest reported

| | KBANK | BBL | SCB (SCBX) | KTB | TTB |
|---|---:|---:|---:|---:|---:|
| price (Y) | 245.00 | 185.00 | 153.50 | 44.25 | 2.74 |
| PBV (Y) | 0.99 | **0.60** | 1.07 | 1.35 | 1.08 |
| PE trailing (Y) | 11.3 | **8.4** | 11.8 | 12.3 | 11.4 |
| dividend yield (Y, trailing 12 m) | 4.92% (= regular 12 ÷ 245, Y excludes the special) | 5.41% | 7.40% | 4.82% | 5.91% |
| ROE (Y TTM) | 8.5% | 6.5% | 8.7% | 10.8% | 9.1% |
| payout (Y) | 56% | 45% | 87% | 58% | 56% |
| market cap (Y, m) | 580,485 | 353,136 | 516,851 | 618,441 | 239,841 |
| profit 9M26 | 40,635 (+3.4%; −0.3% ex one-off) (Q3) | 29,981 (−21.6%) (KOC) | 1H26 21,312 (−15.7%) (BBL book TR) | 37,145 (9M, thansettakij 671949) | 16,139 (+4.8%) (KOC) |
| NIM latest | 2.89% (9M26) | 2.46% (1H26, BBL book) | 3.05% (1H26, BBL book) | 2.44% (Q3/26) | 3.02% (1H26, BBL book) |
| NPL latest | 3.18% (Q3/26) | 3.30% (1H26) | 3.17% (1H26) | 2.93% (Q3/26) | — |
| coverage latest | 177.9% (Q3/26) | 306% (1H26) | — | 205.3% (Q3/26) | — |
| BIS / CET1 latest | 19.77% / n.f. (Q3/26) | 21.4% / 16.9% (1H26) | — | 20.70% / 18.66% (Q3/26) | — |

Read: KBANK is priced at book (PBV 0.99) and at the sector PE; BBL is the one priced at 0.6× book. KBANK's edge is earnings resilience in 2026 (flat vs BBL −22%) and payout; its weaker spots are the lowest coverage of the three big banks shown and a higher structural credit cost. On trailing yield Y puts KBANK (4.9%) **below** BBL (5.4%) and TTB (5.9%) once the special is excluded.

### 2.5 Crisis years — paid? how deep? how long to recover (PP · FS A2 · BOT20/21)

| crisis | DPS before → during | cut | paid? | back to prior level | cause |
|---|---|---:|---|---|---|
| 1997–98 | 6.00 (FY1996, PP) → 3.00 interim only (FY1997) → no PP rows until the FS window (2004 = 1.00 adjusted) | −50% then −100% (reading of the PP gap) | suspended ~years | 6.00 again only in FY2023 (regular 6.50) = ~26 years on the adjusted series (yahoo adjusts pre-2003 by the par change — not like-for-like, DC-1) | systemic NPL + recapitalisation (not re-verified) |
| 2008–09 | 2.00 → 2.00 → 2.50 (FS A1) | 0% | normal | no cut | Thai NPL did not spike |
| 2020 COVID | 5.00 → 2.50 (final only, XD 20 Apr 2021) | **−50%** | final only | 5.00 passed in FY2023 (6.50) = 3 years | BOT order 19 Jun 2020 (no interim, no buyback) + FY2020/21 payout caps (BOT20/21) · EPS −25.3% (FS A5) — the cap, not the profit, set 2.50 (payout 21%, FS A12) |

Both deep cuts had a regulator's hand or a system crisis. KBANK's 2020 cut (−50%) was shallower than BBL's (−64%) because its 2019 base (5.00) was a lower payout.

---

## 3. คำตอบ D1–D18 ทีละข้อ

| # | answer | evidence (FS section / source + date) | type | confidence |
|---|---|---|---|---|
| D1 | **Headline yield 5.7% ≥5% — but regular yield 4.9% is just under C1.** DPS FY2025 14.00 ÷ 245.00 (close 2026-10-27) = 5.7% (FS A10); 2.00 of it is a one-time special (DIV, KHI) → regular 12.00 = 4.9%. 3-year average yield 4.4% total (FS flag AVG_YIELD_3Y; 3-year window = ours) / 3.8% regular (ours). Paid from normal profit? Mostly: FY2025 EPS 20.63 includes ≈5.1 bn more gains on securities than 2024 (Y) → **normal EPS FY2025 = 18.9** (removed: after-tax excess of gain-on-securities over 2024 = 1.69/share; kept: ECL 40,312 m as normal bank cost, insurance/wealth income as recurring; harsher 18.0). Payout on normal EPS: regular 63%, total 74% — < 100%, no PAYOUT flag. No loss year (FS). | FS A10 A5 A12 · 2.1 · 2.3 · Y annual · PR25 | number + person | medium (bank's own gain table not opened) |
| D2 | **Year-5 (FY2030) regular DPS: 12.00 / 13.58 / 15.32 baht at bad 0% / mid 2.5% / good 5% per year** → 4.9% / 5.5% / 6.3% of 245 (on total 14.00 base: 5.7 / 6.5 / 7.3%). Rates are earnings-based: reported-EPS CAGR 10 y 2.3%, 15 y 6.4% (FS A3), 2014→2025 0.6%, 2019→2025 4.1%; on normal 18.9: 1.4% / 5.8% / −0.2% / 2.6%; 5-y 11.3% rejected (base 2020 = BOT-cut year). What supports it: payout already ≥50% policy so DPS tracks EPS; buyback (≤2% of shares) lifts EPS/share; loans +6.3% YoY in Q3/26 (INVX); cost/income 40.8% (Q3); NIM near bottom (K-Research: 8-bank NIM up 4 bp QoQ in Q3). Obstacles: NIM 2.89% and NII −8.9% (Q3); policy rate 1.00% (MPC); profit ex one-off flat in 9M26; provisions already cut to 1.6% — little room left; SME/consumer loans contracting system-wide (BOTQ); Trinity FY26 −5%. **C2 on the regular base: bad case 4.9% < 5% (tripped by 0.1 pt), mid/good pass.** FS flag C2 today uses the mechanical mid 6.1% on 14.00 → not tripped. | FS A3 A4 · section 4 · Q3 · INVX · KR · BOTQ · TRI | number + person | medium |
| D3 | Not applicable as C3 exception (yield ≥5% on the headline). For the record: DPS up 5 straight years (FS A1) but 2021–23 is recovery from the BOT cut and 2024–25 growth came with regular payout 37% → 58% plus two specials (2.1, FS A12) — payout-driven, not counted as growth (A12 rule). | FS A1 A12 · DIV | number | high |
| D4 | **Can 12.00 regular hold if business falls?** On reported EPS 20.63, profit can fall 41.8% before regular payout hits 100% (32.1% vs total 14.00 — FS A5, ours); on normal 18.9: 36.5%. Worst EPS year 2020 −25.3% (FS A5) and the dividend fell 50% — by BOT cap (payout 21%), not inability (A2: one cut ≥10% in 22 years, recovered in 3). Capital: BIS 19.77%, coverage 177.9% at Q3/26 (2.2) vs 18.45% / 161% in Q3 2020. The binding constraint for a bank dividend is a regulator order (2020) or a credit-cost spike: at 2.2% of loans (2022–23 level) ECL would be ≈53 bn, i.e. ≈13 bn more than 2025 → net profit ≈ −21% → regular payout on that profit ≈ 73% (arithmetic, ours) — still payable. | FS A2 A5 A12 · 2.2 · BOT20/21 · `manual_facts/KBANK.json` | number + person | high |
| D5 | Revenue up 11/15 years, streak to latest year = 0 (2025 −2.3%, bank revenue follows the rate cycle — FS A5) · EPS up 3 years (2023–25; 2022 stumble −6% on ECL 51.9 bn) · DPS up 5 years. Stumbles: 2015 (EPS −14%, provisions), 2017 (−15%), 2020 (−25%, COVID + BOT), 2022 (−6%, ECL), 2026 in progress (ex one-off −0.3% 9M, NIM −34 bp YoY). Each was cyclical/provision-driven so far; net profit 2014 46,153 → 2025 49,565 = +0.65%/yr: **the decade is flat**, not a growth record. | FS A1 A5 · 2.2 · Q3 | number + person | high |
| D6 | Founded 8 Jun 1945 (Thai Farmers Bank, WK), listed on SET 1976 (WK) — 81 years old, 50 years listed · paid every year in the FS window 2004–2025 (22 years) but suspended after 1997 (2.5) · market cap 580,485 m (Y) · total assets 4,614,386 m (Q3) · net profit #1 among Thai banks 2024–25 (thairath 2909569). Passes C5 "old and large". Recorded in `manual_facts`. | WK · FS A1 · Y · Q3 · thairath | number | high |
| D7 | Policy (KHI, not verbatim): regular payout ≥50% of consolidated net profit, medium-term 50–60% (raised from 25% in 2025), specials / buyback case by case; FY2024 payout 58.5% incl. special (regular 46.3%), FY2025 67% (KHI). Actual: regular payout 20–31% for 2010–2023, 47% 2024, 58% 2025 (FS A12 on regular DPS, ours). Buyback ≤8.8 bn / 2% of shares, Nov 2025–May 2026 (BB). CEO Kattiya Indaravijaya since Apr 2020 (WK), ROE target double digit (KHI). Holders 10 Sep 2569: Thai NVDR 18.21%, **Gulf Development 9.99%** (SEC count 10.03% at 13 Feb 2026; BOT count < 10%, KHI), State Street Europe 6.13%, Social Security Office 2.81% (SH); Lamsam family not in the top 8. Gulf: "trading and dividend income", "no intervention" (SH); the payout-policy change, specials and buyback all came in 2025, the same period Gulf built its stake (fact of timing — causation = guess). SEC: search for cases against Gulf / its CEO on 2026-10-28 returned none (not proof of none, DC-4). Reading: management turned shareholder-friendly in 2025; whether the 50–60% band survives a bad credit year is untested. | KHI · FS A12 · BB · SH · WK | person | medium |
| D8 | **a. Industry declining?** Slow growth, not decline: system loans +2.0% YoY in Q2/26 on large corporates, SME + consumer contracting, NPL 2.82%, Stage 2 6.78% (BOTQ 18 Aug 2026) · 8 banks Q3/26: loans +3.9%, NIM 3.00% (+4 bp QoQ), NPL 3.11%, coverage 199% (KR 22 Oct 2026) · policy rate 1.00% since 25 Feb 2026 (MPC); 28 Oct 2026 decision not found at writing. KBANK's own revenue: NII −8.9% 9M26 (Q3). **b. What can disrupt:** (1) long low rates → NIM < 3% (happening) · (2) virtual banks — CLICX live since 19 Jun 2026 with a 4% deposit promo (VB); two more licences (SCBX-KakaoBank-WeBank, Ascend) per the BBL book, launch not verified; they target KBANK's own ground (retail deposits, SME, K PLUS 23.9 m users) · (3) BOT consumer-protection rules — INVX estimated a 2–3% profit hit for KBANK, above the sector's 1.5–2% (INVX Jul 2025) · (4) another BOT dividend order (2020) · (5) insurance accounting (TFRS 17) making non-II lumpier (guess). | BOTQ · KR · MPC · VB · INVX · Q3 | person | medium |
| D9 | #1 by net profit 2024–25 (thairath), #1 by total revenue 2025 (251,100 m, thebangkokinsight 1605833 search summary), K PLUS 23.9 m users in 2025 (thestandard search summary) — the retail/SME/digital leader; BBL leads corporate/international, KTB government. Loan market share: not found this round. "Bank of the Year 2026" (thaipublica, Apr 2026) is a magazine award, not a moat. What peers cannot copy quickly: K PLUS scale and SME franchise; what they can: pricing (virtual banks, VB). | thairath · search summaries · VB | person | medium |
| D10 | Bank substitute for "cash": BIS 19.77%, coverage 177.9%, credit cost 1.6%/yr (Q3; 2.2) → `manual_facts`. Ample vs the 2020 starting point (18.45% / 161%). Lower coverage than BBL (306%) and KTB (205%) — KBANK runs thinner reserves relative to NPL. | 2.2 · Q3 · 2.4 | number + person | high |
| D11 | Bank substitute for "debt": NPL 3.18% vs KTB 2.93% (Q3/26), SCB 3.17% (1H26), BBL 3.30% (1H26), 8-bank 3.11% (KR) — mid-pack; NPL stock 93,533 m end-2025 (thairath); Stage 2 8.6% at 4Q25 (TRI) is the number to watch. FS prints no A6 for banks (no ⛔ rows to handle). | 2.4 · KR · TRI · FS A6 note | number | high |
| D12 | Table 2.5: 2008 no cut; 2020 −50% by BOT order, 3 years back; 1997 interim only then a multi-year gap in the dividend record. | PP · FS A2 · BOT20/21 | number | high |
| D13 | Hidden value on paper: Muang Thai Life 38.25% net beneficial interest (MTL; consolidated via Muang Thai Group Holding — minority interests 6,204 m in 2025, Y, reflect it); KAsset, KSecurities, KBTG, Kasikornbank China, Bank Maspion Indonesia (stake not verified) (WK, MTL). At PBV 0.99 the market is not discounting the group the way it discounts BBL (0.60); excess capital ≈ 8 points of BIS over the floor (floor not re-verified) is being returned via specials + buyback (DIV, BB) rather than hidden. No separately listed subsidiary to mark. | Y · MTL · WK · 2.4 | number + person | low–medium |
| D14 | Vs own history (FS A10, year-end closes): yield 5.7% total at the 80th percentile of 2016–2025 year-end yields (1.7–7.7%) → FS label "cheap vs itself" (rule = ours) — but that history is inflated by the payout shift; on **regular** DPS the year-end yields are 2.3 / 1.7 / 2.2 / 3.3 / 2.2 / 2.3 / 2.7 / 4.8 / 6.1 / 6.2% and today 4.9% (ours) — above 7 of 10 years, below 2024–25. PE 11.9 on FY2025 EPS (13.0 on normal 18.9) — above 8 of 10 year-ends (7.7–16.2) and **not < 10** (P3, weak evidence) · PBV 0.99 within 0.54–1.43, above 7 of 10 year-ends · 52-week 178–261 (Y); 2026 range 183.5–258. Brokers: Trinity TP 186 Hold (22 Jan 2026, 0.7× PBV), CGSI FV 190 Hold (Feb 2026), INVX TP 280 Outperform (21 Oct 2026, DDM) — today's 245 is above the first two and below the third. "Another 20–30% down" (ours) = 196 / 171.5 → regular yield 6.1% / 7.0%. Price "appropriate" in Niwes' sense = person's call; on PBV and PE this is a mid-priced bank, on yield a cheap one only if the special repeats. | FS A10 · Y · TRI · KHI · INVX · section 7 | number + person | high |
| D15 | Belief table — section 5 (4 beliefs, counter-evidence with source + date, falsifier tied to a T flag). | section 5 | person | — |
| D16 | Flag table — section 6; every flag names the belief it watches, every belief has a flag. | section 6 | number + person | — |
| D17 | Art's call. Facts: the Niwes leg today = AMATA 35% + BBL 22.5% + TCAP 12.5% (+ TISCO off-plan); finance is already 2 of 3 in-plan names and 3 of 4 with TISCO; Art does not apply F1 "5 stocks 5 industries" (2026-10-19). Adding KBANK makes a second big Thai bank next to BBL: same regulator, same rate cycle, same 2020-type order risk; different book (retail/SME vs corporate), different payout (58% vs 42%), different price (PBV 1.0 vs 0.6). Section 8 gives the arithmetic. KOC's reason for the candidacy ("profit growing while BBL falls") holds on reported numbers and not ex one-off (2.2). | roadmap/agreed-portfolio-framework.md · KOC · section 8 | person | — |
| D18 | n/a — AMATA only. | — | — | — |

---

## 4. ปันผลเทียบต้นทุน (ปันผลปีนั้น ÷ ต้นทุน) — ก้อนที่ซื้อวันนี้ + ถ้าซื้อทุกเดือน (DCA) · facts only, 7–12% = direction (Art 2026-10-28)

Computed with the fact sheet's own functions (`scripts/fact_sheet.py` `yoc_table` / `dca_table` / `dca_yoc`, run 2026-10-28 from `C:/WORKSPACE/projects/4-MaxMahon` with `sys.path` → `scripts`) so the head can reproduce them by writing the scenarios + `special_dividends` into `config.json` and re-running `fact_sheet.py KBANK --refresh`. Price 245.00 (close 2026-10-27). **Primary base = regular DPS FY2025 12.00** (special excluded, deep-dive rule + DC-2); the sheet's base 14.00 is shown for comparison. Not held → no cost basis; "lump" = a cost equal to today's price (plus the F5-style levels of section 7).

### 4.1 Three earnings-based growth scenarios (ours — not Niwes' words, not a forecast)

| scenario | DPS growth/yr | why this number | what must be true |
|---|---:|---|---|
| bad | 0.0% | net profit 2014→2025 +0.65%/yr, EPS 2014→2025 +0.6% (FS A5); normal EPS 10-y 1.4%; 9M26 ex one-off −0.3% (Q3); NIM 2.89% and falling (Q3); Trinity FY26 −5%, DPS held at 12.00 | regular DPS held at 12.00 by keeping payout at the 60% top of the band; no BOT order; no special |
| mid | 2.5% | reported-EPS 10-y CAGR 2.3% (FS A3, base 2015 normal) ≈ normal-EPS 2019→2025 2.6%; plus ≤2% buyback once; system loans +2–4% (BOTQ, KR); BBL mid is also 2.5% — same macro | payout stays 55–60% of normal EPS; NIM stabilises ≥2.8%; credit cost ≤1.7% |
| good | 5.0% | reported-EPS 15-y CAGR 6.4% (FS A3, base 2010) trimmed for the payout already at the top of the band; 2019→2025 4.1%; ROE 8.5% × (1 − 0.58) ≈ 3.6% retained growth + buybacks | rate cycle turns up, NIM back toward 3.2%, cost/income ≤41% held, ROE toward the double-digit target (KHI), no NPL wave |

Rejected: 5-y EPS 11.3% (base 2020 = BOT/COVID year, GM-1); DPS CAGR 41% / 13% (payout-driven, A12 rule); the sheet's mechanical mid 6.1% / good 10%.

### 4.2 ก. Lump bought today at 245.00 — regular DPS in year N ÷ cost (other levels = section 7 ladder)

| scenario | growth | year | regular DPS | @245.00 | @220 (−10%) | @196 (−20%) | @171 (−30%) |
|---|---:|---:|---:|---:|---:|---:|---:|
| bad | 0.0% | 5 | 12.00 | 4.9% | 5.5% | 6.1% | 7.0% |
| bad | 0.0% | 10 | 12.00 | 4.9% | 5.5% | 6.1% | 7.0% |
| bad | 0.0% | 15 / 20 | 12.00 | 4.9% | 5.5% | 6.1% | 7.0% |
| mid | 2.5% | 5 | 13.58 | 5.5% | 6.2% | 6.9% | 7.9% |
| mid | 2.5% | 10 | 15.36 | 6.3% | 7.0% | 7.8% | 9.0% |
| mid | 2.5% | 15 | 17.38 | 7.1% | 7.9% | 8.9% | 10.2% |
| mid | 2.5% | 20 | 19.66 | 8.0% | 8.9% | 10.0% | 11.5% |
| good | 5.0% | 5 | 15.32 | 6.3% | 7.0% | 7.8% | 9.0% |
| good | 5.0% | 10 | 19.55 | 8.0% | 8.9% | 10.0% | 11.4% |
| good | 5.0% | 15 | 24.95 | 10.2% | 11.3% | 12.7% | 14.6% |
| good | 5.0% | 20 | 31.84 | 13.0% | 14.5% | 16.2% | 18.6% |

Same table on the sheet's base 14.00 (special assumed to repeat every year — not a fact): @245 mid = 6.5% (y5) / 7.3% (y10) / 8.3% (y15) / 9.4% (y20); bad = 5.7% flat; good = 7.3 / 9.3 / 11.9 / 15.2%.

Growth needed from 12.00 at cost 245 (facts): to 7% in year 5 = 7.4%/yr, year 10 = 3.6%/yr, year 15 = 2.4%/yr, year 20 = 1.8%/yr · to 12% in year 10 = 9.4%/yr, year 20 = 4.6%/yr. (From 14.00: 7% in year 10 needs 2.1%/yr.)

### 4.3 ข. New money bought monthly for 10 years then held — regular dividend in year N ÷ all money invested (FS A4 DCA rule: price grows with dividend / price flat)

| scenario | growth | year 5 grows / flat | year 10 grows / flat | year 15 grows / flat | year 20 grows / flat |
|---|---:|---|---|---|---|
| bad | 0.0% | 4.9% / 4.9% | 4.9% / 4.9% | 4.9% / 4.9% | 4.9% / 4.9% |
| mid | 2.5% | 5.2% / 5.5% | **5.6% / 6.3%** | 6.3% / 7.1% | **7.1% / 8.0%** |
| good | 5.0% | 5.6% / 6.3% | 6.3% / 8.0% | 8.1% / 10.2% | 10.3% / 13.0% |

Average purchase yield needed for year-10 dividend ÷ money invested to reach 7% / 12%: bad 7.00% / 12.00% · mid 5.47% / 9.37% · good 4.30% / 7.37% (today's regular yield 4.90%).

Same on base 14.00: mid 6.1 / 6.5% (y5) · 6.5 / 7.3% (y10) · 7.3 / 8.3% (y15) · 8.3 / 9.4% (y20); bad 5.7% flat; good 6.5 / 7.3 · 7.4 / 9.3 · 9.4 / 11.9 · 12.0 / 15.2%.

Read (fact): new money at today's price yields 4.9% regular; in the mid case it reaches 5.6–6.3% by year 10 and 7–8% by year 20. For comparison, BBL's book (price 186, mid 2.5%) gave 6.1 / 6.9% at year 10 — BBL starts higher because its regular yield is 5.4% vs KBANK 4.9%. KBANK only beats BBL on this table if the 2.00 special repeats (14.00 base: 6.5 / 7.3%) or the good case (5%) materialises.

### 4.4 ค. Actual past — not run. A monthly-DCA backtest on real closes 2016–2026 was not in this job; not done.

### 4.5 Numbers still unknown that would flip the answer
- Whether the 2.00 special repeats for FY2026 (board ~Feb 2027; CGSI expects it, KHI) — decides 4.9% vs 5.7% as the real starting yield.
- The split of 2025–26 non-interest income between recurring (wealth, insurance fees) and market gains (bank's own table, IR deck unreachable) — decides whether normal EPS is 18.9 or ≈20.6.
- FY2026 full year (≈21 Jan 2027) — first full year of NIM < 3%; Trinity −5%.
- Tier 1 / CET1 and Stage 2 trend after 4Q25 — not found in mirrors.

---

## 5. อะไรทำให้พัง — เรียงตาม โอกาสเกิด × ความเสียหายต่อปันผล

### 5.1 Belief table (D15 — C12 "avoid being fooled by the story") · "Niwes holds banks" / "Gulf is buying" are things to test, not reasons to hold

| # | what we want to believe (1 sentence) | strongest counter-evidence + source + date | what proves it wrong (→ flag in section 6) |
|---|---|---|---|
| B1 | "KBANK is the growth bank: profit #1 two years running, dividend doubled since 2023 — unlike BBL." | Net profit 2014 46,153 → 2025 49,565 = +0.65%/yr; EPS 2014→2025 +0.6% (FS A5) · DPS 6.50 → 14.00 came from regular payout 37% → 58% + specials (FS A12, DIV 26 Feb 2026) · 9M26 ex the 1,455 m one-off −0.3% YoY (Q3 21 Oct 2026) · NIM 3.66% → 2.89% in seven quarters (PR23, Q3) · Trinity FY26F −5% (22 Jan 2026) | T3: normal EPS down 2 fiscal years · T2: mid-case year-10 regular yield < 7% at 245 (it already is: 6.3%) — the growth story needs the good case |
| B2 | "5.7% yield from Thailand's biggest bank is safe and recurring." | 2.00 of the 14.00 is a one-time special (DIV); regular 12.00 = 4.9% < C1 5% · regular payout 58% is at the top of the stated 50–60% band (KHI 4 Aug 2025) — the next step up must come from EPS · Y trailing yield 4.92% (special excluded) ranks KBANK below BBL and TTB (2.4) | T1: FY2026 regular DPS < 12.00 → count starts · no special for FY2026 → total < 14 (not a cut of the regular, but B2 dead) |
| B3 | "BIS 20% and coverage 178% mean the dividend cannot be cut." | 2020: Tier 1 15.7%, BIS 18.5%, coverage 161% (Q3 2020) and the dividend still fell 50% by BOT order (BOT20/21) · credit cost 2.0–2.2% in 2022–24 (2.2) is the highest of the big banks — profit is more NPL-sensitive than BBL's · Stage 2 8.6%, write-offs 6.0 bn in 4Q25 (TRI 22 Jan 2026) · coverage 178% is the lowest of KBANK / BBL / KTB (2.4) | T4-bank: BIS < 16% or a BOT dividend order · T5: NPL > 4.5% or coverage < 140% · T3 |
| B4 | "Gulf at 10% brings a strategic upside (virtual bank, fintech) and keeps management shareholder-friendly." | Gulf states the stake is for "trading and dividend income" and that it does not intervene (SH, thairath 16 Oct 2024; hoonvision 2026) · BOT caps a holder at 10% without approval (KHI 16 Feb 2026) · KBANK's own virtual-bank play is not among the three licensees (VB) · the INTUCH precedent is an analogy, not evidence | No numeric flag — watch D7: a related-party deal, a board change, or a payout-policy change tied to a specific holder would be the signal (person's call) |

### 5.2 Non-belief risks — ranked by chance × damage to regular DPS (facts; judgement is ours)

| # | cause | chance (10 y) | damage to DPS | temporary / permanent | evidence |
|---|---|---|---|---|---|
| 1 | Policy rate ≤1.0% for years → NIM ≤2.9%, NII keeps falling | high — happening: 1.00% since Feb 2026; NII −8.9% 9M26 | DPS flat (payout cannot go much above 60%) | cyclical but possibly 5+ years | MPC · Q3 |
| 2 | SME / retail NPL wave → credit cost back to 2.0–2.2% | medium-high — Stage 2 8.6%, SME + consumer loans contracting system-wide, KBANK's book skews there | profit −20% in the year; DPS −10–25% if the board holds payout ≤60% | 1–3 years | TRI · BOTQ · 2.2 |
| 3 | BOT orders dividend limits again (system shock) | medium — done 2020–21, power not withdrawn | −50% for a year, 3 years back | temporary; trips T1 without business failure | BOT20/21 · 2.5 |
| 4 | Provisions and costs already cut — no more "defence" left when revenue falls | high (it is the 2025–26 mechanism: ECL 51.9 → 40.3 bn, cost/income 44 → 40.8%) | profit falls one-for-one with NII from here | structural | 2.2 · Q3 |
| 5 | Virtual banks + deposit competition raise funding cost / take SME margin | low–medium first 5 years, rising — CLICX live Jun 2026 at 4% promo | NIM −0.1 to −0.3 pt → profit −5–10% | permanent, slow | VB |
| 6 | BOT conduct rules (responsible lending, fee caps) | medium — INVX put the hit at 2–3% of profit for KBANK | −2–3% | permanent | INVX Jul 2025 |
| 7 | Non-interest income is market-driven (securities gains 8.7 bn in 2025, +21% non-II in 9M26) and reverses | medium — exactly what hit BBL in 2026 | EPS −5–10% in the year | temporary | 2.3 · Q3 |
| 8 | 1997-type systemic crisis + recapitalisation | low — BIS 20% | −100% for years + dilution | permanent per old share | 2.5 |
| 9 | Governance shift with a 10% strategic holder (related-party lending, board) | low — no evidence; BOT 10% cap | unknown | — | SH · KHI |

Summary: what makes the dividend disappear (3, 8) is regulator- or crisis-driven and rare; what makes it stall (1, 4) is under way; what makes it dip 10–25% (2, 7) is a normal credit cycle for a bank with KBANK's book. KBANK's main risk to the plan is the same as BBL's — "no growth" — with one difference: KBANK has already used the payout lever, BBL has not.

---

## 6. ธง "ผิดทาง" เฉพาะ KBANK (T1–T6 ปรับให้ธนาคาร — เลขเกณฑ์ กูตั้ง Art เคาะ)

| flag | bank measure | value today (source) | opens a review | points to "permanent" | watches belief (D16) | where to read |
|---|---|---|---|---|---|---|
| T1 | regular DPS of fiscal year below prior year (specials excluded) | FY2025 regular 12.00 (+26%) — not tripped (FS, 2.1) · FY2026 interim 2.00 = same as 2025 (PP); final unknown | regular DPS down 2 fiscal years (FY2026 + FY2027) | down 3 years, or regular < 6.50 (2023 level) without a BOT order | B1, B2 | set.or.th / PP, Feb–Mar (final) + Aug–Sep (interim) — read the board announcement for the regular/special split |
| T2 | regular yield on a cost = today's price in year 10, mid scenario | 6.3% at 245 (section 4.2; on 14.00 base 7.3%); FS mechanical 10.4% — not comparable | mid-case projection < 7% ⇔ 12.00 × 1.025^10 = 15.36 < 17.15 — **already below 7% at 245**; passes at ≤220 (7.0%) | — | B1 | recompute each year after the final dividend |
| T3 | why the dividend fell: normal EPS / payout / BOT | normal EPS FY2025 18.9 (ours, 2.3); 9M26 ex one-off −0.3%; NIM 2.89% | normal EPS down 2 fiscal years **and** NIM < 2.7% four straight quarters | profit down 3 years with credit cost ≤1.7% (= revenue structure broken, not a credit cycle) | B1, B3 | quarterly results (press-release mirrors) |
| T4 (bank) | capital instead of cash flow: BIS trend + payout | BIS 19.77% (Q3); regular payout 58% reported / 63% normal; buyback 2% | BIS < 16% or regular payout > 70% of normal EPS two years, or a BOT dividend order | BIS < 12% or capital raise announced | B3 | quarterly results · BOT circulars |
| T5 | industry: NPL system + policy rate + virtual banks | KBANK NPL 3.18%, system 2.82% (BOTQ), 8-bank 3.11% (KR) · rate 1.00% · CLICX live | KBANK NPL > 4.5% or coverage < 140% · rate ≤0.5% for 2 years · Stage 2 > 10% | NPL > 6% with coverage < 120% · CASA share falling 3 years | B3 | half-year bank tables (thairath 11-bank), BOTQ, MPC |
| T6 (bank) | NPL vs peers + credit cost vs peers | 3.18% vs KTB 2.93 / SCB 3.17 / BBL 3.30; credit cost 1.6% vs BBL 1.5% (1H26) | NPL gap > 1.0 pt above the big-4 average 3 years running, or credit cost > 2.2% two years | gap > 2 pt and coverage below peers | B3 | half-year peer tables |

FS flags on 2026-10-28: T1 ✅ not tripped · T2 ✅ not tripped on the sheet's mechanical scenarios (tripped on this book's mid 2.5% / base 12.00 — see T2 row) · C2 ✅ on the sheet; on this book's bad case 4.9% < 5% · PAYOUT ✅ 68% (74% on normal EPS) · LOSS ✅ none · T4/T6 replaced above. Next data: MPC decision 28 Oct 2026 · FY2026 results ≈ 21 Jan 2027 (Y earnings date 2027-01-20) · final + special dividend board ≈ late Feb 2027, XD ≈ Apr 2027.

---

## 7. ราคาตอนนี้ — เทียบประวัติตัวเอง (ราคาปิดจริง) + เทียบคู่ · ข้อเท็จจริงให้คน DCA คิด ไม่ใช่คำสั่ง

- Close 245.00 on 2026-10-27 (FS, Y) · 52-week 178–261 (Y) → 6% below the high, 38% above the low · 2026 range 183.5–258; 2025 range 146–197; 5-year low 119.0 on 2024-02-15 (Y, real closes).
- Own history (FS A10 + Y year-end closes, not dividend-adjusted): year-end closes 2016–2025 = 177.5 / 232 / 185 / 151 / 113 / 142 / 147.5 / 135 / 155.5 / 194.5 — **245 is above every year-end close of the last ten years**; the last time it closed a year above 232 was 2017. PE 11.9 (13.0 on normal EPS) vs year-end 7.7–16.2 · PBV 0.99 vs 0.54–1.43 · regular yield 4.9% vs year-end 1.7–6.2% (section 3 D14).
- Peers (2.4): mid-priced on PBV/PE; on regular yield below BBL and TTB.
- Brokers: Trinity 186 Hold (Jan 2026) · CGSI 190 Hold (Feb 2026) · INVX 280 Outperform (Oct 2026). Spread 186–280 brackets today's price; the two older targets are below it.
- "Another 20–30% down" (ours, D14): 196 / 171.5 → regular yield 6.1% / 7.0%; total-14 yield 7.1% / 8.2%.

### Cheap levels (for the cash-ammo step if it enters the portfolio) — same shape as the F5 ladder (`roadmap/agreed-portfolio-framework.md` F5: three steps, 1/3 of the ammo each, yield on last full year's dividend, shoot only on market/mood falls, never when `holdings_watch.py` shows "เปิดทบทวน")

| step | price | regular yield (12.00) | total yield (14.00) | PBV (BVPS 247.76, Y) | where that is in KBANK's own history (real closes) |
|---|---:|---:|---:|---:|---|
| 1 | ≤220 (−10%) | 5.5% | 6.4% | 0.89 | still above every year-end close 2016–2025 except 2017 (232); 2025 closed 194.5; 2026 low 183.5; year-10 mid regular yield at this cost = 7.0% (4.2) |
| 2 | ≤196 (−20%) | 6.1% | 7.1% | 0.79 | ≈ 2025 year-end (194.5) and 2025 high (197); above 8 of 10 year-end closes |
| 3 | ≤171 (−30%) | 7.0% | 8.2% | 0.69 | ≈ Trinity 0.7× book (TP 186 Jan 2026); below the 52-week low 178; 2024 year-end 155.5 and 2025 low 146 are lower still |

Ladder convention copied from BBL's F5 steps (−10 / −20 / −30% of the deep-dive price). Facts only: at step 3 the regular yield equals Art's 7% lower direction at year 0; at today's price it needs 2.4%/yr growth for 15 years (4.2). Cash-for-panic is a portfolio question (F5) — no order here.

---

## 8. น้ำหนักในพอร์ต — ถ้าเติม KBANK แล้วกลุ่มธนาคารโดนพร้อมกันแบบปี 2563 ปันผลรวมหายเท่าไร (Art ตั้งใจ R5 — ไม่เสนอแก้)

- KBANK is not in the plan; weight = 0 today. If added at weight w next to BBL 22.5% and TCAP 12.5%, a 2020-type BOT order (KBANK −50%, BBL −64%, TCAP/TISCO finance also covered by the 2020 letter — BOT20) removes ≈ w × 50% + 22.5% × 64% + (TCAP's cut) of the portfolio's dividend for that year, if every holding yields about the same (arithmetic, ours). Example w = 10%: ≈ 5% + 14.4% + TCAP's share ≈ 20%+ of one year's dividend.
- Correlation is the point, not KBANK itself: the 2020 experience was a system-wide order; KBANK and BBL recovered in the same 3 years (FS A2 both).
- No proposal on weight — Art's intent (R5). Facts only.

---

## 9. สิ่งที่ algo ควรเตรียมเพิ่มสำหรับหุ้นธนาคาร (รอบนี้ต้องหามือ)

- `special_dividends` for KBANK (2024: 2.50, 2025: 2.00) must be entered for A1/A2/A3/A4/A12 and the gate's yield to use the regular 12.00 — today the sheet reports 5.7% and +85%/+17% growth with the specials inside. Values at the end.
- `data/manual_facts/KBANK.json` written this job (founded/listed, policy, specials, buyback, bank table 2020–9M2026, BOT 2020 note) — the sheet prints it as-is (`fact_sheet.py` `_manual`).
- Still manual every round: regular/special split from the board announcement (panphol does not flag specials — DC-2); gain-on-securities line (normal EPS); Tier 1 / CET1 (press mirrors print only BIS); Stage 2 and write-offs (broker notes). Sources that worked: thestandard / brandinside / thaipr / brandbuffet / thansettakij mirrors of the bank's own release; Trinity PDFs via curl + pypdf (`C:\WORKSPACE\_shared\knowledge\code\web-fetch-pdf.md`).
- Not done: historical DCA backtest (4.4); 2016–2019 bank rows; bank IR deck (unreachable).

## 10. จุดที่ของเดิมใน `research/` กับใบข้อเท็จจริง ผิด / เก่า

| # | file:line / section | says | actual (source) | type |
|---|---|---|---|---|
| 1 | KOC section 3, KBANK row | yield 5.7% · DCA y10 mid 7.8% / 10.4% · "profit growing while BBL falls" | 5.7% includes a 2.00 special; regular 4.9% (2.1) · DCA numbers were the sheet's mechanical 2.3–10% scenarios on 14.00; on this book's 0 / 2.5 / 5% and 12.00 they are 4.9 / 5.6 / 6.3% (4.3) · 9M26 profit ex the 1,455 m one-off −0.3% (Q3) | superseded |
| 2 | FS A1 | FY2024 12.00 (+85%), FY2025 14.00 (+17%) | regular 9.50 / 12.00; specials 2.50 / 2.00 (2.1, DIV) — config `special_dividends` empty for KBANK | incomplete (config) |
| 3 | FS A3 | DPS CAGR 5 y 41.1%, 10 y 13.3% | base 2020 = BOT-cut year; payout-driven (A12 rule) — not used | data trap (GM-1) |
| 4 | FS A4 / flags T2 C2 | mid 6.1% / good 10% mechanical, base 14.00 → 10.4% y10 | this book: mid 2.5% on 12.00 → 6.3% (4.2); T2 tripped on this basis | superseded pending Art |
| 5 | FS A5 2024 EPS 20.21 / net profit 48,598 | pre-restatement | FY2025 comparatives restate 2024 to 49,603 m / EPS 20.63 (Y, thairath −0.08%) — cause not stated | old basis (noted, not changed) |
| 6 | Trinity 22 Jan 2026 EPS 2025A 20.92 | — | FS/Y 20.63 — share-count basis (2,369 m vs 2,402.6 m implied); payout 67% vs 68% | basis difference |
| 7 | kaohooninternational ?p=578052 (27 Feb 2026) | "BBL FY25 total DPS THB 12 (final 10 + interim 2), payout 50%" | BBL book 2.1 / PP: BBL FY2025 = 2.00 + 8.00 = 10.00 — the summariser's BBL figures conflict with three sources; not used | conflicting source |
| 8 | search summary "FY2021 NIM 3.66%, NII 148,444" | — | those are FY2023 numbers (PR23); FY2021 NIM = 3.21% (PR21) — summariser mixed years | snippet error (DC-3) |
| 9 | thestandard ?p=410576 (fetched as "Q3/2026") | — | page is Q3/2020 (21 Oct 2020) — used only as the 2020 capital row in 2.2 | wrong page, re-labelled |
| 10 | Trinity 22 Jan 2026 "Loans & Accrued interest … 2,411,825" | — | column labels not legible in the text extract; read as 4Q25 — credit cost 2025 "ours" carries that uncertainty (2.2) | uncertain |

---

## ค่าที่ต้องจดลง config — Values for config (NOT written — awaiting Art)

The head writes this into `config.json` (this job did not touch it). Form follows `docs/deep-dive.md` step 3. After writing, re-run `fact_sheet.py KBANK --refresh` so A1/A3/A4/A12 pick the values up.

```json
{
  "special_dividends": {
    "KBANK": {"2024": 2.5, "2025": 2.0},
    "_source_KBANK": "research/kbank-deep-dive-2026-10-28.md section 2.1 — FY2024 special 2.50 (XD 15 May 2025, from retained earnings; share2trade 40990 / kaohoon 741441 Apr 2025) · FY2025 special 2.00 inside the 12.00 final (XD 21 Apr 2026; mitihoon 26 Feb 2026, kaohooninternational 27 Feb 2026). Regular FY2024 = 9.50, FY2025 = 12.00",
    "_as_of": "2026-10-28"
  },
  "normal_eps": {
    "KBANK": {
      "2025": 18.9,
      "2024": 20.21,
      "_source": "research/kbank-deep-dive-2026-10-28.md section 2.3 — FY2025: reported EPS 20.63 (FS/SETSMART; 49,565 m on 2,402.6 m implied shares) minus after-tax excess of gain-on-securities over 2024 ((8,717 - 3,647) m x (1 - 0.199) = 4,060 m = 1.69/share; yfinance annual line, bank's own table not opened); ECL 40,312 m kept as normal bank cost; wealth/insurance income kept as recurring; harsher variant 18.0 (excess over 2022-24 average). FY2024: reported EPS kept (pre-restatement basis of the FS A5 series; restated 20.63), no one-time item identified",
      "_as_of": "2026-10-28"
    }
  },
  "holdings": {
    "growth_scenarios": {
      "KBANK": {
        "bad": 0.0,
        "mid": 0.025,
        "good": 0.05,
        "source": "research/kbank-deep-dive-2026-10-28.md section 4.1 — earnings-based: net profit 2014-2025 +0.65%/yr, reported-EPS CAGR 10 y 2.3% / 15 y 6.4% (FS A3), 2019-2025 4.1%, normal-EPS 2019-2025 2.6%; 5-y 11.3% rejected (base 2020 = BOT-cut year); DPS CAGR rejected (payout 37% -> 58% + specials). bad = regular DPS 12.00 held while NIM compresses; mid = long-run EPS growth + one buyback; good = 15-y reported rate trimmed for payout already at the 60% top of the band. Base DPS = regular 12.00 (special excluded)",
        "as_of": "2026-10-28"
      }
    }
  }
}
```

Note for the head: `growth_scenarios` lives under `holdings` in the current config; KBANK is not a holding — if the sheet only reads overrides for held symbols, entering it there is still how `load_growth_override` finds it (it reads `holdings.growth_scenarios[SYM]` regardless of `costs`).

---

## acceptance (ไล่ทีละข้อ)

- every D1–D18 answered with fact-sheet section or external source + date → section 3, each row has an evidence column with FS section codes and source codes dated in the source table.
- D1 has normal EPS FY2025 with what was removed and why → section 3 D1 + 2.3 (removed: after-tax excess of gain-on-securities over 2024 = 1.69/share → 18.9; kept: ECL, insurance/wealth income; harsher 18.0).
- D2 has a numeric year-5 DPS from an earnings-based rate plus obstacles → section 3 D2 + 4.1/4.2 (12.00 / 13.58 / 15.32 at 0 / 2.5 / 5% → 4.9 / 5.5 / 6.3% of 245).
- D4 uses A2 + the 2020 BOT dividend restriction + the bank table → section 3 D4 (FS A2, BOT20/21, table 2.2 → `manual_facts`).
- D15 has ≥2 beliefs each with sourced counter-evidence and a falsifier tied to a T-flag → section 5.1 (B1–B4; B4's falsifier is a person's watch, stated as such).
- D16 maps every flag to a D15 belief → section 6 column "watches belief".
- D18 = "n/a — AMATA only" → section 3 D18.
- A6 ⛔: the sheet prints no A6 for banks; no ⛔ rows to handle → section 3 D11.
- Forward growth EPS-based on normal earnings; abnormal bases (2020) rejected → 4.1 · real closes used for price history → section 7 (Y `auto_adjust=False`) · DPS cross-checked across 3 sources per year → 2.1 · Q3/2026 and 9M/2026 included → 2.2 · bank table written to `data/manual_facts/KBANK.json` and the sheet re-run → header · DCA/lump y5/y10/y15/y20 both price modes, 3 scenarios, lump at today's price → 4.2/4.3 · values for config at the end · cheap ladder three steps → section 7 · no buy/sell order, no verdict on 7–12% → throughout.
- Files written: `research/kbank-deep-dive-2026-10-28.md` (this) · `data/manual_facts/KBANK.json` (git-ignored under `data/`) · `reports/facts/KBANK_2026-10-28.md` regenerated by `fact_sheet.py KBANK --refresh` (price unchanged 245.00; now prints the manual facts) · scratch: `C:/WORKSPACE/_desk/_scratch/kbank-dd/` (yfinance JSON, Trinity PDF texts). `config.json` and scripts untouched.
