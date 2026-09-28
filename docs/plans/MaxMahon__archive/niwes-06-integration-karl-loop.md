---
project: MaxMahon
created: 2026-04-20
last_updated: 2026-04-20
status: done
---

# Karl Integration Loop — Use → Compare → Learn → Adjust

> Part 6 of 8 — Index: niwes-master-index | Depends on: niwes-04-framework-migration, niwes-03-lesson-skill | Parallel-safe with: none — ปิด feedback loop: Karl run scan + เทียบ watchlist เก่า + เรียน lesson + adjust threshold ตาม findings — make sure framework ใช้ได้จริง ไม่ใช่ build แล้วทิ้ง

## Phase 1: Run Niwes Scan (post-migration)
- [x] รัน `cd projects/MaxMahon && py scripts/run_scan.py` รอบเดียว — เก็บ output ที่ `projects/MaxMahon/reports/integration_loop_scan_{date}.md`. ตรวจ: scan รัน complete, มี top picks ตาม Niwes filter, มี Quality Score breakdown, มี analysis 6 ด้าน. — Acceptance: report saved + ทุก section render ได้ + ไม่มี crash

## Phase 2: Compare with Karl Current Watchlist
- [x] อ่าน `projects/MaxMahon/user_data.json` ดึง watchlist เก่า. สำหรับแต่ละ symbol ใน watchlist: รัน scan single-stock (`py scripts/scan.py --symbol {sym}`) ดู Niwes signals + Quality Score. สร้าง `projects/MaxMahon/reports/integration_loop_watchlist_diff_{date}.md` — table: symbol / สถานะเดิม (ทำไมอยู่ใน watchlist) / Niwes verdict (PASS/FAIL filter) / Quality Score / Niwes Signal Tags / decision (KEEP/DROP/REVIEW). — Acceptance: ทุก symbol watchlist มี row + decision ชัด
- [x] Identify pattern: หุ้นที่ DROP ส่วนใหญ่ fail filter ไหน? (ถ้า 80% fail dividend streak → threshold strict ไป) บันทึกใน same file section 'Pattern Analysis'. — Acceptance: pattern analysis ระบุ threshold ที่อาจปรับ

## Phase 3: Karl เรียน L01-L05 (theoretical foundation)
- [x] Karl เรียน lesson: `/learn niwes` (default = L01 next). อ่าน + คุย + จด notebook lesson 01-05 จบ. ห้าม skip — ต้องเข้าใจ philosophy + criteria ก่อนตัดสินใจ adjust. — Acceptance: 5 ไฟล์ใน `projects/Investic/notebook/niwes/lesson-{01-05}-*.md` exist + แต่ละไฟล์มี 'ตกผลึก' section + Karl personal note

## Phase 4: Adjust Thresholds (data-driven)
- [x] Review pattern analysis (Phase 2) + lesson learnings (Phase 3) — ตัดสินใจ adjust threshold ใน `projects/MaxMahon/scripts/screen_stocks.py`: เช่น dividend streak 5→3 ปี ถ้าเข้มเกินหรือ payout sustainability threshold 70%→80%. ทุก adjustment ต้องมี justification (อ้างจาก lesson หรือ pattern analysis). บันทึก decision log ที่ `projects/MaxMahon/docs/niwes/13-threshold-adjustments.md`. — Acceptance: adjustment ใน screen_stocks.py + decision log แสดงเหตุผลแต่ละ change
- [x] รัน scan ใหม่หลัง adjust + diff กับ baseline (Phase 1): `diff projects/MaxMahon/reports/integration_loop_scan_{date}.md projects/MaxMahon/reports/integration_loop_scan_after_adjust_{date}.md` ดูว่า top picks เปลี่ยนยังไง. บันทึกใน 13-threshold-adjustments.md. — Acceptance: diff visible + impact analysis ใน decision log

## Phase 5: Document Learnings + Update CLAUDE.md
- [x] Update `projects/MaxMahon/CLAUDE.md` — Hard Filters table + Quality Score weights ให้ตรงกับ adjusted thresholds (ถ้ามี change). เพิ่ม link ไป `docs/niwes/13-threshold-adjustments.md` ใน References section — Acceptance: CLAUDE.md sync กับ code จริง
- [x] เพิ่ม pointer ใน Karl memory `~/.claude/projects/C--WORKSPACE/memory/MEMORY.md` Current Focus section — บันทึก completion: 'MaxMahon Niwes framework — calibrated to Karl portfolio ({date})'. — Acceptance: MEMORY.md +1 line
