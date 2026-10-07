---
project: MaxMahon
created: 2026-04-20
last_updated: 2026-04-20
status: done
---

# Data Adapter Niwes Readiness + Backtest Framework

> Part 1 of 8 — Index: niwes-master-index | Depends on: rename-master-index (paths อ้าง projects/MaxMahon/) | Parallel-safe with: none — verify data adapter รองรับ Niwes filters (5-5-5-5) + extend missing fields + backtest 10 ปีย้อนหลังเพื่อพิสูจน์สูตรก่อนเชื่อ

## Phase 1: Data Audit
- [x] Read `projects/MaxMahon/scripts/fetch_data.py` + `projects/MaxMahon/scripts/data_adapter.py` ทั้งไฟล์ — document field ที่มีต่อ stock ใน `projects/MaxMahon/docs/niwes/00-data-schema.md`: list ครบทุก field, source (thaifin/yfinance), unit, year coverage. Highlight: dividend_history dict, count_dividend_streak() function — Acceptance: schema doc แสดงครบทุก field + ระบุ Niwes requirement gap (อะไรขาด เช่น normalized_earnings, payout_sustainability, hidden_value_flag)
- [x] Verify dividend streak coverage ใน universe จริง: รัน `cd projects/MaxMahon && py -c "from scripts.data_adapter import fetch_stock_data; from scripts.fetch_data import count_dividend_streak; import json; symbols = ['CPALL.BK', 'TCAP.BK', 'PTT.BK', 'SCB.BK', 'KBANK.BK']; results = {s: count_dividend_streak(fetch_stock_data(s).get('dividend_history', {})) for s in symbols}; print(json.dumps(results, indent=2))"` — verify ทุก symbol ได้ streak >= 5 ที่จริง. ถ้า data ไม่ครบ → flag ใน schema doc — Acceptance: output แสดง streak ทุก symbol + identify ปัญหาถ้ามี

## Phase 2: Extend missing fields
- [x] เพิ่ม function `compute_normalized_earnings(stock_data)` ใน `projects/MaxMahon/scripts/data_adapter.py` — ตัด extraordinary items ออก: เอา net_income แล้วลบ items ที่ flag เป็น 'extraordinary' หรือ 'one-time' (ใช้ keyword match ใน item name หรือถ้า thaifin มี field ระบุ exclude). Return normalized_eps. — Scope: ห้ามแก้ existing fetch_stock_data signature, แค่ append field. — Acceptance: import ใช้ได้, ตัวอย่าง CPALL ปี 2566 normalized_eps != raw eps ถ้ามี extraordinary
- [x] เพิ่ม function `compute_payout_sustainability(stock_data)` ใน `data_adapter.py` — return dict {year: payout_ratio, sustainable: bool}. Sustainable = payout < 80% AND fcf_yield > dividend_yield (จ่ายจาก cash จริง ไม่ใช่หนี้). — Acceptance: function return dict ถูก format + ตัวอย่าง CPALL ปี 2566 sustainable=true
- [x] เพิ่ม field `hidden_value_flag` ใน stock_data dict — manual flag จาก `projects/MaxMahon/data/hidden_value_holdings.json` (ไฟล์ใหม่: bootstrap จาก ดร.นิเวศน์ research เคส QH→HMPRO, MBK→MBK Spaces, etc.). Function `check_hidden_value(symbol)` อ่าน JSON, return list ของ {parent, holding, market_value_ratio}. — Acceptance: hidden_value_holdings.json มี ≥5 entries + check_hidden_value('QH.BK') return data ของ HMPRO ถือ

### Reference
```python
# current data_adapter.py (existing function as reference)
def fetch_stock_data(symbol: str) -> dict:
    # returns: financials, dividend_history, ratios, etc.
    ...

# new — append functions (ห้ามแก้ existing)
def compute_normalized_earnings(stock_data: dict) -> dict:
    # exclude extraordinary items, return {year: normalized_eps}
    ...

def compute_payout_sustainability(stock_data: dict) -> dict:
    # return {year: {payout_ratio, sustainable: bool}}
    ...

def check_hidden_value(symbol: str) -> list:
    # read hidden_value_holdings.json, return [{parent, holding, market_value_ratio}]
    ...
```

## Phase 3: Backtest framework — พิสูจน์ก่อนเชื่อ
- [x] สร้าง `projects/MaxMahon/scripts/backtest_niwes.py` — backtest 5-5-5-5 portfolio 10 ปีย้อนหลัง (2557→2568): ทุกปีต้นปี apply Niwes filter (yield≥5%, streak≥5, P/E≤15, P/BV≤1.5, no loss 5y), เลือก top 10 หุ้น equal weight, hold 1 ปี, rebalance, accumulate return + dividend. Output: yearly return list + total return + max drawdown + Sharpe vs SET50 benchmark. ใช้ thaifin historical + yfinance prices. — Scope: ห้ามรันจริงตอน build (data fetch ใหญ่) — แค่ implement + dry-run 1 ปี (2566) เพื่อ verify code work. — Acceptance: dry-run 2566 ออก output, code มี comment ระบุวิธีรัน full backtest
- [x] Document backtest result format ที่ `projects/MaxMahon/docs/niwes/00-backtest-protocol.md` — format JSON output, วิธี interpret (ถ้า return < SET50 → ทบทวน threshold หรือ regime change), recommendation: รัน backtest หลัง niwes-04-framework-migration เสร็จ + เก็บผลลัพธ์เป็น baseline สำหรับ Plan 06 integration loop. — Acceptance: doc exists + ระบุ threshold judgment criteria ชัด
