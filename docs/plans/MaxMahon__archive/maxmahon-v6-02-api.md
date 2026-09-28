---
project: maxmahon
created: 2026-04-22
last_updated: 2026-04-23
status: done
---

# MaxMahon v6 · Backend API & Schema

> Part 2 of 9 — modify existing endpoints + add new endpoints + align data schemas | Index: maxmahon-v6-index
> Depends on: maxmahon-v6-01-cleanup
> Parallel-safe with: none

## Phase 1: Data contract schema updates
- [x] Align `projects/MaxMahon/config.json` with new DEFAULT_CONFIG (post-Plan 01): verify keys match `min_dividend_yield`, `min_dividend_streak`, `min_eps_positive_years`, `max_pe`, `bonus_pe`, `max_pbv`, `bonus_pbv`, `min_market_cap`; add new fields `universe: "set_mai"` + `last_saved_at: null`. Scope: JSON only, do not touch server code here. Acceptance: `python -c 'import json; print(json.load(open("config.json")))'` prints dict with 9 keys in filters + universe + last_saved_at top-level.
- [x] Update `projects/MaxMahon/user_data.json` schema: add top-level fields `cash_reserve: 0` (float, default 0 for existing) + `simulated_portfolio: { "positions": [], "cash_reserve_pct": 0.0 }`. Scope: additive only, do not touch existing watchlist/blacklist/notes/transactions. Acceptance: JSON parses; new fields present; existing fields untouched.
- [x] Update `projects/MaxMahon/data/case_study_patterns.json`: add `narrative: str` field to each of 7 remaining patterns (post-Plan 01 ENERGY removal). Narratives are 2-paragraph Thai editorials matching mockup section 5 style. Write narrative per pattern: RETAIL_DEFENSIVE_MOAT, BANK_VALUE_PBV1, HOLDING_CO_HIDDEN, VIETNAM_GROWTH_EXPOSURE (disabled — narrative OK to write anyway), UTILITY_DEFENSIVE, HOSPITAL_AGING, F&B_CONSUMER_BRAND. Scope: preserve existing fields (tag, source, rules, disabled where applicable); add narrative key per pattern. Acceptance: JSON parses; each of 7 pattern entries has a `narrative` string >=200 chars.
- [x] Update `save_exit_baseline()` in `projects/MaxMahon/scripts/screen_stocks.py` (find function by grep): snapshot `entry_score: int` from the screener entry at baseline creation time. Write to `data/exit_baselines.json` alongside existing keys (pe_baseline, pbv_baseline, dy_baseline, date_added). Scope: additive field only; do not touch other baseline logic. Acceptance: new exit baseline entries include `entry_score` int field; existing baselines can be left without (backward compat — load with .get default).

### Reference
```json
// config.json CURRENT (Niwes-era already)
{
  "schedule": { "enabled": true, "day_of_week": "sat", "hour": 9, "minute": 0 },
  "filters": { ... 8 keys ... }
}
// NEW
{
  "schedule": { "enabled": true, "day_of_week": "sat", "hour": 9, "minute": 0 },
  "filters": {
    "min_dividend_yield": 5.0,
    "min_dividend_streak": 5,
    "min_eps_positive_years": 5,
    "max_pe": 15.0,
    "bonus_pe": 8.0,
    "max_pbv": 1.5,
    "bonus_pbv": 1.0,
    "min_market_cap": 5000000000
  },
  "universe": "set_mai",
  "last_saved_at": null
}

// user_data.json additive
{
  "watchlist": [...],
  "blacklist": [...],
  "notes": {...},
  "custom_lists": {},
  "transactions": [...],
  "cash_reserve": 0,
  "simulated_portfolio": { "positions": [], "cash_reserve_pct": 0.0 },
  "updated_at": "..."
}

// case_study_patterns.json (per pattern) add
{
  "tag": "BANK_VALUE_PBV1",
  "source": "docs/niwes/08-case-tcap.md",
  "rules": { ... },
  "narrative": "หุ้นธนาคารไทยถือเป็น value classic — ซื้อที่ราคาต่ำกว่ามูลค่าทางบัญชี (P/BV < 1.0) แล้วรอ cycle เก็บดอกเบี้ย... (2 paragraphs Thai editorial ~250-400 chars)"
}
```

