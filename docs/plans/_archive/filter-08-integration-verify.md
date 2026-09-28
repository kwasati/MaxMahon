---
project: 4-MaxMahon
created: 2026-05-12
last_updated: 2026-05-12
status: active
---

## Target / Goal

### เป้าหมาย
ทำได้: หลัง Plan A-G เสร็จ → รัน weekly scan + daily refresh + simulate flake → ทุก pipeline ทำงานร่วมกันถูกต้อง + manual verify 10 หุ้น ผ่านเกณฑ์ Niwes จริง

### รายละเอียด
- Smoke test ครบ pipeline: weekly scan, daily price refresh, daily refilter, flake retry queue
- Manual verify 10 หุ้น (BBL, PTT, CPALL, KBANK, SCB, ADVANC, TTW, BTS, GLOBAL, CPN) — ดูว่า filter status ตรงกับเกณฑ์ Niwes 5-5-5-5
- Performance check: scan 933 หุ้นจบใน < 30 นาที + yahoo API calls ลด > 50% เทียบก่อน migration
- Data integrity check: zero crash + zero duplicate entry + zero stale candidate

### Scope Boundary
**In scope:**
- End-to-end smoke test ทั้ง pipeline
- Manual verify 10 หุ้น vs Niwes 5-5-5-5 standard
- Performance + data integrity report

**Out of scope:**
- แก้ bug ที่เจอใน Plan A-G (ถ้าเจอ → handoff /bugfix หรือ /plan ใหม่)
- Code changes (Plan H verify only — ไม่แก้ code)

### Non-goals
- ไม่ implement feature ใหม่
- ไม่ refactor code ที่ A-G ทำ
- ไม่ tune scoring algorithm (layer 2)

# Plan H — Integration Verify (End-to-End After 7 Plans)

> Part 8 of 8 — Integration verify. End-to-end test หลัง 7 plan เสร็จ + manual verify 10 หุ้น vs Niwes standard.
> Depends on: filter-01..07 (ทุก plan ต้องเสร็จ)
> Parallel-safe with: none (last phase)

## Phase 1: Weekly scan end-to-end
- [ ] รัน py scripts/scan.py (full 933 symbols) + วัดเวลา + watch log — Acceptance: scan complete < 30 นาที + zero unhandled exception + screener_*.json มี candidates + review_candidates (empty backward compat) + pending_candidates (อาจมีถ้า yahoo flake) + filtered_out_stocks + status_change_log (empty for first scan)
- [ ] Verify schema: py -c 'import json; from pathlib import Path; d=json.loads(sorted(Path("data").glob("screener_*.json"))[-1].read_text()); print(list(d.keys()))' — Acceptance: keys รวม candidates, review_candidates, pending_candidates, filtered_out_stocks, summary, counts, scoring_version='niwes-dividend-first-v2'

### Reference
Verify commands:
```bash
cd C:\WORKSPACE\projects\4-MaxMahon
time py scripts/scan.py
# Expected: < 30 min, zero exception
```

## Phase 2: Daily refresh + refilter + flake retry
- [ ] รัน py scripts/daily_price_refresh.py manual — Acceptance: log แสดง 4 stage sequential: 'EOD refresh complete' + 'flake retry complete' + 'refilter complete' + 'cache write complete'
- [ ] Verify SETSMART financial cache: ls data/setsmart_cache/financial_by_symbol_*.json | wc -l — Acceptance: count ≥ จำนวน symbols ใน latest screener candidates
- [ ] Simulate flake: add 1 symbol to data/flake_queue.json → trigger daily_price_refresh → Acceptance: symbol ถูก retry + ถ้า yahoo working = ลบจาก queue + push to candidates, ถ้า yahoo flake จริง = retry_count เพิ่ม

### Reference
Verify commands:
```bash
py scripts/daily_price_refresh.py
ls data/setsmart_cache/financial_by_symbol_*.json | wc -l
```

## Phase 3: Manual verify 10 หุ้น vs Niwes 5-5-5-5
- [ ] เปิด screener_*.json + manual verify 10 หุ้น (BBL, PTT, CPALL, KBANK, SCB, ADVANC, TTW, BTS, GLOBAL, CPN) — ดูว่า filter_status (PASS/REVIEW/PENDING/FAIL) ตรงกับเกณฑ์ Niwes 5-5-5-5 ที่ user เข้าใจ + score 100 reasonable — Acceptance: 10/10 หุ้น filter_status ตรงกับ manual expectation ของ user (อาร์ทดูเองแล้ว approve)
- [ ] Visual verify mobile + desktop: เปิด http://localhost:50089/ + http://localhost:50089/m → home page → ดู filter chips + candidate cards + status_change badges + pending section ทำงานครบ — Acceptance: ทุก UI element render ครบ (อาร์ทดูเองแล้ว approve)

### Reference
10 หุ้นตัวอย่าง (sector ต่างกัน):
- BBL (Banking)
- PTT (Energy)
- CPALL (Retail)
- KBANK (Banking)
- SCB (Banking)
- ADVANC (Telecom)
- TTW (Utilities)
- BTS (Transport)
- GLOBAL (Retail)
- CPN (Property)

## Phase 4: Performance + data integrity report
- [ ] เก็บสถิติ: yahoo API call count (per scan) ก่อน vs หลัง migration — Acceptance: ลด > 50% (เทียบ baseline ก่อน Plan B)
- [ ] Data integrity check: grep -c 'fail_reasons' scripts/*.log + tail -100 logs — Acceptance: zero unhandled exception + zero hardcoded value ที่ควรมาจาก config
- [ ] เขียน report สรุปสั้นที่ data/research/plan_filter_complete_report.md — สรุป: bug ที่แก้ + improvement ที่เพิ่ม + performance gain + known issue (ถ้ามี) — Acceptance: report file มี + readable

### Reference
Report template:
```markdown
# Plan filter-* Integration Report

## Bug Fixed (12)
- year-completeness (4 ตัวนับ)
- config externalize
- dividend logic swap
- ...

## Improvement Added (2)
- daily refilter
- flake retry queue

## Performance
- scan time: X min (เทียบ baseline Y min)
- yahoo API calls: -N% 

## Known Issues
- ...
```
