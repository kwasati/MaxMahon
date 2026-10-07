---
project: 4-MaxMahon
created: 2026-05-18
last_updated: 2026-05-18
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: รัน py scripts/screen_stocks.py แล้วได้ screener_YYYY-MM-DD.json ที่ candidate score = anchor (internal 0-100) + display_score 0.0-10.0 + breakdown = 4 ด้าน (dividend/cashflow/moat/long_hold) + curl /api/screener + /api/stock/{sym} return new schema + existing pillar score functions ลบทิ้ง (replace_dont_layer)

### รายละเอียด
- Replace quality_score() in screen_stocks.py main() with compute_anchor_score from anchor_scoring.py
- compute_anchor_score(tags, agg) returns dict: anchor_score (int 0-100), display_score (float 0.0-10.0), by_dimension (dict 4 keys: dividend/cashflow/moat/long_hold), disqualified (bool), penalty (int), penalty_tags (list)
- candidate output schema เปลี่ยน: score = anchor_score, display_score = new field, breakdown = by_dimension dict, anchor_stage_tags (existing from Plan 01) preserved
- ลบ old pillar functions: compute_dividend_score / compute_valuation_score / compute_cash_flow_score / compute_hidden_value_score / compute_track_record_score in screen_stocks.py
- ลบ valuation_grade() function ถ้าไม่ใช้แล้ว (check usage in main + API)
- scan.py orchestrator: ใช้ output schema ใหม่ (no change needed if scan.py reads candidates dict)
- report_template.py: markdown report ใช้ anchor breakdown 4 ด้าน (D + C + M + L) แทน 5 pillar (D+V+C+H+T)
- server/app.py /api/screener: return candidates with anchor schema (score + display_score + by_dimension)
- server/app.py /api/stock/{sym}: merge snapshot + screener entry — return anchor breakdown for report page
- Disqualified handling: candidates ที่ติด disqualify_tags (FAKE_PROFIT/CASHFLOW_DETERIORATING/MOAT_ERODING) จะมี anchor_score=0 / display=0.0 + disqualified=True / disqualify_tags=list. API + frontend ต้องแสดง 'DISQUALIFIED' state ชัด
- Existing assign_signals() function (legacy tag generator) — keep parallel หรือ ลบ? Decision: keep แต่ frontend ไม่ใช้ (anchor_stage_tags primary)
- data/exit_baselines.json: stores 'entry_score' field — Plan 03 จะ migrate

### Scope Boundary
**In scope:**
- projects/4-MaxMahon/scripts/screen_stocks.py — replace quality_score in main() + ลบ pillar functions
- projects/4-MaxMahon/scripts/scan.py — minor updates if needed (orchestrator)
- projects/4-MaxMahon/scripts/report_template.py — markdown report ใช้ 4 pillar
- projects/4-MaxMahon/server/app.py — /api/screener + /api/stock/{sym} return anchor schema

**Out of scope:**
- Frontend JS files (Plan 02)
- scripts/anchor_scoring.py / scan_anchor.py / sector_taxonomy.py / fetch_data.py — preserve as-is
- Data cleanup + fresh scan (Plan 03)
- data/exit_baselines.json migration (Plan 03)
- history.json migration (Plan 03)

### Non-goals
- ไม่ keep pillar score backward compat — replace entirely
- ไม่ refactor existing anchor scoring modules (Plan 02 anchor scoring ของ session ก่อนเสร็จแล้ว)
- ไม่ทำ schema versioning / API version bump
- ไม่ migrate user data — preserve

# Anchor Refactor — Pipeline + API Backend

> Part 1 of 3 — Backend pipeline + API refactor. Replace quality_score with anchor scoring throughout Python pipeline + 2 API endpoints. | Index: anchor-refactor-index
> Depends on: none (anchor_scoring module + assign_anchor_stage_tags already exist from earlier plans)
> Parallel-safe with: none — Plan 02 frontend depends on this API contract

