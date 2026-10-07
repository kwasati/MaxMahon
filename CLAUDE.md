# Max Mahon

ชุดสคริปต์คัดหุ้นไทยแนวนิเวศน์ (Dividend-First) + จัดพอร์ต — Art ใช้ผ่านแชทกับ Claude (web + server เก็บแล้ว)

## Commands
- scan/refresh: `py C:\WORKSPACE\projects\4-MaxMahon\scripts\scan.py` (ตัวอื่นใน `scripts\` เรียกแบบเดียวกัน · ตั้ง `PYTHONUTF8=1` ก่อน)
- จัดพอร์ต: `py C:\WORKSPACE\projects\4-MaxMahon\scripts\rebalance.py --cash <Cash Balance> SYM=vol@market ...`
- เทสต์: `py -m pytest tests` หรือ `py -m unittest discover tests` (รันใน `C:\WORKSPACE\projects\4-MaxMahon` · ผ่านทั้งคู่ 9 เทสต์)
- smoke test: `py scripts\_smoke_*.py`

## Rules
- scan pipeline ต้อง deterministic ห้ามเอา AI มาตัดสินใจในสายนี้
- ห้ามแก้ Niwes scoring/ranking module จากโค้ด Hong Lens
- Art ส่งรูปพอร์ต + "จัดพอร์ต max mahon" → ทำตาม `C:\WORKSPACE\projects\4-MaxMahon\docs\portfolio-rebalance.md`
- `data\` `reports\` `config.json` `user_data.json` สคริปต์อ่าน/เขียนตอนรัน — ห้ามย้าย ห้ามเปลี่ยนชื่อ

## → ลูก
- `ROADMAP.md` — SSOT คิว + ข้อตกลง (เปิดก่อนวางแผน/ต่องาน) · `roadmap\` ใบของมัน
- `scripts\` — pipeline ทั้งชุด · `tests\` — เทสต์ของ `scripts\portfolio_*`
- `config.json` — schedule/filters/universe · `user_data.json` — watchlist/notes (scan อ่านตอนรัน)
- `data\` `reports\` — ข้อมูลรัน + รายงาน scan · `research\` — งานวิจัยรายตัว · `docs\` — เอกสาร
- `hong-lens\` — sub-project คัดหุ้นแนวเซียนฮง · เปิด `hong-lens\CLAUDE.md` ก่อนทำงานเรื่อง Hong Lens
- `CHANGELOG.md` — ตอน bump version · `README.md` — WHY/HOW/WHAT
- `_archive\2026-10\` — web + server + mockup + DESIGN.md + แผนเก่า (เปิดกลับ: `_archive\2026-10\README.md`)
