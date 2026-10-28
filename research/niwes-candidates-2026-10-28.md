# Niwes-leg candidates KBANK · KTC · HMPRO vs AMATA · BBL · TCAP (2026-10-28)

Art's order (via Karl/Hermes, 2026-10-28): "ทำเลย deep dive พวกนี้" — the 3 candidates from `research/niwes-keep-or-cut-2026-10-28.md` section 3.
Question: can Art hold and DCA every month forever (10–20 y)? · 7–12% is a direction, not a cut-off · no buy/sell order (R6) · config / `rebalance.py` untouched.

Books (D1–D18 + T1–T6, sources + dates inside): `research/kbank-deep-dive-2026-10-28.md` · `research/ktc-deep-dive-2026-10-28.md` · `research/hmpro-deep-dive-2026-10-28.md` · holdings: `research/<sym>-deep-dive-2026-10-19.md`.
Fair basis: every stock uses **its own deep-dive EPS-based scenarios** (holdings from `config.json` `holdings.growth_scenarios`; candidates from section 4.1 of their book, not yet in config) · prices = close 2026-10-27 · base DPS = last complete FY, regular only (KBANK 12.00 ex 2.00 special) · DCA rule = `scripts/fact_sheet.py` `dca_yoc` (equal money monthly 10 y then hold; "grows" = price rises with DPS / "flat" = price unchanged) — recomputed by the head with that function for all six.

## 1. Answer

| Stock | Read | Why |
|---|---|---|
| KTC | **Strongest candidate — add alongside (new money), decide after 2 checks** | Best mid path of all six (DCA y20 9.2% / 11.1%), strong balance sheet (NPL 1.92%, coverage 413%, TRIS AA). But yield 5.1% rests on a one-year payout jump 46% → 59% (policy ≥40%), and BOT min-payment 10% starts 1 Jan 2027. |
| KBANK | **Not better than BBL at 245** | Regular yield 4.9%, mid growth 2.5% = same as BBL, so every DCA number is below BBL's. Dividend jump came from payout 37% → 58% + specials, not earnings (9M26 ex one-off −0.3%). Would be a third bank. Interesting only at ≤220 / ≤196. |
| HMPRO | **Not now — flat high-yield, watch FY2026** | Highest yield today (5.8%) but EPS flat 6 years, payout 83%, SSS negative 3 years, FCF 2025 < dividend + buyback. Mid y20 6.8–7.1% lowest of the six apart from bad cases; bad case shrinks (−2%/yr). Plus: the only non-financial everyday business. |

> No candidate is a reason to cut AMATA, BBL or TCAP: none of the three holdings shows "wrong track" (F3), and none of the candidates beats them on every axis at once. KTC is the only one that beats a holding (AMATA, TCAP) on the mid DCA path — it fits as an addition funded by new money, not as a replacement.

## 2. Same-basis table (mid = deep-dive mid scenario)

| | AMATA | BBL | TCAP | KBANK | KTC | HMPRO |
|---|---:|---:|---:|---:|---:|---:|
| Price 2026-10-27 | 28.75 | 185.00 | 80.25 | 245.00 | 35.00 | 6.50 |
| Base DPS (last FY, regular) | 1.10 | 10.00 | 3.50 | 12.00 | 1.77 | 0.38 |
| Yield today | 3.8% | 5.4% | 4.4% | 4.9% | 5.1% | 5.8% |
| Normal EPS last FY (book) | in config | 18.6 | 7.32 | 18.9 | 3.02 | 0.46 |
| Payout on normal EPS (base DPS ÷ normal EPS) | — | 54% | 48% | 63% | 59% | 83% |
| Scenarios bad / mid / good | 0 / 5 / 9% | 0 / 2.5 / 4.5% | 1.5 / 4 / 7% | 0 / 2.5 / 5% | 0 / 4 / 6% | −2 / 1 / 5% |
| DCA y5 mid (grows / flat) | 4.3 / 4.9 | 5.8 / 6.1 | 4.8 / 5.3 | 5.2 / 5.5 | 5.6 / 6.2 | 6.0 / 6.1 |
| **DCA y10 mid** | 4.9 / 6.2 | 6.1 / 6.9 | 5.3 / 6.5 | 5.6 / 6.3 | **6.2 / 7.5** | 6.1 / 6.5 |
| **DCA y20 mid** | 8.0 / 10.2 | 7.9 / 8.9 | 7.9 / 9.6 | 7.1 / 8.0 | **9.2 / 11.1** | 6.8 / 7.1 |
| DCA y10 bad (grows / flat) | 3.8 / 3.8 | 5.4 / 5.4 | 4.7 / 5.1 | 4.9 / 4.9 | 5.1 / 5.1 | 5.3 / 4.8 |
| DCA y20 bad (grows / flat) | 3.8 / 3.8 | 5.4 / 5.4 | 5.5 / 5.9 | 4.9 / 4.9 | 5.1 / 5.1 | 4.3 / 3.9 |
| DCA y10 good (grows / flat) | 6.1 / 9.1 | 6.8 / 8.4 | 6.3 / 8.6 | 6.3 / 8.0 | 6.9 / 9.1 | 7.6 / 9.5 |
| Lump at today's price, y10 mid | 6.2% | 6.9% | 6.5% | 6.3% | 7.5% | 6.5% |
| T1–T6 lit (book section 6) | none (watch presale) | none | none | T2 on regular base | none (T5 watch: BOT 2027) | T1/T3/T4 each "one of two" · T5 watch |

