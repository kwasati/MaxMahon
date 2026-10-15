# Max Mahon

ชุดสคริปต์คัดหุ้นไทยแนวนิเวศน์ (Dividend-First) + จัดพอร์ต — Art ใช้ผ่านแชทกับ Claude (web + server เก็บแล้ว)

## Commands
- สแกนทั้งตลาด (2 ขั้น · ตั้ง `PYTHONUTF8=1` · ไม่มีตัวตั้งเวลา รันเมื่อจะใช้ · ราว 9 นาที · รีเฟรชราคาทั้งตลาดเองก่อนสแกน ปิดด้วย `--no-refresh` · `--fresh` ดึงข้อมูลใหม่ไม่ใช้ cache ของวัน ราว 60 นาที): `py C:\WORKSPACE\projects\4-MaxMahon\scripts\screen_stocks.py` → `data\screener_<วันที่>.json` แล้ว `py C:\WORKSPACE\projects\4-MaxMahon\scripts\scan.py` → `reports\scan_<วันที่>.md` · ผลบอกแค่ผ่านด่านทางไหน + ธง ไม่มีคะแนน
- สแกนบางตัว ไม่แตะ `data\` `reports\`: `screen_stocks.py --symbols A,B,C --out-dir <dir>` แล้ว `scan.py --screener <ไฟล์> --out-dir <dir>`
- จัดพอร์ต: `py C:\WORKSPACE\projects\4-MaxMahon\scripts\rebalance.py --cash <Cash Balance> SYM=vol@market ...`
- ใบข้อเท็จจริงต่อหุ้น (แทนคะแนน 0–100 · ไม่มีคะแนนรวม ไม่ตัดสินแทนคน · ปันผลเทียบต้นทุนมี 2 มุม: ก้อนที่ถืออยู่ + ซื้อทุกเดือนแบบ DCA): `py C:\WORKSPACE\projects\4-MaxMahon\scripts\fact_sheet.py <SYM> [--cost SYM=ราคา] [--out <dir>]` → ค่าเริ่ม `reports\facts\`
- เฝ้าหุ้นที่ถือ (รายชื่อ + ขาจาก TARGETS / LEGS ใน `rebalance.py` · นอกแผน + ต้นทุนเฉลี่ยใน `config.json` ท่อน `holdings` · ขา Niwes ได้สถานะ เปิดทบทวน / เฝ้า / ปกติ + ยอดรวมเทียบเป้า 7–12% · ขาเซียนฮงไม่ใช้เกณฑ์นิเวศน์): `py C:\WORKSPACE\projects\4-MaxMahon\scripts\holdings_watch.py [--cost SYM=ราคา] [--refresh] [--out <dir>]` → ค่าเริ่ม `reports\holdings\` · `--refresh` ดึงราคาล่าสุดเฉพาะหุ้นที่ถือ (ใช้กับ `fact_sheet.py` ได้ด้วย) — ไม่มีตัวตั้งเวลา รันเมื่อจะใช้
- เทสต์: `py -m pytest tests` (รันใน `C:\WORKSPACE\projects\4-MaxMahon` · ตั้ง `PYTHONUTF8=1` · ผ่าน 146 เทสต์ — ข้อมูลปันผล `tests\test_dividend_data.py` · ด่านคัด `tests\test_gate.py` · ใบข้อเท็จจริง `tests\test_fact_sheet.py` · เฝ้าหุ้นที่ถือ `tests\test_holdings_watch.py` · ผลสแกน `tests\test_scan_output.py` · จัดพอร์ต `tests\test_rebalance.py` · Hong PEG `tests\test_hong_peg.py`)

## Rules
- scan pipeline ต้อง deterministic ห้ามเอา AI มาตัดสินใจในสายนี้
- ห้ามแก้ module ฝั่ง Niwes (ด่านคัด / ใบข้อเท็จจริง) จากโค้ด Hong Lens
- ไม่มีคะแนน 0–100 แล้ว (ถอด 2026-10-09) — algo ทำแค่ด่านคัด + ใบข้อเท็จจริง + ธง · คะแนน / คำตัดสินเป็นของ Art กับหัวหลัง deep dive ตามแม่แบบ D1–D18 ใน `C:\WORKSPACE\projects\4-MaxMahon\docs\niwes-principles.md`
- หลักนิเวศน์ที่ใช้อ้างได้ = `C:\WORKSPACE\projects\4-MaxMahon\docs\niwes-principles.md` (ทุกข้อมีแหล่ง + ป้ายว่าพูดจริงหรือเราตั้งเอง) — ไฟล์ใน `docs\niwes\` ที่ติดป้าย ⛔ ห้ามอ้างเป็นคำนิเวศน์
- Art ส่งรูปพอร์ต + "จัดพอร์ต max mahon" → ทำตาม `C:\WORKSPACE\projects\4-MaxMahon\docs\portfolio-rebalance.md`
- Art สั่ง deep dive หุ้น → ทำตาม `C:\WORKSPACE\projects\4-MaxMahon\docs\deep-dive.md` (Fable · คิด 2 มุม: ก้อนที่ถืออยู่ + DCA ทุกเดือน 10 ปี)
- `data\` `reports\` `config.json` `user_data.json` สคริปต์อ่าน/เขียนตอนรัน — ห้ามย้าย ห้ามเปลี่ยนชื่อ

## → ลูก
- `ROADMAP.md` — SSOT คิว + ข้อตกลง (เปิดก่อนวางแผน/ต่องาน) · `roadmap\` ใบของมัน
- `C:\WORKSPACE\projects\4-MaxMahon\knowledge\knowledge-index.md` — กับดักข้อมูลที่เจอแล้ว (ตรวจตัวเลขข้ามแหล่ง · เว็บที่ดึงได้ · อัตราโตหลอก) เปิดเฉพาะใบที่งานแตะ
- `scripts\` — 14 ไฟล์: ดึงข้อมูล (`data_adapter` `fetch_data` `set_official_adapter` `setsmart_adapter` `update_universe` `flake_queue`) · สแกน (`screen_stocks` `scan` `report_template` `history_manager`) · รายตัว / พอร์ต (`fact_sheet` `holdings_watch` `rebalance`) · `hong_stage1_scanner` · `tests\` — เทสต์ของทุกกลุ่ม
- `config.json` — filters (ด่าน) / fact_sheet (เกณฑ์ใบข้อเท็จจริง) / special_dividends (ปันผลพิเศษที่ไม่นับเป็นปันผลปกติ) / holdings (นอกแผน + ต้นทุนเฉลี่ย + growth_scenarios = อัตราปันผลโต 3 ฉากจาก deep dive ใช้แทนกฎตายตัว) · `user_data.json` — watchlist/notes (scan อ่านตอนรัน)
- `data\` `reports\` — ข้อมูลรัน + รายงาน scan · `research\` — deep dive ขา Niwes + TISCO (`<sym>-deep-dive-2026-10-09.md` ของ AMATA BBL TCAP TISCO) + ผล Hong scanner (`hong-v5-scan-<วันที่>`) · deep dive ขาเซียนฮงอยู่ `hong-lens\research\` · `docs\` — เอกสาร · `docs\review-2026-10\` — ผล review ระบบ + ตารางช่องว่าง (ที่มาของรูปปัจจุบัน)
- `hong-lens\` — sub-project คัดหุ้นแนวเซียนฮง · เปิด `hong-lens\CLAUDE.md` ก่อนทำงานเรื่อง Hong Lens
- `CHANGELOG.md` — ตอน bump version · `README.md` — WHY/HOW/WHAT
- `_archive\2026-10\` — web + server + mockup + DESIGN.md + แผนเก่า + สคริปต์กับเอกสารที่เลิกใช้ 2026-10-09 (คะแนนเดิม / กฎขายเดิม / จัดพอร์ตชุด server / ของใช้ครั้งเดียว / งานวิจัยรายตัวรุ่น พ.ค. 2026 / ภาพพอร์ตเก่า) (เปิดกลับ: `_archive\2026-10\README.md`)
