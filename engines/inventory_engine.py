"""
Stochastic Inventory Engine — Monte Carlo Demand Forecasting
=============================================================

Mathematical Model
------------------
Traditional deterministic reorder-point systems use:

    Reorder Point (ROP) = d̄ · L + Safety Stock

where d̄ = average daily demand and L = lead time (days).
Safety stock is typically *z · σ_d · √L*, yielding a fixed cushion.

This approach **fails** when:
    • Daily demand is discrete / bursty (common in veterinary clinics).
    • Supplier lead times are stochastic (variable delivery delays).
    • Management wants an explicit **probability of stockout** rather than
      a deterministic threshold.

**Our stochastic formulation:**

    D_daily ~ Poisson(λ)               — demand per day
    L       ~ max(1, Normal(μ_L, σ_L)) — supplier lead time in days
    D_lead  = Σ_{t=1}^{L} D_daily(t)   — demand during lead time (compound)

Because L is random and each day's demand is independent Poisson,
the demand-during-lead-time D_lead has **no closed-form** distribution
when σ_L > 0 (it is a compound Poisson–Normal).  We therefore use
**Monte Carlo simulation** to estimate its distribution empirically.

Value-at-Risk (VaR) for Stockout
---------------------------------
    P(stockout) = P(D_lead > current_stock)

We estimate this probability from the empirical CDF of the simulated
D_lead samples.  The **optimal reorder point** R* is the smallest
integer R such that:

    P(D_lead ≤ R) ≥ target_service_level          (e.g. 0.95)

This is equivalent to the (1 − α)-quantile of D_lead.

Safety Stock
------------
    Safety Stock = R* − d̄ · μ_L

Capital Efficiency
------------------
The engine also reports the *expected days of cover* at the recommended
reorder quantity, allowing managers to balance service level against
capital tied up in inventory.

Algorithm — Monte Carlo Procedure
-----------------------------------
1.  For i = 1 … N_sim:
        a.  Sample L_i ~ max(1, round(Normal(μ_L, σ_L)))
        b.  Sample D_i = Σ_{t=1}^{L_i} Poisson(λ)
2.  Sort {D_i}.
3.  R* = quantile({D_i}, target_service_level)    (ceil to integer)
4.  P(stockout | stock=S) = fraction of D_i > S
5.  Safety Stock = R* − ceil(λ · μ_L)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from numpy.random import Generator, default_rng
from scipy import stats as sp_stats


# ---------------------------------------------------------------------------
# Domain value objects
# ---------------------------------------------------------------------------

@dataclass
class MedicationProfile:
    """
    Statistical profile of a single medication item.

    Parameters
    ----------
    medication_id : str
        Unique identifier.
    name : str
        Human-readable name.
    current_stock : int
        Units currently on hand.
    avg_daily_demand : float
        λ for the Poisson daily demand distribution (estimated from
        historical dispensing records).
    lead_time_mean_days : float
        μ_L — mean supplier lead time in days.
    lead_time_std_days : float
        σ_L — standard deviation of supplier lead time.
    unit_cost : float
        Cost per unit (for capital-efficiency calculations).
    """
    medication_id: str
    name: str
    current_stock: int
    avg_daily_demand: float
    lead_time_mean_days: float = 5.0
    lead_time_std_days: float = 1.5
    unit_cost: float = 1.0


@dataclass
class ForecastResult:
    """
    Result of the stochastic inventory analysis for one medication.

    Attributes
    ----------
    medication_id : str
    name : str
    current_stock : int
    stockout_probability : float
        P(demand_during_lead_time > current_stock).
    optimal_reorder_point : int
        Smallest R such that P(D_lead ≤ R) ≥ service_level.
    safety_stock : int
        optimal_reorder_point − ceil(λ · μ_L).
    recommended_order_quantity : int
        Units to order now (max(0, optimal_reorder_point − current_stock)).
    expected_demand_during_lead : float
        Mean of the simulated D_lead distribution.
    std_demand_during_lead : float
        Std-dev of the simulated D_lead distribution.
    days_of_cover : float
        current_stock / avg_daily_demand (how many days stock lasts at
        average demand, ignoring lead-time uncertainty).
    service_level_achieved : float
        Actual P(D_lead ≤ optimal_reorder_point) from simulation.
    var_95 : float
        95th-percentile of D_lead (Value-at-Risk).
    var_99 : float
        99th-percentile of D_lead.
    capital_at_risk : float
        recommended_order_quantity × unit_cost.
    """
    medication_id: str
    name: str
    current_stock: int
    stockout_probability: float
    optimal_reorder_point: int
    safety_stock: int
    recommended_order_quantity: int
    expected_demand_during_lead: float
    std_demand_during_lead: float
    days_of_cover: float
    service_level_achieved: float
    var_95: float
    var_99: float
    capital_at_risk: float


@dataclass
class BatchForecastResult:
    """Aggregated forecast across all medications."""
    forecasts: list[ForecastResult]
    critical_items: list[ForecastResult]
    total_capital_at_risk: float
    simulation_count: int


# ---------------------------------------------------------------------------
# Core Engine
# ---------------------------------------------------------------------------

class InventoryEngine:
    """
    Stochastic Inventory Engine
    ===========================

    Runs Monte Carlo simulations to forecast medication demand during
    supplier lead time and recommends optimal reorder points.

    Usage
    -----
    >>> engine = InventoryEngine(target_service_level=0.95,
    ...                          num_simulations=10_000)
    >>> result = engine.forecast(medication_profile)
    >>> print(result.stockout_probability)
    >>> print(result.optimal_reorder_point)

    Parameters
    ----------
    target_service_level : float
        Desired probability that stock will *not* run out during lead
        time.  E.g. 0.95 = 95 % service level.
    num_simulations : int
        Number of Monte Carlo iterations (higher = more precise).
    stockout_threshold : float
        Medications with P(stockout) above this are flagged critical.
    seed : int, optional
        RNG seed for reproducibility.
    """

    def __init__(
        self,
        target_service_level: float = 0.95,
        num_simulations: int = 10_000,
        stockout_threshold: float = 0.20,
        seed: Optional[int] = None,
    ) -> None:
        if not 0.0 < target_service_level < 1.0:
            raise ValueError(
                "target_service_level must be in (0, 1); "
                f"got {target_service_level}"
            )
        if num_simulations < 100:
            raise ValueError(
                "num_simulations must be ≥ 100 for statistical significance"
            )

        self._service_level = target_service_level
        self._n_sim = num_simulations
        self._threshold = stockout_threshold
        self._rng: Generator = default_rng(seed)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def forecast(self, profile: MedicationProfile) -> ForecastResult:
        """
        Run the Monte Carlo simulation for a single medication.

        The procedure:
            1. Sample N lead-time values  L_i ~ max(1, round(N(μ_L, σ_L)))
            2. For each L_i, sample D_i = Σ Poisson(λ) over L_i days
            3. Build the empirical distribution of {D_i}
            4. Derive stockout probability, optimal reorder point, etc.

        Returns
        -------
        ForecastResult
        """
        self._validate_profile(profile)

        demand_samples = self._simulate_demand_during_lead_time(profile)

        return self._analyse(profile, demand_samples)

    def consume_stock(self, profile: MedicationProfile, quantity: int) -> int:
        """
        Subtract stock units from a medication profile with strict bounds.

        Parameters
        ----------
        profile : MedicationProfile
            Profile to mutate.
        quantity : int
            Units to consume. Must be a positive integer.

        Returns
        -------
        int
            The updated stock level.

        Raises
        ------
        ValueError
            If quantity is not positive or if consumption would make stock
            negative.
        """
        if quantity <= 0:
            raise ValueError(f"quantity must be > 0; got {quantity}")

        if quantity > profile.current_stock:
            raise ValueError(
                "insufficient stock: cannot consume "
                f"{quantity} units from current_stock={profile.current_stock}"
            )

        profile.current_stock -= quantity
        return profile.current_stock

    def forecast_batch(
        self,
        profiles: list[MedicationProfile],
    ) -> BatchForecastResult:
        """
        Run forecasts for multiple medications and aggregate results.

        Returns
        -------
        BatchForecastResult
            Contains individual forecasts, critical items, and total
            capital at risk.
        """
        if not profiles:
            return BatchForecastResult(
                forecasts=[], critical_items=[],
                total_capital_at_risk=0.0,
                simulation_count=self._n_sim,
            )

        forecasts = [self.forecast(p) for p in profiles]
        critical = [f for f in forecasts
                    if f.stockout_probability >= self._threshold]
        total_capital = sum(f.capital_at_risk for f in forecasts)

        return BatchForecastResult(
            forecasts=forecasts,
            critical_items=sorted(critical,
                                  key=lambda f: -f.stockout_probability),
            total_capital_at_risk=round(total_capital, 2),
            simulation_count=self._n_sim,
        )

    def sensitivity_analysis(
        self,
        profile: MedicationProfile,
        service_levels: Optional[list[float]] = None,
    ) -> dict[float, ForecastResult]:
        """
        Run the simulation once and evaluate reorder points at multiple
        service-level targets.  Useful for plotting the cost-vs-risk
        trade-off curve.

        Parameters
        ----------
        profile : MedicationProfile
        service_levels : list[float], optional
            Defaults to [0.90, 0.92, 0.95, 0.97, 0.99].

        Returns
        -------
        dict mapping service_level → ForecastResult
        """
        self._validate_profile(profile)

        if service_levels is None:
            service_levels = [0.90, 0.92, 0.95, 0.97, 0.99]

        demand_samples = self._simulate_demand_during_lead_time(profile)
        results: dict[float, ForecastResult] = {}

        original_sl = self._service_level
        for sl in service_levels:
            self._service_level = sl
            results[sl] = self._analyse(profile, demand_samples)
        self._service_level = original_sl

        return results

    # ------------------------------------------------------------------
    # Monte Carlo core
    # ------------------------------------------------------------------

    def _simulate_demand_during_lead_time(
        self,
        profile: MedicationProfile,
    ) -> np.ndarray:
        """
        Generate *_n_sim* samples of total demand during the stochastic
        lead time.

        For each simulation run:
            L_i = max(1, round(Normal(μ_L, σ_L)))
            D_i = Σ_{t=1}^{L_i} Poisson(λ)

        Vectorised implementation for performance.
        """
        lam = profile.avg_daily_demand
        mu_l = profile.lead_time_mean_days
        sigma_l = profile.lead_time_std_days

        # Sample lead times (clipped to ≥ 1 day)
        if sigma_l > 0:
            raw_lead = self._rng.normal(mu_l, sigma_l, size=self._n_sim)
            lead_times = np.maximum(1, np.round(raw_lead)).astype(int)
        else:
            lead_times = np.full(self._n_sim, max(1, round(mu_l)), dtype=int)

        # For each lead time L_i, demand = sum of L_i independent Poisson(λ)
        # Property: sum of L_i iid Poisson(λ) = Poisson(L_i · λ)
        # This vectorises the inner loop.
        demand_samples = self._rng.poisson(
            lam=lead_times.astype(float) * lam
        )

        return demand_samples

    # ------------------------------------------------------------------
    # Statistical analysis
    # ------------------------------------------------------------------

    def _analyse(
        self,
        profile: MedicationProfile,
        demand_samples: np.ndarray,
    ) -> ForecastResult:
        """
        Derive all forecast metrics from the simulated demand samples.
        """
        n = len(demand_samples)
        stock = profile.current_stock

        # Empirical stockout probability
        stockout_prob = float(np.mean(demand_samples > stock))

        # Optimal reorder point = quantile at target service level
        rop = int(np.ceil(np.percentile(demand_samples,
                                        self._service_level * 100)))

        # Actual service level achieved at that ROP
        sl_achieved = float(np.mean(demand_samples <= rop))

        # Safety stock
        deterministic_rop = math.ceil(
            profile.avg_daily_demand * profile.lead_time_mean_days
        )
        safety_stock = max(0, rop - deterministic_rop)

        # Recommended order quantity
        order_qty = max(0, rop - stock)

        # Days of cover
        days_of_cover = (stock / profile.avg_daily_demand
                         if profile.avg_daily_demand > 0 else float("inf"))

        # VaR percentiles
        var_95 = float(np.percentile(demand_samples, 95))
        var_99 = float(np.percentile(demand_samples, 99))

        return ForecastResult(
            medication_id=profile.medication_id,
            name=profile.name,
            current_stock=stock,
            stockout_probability=round(stockout_prob, 6),
            optimal_reorder_point=rop,
            safety_stock=safety_stock,
            recommended_order_quantity=order_qty,
            expected_demand_during_lead=round(float(np.mean(demand_samples)), 2),
            std_demand_during_lead=round(float(np.std(demand_samples)), 2),
            days_of_cover=round(days_of_cover, 2),
            service_level_achieved=round(sl_achieved, 6),
            var_95=round(var_95, 2),
            var_99=round(var_99, 2),
            capital_at_risk=round(order_qty * profile.unit_cost, 2),
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_profile(profile: MedicationProfile) -> None:
        """Guard against nonsensical inputs."""
        if profile.avg_daily_demand < 0:
            raise ValueError(
                f"avg_daily_demand must be ≥ 0; got {profile.avg_daily_demand}"
            )
        if profile.lead_time_mean_days <= 0:
            raise ValueError(
                f"lead_time_mean_days must be > 0; got "
                f"{profile.lead_time_mean_days}"
            )
        if profile.lead_time_std_days < 0:
            raise ValueError(
                f"lead_time_std_days must be ≥ 0; got "
                f"{profile.lead_time_std_days}"
            )
        if profile.current_stock < 0:
            raise ValueError(
                f"current_stock must be ≥ 0; got {profile.current_stock}"
            )
