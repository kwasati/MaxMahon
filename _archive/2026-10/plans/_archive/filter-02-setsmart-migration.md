---
project: 4-MaxMahon
created: 2026-05-12
last_updated: 2026-05-18
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: รัน scheduler job ดึง SETSMART งบ 5 ปี × 4 ไตรมาส (20 records ต่อหุ้น) เข้า cache + fetch_fundamentals ใช้ SETSMART เป็น primary สำหรับ ROE/ROA/D/E/EPS งบ 5 ปีล่าสุด + thaifin fallback สำหรับ history > 5 ปี + เลิก fetch yahoo redundant สำหรับ snapshot ที่ SETSMART มีครบ + scan 933 หุ้น yahoo API calls ลด > 50%

### รายละเอียด
- SETSMART subscription = 5 ปีย้อนหลัง (verified ผ่าน live probe data/research/setsmart_depth_probe_2026-05-12.json) — ขอเกิน 5 ปี HTTP 400
- fetch_financial_by_symbol(symbol, start_year, start_quarter, end_year, end_quarter) คืน 20 records ต่อ symbol (5 ปี × 4 quarter)
- fields ที่ SETSMART งบให้: totalAssets, totalLiabilities, shareholderEquity, totalRevenueQuarter/Accum, netProfitQuarter/Accum, epsQuarter/Accum, operatingCashFlow, investingCashFlow, financingCashFlow, roe, roa, de, netProfitMarginQuarter/Accum, fixedAssetTurnover, totalAssetTurnover
- ปัจจุบัน financial cache (data/setsmart_cache/financial_*.json) = ว่างเปล่า เพราะไม่มี scheduler job เรียก cached_financial_bulk
- ปัจจุบัน fetch_fundamentals (data_adapter.py:676-904) fetch yahoo ก่อนเสมอ (line 754-774) แล้ว override ด้วย SETSMART (line 830-861) — wasted yahoo calls
- Snapshot fields ที่ migrate: price, dividend_yield (snapshot), pe_ratio, pb_ratio, market_cap, roe (snapshot), roa, de, eps_accum (latest year)
- ROE/ROA/D/E history > 5 ปี → thaifin (มี 16 ปี — verified BBL 2010-2025)
- SETSMART งบ quarterly granularity — ดี: ได้ trend Q1/Q2/Q3/Q4 trailing, ไม่ต้องรอ thaifin update รายปี
- scheduler job ใหม่: ดึง SETSMART งบ quarterly ทุก 19:00 (หลัง EOD refresh) — ใช้ cached_financial_bulk(year, quarter) สำหรับ current quarter
- Per-symbol financial range cache: เพิ่ม function cached_financial_by_symbol_range(sym, start_y, start_q, end_y, end_q) ใน setsmart_adapter.py + cache file financial_by_symbol_{sym}_{start}_{end}.json

### Scope Boundary
**In scope:**
- scripts/setsmart_adapter.py — เพิ่ม cached_financial_by_symbol_range function
- scripts/data_adapter.py — _fetch_setsmart routing + fetch_fundamentals control flow (skip yahoo เมื่อ SETSMART warm)
- scripts/daily_price_refresh.py — เพิ่ม financial refresh logic (current quarter)
- server/app.py — เพิ่ม APScheduler job financial_refresh (หรือรวมใน existing daily_price_refresh job)

**Out of scope:**
- DPS migration (Plan C — depends on this)
- REVIEW handling (Plan D)
- Normalized EPS (Plan E — depends on this)
- SETSMART EOD subscription tier change
- Migrate ออกจาก thaifin 100% — thaifin ยังจำเป็นสำหรับ history > 5 ปี + fields ที่ SETSMART ไม่มี

### Non-goals
- ไม่ตัด yahoo สำหรับ irreplaceable fields (DPS events, 52w range, capex, interest expense, monthly price)
- ไม่ refactor yahoo retry mechanism (เก็บ Stage 2 retry + integrity guard ตามเดิม)
- ไม่เปลี่ยน cache schema ของ thaifin หรือ yahoo
- ไม่เปลี่ยน trigger interval ของ existing 2 cron jobs

