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


class PortfolioTopupTests(unittest.TestCase):
    @patch(
        "scripts.portfolio_state.load_portfolio",
        return_value={"targets": {"AAA": 95, "cash": 5}},
    )
    def test_missing_price_stops_calculation(self, _load):
        with self.assertRaisesRegex(ValueError, "AAA"):
            rebalance_topup(_state(None), 10_000)

    @patch(
        "scripts.portfolio_state.load_portfolio",
        return_value={"targets": {"AAA": 95, "cash": 5}},
    )
    def test_board_lot_actual_spend_and_cash_remainder(self, _load):
        rows = rebalance_topup(_state(30.0), 10_000)
        by_sym = {row["sym"]: row for row in rows}
        stock = by_sym["AAA"]

        self.assertEqual(stock["shares_to_buy"], 300)
        self.assertEqual(stock["shares_to_buy"] % BOARD_LOT, 0)
        self.assertEqual(stock["baht"], stock["shares_to_buy"] * stock["price"])
        self.assertEqual(by_sym["cash"]["baht"], 1_000)
        self.assertEqual(sum(row["baht"] for row in rows), 10_000)
        self.assertEqual(stock["deficit_pct"], 95.0)


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
