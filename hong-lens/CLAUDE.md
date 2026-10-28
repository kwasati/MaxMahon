# Hong Lens

Sub-project ใน MaxMahon — คัดหุ้นไทยแนวเซียนฮง (Hybrid Value/Growth) สำหรับพอร์ตส่วน 25%

## Commands
- `py C:\WORKSPACE\projects\4-MaxMahon\scripts\hong_stage1_scanner.py --version v5 --universe all` — stage 1 auto scan (ไม่ใส่ flag = รุ่น v2 + SET100 เท่านั้น) · อ่านจาก `data\screener_cache\<วันล่าสุด>\` อย่างเดียว ไม่ยิงเน็ต ราว 1 วินาที → รันสแกนทั้งตลาดของ project แม่ก่อนถ้าจะเอาข้อมูลวันนี้ · ผลออกที่ `research\hong-v5-scan-<วันที่>.md` + `.csv`
- stage 2 = manual review คุยกับ Art ในแชท ไม่มีสคริปต์

## Rules
- **ห้ามแก้ module ฝั่ง Niwes** (ด่านคัด / ใบข้อเท็จจริง / ตัวเฝ้าหุ้น) — Hong scanner ต้อง standalone
- หุ้นขานี้ไม่ใช้ด่านและธงแบบนิเวศน์ (ข้อตกลง N9 ใน `C:\WORKSPACE\projects\4-MaxMahon\roadmap\agreed-selection-system.md`)
- คะแนน PEG แก้ทิศแล้ว 2026-10-09 (ต่ำ = ดี ตาม spec growth/PE ≥ 1.5) — ผลที่ใช้อันดับได้ = `C:\WORKSPACE\projects\4-MaxMahon\research\hong-v5-scan-2026-10-09.md` (ผู้รอด 29 ตัว) · ผลรอบสูตรกลับด้านเก็บที่ `C:\WORKSPACE\projects\4-MaxMahon\_archive\2026-10\research\hong-v5-rerun.md`
- deep dive หุ้นที่ถือ 4 ตัว (TOA SISB SECURE MOSHI) รอบล่าสุด = `research\_deep_<SYM>_2026-10-09.md` · ตารางค่าใน `research\_master_hong-lens_2026-05-21.md` อัปเดตถึง 2026-10-09 เฉพาะตาราง 4 ตัว ส่วนอื่นของไฟล์ยังเป็นค่า พ.ค. 2026
- scanner คิด PEG จากกำไรโตปีเดียวล่าสุด แต่ spec กับ deep dive ใช้โตทบ 3 ปี — ยังไม่แก้ รอ Art เคาะ (หุ้นที่โตชะลอปีล่าสุดจะได้คะแนน PEG ต่ำกว่าที่ spec ให้) → อ่านอันดับคู่กับ PEG 2 แบบเสมอ
- ข้อมูล MaxMahon เชื่อ 100% ไม่ได้ — audit กับเอกสาร SET จริงก่อนสรุปทุกครั้ง
- ห้ามเดา ถ้าข้อมูลไม่ครบให้บอกว่าไม่ครบ
- เป้าคือหา pattern ตรงสไตล์ ไม่ใช่ลอกพอร์ตเซียนฮงตรง ๆ

## → ลูก
- `C:\WORKSPACE\projects\4-MaxMahon\scripts\hong_stage1_scanner.py` — scanner ทั้งหมดอยู่ที่นี่
- `research\` — บันทึกและผลคัด · ผู้สมัครแทน SISB SECURE (SWC PSP KCG) + ชุดขาใหม่ที่เสนอ = `research\hong-candidates-2026-10-28.md` (deep dive `research\_deep_<SYM>_2026-10-28.md`)
- `set-companyprofiles\` `set-factsheets\` — เอกสาร SET ที่ใช้ audit
- `C:\WORKSPACE\projects\4-MaxMahon\CLAUDE.md` — กฎของโปรเจกต์แม่
