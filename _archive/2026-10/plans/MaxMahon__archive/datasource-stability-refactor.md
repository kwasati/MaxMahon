---
project: MaxMahon
created: 2026-04-21
last_updated: 2026-04-21
status: done
---

# Data Source Stability Refactor — Fix yfinance Misuse + Expose thaifin Orphan Fields + Enforce Invariants

> Fix data source bugs จาก build 54-task ที่วางผิด (ใช้ yfinance yearly/historical แทน thaifin primary) + expose thaifin orphan fields (close/dividend_yield/mkt_cap/payout_ratio ต่อปี) + enforce Data Source Invariants ใน CLAUDE.md ป้องกันพลาดซ้ำ. Root cause: `_get_price_avg()` ใน fetch_data.py + `/price-history` ใน server/app.py เรียก yfinance 10y monthly — yfinance Thai stocks > 3-5 ปี history ไม่ครบ = log spam + null values; แต่ thaifin มี yearly close + dividend_yield อยู่แล้วในโค้ด (data_adapter.py line 122, 124) แค่ไม่ได้ expose ใน yearly_metrics dict

## Phase 1: Data Adapter — Expose thaifin orphan fields + compute payout_ratio
- [x] แก้ `projects/MaxMahon/scripts/data_adapter.py` function `_fetch_thaifin()` (บรรทัด 83-290) — **yearly_metrics builder ที่บรรทัด 176-203** เพิ่ม 4 key ต่อ entry: `close` (จาก `closes[year_int]` local dict ที่อ่านที่บรรทัด 122, 132), `dividend_yield` (จาก `dividend_yields[year_int]` ที่อ่านที่ 124, 130 — unit = %), `mkt_cap` (จาก `mkt_cap = _safe(df.loc[year].get('mkt_cap'))` ที่อ่านที่ 123), `bvps` (จาก `bvps = _safe(df.loc[year].get('book_value_per_share'))` ที่อ่านที่ 125) — 4 field เหล่านี้ thaifin มีให้อยู่แล้ว local dict ทิ้งเฉยๆ — scope: ไม่แก้ snapshot-level fields (pe_ratio/pb_ratio latest), ไม่เรียก yfinance — Acceptance: รัน `py -c "import sys; sys.path.insert(0,'scripts'); from data_adapter import fetch_fundamentals; d = fetch_fundamentals('CPALL.BK'); m = d['yearly_metrics'][-1]; assert 'close' in m and 'dividend_yield' in m and 'mkt_cap' in m and 'bvps' in m; print('close:', m['close'], 'dy:', m['dividend_yield'], 'mcap:', m['mkt_cap']); assert m['close'] is not None, 'close should be populated'"` → print ค่าจริง + ไม่ throw AssertionError
- [x] แก้ `projects/MaxMahon/scripts/data_adapter.py` `_fetch_thaifin()` — เพิ่ม `payout_ratio` per year ใน yearly_metrics entry — thaifin **ไม่มี column `payout_ratio` หรือ `dividends_paid`** (line 192 ยืนยัน `"dividends_paid": None  # not in thaifin`), ต้อง compute: `payout_ratio = (dividend_yield / 100) * close / diluted_eps` (yield เป็น %, close เป็น THB, diluted_eps เป็น THB → payout_ratio = decimal); ถ้าขาด value ใดให้ set None + guard `diluted_eps > 0` กัน loss year; ใส่ไว้ใน yearly_metrics dict entry (ต่อจาก task 1.1) — scope: ไม่แก้ snapshot payout_ratio (มีจาก yfinance supplement อยู่แล้ว) — Acceptance: รัน `py -c "import sys; sys.path.insert(0,'scripts'); from data_adapter import fetch_fundamentals; d = fetch_fundamentals('CPALL.BK'); m = d['yearly_metrics'][-1]; pr = m.get('payout_ratio'); print('payout_ratio:', pr); assert pr is None or (0 < pr < 2.0), f'unexpected payout {pr}'"` — ค่าปกติหุ้นไทย 0.3-1.0, บางปีอาจเกิน 1.0 ถ้า special dividend
- [x] แก้ `projects/MaxMahon/scripts/data_adapter.py` function `_holding_mcap()` (บรรทัด 26-35) — ลอง thaifin ก่อน fallback yfinance: `from thaifin import Stock; tf_sym = sym.replace('.BK', ''); tf_stock = Stock(tf_sym); df = tf_stock.yearly_dataframe; if df is not None and not df.empty: latest_mkt_cap = _safe(df.iloc[-1].get('mkt_cap')); if latest_mkt_cap: return int(latest_mkt_cap)` — ถ้า thaifin fail/empty → fallback เดิม `yf.Ticker(sym).info.get('marketCap')` — scope: ไม่แก้ signature/return type — Acceptance: `py -c "import sys; sys.path.insert(0,'scripts'); from data_adapter import _holding_mcap, _HOLDING_MCAP_CACHE; _HOLDING_MCAP_CACHE.clear(); v = _holding_mcap('HMPRO.BK'); print('HMPRO mcap:', v); assert v is not None and v > 1e9, f'expected >1B, got {v}'"` — ได้ค่า market cap HMPRO จาก thaifin (ไม่ error + > 1B)

