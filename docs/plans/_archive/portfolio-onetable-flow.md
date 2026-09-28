---
project: 4-MaxMahon
created: 2026-08-19
last_updated: 2026-08-19
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: เปิดหน้าจัดพอร์ต แก้จำนวนหุ้น+เงินสดในตารางเดียว กดปุ่ม 'บันทึก + คำนวณใหม่' ปุ่มเดียว แล้วตารางล่างขึ้นแผนซื้อทันทีจากเงินสดที่มีอยู่ในตาราง โดยไม่มีช่องกรอกเงินเติมแยก ไม่มีเงินเหลือค้างเพราะซื้อไม่ครบล็อต และไม่มีบล็อก LH/TISCO เหลืออยู่ที่ไหนเลย

### รายละเอียด
- โมเดลใหม่: เงินสดคือช่องที่ 8 ของสัดส่วนรวม 100% ไม่ใช่เงินสำรองพิเศษ - อาร์ทเคาะเอง 2026-08-19
- เงินที่ซื้อได้ (spendable) = เงินสด - total_value * เป้าเงินสด/100 แล้ว clamp ที่ 0 - ไม่มีตัวแปร new_money อีกต่อไป
- อัลกอริทึมใหม่ = greedy ล้วน: วนซื้อทีละ 1 ล็อต (100 หุ้น) ให้ตัวที่ห่างเป้ามากที่สุดเป็นบาท และราคาล็อตยังพอจ่ายไหว แล้วคำนวณระยะห่างใหม่ทุกรอบ จนไม่มีล็อตไหนซื้อไหว
- ต้องคำนวณระยะห่างใหม่ทุกรอบใน loop (ห้ามคิดครั้งเดียวตอนต้นแล้ววนใช้ค่าเดิม) ไม่งั้นเงินจะกองใส่ตัวที่ห่างที่สุดตัวเดียวแทนที่จะเกลี่ย
- ทิ้งของเดิม 2 ชั้น (แบ่งตามสัดส่วนช่องว่างก่อน แล้วค่อยปัดลงเป็นล็อต) เพราะนั่นคือต้นเหตุเงินค้าง: เติม 20,000 ค้างเปล่า 9,069 (45%) / เติม 50,000 ค้าง 19,972 (40%) / เติม 100,000 ค้าง 14,214 (14%)
- tie-break ตอนระยะห่างเท่ากัน = เรียงตามลำดับ key ใน targets เพื่อให้ผลเหมือนเดิมทุกครั้งที่โหลด - ต้องมีเทสพิสูจน์ว่าเรียกซ้ำได้ผลเท่าเดิม
- iteration cap กัน loop วิ่งหนี และถ้าชน cap จริงต้องต่อท้าย note ว่าคำนวณไม่ครบ ห้ามเงียบ เพราะหน้าตาจะเหมือนบั๊กเงินค้างที่งานนี้มาฆ่าพอดี
- แผนซื้อไปอยู่ใน build_state เป็น key ชื่อ plan - GET /api/portfolio/state และ PUT /api/portfolio/holdings เลยได้แผนติดมาด้วยทั้งคู่ ไม่ต้องยิง endpoint ที่สอง
- ฟังก์ชันคำนวณแผนห้าม raise เด็ดขาด เพราะถ้า raise ใน build_state = ทั้งหน้าจอพัง ให้คืน rows ว่าง + note เป็นข้อความไทยแทน
- note มี 4 สถานะ: (ก) ซื้อได้ X บาท (ข) เงินสดยังไม่ถึงเป้า - ยังไม่ต้องซื้อ (ค) ราคาไม่มา: SYM1, SYM2 - กดดึงราคาก่อน (ง) ยังไม่มีมูลค่าพอร์ต
- note เก็บแค่ประโยคสั้น ส่วนวงเล็บรายละเอียดบนจอให้หน้าจอประกอบเองจาก cash + cash_target_baht - กันเลขโผล่ซ้ำสองที่ในบรรทัดเดียว
- แถวเงินสดในแผนซื้อ ต้องต่อท้ายเสมอ ห้ามเข้า sort ตามจำนวนเงิน และห้ามหายแม้ซื้อไม่ได้เลย - ของเดิม sort ตามเงินจะดันแถวเงินสดขึ้นบนสุดเพราะยอดเยอะสุด
- แถวเงินสดต้องมี field pct_after (เงินสดหลังซื้อคิดเป็น % ของพอร์ต) เพราะป้ายบนจอเขียนว่า 'เหลือหลังซื้อ X%'
- ชื่อ field ระยะห่างในแผนซื้อคือ gap_pct - หน้าจอเดิมอ่าน deficit_pct ต้องเปลี่ยนตาม ไม่งั้นทุกแถวขึ้น 'ขาด 0%' เงียบๆ
- ลบ POST /api/portfolio/topup + model PortfolioTopup + ฟังก์ชัน rebalance_topup ทิ้งทั้งหมด
- ปุ่มเดิม 'บันทึกพอร์ต' เปลี่ยนข้อความเป็น 'บันทึก + คำนวณใหม่' - หัวการ์ด 2 เปลี่ยนจาก 'มีเงินมาเพิ่ม' เป็น 'ต้องซื้ออะไรบ้าง'
- ตัดช่องกรอกเงิน #ph-calc-input + ปุ่ม #ph-calc-btn + ฟังก์ชัน _runCalc ทิ้ง - แผนซื้อ render จาก state.plan ที่ติดมากับ response
- ถอด LH/TISCO ออกหมดทั้ง off_plan และ lh_triggers - อาร์ทสั่งเอง 2026-08-19 ว่าจบเรื่องนั้นแล้ว ไม่มีผลอีก
- LH จะยังโผล่ในรายชื่อดึงราคารายวันได้ เพราะมาจากผลสแกนอีกทาง ไม่ใช่ off_plan - อย่าไปไล่ลบต่อ นั่นคนละระบบและอยู่นอกงานนี้
- positions[].missing_price ต้องถูก render จริง - ห้ามโชว์มูลค่า 0 พร้อมป้าย 'ขาด' เพราะแยกไม่ออกจากตัวที่ขาดเป้าจริง และตอนนี้แผนซื้อกินตัวเลขชุดเดียวกันเลยอันตรายกว่าเดิม
- desktop กับ mobile ต้องแก้ใน phase เดียวกัน ห้ามแยก phase เพราะตอนนี้สูตรสองไฟล์ตรงกันเป๊ะ แยกเมื่อไหร่คือจุดที่มันเริ่มเพี้ยนจากกัน
- ห้ามสร้าง class ใหม่หรือใส่ hex/px ตรง - class ที่ใช้มีครบแล้วใน components.css block .pf-home ยกเว้น pf-table-wrap ที่อยู่ใน shared/mobile.css บรรทัด 183 (ของเดิม ไม่ต้องเพิ่มใหม่)
- เงื่อนไขตรวจต้องเป็นแบบที่ตัวทำรันเองได้ (grep / รัน python) - อะไรที่ต้องเปิดเบราว์เซอร์ดู ยกไปเป็นด่านให้อาร์ทตรวจตอนท้าย ไม่ใช่เงื่อนไขของ task
- เอกสารบ้านของโปรเจกต์ (CLAUDE.md) ยังเขียนถึง off_plan / lh_triggers / topup อยู่ ต้องอัปตาม ไม่งั้นเอกสารกับของจริงเพี้ยนกัน
- ตัวเลข acceptance ทั้งหมดคำนวณจริงจาก data/portfolios/A.json + data/price_cache แล้ว และตรวจซ้ำรอบสอง 2026-08-19 หลังรอบแรกใส่เลขที่ปัดเศษแล้วผิด

