---
project: 4-MaxMahon
created: 2026-05-18
last_updated: 2026-05-18
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: ลบ scan output เก่าทั้งหมดที่จาก pillar algo + รัน screen_stocks.py ใหม่ได้ fresh screener_YYYY-MM-DD.json + history.json migrate ครบ + เปิด web เห็นข้อมูลใหม่ + verify ทั้ง flow end-to-end

### รายละเอียด
- Delete old scan output: data/screener_*.json (all dates pre-refactor) + reports/scan_*.md (all dates pre-refactor)
- data/exit_baselines.json migration: stores entry_score (pillar 0-100) — option A: clear file (let next scan rebuild) / option B: convert score / 10 to display_score equivalent. Decision: clear + rebuild (cleanest, anchor entry_score will populate fresh on next NIWES_5555 PASS)
- data/history.json migration: stores scan history with score field (pillar 0-100). User-facing — must keep entries. Option: add note 'legacy_algo' flag on old entries OR transform score field to display_score equivalent (score/10). Decision: transform old entries (score/10 -> display_score, breakdown left as legacy data structure)
- Rerun screen_stocks.py — fresh universe scan with new anchor algo (use clean caches)
- Should NOT delete: data/users/*/user_data.json (user data) + data/setsmart_cache/* (API cache) + data/price_cache/* (price data) + data/screener_cache/* (fetch cache — will repopulate on scan)
- TEST GATE 4 verification:
-   - screener_*.json schema = anchor (not pillar)
-   - reports/scan_YYYY-MM-DD.md format = 4-pillar breakdown
-   - /api/screener returns anchor schema
-   - /api/stock/{sym} returns anchor breakdown
-   - web /v6/desktop home page shows display_score 0.0-10.0
-   - web /v6/desktop report page shows 4-pillar breakdown
-   - mobile pages same
-   - User open web manually to verify (UI verification gate)
- Plan 03 = final integration step — depends on Plan 01 + Plan 02 done
- After this plan done: maxmahon-index Phase 3 last todo can be ticked + Anchor Scoring v1.0 = PRODUCTION READY

### Scope Boundary
**In scope:**
- Delete: projects/4-MaxMahon/data/screener_*.json (all)
- Delete: projects/4-MaxMahon/reports/scan_*.md (all)
- Modify (clear): projects/4-MaxMahon/data/exit_baselines.json
- Migrate: projects/4-MaxMahon/data/history.json (transform old entries)
- Run: py scripts/screen_stocks.py (fresh universe scan)
- Verify: web/v6 pages + API endpoints end-to-end

**Out of scope:**
- Modify any backend logic (Plan 01 done)
- Modify any frontend JS/CSS (Plan 02 done)
- Delete user data: data/users/*/user_data.json
- Delete caches: data/setsmart_cache, data/price_cache, data/screener_cache (preserve to avoid full refetch)
- Schema versioning / migration tooling (one-shot manual migration ok)

### Non-goals
- ไม่ refactor any code (Plan 01 + 02 done)
- ไม่ touch user data (preserve)
- ไม่ delete caches (would slow scan unnecessarily)
- ไม่ทำ rollback path (forward-only)
- ไม่ทำ automated migration script — manual steps + cleanup ทำครั้งเดียว

# Anchor Refactor — Cleanup Old Data + Fresh Scan + TEST GATE 4

> Part 3 of 3 — Cleanup old algo data + fresh scan + TEST GATE 4 end-to-end verification. | Index: anchor-refactor-index
> Depends on: anchor-refactor-01-backend + anchor-refactor-02-frontend (both must merge first)
> Parallel-safe with: none — final integration step

## Phase 1: Delete old scan output
- [x] ลบ projects/4-MaxMahon/data/screener_*.json — all dates (rm data/screener_*.json) + verify no files left except screener_cache/ + scoring_config.json (if exists) — scope: only screener_*.json files at data/ root + ไม่แตะ subdir + ไม่แตะ history.json — Acceptance: ls data/ | grep -E 'screener_.*\.json$' | wc -l = 0
- [x] ลบ projects/4-MaxMahon/reports/scan_*.md — all dates — scope: only reports/scan_*.md (NOT anchor_scan_*.md from Plan 02 anchor scoring + NOT other report types) — Acceptance: ls reports/ | grep '^scan_' | wc -l = 0 + anchor_scan_*.md files preserved (if exists)

### Reference
```bash
cd projects/4-MaxMahon

# Phase 1 deletes
rm data/screener_*.json
ls data/ | head -10  # verify no screener_*.json left

rm reports/scan_*.md
ls reports/ | head -10  # verify only anchor_scan_*.md remains (if any)
```

