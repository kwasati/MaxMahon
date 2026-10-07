---
project: MaxMahon
created: 2026-04-23
last_updated: 2026-04-23
status: done
---

# Data Source Refactor — thaifin Hard-Primary + yahooquery Supplement

> Refactor MaxMahon data layer: thaifin เป็น single source of truth สำหรับทุกอย่างที่มันมี (fundamentals 16y, sector SET taxonomy, ev_per_ebit_da, cash, roa, yoy growth) — swap yfinance → yahooquery เฉพาะ 3 จุดที่ thaifin ไม่มี (realtime price, raw DPS events, capex/interest_expense per year). อ้างอิง research file projects/MaxMahon/docs/research-thai-stock-data-sources.md — yfinance Thai coverage ตื้น (4-5 ปี) + sector ใช้ GICS ไม่ตรง ดร.นิเวศน์ model. ต้องทำก่อน UI redesign + feature จัดพอร์ตสไตล์แมกซ์ เพื่อให้ feature ใหม่ใช้ sector SET แท้ตั้งแต่ต้น

## Phase 1: Expand thaifin coverage (ใช้ของที่มีอยู่ให้เต็ม)
- [x] แก้ `projects/MaxMahon/scripts/data_adapter.py` function `_fetch_thaifin` (บรรทัด 100-318) เพิ่ม extract thaifin columns ที่ยังไม่ได้ใช้เข้า `yearly_metrics[]` dict: `cash` (level เงินสด), `roa_year` (_safe_pct จาก `roa`), `revenue_yoy` (_safe_pct), `net_profit_yoy` (_safe_pct), `eps_yoy` (_safe_pct จาก `earning_per_share_yoy`), `cash_cycle`, `sga_per_revenue_ratio`, `financing_activities`, `ev_per_ebit_da`. เพิ่ม key เดียวกันใน snapshot dict (latest values). — scope: ไม่แก้ schema ที่ s'tream ออก API ให้ UI ในรอบนี้ — Acceptance: รัน `py -c "import sys; sys.path.insert(0,'projects/MaxMahon/scripts'); from data_adapter import _fetch_thaifin; d=_fetch_thaifin('CPALL'); ym=d['yearly_metrics'][-1]; assert 'cash' in ym and 'ev_per_ebit_da' in ym and 'revenue_yoy' in ym; print(ym['cash'], ym['ev_per_ebit_da'], ym['revenue_yoy'])"` ออกค่าตัวเลขไม่ใช่ KeyError
- [x] แก้ `projects/MaxMahon/scripts/screen_stocks.py` quality_score EV/EBITDA bucket (ใช้ grep ค้นหา `ev_ebitda` หรือ `ev_per_ebit` เพื่อหา location) ให้ใช้ thaifin `ev_per_ebit_da` จาก yearly_metrics latest year โดยตรง แทน compute เอง (ถ้า currently compute เอง). ถ้าไม่ได้ compute แต่ pull จาก yfinance ก็ swap เป็น thaifin ตรงๆ — scope: ไม่แก้ logic คะแนน แค่เปลี่ยนแหล่งข้อมูล — Acceptance: screen_stocks.py ไม่อ้างอิง yfinance field สำหรับ EV/EBITDA — grep `yf_info.*ebit|yfinance.*ebit` ต้องไม่เจอใน quality_score function

### Reference
```python
# current (data_adapter.py:200-232) — yearly_metrics dict มีแค่บางช่อง
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
    "dividends_paid": None,
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
    "close": close,
    "dividend_yield": dy,
    "mkt_cap": mkt_cap,
    "bvps": bvps,
    "payout_ratio": payout_ratio_year,
})

# new — เพิ่ม 9 fields จาก thaifin ที่ยังไม่แตะ
# (อ่าน row เพิ่มก่อน append)
cash_val = _safe(df.loc[year].get("cash"))
roa_year = _safe_pct(df.loc[year].get("roa"))
revenue_yoy = _safe_pct(df.loc[year].get("revenue_yoy"))
net_profit_yoy = _safe_pct(df.loc[year].get("net_profit_yoy"))
eps_yoy = _safe_pct(df.loc[year].get("earning_per_share_yoy"))
cash_cycle = _safe(df.loc[year].get("cash_cycle"))
sga_ratio_col = _safe_pct(df.loc[year].get("sga_per_revenue"))  # ชื่อเดียวกับที่มี แต่คง consistency
financing = _safe(df.loc[year].get("financing_activities"))
ev_ebitda_val = _safe(df.loc[year].get("ev_per_ebit_da"))

yearly_metrics.append({
    # ...(ของเดิมทั้งหมด)...
    "cash": cash_val,
    "roa_year": roa_year,
    "revenue_yoy": revenue_yoy,
    "net_profit_yoy": net_profit_yoy,
    "eps_yoy": eps_yoy,
    "cash_cycle": cash_cycle,
    "financing_activities": financing,
    "ev_per_ebit_da": ev_ebitda_val,
})
```

