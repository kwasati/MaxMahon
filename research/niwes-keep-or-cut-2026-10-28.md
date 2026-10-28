# Niwes leg — keep or cut? AMATA · BBL · TCAP (2026-10-28)

Art's order (via Karl/Hermes, 2026-10-28): "วิเคราะห์หุ้น 3 ตัวหลักแนวทาง niwes ว่าควรไปต่อจริงๆใช่ไหม? หรือควรคัทแล้วไปซื้อหุ้นอื่น (นั่นหมายถึงต้องไปค้นหาหุ้นอื่นที่ดีกว่าเข้ามา)"

Frame used (Art): DCA every month forever, hold 10–20 y · 7–12% yield-on-cost is a **direction**, not a cut-off · sell only when "wrong track" (F3: DPS down 2 years running → review temporary vs permanent) · system numbers first, judgement after · no buy/sell order (R6).

Sources: fact sheets `fact_sheet.py --refresh` 2026-10-28 (close 2026-10-27) with deep-dive growth scenarios from `config.json` `holdings.growth_scenarios` · deep dives `research/<sym>-deep-dive-2026-10-19.md` · quarterly: SETSMART `financial-data-and-ratio-by-symbol` and yfinance `quarterly_income_stmt` (both stop at Q2/2026 — Q3/2026 of AMATA and TCAP not out yet, due ~mid-Nov) · BBL / ttb Q3/2026 from news of 20 Oct 2026 (links at the end) · full-market scan `data/screener_2026-10-28.json` → `reports/scan_2026-10-28.md` (fresh fetch, 930 scanned, 118 passed).

## 1. Answer

| Stock | Verdict | Why (1–2 lines) |
|---|---|---|
| AMATA (35%) | **Watch** | No wrong-track signal (T1 / T4 / T6 clear, DPS up 2025 and interim 2026). But growth is cyclical and the cycle turned: presale 2025 −59%, 1H26 = 13% of target, FCF 1H26 negative. Yield 3.8% today; DCA mid case only reaches 4.9–6.2% by year 10. Decide after Q3 presale (mid-Nov) and FY2026 DPS (Feb–Mar 2027). |
| BBL (22.5%) | **Keep** (watch FY2026 DPS) | Yield 5.4% today already ≥ 5%, capital far above 2020, no flag lit. Profit is falling (Q3/26 −31% YoY, 9M −21.6%) so FY2026 DPS may drop — one down year = not wrong track under F3; it is a flat-dividend stock, not a grower. |
| TCAP (12.5%) | **Keep** | Regular DPS never cut in 24 FYs, no flag lit, engine ttb still growing (Q3/26 +3.0%, 9M +4.8%). Only issue is price: 80.25 = yield 4.4%, expensive vs itself. |

> No stock shows "wrong track" today, so by Art's own sell rule (F3) none is a cut. The scan found no candidate that beats all three on dividend-on-DCA, stability and growth at the same time with clean data — the closer ones are worth a deep dive, not a switch.

## 2. The three holdings

### 2.1 Fact-sheet numbers (2026-10-28, close 2026-10-27)

| | AMATA | BBL | TCAP |
|---|---:|---:|---:|
| Price | 28.75 | 185.00 | 80.25 |
| Avg cost (config) | 26.40 | 172.10 | 59.80 |
| DPS FY2025 | 1.10 | 10.00 | 3.50 |
| Yield today / on cost | 3.8% / 4.2% | 5.4% / 5.8% | 4.4% / 5.9% |
| Gate path | growth exception (C3) | main (C1) | growth exception (C3) |
| Growth scenarios bad/mid/good (deep dive, EPS-based) | 0 / 5 / 9% | 0 / 2.5 / 4.5% | 1.5 / 4 / 7% |
| New DCA, year 10, mid (price grows with DPS / flat) | 4.9% / 6.2% | 6.1% / 6.9% | 5.3% / 6.5% |
| New DCA, year 15, mid | 6.3% / 8.0% | 6.9% / 7.8% | 6.5% / 7.9% |
| New DCA, year 10, bad | 3.8% | 5.4% | 4.7% / 5.1% |
| Lump on cost, year 10, mid (T2) | 6.8% ⛔ | 7.4% ✅ | 8.7% ✅ |
| C2: year-5 DPS ÷ today's price, mid | 4.9% ⛔ | 6.1% ✅ | 5.3% ✅ |
| T1 DPS down 2 y · T4 · T6 · PAYOUT · LOSS | all ✅ | ✅ (T4/T6 n/a bank) | ✅ (T4/T6 n/a bank) |

