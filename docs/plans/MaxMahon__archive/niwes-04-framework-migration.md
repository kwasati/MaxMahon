---
project: MaxMahon
created: 2026-04-20
last_updated: 2026-04-20
status: done
---

# MaxMahon Framework Migration — Niwes 100% (Atomic Tasks)

> Part 4 of 8 — Index: niwes-master-index | Depends on: niwes-01-data-adapter-readiness, niwes-02-research-report | Parallel-safe with: niwes-03, niwes-05 — replace Buffett+เซียนฮง ด้วย Niwes 100% atomic split (filter / score / tag / prompt / claude.md / e2e) ป้องกัน atomic risk ถ้า fail กลางทาง

## Phase 1: Archive existing framework
- [x] สร้าง folder `projects/MaxMahon/docs/archive/` + copy snapshot: `cp projects/MaxMahon/scripts/screen_stocks.py projects/MaxMahon/docs/archive/buffett_seanhong_screener_v3.py.txt` + `cp projects/MaxMahon/scripts/scan.py projects/MaxMahon/docs/archive/buffett_seanhong_scan_v3.py.txt`. สร้าง `projects/MaxMahon/docs/archive/README.md` อธิบาย: ทำไม archive (preserve Buffett quality + เซียนฮง active value mindset), ใครจะอยากอ่านเมื่อไหร่ (ถ้า Karl อยากกลับ Buffett mode ในอนาคต), pre-niwes commit hash. — Acceptance: 3 ไฟล์ใน archive + README ครบ + commit hash ระบุ

## Phase 2: Update screen_stocks.py — Niwes hard filters
- [x] แก้ `projects/MaxMahon/scripts/screen_stocks.py` — Read ทั้งไฟล์ก่อนแก้: REPLACE hard filters เดิม (ROE/Net Margin/D/E) ด้วย Niwes 5-5-5-5 filters เท่านั้น: (1) dividend_yield ≥5% (จาก normalized earnings, ใช้ compute_normalized_earnings จาก niwes-01), (2) dividend_streak ≥5 ปีต่อเนื่อง (count_dividend_streak), (3) no loss 5 ปีล่าสุด (eps positive 5/5), (4) P/E ≤ 15 (target ≤8 = bonus), (5) P/BV ≤ 1.5 (target ≤1.0 = bonus), (6) market_cap ≥5B (เก็บไว้). — Scope: ห้ามแตะ Quality Score function, ห้ามแตะ Signal tag function. — Acceptance: รัน `cd projects/MaxMahon && py scripts/screen_stocks.py` ไม่ error, output filtered list ตาม Niwes filters, comment ใน code อ้างอิง ดร.นิเวศน์

### Reference
```python
# current screen_stocks.py — hard filters (อ้าง CLAUDE.md):
# - ROE avg >= 15% non-financial / >= 10% financial
# - Net Margin avg >= 10% (skip financial)
# - D/E <= 1.5 (non-fin) / <= 10 (financial)
# - EPS+ 3/4 ปี, FCF+ 3/4 ปี
# - Market Cap >= 5B

# new — Niwes 5-5-5-5 filters:
# - dividend_yield >= 5% (จาก normalized earnings)
# - dividend_streak >= 5 ปีต่อเนื่อง (no skip)
# - no loss 5 ปี (eps positive 5/5)
# - P/E <= 15 (<=8 bonus)
# - P/BV <= 1.5 (<=1.0 bonus)
# - market_cap >= 5B (keep — Niwes ก็เน้น mid-large)
```

## Phase 3: Update screen_stocks.py — Niwes Quality Score
- [x] แก้ `projects/MaxMahon/scripts/screen_stocks.py` — REPLACE Quality Score weights ด้วย Niwes Dividend-First: Dividend 50 (yield 15 + streak 15 + payout sustainability 10 + dividend growth 10) + Valuation 25 (P/E 10 + P/BV 10 + EV/EBITDA 5) + Cash Flow Strength 15 (FCF positive 5 + OCF/NI ratio 5 + Interest coverage 5) + Hidden Value 10 (manual flag จาก check_hidden_value, +5 ถ้ามี holding listed > parent market cap). Cap 0-100. — Scope: ห้ามแตะ filter (Phase 2), ห้ามแตะ tag (Phase 4). — Acceptance: function compute_quality_score return 0-100, ตัวอย่าง CPALL >70 (high dividend + sustainable)

### Reference
```python
# current Quality Score weights (CLAUDE.md):
# Dividend 35 + Profitability 25 + Growth 20 + Strength 20

# new — Niwes Dividend-First:
# Dividend 50 (yield 15 + streak 15 + payout_sus 10 + div_growth 10)
# Valuation 25 (P/E 10 + P/BV 10 + EV/EBITDA 5)
# Cash Flow Strength 15 (FCF+ 5 + OCF/NI 5 + Interest coverage 5)
# Hidden Value 10 (manual flag)
```