## Phase 2: Swap yfinance → yahooquery (data_adapter supplement)
- [x] Rewrite `projects/MaxMahon/scripts/data_adapter.py` function `_fetch_yfinance_supplement` (บรรทัด 326-395) → rename เป็น `_fetch_yahoo_supplement` ใช้ `yahooquery.Ticker` แทน `yfinance.Ticker`. ต้อง return schema **เหมือนเดิมเป๊ะ** (`info`, `divs`, `recent_dividends`, `dps_by_year`, `capex_by_year`, `operating_income_by_year`, `interest_expense_by_year`). mapping: `Ticker(sym).summary_detail[sym]` → info, `Ticker(sym).dividend_history(start='2000-01-01')` → divs (DataFrame columns: `dividends`), `Ticker(sym).cash_flow(frequency='a')` → DataFrame rows (asOfDate column), extract `CapitalExpenditure` → capex_by_year, `Ticker(sym).income_statement(frequency='a')` → extract `OperatingIncome` + `InterestExpense`. info fields ที่ MaxMahon ใช้: `currentPrice`/`regularMarketPrice` → map ใช้ `Ticker.price[sym].regularMarketPrice`, `marketCap` → `summary_detail.marketCap`, `trailingPE` → `summary_detail.trailingPE`, `forwardPE` → `summary_detail.forwardPE`, `priceToBook` → `key_stats.priceToBook`, `dividendRate` → `summary_detail.dividendRate`, `trailingAnnualDividendRate` → `summary_detail.trailingAnnualDividendRate`, `payoutRatio` → `summary_detail.payoutRatio`, `fiveYearAvgDividendYield` → `summary_detail.fiveYearAvgDividendYield`, `fiftyTwoWeekHigh/Low` → `summary_detail.fiftyTwoWeekHigh/Low`, `fiftyDayAverage/twoHundredDayAverage` → `summary_detail.fiftyDayAverage/twoHundredDayAverage`, `freeCashflow` + `operatingCashflow` → `key_stats`. — scope: ห้ามเปลี่ยน return schema, ห้ามแก้ fetch_fundamentals() — Acceptance: รัน `py -c "import sys; sys.path.insert(0,'projects/MaxMahon/scripts'); from data_adapter import _fetch_yahoo_supplement; d=_fetch_yahoo_supplement('CPALL'); assert d['info'].get('currentPrice'); assert len(d['dps_by_year'])>5; assert len(d['capex_by_year'])>0; print('OK', list(d.keys()))" ออก `OK` + มี key ครบ 7 ตัว
- [x] แก้ `projects/MaxMahon/scripts/data_adapter.py` function `fetch_fundamentals` ทุก reference ของ `_fetch_yfinance_supplement` → `_fetch_yahoo_supplement` (บรรทัด 400 alias + บรรทัด 415). ตัด `yf_info.get("sector")` และ `yf_info.get("industry")` fallback ใน merge section (บรรทัด 470-471) — ใช้ thaifin อย่างเดียวเป็น `sector = tf_info.get("sector", "N/A")` / `industry = tf_info.get("industry", "N/A")` — scope: ห้ามเปลี่ยน field อื่น เช่น price / mkt_cap / DPS fallback — Acceptance: grep `yf_info.get.*sector|yf_info.get.*industry` ใน data_adapter.py ต้องไม่เจอ. รัน `fetch_fundamentals('CPALL')['info']['sector']` ต้อง `== 'Commerce'` (SET taxonomy ไม่ใช่ 'Consumer Defensive' GICS)
- [x] ลบ `projects/MaxMahon/scripts/data_adapter.py` line top-level `import yfinance as yf` ถ้ามี + function alias `fetch_yfinance_supplement = _fetch_yfinance_supplement` (บรรทัด 400) ให้ชี้ไป `_fetch_yahoo_supplement` หรือลบถ้าไม่มี caller ข้าม module. grep ก่อนลบ: `grep -rn "fetch_yfinance_supplement\|from data_adapter import" projects/MaxMahon/scripts/ projects/MaxMahon/server/` — ถ้ามี external caller ต้อง alias ไว้ก่อน — scope: ลบ import ที่ไม่ใช้แล้ว — Acceptance: `py -c "import ast; t=ast.parse(open('projects/MaxMahon/scripts/data_adapter.py').read()); imports=[n.names[0].name for n in ast.walk(t) if isinstance(n,ast.Import)]; assert 'yfinance' not in imports"` ไม่ throw

### Reference
```python
# current (data_adapter.py:326-395) — yfinance supplement
def _fetch_yfinance_supplement(symbol: str) -> dict:
    try:
        import yfinance as yf
        yf_sym = _to_yf_symbol(symbol)
        tk = yf.Ticker(yf_sym)
        info = tk.info or {}
        if len(info) < 5:
            return {"info": info, "divs": None, "error": f"near-empty info ({len(info)} keys)"}
        divs = tk.dividends
        # ... capex, operating_income, interest_expense from tk.cashflow, tk.income_stmt

