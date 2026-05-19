---
title: Data Sources Guide
audience: developers maintaining MaxMahon
last_audit: 2026-05-19
---

# Data Sources Guide

Comprehensive reference for MaxMahon's 4 data sources, field-by-field source map, fallback chains, cache strategy, and cron policies. Every claim in this doc was derived from a direct code read of the adapter files listed in the "Code Quick-Reference" section at the bottom.

## TL;DR

- **SETSMART API** (paid, subscription "Company Fundamental Data") — primary realtime aggregate snapshot (price, P/E, P/BV, market cap, dividend yield) + 5y quarterly financials.
- **set.or.th** (public JSON, Playwright bootstrap) — primary for DPS event history with explicit fiscal year period (~6y coverage in practice).
- **thaifin** (open-source pip) — single source of truth for 10-16y yearly financial history. If thaifin returns empty = stock treated as delisted.
- **yahooquery** (open-source pip) — supplement for 52w range + capex / operating income / interest expense per year + DPS fallback when set.or.th fails.

**Quick decision:** want a field? Check the field-by-field source map below. Want to add a new field? Audit `scripts/data_adapter.py:_fetch_thaifin` columns first (Rule 3 in CLAUDE.md).

## Source-by-Source Reference

### 1. SETSMART API

- **Base URL:** `https://www.setsmart.com/api/listed-company-api`
- **Auth:** `api-key` header, loaded lazily from `.env` → `SETSMART_API_KEY` (`scripts/setsmart_adapter.py:33-53`)
- **Subscription tier:** "Company Fundamental Data" — 4 endpoints listed below, **no dividend-detail endpoint** (separate subscription, not held). DPS history therefore comes from set.or.th, not SETSMART.
- **HTTP method:** GET
- **Retries:** 3 attempts with exponential backoff (1s, 2s) on HTTP 429 / 503 / Timeout. Other 4xx/5xx errors raise `requests.HTTPError` directly. `scripts/setsmart_adapter.py:56-73`

#### 4 endpoints

| Endpoint | Function | Required params | Optional params | Returns |
|---|---|---|---|---|
| `eod-price-by-symbol` | `fetch_eod_by_symbol` | `symbol`, `startDate` | `endDate`, `adjustedPriceFlag` (default `"Y"`) | list of EOD rows for one symbol |
| `eod-price-by-security-type` | `fetch_eod_all` | `securityType` (default `"CS"`), `date` | `adjustedPriceFlag` (default `"Y"`) | list of EOD rows for ALL symbols on that date (~933 CS rows/day) |
| `financial-data-and-ratio-by-symbol` | `fetch_financial_by_symbol` | `symbol`, `startYear`, `startQuarter` | `endYear`, `endQuarter` | list of quarterly financial rows for one symbol |
| `financial-data-and-ratio` | `fetch_financial_all` | `year`, `quarter` | `accountPeriod` (default `"C"`) | list of quarterly financial rows for ALL symbols that quarter |

#### EOD response fields used downstream

From bulk `eod-price-by-security-type` rows (consumed in `scripts/data_adapter.py:766-887` and `scripts/daily_price_refresh.py:106-110`):

- `symbol` — used to match (note: SETSMART returns **without** `.BK` suffix)
- `close` — current price → maps to `price`
- `pe` → maps to `pe_ratio`
- `pbv` → maps to `pb_ratio`
- `marketCap` → maps to `market_cap`
- `dividendYield` → maps to `dy_snapshot` (used only if DPS-based override unavailable)

#### Financial-by-symbol fields used downstream

From `cached_financial_by_symbol_range` (consumed in `scripts/data_adapter.py:638-661` → `_setsmart_financial_to_yearly`):

Per-quarter row keys (per actual `dict.get` calls):
- `year`, `quarter` — index keys
- `totalRevenueAccum` → yearly `revenue`
- `netProfitAccum` → yearly `net_profit`
- `epsAccum` → yearly `eps`
- `operatingCashFlow` → yearly `ocf`
- `investingCashFlow` → yearly `icf`
- `financingCashFlow` → yearly `fcf` (NB: this is **financing** cash flow, named `fcf` in the local dict — see Surprises section)
- `roe`, `roa`, `de` (percentages — divided by 100 when overlaid onto `yearly_metrics`)
- `totalAssets`, `shareholderEquity`

**Year aggregation rule (`_setsmart_financial_to_yearly`):** only Q4 records are kept; each `*Accum` field already contains the full-year accumulated value, so Q4 row = annual snapshot.

#### Cache

- Cache root: `data/setsmart_cache/`
- File schemas (one JSON file per request, raw API response stored as-is):

| File pattern | Source endpoint | Contents | TTL |
|---|---|---|---|
| `eod_{YYYY-MM-DD}.json` | `eod-price-by-security-type` (bulk) | full-day list of CS rows | until file deleted (no TTL — file existence = cache hit) |
| `eod_by_symbol_{SYM}_{startDate}_{endDate}.json` | `eod-price-by-symbol` | list of per-symbol EOD rows for the range | until file deleted |
| `financial_{year}_q{q}.json` | `financial-data-and-ratio` (bulk) | full-quarter list of all-company rows | until file deleted |
| `financial_by_symbol_{SYM}_{ystart}q{qstart}_{yend}q{qend}.json` | `financial-data-and-ratio-by-symbol` | up to ~20 quarterly rows (5y x 4q) for one symbol | until file deleted |

