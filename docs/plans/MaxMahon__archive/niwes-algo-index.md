---
project: MaxMahon
created: 2026-04-21
last_updated: 2026-04-21
status: done
---

# Niwes Algo Framework — Build Order Index

> Part 0 of 6 — Index/build order สำหรับแกะ Niwes เป็น deterministic algo: pure algo scan pipeline + case study detectors + moat tags + 3-tier thresholds + exit baseline + history v2 + UI port + safety/completeness gaps. เปิดไฟล์นี้ก่อน build เสมอ | Depends on: none | Parallel-safe with: none

## Phase 1: Foundation — Screener (no deps)
- [x] /build niwes-algo-01-screener — data pipeline enrichment (price_avg per year, holding_mcap) + case study detectors (5 patterns) + moat tags + 3-tier hard_filter (PASS/REVIEW/FAIL) + exit baseline save/load — scope: ไม่แตะ scan.py / server / UI — MVP checkpoint: หลัง Phase 1-3 ของ plan 01 ทำเสร็จ = สามารถรัน screener แบบ deterministic + return 3 bucket แล้ว (exit baseline เป็น Phase 4 add-on feature) — Acceptance: ทุก task ใน 01 ผ่าน, screener_{date}.json มี candidates/review_candidates/filtered_out_stocks + scoring_version=v2

### Reference
# Foundation layer — ทุก plan หลังจากนี้ consume output ของ 01
# MVP checkpoint: 01 Phase 1-3 = usable screener | Phase 4 = exit feature add-on (optional for MVP)

## Phase 2: Scan Engine (รอ 01 merge)
- [x] /build niwes-algo-02-scan-engine — kill Claude dependency ใน scan.py + template-based markdown report generator + history v2 schema + migration script — scope: ไม่แตะ server/UI — Acceptance: scan pipeline run ได้ไม่มี Claude call, reports/scan_{date}.md produced ตาม template (6 sections), history.json v2 schema

### Reference
# 02 consumes screener format ใหม่ — ต้องรอ 01 merge

## Phase 3: Server + UI (parallel-safe หลัง 02 merge)
- [x] /build niwes-algo-03-server — extract analysis helpers + split analysis endpoint (GET cache-only + POST trigger, keep 3-perspective schema) + history v2 API + patterns API + exit-status API + price-history endpoint — scope: ไม่แตะ scan pipeline / UI — Acceptance: endpoints return JSON ถูก schema, curl test ผ่าน
- [x] /build niwes-algo-04-ui — extend web/ UI: score breakdown + price history + yield trend charts + dividend history table + watchlist exit status + case study/moat tags + on-demand Claude button (target existing #analysis-section) + history v2 display ใน #history-list — scope: ไม่แตะ backend/scan — Acceptance: detail panel render ครบ, on-demand button work, ไม่มี auto Claude call ตอนเปิด detail

### Reference
# 03 + 04 parallel ได้เพราะแตะไฟล์คนละกลุ่ม (server/app.py vs web/*)
# ทั้งคู่ต้องรอ 02 merge เพราะ consume scan output format ใหม่

## Phase 4: Gaps — Safety + Completeness + Features (รอ 03+04 merge)
- [x] /build niwes-algo-05-gaps — rethinking gaps: delisted-safe fetch + yfinance auto_adjust=False + 3 patterns เพิ่ม (UTILITY/HOSPITAL/F&B) + VN pattern disable + sector spread ใน report + REVIEW UI tab + Claude cache TTL 7d + Telegram exit alert (Karl Notify bot) + transactions+P&L endpoints+UI + integration test (curated 10 symbols + benchmark <5min) — scope: polish + safety pass ทั้ง stack — Acceptance: integration test pass 6/6 tag assertions, Telegram alert ทำงาน, REVIEW tab แสดง review_candidates, P&L endpoint compute ถูก

### Reference
# 05 = final polish — fix gaps ที่ rethinking พบ (5 MUST + 6 SHOULD)

## Phase 5: Wrap-up
- [x] อัพเดท projects/MaxMahon/CLAUDE.md — Architecture section เปลี่ยน 'AI: Weekly pipeline + discovery ใช้ SDK' เป็น 'AI: on-demand only (Karl trigger จาก UI หลังเห็น algo output); scan pipeline = pure deterministic algo'; เพิ่ม reference ถึง case_study_patterns.json + exit_baselines.json + history v2 schema + transactions schema + telegram_alert.py; อัพเดท Analysis Framework section ให้สะท้อน case study pattern + moat tags + 8 patterns (7 active + 1 disabled VN); scoring_version = niwes-dividend-first-v2 — scope: แก้เฉพาะ CLAUDE.md root — Acceptance: diff แสดง AI pipeline description เปลี่ยน + ref file paths ใหม่ครบ

### Reference
# projects/MaxMahon/CLAUDE.md — current line 6:
# - AI: Weekly pipeline + discovery ใช้ SDK + prompt caching

# new:
# - AI: On-demand only — scan pipeline = pure deterministic algo (Niwes framework แกะเป็น Python rules).
#   Claude SDK ใช้เฉพาะเมื่อ Karl กดขอ 'วิเคราะห์เพิ่มเติม' ใน UI ต่อหุ้น 1 ตัว (POST /api/stock/{sym}/analyze)
#   cache TTL 7 วัน — auth ผ่าน MAX_ANTHROPIC_API_KEY