## Phase 2: Modify 9 existing endpoints (additive, non-breaking)
- [x] Modify `GET /api/screener` handler in `projects/MaxMahon/server/app.py` line 188: for each candidate, add fields `score_delta: int | null` (current - previous_scan_score), `previous_score: int | null`, `score_streak_weeks: int | null`, `is_new_this_week: bool` (alias of existing `is_new_in_batch`). Also add top-level `summary: { total_scanned, passed_count, review_count, avg_yield, top_score, new_entrants, sectors }` precomputed from the screener data. Scope: additive only, keep existing fields. Acceptance: `curl /api/screener` returns each candidate with 4 new fields + top-level summary object with 7 keys.
- [x] Modify `GET /api/stock/{symbol}` handler in `projects/MaxMahon/server/app.py` line 215: add fields `narrative: { case_text: str | null, lede: str | null }` (null when no Deep Analyze has run), `five_year_history: list[{year, revenue, net_income, eps, roe, net_margin, de, ocf, dps}]` (derive from yearly_metrics + dividend_history join), `dividend_history_10y: list[{year, dps, yield_pct}]` (explicit 10y aggregate), `reasons_narrative: list[str]` (keep existing reasons as-is; frontend handles markdown bolding). Scope: additive. Acceptance: response includes all 3 new top-level fields.
- [x] Modify `GET /api/stock/{symbol}/patterns` handler in `projects/MaxMahon/server/app.py` line 2030: for each matched pattern, include `narrative: str` field by lookup in `data/case_study_patterns.json` by pattern tag. Scope: additive. Acceptance: response matched_patterns[].narrative is populated; empty string if pattern tag lookup fails.
- [x] Modify `GET /api/history/v2` handler in `projects/MaxMahon/server/app.py` line 2010: ensure each scan entry exposes `counts.passed`, `counts.review`, `counts.failed`, `counts.avg_yield`, `counts.top_score`, `counts.new_entrants`, `counts.sectors`. Also add `signature_version: str` at top level + stable empty-state shape `{scans: [], count: 0}` when no scans. Scope: additive at each scan entry level; existing consumers unaffected. Acceptance: response `scans[0].counts` has all 7 keys; empty state returns `{scans: [], count: 0, signature_version: "v2"}`.
- [x] Modify `GET /api/watchlist/{symbol}/exit-status` handler in `projects/MaxMahon/server/app.py` line 2081: add `narrative: str` (italicized paragraph matching mockup section 10 style), `trigger_rules: list[{label, threshold, current, status}]` (expand triggers to include threshold values — 5 rules table), `entry_context: { entry_date, entry_pe, entry_yield, delta_score, weeks_held }`. Scope: additive. Acceptance: response has 3 new top-level fields; existing severity/triggers untouched.
- [x] Modify `GET /api/portfolio/pnl` handler in `projects/MaxMahon/server/app.py` line 1384: for each position, add `name: str` (join from screener/snapshot), `dividends_received: float` (cumulative DPS × qty held, computed from transactions[].qty + dates × dividend_history DPS), `dividend_yield_on_cost: float` (annual DPS × qty / cost_basis), `weight_pct: float` (MV / total MV). Also add top-level `total.dividends_received: float` + `total.cash_reserve: float` (from `user_data.cash_reserve`). Scope: additive. Acceptance: positions[] each have 4 new fields; totals has 2 new fields.
- [x] Modify `GET /api/settings` handler in `projects/MaxMahon/server/app.py` line 800: return the aligned Niwes schema (post-Plan 01 Phase 1 fix), include `universe: "set_only" | "set_mai"` + `last_saved_at: isodatestr | null` + computed `next_run_at: isodatestr | null` (from APScheduler state). Scope: additive beyond existing filters. Acceptance: response has `schedule`, `filters` (8 Niwes keys), `universe`, `last_saved_at`, `next_run_at`.
- [x] Modify `POST /api/settings` handler in `projects/MaxMahon/server/app.py` line 805: validate input against new Niwes schema; merge into config.json; set `last_saved_at: datetime.now().isoformat()`; re-apply scheduler. Scope: reject unknown filter keys (pattern: 400 with explicit message); accept new universe field. Acceptance: POST with invalid key returns 400; POST with valid body writes config.json with updated last_saved_at.
- [x] Modify `GET /api/user` handler in `projects/MaxMahon/server/app.py` line 1238: include new top-level fields from user_data.json (`cash_reserve`, `simulated_portfolio`) passthrough; do NOT pre-join watchlist here (enriched endpoint in Phase 3 handles that). Scope: passthrough only. Acceptance: response includes cash_reserve + simulated_portfolio fields.

