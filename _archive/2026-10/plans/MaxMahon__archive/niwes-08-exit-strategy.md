---
project: MaxMahon
created: 2026-04-20
last_updated: 2026-04-20
status: done
---

# Exit Strategy — Sell Rules + Structural Risk Monitor

> Part 8 of 8 — Index: niwes-master-index | Depends on: niwes-02-research-report, niwes-04-framework-migration | Parallel-safe with: niwes-07 — Niwes สอนเลือกหุ้นแต่ไม่สอนขาย — Plan นี้เพิ่ม exit rules (เคส OR), structural risk monitor (Thai macro), exit decision template — เพื่อ Karl ลงทุน 100M ปันผลโดยไม่ติดในตลาดที่ structural broken

## Phase 1: Document Niwes Exit Rules (จาก research)
- [x] สร้าง `projects/MaxMahon/docs/niwes/15-exit-rules.md` — รวบรวม exit rules จาก research (`projects/MaxMahon/docs/niwes/09-case-or-exit.md` + interview quotes): (1) Thesis change (business model เปลี่ยน, moat หาย), (2) Filter degradation (ผ่าน 5-5-5-5 → fail = sell signal), (3) Valuation overshoot (P/E > 25 จาก base 8 = bubble territory), (4) Better opportunity (rotate ไป opportunity ที่ดีกว่า), (5) Capital need (Karl personal). แต่ละ rule + verbatim quote + เคส example. — Acceptance: ≥5 rules + ทุกข้อ verbatim quote + ตัวอย่างเคสจริง
- [x] เพิ่ม rule 'When NOT to sell' (ดร.นิเวศน์ถือ CPALL 17 ปี): (1) Short-term price drop (<30%) ที่ thesis ยังอยู่ — ห้ามขายตามอารมณ์, (2) Sector rotation noise — ดูธุรกิจ ไม่ดู price, (3) Macro fear ที่ไม่กระทบ business directly. — Acceptance: 'When NOT to sell' section ครบ ≥3 rules

## Phase 2: Exit Signal Detection ใน Screener
- [x] เพิ่ม function `detect_exit_signal(symbol, current_data, historical_baseline)` ใน `projects/MaxMahon/scripts/screen_stocks.py` — return list ของ exit triggers: (1) FILTER_DEGRADATION (เคยผ่าน 5-5-5-5 → ตอนนี้ fail field ไหน), (2) VALUATION_BUBBLE (P/E > P/E_baseline * 3), (3) THESIS_CHANGE_FLAG (manual flag จาก news monitoring Plan 07). Function รันต่อหุ้นใน watchlist (ไม่ใช่ทั้ง universe). — Scope: ห้าม auto-sell — แค่ flag. — Acceptance: function return list of triggers ต่อ symbol
- [x] เพิ่ม signal tag `EXIT_SIGNAL` ใน scan output — ถ้าหุ้นใน watchlist มี exit trigger → tag + แสดงใน scan report section ใหม่ 'Watchlist Exit Alerts'. — Acceptance: scan report มี section ใหม่ + แสดง symbols ที่มี trigger

## Phase 3: Structural Risk Monitor (Thai macro)
- [x] สร้าง `projects/MaxMahon/scripts/monitor_thai_macro.py` — pull macro indicators ที่ ดร.นิเวศน์ใช้ assess structural Thai issue: (1) Thai GDP growth (จาก BOT API หรือ tradingeconomics), (2) Foreign Direct Investment (FDI) inflows trend, (3) Current Account Balance, (4) Foreign holdings ใน SET (จาก SET data), (5) Demographic dependency ratio (NESDB). Save snapshot ที่ `projects/MaxMahon/data/thai_macro_{date}.json`. — Scope: ใช้ public API/scrape เท่านั้น — ห้าม paid data source. ถ้า indicator ไม่มี free source → flag 'manual update' + skip. — Acceptance: script รันได้ + JSON มี ≥3 indicators
- [x] สร้าง `projects/MaxMahon/scripts/structural_risk_score.py` — คำนวณ Structural Risk Score จาก macro snapshot: 0-100 (0 = healthy, 100 = severe structural break). Formula simple: ถ่วงน้ำหนัก trend ของแต่ละ indicator (GDP declining 3y = risk +30, FDI declining = +25, Foreign holdings declining = +25, Dependency ratio rising fast = +20). Output trigger ถ้า score > 70 → 'reduce Thai allocation per ดร.นิเวศน์ playbook (60→30%)'. — Acceptance: function return score + recommendation

## Phase 4: Karl Exit Decision Template
- [x] สร้าง `projects/MaxMahon/docs/niwes/16-exit-decision-template.md` — template Karl ใช้ตอนตัดสินใจขาย: (1) Symbol + buy info (entry date, price, current price), (2) Trigger source (filter degradation / valuation / thesis / macro / personal), (3) Niwes rules check (8 ข้อจาก 15-exit-rules.md — แต่ละข้อ TRIGGERED/NOT), (4) Decision + reasoning (paragraph), (5) Action (full sell / partial sell / hold). — Acceptance: template + 1 example fill (เคส OR ของ ดร.นิเวศน์)
- [x] เพิ่ม API endpoint `/api/exit_check/{symbol}` ใน `projects/MaxMahon/server/app.py` — รับ symbol, return JSON: {triggers: [...], niwes_rules_check: {...}, structural_risk_score: N, recommendation: 'HOLD'|'REVIEW'|'CONSIDER_EXIT'}. ใช้ functions จาก Phase 2-3. — Scope: ห้าม auto-execute trade — informational only. — Acceptance: endpoint return JSON ถูก format + ทดสอบกับ symbol ใน watchlist ใช้ได้
