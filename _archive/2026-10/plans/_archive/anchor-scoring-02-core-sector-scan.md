---
project: 4-MaxMahon
created: 2026-05-18
last_updated: 2026-05-18
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: รัน py scripts/scan_anchor.py แล้วได้ output reports/anchor_scan_YYYY-MM-DD.md ที่ TOP candidates per anchor band (high/mid/low) + disqualify list ตาม spec v1.0 — internal 0-100 / display 0.0-10.0

### รายละเอียด
- Phase 1 anchor_scoring.py: DEFAULT_SCORING_CONFIG dict (ตรง spec v1.0 Implementation notes) + compute functions per ด้าน + apply disqualify/penalty + display conversion
- Phase 2 sector_taxonomy.py: STABLE_SECTORS / CYCLICAL_SECTORS / STABLE_UTILITY_SYMBOLS lists (จาก parent plan section 7) + load helper + Plan 01 inline list refactor to use this module
- Phase 3 scan_anchor.py CLI: รัน standalone บน screener output file (default = latest) + iterate ทุก PASS หุ้น + compute anchor score + sort + write markdown report ที่ reports/anchor_scan_YYYY-MM-DD.md
- Phase 4 TEST GATE 3: run scan_anchor.py + verify 5 หุ้น Niwes sample คะแนนใกล้ Phase 6 verify ของ spec
- anchor_scoring.py compute order ตรงตาม spec Calculation order (8 steps): check disqualify -> dividend -> cashflow -> moat -> long_hold -> sum -> penalty -> max(0, total - penalty)
- Bonus step function = discrete floor lookup (find largest threshold where value >= threshold for 'higher is better')
- Long_hold base_additive = sum of STABLE + RESILIENT bases (orthogonal, ไม่ exclusive)
- scan_anchor.py = standalone CLI ไม่กระทบ existing scan.py / quality_score / report.js / server endpoint
- scan_anchor.py output bands: high (anchor >= 80 / display >= 8.0) / mid (50-79 / 5.0-7.9) / low (1-49 / 0.1-4.9) / disqualified (anchor=0)
- Report format: markdown table per band + count summary + per-stock breakdown (4 ด้าน + penalty + display)
- Plan 01 inline sector list (STABLE_SECTORS_TEMP etc.) refactor to import from sector_taxonomy.py — backward compat preserved
- anchor_scoring.py reads anchor_stage_tags + aggregates 21 fields from Plan 01 output (screener_*.json)
- scan_anchor.py CLI flag: --screener (path to screener json, default = latest) / --out (output report path, default = reports/anchor_scan_YYYY-MM-DD.md)

### Scope Boundary
**In scope:**
- projects/4-MaxMahon/scripts/anchor_scoring.py (NEW) — DEFAULT_SCORING_CONFIG + compute functions + apply_disqualify + apply_penalty + display conversion
- projects/4-MaxMahon/scripts/sector_taxonomy.py (NEW) — sector lists + load_sector_taxonomy() helper
- projects/4-MaxMahon/scripts/scan_anchor.py (NEW) — CLI script + markdown report generator
- projects/4-MaxMahon/scripts/screen_stocks.py — refactor assign_anchor_stage_tags() to use sector_taxonomy.py imports (replace inline lists from Plan 01)
- projects/4-MaxMahon/reports/anchor_scan_YYYY-MM-DD.md (output, gitignored)

**Out of scope:**
- Existing quality_score() / scan.py / report.py / report.js / server endpoint — ไม่กระทบ
- Replace pillar-based pipeline (deferred to future plan)
- UI integration (deferred — frontend ยังใช้ existing fields)
- Cron schedule integration (future plan — manual CLI for now)

### Non-goals
- ไม่ replace existing quality_score — parallel co-exist ระหว่าง transition
- ไม่ทำ /api endpoint สำหรับ anchor score (future plan)
- ไม่ change frontend UI (future plan)
- ไม่ schedule scan_anchor.py ใน APScheduler (manual CLI run first)
- ไม่ refactor screener output schema เพิ่ม anchor_score key (future plan — scan_anchor reads input ออก output)