Cache reader functions: `cached_eod_bulk`, `cached_eod_history`, `cached_financial_bulk`, `cached_financial_by_symbol_range` (`scripts/setsmart_adapter.py:103-142`).

#### Subscription / coverage notes

- **Package coverage:** smoke test (`scripts/setsmart_adapter.py:171-192`) shows BBL EOD coverage starts ~2022 (~3 years history). For pre-2022 yearly history, thaifin is required.
- **Quarterly financial coverage:** 5 years back per subscription (~20 quarterly records max).

#### Code

`scripts/setsmart_adapter.py` — 207 lines, no rate-limit beyond requests-level retry.

---

### 2. set.or.th Public JSON API

- **URL pattern:** `https://www.set.or.th/api/set/stock/{SYMBOL}/corporate-action?lang=en`
- **Auth:** none. But Cloudflare blocks plain HTTPS requests (403).
- **Playwright bootstrap:** module-level singleton browser context (`scripts/set_official_adapter.py:47-76`) launches headless Chromium once per process, visits `https://www.set.or.th/en/market` to receive Cloudflare clearance cookies, then reuses the same `BrowserContext.request` (APIRequestContext) for every subsequent JSON call.
- **Referer required:** API call sends `Referer: https://www.set.or.th/en/market/product/stock/quote/{SYMBOL}/rights-benefits` plus `Accept: application/json`.
- **Inter-request delay:** caller-side `time.sleep(1.5)` between symbols in the weekly cron loop (`server/app.py:1143`).

#### Response filtering

`fetch_dividends` filters events down to: `caType == "XD"` AND `dividendType == "Cash Dividend"` (`scripts/set_official_adapter.py:151-153`). Stock dividends, rights, warrants etc. are dropped.

#### Per-event fields returned (post-filter)

Each event is normalized to:

| Key | Source field | Notes |
|---|---|---|
| `xdate` | `xdate[:10]` | YYYY-MM-DD |
| `payment_date` | `paymentDate[:10]` | |
| `begin_operation` | `beginOperation[:10]` | start of fiscal period |
| `end_operation` | `endOperation[:10]` or inferred | end of fiscal period (FY year derived from this) |
| `period_inferred` | bool | `True` when SET returned null `endOperation` and FY was inferred from xdate |
| `dps` | `float(dividend)` | per-share amount in THB |
| `dividend_type` | `dividendType` | always `"Cash Dividend"` post-filter |
| `source_of_dividend` | `sourceOfDividend` | e.g. `"Net Profit"` or `"Retained Earnings"` |

#### Two dividend types — fiscal year attribution

- **Net Profit dividends** typically have both `beginOperation` and `endOperation` filled → FY is taken directly from `int(end_operation[:4])`.
- **Retained Earnings dividends + interim payouts** typically have `endOperation = null` → fall back to xdate heuristic (`scripts/set_official_adapter.py:155-172`):
  - xdate month Jan-Jun → final of previous FY (end_op = `{prev_year}-12-31`)
  - xdate month Jul-Dec → interim of current FY (end_op = `{curr_year}-12-31`)
  - `period_inferred = True` flag is set on these so the caller knows the FY came from heuristic, not explicit period.

#### Cache

- Path: `data/set_dividend_cache/{SYMBOL}.json` (symbol stripped of `.BK`, uppercased)
- Schema:
  ```json
  {
    "symbol": "HTC",
    "fetched_at": "2026-05-19T06:00:00+00:00",
    "events": [ {xdate, payment_date, begin_operation, end_operation, period_inferred, dps, dividend_type, source_of_dividend}, ... ]
  }
  ```
- TTL: 7 days (`CACHE_TTL_DAYS = 7`, configurable per-call via `cached_dividends(symbol, max_age_days=...)`).
- Atomic write: temp file (`tempfile.mkstemp` in same dir) + `os.replace` — guarantees no half-written cache (`scripts/set_official_adapter.py:208-228`).
- Corrupt JSON / missing keys → cache treated as miss + re-fetch.

#### Coverage limit

Empirically ~6 years of history per symbol (verified via `docs/dps-set-fix-verification-2026-05-19.md`). Older DPS data from set.or.th appears truncated.

#### Code

`scripts/set_official_adapter.py` — 279 lines. Public API: `fetch_dividends`, `cached_dividends`, `dps_by_fiscal_year`.

---

### 3. thaifin