# Plan B — SETSMART Migration (Primary 5-Year Quarterly + Yahoo Redundant Cleanup)

> Part 2 of 7 — SETSMART migration. เปลี่ยนงบ 5 ปีล่าสุด + snapshot → SETSMART primary + thaifin/yahoo fallback. คุ้มเงิน subscription + แม่นกว่า + ลด yahoo redundant calls.
> Depends on: filter-01-year-completeness (foundation — filter logic ต้องเสถียรก่อน data source เปลี่ยน)
> Parallel-safe with: none (blocks Plan C + Plan E)

## Phase 1: SETSMART adapter — range fetch + per-symbol cache
- [x] แก้ scripts/setsmart_adapter.py — เพิ่ม function cached_financial_by_symbol_range(symbol, start_year, start_quarter, end_year, end_quarter) — ใช้ fetch_financial_by_symbol() + cache file at data/setsmart_cache/financial_by_symbol_{symbol}_{start_y}q{start_q}_{end_y}q{end_q}.json — Scope: ไม่แก้ existing functions, เพิ่ม function ใหม่เท่านั้น — Acceptance: cached_financial_by_symbol_range('BBL', '2021', '1', '2025', '4') คืน 20 records + cache file ถูก write
- [x] แก้ scripts/setsmart_adapter.py __main__ smoke test — เพิ่ม smoke 6/7 test cached_financial_by_symbol_range สำหรับ BBL 5 ปี — Acceptance: py scripts/setsmart_adapter.py แสดง '[smoke 6/7] cached_financial_by_symbol_range BBL 2021-2025 → 20 records'

### Reference
```python
# current (scripts/setsmart_adapter.py:121-127)
def cached_eod_history(symbol: str, start_date: str, end_date: str) -> list[dict]:
    cache_file = CACHE_DIR / f"eod_by_symbol_{symbol}_{start_date}_{end_date}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))
    data = fetch_eod_by_symbol(symbol, start_date, end_date)
    cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data

# new (เพิ่มหลัง cached_eod_history)
def cached_financial_by_symbol_range(symbol: str, start_year: str, start_quarter: str,
                                      end_year: str, end_quarter: str) -> list[dict]:
    """Cache SETSMART financial-data-and-ratio-by-symbol for date range.
    
    SETSMART subscription = 5 years back. To get 5y quarterly:
        cached_financial_by_symbol_range('BBL', '2021', '1', '2025', '4') → 20 records
    """
    cache_file = CACHE_DIR / f"financial_by_symbol_{symbol}_{start_year}q{start_quarter}_{end_year}q{end_quarter}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))
    data = fetch_financial_by_symbol(symbol, start_year, start_quarter, end_year, end_quarter)
    cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data
```

## Phase 2: _fetch_setsmart routing — ใช้ range cache
- [x] แก้ scripts/data_adapter.py _fetch_setsmart (บรรทัด 617-666) — เปลี่ยน logic ที่ดึง financial: แทนที่ walk newest→older ของ financial_{year}_q{quarter}.json → ใช้ cached_financial_by_symbol_range(symbol, str(current_year-4), '1', str(current_year-1), '4') เพื่อ get 5y × 4q = 20 records — Scope: ไม่แก้ EOD logic, แค่ financial path — Acceptance: _fetch_setsmart('BBL') คืน dict มี 'financial' key ที่ value = list 20 records (5y × 4q) + 'financial_quarterly' key ที่ value = dict { (year, quarter): record }
- [x] เพิ่ม helper function ใน data_adapter.py: _setsmart_financial_to_yearly(records: list[dict]) -> dict — group 4 quarters ของแต่ละปีเป็น record ปี (รวม accumulated fields + เลือก Q4 accum หรือ sum quarter values ตามความเหมาะสม) — Acceptance: คืน dict {year: {revenue, net_profit, eps, ocf, icf, fcf, roe, roa, de}} ครบ 5 ปี

