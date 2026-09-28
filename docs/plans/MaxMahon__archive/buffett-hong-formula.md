---
project: MaxMahon
created: 2026-04-12
last_updated: 2026-04-12
status: done
---

# Max Mahon — Buffett Hong Formula ปรับสูตรให้ตรงหลักการ + เหมาะตลาดไทย

> ปรับสูตรคัดหุ้นให้ตรงหลักการ Buffett จริงๆ + เหมาะกับตลาดไทย — ROE แยก sector, valuation น้ำหนักใหม่, แก้ข้อมูล yfinance ที่ขาด/ผิด, ใช้ SG&A ที่มีอยู่แล้ว

## Phase 1: Hard Filter + Data — ปลดล็อก sector ที่ถูกตัดผิด
- [x] แยก ROE hard filter ตาม sector — financial: avg ≥ 10% floor ≥ 8% (ธนาคารไทย ROE 7-9% ปกติ), non-financial: คงเดิม avg ≥ 15% floor ≥ 12% + เพิ่ม is_financial check ใน ROE section ของ hard_filter() เหมือนที่ทำกับ D/E และ net margin อยู่แล้ว
- [x] แก้ metrics.de ส่ง dashboard ผิด 100 เท่า — screen_stocks.py main() ตอนสร้าง entry['metrics'] ต้อง /100 สำหรับ debt_to_equity จาก info + แก้ five_year_avg_yield null fallback — คำนวณจาก dividend_history (avg DPS 5 ปีล่าสุด / current_price * 100) เมื่อ info field เป็น null

### Reference
```python
# screen_stocks.py hard_filter() — current ROE (no sector split)
if avg_roe < HARD_FILTERS["min_roe_avg"] - 0.005:
    reasons.append(f"avg ROE {avg_roe*100:.0f}% < 15%")

# new — split by sector
roe_target = 0.10 if is_financial else HARD_FILTERS["min_roe_avg"]
roe_floor = 0.08 if is_financial else HARD_FILTERS["min_roe_floor"]
if avg_roe < roe_target - 0.005:
    reasons.append(f"avg ROE {avg_roe*100:.0f}% < {roe_target*100:.0f}%")
if min_roe < roe_floor - 0.005:
    reasons.append(f"min ROE {min_roe*100:.0f}% < {roe_floor*100:.0f}%")

# metrics.de fix
"de": (data.get("debt_to_equity") or 0) / 100,  # yfinance returns percentage

# five_year_avg_yield fallback
five_yr_yield = data.get("five_year_avg_yield")
if five_yr_yield is None and data.get("dividend_history") and data.get("price"):
    dh = data["dividend_history"]
    recent_5 = sorted(dh.keys())[-5:]
    if recent_5:
        avg_dps = sum(dh[y] for y in recent_5) / len(recent_5)
        five_yr_yield = avg_dps / data["price"] * 100 if data["price"] > 0 else None
```

## Phase 2: Scoring — ปรับน้ำหนัก + ใช้ข้อมูลที่มี
- [x] ปรับ valuation_grade น้ำหนักใหม่ — PEG 20%, P/E vs sector 35%, yield vs 5y avg 30%, 52w position 15% (ลดจาก 25% เพราะเป็น technical ไม่ใช่ fundamental) + sector median P/E ต้องใส่ข้อมูลเพิ่ม note ว่าคำนวณจากหุ้นที่ผ่าน filter เท่านั้น
- [x] เพิ่ม SG&A ratio เข้า profitability_score — SG&A/Revenue < 0.30 ให้ 3 pts จากส่วน gross margin (ปรับ gross margin จาก 10 pts เป็น 7 pts + SG&A 3 pts = ยังรวม 10 pts) + แก้ OCF/NI > 1.5 ใน strength_score ให้ได้ 5 pts เต็ม (depreciation-heavy businesses ไม่ควรโดนลดคะแนน) เปลี่ยน range จาก 0.8-1.5 เป็น 0.8-3.0 สำหรับ full score

### Reference
```python
# valuation_grade — new weights
# PEG (20 pts instead of 25)
if peg and peg < 1: score += 20
elif peg and peg < 2: score += 12
elif peg and peg < 3: score += 4

# P/E vs sector (35 pts instead of 25)
if pe and pe < median_pe * 0.8: score += 35
elif pe and pe < median_pe * 1.2: score += 21
elif pe and pe < median_pe * 2: score += 7

# Yield vs 5y avg (30 pts instead of 25)
if ratio > 1.3: score += 30
elif ratio > 0.9: score += 18
elif ratio > 0.6: score += 6

# 52w position (15 pts instead of 25)
if pos_52w < 0.3: score += 15
elif pos_52w < 0.6: score += 9
elif pos_52w < 0.8: score += 3

# profitability_score — add SG&A
# Gross Margin (7 pts instead of 10)
if avg_gm >= 0.40: score += 7
elif avg_gm >= 0.30: score += 5
elif avg_gm >= 0.20: score += 3
# SG&A efficiency (3 pts — new)
sga_vals = [m["sga_ratio"] for m in yearly if m.get("sga_ratio") is not None]
if sga_vals:
    avg_sga = sum(sga_vals) / len(sga_vals)
    if avg_sga < 0.30: score += 3
    elif avg_sga < 0.50: score += 1

# strength_score — OCF/NI fix
if 0.8 <= ocf_ni <= 3.0:
    score += 5  # was 1.5 ceiling
elif 0.5 <= ocf_ni:
    score += 3
```

## Phase 3: อัพเดต CLAUDE.md + เพิ่ม note หลักการ
- [x] อัพเดต CLAUDE.md — แก้ Hard Filters section เพิ่ม ROE financial sector, แก้ Quality Score table ใส่ SG&A, แก้ references note ว่าเซียนฮงไม่มีเกณฑ์ตัวเลขชัดเจน (เป็นการสังเกตพอร์ต) + เพิ่ม Data Quality Notes section บอกข้อจำกัด yfinance สำหรับหุ้นไทย (ธนาคาร data ว่าง, five_year_avg_yield null บ่อย, debt_to_equity เป็น %)

### Reference
```markdown
## Hard Filters
- ROE เฉลี่ย ≥ 15% non-financial / ≥ 10% financial (ไม่มีปีต่ำกว่า 12% / 8%)

## Quality Score (100 คะแนน)
| Profitability | 30 | ROE consistency (15) + Gross Margin (7) + SG&A efficiency (3) + Net Margin trend (5) |

## References
- เซียนฮง สถาพร: เน้น cash flow quality, ความสม่ำเสมอ, หนี้น้อย (เกณฑ์ตัวเลขเช่น P/E ≤ 15 มาจากการวิเคราะห์พอร์ตโดย secondary sources ไม่ใช่เกณฑ์ที่แกประกาศ)

## Data Quality Notes (yfinance .BK)
- ธนาคารไทย: yearly_metrics ส่วนใหญ่ null → ใช้ info fallback
- five_year_avg_yield: null บ่อย → fallback คำนวณจาก dividend_history
- debt_to_equity จาก info: เป็น percentage (ต้อง /100)
```
