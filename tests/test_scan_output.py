"""Scan output tests (entry shape, order, report, history) — fixtures only, no network."""
import sys
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from screen_stocks import build_entry, candidate_sort_key, parse_symbols  # noqa: E402
from report_template import generate_report_md, CLOSING  # noqa: E402
from history_manager import build_v2_entry, passed_of  # noqa: E402

CY = datetime.now().year
FORBIDDEN = ["score", "display_score", "breakdown", "disqualified", "penalty", "penalty_tags",
             "signals", "anchor_stage_tags", "exit_triggers", "valuation", "score_streak_weeks"]
NOW = datetime(2026, 10, 9, 12, 0)


def stock(dy, dps_hist=None, g5=0.05, g10=0.04, price=100.0):
    hist = dps_hist or {CY - 1 - i: 5.0 for i in range(10)}
    return {
        "symbol": "T.BK", "name": "Test", "sector": "Commerce", "sector_profile": "general",
        "price": price, "price_as_of": "2026-10-08", "dividend_yield": dy, "pe_ratio": 9.0, "pb_ratio": 1.1,
        "market_cap": 10e9, "payout_ratio": 0.5, "dividend_history": hist,
        "yearly_metrics": [{"year": str(CY - 5 + i), "diluted_eps": 1.0} for i in range(5)],
        "aggregates": {"dividend_streak": 10, "dividend_growth_streak": 4, "dps_cagr": g5, "dps_10y_cagr": g10,
                       "dividend_last_complete_fy": CY - 1, "data_gaps": ["x_gap"]},
    }


def cand(sym, path, dy, watch=False):
    return {"symbol": sym, "name": sym, "sector": "S", "in_watchlist": watch, "gate_path": path,
            "gate_flags": [], "price": 10.0, "price_as_of": "2026-10-08", "dividend_yield": dy,
            "last_dps": 0.6, "last_dps_fy": CY - 1, "projected_yield_5y": 5.5 if path == "growth" else None,
            "growth_used": 0.1 if path == "growth" else None, "dps_cagr_5y": 0.05, "dps_cagr_10y": 0.04,
            "dividend_streak": 8, "material_cuts_10y": 0, "pe": 8.0, "pbv": 1.0, "market_cap": 1e10, "data_gaps": []}


def screener(cands, failed=None, pending=None):
    return {"date": "2026-10-09", "gate_version": "niwes-gate-2026-10", "total_scanned": 5,
            "candidates": cands, "filtered_out_stocks": failed or [], "pending_candidates": pending or []}


class EntryTest(unittest.TestCase):
    def test_main_path_entry_shape(self):
        # assert: yield 6% -> gate_path main, no projection, wanted keys present, no score/label keys
        e = build_entry("T.BK", stock(6.0), True)
        self.assertEqual(e["gate_path"], "main")
        self.assertIsNone(e["projected_yield_5y"])
        self.assertTrue(e["in_watchlist"])
        for k in ("symbol", "name", "sector", "sector_profile", "gate_flags", "price", "price_as_of", "dividend_yield",
                  "last_dps", "last_dps_fy", "dps_cagr_5y", "dps_cagr_10y", "dividend_streak",
                  "material_cuts_10y", "pe", "pbv", "market_cap", "data_gaps"):
            self.assertIn(k, e)
        for k in FORBIDDEN:
            self.assertNotIn(k, e)
        self.assertEqual(e["data_gaps"], ["x_gap"])

    def test_growth_path_entry_has_projection(self):
        # assert: yield 3% with g=15% (cap) -> growth path, projected yield = dps x 1.15^5 / price, rate used = 0.15
        e = build_entry("T.BK", stock(3.0, g5=0.15, g10=0.15, price=100.0), False)
        self.assertEqual(e["gate_path"], "growth")
        self.assertAlmostEqual(e["growth_used"], 0.15)
        self.assertAlmostEqual(e["projected_yield_5y"], 5.0 * 1.15 ** 5 / 100 * 100, places=6)

    def test_material_cuts_counted_in_last_10_years(self):
        # assert: one 50% cut inside the 10-year window counts 1, an older cut does not
        hist = {CY - 1 - i: 5.0 for i in range(14)}
        hist[CY - 3] = 2.5          # cut inside the window (vs CY-4 = 5.0)
        hist[CY - 13] = 2.5         # cut 13 years back, outside the window
        e = build_entry("T.BK", stock(6.0, dps_hist=hist), False)
        self.assertEqual(e["material_cuts_10y"], 1)


