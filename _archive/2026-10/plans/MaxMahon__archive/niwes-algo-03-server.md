---
project: MaxMahon
created: 2026-04-21
last_updated: 2026-04-21
status: done
---

# Server: On-demand Claude + History v2 + Patterns + Exit + Price History APIs

> Part 3 of 5 — refactor server/app.py: extract helpers → split analysis endpoint (GET cache-only + POST trigger keep 3-perspective schema), add history v2/patterns/exit-status/price-history endpoints | Index: niwes-algo-index | Depends on: niwes-algo-02-scan-engine | Parallel-safe with: niwes-algo-04-ui

## Phase 1: Extract Helpers + Split Analysis Endpoint
- [x] แก้ `projects/MaxMahon/server/app.py` — **ก่อน refactor** ให้ extract 2 helpers ออกจาก current `get_stock_analysis()` (lines 1688-1750+) เป็น module-level functions: `build_analysis_prompt(symbol: str) -> str` (คัด code ที่ build prompt จาก snapshot + screener + history ออกมา), `parse_analysis_response(raw: str) -> dict` (JSON extractor ที่ return `{buffett: str, hong: str, max: str}`) — scope: ไม่เปลี่ยน behavior เดิม, แค่ refactor เป็น standalone functions — Acceptance: functions import ได้แยก; current GET endpoint ยัง work
- [x] สร้าง dir `projects/MaxMahon/data/analysis_cache/` + เพิ่ม `data/analysis_cache/` ใน `.gitignore` — Acceptance: dir exists + gitignore entry
- [x] Refactor `GET /api/stock/{symbol}/analysis` เป็น **cache-only** (ไม่เรียก Claude) — อ่าน `data/analysis_cache/{symbol}.json`, return JSON ถ้ามี, raise HTTPException 404 `{status:'no_cache', hint:'POST /analyze to generate'}` ถ้าไม่มี — scope: ไม่เปลี่ยน URL/method — Acceptance: curl GET stock ที่ไม่เคย analyze → 404 with hint; curl GET stock ที่ cache แล้ว → 200 JSON
- [x] เพิ่ม endpoint `POST /api/stock/{symbol}/analyze` — trigger Claude (reuse `_anthropic_client` line 56-61), call `build_analysis_prompt(symbol)` + `messages.create(model='claude-opus-4-7', max_tokens=2000, timeout=60.0)` + `parse_analysis_response(raw)`, write cache `{analyzed_at, model, buffett, hong, max}` (**keep 3-perspective schema** เพื่อ backward compat กับ UI render เดิม), return payload เหมือนกัน — scope: ไม่ auto-trigger, คนต้องเรียก explicit — Acceptance: curl POST /api/stock/CPALL.BK/analyze → 200 + cache file created; ทำ GET ตาม → return cached

### Reference
```python
# projects/MaxMahon/server/app.py — CURRENT (lines 1688-1750+)
@app.get("/api/stock/{symbol}/analysis")
async def get_stock_analysis(symbol: str):
    if _anthropic_client is None:
        raise HTTPException(503, "anthropic package not installed")
    # inline: load snapshot + screener + build prompt
    # ... build prompt inline ...
    response = await loop.run_in_executor(None,
        lambda: _anthropic_client.messages.create(model="claude-opus-4-7", max_tokens=2000,
            messages=[{"role":"user","content":prompt}], timeout=60.0))
    raw_text = response.content[0].text.strip()
    # inline JSON extraction → return {buffett, hong, max}

# NEW — step 1: extract helpers (module level)
import re
from pathlib import Path
import json

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_ANALYSIS_CACHE_DIR = _DATA_DIR / "analysis_cache"
_ANALYSIS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

def build_analysis_prompt(symbol: str) -> str:
    # Move the prompt-building code from current endpoint here verbatim.
    # Load latest snapshot + screener + history; build the Thai prompt that
    # yields a JSON of {buffett, hong, max}.
    ...
    return prompt

def parse_analysis_response(raw: str) -> dict:
    # Try strict JSON parse; fall back to regex-extract a {...} block.
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try: return json.loads(m.group(0))
            except Exception: pass
        return {"buffett": raw, "hong": "", "max": ""}

# NEW — step 2: split endpoints
@app.get("/api/stock/{symbol}/analysis")
async def get_cached_analysis(symbol: str):
    """Cache-only — no Claude call."""
    cache_file = _ANALYSIS_CACHE_DIR / f"{symbol}.json"
    if not cache_file.exists():
        raise HTTPException(404, detail={"status":"no_cache", "hint":"POST /api/stock/{symbol}/analyze to generate"})
    return json.loads(cache_file.read_text(encoding="utf-8"))

@app.post("/api/stock/{symbol}/analyze")
async def trigger_analysis(symbol: str):
    if _anthropic_client is None:
        raise HTTPException(503, "anthropic package not installed or MAX_ANTHROPIC_API_KEY missing")
    prompt = build_analysis_prompt(symbol)
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None,
        lambda: _anthropic_client.messages.create(model="claude-opus-4-7", max_tokens=2000,
            messages=[{"role":"user","content":prompt}], timeout=60.0))
    raw = response.content[0].text.strip()
    parsed = parse_analysis_response(raw)
    payload = {
        "analyzed_at": datetime.now().isoformat(timespec="seconds"),
        "model": "claude-opus-4-7",
        "buffett": parsed.get("buffett", ""),
        "hong": parsed.get("hong", ""),
        "max": parsed.get("max", ""),
    }
    (_ANALYSIS_CACHE_DIR / f"{symbol}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload
```

