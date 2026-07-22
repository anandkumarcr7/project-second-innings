"""
Automated unit tests for Project Second Innings.

Test cases are derived from the Verification Plan (docs/06_Verification_Plan.md).
"""

from __future__ import annotations

import dataclasses
import json
import math
import tempfile
from pathlib import Path

import pytest

from second_innings.engine import (
    calculate_fi_targets,
    run_stress_tests,
    simulate,
    solve_minimum_corpus,
)
from second_innings.models import RetirementScenario
from second_innings.scenario_io import load_scenario, save_scenario


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def _make_scenario(**overrides) -> RetirementScenario:
    """Return a baseline scenario; keyword arguments override defaults."""
    defaults = dict(
        scenario_name="Test",
        current_age=38,
        retirement_age=40,
        retirement_duration_years=10,
        monthly_expenses=100_000,        # ₹1 lakh / month → ₹12 lakh / year
        current_assets=12_000_000,       # ₹1.2 Cr
        annual_passive_income=0.0,
        inflation_rate=0.0,
        conservative_return=0.07,
        typical_return=0.09,
        optimistic_return=0.11,
        effective_tax_rate=0.0,
        currency="INR",
    )
    defaults.update(overrides)
    return RetirementScenario(**defaults)


# ---------------------------------------------------------------------------
# TC-001  Zero return, zero inflation — exact depletion
# ---------------------------------------------------------------------------

class TestTC001ZeroReturnZeroInflation:
    def test_corpus_decreases_by_annual_expense_each_year(self):
        scenario = _make_scenario(
            retirement_duration_years=10,
            monthly_expenses=100_000,   # ₹12 lakh / year
            current_assets=12_000_000,
        )
        result = simulate(scenario, 12_000_000, 0.0)
        annual = 1_200_000
        for record in result.projection:
            expected_close = 12_000_000 - record.year * annual
            assert math.isclose(record.closing_corpus, expected_close, abs_tol=1.0), (
                f"Year {record.year}: expected {expected_close}, got {record.closing_corpus}"
            )

    def test_ending_corpus_is_zero(self):
        scenario = _make_scenario(retirement_duration_years=10,
                                   monthly_expenses=100_000,
                                   current_assets=12_000_000)
        result = simulate(scenario, 12_000_000, 0.0)
        assert math.isclose(result.ending_corpus, 0.0, abs_tol=1.0)

    def test_result_is_pass(self):
        scenario = _make_scenario(retirement_duration_years=10,
                                   monthly_expenses=100_000,
                                   current_assets=12_000_000)
        result = simulate(scenario, 12_000_000, 0.0)
        assert result.result == "PASS"
        assert result.failure_year is None


# ---------------------------------------------------------------------------
# TC-002  Insufficient corpus — failure correctly identified
# ---------------------------------------------------------------------------

class TestTC002InsufficientCorpus:
    def test_result_is_fail(self):
        scenario = _make_scenario(retirement_duration_years=10,
                                   monthly_expenses=100_000)
        result = simulate(scenario, 10_000_000, 0.0)  # ₹1 Cr < ₹1.2 Cr needed
        assert result.result == "FAIL"

    def test_failure_year_identified(self):
        scenario = _make_scenario(retirement_duration_years=10,
                                   monthly_expenses=100_000)
        result = simulate(scenario, 10_000_000, 0.0)
        # 10M / 1.2M ≈ 8.33 → fails in year 9
        assert result.failure_year == 9

    def test_failure_year_has_negative_corpus(self):
        scenario = _make_scenario(retirement_duration_years=10,
                                   monthly_expenses=100_000)
        result = simulate(scenario, 10_000_000, 0.0)
        fy = result.failure_year
        assert fy is not None
        assert result.projection[fy - 1].closing_corpus < 0


# ---------------------------------------------------------------------------
# TC-003  Return equals inflation — no unexpected drift
# ---------------------------------------------------------------------------

class TestTC003ReturnEqualsInflation:
    def test_simulation_runs_without_error(self):
        scenario = _make_scenario(
            inflation_rate=0.07,
            typical_return=0.07,
            retirement_duration_years=10,
        )
        result = simulate(scenario, 12_000_000, 0.07)
        assert len(result.projection) == 10

    def test_all_year_values_are_finite(self):
        scenario = _make_scenario(inflation_rate=0.07, typical_return=0.07,
                                   retirement_duration_years=10)
        result = simulate(scenario, 12_000_000, 0.07)
        for rec in result.projection:
            assert math.isfinite(rec.closing_corpus)


