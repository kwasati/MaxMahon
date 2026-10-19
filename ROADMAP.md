# maxmahon Roadmap
SSOT · ทุกแถว = ชื่อ + สถานะสั้น + path ใบ · เนื้ออยู่ในใบ `roadmap\` · งานเสร็จย้ายไป `roadmap\closed.md` · กติกา `C:\WORKSPACE\_shared\docs\workflow\index-tree.md`

## สถานะ
| เรื่อง | สถานะ | ใบ |
|---|---|---|
| ใช้งานอยู่ = ชุดสคริปต์ผ่านแชท (web + server เก็บแล้ว 2026-10-07) | v7.0.0 (2026-10-09): ด่าน + ใบข้อเท็จจริง + ตัวเฝ้าหุ้นที่ถือ + deep dive ครบ 8 ตัว ไม่มีคะแนน 0–100 · ตรวจแผนจัดพอร์ต กับ วิเคราะห์หุ้นที่ถือ รอ Art ตัดสิน | `roadmap\queue-selection-rebuild.md` |

## ลำดับงาน
| คิว | ชื่อ | สถานะ | ใบ | desk |
|---:|---|---|---|---|
| 1 | ตรวจสูตร / แผนการจัดพอร์ตว่าถูกจริงไหม | สูตรใน `rebalance.py` ตรวจแล้วคิดถูก (ตอน review สคริปต์ทั้งหมด) · รอคุยกับ Art: แผนเงินสดซื้อของถูก + วิธีเกลี่ยเศษ | `roadmap\queue-rebalance-formula-check.md` | |
| 2 | วิเคราะห์หุ้นที่ถืออยู่ตอนนี้ใหม่ — แนวโน้ม + ต้องปรับแผนไหม | deep dive ครบ 8 ตัว 2026-10-09 · รอ Art ตัดสิน 9 เรื่อง (รายการในใบ) | `roadmap\queue-holdings-reanalysis.md` | |
| 3 | เกลาหลัก deep dive ขา Niwes | ลุย: แก้ระบบ 10 ใบงาน (DeepSeek ค่าเริ่ม) · ใบ 1 ที่มา yield ผ่าน (2b3fa4a) · ต่อใบ 2 → deep dive ใหม่ทั้งเล่ม AMATA BBL TCAP | `roadmap\queue-niwes-deepdive-principles.md` | z79h |

## ข้อตกลงที่ล็อก
| งานแตะเรื่อง | ใบ |
|---|---|
| จัดพอร์ต | `roadmap\agreed-portfolio-rebalance.md` |
| กฎ scan | `roadmap\agreed-scan-rules.md` |
| กรอบพอร์ต 70/25/5 | `roadmap\agreed-portfolio-framework.md` |
| สายคัดหุ้น (ด่าน / ใบข้อเท็จจริง / deep dive / คะแนน) | `roadmap\agreed-selection-system.md` |

## เสร็จแล้ว / ปิดถาวร
| เรื่อง | ใบ |
|---|---|
| งานที่เสร็จ / ปิด (รู้ว่ามี ไม่ต้องอ่านทุกครั้ง · ปิดถาวร = อย่าเสนอซ้ำ) | `roadmap\closed.md` |
