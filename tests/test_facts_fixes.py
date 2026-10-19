"""job-10: ปันผลพิเศษ · อัตราโตจาก deep dive · หนี้ผิดปกติ/แบงก์ · ขอบเขตประวัติปันผล — fixtures only, no network."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import fact_sheet as fs  # noqa: E402
import fetch_data as fd  # noqa: E402
import holdings_watch as hw  # noqa: E402
from tests.test_fact_sheet import make_data, CFG  # noqa: E402

# DPS ปกติโตทุกปี + พิเศษ 4.0 ใน 2019 (เหมือน TCAP: รวม 2019 = 7.0 แล้วปีถัดไปดูเหมือน "ลด")
REG = {2015: 1.8, 2016: 2.0, 2017: 2.2, 2018: 2.6, 2019: 3.0, 2020: 3.0, 2021: 3.0, 2022: 3.1, 2023: 3.2, 2024: 3.3}


class SpecialDividendTest(unittest.TestCase):
    def test_split_removes_special_and_caps_at_total(self):
        # assert: 7.0 total - 4.0 special = 3.0 regular, removed=4.0 · special bigger than the year is capped (never negative)
        reg, rem = fd.split_special_dividends({2019: 7.0, 2020: 3.0, "2021": 1.0}, {2019: 4.0, 2021: 5.0})
        self.assertEqual(reg[2019], 3.0)
        self.assertEqual(rem[2019], 4.0)
        self.assertEqual(reg["2021"], 0.0)
        self.assertEqual(rem[2021], 1.0)
        self.assertEqual(reg[2020], 3.0)

    def test_special_dividends_for_reads_config(self):
        # assert: config {"TCAP": {"2019": 4.0}} -> {2019: 4.0}; .BK suffix ok; other symbol / missing file -> {}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "c.json"
            p.write_text(json.dumps({"special_dividends": {"TCAP": {"2019": 4.0}}}), encoding="utf-8")
            self.assertEqual(fd.special_dividends_for("TCAP.BK", p), {2019: 4.0})
            self.assertEqual(fd.special_dividends_for("BBL", p), {})
            self.assertEqual(fd.special_dividends_for("TCAP", Path(d) / "nope.json"), {})

    def test_real_config_has_tcap_2019(self):
        # assert: ค่าเริ่มใน config.json = TCAP FY2019 4.0 ตาม deep dive ข้อ 2.1
        self.assertEqual(fd.special_dividends_for("TCAP"), {2019: 4.0})

    def test_cuts_and_t1_use_regular_only_and_sheet_prints_both_columns(self):
        # assert: total 7.0 in 2019 looks like a cut in 2020 (cut_count >= 1); after the split regular has 0 cuts,
        #         T1 not triggered, sheet prints ปกติ / พิเศษ / รวม columns with 4 and 7
        total = dict(REG)
        total[2019] = 7.0
        d_total = make_data(dps=total)
        self.assertGreaterEqual(fs.compute_fact_sheet(d_total, cfg=CFG, today="2026-10-09")["cut_count"], 1)
        reg, rem = fd.split_special_dividends(total, {2019: 4.0})
        d = make_data(dps=reg)
        d["dividend_history_special"] = rem
        out = fs.compute_fact_sheet(d, cfg=CFG, today="2026-10-09")
        self.assertEqual(out["cut_count"], 0)
        self.assertFalse(next(f for f in out["flags"] if f["code"] == "T1")["triggered"])
        md = fs.render_markdown(out)
        self.assertIn("ปันผลพิเศษ (บาท)", md)
        self.assertIn("4.0000", md)
        self.assertIn("7.0000", md)


class GrowthOverrideTest(unittest.TestCase):
    OV = {"bad": 0.03, "mid": 0.07, "good": 0.11, "source": "research/x.md ท่อน 4.1", "as_of": "2026-10-09"}

    def test_override_is_main_table_with_label_and_fixed_line(self):
        # assert: rates = 3/7/11 · rates_fixed kept · A4 has the deep dive label + source + fixed-rule comparison line
        out = fs.compute_fact_sheet(make_data(), cfg=CFG, today="2026-10-09", growth_override=self.OV)
        self.assertEqual(out["rates"], {"bad": 0.03, "mid": 0.07, "good": 0.11})
        self.assertNotEqual(out["rates_fixed"], out["rates"])
        md = fs.render_markdown(out)
        self.assertIn("อัตราโตจาก deep dive 2026-10-09 — สมมติฐานของคน รอ Art เคาะ", md)
        self.assertIn("เทียบกฎตายตัว:", md)
        self.assertIn("research/x.md ท่อน 4.1", md)
        rule_line = next(l for l in md.splitlines() if l.startswith("- กลาง = ค่าเฉลี่ย"))
        self.assertNotIn("7.0%", rule_line)   # rule bullets show the fixed rate, not the override
        mid10 = next(r for r in out["yoc"] if r["scenario"] == "mid" and r["year"] == 10)
        base = out["dividends"]["base_dps"]
        self.assertAlmostEqual(mid10["dps"], base * 1.07 ** 10)

    def test_without_override_or_incomplete_override_uses_fixed_rule(self):
        # assert: no override / missing 'good' -> same as before (rates == rates_fixed, no deep dive label)
        for ov in (None, {"bad": 0.03, "mid": 0.07}):
            out = fs.compute_fact_sheet(make_data(), cfg=CFG, today="2026-10-09", growth_override=ov)
            self.assertEqual(out["rates"], out["rates_fixed"])
            self.assertEqual(out["rates_source"]["kind"], "fixed")
            self.assertNotIn("deep dive", fs.render_markdown(out))

    def test_t2_uses_override_mid(self):
        # assert: T2 detail quotes the override mid 7.0%/yr
        out = fs.compute_fact_sheet(make_data(), costs=[40.0], cfg=CFG, today="2026-10-09", growth_override=self.OV)
        self.assertIn("โต 7.0%/ปี", next(f for f in out["flags"] if f["code"] == "T2")["detail"])

    def test_real_config_has_amata_with_source(self):
        # assert: config AMATA 3/7/11 + source + as_of
        g = hw.load_holdings_cfg()["growth_scenarios"]
        self.assertEqual((g["AMATA"]["bad"], g["AMATA"]["mid"], g["AMATA"]["good"]), (0.03, 0.07, 0.11))
        self.assertIn("amata-deep-dive", g["AMATA"]["source"])
        self.assertEqual(g["AMATA"]["as_of"], "2026-10-09")

    def test_watch_report_names_rates_used_per_stock(self):
        # assert: roll-up lists the deep dive stock with the label and fixed rates; fixed stock says กฎตายตัว
        rows = [{"symbol": "AAA", "error": None, "leg": hw.LEG_NIWES, "scenario_ok": True,
                 "rates": {"bad": 0.03, "mid": 0.07, "good": 0.11}, "rates_fixed": {"bad": 0.0, "mid": 0.04, "good": 0.08},
                 "rates_source": {"kind": "deep_dive", "as_of": "2026-10-09", "source": "s.md"}},
                {"symbol": "BBB", "error": None, "leg": hw.LEG_NIWES, "scenario_ok": True,
                 "rates": {"bad": 0.0, "mid": 0.02, "good": 0.04}, "rates_fixed": {"bad": 0.0, "mid": 0.02, "good": 0.04},
                 "rates_source": {"kind": "fixed"}}]
        txt = "\n".join(hw.rates_used_lines(rows))
        self.assertIn("AAA: **deep dive 2026-10-09**", txt)
        self.assertIn("BBB: กฎตายตัว", txt)


class DebtTest(unittest.TestCase):
    def _row(self, y, liab, ta, eq):
        return {"year": y, "liabilities": liab, "total_assets": ta, "equity": eq}

    def test_suspect_years_bbl_like(self):
        # assert: BBL-like cache where 2019-2021 total liabilities sit at ~1/10 of assets-equity
        #         -> exactly those 3 years suspect from the balance-sheet identity, neighbours (consistent) not
        def cons(y, liab, ta):
            return self._row(y, liab, ta, ta - liab)
        rows = [cons(2015, 2.4e12, 4.6e12), cons(2016, 2.5e12, 4.7e12), cons(2017, 2.6e12, 4.8e12), cons(2018, 2.7e12, 4.9e12)]
        rows += [self._row(2019, 2.81e11, 3.87e12, 1.08e12),  # assets-equity = 2.79e12
                 self._row(2020, 3.31e11, 4.2e12, 1.2e12),     # assets-equity = 3.0e12
                 self._row(2021, 4.26e11, 4.4e12, 1.1e12)]     # assets-equity = 3.3e12
        rows += [cons(2022, 3.9e12, 5.6e12), cons(2023, 4.0e12, 5.7e12), cons(2024, 4.0e12, 5.7e12)]
        self.assertEqual(fs.suspect_liability_years(rows, 0.10), {2019, 2020, 2021})

    def test_normal_growth_not_suspect(self):
        # assert: a real drop in liabilities (TCAP-like) that still matches assets-equity is NOT suspect:
        #         2018 liab 9.23e11 vs assets-equity 9.2e11 (~0.3% gap), 2019 liab 8.7e10 vs assets-equity 9.5e10 (8.4% gap)
        rows = [self._row(2016, 1.0e12, 4.0e12, 3.0e12),
                self._row(2017, 9.6e11, 3.99e12, 3.03e12),
                self._row(2018, 9.23e11, 3.8e12, 2.88e12),   # assets-equity = 9.2e11
                self._row(2019, 8.7e10, 9.4e11, 8.45e11)]    # assets-equity = 9.5e10
        self.assertEqual(fs.suspect_liability_years(rows, 0.10), set())

    def test_general_stock_shows_text_instead_of_number_and_skips_t6(self):
        # assert: a bad year prints ข้อมูลปีนี้น่าสงสัย and is the only year marked suspect
        d = make_data()
        d["yearly_metrics"][5]["total_debt"] = 1e6   # 1000x below neighbours
        d["yearly_metrics"][5]["total_assets"] = 3000e6  # contradict liabilities (assets-equity 2e9 vs 1e6)
        out = fs.compute_fact_sheet(d, cfg=CFG, today="2026-10-09")
        bad = [x for x in out["debt"] if x["suspect"]]
        self.assertEqual([x["year"] for x in bad], [int(d["yearly_metrics"][5]["year"])])
        self.assertIn("ข้อมูลปีนี้น่าสงสัย", fs.render_markdown(out))

    def test_bank_has_no_debt_table_and_no_t6(self):
        # assert: bank sheet: no T6 flag, A6 says why in one line, no 'หนี้สินรวม/ทุน' table header
        out = fs.compute_fact_sheet(make_data("bank", liab_step=0.2), cfg=CFG, today="2026-10-09")
        self.assertNotIn("T6", [f["code"] for f in out["flags"]])
        md = fs.render_markdown(out)
        self.assertIn("ไม่พิมพ์ตารางหนี้ต่อทุนสำหรับแบงก์", md)
        self.assertNotIn("หนี้สินรวม/ทุน", md)


class HistoryScopeTest(unittest.TestCase):
    def test_line_under_dividend_table(self):
        # assert: earliest FY in the table is announced as the data start
        dps = {y: 1.0 for y in range(2004, 2025)}
        md = fs.render_markdown(fs.compute_fact_sheet(make_data(dps=dps), cfg=CFG, today="2026-10-09"))
        self.assertIn("ระบบมีข้อมูลตั้งแต่ปี 2004 — เหตุการณ์ก่อนหน้านั้นไม่อยู่ในตาราง", md)


class NormalEpsTest(unittest.TestCase):
    def test_normal_eps_for_reads_config(self):
        # assert: config {"normal_eps": {"AMATA": {"2025": 2.1, "_source": "x"}}} -> {2025: 2.1};
        #         other symbol / missing file -> {}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "c.json"
            p.write_text(json.dumps({"normal_eps": {"AMATA": {"2025": 2.1, "_source": "x"}}}), encoding="utf-8")
            self.assertEqual(fd.normal_eps_for("AMATA", p), {2025: 2.1})
            self.assertEqual(fd.normal_eps_for("BBL", p), {})
            self.assertEqual(fd.normal_eps_for("AMATA", Path(d) / "nope.json"), {})

    def test_apply_normal_eps_overlays_and_keeps_total(self):
        # assert: rows [{"year":"2024","diluted_eps":1.0}, {"year":"2025","diluted_eps":3.0}] with normal {2025:-0.5}
        #         -> 2025 row diluted_eps == -0.5 and diluted_eps_total == 3.0; 2024 row untouched (no diluted_eps_total)
        rows = [{"year": "2024", "diluted_eps": 1.0}, {"year": "2025", "diluted_eps": 3.0}]
        fd.apply_normal_eps(rows, {2025: -0.5})
        self.assertEqual(rows[0], {"year": "2024", "diluted_eps": 1.0})
        self.assertEqual(rows[1]["diluted_eps"], -0.5)
        self.assertEqual(rows[1]["diluted_eps_total"], 3.0)

    def test_cache_not_reused_when_normal_eps_differs(self):
        # assert: cached dict whose normal_eps_applied differs from config is not reused -> fresh fetch returned
        cached = {"symbol": "AMATA", "price": 10.0, "normal_eps_applied": {2025: 9.9}}
        fresh = {"symbol": "AMATA", "price": 10.0, "normal_eps_applied": {2025: 2.1}}
        with mock.patch.object(fd, "_load_from_cache", return_value=cached), \
             mock.patch.object(fd, "normal_eps_for", return_value={2025: 2.1}), \
             mock.patch.object(fd, "fetch_multi_year", return_value=dict(fresh)), \
             mock.patch.object(fd, "_save_to_cache"):
            out = fd.fetch_multi_year_safe("AMATA")
        self.assertEqual(out, fresh)
        self.assertNotEqual(out.get("normal_eps_applied"), cached["normal_eps_applied"])


if __name__ == "__main__":
    unittest.main()
