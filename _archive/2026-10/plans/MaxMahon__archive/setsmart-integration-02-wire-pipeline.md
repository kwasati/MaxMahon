---
project: MaxMahon
created: 2026-04-27
last_updated: 2026-04-27
status: done
---

## Target / Goal
ทำได้: เปิด `https://max.intensivetrader.com/report/BBL.BK` แล้วเห็น dividend yield 6.8% ±0.1% (ตรง SET reference) ไม่ใช่ 10.41% (ค่าเก่าจาก screener cache) — เพราะ /api/stock/{sym} override snapshot fields จาก SETSMART cache ที่ refresh ทุกวัน 19:00. ทุก field aggregate (yield/pe/pbv/marketCap) ของ 4 หุ้น (BBL/METCO/QH/SAT) ตรง SET ภายใน ±0.1%

# Wire SETSMART into MaxMahon Pipeline

> Part 2 of 2 — Pipeline Wiring | Index: setsmart-integration-index. ผูก SETSMART adapter (จาก Plan 01) เป็น primary layer ใน fetch_fundamentals + แก้ /api/stock endpoint ให้ override snapshot fields จาก SETSMART cache (แก้ root cause ของ data freshness — UI ไม่ต้องรอ scan ใหม่) + แก้ daily_price_refresh ให้ pre-warm SETSMART EOD bulk (1 request/วัน) + re-verify 4 หุ้น vs SET reference + verify บน UI ตาเปล่า. Depends on: setsmart-integration-01-adapter (adapter module + cache layer ต้องพร้อม). Parallel-safe with: none.

## Phase 1: Wire fetch_fundamentals + API endpoint
- [x] เพิ่ม helper function `_fetch_setsmart(symbol)` ใน `projects/MaxMahon/scripts/data_adapter.py` (วางหลัง `_fetch_yahoo_supplement` ราวบรรทัด 590) — อ่านจาก cache files ของ SETSMART (`data/setsmart_cache/eod_*.json` ล่าสุด + `financial_*.json` ล่าสุด) → return dict `{eod: row|None, financial: row|None}` หรือ None ถ้าไม่มี cache. ดู reference snippet. **Prerequisite:** `data_adapter.py` ปัจจุบันยังไม่มี `ROOT` module-level constant — agent ต้องเพิ่ม `from pathlib import Path` ที่ top + `ROOT = Path(__file__).resolve().parent.parent` หลัง imports (ตามตัวอย่างใน `daily_price_refresh.py:20`) ก่อนใช้ใน `_fetch_setsmart`. — Scope: เพิ่ม helper อย่างเดียว ห้ามแก้ `fetch_fundamentals` ใน task นี้ (task ถัดไป). ห้าม import setsmart_adapter ที่ top-level (lazy import ใน function เพื่อกัน circular). — Acceptance: รัน inline test (เขียน script ชั่วคราว `_test_ss_helper.py` ใน projects/MaxMahon/scripts/ ที่ import `_fetch_setsmart` แล้วเรียกด้วย 'BBL.BK' + print result + ลบไฟล์ test ทิ้งหลังรัน) ต้องไม่ raise exception (output อาจ None ถ้ายังไม่มี cache, ไม่ใช่ bug)
- [x] แก้ function `fetch_fundamentals(symbol)` ใน `projects/MaxMahon/scripts/data_adapter.py` (บรรทัด 600+) — เพิ่ม SETSMART layer เป็น primary. ขั้นตอน: (a) เพิ่ม `ss_data = _fetch_setsmart(symbol)` หลัง yahoo_supplement, (b) ปรับ error check ให้ต้อง all 3 fail (`yf+tf+ss`) ก่อน return delisted, (c) หลัง merge thaifin+yahoo เสร็จ — เพิ่ม block override aggregate fields ด้วย SETSMART (price, dy, pe_ratio, pb_ratio, market_cap จาก ss_eod + roe/roa/de/eps_diluted ใน yearly_metrics ที่ตรง year). ดู reference snippet. — Scope: ห้ามแก้ logic จัด FY (heuristic จาก plan ก่อน) — heuristic ยังคง compute เป็น layer fallback. ห้ามแตะ `_fetch_thaifin`, `_fetch_yahoo_supplement`, `_attribute_dividends_to_fiscal_years`. — Acceptance: เขียน script ชั่วคราว `_test_fetch_fund.py` ที่ import `fetch_fundamentals` + เรียกด้วย 'BBL.BK' + print yield/price + ลบไฟล์ test ทิ้งหลังรัน — ต้องคืนค่ายอดถูกต้อง (yield 6-7% สำหรับ BBL) ไม่ raise
- [x] แก้ endpoint `/api/stock/{symbol}` ใน `projects/MaxMahon/server/app.py` (function `get_stock`, บรรทัด 288-336) — เพิ่ม block "override snapshot fields จาก SETSMART cache" หลัง screener loop จบ (ก่อน 'Also check request files' ที่บรรทัด ~324). อ่าน latest `data/setsmart_cache/eod_*.json` → match symbol (no .BK suffix) → override `metrics.dividend_yield`, `metrics.pe`, `metrics.pbv` + top-level `price`, `market_cap` ของ stock_data ด้วยค่าจาก SETSMART (ถ้ามี cache). ถ้า SETSMART cache ไม่มี → log warning + fall back screener cache (legacy behavior). ดู reference snippet. — Scope: แก้แค่ `get_stock` function. ห้ามแตะ field `score`/`breakdown`/`signals`/`reasons`/`aggregates`/`yearly_metrics`/`dividend_history` (compute-heavy, ยังใช้ scan cache). ห้ามแตะ `/api/stock/{sym}/analyze`, `/api/stock/{sym}/price-history`. — Acceptance (self-review ใน worktree ก่อน commit): (a) `py -m py_compile server/app.py` ผ่าน (no syntax error), (b) `py -c "import sys; sys.path.insert(0, '.'); from server.app import get_stock; print('import OK')"` ไม่ raise exception, (c) grep `"SETSMART override applied"` ใน `server/app.py` พบ log line ที่เพิ่มใหม่. **Full endpoint verify (warm cache + restart server + curl)** ย้ายไป Phase 2 task 3 ที่ทำหลัง merge — task 1.3 ทำได้แค่ static verification เพราะ server runtime ใช้ code จาก main path ไม่ใช่ worktree

