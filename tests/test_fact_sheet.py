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
        # assert: bad = min window (0..cap) - good = max window capped - mid = mean
        r = fs.growth_scenarios({5: 0.30, 10: 0.09, 15: 0.04, 20: None}, 0.10)
        self.assertAlmostEqual(r["bad"], 0.04)
        self.assertAlmostEqual(r["good"], 0.10)
        self.assertAlmostEqual(r["mid"], 0.07)
        r = fs.growth_scenarios({5: 0.02, 10: -0.03}, 0.10)
        self.assertEqual(r["bad"], 0.0)
        self.assertAlmostEqual(r["good"], 0.02)

    def test_scenario_order_always_holds(self):
        # assert: SISB-like (huge 5y window) and negative / mixed windows keep bad <= mid <= good
        for cagrs in ({5: 0.463, 10: 0.20}, {5: 0.463, 10: 0.30, 15: 0.5}, {5: -0.2, 10: -0.1}, {5: 0.5, 10: 0.0, 20: 0.02},
                      {10: 0.05}, {5: 0.12, 10: 0.12}):
            r = fs.growth_scenarios(cagrs, 0.10)
            self.assertLessEqual(r["bad"], r["mid"])
            self.assertLessEqual(r["mid"], r["good"])

    def test_cap_applies_to_every_scenario(self):
        # assert: all windows above the cap -> bad = mid = good = cap (cap is not only for good)
        r = fs.growth_scenarios({5: 0.463, 10: 0.25}, 0.10)
        self.assertEqual((r["bad"], r["mid"], r["good"]), (0.10, 0.10, 0.10))

    def test_history_under_min_window_is_insufficient(self):
        # assert: no window >= 10y -> all None; T2 flag None; yoc rows have no DPS; render says ข้อมูลไม่พอ; required-growth table still printed
        r = fs.growth_scenarios({5: 0.20, 10: None, 15: None}, 0.10)
        self.assertEqual(r, {"bad": None, "mid": None, "good": None})
        self.assertIsNone(fs.flag_t2(1.0, r, [{"cost": 20, "label": "x"}], 10, 7)["triggered"])
        d = make_data(dps={y: 1.0 + 0.1 * (y - 2018) for y in range(2018, 2025)}, n_years=7)
        out = fs.compute_fact_sheet(d, cfg=CFG, today="2026-10-09")
        self.assertIsNone(out["rates"]["mid"])
        self.assertTrue(all(x["dps"] is None for x in out["yoc"]))
        self.assertIn(fs.INSUFFICIENT, fs.render_markdown(out))
        self.assertTrue(out["required"])


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


