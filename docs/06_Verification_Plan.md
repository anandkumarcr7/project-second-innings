# Project Second Innings
# Verification Plan

**Version:** 0.1  
**Status:** Draft

---

# 1. Purpose

This document defines the verification strategy for Project Second Innings.

The objective is to ensure the retirement model is mathematically correct, robust against edge cases, and reliable enough to support financial planning decisions.

The verification plan covers:

- Core financial calculations
- Corpus solver
- Stress testing
- Input validation
- Scenario management
- Export functionality
- End-to-end workflow

---

# 2. Verification Strategy

The project will be verified using the following techniques:

1. Manual reference calculations
2. Automated unit tests
3. Boundary-condition testing
4. End-to-end workflow testing
5. Regression testing

---

# 3. Core Calculation Tests

## TC-001 — Zero Return, Zero Inflation

### Inputs

- Starting corpus: ₹1.2 Cr
- Annual expense: ₹12 lakh
- Return: 0%
- Inflation: 0%
- Passive income: ₹0
- Duration: 10 years

### Expected Result

- Corpus decreases by ₹12 lakh every year.
- Ending corpus after Year 10 is ₹0.
- Result = PASS.

---

## TC-002 — Insufficient Corpus

### Inputs

- Starting corpus: ₹1 Cr
- Annual expense: ₹12 lakh
- Return: 0%
- Inflation: 0%
- Duration: 10 years

### Expected Result

- Corpus becomes negative before the end of Year 10.
- Result = FAIL.
- Failure year is correctly identified.

---

## TC-003 — Return Equals Inflation

### Goal

Verify behavior when annual investment return equals inflation.

### Expected Result

- Annual projection matches independently calculated reference values.
- No unexpected drift in calculations.

---

## TC-004 — Passive Income Covers Expenses

### Inputs

- Annual expense: ₹12 lakh
- Passive income: ₹12 lakh
- Return: 0%

### Expected Result

- Net withdrawal = ₹0.
- Corpus remains unchanged.
- Result = PASS.

---

## TC-005 — Passive Income Exceeds Expenses

### Expected Result

- Net withdrawal shall never become negative.
- Excess passive income shall not increase corpus unless explicitly supported by the model.

---

# 4. Inflation Tests

## TC-006 — Expense Inflation

### Inputs

- Year 1 expense = ₹12 lakh
- Inflation = 10%

### Expected Result

| Year | Annual Expense |
|------|---------------:|
| 1 | ₹12.00 lakh |
| 2 | ₹13.20 lakh |
| 3 | ₹14.52 lakh |

---

## TC-007 — Zero Inflation

### Expected Result

Annual expenses remain constant throughout retirement.

---

# 5. Tax Tests

## TC-008 — Positive Return Tax

### Expected Result

Tax is applied only to positive investment growth.

---

## TC-009 — Negative Return Tax

### Expected Result

No tax is applied when annual investment growth is negative.

---

## TC-010 — Zero Tax Rate

### Expected Result

Net investment growth equals gross investment growth.

---

# 6. Corpus Solver Tests

## TC-011 — Solver Finds Correct Corpus

### Expected Result

For the simple case:

```
Required Corpus = Annual Expense × Retirement Duration
```

The solver returns the expected value within the configured tolerance.

---

## TC-012 — Solver Convergence

### Expected Result

The solver:

- Converges successfully
- Returns a passing corpus
- Meets the configured tolerance

---

## TC-013 — Upper Bound Expansion

### Expected Result

If the initial upper bound is insufficient, the solver automatically expands the search space until a valid solution is found.

---

# 7. Financial Independence Target Tests

## TC-014 — Target Ordering

### Expected Result

```
Sleep Okay ≤ Sleep Well ≤ Sleep Best
```

Any violation shall be flagged.

---

## TC-015 — FI Achieved

### Expected Result

When:

```
Current Assets ≥ Selected Target
```

The application displays:

- FI Achieved
- Funding Gap ≤ 0
- Percent Complete ≥ 100%

---

## TC-016 — FI Not Yet Achieved

### Expected Result

When:

```
Current Assets < Selected Target
```

The application displays:

- Not Yet FI
- Positive funding gap
- Percent Complete < 100%

---

# 8. Stress-Test Verification

## TC-017 — Early Market Crash

### Expected Result

The required corpus shall not decrease compared to the baseline scenario.

---

## TC-018 — Elevated Inflation

### Expected Result

Increasing inflation shall never reduce the required corpus.

---

## TC-019 — Longer Retirement

### Expected Result

Increasing retirement duration shall never reduce the required corpus.

---

## TC-020 — Loss of Passive Income

### Expected Result

Removing passive income shall not improve retirement outcomes.

---

# 9. Input Validation Tests

## TC-021 — Negative Expense

### Expected Result

Negative monthly expenses are rejected.

---

## TC-022 — Invalid Retirement Duration

### Expected Result

Zero or negative retirement duration is rejected.

---

## TC-023 — Invalid Tax Rate

### Expected Result

Unsupported tax values are rejected.

---

## TC-024 — Missing Required Input

### Expected Result

The application displays a clear validation message.

---

# 10. Scenario Management Tests

## TC-025 — Save and Reload Scenario

### Expected Result

Loaded scenario exactly matches the saved values.

---

## TC-026 — Model Version

### Expected Result

Every saved scenario includes the model version.

---

## TC-027 — Invalid Scenario File

### Expected Result

Malformed JSON produces a user-friendly error without crashing the application.

---

# 11. Export Tests

## TC-028 — CSV Export

### Expected Result

The exported CSV exactly matches the projection displayed in the application.

---

## TC-029 — Assumption Export

### Expected Result

Exported files include the assumptions used to generate the results.

---

## TC-030 — PDF Export

### Expected Result

When implemented, the generated PDF matches the displayed results.

---

# 12. End-to-End Acceptance Test

## AT-001 — Complete Financial Independence Workflow

The user shall be able to:

1. Enter retirement assumptions.
2. Calculate FI corpus targets.
3. Compare current assets with the selected target.
4. View the retirement projection.
5. Run stress tests.
6. Save the scenario.
7. Export the results.

### Expected Result

The complete workflow executes successfully without calculation or data integrity errors.

---

# 13. Regression Testing

Whenever a defect is discovered:

1. Create a test that reproduces the defect.
2. Fix the defect.
3. Verify the new test passes.
4. Verify all existing tests continue to pass.

---

# 14. Exit Criteria

The retirement calculation engine is considered verified when:

- All core calculation tests pass.
- All solver tests pass.
- All validation tests pass.
- All stress-test verification cases pass.
- At least one complete reference scenario matches manual calculations.
- No known high-severity calculation defects remain.