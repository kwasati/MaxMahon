"""MaxMahon Anchor Scoring v1.0 — pure computation module.

Reads anchor_stage_tags + aggregates (from screen_stocks.py output) and
computes anchor score per spec v1.0 (docs/scoring-anchor-spec.md).

Internal scale: 0-100 (int). Display: 0.0-10.0 (1 decimal via display_scale).
Side-by-side with existing pillar-based quality_score — does NOT replace.
"""
from typing import Optional


# DEFAULT_SCORING_CONFIG — copy from spec v1.0 verbatim
# (do not modify thresholds without spec change)
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
                    'steps': [(0.40, 0), (0.30, 1), (0.20, 2)],   # v1.2: shifted right
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
        'CYCLICAL_BUSINESS': -3,   # v1.2: lighter penalty (Thai-pragmatic)
    },
    'no_action_tags': ['MIXED_STABILITY', 'NO_MOAT', 'INTERMITTENT'],
    'display_scale': 10,
}


def bonus_lookup(value: Optional[float], steps: list, lower_is_better: bool = False,
                 lower_magnitude_is_better: bool = False) -> int:
    """Step function — find largest threshold where value qualifies.

    Returns the score at the appropriate step. Returns 0 if value None or
    doesn't pass any threshold.
    """
    if value is None:
        return 0
    if lower_magnitude_is_better:
        # e.g. crisis_drop: value is negative, closer to 0 (smaller |value|) is better
        # steps sorted ascending: (-0.40, 0), (-0.29, 1), (-0.14, 2), (-0.04, 3)
        score = 0
        for threshold, pts in steps:
            if value >= threshold:  # value=-0.10 >= threshold=-0.14 -> qualifies
                score = pts
        return score
    if lower_is_better:
        # e.g. eps_cv: value positive, smaller is better
        # steps: (0.30, 0), (0.24, 1), (0.15, 2)
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


def check_disqualify(tags: list, config: dict = None) -> bool:
    config = config or DEFAULT_SCORING_CONFIG
    return bool(set(tags) & set(config['disqualify_tags']))


def apply_penalty(tags: list, config: dict = None) -> int:
    config = config or DEFAULT_SCORING_CONFIG
    return sum(config['penalty_tags'].get(t, 0) for t in tags)


def compute_dividend(tags: list, agg: dict, config: dict = None) -> int:
    config = config or DEFAULT_SCORING_CONFIG
    dim = config['anchor']['dividend']
    # Base: pick the tier tag that's in dividend.base (max across all matches)
    base = 0
    for tag in tags:
        if tag in dim['base']:
            base = max(base, dim['base'][tag])
    # Bonus: dps_cagr (from Plan 01 existing aggregate)
    bonus = 0
    if 'dps_5y_cagr' in dim['bonus_metrics']:
        value = agg.get('dps_cagr')  # Plan 01 uses dps_cagr key
        bonus = bonus_lookup(value, dim['bonus_metrics']['dps_5y_cagr']['steps'])
    # Modifier: ROE trend (first match)
    modifier = 0
    for tag in tags:
        if tag in dim['modifiers']:
            modifier = dim['modifiers'][tag]
            break
    total = base + bonus + modifier
    return min(max(total, 0), dim['cap'])


def compute_cashflow(tags: list, agg: dict, config: dict = None) -> int:
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


def compute_moat(tags: list, agg: dict, config: dict = None) -> int:
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
    # Modifier: GM trend
    gm_trend = agg.get('gm_trend', 'stable') or 'stable'
    gm_tag = 'GM_' + gm_trend.upper()  # 'GM_IMPROVING' / 'GM_STABLE' / 'GM_DECLINING'
    modifier = dim['modifiers'].get(gm_tag, 0)
    total = base + bonus + modifier
    return min(max(total, 0), dim['cap'])


