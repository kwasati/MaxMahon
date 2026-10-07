---
project: 4-MaxMahon
created: 2026-05-18
last_updated: 2026-05-18
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: เปิด MaxMahon web -> เห็นคะแนน anchor 0.0-10.0 (4 ด้าน) แทน score เก่า 100 pts (5 pillar) + ทุก scan output ใหม่ใช้ anchor algo + ลบ scan เก่าหมด

### รายละเอียด
- 3 sub-plans sequential: 01 backend (pipeline + API) -> 02 frontend (4 JS + CSS) -> 03 cleanup-rescan (delete old + fresh scan + TEST GATE 4)
- Plan 01 = Python only (no UI risk) — pipeline replace quality_score + 2 API endpoints
- Plan 02 = frontend update (4 JS files + CSS) — needs user visual verify
- Plan 03 = ops (delete old screener_*.json + reports/scan_*.md + history.json migration + fresh scan + verify)
- Backward compat: NO — replace_dont_layer rule, ของเก่า quality_score หายจาก pipeline + UI
- User data preserve: data/users/{uid}/user_data.json (watchlist, blacklist, transactions) — DO NOT touch
- Cache preserve: data/setsmart_cache, data/price_cache — keep (not score-related)
- history.json migration: keep entries (user-facing history) but update score field to anchor — handle migration in Plan 03
- exit_baselines.json: stores score field — may need migration or rebuild on fresh scan (handle in Plan 03)
- TEST GATE 4 = run fresh universe scan + verify web display + score values match anchor model
- UI changes need user visual verify (per /build skill rule) — Plan 02 ends with 'อาร์ทเปิดเว็บดู' checkpoint

### Scope Boundary
**In scope:**
- .claude/plans/4-MaxMahon/anchor-refactor-index.md (this file)
- .claude/plans/4-MaxMahon/anchor-refactor-01-backend.md
- .claude/plans/4-MaxMahon/anchor-refactor-02-frontend.md
- .claude/plans/4-MaxMahon/anchor-refactor-03-cleanup-rescan.md

**Out of scope:**
- Implementation code (อยู่ใน sub-plans)
- User data files (preserve)
- Cache files (preserve)

### Non-goals
- ไม่ implement code ใน index นี้ - แค่ orchestrate
- ไม่ keep backward compat กับ pillar score (replace entirely)
- ไม่ refactor anchor_scoring.py / scan_anchor.py / sector_taxonomy.py — Plan 02 ของ anchor scoring เสร็จแล้ว เก็บ as-is
- ไม่ migrate user transactions (preserve)

# Anchor Scoring Refactor — Pipeline + UI/API + Fresh Scan

> Master index ของ Anchor Refactor — เปลี่ยน MaxMahon production pipeline + UI ใช้ anchor scoring v1.0 แทน pillar score เก่า. 3 sub-plans sequential + TEST GATE 4

## Phase 1: Build order — Sequential
- [x] /build anchor-refactor-01-backend — replace quality_score in pipeline + update 2 API endpoints. Scope: ไม่แตะ frontend — Acceptance: รัน screen_stocks.py แล้วได้ screener_*.json schema ใหม่ (anchor score + display + 4 ด้าน breakdown) + curl /api/screener return new schema
- [x] /build anchor-refactor-02-frontend — update 4 JS pages (home + report desktop+mobile) + CSS layout. Scope: ไม่แตะ Python — Acceptance: เปิด web/v6 page เห็น display 0.0-10.0 + 4-pillar chart (อาร์ทเปิดเว็บ verify)
- [x] /build anchor-refactor-03-cleanup-rescan — delete old scan data + rerun fresh universe scan + migrate history.json + TEST GATE 4. Acceptance: data/screener_*.json + reports/scan_*.md ลบเก่าหมด + fresh screener_YYYY-MM-DD.json ใช้ anchor schema + web เปิดดูได้ + history.json migrate complete

### Reference
Reference docs:
- spec: `C:\WORKSPACE\projects\4-MaxMahon\docs\scoring-anchor-spec.md` v1.0
- anchor module ready: `scripts/anchor_scoring.py` (compute_anchor_score function)
- standalone scan ref: `scripts/scan_anchor.py` (Plan 02 anchor scoring)
- assign_anchor_stage_tags: in `scripts/screen_stocks.py` already integrated
- Master parent: `niwes-refactor-v2-design.md` (Stage 1-6 tag rules)
