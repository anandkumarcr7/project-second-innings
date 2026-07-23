# Project Second Innings
## Detailed Design

**Version:** 0.3  
**Status:** Draft

---

# 1. Purpose

Define the calculation method used to estimate the Financial Independence corpus and generate the retirement projection.

The initial model will be:

- deterministic,
- annual,
- inflation-aware,
- tax-aware,
- and easy to verify manually.

---

# 2. Annual Simulation Flow

For every retirement year:

1. Start with the opening corpus.
2. Calculate investment growth.
3. Apply tax to investment growth.
4. Inflate annual expenses.
5. Calculate passive income.
6. Withdraw the remaining expense from the corpus.
7. Calculate the closing corpus.
8. Repeat for the next year.

---

# 3. Core Equations

## 3.1 Annual Expense

The user enters current monthly expenses.

```text
Base Annual Expense = Monthly Expense × 12

Annual Expense(n)
    = Base Annual Expense × (1 + Inflation Rate)^(n - 1)

```

## 3.2 Investment Growth
Gross Growth(n)
    = Opening Corpus(n) × Annual Return

## 3.3 Tax on Investment Growth
Tax(n)
    = max(Gross Growth(n), 0) × Effective Tax Rate

Net Growth(n)
    = Gross Growth(n) - Tax(n)

** No tax is applied on negative returns

## 3.4 Passive Income
Net Withdrawal(n)
    = max(Annual Expense(n) - Passive Income(n), 0)

## 3.5 Closing Corpus
Closing Corpus(n)
    = Opening Corpus(n)
    + Net Growth(n)
    - Net Withdrawal(n)

Opening Corpus(n + 1)
    = Closing Corpus(n)

## 3.6 Real Corpus
Real Closing Corpus(n)
    = Closing Corpus(n) / (1 + Inflation Rate)^n

# PASS and FAIL Definition
PASS:
Closing Corpus(n) >= 0 for every year

FAIL:
Closing Corpus(n) < 0 in any year

# 5. Minimum Corpus Solver
The system will determine the minimum starting corpus using binary search.

## 5.1 Solver Process
- Select a lower corpus bound.
- Select an upper corpus bound.
- Calculate the midpoint.
- Run the retirement simulation using the midpoint corpus.
- If the simulation passes, reduce the upper bound.
- If the simulation fails, increase the lower bound.
- Repeat until the difference between bounds is within tolerance.

low = 0
high = initial_upper_bound

while high - low > tolerance:

    trial_corpus = (low + high) / 2

    result = simulate(trial_corpus)

    if result passes:
        high = trial_corpus
    else:
        low = trial_corpus

minimum_corpus = high

# 6. FI Targets
## 6.1 Sleep Okay
Minimum corpus required under the typical return assumption.
Sleep Okay
    = Minimum Corpus using Typical Return

## 6.2 Sleep Well
Sleep Well
    = Stress-Test Corpus × (1 + Sleep Well Margin)

## 6.3 Sleep Best
Sleep Best
    = Minimum Corpus using risk-free Return
      × (1 + Sleep Best Margin)

# 7. Financial Independence Status

## 7.1 Projected Assets at Retirement

Before evaluating the funding gap, current assets are augmented with expected
future savings accumulated between now and the planned retirement age.

```text
Years to Retirement
    = Retirement Age - Current Age

Projected Assets
    = Current Assets + Years to Retirement × Average Annual Savings
```

When Average Annual Savings = 0, Projected Assets = Current Assets and all
existing FI calculations are unchanged.

## 7.2 Funding Gap and FI Status

```text
Funding Gap
    = Selected Target Corpus - Projected Assets

Percent Complete
    = Projected Assets / Selected Target Corpus × 100

FI Achieved:
Projected Assets >= Selected Target Corpus

Not Yet FI:
Projected Assets < Selected Target Corpus
```

A negative funding gap represents surplus assets.

The retirement projection and stress tests use Projected Assets as the
opening corpus, not Current Assets.

# 8. Initial Stress Tests
## 8.1 Early Market Crash
Apply a negative return during the first retirement year.
Example, Year 1 Return = -25%
Subsequent Years = Typical Return

## 8.2 Prolonged Weak Returns

Reduce annual returns for an initial period.

Example:

Years 1–5 Return = Conservative Return
Remaining Years = Typical Return

## 8.3 Elevated Inflation

Increase inflation above the base assumption.

Example:

Stress Inflation
    = Base Inflation + 2%


## 8.4 Longer Retirement

Extend the retirement duration.

Example:

Stress Duration
    = Base Duration + 10 years

## 8.5 Temporary Spending Increase

Increase expenses for a selected period.

Example:

Years 1–5 Expenses
    = Base Expenses × 1.20

## 8.6 Loss of Passive Income
Set passive income to zero.

# 9 Calculation Order

The initial annual model will use the following order:

Opening Corpus
    ↓
Investment Growth
    ↓
Tax on Positive Growth
    ↓
Expense Withdrawal
    ↓
Closing Corpus

This assumes returns occur before annual expenses are withdrawn.

The calculation order must remain consistent because changing it can alter the required corpus.

# 10. Solver Tolerance

The solver does not need to identify the corpus to the nearest rupee.

Proposed initial tolerance:

₹1,000

For large crore-scale calculations, this provides more than sufficient precision.

# 11. Multi-Scenario Projection Chart

The retirement projection chart displays three closing corpus trajectories
simultaneously. All three simulations use the same opening corpus (Projected
Assets at Retirement) and the same expense and inflation assumptions. Only the
annual return rate differs.

| Curve | Return Rate Used | Colour |
|---|---|---|
| Optimistic | `optimistic_return` | Green |
| Typical (Base Case) | `typical_return` | Blue |
| Conservative | `conservative_return` | Red |

The legend labels each curve with its scenario name and the actual return
percentage (e.g. "Typical (8%)") so the reader can immediately identify the
assumptions without consulting the sidebar.

The chart does not display real (inflation-adjusted) corpus; the year-by-year
table below the chart provides that column for users who need it.