## Phase 2: Clear exit_baselines + migrate history.json
- [x] Clear projects/4-MaxMahon/data/exit_baselines.json — write {} (empty dict) — old entry_score values are pillar based and don't translate cleanly. Fresh entries will populate on next scan ที่มีหุ้น NIWES_5555 PASS. scope: ไม่แตะ exit_baselines.json schema (just clear data) — Acceptance: cat data/exit_baselines.json = '{}'
- [x] Migrate projects/4-MaxMahon/data/history.json — transform old score field (pillar 0-100) -> display_score equivalent (score/10 rounded 1 decimal). For each scan_history entry: rename 'score' field to 'legacy_score' + add 'display_score' = legacy_score/10. Preserve all other fields (date, watchlist_status, transactions, etc.). scope: ไม่ลบ entries, ไม่แตะ structure other than score field — Acceptance: py -c 'import json; d=json.load(open("data/history.json")); print(list(d.keys())[:5]); first=d["scans"][0] if d.get("scans") else None; print(first)' shows migrated structure + cat data/history.json valid JSON

### Reference
```python
# Migration script approach:
import json
from pathlib import Path

ROOT = Path('projects/4-MaxMahon')

# Clear exit_baselines.json
(ROOT / 'data' / 'exit_baselines.json').write_text('{}\n', encoding='utf-8')

# Migrate history.json
history_path = ROOT / 'data' / 'history.json'
if history_path.exists():
    data = json.loads(history_path.read_text(encoding='utf-8'))
    # Schema: data may have 'top_candidates': [...], 'scans': [...], etc.
    # Transform any score field found in nested structures
    def transform(obj):
        if isinstance(obj, dict):
            if 'score' in obj and 'display_score' not in obj:
                old_score = obj['score']
                if isinstance(old_score, (int, float)):
                    obj['legacy_score'] = old_score
                    obj['display_score'] = round(old_score / 10, 1)
                    # keep old 'score' field for now (will rebuild on next scan)
            for v in obj.values():
                transform(v)
        elif isinstance(obj, list):
            for item in obj:
                transform(item)
    transform(data)
    history_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
```

**Note:** Read actual history.json structure first to verify migration covers all nested score fields.

## Phase 3: Fresh universe scan with new algo
- [x] รัน py scripts/screen_stocks.py — fresh scan 933 universe with new anchor pipeline. ใช้เวลา ~10-15 นาที. scope: just run + verify no error + verify output schema — Acceptance: scan completes + data/screener_2026-MM-DD.json created with new schema (candidates มี score + display_score + breakdown 4 ด้าน + disqualified + anchor_stage_tags) + reports/scan_2026-MM-DD.md created with 4-pillar markdown format

### Reference
```bash
cd projects/4-MaxMahon
SETSMART_API_KEY=... PYTHONUTF8=1 py scripts/screen_stocks.py

# Expected ending:
# ...
# Saved -> data/screener_YYYY-MM-DD.json
# report written: reports/scan_YYYY-MM-DD.md

# Verify schema
py -c "
import json
d = json.load(open('data/screener_2026-05-18.json'))
c = d['candidates'][0]
print('Keys:', sorted(c.keys()))
print('Score:', c.get('score'))
print('Display:', c.get('display_score'))
print('Breakdown:', c.get('breakdown'))
print('Disqualified:', c.get('disqualified'))
print('Anchor tags:', c.get('anchor_stage_tags'))
"
```

## Phase 4: TEST GATE 4 — End-to-end verification (UI check requires user)
- [x] Verify /api/screener + /api/stock/{sym} return new schema — start server (max-server.bat or py -m uvicorn server.app:app --port 50089) + curl 2 endpoints (need auth — use Supabase JWT or skip if dev). scope: API verification — Acceptance: curl /api/screener returns candidates with anchor schema + curl /api/stock/BBL returns anchor breakdown
- [x] TEST GATE 4 user verification — เปิด https://max.intensivetrader.com (หรือ localhost:50089) บน desktop + mobile + verify: (1) home page candidate cards show display_score 0.0-10.0 + 4-pillar breakdown chip (2) disqualified candidates show 'DISQUALIFIED' badge (3) /report/BBL page shows 4-pillar chart + penalty tags + disqualify state (4) mobile /m + /m/report/BBL same (5) no 'undefined' or broken UI elements. scope: UI verification — Acceptance: อาร์ทเปิดเว็บ + confirm 'ใช้ได้' ทุก checkpoint — กู verify ด้วยตาเปล่าไม่ได้

### Reference
```bash
# API verification (skip auth in dev — direct python call):
cd projects/4-MaxMahon
py -c "
import json
from server.app import _build_screener_payload  # or similar internal function
# OR direct call without server:
from pathlib import Path
import json
d = json.loads(Path('data/screener_2026-05-18.json').read_text(encoding='utf-8'))
print('Has candidates:', len(d.get('candidates', [])))
if d.get('candidates'):
    c = d['candidates'][0]
    expected_keys = ['score', 'display_score', 'breakdown', 'disqualified', 'anchor_stage_tags']
    for k in expected_keys:
        print(f'{k}: {c.get(k)}')
"

# UI verification (user manual):
# 1. Start server: max-server.bat (or py -m uvicorn server.app:app --port 50089)
# 2. Open https://max.intensivetrader.com OR http://localhost:50089/
# 3. Login + verify pages
# 4. Mobile: http://localhost:50089/m/
# 5. User confirms 'ใช้ได้' on all checkpoints
```

**Note:** UI verification = user manual check (per /build skill UI bypass rule). กู cannot verify visual output.