### Reference
```python
# projects/MaxMahon/scripts/data_adapter.py — yearly_metrics builder (current @ line 176-203)

            yearly_metrics.append({
                "year": year_str,
                "revenue": revenue,
                "gross_profit": gross_profit,
                "operating_income": operating_income,
                "net_income": net_income,
                "ebitda": ebitda,
                "interest_expense": interest_expense,
                "diluted_eps": diluted_eps,
                "sga": sga,
                "equity": equity,
                "total_debt": total_debt,
                "total_assets": total_assets,
                "ocf": ocf,
                "fcf": fcf,
                "capex": investing,  # negative = spending
                "dividends_paid": None,  # not in thaifin
                "roe": roe,
                "gross_margin": gross_margin,
                "net_margin": net_margin,
                "operating_margin": operating_margin,
                "sga_ratio": sga_ratio,
                "de_ratio": de_ratio,
                "current_ratio": current_ratio,
                "interest_coverage": interest_coverage,
                "ocf_ni_ratio": ocf_ni_ratio,
                "capital_intensity": capital_intensity,
            })

# NEW — add 5 fields from thaifin (4 orphan + 1 computed)
# NOTE: `close`, `dy`, `mkt_cap`, `bvps` already read earlier in the loop
# (lines 122-125); just wasn't included in the final dict.
# `payout_ratio` is computed from dividend_yield (%) × close / diluted_eps.

            # Payout ratio per year — thaifin doesn't provide directly; compute
            payout_ratio_year = None
            if dy is not None and close is not None and diluted_eps is not None and diluted_eps > 0:
                # dy is percentage (e.g. 5.2), close is THB, diluted_eps is THB
                dps_approx = (dy / 100.0) * close  # THB
                payout_ratio_year = dps_approx / diluted_eps  # decimal (0-1+)

            yearly_metrics.append({
                "year": year_str,
                "revenue": revenue,
                "gross_profit": gross_profit,
                "operating_income": operating_income,
                "net_income": net_income,
                "ebitda": ebitda,
                "interest_expense": interest_expense,
                "diluted_eps": diluted_eps,
                "sga": sga,
                "equity": equity,
                "total_debt": total_debt,
                "total_assets": total_assets,
                "ocf": ocf,
                "fcf": fcf,
                "capex": investing,
                "dividends_paid": None,  # not in thaifin
                "roe": roe,
                "gross_margin": gross_margin,
                "net_margin": net_margin,
                "operating_margin": operating_margin,
                "sga_ratio": sga_ratio,
                "de_ratio": de_ratio,
                "current_ratio": current_ratio,
                "interest_coverage": interest_coverage,
                "ocf_ni_ratio": ocf_ni_ratio,
                "capital_intensity": capital_intensity,
                # Plan: datasource-stability — expose thaifin orphan fields
                "close": close,            # THB per share (yearly close)
                "dividend_yield": dy,      # % (thaifin already provides)
                "mkt_cap": mkt_cap,        # market cap per year
                "bvps": bvps,              # book value per share
                "payout_ratio": payout_ratio_year,  # decimal, computed
            })
```