### Scope Boundary
**In scope:**
- scripts/portfolio_state.py - เพิ่ม compute_buy_plan, ต่อเข้า build_state, ลบ rebalance_topup, ถอด off_plan/lh_triggers
- server/app.py - ลบ endpoint topup + model PortfolioTopup, ลบ endpoint lh-signals, ถอด off_plan ออกจาก PortfolioHoldingsUpdate
- web/v6/static/js/pages/portfolio-home.js - ตารางเดียว + ปุ่มเดียว + render plan + missing_price + ลบบล็อกนอกแผน
- web/v6/static/js/pages/portfolio-home.mobile.js - แก้คู่กับ desktop ทุกจุด
- scripts/daily_price_refresh.py - ถอด off_plan ออกจาก _load_symbols
- scripts/migrate_portfolio_to_separate.py - ถอด seed off_plan/lh_triggers
- data/portfolios/A.json, B.json, C.json - ลบ block off_plan + lh_triggers
- tests/test_portfolio_math.py - เขียนเทสของ topup ใหม่ให้ตรง contract ใหม่
- CLAUDE.md - อัปบรรทัดที่บรรยาย off_plan / lh_triggers / topup / lh-signals

**Out of scope:**
- scripts/portfolio_builder.py และ endpoint /api/portfolio/builder - คนละหน้า (จัดพอร์ตจากผลสแกน) ไม่แตะ
- เครื่องจำลอง DCA ใน server/app.py (บรรทัด ~1436-1650) - คนละหน้าจอ คนละบั๊ก ไปทำแยก
- web/v6/static/css/components.css และ shared/mobile.css - ไม่ต้องแก้ CSS เลย (กฎเดิมของ .topup-in ที่กลายเป็นของตายจะถูกทิ้งไว้ก่อนโดยตั้งใจ)
- avg_cost ที่เป็น 0 ทั้ง 7 ตัว และการเพิ่มช่องกรอกต้นทุน - อาร์ทยังไม่ได้สั่ง
- data/portfolio.json ตัว legacy - ปล่อยไว้ทั้ง key เดิม เพราะไม่มีใครอ่าน 2 key นั้นแล้ว
- CHANGELOG.md - เป็นบันทึกอดีต ห้ามแก้ย้อนหลัง
- รายชื่อหุ้นจากผลสแกน/watchlist ที่ทำให้ LH ยังถูกดึงราคา - คนละระบบ ห้ามแตะ

### Non-goals
- ไม่แก้บั๊กนับปันผลซ้ำในเครื่องจำลอง DCA - รุนแรงกว่านี้แต่คนละหน้าจอ ต้องแยกใบงานเพื่อไม่ให้ scope บาน
- ไม่ทำกำไร/ขาดทุนรายตัว - ต้องมีต้นทุนก่อน ซึ่งยังไม่มีช่องให้กรอก และอาร์ทไม่ได้ขอ
- ไม่แก้บั๊กปักหมุด 2 ตัวกลุ่มเดียวกันแล้วตัวที่สองหาย - อยู่หน้าจัดพอร์ตจากผลสแกน คนละที่
- ไม่เพิ่มปุ่ม/โหมด/ตัวเลือกใหม่ในหน้านี้ - เป้าคือลดของบนจอ ไม่ใช่เพิ่ม
- ไม่ทำ migration ย้อนหลังของไฟล์พอร์ตเก่า - แค่ลบ key ที่ไม่ใช้ออกตรงๆ
- ไม่เก็บกวาด CSS ที่กลายเป็นของตาย - แยกทำทีหลังได้ ไม่คุ้มเสี่ยงตอนนี้

### Skill Flow
- /build -> /qc -> /done

### Stop Conditions
- ไฟล์จริงไม่ตรงกับ snippet ใน Reference - หยุดถามก่อน ห้ามเดาแล้วแก้
- ตัวเลข acceptance ที่รันได้ไม่ตรงกับที่เขียนไว้ในแผน - หยุดรายงานตัวเลขที่ได้จริง ห้ามแก้แผนเอง
- เจอที่อื่นที่อ่าน off_plan หรือ lh_triggers นอกเหนือจากรายการใน Phase 2 - หยุดแจ้งก่อนลบ
- ต้องเพิ่ม class ใหม่หรือ token ใหม่ที่ไม่มีใน components.css หรือ shared/mobile.css - หยุดถาม เพราะแปลว่า mockup ไม่ครบ

### Report-Back Contract
- verdict
- ไฟล์ที่แตะ
- ผลรันจริงของ acceptance ทั้งหมดใน Phase 1 (ตัวเลขเต็ม ไม่ปัดเศษ)
- ผล py -m pytest tests/test_portfolio_math.py
- ผล grep off_plan/lh_triggers/topup/lh-signals ว่าเหลือกี่จุดและอยู่ไฟล์ไหน
- รายการที่ต้องให้อาร์ทเปิดจอตรวจเอง
- อะไรที่ยังค้าง

# จัดพอร์ต ตารางเดียว - ตัดช่องเงินเติม + เลิกทิ้งเงินค้าง + ถอด LH/TISCO

> หน้าจัดพอร์ตเดิมมี 2 ก้อนแยกกัน - ตารางพอร์ต กับ ช่องกรอกเงินเติมที่ต้องกดคำนวณอีกปุ่ม ทำให้เงินที่แบ่งให้หุ้นที่ซื้อไม่ครบ 1 ล็อตตกไปกองเป็นเงินสดเงียบๆ (เติม 20,000 ค้างเปล่า 45%). งานนี้ยุบเหลือตารางเดียวปุ่มเดียวตามที่อาร์ทเคาะ แก้จำนวนหุ้น+เงินสดแล้วกดบันทึก แผนซื้อโผล่เอง พร้อมถอด LH/TISCO ที่จบเรื่องแล้วออกทั้งระบบ. รอบนี้แก้จากผลตรวจแผนรอบแรก (ตก 6 จุดหนัก 15 จุดเล็ก) เลขบรรทัดกับโค้ดอ้างอิงทุกจุดเปิดไฟล์จริงยืนยันแล้ว. Mockup: C:\WORKSPACE\.claude\artifacts\maxmahon-portfolio-onetable.html