- **Package:** `thaifin` (pip, open-source — scrapes thaifin.com behind the scenes)
- **Auth:** none
- **No local cache layer** — every call hits thaifin's own backend in-memory. Process-level call costs whatever the library returns (~1-3s typical).
- **API used:** `from thaifin import Stock`; `Stock(symbol_without_BK).yearly_dataframe` returns a pandas DataFrame indexed by year (Period or int).
- **Coverage:** 10-16 years of yearly financial data per symbol (broader than SETSMART's ~3y EOD package and ~5y financial-by-symbol).

#### Columns consumed from `yearly_dataframe` (verified via `df.loc[year].get(...)` calls in `scripts/data_adapter.py:121-271`):

- `revenue`
- `gross_profit`
- `net_profit`
- `earning_per_share` → `diluted_eps`
- `sga`
- `equity`
- `total_debt`
- `asset` → `total_assets`
- `operating_activities` → `ocf`
- `investing_activities` → `capex` (negative number, signed)
- `financing_activities`
- `close`
- `mkt_cap`
- `dividend_yield` (percentage, e.g. 5.2)
- `book_value_per_share` → `bvps`
- `da` (depreciation & amortization)
- `roe`, `roa` (percentages — divided by 100 by `_safe_pct`)
- `gpm`, `npm` (percentages → decimals)
- `sga_per_revenue` (percentage → decimal `sga_ratio`)
- `debt_to_equity` (already ratio, e.g. 1.2)
- `cash`
- `revenue_yoy`, `net_profit_yoy`, `earning_per_share_yoy` (percentages → decimals)
- `cash_cycle`
- `ev_per_ebit_da`

Snapshot-only (from latest year row): `price_earning_ratio` → `pe_ratio`; `price_book_value` → `pb_ratio`.

#### Fields thaifin does NOT provide (must come from elsewhere)

- `interest_expense` — thaifin does not break out interest expense; supplied by yahoo (`InterestExpense` line item from `tk.income_statement(frequency='a')`)
- `current_ratio` — not in thaifin yearly schema; supplied by yahoo `financial_data.currentRatio`
- `operating_income` line item (gross_profit - sga is computed as fallback) — yahoo's `OperatingIncome` overrides when available
- `dividends_paid` cash-flow line — always None from thaifin (`scripts/data_adapter.py:247`)
- Capex separated from investing activities — thaifin lumps these into `investing_activities`; yahoo `CapitalExpenditure` overrides
- 52-week high/low — not in yearly data; yahoo `summary_detail.fiftyTwoWeekHigh`/`fiftyTwoWeekLow`
- DPS events per ex-date — only yearly `dividend_yield` available; DPS event series comes from set.or.th or yahoo

#### Failure mode

`_fetch_thaifin` wraps everything in `try/except Exception` and returns `None` on any failure (`scripts/data_adapter.py:378-380`). `fetch_fundamentals` then returns `None` to signal "delisted/missing" — no fallback to yahoo for yearly history.

#### Code

`scripts/data_adapter.py:_fetch_thaifin()` lines 121-380.

---

### 4. yahooquery

- **Package:** `yahooquery` (pip, open-source — hits Yahoo Finance backend)
- **Auth:** none
- **No local cache layer** — every call hits Yahoo. Rate limiting is the main pain point.
- **Symbol convention:** Yahoo expects `.BK` suffix for Thai stocks (`PTT.BK`). `_to_yf_symbol` normalizes.

#### Endpoints called by `_fetch_yahoo_supplement` (`scripts/data_adapter.py:454-635`)

- `tk.summary_detail[sym]` → 52w high/low, 50d/200d avg, dividendRate, trailingAnnualDividendRate, payoutRatio, fiveYearAvgDividendYield, marketCap, trailingPE, dividendYield
- `tk.price[sym]` → regularMarketPrice (current price), marketCap, shortName, currency
- `tk.key_stats[sym]` → priceToBook, forwardPE, trailingEps, forwardEps, freeCashflow
- `tk.financial_data[sym]` → currentPrice, marketCap, forwardPE, freeCashflow, operatingCashflow, revenueGrowth, earningsGrowth, profitMargins, grossMargins, operatingMargins, returnOnEquity, returnOnAssets, debtToEquity, currentRatio, totalRevenue
- `tk.dividend_history(start="2000-01-01")` → DataFrame of DPS events (used as fallback for `dividend_history` when set.or.th fails)
- `tk.cash_flow(frequency='a')` → annual `CapitalExpenditure` → `capex_by_year`
- `tk.income_statement(frequency='a')` → annual `OperatingIncome`, `InterestExpense` → `operating_income_by_year`, `interest_expense_by_year`

#### Retry logic (dividend_history only)

Dividend fetch is wrapped in a 3-attempt retry with delays `[0.5, 1.0]` seconds between attempts (`scripts/data_adapter.py:539-580`). Other endpoints have no retry — failure returns empty dict / `None`.

#### Snapshot flag

`_fetch_yahoo_supplement(symbol, snapshot=True)`:
- When `snapshot=True` (default): early-return with `error: "near-empty info (no price)"` if yahoo's `currentPrice` is None — used when yahoo is the only price source.
- When `snapshot=False` (called by `fetch_fundamentals` once SETSMART has a warm snapshot): skip the early-return gate so dividends/capex/IE still fetch even if yahoo's summary endpoints flake (`scripts/data_adapter.py:527-528, 775`).

#### DPS-from-yahoo issue (why deprecated as primary)

Yahoo's `dividend_history` returns split-adjusted DPS — retroactive adjustments for stock splits / stock dividends silently rewrite historical DPS amounts. This produces wrong values for stocks with split history. set.or.th returns the raw DPS as paid, so it is now the primary source. Yahoo DPS only used as fallback (tag `DPS_SOURCE_YAHOO` in `warnings`).

#### Fiscal-year attribution (yahoo branch)

`_attribute_dividends_to_fiscal_years` (`scripts/data_adapter.py:383-451`) groups yahoo DPS events into FY buckets:
- ex-date Jan-Jun → "final" of previous FY
- ex-date Jul-Dec → "interim" of current FY
- Pattern-detect typical payment count per FY (Counter mode over older FYs); FY = complete when actual events >= typical count
- Returns `{by_fy, is_complete, events_per_fy, typical_count}`

This same heuristic is mirrored in `set_official_adapter.fetch_dividends` for events with null `endOperation`.

#### Code

`scripts/data_adapter.py:_fetch_yahoo_supplement()` lines 454-635.

---

## Field-by-Field Source Map (top-level fetch_fundamentals return dict)

Every field that `fetch_fundamentals()` returns to its caller. Code locations refer to `scripts/data_adapter.py` unless otherwise noted.

| Field | Primary | Fallback 1 | Fallback 2 | Code |
|---|---|---|---|---|
| `symbol` | normalized (`.BK` suffix) | — | — | line 978 |
| `name` | thaifin `info.name` | yahoo `shortName` | — | line 872 |
| `sector` | thaifin `info.sector` | `"N/A"` | — | line 873 |
| `industry` | thaifin `info.industry` | `"N/A"` | — | line 874 |
| `currency` | yahoo `currency` | `"THB"` literal | — | line 982 |
| `price` | SETSMART EOD `close` | yahoo `currentPrice`/`regularMarketPrice` | — (thaifin yearly close not used as live price) | lines 878, 890 |
| `market_cap` | SETSMART EOD `marketCap` | yahoo `marketCap` | thaifin snapshot `market_cap` | lines 881, 891 |
| `pe_ratio` | SETSMART EOD `pe` | yahoo `trailingPE` | thaifin snapshot `pe_ratio` | lines 879, 892 |
| `forward_pe` | yahoo `forwardPE` | — | — | line 897 |
| `pb_ratio` | SETSMART EOD `pbv` | yahoo `priceToBook` | thaifin snapshot `pb_ratio` | lines 880, 893 |
| `dividend_yield` | computed `dps_current / price * 100` (where `dps_current` = set.or.th or yahoo FY DPS) | SETSMART EOD `dividendYield` | None | lines 908-913 |
| `dps` (current FY DPS) | yahoo FY DPS for `latest_complete_fy` | None | — | line 904 |
| `dividend_rate` | alias of `dps_current` | — | — | line 931 |
| `payout_ratio` | computed `dps_current / diluted_eps` (year-matched on `latest_complete_fy`) | yahoo `payoutRatio` | — | lines 933-942 |
| `five_year_avg_yield` | computed mean DPS of last 5 complete FYs / price | yahoo `fiveYearAvgDividendYield` | — | lines 920-929 |
| `eps_trailing` | thaifin snapshot `eps_trailing` | yahoo `trailingEps` | — | line 945 |
| `eps_forward` | yahoo `forwardEps` | — | — | line 946 |
| `revenue` | thaifin snapshot `revenue` | yahoo `totalRevenue` | — | line 949 |
| `revenue_growth` | thaifin snapshot `revenue_growth` (decimal) | yahoo `revenueGrowth` | — | line 950 |
| `earnings_growth` | thaifin snapshot `earnings_growth` | yahoo `earningsGrowth` | — | line 951 |
| `profit_margin` | thaifin snapshot `profit_margin` | yahoo `profitMargins` | — | line 952 |
| `gross_margins` | thaifin snapshot `gross_margins` | yahoo `grossMargins` | — | line 953 |
| `operating_margins` | thaifin snapshot `operating_margins` (currently always None) | yahoo `operatingMargins` | — | line 954 |
| `roe` | thaifin snapshot `roe` (decimal) | yahoo `returnOnEquity` | — | line 955 |
| `roa` | thaifin snapshot `roa` (decimal) | yahoo `returnOnAssets` | — | line 956 |
| `debt_to_equity` | thaifin snapshot `debt_to_equity` (percentage) | yahoo `debtToEquity` | — | line 957 |
| `current_ratio` | thaifin snapshot `current_ratio` (always None) | yahoo `currentRatio` | — | line 958 |
| `free_cashflow` | yahoo `freeCashflow` | thaifin snapshot `free_cashflow` | — | line 961 |
| `operating_cashflow` | yahoo `operatingCashflow` | thaifin snapshot `operating_cashflow` | — | line 962 |
| `recent_dividends` | yahoo `tail(8)` of `dividend_history` | `[]` | — | line 965 |
| `52w_high` | yahoo `fiftyTwoWeekHigh` | — | — | line 968 |
| `52w_low` | yahoo `fiftyTwoWeekLow` | — | — | line 969 |
| `50d_avg` | yahoo `fiftyDayAverage` | — | — | line 970 |
| `200d_avg` | yahoo `twoHundredDayAverage` | — | — | line 971 |
| `yearly_metrics` | thaifin yearly (base) + yahoo patches + SETSMART overrides | — | — | line 790, 820-869 |
| `dividend_history` | set.or.th `dps_by_fiscal_year` | yahoo `dps_by_fiscal_year` (with `DPS_SOURCE_YAHOO` tag) | — | lines 800-817 |
| `fy_is_complete` | yahoo `_attribute_dividends_to_fiscal_years.is_complete` | `{}` | — | line 1014 |
| `dividend_source` | `"set_official"` or `"yahoo"` or `"unknown"` | — | — | lines 810, 816 |
| `warnings` | `["DPS_SOURCE_YAHOO"]` when yahoo fallback used | `[]` | — | line 1016 |

## Field-by-Field Source Map (yearly_metrics rows)

`yearly_metrics` is a list of dicts, one per year. Base values come from thaifin, then yahoo patches selected fields, then SETSMART overrides ROE/ROA/D-E/EPS for years within its 5y range. Code lines refer to `scripts/data_adapter.py`.

| `yearly_metrics[N].field` | Source (after all patches) | Patch step | Code |
|---|---|---|---|
| `year` | thaifin index (string) | — | line 232 |
| `revenue` | thaifin `revenue` | — | line 233 |
| `gross_profit` | thaifin `gross_profit` | — | line 234 |
| `operating_income` | thaifin `gross_profit - sga` (fallback) | yahoo `OperatingIncome` (patch) | lines 235, 832-835 |
| `net_income` | thaifin `net_profit` | — | line 236 |
| `ebitda` | thaifin `net_income + da` (fallback) | yahoo OI-based recompute when OI patched | lines 237, 843-846 |
| `interest_expense` | None from thaifin | yahoo `InterestExpense` patch | lines 238, 837-838 |
| `diluted_eps` | thaifin `earning_per_share` | — (note: SETSMART EPS overlaid as separate `eps_setsmart` field — does NOT overwrite diluted_eps) | line 239, 868-869 |
| `sga` | thaifin `sga` | — | line 240 |
| `equity` | thaifin `equity` | — | line 241 |
| `total_debt` | thaifin `total_debt` | — | line 242 |
| `total_assets` | thaifin `asset` | — | line 243 |
| `ocf` | thaifin `operating_activities` | — | line 244 |
| `fcf` | thaifin `ocf + investing` (fallback) | yahoo `ocf - abs(capex)` (when yahoo capex patched) | lines 245, 826-828 |
| `capex` | thaifin `investing_activities` (signed) | yahoo `CapitalExpenditure` (patch — keeps negative-sign convention) | lines 246, 824-826 |
| `dividends_paid` | None (thaifin doesn't expose) | — | line 247 |
| `roe` | thaifin `roe / 100` | SETSMART `roe / 100` (overrides for years in 5y range) | lines 248, 862-863 |
| `roa` | **Not present in base thaifin row.** Only added when SETSMART has data for that year (`m["roa"] = ss_y["roa"] / 100`). Callers should treat absence as "no ROA available — fall back to `roa_year` from thaifin or aggregate `avg_roe`" | SETSMART `roa / 100` (only writer) | lines 864-865 |
| `roa_year` | thaifin `roa / 100` (always present — this is the thaifin ROA value, named `roa_year` to avoid collision with the SETSMART-added `roa` key) | — | line 264 |
| `gross_margin` | thaifin `gpm / 100` | — | line 249 |
| `net_margin` | thaifin `npm / 100` | — | line 250 |
| `operating_margin` | thaifin `operating_income / revenue` | yahoo OI-based recompute | lines 251, 836 |
| `sga_ratio` | thaifin `sga_per_revenue / 100` | — | line 252 |
| `de_ratio` | thaifin `debt_to_equity` (raw ratio) | SETSMART `de` (raw ratio) | lines 253, 866-867 |
| `current_ratio` | None | — | line 254 |
| `interest_coverage` | None from thaifin | computed `OI / IE` when both yahoo values present, capped at 200 | lines 255, 839-841 |
| `ocf_ni_ratio` | thaifin `ocf / net_income` | — | line 256 |
| `capital_intensity` | thaifin `abs(investing) / ocf` | — | line 257 |
| `close` | thaifin `close` (yearly close) | — | line 258 |
| `dividend_yield` | thaifin `dividend_yield` (percentage) | — | line 259 |
| `mkt_cap` | thaifin `mkt_cap` | — | line 260 |
| `bvps` | thaifin `book_value_per_share` | — | line 261 |
| `payout_ratio` | thaifin-computed: `(dy/100) * close / diluted_eps` | — | line 262 |
| `cash` | thaifin `cash` | — | line 263 |
| `revenue_yoy` | thaifin `revenue_yoy / 100` | — | line 265 |
| `net_profit_yoy` | thaifin `net_profit_yoy / 100` | — | line 266 |
| `eps_yoy` | thaifin `earning_per_share_yoy / 100` | — | line 267 |
| `cash_cycle` | thaifin `cash_cycle` | — | line 268 |
| `financing_activities` | thaifin `financing_activities` | — | line 269 |
| `ev_per_ebit_da` | thaifin `ev_per_ebit_da` | — | line 270 |
| `eps_setsmart` | SETSMART `eps` (added only when SETSMART has data for that year — does NOT overwrite `diluted_eps`) | — | line 869 |

## Decision Matrix — "When to use which source"

| Need | Use |
|---|---|
| Realtime / today's price | SETSMART EOD `close` → yahoo `regularMarketPrice` fallback |
| Today's snapshot P/E, P/BV, market cap, dividend yield | SETSMART EOD → yahoo → thaifin snapshot |
| FY-attributed DPS event history (exact values, no split-adjust) | set.or.th `dps_by_fiscal_year` |
| DPS fallback when set.or.th fails | yahoo `dividend_history` + heuristic FY attribution + tag `DPS_SOURCE_YAHOO` |
| 10-16 year yearly financial history | thaifin (single source, no fallback) |
| 5-year quarterly financials (raw quarter rows) | SETSMART `financial-data-and-ratio-by-symbol` |
| 5-year yearly ROE/ROA/D-E/EPS overrides | SETSMART (Q4 accumulated rows) |
| 52-week high/low + 50d/200d avg | yahoo `summary_detail` (only source) |
| Capex per year (separated from investing activities) | yahoo `cash_flow.CapitalExpenditure` (thaifin lumps together) |
| Interest expense per year | yahoo `income_statement.InterestExpense` (thaifin doesn't break out) |
| Operating income per year (line item, not derived) | yahoo `income_statement.OperatingIncome` |
| Long-term dividend streak (20+ years) | thaifin yearly `dividend_yield > 0` rows |
| Recent DPS values (last ~6 years) for verified FY attribution | set.or.th |
| Hidden-value holding market cap lookup | thaifin first → yahoo fallback (`scripts/data_adapter.py:40-73`) |
| Current ratio | yahoo `financial_data.currentRatio` (thaifin doesn't have it) |
| Forward EPS / forward PE | yahoo only |

## Priority / Order Diagram

```
fetch_fundamentals(symbol):
+- 0. _fetch_setsmart(symbol)            # data/setsmart_cache/* readers
|   +- eod_row    (latest non-empty bulk file walked newest -> 7d back, filter eod_*.json skip empty)
|   +- financial_records (cached_financial_by_symbol_range, 5y x 4q, lazy import)
|   +- financial_yearly  (Q4 accumulated -> {year: {revenue, net_profit, eps, ocf, icf, fcf, roe, roa, de, total_assets, shareholder_equity}})
|   +- use_ss_snapshot = bool(eod_row and eod_row.close is not None)
|
+- 1. _fetch_thaifin(symbol)             # REQUIRED -- returns None on failure -> stock = delisted
|   +- yearly_metrics list (10-16 years, full thaifin schema)
|   +- snapshot dict (latest year's PE/PBV/DY/ROE etc.)
|   +- info {name, sector, industry}
|
+- 2. _fetch_yahoo_supplement(symbol, snapshot=not use_ss_snapshot)
|   +- info dict (currentPrice / 52w / payoutRatio / etc.)
|   +- dividend_history retry loop (3 attempts)
|       +- dps_by_year (calendar-year, debug)
|       +- dps_by_fiscal_year + fy_is_complete (SET-style FY attribution)
|   +- cash_flow annual -> capex_by_year
|   +- income_statement annual -> operating_income_by_year, interest_expense_by_year
|
+- 3. Patch yearly_metrics with yahoo data (lines 819-846)
|   +- m.capex = yahoo capex (negative)
|   +- m.fcf = m.ocf - abs(capex)         # overrides thaifin's ocf+investing
|   +- m.operating_income = yahoo OI
|   +- m.operating_margin = OI / revenue
|   +- m.interest_expense = yahoo IE
|   +- m.interest_coverage = OI / IE (capped at 200)
|   +- m.ebitda = OI + DA (recomputed from yahoo OI when available)
|
+- 4. SETSMART yearly override of yearly_metrics (lines 853-869)
|   +- m.roe = SETSMART roe / 100   (per-year match)
|   +- m.roa = SETSMART roa / 100
|   +- m.de_ratio = SETSMART de
|   +- m.eps_setsmart = SETSMART eps   (NOTE: separate field, does NOT overwrite diluted_eps)
|
+- 5. Build dividend_history (PRIMARY for downstream streak/growth calc)
|   +- try set.or.th dps_by_fiscal_year(sym) -> dividend_source = "set_official"
|   +- if empty / fails: fallback yahoo dps_by_fiscal_year -> dividend_source = "yahoo", warnings += ["DPS_SOURCE_YAHOO"]
|
+- 6. Snapshot fields (price/PE/PBV/mcap):
|   +- if use_ss_snapshot: SETSMART EOD -> fallback thaifin snapshot
|   +- else:               yahoo info  -> fallback thaifin snapshot
|
+- 7. Compute dividend_yield + dps_current + five_year_avg_yield:
    +- dps_current = yahoo dps_by_fiscal_year[latest_complete_fy]   # <-- yahoo only, NOT set.or.th
    +- dividend_yield = (dps_current / price) * 100  if dps_current is not None
    +- elif dy_snapshot (SETSMART EOD dividendYield) is not None: dy = dy_snapshot
    +- else: dy = None
    +- five_year_avg_yield = mean(yahoo dps_by_fiscal_year[last 5 complete FYs]) / price * 100
                            fallback yahoo summary_detail.fiveYearAvgDividendYield
```

## Cache Strategy

| Source | Cache Path | Per-file schema | TTL | Refresh job |
|---|---|---|---|---|
| SETSMART EOD bulk | `data/setsmart_cache/eod_{YYYY-MM-DD}.json` | list of dicts (raw API) | file existence (no expiry) | `daily_price_refresh` 19:00 Asia/Bangkok (walks today->7d back) |
| SETSMART EOD per-symbol range | `data/setsmart_cache/eod_by_symbol_{SYM}_{from}_{to}.json` | list | file existence | on-demand |
| SETSMART financial bulk per quarter | `data/setsmart_cache/financial_{year}_q{q}.json` | list | file existence | on-demand |
| SETSMART financial per-symbol range | `data/setsmart_cache/financial_by_symbol_{SYM}_{ystart}q{qstart}_{yend}q{qend}.json` | list (~20 quarterly rows) | file existence | warmed nightly by `daily_price_refresh._refresh_setsmart_financial` after EOD pass |
| set.or.th dividend per symbol | `data/set_dividend_cache/{SYMBOL}.json` | `{symbol, fetched_at, events[]}` | 7 days (configurable per-call) | `weekly_dividend_refresh` Sun 06:00 Asia/Bangkok |
| thaifin | n/a | n/a (library hits backend each call) | n/a | per call |
| yahooquery | n/a | n/a (library hits backend each call) | n/a | per call |
| Aggregated per-stock snapshot | `data/screener_cache/{YYYY-MM-DD}/{symbol}.json` | full `fetch_fundamentals` return dict | same-day only (filename + `fetched_at` prefix match required) | written by `fetch_data._save_to_cache` after each successful fetch (skipped if `dy > 0` but `dividend_history` empty — yahoo flake guard) |
| Per-symbol latest price | `data/price_cache/{symbol}.json` | `{symbol, price, fetched_at, source}` (`source` in `setsmart` or `yahoo`) | rewritten each refresh | `daily_price_refresh` 19:00 |

## Refresh Schedule (APScheduler in `server/app.py`)

| Job ID | Function | Cron | Source code |
|---|---|---|---|
| `max_pipeline` | `scheduled_run` (unified scan over 933 universe) | Configurable via `config.schedule` (default Sun 09:00 Asia/Bangkok) | `server/app.py:1060-1068`, registered at 1165-1172 |
| `daily_price_refresh` | `scheduled_price_refresh_job` -> `scripts/daily_price_refresh.refresh_prices` | Every day 19:00 Asia/Bangkok | `server/app.py:1071-1088`, registered at 1182-1190 |
| `weekly_dividend_refresh` | `scheduled_dividend_refresh_job` (set.or.th for full `set_universe.json`) | Sun 06:00 Asia/Bangkok | `server/app.py:1091-1147`, registered at 1197-1206 |

All three jobs are registered unconditionally in `apply_schedule(config)` except `max_pipeline` which respects `schedule.enabled` toggle.

## Subscription / Access Notes

- **SETSMART** — paid subscription. Tier held: "Company Fundamental Data" — exposes 4 endpoints documented above. Does **not** include the dividend-detail endpoint (separate subscription, not held). API key in root `.env` as `SETSMART_API_KEY`. Loader strips quotes and whitespace.
- **set.or.th** — free public API but Cloudflare-protected. Playwright Chromium headless must visit any set.or.th HTML page first to bank clearance cookies; same `BrowserContext` then makes JSON API calls via its `APIRequestContext`. Module-level singleton — bootstrap only happens once per process.
- **thaifin** — pip package, no auth.
- **yahooquery** — pip package, no auth. Heavy rate limiting can produce empty responses; partial mitigations: dividend retry loop (3x), batch sizing of 20 (`daily_price_refresh._yahoo_fetch_batch`), 30s sleep + 1.5s/symbol sequential retry for stubborn flakes.

## Error / Fallback Behavior

| Failure scenario | Behavior |
|---|---|
| SETSMART API HTTP 429/503 | requests-level retry 3x with exp backoff (1s, 2s) then raises `requests.HTTPError` |
| SETSMART API HTTP 500 (out-of-coverage date range) | raised; smoke test wraps explicitly, but `_fetch_setsmart` general `except Exception` returns None (logs warning) |
| SETSMART cache miss + API fails | `_fetch_setsmart` returns None; `fetch_fundamentals` falls back to yahoo + thaifin snapshot |
| SETSMART EOD bulk no data for last 8 days | `_load_setsmart_eod_map` returns `({}, None)` and `daily_price_refresh` falls back to yahoo batch |
| set.or.th Playwright import fails | `_SET_OFFICIAL_AVAILABLE = False` at module load (warning logged); `fetch_fundamentals` falls back to yahoo DPS + tags `DPS_SOURCE_YAHOO` |
| set.or.th API returns non-200 | `fetch_dividends` raises RuntimeError → caught in `fetch_fundamentals` exception handler → fallback yahoo + tag |
| set.or.th returns empty events list | `fetch_fundamentals` raises ValueError("set.or.th returned empty") → caught → fallback yahoo + tag |
| thaifin returns empty / raises | `_fetch_thaifin` returns None → `fetch_fundamentals` returns None → caller marks `{delisted: True}` |
| yahoo `dividend_history` empty (parallel rate-limit flake) | 3-attempt retry with delays; on final fail logged as warning, `dividend_history` left empty |
| yahoo summary endpoints flake while SETSMART is warm | `_fetch_yahoo_supplement(snapshot=False)` skips the no-price gate so dividends/capex/IE still fetch; info dict left mostly empty |
| Cache integrity (downstream save) | `fetch_data._save_to_cache` skips writing when `dividend_yield > 0` but `dividend_history` empty (yahoo poison guard) |

## Surprises / Findings During Audit

0. **Top-level snapshot DPS ignores `dividend_source`:** when set.or.th succeeds, `dividend_history` is built from set.or.th — but the snapshot fields `dps`, `dividend_rate`, `dividend_yield` (computed), and `five_year_avg_yield` read from **yahoo's** `dps_by_fiscal_year` regardless (`scripts/data_adapter.py:904, 923`). The values typically agree, but for stocks with stock splits the yahoo DPS is split-adjusted and the set.or.th `dividend_history` is not — so a downstream UI showing both will see mismatched numbers. Fix: change line 904/923 to read from set.or.th's `dps_by_fiscal_year` when `dividend_source == "set_official"`.
1. **Dead code in thaifin branch:** `_fetch_thaifin` computes a `dividend_history` dict from yearly `dy% * close / 100` (`scripts/data_adapter.py:294-301`) and returns it inside the `tf_data` dict. But `fetch_fundamentals` unconditionally rebuilds `dividend_history` from set.or.th (or yahoo fallback) before the return statement, so the thaifin-derived DPS is never surfaced. Worth removing or wiring back as a tertiary fallback when both set.or.th and yahoo fail.
2. **Naming collision in SETSMART aggregation:** `_setsmart_financial_to_yearly` stores `financingCashFlow` under the dict key `"fcf"` (`scripts/data_adapter.py:655`). The real free cash flow (OCF - capex) is computed elsewhere. The collision is harmless because this dict is only consumed for `roe/roa/de/eps` overrides, but a future maintainer overlaying `fcf` from `ss_fin_yearly` would silently use financing cash flow instead.
3. **`eps_setsmart` is intentionally not overwriting `diluted_eps`:** the SETSMART overlay block writes `m["eps_setsmart"]` (a new key) instead of overwriting `m["diluted_eps"]` (`scripts/data_adapter.py:868-869`). This preserves thaifin EPS for streak / CAGR calculations. Document this so callers don't reach for `eps_setsmart` thinking it's the official EPS.
3a. **`roa` key in yearly_metrics is SETSMART-only, not thaifin:** the base thaifin row stores ROA under `roa_year` (line 264). The `roa` key is created only when SETSMART has data for that year (lines 864-865) — so years outside SETSMART's 5y range will be **missing** the `roa` key entirely. The inline comment at line 850 ("thaifin schema: m[\"roe\"], m[\"roa\"] ...") is misleading on this point. Downstream code that needs ROA-per-year should read `m.get("roa") or m.get("roa_year")`.
4. **`current_ratio` is hard-coded None from thaifin** (`scripts/data_adapter.py:254`) — only yahoo provides it. Worth flagging in field doc.
5. **`fy_is_complete` in `fetch_fundamentals` return dict comes from yahoo only** (`yf_fy_complete` at line 1014) — even when `dividend_source == "set_official"`. set.or.th doesn't currently produce its own completeness flag dict; the heuristic relies on yahoo's calendar pattern. If yahoo retry fails this dict is empty, which downgrades `count_dividend_streak` to the year-based fallback (`y < current_year`).
6. **`dividends_paid` from thaifin yearly is always None** (`scripts/data_adapter.py:247`) — code-level comment confirms thaifin's cash-flow split doesn't include this line. `compute_payout_sustainability` is built around DPS instead.
7. **SETSMART EOD `close` is "adjusted" by default** (`adjustedPriceFlag="Y"` — `scripts/setsmart_adapter.py:78`). For DPS x price compatibility audits this is fine; for raw historical comparisons it matters.
8. **`fetch_eod_by_symbol` is exposed but never called by the orchestrator.** The only invocations are in smoke tests. The orchestrator pulls EOD from the bulk file walk, not per-symbol. Per-symbol range is hooked up to `cached_eod_history` (also unused in current pipeline). Worth flagging that these are reserved for future use or could be removed.
9. **`fetch_yfinance_supplement` alias** still exposed for backward compatibility (`scripts/data_adapter.py:744`) — DEPRECATED in comment. New code should call `fetch_yahoo_supplement` directly.
10. **Holding mcap cache (`_HOLDING_MCAP_CACHE`)** is process-level only; resets on restart. Fine for short-lived scan jobs but means each fresh process re-hits thaifin / yahoo for every hidden-value holding. Adequate for current scale.

## Code Quick-Reference

- Adapter modules:
  - `scripts/setsmart_adapter.py` — SETSMART API client (207 lines, 4 endpoints + 4 cache wrappers)
  - `scripts/set_official_adapter.py` — set.or.th DPS adapter (279 lines)
- Orchestrator: `scripts/data_adapter.py:fetch_fundamentals()` lines 747-1017
- Sub-fetchers:
  - thaifin: `scripts/data_adapter.py:_fetch_thaifin()` lines 121-380
  - yahoo: `scripts/data_adapter.py:_fetch_yahoo_supplement()` lines 454-635
  - SETSMART local cache reader: `scripts/data_adapter.py:_fetch_setsmart()` lines 665-737
- Yearly aggregation helper: `scripts/data_adapter.py:_setsmart_financial_to_yearly()` lines 638-661
- Top-level fetch + cache: `scripts/fetch_data.py:fetch_multi_year_safe()` lines 711-732, cache I/O 640-672
- Daily price refresh: `scripts/daily_price_refresh.py:refresh_prices()` lines 260-346
- Weekly dividend refresh: `server/app.py:scheduled_dividend_refresh_job()` lines 1091-1147
- Cron registration: `server/app.py:apply_schedule()` lines 1153-1206
