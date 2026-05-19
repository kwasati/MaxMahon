# DPS set.or.th Fix Verification - 2026-05-19

Verifies `set_official_adapter.dps_by_fiscal_year()` against SETSMART ground truth (where available).

Tolerance: +/-5.0% per fiscal-year.

## HTC

**Fetched:** FY2020=1.12, FY2021=1.79, FY2022=1.52, FY2023=1.52, FY2024=1.05, FY2025=0.99

| FY | Expected | Actual | Status |
|----|----------|--------|--------|
| 2022 | 1.52 | 1.52 | PASS |
| 2023 | 1.52 | 1.52 | PASS |
| 2024 | 1.05 | 1.05 | PASS |
| 2025 | 0.99 | 0.99 | PASS |

## BBL

**Fetched:** FY2020=2.5, FY2021=3.5, FY2022=4.5, FY2023=7.0, FY2024=8.5, FY2025=10.0

_pending manual ground truth - data fetched OK_

## ILM

**Fetched:** FY2020=0.27, FY2021=0.55, FY2022=0.8, FY2023=1.0, FY2024=1.0, FY2025=1.0

_pending manual ground truth - data fetched OK_

## KBANK

**Fetched:** FY2020=2.5, FY2021=3.25, FY2022=4.0, FY2023=6.5, FY2024=12.0, FY2025=14.0

_pending manual ground truth - data fetched OK_

## PTT

**Fetched:** FY2020=0.82, FY2021=2.0, FY2022=2.0, FY2023=2.0, FY2024=2.1, FY2025=2.3

_pending manual ground truth - data fetched OK_

## AMATA

**Fetched:** FY2020=0.2, FY2021=0.4, FY2022=0.6, FY2023=0.65, FY2024=0.8, FY2025=1.1

_pending manual ground truth - data fetched OK_

## Summary

- HTC: PASS 4/4
- BBL: pending manual verify
- ILM: pending manual verify
- KBANK: pending manual verify
- PTT: pending manual verify
- AMATA: pending manual verify

**Overall (symbols with ground truth):** PASS 4/4
