"""
Retirement simulation engine for Project Second Innings.

Implements:
  - deterministic annual simulation
  - binary-search minimum corpus solver
  - FI target calculation (Sleep Okay / Well / Best)
  - predefined stress-test suite
"""

from __future__ import annotations

import dataclasses
from typing import List, Optional

from .models import (
    AnnualProjectionRecord,
    FITargetResult,
    RetirementScenario,
    SimulationResult,
    StressTestResult,
)

_SOLVER_TOLERANCE = 1.0  # rupees


# ---------------------------------------------------------------------------
# Core simulation
# ---------------------------------------------------------------------------

def simulate(
    scenario: RetirementScenario,
    opening_corpus: float,
    return_rate: float,
    *,
    return_rate_sequence: Optional[List[float]] = None,
    expense_multiplier_sequence: Optional[List[float]] = None,
) -> SimulationResult:
    """
    Run a deterministic annual retirement simulation.

    Parameters
    ----------
    scenario:
        Retirement assumptions (expenses, inflation, tax, duration, …).
    opening_corpus:
        Starting corpus value.
    return_rate:
        Default annual return rate applied to every year unless overridden.
    return_rate_sequence:
        Optional per-year return rates.  Element 0 applies to year 1.
        Any year beyond the list length falls back to *return_rate*.
    expense_multiplier_sequence:
        Optional per-year expense multipliers (e.g. 1.20 = 20% higher spending).
        Same indexing convention as *return_rate_sequence*.

    Returns
    -------
    SimulationResult with the full year-by-year projection.
    """
    projection: List[AnnualProjectionRecord] = []
    corpus = opening_corpus
    failure_year: Optional[int] = None
    base_annual_expense = scenario.monthly_expenses * 12
    duration = scenario.retirement_duration_years

    for year in range(1, duration + 1):
        age = scenario.retirement_age + year - 1
        opening = corpus

        # ── Return rate for this year ──────────────────────────────────────
        if return_rate_sequence and year <= len(return_rate_sequence):
            rate = return_rate_sequence[year - 1]
        else:
            rate = return_rate

        # ── Inflation-adjusted annual expense ─────────────────────────────
        inflated_expense = base_annual_expense * (1 + scenario.inflation_rate) ** (year - 1)
        if expense_multiplier_sequence and year <= len(expense_multiplier_sequence):
            inflated_expense *= expense_multiplier_sequence[year - 1]

        # ── Investment growth (Section 3.2 / 3.3) ────────────────────────
        gross_growth = opening * rate
        tax = max(gross_growth, 0.0) * scenario.effective_tax_rate
        net_growth = gross_growth - tax

        # ── Withdrawal (Section 3.4) ──────────────────────────────────────
        passive_income = scenario.annual_passive_income
        net_withdrawal = max(inflated_expense - passive_income, 0.0)

        # ── Closing corpus (Section 3.5) ──────────────────────────────────
        closing = opening + net_growth - net_withdrawal

        # ── Real corpus (Section 3.6) ─────────────────────────────────────
        real_closing = closing / (1 + scenario.inflation_rate) ** year

        # ── Status ────────────────────────────────────────────────────────
        status = "FAIL" if closing < 0 else "PASS"
        if status == "FAIL" and failure_year is None:
            failure_year = year

        projection.append(AnnualProjectionRecord(
            year=year,
            age=age,
            opening_corpus=opening,
            investment_growth=net_growth,
            taxes=tax,
            expenses=inflated_expense,
            passive_income=passive_income,
            net_withdrawal=net_withdrawal,
            closing_corpus=closing,
            real_closing_corpus=real_closing,
            status=status,
        ))

        corpus = closing

    overall = "FAIL" if failure_year is not None else "PASS"
    return SimulationResult(
        scenario=scenario,
        opening_corpus=opening_corpus,
        ending_corpus=corpus,
        result=overall,
        failure_year=failure_year,
        projection=projection,
    )


# ---------------------------------------------------------------------------
# Minimum corpus solver (Section 5)
# ---------------------------------------------------------------------------

