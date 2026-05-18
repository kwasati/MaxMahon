"""MaxMahon Anchor Scan v1.0 — standalone CLI for anchor scoring report.

Reads screener output (with anchor_stage_tags + 21 aggregates from Plan 01) and
generates a markdown report with TOP candidates per anchor band.

Does NOT replace existing scan.py — runs side-by-side for validation.

Usage:
    py scripts/scan_anchor.py
    py scripts/scan_anchor.py --screener data/screener_2026-05-18.json
    py scripts/scan_anchor.py --out reports/anchor_custom.md
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
        parts.append(f'P={result["penalty"]} ({ptags})')
    return ' + '.join(parts)


def _render_report(scored: list, scan_date: str) -> str:
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

    band_labels = [
        ('high', 'High Anchor (8.0-10.0)'),
        ('mid', 'Mid Anchor (5.0-7.9)'),
        ('low', 'Low Anchor (0.1-4.9)'),
        ('disqualified', 'Disqualified (0.0)'),
    ]

    for band_name, label in band_labels:
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
    parser.add_argument('--screener', default=None,
                        help='Path to screener_*.json (default = latest in data/)')
    parser.add_argument('--out', default=None,
                        help='Output report path (default = reports/anchor_scan_YYYY-MM-DD.md)')
    args = parser.parse_args()

    screener_path = Path(args.screener) if args.screener else _latest_screener_path()
    print(f'Using screener: {screener_path}')
    data = json.loads(screener_path.read_text(encoding='utf-8'))

    candidates = data.get('candidates', [])
    print(f'Loaded {len(candidates)} PASS candidates')

    scored = []
    skipped = 0
    for cand in candidates:
        sym = cand.get('symbol', '')
        tags = cand.get('anchor_stage_tags', [])
        agg = cand.get('aggregates', {})
        if not tags:
            skipped += 1
            continue  # screener was generated before Plan 01 — anchor_stage_tags missing
        result = compute_anchor_score(tags, agg)
        scored.append({'symbol': sym, 'anchor_stage_tags': tags, 'result': result})

    if skipped > 0:
        print(f'WARNING: skipped {skipped} candidates without anchor_stage_tags '
              '(screener generated before Plan 01 deploy — re-run screen_stocks.py to refresh)')
    print(f'Scored {len(scored)} stocks')

    today = datetime.now().strftime('%Y-%m-%d')
    out_path = Path(args.out) if args.out else ROOT / 'reports' / f'anchor_scan_{today}.md'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(_render_report(scored, today), encoding='utf-8')
    print(f'Report written: {out_path}')


if __name__ == '__main__':
    main()
