"""holdings_watch tests - fake fact sheets, injected builder/refresher. No network, no files read or written."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import fact_sheet as fsmod  # noqa: E402
import holdings_watch as hw  # noqa: E402
import rebalance  # noqa: E402

CFG = dict(fsmod.DEFAULT_CFG)
HCFG = dict(hw.DEFAULT_HOLDINGS)
BANNED = ("ซื้อ", "ขาย", "ควร")


def flag(code, trig):
    return {"code": code, "name": f"ธง {code}", "triggered": trig, "detail": f"รายละเอียด {code}"}


def fake_fs(sym, price=20.0, base=1.0, trig=(), age=1, missing=()):
    """Minimal sheet in the shape build_fact_sheet returns; cost levels = [price]; yoc mid year 10 = dps 2.0 / cost."""
    flags = [flag(c, True if c in trig else (None if c in missing else False)) for c in ("T1", "T2", "T4", "T6")]
    yoc = [{"scenario": k, "year": 10, "yoc": [d / price * 100]} for k, d in (("bad", 1.0), ("mid", 2.0), ("good", 4.0))]
    return {"symbol": sym + ".BK", "price": price, "price_date": "2026-10-08", "price_age_days": age,
            "dividends": {"base_dps": base}, "today": {"yield": base / price * 100},
            "costs": [{"cost": price, "label": "ราคาวันนี้"}], "yoc": yoc,
            "rates": {"bad": 0.0, "mid": 0.05, "good": 0.10},
            "price_label": {"label": "กลางเทียบตัวเอง"}, "gate": {"status": "PASS"}, "flags": flags,
            "date": "2026-10-09", "cfg": CFG}


class EntriesTest(unittest.TestCase):
    def test_plan_plus_off_plan_and_new_target_needs_no_code_change(self):
        # assert: in-plan = TARGETS keys, TISCO off-plan; a fake TARGETS key shows up without touching holdings_watch
        e = hw.holding_entries(HCFG)
        self.assertEqual([x["symbol"] for x in e if x["in_plan"]], list(rebalance.TARGETS))
        self.assertEqual([x["symbol"] for x in e if not x["in_plan"]], ["TISCO"])
        rebalance.TARGETS["ZZZ"] = 1.0
        try:
            self.assertIn("ZZZ", [x["symbol"] for x in hw.holding_entries(HCFG) if x["in_plan"]])
        finally:
            del rebalance.TARGETS["ZZZ"]

    def test_off_plan_dup_with_plan_not_repeated(self):
        # assert: off_plan listing a plan stock does not duplicate it
        e = hw.holding_entries({"off_plan": ["amata", "TISCO"]})
        self.assertEqual([x["symbol"] for x in e].count("AMATA"), 1)


class CostTest(unittest.TestCase):
    def test_config_cost_overridden_by_cli(self):
        # assert: config 0 = not entered; config value used; --cost wins over config; last --cost wins
        c = hw.resolve_costs({"AMATA": 0, "BBL": 150}, {"AMATA": [27.5], "BBL": [160, 170]})
        self.assertEqual(c, {"AMATA": 27.5, "BBL": 170.0})
        self.assertEqual(hw.resolve_costs({"BBL": 150}, {}), {"BBL": 150.0})
        self.assertEqual(hw.resolve_costs({"AMATA": 0}, {}), {})


class StatusTest(unittest.TestCase):
    def test_three_states(self):
        # assert: T1 -> เปิดทบทวน (even with other flags) · other flag only -> เฝ้า · none (or only no-data) -> ปกติ
        self.assertEqual(hw.status_of(fake_fs("A", trig=("T2", "T1"))), hw.REVIEW)
        self.assertEqual(hw.status_of(fake_fs("A", trig=("T6",))), hw.WATCH)
        self.assertEqual(hw.status_of(fake_fs("A", missing=("T4",))), hw.NORMAL)


class SummaryTest(unittest.TestCase):
    ENTRY = {"symbol": "AAA", "in_plan": True, "target": 10.0}

    def test_no_cost_uses_price_and_cost_entered_is_shown(self):
        # assert: no cost -> text says use today's price, yoc_now = base/price; cost given -> shown, yoc_now = base/cost
        r = hw.summarize(self.ENTRY, fake_fs("AAA", price=20, base=1), None, 10)
        self.assertEqual(r["cost_text"], hw.NO_COST_TEXT)
        self.assertAlmostEqual(r["yoc_now"], 5.0)
        self.assertAlmostEqual(r["yoc_scen"]["mid"], 10.0)
        fs = fake_fs("AAA", price=20, base=1)
        fs["costs"] = [{"cost": 10.0, "label": "ต้นทุนที่ส่งมา"}, {"cost": 20.0, "label": "ราคาวันนี้"}]
        for y in fs["yoc"]:
            y["yoc"] = [y["yoc"][0] * 2, y["yoc"][0]]
        r = hw.summarize(self.ENTRY, fs, 10.0, 10)
        self.assertEqual(r["cost_text"], "10")
        self.assertAlmostEqual(r["yoc_now"], 10.0)
        self.assertAlmostEqual(r["yoc_scen"]["mid"], 20.0)

    def test_error_stub_row(self):
        # assert: sheet with error -> row.error set, no status
        r = hw.summarize(self.ENTRY, {"symbol": "AAA.BK", "error": "fetch failed"}, None, 10)
        self.assertEqual(r["error"], "fetch failed")
        self.assertIsNone(r["status"])


class RollupTest(unittest.TestCase):
    def test_weighted_by_target_and_skips_named(self):
        # assert: weights = target share among stocks that have the number; no-data / error stock skipped and named; off-plan ignored
        e = lambda s, w, ip=True: {"symbol": s, "in_plan": ip, "target": w, "leg": "niwes" if ip else None}
        a = hw.summarize(e("A", 30.0), fake_fs("A", price=20, base=1), None, 10)       # now 5%, mid 10%
        b = hw.summarize(e("B", 10.0), fake_fs("B", price=10, base=1), None, 10)       # now 10%, mid 20%
        c = hw.summarize(e("C", 10.0), {"symbol": "C.BK", "error": "x"}, None, 10)
        o = hw.summarize(e("O", None, False), fake_fs("O", price=10, base=3), None, 10)
        roll = hw.portfolio_rollup([a, b, c, o])
        self.assertAlmostEqual(roll["now"]["value"], (30 * 5 + 10 * 10) / 40)
        self.assertAlmostEqual(roll["mid"]["value"], (30 * 10 + 10 * 20) / 40)
        self.assertEqual(roll["now"]["skipped"], ["C"])


    def test_insufficient_scenarios_skipped_in_rollup_and_cell_says_so(self):
        # assert: stock with rates None -> year-10 cells "ข้อมูลไม่พอ"; skipped (named) in the 3 scenario rollups but kept in "วันนี้"; rollup bad<=mid<=good
        e = lambda s, w: {"symbol": s, "in_plan": True, "target": w, "leg": "niwes"}
        a = hw.summarize(e("A", 30.0), fake_fs("A", price=20, base=1), None, 10)
        d = fake_fs("D", price=10, base=1)
        d["rates"] = {"bad": None, "mid": None, "good": None}
        b = hw.summarize(e("D", 10.0), d, None, 10)
        self.assertEqual(hw._scen(b, "mid"), fsmod.INSUFFICIENT)
        roll = hw.portfolio_rollup([a, b])
        self.assertEqual(roll["mid"]["skipped"], ["D"])
        self.assertEqual(roll["now"]["skipped"], [])
        self.assertLessEqual(roll["bad"]["value"], roll["mid"]["value"])
        self.assertLessEqual(roll["mid"]["value"], roll["good"]["value"])


class RunTest(unittest.TestCase):
    NO_CFG = ROOT / "tests" / "_no_such_config.json"  # missing file -> defaults, so real config costs do not leak in

    def setUp(self):
        self.calls = []

    def builder(self, sym, costs):
        self.calls.append((sym, costs))
        if sym == "BBL":
            raise RuntimeError("boom")
        if sym == "TCAP":
            return {"symbol": "TCAP.BK", "error": "fetch failed"}
        return fake_fs(sym, trig=("T1",) if sym == "AMATA" else (), age=30 if sym == "TOA" else 1)

    def test_failure_does_not_sink_report_and_text_is_clean(self):
        # assert: BBL raises + TCAP error stub -> rows say ดึงข้อมูลไม่ได้ + เหตุ, others present; AMATA T1 -> เปิดทบทวน with question;
        #         stale TOA warned on top; TISCO off-plan present; cost passed only to the stock that has one; no ซื้อ/ขาย/ควร anywhere
        text, rows, _, _ = hw.run({"AMATA": [27.5]}, builder=self.builder, today="2026-10-09", cfg_path=self.NO_CFG)
        self.assertEqual(len(rows), len(rebalance.TARGETS) + 1)
        self.assertIn("ดึงข้อมูลไม่ได้", text)
        self.assertIn("RuntimeError: boom", text)
        self.assertIn("fetch failed", text)
        self.assertIn("เปิดทบทวน", text)
        self.assertIn("ชั่วคราวหรือถาวร", text)
        self.assertIn("TISCO | นอกแผน", text)
        self.assertTrue(text.split("\n")[2].startswith("⏳ ราคาเก่าเกิน"))
        self.assertIn("TOA (30 วัน)", text)
        self.assertEqual(dict(self.calls)["AMATA"], [27.5])
        self.assertIsNone(dict(self.calls)["SISB"])
        for w in BANNED:
            self.assertNotIn(w, text)

    def test_same_input_same_text_and_refresh_info_shown(self):
        # assert: two runs without refresh give identical text; refresh adds a line with the refresher's result
        a = hw.run({}, builder=self.builder, today="2026-10-09", cfg_path=self.NO_CFG)[0]
        b = hw.run({}, builder=self.builder, today="2026-10-09", cfg_path=self.NO_CFG)[0]
        self.assertEqual(a, b)
        fake = lambda syms: {s: {"ok": s != "TOA", "date": "2026-10-08", "close": 1.5, "error": None if s != "TOA" else "no data"} for s in syms}
        t = hw.run({}, refresh=True, builder=self.builder, refresher=fake, today="2026-10-09", cfg_path=self.NO_CFG)[0]
        self.assertIn("รีเฟรชราคา:", t)
        self.assertIn("TOA ไม่ได้ (no data)", t)


class RefreshPricesTest(unittest.TestCase):
    def test_writes_refresh_file_not_bulk_and_failure_is_isolated(self):
        # assert: latest row per symbol -> data/setsmart_cache/eod_<date>_refresh.json (never eod_<date>.json); today's screener_cache
        #         entry dropped; a symbol with no rows / raising fetcher -> ok False + reason, others still written (tmp dir, no network)
        import json
        import tempfile
        import data_adapter as da
        rows = {"AAA": [{"date": "2026-10-07", "symbol": "AAA", "close": 10.0}, {"date": "2026-10-08", "symbol": "AAA", "close": 11.0}],
                "BBB": []}

        def fetcher(sym, start, end):
            if sym == "CCC":
                raise RuntimeError("down")
            return rows[sym]

        old, tmp = da.ROOT, tempfile.TemporaryDirectory()
        try:
            da.ROOT = Path(tmp.name)
            day = da.datetime.now().strftime("%Y-%m-%d")
            stale = da.ROOT / "data" / "screener_cache" / day / "AAA.BK.json"
            stale.parent.mkdir(parents=True)
            stale.write_text("{}", encoding="utf-8")
            res = da.refresh_prices(["AAA.BK", "BBB", "CCC"], fetcher=fetcher)
            cache = da.ROOT / "data" / "setsmart_cache"
            self.assertEqual(res["AAA"], {"ok": True, "date": "2026-10-08", "close": 11.0, "error": None})
            self.assertFalse(res["BBB"]["ok"])
            self.assertIn("down", res["CCC"]["error"])
            self.assertEqual([p.name for p in cache.iterdir()], ["eod_2026-10-08_refresh.json"])
            self.assertEqual(json.loads((cache / "eod_2026-10-08_refresh.json").read_text(encoding="utf-8"))[0]["close"], 11.0)
            self.assertFalse(stale.exists())
        finally:
            da.ROOT = old
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main()


class LegTest(unittest.TestCase):
    def test_entries_sorted_by_leg_from_rebalance_legs(self):
        # assert: order niwes -> hong -> off-plan; leg values come from rebalance.LEGS; TISCO has no leg
        e = hw.holding_entries(HCFG)
        self.assertEqual([x["leg"] for x in e], ["niwes"] * 3 + ["hong"] * 4 + [None])
        self.assertEqual([x["symbol"] for x in e if x["leg"] == "hong"], rebalance.LEGS["hong"])

    def test_hong_row_has_no_gate_flags_scenarios_but_keeps_pnl_and_yield(self):
        # assert: hong status text; flags/gate/year-10 cells "—" even when T1 would trigger; pnl vs cost = (20/16-1)=+25.0%
        ent = {"symbol": "TOA", "in_plan": True, "target": 7.5, "leg": "hong"}
        r = hw.summarize(ent, fake_fs("TOA", price=20, base=1, trig=("T1",)), 16.0, 10)
        self.assertEqual(r["status"], hw.HONG_STATUS)
        self.assertEqual(r["flags"], [])
        self.assertAlmostEqual(r["pnl_pct"], 25.0)
        self.assertAlmostEqual(r["yoc_now"], 1 / 16.0 * 100)
        self.assertAlmostEqual(r["yield_today"], 5.0)

    def test_report_hong_rows_dashed_rollup_niwes_only_and_cost_date(self):
        # assert: report says เฉพาะขา Niwes, mentions hong_stage1_scanner + cost date; hong T1 does not create a เปิดทบทวน section
        def builder(sym, costs):
            return fake_fs(sym, trig=("T1",) if sym == "TOA" else ())
        text, rows, _, _ = hw.run({}, builder=builder, today="2026-10-09",
                                  cfg_path=ROOT / "tests" / "_no_such_config.json")
        self.assertIn("เฉพาะขา Niwes", text)
        self.assertIn("hong_stage1_scanner.py", text)
        self.assertNotIn("### TOA", text)
        self.assertEqual([r["leg"] for r in rows if r["in_plan"]], ["niwes"] * 3 + ["hong"] * 4)
        roll = hw.portfolio_rollup(rows)
        self.assertEqual(roll["now"]["skipped"], [])
        # niwes only: 3 stocks, weights 35/22.5/12.5 -> same yoc each (price 20 base 1 => 5%)
        self.assertAlmostEqual(roll["now"]["value"], 5.0)
