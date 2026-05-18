"""MaxMahon Sector Taxonomy — Stage 5 stability classification.

Sector mapping based on Niwes parent plan section 7. Sectors derived from
thaifin sector field; symbol-level exceptions override for utility-like stocks.
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
    'Banking',
    'Finance & Securities',
    'Insurance',
}

# Symbol-level overrides - utility-like stocks that are stable even if
# their sector classifies as cyclical (e.g. electricity utilities in Energy)
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
    """Return all sector lists as dict - for config inspection / UI display."""
    return {
        'stable_sectors': sorted(STABLE_SECTORS),
        'cyclical_sectors': sorted(CYCLICAL_SECTORS),
        'stable_utility_symbols': sorted(STABLE_UTILITY_SYMBOLS),
    }


if __name__ == '__main__':
    # Smoke test
    assert is_stable_sector('Commerce') is True
    assert is_stable_sector('Banking') is False
    assert is_stable_sector('Energy & Utilities', 'EGCO') is True  # exception
    assert is_cyclical_sector('Banking') is True
    print('sector_taxonomy smoke OK')
    print(f'Stable sectors: {len(STABLE_SECTORS)}')
    print(f'Cyclical sectors: {len(CYCLICAL_SECTORS)}')
    print(f'Stable utility symbols: {len(STABLE_UTILITY_SYMBOLS)}')