# Anchor Scoring — Core + Sector Taxonomy + Standalone Scan

> Part 2 of 2 — Anchor scoring core + sector taxonomy + standalone scan CLI. Validates spec v1.0 on 932 universe. | Index: anchor-scoring-index
> Depends on: anchor-scoring-01-aggregates-tags (Plan 01 must finish — uses 21 aggregates + Stage 1-6 tags)
> Parallel-safe with: none — Plan 01 must complete

## Phase 1: anchor_scoring.py core module
- [x] สร้าง scripts/anchor_scoring.py — module containing: (1) DEFAULT_SCORING_CONFIG dict ตรงตาม spec v1.0 (ดู scoring-anchor-spec.md DEFAULT_SCORING_CONFIG block) (2) helper bonus_lookup(value, steps, lower_is_better=False) สำหรับ step function (3) compute_dividend(tags, agg, config) -> float (4) compute_cashflow(tags, agg, config) -> float (5) compute_moat(tags, agg, config) -> float (6) compute_long_hold(tags, agg, config) -> float (7) check_disqualify(tags, config) -> bool (8) apply_penalty(tags, config) -> float (9) compute_anchor_score(tags, agg, config) -> dict — orchestrates all 8 step calculation per spec — returns {anchor_score: int 0-100, display_score: float 0.0-10.0, by_dimension: dict, disqualified: bool, penalty: int} — scope: ไม่กระทบ existing modules — Acceptance: import anchor_scoring + compute_anchor_score(tags, agg) returns dict with expected keys for sample CPALL (disqualified=True ถ้า CASHFLOW_DETERIORATING ติด)

### Reference
Create new file at projects/4-MaxMahon/scripts/anchor_scoring.py.

Spec source: `docs/scoring-anchor-spec.md` v1.0 — Section 'Re-alignment with Implementation Plan (DEFAULT_SCORING_CONFIG)' has the full Python dict definition. Copy that dict verbatim into this module.

