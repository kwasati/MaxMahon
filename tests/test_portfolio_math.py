import unittest
from unittest.mock import patch

from scripts.portfolio_builder import allocate_80_20
from scripts.portfolio_state import BOARD_LOT, compute_buy_plan


def _state(price, cash, total_value):
    return {
        "positions": [
            {
                "sym": "AAA",
                "current_value": 0,
                "price": price,
                "missing_price": price is None,
            }
        ],
        "cash": cash,
        "total_value": total_value,
        "summary": {"missing_prices": ["AAA"] if price is None else []},
    }


class BuyPlanTests(unittest.TestCase):
    def test_board_lot_actual_spend_and_cash_remainder(self):
        st = _state(price=30.0, cash=10_000, total_value=10_000)
        plan = compute_buy_plan(st, {"AAA": 95, "cash": 5})
        rows = {r["sym"]: r for r in plan["rows"]}
        stock = rows["AAA"]

        self.assertEqual(stock["shares_to_buy"] % BOARD_LOT, 0)
        self.assertEqual(stock["baht"], stock["shares_to_buy"] * stock["price"])
        # ผลรวมทุกแถว (หุ้น + เงินสด) ต้องเท่ากับเงินสดตั้งต้นเป๊ะ — เงินห้ามหายระหว่างทาง
        self.assertAlmostEqual(
            sum(r["baht"] for r in plan["rows"]), 10_000, places=2
        )
        # แถวเงินสดต้องเป็นแถวสุดท้ายเสมอ
        self.assertEqual(plan["rows"][-1]["sym"], "cash")

    def test_missing_price_returns_empty_plan_without_raising(self):
        st = _state(price=None, cash=10_000, total_value=10_000)
        # ห้าม raise แม้ราคาไม่มา — build_state เรียกฟังก์ชันนี้ตรงๆ
        # raise ที่นี่ = ทั้งหน้าจอพัง ไม่ใช่แค่ตารางแผนซื้อหาย
        plan = compute_buy_plan(st, {"AAA": 95, "cash": 5})
        self.assertEqual(plan["rows"], [])
        self.assertIn("AAA", plan["note"])

    def test_cash_below_target_yields_zero_spendable(self):
        # เป้าเงินสด 50% ของพอร์ต 10,000 แต่มีเงินสดแค่ 1,000 - ต่ำกว่าเป้า
        st = _state(price=30.0, cash=1_000, total_value=10_000)
        plan = compute_buy_plan(st, {"AAA": 50, "cash": 50})
        self.assertEqual(plan["spendable"], 0.0)
        rows = {r["sym"]: r for r in plan["rows"]}
        self.assertEqual(rows["AAA"]["shares_to_buy"], 0)
        self.assertIn("cash", rows)

    def test_row_sum_reconciles_to_starting_cash_across_two_stocks(self):
        # หุ้น 2 ตัวราคาต่างกัน ล็อตซื้อไม่ลงตัวพอดี - เงินเศษต้องตกเป็นแถวเงินสด
        # ไม่ใช่หายไปเงียบๆ ระหว่างทาง (นี่คือบั๊กเดิมที่งานนี้มาฆ่า)
        state = {
            "positions": [
                {"sym": "X", "current_value": 0.0, "price": 33.0},
                {"sym": "Y", "current_value": 0.0, "price": 17.0},
            ],
            "cash": 15_000.0,
            "total_value": 50_000.0,
        }
        targets = {"X": 40, "Y": 30, "cash": 10}
        plan = compute_buy_plan(state, targets)
        self.assertEqual(plan["spendable"], 10_000.0)
        self.assertAlmostEqual(
            sum(r["baht"] for r in plan["rows"]), 15_000.0, places=2
        )
        self.assertEqual(plan["rows"][-1]["sym"], "cash")

    def test_expensive_lot_does_not_strand_money(self):
        # RICH ล็อตละ 19,000 ขาดเป้าเยอะสุด แต่ซื้อไม่ไหวด้วยเงิน 12,000
        # CHEAP ล็อตละ 1,000 ขาดเป้าน้อยกว่า แต่ซื้อไหว -> เงินต้องไปที่ CHEAP
        # ของเดิม (แบ่งสัดส่วนช่องว่างก่อน แล้วค่อยปัดลงเป็นล็อต) จะจองเงินให้ RICH
        # ตามสัดส่วนช่องว่างแล้วปัดลงเหลือ 0 หุ้น เงินก้อนนั้นตกเป็นเงินสดหายไปเงียบๆ
        # - เทสนี้กันไม่ให้กลับมา (เคยหายไปถึง 45% ของเงินเติมรอบหนึ่ง)
        state = {
            "positions": [
                {"sym": "RICH", "current_value": 0.0, "price": 190.0},
                {"sym": "CHEAP", "current_value": 0.0, "price": 10.0},
            ],
            "cash": 12_000.0,
            "total_value": 1_000_000.0,
        }
        targets = {"RICH": 50, "CHEAP": 5, "cash": 0}
        plan = compute_buy_plan(state, targets)
        rows = {r["sym"]: r for r in plan["rows"]}
        self.assertGreater(rows["CHEAP"]["shares_to_buy"], 0)
        self.assertLess(rows["cash"]["baht"], 1_000)

    def test_deterministic_across_repeated_calls(self):
        # AAA/BBB ห่างเป้าเท่ากันเป๊ะและราคาเท่ากัน - tie ต้องแตกด้วยลำดับ key
        # ใน targets เสมอ ไม่ใช่สุ่ม ไม่งั้นหน้าจอโหลดซ้ำแล้วได้แผนซื้อคนละอัน
        state = {
            "positions": [
                {"sym": "AAA", "current_value": 0.0, "price": 50.0},
                {"sym": "BBB", "current_value": 0.0, "price": 50.0},
            ],
            "cash": 20_000.0,
            "total_value": 1_000_000.0,
        }
        targets = {"AAA": 10, "BBB": 10, "cash": 0}
        results = [compute_buy_plan(state, targets) for _ in range(5)]
        for result in results[1:]:
            self.assertEqual(result, results[0])


class PortfolioBuilderWeightTests(unittest.TestCase):
    def test_weights_always_total_one_hundred(self):
        for count in range(1, 6):
            with self.subTest(count=count):
                picks = [{"symbol": str(i)} for i in range(count)]
                rows = allocate_80_20(picks)
                self.assertEqual(sum(row["weight_pct"] for row in rows), 100.0)

    def test_five_stock_weights_are_unchanged(self):
        picks = [{"symbol": str(i)} for i in range(5)]
        rows = allocate_80_20(picks)
        self.assertEqual(
            [row["weight_pct"] for row in rows],
            [40.0, 35.0, 12.0, 8.0, 5.0],
        )


if __name__ == "__main__":
    unittest.main()