class OrderTest(unittest.TestCase):
    def test_main_before_growth_then_yield_then_symbol(self):
        # assert: fixed order main (yield desc, symbol asc) then growth (yield desc)
        cs = [cand("G1", "growth", 4.0), cand("B", "main", 6.0), cand("A", "main", 6.0),
              cand("C", "main", 8.0), cand("G2", "growth", 3.0)]
        self.assertEqual([c["symbol"] for c in sorted(cs, key=candidate_sort_key)], ["C", "A", "B", "G1", "G2"])

    def test_parse_symbols(self):
        # assert: bare + .BK forms normalised, duplicates dropped, order kept
        self.assertEqual(parse_symbols("bbl, AMATA.BK,BBL"), ["BBL.BK", "AMATA.BK"])


OLD_PREV = {"iso_week": "2026-W33", "counts": {"passed": 2}, "top_candidates": [
    {"symbol": "OLD.BK", "score": 77, "tags": ["NIWES_5555"]}, {"symbol": "KEEP.BK", "score": 60}]}


class ReportTest(unittest.TestCase):
    def render(self, data, prev=None):
        return generate_report_md(data, "2026-W41", NOW, prev)

    def test_old_shape_prev_new_and_dropped(self):
        # assert: old prev (score/top_candidates) does not crash; NEW listed as new; OLD (now failed) as dropped with reason
        data = screener([cand("KEEP.BK", "main", 6.0), cand("NEW.BK", "growth", 3.0)],
                        failed=[{"symbol": "OLD.BK", "reasons": ["yield ต่ำ"], "in_watchlist": True}])
        md = self.render(data, OLD_PREV)
        self.assertIn("## เข้าใหม่รอบนี้\n\n- NEW (ทางอนุโลม)", md)
        self.assertIn("## หลุดจากรอบก่อน\n\n- OLD — yield ต่ำ", md)
        self.assertIn("**OLD** — yield ต่ำ", md)  # watchlist fail section

    def test_no_prev(self):
        # assert: no previous scan -> both diff sections say there is nothing to compare
        md = self.render(screener([cand("A.BK", "main", 6.0)]), None)
        self.assertEqual(md.count("_ไม่มีรอบก่อนให้เทียบ_"), 2)

    def test_empty_candidates(self):
        # assert: empty list -> tables say none, summary says 0, closing line present
        md = self.render(screener([]), None)
        self.assertIn("ผ่านด่าน 0 ตัว (ทางหลัก 0 / ทางอนุโลม 0)", md)
        self.assertIn("## ผ่านทางหลัก (yield ถึงเกณฑ์)\n\n_ไม่มี_", md)
        self.assertTrue(md.rstrip().endswith(CLOSING))

    def test_no_score_in_report_and_growth_columns(self):
        # assert: no score column; growth table carries projected yield + rate; price date shown
        md = self.render(screener([cand("A.BK", "main", 6.0), cand("G.BK", "growth", 3.0)]), None)
        self.assertNotIn("คะแนน", md)
        self.assertNotIn("Score", md)
        self.assertIn("yield ที่คาดปีที่ 5", md)
        self.assertIn("5.50%", md)
        self.assertIn("วันที่ของราคา: 2026-10-08", md)

    def test_deterministic(self):
        # assert: same input twice -> identical text
        data = screener([cand("A.BK", "main", 6.0)])
        self.assertEqual(self.render(data, OLD_PREV), self.render(data, OLD_PREV))


