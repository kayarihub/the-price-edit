import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from analyze import units_at_price, select_optimum

class TestPricingLogic(unittest.TestCase):
    def test_baseline_units(self):
        self.assertEqual(units_at_price(100,20,20,-2),100)
    def test_demand_decreases_when_price_rises(self):
        self.assertLess(units_at_price(100,22,20,-2),100)
    def test_margin_and_competitor_constraints(self):
        scenarios=[
            dict(price=100,competitor_price=100,gross_margin_pct=45,weekly_gross_profit=500,price_change_pct=0),
            dict(price=120,competitor_price=100,gross_margin_pct=55,weekly_gross_profit=1000,price_change_pct=20),
            dict(price=105,competitor_price=100,gross_margin_pct=25,weekly_gross_profit=800,price_change_pct=5),
        ]
        self.assertEqual(select_optimum(scenarios)["price"],100)
    def test_no_feasible_scenario(self):
        self.assertIsNone(select_optimum([
            dict(price=100,competitor_price=50,gross_margin_pct=20,weekly_gross_profit=1,price_change_pct=0)
        ]))

if __name__ == "__main__":
    unittest.main()