## Phase 1: หลังบ้าน - เครื่องคำนวณแผนซื้อตัวใหม่
- [x] Pre-build Review: อ่าน plan ทั้งไฟล์ + เปิด mockup C:\WORKSPACE\.claude\artifacts\maxmahon-portfolio-onetable.html + อ่านไฟล์จริงตาม scope และ Reference ก่อนแก้ code; ตรวจว่า path, บรรทัด, snippet และ acceptance ตรงกันไหม; ถ้ามีข้อสงสัย/ข้อมูลไม่พอ/spec ขัดกัน ให้หยุดถามก่อนลงมือ; ถ้าชัดให้ตอบว่า plan clear แล้วเริ่ม task ถัดไป
- [x] เพิ่มค่าคงที่ `MAX_LOT_ITERATIONS = 10000` ใต้ `BOARD_LOT = 100` ใน `projects/4-MaxMahon/scripts/portfolio_state.py` (บรรทัด 41) - scope: ไม่แตะค่าอื่น - Acceptance: `py -c "import sys; sys.path.insert(0,'scripts'); import portfolio_state as p; print(p.MAX_LOT_ITERATIONS)"` จาก `projects/4-MaxMahon` พิมพ์ 10000
- [x] สร้างฟังก์ชัน `compute_buy_plan(state: dict, targets: dict) -> dict` ใน `projects/4-MaxMahon/scripts/portfolio_state.py` วางไว้ก่อน `build_state` ตาม snippet ใน Reference (ก็อปทั้งก้อน ห้ามย่อ) - ต้องเป็น pure + total (ห้ามมี raise, ห้ามอ่านไฟล์, ห้ามเรียก read_price), ต้องคำนวณระยะห่างใหม่ทุกรอบใน loop, แถวเงินสดต่อท้ายหลัง sort เสมอ และต้องต่อท้าย note ถ้าชน iteration cap - scope: ยังไม่แตะ `build_state` ใน task นี้ - Acceptance: เรียกตรงๆ ด้วย state จาก `build_state('A')` ปัจจุบัน (เงินสด 419,984) ได้ `spendable == 0.0`, ไม่มีแถวไหน `shares_to_buy` มากกว่า 0, `note == 'เงินสดยังไม่ถึงเป้า - ยังไม่ต้องซื้อ'` และแถวสุดท้ายของ `rows` คือ `sym == 'cash'` ที่มี `baht == 419984.0` กับ `pct_after == 4.6`
- [x] ต่อ `compute_buy_plan` เข้า `build_state` ใน `projects/4-MaxMahon/scripts/portfolio_state.py` โดยเพิ่ม key `"plan"` ใน dict ที่ return (บรรทัด 290-308) ตาม snippet ใน Reference - scope: ห้ามเปลี่ยน/ลบ key เดิมตัวอื่นใน task นี้ - Acceptance: `build_state('A')['plan']` มีครบ 4 key `spendable / cash_target_baht / rows / note` และ key เดิมทั้งหมด (positions, off_plan, cash, cash_pct, cash_target_pct, total_value, summary, lh_triggers, updated_at, name, price_as_of) ยังอยู่ครบเหมือนเดิม
- [x] พิสูจน์ตัวเลขด้วย state จำลอง: เอา `build_state('A')` มาแก้ `cash` เป็น 719984.0 และ `total_value` เป็น 9428084.0 แล้วเรียก `compute_buy_plan(state, targets)` โดย targets อ่านจาก `load_portfolio('A')['targets']` - scope: ห้ามแก้ไฟล์ข้อมูลจริงเพื่อทดสอบ ให้แก้ dict ในหน่วยความจำเท่านั้น - Acceptance: `spendable == 248579.8` (ห้ามปัดเป็น 248580) และซื้อ BBL 700 / SISB 6800 / TOA 1800 / SECURE 1900 หุ้น รวมลงเงิน 247890.0 และแถวเงินสดได้ `baht == 472094.0` กับ `pct_after == 5.01` และ MOSHI/AMATA/TCAP ได้ `shares_to_buy == 0` และ `gap_pct` ของ BBL/SISB/TOA/SECURE = 1.74 / 1.14 / 0.74 / 0.71
- [x] ลบฟังก์ชัน `rebalance_topup` ทั้งก้อน (บรรทัด 314-447) ออกจาก `projects/4-MaxMahon/scripts/portfolio_state.py` พร้อมแก้ docstring หัวไฟล์ที่ยังโฆษณา Phase 3 top-up calculator และบรรทัดใน Public API ที่ลิสต์ `rebalance_topup(state, new)` - scope: ห้ามลบ `save_portfolio` / `read_price` / `_round2` / `_price_cache_as_of` - Acceptance: `grep -rn rebalance_topup projects/4-MaxMahon/scripts/` ไม่เจอ และ `py -c "import sys; sys.path.insert(0,'scripts'); import portfolio_state"` ไม่ error
- [x] ลบ endpoint `POST /api/portfolio/topup` (บรรทัด 3075-3086) + class `PortfolioTopup` (บรรทัด 3071-3072) + ชื่อ `rebalance_topup` ในบรรทัด 3008 ของ import block ออกจาก `projects/4-MaxMahon/server/app.py` - scope: ห้ามแตะ endpoint `/api/portfolio/state`, `/api/portfolio/holdings`, `/api/portfolios` - Acceptance: `grep -n "topup\|PortfolioTopup\|rebalance_topup" projects/4-MaxMahon/server/app.py` ไม่เจอ และ `py -c "import server.app"` จาก `projects/4-MaxMahon` ไม่ error

