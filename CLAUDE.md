# Max Mahon

เอเจนต์คัดหุ้นไทยแนวนิเวศน์ (Dividend-First) — scan pipeline เป็นอัลกอริทึมล้วน AI เรียกเฉพาะตอน Art กดขอ

## Commands
- start server: `C:\WORKSPACE\projects\4-MaxMahon\max-server.bat` — **Art รันเอง ห้ามรันแทน**
- scan/refresh: `py scripts\<script>.py` (ตั้ง `PYTHONUTF8=1` ก่อน)
- smoke test: `py scripts\_smoke_*.py`

## Rules
- แก้ UI -> อ่าน `DESIGN.md` ก่อน · ใช้ `var(--xxx)` semantic token ห้าม hardcode hex/px ห้ามอ้าง primitive ตรง
- ทุก token ต้องมี dark counterpart · ทุก route ต้องมี `pages\{route}.js` + `pages\{route}.mobile.js`
- แก้ desktop แล้วต้องเช็ค `mobile.css` override ตาม — แยกชั้น ไม่ใช่ responsive ไฟล์เดียว
- scan pipeline ต้อง deterministic ห้ามเอา AI มาตัดสินใจในสายนี้
- ห้ามแก้ Niwes scoring/ranking module จากโค้ด Hong Lens
- Art ส่งรูปพอร์ต + "จัดพอร์ต max mahon" → ทำตาม `C:\WORKSPACE\projects\4-MaxMahon\docs\portfolio-rebalance.md`

## → ลูก
- `server\app.py` — FastAPI app (port 50089, https://max.intensivetrader.com)
- `scripts\` — pipeline ทั้งชุด (fetch_data, data_adapter, history_manager, anchor_scoring, case_study_detector, daily_price_refresh)
- `web\` — frontend v6 (desktop + mobile แยก module ต่อ route)
- `hong-lens\` — sub-project คัดหุ้นแนวเซียนฮง มี `CLAUDE.md` เอง
- `data\` `reports\` `research\` `docs\`
- `DESIGN.md` — token/typography/component spec + กฎเหล็ก
- `CHANGELOG.md`
- `hong-lens\CLAUDE.md` — ก่อนทำงานเรื่อง Hong Lens
