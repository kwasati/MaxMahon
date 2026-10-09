# Hong Stage 1 Scan — v5 (Skip Gate 2) — 2026-05-21

> **Scan date:** 2026-05-21  
> **Data cache date:** 2026-05-20  
> **Universe:** 841  
> **Scanned:** 841  
> **Passed 6 hard gates:** **39**  
> **Elapsed:** 0.0s  

> **WARNING:** Gate 2 (Cash Adequacy) removed in v5 because cache has no
> `short_term_debt` and no `dividends_paid` per FY — v4 proxies were unreliable.
> Every survivor below is flagged `MANUAL_CHECK_NEEDED: cash_adequacy` and must be
> verified in Stage 2 manual review (annual report — short-term debt + dividends paid).

## 6 Hard Gates

| # | Gate | Threshold |
|---|------|-----------|
| 1 | Solvency (sector-aware) | default D/E ≤ 1.0, retail ≤ 2.5, bank ROA 3y ≥ 1% |
| 3 | Margin slope | gm 3y slope ≥ 0 AND nm 3y slope ≥ 0 |
| 4 | CFO / Net profit | 3y avg ≥ 0.8 |
| 5 | ROE relative | 3y avg ≥ max(industry median, 12%) |
| 6 | Profit new high | latest = max of last 5y |
| 7 | Forward PE | ≤ 15 (trailing fallback) |

**Gate 2 (Cash adequacy) REMOVED** — manual review required.

## Sweet Spot Composite (rank survivors)

Composite = CAGR_score × 0.4 + Yield_score × 0.3 + PEG_score × 0.3

- **CAGR 3y:** 0%→0, 26%+→100 capped
- **Dividend yield:** 0→0, 4%→70, 7%+→100
- **PEG (Fwd PE / growth%):** 0→0, 1.0→50, 1.5+→100

## Gate failure breakdown (6 gates)

| Gate | Failed | No-data |
|------|--------|---------|
| Gate 1 Solvency | 290 | 2 |
| Gate 3 Margin slope | 510 | 54 |
| Gate 4 CFO/NP | 111 | 339 |
| Gate 5 ROE relative | 591 | 35 |
| Gate 6 New high | 620 | 36 |
| Gate 7 Fwd PE | 204 | 139 |

## Top 30 by Composite Score (39 survivors)