# new (yahooquery) — return schema เดิมเป๊ะ
def _fetch_yahoo_supplement(symbol: str) -> dict:
    """Fetch realtime price + DPS events + capex/interest via yahooquery (swapped from yfinance)."""
    try:
        from yahooquery import Ticker
        yq_sym = _to_yf_symbol(symbol)  # .BK suffix เดิม
        tk = Ticker(yq_sym)

        # Build info dict จาก multiple endpoints — maintain yfinance-style keys
        sd = tk.summary_detail.get(yq_sym, {}) if isinstance(tk.summary_detail, dict) else {}
        px = tk.price.get(yq_sym, {}) if isinstance(tk.price, dict) else {}
        ks = tk.key_stats.get(yq_sym, {}) if isinstance(tk.key_stats, dict) else {}
        fd = tk.financial_data.get(yq_sym, {}) if isinstance(tk.financial_data, dict) else {}
        info = {
            "currentPrice": px.get("regularMarketPrice") or fd.get("currentPrice"),
            "regularMarketPrice": px.get("regularMarketPrice"),
            "marketCap": sd.get("marketCap") or px.get("marketCap"),
            "trailingPE": sd.get("trailingPE"),
            "forwardPE": sd.get("forwardPE") or ks.get("forwardPE"),
            "priceToBook": ks.get("priceToBook"),
            "dividendRate": sd.get("dividendRate"),
            "trailingAnnualDividendRate": sd.get("trailingAnnualDividendRate"),
            "payoutRatio": sd.get("payoutRatio"),
            "fiveYearAvgDividendYield": sd.get("fiveYearAvgDividendYield"),
            "fiftyTwoWeekHigh": sd.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekLow": sd.get("fiftyTwoWeekLow"),
            "fiftyDayAverage": sd.get("fiftyDayAverage"),
            "twoHundredDayAverage": sd.get("twoHundredDayAverage"),
            "freeCashflow": ks.get("freeCashflow") or fd.get("freeCashflow"),
            "operatingCashflow": fd.get("operatingCashflow"),
            "trailingEps": ks.get("trailingEps"),
            "forwardEps": ks.get("forwardEps"),
            "dividendYield": sd.get("dividendYield"),
            "revenueGrowth": fd.get("revenueGrowth"),
            "earningsGrowth": fd.get("earningsGrowth"),
            "profitMargins": fd.get("profitMargins"),
            "grossMargins": fd.get("grossMargins"),
            "operatingMargins": fd.get("operatingMargins"),
            "returnOnEquity": fd.get("returnOnEquity"),
            "returnOnAssets": fd.get("returnOnAssets"),
            "debtToEquity": fd.get("debtToEquity"),
            "currentRatio": fd.get("currentRatio"),
            "totalRevenue": fd.get("totalRevenue"),
            "shortName": px.get("shortName"),
        }
        if info.get("currentPrice") is None:
            return {"info": {}, "divs": None, "error": "no price data"}

        # Dividends — yahooquery dividend_history returns DataFrame (date index, dividends col)
        divs_df = tk.dividend_history(start="2000-01-01")
        dps_by_year = {}
        recent_divs = []
        divs = None
        if hasattr(divs_df, 'shape') and not divs_df.empty:
            # multi-index (symbol, date) — filter
            if hasattr(divs_df.index, 'get_level_values'):
                divs_df = divs_df.xs(yq_sym, level=0) if yq_sym in divs_df.index.get_level_values(0) else divs_df
            divs = divs_df['dividends'] if 'dividends' in divs_df.columns else divs_df.iloc[:, 0]
            recent_divs = divs.tail(8).tolist()
            for idx, val in divs.items():
                y = idx.year if hasattr(idx, 'year') else int(str(idx)[:4])
                dps_by_year[y] = dps_by_year.get(y, 0) + round(float(val), 4)

        # Capex + Operating Income + Interest Expense — cash_flow + income_statement annual
        capex_by_year, operating_income_by_year, interest_expense_by_year = {}, {}, {}
        try:
            cf = tk.cash_flow(frequency='a')  # DataFrame with asOfDate col
            if hasattr(cf, 'shape') and not cf.empty and 'CapitalExpenditure' in cf.columns:
                for _, row in cf.iterrows():
                    y = row['asOfDate'].year if hasattr(row['asOfDate'], 'year') else int(str(row['asOfDate'])[:4])
                    val = _safe(row['CapitalExpenditure'])
                    if val is not None:
                        capex_by_year[y] = val
        except Exception:
            pass
        try:
            inc = tk.income_statement(frequency='a')
            if hasattr(inc, 'shape') and not inc.empty:
                for _, row in inc.iterrows():
                    y = row['asOfDate'].year if hasattr(row['asOfDate'], 'year') else int(str(row['asOfDate'])[:4])
                    oi = _safe(row.get('OperatingIncome'))
                    ie = _safe(row.get('InterestExpense'))
                    if oi is not None: operating_income_by_year[y] = oi
                    if ie is not None: interest_expense_by_year[y] = ie
        except Exception:
            pass

        return {
            "info": info,
            "divs": divs,
            "recent_dividends": recent_divs,
            "dps_by_year": dps_by_year,
            "capex_by_year": capex_by_year,
            "operating_income_by_year": operating_income_by_year,
            "interest_expense_by_year": interest_expense_by_year,
        }
    except Exception as e:
        logger.warning("yahooquery failed for %s: %s", symbol, e)
        return {"info": {}, "divs": None, "recent_dividends": [],
                "dps_by_year": {}, "capex_by_year": {},
                "operating_income_by_year": {}, "interest_expense_by_year": {}}