# ---------------------------------------------------------------------------
# TC-004  Passive income exactly covers expenses
# ---------------------------------------------------------------------------

class TestTC004PassiveIncomeCoversExpenses:
    def test_net_withdrawal_is_zero_every_year(self):
        scenario = _make_scenario(
            annual_passive_income=1_200_000,  # = annual expense
            inflation_rate=0.0,
            monthly_expenses=100_000,
        )
        result = simulate(scenario, 10_000_000, 0.0)
        for rec in result.projection:
            assert math.isclose(rec.net_withdrawal, 0.0, abs_tol=1.0)

    def test_corpus_stays_constant(self):
        scenario = _make_scenario(
            annual_passive_income=1_200_000,
            inflation_rate=0.0,
            monthly_expenses=100_000,
        )
        result = simulate(scenario, 10_000_000, 0.0)
        for rec in result.projection:
            assert math.isclose(rec.closing_corpus, 10_000_000, abs_tol=1.0)

    def test_result_is_pass(self):
        scenario = _make_scenario(
            annual_passive_income=1_200_000,
            inflation_rate=0.0,
            monthly_expenses=100_000,
        )
        result = simulate(scenario, 10_000_000, 0.0)
        assert result.result == "PASS"


# ---------------------------------------------------------------------------
# TC-005  Passive income exceeds expenses — no negative withdrawal
# ---------------------------------------------------------------------------

class TestTC005PassiveIncomeExceedsExpenses:
    def test_net_withdrawal_never_negative(self):
        scenario = _make_scenario(
            annual_passive_income=2_000_000,  # > ₹12 lakh expense
            inflation_rate=0.0,
            monthly_expenses=100_000,
        )
        result = simulate(scenario, 5_000_000, 0.0)
        for rec in result.projection:
            assert rec.net_withdrawal >= 0.0

    def test_corpus_does_not_decrease_with_zero_return(self):
        """Corpus should be non-decreasing when passive income > expenses and return = 0."""
        scenario = _make_scenario(
            annual_passive_income=2_000_000,
            inflation_rate=0.0,
            monthly_expenses=100_000,
        )
        result = simulate(scenario, 5_000_000, 0.0)
        for rec in result.projection:
            assert rec.closing_corpus >= rec.opening_corpus - 1.0  # within tolerance


# ---------------------------------------------------------------------------
# TC-006  Expense inflation — first three years match reference values
# ---------------------------------------------------------------------------

class TestTC006ExpenseInflation:
    def test_expenses_compound_correctly(self):
        scenario = _make_scenario(
            inflation_rate=0.10,
            monthly_expenses=100_000,  # base annual = ₹12 lakh
            retirement_duration_years=5,
        )
        result = simulate(scenario, 100_000_000, 0.0)
        base = 1_200_000
        assert math.isclose(result.projection[0].expenses, base * 1.00, rel_tol=1e-6)
        assert math.isclose(result.projection[1].expenses, base * 1.10, rel_tol=1e-6)
        assert math.isclose(result.projection[2].expenses, base * 1.21, rel_tol=1e-6)


# ---------------------------------------------------------------------------
# TC-007  Zero inflation — expenses stay constant
# ---------------------------------------------------------------------------

class TestTC007ZeroInflation:
    def test_annual_expenses_unchanged(self):
        scenario = _make_scenario(inflation_rate=0.0, monthly_expenses=100_000,
                                   retirement_duration_years=10)
        result = simulate(scenario, 50_000_000, 0.0)
        for rec in result.projection:
            assert math.isclose(rec.expenses, 1_200_000, abs_tol=1.0)


# ---------------------------------------------------------------------------
# TC-008  Tax applied only to positive return
# ---------------------------------------------------------------------------

class TestTC008PositiveReturnTax:
    def test_tax_applied_on_positive_growth(self):
        scenario = _make_scenario(
            effective_tax_rate=0.20,
            inflation_rate=0.0,
            retirement_duration_years=1,
        )
        result = simulate(scenario, 1_000_000, 0.05)
        rec = result.projection[0]
        expected_gross = 1_000_000 * 0.05       # 50,000
        expected_tax = expected_gross * 0.20     # 10,000
        assert math.isclose(rec.taxes, expected_tax, abs_tol=0.01)
        assert math.isclose(rec.investment_growth, expected_gross - expected_tax, abs_tol=0.01)


# ---------------------------------------------------------------------------
# TC-009  No tax on negative return
# ---------------------------------------------------------------------------

