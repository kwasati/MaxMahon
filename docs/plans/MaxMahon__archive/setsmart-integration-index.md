---
project: MaxMahon
created: 2026-04-27
last_updated: 2026-04-27
status: done
---

## Target / Goal
ทำได้: รัน `py scripts/_verify_dps_fix.py` ได้ METCO/BBL/QH/SAT yield ตรง SET ภายใน ±0.1% (ไม่ใช่ ±1% เหมือน heuristic) เพราะอ่านจาก SETSMART ตรง — heuristic FY attribution กลายเป็น layer รอง

# SETSMART Integration — Index

> Master plan ของการ wire SETSMART API เป็น primary source of truth ใน MaxMahon. แตก 2 sub-plan: 01-adapter สร้าง standalone wrapper + cache + smoke test (ทดสอบ rate limit + package coverage), 02-wire-pipeline ผูก SETSMART เข้า fetch_fundamentals + daily_price_refresh + re-verify 4 หุ้น. ทำตามลำดับ — Plan 02 depends on Plan 01.

## Phase 1: Foundation (sequential)
- [x] /build .claude/plans/MaxMahon/setsmart-integration-01-adapter.md — สร้าง SETSMART adapter module + cache layer + smoke test ที่ดึงข้อมูล 4 หุ้น verify + bulk EOD + bulk Financial + รายงาน package coverage (กี่ปี). — Acceptance: รัน `py scripts/setsmart_adapter.py` smoke test ผ่าน + cache file ที่ data/setsmart_cache/ สร้างถูก + console output ระบุ package start year (history coverage)

## Phase 2: Wire Pipeline (depends on Phase 1)
- [x] /build .claude/plans/MaxMahon/setsmart-integration-02-wire-pipeline.md — Wire SETSMART เข้า fetch_fundamentals (primary) + แก้ daily_price_refresh ใช้ SETSMART EOD bulk แทน yahooquery batch + re-verify 4 หุ้น. — Acceptance: รัน `_verify_dps_fix.py` แล้ว METCO/BBL/QH/SAT yield ตรง SET ±0.1% + watchlist + daily refresh + scan ไม่ broken
