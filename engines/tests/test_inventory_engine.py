"""
Unit tests for the Stochastic Inventory Engine.

Tests cover:
    • Single-medication forecast correctness
    • Batch forecast aggregation
    • Sensitivity analysis across service levels
    • Deterministic lead-time special case
    • Zero-demand edge case
    • High-demand / low-stock → high stockout probability
    • Seed reproducibility
    • Input validation
    • Statistical plausibility of Monte Carlo outputs
"""

from __future__ import annotations

import math
import unittest

from engines.inventory_engine import (
    ForecastResult,
    InventoryEngine,
    MedicationProfile,
)


# -- helpers ----------------------------------------------------------------

def _profile(
    mid: str = "M1",
    stock: int = 50,
    demand: float = 5.0,
    lt_mean: float = 5.0,
    lt_std: float = 1.5,
    cost: float = 2.0,
) -> MedicationProfile:
    return MedicationProfile(
        medication_id=mid, name=f"Med-{mid}",
        current_stock=stock,
        avg_daily_demand=demand,
        lead_time_mean_days=lt_mean,
        lead_time_std_days=lt_std,
        unit_cost=cost,
    )


def _engine(sl: float = 0.95, n: int = 10_000,
            seed: int = 42) -> InventoryEngine:
    return InventoryEngine(
        target_service_level=sl,
        num_simulations=n,
        seed=seed,
    )


# -- tests ------------------------------------------------------------------

class TestSingleForecast(unittest.TestCase):

    def test_basic_forecast_fields(self):
        engine = _engine()
        result = engine.forecast(_profile())
        self.assertIsInstance(result, ForecastResult)
        self.assertEqual(result.medication_id, "M1")
        self.assertGreaterEqual(result.stockout_probability, 0.0)
        self.assertLessEqual(result.stockout_probability, 1.0)
        self.assertGreater(result.optimal_reorder_point, 0)
        self.assertGreaterEqual(result.safety_stock, 0)

    def test_expected_demand_close_to_lambda_times_lead(self):
        """E[D_lead] ≈ λ · μ_L for large N."""
        profile = _profile(demand=5.0, lt_mean=5.0, lt_std=0.0)
        engine = _engine(n=50_000)
        result = engine.forecast(profile)
        # With σ_L=0, D_lead ~ Poisson(25), so E ≈ 25
        self.assertAlmostEqual(result.expected_demand_during_lead, 25.0,
                               delta=1.0)

    def test_high_stock_low_stockout(self):
        """Ample stock should yield near-zero stockout probability."""
        profile = _profile(stock=200, demand=2.0, lt_mean=3.0, lt_std=0.5)
        engine = _engine()
        result = engine.forecast(profile)
        self.assertLess(result.stockout_probability, 0.01)

    def test_low_stock_high_stockout(self):
        """Critically low stock should yield high stockout probability."""
        profile = _profile(stock=5, demand=10.0, lt_mean=7.0, lt_std=2.0)
        engine = _engine()
        result = engine.forecast(profile)
        self.assertGreater(result.stockout_probability, 0.90)

    def test_service_level_achieved(self):
        """At the optimal reorder point, achieved SL must ≥ target."""
        engine = _engine(sl=0.95)
        result = engine.forecast(_profile())
        self.assertGreaterEqual(result.service_level_achieved, 0.95)

    def test_days_of_cover(self):
        profile = _profile(stock=50, demand=5.0)
        engine = _engine()
        result = engine.forecast(profile)
        self.assertAlmostEqual(result.days_of_cover, 10.0, places=1)

    def test_capital_at_risk(self):
        profile = _profile(stock=0, demand=5.0, cost=10.0)
        engine = _engine()
        result = engine.forecast(profile)
        self.assertEqual(
            result.capital_at_risk,
            result.recommended_order_quantity * 10.0,
        )

    def test_var_ordering(self):
        """VaR_99 ≥ VaR_95 always."""
        engine = _engine()
        result = engine.forecast(_profile())
        self.assertGreaterEqual(result.var_99, result.var_95)