## Phase 1: Pipeline — replace quality_score in screen_stocks.py main()
- [x] แก้ scripts/screen_stocks.py main() — replace quality_score(data) call กับ compute_anchor_score(anchor_stage_tags, agg) จาก anchor_scoring module. Output dict per candidate: score=anchor_score (int 0-100), display_score=float 0.0-10.0, breakdown=by_dimension dict (4 keys), disqualified=bool, penalty=int, penalty_tags=list, anchor_stage_tags=existing list. ลบ result['breakdown'] dict ที่มี 5 pillar (dividend/valuation/cash_flow/hidden_value/track_record). scope: ไม่ลบ assign_signals() ยัง (parallel co-exist) + ไม่แตะ existing dividend_history schema — Acceptance: รัน screen_stocks.py แล้ว screener_*.json candidate entry มี keys: score (0-100), display_score (0.0-10.0), breakdown {dividend, cashflow, moat, long_hold}, disqualified, anchor_stage_tags

### Reference
```python
# current (scripts/screen_stocks.py main() loop — around line 1054)
# (after fetch + hard_filter)
anchor_stage_tags = assign_anchor_stage_tags(data, data.get('aggregates', {}))
result = quality_score(data)  # OLD — pillar based
# result['score'] = 0-100 int
# result['breakdown'] = {dividend, valuation, cash_flow, hidden_value, track_record}
# result['signals'] = list
# result['reasons'] = list

# Then result_entry build (around line 1080-1127):
result_entry = {
    'symbol': sym,
    'name': data.get('name'),
    'sector': data.get('sector'),
    'score': result['score'],  # OLD 0-100 pillar
    'breakdown': result['breakdown'],  # OLD 5 pillar
    'signals': result['signals'],
    'anchor_stage_tags': anchor_stage_tags,
    ...
}

# new
from anchor_scoring import compute_anchor_score

anchor_stage_tags = assign_anchor_stage_tags(data, data.get('aggregates', {}))
anchor_result = compute_anchor_score(anchor_stage_tags, data.get('aggregates', {}))
# anchor_result = {
#   'anchor_score': int 0-100,
#   'display_score': float 0.0-10.0,
#   'by_dimension': {'dividend', 'cashflow', 'moat', 'long_hold'},
#   'disqualified': bool,
#   'disqualify_tags': list (if disqualified),
#   'penalty': int (negative or 0),
#   'penalty_tags': list,
# }

# Legacy signals — keep for now (parallel co-exist, frontend will use anchor_stage_tags)
legacy_signals = assign_signals(data, anchor_result['anchor_score'])

result_entry = {
    'symbol': sym,
    'name': data.get('name'),
    'sector': data.get('sector'),
    'score': anchor_result['anchor_score'],  # NEW: anchor int 0-100
    'display_score': anchor_result['display_score'],  # NEW: float 0.0-10.0
    'breakdown': anchor_result['by_dimension'],  # NEW: 4-pillar dict
    'disqualified': anchor_result['disqualified'],
    'penalty': anchor_result['penalty'],
    'penalty_tags': anchor_result.get('penalty_tags', []),
    'disqualify_tags': anchor_result.get('disqualify_tags', []),
    'signals': legacy_signals,  # legacy — keep parallel
    'anchor_stage_tags': anchor_stage_tags,
    ...
}
```

## Phase 2: Remove old pillar functions + valuation_grade cleanup
- [x] ลบ scripts/screen_stocks.py functions: compute_dividend_score (lines around 146-231) + compute_valuation_score (234-288) + compute_cash_flow_score (291-335) + compute_hidden_value_score (338-353) + compute_track_record_score (356-385) + quality_score (lines around 733-771) — ทั้งหมดถูก replace ด้วย compute_anchor_score แล้ว — scope: ไม่ลบ assign_signals (legacy keep) + ไม่ลบ valuation_grade (อาจยังใช้ที่อื่น verify ก่อน) — Acceptance: grep 'def compute_dividend_score|def quality_score' ใน screen_stocks.py = 0 hits + py -m py_compile screen_stocks.py passes + ไม่มี undefined references จาก deleted functions
- [x] Verify scripts/screen_stocks.py valuation_grade() function (lines around 646-730) ยังถูกเรียกที่ไหน — grep 'valuation_grade' across project. ถ้าไม่ใช้แล้ว = ลบ. ถ้ายังใช้ = keep + note. — scope: ไม่ refactor anchor scoring — Acceptance: ตัดสินใจชัดเจน (delete vs keep) + comment in commit