## Phase 4: Update screen_stocks.py — Niwes Signal Tags
- [x] แก้ `projects/MaxMahon/scripts/screen_stocks.py` — REPLACE signal tags: ADD NIWES_5555 (ผ่านสูตรครบ), HIDDEN_VALUE (subsidiary listed > parent), QUALITY_DIVIDEND (yield 5%+ payout <70% streak 10ปี+), DEEP_VALUE (P/E ≤8 + P/BV ≤1), DIVIDEND_TRAP (rename จาก YIELD_TRAP). REMOVE COMPOUNDER, CASH_COW, TURNAROUND, CONTRARIAN. KEEP DATA_WARNING. — Scope: ห้ามแตะ filter/score. — Acceptance: function assign_signal_tags return Niwes tags only, รัน screen ตัวอย่างเห็น tags ใหม่

### Reference
```python
# current tags: YIELD_TRAP, DIVIDEND_KING, COMPOUNDER, CASH_COW, CONTRARIAN, TURNAROUND, DATA_WARNING

# new Niwes tags:
# - NIWES_5555 (passes 5-5-5-5 filter)
# - HIDDEN_VALUE (check_hidden_value > parent mcap)
# - QUALITY_DIVIDEND (yield>=5 + payout<70 + streak>=10)
# - DEEP_VALUE (P/E<=8 + P/BV<=1)
# - DIVIDEND_TRAP (yield>8 + ROE declining + payout>100)
# - DATA_WARNING (keep)
# REMOVED: COMPOUNDER, CASH_COW, CONTRARIAN, TURNAROUND, DIVIDEND_KING
```

## Phase 5: Update scan.py — Niwes prompt + Analysis Framework
- [x] แก้ `projects/MaxMahon/scripts/scan.py` — Read ทั้งไฟล์ก่อนแก้. REPLACE system prompt section ที่อ้าง Buffett+เซียนฮง ด้วย Niwes philosophy + verbatim quote ของ ดร.นิเวศน์ (≥3 quotes จาก projects/MaxMahon/docs/niwes/03-philosophy.md). REPLACE Analysis Framework 6 ด้านเดิม ด้วย Niwes-style: (1) Dividend Sustainability, (2) Hidden Value, (3) Business Quality (ขาดไม่ได้ของผู้บริโภค), (4) Valuation Discipline (P/E vs historical), (5) DCA Suitability (10-20 ปีไหม), (6) Macro Risk (sector concentration + structural Thai). — Scope: ห้ามแตะ user prompt (data section). — Acceptance: prompt ไม่มี Buffett/เซียนฮง references, มี ≥3 verbatim quotes ดร.นิเวศน์, รัน `cd projects/MaxMahon && py scripts/scan.py` ออก report ตาม 6 ด้านใหม่

## Phase 6: Update CLAUDE.md
- [x] แก้ `projects/MaxMahon/CLAUDE.md` — Read ทั้งไฟล์ก่อนแก้. UPDATE: Architecture Philosophy line (เป็น 'Dr.Niwes Way: VI ฉบับ ดร.นิเวศน์ — Dividend-First + Hidden Value + 5-5-5-5'), REPLACE Hard Filters table (5-5-5-5), REPLACE Quality Score table (Niwes weights), REPLACE Signal Tags table (Niwes tags), REPLACE Analysis Framework section (6 ด้าน Niwes). ADD section 'References' ลิงค์ไป `docs/niwes/00-index.md` + `docs/archive/README.md`. KEEP sections อื่น (Data Sources, Pipeline, Server, Key Files, Rules). — Acceptance: CLAUDE.md ไม่มี Buffett/เซียนฮง mentions (except archive link), มี Niwes framework ครบ, มี link ไป archive

### Reference
```markdown
# current Philosophy line:
- **Philosophy:** Dividend-First (passive income DCA) + Warren Buffett (quality) + เซียนฮง สถาพร (value growth)

# new:
- **Philosophy:** Dr.Niwes Way — VI ฉบับ ดร.นิเวศน์ เหมวชิรวรากร — Dividend-First + Hidden Value + สูตร 5-5-5-5 (yield≥5% / streak≥5ปี / 5หุ้น / 5sectors / ถือ≥5ปี) — บิดา VI ไทย
```

## Phase 7: End-to-end scan + baseline diff
- [x] รัน `cd projects/MaxMahon && py scripts/run_scan.py` รอบเดียว full pipeline (fetch + universe + screen + scan). เก็บ output report เป็น baseline `projects/MaxMahon/reports/baseline_niwes_v1_{date}.md`. ตรวจ: scan_*.md ใหม่ generate สำเร็จ + มี Niwes signal tags + analysis ตาม 6 ด้านใหม่ + Quality Score distribution กระจายใหม่ (top scorer = high dividend). ห้าม require 'top 5 picks' (Niwes filter strict อาจเหลือ <5 ตัว) — แค่ require 'มี analysis ออกมาตาม framework ใหม่' พอ. ถ้า zero stock pass filter → flag ใน task report 'threshold ต้องทบทวน' แต่ task ยังถือว่า PASS. — Acceptance: scan_*.md generate สำเร็จ, baseline_niwes_v1_{date}.md saved, ไม่มี Python crash