def solve_minimum_corpus(
    scenario: RetirementScenario,
    return_rate: float,
    *,
    return_rate_sequence: Optional[List[float]] = None,
    expense_multiplier_sequence: Optional[List[float]] = None,
    tolerance: float = _SOLVER_TOLERANCE,
) -> float:
    """
    Binary-search for the minimum starting corpus that produces a PASS.

    The solver expands the upper bound automatically if the initial estimate
    is insufficient (TC-013).

    Parameters
    ----------
    scenario:
        Retirement assumptions.
    return_rate:
        Constant return rate (fallback when no sequence is provided).
    tolerance:
        Convergence threshold in currency units (default 1 rupee).
    """
    def _run(corpus: float) -> str:
        return simulate(
            scenario, corpus, return_rate,
            return_rate_sequence=return_rate_sequence,
            expense_multiplier_sequence=expense_multiplier_sequence,
        ).result

    base_annual = scenario.monthly_expenses * 12
    lower = 0.0
    upper = base_annual * scenario.retirement_duration_years

    # Expand upper bound until a PASS is found
    while _run(upper) == "FAIL":
        upper *= 2.0

    # Binary search
    while (upper - lower) > tolerance:
        mid = (lower + upper) / 2.0
        if _run(mid) == "PASS":
            upper = mid
        else:
            lower = mid

    return upper


# ---------------------------------------------------------------------------
# FI target calculation (Section 6)
# ---------------------------------------------------------------------------

def calculate_fi_targets(
    scenario: RetirementScenario,
    selected_target: str = "sleep_well",
) -> FITargetResult:
    """
    Calculate Sleep Okay, Sleep Well, and Sleep Best corpus targets.

    Sleep Okay  = minimum corpus under the *typical* return assumption.
    Sleep Well  = minimum corpus under the *conservative* return
                  × (1 + sleep_well_margin).
    Sleep Best  = minimum corpus under the *conservative* return
                  × (1 + sleep_best_margin).

    Parameters
    ----------
    selected_target:
        One of "sleep_okay", "sleep_well", or "sleep_best".
    """
    if selected_target not in ("sleep_okay", "sleep_well", "sleep_best"):
        raise ValueError(f"Invalid selected_target: {selected_target!r}")

    sleep_okay = solve_minimum_corpus(scenario, scenario.typical_return)
    conservative_base = solve_minimum_corpus(scenario, scenario.conservative_return)

    sleep_well = conservative_base * (1.0 + scenario.sleep_well_margin)
    sleep_best = conservative_base * (1.0 + scenario.sleep_best_margin)

    target_corpus = {"sleep_okay": sleep_okay,
                     "sleep_well": sleep_well,
                     "sleep_best": sleep_best}[selected_target]

    years_to_retirement = max(scenario.retirement_age - scenario.current_age, 0)
    projected_assets = (scenario.current_assets
                        + years_to_retirement * scenario.average_annual_savings)

    funding_gap = target_corpus - projected_assets
    percent_complete = (projected_assets / target_corpus * 100.0
                        if target_corpus > 0 else 0.0)
    fi_status = "FI Achieved" if projected_assets >= target_corpus else "Not Yet FI"

    return FITargetResult(
        sleep_okay_corpus=sleep_okay,
        sleep_well_corpus=sleep_well,
        sleep_best_corpus=sleep_best,
        current_assets=scenario.current_assets,
        projected_assets=projected_assets,
        selected_target=selected_target,
        funding_gap=funding_gap,
        percent_complete=percent_complete,
        fi_status=fi_status,
    )


# ---------------------------------------------------------------------------
# Stress-test suite (Section 8)
# ---------------------------------------------------------------------------

def _classify_severity(result: str, failure_year: Optional[int], duration: int) -> str:
    if result == "PASS":
        return "Low"
    if failure_year is not None and failure_year <= duration // 3:
        return "High"
    return "Medium"


