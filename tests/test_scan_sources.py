"""Scan: แหล่งปันผล · ธง YIELD_ABNORMAL · ถ้อยคำ refresh log — fixtures only, no network."""
import sys
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from screen_stocks import gate_flags, dividend_source_counts  # noqa: E402
from report_template import generate_report_md, source_summary  # noqa: E402
from data_adapter import refresh_prices_bulk  # noqa: E402
from tests.test_gate import make  # noqa: E402
from tests.test_scan_output import cand, screener  # noqa: E402

NOW = datetime(2026, 10, 9, 12, 0)


class SourcesTest(unittest.TestCase):
    def test_counts_split_set_yahoo_none(self):
        # assert: set_official / set_official+yahoo -> set · yahoo with history -> yahoo_only · else none · delisted skipped
        f = {"A": {"dividend_source": "set_official", "dividend_history": {2024: 1}},
             "B": {"dividend_source": "set_official+yahoo", "dividend_history": {2024: 1}},
             "C": {"dividend_source": "yahoo", "dividend_history": {2024: 1}},
             "D": {"dividend_source": "yahoo", "dividend_history": {}},
             "E": {"delisted": True}}
        self.assertEqual(dividend_source_counts(f), {"set": 2, "yahoo_only": 1, "none": 1, "total": 4})

    def test_warning_only_over_share(self):
        # assert: yahoo-only 3/4 > 0.5 -> warn on top; 1/4 -> line but no warn; no counts -> nothing
        _, warn = source_summary({"total": 4, "set": 1, "yahoo_only": 3, "none": 0}, 0.5)
        self.assertIn("yahoo อย่างเดียว 75%", warn)
        line, warn = source_summary({"total": 4, "set": 3, "yahoo_only": 1, "none": 0}, 0.5)
        self.assertEqual(warn, "")
        self.assertIn("set.or.th 3", line)
        self.assertEqual(source_summary(None, 0.5), ("", ""))

    def test_report_has_sources_and_top_warning(self):
        # assert: warning comes before the summary section; summary lists the three counts
        s = screener([cand("AAA.BK", "main", 6.0)])
        s["dividend_sources"] = {"total": 10, "set": 2, "yahoo_only": 8, "none": 0}
        md = generate_report_md(s, "2026-W41", NOW, None, stale_days=5)
        self.assertLess(md.index("yahoo อย่างเดียว 80%"), md.index("## สรุป"))
        self.assertIn("yahoo อย่างเดียว 8", md)


class AbnormalYieldTest(unittest.TestCase):
    def test_flag_over_threshold_only(self):
        # assert: 157.9% -> YIELD_ABNORMAL; 8% -> none; flag never changes the gate (flags only)
        self.assertTrue(any(f.startswith("YIELD_ABNORMAL") for f in gate_flags(make(157.9))))
        self.assertFalse(any(f.startswith("YIELD_ABNORMAL") for f in gate_flags(make(8.0))))

    def test_report_separates_abnormal(self):
        # assert: abnormal stock sits in its own section, not in the main table
        bad = cand("JAS.BK", "main", 157.9)
        bad["gate_flags"] = ["YIELD_ABNORMAL:157.9%"]
        md = generate_report_md(screener([cand("OK.BK", "main", 6.0), bad]), "2026-W41", NOW, None, stale_days=5)
        main_part = md.split("## ผ่านทางหลัก")[1].split("## ")[0]
        self.assertIn("OK", main_part)
        self.assertNotIn("JAS", main_part)
        self.assertIn("## ต้องตรวจข้อมูลก่อนเชื่อ", md)
        self.assertIn("JAS", md.split("## ต้องตรวจข้อมูลก่อนเชื่อ")[1])


class RefreshWordingTest(unittest.TestCase):
    def test_reason_matches_cause(self):
        # assert: fallback disabled -> "ไม่ได้ยิง fallback รายตัว" (not "เกินโควตา")
        bulk = lambda d: [{"symbol": "AAA", "close": 1.0}]  # noqa: E731
        r = refresh_prices_bulk(["AAA.BK", "ZZZ.BK"], bulk_fetcher=bulk, max_per_symbol_fallback=0)
        why = r["failed"]["ZZZ"]
        self.assertIn("ไม่ได้ยิง fallback รายตัว", why)
        self.assertNotIn("เกินโควตา", why)


if __name__ == "__main__":
    unittest.main()