### Reference
```python
# Functions to delete (around these line ranges — verify before edit):
# - compute_dividend_score (lines 146-231)
# - compute_valuation_score (lines 234-288)  
# - compute_cash_flow_score (lines 291-335)
# - compute_hidden_value_score (lines 338-353)
# - compute_track_record_score (lines 356-385)
# - quality_score (lines 733-771)

# Keep:
# - assign_signals (lines 569-643 area) — legacy parallel
# - hard_filter (lines 78-145 area) — Niwes 5-5-5-5 filter
# - assign_anchor_stage_tags (lines 651-755 area) — Plan 01 anchor tags
```

## Phase 3: report_template.py — markdown report ใช้ 4 pillar anchor
- [x] แก้ scripts/report_template.py _top_pick_md function — ใช้ candidate['breakdown'] ที่เป็น anchor 4 ด้าน (dividend/cashflow/moat/long_hold) แทน 5 pillar เก่า (dividend/valuation/cash_flow/hidden_value/track_record). Display format: 'D{x}+C{y}+M{z}+L{w}' (4 chars) + show display_score 0.0-10.0 + show disqualified state — scope: ไม่แตะ markdown structure (heading, sections) — Acceptance: รัน scan + report.md ที่ generated มี breakdown 4 pillar + display score + disqualified marker

### Reference
```python
# current (around scripts/report_template.py:47-60 _top_pick_md)
def _top_pick_md(c):
    bd = c.get('breakdown', {})
    return f"  - {c['symbol']} - {c['score']}/100 (D{bd.get('dividend',0)}+V{bd.get('valuation',0)}+C{bd.get('cash_flow',0)}+H{bd.get('hidden_value',0)})"

# new
def _top_pick_md(c):
    bd = c.get('breakdown', {})
    display = c.get('display_score', c['score'] / 10)
    if c.get('disqualified'):
        dq = ', '.join(c.get('disqualify_tags', []))
        return f"  - {c['symbol']} - DISQUALIFIED ({dq})"
    parts = f"D{bd.get('dividend',0)}+C{bd.get('cashflow',0)}+M{bd.get('moat',0)}+L{bd.get('long_hold',0)}"
    penalty = c.get('penalty', 0)
    if penalty < 0:
        parts += f" P{penalty}"
    return f"  - {c['symbol']} - {display:.1f}/10.0 ({parts})"
```

## Phase 4: server/app.py — /api/screener + /api/stock/{sym} return anchor schema
- [x] แก้ server/app.py /api/screener endpoint — return candidates field schema ใหม่ (score=anchor_score, display_score, breakdown=4 pillar dict, disqualified, penalty, penalty_tags, disqualify_tags, anchor_stage_tags). scope: ไม่แตะ /api/screener pending_candidates section (filter-07 done already) + ไม่แตะ /api/screener/trend — Acceptance: curl http://localhost:50089/api/screener (with auth) returns candidate dicts มี keys ทั้งหมด: score, display_score, breakdown {dividend,cashflow,moat,long_hold}, disqualified, anchor_stage_tags
- [x] แก้ server/app.py /api/stock/{sym} endpoint — merge snapshot + screener data + return anchor breakdown for single stock. scope: ไม่แตะ /api/stock/{sym}/analyze (Claude deep analyze) + ไม่แตะ /api/stock/{sym}/price-history — Acceptance: curl /api/stock/BBL returns dict มี anchor score + breakdown + display + disqualified status
- [x] Smoke test — start server (max-server.bat) + curl 2 endpoints + verify new schema. scope: smoke only — Acceptance: 2 endpoints return new schema without error

### Reference
```python
# server/app.py — find /api/screener handler
# current returns:
# data = read_json(screener_path)
# data['candidates'] = [...]  # built from screener_*.json directly

# new — the candidates field already has new schema from Phase 1 (pipeline writes new schema)
# so /api/screener just passes through. Verify no transformation strips new fields.

# /api/stock/{sym} — find handler (around line 277-331 per earlier exploration)
# Returns merged snapshot. Need to verify candidate breakdown passed through correctly.
# (Mostly should work transparently since data flows from screener json.)
```
