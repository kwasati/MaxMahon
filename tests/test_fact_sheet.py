"""Fact sheet tests — pure calculators + compute/render on fixture dicts. No network, no files read."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import fact_sheet as fs  # noqa: E402

CFG = dict(fs.DEFAULT_CFG)


def make_data(profile="general", dps=None, n_years=10, eps=2.0, ocf=500e6, capex=-100e6, liab_step=0.0):
    last = 2024
    dps = dps if dps is not None else {y: 1.0 + 0.1 * (y - 2005) for y in range(2005, last + 1)}
    ym = [{"year": str(y), "diluted_eps": eps, "roe": 0.12, "net_income": 200e6, "ocf": ocf, "capex": capex,
           "total_debt": (1.0 + liab_step * (y - (last - n_years + 1))) * 1000e6, "equity": 1000e6, "bvps": 10.0,
           "dividends_paid": None} for y in range(last - n_years + 1, last + 1)]
    return {"symbol": "T.BK", "name": "Test", "sector": "Banking" if profile == "bank" else "Commerce",
            "sector_profile": profile, "price": 50.0, "price_as_of": "2026-10-09", "market_cap": 5e9,
            "pe_ratio": 8.0, "pb_ratio": 1.0, "dividend_yield": 2.0, "fetched_at": "2026-10-09T10:00:00",
            "yearly_metrics": ym, "dividend_history": dps, "fy_is_complete": {y: True for y in dps},
            "dividend_history_source": {y: "yahoo" for y in dps}}


class DividendCutsTest(unittest.TestCase):
    def test_count_year_and_recovery(self):
        # assert: cut 2006 (-40%) recovers in 2 yrs (2008 back to 1.0); 2010 cut (-18%) not recovered; material flag by 10% rule
        d = {2005: 1.0, 2006: 0.6, 2007: 0.7, 2008: 1.0, 2009: 1.1, 2010: 0.9}
        cuts = fs.dividend_cuts(d, 10)
        self.assertEqual([c["fy"] for c in cuts], [2006, 2010])
        self.assertAlmostEqual(cuts[0]["change"], -0.4)
        self.assertEqual(cuts[0]["recovery_years"], 2)
        self.assertIsNone(cuts[1]["recovery_years"])
        self.assertTrue(all(c["material"] for c in cuts))

    def test_small_cut_counted_but_not_material(self):
        # assert: -5% cut is a cut (count 1) but material (>=10%) count is 0
        cuts = fs.dividend_cuts({2005: 1.0, 2006: 0.95}, 10)
        self.assertEqual(len(cuts), 1)
        self.assertFalse(cuts[0]["material"])

    def test_gap_year_not_compared(self):
        # assert: 2005 -> 2007 (2006 missing) is not read as a cut
        self.assertEqual(fs.dividend_cuts({2005: 1.0, 2007: 0.5}, 10), [])


class GrowthTest(unittest.TestCase):
    def test_four_windows(self):
        # assert: 5/10/15/20y CAGR from last complete FY; window longer than history -> None
        hist = {y: 1.0 * 1.05 ** (y - 2005) for y in range(2005, 2025)}  # 20 values, 19 years of span
        d = {"dividend_history": hist, "fy_is_complete": {y: True for y in hist}}
        c = fs.cagr_windows(d, [5, 10, 15, 20])
        for n in (5, 10, 15):
            self.assertAlmostEqual(c[n], 0.05, places=6)
        self.assertIsNone(c[20])

    def test_scenarios_rule(self):
        # assert: bad = min window (floored at 0) · good = 5y capped · mid = mean
        r = fs.growth_scenarios({5: 0.30, 10: 0.09, 15: 0.04, 20: None}, 0.15)
        self.assertAlmostEqual(r["bad"], 0.04)
        self.assertAlmostEqual(r["good"], 0.15)
        self.assertAlmostEqual(r["mid"], 0.095)
        r = fs.growth_scenarios({5: 0.02, 10: -0.03}, 0.15)
        self.assertEqual(r["bad"], 0.0)

    def test_scenarios_without_5y(self):
        # assert: no 5y window -> good and mid are None, bad still from available windows
        r = fs.growth_scenarios({5: None, 10: 0.06}, 0.15)
        self.assertAlmostEqual(r["bad"], 0.06)
        self.assertIsNone(r["good"])
        self.assertIsNone(r["mid"])


class YocTableTest(unittest.TestCase):
    def test_yoc_and_required_growth(self):
        # assert: DPS_10 = 1*(1.07)^10, yoc at cost 20; required growth to 7% = (0.07*20/1)^(1/10)-1
        costs = [{"cost": 20.0, "label": "x"}]
        rows = fs.yoc_table(1.0, {"bad": 0.03, "mid": 0.07, "good": None}, costs, [10])
        mid = next(r for r in rows if r["scenario"] == "mid")
        self.assertAlmostEqual(mid["dps"], 1.07 ** 10)
        self.assertAlmostEqual(mid["yoc"][0], 1.07 ** 10 / 20 * 100)
        good = next(r for r in rows if r["scenario"] == "good")
        self.assertIsNone(good["dps"])
        req = fs.required_growth(1.0, costs, [7, 12], [10])[0]["growth"]
        self.assertAlmostEqual(req[0], 1.4 ** 0.1 - 1)
        self.assertAlmostEqual(req[1], 2.4 ** 0.1 - 1)

    def test_cost_levels(self):
        # assert: supplied + price + price x0.8 x0.6; a duplicate cost (24 == 30 x 0.8) is dropped
        lv = fs.cost_levels(30.0, [24.0], [0.8, 0.6])
        self.assertEqual([round(c["cost"], 2) for c in lv], [24.0, 30.0, 18.0])


class PriceLabelTest(unittest.TestCase):
    H = [{"yield": float(y)} for y in range(2, 10)]  # 2..9

    def test_three_labels_and_insufficient(self):
        # assert: top 25% of own yields = ถูก · bottom 25% = แพง · middle = กลาง · <5 yrs / no value = ข้อมูลไม่พอ
        self.assertEqual(fs.price_label(9.5, self.H, CFG)["label"], "ถูกเทียบตัวเอง")
        self.assertEqual(fs.price_label(1.0, self.H, CFG)["label"], "แพงเทียบตัวเอง")
        self.assertEqual(fs.price_label(5.5, self.H, CFG)["label"], "กลางเทียบตัวเอง")
        self.assertEqual(fs.price_label(5.5, self.H[:4], CFG)["label"], "ข้อมูลไม่พอ")
        self.assertEqual(fs.price_label(None, self.H, CFG)["label"], "ข้อมูลไม่พอ")


class FlagTest(unittest.TestCase):
    def _t1(self, d):
        return fs.flag_t1(d, fs.dividend_cuts(d, 10), 2)

    def test_t1(self):
        # assert: two adjacent cuts ending at last FY = ติด · one cut = ไม่ติด · cut then rise = ไม่ติด · empty = None
        self.assertTrue(self._t1({2022: 1.0, 2023: 0.8, 2024: 0.6})["triggered"])
        self.assertFalse(self._t1({2023: 1.0, 2024: 0.8})["triggered"])
        self.assertFalse(self._t1({2022: 1.0, 2023: 0.8, 2024: 0.9})["triggered"])
        self.assertIsNone(self._t1({})["triggered"])
        self.assertIn("-20%", self._t1({2023: 1.0, 2024: 0.8})["detail"])

    def test_t2(self):
        # assert: mid 3%, base 1.0 -> year-10 DPS 1.344: at cost 20 = 6.7% (<7 ติด), cost 10 = 13.4% (ไม่ติด), mid None -> None
        lv = lambda c: [{"cost": c, "label": "ต้นทุนที่ส่งมา"}]
        self.assertTrue(fs.flag_t2(1.0, {"mid": 0.03}, lv(20), 10, 7)["triggered"])
        self.assertFalse(fs.flag_t2(1.0, {"mid": 0.03}, lv(10), 10, 7)["triggered"])
        self.assertIsNone(fs.flag_t2(1.0, {"mid": None}, lv(20), 10, 7)["triggered"])
        self.assertIn("6.7%", fs.flag_t2(1.0, {"mid": 0.03}, lv(20), 10, 7)["detail"])

    def test_t4(self):
        # assert: free < paid in 2 adjacent latest years = ติด · one bad year = ไม่ติด · non-adjacent/short = None
        row = lambda y, f, p: {"year": y, "free": f, "paid": p}
        self.assertTrue(fs.flag_t4([row(2023, 5, 1), row(2024, -1, 2), row(2025, 1, 2)], 2)["triggered"])
        self.assertFalse(fs.flag_t4([row(2024, 5, 1), row(2025, 1, 2)], 2)["triggered"])
        self.assertIsNone(fs.flag_t4([row(2022, 1, 2), row(2025, 1, 2)], 2)["triggered"])
        self.assertIsNone(fs.flag_t4([row(2025, 1, 2)], 2)["triggered"])

    def test_t6(self):
        # assert: liab/equity rose 3 steps in a row = ติด · a dip = ไม่ติด · fewer than 4 points = None
        mk = lambda vals: [{"year": 2020 + i, "liab_to_equity": v} for i, v in enumerate(vals)]
        self.assertTrue(fs.flag_t6(mk([1.0, 1.1, 1.2, 1.3]), 3)["triggered"])
        self.assertFalse(fs.flag_t6(mk([1.0, 1.1, 1.05, 1.3]), 3)["triggered"])
        self.assertIsNone(fs.flag_t6(mk([1.0, 1.1, 1.2]), 3)["triggered"])

    def test_payout_and_loss(self):
        # assert: payout 120% over limit 100% = ติด · eps<=0 year listed as loss year
        self.assertTrue(fs.flag_payout([{"year": 2024, "dps": 1.2, "eps": 1.0, "payout": 1.2}], 1.0)["triggered"])
        self.assertFalse(fs.flag_payout([{"year": 2024, "dps": 0.5, "eps": 1.0, "payout": 0.5}], 1.0)["triggered"])
        rows = [{"year": 2023, "eps": -0.5, "net_income": -1}, {"year": 2024, "eps": 1.0, "net_income": 1}]
        self.assertEqual(fs.loss_years(rows, 10), [2023])
        self.assertTrue(fs.flag_loss([2023], 10)["triggered"])


class ComputeAndRenderTest(unittest.TestCase):
    def test_general_has_a7_and_t4(self):
        # assert: general company computes cash table (OCF-invest, 400m) and carries a T4 flag
        out = fs.compute_fact_sheet(make_data(), costs=[40.0], cfg=CFG, today="2026-10-09")
        self.assertIsNotNone(out["cash"])
        self.assertAlmostEqual(out["cash"][-1]["free"], 400e6)
        self.assertIn("T4", [f["code"] for f in out["flags"]])
        self.assertEqual(out["costs"][0]["cost"], 40.0)

    def test_bank_skips_a7_and_t4(self):
        # assert: bank -> no cash table, no T4 flag, rendered A7 says not printed and OCF column absent
        out = fs.compute_fact_sheet(make_data("bank"), cfg=CFG, today="2026-10-09")
        self.assertIsNone(out["cash"])
        self.assertNotIn("T4", [f["code"] for f in out["flags"]])
        md = fs.render_markdown(out)
        self.assertIn("ไม่พิมพ์สำหรับแบงก์", md)
        self.assertNotIn("เงินสดจากดำเนินงาน |", md)
        general = fs.render_markdown(fs.compute_fact_sheet(make_data(), cfg=CFG, today="2026-10-09"))
        self.assertIn("เงินสดจากดำเนินงาน |", general)

    def test_t6_end_to_end(self):
        # assert: liabilities rising 0.2 per year over 10 yrs -> T6 flag triggered in the assembled sheet
        out = fs.compute_fact_sheet(make_data(liab_step=0.2), cfg=CFG, today="2026-10-09")
        self.assertTrue(next(f for f in out["flags"] if f["code"] == "T6")["triggered"])

    def test_short_data_says_no_data_and_does_not_crash(self):
        # assert: 2 yrs of data, no closes -> render ok, contains ไม่มีข้อมูล, price label ข้อมูลไม่พอ, no scenario rate
        d = make_data(dps={2023: 1.0, 2024: 1.2}, n_years=2)
        out = fs.compute_fact_sheet(d, cfg=CFG, today="2026-10-09")
        md = fs.render_markdown(out)
        self.assertIn(fs.NA, md)
        self.assertEqual(out["price_label"]["label"], "ข้อมูลไม่พอ")
        self.assertIsNone(out["rates"]["mid"])
        self.assertIsNone(out["cagrs"][5])

    def test_empty_data(self):
        # assert: no dividends / no statements -> no crash, base dps None
        out = fs.compute_fact_sheet({"symbol": "E.BK", "price": 10.0}, cfg=CFG, today="2026-10-09")
        self.assertIsNone(out["dividends"]["base_dps"])
        self.assertIn(fs.NA, fs.render_markdown(out))

    def test_no_verdict_words_and_deterministic(self):
        # assert: no buy/sell/score wording as a verdict; two renders of the same input are identical
        out = fs.compute_fact_sheet(make_data(), costs=[40.0], cfg=CFG, closes={y: 30.0 + y - 2015 for y in range(2015, 2025)}, today="2026-10-09")
        a, b = fs.render_markdown(out), fs.render_markdown(out)
        self.assertEqual(a, b)
        for word in ("ควรซื้อ", "ควรขาย", "คะแนนรวม:", "อันดับที่"):
            self.assertNotIn(word, a)

    def test_stale_price_warned(self):
        # assert: price from 44 days before today -> sheet says ราคาเก่า
        d = make_data()
        d["price_as_of"] = "2026-08-26"
        md = fs.render_markdown(fs.compute_fact_sheet(d, cfg=CFG, today="2026-10-09"))
        self.assertIn("ราคาเก่า 44 วัน", md)

    def test_cash_vs_dividend_uses_reported_when_present(self):
        # assert: reported dividends_paid wins over DPS x shares estimate; estimate labelled ประมาณ
        rows = [{"year": 2024, "ocf": 500.0, "invest": 100.0, "dividends_paid": -50.0},
                {"year": 2023, "ocf": 500.0, "invest": 100.0, "dividends_paid": None}]
        c = {r["year"]: r for r in fs.cash_vs_dividend(rows, {2023: 2.0, 2024: 2.0}, 10)}
        self.assertEqual(c[2024]["paid"], 50.0)
        self.assertAlmostEqual(c[2024]["times"], 8.0)
        self.assertEqual(c[2023]["paid"], 20.0)
        self.assertIn("ประมาณ", c[2023]["paid_source"])

    def test_price_history_rules(self):
        # assert: PE only when EPS>0, yield = FY DPS / year-end close
        rows = [{"year": 2023, "eps": -1.0, "bvps": 10.0}, {"year": 2024, "eps": 2.0, "bvps": 10.0}]
        h = fs.price_history(rows, {2023: 1.0, 2024: 1.0}, {2023: 20.0, 2024: 25.0})
        self.assertIsNone(h[0]["pe"])
        self.assertAlmostEqual(h[1]["pe"], 12.5)
        self.assertAlmostEqual(h[1]["yield"], 4.0)
        self.assertAlmostEqual(h[1]["pbv"], 2.5)


class YieldVsNiwesLineTest(unittest.TestCase):
    def test_line_says_below_or_reaches_bar(self):
        # assert: yield 3.6% vs bar 5 -> "ต่ำกว่า" · 5.0% -> "ถึง" · None -> ไม่มีข้อมูล (label alone must not read as passing the bar)
        self.assertIn("ต่ำกว่า เกณฑ์ 5% ของนิเวศน์", fs.yield_vs_niwes_line(3.6, 5))
        self.assertIn("yield วันนี้ 5.0% ถึง เกณฑ์ 5%", fs.yield_vs_niwes_line(5.0, 5))
        self.assertIn(fs.NA, fs.yield_vs_niwes_line(None, 5))


if __name__ == "__main__":
    unittest.main()
