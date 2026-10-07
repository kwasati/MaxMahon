---
project: maxmahon
created: 2026-04-22
last_updated: 2026-04-23
status: done
---

# MaxMahon v6 · Backend Cleanup & Archive

> Part 1 of 9 — backend cleanup, archive legacy assets, unify pipeline, run fresh scan | Index: maxmahon-v6-index
> Depends on: none
> Parallel-safe with: none (must complete before 02)

## Phase 1: Safe deletes (dead code)
- [x] Delete `fmt()` helper in `projects/MaxMahon/scripts/scan.py` lines 43-52. Scope: do not touch any other function. Acceptance: `grep "\bfmt\(" projects/MaxMahon/scripts/scan.py` returns 0 matches.
- [x] Delete `build_stock_section()` in `projects/MaxMahon/scripts/scan.py` lines 55-136 (full function body). Scope: do not touch callers (there are none). Acceptance: `grep "build_stock_section" projects/MaxMahon` returns only matches in `docs/archive/`.
- [x] Delete `build_filtered_section()` in `projects/MaxMahon/scripts/scan.py` lines 139-156. Acceptance: `grep "build_filtered_section" projects/MaxMahon` returns 0 matches outside archive.
- [x] Delete `load_historical_candidates()` in `projects/MaxMahon/scripts/scan.py` lines 159-172. Acceptance: `grep "load_historical_candidates" projects/MaxMahon` returns 0 matches outside archive.
- [x] Delete `classify_stocks()` function in `projects/MaxMahon/scripts/scan.py` lines 175-237 AND its call site + print log at lines 290-297. Scope: also drop unused imports `detect_exit_signal`, `load_exit_baseline` from lines 19-24. Acceptance: `grep "classify_stocks" projects/MaxMahon` returns 0 matches.
- [x] Delete `build_exit_alerts_section()` in `projects/MaxMahon/scripts/scan.py` lines 240-253. Acceptance: `grep "build_exit_alerts_section"` returns 0 matches.
- [x] Delete unused variable `notes = user_data.get("notes", {})` at `projects/MaxMahon/scripts/scan.py` line 288. Acceptance: `grep "\bnotes\b" projects/MaxMahon/scripts/scan.py` returns 0 matches.
- [x] Delete unused variable `scan_date = screener_data.get("date", today)` at `projects/MaxMahon/scripts/scan.py` line 302. Acceptance: `grep "\bscan_date\b" projects/MaxMahon/scripts/scan.py` returns 0 matches.
- [x] Delete unused `import os` at `projects/MaxMahon/scripts/scan.py` line 4. Acceptance: `ruff check projects/MaxMahon/scripts/scan.py` shows no unused-import warning.
- [x] Delete `_fetch_yfinance_full()` function in `projects/MaxMahon/scripts/data_adapter.py` lines 398-413. Scope: do not touch `_fetch_yfinance_legacy` in fetch_data.py. Acceptance: `grep "_fetch_yfinance_full" projects/MaxMahon` returns 0 matches.
- [x] Delete root-level `projects/MaxMahon/data/analysis_cache.json` (39KB stale file). Scope: keep `data/analysis_cache/` folder (server creates at startup). Acceptance: `grep -n "analysis_cache\.json\b" projects/MaxMahon/server projects/MaxMahon/scripts` returns 0 matches.
- [x] Replace `DEFAULT_CONFIG` block in `projects/MaxMahon/server/app.py` lines 756-768 with Niwes-era schema matching `screen_stocks.py DEFAULT_FILTERS` lines 29-38 (keys: min_dividend_yield, min_dividend_streak, min_eps_positive_years, max_pe, bonus_pe, max_pbv, bonus_pbv, min_market_cap). Scope: do not rename constants; only change dict contents. Acceptance: GET /api/settings returns only 8 Niwes filter keys (no roe, margin, de, fcf keys).
- [x] Delete `import math` at `projects/MaxMahon/scripts/fetch_data.py` line 10. Acceptance: `grep "\bmath\." projects/MaxMahon/scripts/fetch_data.py` returns 0 matches.
- [x] Delete `import time` at `projects/MaxMahon/scripts/screen_stocks.py` line 6 + trim unused adapters from line 19 import (`normalize_yield`, `FINANCIAL_SECTORS`). Keep `fetch_multi_year`, `fetch_multi_year_safe`. Acceptance: `grep "\btime\." projects/MaxMahon/scripts/screen_stocks.py` returns 0 matches; module imports only used adapters.
- [x] Delete `else:` fallback branch in `projects/MaxMahon/scripts/fetch_data.py` lines 466-470 (watchlist.json legacy load); also delete `WATCHLIST = ROOT / "watchlist.json"` at line 30. Scope: keep unconditional `if USER_DATA.exists():` branch. Acceptance: module loads user_data.json unconditionally; no watchlist.json references remain.
- [x] Delete `else:` fallback branch in `projects/MaxMahon/scripts/screen_stocks.py` lines 629-632 (watchlist.json legacy load); also delete `WATCHLIST = ROOT / "watchlist.json"` at line 15. Acceptance: module loads user_data.json unconditionally; no watchlist.json references remain.
- [x] Remove `ENERGY_CYCLICAL_EXIT` pattern block (lines 65-78) from `projects/MaxMahon/data/case_study_patterns.json`. Scope: keep all other 7 patterns untouched; JSON must remain valid. Acceptance: `grep "ENERGY_CYCLICAL_EXIT" projects/MaxMahon/data/case_study_patterns.json` returns 0 matches; JSON parses cleanly with 7 remaining patterns.
- [x] Change condition at `projects/MaxMahon/scripts/case_study_detector.py` line 41 from `if p.get("anti_rules") or p.get("disabled"):` to `if p.get("disabled"):` (Option B — cleaner signal since anti-rule concept removed). Scope: only that line. Acceptance: VIETNAM_GROWTH_EXPOSURE still skipped via disabled flag; no other patterns affected.