class HistoryTest(unittest.TestCase):
    def test_new_entry_has_no_score_and_counts_by_path(self):
        # assert: entry keeps date / counts by path / passed + gate_path, none of the old score fields
        data = screener([cand("A.BK", "main", 6.0), cand("G.BK", "growth", 3.0)])
        e = build_v2_entry(data, NOW, "scan_2026-10-09.md")
        self.assertEqual(e["counts"]["passed_main"], 1)
        self.assertEqual(e["counts"]["passed_growth"], 1)
        self.assertEqual(e["passed"], [{"symbol": "A.BK", "gate_path": "main"}, {"symbol": "G.BK", "gate_path": "growth"}])
        for k in ("top_candidates", "entry_thesis", "scoring_version", "watchlist_status", "price_snapshot"):
            self.assertNotIn(k, e)

    def test_passed_of_reads_old_and_new_shapes(self):
        # assert: old entry -> symbols with path None; new entry -> path kept; junk -> {}
        self.assertEqual(passed_of(OLD_PREV), {"OLD.BK": None, "KEEP.BK": None})
        new = build_v2_entry(screener([cand("A.BK", "main", 6.0)]), NOW, "r.md")
        self.assertEqual(passed_of(new), {"A.BK": "main"})
        self.assertEqual(passed_of(None), {})
        self.assertEqual(passed_of({"iso_week": "x"}), {})


class RefreshAndStaleTest(unittest.TestCase):
    def test_refresh_called_for_full_scan_with_none_and_for_symbols_with_list(self):
        # assert: refresh_market_prices passes the refresher None (whole market) or the given list; summary printed with counts + date
        import io
        from contextlib import redirect_stdout
        import screen_stocks as ss
        seen = []

        def fake(syms):
            seen.append(syms)
            return {"date": "2026-10-08", "bulk_calls": 1, "ok": {"A": "2026-10-08"}, "failed": {"B": "no row"}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            ss.refresh_market_prices(None, refresher=fake)
            ss.refresh_market_prices(["A.BK"], refresher=fake)
        self.assertEqual(seen, [None, ["A.BK"]])
        self.assertIn("1 refreshed, 1 failed", buf.getvalue())
        self.assertIn("refresh failed B: no row", buf.getvalue())

    def test_no_refresh_flag_never_calls_refresher(self):
        # assert: main(--no-refresh) with refresh_prices_bulk patched to raise -> not called (stops at empty fake universe)
        import tempfile
        import screen_stocks as ss
        tmp = tempfile.TemporaryDirectory()
        uni, ud = Path(tmp.name) / "u.json", Path(tmp.name) / "ud.json"
        uni.write_text('{"symbols": []}', encoding="utf-8")
        ud.write_text("{}", encoding="utf-8")
        old = (ss.refresh_prices_bulk, ss.UNIVERSE, ss.USER_DATA)

        def boom(*a, **k):
            raise AssertionError("refresh must not run")
        try:
            ss.refresh_prices_bulk, ss.UNIVERSE, ss.USER_DATA = boom, uni, ud
            ss.main(["--no-refresh", "--out-dir", str(Path(tmp.name) / "o")])
            with self.assertRaises(AssertionError):
                ss.main(["--out-dir", str(Path(tmp.name) / "o")])
        finally:
            ss.refresh_prices_bulk, ss.UNIVERSE, ss.USER_DATA = old
            tmp.cleanup()

    def test_report_warns_on_old_price_and_stays_silent_when_fresh(self):
        # assert: price 2026-08-26 vs scan 2026-10-09, limit 5 -> top warning with "1 จาก 2"; all fresh -> no warning text
        old = cand("OLD.BK", "main", 6.0)
        old["price_as_of"] = "2026-08-26"
        data = screener([old, cand("NEW.BK", "main", 5.5)])
        md = generate_report_md(data, "2026-W41", NOW, None, stale_days=5)
        self.assertIn("ราคาเก่าเกิน 5 วัน 1 จาก 2", md)
        self.assertLess(md.index("ราคาเก่าเกิน"), md.index("## สรุป"))
        fresh = generate_report_md(screener([cand("NEW.BK", "main", 5.5)]), "2026-W41", NOW, None, stale_days=5)
        self.assertNotIn("ราคาเก่าเกิน", fresh)


if __name__ == "__main__":
    unittest.main()
