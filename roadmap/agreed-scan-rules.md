# ข้อตกลง: กฎ scan
ใบของ `C:\WORKSPACE\projects\4-MaxMahon\ROADMAP.md` · สร้าง 2026-10-07

## ข้อตกลงที่ล็อก (รหัส · ข้อความ · วันที่ + คำ Art)
ไม่มีวันที่ในไฟล์เดิม · คัดตัวอักษรเดิม · ต้นทางก่อนแก้ 2026-10-07
- S1 scan pipeline ต้อง deterministic ห้ามเอา AI มาตัดสินใจในสายนี้ — เดิม `C:\WORKSPACE\projects\4-MaxMahon\CLAUDE.md` บรรทัด 14
- S2 ห้ามแก้ Niwes scoring/ranking module จากโค้ด Hong Lens — เดิม `C:\WORKSPACE\projects\4-MaxMahon\CLAUDE.md` บรรทัด 15
- S3 **ห้ามแก้ Niwes scoring/ranking module** — Hong scanner ต้อง standalone — `C:\WORKSPACE\projects\4-MaxMahon\hong-lens\CLAUDE.md` บรรทัด 10
- S4 **ปรัชญา:** pure deterministic — ไม่มี LLM ตัดสินแทน user, ไม่มี ML black box. ทุก tag + คะแนน **reproducible 100%** ถ้าข้อมูลเดิม. Claude SDK ใช้เฉพาะตอน user กด "วิเคราะห์เพิ่ม" ต่อตัว (cache 7 วัน) — `C:\WORKSPACE\projects\4-MaxMahon\README.md` บรรทัด 100