### Reference
```python
# scan.py lines 43-52 CURRENT
def fmt(val, pct=False, billions=False):
    if val is None:
        return "N/A"
    if pct:
        return f"{val * 100:.1f}%"
    if billions:
        return f"{val / 1e9:.1f}B"
    if isinstance(val, float):
        return f"{val:,.2f}"
    return f"{val:,}"
# NEW: (deleted — 0 lines)

# scan.py lines 290-297 CURRENT call-site
    top_candidates, watchlist_current, new_in_batch, watchlist_exit_alerts = classify_stocks(
        screener_data, watchlist, screener_path
    )
    print(
        f"Classified: top={len(top_candidates)} watchlist={len(watchlist_current)} "
        f"new={len(new_in_batch)} exit_alerts={len(watchlist_exit_alerts)}"
    )
# NEW: (deleted — both the call and the print log)

# data_adapter.py lines 398-413 CURRENT
def _fetch_yfinance_full(symbol: str) -> dict | None:
    """Full yfinance fallback — same logic as old fetch_multi_year."""
    try:
        import yfinance as yf
        yf_sym = _to_yf_symbol(symbol)
        tk = yf.Ticker(yf_sym)
        info = tk.info or {}
        if len(info) < 5:
            return None
        return {"tk": tk, "info": info}
    except Exception as e:
        logger.warning("yfinance full fallback failed for %s: %s", symbol, e)
        return None
# NEW: (deleted)

# server/app.py lines 756-768 CURRENT
DEFAULT_CONFIG = {
    "schedule": {"enabled": True, "day_of_week": "sun", "hour": 9, "minute": 0},
    "filters": {
        "min_roe_avg": 0.15,
        "min_roe_floor": 0.12,
        "min_net_margin": 0.10,
        "max_de_non_fin": 1.5,
        "max_de_financial": 10,
        "min_eps_positive_years": 3,
        "min_fcf_positive_years": 3,
        "min_market_cap": 5_000_000_000,
    },
}
# NEW
DEFAULT_CONFIG = {
    "schedule": {"enabled": True, "day_of_week": "sat", "hour": 9, "minute": 0},
    "filters": {
        "min_dividend_yield": 5.0,
        "min_dividend_streak": 5,
        "min_eps_positive_years": 5,
        "max_pe": 15.0,
        "bonus_pe": 8.0,
        "max_pbv": 1.5,
        "bonus_pbv": 1.0,
        "min_market_cap": 5_000_000_000,
    },
    "universe": "set_mai",
}

# case_study_detector.py line 41 CURRENT
for p in patterns.values():
    if p.get("anti_rules") or p.get("disabled"):
        continue
# NEW
for p in patterns.values():
    if p.get("disabled"):
        continue

# fetch_data.py lines 466-470 CURRENT
if USER_DATA.exists():
    user_data = json.loads(USER_DATA.read_text(encoding="utf-8"))
    symbols = user_data.get("watchlist", [])
else:
    # Fallback to old watchlist.json
    watchlist = json.loads(WATCHLIST.read_text(encoding="utf-8"))
    symbols = [s["symbol"] for s in watchlist["stocks"]]
# NEW
user_data = json.loads(USER_DATA.read_text(encoding="utf-8"))
symbols = user_data.get("watchlist", [])
```