### Reference
```python
# current (data_adapter.py:600-619 — fetch_fundamentals start)
def fetch_fundamentals(symbol: str) -> dict:
    """Fetch fundamentals using thaifin (primary) + yahooquery (supplement).

    Returns schema identical to fetch_multi_year() output.
    """
    yf_sym = _to_yf_symbol(symbol)

    # 1. Try thaifin for historical data
    tf_data = _fetch_thaifin(symbol)

    # 2. Always get yahooquery supplement for realtime data
    yf_supp = _fetch_yahoo_supplement(symbol)
    yf_info = yf_supp.get("info", {})

    # If Yahoo supplement also empty, check thaifin
    if "error" in yf_supp and tf_data is None:
        return {"symbol": yf_sym, "error": yf_supp["error"]}

    # 3. If thaifin failed → return delisted marker (no fallback)
    use_thaifin = tf_data is not None and len(tf_data.get("yearly_metrics", [])) > 0

# new — เพิ่ม SETSMART primary layer ก่อน thaifin
def fetch_fundamentals(symbol: str) -> dict:
    """Fetch fundamentals — SETSMART (primary) + thaifin (history) + yahooquery (DPS events + 52w).

    Returns schema identical to fetch_multi_year() output.
    """
    yf_sym = _to_yf_symbol(symbol)
    tf_sym = _to_tf_symbol(symbol)

    # 0. SETSMART primary — realtime aggregate (yield, P/E, P/BV, market cap, EPS, ROE, ROA)
    ss_data = _fetch_setsmart(symbol)

    # 1. Try thaifin for historical data (still needed for 10+yr history beyond SETSMART package)
    tf_data = _fetch_thaifin(symbol)

    # 2. Always get yahooquery supplement for DPS event-by-event + 52w + capex/oi/ie
    yf_supp = _fetch_yahoo_supplement(symbol)
    yf_info = yf_supp.get("info", {})

    # If Yahoo + thaifin empty, AND no SETSMART → delisted/missing
    if "error" in yf_supp and tf_data is None and ss_data is None:
        return {"symbol": yf_sym, "error": yf_supp["error"]}

    # 3. Decide layer for each field — SETSMART > thaifin > yahooquery
    use_thaifin = tf_data is not None and len(tf_data.get("yearly_metrics", [])) > 0
    use_setsmart = ss_data is not None
```