### Reference
```python
# /api/screener enrichment sketch
@app.get("/api/screener")
def get_screener(user=Depends(verify_token)):
    data = load_latest_screener()
    prev = load_previous_screener()
    prev_scores = {c['symbol']: c['score'] for c in (prev.get('candidates') or [])} if prev else {}
    for c in data['candidates']:
        prev_score = prev_scores.get(c['symbol'])
        c['previous_score'] = prev_score
        c['score_delta'] = (c['score'] - prev_score) if prev_score is not None else None
        c['is_new_this_week'] = c.get('is_new_in_batch', False)
        c['score_streak_weeks'] = c.get('score_streak_weeks')  # written at scan time (Phase 6)
    # top-level summary
    yields = [c['yield'] for c in data['candidates'] if c.get('yield')]
    data['summary'] = {
        'total_scanned': data.get('total_scanned', 0),
        'passed_count': len([c for c in data['candidates'] if c.get('tier') == 'PASS']),
        'review_count': len([c for c in data['candidates'] if c.get('tier') == 'REVIEW']),
        'avg_yield': round(sum(yields)/len(yields), 2) if yields else 0,
        'top_score': max((c['score'] for c in data['candidates']), default=0),
        'new_entrants': len([c for c in data['candidates'] if c.get('is_new_in_batch')]),
        'sectors': len({c.get('sector') for c in data['candidates'] if c.get('sector')}),
    }
    return data
```