Payout on normal EPS: BBL 10.00 ÷ 18.6 · TCAP 3.50 ÷ 7.32 · KBANK 12.00 ÷ 18.9 · KTC 1.77 ÷ 3.02 · HMPRO 0.38 ÷ 0.46 (head's arithmetic from the books' normal EPS). AMATA normal EPS: `config.json` `normal_eps.AMATA`.

## 3. Per candidate — what decides it

**KTC** (book sections 1, 4, 5, 6)
- For: ROE 19%, mid 4% backed by EPS 2018→25 6.1% / 2022→25 3.2%; 9M26 profit +14.3% (from lower ECL + funding cost, revenue +0.4%).
- Against: receivables +0.8%, card industry −3.7% (11M25, BOT) — no volume growth; payout reversion to 45% → DPS 1.36, DCA y10 5.8%; BOT min payment 8% → 10% (2027) / rate-ceiling cut ≈ −5–10% EPS per step, permanent.
- Checks before any money: FY2026 DPS keeps payout ≈59% (Feb–Mar 2027) · 2027 results after the min-payment step.
- Concentration: would make 3 of 4 Niwes names financial-sector (BBL, TCAP, KTC — AMATA the only non-financial); KTC is a KTB subsidiary.

**KBANK** (book sections 1, 4, 7, 8)
- At 245 it is above every year-end close since 2017; regular yield 4.9% misses C1 5% by 0.1 pt; bad case misses C2 by 0.1 pt.
- Risks: NIM 3.66% → 2.89% with provisions and costs already cut; structural credit cost 2.0–2.2% (2022–24) vs BBL 1.2–1.3%; BOT dividend order (2020 repeat).
- Overlap with BBL: same sector, same mid growth, lower yield → adds bank concentration without a better path.

**HMPRO** (book sections 1, 4, 6, 10)
- Yield 5.8% exists because price fell 58% from 2022 while DPS stayed flat; stores +17% but sales per store −12% (2019→25).
- FY2026 decides it: T1 (one cut, FY2025 −12%), T3 (normal EPS down 1 y), T4 (FCF < dividend + buyback, cash 5.6 → 1.7 bn) are each at "one of two".
- Correction to keep-or-cut 2026-10-28: Q2/26 was +14.0% YoY (not −7%); 1H26 −3.5%.

## 4. Cheap levels (for the F5 cash-ammo step, only if a stock enters the plan · ours, not Niwes · from each book's cheap-levels section)

| Stock | Step 1 | Step 2 | Step 3 | Basis |
|---|---|---|---|---|
| KTC | ≤29.50 (6.0%) | ≤27.00 (6.6%) | ≤24.50 (7.2%) | yield on 1.77 · step 3 ≈ 2025–26 trough |
| KBANK | ≤220 (5.5%) | ≤196 (6.1%) | ≤171 (7.0%) | yield on regular 12.00 · −10/−20/−30% |
| HMPRO | ≤5.80 (6.6%) | ≤5.40 (7.0%) | ≤4.75 (8.0%) | yield on 0.38 · step 1 = 10-y low close · no shot while T1 + permanent T3 lit |

## 5. For Art to decide (not decided here)
1. KTC: enter the plan as an addition (new money, weight not proposed — R5/R6), or wait for FY2026 payout + BOT 2027 step first.
2. KBANK / HMPRO: leave out now; keep their cheap levels on file (KBANK ≤196 · HMPRO after FY2026).
3. Config values from the three books ("values for config" section of each): normal_eps, growth_scenarios, special_dividends KBANK 2024 2.50 / 2025 2.00 — enter only if a stock enters the watch/plan.

## Data gaps (from the books)
- KBANK: CET1/Tier 1 after 2023 not found; normal EPS from the yfinance gain-on-securities line (bank's own table not opened).
- KTC: FY2025 tax rate 27.7% vs 20.3% unexplained (if one-off, normal EPS ≈3.3); AEONTS peer line not fetched.
- HMPRO: Q3/2026 not published as of 2026-10-28; full-year SSS by format not found; LH/QH related-party detail not read.
- AMATA / TCAP Q3/2026 not out yet (keep-or-cut 2026-10-28).