def run_stress_tests(
    scenario: RetirementScenario,
    opening_corpus: Optional[float] = None,
) -> List[StressTestResult]:
    """
    Run the predefined suite of six deterministic stress tests (FR-029).

    Each test uses *opening_corpus* as the starting corpus.
    If *opening_corpus* is None, ``scenario.current_assets`` is used.

    Returns a list of :class:`StressTestResult` objects, one per test.
    """
    corpus = opening_corpus if opening_corpus is not None else scenario.current_assets
    duration = scenario.retirement_duration_years
    results: List[StressTestResult] = []

    # ── 1. Early Market Crash (Section 8.1) ──────────────────────────────
    crash_seq = [-0.25] + [scenario.typical_return] * (duration - 1)
    sim = simulate(scenario, corpus, scenario.typical_return,
                   return_rate_sequence=crash_seq)
    results.append(StressTestResult(
        test_name="Early Market Crash",
        assumptions_changed={"year_1_return": -0.25,
                             "subsequent_return": scenario.typical_return},
        result=sim.result,
        failure_year=sim.failure_year,
        ending_corpus=sim.ending_corpus,
        severity=_classify_severity(sim.result, sim.failure_year, duration),
    ))

    # ── 2. Prolonged Weak Returns (Section 8.2) ───────────────────────────
    weak_seq = ([scenario.conservative_return] * 5
                + [scenario.typical_return] * max(duration - 5, 0))
    sim = simulate(scenario, corpus, scenario.typical_return,
                   return_rate_sequence=weak_seq)
    results.append(StressTestResult(
        test_name="Prolonged Weak Returns",
        assumptions_changed={"years_1_5_return": scenario.conservative_return,
                             "remaining_return": scenario.typical_return},
        result=sim.result,
        failure_year=sim.failure_year,
        ending_corpus=sim.ending_corpus,
        severity=_classify_severity(sim.result, sim.failure_year, duration),
    ))

    # ── 3. Elevated Inflation (Section 8.3) ──────────────────────────────
    high_inf = dataclasses.replace(scenario,
                                   inflation_rate=scenario.inflation_rate + 0.02)
    sim = simulate(high_inf, corpus, scenario.typical_return)
    results.append(StressTestResult(
        test_name="Elevated Inflation",
        assumptions_changed={"inflation_rate": high_inf.inflation_rate},
        result=sim.result,
        failure_year=sim.failure_year,
        ending_corpus=sim.ending_corpus,
        severity=_classify_severity(sim.result, sim.failure_year, duration),
    ))

    # ── 4. Longer Retirement (Section 8.4) ───────────────────────────────
    long_ret = dataclasses.replace(scenario,
                                   retirement_duration_years=duration + 10)
    sim = simulate(long_ret, corpus, scenario.typical_return)
    results.append(StressTestResult(
        test_name="Longer Retirement",
        assumptions_changed={"retirement_duration_years": long_ret.retirement_duration_years},
        result=sim.result,
        failure_year=sim.failure_year,
        ending_corpus=sim.ending_corpus,
        severity=_classify_severity(sim.result, sim.failure_year,
                                    long_ret.retirement_duration_years),
    ))

    # ── 5. Temporary Spending Increase (Section 8.5) ─────────────────────
    spend_seq = [1.20] * 5 + [1.0] * max(duration - 5, 0)
    sim = simulate(scenario, corpus, scenario.typical_return,
                   expense_multiplier_sequence=spend_seq)
    results.append(StressTestResult(
        test_name="Temporary Spending Increase",
        assumptions_changed={"years_1_5_expense_multiplier": 1.20},
        result=sim.result,
        failure_year=sim.failure_year,
        ending_corpus=sim.ending_corpus,
        severity=_classify_severity(sim.result, sim.failure_year, duration),
    ))

    # ── 6. Loss of Passive Income (Section 8.6) ───────────────────────────
    no_passive = dataclasses.replace(scenario, annual_passive_income=0.0)
    sim = simulate(no_passive, corpus, scenario.typical_return)
    results.append(StressTestResult(
        test_name="Loss of Passive Income",
        assumptions_changed={"annual_passive_income": 0.0},
        result=sim.result,
        failure_year=sim.failure_year,
        ending_corpus=sim.ending_corpus,
        severity=_classify_severity(sim.result, sim.failure_year, duration),
    ))

    return results