# current (data_adapter.py:470-471) — sector/industry มี yfinance fallback
sector = tf_info.get("sector") or yf_info.get("sector", "N/A")
industry = tf_info.get("industry") or yf_info.get("industry", "N/A")

# new — thaifin อย่างเดียว
sector = tf_info.get("sector", "N/A")
industry = tf_info.get("industry", "N/A")
```

## Phase 3: Swap yfinance → yahooquery (server/app.py — 3 จุด)
- [x] แก้ `projects/MaxMahon/server/app.py` DCA stock endpoint (บรรทัด 922-933) — swap `import yfinance as yf` + `yf.Ticker(ticker_symbol)` → yahooquery. ต้องคง behavior: รับ symbol → fetch historical → ใช้ต่อใน DCA backtest logic ด้านล่าง. Note: code ด้านล่างอาจใช้ `ticker.history(period=..., interval=...)` หรือ `ticker.dividends` — ต้องอ่าน 934-920 บรรทัดถัดไปก่อน swap เพราะ yahooquery มี API ต่าง (`tk.history(period='max')` คืน multi-index DataFrame, `tk.dividend_history()` แยก) — ต้อง wrap call ให้คืน pandas DataFrame/Series รูปแบบเดิมให้ downstream code ไม่พัง — scope: ไม่แก้ DCA logic คำนวณ แค่ swap data source — Acceptance: GET `/api/simulate/dca?symbol=CPALL&days=1,15` ตอบ 200 + มีค่า backtest + forward projection (test manually หรือ curl)
- [x] แก้ `projects/MaxMahon/server/app.py` `/api/stock/{symbol}/price-history` monthly path (บรรทัด 2279-2304) — swap `import yfinance as yf` + `yf.Ticker(symbol).history(period='10y', interval='1mo', auto_adjust=False)` → yahooquery equivalent. yahooquery: `Ticker(symbol).history(period='10y', interval='1mo', adj_ohlc=False)` คืน DataFrame index = (symbol, date) — ต้อง `.xs(symbol, level=0)` ก่อนใช้. downstream code iterate `hist.iterrows()` ใช้ `row['Close']` หรือ `row['close']` (yahooquery lowercase!) — ต้อง map key. — scope: ไม่แก้ cache logic / yearly path — Acceptance: GET `/api/stock/CPALL.BK/price-history?granularity=monthly` ตอบ 200 + มี data list + field `source` เปลี่ยนเป็น `yahooquery_monthly` แทน `yfinance_monthly`
- [x] แก้ `projects/MaxMahon/server/app.py` function `_yf_monthly_series` (บรรทัด 2317-2350) — rename เป็น `_yahoo_monthly_series` ใช้ yahooquery แทน. ต้องคง return schema `list[tuple(date_str, close, div_this_month)]`. update caller `simulate_dca_portfolio` (บรรทัด 2360ish) + `simulate_portfolio_backtest` (ถ้ามี) ใช้ชื่อใหม่ — scope: ห้ามเปลี่ยน return tuple format — Acceptance: POST `/api/simulate/dca-portfolio` ด้วย payload 2 positions ตอบ 200 + มี monthly projection
- [x] ลบ `import yfinance as yf` ใน `projects/MaxMahon/server/app.py` ทั้งหมด (3 จุด: บรรทัด 922, 2282, 2323) — swap tasks ด้านบนควรทำให้ไม่ต้องใช้แล้ว. grep ยืนยัน: `grep -n "yfinance\|yf\." projects/MaxMahon/server/app.py` — ผลต้องว่าง — scope: ตัดเฉพาะ yfinance, ห้ามแตะ library อื่น — Acceptance: grep `yfinance\|import yf` ใน server/app.py ไม่เจอ

### Reference
```python
# current (server/app.py:922-931)
import yfinance as yf
import pandas as pd
ticker_symbol = symbol if ".BK" in symbol.upper() else symbol + ".BK"
ticker_symbol = ticker_symbol.upper()
try:
    ticker = yf.Ticker(ticker_symbol)
