# Hong Lens

Sub-project ใน MaxMahon — คัดหุ้นไทยแนวเซียนฮง (Hybrid Value/Growth) สำหรับพอร์ตส่วน 25%

## Stack
Python · ยืม data layer ของ MaxMahon มาสแกน · scanner standalone ตัวเดียว

## Layout
- `C:\WORKSPACE\projects\4-MaxMahon\scripts\hong_stage1_scanner.py` — scanner ทั้งหมดอยู่ที่นี่
- `research\` — บันทึกและผลคัด
- `set-companyprofiles\` `set-factsheets\` — เอกสาร SET ที่ใช้ audit
- `MEMORY.md` — รายชื่อหุ้นที่ผ่าน/ตก พร้อมเหตุผล

## Commands
- `py C:\WORKSPACE\projects\4-MaxMahon\scripts\hong_stage1_scanner.py` — stage 1 auto scan
- stage 2 = manual review คุยกับ Art ในแชท ไม่มีสคริปต์

## Rules
- **ห้ามแก้ Niwes scoring/ranking module** — Hong scanner ต้อง standalone
- ข้อมูล MaxMahon เชื่อ 100% ไม่ได้ — audit กับเอกสาร SET จริงก่อนสรุปทุกครั้ง
- ห้ามเดา ถ้าข้อมูลไม่ครบให้บอกว่าไม่ครบ
- เป้าคือหา pattern ตรงสไตล์ ไม่ใช่ลอกพอร์ตเซียนฮงตรง ๆ

## Read first
- `MEMORY.md` — รายชื่อปัจจุบันและเหตุผล
- `C:\WORKSPACE\projects\4-MaxMahon\CLAUDE.md` — กฎของโปรเจกต์แม่