class DcaTest(unittest.TestCase):
    G, F = fs.PRICE_GROWS, fs.PRICE_FLAT

    def test_zero_growth_both_cases_equal_today_yield(self):
        # assert: dps 1.00 price 20 (yield 5%) growth 0% -> both price cases 5.0% in years 5 / 10 / 15
        for n in (5, 10, 15):
            for m in (self.G, self.F):
                self.assertAlmostEqual(fs.dca_yoc(1.0, 20.0, 0.0, n, 10, m), 5.0)

    def test_flat_price_beats_growing_price_and_both_within_lump_sum(self):
        # assert: g>0 -> flat >= grows, both <= lump sum at cost = today's price (dps_N / price), every year
        for g in (0.02, 0.05, 0.10):
            for n in (5, 10, 15):
                lump = 1.0 * (1 + g) ** n / 20.0 * 100
                a, b = fs.dca_yoc(1.0, 20.0, g, n, 10, self.G), fs.dca_yoc(1.0, 20.0, g, n, 10, self.F)
                self.assertGreater(b, a)
                self.assertLessEqual(a, lump + 1e-9)
                self.assertLessEqual(b, lump + 1e-9)

    def test_year15_not_below_year10_when_growth_nonnegative(self):
        # assert: g >= 0 -> year 15 >= year 10 in both cases (buying stops after year 10)
        for g in (0.0, 0.03, 0.10):
            for m in (self.G, self.F):
                self.assertGreaterEqual(fs.dca_yoc(1.0, 20.0, g, 15, 10, m) + 1e-9, fs.dca_yoc(1.0, 20.0, g, 10, 10, m))

    def test_hand_calculated_monthly_case(self):
        # assert: dps 1.00 price 20 g=100%, buy 1 year (12 months), year 1, price grows with dividend.
        # By hand: month k price = 20 x 2^(k/12) -> shares per money unit = 2^(-k/12)/20; mean over k=0..11 of 2^(-k/12)
        # = (1-0.5)/(1-2^(-1/12))/12 = 0.74238; DPS_1 = 1 x 2 = 2.00; yoc = 2.00 x 0.74238 / 20 x 100 = 7.42%
        self.assertAlmostEqual(fs.dca_yoc(1.0, 20.0, 1.0, 1, 1, self.G), 7.42, places=2)
        self.assertAlmostEqual(fs.dca_yoc(1.0, 20.0, 1.0, 1, 1, self.F), 10.0, places=2)  # flat: 2.00 / 20

    def test_insufficient_data_is_none(self):
        # assert: no growth scenario / no dps / no price -> None, never a number
        self.assertIsNone(fs.dca_yoc(1.0, 20.0, None, 10, 10, self.G))
        self.assertIsNone(fs.dca_yoc(None, 20.0, 0.05, 10, 10, self.G))
        self.assertIsNone(fs.dca_yoc(1.0, None, 0.05, 10, 10, self.F))
        self.assertIsNone(fs.dca_required_yield(None, 7, 10))

    def test_required_yield_formula(self):
        # assert: target 7%, g 5%, year 10 -> 7 / 1.05^10 = 4.30
        self.assertAlmostEqual(fs.dca_required_yield(0.05, 7, 10), 4.297, places=2)

    def test_sheet_without_scenarios_says_insufficient(self):
        # assert: history < 10y -> DCA section is ข้อมูลไม่พอ (no table) ; with scenarios the section and heading render
        short = fs.compute_fact_sheet(make_data(dps={2023: 1.0, 2024: 1.1}), cfg=CFG, today="2026-10-09")
        self.assertFalse(any(x["ok"] for x in short["dca"]))
        self.assertIn("ถ้าซื้อทุกเดือน (DCA)", fs.render_markdown(short))
        full = fs.compute_fact_sheet(make_data(), cfg=CFG, today="2026-10-09")
        md = fs.render_markdown(full)
        self.assertTrue(all(x["ok"] for x in full["dca"]))
        self.assertIn("ราคาโตเท่าปันผล", md)
        self.assertIn("ก้อนที่ถืออยู่ (ต้นทุนคงที่)", md)
        self.assertEqual(md, fs.render_markdown(full))


class YieldVsNiwesLineTest(unittest.TestCase):
    def test_line_says_below_or_reaches_bar(self):
        # assert: yield 3.6% vs bar 5 -> "ต่ำกว่า" · 5.0% -> "ถึง" · None -> ไม่มีข้อมูล (label alone must not read as passing the bar)
        self.assertIn("ต่ำกว่า เกณฑ์ 5% ของนิเวศน์", fs.yield_vs_niwes_line(3.6, 5))
        self.assertIn("yield วันนี้ 5.0% ถึง เกณฑ์ 5%", fs.yield_vs_niwes_line(5.0, 5))
        self.assertIn(fs.NA, fs.yield_vs_niwes_line(None, 5))