def compute_long_hold(tags: list, agg: dict, config: dict = None) -> int:
    config = config or DEFAULT_SCORING_CONFIG
    dim = config['anchor']['long_hold']
    # Additive base
    base = 0
    for tag in tags:
        if tag in dim['base_additive']:
            base += dim['base_additive'][tag]
    # Bonus 1: eps_cv (lower is better)
    bonus_eps = bonus_lookup(
        agg.get('eps_cv_10y'),
        dim['bonus_metrics']['eps_cv_10y']['steps'],
        lower_is_better=True,
    )
    # Bonus 2: crisis drop avg (lower magnitude is better)
    drop_2011 = agg.get('crisis_2011_drop_pct')
    drop_2020 = agg.get('crisis_2020_drop_pct')
    avg_drop = None
    if drop_2011 is not None and drop_2020 is not None:
        avg_drop = (drop_2011 + drop_2020) / 2
    elif drop_2020 is not None:
        avg_drop = drop_2020  # use 2020 only if 2011 missing
    elif drop_2011 is not None:
        avg_drop = drop_2011
    bonus_crisis = bonus_lookup(
        avg_drop,
        dim['bonus_metrics']['crisis_drop_avg_pct']['steps'],
        lower_magnitude_is_better=True,
    )
    total = base + bonus_eps + bonus_crisis
    return min(max(total, 0), dim['cap'])


def compute_anchor_score(tags: list, agg: dict, config: dict = None) -> dict:
    """Top-level orchestrator — 8 step calculation per spec.

    Returns: {
        anchor_score: int 0-100,
        display_score: float 0.0-10.0,
        by_dimension: {dividend, cashflow, moat, long_hold},
        disqualified: bool,
        disqualify_tags: list (if disqualified),
        penalty: int (negative or 0),
        penalty_tags: list,
    }
    """
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
            'penalty_tags': [],
        }

    # Step 2-5: Compute 4 dimensions
    d_score = compute_dividend(tags, agg, config)
    c_score = compute_cashflow(tags, agg, config)
    m_score = compute_moat(tags, agg, config)
    l_score = compute_long_hold(tags, agg, config)

    # Step 6: Sum + total cap
    total = d_score + c_score + m_score + l_score
    total = min(total, config['anchor']['total_cap'])

    # Step 7: Penalty (negative or 0)
    penalty = apply_penalty(tags, config)

    # Step 8: Floor at 0
    final = max(0, total + penalty)

    return {
        'anchor_score': final,
        'display_score': round(final / config['display_scale'], 1),
        'by_dimension': {
            'dividend': d_score,
            'cashflow': c_score,
            'moat': m_score,
            'long_hold': l_score,
        },
        'disqualified': False,
        'penalty': penalty,
        'penalty_tags': [t for t in tags if t in config['penalty_tags']],
    }


if __name__ == '__main__':
    # Smoke test with sample data
    sample_cpall_tags = [
        'GROWING_DIVIDEND', 'ROE_IMPROVING', 'CASHFLOW_HEALTHY',
        'STRONG_MOAT', 'STABLE_BUSINESS', 'RESILIENT_THROUGH_CRISIS',
    ]
    sample_cpall_agg = {
        'dps_cagr': 0.13,
        'ccr_avg_3y': 0.94,
        'roe_consecutive_15plus_years': 15,
        'gm_trend': 'stable',
        'eps_cv_10y': 0.22,
        'crisis_2011_drop_pct': -0.10,
        'crisis_2020_drop_pct': -0.18,
    }
    result = compute_anchor_score(sample_cpall_tags, sample_cpall_agg)
    print(f'Sample CPALL anchor_score = {result["anchor_score"]} (display {result["display_score"]})')
    print(f'  Breakdown: {result["by_dimension"]}')
    print(f'  Penalty: {result["penalty"]} (tags: {result["penalty_tags"]})')

    # Sample with disqualify (CASHFLOW_DETERIORATING)
    sample_ptt_tags = ['STABLE_PAYER', 'CASHFLOW_HEALTHY', 'CASHFLOW_DETERIORATING']
    result_dq = compute_anchor_score(sample_ptt_tags, {})
    print(f'\nSample PTT (disqualified): anchor_score = {result_dq["anchor_score"]}, disqualified={result_dq["disqualified"]}, tags={result_dq["disqualify_tags"]}')