```python
# new helper (add near _fetch_yahoo_supplement at ~line 429+ in data_adapter.py)
def _fetch_setsmart(symbol: str) -> dict | None:
    """Fetch aggregate data from SETSMART (cached bulk endpoints).

    Returns dict with EOD snapshot (latest day) + financial ratios (latest quarter), or None on failure.
    Reads from data/setsmart_cache/ — populated by daily_price_refresh + weekly scan.
    """
    try:
        from datetime import datetime
        from scripts.setsmart_adapter import cached_eod_bulk, cached_financial_bulk

        sym_no_bk = _to_tf_symbol(symbol)  # 'BBL.BK' → 'BBL' (SETSMART uses no .BK suffix)

        # Find most recent EOD cache file
        cache_dir = ROOT / "data" / "setsmart_cache"  # ROOT = Path(__file__).resolve().parent.parent
        eod_files = sorted(cache_dir.glob("eod_*.json"), reverse=True)
        eod_row = None
        if eod_files:
            latest_eod = json.loads(eod_files[0].read_text(encoding="utf-8"))
            for r in latest_eod:
                if r.get("symbol") == sym_no_bk:
                    eod_row = r
                    break

        # Find most recent Financial cache
        fin_files = sorted(cache_dir.glob("financial_*.json"), reverse=True)
        fin_row = None
        if fin_files:
            latest_fin = json.loads(fin_files[0].read_text(encoding="utf-8"))
            for r in latest_fin:
                if r.get("symbol") == sym_no_bk:
                    fin_row = r
                    break

        if eod_row is None and fin_row is None:
            return None

        return {"eod": eod_row, "financial": fin_row}
    except Exception as e:
        logger.warning("SETSMART fetch failed for %s: %s", symbol, e)
        return None
```

```python
# new — ใน fetch_fundamentals after merge thaifin + yahooquery (around line 690+)
# OVERRIDE aggregate fields with SETSMART when available (primary layer)
if use_setsmart:
    ss_eod = ss_data.get("eod") or {}
    ss_fin = ss_data.get("financial") or {}

    # Override realtime price snapshot
    if ss_eod.get("close") is not None:
        price = ss_eod["close"]
    if ss_eod.get("dividendYield") is not None:
        dy = ss_eod["dividendYield"]  # SETSMART value (overrides heuristic-computed)
    if ss_eod.get("pe") is not None:
        pe_ratio = ss_eod["pe"]
    if ss_eod.get("pbv") is not None:
        pb_ratio = ss_eod["pbv"]
    if ss_eod.get("marketCap") is not None:
        market_cap = ss_eod["marketCap"]

    # Override quarterly ratios in latest yearly_metric
    # (apply ss_fin.roe/roa/de/eps to the row matching ss_fin.year if present)
    if ss_fin and yearly_metrics:
        target_year = ss_fin.get("year")
        for m in yearly_metrics:
            if m["year"] == target_year:
                if ss_fin.get("roe") is not None:
                    m["roe"] = ss_fin["roe"] / 100.0
                if ss_fin.get("roa") is not None:
                    m["roa"] = ss_fin["roa"] / 100.0
                if ss_fin.get("de") is not None:
                    m["de_ratio"] = ss_fin["de"]
                if ss_fin.get("epsAccum") is not None:
                    m["eps_diluted"] = ss_fin["epsAccum"]
                break
```

