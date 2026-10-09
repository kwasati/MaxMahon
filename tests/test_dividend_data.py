"""Dividend data-foundation tests (job-06). Offline: fixtures only, no network."""
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from scripts import data_adapter as da
from scripts import fetch_data as fd

FIX = json.loads((Path(__file__).parent / "fixtures" / "dividend_sources.json").read_text(encoding="utf-8"))
SET_BY_FY = {int(k): v for k, v in FIX["set_by_fy"].items()}


def _yahoo_by_fy():
    s = pd.Series([e[1] for e in FIX["yahoo_events"]], index=pd.to_datetime([e[0] for e in FIX["yahoo_events"]]))
    return da._attribute_dividends_to_fiscal_years(s)["by_fy"]


def _merged(set_by_fy=None):
    return da.merge_dividend_sources(SET_BY_FY if set_by_fy is None else set_by_fy, _yahoo_by_fy())


def _complete_flags(history, year=2026):
    return {y: y < year for y in history}


def _rows(n=12):
    return [{"year": str(2010 + i), "revenue": 100.0, "diluted_eps": 1.0, "roe": 0.1, "net_margin": 0.1,
             "gross_margin": 0.3, "operating_margin": 0.2, "fcf": 1.0, "ocf": 1.0, "ebitda": 1.0}
            for i in range(n)]


class MergeSourcesTest(unittest.TestCase):
    """item 1: long history from two sources; FY0 of the set window comes from yahoo."""

    def test_long_history_and_sources(self):
        m = _merged()
        hist, src = m["history"], m["source_by_fy"]
        self.assertEqual(min(hist), 2007)
        self.assertEqual(sorted(hist), list(range(2007, 2027)))  # no gap, 20 FYs
        self.assertEqual(src[2020], "yahoo")                     # first window year → yahoo
        self.assertEqual(src[2010], "yahoo")
        self.assertEqual(src[2021], "set")
        self.assertAlmostEqual(hist[2020], 3.0, places=2)         # not set's partial 1.8
        flags = _complete_flags(hist)
        self.assertGreaterEqual(fd.count_dividend_streak(hist, flags), 15)

    def test_yahoo_only_when_set_empty(self):
        m = da.merge_dividend_sources({}, _yahoo_by_fy())
        self.assertTrue(all(v == "yahoo" for v in m["source_by_fy"].values()))

    def test_first_window_year_kept_partial_if_yahoo_lacks_it(self):
        m = da.merge_dividend_sources({2020: 1.8, 2021: 3.0}, {})
        self.assertEqual(m["source_by_fy"][2020], "set_partial")


class MismatchTest(unittest.TestCase):
    """item 2: sources that disagree are flagged, never merged silently."""

    def test_agreeing_sources_have_no_mismatch(self):
        m = _merged()
        self.assertEqual(m["mismatches"], {})
        self.assertEqual(m["overlap_matches"], m["overlap_years"])
        self.assertGreaterEqual(m["overlap_years"], 5)

    def test_split_adjusted_yahoo_is_flagged_with_both_values(self):
        yh = dict(_yahoo_by_fy())
        yh[2022] = yh[2022] / 2  # yahoo halves DPS after a 2:1 split, set keeps the raw value
        m = da.merge_dividend_sources(SET_BY_FY, yh)
        self.assertIn(2022, m["mismatches"])
        self.assertAlmostEqual(m["mismatches"][2022]["set"], 3.1, places=2)
        self.assertAlmostEqual(m["mismatches"][2022]["yahoo"], 1.55, places=2)
        self.assertEqual(m["overlap_matches"], m["overlap_years"] - 1)

    def test_rounding_noise_is_not_a_mismatch(self):
        m = da.merge_dividend_sources({2021: 0.4, 2022: 0.6}, {2020: 0.3, 2021: 0.4004, 2022: 0.6})
        self.assertEqual(m["mismatches"], {})

    def test_year_missing_in_set_window_but_in_yahoo_is_flagged(self):
        m = da.merge_dividend_sources({2020: 1.0, 2021: 2.0, 2023: 2.0}, {2020: 2.0, 2022: 2.0})
        self.assertEqual(m["mismatches"][2022], {"set": None, "yahoo": 2.0})
        self.assertNotIn(2022, m["history"])