except Exception as e:
    raise HTTPException(400, f"Cannot fetch ticker: {e}")

# new
from yahooquery import Ticker as YQTicker
import pandas as pd
ticker_symbol = symbol if ".BK" in symbol.upper() else symbol + ".BK"
ticker_symbol = ticker_symbol.upper()
try:
    ticker = YQTicker(ticker_symbol)
except Exception as e:
    raise HTTPException(400, f"Cannot fetch ticker: {e}")
# downstream: ticker.history(period='max', interval='1mo') → DataFrame (needs .xs(ticker_symbol, level=0))
# downstream: ticker.dividend_history(start='...') → DataFrame


# current (server/app.py:2280-2304) — monthly price-history
if granularity == 'monthly':
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
        ...
    }

# new
if granularity == 'monthly':
    try:
        from yahooquery import Ticker as YQTicker
        loop = asyncio.get_event_loop()
        hist = await loop.run_in_executor(
            None,
            lambda: YQTicker(symbol).history(period="10y", interval="1mo", adj_ohlc=False),
        )
    except Exception as e:
        raise HTTPException(503, f"yahooquery fetch failed: {e}")
    if not hasattr(hist, 'shape') or hist.empty:
        raise HTTPException(404, f"no monthly price history for {symbol}")
    # yahooquery multi-index (symbol, date) — flatten
    if hasattr(hist.index, 'get_level_values') and symbol in hist.index.get_level_values(0):
        hist = hist.xs(symbol, level=0)
    data = [
        {"date": idx.strftime("%Y-%m-%d") if hasattr(idx, 'strftime') else str(idx), "close": float(row.get("close") or row.get("Close") or 0)}
        for idx, row in hist.iterrows()
    ]
    payload = {
        "symbol": symbol,
        "source": "yahooquery_monthly",
        ...
    }