```python
"""MaxMahon Anchor Scoring v1.0 — pure computation module.

Reads anchor_stage_tags + aggregates (from screen_stocks.py output) and
computes anchor score per spec v1.0 (docs/scoring-anchor-spec.md).

Internal scale: 0-100. Display scale: 0.0-10.0 (divide by display_scale, 1 decimal).
Side-by-side with existing pillar-based quality_score — does NOT replace.
"""
from typing import Optional


# Copy from spec v1.0 verbatim (do not modify thresholds without spec change)
DEFAULT_SCORING_CONFIG = {
    'anchor': {
        'dividend': {
            'base': {
                'GROWING_DIVIDEND': 14,
                'STABLE_PAYER': 6,
                'NEW_PAYER': 2,
                'INTERMITTENT': 0,
            },
            'bonus_metrics': {
                'dps_5y_cagr': {
                    'steps': [(0.00, 0), (0.03, 5), (0.06, 9), (0.10, 12), (0.15, 13)],
                },
            },
            'modifiers': {
                'ROE_IMPROVING': 3,
                'ROE_STABLE': 0,
                'ROE_DECLINING': -5,
            },
            'cap': 35,
        },
        'cashflow': {
            'base': {
                'CASHFLOW_HEALTHY': 17,
                'CASHFLOW_OK': 9,
                'CASHFLOW_BELOW_PROFIT': 0,
                'FAKE_PROFIT': 0,
                'CASHFLOW_DETERIORATING': 0,
            },
            'bonus_metrics': {
                'ccr_avg_3y': {'steps': [(1.0, 3), (1.5, 6), (2.0, 8)]},
            },
            'cap': 25,
        },
        'moat': {
            'base': {
                'STRONG_MOAT': 10,
                'MODERATE_MOAT': 4,
                'NO_MOAT': 0,
                'MOAT_ERODING': 0,
                'ROE_FUELED_BY_DEBT': 0,
            },
            'bonus_metrics': {
                'roe_consecutive_15plus_years': {'steps': [(10, 5), (15, 9), (20, 11)]},
            },
            'modifiers': {
                'GM_IMPROVING': 2,
                'GM_STABLE': 0,
                'GM_DECLINING': -3,
            },
            'cap': 25,
        },
        'long_hold': {
            'base_additive': {
                'STABLE_BUSINESS': 4,
                'RESILIENT_THROUGH_CRISIS': 6,
            },
            'bonus_metrics': {
                'eps_cv_10y': {
                    'steps': [(0.30, 0), (0.24, 1), (0.15, 2)],
                    'lower_is_better': True,
                },
                'crisis_drop_avg_pct': {
                    'steps': [(-0.40, 0), (-0.29, 1), (-0.14, 2), (-0.04, 3)],
                    'lower_magnitude_is_better': True,
                },
            },
            'cap': 15,
        },
        'total_cap': 100,
    },
    'disqualify_tags': ['FAKE_PROFIT', 'CASHFLOW_DETERIORATING', 'MOAT_ERODING'],
    'penalty_tags': {
        'YIELD_TRAP': -15,
        'DIVIDEND_SHRINKING': -10,
        'ROE_FUELED_BY_DEBT': -10,
        'CASHFLOW_BELOW_PROFIT': -5,
        'CYCLICAL_BUSINESS': -5,
    },
    'no_action_tags': ['MIXED_STABILITY', 'NO_MOAT', 'INTERMITTENT'],
    'display_scale': 10,
}


def bonus_lookup(value: Optional[float], steps: list, lower_is_better: bool = False,
                lower_magnitude_is_better: bool = False) -> int:
    """Step function — find largest threshold where value qualifies.
    
    Returns the score at the appropriate step. Returns 0 if value < first threshold (higher_is_better)
    or value > first threshold (lower_is_better) or |value| > first |threshold| (lower_magnitude_is_better).
    """
    if value is None:
        return 0
    if lower_magnitude_is_better:
        # crisis_drop_avg: value is negative; closer to 0 (smaller |value|) is better
        score = 0
        for threshold, pts in steps:
            if value >= threshold:  # e.g. value=-0.10, threshold=-0.14 -> -0.10 >= -0.14 True
                score = pts
        return score
    if lower_is_better:
        # eps_cv: value is positive; smaller is better
        score = 0
        for threshold, pts in steps:
            if value <= threshold:
                score = pts
        return score
    # higher_is_better (default)
    score = 0
    for threshold, pts in steps:
        if value >= threshold:
            score = pts
    return score


def check_disqualify(tags: list[str], config: dict = None) -> bool:
    config = config or DEFAULT_SCORING_CONFIG
    return bool(set(tags) & set(config['disqualify_tags']))


def apply_penalty(tags: list[str], config: dict = None) -> int:
    config = config or DEFAULT_SCORING_CONFIG
    return sum(config['penalty_tags'].get(t, 0) for t in tags)


def compute_dividend(tags: list[str], agg: dict, config: dict = None) -> int:
    config = config or DEFAULT_SCORING_CONFIG
    dim = config['anchor']['dividend']
    # Base: pick the tier tag that's in dividend.base
    base = 0
    for tag in tags:
        if tag in dim['base']:
            base = max(base, dim['base'][tag])
    # Bonus
    bonus = 0
    if 'dps_5y_cagr' in dim['bonus_metrics']:
        value = agg.get('dps_cagr')  # Plan 01 uses dps_cagr from existing aggregates
        bonus = bonus_lookup(value, dim['bonus_metrics']['dps_5y_cagr']['steps'])
    # Modifier (ROE trend)
    modifier = 0
    for tag in tags:
        if tag in dim['modifiers']:
            modifier = dim['modifiers'][tag]
            break
    total = base + bonus + modifier
    return min(max(total, 0), dim['cap'])


def compute_cashflow(tags: list[str], agg: dict, config: dict = None) -> int:
    config = config or DEFAULT_SCORING_CONFIG
    dim = config['anchor']['cashflow']
    base = 0
    for tag in tags:
        if tag in dim['base']:
            base = max(base, dim['base'][tag])
    bonus = 0
    if 'ccr_avg_3y' in dim['bonus_metrics']:
        value = agg.get('ccr_avg_3y')
        bonus = bonus_lookup(value, dim['bonus_metrics']['ccr_avg_3y']['steps'])
    total = base + bonus
    return min(max(total, 0), dim['cap'])


def compute_moat(tags: list[str], agg: dict, config: dict = None) -> int:
    config = config or DEFAULT_SCORING_CONFIG
    dim = config['anchor']['moat']
    base = 0
    for tag in tags:
        if tag in dim['base']:
            base = max(base, dim['base'][tag])
    bonus = 0
    if 'roe_consecutive_15plus_years' in dim['bonus_metrics']:
        value = agg.get('roe_consecutive_15plus_years')
        bonus = bonus_lookup(value, dim['bonus_metrics']['roe_consecutive_15plus_years']['steps'])
    # Modifier (GM trend)
    gm_trend = agg.get('gm_trend', 'stable')
    gm_tag = 'GM_' + gm_trend.upper()  # 'GM_IMPROVING' / 'GM_STABLE' / 'GM_DECLINING'
    modifier = dim['modifiers'].get(gm_tag, 0)
    total = base + bonus + modifier
    return min(max(total, 0), dim['cap'])


def compute_long_hold(tags: list[str], agg: dict, config: dict = None) -> int:
    config = config or DEFAULT_SCORING_CONFIG
    dim = config['anchor']['long_hold']
    # Additive base
    base = 0
    for tag in tags:
        if tag in dim['base_additive']:
            base += dim['base_additive'][tag]
    # Bonus 1: eps_cv
    bonus_eps = bonus_lookup(
        agg.get('eps_cv_10y'),
        dim['bonus_metrics']['eps_cv_10y']['steps'],
        lower_is_better=True
    )
    # Bonus 2: crisis drop avg
    drop_2011 = agg.get('crisis_2011_drop_pct')
    drop_2020 = agg.get('crisis_2020_drop_pct')
    avg_drop = None
    if drop_2011 is not None and drop_2020 is not None:
        avg_drop = (drop_2011 + drop_2020) / 2
    bonus_crisis = bonus_lookup(
        avg_drop,
        dim['bonus_metrics']['crisis_drop_avg_pct']['steps'],
        lower_magnitude_is_better=True
    )
    total = base + bonus_eps + bonus_crisis
    return min(max(total, 0), dim['cap'])


def compute_anchor_score(tags: list[str], agg: dict, config: dict = None) -> dict:
    """Top-level orchestrator — 8 step calculation per spec."""
    config = config or DEFAULT_SCORING_CONFIG
    
    # Step 1: Disqualify check
    if check_disqualify(tags, config):
        return {
            'anchor_score': 0,
            'display_score': 0.0,
            'by_dimension': {'dividend': 0, 'cashflow': 0, 'moat': 0, 'long_hold': 0},
            'disqualified': True,
            'disqualify_tags': [t for t in tags if t in config['disqualify_tags']],
            'penalty': 0,
        }
    
    # Step 2-5: Compute 4 dimensions
    d_score = compute_dividend(tags, agg, config)
    c_score = compute_cashflow(tags, agg, config)
    m_score = compute_moat(tags, agg, config)
    l_score = compute_long_hold(tags, agg, config)
    
    # Step 6: Sum + total cap
    total = d_score + c_score + m_score + l_score
    total = min(total, config['anchor']['total_cap'])
    
    # Step 7: Penalty
    penalty = apply_penalty(tags, config)
    
    # Step 8: Floor at 0
    final = max(0, total + penalty)  # penalty is negative
    
    return {
        'anchor_score': final,
        'display_score': round(final / config['display_scale'], 1),
        'by_dimension': {'dividend': d_score, 'cashflow': c_score, 'moat': m_score, 'long_hold': l_score},
        'disqualified': False,
        'penalty': penalty,
        'penalty_tags': [t for t in tags if t in config['penalty_tags']],
    }
```

