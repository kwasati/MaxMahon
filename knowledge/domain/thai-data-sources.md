# เลือกที่ดึงข้อมูลหุ้นไทย (เว็บไหนเปิดได้ / ใช้อะไรแทน)
ใบของ `C:\WORKSPACE\projects\4-MaxMahon\knowledge\knowledge-index.md` · สร้าง 2026-10-15 · ทุกข้อบอกชนิด: **กฎ** (Art สั่ง/เคาะ ต้องทำตาม) หรือ **ข้อค้นพบ** (ผลจากรายงาน ไม่ผูกมัดการใช้จริง) · ไม่มีคำ Art รองรับ → ข้อค้นพบ

### TD-1 เว็บที่ fetcher ใช้ไม่ได้ + ทางแทน
- ชนิด: ข้อค้นพบ
- เนื้อ: kaohoon / Bangkok Post / prachachat ตอบ 403/402 · set.or.th / settrade โหลดด้วย JS อ่านตัวเลขไม่ได้ · bangkokbank.com timeout 60 วิทุก URL → งบรายไตรมาสใช้ yfinance `quarterly_income_stmt / balance_sheet / cashflow` (ตรงกับ MD&A ทุกตัวที่เทียบ) · PDF ของ IR ใช้ curl + pypdf (ดู `C:\WORKSPACE\_shared\knowledge\code\web-fetch-pdf.md`)
- ทำไม: เสียรอบ fetch ซ้ำหลายสิบครั้ง
- ที่มา: กล่อง MaxMahon (ย่อยกล่องจด 2026-10-15)
- ใช้เมื่อ: project:maxmahon
- คำจับ: 403 · timeout · settrade

### TD-2 yahooquery ไม่รับ trailing ทุกงบ
- ชนิด: ข้อค้นพบ
- เนื้อ: `trailing=` ใช้ได้กับ `income_statement()` เท่านั้น `balance_sheet()` / `cash_flow()` ไม่รับ
- ทำไม: script ล้มเมื่อส่ง trailing
- ที่มา: กล่อง MaxMahon (ย่อยกล่องจด 2026-10-15)
- ใช้เมื่อ: project:maxmahon
- คำจับ: yahooquery · trailing