class TestDeterministicLeadTime(unittest.TestCase):
    """Special case where σ_L = 0 → lead time is constant."""

    def test_deterministic_lead_time(self):
        profile = _profile(demand=4.0, lt_mean=5.0, lt_std=0.0)
        engine = _engine(n=20_000, seed=123)
        result = engine.forecast(profile)
        # D_lead ~ Poisson(20), std ≈ sqrt(20) ≈ 4.47
        self.assertAlmostEqual(result.expected_demand_during_lead, 20.0,
                               delta=0.5)
        self.assertAlmostEqual(result.std_demand_during_lead, 4.47,
                               delta=0.5)


class TestZeroDemand(unittest.TestCase):

    def test_zero_demand_no_stockout(self):
        profile = _profile(stock=10, demand=0.0)
        engine = _engine()
        result = engine.forecast(profile)
        self.assertAlmostEqual(result.stockout_probability, 0.0, places=4)
        self.assertEqual(result.recommended_order_quantity, 0)
        self.assertEqual(result.days_of_cover, float("inf"))


class TestBatchForecast(unittest.TestCase):

    def test_batch_returns_all(self):
        profiles = [_profile(f"M{i}", stock=i * 10) for i in range(1, 4)]
        engine = _engine()
        batch = engine.forecast_batch(profiles)
        self.assertEqual(len(batch.forecasts), 3)

    def test_critical_items_filtered(self):
        profiles = [
            _profile("SAFE", stock=200, demand=1.0),
            _profile("RISKY", stock=5, demand=10.0, lt_mean=7.0, lt_std=2.0),
        ]
        engine = InventoryEngine(
            target_service_level=0.95, num_simulations=10_000,
            stockout_threshold=0.20, seed=42,
        )
        batch = engine.forecast_batch(profiles)
        critical_ids = [f.medication_id for f in batch.critical_items]
        self.assertIn("RISKY", critical_ids)
        self.assertNotIn("SAFE", critical_ids)

    def test_empty_batch(self):
        engine = _engine()
        batch = engine.forecast_batch([])
        self.assertEqual(batch.forecasts, [])
        self.assertEqual(batch.total_capital_at_risk, 0.0)


class TestSensitivityAnalysis(unittest.TestCase):

    def test_higher_sl_requires_higher_rop(self):
        engine = _engine()
        results = engine.sensitivity_analysis(
            _profile(),
            service_levels=[0.90, 0.95, 0.99],
        )
        self.assertLessEqual(
            results[0.90].optimal_reorder_point,
            results[0.95].optimal_reorder_point,
        )
        self.assertLessEqual(
            results[0.95].optimal_reorder_point,
            results[0.99].optimal_reorder_point,
        )


class TestReproducibility(unittest.TestCase):

    def test_same_seed_same_result(self):
        p = _profile()
        r1 = InventoryEngine(seed=99).forecast(p)
        r2 = InventoryEngine(seed=99).forecast(p)
        self.assertEqual(r1.stockout_probability, r2.stockout_probability)
        self.assertEqual(r1.optimal_reorder_point, r2.optimal_reorder_point)

    def test_different_seed_different_result(self):
        """With enough simulations, different seeds should give close but
        not necessarily identical results (stochastic test — we only check
        they run without error)."""
        p = _profile()
        r1 = InventoryEngine(seed=1).forecast(p)
        r2 = InventoryEngine(seed=2).forecast(p)
        # Both should be valid
        self.assertGreaterEqual(r1.service_level_achieved, 0.90)
        self.assertGreaterEqual(r2.service_level_achieved, 0.90)


class TestValidation(unittest.TestCase):

    def test_consume_stock_blocks_negative_inventory(self):
        engine = _engine()
        profile = _profile(stock=3)
        with self.assertRaises(ValueError):
            engine.consume_stock(profile, quantity=4)
        self.assertEqual(profile.current_stock, 3)

    def test_negative_demand_rejected(self):
        with self.assertRaises(ValueError):
            _engine().forecast(_profile(demand=-1.0))

    def test_zero_lead_time_rejected(self):
        with self.assertRaises(ValueError):
            _engine().forecast(_profile(lt_mean=0.0))

    def test_negative_stock_rejected(self):
        with self.assertRaises(ValueError):
            _engine().forecast(_profile(stock=-5))

    def test_bad_service_level_rejected(self):
        with self.assertRaises(ValueError):
            InventoryEngine(target_service_level=1.5)

    def test_too_few_simulations_rejected(self):
        with self.assertRaises(ValueError):
            InventoryEngine(num_simulations=10)


if __name__ == "__main__":
    unittest.main()