### Reference
```python
# current (scripts/portfolio_state.py:41)
BOARD_LOT = 100

# new
BOARD_LOT = 100
MAX_LOT_ITERATIONS = 10000  # runaway guard — ชน cap เมื่อไหร่ต้องบอก ห้ามเงียบ


# new — วางก่อน build_state. pure + total: ห้าม raise เพราะ build_state เรียกตัวนี้
# ถ้า raise = ทั้งหน้าจอพัง ไม่ใช่แค่ตารางแผนซื้อหาย
def compute_buy_plan(state: dict, targets: dict) -> dict:
    """เงินสดส่วนที่เกินเป้าของตัวเอง ควรไปลงตัวไหนบ้าง.

    เงินสด = ช่องหนึ่งในสัดส่วนรวม 100% ไม่ใช่เงินสำรอง:
        spendable = cash - total_value * targets['cash']/100   (clamp 0)

    greedy: วนซื้อทีละ 1 ล็อต ให้ตัวที่ห่างเป้ามากที่สุดเป็นบาทและยังจ่ายไหว
    แล้วคำนวณระยะห่างใหม่ทุกรอบ เงินเศษที่ซื้อล็อตไม่ไหวจึงตกเป็นเงินสดจริงๆ
    ไม่ใช่เงินที่ถูกจองไว้ให้ตัวที่ซื้อไม่ลงแล้วหายเงียบแบบของเดิม
    """
    total_value = float(state.get("total_value", 0) or 0)
    cash = float(state.get("cash", 0) or 0)
    positions = state.get("positions", []) or []

    cv = {p["sym"]: float(p.get("current_value", 0) or 0) for p in positions}
    px = {p["sym"]: p.get("price") for p in positions}
    stocks = [s for s in targets if s != "cash"]

    missing = [s for s in stocks
               if not isinstance(px.get(s), (int, float)) or float(px.get(s) or 0) <= 0]
    if missing:
        return {"spendable": 0.0, "cash_target_baht": 0.0, "rows": [],
                "note": "ราคาไม่มา: " + ", ".join(missing) + " - กดดึงราคาก่อน"}
    if total_value <= 0:
        return {"spendable": 0.0, "cash_target_baht": 0.0, "rows": [],
                "note": "ยังไม่มีมูลค่าพอร์ต"}

    cash_target_baht = total_value * float(targets.get("cash", 0) or 0) / 100.0
    spendable = max(0.0, cash - cash_target_baht)

    bought = {s: 0 for s in stocks}
    left = spendable
    truncated = True
    for _ in range(MAX_LOT_ITERATIONS):
        pick, best_gap = None, 0.0
        for s in stocks:  # ลำดับ key ใน targets = tie-break ที่นิ่ง
            lot_cost = float(px[s]) * BOARD_LOT
            if lot_cost > left + 1e-9:
                continue
            # คำนวณใหม่ทุกรอบ (ห้าม cache) ไม่งั้นเงินกองใส่ตัวเดียว
            gap = (total_value * float(targets.get(s, 0) or 0) / 100.0
                   - (cv[s] + bought[s] * float(px[s])))
            if gap > best_gap:
                pick, best_gap = s, gap
        if pick is None:
            truncated = False
            break
        bought[pick] += BOARD_LOT
        left -= float(px[pick]) * BOARD_LOT

    rows = []
    spent = 0.0
    for s in stocks:
        price = float(px[s])
        gap0 = total_value * float(targets.get(s, 0) or 0) / 100.0 - cv[s]
        baht = _round2(bought[s] * price)
        spent += baht
        rows.append({
            "sym": s,
            "status": "under" if gap0 > 1e-9 else "over",
            "gap_pct": _round2(max(0.0, gap0) / total_value * 100.0),
            "price": price,
            "shares_to_buy": bought[s],
            "baht": baht,
        })
    rows.sort(key=lambda r: r["baht"], reverse=True)

    # แถวเงินสด — ต่อท้าย "หลัง" sort เสมอ ห้ามให้มันเข้าไปเรียงกับหุ้น
    cash_after = _round2(cash - spent)
    rows.append({
        "sym": "cash", "status": "ok", "gap_pct": 0.0, "price": None,
        "shares_to_buy": None, "baht": cash_after,
        "pct_after": _round2(cash_after / total_value * 100.0),
    })

    if spendable <= 0:
        note = "เงินสดยังไม่ถึงเป้า - ยังไม่ต้องซื้อ"
    else:
        note = "ซื้อได้ " + format(spendable, ",.0f") + " บาท"
    if truncated:
        note += " (คำนวณไม่ครบ - ล็อตเยอะเกิน)"

    return {
        "spendable": _round2(spendable),
        "cash_target_baht": _round2(cash_target_baht),
        "rows": rows,
        "note": note,
    }
```

```python
# current (scripts/portfolio_state.py:290-308) — dict ที่ build_state return
    return {
        "positions": positions,
        "off_plan": off_plan_out,
        "cash": _round2(cash),
        ...
        "price_as_of": _price_cache_as_of(),
    }

# new — เพิ่ม "plan" (off_plan ยังอยู่ใน Phase 1, ไปลบใน Phase 2)
    state = {
        "positions": positions,
        "off_plan": off_plan_out,
        "cash": _round2(cash),
        ...
        "price_as_of": _price_cache_as_of(),
    }
    state["plan"] = compute_buy_plan(state, targets)
    return state
```

```python
# current (server/app.py:3071-3086) — ยืนยันจากไฟล์จริง 2026-08-19
class PortfolioTopup(BaseModel):
    new_money: float


@app.post("/api/portfolio/topup")
async def portfolio_topup(...):
    ...

# new
# ลบทั้งก้อน — แผนซื้อมากับ build_state แล้ว ไม่ต้องมี endpoint ที่สอง
# และลบชื่อ rebalance_topup ที่บรรทัด 3008 ของ import block ด้วย
```