```python
# projects/MaxMahon/scripts/data_adapter.py — _holding_mcap current @ line 26-35

def _holding_mcap(sym: str) -> "int | None":
    if sym in _HOLDING_MCAP_CACHE:
        return _HOLDING_MCAP_CACHE[sym]
    try:
        import yfinance as yf
        v = yf.Ticker(sym).info.get("marketCap")
    except Exception:
        v = None
    _HOLDING_MCAP_CACHE[sym] = v
    return v

# NEW — try thaifin first, fallback yfinance

def _holding_mcap(sym: str) -> "int | None":
    if sym in _HOLDING_MCAP_CACHE:
        return _HOLDING_MCAP_CACHE[sym]
    v = None
    # Try thaifin first (primary source for Thai stocks)
    try:
        from thaifin import Stock
        tf_sym = sym.replace(".BK", "")
        tf_stock = Stock(tf_sym)
        df = tf_stock.yearly_dataframe
        if df is not None and not df.empty:
            latest_mkt_cap = _safe(df.iloc[-1].get("mkt_cap"))
            if latest_mkt_cap is not None and latest_mkt_cap > 0:
                v = int(latest_mkt_cap)
    except Exception:
        pass
    # Fallback to yfinance (for non-Thai holdings or when thaifin fails)
    if v is None:
        try:
            import yfinance as yf
            yf_v = yf.Ticker(sym).info.get("marketCap")
            if yf_v:
                v = int(yf_v)
        except Exception:
            pass
    _HOLDING_MCAP_CACHE[sym] = v
    return v
```

## Phase 2: fetch_data.py — Remove yfinance price_avg (ใช้ thaifin close จาก Phase 1 แทน)
- [x] ลบ function `_get_price_avg()` ทั้งฟังก์ชัน (บรรทัด 41-72) + constants `_PRICE_AVG_CACHE_DIR`, `_PRICE_AVG_CACHE_TTL` (บรรทัดก่อนหน้า ~33-38) + imports ที่ใช้เฉพาะ function นี้ ถ้ามี (`timedelta` อาจยังใช้ที่อื่น ต้อง grep ก่อนลบ) — scope: ลบเฉพาะ function + constants + cache dir init, ไม่แตะ `_PRICE_CACHE` ที่เป็น in-memory dict คนละตัว — Acceptance: `grep -n '_get_price_avg\|_PRICE_AVG_CACHE_DIR\|_PRICE_AVG_CACHE_TTL' projects/MaxMahon/scripts/fetch_data.py` return 0 lines
- [x] ลบ call site ใน adapter path (บรรทัด 447-449): `yf_sym = adapter_result.get(...); for m in yearly_metrics: m['price_avg'] = _get_price_avg(...)` — Phase 1 expose `close` ต่อปีแล้ว ไม่ต้อง compute ซ้ำ — scope: ลบ 3 บรรทัด (yf_sym var + for loop) ใน adapter path เท่านั้น, ไม่แตะ legacy (task 2.3) — Acceptance: `grep -n 'price_avg' projects/MaxMahon/scripts/fetch_data.py` return 0 lines ใน range บรรทัด 440-470
- [x] **ลบ call site ที่ 2 ใน `_fetch_yfinance_legacy`** (บรรทัด 357-358) — `for m in yearly_metrics: m['price_avg'] = _get_price_avg(symbol, int(m['year']))` **ต้องลบ** (ไม่ใช่แค่แก้ reference เพราะ task 2.1 ลบ function ไปแล้ว → call site นี้ = NameError) — หลังลบ loop นี้, **เพิ่ม 5 fields ใหม่ใน yearly_metrics.append dict** (บรรทัด ~326-353) เพื่อ schema parity กับ thaifin path: `close: None` (legacy ไม่ fetch per-year close), `dividend_yield: None` (yfinance yearly ไม่มี per-year yield), `mkt_cap: None`, `bvps: safe_div(equity, info.get('sharesOutstanding'))`, `payout_ratio: safe_div(div_paid, net_income) if net_income > 0 else None` — scope: 2 สิ่งในไฟล์เดียว — (a) ลบ for loop ที่ 357-358, (b) เพิ่ม 5 key ใน append dict — Acceptance: (1) `grep -n 'price_avg' projects/MaxMahon/scripts/fetch_data.py` return 0 lines ทั้งไฟล์; (2) `py -c "import sys; sys.path.insert(0,'scripts'); import fetch_data; print('import ok')"` ไม่ error (ถ้าลบ function แต่ยังมี call site เหลือ = NameError ตอน import)
- [x] Cleanup filesystem — ลบ folder `projects/MaxMahon/data/price_avg_cache/` (932 stale JSON files) + ลบ line `data/price_avg_cache/` จาก `projects/MaxMahon/.gitignore` — scope: filesystem + gitignore เท่านั้น — Acceptance: `ls projects/MaxMahon/data/price_avg_cache/ 2>&1 | grep -q 'No such file' && ! grep -q 'price_avg_cache' projects/MaxMahon/.gitignore` exit 0

