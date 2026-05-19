"""Verify set.or.th DPS adapter against SETSMART ground truth.

Fetches dividends via `set_official_adapter.dps_by_fiscal_year()` for a
curated symbol list, compares to hardcoded ground truth (where available),
and writes a markdown report under docs/.

Run: py scripts/_verify_dps_set_fix.py
"""

from __future__ import annotations

import sys
import traceback
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

from set_official_adapter import dps_by_fiscal_year  # noqa: E402


GROUND_TRUTH: dict[str, dict[int, float]] = {
    'HTC':   {},  # pending manual verify from setsmart.com
    'BBL':   {},  # pending manual verify from setsmart.com
    'ILM':   {},  # pending manual verify from setsmart.com
    'KBANK': {},  # pending manual verify from setsmart.com
    'PTT':   {},  # pending manual verify from setsmart.com
    'AMATA': {},  # pending manual verify from setsmart.com
}

TOLERANCE_PCT = 5.0


def verify_symbol(
    sym: str,
    truth: dict[int, float],
) -> tuple[dict[int, float] | None, list[tuple[int, float, float | None, str]], str | None]:
    """Fetch DPS for sym and compare against truth dict.

    Returns (fetched, results, error).
    - fetched = {fy: dps} or None if fetch failed
    - results = list of (fy, expected, actual_or_None, status)
    - error = error string if fetch failed, else None
    """
    try:
        fetched = dps_by_fiscal_year(sym)
    except Exception as exc:  # noqa: BLE001
        return None, [], f'{type(exc).__name__}: {exc}'

    results: list[tuple[int, float, float | None, str]] = []
    for fy, expected in truth.items():
        actual = fetched.get(fy)
        if actual is None:
            results.append((fy, expected, None, 'MISSING'))
            continue
        if expected == 0:
            status = 'PASS' if actual == 0 else 'FAIL'
            results.append((fy, expected, actual, status))
            continue
        diff_pct = abs(actual - expected) / expected * 100
        status = 'PASS' if diff_pct <= TOLERANCE_PCT else 'FAIL'
        results.append((fy, expected, actual, status))
    return fetched, results, None


def _format_fetched(fetched: dict[int, float] | None) -> str:
    if not fetched:
        return '(empty)'
    items = sorted(fetched.items())
    return ', '.join(f'FY{fy}={dps}' for fy, dps in items)


def main() -> int:
    today = datetime.now().strftime('%Y-%m-%d')
    docs_dir = ROOT / 'docs'
    docs_dir.mkdir(parents=True, exist_ok=True)
    report_path = docs_dir / f'dps-set-fix-verification-{today}.md'

    md_lines: list[str] = [
        f'# DPS set.or.th Fix Verification - {today}',
        '',
        'Verifies `set_official_adapter.dps_by_fiscal_year()` against SETSMART '
        'ground truth (where available).',
        '',
        f'Tolerance: +/-{TOLERANCE_PCT:.1f}% per fiscal-year.',
        '',
    ]

    total_pass = 0
    total_checked = 0
    symbols_with_truth = 0
    summary_lines: list[str] = []

    for sym, truth in GROUND_TRUTH.items():
        print(f'=== {sym} ===')
        fetched, results, err = verify_symbol(sym, truth)
        md_lines.append(f'## {sym}')
        md_lines.append('')

        if err is not None:
            print(f'  ERROR: {err}')
            md_lines.append(f'**ERROR:** {err}')
            md_lines.append('')
            summary_lines.append(f'{sym}: ERROR ({err})')
            continue

        print(f'  fetched: {_format_fetched(fetched)}')
        md_lines.append(f'**Fetched:** {_format_fetched(fetched)}')
        md_lines.append('')

        if not truth:
            label = 'pending manual ground truth - data fetched OK'
            print(f'  {label}')
            md_lines.append(f'_{label}_')
            md_lines.append('')
            summary_lines.append(f'{sym}: pending manual verify')
            continue

        symbols_with_truth += 1
        md_lines.append('| FY | Expected | Actual | Status |')
        md_lines.append('|----|----------|--------|--------|')
        sym_pass = 0
        for fy, expected, actual, status in results:
            actual_str = f'{actual}' if actual is not None else '(missing)'
            print(f'  FY{fy}: expected={expected}  actual={actual_str}  {status}')
            md_lines.append(f'| {fy} | {expected} | {actual_str} | {status} |')
            total_checked += 1
            if status == 'PASS':
                sym_pass += 1
                total_pass += 1
        md_lines.append('')
        summary_lines.append(f'{sym}: PASS {sym_pass}/{len(results)}')
        print(f'  -> {sym}: PASS {sym_pass}/{len(results)}')
        print()

    md_lines.append('## Summary')
    md_lines.append('')
    for line in summary_lines:
        md_lines.append(f'- {line}')
    md_lines.append('')
    md_lines.append(
        f'**Overall (symbols with ground truth):** PASS {total_pass}/{total_checked}'
    )
    md_lines.append('')

    report_path.write_text('\n'.join(md_lines), encoding='utf-8')

    print('=' * 50)
    print('Summary')
    print('=' * 50)
    for line in summary_lines:
        print(f'  {line}')
    print()
    print(f'PASS {total_pass}/{total_checked} (ground-truth symbols only)')
    print(f'Report: {report_path}')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        sys.exit(1)
