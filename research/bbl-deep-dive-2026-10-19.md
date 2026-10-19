# BBL deep dive — "ถือและซื้อตัวนี้ต่อไปทุกเดือนอีก 10 ปี เรามาถูกทางไหม?"

- Written 2026-10-19 · job job-13-dd-bbl (desk z79h) · Niwes leg, 22.5% weight · holding 3,400 shares, average cost 172.10 (`config.json` holdings.costs)
- Template: `docs/deep-dive.md` (steps + pass criteria) · questions D1–D18 and flags T1–T6: `docs/niwes-principles.md` sections 4–5 · 10-section layout copied from `research/amata-deep-dive-2026-10-09.md` (format only)
- Starting data = fact sheet `reports/holdings/BBL_2026-10-19.md` (FS) built after the system changes (EPS-based growth, normal EPS slots, C2 flag). Nothing was copied from the 2026-10-09 book; it was read for leads only and every number was re-checked (section 10).
- Owner's 7–12% yield-on-cost target is parked (deep-dive.md): A4 / DCA numbers are reported as facts, no conclusion on whether the target is reached.
- **Q3/2026 results: not published as of 2026-10-19.** yfinance earnings calendar = 2026-10-20 (Y) · broker preview 16 Oct 2026 expects net profit 9.8 bn, −29% YoY, +3% QoQ (BLS) · sector preview 14 Oct 2026 (TK). Everything below ends at 2Q26 / 1H26 actuals.
- Language: this book is written in English (worker rule); Thai headings are copied from the template files.

## รหัสแหล่ง (ใช้ซ้ำทั้งไฟล์)

| code | source | data to | fetched |
|---|---|---|---|
| FS | `reports/holdings/BBL_2026-10-19.md` — `fact_sheet.py BBL --cost BBL=172.10` after the system changes: A1 DPS 2004–2025 (set.or.th 2021+, yahoo before), A2 cuts, A3 CAGR, A4 yield-on-cost (config scenarios of 2026-10-09 still in effect), A5 EPS/ROE 2010–2025, A12 payout, A10 year-end PE/PBV/yield 2016–2025 | FY2025 · close 186.00 on 2026-10-15 | 2026-10-19 |
| Y | yahoo via yfinance (`C:/WORKSPACE/_desk/maxmahon/z79h/files/bbl_yf.py` → `bbl_yf_out.json`): annual P&L/BS 2022–2025, quarterly 2Q25–2Q26, XD list 2019–2026, close 185.00 on 2026-10-19, 52-week 152.5–204.0, market cap 353,136 m, shares 1,908.8 m, book value/share 303.6, earnings date 2026-10-20; peer snapshot KBANK SCB KTB TTB | 2Q26 · 2026-10-19 | 2026-10-19 |
| PP | aio.panphol.com/stock/BBL/dividend (every XD row 2015–2026 + 1981–1997 window) · /sholder (top holders, record 10 Sep — page year not legible in fetch) | XD 9 Sep 2026 | 2026-10-19 |
| PR21–PR25 | BBL full-year press releases via mirrors: FY2021 thaipr.net ?p=3146796 (21 Jan 2022) · FY2022 thaipr.net ?p=3293129 (20 Jan 2023) · FY2023 brandinside.asia ?p=161913 (18 Jan 2024) · FY2024 thaipr.net ?p=3563659 (22 Jan 2025) · FY2025 thaitabloid.com/archives/274317 + thansettakij 649446 + thairath 2908988 (20–29 Jan 2026) — ECL, NPL, coverage, CET1/Tier1/CAR, NIM, loans | FY2025 | 2026-10-19 |
| IQ | infoquest.co.th/2026/619524 (22 Jul 2026) — Q2/2026 + 1H26 results: profit, NIM, ECL, loans, deposits, NPL, coverage, CAR/Tier1/CET1 | 30 Jun 2026 | 2026-10-19 |
| TR | thairath 2947799 (22 Jul 2026) — 11 Thai banks 1H26: profit, NIM, NPL ratio and amount | 30 Jun 2026 | 2026-10-19 |
| UOBKH | UOB Kay Hian results note 22 Oct 2025 (utrade.co.th PDF, extracted with pypdf → `files/utrade_bbl.pdf`): 3Q25 table, 2024 actual credit cost 1.29%, FVPL/investment gains by quarter 2025, 2025 targets, GGM cost of equity 11%, holders Oct 2025 | 3Q25 | 2026-10-19 |
| DBS | DBS Vickers 29 Apr 2026 note (1Q26: NPL 3.1%, coverage 318%, ECL 9.0 bn, FY26 guidance, TP 168 HOLD at 0.56x) · DBS 2Q26 note via search summary only (credit cost 148 bp 1H26 vs 152 bp FY25, CET1 16.9%, ECL 8.4 bn 2Q26) | 2Q26 | 2026-10-19 |
| BLS | hoonvision.com/hoonset/bbl-11 (16 Oct 2026) — Q3/26 preview: profit 9.8 bn, NIM 2.4%, NPL 3.5%, coverage 303%, FY26 −15%, FY27 +4%, TP 210 (from 213) | preview | 2026-10-19 |
| TK | thansettakij 671402 (14 Oct 2026) — sector Q3/26 preview: 6–7 banks profit −7 to −13% YoY, NII −7.4%, NIM bottoming after 75 bp of cuts | preview | 2026-10-19 |
| BOT20 | thaipublica 19 Jun 2020 — BOT order to suspend 2020 interim dividends + buybacks (Governor Veerathai) · BOT21 = bot.or.th press release 82/2564, 11 Nov 2021 — FY2021 dividends ≤50% of profit; FY2020 rule was ≤2019 payout rate and ≤50% of 2020 profit | 2020–21 | 2026-10-19 |
| BOTQ | BOT Banking Sector Quarterly Briefs: Q4/2025 (news-20260217, 17 Feb 2026) · Q2/2026 (news-20260818, 18 Aug 2026) · 2024–2025 quarters via search summaries (pattayamail, nationthailand) | 2Q26 | 2026-10-19 |
| MPC | naewna 961443 (29 Apr 2026: hold 1.00%, GDP 2569 1.5% / 2570 2.0%) · nationthailand 40070282 (26 Aug 2026: hold 1.00%, unanimous) · no October 2026 decision found in search | 26 Aug 2026 | 2026-10-19 |
| HH | naewna 977867 (17 Jul 2026, SCB EIC) — household debt 85.9% of GDP Q1/2569, "constraint-driven deleveraging" | Q1/2026 | 2026-10-19 |
| VB | search summaries only: 3 virtual-bank licences approved 19 Jun 2025 (KTB+AIS+OR "CLICX" · SCBX+KakaoBank+WeBank · Ascend Money); CLICX "expected" June 2026, two groups asked for delay — actual launch not verified this round | 2026 | 2026-10-19 |
| PMT | bisnis.com 30 Jul 2026 — Permata 1H26 profit IDR 1.72 tn +4.5%, loans IDR 171.2 tn +5.3%, NPL 2.1%, coverage 367.5% · idnfinancials Q1/26 · BNLI market cap IDR 82.7–87.6 tn (Jul 2026, search summary) | 1H26 | 2026-10-19 |
| WK | en.wikipedia.org/wiki/Bangkok_Bank — established 1944, listed on SET 1975, president Chartsiri Sophonpanich, Permata 89.12% bought 2020 for Rp 33.66 tn (US$2.3 bn) | — | 2026-10-19 |
| SH | shareholder snippets: 23 Apr 2569 Thai NVDR 23.38%, City Realty 4.70%, top 21 holders 54.84% (pptvhd36/panphol via search) · UOBKH Oct 2025: Thai NVDR 23.24, City Realty 4.77, Social Security Office 4.30 · SEC = bangkokbiznews 1242195 (19 Oct 2026) | 2026 | 2026-10-19 |
| DP | dividend-policy wording = search-engine summary of a bangkokbank.com AGM-2026 document (…/-/media/e5d793cf98bf476c91d0c3f3b91ead7c.ashx); the original could not be opened → **not verbatim** | AGM 10 Apr 2026 | 2026-10-19 |
| OLD | `research/bbl-deep-dive-2026-10-09.md` — leads only; its numbers are not reused unless re-checked here (section 10) | 2026-10-09 | — |