### Reference
```python
# projects/MaxMahon/scripts/fetch_data.py — DELETE these (lines 36-72 approx)

_PRICE_AVG_CACHE_DIR = _DATA_DIR / "price_avg_cache"
_PRICE_AVG_CACHE_DIR.mkdir(parents=True, exist_ok=True)
_PRICE_AVG_CACHE_TTL = timedelta(days=30)


def _get_price_avg(yf_sym: str, year: int) -> float | None:
    """..."""
    # 40+ lines of yfinance history + cache logic
    ...
```

```python
# fetch_data.py adapter path — current @ lines 447-449

        yf_sym = adapter_result.get("symbol") or normalize_symbol(symbol)[1]
        for m in yearly_metrics:
            m["price_avg"] = _get_price_avg(yf_sym, int(m["year"]))

# NEW — delete these 3 lines entirely
# (thaifin yearly_metrics already includes close/dividend_yield/mkt_cap/bvps/payout_ratio per year from Phase 1)
```

```python
# fetch_data.py legacy path — current @ lines 326-358 (_fetch_yfinance_legacy)

            yearly_metrics.append({
                "year": year_str,
                "revenue": revenue,
                # ... 23 fields ...
                "capital_intensity": capital_intensity,
            })

    yearly_metrics.sort(key=lambda x: x["year"])

    for m in yearly_metrics:
        m["price_avg"] = _get_price_avg(symbol, int(m["year"]))   # <-- DELETE loop

# NEW — (a) delete loop at 357-358, (b) add 5 fields to append dict

            # Schema parity with thaifin path (datasource-stability Phase 2 task 3)
            bvps_legacy = safe_div(equity, info.get("sharesOutstanding")) if equity and info.get("sharesOutstanding") else None
            payout_ratio_legacy = safe_div(div_paid, net_income) if net_income and net_income > 0 else None

            yearly_metrics.append({
                "year": year_str,
                "revenue": revenue,
                # ... 23 fields เดิม ...
                "capital_intensity": capital_intensity,
                # Plan: datasource-stability — schema parity with thaifin
                "close": None,             # legacy yfinance doesn't track per-year close
                "dividend_yield": None,    # yfinance yearly doesn't provide dy per year
                "mkt_cap": None,           # historical mcap not fetched in legacy
                "bvps": bvps_legacy,
                "payout_ratio": payout_ratio_legacy,
            })

    yearly_metrics.sort(key=lambda x: x["year"])

    # DELETED: for m in yearly_metrics: m["price_avg"] = _get_price_avg(symbol, int(m["year"]))
    # (function removed by task 2.1; thaifin path handles close via Phase 1)
```