## Phase 2: ถอด LH/TISCO ออกทั้งระบบ
- [x] ลบการสร้าง `off_plan_out` (บรรทัด 264-285), key `"off_plan"` (บรรทัด 292) และ key `"lh_triggers"` (บรรทัด 304) ออกจาก `build_state` ใน `projects/4-MaxMahon/scripts/portfolio_state.py` พร้อมลบ docstring ที่บรรยาย 2 key นั้น (บรรทัด 177-178, 185) และคอมเมนต์บรรทัด 56 - scope: ห้ามแตะการคำนวณ positions/cash/total_value/summary - Acceptance: `build_state('A')` ไม่มี key `off_plan` และ `lh_triggers` แล้ว แต่ `total_value` ยังได้ 9128084.0 เท่าเดิม และ `plan['rows']` ยังมี 8 แถว
- [x] ลบ field `off_plan` ออกจาก class `PortfolioHoldingsUpdate` (บรรทัด 3046) และลบ 2 บรรทัดที่เขียนค่านั้นลงไฟล์ (บรรทัด 3065-3066) ใน `projects/4-MaxMahon/server/app.py` พร้อมแก้ docstring บรรทัด 3057-3058 ที่ระบุ lh_triggers - scope: ห้ามแตะ field `holdings` และ `cash` - Acceptance: `grep -n "off_plan" projects/4-MaxMahon/server/app.py` ไม่เจอ และ `py -c "import server.app"` ไม่ error
- [x] ลบ endpoint `GET /api/portfolio/lh-signals` ทั้งก้อน (บรรทัด 3087-3152) ออกจาก `projects/4-MaxMahon/server/app.py` - scope: ห้ามลบ endpoint `PUT /api/portfolio/{pf}/name` ที่อยู่ถัดไป (บรรทัด 3159) - Acceptance: `grep -n "lh-signals\|lh_triggers" projects/4-MaxMahon/server/app.py` ไม่เจอ และ `py -c "import server.app"` ไม่ error
- [x] ลบบรรทัด 84 `| set(pf.get("off_plan", {}).keys())` ออกจาก `_load_symbols()` ใน `projects/4-MaxMahon/scripts/daily_price_refresh.py` โดยเก็บ `targets` และ `holdings` ไว้ตาม snippet ใน Reference - scope: ห้ามแตะการรวม symbol จาก watchlist / PASS / screener - Acceptance: เรียก `_load_symbols()` แล้ว `TISCO.BK` หายจากผลลัพธ์ และหุ้น 7 ตัวในพอร์ตยังอยู่ครบ. **`LH.BK` จะยังอยู่ ซึ่งถูกต้อง** เพราะมันมาจากไฟล์ผลสแกน (`data/screener_*.json`) คนละทางกับ off_plan - ห้ามไล่ลบต่อ
- [x] ลบการ seed `off_plan` (บรรทัด 78-81 `seed_offplan = {...}` และบรรทัด 87 `"off_plan": seed_offplan,`) กับ `lh_triggers` (บรรทัด 88) ออกจาก `projects/4-MaxMahon/scripts/migrate_portfolio_to_separate.py` - scope: **ห้ามแตะบรรทัด 74-77 ซึ่งคือ `seed_holdings` คนละตัวกัน** และห้ามแตะการ seed targets/cash/meta - Acceptance: `grep -n "off_plan\|lh_triggers" projects/4-MaxMahon/scripts/migrate_portfolio_to_separate.py` ไม่เจอ, `grep -n "seed_holdings" ...` ยังเจอ 2 จุด, และ `py -c "import ast,pathlib; ast.parse(pathlib.Path('scripts/migrate_portfolio_to_separate.py').read_text(encoding='utf-8'))"` ผ่าน
- [x] ลบ block `off_plan` และ `lh_triggers` ออกจาก `projects/4-MaxMahon/data/portfolios/A.json`, `B.json`, `C.json` ด้วยสคริปต์ Python ที่โหลด json แล้ว pop key แล้วเขียนกลับด้วย `ensure_ascii=False, indent=2` - scope: ห้ามแตะ targets/holdings/cash/meta/name/updated_at และห้ามแตะ `data/portfolio.json` ตัว legacy - Acceptance: ทั้ง 3 ไฟล์ไม่มี 2 key นั้นแล้ว, `targets` ยังรวมได้ 100.0, และ `build_state('A')['total_value']` ยังได้ 9128084.0
- [x] อัป `projects/4-MaxMahon/CLAUDE.md` บรรทัด 152-153 ที่บรรยาย `portfolio_state.py` และ `data/portfolios/{A,B,C}.json` ให้ตัดคำว่า off_plan / lh_triggers / topup / lh-signals ออก และเพิ่มว่า `build_state` คืน `plan` (แผนซื้อ) มาด้วย - scope: ห้ามแตะ section อื่นของ CLAUDE.md - Acceptance: `grep -n "off_plan\|lh_triggers\|lh-signals\|topup" projects/4-MaxMahon/CLAUDE.md` ไม่เจอ และบรรทัดที่บรรยาย portfolio_state มีคำว่า `plan` อยู่

### Reference
```python
# current (scripts/daily_price_refresh.py:81-85) — ยืนยันจากไฟล์จริง 2026-08-19
            pf_syms = (
                set(pf.get("targets", {}).keys())
                | set(pf.get("holdings", {}).keys())
                | set(pf.get("off_plan", {}).keys())
            )

# new — ลบเฉพาะบรรทัด off_plan เก็บ targets กับ holdings ไว้
            pf_syms = (
                set(pf.get("targets", {}).keys())
                | set(pf.get("holdings", {}).keys())
            )
```

```python
# current (scripts/migrate_portfolio_to_separate.py:74-88) — ยืนยันจากไฟล์จริง 2026-08-19
        seed_holdings = {                                    # 74  <-- ห้ามแตะ
            sym: {"shares": 0, "avg_cost": 0}                # 75  <-- ห้ามแตะ
            for sym in (a_data.get("holdings", {}) or {})    # 76  <-- ห้ามแตะ
        }                                                    # 77  <-- ห้ามแตะ
        seed_offplan = {                                     # 78  <-- ลบ
            sym: {"shares": 0, "avg_cost": 0, "mode": (info or {}).get("mode", "hold")}
            for sym, info in (a_data.get("off_plan", {}) or {}).items()
        }                                                    # 81  <-- ลบ
        seed = {
            "name": PF_NAMES[pid],
            "targets": dict(a_data.get("targets", {}) or {}),
            "holdings": seed_holdings,
            "cash": 0,
            "off_plan": seed_offplan,                        # 87  <-- ลบ
            "lh_triggers": dict(a_data.get("lh_triggers", {}) or {}),  # 88  <-- ลบ
            "meta": dict(a_data.get("meta", {}) or {}),
        }
```

```python
# current (server/app.py:3043-3046) — verbatim
class PortfolioHoldingsUpdate(BaseModel):
    holdings: Optional[dict] = None
    cash: Optional[float] = None
    off_plan: Optional[dict] = None

# new
class PortfolioHoldingsUpdate(BaseModel):
    holdings: Optional[dict] = None
    cash: Optional[float] = None
```

```python
# current (server/app.py:3065-3066) — verbatim
    if body.off_plan is not None:
        data["off_plan"] = body.off_plan

# new
# ลบสองบรรทัดนี้ทิ้ง
```

รายการที่อ่าน/เขียน off_plan หรือ lh_triggers ทั้งหมด (เปิดไฟล์จริงยืนยันครบทุกบรรทัด 2026-08-19 — ถ้าเจอที่อื่นนอกรายการนี้ ให้หยุดถามก่อนลบ):

- `scripts/portfolio_state.py` 56 (คอมเมนต์), 177-178 + 185 (docstring), 264-285 (off_plan_out), 292, 304
- `server/app.py` 3046, 3057-3058, 3065-3066, 3087-3152
- `scripts/daily_price_refresh.py` 84 (บรรทัดเดียว ไม่ใช่ทั้ง block)
- `scripts/migrate_portfolio_to_separate.py` 78-81, 87, 88
- `data/portfolios/A.json` 43-54 (off_plan), 55-64 (lh_triggers) และ B.json / C.json โครงเดียวกัน
- `CLAUDE.md` 152-153 (เอกสาร)
- ฝั่งหน้าจอ (ทำใน Phase 3): `portfolio-home.js` 5, 9-11, 300, 328, 342, 345 และ `portfolio-home.mobile.js` 5, 10-12, 286, 313, 327, 330
- `CHANGELOG.md` 37, 59, 61 = ประวัติเก่า **ห้ามแก้** (บันทึกอดีต ไม่ใช่สถานะปัจจุบัน)
- `data/portfolio.json` legacy = ปล่อยไว้ ไม่มีใครอ่าน 2 key นั้นแล้ว

