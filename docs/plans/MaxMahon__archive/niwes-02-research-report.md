---
project: MaxMahon
created: 2026-04-20
last_updated: 2026-04-20
status: done
---

# ดร.นิเวศน์ — Deep Research Report (with Verbatim Quote Rule)

> Part 2 of 8 — Index: niwes-master-index | Depends on: rename-master-index (paths อ้าง projects/MaxMahon/) | Parallel-safe with: niwes-01 — deep research 12 ไฟล์ ครอบ biography/philosophy/criteria/portfolio/case studies/current/views — บังคับ verbatim quote + URL verify ป้องกัน hallucination

## Phase 1: Source Collection + URL Verify
- [x] สร้าง `projects/MaxMahon/docs/niwes/00-sources.md` — ใช้ Agent (researcher subagent_type) ค้น sources ภาษาไทย: บทสัมภาษณ์ (kaohoon, prachachat, thestandard, finnomena, bangkokbiznews, longtunman, thunhoon, mgronline, posttoday, thansettakij), บทความที่ ดร.นิเวศน์ เขียนเอง (Investment Forum, ThaiVI), หนังสือ (ตีแตก, VI ฉบับเซียน, เซียนหุ้นมือทอง), รายการ TV (Money Talk, Stock Action, Bottom Line). แต่ละ source ต้อง: (1) URL ที่ access ได้, (2) วันที่, (3) สรุปสั้น 1-2 บรรทัด, (4) ทำ WebFetch HEAD verify ว่า URL ยังเปิดได้ — ระบุ HTTP status. ถ้า fetch fail → ลบจาก list หรือ flag 'archive only'. — Acceptance: ≥30 sources, ≥80% มี HTTP 200 verified, format ตาม template
- [x] สร้าง rule file `projects/MaxMahon/docs/niwes/00-research-rules.md` — บังคับ rule สำหรับทุก task ในเฟสถัดไป: (1) ทุก quote ต้อง verbatim — ห้าม paraphrase, (2) ทุก quote ต้องมี source URL + วันที่ + ผู้สัมภาษณ์ ติดข้างหลัง, (3) ห้าม invent quote ฟังเหมือน ดร.นิเวศน์, (4) ถ้าไม่มี quote จริงสำหรับ statement → ใส่ 'paraphrase from {URL}' ชัดเจน, (5) ถ้าไม่มั่นใจ statement → flag '[VERIFY]' ใน text — Acceptance: rule file exists + ทุก task Phase 2-5 reference rule นี้

### Reference
```markdown
# 00-sources.md template
## บทสัมภาษณ์
- [Title — ชื่อสื่อ — วันที่](URL) — HTTP {status} — สรุปสั้น 1-2 บรรทัด

## หนังสือ
- ชื่อหนังสือ — ปีพิมพ์ — สำนักพิมพ์ — สรุป
```

## Phase 2: Biography + Investment Journey
- [x] สร้าง `projects/MaxMahon/docs/niwes/01-biography.md` — ประวัติเต็ม: เกิด, การศึกษา, อาชีพก่อน VI, เหตุการณ์ปลดออก 2540, จุดเริ่มลงทุน, milestone — เน้น human-side. ทุก quote verbatim ตาม 00-research-rules.md. ทุกย่อหน้ามี source citation. — Acceptance: ≥800 คำ, มี timeline, มี ≥10 source citations, 0 [VERIFY] flags (clean facts)
- [x] สร้าง `projects/MaxMahon/docs/niwes/02-investment-journey.md` — Timeline พอร์ตตามปี 2540→2568 ครบทุกจุดเปลี่ยนสำคัญ ≥10 events. ตั้งบริษัท ตีแตก จำกัด ปี 2567 (เปลี่ยน allocation 60%→30% ไทย). ทุก milestone มี quote หรือ source. — Acceptance: timeline ครบ + ทุก event มี source

