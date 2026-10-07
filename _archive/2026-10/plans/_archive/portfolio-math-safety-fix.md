---
project: 4-MaxMahon
created: 2026-07-27
last_updated: 2026-07-27
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: เครื่องคำนวณเติมเงินของพอร์ต A/B/C หยุดเมื่อราคาหาย แนะนำหุ้นเป็นชุดละ 100 หุ้น แสดงช่องว่างเป็นเปอร์เซ็นต์พอร์ตจริง และพอร์ตแนะนำรวมน้ำหนัก 100.0%

### รายละเอียด
- ถ้าหุ้นในแผนตัวใดไม่มีราคาหรือราคาไม่มากกว่าศูนย์ ให้หยุดคำนวณและบอกให้ดึงราคาใหม่
- หุ้นไทยซื้อเป็นชุดละ 100 หุ้น เงินที่ใช้ซื้อหุ้นต้องเท่ากับจำนวนหุ้นคูณราคา
- เงินที่เหลือจากการปัดชุดซื้อให้รวมในช่องเงินสด เพื่อให้ยอดจัดสรรรวมเท่ากับเงินใหม่
- ค่าเปอร์เซ็นต์ที่ขาดต้องเป็นช่องว่างเทียบมูลค่าพอร์ตหลังเติมเงิน ไม่ใช่เทียบเงินใหม่
- หุ้นที่ยังขาดแต่เงินไม่ถึงหนึ่งชุดต้องไม่ถูกแสดงว่าเกินหรือตรงเป้า
- เมื่อพอร์ตแนะนำมีน้อยกว่า 5 ตัว น้ำหนักหลังปัดเศษต้องรวม 100.0%

### Scope Boundary
**In scope:**
- projects/4-MaxMahon/scripts/portfolio_state.py
- projects/4-MaxMahon/scripts/portfolio_builder.py
- projects/4-MaxMahon/web/v6/static/js/pages/portfolio-home.js
- projects/4-MaxMahon/web/v6/static/js/pages/portfolio-home.mobile.js
- projects/4-MaxMahon/tests/__init__.py
- projects/4-MaxMahon/tests/test_portfolio_math.py

**Out of scope:**
- สูตรคะแนนคัดหุ้นและการจัดอันดับ
- targets และ holdings ใน data/portfolios
- ระบบดึงราคาและ price cache
- หน้าพอร์ต builder รุ่นเก่าและไฟล์ archive

### Non-goals
- ไม่เปลี่ยนสัดส่วนเป้าหมายของพอร์ต A/B/C
- ไม่เพิ่มการซื้อขาย odd lot
- ไม่แก้ข้อมูลพอร์ตหรือราคาปัจจุบัน

# Portfolio Math Safety Fix

> แก้บั๊กคำนวณใน flow เติมเงินและน้ำหนักพอร์ต โดยรักษาสูตรแบ่งเงินตามช่องว่างเดิม แต่ทำให้ผลลัพธ์ซื้อได้จริงและสื่อความหมายถูกต้อง

## Phase 1: Safe portfolio calculations
- [x] แก้ `projects/4-MaxMahon/scripts/portfolio_state.py` ให้ตรวจราคาทุกหุ้นก่อนคำนวณ เปลี่ยนจำนวนซื้อเป็นชุดละ 100 หุ้น คิดยอดหุ้นจากจำนวนที่ซื้อจริง ย้ายเงินปัดเศษไปเงินสด และคำนวณเปอร์เซ็นต์ขาดจากมูลค่าพอร์ตหลังเติมเงิน โดยห้ามเปลี่ยนสูตรแบ่งเงินตามช่องว่างเดิม — Acceptance: ราคาหาย raise ValueError; หุ้นทุกตัวที่ซื้อหาร 100 ลงตัว; `sum(baht)` เท่ากับเงินใหม่; `baht` หุ้นเท่ากับ shares คูณ price; เปอร์เซ็นต์ขาดไม่ใช้เงินใหม่เป็นตัวหาร
- [x] แก้ `projects/4-MaxMahon/scripts/portfolio_builder.py` ให้ชดเชยเศษปัดน้ำหนักที่ตัวสุดท้าย โดยห้ามเปลี่ยนลำดับและน้ำหนักฐาน — Acceptance: จำนวนตัว 1 ถึง 5 รวมน้ำหนัก 100.0% ทุกกรณี และกรณี 5 ตัวยังคง 40/35/12/8/5
- [x] แก้ `projects/4-MaxMahon/web/v6/static/js/pages/portfolio-home.js` และ `projects/4-MaxMahon/web/v6/static/js/pages/portfolio-home.mobile.js` ให้แสดงเฉพาะยอดซื้อจริง แสดงเงินเหลือในช่องเงินสด และแยกหุ้นที่ยังขาดแต่เงินไม่ถึง 100 หุ้นออกจากหุ้นเกินหรือตรงเป้า — Acceptance: desktop และ mobile ใช้กติกาเดียวกัน ไม่มีแถวบอกซื้อหุ้น 0 หุ้น และไม่เรียกหุ้นขาดว่าเกินหรือตรงเป้า
- [x] สร้าง `projects/4-MaxMahon/tests/test_portfolio_math.py` ด้วย unittest ครอบราคาหาย หน่วย 100 หุ้น ยอดเงินจริง เปอร์เซ็นต์ขาด และน้ำหนัก 1 ถึง 5 ตัว — Acceptance: `py -m unittest tests.test_portfolio_math -v` ผ่านทั้งหมด และ `py -m py_compile scripts/portfolio_state.py scripts/portfolio_builder.py` ผ่าน

### Reference
```python
# current (scripts/portfolio_state.py:367-368, 389-405, 417-418)
tval = base_new * float(targets.get(s, 0) or 0) / 100.0
deficit[s] = max(0.0, tval - cv.get(s, 0.0))
baht = {s: _round2(topup.get(s, 0.0)) for s in slots}
shares_to_buy = int(math.floor(baht[s] / price))
(deficit.get(s, 0.0) / new_money * 100) if new_money > 0 else 0.0

# new
# reject missing or invalid prices before allocation
# keep ideal top-up math, floor stock purchases to BOARD_LOT = 100
# set stock baht to shares_to_buy * price and move all residual to cash
# deficit_pct = deficit / base_new * 100

# current (scripts/portfolio_builder.py:112-118)
base = DEFAULT_WEIGHTS[:n]
total = sum(base)
weights = [round(w / total * 100, 1) for w in base]
for s, w in zip(picks, weights):
    s['weight_pct'] = w

# new
base = DEFAULT_WEIGHTS[:n]
total = sum(base)
weights = [round(w / total * 100, 1) for w in base]
weights[-1] = round(100.0 - sum(weights[:-1]), 1)
for s, w in zip(picks, weights):
    s['weight_pct'] = w

# current (portfolio-home desktop/mobile)
const isBuy = (r.status === 'under') && ((r.baht || 0) > 0);
if (isBuy) buys.push(r);
else skips.push(r);

# new
# rows with executable stock shares or positive cash are shown
# underweight rows with zero executable shares are grouped as below-board-lot
# over/on-target rows remain separate
```