class CompleteYearsTest(unittest.TestCase):
    """item 3: one function decides complete years; every YoY aggregate reads it."""

    def setUp(self):
        self.hist = _merged()["history"]
        self.flags = _complete_flags(self.hist)

    def test_incomplete_year_excluded_everywhere(self):
        complete = da.complete_dividend_by_year(self.hist, self.flags)
        self.assertNotIn(2026, complete)
        self.assertEqual(da.last_complete_fy(self.hist, self.flags), 2025)
        agg = fd._build_aggregates(_rows(), self.hist, fy_is_complete=self.flags)
        # 2026 = 1.5 (half year) would look like a cut vs 3.5 if it leaked in
        self.assertEqual(agg["dividend_growth_streak"], fd.count_dividend_growth_streak(self.hist, self.flags))
        self.assertGreater(agg["rising_ratio"], 0.5)
        self.assertGreater(agg["avg_yoy_growth"], 0)
        self.assertEqual(agg["dividend_last_complete_fy"], 2025)

    def test_legacy_no_flags_uses_calendar_year(self):
        with patch.object(da, "datetime") as dt:
            dt.now.return_value.year = 2026
            self.assertNotIn(2026, da.complete_dividend_by_year({2025: 1.0, 2026: 0.5}))


class StreakTest(unittest.TestCase):
    """item 4: a missing year in the middle stops the streak."""

    def test_gap_stops_streak(self):
        hist = {2020: 1.0, 2021: 1.0, 2022: 1.0, 2024: 1.0, 2025: 1.0}  # CIMBT shape (2023 missing)
        flags = {y: True for y in hist}
        self.assertEqual(fd.count_dividend_streak(hist, flags), 2)

    def test_zero_year_stops_streak(self):
        hist = {2022: 1.0, 2023: 0.0, 2024: 1.0, 2025: 1.0}
        self.assertEqual(fd.count_dividend_streak(hist, {y: True for y in hist}), 2)

    def test_growth_streak_stops_at_gap(self):
        hist = {2021: 1.0, 2022: 2.0, 2024: 3.0, 2025: 4.0}
        self.assertEqual(fd.count_dividend_growth_streak(hist, {y: True for y in hist}), 1)

    def test_rising_ratio_ignores_pair_across_gap(self):
        hist = {2021: 1.0, 2022: 2.0, 2024: 3.0, 2025: 4.0}
        self.assertEqual(fd._compute_rising_ratio(hist, {y: True for y in hist}), 1.0)


class CagrTest(unittest.TestCase):
    """item 5: dps_cagr is a true 5-year CAGR over complete years; 10y added."""

    def setUp(self):
        self.hist = _merged()["history"]
        self.flags = _complete_flags(self.hist)

    def test_five_year_cagr_uses_fy2020_base_3_0(self):
        agg = fd._build_aggregates(_rows(), self.hist, fy_is_complete=self.flags)
        self.assertAlmostEqual(agg["dps_cagr"], (3.5 / 3.0) ** (1 / 5) - 1, places=6)
        self.assertEqual(agg["dps_5y_cagr"], agg["dps_cagr"])

    def test_ten_year_cagr(self):
        agg = fd._build_aggregates(_rows(), self.hist, fy_is_complete=self.flags)
        self.assertAlmostEqual(agg["dps_10y_cagr"], (3.5 / self.hist[2015]) ** (1 / 10) - 1, places=6)

    def test_none_when_history_too_short(self):
        hist = {2023: 1.0, 2024: 1.1, 2025: 1.2}
        flags = {y: True for y in hist}
        self.assertIsNone(fd.compute_dps_cagr(hist, flags, 5))
        self.assertIsNone(fd.compute_dps_cagr(hist, flags, 10))


