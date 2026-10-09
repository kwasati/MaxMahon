# Max Mahon

ชุดสคริปต์ช่วย Art ลงทุนหุ้นปันผลไทยแบบถือยาว — algo เตรียมข้อเท็จจริง คนตัดสิน · ใช้ผ่านแชทกับ Claude (web + server เลิกใช้ 2026-10-07 เก็บที่ `_archive/2026-10/`)

## WHY

- เป้า: "หุ้นปันผลดี ที่จะถือ 10-20 ปี" ปันผลเทียบต้นทุน 7–12% ต่อปีเมื่อถือไปหลายปี · ลงเงินแบบ DCA ซื้อทุกเดือนตลอด 10 ปี (ข้อตกลง F2 F4 ใน `roadmap/agreed-portfolio-framework.md`)
- พอร์ต 3 ส่วน: ขา Niwes 70 (หุ้นปันผลตามหลัก ดร.นิเวศน์) + ขาเซียนฮง 25 (หุ้นโต คัดด้วย Hong scanner) + เงินสด 5 — รายชื่อกับสัดส่วนอยู่ที่ `scripts/rebalance.py` ที่เดียว
- ขายกรณีเดียว = "ผิดทาง": หุ้นไม่ตรงเป้าแล้ว ปันผลลดลงเรื่อย ๆ (ข้อตกลง F3)
- เครื่องไม่ตัดสินแทนคน: ไม่มีคะแนนรวม ไม่มีคำสั่งซื้อขาย ทุกตัวเลขรันซ้ำได้ผลเดิม (ข้อตกลง N2 N3 · S1)

## HOW

สายงานจากกว้างไปแคบ:

1. **ดึงข้อมูล** — SETSMART (ราคา / yield / PE / PBV / มูลค่าบริษัท) + thaifin (งบย้อนหลัง 10–16 ปี) + set.or.th กับ yahoo (ปันผลรายปี รวมกันได้ 20 ปีขึ้นไป · ปีที่ยังจ่ายไม่ครบไม่เข้าฐานเทียบรายปี) — `data_adapter.py` `fetch_data.py` · รายละเอียดแหล่ง: `docs/data-sources-guide.md`
2. **ด่านคัดทั้งตลาด** (`screen_stocks.py` → `scan.py`) — ผ่านเมื่อ: มูลค่าบริษัท ≥5 พันล้าน และ (yield ≥5% หรือ yield 2–5% ที่ปันผลโต 3 ปีติดและคำนวณแล้วถึง 5% ของราคาวันนี้ใน 5 ปี) · PE / PBV / ปีขาดทุนไม่ตัดทิ้ง ออกเป็นธง · ผลคือรายชื่อที่ผ่าน + ทางที่ผ่าน + ธง ไม่มีอันดับคุณภาพ
3. **ใบข้อเท็จจริงต่อหุ้น** (`fact_sheet.py`) — ปันผลรายปี · ครั้งที่ลดและกี่ปีฟื้น · อัตราโต 4 ช่วงเวลา · ปันผลเทียบต้นทุน 3 ฉาก ทั้งแบบก้อนที่ถืออยู่และแบบ DCA · เงินสดเทียบปันผล · หนี้ · ประวัติ PE / PBV / yield ของตัวเอง + ป้ายราคาเทียบตัวเอง · ธงผิดทาง T1 T2 T4 T6
4. **deep dive รายตัว** (คน + Fable) — ตอบคำถาม D1–D18 ตามหลักนิเวศน์ แล้ว Art กับหัวเคาะ — ขั้นตอน: `docs/deep-dive.md`
5. **เฝ้าหุ้นที่ถือ** (`holdings_watch.py`) — ทุกตัวในพอร์ต แยกขา Niwes / เซียนฮง / นอกแผน · ขา Niwes ได้สถานะ เปิดทบทวน (ปันผลลด 2 ปีติด) / เฝ้า / ปกติ + ยอดรวมเทียบเป้า 7–12%
6. **จัดพอร์ต** (`rebalance.py`) — ใช้เงินสดส่วนที่เกินช่อง 5% ซื้อตัวที่ต่ำกว่าเป้า ไม่ขายตัวเกินเป้า — ขั้นตอน: `docs/portfolio-rebalance.md`

ขาเซียนฮงคัดด้วย `hong_stage1_scanner.py` แยกขาดจากสายข้างบน — ดู `hong-lens/CLAUDE.md`

เกณฑ์ไหนมาจากคำ ดร.นิเวศน์ เกณฑ์ไหนเราตั้งเอง: `docs/niwes-principles.md` (ทุกข้อมีแหล่ง + ป้าย) · ทำไมระบบเป็นรูปนี้: `docs/review-2026-10/system-gap.md`

## WHAT

```
scripts/             # 14 ไฟล์ — ดึงข้อมูล: data_adapter fetch_data set_official_adapter setsmart_adapter update_universe flake_queue
                     #          สแกน: screen_stocks scan report_template history_manager
                     #          รายตัว / พอร์ต: fact_sheet holdings_watch rebalance · ขาเซียนฮง: hong_stage1_scanner
tests/               # pytest — 1 ไฟล์ต่อกลุ่ม ไม่ยิงเน็ต
config.json          # filters (ด่าน) · fact_sheet (เกณฑ์ใบข้อเท็จจริง) · holdings (นอกแผน + ต้นทุนเฉลี่ย)
user_data.json       # watchlist + blacklist + notes
docs/                # niwes-principles.md (หลัก) · deep-dive.md · portfolio-rebalance.md (ขั้นตอน) · data-sources-guide.md
                     # niwes/ (ฐานค้นคว้า ดร.นิเวศน์) · review-2026-10/ (ผล review ระบบ)
research/            # deep dive ขา Niwes + TISCO (<sym>-deep-dive-<วันที่>.md) + ผล Hong scanner
hong-lens/           # sub-project คัดหุ้นแนวเซียนฮง
reports/             # ผลรัน: scan_*.md · facts/ · holdings/
data/                # cache + screener + history (gitignored)
roadmap/ ROADMAP.md  # คิวงาน + ข้อตกลงที่ล็อก
_archive/2026-10/    # web / server / สคริปต์ / เอกสารที่เลิกใช้
```

คำสั่งทั้งหมดอยู่ใน `CLAUDE.md` · ตั้ง `PYTHONUTF8=1` ก่อนรัน · API key โหลดจาก `C:/WORKSPACE/.env` · ไม่มีตัวตั้งเวลา รันเมื่อจะใช้ (ข้อตกลง N7)

## Changelog

[CHANGELOG.md](CHANGELOG.md) — version ล่าสุด **v7.0.0** (2026-10-09)