## Phase 3: Philosophy + Frameworks
- [x] สร้าง `projects/MaxMahon/docs/niwes/03-philosophy.md` — แก่นความคิด ≥6 ปรัชญาหลัก (ซื้อธุรกิจ, ปันผลคำตอบสุดท้าย, ถือยาว, safety first, downside before upside, mental models). แต่ละข้อมี verbatim quote + เปรียบเทียบ Graham/Buffett/Niwes. — Acceptance: ≥6 ปรัชญา + ทุกข้อมี ≥1 verbatim quote
- [x] สร้าง `projects/MaxMahon/docs/niwes/04-criteria.md` — เกณฑ์ครบ: สูตร 5-5-5-5 ฉบับเต็ม, P/E target 7-8x, P/BV<1, dividend yield ≥5% normalized, payout sustainable, ROE consistent, no loss 5y, hidden asset, moat, daily-use business. แต่ละเกณฑ์ + quote + ตัวอย่างหุ้นที่ผ่าน. — Acceptance: ≥10 เกณฑ์ + ทุกข้อมีตัวอย่างหุ้น
- [x] สร้าง `projects/MaxMahon/docs/niwes/05-portfolio-construction.md` — Asset allocation 30-30-30-10, จำนวนหุ้น 5-10 concentrated, position sizing tier, sector mix. — Acceptance: allocation logic ครบ + position sizing rules

## Phase 4: Case Studies (5 cases)
- [x] สร้าง `projects/MaxMahon/docs/niwes/06-case-cpall.md` — CPALL: 22.5M หุ้น เม.ย.2551 ที่ 236M, stock dividend 1:1 → 45M หุ้น ปัจจุบัน ~2,081M, ปันผลปี 67 = 60.75M, ถือ 17 ปี — entry+thesis+holding+lessons + verbatim quotes — Acceptance: case ครบทุก dimension + ≥3 quotes
- [x] สร้าง `projects/MaxMahon/docs/niwes/07-case-tcap.md` — TCAP: เข้ามี.ค.2557 ราคา 35.18, PE 7-8x + PBV<1 + dividend ~5% — Acceptance: case ครบ + hidden value (TMB stake) อธิบาย
- [x] สร้าง `projects/MaxMahon/docs/niwes/08-case-qh.md` — QH: hidden value (HMPRO 19.87% > QH market cap) — เป็น mental model หลัก — Acceptance: คำนวณตัวเลขจริง + อธิบายเข้าใจง่าย
- [x] สร้าง `projects/MaxMahon/docs/niwes/09-case-or-exit.md` — OR: ถือ 244,298,900 หุ้น (2.04%) ~7,756M → ขายหมด ก.ย.2564-มี.ค.2565 — เหตุผล thesis change — Acceptance: ครบ entry+exit reasoning + lesson
- [x] สร้าง `projects/MaxMahon/docs/niwes/10-case-vietnam-fpt.md` — Vietnam pivot + ตีแตก จำกัด + FPT >40% พอร์ต VN — Acceptance: thesis + entry strategy ครบ

## Phase 5: Current State + Recent Views
- [x] สร้าง `projects/MaxMahon/docs/niwes/11-current-portfolio.md` — พอร์ตล่าสุด ต้นปี 2568: CPALL/TCAP/QH/BCP/MC/BCPG ไทย, FPT/MWG/ACV/VRE/REE VN, DR + กองทุน global. ตารางครบ symbol/holder/shares/%/value/sector/period + source — Acceptance: ตารางครบ + source per row
- [x] สร้าง `projects/MaxMahon/docs/niwes/12-recent-views-2025-2026.md` — มุมมองตลาด 2025/2026 ≥8 quote สำคัญ + บริบท + เหตุผลปรับ allocation — Acceptance: ≥8 verbatim quotes + บริบทแต่ละ

## Phase 6: Index + Cross-references
- [x] สร้าง `projects/MaxMahon/docs/niwes/00-index.md` — TOC + คำอธิบาย + Quick Start (อ่านลำดับนี้) + 'For MaxMahon framework' (ไฟล์ไหนไป implement). ตรวจ link ทุกอันใช้ relative path ใช้ได้. — Acceptance: TOC ครบทุกไฟล์ + ทุก link clickable