```python
# current (server/app.py:288-336 — get_stock endpoint)
@app.get("/api/stock/{symbol}")
async def get_stock(symbol: str):
    """Merge stock data from snapshot + screener."""
    stock_data = None

    # Try snapshot first (watchlist stocks)
    snap_path = find_latest("snapshot_*.json", DATA_DIR)
    if snap_path:
        snap = read_json(snap_path)
        for s in snap.get("stocks", []):
            if _norm_sym(s.get("symbol", "")) == _norm_sym(symbol):
                stock_data = dict(s)
                break

    # Enrich or fallback from screener (discoveries + score)
    scr_path = find_latest("screener_*.json", DATA_DIR)
    if scr_path:
        scr = read_json(scr_path)
        for c in scr.get("candidates", []):
            if _norm_sym(c.get("symbol", "")) == _norm_sym(symbol):
                if stock_data is None:
                    stock_data = dict(c)
                else:
                    stock_data["score"] = c.get("score")
                    stock_data["breakdown"] = c.get("breakdown")
                    stock_data["signals"] = c.get("signals")
                    stock_data["reasons"] = c.get("reasons")
                    stock_data["screener_metrics"] = c.get("metrics")
                    for key in ("aggregates", "yearly_metrics", "dividend_history"):
                        if key not in stock_data and key in c:
                            stock_data[key] = c[key]
                break

    # ... rest of get_stock

# new — เพิ่ม override snapshot fields จาก SETSMART cache หลัง screener load
# วาง block นี้ "หลัง" screener loop เสร็จ (ก่อน "Also check request files" — ราวบรรทัด 323)
    # Override snapshot fields with SETSMART cache (daily refresh layer)
    # Compute-heavy fields (score/breakdown/signals/aggregates) ยังจาก screener cache เดิม
    # Snapshot fields (yield/pe/pbv/marketCap/price) override จาก SETSMART (refresh ทุกวัน 19:00)
    if stock_data is not None:
        try:
            from scripts.setsmart_adapter import CACHE_DIR as SS_CACHE_DIR
            sym_no_bk = _norm_sym(symbol).replace(".BK", "")

            # Find most recent SETSMART EOD cache
            eod_files = sorted(SS_CACHE_DIR.glob("eod_*.json"), reverse=True)
            ss_eod_row = None
            if eod_files:
                latest_eod = json.loads(eod_files[0].read_text(encoding="utf-8"))
                for r in latest_eod:
                    if r.get("symbol") == sym_no_bk:
                        ss_eod_row = r
                        break

            if ss_eod_row:
                # Override metrics dict (where dividend_yield, pe, pbv live in screener candidate schema)
                metrics = stock_data.get("metrics") or {}
                if ss_eod_row.get("dividendYield") is not None:
                    metrics["dividend_yield"] = ss_eod_row["dividendYield"]
                if ss_eod_row.get("pe") is not None:
                    metrics["pe"] = ss_eod_row["pe"]
                if ss_eod_row.get("pbv") is not None:
                    metrics["pbv"] = ss_eod_row["pbv"]
                stock_data["metrics"] = metrics

                # Override top-level snapshot fields
                if ss_eod_row.get("close") is not None:
                    stock_data["price"] = ss_eod_row["close"]
                if ss_eod_row.get("marketCap") is not None:
                    stock_data["market_cap"] = ss_eod_row["marketCap"]

                logger.info("SETSMART override applied for %s: yield=%s, pe=%s",
                            symbol, ss_eod_row.get("dividendYield"), ss_eod_row.get("pe"))
        except Exception as e:
            logger.warning("SETSMART override skipped for %s: %s", symbol, e)
```