T2 and C2 are our thresholds (7% = Art's direction, now parked as a cut-off; 5% = Niwes C2) — they say "the dividend path is slower than wanted", not "the business broke".

### 2.2 Direction 3–5% → 5% → higher (Art's question)

- **AMATA** — today 3.8% of price. Reaches 5% of today's price in year 5 only in the good case (9%/yr → 5.9% flat price); mid case 4.9%. Lump at 26.40 reaches 5.3% in year 5 (mid). Long-term: mid case passes 7% on new DCA money only around year 15 at flat price (8.0%). Upside not in the table: if FY2026 DPS is set at the 40% payout floor on a 1H-boosted year, FY2026 DPS could be ~1.7–1.8 (deep dive 4.4, `guess:`) — but that is a transfer peak after a presale slump.
- **BBL** — already above 5%; the path is 5.4% → 6–7% over 10 years (mid). Bad case = flat 5.4% forever. It moves toward 7% only via slow growth or buying cheaper (F5 ladder ≤167 / ≤149 / ≤130).
- **TCAP** — 4.4% today, 5% of today's price by year 5 in mid (5.3%); 6.5% by year 10 at flat price. Lump already 5.9% on cost.

### 2.3 Latest quarter — any "wrong track" sign?

| | Latest data | Read |
|---|---|---|
| AMATA | Net profit Q1/26 1,379 m · Q2/26 1,584 m (yfinance; Q2/25 140 m) — record, but deep dive section 1 #5: transfers of 2024 sales + 366 m disposal gain; presale 1H26 377–378 rai vs target 2,800; backlog 22.3 bn (Sep 25) → 18.4 bn (Jun 26) | Profit now ≠ future. Earnings risk sits in 2027–28 (deep dive section 5). Not wrong track yet; T3 trigger = presale < 1,500 rai/yr. |
| BBL | Q3/26 net profit 9,489 m −31.2% YoY; 9M 29,981 m −21.6% (news 20 Oct 2026); 1H26 already −16.2% (deep dive). Interim DPS 2026 held at 2.00 | Rate-cut driven (NIM). If FY2026 DPS < 10 → T1 year 1 only. Review opens only if FY2027 also lower (deep dive section 6). NIM / NPL Q3 figures seen only in a search snippet — not verified, not used. |
| TCAP | Q2/26 net profit 2,641 m (+28% YoY) — boosted by dividend income + lower provisions (deep dive section 1 #3). ttb Q3/26 5,457 m +3.0%, 9M 16,139 m +4.8% (news) | Engine (ttb) still growing. Buyback 7,500 m deadline 16 Feb 2027 still unproven. |

## 3. Scan — anything better?

Filter on the 2026-10-28 scan (mechanical, ours): passed gate · DPS FY2025 · no LOSS / PAYOUT_OVER_100 / YIELD_ABNORMAL / DIVIDEND_HISTORY_SHORT flag · then fact sheet (same script, **rule-based growth, not deep-dive** — so their DCA numbers are more optimistic than our three's deep-dive numbers; not apples-to-apples) + TTM check from yfinance quarterly (GM-2).

| Stock | Yield | Paid (y) / cuts ≥10% in 10 y | EPS growth 10 y (FS A3) | Latest | DCA y10 mid (rule-based) | Read |
|---|---:|---|---:|---|---|---|
| KBANK | 5.7% | 22 / 1 | 2.3% (15 y 6.4%) | Q2/26 13,247 m vs 12,488 m (+6%) | 7.8% / 10.4% | Same sector as BBL + TCAP; profit growing while BBL's falls. 3-y avg yield 4.4%. **Deep dive candidate (vs BBL).** |
| KTC | 5.1% | 14 / 0 | 14.2% (cache, see note) | Q2/26 2,225 m vs 1,895 m (+17%) | 8.0% / 11.8% | Profit 2022→2025 7,079 → 7,668 m (+2.7%/yr), ROE 24% → 18.5%. 3-y avg yield 4.2%. EPS series in cache has breaks (2014 2.44 → 2015 0.80) — growth figure not trusted. **Deep dive candidate.** |
| HMPRO | 5.8% | 24 / 2 | 5.6% | Q2/26 1,594 m vs 1,707 m (−7%) | 8.0% / 10.6% | Daily-life business (C10-type), clean balance sheet. But profit flat 2022–2025 (6,217 → 6,011 m), revenue down 2025, DPS down FY2025. **Deep dive candidate — only if growth story holds.** |
| AEONTS | 6.2% | 25 / 0 | 2.0% (5 y −3.9%) | — | 6.5% / 6.8% | Dividend grew via payout while profit fell (3,815 → 2,860 m 2023→2025). Not better. |
| STANLY | 8.7% | 13 / 1 | 4.4% (cache) | Q2/26 362 m vs 443 m (−18%) | 12.6% / 17.4% | **Data not trusted**: cache EPS 25.04 in 2025 while net profit fell 1,757 → 1,388 m; on profit ÷ shares the FY2025 payout may be ≥100%. Not ranked until checked. |

Others looked at and dropped: AP (T1 lit — DPS down 2 years), PTT (EPS 15 y −0.2%, commodity), SAT (EPS 15 y −0.9%), TISCO (already held, off plan), TTB (already 74% of TCAP).

> None is clearly better than the three across all axes. KBANK and KTC look stronger on recent earnings growth; HMPRO is closest to Niwes' everyday-business picture but its growth has stalled. All three need a deep dive (D1–D18) with deep-dive growth scenarios before any comparison is fair.

## 4. For Art to decide (not decided here)
1. AMATA at 35%: keep DCA as is through the presale test (mid-Nov Q3, FY2026 Feb–Mar 2027), or slow new money until presale recovers — DCA yield at today's price 3.8%.
2. Whether to deep dive KBANK / KTC / HMPRO (≤3), using `docs/deep-dive.md`.
3. BBL: one-year DPS cut in FY2026 (if it comes) = hold per F3 — confirm.

## Data gaps
- AMATA / TCAP Q3/2026 not published yet (SETSMART + yfinance stop at Q2/2026).
- BBL Q3/2026 NIM / NPL / coverage: only seen in a search summary — not verified.
- KBANK Q3/2026 not checked.
- Candidate DCA tables use the fact sheet's mechanical growth rule (no deep dive) — overstated vs our holdings.
- KTC and STANLY EPS history in cache inconsistent (DC-3) — needs annual reports.

## Sources (news, 20 Oct 2026)
- BBL Q3/2026: https://www.infoquest.co.th/2026/666934 · https://www.thansettakij.com/finance/stockmarket/671898 · https://www.mitihoon.com/2026/10/20/687572/
- ttb Q3/2026: https://www.workpointtoday.com/ttb-q3-69-817375-2 · https://www.thansettakij.com/finance/stockmarket/671831