## Phase 2: Archive legacy (move to _archive/v5/)
- [x] Create folder structure `projects/MaxMahon/_archive/v5/` with subfolders: `web/`, `scripts/`, `scripts/monitor/`, `scripts/migrations/`, `scripts/tmp/`, `reports/`, `data/`, `data/snapshots/`, `data/screeners/`, `data/requests/`, `data/monitor/`. Acceptance: all folders exist and are empty.
- [x] Move monitor cluster scripts to `_archive/v5/scripts/monitor/`: `monitor_niwes_news.py`, `diff_niwes_portfolio.py`, `alert_niwes.py`, `_niwes_cache.py`, `monitor_thai_macro.py`, `show_niwes_diff_history.py`, `backtest_niwes.py`, `run_monitor_pipeline.bat`. Acceptance: none of these files exist in `scripts/` anymore; all present in `_archive/v5/scripts/monitor/`.
- [x] Move `scripts/structural_risk_score.py` to `_archive/v5/scripts/monitor/structural_risk_score.py` (Karl decision: archive since /api/exit_check is being removed in Phase 3 + monitor cluster is gone). Acceptance: file moved; no import of structural_risk_score remains in live code.
- [x] Move old frontend web/ files to `_archive/v5/web/`: `web/index.html`, `web/app.js`, `web/style.css`, `web/mobile.html`, `web/mockup.html`, `web/mockup-flow.html`. Scope: keep `web-v6-mockup/` at project root untouched. Acceptance: `web/` folder still exists but empty (server routing updated in Plan 02); v6 frontend will populate `web/v6/`.
- [x] Move all reports/*.md to `_archive/v5/reports/` (15 files): `_placeholder_integration_loop_after_adjust.md`, `baseline_niwes_v1_2026-04-20.md`, `discovery_2026-04-12.md`, `discovery_2026-04-14.md`, `discovery_2026-04-19.md`, `integration_loop_karl_todo_2026-04-20.md`, `integration_loop_scan_2026-04-20.md`, `integration_loop_watchlist_diff_2026-04-20.md`, `scan_2026-04-19.md`, `scan_2026-04-20.md`, `scan_2026-04-21.md`, `weekly_2026-04-11.md`, `weekly_2026-04-12.md`, `weekly_2026-04-19.md`. Acceptance: `reports/` folder empty; fresh scan will write new scan_{today}.md here.
- [x] Move data snapshots to `_archive/v5/data/snapshots/`: `data/snapshot_2026-04-11.json` through `snapshot_2026-04-21.json` (6 files). Acceptance: no `snapshot_*.json` remain in `data/`; archive folder has 6 files.
- [x] Move data screeners to `_archive/v5/data/screeners/`: `screener_2026-04-12.json`, `screener_2026-04-13.json`, `screener_2026-04-14.json`, `screener_2026-04-21.json`, `screener_curated_niwes06_2026-04-20.json` (5 files). Acceptance: no `screener_*.json` remain in `data/`.
- [x] Move `data/request_2026-04-12_LH.json` + `data/request_2026-04-15_BDMS.json` to `_archive/v5/data/requests/`. Acceptance: no `request_*.json` remain in `data/`.
- [x] Move monitor output files to `_archive/v5/data/monitor/`: `niwes_diff_history.json`, `niwes_diff_latest.json`, `niwes_alert_sent.json`, `niwes_news_2026-04-20.json`, `niwes_news_seen.json`, `monitor_log_2026-04-20.log`, `thai_macro_2026-04-20.json`. Acceptance: no monitor files remain in `data/`.
- [x] Move `data/history.json` + `data/history.json.v1.bak` to `_archive/v5/data/`. Scope: next scan will create fresh `data/history.json`. Acceptance: no history files remain in `data/`.
- [x] Move migration scripts to `_archive/v5/scripts/migrations/`: `scripts/migrate_watchlist.py`, `scripts/migrate_history_v2.py`. Acceptance: neither file in `scripts/`.
- [x] Move `tmp/run_curated_screen.py` to `_archive/v5/scripts/tmp/run_curated_screen.py`. If `tmp/` folder is empty after move, keep as empty folder. Acceptance: file moved.
- [x] Move `scripts/integration_test.py` to `_archive/v5/scripts/integration_test.py` (Karl decision: archive, rewrite as pytest later). Acceptance: file moved.
- [x] Move `scripts/run_scan.py` to `_archive/v5/scripts/run_scan.py` (pipeline unified into server PIPELINE_MAP). Acceptance: file moved; no import references remain.
- [x] Move `user_data.backup.json` (root) to `_archive/v5/data/user_data.backup.json` (Karl decision: archive for audit trail). Acceptance: file moved.
- [x] Move root `watchlist.json` to `_archive/v5/data/watchlist.json` (after Phase 1 fallback branches are deleted). Acceptance: file moved; `grep "watchlist\.json" projects/MaxMahon` returns 0 matches in source code.
- [x] Add `_archive/` to `projects/MaxMahon/.gitignore` (Karl decision: lean repo, archive is local-only audit trail). Scope: append one line, do not reorder existing entries. Acceptance: `.gitignore` contains `_archive/` line; `git status` shows no _archive/ files tracked.
- [x] Create `projects/MaxMahon/_archive/v5/README.md` documenting: archive date 2026-04-22, reason (v5 → v6 frontend rewrite + pipeline simplification), restore recipe (copy back to original path), note on Windows Task Scheduler jobs for monitor cluster (must be manually re-enabled). Acceptance: README present, ~20 lines, covers the 3 bullets.

### Reference
```markdown
# _archive/v5/README.md (expected contents)

# MaxMahon v5 Archive

**Archive date:** 2026-04-22
**Reason:** v5 → v6 transition — frontend rewrite to vintage newspaper mockup + pipeline unification (removed standalone run_scan.py + monitor cluster + dead helpers).

## Folder map
- `web/` — old v5 frontend (index/app.js/style.css/mobile + mockups)
- `scripts/` — run_scan.py, integration_test.py, structural_risk_score.py
- `scripts/monitor/` — Niwes news scraper + portfolio diff + macro fetch cluster (7 files + bat)
- `scripts/migrations/` — one-shot migrate_watchlist + migrate_history_v2 (already executed)
- `scripts/tmp/` — dev one-offs (run_curated_screen.py)
- `reports/` — historical scan/discovery/weekly/integration_loop MDs
- `data/` — history.json + v1 backup + user_data.backup.json + watchlist.json
- `data/snapshots/` — snapshot_YYYY-MM-DD.json (6 files)
- `data/screeners/` — screener_YYYY-MM-DD.json (5 files)
- `data/requests/` — request_YYYY-MM-DD_{SYM}.json
- `data/monitor/` — niwes_diff/news/alert + thai_macro outputs

## Restore recipe
To restore an archived script: copy back to its original path (see list above).

## Note on monitor cluster
Windows Task Scheduler jobs (see `docs/niwes/14-monitoring-setup.md`) must be manually re-enabled if the monitor cluster is restored.
```

## Phase 3: Remove 3 deprecated endpoints
- [x] Remove endpoint `PUT /api/user/lists/{list_name}` handler at `projects/MaxMahon/server/app.py` line 1318 (v6 has no custom-lists UI; `custom_lists` in user_data.json stays as `{}` default). Scope: delete the full `@app.put(...)` decorator block + function body; do not touch `load_user_data` default. Acceptance: `grep "@app.put(\"/api/user/lists" projects/MaxMahon/server/app.py` returns 0 matches.
- [x] Remove endpoint `DELETE /api/user/lists/{list_name}` handler at `projects/MaxMahon/server/app.py` line 1332. Acceptance: `grep "@app.delete(\"/api/user/lists" projects/MaxMahon/server/app.py` returns 0 matches.
- [x] Remove endpoint `GET /api/exit_check/{symbol}` handler at `projects/MaxMahon/server/app.py` line 1902 AND the `from structural_risk_score import ...` at line 1925 (drops with it). Scope: do not touch `/api/watchlist/{sym}/exit-status` — that is the single source of truth going forward. Acceptance: `grep "@app.get(\"/api/exit_check" projects/MaxMahon/server/app.py` returns 0 matches; no import of `structural_risk_score` remains.

### Reference
```python
# server/app.py line ~1318 CURRENT
@app.put("/api/user/lists/{list_name}")
def update_user_list(list_name: str, body: dict = Body(...), user=Depends(verify_token)):
    # ... body ...
# NEW: (deleted entire handler)

# server/app.py line ~1902 CURRENT
@app.get("/api/exit_check/{symbol}")
def exit_check(symbol: str, user=Depends(verify_token)):
    from structural_risk_score import compute_structural_risk  # line 1925
    # ... body ...
# NEW: (deleted entire handler + the import line)
```

## Phase 4: Unify pipeline documentation
- [x] Update `projects/MaxMahon/README.md` line 28: replace `py scripts/run_scan.py                # full scan (fetch + screen + analyze)` with `# Trigger scan via API: curl -X POST http://localhost:50089/api/scan/trigger -H "Authorization: Bearer $MAX_TOKEN"`. Scope: only this line. Acceptance: README no longer references run_scan.py as executable; new line documents API trigger path.
- [x] Delete `projects/MaxMahon/README.md` line 44 `  run_scan.py        # pipeline runner` from directory-tree section. Scope: only that bullet. Acceptance: README directory tree no longer lists run_scan.py.
- [x] Delete bullet `- `scripts/run_scan.py` — pipeline runner (fetch + universe + screen + scan)` at `projects/MaxMahon/CLAUDE.md` line 71. Scope: only that one line. Acceptance: CLAUDE.md Key Files section no longer mentions run_scan.py.
- [x] Leave `projects/MaxMahon/CHANGELOG.md` line 82 as-is (historical record, immutable). Acceptance: CHANGELOG unchanged; verify with `git diff` no touch.

### Reference
```
# README.md line 28 CURRENT
py scripts/run_scan.py                # full scan (fetch + screen + analyze)

# README.md line 28 NEW
# Trigger scan via API: curl -X POST http://localhost:50089/api/scan/trigger -H "Authorization: Bearer $MAX_TOKEN"

# CLAUDE.md line 71 CURRENT
- `scripts/run_scan.py` — pipeline runner (fetch + universe + screen + scan)
# NEW: (deleted)
```

## Phase 5: Fresh scan sanity check
- [x] Start server (foreground — Karl's rule): from `projects/MaxMahon/`, run `py -m uvicorn server.app:app --host 0.0.0.0 --port 50089 --log-level warning --no-access-log` OR `max-server.bat`. Scope: leave running in one terminal; do NOT background. Acceptance: server listening on port 50089; `/api/status` returns 200.
- [x] Trigger scan via API: `curl -X POST http://localhost:50089/api/scan/trigger -H "Authorization: Bearer $MAX_TOKEN"`. Acceptance: 200 response with `started: true` and pipeline status. Wait for completion (watch `/api/events` SSE or poll `/api/status`).
- [x] Verify scan outputs created: check `data/snapshot_{today}.json` exists (>10KB), `data/screener_{today}.json` exists (>100KB), `data/history.json` exists with `scans[0].num == 1`, `reports/scan_{today}.md` exists (>5KB). Acceptance: all 4 files present with non-trivial size.
- [x] Sanity check API endpoints: `curl http://localhost:50089/api/screener -H "Authorization: Bearer $MAX_TOKEN"` returns non-empty `candidates[]`; `curl http://localhost:50089/api/history/v2 ...` returns `{"scans": [{"num": 1, ...}], "count": 1}`; `curl http://localhost:50089/api/reports/scan?num=1 ...` returns the new MD file. Acceptance: all 3 curls return expected shapes.
- [x] Commit Phase 1-4 changes: `git -C projects/MaxMahon add -A && git -C projects/MaxMahon commit -m "v6 cleanup: archive v5 assets + remove dead code + unify pipeline"`. Scope: one commit for all cleanup; do not push yet (Plan 09 pushes final). Acceptance: commit created; `git log -1 --oneline` shows the cleanup commit.