## Phase 2: Daily refresh + verify (script + UI)
- [x] แก้ `projects/MaxMahon/scripts/daily_price_refresh.py` — ก่อน yahooquery batch loop เพิ่ม section ดึง SETSMART EOD bulk (1 request ครอบทั้งตลาด ~4000 หุ้น) + เก็บลง `data/setsmart_cache/eod_{YYYY-MM-DD}.json` ใช้ `cached_eod_bulk()` จาก setsmart_adapter. yahooquery batch เดิมยังคงไว้ (สำหรับ DPS events). ถ้า SETSMART fetch fail → log warning แล้วเดินต่อด้วย yahooquery (ไม่ block daily refresh). ดู reference snippet. — Scope: แก้แค่ฟังก์ชัน `refresh_prices()` (เพิ่ม section 0 ก่อน yahooquery batch loop). ห้ามลบ yahooquery batch logic. ห้ามแตะ `_load_symbols` หรือ inline cache file write ใน loop. — Acceptance: รัน `cd projects/MaxMahon && py scripts/daily_price_refresh.py` ต้องเห็น log 'SETSMART EOD bulk: N rows for YYYY-MM-DD' (N>3000) + ไฟล์ cache ถูกสร้าง + yahooquery batch ยังทำงานปกติ (ไม่ exception)
- [x] ลบไฟล์ verification เก่า + รัน `py scripts/_verify_dps_fix.py` (script เดิมไม่ต้องแก้) ที่ `cd projects/MaxMahon` — script จะอ่าน fetch_fundamentals (ตอนนี้ใช้ SETSMART primary) → write `docs/dps-fix-verification-{YYYY-MM-DD}.md`. ตรวจ output 4 หุ้น (BBL/METCO/QH/SAT) — yield ทุกตัวต้องตรง SET reference ภายใน **±0.1%** (เข้มขึ้นจาก ±1% เพราะ data จาก SET ตรง). อัพเดต report บน main branch. — Scope: ห้ามแก้ verify script. ห้ามแก้ data_adapter (เสร็จไปแล้ว Phase 1). — Acceptance: ไฟล์ `docs/dps-fix-verification-{YYYY-MM-DD}.md` ระบุ METCO yield 11.36% (ตรง SET 11.4% ±0.1%) + BBL ตรง 6.8% ±0.1% + QH ตรง 6-7% ±0.1% + SAT ตรง 11% ±0.1% + commit message ระบุ 're-verified after SETSMART wire'. ถ้าไม่ผ่าน ±0.1% ใน case ใด → STOP + รายงาน user (ไม่ใช่ acceptable failure — primary source must match SET)
- [x] Verify endpoint บน production — ทำตามลำดับ: (1) restart MaxMahon server (`max-server.bat` หรือ kill+start uvicorn port 50089), (2) รัน `curl -s http://localhost:50089/api/stock/BBL.BK | py -c "import json,sys; d=json.loads(sys.stdin.read()); print('yield:', d.get('metrics',{}).get('dividend_yield'), 'pe:', d.get('metrics',{}).get('pe'), 'price:', d.get('price'))"` — ต้องเห็น yield ระหว่าง 6.7-6.9% (ตรง SET) ไม่ใช่ 10.41%, (3) ทำซ้ำกับ METCO/QH/SAT — ทุกตัวต้องอยู่ใน ±0.1% ของ SET reference, (4) Optional UI check — เปิด `https://max.intensivetrader.com/report/BBL.BK` ตาดู 5-5-5-5 yield + Niwes scoring breakdown ด้วยตา. — Scope: ห้ามแก้ code. ห้ามแก้ test/verify scripts. แค่ verify deployed behavior. — Acceptance: curl output ของ 4 หุ้นทุกตัวมี yield ตรง SET ±0.1% + server log แสดง 'SETSMART override applied' สำหรับทุก request + UI หน้า report แสดงตัวเลขเดียวกับ curl (ถ้าเปิดตรวจตาเปล่า). ถ้า curl กลับมาด้วย yield 10.41% (BBL) → STOP, รายงาน user (override block ไม่ทำงาน — debug ใน Phase 1 task 3)

### Reference
```python
# current (daily_price_refresh.py:60-100 — refresh_prices function)
def refresh_prices() -> dict:
    """Fetch current prices for watchlist + PASS candidates and cache to disk."""
    symbols = _load_symbols()
    logger.info(f"refreshing {len(symbols)} symbols")
    fetched: dict[str, float] = {}

    for i in range(0, len(symbols), 20):
        chunk = symbols[i:i + 20]
        try:
            tk = Ticker(chunk)
            prices = tk.price
            # ... (existing yahooquery batch logic — write to CACHE_DIR/{sym}.json inline)
        except Exception as e:
            logger.warning(f"batch {i} failed: {e}")
        time.sleep(0.2)

    return fetched

# new — เพิ่ม SETSMART EOD bulk fetch (1 request/วัน) ก่อน yahooquery batch loop
def refresh_prices() -> dict:
    """Fetch current prices for watchlist + PASS candidates and cache to disk."""
    # 0. NEW — SETSMART EOD bulk (1 request, ดึงทั้งตลาด ~4000 หุ้น)
    try:
        from datetime import datetime, timedelta
        from scripts.setsmart_adapter import cached_eod_bulk
        # Walk back to find a trading day
        for delta in range(1, 8):
            d = (datetime.now() - timedelta(days=delta)).strftime("%Y-%m-%d")
            data = cached_eod_bulk(d)
            if len(data) > 0:
                logger.info("SETSMART EOD bulk: %d rows for %s", len(data), d)
                break
    except Exception as e:
        logger.warning("SETSMART bulk fetch failed (will fallback to yahooquery): %s", e)

    # 1. Existing — yahooquery batch (kept for DPS events + price snapshot fallback)
    symbols = _load_symbols()
    logger.info(f"refreshing {len(symbols)} symbols")
    fetched: dict[str, float] = {}
    for i in range(0, len(symbols), 20):
        chunk = symbols[i:i + 20]
        # ... (existing logic unchanged)
    return fetched
```
