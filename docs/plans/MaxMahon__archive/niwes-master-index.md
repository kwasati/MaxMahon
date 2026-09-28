---
project: MaxMahon
created: 2026-04-20
last_updated: 2026-04-20
status: done
---

# Niwes Master Plan v3 — Index

> Master index 8 sub-plans — ดร.นิเวศน์ เป็น role model 100% สำหรับ MaxMahon + Karl. Build sequential foundation → parallel build → integration. รัน rename-master-index ก่อนเสมอ (paths ทั้งหมดอ้าง projects/MaxMahon/)

## Phase 1: Foundation (sequential, must complete before Phase 2)
- [x] /build niwes-01-data-adapter-readiness — verify + extend MaxMahon data adapter รองรับ Niwes (normalized earnings, payout sustainability, hidden value flag) + backtest framework — Acceptance: backtest_niwes.py ทำงาน + 5-5-5-5 portfolio 10 ปี return คำนวณได้
- [x] /build niwes-02-research-report — deep research ดร.นิเวศน์ → projects/MaxMahon/docs/niwes/ พร้อม verbatim quote rule + WebFetch verify — Acceptance: 12+ ไฟล์ + 00-index.md เปิดได้ + ทุก quote มี URL

## Phase 2: Build framework + lesson + howto (parallel-safe)
- [x] /build niwes-03-lesson-skill — lesson 17 บท + Niwes mode ใน learn skill + reference memory (Investic project) — Acceptance: /learn niwes ใช้งานได้ + lesson 01 + L15-17 hands-on พร้อม
- [x] /build niwes-04-framework-migration — replace Buffett+เซียนฮง ด้วย Niwes 100% (atomic split: filters → score → tags → prompt → CLAUDE.md → e2e) — Acceptance: scan รอบใหม่ generate report Niwes signals + diff vs baseline
- [x] /build niwes-05-foreign-stock-howto — DR/VN/US/Tax/Holding (WebFetch raw legal text + DR list authoritative) — Acceptance: 7 ไฟล์ + Karl roadmap + ทุก legal claim มี source

## Phase 3: Integration + advanced (sequential after Phase 2)
- [x] /build niwes-06-integration-karl-loop — Karl run scan + เทียบ watchlist + เรียน L01-L05 + adjust threshold — Acceptance: Karl decision document + adjusted thresholds committed
- [x] /build niwes-07-monitoring-update — cron ดึงข่าว ดร.นิเวศน์ + diff alert + Telegram notify — Acceptance: cron รัน weekly + alert ส่ง Telegram เมื่อพอร์ตเปลี่ยน
- [x] /build niwes-08-exit-strategy — sell rules + structural risk monitor + exit decision template — Acceptance: exit_signal detection ใน screener + structural risk indicator pull จาก macro source