## Phase 3: Add 6 new endpoints
- [x] Add `POST /api/simulate/dca-portfolio` handler in `projects/MaxMahon/server/app.py` (near existing /api/dca). Body: `{positions:[{symbol, weight_pct}], monthly_amount:float, duration_years:int, reinvest_dividends:bool}`. Implementation: loop per-position using existing `/api/dca/{symbol}` internal logic, sum by month_index. Response: `{total_invested, ending_value, total_return_pct, cagr_pct, total_dividends, avg_yoc_pct, duration_months, per_position:[...], timeline:[...]}`. Scope: new endpoint; do not modify /api/dca/{symbol}. Acceptance: POST with 3 positions returns non-zero ending_value + per_position[] length 3 + timeline[] with duration_months entries.
- [x] Add `POST /api/simulate/portfolio-backtest` handler in `projects/MaxMahon/server/app.py` (CRITICAL — Karl-emphasized). Body: `{positions:[{symbol, weight_pct}], start_date:"YYYY-MM-DD", monthly_amount:float, reinvest_dividends:bool, benchmark:"SET"}`. Implementation: yfinance monthly history per symbol + TDEX ETF benchmark (fallback `^SET`); Cash symbol = idle no return (MVP per Karl); reinvest dividends on declaration date at that month's price; compute max_drawdown over rolling peak; benchmark applies same ฿/month schedule to TDEX. Response schema matches `_api_plan_inputs.md` Section 2.2 (total_invested, portfolio_value_today, total_return_pct, cagr_pct, dividends_received_total, max_drawdown_pct, max_drawdown_date, benchmark:{symbol, ending_value, return_pct, delta_vs_portfolio}, timeline:[{date, invested_cumulative, portfolio_value, dividends_cumulative, benchmark_value}], yearly_breakdown:[{year, invested_ytd, port_value_ytd, dividends_ytd, benchmark_ytd}], assumptions:{benchmark_proxy:"TDEX ETF (fallback ^SET)", transaction_costs_modeled:false, tax_modeled:false, cash_return_rate_pct:0}). Scope: new endpoint. Acceptance: POST with `{positions:[{BBL.BK,20},{TCAP.BK,15},{Cash,4}], start_date:"2015-01-01", monthly_amount:10000, reinvest_dividends:true, benchmark:"SET"}` returns 7 result fields + timeline + yearly_breakdown + assumptions with benchmark_proxy documented.
- [x] Add `GET /api/watchlist/enriched` handler in `projects/MaxMahon/server/app.py` (new near /api/watchlist). Response: `{summary:{tracked, hold, review, consider_exit, avg_delta_entry, oldest_position_days}, positions:[{symbol, name, current_score, entry_score, delta_entry, entry_date, days_held, exit_signal, note}]}`. Implementation: join `user_data.watchlist[]` × latest screener (score) × `exit_baselines.json` (entry_score, date_added) × `user_data.notes[sym]`. Scope: new endpoint; single call replaces N+1 pattern. Acceptance: response has summary with 6 keys + positions[] length == watchlist length.
- [x] Add `GET /api/watchlist/compare?symbols=A,B,C` handler in `projects/MaxMahon/server/app.py` (new). Support up to 3 symbols (Karl decision). Response: `{symbols:[...], rows:[{label, values:[v1,v2,v3], best_index:int|null, delta:str}]}` with rows = Score, Yield, P/E, P/BV, Streak, Payout, ROE, Exit Signal, Mcap (B THB), Signals. Scope: new endpoint. Acceptance: GET `/api/watchlist/compare?symbols=BBL.BK,TCAP.BK` returns rows[] length 10; best_index matches value per row semantics.
- [x] Add `GET /api/portfolio/simulated` + `PUT /api/portfolio/simulated` handlers in `projects/MaxMahon/server/app.py`. GET response: `{positions:[{symbol, name, label, weight_pct, current_price, target_yield_pct, score, signals}], cash_reserve_pct, total_weight_pct, projected_yoc_pct, concentration_profile:"30/30/30/10"}`. PUT body: `{positions:[{symbol, label, weight_pct}], cash_reserve_pct}`. Implementation: stored in `user_data.simulated_portfolio`; derive current_price/score/signals from screener lookup. Scope: 2 new handlers. Acceptance: PUT then GET round-trips; label field free-text preserved (Karl decision).
- [x] Add `GET /api/screener/trend?weeks=12` handler in `projects/MaxMahon/server/app.py`. Response: `{weeks:[{week_label, scan_date, passed, review, avg_yield, top_score}]}` — derive from `history.json scans[]` last N entries. Scope: new endpoint. Acceptance: GET with default weeks=12 returns weeks[] with up to 12 entries; each entry has 6 keys.