```

## Phase 4: Remove yfinance legacy fallback (ปิด door ห้ามกลับมาใช้)
- [x] ลบ `projects/MaxMahon/scripts/fetch_data.py` function `_fetch_yfinance_legacy` ทั้งหมด (บรรทัด 198 ถึงจบ function — อ่านก่อนเพื่อหา end line) + ลบ `from scripts.data_adapter import ... fetch_yfinance_supplement` (บรรทัด 26 ถ้ามี) + ลบ `import yfinance as yf` (บรรทัด 15). แก้ `fetch_multi_year` (บรรทัด 404+) ที่ fallback เรียก `_fetch_yfinance_legacy(symbol)` (บรรทัด 432-433) → แทนที่ด้วย `return {"symbol": symbol, "delisted": True, "error": "thaifin fetch failed — no fallback"}`. แก้ docstring บรรทัด 3-5 (`Fallback: yfinance ... / Supplement: yfinance ...`) → `Supplement: yahooquery (realtime price, DPS events, capex/interest per year)` + ลบบรรทัด `Fallback:` ทิ้ง — scope: ไม่แก้ validate_metrics หรือ sanity check — Acceptance: grep `yfinance\|_fetch_yfinance` ใน fetch_data.py ไม่เจอ. `py -c "import ast; t=ast.parse(open('projects/MaxMahon/scripts/fetch_data.py').read()); funcs=[n.name for n in ast.walk(t) if isinstance(n,ast.FunctionDef)]; assert '_fetch_yfinance_legacy' not in funcs"` ไม่ throw
- [x] แก้ `projects/MaxMahon/scripts/update_universe.py` comment บรรทัด 17 `# Combine, add .BK suffix for yfinance compatibility` → `# Combine, add .BK suffix for Yahoo (yahooquery) compatibility` — scope: ไม่แก้ logic — Acceptance: grep `yfinance` ใน update_universe.py ไม่เจอ

### Reference
```python
# current (fetch_data.py:3-15)
"""Fetch multi-year financial data for a stock from thaifin (primary).
Fallback: yfinance (4-5 years statements + realtime price)
Supplement: yfinance always used for realtime price, 52w range, forward PE, etc.
"""
import yfinance as yf

# new
"""Fetch multi-year financial data for a stock from thaifin (primary only).
Supplement: yahooquery (realtime price, DPS events, capex + interest_expense per year).
No fallback: if thaifin fails the stock is treated as delisted/missing.
"""
# (remove `import yfinance as yf` entirely)


# current (fetch_data.py:430-433) — fetch_multi_year fallback
    # Fallback: full yfinance legacy
    return _fetch_yfinance_legacy(symbol)

# new
    # No legacy fallback — thaifin is single source of truth for fundamentals
    return {"symbol": symbol, "delisted": True, "error": "thaifin fetch returned no data"}
```