```
# projects/MaxMahon/.gitignore — append
data/analysis_cache/
```

## Phase 2: History v2 + Patterns + Exit-Status Endpoints
- [x] เพิ่ม endpoint `GET /api/history/v2` ใน server/app.py — import `from history_manager import load_history` (add scripts/ to sys.path) — support query params `?limit=N` (default 50, clamp 1-200) + `?symbol=XXX` (filter entries ที่มี symbol ใน top_candidates) — return `{scans: [...], count: N}` — scope: read-only — Acceptance: curl `/api/history/v2?limit=5` → 200 JSON มี scans array + count key; `?symbol=CPALL.BK` filter ถูก
- [x] เพิ่ม endpoint `GET /api/stock/{symbol}/patterns` — อ่าน latest screener file (sorted glob `screener_*.json`) — หา symbol ใน candidates/review_candidates/filtered_out_stocks (fallback order) — ถ้าเจอ return `{symbol, signals, case_study_tags, moat_tags, hidden_holdings, bucket: 'candidates'|'review'|'filtered'}`; ถ้าไม่เจอเลย → 404 — case_study_tags = signals ที่เป็น key ใน case_study_patterns.json; moat_tags = signals ∩ {BRAND_MOAT,STRUCTURAL_MOAT,GOVT_LOCKIN}; hidden_holdings = `check_hidden_value(symbol)` (ผ่าน data_adapter import) — scope: ไม่ recompute patterns, อ่าน precomputed signals — Acceptance: curl stock ที่อยู่ review bucket ไม่ใช่ candidates → return JSON ด้วย bucket='review'
- [x] เพิ่ม endpoint `GET /api/watchlist/{symbol}/exit-status` — อ่าน `data/exit_baselines.json` (default {}) + latest screener → หา candidate/review entry ของ symbol → return `{symbol, in_watchlist: bool, baseline: dict|null, triggers: [...], severity_summary: {high, medium}}`; ถ้า symbol ไม่มีใน screener (filtered out) → lookup watchlist file ดู in_watchlist เอง + triggers=[] — scope: ไม่ recompute exit signals — Acceptance: curl stock watchlist + มี baseline → 200 JSON มี baseline dict + triggers array

