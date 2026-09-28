---
project: MaxMahon
created: 2026-04-23
last_updated: 2026-04-23
status: done
---

# MaxMahon Next Milestone — Master Plan

> Orchestrator plan สำหรับ 3 deliverables ถัดไปของ MaxMahon (หลัง data refactor thaifin-hard-primary เสร็จ): (01) QC fix ระบบคัดหุ้น — แก้ 2 critical bugs ที่ dead bucket 10 คะแนน + case_study rule coverage / (02) Feature จัดพอร์ตสไตล์แมกซ์ — backend Niwes composite + 80/20 weight + portfolio-builder page / (03) UI port — เอา Robinhood muted sage tokens จาก mockup ไปแทน vintage newspaper tokens + redesign 6 pages. Build order บังคับ sequential เพราะ (02) ใช้ scoring ที่แก้แล้วจาก (01), (03) ใช้ page endpoint จาก (02)

## Phase 1: QC Correctness (no deps)
- [x] /build maxmahon-next-01-qc-fix — แก้ payout sustainability dead bucket + case_study detector rule coverage + dead near_miss param + D/E null safety

## Phase 2: Portfolio Builder Feature (depends 01)
- [x] /build maxmahon-next-02-portfolio-builder — สร้าง feature จัดพอร์ตสไตล์แมกซ์ backend (API endpoint + Niwes composite + 80/20 allocation + override) + new /portfolio-builder page ใช้ scoring ที่แก้ถูกแล้วจาก plan 01

## Phase 3: UI Port (depends 02)
- [x] /build maxmahon-next-03-ui-port — port Robinhood muted sage tokens เป็น production tokens.css/base.css/mobile.css + redesign 6 existing pages (home/report/watchlist/portfolio/simulator/settings) + wire portfolio-builder page ให้ใช้ design system ใหม่