## Phase 2: sector_taxonomy.py module + Plan 01 refactor
- [x] สร้าง scripts/sector_taxonomy.py — module with STABLE_SECTORS / CYCLICAL_SECTORS / STABLE_UTILITY_SYMBOLS lists (from parent plan section 7) + load_sector_taxonomy() helper + is_stable_sector(sector, symbol) + is_cyclical_sector(sector) — scope: pure data module, ไม่กระทบ existing — Acceptance: from sector_taxonomy import STABLE_SECTORS; 'Commerce' in STABLE_SECTORS = True
- [x] Refactor scripts/screen_stocks.py assign_anchor_stage_tags() — replace inline STABLE_SECTORS_TEMP / CYCLICAL_SECTORS_TEMP / STABLE_UTILITY_SYMBOLS_TEMP imports จาก sector_taxonomy.py — scope: ไม่เปลี่ยน function behavior — Acceptance: assign_anchor_stage_tags บน CPALL ยัง return tags ที่ Plan 01 expected

### Reference
Create new file at projects/4-MaxMahon/scripts/sector_taxonomy.py.

```python
"""MaxMahon Sector Taxonomy — Stage 5 stability classification.

From Niwes parent plan section 7. Sectors based on thaifin sector field.
"""

STABLE_SECTORS = {
    'Commerce',
    'Food & Beverage',
    'Health Care Services',
    'Information & Communication Technology',
    'Media & Publishing',
    'Tourism & Leisure',
    'Transportation & Logistics',
}

CYCLICAL_SECTORS = {
    'Energy & Utilities',
    'Petrochemicals & Chemicals',
    'Steel',
    'Construction Materials',
    'Property Development',
    'Mining',
    'Banking',  # cyclical credit cycle
    'Finance & Securities',
    'Insurance',
}

# Sector-level mismatch — utility-like symbols that are actually stable
# (these override CYCLICAL_SECTORS if sector classifies them as cyclical)
STABLE_UTILITY_SYMBOLS = {
    'EGCO', 'GPSC', 'RATCH', 'BPP', 'BCPG',  # electricity
    'WHAUP',  # utility infrastructure
    'TPIPP',  # power
}


def is_stable_sector(sector: str, symbol: str = '') -> bool:
    """True if symbol in stable utility exception list OR sector in STABLE_SECTORS."""
    sym = (symbol or '').replace('.BK', '').upper()
    if sym in STABLE_UTILITY_SYMBOLS:
        return True
    return sector in STABLE_SECTORS


def is_cyclical_sector(sector: str) -> bool:
    return sector in CYCLICAL_SECTORS


def load_sector_taxonomy() -> dict:
    """Return all sector lists as dict — for config inspection / UI display."""
    return {
        'stable_sectors': sorted(STABLE_SECTORS),
        'cyclical_sectors': sorted(CYCLICAL_SECTORS),
        'stable_utility_symbols': sorted(STABLE_UTILITY_SYMBOLS),
    }
```