### Reference
```python
# current (scripts/data_adapter.py:617-666) — _fetch_setsmart
def _fetch_setsmart(symbol: str) -> dict | None:
    """Read SETSMART cache for symbol. Returns {eod, financial} or None."""
    from setsmart_adapter import CACHE_DIR
    eod_data = None
    financial_data = None
    # ... walk newest cache file ...

# new — รับ financial เป็น range
from setsmart_adapter import cached_financial_by_symbol_range
from datetime import datetime

def _fetch_setsmart(symbol: str) -> dict | None:
    from setsmart_adapter import CACHE_DIR
    eod_data = None
    # ... existing EOD walk logic — keep as is ...
    
    # NEW: financial 5y quarterly range
    current_year = datetime.now().year
    start_y = str(current_year - 5)
    try:
        financial_records = cached_financial_by_symbol_range(
            symbol, start_y, '1', str(current_year - 1), '4'
        )
    except Exception as e:
        logger.warning("SETSMART financial fetch failed for %s: %s", symbol, e)
        financial_records = []
    
    financial_quarterly = {}
    for r in financial_records:
        y = r.get('year')
        q = r.get('quarter')
        if y and q:
            financial_quarterly[(int(y), int(q))] = r
    
    return {
        "eod": eod_data,
        "financial": financial_records,
        "financial_quarterly": financial_quarterly,
        "financial_yearly": _setsmart_financial_to_yearly(financial_records),
    }

def _setsmart_financial_to_yearly(records: list[dict]) -> dict:
    """Group 4 quarters into yearly aggregate. Use Q4 accumulated fields."""
    by_year_q4 = {}
    for r in records:
        y = r.get('year')
        q = r.get('quarter')
        if y and q == 4:
            by_year_q4[int(y)] = {
                'revenue': r.get('totalRevenueAccum'),
                'net_profit': r.get('netProfitAccum'),
                'eps': r.get('epsAccum'),
                'ocf': r.get('operatingCashFlow'),
                'icf': r.get('investingCashFlow'),
                'fcf': r.get('financingCashFlow'),
                'roe': r.get('roe'),
                'roa': r.get('roa'),
                'de': r.get('de'),
                'total_assets': r.get('totalAssets'),
                'shareholder_equity': r.get('shareholderEquity'),
            }
    return by_year_q4
```

## Phase 3: fetch_fundamentals — SETSMART primary, skip yahoo redundant
- [x] แก้ scripts/data_adapter.py fetch_fundamentals (บรรทัด 676-904) — รับ ss_data จาก _fetch_setsmart ก่อน → ถ้า ss_data['eod'] มี close,pe,pbv,marketCap,dividendYield ครบ → set price/pe_ratio/pb_ratio/market_cap/dy จาก SETSMART ทันที — Scope: ยังเรียก _fetch_yahoo_supplement สำหรับ DPS events + 52w + capex + interest_expense (irreplaceable) — Acceptance: เมื่อ SETSMART cache warm → fetch_fundamentals('BBL') ไม่เรียก yahooquery.Ticker(sym).price[sym] (verify ด้วย log)
- [x] แก้ scripts/data_adapter.py fetch_fundamentals — สำหรับ ROE/ROA/D/E/EPS งบ 5 ปีล่าสุด: ใช้ ss_data['financial_yearly'] override yearly_metrics สำหรับปีที่อยู่ใน 5y range — thaifin yearly_metrics เก็บไว้สำหรับปีก่อนหน้า — Scope: ไม่ลบ thaifin path, แค่ override ปีที่ overlap — Acceptance: BBL yearly_metrics[2024]['roe'] = SETSMART value (ไม่ใช่ thaifin), yearly_metrics[2010]['roe'] = thaifin value
- [x] แก้ scripts/data_adapter.py SETSMART override block (บรรทัด 830-861) — refactor ให้รวมเข้ากับ logic ใหม่ (line 700-790 ส่วน snapshot — ไม่ override ทับ แต่ build จาก SETSMART ตั้งแต่ต้น) — Scope: ลบ block 830-861 ถ้า redundant, หรือ keep เป็น fallback safety — Acceptance: code ไม่ซ้ำซ้อน + ตัวเลขผลลัพธ์ตรงกับเดิม (BBL price/pe/pbv ตรง SETSMART EOD ล่าสุด)