## Phase 3: server/app.py — price-history endpoint refactor (thaifin primary, yfinance granularity fallback)
- [x] แก้ `projects/MaxMahon/server/app.py` endpoint `/api/stock/{symbol}/price-history` (บรรทัด ~2147-2172) — เปลี่ยน primary source เป็น thaifin yearly `close`: อ่าน `data/price_history/{symbol}_yearly.json` cache (new cache key suffix), ถ้ายังไม่มี/ expired fetch จาก `fetch_multi_year(symbol)` แล้ว extract `[{date: f'{m["year"]}-12-31', close: m['close']} for m in yearly_metrics if m.get('close') is not None]` — response shape เพิ่ม field `source: 'thaifin_yearly'`; keep existing `fetched_at` + `symbol` fields; cache TTL 24 ชั่วโมง — scope: default granularity = yearly, ไม่เรียก yfinance.history() ใน default path — Acceptance: `curl http://localhost:50089/api/stock/CPALL.BK/price-history` → JSON มี `source: 'thaifin_yearly'` + `data` array ~10-15 จุด ละปี + date format 'YYYY-12-31' + ไม่ crash + ไม่พ่น yfinance log spam
- [x] เพิ่ม query param `?granularity=yearly|monthly` ใน `/api/stock/{symbol}/price-history` — default=`yearly` (thaifin path ข้อ 3.1), `monthly` → fall through to yfinance `period='10y', interval='1mo', auto_adjust=False` เหมือนเดิม (เก็บไว้สำหรับ DCA simulator use case) + cache แยก key (`{symbol}_monthly.json` vs `{symbol}_yearly.json`) — scope: ถ้า granularity ผิด → 400 error, ไม่ break DCA — Acceptance: `curl http://localhost:50089/api/stock/CPALL.BK/price-history?granularity=monthly` → JSON มี `source: 'yfinance_monthly'` + ~120 จุด; `?granularity=yearly` → thaifin path; `?granularity=invalid` → 400

### Reference
```python
# projects/MaxMahon/server/app.py — current @ lines 2123-2172 (price-history endpoint)

@app.get("/api/stock/{symbol}/price-history")
async def get_price_history(symbol: str):
    cache_file = _PRICE_HIST_DIR / f"{symbol}.json"
    now = datetime.now()
    if cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            fetched_at = datetime.fromisoformat(cached["fetched_at"])
            if now - fetched_at < timedelta(hours=_PRICE_HIST_TTL_HOURS):
                return cached
        except (KeyError, ValueError, json.JSONDecodeError):
            pass

    try:
        import yfinance as yf
        loop = asyncio.get_event_loop()
        hist = await loop.run_in_executor(
            None,
            lambda: yf.Ticker(symbol).history(
                period="10y", interval="1mo", auto_adjust=False
            ),
        )
    except Exception as e:
        raise HTTPException(503, f"yfinance fetch failed: {e}")

    if hist.empty:
        raise HTTPException(404, f"no price history for {symbol}")

    data = [
        {"date": idx.strftime("%Y-%m-%d"), "close": float(row["Close"])}
        for idx, row in hist.iterrows()
    ]
    payload = {
        "symbol": symbol,
        "fetched_at": now.isoformat(timespec="seconds"),
        "data": data,
    }
    cache_file.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return payload

# NEW — thaifin primary + granularity query param

@app.get("/api/stock/{symbol}/price-history")
async def get_price_history(symbol: str, granularity: str = "yearly"):
    """Price history — thaifin yearly (primary) or yfinance monthly (for DCA)."""
    if granularity not in ("yearly", "monthly"):
        raise HTTPException(400, f"granularity must be 'yearly' or 'monthly', got '{granularity}'")

    cache_file = _PRICE_HIST_DIR / f"{symbol}_{granularity}.json"
    now = datetime.now()
    if cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            fetched_at = datetime.fromisoformat(cached["fetched_at"])
            if now - fetched_at < timedelta(hours=_PRICE_HIST_TTL_HOURS):
                return cached
        except (KeyError, ValueError, json.JSONDecodeError):
            pass

    if granularity == "yearly":
        # Thaifin primary — use yearly close from yearly_metrics
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
        from fetch_data import fetch_multi_year
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: fetch_multi_year(symbol))
        if not result or "error" in result:
            raise HTTPException(404, f"no data for {symbol}")
        yearly = result.get("yearly_metrics", [])
        data = [
            {"date": f"{m['year']}-12-31", "close": m["close"]}
            for m in yearly if m.get("close") is not None
        ]
        if not data:
            raise HTTPException(404, f"no yearly close data for {symbol}")
        payload = {
            "symbol": symbol,
            "source": "thaifin_yearly",
            "granularity": "yearly",
            "fetched_at": now.isoformat(timespec="seconds"),
            "data": data,
        }
    else:
        # Monthly granularity — yfinance (for DCA simulator)
        try:
            import yfinance as yf
            loop = asyncio.get_event_loop()
            hist = await loop.run_in_executor(
                None,
                lambda: yf.Ticker(symbol).history(
                    period="10y", interval="1mo", auto_adjust=False
                ),
            )
        except Exception as e:
            raise HTTPException(503, f"yfinance fetch failed: {e}")
        if hist.empty:
            raise HTTPException(404, f"no monthly price history for {symbol}")
        data = [
            {"date": idx.strftime("%Y-%m-%d"), "close": float(row["Close"])}
            for idx, row in hist.iterrows()
        ]
        payload = {
            "symbol": symbol,
            "source": "yfinance_monthly",
            "granularity": "monthly",
            "fetched_at": now.isoformat(timespec="seconds"),
            "data": data,
        }

    cache_file.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return payload
```

