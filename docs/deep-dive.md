# deep dive หุ้นรายตัว (ขา Niwes)

Art สั่ง deep dive หุ้นตัวหนึ่ง → ทำตามนี้ · คำถามที่ต้องตอบ: "ถือและซื้อตัวนี้ต่อทุกเดือนอีก 10 ปี มาถูกทางไหม"

## ขั้นตอน
1. ออกใบข้อเท็จจริง (ตั้ง `PYTHONUTF8=1`): `py C:\WORKSPACE\projects\4-MaxMahon\scripts\fact_sheet.py <SYM> --refresh --cost <SYM>=<ต้นทุนเฉลี่ย>` — ต้นทุนของหุ้นที่ถืออยู่ใน `config.json` ท่อน `holdings`
2. ส่งงานให้ Fable (ข้อตกลง N10) ตอบคำถาม D1–D18 ใน `C:\WORKSPACE\projects\4-MaxMahon\docs\niwes-principles.md` ท่อน 5 + ตัววัด T1–T6 ท่อน 4 · ต้นแบบรูปเล่ม 10 ท่อน: `C:\WORKSPACE\projects\4-MaxMahon\research\amata-deep-dive-2026-10-09.md`
3. ผลวางที่ `research\<sym>-deep-dive-<yyyy-mm-dd>.md` · ของเก่าของหุ้นตัวเดียวกันย้ายเข้า `_archive\<yyyy-mm>\research\`
4. หัวใส่ผลของ deep dive กลับเข้าระบบใน `config.json`: อัตราปันผลโต 3 ฉาก → `holdings.growth_scenarios` (ต้องมี `source` ชี้ท่อนในไฟล์ + `as_of`) · ปันผลพิเศษที่เจอ → `special_dividends` — ใบข้อเท็จจริงกับตัวเฝ้าหุ้นจะใช้ค่านี้แทนกฎตายตัว
5. หัวสรุปให้ Art: คำตอบ 1 หน้า + ตารางปันผลเทียบต้นทุน 2 มุม + รายการที่ต้องตัดสิน → Art กับหัวเคาะคะแนน / ทางไป (ข้อตกลง N2 N3)

## กติกา
- ตัวเลขและคำพูดทุกตัวมีแหล่ง + วันที่ · ยังไม่พิสูจน์ขึ้นต้นว่า `เดา:` · หาไม่ได้เขียนว่าหาไม่ได้
- อ้างคำ ดร.นิเวศน์ ได้เฉพาะที่มีใน `docs\niwes-principles.md` หรือมีแหล่งที่เปิดได้
- ราคาย้อนหลังใช้ราคาปิดจริง ไม่ใช่ราคาปรับปันผล (deep dive AMATA รอบแรกพลาดจุดนี้ สรุปว่าราคาแพงผิด)
- โอกาสถึงเป้า 7–12% คิด 2 มุมเสมอ: ก้อนที่ถืออยู่ (ต้นทุนคงที่) กับเงิน DCA ที่ซื้อทุกเดือน 10 ปี (ข้อตกลง F4) + ทดสอบ DCA กับราคาและปันผลจริงย้อนหลัง
- อัตราปันผลโตที่ฐานเป็นปีผิดปกติ (โควิด / ปันผลพิเศษ) ห้ามใช้เป็นอัตราปกติ
- ไม่สั่งซื้อ / ขาย (ข้อตกลง R6) · ขาเซียนฮงไม่ใช้แม่แบบนี้ (ข้อตกลง N9) → `C:\WORKSPACE\projects\4-MaxMahon\hong-lens\CLAUDE.md`

## ที่มา
- ข้อตกลง: `C:\WORKSPACE\projects\4-MaxMahon\roadmap\agreed-selection-system.md` (N1–N10) · `C:\WORKSPACE\projects\4-MaxMahon\roadmap\agreed-portfolio-framework.md` (F1–F4)
