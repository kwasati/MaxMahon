---
project: 4-MaxMahon
created: 2026-05-18
last_updated: 2026-05-18
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: เปิดไฟล์ index นี้ -> รู้ build order ของ Plan 01 + 02 + Test Gate 3 -> เริ่ม /build ตามลำดับได้ทันที (ไม่ต้องเดา)

### รายละเอียด
- 2 sub-plans sequential build order: 01 aggregates + tags -> 02 scoring + scan
- Plan 01 = block Plan 02 (Plan 02 ใช้ aggregates + tags ที่ Plan 01 produce)
- Plan 02 จบที่ TEST GATE 3 = รัน standalone scan 932 หุ้น เห็น TOP anchor candidates ตาม anchor model v1.0
- ทุก implementation work ใน submodule projects/4-MaxMahon
- เก็บ existing pillar-based 100pts scoring คู่ขนาน (ไม่ replace) ระหว่าง transition — กัน break frontend
- Plan 02 standalone scan script (scan_anchor.py) = independent CLI ไม่กระทบ existing scan.py / quality_score / report.js / server endpoint
- spec source = docs/scoring-anchor-spec.md v1.0 (DEFAULT_SCORING_CONFIG dict + Calculation order)
- Phase 1 infra (filter-01/02/03/07) DONE 2026-05-18 — data quality stable พร้อม implement scoring

### Scope Boundary
**In scope:**
- .claude/plans/4-MaxMahon/anchor-scoring-index.md (this file)
- .claude/plans/4-MaxMahon/anchor-scoring-01-aggregates-tags.md
- .claude/plans/4-MaxMahon/anchor-scoring-02-core-sector-scan.md
- Build order documentation + test gate definition

**Out of scope:**
- Implementation code (อยู่ใน sub-plans)
- Spec content (อยู่ใน docs/scoring-anchor-spec.md v1.0)
- Future plan: replace existing pillar-based pipeline + UI/API rewrite (deferred ทำหลัง standalone scan validate spec แล้ว)

### Non-goals
- ไม่ implement code ใน index นี้ - แค่ orchestrate build order
- ไม่ replace existing scoring pipeline (deferred to future plan)
- ไม่ retroactive — sub-plans build fresh on top of current scan output
- ไม่ break backward compat กับ existing frontend (parallel co-exist ระหว่าง transition)

# Anchor Scoring Implementation — Master Index

> Master index ของ Anchor Scoring v1.0 implementation — 2 sub-plans sequential + Test Gate 3 standalone scan. Plan 01 (aggregates + tags) -> Plan 02 (scoring + sector + scan) ตาม spec v1.0

## Phase 1: Build order — Sequential
- [x] /build anchor-scoring-01-aggregates-tags — extend _build_aggregates 21 missing fields + assign Stage 1-6 tags ใน screen_stocks.py — scope: ไม่แตะ existing quality_score/assign_signals — Acceptance: fetch_multi_year(sym) returns aggregates dict ที่มี 21 fields ใหม่ + screener output ทุก PASS หุ้น มี anchor_stage_tags ครบ Stage 2-5
- [x] /build anchor-scoring-02-core-sector-scan — anchor_scoring.py compute module + sector_taxonomy.py + scan_anchor.py standalone CLI script — scope: ไม่ replace existing scan.py / quality_score — Acceptance: รัน py scripts/scan_anchor.py แล้วได้ reports/anchor_scan_YYYY-MM-DD.md ที่ TOP candidates per anchor band (0-100 internal / display 0.0-10.0)
- [x] TEST GATE 3 — Anchor Scan Validation — รัน scan_anchor.py บน 932 universe + verify Niwes invariants: หุ้น DIVIDEND_SHRINKING/MOAT_ERODING/CASHFLOW_DETERIORATING ติด disqualify ได้ถูก + 5 หุ้น sample (PTT/SCC/CPALL/ADVANC/BDMS) คะแนนใกล้เคียง Phase 6 verify ของ spec — Acceptance: scan output stable + 5 หุ้น sample anchor score ตรง expectation ของ spec Phase 6 (PTT/SCC/CPALL = 0 / ADVANC ~57 / BDMS ~52)

### Reference
Reference docs:
- spec source: `C:\WORKSPACE\projects\4-MaxMahon\docs\scoring-anchor-spec.md` v1.0 (TOC + DEFAULT_SCORING_CONFIG dict + Calculation order)
- parent design: `C:\WORKSPACE\.claude\plans\4-MaxMahon\niwes-refactor-v2-design.md` Stage 1-6 FINAL tag rules
- master index: `C:\WORKSPACE\.claude\plans\4-MaxMahon\maxmahon-index.md` (this implementation = Phase 3)
- latest scan: `C:\WORKSPACE\projects\4-MaxMahon\data\screener_2026-05-18.json` (932 stocks fresh data)

Gap analysis 2026-05-18:
- 21 aggregate fields missing (88% of spec requirement)
- Stage 1-6 tags ยัง assign ไม่ครบใน screen_stocks.py
- See sub-plans for granular task breakdown