## Phase 4: UI Consumers — renderYieldTrend + renderDividendHistoryTable + loadPriceHistoryChart
- [x] แก้ `projects/MaxMahon/web/app.js` function `renderYieldTrend(canvasId, dividendHistory, yearlyMetrics)` (บรรทัด 945-983) — เปลี่ยนจาก compute `dps / price_avg × 100` เอง เป็นอ่าน `ym.dividend_yield` ตรงๆ (unit=%, thaifin ให้มาจาก Phase 1); keep rolling 5y avg — scope: signature เดิม, behavior เดิม (line chart 2 dataset), แค่เปลี่ยน data source — Acceptance: (1) grep `ym.price_avg` ใน web/app.js return 0 lines ใน scope function renderYieldTrend; (2) grep `ym.dividend_yield\|m.dividend_yield` return ≥1 line ใน renderYieldTrend
- [x] Verify task 1.2 (payout_ratio compute) ทำงานถึง UI — `renderDividendHistoryTable()` (บรรทัด 985-1010) บรรทัด 994 อ่าน `(ym.get(y) || {}).payout_ratio` อยู่แล้ว ไม่ต้องแก้โค้ด — scope: verification task, ไม่ edit — Acceptance: (1) grep `payout_ratio` ใน projects/MaxMahon/scripts/data_adapter.py → มี 1+ line ใน yearly_metrics.append block (แสดงว่า Phase 1 task 2 expose แล้ว); (2) grep `payout_ratio` ใน projects/MaxMahon/web/app.js renderDividendHistoryTable scope → มี 1 line (unchanged); (3) manual browser test: เปิด detail CPALL.BK → dividend history table column Payout แสดงค่า % แทน '—' อย่างน้อย 80% ของแถว
- [x] แก้ `projects/MaxMahon/web/app.js` function `loadPriceHistoryChart(symbol, canvasId)` (บรรทัด 910-943) — รับ response shape ใหม่ (thaifin yearly: ≤15 จุด, date=`YYYY-12-31`) — Chart.js options: เพิ่ม x-axis label formatter แสดงเฉพาะปี (`callback: function(val) { return this.getLabelForValue(val).slice(0, 4); }`) + `pointRadius: 3` (yearly จุดน้อย จะดูดีกว่าเมื่อเห็นจุด) + ลบ `maxTicksLimit: 10` (ปกติมีแค่ ~15 จุด); label dataset เปลี่ยนเป็น `'ราคา (ปิดสิ้นปี)'` — scope: signature เดิม, ไม่เพิ่ม query param, ใช้ default granularity (yearly) — Acceptance: เปิด detail CPALL.BK → line chart แสดง ~10-15 จุด + x-axis label เป็นปี (2015, 2016, ...) + มี pointRadius visible + no 'maxTicksLimit' ใน chart options