| Rank | Sym | Name | Sector | Composite | CAGR3y | Yield | PEG | ROE | FwdPE | Manual_Cash_Check |
|------|-----|------|--------|-----------|--------|-------|-----|-----|-------|-------------------|
| 1 | ICHI | ICHITAN GROUP PUBLIC COMP | Food & Beverage | 100.0 | 27.4% | 8.5% | 7.72 | 21.4% | 12.6 | PENDING |
| 2 | SECURE | NFORCE SECURE PUBLIC COMP | - | 99.1 | 30.2% | 8.8% | 1.47 | 15.7% | 7.5 | PENDING |
| 3 | XO | EXOTIC FOOD PUBLIC COMPAN | - | 85.3 | 19.6% | 5.4% | 12.83 | 42.0% | 9.3 | PENDING |
| 4 | SISB | SISB PUBLIC COMPANY LIMIT | Professional Servi | 84.7 | 37.6% | 5.0% | 1.18 | 26.9% | 10.3 | PENDING |
| 5 | TKN | TAOKAENOI FOOD & MARKETIN | Food & Beverage | 84.6 | 66.2% | 6.2% | 1.06 | 30.7% | 13.3 | PENDING |
| 6 | SAV | Samart Aviation Solutions | Transportation & L | 80.7 | 39.9% | 8.4% | 0.71 | 34.8% | 12.5 | PENDING |
| 7 | UBA | Utility Business Alliance | - | 77.4 | 11.3% | 9.1% | 9.83 | 13.6% | 9.0 | PENDING |
| 8 | CPALL | CP ALL PUBLIC COMPANY LIM | Commerce | 76.8 | 28.6% | 3.5% | 1.11 | 20.0% | 12.5 | PENDING |
| 9 | TVO | THAI VEGETABLE OIL PUBLIC | Food & Beverage | 76.8 | 10.9% | 7.9% | 2.36 | 15.6% | 9.6 | PENDING |
| 10 | AKR | EKARAT ENGINEERING PUBLIC | Industrial Materia | 76.6 | 46.0% | 7.6% | 0.44 | 15.0% | 11.9 | PENDING |
| 11 | NSL | NSL FOODS PUBLIC COMPANY  | Food & Beverage | 74.5 | 26.6% | 4.8% | 0.75 | 27.9% | 8.7 | PENDING |
| 12 | READY | READYPLANET PUBLIC COMPAN | - | 73.5 | 37.9% | 9.9% | 0.24 | 20.2% | 7.3 | PENDING |
| 13 | TFM | THAI UNION FEEDMILL PUBLI | Agribusiness | 72.8 | 88.5% | 9.2% | 0.19 | 18.5% | 6.8 | PENDING |
| 14 | TSC | THAI STEEL CABLE PUBLIC C | Automotive | 71.7 | 7.6% | 7.9% | 1.84 | 16.8% | 11.0 | PENDING |
| 15 | TOA | TOA PAINT (THAILAND) PUBL | Construction Mater | 70.3 | 27.2% | 6.4% | 0.15 | 17.9% | 7.8 | PENDING |
| 16 | POLY | Polynet Public Company Li | Automotive | 70.3 | 21.0% | 8.0% | 0.53 | 16.2% | 11.9 | PENDING |
| 17 | MASTER | Master Style Public Compa | Health Care Servic | 70.3 | 47.5% | 5.0% | 0.42 | 48.6% | 10.6 | PENDING |
| 18 | KCG | KCG CORPORATION PUBLIC CO | Food & Beverage | 70.0 | 27.8% | 5.2% | 0.35 | 15.5% | 8.5 | PENDING |
| 19 | ILINK | INTERLINK COMMUNICATION P | Information & Comm | 69.1 | 16.9% | 6.9% | 0.89 | 12.6% | 5.6 | PENDING |
| 20 | AMARC | ASIA MEDICAL AND AGRICULT | - | 68.4 | 121.9% | 6.3% | 0.03 | 12.6% | 8.8 | PENDING |
| 21 | ILM | INDEX LIVING MALL PUBLIC  | Commerce | 67.0 | 4.6% | 8.0% | 8.26 | 12.2% | 8.7 | PENDING |
| 22 | SANKO | SANKO DIECASTING (THAILAN | - | 66.3 | 72.3% | 5.0% | 0.15 | 19.6% | 4.0 | PENDING |
| 23 | MOSHI | Moshi Moshi Retail Corpor | Commerce | 65.1 | 38.3% | 3.5% | 0.46 | 24.4% | 13.3 | PENDING |
| 24 | HTC | HAAD THIP PUBLIC COMPANY  | Food & Beverage | 64.8 | 4.0% | 6.6% | 20.48 | 14.1% | 10.7 | PENDING |
| 25 | AIT | ADVANCED INFORMATION TECH | Information & Comm | 63.6 | 2.4% | 7.7% | 8.21 | 13.6% | 12.4 | PENDING |
| 26 | OSP | OSOTSPA PUBLIC COMPANY LI | Food & Beverage | 63.5 | 23.8% | 5.5% | 0.10 | 15.6% | 12.3 | PENDING |
| 27 | YUASA | YUASA BATTERY (THAILAND)  | - | 63.0 | 20.9% | 6.5% | 0.15 | 12.5% | 6.1 | PENDING |
| 28 | PM | PREMIER MARKETING PUBLIC  | Food & Beverage | 62.7 | 19.2% | 7.7% | 0.21 | 27.2% | 10.9 | PENDING |
| 29 | KDH | THONBURI MEDICAL CENTRE P | Health Care Servic | 61.7 | 55.0% | 3.2% | 0.32 | 16.4% | 10.7 | PENDING |
| 30 | PSP | P.S.P.Specialties Public  | Industrial Materia | 57.2 | 16.6% | 6.2% | 0.28 | 21.3% | 7.4 | PENDING |

## Limitations & Notes

- **Gate 2 removed:** Cache has no `short_term_debt` (only `total_debt`) and no `dividends_paid` per FY. v4 proxies (0.3 * total_debt + dps * shares) were unreliable. Every survivor is flagged `MANUAL_CHECK_NEEDED: cash_adequacy` — Stage 2 must verify from annual report.
- **CAGR 3y:** computed from net_income series (3 intervals → 4 data points). Returns -100% if latest year unprofitable, None if 3y-ago year ≤ 0.
- **PEG growth source:** prefers `earnings_growth` (yfinance fwd), falls back to 3y CAGR.
- **Bank gate 1:** banks evaluated by ROA 3y ≥ 1% instead of D/E.
- **Industry-median ROE:** only sectors with ≥3 valid samples; otherwise gate 5 threshold = 12% absolute floor.
- **Stage 1 only:** quantitative pass — Stage 2 manual (management, moat, governance, **cash adequacy**) still required.