### Reference
```python
# current control flow (scripts/data_adapter.py:676-904 simplified)
def fetch_fundamentals(symbol):
    tf_result = _fetch_thaifin(symbol)
    yf_result = _fetch_yahoo_supplement(symbol)  # ALWAYS called
    ss_data = _fetch_setsmart(symbol)
    
    # ... build snapshot from thaifin + yahoo ...
    price = yf_info.get('regularMarketPrice')  # line 754
    pe_ratio = yf_info.get('trailingPE')  # line 758
    pb_ratio = yf_info.get('priceToBook')  # line 760
    market_cap = yf_info.get('marketCap')  # line 755
    
    # ... yahoo DPS attribution ...
    
    # SETSMART override (line 830-861)
    if use_setsmart:
        if ss_eod.get('close') is not None:
            price = ss_eod['close']
        if ss_eod.get('dividendYield') is not None:
            dy = ss_eod['dividendYield']
        if ss_eod.get('pe') is not None:
            pe_ratio = ss_eod['pe']
        # ...

# new — SETSMART first, yahoo only for irreplaceable
def fetch_fundamentals(symbol):
    ss_data = _fetch_setsmart(symbol)
    ss_eod = (ss_data or {}).get('eod') or {}
    ss_fin_yearly = (ss_data or {}).get('financial_yearly') or {}
    
    # Snapshot: SETSMART first
    use_ss_snapshot = bool(ss_eod and ss_eod.get('close'))
    if use_ss_snapshot:
        price = ss_eod.get('close')
        dy = ss_eod.get('dividendYield')
        pe_ratio = ss_eod.get('pe')
        pb_ratio = ss_eod.get('pbv')
        market_cap = ss_eod.get('marketCap')
        bvps_snapshot = ss_eod.get('bvps')
    else:
        price = pe_ratio = pb_ratio = market_cap = dy = bvps_snapshot = None
    
    # thaifin yearly history (16 years — full)
    tf_result = _fetch_thaifin(symbol)
    
    # yahoo: only for irreplaceable (DPS events, 52w, capex, interest_expense)
    yf_result = _fetch_yahoo_supplement(symbol, snapshot=not use_ss_snapshot)
    # ^ pass snapshot=False if SETSMART warm — yahoo supplement skips info[] fetch
    
    # Fallback snapshot to yahoo if SETSMART cold
    if not use_ss_snapshot:
        yf_info = yf_result.get('info') or {}
        price = price or yf_info.get('regularMarketPrice')
        # ... etc
    
    # Override yearly_metrics ROE/ROA/D/E/EPS for 5y range with SETSMART quarterly aggregate
    for ym in yearly_metrics:
        y = ym.get('year')
        if y in ss_fin_yearly:
            ym['roe'] = ss_fin_yearly[y]['roe']
            ym['roa'] = ss_fin_yearly[y]['roa']
            ym['debt_to_equity'] = ss_fin_yearly[y]['de']
            ym['eps_setsmart'] = ss_fin_yearly[y]['eps']
            # ... etc
```

## Phase 4: Scheduler job — financial cache refresh
- [x] แก้ scripts/daily_price_refresh.py — เพิ่ม function _refresh_setsmart_financial(symbols: list[str]) ที่เรียก cached_financial_by_symbol_range สำหรับทุก symbol ใน list (watchlist + candidates) — Scope: ไม่กระทบ existing EOD refresh logic — Acceptance: function รัน 5 หุ้น (BBL, PTT, CPALL, KBANK, SCB) สำเร็จ + cache file สร้างใหม่ครบ 5 ไฟล์ที่ data/setsmart_cache/financial_by_symbol_*.json
- [x] แก้ scripts/daily_price_refresh.py refresh_prices function (บรรทัด 136-203) — เรียก _refresh_setsmart_financial หลัง EOD refresh — Acceptance: refresh_prices() จบ + ทั้ง EOD cache + financial cache ใหม่หมด
- [x] Verify server/app.py APScheduler — existing daily_price_refresh job (บรรทัด 1090-1097) จะ trigger function ใหม่อัตโนมัติ (เพราะแก้ในไฟล์ที่ scheduler import) — Acceptance: เริ่ม server แล้วรอ 19:00 (หรือ trigger manual via /api/admin/price-refresh/trigger) → log แสดง 'SETSMART financial refresh complete'