## Phase 3: หน้าจอ - ตารางเดียว ปุ่มเดียว (desktop + mobile คู่กัน)
- [x] แก้ `_renderShell()` ใน `projects/4-MaxMahon/web/v6/static/js/pages/portfolio-home.js` และ `portfolio-home.mobile.js`: เปลี่ยนข้อความปุ่ม `#ph-save` (บรรทัด 127 ฝั่ง desktop) เป็น 'บันทึก + คำนวณใหม่' **และแก้ข้อความที่ `_saveAll` รีเซ็ตกลับใน finally ให้ตรงกันด้วย**, เปลี่ยนหัวการ์ด 2 จาก 'มีเงินมาเพิ่ม' เป็น 'ต้องซื้ออะไรบ้าง' พร้อม hint 'เงินสดส่วนที่เกินเป้า เติมเข้าตัวที่ขาด ดึงพอร์ตกลับสัดส่วน', ลบ `div.topup-in` (บรรทัด 137-141 ฝั่ง desktop) แล้วใส่ `'<div class="pf-card-f" id="ph-plan-head" style="border-top:none;padding-top:var(--sp-3)"></div>' +` แทน - scope: ห้ามแตะบรรทัด 136 ซึ่งเป็น `'</div>' +` ปิด `.pf-card-h` และห้ามแตะ pf-header / pf-tabbar / pf-hintbar / pf-total / ตารางพอร์ต - Acceptance: `grep -n "ph-calc-input\|ph-calc-btn\|topup-in\|บันทึกพอร์ต" projects/4-MaxMahon/web/v6/static/js/pages/portfolio-home*.js` ไม่เจอ และ `grep -c "ph-plan-head" ...` เจอไฟล์ละอย่างน้อย 1 จุด
- [x] ลบฟังก์ชัน `_runCalc` (บรรทัด 370-387 ฝั่ง desktop) และการผูก event ของ `#ph-calc-btn` กับ Enter บน `#ph-calc-input` ใน `_bindEvents` ออกจากทั้งสองไฟล์ แล้วแก้ `_renderCalcTable` ให้รับ `plan` object แทน array: เขียน `#ph-plan-head` เป็น span class `note` (เติม class `warn` ด้วยเมื่อ `plan.spendable` ไม่มากกว่า 0) บรรจุ `plan.note` แล้วตามด้วย span class `dim` ที่ประกอบจาก `state.cash` กับ `plan.cash_target_baht` - scope: คงข้อความเดิมทุกตัวอักษรของ 'ยังขาด แต่เงินไม่พอซื้อครบ 100 หุ้น' และ 'เกิน/ตรงเป้า - ไม่ต้องซื้อ'; **ห้ามเอา `plan.spendable` ไปพิมพ์ซ้ำต่อท้าย `plan.note` เพราะ note มีเลขนั้นอยู่แล้ว** - Acceptance: `grep -n "_runCalc\|new_money\|api/portfolio/topup" projects/4-MaxMahon/web/v6/static/js/pages/portfolio-home*.js` ไม่เจอ
- [x] เปลี่ยน `r.deficit_pct` เป็น `r.gap_pct` ที่ `projects/4-MaxMahon/web/v6/static/js/pages/portfolio-home.js` บรรทัด 409 และ `portfolio-home.mobile.js` บรรทัด 393 - scope: แก้แค่ชื่อ field ไม่แตะการ `.toFixed(1)` หรือข้อความป้าย - Acceptance: `grep -rn "deficit_pct" projects/4-MaxMahon/web/v6/static/js/` ไม่เจอ และ `grep -rn "gap_pct" projects/4-MaxMahon/web/v6/static/js/` เจอไฟล์ละ 1 จุด
- [x] แก้การจัดแถวใน `_renderCalcTable` ของทั้งสองไฟล์: แยกแถวที่ `sym === 'cash'` ออกจากกอง `buys` ก่อน sort แล้วต่อท้ายตารางเป็นแถวสุดท้ายเสมอ โดยป้ายสถานะเขียน `'เหลือหลังซื้อ ' + r.pct_after + '%'` ใน span class `st ok` - scope: ห้ามเปลี่ยนการ sort ของแถวหุ้น (ยังเรียง `baht` มากไปน้อยเหมือนเดิม) - Acceptance: อ่านโค้ดแล้วแถว cash ไม่ผ่าน `buys.sort` และถูกต่อท้ายหลังทั้ง `belowLot` และ `skips`; ถ้าซื้อไม่ได้เลย แถว cash ก็ยังต้องถูก render (ตรง mockup pane 2) - `grep -c "pct_after"` เจอไฟล์ละ 1 จุด
- [x] เพิ่มข้อความกรณีเงินสดไม่ถึงเป้าใน `_renderCalcTable` ของทั้งสองไฟล์: เมื่อ `plan.spendable` ไม่มากกว่า 0 แถวหุ้นที่ `status === 'under'` ให้รวมเป็นบรรทัดเดียวข้อความ 'ยังขาดเป้า แต่เงินสดยังไม่มีส่วนเกินให้ซื้อ' (แทนข้อความ 'ยังขาด แต่เงินไม่พอซื้อครบ 100 หุ้น' ซึ่งใช้ตอนมีเงินแต่ไม่พอล็อต) - scope: ไม่แตะกรณีที่ `spendable` มากกว่า 0 - Acceptance: `grep -c "ยังขาดเป้า แต่เงินสดยังไม่มีส่วนเกินให้ซื้อ" projects/4-MaxMahon/web/v6/static/js/pages/portfolio-home.js` = 1 และไฟล์ mobile = 1
- [x] แก้ `_load()` และ `_saveAll()` ในทั้งสองไฟล์ให้เรียก `_renderCalcTable` ด้วย `_state.plan` ทุกครั้งหลังได้ response - scope: ห้ามเพิ่ม fetch ใหม่ เพราะแผนซื้อติดมากับ response เดิมแล้ว - Acceptance: `grep -c "MMApi.post" projects/4-MaxMahon/web/v6/static/js/pages/portfolio-home.js` = 0 และ `grep -c "_renderCalcTable" ...` เจอไฟล์ละอย่างน้อย 3 จุด (นิยาม + เรียกใน _load + เรียกใน _saveAll)
- [x] แก้ `_renderRows()` ในทั้งสองไฟล์ให้อ่าน `p.missing_price`: ถ้าเป็น true ให้ช่องมูลค่า render span class `warn` ข้อความ 'ราคาไม่มา' แทนตัวเลข 0 และช่องสัดส่วน render span class `st ok` ข้อความ 'ยังไม่รู้' ตามด้วย span class `dim` ข้อความ 'รอดึงราคา' แทนป้าย 'ขาด' กับแท่ง ตาม mockup pane 3 - scope: ห้ามเปลี่ยนการ render ของแถวที่ราคามาปกติ และห้ามแตะแถวเงินสด - Acceptance: `grep -c "missing_price" projects/4-MaxMahon/web/v6/static/js/pages/portfolio-home.js` อย่างน้อย 1 และ mobile อย่างน้อย 1
- [x] ลบ `details#ph-offplan-det` ทั้งก้อนออกจาก `_renderShell()`, ลบฟังก์ชัน `_renderOffPlan` และ `_loadLhSignals` พร้อมทุกจุดที่เรียกทั้งสองตัว และแก้คอมเมนต์หัวไฟล์ **บรรทัด 5 กับ 9-11** ของ `portfolio-home.js` (mobile = บรรทัด 5 กับ 10-12) ที่ยังเขียนถึง 'กรอกเงินรอบนี้', `off_plan[]`, `lh-signals`, `topup` - scope: ห้ามลบ `details` อีกอันที่เป็นบล็อก 'แผนการลงทุน - Niwes 70' ซึ่งต้องอยู่เหมือนเดิม - Acceptance: `grep -rn "off_plan\|offplan\|lh-signals\|LhSignals\|กรอกเงินรอบนี้" projects/4-MaxMahon/web/v6/static/js/` ไม่เจอเลยสักจุด และ `grep -c "แผนการลงทุน" projects/4-MaxMahon/web/v6/static/js/pages/portfolio-home.js` = 1
- [x] เทียบ `portfolio-home.js` กับ `portfolio-home.mobile.js` บรรทัดต่อบรรทัดเฉพาะส่วนคำนวณและ render ตัวเลข - scope: ความต่างที่ยอมให้มีคือ `_REPORT_BASE` (`/report/` เทียบกับ `/m/report/`) และข้อความ hint ที่สั้นกว่าฝั่ง mobile เท่านั้น - Acceptance: ไม่มีจุดไหนที่สองไฟล์คำนวณตัวเลขเดียวกันด้วยสูตรต่างกัน รายงานรายการความต่างที่เหลือทั้งหมดออกมาเป็น list
- [x] รวบรายการที่ต้องให้อาร์ทเปิดจอตรวจเอง (ตัวทำเช็คเองไม่ได้): หน้าตาตรง mockup pane 1/2/3/4 ไหม, กดปุ่มครั้งเดียวแล้วยิง network แค่ครั้งเดียวไหม, แถวเงินสดอยู่ล่างสุดไหม, ป้าย 'ขาด X%' ขึ้นเลขจริงไม่ใช่ 0% - scope: แค่เขียนรายการ ไม่ต้องทดลองเอง - Acceptance: มีรายการเป็น bullet ส่งกลับใน report_back