### Reference
```python
# /api/simulate/portfolio-backtest sketch
from pydantic import BaseModel
class BacktestRequest(BaseModel):
    positions: list[dict]
    start_date: str
    monthly_amount: float
    reinvest_dividends: bool = True
    benchmark: str = "SET"

@app.post("/api/simulate/portfolio-backtest")
def portfolio_backtest(req: BacktestRequest, user=Depends(verify_token)):
    # Load monthly price + dividend history per symbol via yfinance
    # Load TDEX ETF history; fallback to ^SET if empty
    benchmark_symbol = "TDEX.BK"
    bench = _yf_monthly_series(benchmark_symbol) or _yf_monthly_series("^SET")
    proxy_label = "TDEX ETF (Thai dividend, includes reinvest)" if bench is benchmark_symbol else "^SET index (price-only)"
    # DCA schedule per month: allocate monthly_amount by weight_pct → buy shares at month-open price
    # Reinvest dividends on ex-div month at that month-open price
    # Compute rolling max → drawdown
    # Assumptions block:
    return {
        ...,
        "assumptions": {
            "benchmark_proxy": proxy_label,
            "transaction_costs_modeled": False,
            "tax_modeled": False,
            "cash_return_rate_pct": 0,
        },
    }
```

## Phase 4: Admin namespace migration (/api/admin/*)
- [x] Create new file `projects/MaxMahon/server/admin.py` with FastAPI APIRouter(prefix='/api/admin'). Move handlers from `server/app.py`: `GET /api/reports` (line ~694) → `GET /api/admin/reports`, `GET /api/reports/scan` (line ~705) → `GET /api/admin/reports/scan`, `POST /api/request` (line ~514) → `POST /api/admin/request`, `GET /api/requests` (line ~585) → `GET /api/admin/requests`, `GET /api/request/status` (line ~579) → `GET /api/admin/request/status`, `POST /api/scan/trigger` (line ~660) → `POST /api/admin/scan/trigger`, `GET /api/events` SSE (line ~671) → `GET /api/admin/events`, `GET /api/history` v1 (line ~310) → `GET /api/admin/history`. Scope: move, don't delete; update imports accordingly. Acceptance: admin.py exists; all 8 moved endpoints respond under `/api/admin/*`; `grep "@app.get(\"/api/reports\"" server/app.py` returns 0 matches (moved to router).
- [x] Mount admin router in `projects/MaxMahon/server/app.py`: add `from server.admin import router as admin_router` near existing imports, then `app.include_router(admin_router)` after app creation. Scope: one import + one include_router call. Acceptance: server starts without error; `/api/admin/reports` responds; `/api/reports` returns 404 (moved).
- [x] Leave `PUT /api/user/blacklist` at `server/app.py` line 1284 in main app (not moved) — Karl decision 'keep for now'. Verify no changes needed. Acceptance: endpoint still mounted at original path.
- [x] Document in `projects/MaxMahon/server/admin.py` module docstring: 'Legacy/admin endpoints. v6 frontend does not call these. Kept for external API consumers + CLI debugging. Consider removal in v7 if still unused.' Acceptance: docstring present at top of admin.py.

### Reference
```python
# server/admin.py NEW
"""Admin / legacy endpoints. v6 frontend does not call these.
Kept for external API consumers + CLI debugging. Review for removal in v7."""
from fastapi import APIRouter, Depends, Body, Query
from server.auth import verify_token  # adapt to actual import path

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/reports")
def list_reports(...):
    ...

@router.post("/scan/trigger")
def trigger_scan(...):
    ...
# ... etc for 8 endpoints


# server/app.py additions
from server.admin import router as admin_router
# ... after app = FastAPI(...)
app.include_router(admin_router)
```