Then in scripts/screen_stocks.py, replace:
```python
# Plan 01 inline (REMOVE):
STABLE_SECTORS_TEMP = {...}
CYCLICAL_SECTORS_TEMP = {...}
STABLE_UTILITY_SYMBOLS_TEMP = {...}

# With (NEW import):
from sector_taxonomy import is_stable_sector, is_cyclical_sector

# In assign_anchor_stage_tags() Stage 5 logic:
# OLD:
# is_stable_sector = (sector in STABLE_SECTORS_TEMP) or (symbol in STABLE_UTILITY_SYMBOLS_TEMP)
# is_cyclical_sector = sector in CYCLICAL_SECTORS_TEMP

# NEW:
stable = is_stable_sector(sector, symbol)
cyclical = is_cyclical_sector(sector)
```

## Phase 3: scan_anchor.py standalone CLI + markdown report
- [x] สร้าง scripts/scan_anchor.py — CLI script ที่ (1) parse CLI args: --screener (default = latest data/screener_*.json) / --out (default = reports/anchor_scan_YYYY-MM-DD.md) (2) load screener json + iterate ทุก PASS หุ้น (3) ใช้ anchor_stage_tags + aggregates -> compute_anchor_score (4) sort by anchor_score desc + group by band: high (80-100), mid (50-79), low (1-49), disqualified (0) (5) write markdown report with band sections + TOP candidates + per-stock breakdown — scope: pure CLI, ไม่กระทบ existing — Acceptance: py scripts/scan_anchor.py runs without error + output file created at reports/anchor_scan_YYYY-MM-DD.md + contains at least 4 band sections