### Reference
Mockup (source of truth ของหน้าตา - ต้องตรง 100%): `C:\WORKSPACE\.claude\artifacts\maxmahon-portfolio-onetable.html`

Element -> source mapping:

| ของบนจอ | มาจาก |
|---|---|
| ตารางพอร์ต | `GET /api/portfolio/state?pf=` -> `positions[]`, `cash`, `cash_pct`, `cash_target_pct`, `total_value` |
| ปุ่ม 'บันทึก + คำนวณใหม่' | `PUT /api/portfolio/holdings?pf=` body `{holdings, cash}` -> response = build_state (มี `plan` ติดมาแล้ว) |
| บรรทัด 'ซื้อได้ X บาท' (`#ph-plan-head`) | `plan.note` (ประโยคหลัก) + `state.cash` และ `plan.cash_target_baht` (วงเล็บ) |
| ตารางแผนซื้อ (`#ph-calc-body`) | `plan.rows[]` -> `sym / status / gap_pct / price / shares_to_buy / baht` |
| แถวเงินสด | `plan.rows[]` ตัวที่ `sym === 'cash'` -> `baht` + `pct_after` (ต่อท้ายเสมอ ไม่เข้า sort) |
| แถว 'ราคาไม่มา' | `positions[].missing_price` |

class ที่ใช้ทั้งหมดมีอยู่แล้ว **ไม่ต้องเพิ่มใหม่**:
- ใน `web/v6/static/css/components.css` block `.pf-home` (บรรทัด 1307 เป็นต้นไป): `pf-wrap pf-header pf-pricebtn pf-pricebtn-ico pf-priceinfo pf-tabbar pf-tab pf-tab-active pf-tab-dot pf-tab-nm pf-hintbar pf-total lbl val pf-card pf-card-h pf-card-f pf-table pf-btn pf-minor pf-foot qty alloc now arrow tgt bar fill mk st sym sub g niwes hong cash buyrow b skip mono dim warn note hint chev det-body det-text`
- ใน `web/v6/shared/mobile.css` บรรทัด 183: `pf-table-wrap` (ของเดิม ไม่ใช่ของใหม่)

**ห้ามเพิ่ม class ใหม่ ห้ามใส่ hex/px ตรง** ถ้าคิดว่าต้องเพิ่ม = หยุดถาม

```javascript
// current (portfolio-home.js:137-141) — ยืนยันจากไฟล์จริง 2026-08-19
// บรรทัด 136 คือ '</div>' + ที่ปิด .pf-card-h — ห้ามแตะ
        '<div class="topup-in">' +
          '<input class="mono" id="ph-calc-input" inputmode="numeric" value="100,000">' +
          '<span class="cur">บาท</span>' +
          '<button class="pf-btn" id="ph-calc-btn" type="button" style="margin-left:auto">คำนวณ &rarr;</button>' +
        '</div>' +

// new — ลบทั้งก้อน แล้วใส่หัวบอกเงินที่ซื้อได้แทน
        '<div class="pf-card-f" id="ph-plan-head" style="border-top:none;padding-top:var(--sp-3)"></div>' +
```

```javascript
// current (portfolio-home.js:409 / portfolio-home.mobile.js:393) — verbatim
    const deficit = r.deficit_pct != null ? r.deficit_pct.toFixed(1) : '0';

// new
    const deficit = r.gap_pct != null ? r.gap_pct.toFixed(1) : '0';
```

```javascript
// current (portfolio-home.js:381) — verbatim (ใช้ window.MMApi ไม่ใช่ api())
    const res = await window.MMApi.post('/api/portfolio/topup?pf=' + _currentPfId, { new_money: money });

// new — ลบ _runCalc ทั้งฟังก์ชัน แล้วให้ _load() กับ _saveAll() เรียกตรงนี้แทน
    _renderCalcTable(root.querySelector('#ph-calc-body'), _state.plan || null);
```