## Phase 5: Update docs + CLAUDE.md + CHANGELOG
- [x] แก้ `projects/MaxMahon/CLAUDE.md` — (a) บรรทัด 5 `Python + thaifin + yfinance (supplement)` → `Python + thaifin (primary) + yahooquery (supplement)`. (b) Data Sources section (บรรทัด 15-20) `Supplement: yfinance` → `Supplement: yahooquery`. (c) Data Source Invariants Rule 1 เพิ่มประโยค `thaifin เป็น single source of truth ไม่มี fallback — ถ้า thaifin fail = stock delisted`. (d) Rule 2 replace `yfinance` → `yahooquery` + update whitelist (ตัด Forward PE เพราะ thaifin มีผ่าน price_earning_ratio / market_cap snapshot เพราะ thaifin มี mkt_cap yearly — เหลือ: **Realtime price**, **Raw dividends history (DPS events)**, **Capex + Operating Income + Interest Expense per year**, **52w range**, **DCA simulator monthly granular price**). (e) Rule 3 examples เปลี่ยน `yf.Ticker` → `yahooquery.Ticker`. (f) Key Files บรรทัด 77 `thaifin + yfinance adapter` → `thaifin + yahooquery adapter`. — scope: ไม่แก้ Niwes section / Scoring / Pipeline — Acceptance: grep `yfinance` ใน CLAUDE.md ไม่เจอเลย
- [x] แก้ `projects/MaxMahon/README.md` + `projects/MaxMahon/docs/niwes/00-backtest-protocol.md` + `projects/MaxMahon/docs/niwes/00-data-schema.md` — replace yfinance references → yahooquery (cosmetic). แก้ `projects/MaxMahon/max-server.bat` ถ้ามี reference — scope: ไม่เขียน doc เพิ่ม ไม่เปลี่ยน structure — Acceptance: grep -r `yfinance` projects/MaxMahon/ — เหลือแค่ `docs/research-thai-stock-data-sources.md` (research เก็บชื่อ library เพื่อเปรียบเทียบ = ควรมี) + `CHANGELOG.md` entry ใหม่ (release note)
- [x] เขียน entry ใหม่ใน `projects/MaxMahon/CHANGELOG.md` version `v5.1.0` (bump minor จาก v5.0.0) — หัวข้อ `Data Source Refactor — thaifin Hard-Primary + yahooquery Supplement`. list การเปลี่ยน: (1) ตัด yfinance ออกจาก code ทั้งหมด (4 files), (2) swap supplement → yahooquery (stable API + deeper statements), (3) sector ใช้ thaifin SET taxonomy อย่างเดียว (ตัด GICS fallback จาก yfinance), (4) expose thaifin columns ใหม่ 9 ตัว (cash, roa_year, revenue_yoy, net_profit_yoy, eps_yoy, cash_cycle, financing_activities, ev_per_ebit_da), (5) ใช้ thaifin ev_per_ebit_da ตรงๆ แทน compute เอง, (6) ลบ _fetch_yfinance_legacy fallback (thaifin = single source of truth). Link อ้างอิง research file. — scope: ไม่แก้ entry เก่า — Acceptance: มี `## v5.1.0` entry ใน CHANGELOG.md

### Reference
```markdown
# current (CLAUDE.md:28-46) — Rule 2
**Rule 2 — yfinance ใช้ได้เฉพาะ:**
- Realtime price (current close)
- 52-week range
- Market cap snapshot (ปัจจุบัน — ใช้ thaifin ถ้ามี historical)
- Forward PE
- Raw dividends history (pandas Series of DPS events — สำหรับ DPS = source of truth)
- DCA simulator (granular monthly price สำหรับ backtest — ผ่าน `/api/stock/{sym}/price-history?granularity=monthly`)

**Rule 3 — ก่อนเพิ่ม field ใหม่ใน yearly_metrics:**
- ...
- ❌ เรียก `yf.Ticker(sym).history(period='10y', interval='1mo')` เพื่อ compute `price_avg` — thaifin มี `close` per year อยู่แล้ว
- ❌ เรียก `yf.Ticker(sym).info.get('marketCap')` เพื่อ historical mcap — thaifin มี `mkt_cap` per year
- ✅ เรียก `yf.Ticker(sym).history(period='10y', interval='1mo')` เฉพาะ DCA simulator endpoint ที่ต้องการ granular monthly
- ✅ เรียก `yf.Ticker(sym).info.get('fiftyTwoWeekHigh')` เพราะ thaifin ไม่มี 52w range

# new
**Rule 2 — yahooquery ใช้ได้เฉพาะ:**
- Realtime price (current close)
- 52-week range + 50d/200d moving average
- Raw dividends history (DPS events timestamp + amount — source of truth สำหรับ DPS)
- Capex + Operating Income + Interest Expense per year (thaifin ไม่แยกจาก investing_activities / gross-sga)
- DCA simulator granular monthly price (backtest — ผ่าน `/api/stock/{sym}/price-history?granularity=monthly`)

**Rule 3 — ก่อนเพิ่ม field ใหม่ใน yearly_metrics:**
- ...
- ❌ เรียก `yahooquery.Ticker(sym).history(period='10y', interval='1mo')` เพื่อ compute `price_avg` — thaifin มี `close` per year อยู่แล้ว
- ❌ เรียก `yahooquery.Ticker(sym).price[sym]['marketCap']` เพื่อ historical mcap — thaifin มี `mkt_cap` per year
- ✅ เรียก `yahooquery.Ticker(sym).history(period='10y', interval='1mo')` เฉพาะ DCA simulator endpoint
- ✅ เรียก `yahooquery.Ticker(sym).summary_detail[sym]['fiftyTwoWeekHigh']` เพราะ thaifin ไม่มี 52w range
```

