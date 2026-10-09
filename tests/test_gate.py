"""Gate (hard_filter) tests — fixture only, no network."""
import sys
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from screen_stocks import hard_filter, gate_flags, projected_yield_5y  # noqa: E402

CY = datetime.now().year


def make(dy, price=100.0, dps=None, cagr5=None, cagr10=None, growth_streak=0, mcap=10e9,
         eps=None, pe=10, pbv=1.0, payout=0.5, gaps=None, streak=10, hist="auto"):
    if dps is None:
        dps = dy * price / 100
    eps = eps if eps is not None else [1.0] * 5
    years = list(range(CY - len(eps), CY))
    if hist == "auto":
        hist = {CY - 1: dps}
    return {
        "symbol": "T.BK", "price": price, "dividend_yield": dy, "pe_ratio": pe, "pb_ratio": pbv,
        "market_cap": mcap, "payout_ratio": payout, "dividend_history": hist,
        "yearly_metrics": [{"year": str(y), "diluted_eps": e} for y, e in zip(years, eps)],
        "aggregates": {
            "dividend_streak": streak, "dividend_growth_streak": growth_streak,
            "dps_cagr": cagr5, "dps_10y_cagr": cagr10,
            "dividend_last_complete_fy": CY - 1, "data_gaps": gaps or [],
        },
    }


class GateTest(unittest.TestCase):
    def test_main_path_yield_6_passes(self):
        # assert: yield 6% -> PASS, no PASSED_VIA_GROWTH flag
        d = make(6.0)
        self.assertEqual(hard_filter(d)[0], "PASS")
        self.assertFalse(any(f.startswith("PASSED_VIA_GROWTH") for f in gate_flags(d)))

    def test_growth_path_passes_with_flag(self):
        # assert: yield 4, dps 4, g=0.10 -> 4*1.1^5=6.44% >= 5 -> PASS + flag
        d = make(4.0, cagr5=0.10, cagr10=0.12, growth_streak=3)
        self.assertEqual(hard_filter(d)[0], "PASS")
        self.assertTrue(any(f.startswith("PASSED_VIA_GROWTH") for f in gate_flags(d)))

    def test_growth_not_enough_fails(self):
        # assert: yield 3, g=0.10 -> 3*1.61=4.83% < 5 -> FAIL
        d = make(3.0, cagr5=0.10, cagr10=0.10, growth_streak=3)
        self.assertEqual(hard_filter(d)[0], "FAIL")

    def test_no_growth_fails(self):
        # assert: yield 4 with growth_streak 0 / g None -> FAIL
        self.assertEqual(hard_filter(make(4.0, cagr5=0.2, growth_streak=0))[0], "FAIL")
        self.assertEqual(hard_filter(make(4.0, growth_streak=3))[0], "FAIL")
        self.assertEqual(hard_filter(make(4.0, cagr5=-0.05, growth_streak=3))[0], "FAIL")

    def test_growth_capped_at_015(self):
        # assert: cagr 0.40 is capped to 0.15 -> g==0.15, projected = 3*1.15^5=6.03
        d = make(3.0, cagr5=0.40, cagr10=0.50, growth_streak=3)
        py, g = projected_yield_5y(d)
        self.assertAlmostEqual(g, 0.15)
        self.assertAlmostEqual(py, 3.0 * 1.15 ** 5, places=6)

    def test_lower_of_two_cagr_used(self):
        # assert: g = min(0.05, 0.20) = 0.05 -> 3*1.05^5=3.83 < 5 -> FAIL
        d = make(3.0, cagr5=0.20, cagr10=0.05, growth_streak=4)
        self.assertAlmostEqual(projected_yield_5y(d)[1], 0.05)
        self.assertEqual(hard_filter(d)[0], "FAIL")

    def test_pe_pbv_do_not_fail(self):
        # assert: PE 30 / PBV 5 with yield 6 -> PASS
        self.assertEqual(hard_filter(make(6.0, pe=30, pbv=5))[0], "PASS")

    def test_loss_years_flag_but_pass(self):
        # assert: 2 loss years in 5 -> PASS + LOSS_YEARS:2/5
        d = make(6.0, eps=[1.0, -0.5, 1.0, -0.2, 1.0])
        self.assertEqual(hard_filter(d)[0], "PASS")
        self.assertIn("LOSS_YEARS:2/5", gate_flags(d))

    def test_short_eps_and_payout_and_div_short_flags(self):
        # assert: 3 EPS years, payout 1.2, data_gaps -> three flags, still PASS
        d = make(6.0, eps=[1.0, 1.0, 1.0], payout=1.2, gaps=["dividend_history_short"])
        flags = gate_flags(d)
        self.assertEqual(hard_filter(d)[0], "PASS")
        self.assertIn("EPS_HISTORY_SHORT:3", flags)
        self.assertIn("PAYOUT_OVER_100", flags)
        self.assertIn("DIVIDEND_HISTORY_SHORT", flags)

    def test_small_market_cap_fails(self):
        # assert: mcap 4B < 5B -> FAIL even with yield 8
        self.assertEqual(hard_filter(make(8.0, mcap=4e9))[0], "FAIL")

    def test_yahoo_flake_pending(self):
        # assert: yield>0, streak 0, no history -> PENDING
        self.assertEqual(hard_filter(make(6.0, streak=0, hist={}))[0], "PENDING")

    def test_no_dividend_data_fails(self):
        # assert: yield None -> FAIL
        self.assertEqual(hard_filter(make(None, dps=0.0))[0], "FAIL")


if __name__ == "__main__":
    unittest.main()
