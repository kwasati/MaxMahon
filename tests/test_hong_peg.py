"""peg_score tests - PEG = PE/growth, lower is better; score from ratio = 1/PEG (spec: growth/PE >= 1.5 -> 100, 1 -> 50)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import hong_stage1_scanner as hs  # noqa: E402


def test_anchor_points():
    # assert: PEG 0.5 -> 100 · PEG 1.0 -> 50 · PEG 2.0 -> 25 · PEG 0.67 (ratio ~1.5) -> ~100
    assert hs.peg_score(0.5) == 100.0
    assert hs.peg_score(1.0) == 50.0
    assert hs.peg_score(2.0) == 25.0
    assert abs(hs.peg_score(1 / 1.5) - 100.0) < 1e-9


def test_none_and_nonpositive_are_zero():
    # assert: None / 0 / negative PEG -> 0
    assert hs.peg_score(None) == 0.0 and hs.peg_score(0) == 0.0 and hs.peg_score(-1.2) == 0.0


def test_lower_peg_never_scores_lower():
    # assert: monotonic non-increasing in PEG over 0.01..20
    pegs = [0.01 * k for k in range(1, 2001)]
    scores = [hs.peg_score(p) for p in pegs]
    assert all(a >= b for a, b in zip(scores, scores[1:]))
    assert all(0.0 <= x <= 100.0 for x in scores)


def test_toa_vs_ichi_direction():
    # assert: the old bug is gone - TOA PEG 0.151 scores above ICHI PEG 7.72
    assert hs.peg_score(0.151) > hs.peg_score(7.72)