Unreachable this round: bangkokbank.com (curl connection reset / 90 s timeout ×3, WebFetch 60 s timeout ×3 — IR presentations 4Q25 + 2Q26, dividend announcement PDF, dividend-policy page) · set.or.th API 403 (Incapsula) · regulationasia + marketscreener paywalled. Consequence: bank ratios come from press-release mirrors and broker notes, not from the IR deck.

---

## 1. คำตอบ 1 หน้า

**Answer (facts first, decision stays with Art and the head — R6):** BBL today is a bank whose dividend is covered several times over by capital and provisions, priced below book, yielding 5.4% on the last full year — but the earnings that paid FY2025's 10.00 baht were held up by a one-year jump in market gains, and 2026 operating profit is falling. "Right track" for 10 more years of monthly buying therefore rests on one question: does the dividend hold at ~10 baht while NIM compresses, not on dividend growth.

1. **Yield today passes C1 but not cleanly.** DPS FY2025 10.00 ÷ 186.00 = 5.4% (FS A10) · 3-year average yield 4.6% (FS, flag AVG_YIELD_3Y) · FY2025 EPS 24.09 includes ~12.7 bn of extra non-interest income vs 2024 (Y) — our normal EPS for FY2025 is **18.6**, payout on normal EPS 54% (section 3 D1).
2. **Year-5 dividend on an earnings-based rate is 10.0 / 11.3 / 12.5 baht (bad 0% / mid 2.5% / good 4.5%)** → 5.4% / 6.1% / 6.7% of today's price; all ≥5% (C2) only if the payout does not fall back toward its 16-year norm of 35–42% (FS A12). On cost 172.10: 5.8% / 6.6% / 7.2% in year 5 (section 4, facts only).
3. **The dividend has been cut twice in 30 years and both times a regulator or a system crisis was involved**: FY1997 −67% then nothing FY1998–2003 (PP gap, old book), FY2020 −64% by BOT order (BOT20/BOT21). Capital today (CET1 16.9%, CAR 21.4%, coverage 306%, IQ) is far above 2020 levels — the risk is a repeat order, not insolvency.
4. **2026 is the first down-year of the 5-year streak**: 1H26 profit 20,492 m −16.2% YoY, NIM 2.46% (IQ) · brokers see FY26 −11% to −15% (DBS, BLS) · interim FY2026 held at 2.00 (XD 9 Sep 2026, PP/Y). NPL 3.3% is the highest of the big four and the NPL stock rose 11% in six months (TR).
5. **What does not hold up in the old story**: "dividend grows 32%/yr" (base = BOT-cut year 2020), "PBV 0.6 = half price" (PBV has sat at 0.47–0.96 for ten years while ROE 7–8% stays below the 11% cost of equity brokers use), "excess capital will be released" (payout 35–45% for 16 years, policy has no % commitment).

