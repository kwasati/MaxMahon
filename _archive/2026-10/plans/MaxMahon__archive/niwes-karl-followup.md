---
project: MaxMahon
created: 2026-04-20
last_updated: 2026-04-21
status: done
---

# Niwes Followup — Karl Action Items

> หลัง niwes v3 build เสร็จ 8 plans — Karl ต้องทำ human-in-loop tasks: เรียน L01-L05, review watchlist findings, approve threshold adjustments, verify manual items. Plan นี้เป็น roadmap กัน Karl ลืม — อ่านเรียงลำดับแล้ว check ทีละข้อ

## Phase 1: เรียน Niwes Foundation (L01-L05)
- [ ] เรียน Lesson 01 — Biography + Philosophy: รัน `/learn niwes` ใน chat (default = next = L01). คุยตกผลึกกับ Karl agent จนจบบท. จบแล้วมี `projects/Investic/notebook/niwes/lesson-01-biography-philosophy.md` updated with 'ตกผลึก' section + Karl personal note. — Acceptance: ไฟล์ lesson-01 มี section 'ตกผลึก' + 'Karl personal note' ที่ Karl เขียนเอง (ไม่ใช่ของเดิม template)
- [ ] เรียน Lesson 02 — Investment Journey 1997-2026: `/learn niwes` (ตัวถัดไป). Timeline ทุกจุดเปลี่ยน + ตั้งบริษัทตีแตก. — Acceptance: lesson-02-investment-journey.md exists + มี personal note
- [ ] เรียน Lesson 03 — สูตร 5-5-5-5 ฉบับเต็ม: `/learn niwes`. เข้าใจทุก '5' + ตัวอย่างหุ้นที่ผ่าน. — Acceptance: lesson-03-5555-formula.md exists + personal note + Karl ตอบได้ว่าทำไม 5 ปี streak, ไม่ใช่ 3
- [ ] เรียน Lesson 04 — Hidden Asset Mental Model: `/learn niwes`. เคส QH ถือ HMPRO > market cap. — Acceptance: lesson-04-hidden-asset.md exists + personal note + Karl คิด hidden value model ได้เอง 1-2 หุ้นไทย
- [ ] เรียน Lesson 05 — Case CPALL (ถือ 17 ปี): `/learn niwes`. entry 2551 + stock dividend + ทำไมไม่ขาย. — Acceptance: lesson-05-case-cpall.md exists + personal note + Karl สามารถอธิบายได้ว่าทำไม ดร.นิเวศน์ไม่ขาย CPALL แม้ราคาลด

## Phase 2: Review Watchlist Findings
- [ ] อ่าน `projects/MaxMahon/reports/integration_loop_watchlist_diff_2026-04-20.md` — watchlist 15 ตัว 87% fail Niwes. ทำความเข้าใจว่าทำไม: P/BV>1.5 (92%), P/E>15 (69%), Yield<5% (69%). — Scope: ห้าม delete watchlist — แค่อ่าน + เข้าใจ. — Acceptance: Karl ตอบได้ว่า watchlist ปัจจุบันตรง Niwes แค่ไหน + ตัวไหนใน watchlist ควร DROP
- [ ] อ่าน `projects/MaxMahon/reports/integration_loop_scan_2026-04-20.md` — top picks Niwes scan. ตัวไหนผ่าน 5-5-5-5. — Acceptance: Karl รู้ top 5-10 หุ้น Niwes candidate + เทียบกับ watchlist เห็นความต่าง
- [ ] อ่าน `projects/MaxMahon/reports/integration_loop_karl_todo_2026-04-20.md` — summary + Karl's next steps จาก agent view. — Acceptance: Karl เข้าใจ next steps workflow ทั้งหมด

