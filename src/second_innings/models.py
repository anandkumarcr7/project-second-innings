"""
Data models for Project Second Innings.

These dataclasses represent the core entities used throughout the application:
retirement scenario assumptions, annual projection records, simulation results,
FI target results, and stress-test results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


MODEL_VERSION = "0.1"


@dataclass
class RetirementScenario:
    """All user-supplied assumptions for a retirement simulation."""

    scenario_name: str
    current_age: int
    retirement_age: int
    retirement_duration_years: int
    monthly_expenses: float          # current monthly retirement expenses
    current_assets: float            # current investable / liquid assets
    annual_passive_income: float     # passive income received after retirement
    inflation_rate: float            # e.g. 0.07 for 7%
    conservative_return: float       # e.g. 0.07
    typical_return: float            # e.g. 0.09
    optimistic_return: float         # e.g. 0.11
    effective_tax_rate: float        # simplified tax on investment returns, e.g. 0.10
    currency: str = "INR"
    model_version: str = MODEL_VERSION
    sleep_well_margin: float = 0.10  # design margin for Sleep Well target
    sleep_best_margin: float = 0.25  # design margin for Sleep Best target
    average_annual_savings: float = 0.0  # expected savings per year until retirement

    def __post_init__(self) -> None:
        if self.monthly_expenses <= 0:
            raise ValueError("monthly_expenses must be greater than zero.")
        if self.retirement_duration_years <= 0:
            raise ValueError("retirement_duration_years must be greater than zero.")
        if not (0.0 <= self.effective_tax_rate <= 1.0):
            raise ValueError("effective_tax_rate must be between 0 and 1 (inclusive).")
        if self.sleep_well_margin < 0 or self.sleep_best_margin < 0:
            raise ValueError("Design margins must be non-negative.")
        if self.sleep_best_margin < self.sleep_well_margin:
            raise ValueError("sleep_best_margin must be >= sleep_well_margin.")
        if self.average_annual_savings < 0:
            raise ValueError("average_annual_savings must be non-negative.")


@dataclass
class AnnualProjectionRecord:
    """One row in the year-by-year retirement projection table."""

    year: int
    age: int
    opening_corpus: float
    investment_growth: float   # net of tax
    taxes: float
    expenses: float            # inflation-adjusted annual expenses
    passive_income: float
    net_withdrawal: float      # max(expenses - passive_income, 0)
    closing_corpus: float
    real_closing_corpus: float  # closing corpus in today's purchasing power
    status: str                 # "PASS" or "FAIL"


@dataclass
class SimulationResult:
    """Output of a single deterministic retirement simulation run."""

    scenario: RetirementScenario
    opening_corpus: float
    ending_corpus: float
    result: str                    # "PASS" or "FAIL"
    failure_year: Optional[int]    # first year with negative closing corpus, or None
    projection: List[AnnualProjectionRecord]


@dataclass
class FITargetResult:
    """Financial Independence corpus targets and funding-gap analysis."""

    sleep_okay_corpus: float
    sleep_well_corpus: float
    sleep_best_corpus: float
    current_assets: float
    projected_assets: float    # current_assets + years_to_retirement × average_annual_savings
    selected_target: str       # "sleep_okay" | "sleep_well" | "sleep_best"
    funding_gap: float         # target - projected_assets  (negative = surplus)
    percent_complete: float    # projected_assets / target × 100
    fi_status: str             # "FI Achieved" | "Not Yet FI"


@dataclass
class StressTestResult:
    """Result of a single deterministic stress test."""

    test_name: str
    assumptions_changed: Dict[str, object]
    result: str                   # "PASS" or "FAIL"
    failure_year: Optional[int]
    ending_corpus: float
    severity: str                 # "Low" | "Medium" | "High"
