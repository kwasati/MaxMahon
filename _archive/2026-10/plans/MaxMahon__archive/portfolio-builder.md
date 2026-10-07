---
project: MaxMahon
created: 2026-04-18
last_updated: 2026-04-21
status: done
---

# Portfolio Builder — Normalize + Correlation

> ยกระดับ Max จาก analyst รายตัว → portfolio manager โดยใช้ Normalize เปรียบเทียบการเติบโต + Correlation คัดคู่กระจายความเสี่ยง (idea จากบทเรียน Investic EP6 Multi-Asset Comparison) — ยังไม่เริ่ม implement เก็บเป็น backlog ไว้

## Phase 1: Concept & Design (Backlog)
- [ ] วางแนวทาง Normalize engine — ดึงราคาย้อนหลังของหุ้นที่ผ่าน checklist แล้ว rebase ทุกตัวให้เริ่มที่ 100 เทียบกับ SET benchmark เพื่อเห็นว่าตัวไหนโตกว่าตลาด
- [ ] วางแนวทาง Correlation matrix — คำนวณ correlation ของทุกคู่ในกลุ่มหุ้นที่ผ่าน checklist ย้อน 1-3 ปี หาคู่ที่ correlation ต่ำ (กระจายความเสี่ยงได้จริง)
- [ ] ออกแบบ UI แสดง normalize chart หลายตัวบนกราฟเดียว + correlation heatmap/table ให้ user เห็นภาพรวม
- [ ] กำหนด logic portfolio recommendation — คัดหุ้นที่ (1) ผ่าน checklist (2) โตกว่า SET (3) correlation ต่ำระหว่างกัน = พอร์ตที่โตดี + กระจายความเสี่ยงจริงไม่หลอกตัวเอง
- [ ] เชื่อม Max กับแนวคิด 'เส้นทับกัน = หลอกตัวเอง' — เตือน user เมื่อเลือกหุ้นที่ correlation สูงเกิน 0.9 ว่า 'ซื้อตัวเดียวก็พอ ไม่ต้องซ้ำซ้อน'

### Reference
อ้างอิง: projects/Investic/notebook/lesson-07-multi-asset-comparison.md (จะสร้างหลังจบ lesson) — หลักการ Normalize + Correlation จาก Investic EP6. Prerequisite: ต้องเรียน Investic ให้จบ Series 1 ก่อน แล้วค่อยกลับมาทำอันนี้
