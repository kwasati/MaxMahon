# จัดพอร์ต Max Mahon (pillar 1 หุ้นปันผล)

Art ส่งรูปหน้า Portfolio จากแอปโบรก + พิมพ์ "จัดพอร์ต max mahon" → ทำตามนี้ ไม่ต้องถาม

## ขั้นตอน
1. อ่านจากรูป: Symbol / Avail Vol / Market (ราคา) ทุกแถว + Cash Balance
2. รัน (ตั้ง `PYTHONUTF8=1`): `py C:\WORKSPACE\projects\4-MaxMahon\scripts\rebalance.py --cash <Cash Balance> SYM=vol@market ...` ใส่ทุกตัวในรูป
3. ตอบ Art: ตารางซื้อ (หุ้น / ตอนนี้→เป้า / ซื้อกี่หุ้น / ใช้เงิน) + เงินสดเหลือ + ตัวนอกแผน 1 บรรทัด
4. Art มีหลายพอร์ต — รูปแต่ละรอบอาจเป็นคนละพอร์ต · ห้ามเทียบกับรอบก่อน/snapshot แล้วทักว่าผิดปกติ จัดตามรูปที่ส่งมาอย่างเดียว

## กติกา
- เป้า + วิธีคิดอยู่ใน `scripts\rebalance.py` (TARGETS) — แก้เป้าที่นั่นที่เดียว
- เติมแค่ตัวที่ต่ำกว่าเป้า · ตัวเกินเป้าไม่ขาย · เงินไม่พอ → เกลี่ยตามยอดที่ขาด · ปัดลงทีละ 100 หุ้น
- นอกแผน (TISCO legacy, LALIN ฯลฯ) ไม่นับฐาน ไม่เติม · TISCO หยุดเติม ปล่อยเจือจางเอง
- บทบาทหุ้นวัดจากทิศที่เติม: AMATA = ตัวหลัก (ไม่ใช่ TISCO ถึงจะใหญ่)
- การเงินกระจุก (BBL+TCAP+TISCO) = Art ตั้งใจ ไม่ต้องเสนอแก้
- AI คำนวณให้ Art ตัดสินเอง · ไม่สั่งขาย/ซื้อนอกกรอบนี้

## ที่มา
- snapshot + projection: `C:\WORKSPACE\projects\4-MaxMahon\research\portfolio-snapshot-2026-07-20.md`
- กรอบ 70/25/5: `C:\WORKSPACE\projects\4-MaxMahon\research\_portfolio_70-25-5_framework_2026-05-20.md`