## Phase 6: End-to-end verify (smoke test)
- [x] รัน smoke test script: สร้าง `_shared/tmp/verify_thaifin_primary.py` ที่ import `fetch_multi_year` จาก scripts/fetch_data.py รัน 5 หุ้น CPALL/TCAP/QH/BCP/MC ตรวจ: (a) sector ต้องเป็น SET taxonomy — `CPALL='Commerce'`, `TCAP='Banking'`, `QH='Property Development'`, `BCP='Energy & Utilities'`, `MC='Commerce'` (ต้องไม่ใช่ 'Consumer Defensive' ฯลฯ), (b) `yearly_metrics[-1]` ต้องมี key ใหม่ครบ: `cash`, `ev_per_ebit_da`, `revenue_yoy`, `cash_cycle`, (c) dividend_history ต้องมี data 10+ ปี (DPS events ไม่หาย), (d) capex (negative) ต้องมี ≥ 3 ปี, (e) interest_coverage ต้องมีค่า (operating_income / interest_expense ทำงาน), (f) รัน grep `yfinance` ทั้ง projects/MaxMahon/scripts/ + server/ + update_universe.py → ต้องไม่เจอ. ลบ script หลัง verify เสร็จ — scope: ไม่แก้ code — Acceptance: 5/5 หุ้นผ่านทุก assertion + grep yfinance ใน code ว่าง

### Reference
```python
# _shared/tmp/verify_thaifin_primary.py (temp, ลบหลัง verify)
import sys, subprocess
from pathlib import Path
sys.path.insert(0, str(Path('projects/MaxMahon/scripts').resolve()))
from fetch_data import fetch_multi_year

EXPECT = {
    'CPALL': 'Commerce',
    'TCAP': 'Banking',
    'QH': 'Property Development',
    'BCP': 'Energy & Utilities',
    'MC': 'Commerce',
}
NEW_KEYS = ['cash', 'ev_per_ebit_da', 'revenue_yoy', 'cash_cycle']

for sym, expect_sector in EXPECT.items():
    d = fetch_multi_year(sym)
    assert d.get('sector') == expect_sector, f'{sym}: expected {expect_sector}, got {d.get("sector")}'
    ym = d['yearly_metrics'][-1]
    for k in NEW_KEYS:
        assert k in ym, f'{sym}: missing key {k}'
    assert len(d.get('dividend_history', {})) >= 10, f'{sym}: DPS history thin'
    capex_years = sum(1 for m in d['yearly_metrics'] if m.get('capex') and m['capex'] < 0)
    assert capex_years >= 3, f'{sym}: capex years < 3'
    print(f'{sym}: OK (sector={d["sector"]}, yrs={len(d["yearly_metrics"])})')

# grep check
result = subprocess.run(['grep', '-rn', 'yfinance',
    'projects/MaxMahon/scripts/', 'projects/MaxMahon/server/'],
    capture_output=True, text=True)
assert not result.stdout.strip(), f'yfinance still referenced:\n{result.stdout}'
print('✓ no yfinance references in code')
print('✓ 5/5 stocks passed — refactor verified')
```