## Phase 4: เทส
- [x] แก้ import บรรทัด 5 ของ `projects/4-MaxMahon/tests/test_portfolio_math.py` จาก `from scripts.portfolio_state import BOARD_LOT, rebalance_topup` เป็น `from scripts.portfolio_state import BOARD_LOT, compute_buy_plan` และแก้ helper `_state` (บรรทัด 8-20 เป็น module-level function ไม่ใช่ method) ให้รับ `price`, `cash`, `total_value` แล้วคืน dict ที่มี key `positions` / `cash` / `total_value` - scope: ห้ามแตะ import ของ `allocate_80_20` บรรทัด 4 - Acceptance: `py -c "import ast,pathlib; ast.parse(pathlib.Path('tests/test_portfolio_math.py').read_text(encoding='utf-8'))"` ผ่าน
- [x] เขียน class `PortfolioTopupTests` (เริ่มบรรทัด 23 ถึง 46) ใหม่เป็น `BuyPlanTests` ที่ทดสอบ `compute_buy_plan` แทน `rebalance_topup` โดยเรียก helper แบบ `_state(...)` (module-level ไม่ใช่ `self._state`) - scope: **ห้ามแตะ `PortfolioBuilderWeightTests` ที่เริ่มบรรทัด 49 ถึง 63** เพราะสูตรน้ำหนัก 80/20 ไม่ได้เปลี่ยน - Acceptance: `py -m pytest tests/test_portfolio_math.py -q` ผ่านหมด และ `grep -c rebalance_topup tests/test_portfolio_math.py` = 0
- [x] เพิ่มเทส 3 เคสใน `BuyPlanTests` ที่ `projects/4-MaxMahon/tests/test_portfolio_math.py`: (ก) ราคาไม่มา -> `rows` ว่าง + `note` มีชื่อหุ้นตัวนั้น + **ไม่ raise** (ข) เงินสดต่ำกว่าเป้า -> `spendable == 0` + ไม่มีแถวไหน `shares_to_buy` มากกว่า 0 + แถว cash ยังอยู่ (ค) ผลรวม `baht` ของหุ้นทุกตัวบวกแถวเงินสด ต้องเท่ากับเงินสดตั้งต้นเป๊ะ - scope: ห้ามเรียก API หรืออ่านไฟล์พอร์ตจริงในเทส ให้ส่ง `targets` เป็น dict ตรงๆ - Acceptance: ทั้ง 3 เคสผ่าน และเคส (ก) ยืนยันว่าไม่มี exception หลุดออกมา
- [x] เพิ่มเทสกันเงินค้างแบบเดิมกลับมา ที่ `projects/4-MaxMahon/tests/test_portfolio_math.py`: สร้างเคสที่หุ้นราคาแพง (ล็อตละ 19,000) ขาดเป้ามากที่สุด แต่เงินที่ซื้อได้มีแค่ 12,000 และมีหุ้นถูกอีกตัวที่ขาดเป้าและซื้อไหว - scope: เทสเดียวจบ ไม่ต้อง parametrize - Acceptance: หุ้นถูกได้ `shares_to_buy` มากกว่า 0 และเงินสดที่เหลือน้อยกว่าราคา 1 ล็อตของหุ้นถูก
- [x] เพิ่มเทสความนิ่งของผลลัพธ์ ที่ `projects/4-MaxMahon/tests/test_portfolio_math.py`: สร้างเคสที่หุ้น 2 ตัวมีระยะห่างจากเป้าเท่ากันเป๊ะและราคาเท่ากัน แล้วเรียก `compute_buy_plan` 5 ครั้งด้วย input ชุดเดิม - scope: ไม่ต้องทดสอบว่าตัวไหนชนะ แค่ต้องได้ผลเดิมทุกครั้ง - Acceptance: ผลลัพธ์ทั้ง 5 ครั้งเท่ากันทุก field
- [x] เพิ่มเทส iteration cap ที่ `projects/4-MaxMahon/tests/test_portfolio_math.py`: patch `MAX_LOT_ITERATIONS` ให้เหลือ 2 แล้วสร้างเคสที่ต้องซื้อมากกว่า 2 ล็อต - scope: คืนค่าเดิมหลังเทสจบ - Acceptance: `note` ต่อท้ายด้วย '(คำนวณไม่ครบ - ล็อตเยอะเกิน)' และยังไม่ raise

### Reference
```python
# current (tests/test_portfolio_math.py:4-8) — verbatim จากไฟล์จริง 2026-08-19
from scripts.portfolio_builder import allocate_80_20
from scripts.portfolio_state import BOARD_LOT, rebalance_topup


def _state(price):        # <-- module-level function ไม่ใช่ method ของ class

# new
from scripts.portfolio_builder import allocate_80_20
from scripts.portfolio_state import BOARD_LOT, compute_buy_plan


def _state(price, cash, total_value):
    return {
        "positions": [{"sym": "AAA", "current_value": 0.0, "price": price}],
        "cash": cash,
        "total_value": total_value,
    }
```

```python
# current (tests/test_portfolio_math.py:23) — class เริ่มบรรทัด 23 ไม่ใช่ 24
class PortfolioTopupTests(unittest.TestCase):

# current (tests/test_portfolio_math.py:49) — ห้ามแตะตั้งแต่บรรทัดนี้ถึง 63
class PortfolioBuilderWeightTests(unittest.TestCase):

# new — contract ใหม่: ไม่มี new_money แล้ว เงินสดอยู่ใน state
class BuyPlanTests(unittest.TestCase):
    def test_board_lot_actual_spend_and_cash_remainder(self):
        st = _state(price=30.0, cash=10_000, total_value=10_000)
        plan = compute_buy_plan(st, {"AAA": 95, "cash": 5})
        rows = {r["sym"]: r for r in plan["rows"]}
        self.assertEqual(rows["AAA"]["shares_to_buy"] % BOARD_LOT, 0)
        self.assertEqual(rows["AAA"]["baht"],
                         rows["AAA"]["shares_to_buy"] * 30.0)
        # ผลรวมต้องเท่าเงินสดตั้งต้นเป๊ะ — เงินห้ามหายระหว่างทาง
        self.assertAlmostEqual(
            sum(r["baht"] for r in plan["rows"]), 10_000, places=2)
        # แถวเงินสดต้องเป็นแถวสุดท้ายเสมอ
        self.assertEqual(plan["rows"][-1]["sym"], "cash")

    def test_expensive_lot_does_not_strand_money(self):
        # RICH ล็อตละ 19,000 ขาดเป้าเยอะสุด แต่ซื้อไม่ไหวด้วยเงิน 12,000
        # CHEAP ล็อตละ 1,000 ขาดเป้าน้อยกว่า แต่ซื้อไหว -> เงินต้องไปที่ CHEAP
        # ของเดิมจะแบ่งเงินให้ RICH ตามสัดส่วนช่องว่าง แล้วปัดลงเหลือ 0 หุ้น
        # เงินก้อนนั้นตกเป็นเงินสดหายไปเฉยๆ — เทสนี้กันไม่ให้กลับมา
        ...
        self.assertGreater(rows["CHEAP"]["shares_to_buy"], 0)
        self.assertLess(rows["cash"]["baht"], 1_000)
```