### Reference
Create new file at projects/4-MaxMahon/scripts/scan_anchor.py.

```python
"""MaxMahon Anchor Scan v1.0 — standalone CLI for anchor scoring report.

Reads screener output (with anchor_stage_tags + 21 aggregates from Plan 01) and
generates a markdown report with TOP candidates per anchor band.

Does NOT replace existing scan.py — runs side-by-side for validation.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

from anchor_scoring import compute_anchor_score, DEFAULT_SCORING_CONFIG


def _latest_screener_path() -> Path:
    candidates = sorted((ROOT / 'data').glob('screener_*.json'), reverse=True)
    if not candidates:
        sys.exit('ERROR: no screener_*.json found in data/')
    return candidates[0]


def _classify_band(score: int) -> str:
    if score >= 80:
        return 'high'
    if score >= 50:
        return 'mid'
    if score >= 1:
        return 'low'
    return 'disqualified'


def _format_breakdown(result: dict) -> str:
    if result.get('disqualified'):
        dq = ', '.join(result.get('disqualify_tags', []))
        return f'DISQUALIFIED ({dq})'
    by_dim = result['by_dimension']
    parts = [
        f'D={by_dim["dividend"]}',
        f'C={by_dim["cashflow"]}',
        f'M={by_dim["moat"]}',
        f'L={by_dim["long_hold"]}',
    ]
    if result['penalty'] < 0:
        ptags = ', '.join(result.get('penalty_tags', []))
        parts.append(f'P={result["penalty"]}({ptags})')
    return ' + '.join(parts)


def _render_report(scored: list[dict], scan_date: str) -> str:
    bands = {'high': [], 'mid': [], 'low': [], 'disqualified': []}
    for entry in scored:
        band = _classify_band(entry['result']['anchor_score'])
        bands[band].append(entry)
    # Sort within each band by score desc
    for band in ('high', 'mid', 'low'):
        bands[band].sort(key=lambda e: e['result']['anchor_score'], reverse=True)
    
    lines = [
        f'# MaxMahon Anchor Scan — {scan_date}',
        '',
        f'**Spec:** v1.0 (internal 0-100 / display 0.0-10.0, 1 decimal)',
        f'**Scored:** {len(scored)} stocks',
        f'**Bands:** high={len(bands["high"])}, mid={len(bands["mid"])}, low={len(bands["low"])}, disqualified={len(bands["disqualified"])}',
        '',
    ]
    
    for band_name, label in [('high', 'High Anchor (8.0-10.0)'), ('mid', 'Mid Anchor (5.0-7.9)'),
                              ('low', 'Low Anchor (0.1-4.9)'), ('disqualified', 'Disqualified (0.0)')]:
        entries = bands[band_name]
        lines.append(f'## {label} — {len(entries)} stocks')
        lines.append('')
        if not entries:
            lines.append('_(none)_')
            lines.append('')
            continue
        lines.append('| Symbol | Score | Display | Breakdown | Tags |')
        lines.append('|--------|-------|---------|-----------|------|')
        for e in entries[:30]:  # top 30 per band
            sym = e['symbol']
            score = e['result']['anchor_score']
            display = e['result']['display_score']
            breakdown = _format_breakdown(e['result'])
            tags = ', '.join(e.get('anchor_stage_tags', []))
            lines.append(f'| {sym} | {score} | {display} | {breakdown} | {tags} |')
        if len(entries) > 30:
            lines.append(f'| ... | | | | _({len(entries) - 30} more)_ |')
        lines.append('')
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='MaxMahon Anchor Scan v1.0')
    parser.add_argument('--screener', default=None, help='Path to screener_*.json (default = latest)')
    parser.add_argument('--out', default=None, help='Output report path (default = reports/anchor_scan_YYYY-MM-DD.md)')
    args = parser.parse_args()
    
    screener_path = Path(args.screener) if args.screener else _latest_screener_path()
    print(f'Using screener: {screener_path}')
    data = json.loads(screener_path.read_text(encoding='utf-8'))
    
    candidates = data.get('candidates', [])
    print(f'Loaded {len(candidates)} PASS candidates')
    
    scored = []
    for cand in candidates:
        sym = cand.get('symbol', '')
        tags = cand.get('anchor_stage_tags', [])
        agg = cand.get('aggregates', {})
        if not tags or not agg:
            continue  # Plan 01 not yet integrated for this entry
        result = compute_anchor_score(tags, agg)
        scored.append({'symbol': sym, 'anchor_stage_tags': tags, 'result': result})
    
    print(f'Scored {len(scored)} stocks')
    
    today = datetime.now().strftime('%Y-%m-%d')
    out_path = Path(args.out) if args.out else ROOT / 'reports' / f'anchor_scan_{today}.md'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(_render_report(scored, today), encoding='utf-8')
    print(f'Report written: {out_path}')


if __name__ == '__main__':
    main()
```