class TestTC009NegativeReturnNoTax:
    def test_tax_is_zero_on_negative_return(self):
        scenario = _make_scenario(
            effective_tax_rate=0.20,
            inflation_rate=0.0,
            retirement_duration_years=1,
        )
        result = simulate(scenario, 1_000_000, -0.05)
        rec = result.projection[0]
        assert math.isclose(rec.taxes, 0.0, abs_tol=0.01)

    def test_net_growth_equals_gross_on_negative_return(self):
        scenario = _make_scenario(effective_tax_rate=0.20, inflation_rate=0.0,
                                   retirement_duration_years=1)
        result = simulate(scenario, 1_000_000, -0.05)
        rec = result.projection[0]
        expected = 1_000_000 * -0.05   # -50,000
        assert math.isclose(rec.investment_growth, expected, abs_tol=0.01)


# ---------------------------------------------------------------------------
# TC-010  Zero tax rate — net growth equals gross growth
# ---------------------------------------------------------------------------

class TestTC010ZeroTaxRate:
    def test_net_growth_equals_gross_growth(self):
        scenario = _make_scenario(effective_tax_rate=0.0, inflation_rate=0.0,
                                   retirement_duration_years=1)
        result = simulate(scenario, 1_000_000, 0.09)
        rec = result.projection[0]
        expected = 1_000_000 * 0.09
        assert math.isclose(rec.taxes, 0.0, abs_tol=0.01)
        assert math.isclose(rec.investment_growth, expected, abs_tol=0.01)


# ---------------------------------------------------------------------------
# TC-011  Solver finds correct corpus (zero return, zero inflation)
# ---------------------------------------------------------------------------

class TestTC011SolverFindsCorrctCorpus:
    def test_simple_case_matches_annual_x_duration(self):
        """Required corpus = annual_expense × duration when return = inflation = 0."""
        scenario = _make_scenario(
            inflation_rate=0.0,
            monthly_expenses=100_000,
            retirement_duration_years=10,
        )
        expected = 1_200_000 * 10  # 12,000,000
        result = solve_minimum_corpus(scenario, 0.0)
        assert math.isclose(result, expected, abs_tol=2.0)


# ---------------------------------------------------------------------------
# TC-012  Solver convergence — returns a passing corpus
# ---------------------------------------------------------------------------

class TestTC012SolverConvergence:
    def test_solved_corpus_passes_simulation(self):
        scenario = _make_scenario(
            inflation_rate=0.07,
            monthly_expenses=100_000,
            retirement_duration_years=30,
        )
        corpus = solve_minimum_corpus(scenario, scenario.typical_return)
        sim = simulate(scenario, corpus, scenario.typical_return)
        assert sim.result == "PASS"

    def test_one_rupee_below_fails(self):
        scenario = _make_scenario(
            inflation_rate=0.07,
            monthly_expenses=100_000,
            retirement_duration_years=30,
        )
        corpus = solve_minimum_corpus(scenario, scenario.typical_return)
        sim = simulate(scenario, corpus - 2.0, scenario.typical_return)
        assert sim.result == "FAIL"


# ---------------------------------------------------------------------------
# TC-013  Solver upper-bound expansion
# ---------------------------------------------------------------------------

class TestTC013UpperBoundExpansion:
    def test_solver_works_with_pessimistic_initial_estimate(self):
        """High inflation scenario requires a corpus far above naive initial bound."""
        scenario = _make_scenario(
            inflation_rate=0.10,
            monthly_expenses=100_000,
            retirement_duration_years=40,
            effective_tax_rate=0.10,
        )
        corpus = solve_minimum_corpus(scenario, 0.03)  # very low return
        sim = simulate(scenario, corpus, 0.03)
        assert sim.result == "PASS"


# ---------------------------------------------------------------------------
# TC-014  Target ordering: Sleep Okay ≤ Sleep Well ≤ Sleep Best
# ---------------------------------------------------------------------------

class TestTC014TargetOrdering:
    def test_sleep_okay_le_sleep_well_le_sleep_best(self):
        scenario = _make_scenario(
            inflation_rate=0.07,
            monthly_expenses=150_000,
            retirement_duration_years=40,
            sleep_well_margin=0.10,
            sleep_best_margin=0.25,
        )
        fi = calculate_fi_targets(scenario)
        assert fi.sleep_okay_corpus <= fi.sleep_well_corpus + 1.0
        assert fi.sleep_well_corpus <= fi.sleep_best_corpus + 1.0


# ---------------------------------------------------------------------------
# TC-015  FI Achieved
# ---------------------------------------------------------------------------

