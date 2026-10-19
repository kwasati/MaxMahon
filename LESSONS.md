# LESSONS — กล่องจด 4-MaxMahon
กล่องจดรอย่อย · ต่อท้ายด้วย `ws.mjs pass` เท่านั้น · ห้ามอ่านเพื่อใช้งาน — ความรู้ที่ใช้ได้อยู่ใน knowledge · ย่อยเมื่อ Art สั่ง


## 2026-10-19 job-13-dd-bbl (desk maxmahon/z79h)
<!-- z79h/job-13-dd-bbl -->
- bangkokbank.com unreachable by every route (curl: connection reset / 90 s timeout x3; WebFetch 60 s timeout x3) — but the bank's year-end press release is mirrored word-for-word on thaipr.net (?p=3146796 / 3293129 / 3563659) and thaitabloid.com (274317) with ECL, NPL, coverage, CET1/Tier1/CAR, NIM, loans · why: IR deck is the only place with the per-year bank table, mirrors carry the same numbers · evidence: table 2.2 of the book, all five FY rows filled from mirrors 2026-10-19.
- WebFetch's summariser mislabels dates on paywalled or Thai-calendar pages (marketscreener headline item summarised as "April 17, 2025" for a "Q1 2026" story; panphol sholder record "September 10, 2024" where the page is in B.E. years) · why: the small model guesses when the text is thin · evidence: both fetches 2026-10-19; book section 10 #8 flags the ambiguity. Treat any date from a fetch summary as unverified unless the article text was quoted.
- Normal EPS for a bank cannot be read from yfinance's "Gain On Sale Of Security" (FY2025 +12,473 m but Q4/25 −7,169 m, Q3/25 +9,223 m — inconsistent with UOBKH's quarterly FVPL/investment gains) · why: yahoo maps bank P&L lines inconsistently · evidence: files/bbl_yf_out.json vs utrade note 22 Oct 2025. Used total revenue − NII delta vs 2024 instead (book 2.3) — the bank's own gain table is still the thing to get.


## 2026-10-19 job-12-dd-amata (desk maxmahon/z79h)
<!-- z79h/job-12-dd-amata -->
- thaifin/SETSMART `diluted_eps` in `yearly_metrics` is unreliable before 2019 for AMATA (2011 0.45 / 2012 1.49 / 2015 0.47 / 2017 1.52 vs attributable profit ÷ shares 0.87 / 1.35 / 1.14 / 1.32) · why: probably separate-statement EPS in some years; the `net_income` column IS attributable (company FY2017 deck matches 1,198 / 1,409 exactly) · evidence: `data/screener_cache/2026-10-19/AMATA.BK.json` vs `_desk/maxmahon/z79h/files/sa_23416.txt` lines 266-267 → any EPS CAGR whose base-year EPS × shares ≠ net profit ±10% is suspect
- investor.amata.com document pages (annual-reports / presentations / company-profile) return 500/404 while the dividend-information and financial-highlights pages work; the 2025 One Report is on amata.listedcompany.com (curl 24 MB, pypdf 306 pages in 9 s) and the 9M-2025 deck on api.lcp.setgroup.or.th/file/presentation/8951 · why: SET-hosted mirrors are the reliable primary sources for this stock · evidence: fetch log in this job
- Brokers and news quote three different AMATA "net profit" figures for one quarter (Q2/2026: 1,795 incl. minorities / 1,584 attributable / 1,286 normalized) and mix presale with transfers (594 rai transfers vs 378 rai presale 1H2026) · why: industrial-estate reporting has two volume measures and a large minority line · evidence: PR vs R1 vs PI in the book's source table


## 2026-10-19 job-14-dd-tcap (desk maxmahon/z79h)
<!-- z79h/job-14-dd-tcap -->
- SEC One Report zip: plain `curl` returned http 000; adding `-e <SEC page URL> --tlsv1.2` and a browser UA made it download (43.6 MB, 506-page PDF inside). The zip also carries `FINANCIAL_STATEMENTS.XLS` — old BIFF format, needs `xlrd` (installed this job), and it holds the **separate** (parent-only) statements that the One Report text search could not isolate.
- The SET-hosted "MDA_TH_Final_20200219.pdf" that search returns for TCAP FY2019 is the Stock Exchange's own MD&A, not TCAP's — check the first page before trusting a search hit.
- FS cache EPS disagrees with the company for FY2019 (7.03 vs 9.43) and FY2020 (6.12 vs 6.26); yfinance quarterly EPS matched the MD&A exactly (2.52 / 2.02) — DC-3 applies to yearly_metrics EPS, not only to liabilities.
- WebFetch's summariser can misread a table cell (TCAP IR dividend table FY2020 net profit came back as "3,124" while EPS 6.26 × 1,049 mn ≈ 6,567) — cross-foot every table the tool reproduces.
