# Hong leg — candidates to replace SISB · SECURE (2026-10-28)

Request: Art via Karl 2026-10-28 — deep dive SWC · PSP · KCG and propose a new Hong set inside the 25% leg. SISB · SECURE = cut, still held, no new buys, sell at the time the replacement is bought (agreement F6 in `C:\WORKSPACE\projects\4-MaxMahon\roadmap\agreed-portfolio-framework.md`). No buy/sell orders (R6) — this is a proposal for Art. `rebalance.py` TARGETS not touched.

Sources: deep dives `_deep_SWC_2026-10-28.md` · `_deep_PSP_2026-10-28.md` · `_deep_KCG_2026-10-28.md` (this folder) · TOA / MOSHI from `hong-keep-or-cut-2026-10-28.md`. Quarterly EPS + price (close 2026-10-27) re-checked by the head against SETSMART pull 2026-10-28 and `data\screener_cache\2026-10-28\`: SWC TTM EPS 0.40 → PE 12.1 · PSP H1/26 EPS 0.57 vs 0.38, TTM 0.80 → PE 9.5 · KCG H1/26 0.50 vs 0.40, TTM ~1.02 → PE 10.1 — all match the deep dives.

## The 5 names side by side

| | KCG | PSP | SWC | MOSHI | TOA |
|---|---|---|---|---|---|
| Status | candidate | candidate | candidate | held 3.75% | held 7.5% |
| 3-y profit CAGR (2022→25) | 27.8% NP (fixed 545 m shares since IPO) | 16.5% NP · EPS ~6% (IPO dilution) · 2-y EPS 26.7% | 111% NP — trough base (2025 NP still below 2018) | 24.6% EPS / 38.3% NP | 28.9% — low 2022 base (2019→25 = 5.1%) |
| H1/26 profit y-y | +25% | +50% EPS | +63% | +22% | +21% |
| Where 2026 growth comes from | butter/cheese cost at 5-y low; sales H1 +4%, Q2 +0.3% | base-oil price spike (company's own MD&A) — windfall | selling-expense "accounting adjustment"; GM fell | ~35 new stores/yr; SSSG slowing | margin at record; sales flat |
| PE TTM | 10.1 | 9.5 | 12.1 | 16.1 | 9.0 |
| PEG 3-y / current pace | 0.36 / 0.40 | 0.57 (NP) / 0.19 (H1) — 2027 profit likely −15–20% | 0.11 / 0.49 TTM · 0.76 on sustainable 16% → fails | 0.66 / 0.75 | 0.31 / 0.90 → fails |
| Hong cash gate (#2) | ❌ cash 0.17× OD (importer, bank-funded WC; CFO 2.1× NP) | ❌ ~0.2× | ✅ net cash 358 m | ✅ | ✅ |
| Biggest flag | dairy cost cycle turning up | deputy CEO / largest holder sanctioned by SEC 1 Sep 2026 (META) | ~80 k baht/day turnover; TOA family (2nd Tangkaravakoon name) | SSSG ~0–2% in Q3 | GM at cycle top |
| Deep-dive verdict | enter small · max 6.25% | not as growth slot · ≤3.75% after Q3 + SEC outcome | not full slot · ≤3.75% after Q3 | go on | watch |
| Base-case price (deep dive) | 10.8–13.0 vs 10.40 (+4–25%) + ~5.5% yield | 2027 basis 6.6–8.2 vs 7.60 (−13 to +8%) | 4.3–5.6 vs 4.88 (−12 to +15%) | — | — |

> None of the three is a clean 26%-compounder. KCG is the only one whose growth is three straight years and still running; PSP and SWC are 2026 jumps from a windfall / an unexplained expense line, and both need Q3/26 (~12–13 Nov 2026) before any money.

## Proposed Hong set (inside 25%)

| Stock | Now | Proposed | Why |
|---|---:|---:|---|
| TOA | 7.5 | 7.5 | unchanged — watch on Q3 margin (keep-or-cut); not cut |
| MOSHI | 3.75 | 6.25 | only held name with growth intact (H1 +22%, sales +17%); PE 16 is why it stops at 6.25 |
| KCG | — | 6.25 | 3-y NP +28%/yr, H1 +25%, profit = cash, PE 10; cap 6.25 because cash gate fails + thin turnover + cost-cycle margin |
| SISB | 7.5 | 0 | cut (F6) — sold when KCG / MOSHI are bought |
| SECURE | 6.25 | 0 (5.0 held until Q3) | cut (F6) — the 5.0 below stays in the shares already held, no new buys |
| Open slot | — | 5.0 | decided after Q3/26 (~13 Nov 2026): PSP or SWC if their Q3 confirms (deep-dive triggers below); otherwise re-scan |
| **Total** | **25.0** | **25.0** | |

- **Sequence (F6):** buying KCG + MOSHI top-up (8.75%) is funded by selling SISB (7.5%) + part of SECURE (1.25%); the remaining 5.0% stays in SECURE until the open slot is filled — no new SECURE buys. SECURE's own Q3 lands the same week.
- **Entry pace:** Hong 30:30:30:10 (`_master_hong-lens_2026-05-21.md` entry rule) for KCG.
- **Q3 checks that open the 5% slot:** PSP — GM stays ≥ ~18% and SEC outcome on the deputy CEO known · SWC — Q3 NP ≥ +15% y-y with GM ≥ 40% and the expense adjustment explained. Either fails → slot stays shut, re-run `hong_stage1_scanner.py --version v5 --universe all` after Q3 data.
- Concentration if SWC is ever picked: TOA + SWC = two companies of one family in a 25% leg — Art to decide.

## For Art to decide
1. Accept KCG despite failing Hong cash gate #2 (the reason it was cut in May 2026)?
2. MOSHI 3.75 → 6.25?
3. Hold the 5% open slot in SECURE until Q3, or move it now to KCG / MOSHI?
4. Then TARGETS in `scripts\rebalance.py` get updated in one change.