### Reference
```javascript
// projects/MaxMahon/web/app.js — renderYieldTrend current @ line 945-983

function renderYieldTrend(canvasId, dividendHistory, yearlyMetrics) {
  const el = document.getElementById(canvasId);
  if (!el) return;
  const years = Object.keys(dividendHistory || {}).sort();
  const yearMap = new Map((yearlyMetrics || []).map(m => [String(m.year), m]));
  const points = years
    .map(y => {
      const dps = dividendHistory[y];
      const ym = yearMap.get(y) || {};
      const priceAvg = ym.price_avg;
      if (!priceAvg || priceAvg <= 0) return null;
      return { year: y, value: (dps / priceAvg) * 100 };
    })
    .filter(Boolean);
  // ...rolling compute + chart...
}

// NEW — use thaifin's dividend_yield directly (unit=%)

function renderYieldTrend(canvasId, dividendHistory, yearlyMetrics) {
  const el = document.getElementById(canvasId);
  if (!el) return;
  const points = (yearlyMetrics || [])
    .map(m => {
      const dy = m.dividend_yield;  // unit=% from thaifin
      if (dy == null || dy <= 0) return null;
      return { year: String(m.year), value: dy };
    })
    .filter(Boolean);
  if (points.length < 3) {
    el.replaceWith(Object.assign(document.createElement('div'), {
      className: 'chart-placeholder',
      textContent: 'ข้อมูล yield trend ไม่พอ (ต้องการ ≥3 จุด)',
    }));
    return;
  }
  const yields = points.map(p => p.value);
  const labels = points.map(p => p.year);
  const rolling = yields.map((_, i, arr) => {
    const slice = arr.slice(Math.max(0, i - 4), i + 1);
    return slice.reduce((a, b) => a + b, 0) / slice.length;
  });
  new Chart(el.getContext('2d'), {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'Yield %', data: yields, borderColor: '#1d5b4f', tension: 0.1 },
        { label: 'Rolling 5y', data: rolling, borderColor: '#b45309', borderDash: [4, 4], tension: 0.1 },
      ],
    },
    options: { responsive: true, maintainAspectRatio: false },
  });
}
```

```javascript
// projects/MaxMahon/web/app.js — loadPriceHistoryChart current @ line ~910-943

async function loadPriceHistoryChart(symbol, canvasId) {
  const el = document.getElementById(canvasId);
  if (!el) return;
  try {
    const res = await fetch(`${API}/api/stock/${encodeURIComponent(symbol)}/price-history`);
    if (!res.ok) throw new Error('fetch fail ' + res.status);
    const { data } = await res.json();
    if (!data || !data.length) throw new Error('empty');
    new Chart(el.getContext('2d'), {
      type: 'line',
      data: {
        labels: data.map(p => p.date),
        datasets: [{
          label: 'ราคา',
          data: data.map(p => p.close),
          borderColor: '#1f3f76',
          tension: 0.2,
          fill: false,
          pointRadius: 0,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { ticks: { maxTicksLimit: 10 } } },
      },
    });
  } catch (e) {
    el.replaceWith(Object.assign(document.createElement('div'), {
      className: 'chart-placeholder',
      textContent: 'ข้อมูลราคาย้อนหลังยังไม่พร้อม',
    }));
  }
}

// NEW — handle yearly granularity response (15 points max, YYYY-12-31 dates)

async function loadPriceHistoryChart(symbol, canvasId) {
  const el = document.getElementById(canvasId);
  if (!el) return;
  try {
    const res = await fetch(`${API}/api/stock/${encodeURIComponent(symbol)}/price-history`);
    if (!res.ok) throw new Error('fetch fail ' + res.status);
    const { data } = await res.json();
    if (!data || !data.length) throw new Error('empty');
    new Chart(el.getContext('2d'), {
      type: 'line',
      data: {
        labels: data.map(p => p.date),
        datasets: [{
          label: 'ราคา (ปิดสิ้นปี)',
          data: data.map(p => p.close),
          borderColor: '#1f3f76',
          tension: 0.2,
          fill: false,
          pointRadius: 3,  // yearly = fewer points, show them
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: {
              callback: function(val) {
                const label = this.getLabelForValue(val) || '';
                return label.slice(0, 4);  // 'YYYY-12-31' → 'YYYY'
              },
            },
          },
        },
      },
    });
  } catch (e) {
    el.replaceWith(Object.assign(document.createElement('div'), {
      className: 'chart-placeholder',
      textContent: 'ข้อมูลราคาย้อนหลังยังไม่พร้อม',
    }));
  }
}
```