**Confidence: medium.** Dividend, profit, capital and NPL figures agree across 2–3 sources (FS, Y, PP, PR, IQ). Low-confidence items: normal EPS (computed from yfinance line items, not the bank's own FVTPL/investment-gain table — IR deck unreachable), growth scenarios (judgement), Q3/2026 (unpublished).

**Items Art and the head must decide (not decided here):**
- Which growth scenario set goes into `holdings.growth_scenarios` (proposed bad 0% / mid 2.5% / good 4.5%, section "ค่าที่ต้องจดลง config") and whether normal EPS FY2025 = 18.6 (strip all excess gains vs 2024) or the softer 20.5 (FY2026 forecast run-rate) is the base.
- Whether "dividend held flat at 10 for 5 years" (bad case, 5.4% on today's price) still counts as right track under C2/C4, since it passes 5% only by 0.4 points.
- Whether a BOT-ordered cut (like 2020) counts toward T1 — it trips the statistic without being a business failure.

---

## 2. ใบข้อเท็จจริง

### 2.1 Dividend per share by fiscal year — three sources compared (FS A1 · PP · Y XD list)

| FY | FS A1 (set.or.th / yahoo) | PP (interim + final) | Y XD list | agree? |
|---|---:|---|---|---|
| 2017 | 6.50 | 2.00 (XD 5 Sep 2017) + 4.50 (XD 23 Apr 2018) | — | ✓ |
| 2018 | 6.50 | 2.00 + 4.50 (XD 23 Apr 2019) | 4.50 on 2019-04-23 | ✓ |
| 2019 | 7.00 | 2.00 (XD 4 Sep 2019) + 5.00 (XD 21 Apr 2020) | 2.00 + 5.00 | ✓ |
| 2020 | 2.50 | 2.50 (XD 21 Apr 2021) — no interim (BOT order) | 2.50 | ✓ |
| 2021 | 3.50 | 1.00 (XD 8 Sep 2021) + 2.50 (XD 21 Apr 2022) | 1.00 + 2.50 | ✓ |
| 2022 | 4.50 | 1.50 + 3.00 (XD 21 Apr 2023) | 1.50 + 3.00 | ✓ |
| 2023 | 7.00 | 2.00 + 5.00 (XD 23 Apr 2024) | 2.00 + 5.00 | ✓ |
| 2024 | 8.50 | 2.00 + 6.50 (XD 23 Apr 2025) | 2.00 + 6.50 | ✓ |
| 2025 | 10.00 | 2.00 (XD 10 Sep 2025) + 8.00 (XD 22 Apr 2026, paid 8 May 2026) | 2.00 + 8.00 | ✓ |
| 2026 (open) | 2 (FS "ปีที่ยังไม่ครบ") | 2.00 interim (XD 9 Sep 2026, paid 25 Sep 2026) | 2.00 | ✓ — not a full year, not counted |

Before 2004 (PP window 1981–1997 fetched): FY1996 = 3.00 + 3.00 = 6.00 · FY1997 = 2.00 interim only (XD 9 Sep 1997) · no PP rows returned for FY1998–2004 in this fetch (the old book read it as suspended FY1998–2003; FS A1 starts 2004 = 1.75 from yahoo). Per-share comparison across the 1998–99 recapitalisation is not like-for-like — treat "no dividend for ~6 years" as the fact, not the exact per-share path. Panphol labels every row "เงินปันผล" (no special flag): no special dividends found in 2015–2026 → nothing for `special_dividends`.

### 2.2 Bank table — the numbers that replace "cash" and "debt" for a bank (D4 D10 D11) · each row from the bank's own year-end press release unless marked

| year | net profit (m) | NIM | ECL set aside (m) | credit cost | NPL ratio | coverage | CET1 | Tier 1 | CAR | loans (m) | source |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2021 | 26,507 | 2.10% | 34,134 | 1.32% (ours: ECL ÷ year-end loans) | 3.2% | 225.8% | 15.2% | 16.0% | 19.6% | 2,588,339 | PR21 |
| 2022 | 29,306 | 2.42% | 32,647 | 1.22% (ours) | 3.1% | 260.8% | 14.9% | 15.7% | 19.1% | 2,682,691 | PR22 |
| 2023 | 41,636 | 3.02% | 33,666 | 1.26% (ours, loans ≈2.67 tn) | 2.7% | 314.7% | 15.4% | 16.1% | 19.6% | ≈2,670,000 | PR23 |
| 2024 | 45,211 | 3.06% | 34,838 | 1.29% (bank-reported, UOBKH) | 2.7% | 334.3% | 16.2% | 17.0% | 20.4% | 2,693,301 | PR24 · UOBKH |
| 2025 | 46,007 | 2.75% | 36,147 | 1.52% (DBS, on average loans) · 1.39% (ours) | 3.0% | 324.1% | 17.2% | 17.2% | 21.8% | 2,608,286 (−3.2%) | PR25 · DBS |
| 1H26 | 20,492 (−16.2%) | 2.46% | 17,435 | 1.48% (DBS) | 3.3% (105,261 m, TR) | 306.3% | 16.9% | 16.9% | 21.4% | 2,678,467 (+2.7% YTD) | IQ · TR · DBS |
| 3Q26 (preview) | 9,800 (BLS est.) | 2.4% | — | — | 3.5% (est.) | 303% (est.) | — | — | — | — | BLS 16 Oct 2026 — not actual |

Read: credit cost has run 1.2–1.5% of loans every year since 2021 — this is a **normal cost** of BBL's book (D1: provisions are not one-offs for a bank). Coverage was built from 226% to 334% in 2021–24 and is now being drawn down slowly (306%) while the NPL ratio climbs back to 3.3%. CET1 ≈ 17% is roughly double the D-SIB floor (8.0% CET1 incl. buffers — regulatory floor from the old book, not re-verified this round). 2016–2020 rows of the old book (NPL 3.2–3.9%, coverage 160–220%, CET1 2019 17.0%) came from search snippets of annual reports and were **not re-verified** (IR site unreachable) — they are not entered in `manual_facts`.

### 2.3 Where FY2025 profit came from — basis for normal EPS (Y annual lines; bank's own FVTPL/investment table not opened)

| line (m baht) | 2022 | 2023 | 2024 | 2025 | note |
|---|---:|---:|---:|---:|---|
| net interest income (Y) | 107,574 | 141,237 | 144,054 | 134,331 | −9,723 in 2025 (press release: "NII declined", NIM 2.75% vs 3.06%) |
| total revenue − NII = non-interest income (Y) | 37,930 | 38,495 | 43,941 | 56,650 | **+12,709 in 2025** · UOBKH 9M25 alone: FVPL gains 9.63 bn + investment gains 10.0 bn; FVPL = unrealised equity mark-to-market (UOBKH channel check) |
| ECL (PR) | 32,647 | 33,666 | 34,838 | 36,147 | normal cost |
| pre-tax (Y) | 37,229 | 52,046 | 56,567 | 55,988 | |
| net profit (Y = FS) | 29,306 | 41,636 | 45,211 | 46,007 | +1.8% |
| EPS (FS A5) | 15.36 | 21.82 | 23.69 | 24.09 | |

Normal EPS FY2025 (our number): strip the excess of 2025 non-interest income over 2024 (12,709 m pre-tax × (1 − 17.2% effective tax) = 10,525 m = 5.51/share) → **24.10 − 5.51 = 18.6**. Harsher variant (excess over the 2022–24 average 40,122 m): 16.9. Cross-checks: 1H26 EPS 10.74 annualised ≈ 21.5 with NIM already down to 2.46%; BLS FY26 −15% ⇒ ≈ 39.1 bn ⇒ EPS ≈ 20.5. So "what BBL earns without the 2025 market gains" sits in the 17–21 range; 18.6 is the value proposed for `normal_eps` (section "ค่าที่ต้องจดลง config"). Nothing was removed for provisions (normal cost) or for Permata (recurring).

### 2.4 Big-bank peers — snapshot Y 2026-10-19 (close) + TR 1H26

| | BBL | KBANK | SCB (SCBX) | KTB | TTB |
|---|---:|---:|---:|---:|---:|
| price | 185.00 | 238.00 | 148.00 | 43.75 | 2.92 |
| PBV (Y) | **0.61** | 0.97 | 1.03 | 1.35 | 1.10 |
| PE trailing (Y) | **8.4** | 11.0 | 11.5 | 12.3 | 12.2 |
| dividend yield (Y, trailing 12 m) | 5.38% | 5.11% | 7.70% | 4.93% | 5.51% |
| ROE (Y TTM) | **7.3%** | 8.8% | 9.1% | 11.5% | 9.0% |
| payout (Y) | **45%** | 56% | 87% | 58% | 56% |
| profit 1H26 (TR) | 20,492 (−16.2%) | 27,915 (+6.2%) | 21,312 (−15.7%) | 24,562 (+7.6%) | — |
| NIM 1H26 (TR) | 2.46% | 2.91% | 3.05% | — | 3.02% |
| NPL 1H26 (TR) | 3.30% (105,261 m) | — | 3.17% (91,934 m) | 2.92% (93,706 m) | — |

Read: cheapest on book and earnings, lowest ROE, lowest payout, largest NPL stock. The discount is explained, not overlooked (D13, D14).

### 2.5 Crisis years — paid? how deep? how long to recover (PP · FS A2 · BOT20 · BOT21)

| crisis | DPS before → during | cut | paid? | back to prior level | cause |
|---|---|---:|---|---|---|
| 1997–98 | 6.00 (FY1996) → 2.00 (FY1997 interim only) → none (≈FY1998–2003, PP gap) | −67% then −100% | suspended ~6 years | 6.00 again only in FY2011 (FS A1) = ~15 years | systemic NPL + recapitalisation (old book; not re-verified) |
| 2008–09 | 3.00 → 3.00 → 4.00 | 0% | normal | no cut | Thai NPL did not spike (FS A2) |
| 2020 COVID | 7.00 → 2.50 (final only) | **−64%** | final only | 7.00 in FY2023 = 3 years; new high FY2024 | BOT letter 19 Jun 2020: suspend 2020 interim dividend + buybacks, 1–3-year capital plan (BOT20) · FY2020 dividend capped at ≤2019 payout rate and ≤50% of 2020 profit; FY2021 ≤50% of profit (BOT21) · EPS −52% (FS A5) |

Both deep cuts had a regulator's hand. BBL's low payout (28% in 2020, FS A12) is what let it keep paying something and recover in 3 years.

---

## 3. คำตอบ D1–D18 ทีละข้อ

| # | answer | evidence (FS section / source + date) | type | confidence |
|---|---|---|---|---|
| D1 | **Yield 5.4% ≥5% — passes C1 on the headline.** DPS FY2025 10.00 ÷ 186.00 (close 2026-10-15) = 5.4%; 3-yr average yield 4.6% (below the 5% line, flag AVG_YIELD_3Y; 3-year window = ours). Paid from normal profit? Partly: FY2025 EPS 24.09 is the A5 jump year (+1.7% on 2024 while NII fell 9.7 bn) — non-interest income rose 12.7 bn, 9M25 alone had 9.6 bn unrealised FVPL equity gains + 10.0 bn realised bond gains (UOBKH). **Normal EPS FY2025 = 18.6** (removed: after-tax excess of non-interest income over 2024, 5.51/share; kept: provisions 36,147 m as normal bank cost, Permata as recurring). Payout on normal EPS = 54%, still < 100%. No loss year, no LOSS flag (FS). | FS A10 A5 A12 · Y annual 2022–25 · UOBKH 22 Oct 2025 · PR25 | number + person | medium (bank's own gain table not opened) |
| D2 | **Year-5 (FY2030) DPS: 10.00 / 11.31 / 12.46 baht at bad 0% / mid 2.5% / good 4.5% per year** → 5.4% / 6.1% / 6.7% of 186.00; on cost 172.10: 5.8% / 6.6% / 7.2%. Rates are earnings-based (A3 EPS CAGR 10 y 3.0%, 15 y 4.2% on reported EPS — base years 2015/2010 normal; on normal EPS 18.6 the same windows give 0.4% / 2.4%; 5-y 21.8% rejected, base 2020 = BOT-cut year). What supports it: NIM floor after the rate-cut cycle (TK), corporate + international loans growing (IQ), Permata +4.5% (PMT), payout room 42→50% without touching capital. Obstacles: NIM 2.46% and falling (IQ), system loans +2.0% only (BOTQ Q2/26), SME/consumer contracting, FY26 profit −11 to −15% (DBS/BLS) — the mid case needs payout to hold ≥50% of normal EPS. C2 flag on FS today: not tripped (uses config mid 4.0%); on proposed mid 2.5% still ≥5%. | FS A3 A4 · section 4 · IQ · TK · DBS · BLS · PMT | number + person | medium |
| D3 | Not applicable as C3 exception (yield already ≥5%). For the record: DPS up 5 straight years (FS A1) but 2021–23 is recovery from the BOT cut and 2024–25 growth came with payout rising 32→42% (FS A12) — payout-driven, not counted as growth. | FS A1 A12 | number | high |
| D4 | **Can the 10.00 hold if business falls?** On reported EPS 24.09 profit can fall 58.5% before payout hits 100% (FS A5, our number); on normal EPS 18.6 it can fall 46%. Worst EPS year 2020 −52% (FS A5) and DPS still 2.50 — cut by BOT order, not by inability (A2: one cut ≥10% in 22 years, recovered in 3). Capital: CET1 16.9%, CAR 21.4%, coverage 306% at 1H26 (table 2.2) vs 15.2% / 19.6% / 226% at end-2021. The binding constraint is a regulator order (BOT20 2020: suspend interim; BOT21: payout caps for FY2020–21), not earnings. | FS A2 A5 A12 · table 2.2 · BOT20 BOT21 · `manual_facts/BBL.json` | number + person | high |
| D5 | Revenue up 11/15 years, streak to latest year = 0 (2025 −0.6%, bank revenue follows the rate cycle — FS A5 note) · EPS up 5 years (base 2020 abnormal) · DPS up 5 years. Stumbles: 2016 (EPS −7%), 2020 (−52%, COVID + BOT), 2026 in progress (1H −16.2%, NIM −35 bp guidance, DBS). Each was cyclical so far; 2026 is the test of whether low rates (1.00% since Feb 2026, MPC) make it longer. DPS 2012–2018 flat at 6.50 for seven years (FS A1) — C7 "up every year" is not BBL's history. | FS A1 A5 · IQ · DBS · MPC | number + person | high |
| D6 | Established 1944 (WK; Dec 1944), listed on SET 1975 (WK) — 82 years old, 51 years listed · paid every year in the FS window 2004–2025 (22 years) but ~6 years suspended after 1997 (2.1) · market cap 353,136 m (Y 2026-10-19) · total assets 4.68 tn (Y 2Q26). Passes C5 "old and large". Recorded in `manual_facts`. | WK · FS A1 · Y | number | high |
| D7 | Policy (DP, not verbatim): pay dividends when results are profitable, considering long-term shareholder return and capital adequacy; remainder may go to reserves — **no % stated**. Actual payout 35–45% of reported EPS for 16 years, 28–32% in 2020–23 (FS A12); interim fixed at 2.00 since 2011 except 2020–22. AGM 10 Apr 2026 approved FY2025 10.00 (DP). President Chartsiri Sophonpanich (WK; search 2026). Holders 23 Apr 2569: Thai NVDR 23.38%, City Realty 4.70%; Oct 2025: Social Security Office 4.30% (SH, UOBKH). SEC: a private individual's Form 246-2 filings claiming 5.0122% of BBL are under SEC investigation as not backed by real transactions (bangkokbiznews 19 Oct 2026) — a false filing, not a BBL holder issue. No minority-unfriendly deal found this round (searched holders + SEC, DC-4). Reading: conservative, balance-sheet-first management; shareholders are paid steadily but never generously. | DP · FS A12 · SH · SEC · WK | person | medium |
| D8 | **a. Industry declining?** Not declining, growing slowly: system loans contracted 6 straight quarters (Q3/24 −2.0% … Q4/25 −1.1%) and turned +2.0% YoY in Q2/26 on large corporates; SME loans down 14+ quarters; system NPL 2.84% end-2025 → 2.82% Q2/26 (BOTQ) · policy rate 1.00% since Feb 2026, held 29 Apr, 24 Jun, 26 Aug 2026 (MPC) · GDP 2569 1.5%, 2570 2.0% (MPC Apr 2026) · household debt 85.9% of GDP, falling because credit is tighter, not because households are richer (HH). BBL revenue (A5) echoes this: 2025 −0.6%, 1H26 NII −12.4% (IQ). **b. What can disrupt:** (1) long low rates → NIM stuck ≤2.5% (happening) · (2) virtual banks — 3 licences approved 19 Jun 2025, first launch "expected" Jun 2026, not verified live (VB); they target retail/SME where BBL is small · (3) corporate clients moving to bond market (slow, ongoing) · (4) another BOT dividend order (happened 2020). | BOTQ · MPC · HH · VB · IQ · FS A5 | person | medium |
| D9 | Not number one in every line. Strength no Thai peer matches: corporate lending ~49% of loans and international ~23% (old book from IR snippet — not re-verified; 1H26 growth came from "corporate and foreign-entity loans", IQ) + Permata 89.12% (WK). Loses on retail/digital (KBANK, SCB) and on ROE (lowest, table 2.4). Market-share number: not found this round. | IQ · table 2.4 · WK | person | medium |
| D10 | Bank substitute for "cash": CET1 16.9% / CAR 21.4% (IQ 1H26), coverage 306%, credit cost 1.2–1.5%/yr for five years (table 2.2 → `manual_facts`). Ample by any Thai-bank standard; it is the reason the 2020 cut was an order, not a necessity. | table 2.2 · IQ · DBS | number + person | high |
| D11 | Bank substitute for "debt": NPL 3.3% vs KTB 2.92%, SCB 3.17% (TR) — highest of the big four, stock +11.2% YTD to 105,261 m, largest in the system (TR) — but coverage highest. FS prints no A6 for banks; see section 10 #1 on the ⛔ cache rows 2019–2021. | TR · FS A6 note | number | high |
| D12 | Table 2.5: 2008/2011 no cut; 2020 −64% by order, 3 years to recover; 1997 suspended ~6 years, ~15 years to the old level. | PP · FS A2 · BOT20 | number | high |
| D13 | Hidden value exists on paper, market prices it at 0.61× book: Permata 89.12% (WK) — BNLI market cap IDR 82.7–87.6 tn (Jul 2026, PMT search) × 89.12% ≈ IDR 74–78 tn; guess: at ~0.002 THB/IDR (rate not verified) ≈ 150 bn THB ≈ 40% of BBL's market cap · excess capital ≈ 9 points of CET1 over the floor · 1H26 Permata profit IDR 1.72 tn × 89.12% ≈ 1.53 tn ≈ 15% of BBL profit (guess on rate). Not unlocked in 5 years: no buyback, payout flat, ROE 7–8% < 11% cost of equity (UOBKH GGM). | WK · PMT · UOBKH | number + person | low–medium |
| D14 | Cheap vs own history (FS A10 label: yield at the 80th percentile of 10-year year-end yields 2.1–5.9%) · PE 7.7 on FY2025 EPS, 8.4 trailing (Y) — **10.0 on normal EPS 18.6**, i.e. exactly at the P3 "PE < 10" line (weak evidence, summarised S2) · PBV 0.61 within 0.47–0.96 · 52-week 152.5–204.0 (Y) · broker TPs 168 (DBS Apr 2026, 0.56× FY26 book, HOLD) and 210 (BLS Oct 2026). "Another 20–30% down" (ours) = 148.8–130.2 → yield 6.7–7.7% on 10.00. Price "appropriate" in Niwes' sense = person's call. | FS A10 · Y · DBS · BLS | number + person | high |
| D15 | Belief table — see section 5 (≥2 beliefs, counter-evidence with source + date, falsifier tied to a T flag). | section 5 | person | — |
| D16 | Flag table — section 6; every flag names the belief it watches, every belief has a flag. | section 6 | number + person | — |
| D17 | Art's call. Facts: Niwes leg = AMATA (industrial estate) + BBL + TCAP (finance) + TISCO off-plan (finance) — finance is 3 of 4 names; BBL 22.5% weight; Art does not apply F1 "5 stocks 5 industries" (niwes-principles F1, 2026-10-19). Section 8 gives the arithmetic of a bank-wide cut. | roadmap/agreed-portfolio-framework.md · section 8 | person | — |
| D18 | n/a — AMATA only. | — | — | — |

---

## 4. ปันผลเทียบต้นทุน (ปันผลปีนั้น ÷ ต้นทุน) — ก้อนที่ถืออยู่ + ถ้าซื้อทุกเดือน (DCA) · facts only, target 7–12% parked (Art 2026-10-18)

Computed with the fact sheet's own functions (`scripts/fact_sheet.py` `yoc_table` / `dca_yoc`, run from `files/` on 2026-10-19) so the head can reproduce them by writing the scenarios into `config.json` and re-running `fact_sheet.py BBL --refresh --cost BBL=172.10`. Base DPS = FY2025 10.00 · price 186.00 (close 2026-10-15) · cost 172.10.

### 4.1 Three earnings-based growth scenarios (ours — not Niwes' words, not a forecast)

| scenario | DPS growth/yr | why this number | what must be true |
|---|---:|---|---|
| bad | 0.0% | normal EPS 18.6 (2025) vs 17.90 (2015) = +0.4%/yr over 10 years (FS A5 + 2.3); FY26 profit −11 to −15% (DBS/BLS); NIM 2.46% (IQ) | DPS held at 10.00 by raising payout toward 55–60% of normal EPS; no BOT order |
| mid | 2.5% | 15-year normal-EPS CAGR 2.4% (18.6 vs 12.96 in 2010); reported-EPS 10-y 3.0% (FS A3, base 2015 normal); system loans +2% (BOTQ) + NIM floor (TK) + Permata +4–5% (PMT) | payout ≥50% of normal EPS and earnings back to growth from 2027 (BLS FY27 +4%) |
| good | 4.5% | reported-EPS 15-y CAGR 4.2% (FS A3) + 6-y 2019→2025 4.3%; payout room to 55% | rate cycle turns up, NPL stock stops growing, Permata keeps double-digit corporate loan growth |

Current config (2026-10-09 book, bad 1.5 / mid 4.0 / good 6.0) was dividend-growth-based and is superseded by the table above once Art decides.

### 4.2 ก. Lump held: 3,400 shares at 172.10 — DPS in year N ÷ cost (other cost levels kept for comparison, as in FS A4)

| scenario | growth | year | DPS | @172.10 | @186.00 | @148.80 | @111.60 |
|---|---:|---:|---:|---:|---:|---:|---:|
| bad | 0.0% | 5 | 10.00 | 5.8% | 5.4% | 6.7% | 9.0% |
| bad | 0.0% | 10 | 10.00 | 5.8% | 5.4% | 6.7% | 9.0% |
| bad | 0.0% | 15 | 10.00 | 5.8% | 5.4% | 6.7% | 9.0% |
| mid | 2.5% | 5 | 11.31 | 6.6% | 6.1% | 7.6% | 10.1% |
| mid | 2.5% | 10 | 12.80 | 7.4% | 6.9% | 8.6% | 11.5% |
| mid | 2.5% | 15 | 14.48 | 8.4% | 7.8% | 9.7% | 13.0% |
| good | 4.5% | 5 | 12.46 | 7.2% | 6.7% | 8.4% | 11.2% |
| good | 4.5% | 10 | 15.53 | 9.0% | 8.3% | 10.4% | 13.9% |
| good | 4.5% | 15 | 19.35 | 11.2% | 10.4% | 13.0% | 17.3% |

Growth needed from 10.00 (FS A4 "required growth", facts): to 7% of 172.10 in year 5 = 3.8%/yr, in year 10 = 1.9%/yr · to 12% in year 10 = 7.5%/yr.

### 4.3 ข. New money bought monthly for 10 years then held — dividend in year N ÷ all money invested (FS A4 DCA rule: price grows with dividend / price flat)

| scenario | growth | year 5 grows / flat | year 10 grows / flat | year 15 grows / flat |
|---|---:|---|---|---|
| bad | 0.0% | 5.4% / 5.4% | 5.4% / 5.4% | 5.4% / 5.4% |
| mid | 2.5% | 5.7% / 6.1% | 6.1% / 6.9% | 6.9% / 7.8% |
| good | 4.5% | 6.0% / 6.7% | 6.8% / 8.3% | 8.4% / 10.4% |

Read (fact): new money bought at today's 5.4% yield stays within 5–7% for a decade in every scenario but "good + flat price". The lump at 172.10 does 0.4–0.6 points better than new money because its cost is 7.5% below today's price.

### 4.4 ค. Actual past — not re-run this round. The 2026-10-09 book's backtest script (`files/bbl_dca_backtest.py`, desk krv3, archived) is not in this job's file list; its result ("DCA 15 years ≈ 6.3%") is OLD and not re-verified.

### 4.5 Numbers still unknown that would flip the answer
- FY2025 FVTPL vs investment-gain split from the bank's own table (IR deck unreachable) — decides whether normal EPS is 18.6 or nearer 20.
- Q3/2026 actual (due 2026-10-20, Y) — first read on whether NIM has bottomed (TK) and whether the NPL stock keeps growing.
- FY2026 final dividend (board ~late Feb 2027): any cut below 8.00 final makes FY2026 < 10.00 → T1 count starts.

---

## 5. อะไรทำให้พัง — เรียงตาม โอกาสเกิด × ความเสียหายต่อปันผล

### 5.1 Belief table (D15 — C12 "avoid being fooled by the story") · ≥2 beliefs · "Niwes holds banks" is not among the reasons to hold

| # | what we want to believe (1 sentence) | strongest counter-evidence + source + date | what proves it wrong (→ flag in section 6) |
|---|---|---|---|
| B1 | "BBL is the safest Thai bank — CET1 17%, coverage 300%+ — so the dividend can only hold or rise." | Capital did not protect the dividend in 2020: CET1 ≈17% (old book, 2019) and the dividend still fell 64% because BOT ordered it (BOT20 19 Jun 2020; BOT21 11 Nov 2021) · NPL stock 105,261 m, +11.2% in 6 months, largest in the system, ratio 3.3% highest of big four (TR 22 Jul 2026) · 1H26 profit −16.2% (IQ 22 Jul 2026) | T3: normal EPS down 2 fiscal years **and** NIM < 2.3% four straight quarters · T5: NPL > 4.5% or coverage < 200% · T4-bank: CET1 < 14% or a new BOT dividend order |
| B2 | "PBV 0.6 is half price; the market will re-rate it and release the excess capital." | PBV has sat at 0.47–0.96 for ten year-ends (FS A10) with ROE 7–8% (FS A5) below the 11% cost of equity brokers use (UOBKH 22 Oct 2025, GGM) · DBS values it at 0.56× FY26 book, TP 168 (29 Apr 2026) · payout 35–45% for 16 years, policy states no % (FS A12, DP) — no buyback, no special dividend since at least 2015 (PP) | T2: year-10 yield on cost under the mid scenario < 7% (needs DPS < 12.05 in FY2035 on 172.10) · payout still ≤45% of reported EPS at FY2027 = "good" scenario dead |
| B3 | "Dividend has grown 32%/yr for 5 years — this is a growth-dividend stock." | Base year 2020 is the BOT-cut year (FS A1: 2.50); DPS was flat at 6.50 for 2012–2018 (FS A1); EPS CAGR 10 y 3.0%, 15 y 4.2% (FS A3); on normal EPS 10-y growth is 0.4% (2.3) · consensus/broker FY26 profit −11 to −15% (DBS Apr 2026, BLS Oct 2026) | T1: DPS down 2 fiscal years in a row · T2 as above |
| B4 | "A 5.4% bank yield today is safe for the next 10 years because BBL has paid for 22 years." | FS A1 window starts 2004 and hides ~6 years with no dividend after 1997 (PP window, 2.1); the 2020 cut shows a dividend can drop 64% in one year with profit down 52% (FS A2 A5) | T1 + T4-bank (capital raise announced or CET1 < 11%) |

### 5.2 Non-belief risks — ranked by chance × damage to DPS (facts; judgement is ours)

| # | cause | chance (10 y) | damage to DPS | temporary / permanent | evidence |
|---|---|---|---|---|---|
| 1 | Policy rate ≤1.0% for years → NIM 2.2–2.5%, profit flat/down | high — happening: 1.00% since Feb 2026, held Aug 2026 (MPC); GDP 1.5–2.0% | DPS flat; payout rises instead of DPS | cyclical but the cycle may be 5+ years | MPC · IQ · TK |
| 2 | NPL keeps rising → provisions above 1.5% of loans | medium-high — NPL 3.3% and +11% YTD (TR); BLS expects 3.5% in Q3 | profit −20–40% in the year; DPS −10–30% if the board protects capital | 1–3 years (coverage 306% absorbs first) | TR · BLS · table 2.2 |
| 3 | BOT orders dividend limits again (system shock) | medium — done in 2020–21, power not withdrawn | −50 to −70% for a year, 2–3 years back | temporary, but trips T1 without business failure | BOT20 BOT21 |
| 4 | 1997-type systemic crisis with recapitalisation | low — CET1 17%, foreign debt low (not re-verified) | −100% for years + dilution | permanent per old share | PP · table 2.5 |
| 5 | Permata / Indonesia shock (IDR, rules) | medium | ≤15% of profit (PMT share) → DPS −5–10% | temporary | PMT |
| 6 | Virtual banks + digital rivals lift deposit costs | low first 5 years, rising after | NIM −0.1 to −0.3 pt → profit −5–10% | permanent, slow | VB |
| 7 | Management keeps payout at 40–45% despite excess capital | high — 16-year pattern | DPS not cut, but "good" scenario never happens | cultural | FS A12 · DP |
| 8 | Political/tax measures on banks (debt-relief programmes, windfall tax) | medium | −5–10% in the year | temporary | HH (debt measures) |

Summary: what makes the dividend disappear permanently (4, 6) is low-probability and slow; what makes it stall or dip (1, 2, 3, 7) is high-probability and partly under way. BBL's main risk to the plan is "no growth", not failure.

---

## 6. ธง "ผิดทาง" เฉพาะ BBL (T1–T6 ปรับให้ธนาคาร — เลขเกณฑ์ กูตั้ง Art เคาะ)

| flag | bank measure | value today (source) | opens a review | points to "permanent" | watches belief (D16) | where to read |
|---|---|---|---|---|---|---|
| T1 | DPS of fiscal year below prior year | FY2025 10.00 (+18%) — not tripped (FS) · FY2026 interim held 2.00 (PP); final unknown | down 2 fiscal years (FY2026 + FY2027) | down 3 years, or DPS < 7.00 (2019 level) without a BOT order | B3, B4 | set.or.th / PP, Feb–Mar (final) + Aug–Sep (interim) |
| T2 | yield on cost 172.10 in year 10, mid scenario | config mid 4.0% → 8.6% (FS, not tripped) · proposed mid 2.5% → 7.4%; bad 0% → 5.8% | mid-case projection < 7% ⇔ latest DPS × (1.025)^10 < 12.05 ⇔ latest DPS < 9.41 | — | B2, B3 | recompute each year after the final dividend (fact sheet A4) |
| T3 | why the dividend fell: normal EPS / payout / BOT | normal EPS FY2025 18.6 (ours); 1H26 EPS 10.74, −16% (IQ); NIM 2.46% | normal EPS down 2 fiscal years **and** NIM < 2.3% four straight quarters | profit down 3 years with NPL not the cause (= revenue structure broken) | B1 | quarterly results (press release mirrors; IR deck when reachable) |
| T4 (bank) | capital instead of cash flow: CET1 trend + payout | CET1 16.9%, CAR 21.4% (IQ 1H26); payout 42% reported / 54% normal | CET1 < 14% or payout > 70% of normal EPS two years, or a BOT dividend order | CET1 < 11% or capital raise announced | B1, B4 | quarterly results · BOT circulars |
| T5 | industry: NPL system + policy rate + virtual banks | BBL NPL 3.3%, system 2.82% (BOTQ Q2/26) · rate 1.00% · virtual banks not verified live | BBL NPL > 4.5% or coverage < 200% · rate ≤ 0.5% for 2 years | NPL > 6% with coverage < 150% (1997 picture) · CASA shrinking 3 years | B1 | TR half-year · BOTQ · MPC |
| T6 (bank) | NPL vs peers + NPL stock growth | 3.3% vs KTB 2.92 / SCB 3.17 (TR); stock +11.2% YTD | gap > 1.0 pt above peers 3 years running | gap > 2 pt and coverage below peers | B1 | TR half-year |

FS flags on 2026-10-19: T1 ✅ not tripped · T2 ✅ not tripped (config mid 4.0%) · C2 ✅ not tripped · PAYOUT ✅ 42% · LOSS ✅ none · T4/T6 not computed for banks by the sheet (replaced here). Next data: Q3/2026 on 2026-10-20 (Y) · FY2026 results ~Jan 2027 · final dividend board ~late Feb 2027, XD ~Apr 2027.

---

## 7. ราคาตอนนี้ — เทียบประวัติตัวเอง (ราคาปิดจริง) + เทียบคู่ · ข้อเท็จจริงให้คน DCA คิด ไม่ใช่คำสั่ง

- Close 186.00 on 2026-10-15 (FS) · 185.00 on 2026-10-19 (Y) · 52-week 152.5–204.0 (Y) → 10% below the high, 21% above the low.
- Own history (FS A10, year-end closes, not dividend-adjusted): yield 5.4% at the 80th percentile of 2016–2025 year-end yields (2.1–5.9%) → label "cheap vs itself" (rule = ours) · PE 7.7 on FY2025 EPS, 10.0 on normal EPS 18.6 · PBV 0.61 (range 0.47–0.96).
- Peers (2.4): lowest PBV and PE, lowest ROE and payout — discount matches fundamentals.
- Brokers: DBS TP 168 HOLD (29 Apr 2026, 0.56× FY26 book) · BLS TP 210 (16 Oct 2026). Spread 168–210 brackets today's price.
- "Another 20–30% down" (ours, D14): 148.8 / 130.2 → yield on 10.00 = 6.7% / 7.7%. Cash-for-panic (P2/F4) is a portfolio question → `roadmap/queue-rebalance-formula-check.md`.

---

## 8. น้ำหนักในพอร์ต — ถ้ากลุ่มธนาคารโดนพร้อมกันแบบปี 2563 ปันผลรวมหายเท่าไร (Art ตั้งใจ R5 — ไม่เสนอแก้)

- BBL = 22.5% of the plan (job). A 2020-size cut (−64%) on BBL alone removes ≈ 22.5% × 64% ≈ **14% of the portfolio's dividend** for that year, if every holding yields about the same (arithmetic, ours).
- A 2020-type order hits every Thai bank/finance name at once: in 2020 BOT's letter covered all commercial banks (BOT20); TCAP and TISCO are finance too (D17). The 2020 experience: BBL −64%, recovered in 3 years (FS A2).
- No proposal to change the weight — Art's intent (R5). Facts only.

---

## 9. สิ่งที่ algo ควรเตรียมเพิ่มสำหรับหุ้นธนาคาร (รอบนี้ต้องหามือ)

- The sheet now has a `manual_facts` slot; this job fills `data/manual_facts/BBL.json` (founding/listing year, policy, bank table 2021–1H26). The sheet prints the keys as-is (`fact_sheet.py` `_manual`) — no computation on them.
- Still manual every round: FVTPL / investment-gain split (needed for normal EPS), NPL stock vs peers (TR half-year), BOT circulars, Q3 timing. Source that works without the IR site: thaipr / thaitabloid mirrors of the bank's own press release (same wording, same numbers) — add to `thai-data-sources` if the head agrees.
- Not done: historical backtest (4.4) and 2016–2020 bank ratios (IR deck unreachable).

## 10. จุดที่ของเดิมใน `research/` กับใบข้อเท็จจริง ผิด / เก่า

| # | file:line / section | says | actual (source) | type |
|---|---|---|---|---|
| 1 | old fact sheet (desk krv3) A6 rows 2019–2021, cited in OLD section 10 #1 | total liabilities 281,291 / 330,552 / 425,524 m; D/E 0.66 / 0.74 / 0.86 | **cache data error** — real liabilities are ≈3.9–4.1 tn (Y: 2022 3,914,610 m; 2025 4,030,659 m; 2Q26 4,100,139 m); the new FS prints no A6 for banks. Those three rows are not used anywhere in this book. | data error |
| 2 | OLD 4.1 / `config.json` growth_scenarios BBL (bad 1.5 / mid 4.0 / good 6.0, as_of 2026-10-09) | dividend-growth scenarios ("DPS 0/3/5% → 3/5/7%") | superseded by earnings-based 0 / 2.5 / 4.5% (section 4.1) pending Art's decision — the FS A4 table of 2026-10-19 still shows the old set | superseded |
| 3 | OLD D1 "paid from normal profit: profit 46,007 +1.8%, payout 42%, no asset sales" | treats FY2025 as normal | FY2025 carried ≈12.7 bn extra non-interest income (Y; UOBKH 9M25 FVPL 9.6 bn + investment 10.0 bn) → normal EPS 18.6, payout 54% (2.3) | wrong (incomplete) |
| 4 | OLD 2.2 rows 2016–2020 (NIM/NPL/coverage/CET1 via "IRS" search snippets) | — | not re-verified this round (IR site unreachable); 2021–2025 rows now come from the bank's own year-end press releases (table 2.2) and differ slightly where OLD used broker numbers (e.g. 2025 coverage 295.0% UOBKH forecast vs 324.1% actual) | old / unverified |
| 5 | OLD 2.4 peer table (Y snapshot 9 Oct 2026) | prices 182.50 / 227 / 144.5 / 42 / 2.88 | updated 2026-10-19 (2.4); yields in OLD used PP FY2025 DPS, here Y trailing-12-month — not like-for-like | old |
| 6 | OLD D3 / 6 "FY2026 DPS consensus 9.81 (MS)" | — | marketscreener paywalled this round — not re-verified; not used | unverified |
| 7 | OLD 2.3 "Permata ≈15% of profit (MB)" and "bought for ~US$2.7 bn (no source)" | — | 1H26: IDR 1.72 tn × 89.12% ≈ 15% of BBL profit (PMT, rate guessed) · purchase Rp 33.66 tn = US$2.3 bn (WK) | corrected |
| 8 | OLD D7 holders "10 Sep 2569 Thai NVDR 21.86%" (PP) | — | PP page in this fetch shows the same list but the year is not legible; 23 Apr 2569 list: Thai NVDR 23.38%, City Realty 4.70% (SH) · "City Realty = Sophonpanich family" is OLD's statement, not re-verified | ambiguous |
| 9 | OLD 6 "Q3/2569 ~20–22 Oct" | guess | Y earnings calendar 2026-10-20 — consistent | confirmed |
| 10 | FS A4 header "อัตราโตจาก deep dive 2026-10-09" | points at the OLD book | after this book is accepted the pointer must change to `research/bbl-deep-dive-2026-10-19.md` section 4.1 (config `source`) | to update |

---

## ค่าที่ต้องจดลง config

The head writes this into `config.json` (this job does not touch it). Form follows `docs/deep-dive.md` step 3 (value + `_source` + `_as_of`). After writing, re-run `fact_sheet.py BBL --refresh --cost BBL=172.10` so A3/A4/A12 pick the values up.

```json
{
  "normal_eps": {
    "BBL": {
      "2025": 18.6,
      "2024": 23.69,
      "_source": "research/bbl-deep-dive-2026-10-19.md section 2.3 — FY2025: reported EPS 24.10 minus after-tax excess of non-interest income over 2024 (12,709 m pre-tax x (1-0.172) = 5.51/share; yfinance annual lines, 9M25 FVPL 9.63 bn + investment gains 10.0 bn per UOB Kay Hian 22 Oct 2025); provisions (ECL 36,147 m) kept as normal bank cost; harsher variant 16.9 (excess over 2022-24 average). FY2024: reported EPS kept, no exceptional item identified",
      "_as_of": "2026-10-19"
    }
  },
  "holdings": {
    "growth_scenarios": {
      "BBL": {
        "bad": 0.0,
        "mid": 0.025,
        "good": 0.045,
        "source": "research/bbl-deep-dive-2026-10-19.md section 4.1 — earnings-based: normal-EPS CAGR 10 y 0.4% / 15 y 2.4% (2015 and 2010 bases, both normal years); reported-EPS CAGR 10 y 3.0% / 15 y 4.2% (FS A3); 5-y 21.8% rejected (base 2020 = BOT-cut year). bad = dividend held flat while payout rises; mid = long-run normal EPS growth; good = reported-EPS 15-y rate with payout room to 55%",
        "as_of": "2026-10-19"
      }
    }
  }
}
```

`special_dividends`: none for BBL (every XD row 2015–2026 on panphol is a regular dividend — 2.1).

---

## acceptance (ไล่ทีละข้อ)

- every D1–D18 answered with fact-sheet section or external source + date → section 3, each row has an evidence column with FS section codes and source codes dated in the source table.
- D1 has normal EPS FY2025 with what was removed and why → section 3 D1 + 2.3 (removed: after-tax excess non-interest income over 2024 = 5.51/share; kept: provisions, Permata).
- D2 has a numeric year-5 DPS from an earnings-based rate plus obstacles → section 3 D2 + 4.1/4.2 (10.00 / 11.31 / 12.46 at 0 / 2.5 / 4.5%).
- D4 uses A2 + the 2020 BOT dividend restriction + the bank table → section 3 D4 (FS A2, BOT20/BOT21, table 2.2 → `manual_facts`).
- D15 has ≥2 beliefs each with sourced counter-evidence and a falsifier tied to a T-flag → section 5.1 (B1–B4).
- D16 maps every flag to a D15 belief → section 6 column "watches belief".
- D18 = "n/a — AMATA only" → section 3 D18.
- the A6 ⛔ years 2019–2021 are a cache data error — stated and not used → section 10 #1, section 3 D11.
- files written + where the config JSON block is + whether `data/manual_facts/` is git-ignored → job result (`## สถานะ/ผล`).