class CrisisDropTest(unittest.TestCase):
    """item 6: crisis drops come from cached bars with one formula; stable across runs."""

    def test_formula_from_cached_bars(self):
        bars = FIX["monthly_bars"]
        self.assertAlmostEqual(fd._crisis_drop_from_bars(bars, 2010, 2011), 60.0 / 100.0 - 1)
        self.assertAlmostEqual(fd._crisis_drop_from_bars(bars, 2019, 2020), 48.0 / 120.0 - 1)

    def test_no_data_is_none_not_another_formula(self):
        self.assertIsNone(fd._crisis_drop_from_bars([], 2010, 2011))
        self.assertIsNone(fd._crisis_drop_from_bars(FIX["monthly_bars"][:2], 2010, 2011))  # no 2011 bars

    def test_aggregate_twice_gives_identical_dict_and_never_hits_network(self):
        hist = _merged()["history"]
        flags = _complete_flags(hist)
        with patch.object(fd, "load_crisis_bars", return_value=FIX["monthly_bars"]), \
             patch.dict("sys.modules", {"yahooquery": None}):  # any network import would raise
            a = fd._build_aggregates(_rows(), hist, fy_is_complete=flags, symbol="TCAP")
            b = fd._build_aggregates(_rows(), hist, fy_is_complete=flags, symbol="TCAP")
        self.assertEqual(a, b)
        self.assertAlmostEqual(a["crisis_2011_drop_pct"], -0.4)

    def test_no_symbol_gives_none(self):
        agg = fd._build_aggregates(_rows(), {2024: 1.0}, fy_is_complete={2024: True})
        self.assertIsNone(agg["crisis_2011_drop_pct"])
        self.assertIsNone(agg["crisis_2020_drop_pct"])


class CrisisDividendFactsTest(unittest.TestCase):
    """item 7: DPS change in 2008/2009/2011/2020 + years to regain the pre-cut level."""

    def test_cut_and_recovery(self):
        hist = {2007: 1.0, 2008: 0.5, 2009: 0.6, 2010: 1.0, 2011: 1.2, 2019: 2.0, 2020: 1.0, 2021: 1.5, 2022: 2.0}
        f = da.dividend_crisis_facts(hist, {y: True for y in hist})
        self.assertAlmostEqual(f["dps_change_2008"], -0.5)
        self.assertEqual(f["dps_recovery_years_2008"], 2)    # 2010 back to 1.0
        self.assertAlmostEqual(f["dps_change_2009"], 0.2)
        self.assertEqual(f["dps_recovery_years_2009"], 0)    # no cut
        self.assertAlmostEqual(f["dps_change_2020"], -0.5)
        self.assertEqual(f["dps_recovery_years_2020"], 2)    # 2022 back to 2.0

    def test_not_recovered_and_missing(self):
        hist = {2019: 2.0, 2020: 1.0, 2021: 1.5}
        f = da.dividend_crisis_facts(hist, {y: True for y in hist})
        self.assertIsNone(f["dps_recovery_years_2020"])      # never regained 2.0
        self.assertIsNone(f["dps_change_2008"])              # no 2007/2008 data
        self.assertIsNone(f["dps_recovery_years_2008"])

    def test_fixture_values_present_in_aggregates(self):
        hist = _merged()["history"]
        agg = fd._build_aggregates(_rows(), hist, fy_is_complete=_complete_flags(hist))
        for y in (2008, 2009, 2011, 2020):
            self.assertIn(f"dps_change_{y}", agg)
            self.assertIn(f"dps_recovery_years_{y}", agg)
        self.assertAlmostEqual(agg["dps_change_2008"], 0.0)


class DataGapsAndProfileTest(unittest.TestCase):
    """items 8-9: data_gaps flags short data without changing defaults; sector_profile label."""

    def test_short_data_flags_gaps_but_keeps_defaults(self):
        agg = fd._build_aggregates(_rows(3), {2025: 1.0}, fy_is_complete={2025: True})
        self.assertEqual(agg["roe_trend"], "ROE_STABLE")
        self.assertEqual(agg["gm_trend"], "stable")
        self.assertEqual(agg["net_debt_increases_in_3y"], 0)
        for name in ("roe_trend", "gm_trend", "net_debt_increases_in_3y", "rising_ratio",
                     "avg_yoy_growth", "dividend_history_short"):
            self.assertIn(name, agg["data_gaps"])

    def test_full_data_has_no_trend_gaps(self):
        hist = _merged()["history"]
        agg = fd._build_aggregates(_rows(14), hist, fy_is_complete=_complete_flags(hist))
        self.assertNotIn("roe_trend", agg["data_gaps"])
        self.assertNotIn("gm_trend", agg["data_gaps"])
        self.assertNotIn("dividend_history_short", agg["data_gaps"])

    def test_sector_profile(self):
        for sector in ("Banking", "Finance & Securities", "Insurance"):
            self.assertEqual(da.classify_sector_profile(sector), "bank")
        for sector in ("Property Fund & REIT", "Property Fund & REITs"):
            self.assertEqual(da.classify_sector_profile(sector), "reit")
        for sector in ("Property Development", "Food & Beverage", None):
            self.assertEqual(da.classify_sector_profile(sector), "general")


if __name__ == "__main__":
    unittest.main()