## Phase 4: TEST GATE 3 — Anchor Scan Validation
- [x] รัน py scripts/scan_anchor.py บน latest screener (จาก Plan 01 build) — verify output report เกิดที่ reports/anchor_scan_YYYY-MM-DD.md + open ดูเอง verify Niwes invariants: (1) หุ้นที่มี CASHFLOW_DETERIORATING/FAKE_PROFIT/MOAT_ERODING ต้องอยู่ band 'disqualified' (2) หุ้นที่มี penalty heavy (DIVIDEND_SHRINKING/YIELD_TRAP) ต้องคะแนนต่ำลง 10-15+ คะแนน (3) ADVANC/BDMS ต้องอยู่ band mid (50-79) อย่างน้อย (4) PTT/SCC/CPALL = disqualified ตรง Phase 6 verify spec (sample 5 หุ้น Niwes) — scope: validation only, ไม่ adjust spec — Acceptance: report file ครบทุก band section + Niwes 5 หุ้น sample ตรง Phase 6 verify expectation อย่างน้อย 4/5 (PTT/SCC/CPALL disqualified + ADVANC/BDMS = mid+)

### Reference
```bash
cd C:\WORKSPACE\projects\4-MaxMahon
SETSMART_API_KEY=... py scripts/scan_anchor.py
# Expected output:
# Using screener: data/screener_2026-05-18.json
# Loaded 56 PASS candidates
# Scored 56 stocks
# Report written: reports/anchor_scan_2026-05-18.md

# Manual verification:
# cat reports/anchor_scan_2026-05-18.md | head -50
# Look for:
# - Disqualified section contains PTT, SCC, CPALL (if they pass hard_filter into screener)
# - High band contains ADVANC, BDMS, BBL, or similar quality blue chips
# - Each disqualified entry shows reason tag (FAKE_PROFIT / CASHFLOW_DETERIORATING / MOAT_ERODING)
# - Display scores at 0.0-10.0 with 1 decimal (e.g. 7.4, 5.2)
```

If validation fails (e.g. Niwes sample doesn't match), do NOT auto-adjust spec — report findings + ask Karl. Spec v1.0 = strict Niwes pure form per design discussion.