class TestTC015FIAchieved:
    def test_fi_achieved_when_assets_gte_target(self):
        scenario = _make_scenario(
            inflation_rate=0.07,
            monthly_expenses=100_000,
            retirement_duration_years=10,
            current_assets=500_000_000,  # very large corpus
        )
        fi = calculate_fi_targets(scenario, selected_target="sleep_best")
        assert fi.fi_status == "FI Achieved"
        assert fi.funding_gap <= 0.0
        assert fi.percent_complete >= 100.0


# ---------------------------------------------------------------------------
# TC-016  Not Yet FI
# ---------------------------------------------------------------------------

class TestTC016NotYetFI:
    def test_not_yet_fi_when_assets_lt_target(self):
        scenario = _make_scenario(
            inflation_rate=0.07,
            monthly_expenses=200_000,
            retirement_duration_years=40,
            current_assets=1_000,  # trivially small
        )
        fi = calculate_fi_targets(scenario, selected_target="sleep_okay")
        assert fi.fi_status == "Not Yet FI"
        assert fi.funding_gap > 0.0
        assert fi.percent_complete < 100.0


# ---------------------------------------------------------------------------
# TC-017  Stress: early crash corpus >= baseline
# ---------------------------------------------------------------------------

class TestTC017EarlyCrashCorpus:
    def test_crash_corpus_gte_baseline(self):
        scenario = _make_scenario(
            inflation_rate=0.07,
            monthly_expenses=100_000,
            retirement_duration_years=30,
        )
        baseline = solve_minimum_corpus(scenario, scenario.typical_return)
        crash_seq = [-0.25] + [scenario.typical_return] * 29
        crash_corpus = solve_minimum_corpus(scenario, scenario.typical_return,
                                            return_rate_sequence=crash_seq)
        assert crash_corpus >= baseline - 1.0


# ---------------------------------------------------------------------------
# TC-018  Stress: elevated inflation corpus >= baseline
# ---------------------------------------------------------------------------

class TestTC018ElevatedInflationCorpus:
    def test_higher_inflation_needs_more_corpus(self):
        base_scenario = _make_scenario(inflation_rate=0.07, monthly_expenses=100_000,
                                        retirement_duration_years=30)
        high_inf = dataclasses.replace(base_scenario, inflation_rate=0.09)

        base_corpus = solve_minimum_corpus(base_scenario, base_scenario.typical_return)
        high_corpus = solve_minimum_corpus(high_inf, high_inf.typical_return)
        assert high_corpus >= base_corpus - 1.0


# ---------------------------------------------------------------------------
# TC-019  Stress: longer retirement corpus >= baseline
# ---------------------------------------------------------------------------

class TestTC019LongerRetirementCorpus:
    def test_longer_duration_needs_more_corpus(self):
        base_scenario = _make_scenario(inflation_rate=0.07, monthly_expenses=100_000,
                                        retirement_duration_years=30)
        long_scenario = dataclasses.replace(base_scenario, retirement_duration_years=40)

        base_corpus = solve_minimum_corpus(base_scenario, base_scenario.typical_return)
        long_corpus = solve_minimum_corpus(long_scenario, long_scenario.typical_return)
        assert long_corpus >= base_corpus - 1.0


# ---------------------------------------------------------------------------
# TC-020  Stress: loss of passive income does not improve outcomes
# ---------------------------------------------------------------------------

class TestTC020LossOfPassiveIncome:
    def test_no_passive_income_needs_more_corpus(self):
        scenario_with = _make_scenario(
            annual_passive_income=600_000,
            inflation_rate=0.07,
            monthly_expenses=100_000,
            retirement_duration_years=30,
        )
        scenario_without = dataclasses.replace(scenario_with, annual_passive_income=0.0)

        corpus_with = solve_minimum_corpus(scenario_with, scenario_with.typical_return)
        corpus_without = solve_minimum_corpus(scenario_without, scenario_without.typical_return)
        assert corpus_without >= corpus_with - 1.0


# ---------------------------------------------------------------------------
# TC-021  Input validation — negative monthly expenses
# ---------------------------------------------------------------------------

class TestTC021NegativeExpense:
    def test_negative_monthly_expenses_raises(self):
        with pytest.raises(ValueError, match="monthly_expenses"):
            _make_scenario(monthly_expenses=-1)

    def test_zero_monthly_expenses_raises(self):
        with pytest.raises(ValueError, match="monthly_expenses"):
            _make_scenario(monthly_expenses=0)


# ---------------------------------------------------------------------------
# TC-022  Input validation — invalid retirement duration
# ---------------------------------------------------------------------------