## Phase 5: Static routing for v6 (serve web/v6/)
- [x] Update `GET /` handler in `projects/MaxMahon/server/app.py` line 2216: serve `web/v6/desktop/index.html` with cache-bust substitution (replace current `web/index.html` reference). Scope: one file path change; keep cache-bust logic. Acceptance: `curl http://localhost:50089/` returns HTML with `<html` tag + cache-bust token; Content-Type text/html.
- [x] Update `GET /mobile` handler in `projects/MaxMahon/server/app.py` line 2210: serve `web/v6/mobile/index.html`; also add new route `GET /m` that serves same file. Scope: 2 route handlers point to same mobile entry. Acceptance: both `/mobile` and `/m` return the mobile HTML.
- [x] Update StaticFiles mount in `projects/MaxMahon/server/app.py` (`app.mount("/", StaticFiles(...))` near end of file): change mount root to `web/v6/` OR add separate mount for `web/v6/static/` at `/static/v6/`. Scope: ensure `/static/v6/js/*`, `/static/v6/css/*` resolve from `web/v6/static/`. Acceptance: `curl /static/v6/css/base.css` returns CSS content once Plan 03 writes that file.
- [x] Note: `web/` directory itself will be empty after Plan 01 archive. Once v6 frontend ships (Plan 03-08), `web/v6/*` will exist. For Plan 02, leave empty `web/v6/` placeholder; static route will 404 until Plan 03 creates files. Scope: create placeholder `web/v6/desktop/index.html` + `web/v6/mobile/index.html` stub (<html><body>v6 foundation pending</body></html>) so routes don't 500. Acceptance: stubs exist; `/` returns stub; `/m` returns stub.

### Reference
```python
# server/app.py line ~2216 CURRENT
@app.get("/")
def index():
    html = (WEB_DIR / "index.html").read_text(encoding="utf-8")
    html = html.replace("{{CACHEBUST}}", str(int(time.time())))
    return HTMLResponse(html)
# NEW
@app.get("/")
def index():
    html = (WEB_DIR / "v6" / "desktop" / "index.html").read_text(encoding="utf-8")
    html = html.replace("{{CACHEBUST}}", str(int(time.time())))
    return HTMLResponse(html)

# server/app.py line ~2210 CURRENT
@app.get("/mobile")
def mobile():
    return FileResponse(WEB_DIR / "mobile.html")
# NEW
@app.get("/mobile")
@app.get("/m")
def mobile():
    return FileResponse(WEB_DIR / "v6" / "mobile" / "index.html")

# Static mount update
app.mount("/static/v6", StaticFiles(directory=str(WEB_DIR / "v6" / "static")), name="v6-static")
```

## Phase 6: Score streak computation in scan pipeline
- [x] Add `score_streak_weeks` computation in `projects/MaxMahon/scripts/screen_stocks.py` (inside the main screen loop where each stock's screener entry is built): for each symbol, read last N screener_*.json files, compute consecutive scans where score increased month-over-month, write `score_streak_weeks: int` into the candidate dict. Scope: additive field per candidate; do not change score computation. Acceptance: screener output JSON entries include `score_streak_weeks` (int >= 0); scan.py and /api/screener pick it up automatically.
- [x] Persist `score_streak_weeks` in `projects/MaxMahon/scripts/scan.py` writeback: ensure when scan writes final screener_{date}.json, the `score_streak_weeks` field is preserved (should be automatic if it is in the dict upstream; verify). Scope: verification + no-op if pass-through works. Acceptance: after one scan run, `jq '.candidates[0].score_streak_weeks' data/screener_{date}.json` returns an int.

### Reference
```python
# screen_stocks.py (sketch inside main loop)
def compute_score_streak(symbol: str, current_score: int, history_glob: list[Path]) -> int:
    """Count consecutive prior scans where score went up for this symbol."""
    # Sort by mtime (not lex — avoids curated/backup suffix bugs, per MEMORY lesson)
    recent = sorted(history_glob, key=lambda p: p.stat().st_mtime, reverse=True)[:20]
    streak = 0
    last = current_score
    for f in recent:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            match = next((c for c in data.get('candidates', []) if c['symbol'] == symbol), None)
            if match and match['score'] <= last:
                streak += 1
                last = match['score']
            else:
                break
        except Exception:
            break
    return streak

# Within the per-stock screener build:
for cand in candidates:
    cand['score_streak_weeks'] = compute_score_streak(cand['symbol'], cand['score'], prior_screener_files)
```
