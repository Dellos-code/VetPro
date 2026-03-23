"""
VetPro Algorithmic Engines
==========================

Core algorithmic & mathematical engine module for the VetPro
Veterinary Clinic Management System.

Contains two primary engines:
    - SchedulerEngine: Multi-constraint heuristic appointment optimizer
    - InventoryEngine: Stochastic Monte Carlo inventory forecaster
"""

from engines.scheduler_engine import SchedulerEngine
from engines.inventory_engine import InventoryEngine

__all__ = ["SchedulerEngine", "InventoryEngine"]