### Reference
```python
# current (scripts/daily_price_refresh.py:136-203) — refresh_prices
def refresh_prices():
    symbols = _load_symbols()
    logger.info("refreshing %d symbols", len(symbols))
    setsmart_map = _load_setsmart_eod_map(symbols)
    # ... yahoo batch fallback for missing ...
    # ... write price_cache/{sym}.json ...

# new — add financial refresh
from setsmart_adapter import cached_financial_by_symbol_range
from datetime import datetime

def _refresh_setsmart_financial(symbols: list[str]):
    """Refresh SETSMART per-symbol financial cache (5y quarterly)."""
    current_year = datetime.now().year
    start_y = str(current_year - 5)
    end_y = str(current_year - 1)
    success_count = 0
    for sym in symbols:
        try:
            records = cached_financial_by_symbol_range(sym, start_y, '1', end_y, '4')
            if records:
                success_count += 1
        except Exception as e:
            logger.warning("SETSMART financial refresh failed for %s: %s", sym, e)
    logger.info("SETSMART financial refresh: %d/%d success", success_count, len(symbols))

def refresh_prices():
    symbols = _load_symbols()
    logger.info("refreshing %d symbols", len(symbols))
    setsmart_map = _load_setsmart_eod_map(symbols)
    # ... existing EOD logic ...
    
    # NEW: financial refresh
    _refresh_setsmart_financial(symbols)
```

```python
# Verify server/app.py:1090-1097 — existing job will auto-trigger new logic
scheduler.add_job(
    scheduled_price_refresh_job,
    "cron",
    id="daily_price_refresh",
    hour=19, minute=0,
    timezone="Asia/Bangkok",
    replace_existing=True,
)
# scheduled_price_refresh_job() imports daily_price_refresh.refresh_prices() — will pick up new financial logic
```

## Phase 5: Smoke test + verify
- [x] ลบ cache เก่า: rm data/setsmart_cache/financial_*.json (เก่าจาก probe research) — Acceptance: ls data/setsmart_cache/ | grep financial | wc -l = 0 (ก่อนรัน refresh)
- [x] รัน py scripts/daily_price_refresh.py (manual trigger) — Acceptance: เสร็จไม่ error + data/setsmart_cache/financial_by_symbol_*.json มีไฟล์ครบทุก symbol ที่ scan (~ใน watchlist + candidates) + แต่ละไฟล์มี 20 records
- [x] Verify yahoo redundant skip: py -c 'from scripts.data_adapter import fetch_fundamentals; import logging; logging.basicConfig(level=logging.DEBUG); r=fetch_fundamentals("BBL"); print(r["price"], r["pe_ratio"])' — Acceptance: log แสดงว่า yahooquery price[sym] ไม่ถูกเรียก (เพราะ SETSMART มี) แต่ dividend_history ยังถูกเรียก (irreplaceable)
- [x] รัน weekly scan smoke 5 หุ้น: py scripts/scan.py --symbols BBL,PTT,CPALL,KBANK,SCB --no-write — Acceptance: 5/5 หุ้น fetched สำเร็จ + scan output ตรงกับเดิม + yahoo API calls per scan ลด > 50% (estimate via log count)

### Reference
Verify commands:
```bash
cd C:\WORKSPACE\projects\4-MaxMahon
rm data/setsmart_cache/financial_*.json
py scripts/daily_price_refresh.py
ls data/setsmart_cache/ | grep financial_by_symbol
# Should show 1 file per symbol refreshed

py -c "from scripts.data_adapter import fetch_fundamentals; r=fetch_fundamentals('BBL'); print('price:', r['price'], 'pe:', r['pe_ratio'], 'fy_complete:', r.get('fy_is_complete'))"
```