## Phase 5: Invariants + Verify
- [x] แก้ `projects/MaxMahon/CLAUDE.md` — เพิ่ม section ใหม่ '### Data Source Invariants' หลัง section 'Data Sources' (current line 15-20) — insert ระหว่างบรรทัด 20 (`...via thaifin`) และ 22 (`### User Data`) — 3 rules + don't/do examples — scope: **ห้ามแก้ section อื่น** (Scoring version, Reference files, Alerting etc.), เพิ่มเฉพาะ invariants block — Acceptance: `grep -A 20 'Data Source Invariants' projects/MaxMahon/CLAUDE.md` return header + 3 rules + examples; ยังมี `### User Data` อยู่หลัง section ใหม่นี้
- [x] Integration test rerun + grep log spam — รัน `py C:/WORKSPACE/projects/MaxMahon/scripts/integration_test.py 2>&1 | tee /tmp/integ_log.txt` แล้วตรวจ `grep -c 'possibly delisted' /tmp/integ_log.txt` — ค่าต้อง **0** (ไม่มี yfinance log spam จาก price_avg path อีก); integration test tag assertions อาจยัง 3/5 (data-driven — CPALL/GULF fail 5-5-5-5 ไม่เกี่ยว data source) + runtime < 60s (เร็วขึ้นจาก 14s เดิมเพราะไม่ fetch yfinance monthly history) — scope: verify ผ่าน log analysis, ไม่แก้ integration_test.py — Acceptance: 'possibly delisted' count = 0 + runtime < 60s + integration test benchmark PASS

### Reference
```markdown
<!-- projects/MaxMahon/CLAUDE.md — insert AFTER line 20 ('Universe: 933 stocks...'), BEFORE line 22 ('### User Data') -->

### Data Sources
- **Primary:** thaifin — 10-16 ปี financial statements + ratios
- **Supplement:** yfinance — realtime price, 52w range, forward PE, market cap, DPS, capex, interest_expense
- **DPS = Source of Truth** — ปันผลต่อหุ้นใช้จาก yfinance dividends history โดยตรง, yield% คำนวณจาก DPS/price
- **FCF = OCF - capex** — ไม่ใช้ total investing activities
- **Universe:** 933 stocks (SET 704 + mai 229) via thaifin

### Data Source Invariants

**Rule 1 — Historical/yearly data:**
- ใช้ **thaifin เท่านั้น** สำหรับ field ที่เป็นต่อปี (close, dividend_yield, mkt_cap, bvps, payout_ratio, pe_ratio, pb_ratio, roe, net_margin, revenue, earnings, etc.)
- yfinance yearly ใช้ได้เฉพาะเป็น **fallback** เมื่อ thaifin fail (ผ่าน `_fetch_yfinance_legacy` path ใน fetch_data.py)

**Rule 2 — yfinance ใช้ได้เฉพาะ:**
- Realtime price (current close)
- 52-week range
- Market cap snapshot (ปัจจุบัน — ใช้ thaifin ถ้ามี historical)
- Forward PE
- Raw dividends history (pandas Series of DPS events — สำหรับ DPS = source of truth)
- DCA simulator (granular monthly price สำหรับ backtest — ผ่าน `/api/stock/{sym}/price-history?granularity=monthly`)

**Rule 3 — ก่อนเพิ่ม field ใหม่ใน yearly_metrics:**
- Cross-check `_fetch_thaifin` column list ก่อนเสมอ (data_adapter.py:107-146 reads)
- ถ้า thaifin มี column นั้น → expose ตรงๆ ใน yearly_metrics dict (build at line 176-203) ห้ามเรียก yfinance
- ถ้า thaifin ไม่มี → document reason ใน code comment (เช่น `interest_expense` ไม่มีใน thaifin → yfinance supplement)

**ตัวอย่าง:**
- ❌ เรียก `yf.Ticker(sym).history(period='10y', interval='1mo')` เพื่อ compute `price_avg` — thaifin มี `close` per year อยู่แล้ว
- ❌ เรียก `yf.Ticker(sym).info.get('marketCap')` เพื่อ historical mcap — thaifin มี `mkt_cap` per year
- ✅ เรียก `yf.Ticker(sym).history(period='10y', interval='1mo')` เฉพาะ DCA simulator endpoint ที่ต้องการ granular monthly
- ✅ เรียก `yf.Ticker(sym).info.get('fiftyTwoWeekHigh')` เพราะ thaifin ไม่มี 52w range
```
