---
date: 2026-05-19
source: docs/niwes/04-criteria.md (13 เกณฑ์)
purpose: แผนที่ว่า criteria ของ Niwes คลุมไปแค่ไหนใน manual ranking 2026-05-19
---

# Niwes Criteria Coverage Map

ดร.นิเวศน์ มี **13 เกณฑ์** ใน criteria.md — manual ranking 2026-05-19 คลุมไปแค่ครึ่ง ที่เหลือยังไม่ได้

## Visual Matrix

```
                      เลขได้ (Quant)                  ต้องคนคิด (Qual)
                  ┌─────────────────────┬─────────────────────┐
                  │  #1 yield ≥5% ตอนนี้  │                     │
   ✅ คลุมแล้ว     │  #3 PBV <1.0         │  #12 diversify       │
                  │  #4 yield normalized │       5+ หุ้น/sector  │
                  │  #5 dividend จาก op  │                     │
                  │  #6 รายได้/กำไร/     │                     │
                  │      ปันผล ขึ้นทุกปี  │                     │
                  ├─────────────────────┼─────────────────────┤
                  │  #2 yield ≥5%        │  #7 ธุรกิจ 3+ ปี      │
   ⏳ ยังไม่คลุม   │      อีก 5 ปี        │  #9 moat / mid-tier  │
                  │  #8 hidden value     │  #10 daily-use      │
                  │  #11 ROE 10y + no    │  #13 geographic     │
                  │       loss           │       30/30/30      │
                  └─────────────────────┴─────────────────────┘
```

## Status Table

| # | เกณฑ์ Niwes | ดูจากอะไร | สถานะ | หมายเหตุ |
|:---:|---|---|:---:|---|
| 1 | yield ≥5% ตอนนี้ | snapshot DPS/ราคา | ✅ | filter หลัก ผ่าน 55/56 (ตัด AWC) |
| 2 | yield ≥5% อีก 5 ปี | ต้องคาดการณ์ | ⏳ | ใช้ DPS trend + payout sustainability พอประมาณได้ |
| 3 | PE 7-8 (target) | snapshot | ✅ | 5-5-5-5 floor PE ≤15 ผ่านหมด |
| 4 | PBV <1.0 | snapshot | ✅ | algo 5-5-5-5 ตัด PBV >1.5 — ลึกกว่านี้ต้องไล่ดู |
| 5 | จ่ายปันผลจาก operating profit (เงินสดเหลือเฟือ) | OCF/FCF/Cash 3 ปี | ✅ | manual ranking score 5 ข้อ มี 3 ข้อจากนี้ |
| 6 | รายได้/กำไร/ปันผล "เพิ่มทุกปี" | strict YoY 3 ปี | ✅ | strict pairwise — ⓓ + ⓡ ใน score |
| 7 | ธุรกิจอยู่กับเรา 3+ ปี | qualitative — sector + structural | ⏳ | ต้องคนตัดสิน (FaceID/cement/banking ทน — tech/fashion ไม่ทน) |
| 8 | Hidden Value (sum-of-parts > mcap) | look-through holdings | ⏳ | algo flag `HIDDEN_VALUE` แต่ยังไม่ pull มาดู QH style |
| 9 | Moat / mid-tier ที่โตได้ | qualitative — market position | ⏳ | คนคิด: BBL ใหญ่อิ่ม / KKP กลาง runway ยาวกว่า |
| 10 | Daily-use + ไม่ sexy | qualitative — consumer behavior | ⏳ | HTC = โค้กใต้ ✓ / ROJNA = นิคม ไม่ daily แต่ structural |
| 11 | ROE consistent + ไม่ขาดทุน 10y | net_income + roe 10 ปี | ⟳ | กำลังทำ — pull data + แสดง bar 10 ปี |
| 12 | กระจาย 5+ หุ้น 5+ sector | portfolio | ✅ | 5-5-5-5 floor #3 — manual ranking มี 18 sector ครอบ |
| 13 | Geographic 30/30/30/Cash | portfolio struct | ⏳ | Niwes ล่าสุด (2024) ย้ายไป US/Vietnam — ตลาดไทยอย่างเดียวเสี่ยง |

## 4 เกณฑ์ที่ยังต้องเก็บ (เลขได้)

| ข้อ | ทำยังไง | ใช้ data ไหน |
|---|---|---|
| #2 yield 5 ปีหน้า ≥5% | project DPS forward + assume price flat | DPS growth rate × current price |
| #8 Hidden Value | check listed subsidiary holdings vs mcap | `hidden_value_holdings.json` (algo มีอยู่) |
| #11 ROE 10y + no loss | ROE trend + count loss years | yearly_metrics.roe + net_income 10 ปี |
| (extra) D/E + Interest Coverage | balance sheet ratio | yearly_metrics.de_ratio + interest_coverage |

## 4 เกณฑ์ที่ algo ทำไม่ได้ (คนคิด)

| ข้อ | กระบวนการ | ตัวอย่าง |
|---|---|---|
| #7 ธุรกิจ 3+ ปี | ดู structural change ของ sector | MAJOR สู้ streaming ไม่ไหว / SCCC ยังขายปูน |
| #9 Moat / mid-tier | เทียบกับคู่แข่งใน sector | KBANK vs SCB vs BBL — ใครยังมี runway? |
| #10 Daily-use + ไม่ sexy | คิดถึงพฤติกรรมผู้บริโภค | ILM ค้าปลีกบ้าน daily ✓ / NER ยาง — daily น้อย |
| #13 Geographic | portfolio strategy | Niwes ย้าย Thai 65→30% 2024 |

## ลำดับงานต่อ

1. ⟳ **ROE 10y + D/E ทุกตัว** (กำลังทำใน manual ranking file)
2. ⏳ Hidden Value pull จาก `data/hidden_value_holdings.json` ดู QH/MBK/TCAP style ใน 55 ตัว
3. ⏳ Forward yield projection (DPS growth × current price ใส่ในตาราง)
4. ⏳ Moat tag manual review ตัว Tier S+A
5. ⏳ Geographic — discuss portfolio construction (separate convo)