class TestTC022InvalidDuration:
    def test_zero_duration_raises(self):
        with pytest.raises(ValueError, match="retirement_duration_years"):
            _make_scenario(retirement_duration_years=0)

    def test_negative_duration_raises(self):
        with pytest.raises(ValueError, match="retirement_duration_years"):
            _make_scenario(retirement_duration_years=-5)


# ---------------------------------------------------------------------------
# TC-023  Input validation — invalid tax rate
# ---------------------------------------------------------------------------

class TestTC023InvalidTaxRate:
    def test_negative_tax_rate_raises(self):
        with pytest.raises(ValueError, match="effective_tax_rate"):
            _make_scenario(effective_tax_rate=-0.01)

    def test_tax_rate_above_one_raises(self):
        with pytest.raises(ValueError, match="effective_tax_rate"):
            _make_scenario(effective_tax_rate=1.01)


# ---------------------------------------------------------------------------
# TC-025 / TC-026  Scenario save and reload (including model version)
# ---------------------------------------------------------------------------

class TestTC025SaveReloadScenario:
    def test_reload_matches_original(self):
        scenario = _make_scenario(scenario_name="SaveTest", inflation_rate=0.07)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_scenario.json"
            save_scenario(scenario, path)
            loaded = load_scenario(path)
        assert dataclasses.asdict(loaded) == dataclasses.asdict(scenario)

    def test_saved_json_includes_model_version(self):
        scenario = _make_scenario()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "s.json"
            save_scenario(scenario, path)
            data = json.loads(path.read_text())
        assert "model_version" in data

    def test_saved_json_includes_dates(self):
        scenario = _make_scenario()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "s.json"
            save_scenario(scenario, path)
            data = json.loads(path.read_text())
        assert "saved_date" in data
        assert "last_modified_date" in data


# ---------------------------------------------------------------------------
# TC-027  Scenario load — malformed JSON produces a friendly error
# ---------------------------------------------------------------------------

class TestTC027InvalidScenarioFile:
    def test_malformed_json_raises_value_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bad.json"
            path.write_text("{not valid json", encoding="utf-8")
            with pytest.raises(ValueError, match="Malformed"):
                load_scenario(path)

    def test_missing_fields_raises_value_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "incomplete.json"
            path.write_text(json.dumps({"scenario_name": "only_name"}), encoding="utf-8")
            with pytest.raises(ValueError, match="Invalid scenario data"):
                load_scenario(path)


# ---------------------------------------------------------------------------
# UC-010  Projected assets at retirement
# ---------------------------------------------------------------------------

class TestUC010ProjectedAssets:
    def test_zero_savings_projected_equals_current(self):
        scenario = _make_scenario(average_annual_savings=0)
        fi = calculate_fi_targets(scenario)
        assert math.isclose(fi.projected_assets, scenario.current_assets, abs_tol=1.0)

    def test_projected_assets_formula(self):
        scenario = _make_scenario(
            current_age=38,
            retirement_age=45,
            average_annual_savings=1_000_000,  # ₹10 lakh / year
            current_assets=10_000_000,
        )
        expected = 10_000_000 + (45 - 38) * 1_000_000  # = 17_000_000
        fi = calculate_fi_targets(scenario)
        assert math.isclose(fi.projected_assets, expected, abs_tol=1.0)

    def test_fi_status_uses_projected_assets(self):
        """Savings should be able to push status from Not Yet FI to FI Achieved."""
        scenario_without = _make_scenario(
            current_age=38,
            retirement_age=45,
            monthly_expenses=100_000,
            retirement_duration_years=10,
            current_assets=1_000,        # well below target
            average_annual_savings=0,
        )
        fi_without = calculate_fi_targets(scenario_without, selected_target="sleep_okay")
        assert fi_without.fi_status == "Not Yet FI"

        scenario_with = dataclasses.replace(
            scenario_without, average_annual_savings=5_000_000
        )
        fi_with = calculate_fi_targets(scenario_with, selected_target="sleep_okay")
        assert fi_with.fi_status == "FI Achieved"

    def test_funding_gap_uses_projected_assets(self):
        scenario = _make_scenario(
            current_age=38,
            retirement_age=45,
            average_annual_savings=1_000_000,
            current_assets=10_000_000,
            monthly_expenses=100_000,
            retirement_duration_years=10,
        )
        fi = calculate_fi_targets(scenario, selected_target="sleep_okay")
        expected_projected = 10_000_000 + 7 * 1_000_000
        assert math.isclose(fi.funding_gap, fi.sleep_okay_corpus - expected_projected, abs_tol=2.0)

    def test_negative_savings_raises(self):
        with pytest.raises(ValueError, match="average_annual_savings"):
            _make_scenario(average_annual_savings=-1)