### Reference
```python
# server/app.py — add endpoints
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from history_manager import load_history  # noqa: E402
from data_adapter import check_hidden_value  # noqa: E402

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def _latest_screener() -> dict:
    files = sorted(_DATA_DIR.glob("screener_*.json"), reverse=True)
    if not files:
        raise HTTPException(404, "no screener file found")
    return json.loads(files[0].read_text(encoding="utf-8"))

@app.get("/api/history/v2")
async def get_history_v2(limit: int = 50, symbol: str | None = None):
    limit = min(max(limit, 1), 200)
    hist = load_history()
    scans = hist.get("scans", [])
    if symbol:
        scans = [s for s in scans if any(c.get("symbol") == symbol for c in s.get("top_candidates", []))]
    scans = scans[-limit:]
    return {"scans": scans, "count": len(scans)}

@app.get("/api/stock/{symbol}/patterns")
async def get_stock_patterns(symbol: str):
    screener = _latest_screener()
    entry = next((c for c in screener.get("candidates", []) if c["symbol"] == symbol), None)
    bucket = "candidates" if entry else None
    if not entry:
        entry = next((c for c in screener.get("review_candidates", []) if c.get("symbol") == symbol), None)
        bucket = "review" if entry else bucket
    if not entry:
        entry = next((c for c in screener.get("filtered_out_stocks", []) if c.get("symbol") == symbol), None)
        bucket = "filtered" if entry else bucket
    if not entry:
        raise HTTPException(404, f"symbol {symbol} not in latest screener")
    signals = entry.get("signals", [])
    patterns = json.loads((_DATA_DIR / "case_study_patterns.json").read_text(encoding="utf-8"))
    case_tags = [s for s in signals if s in patterns]
    moat_tags = [s for s in signals if s in {"BRAND_MOAT","STRUCTURAL_MOAT","GOVT_LOCKIN"}]
    return {
        "symbol": symbol,
        "signals": signals,
        "case_study_tags": case_tags,
        "moat_tags": moat_tags,
        "hidden_holdings": check_hidden_value(symbol),
        "bucket": bucket,
    }

@app.get("/api/watchlist/{symbol}/exit-status")
async def get_exit_status(symbol: str):
    baselines = {}
    if (_DATA_DIR / "exit_baselines.json").exists():
        baselines = json.loads((_DATA_DIR / "exit_baselines.json").read_text(encoding="utf-8"))
    screener = _latest_screener()
    entry = next((c for c in screener.get("candidates", []) if c["symbol"] == symbol), None) \
        or next((c for c in screener.get("review_candidates", []) if c.get("symbol") == symbol), None)
    triggers = (entry or {}).get("exit_triggers", []) if entry else []
    user_data = json.loads((Path(__file__).resolve().parent.parent / "user_data.json").read_text(encoding="utf-8")) \
        if (Path(__file__).resolve().parent.parent / "user_data.json").exists() else {}
    in_wl = symbol in set(user_data.get("watchlist", []))
    return {
        "symbol": symbol,
        "in_watchlist": in_wl,
        "baseline": baselines.get(symbol),
        "triggers": triggers,
        "severity_summary": {
            "high": sum(1 for t in triggers if t.get("severity") == "high"),
            "medium": sum(1 for t in triggers if t.get("severity") == "medium"),
        },
    }
```

## Phase 3: Price History Endpoint
- [x] เพิ่ม endpoint `GET /api/stock/{symbol}/price-history` ใน server/app.py — ดึง 10yr monthly closes จาก yfinance `yf.Ticker(yf_sym).history(period='10y', interval='1mo')` + cache ผล 24h ใน `data/price_history/{symbol}.json` `{fetched_at, data: [{date:'YYYY-MM-DD', close: float}, ...]}` (refresh ถ้า fetched_at เกิน 24h) — return cached data — scope: error-safe (fetch fail → return 503 + hint), สร้าง dir อัตโนมัติ + เพิ่ม `data/price_history/` ใน gitignore — Acceptance: curl `/api/stock/CPALL.BK/price-history` → 200 + JSON มี `data` array ~120 entries (10yr × 12 months)

### Reference
```python
# server/app.py — new endpoint
import yfinance as yf
from datetime import datetime, timedelta

_PRICE_HIST_DIR = _DATA_DIR / "price_history"
_PRICE_HIST_DIR.mkdir(parents=True, exist_ok=True)
_PRICE_CACHE_TTL_HOURS = 24

@app.get("/api/stock/{symbol}/price-history")
async def get_price_history(symbol: str):
    cache_file = _PRICE_HIST_DIR / f"{symbol}.json"
    now = datetime.now()
    if cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            fetched_at = datetime.fromisoformat(cached["fetched_at"])
            if now - fetched_at < timedelta(hours=_PRICE_CACHE_TTL_HOURS):
                return cached
        except (KeyError, ValueError, json.JSONDecodeError):
            pass
    loop = asyncio.get_event_loop()
    try:
        hist = await loop.run_in_executor(None,
            lambda: yf.Ticker(symbol).history(period="10y", interval="1mo"))
    except Exception as e:
        raise HTTPException(503, f"yfinance fetch failed: {e}")
    if hist.empty:
        raise HTTPException(404, f"no price history for {symbol}")
    data = [{"date": idx.strftime("%Y-%m-%d"), "close": float(row["Close"])} 
            for idx, row in hist.iterrows()]
    payload = {"symbol": symbol, "fetched_at": now.isoformat(timespec="seconds"), "data": data}
    cache_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload
```

```
# projects/MaxMahon/.gitignore — append
data/price_history/
```