class WrapUpFixesTest(unittest.TestCase):
    def test_a7_prefers_cash_flow_dividends_over_estimate(self):
        # assert: dividends_paid from the cash flow replaces DPS x shares for its year (1,000 not 1.0 x 100 shares), labelled
        # งบกระแสเงินสด; a year without it stays ประมาณ; A7 text says which years used which way
        d = make_data()
        out = fs.compute_fact_sheet(d, cfg=CFG, today="2026-10-09", dividends_paid={2024: 1000.0})
        c = {x["year"]: x for x in out["cash"]}
        self.assertEqual(c[2024]["paid"], 1000.0)
        self.assertIn("งบกระแสเงินสด", c[2024]["paid_source"])
        self.assertIn("ประมาณ", c[2023]["paid_source"])
        md = fs.render_markdown(out)
        self.assertIn("ปีที่ใช้เงินปันผลจ่ายจริงจากงบกระแสเงินสด = 2024", md)

    def test_a6_uses_yahoo_liabilities_when_cache_is_off_by_more_than_gap(self):
        # assert: cache liabilities 1000 vs yahoo 800 (25% apart) -> row uses 800, source yahoo, ratio 0.8, cache value kept
        # and the sheet prints the replacement; 1000 vs 950 (5%) keeps the cache value
        d = make_data(n_years=3)
        ib = {2024: {"total_debt": 300e6, "equity": 1000e6, "lease": None, "liabilities": 800e6},
              2023: {"total_debt": 300e6, "equity": 1000e6, "lease": None, "liabilities": 950e6}}
        out = fs.compute_fact_sheet(d, cfg=CFG, today="2026-10-09", interest_bearing=ib)
        r = {x["year"]: x for x in out["debt"]}
        self.assertEqual(r[2024]["liabilities"], 800e6)
        self.assertEqual(r[2024]["liab_source"], "yahoo")
        self.assertEqual(r[2024]["liab_cache"], 1000e6)
        self.assertAlmostEqual(r[2024]["liab_to_equity"], 0.8)
        self.assertEqual(r[2023]["liab_source"], "cache")
        self.assertIn("ใช้หนี้สินรวมจาก yahoo", fs.render_markdown(out))

    def test_a6_lease_line_when_known_and_note_when_not(self):
        # assert: lease 400 of interest-bearing 500 -> separate line with 80% and the "ส่วนใหญ่คือหนี้เช่า" remark;
        # no lease data -> the fixed note about lease + trade payables under the debt table
        d = make_data(n_years=2)
        with_lease = {2024: {"total_debt": 500e6, "equity": 1000e6, "lease": 400e6, "liabilities": 1000e6}}
        md = fs.render_markdown(fs.compute_fact_sheet(d, cfg=CFG, today="2026-10-09", interest_bearing=with_lease))
        self.assertIn("แยกหนี้เช่า ปี 2024", md)
        self.assertIn("= 80% ของหนี้มีดอกเบี้ย", md)
        self.assertIn("ส่วนใหญ่คือหนี้เช่า", md)
        self.assertNotIn("หนี้สินรวมนับรวมหนี้สินตามสัญญาเช่า", md)
        md2 = fs.render_markdown(fs.compute_fact_sheet(d, cfg=CFG, today="2026-10-09"))
        self.assertIn("หนี้สินรวมนับรวมหนี้สินตามสัญญาเช่าและเจ้าหนี้การค้า — ธง T6 ติดไม่ได้แปลว่ากู้เพิ่ม", md2)


class AvgYieldTest(unittest.TestCase):
    def test_last_three_years_mean_dps_over_price(self):
        # assert: mean of last 3 complete FYs (0.65+0.80+1.10)/3 = 0.85 / price 31.75 * 100 ≈ 2.68%
        # (job brief said "≈ 2.73" — arithmetic slip; the true value is 2.677)
        self.assertAlmostEqual(fs.avg_yield({2023: 0.65, 2024: 0.80, 2025: 1.10}, 31.75, 3), 2.68, places=2)

    def test_fewer_complete_fys_than_years_is_none(self):
        # assert: only 2 complete FYs but years=3 -> not enough history -> None
        self.assertIsNone(fs.avg_yield({2024: 0.80, 2025: 1.10}, 31.75, 3))

    def test_price_zero_is_none(self):
        # assert: price 0 -> cannot divide -> None
        self.assertIsNone(fs.avg_yield({2023: 0.65, 2024: 0.80, 2025: 1.10}, 0, 3))


if __name__ == "__main__":
    unittest.main()