## Phase 3: Approve + Apply Threshold Adjustments
- [ ] เปิด `projects/MaxMahon/docs/niwes/13-threshold-adjustments.md` — 5 recommendations PENDING review. สำหรับแต่ละ adjustment: กรอก field 'Lesson justification' (อ้างจาก L01-L05 ที่เพิ่งเรียน) + mark APPROVED/REJECTED. — Scope: ห้าม auto-edit screen_stocks.py. — Acceptance: ทุก 5 adjustments มี Lesson justification filled + status APPROVED หรือ REJECTED (ไม่มี PENDING)
- [ ] ถ้ามี adjustment APPROVED → สั่ง agent แก้ threshold ใน `projects/MaxMahon/scripts/screen_stocks.py` (prompt agent โดยบอก decision log 13-threshold-adjustments.md). แก้เสร็จ → commit per adjustment. — Acceptance: screen_stocks.py มี threshold ใหม่ตาม approved adjustments + commit message อ้าง 13-threshold-adjustments.md entry
- [ ] รัน scan ใหม่หลัง adjust: `cd projects/MaxMahon && py scripts/run_scan.py` (หรือ curated subset). Save เป็น `projects/MaxMahon/reports/integration_loop_scan_after_adjust_{YYYY-MM-DD}.md`. Diff กับ baseline. บันทึก impact analysis ใน 13-threshold-adjustments.md section 'Post-adjust impact'. — Acceptance: diff report + impact analysis ระบุชัดว่า top picks เปลี่ยนยังไง

## Phase 4: Manual Verify Tasks (agents flag)
- [ ] Verify news scraper CSS selectors: เปิด `projects/MaxMahon/scripts/monitor_niwes_news.py` — 4/5 sites return 0 (kaohoon, prachachat, thestandard, longtunman). เปิด browser → devtools → หา selector ที่ถูก → patch script → test รัน. — Scope: แก้แค่ scraper, ไม่แตะ diff/alert. — Acceptance: รัน script รอบเดียว → ≥5 items จาก 2+ sites
- [ ] Verify 6 rd.go.th PDFs flagged `[VERIFY]` ใน `projects/MaxMahon/docs/foreign-investment/04-tax-comprehensive.md`: ดาวน์โหลด PDF ผ่าน Adobe Reader → copy Thai text → update doc ลบ `[VERIFY]` flag. PDFs ที่ต้องดู: ป.161/2566 ฉบับเต็ม + DTA US full + ภงด.95 form + มาตรา 50(2)(จ) raw + 40(4)(ข) raw + 42(17). — Acceptance: 04-tax-comprehensive.md มี 0 [VERIFY] flags (หรือ ≤3 ที่ verify ไม่ได้จริงๆ)
- [ ] Verify KKPS Vietnam direct service: โทร 02-680-2222 (KKPS helpdesk) ถามว่าเปิดบัญชี VN ตรงได้ไหม + fee structure. Update `projects/MaxMahon/docs/foreign-investment/02-vietnam-direct.md` section broker comparison ลบ [VERIFY] flag. — Acceptance: doc update + ลบ [VERIFY] flag สำหรับ KKPS
- [ ] Verify Foreign SET holdings % source: หา free API หรือ SET data page ที่ให้ foreign holding trend (monthly/weekly). ถ้าหาเจอ → patch `projects/MaxMahon/scripts/monitor_thai_macro.py` function `fetch_foreign_set_holdings()` จาก placeholder เป็น real fetch. — Acceptance: script return real data (not manual_update_needed)

## Phase 5: First Real Niwes Buy (Karl proves the framework)
- [ ] เลือก top 3 candidates จาก post-adjust scan + pass Karl's sanity check (Niwes rules อ่านจริงจาก L01-L05, ไม่ใช่แค่ number filter). บันทึก decision ที่ `projects/MaxMahon/docs/niwes/20-karl-first-buys.md` — สำหรับแต่ละตัว: ทำไมเลือก, entry price target, DCA plan, exit conditions (reference 15-exit-rules.md). — Acceptance: ไฟล์มี 3 candidates + rationale ≥5 บรรทัด/ตัว + DCA plan เฉพาะ
- [ ] Simulate buy 1 หุ้น (paper trade หรือ real ขนาดเล็ก ≤10K) ตัวแรก. Track เข้า user_data.json watchlist + note. — Acceptance: watchlist มี entry ใหม่ + note บันทึก entry date/price/rationale
- [ ] Update `~/.claude/projects/C--WORKSPACE/memory/MEMORY.md` Current Focus section: เปลี่ยน 'Max Mahon — AI analysis API + Buffett/เซียนฮง checklist split (uncommitted)' เป็น 'MaxMahon — Niwes framework live + Karl calibrated + first buys simulated ({date})'. — Acceptance: MEMORY.md line updated
