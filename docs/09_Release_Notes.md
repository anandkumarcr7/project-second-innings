# Project Second Innings
## Release Notes

---

## Release 0.5 — 2026-08-09

### Bug Fix

#### Pre-Retirement Inflation Not Applied to Monthly Expenses

**Problem:** `monthly_expenses` (entered in today's dollars) was used directly
as the Year-1 retirement expense without inflating it forward to the retirement
date.  For example, \$4,500/month today with a 10-year horizon to retirement
at ~4 % inflation should be ~\$6,661 at retirement, but the engine used \$4,500.

**Fix:** `engine.simulate()` and `engine.solve_minimum_corpus()` now multiply
`monthly_expenses × 12` by `(1 + inflation_rate) ^ years_to_retirement` before
the retirement simulation loop begins.  Section 3.1 of the Detailed Design has
been updated to match.

**Impact:** All corpus calculations (minimum corpus, FI targets, stress tests)
now produce higher, correct values for anyone whose retirement date is in the
future.  Scenarios where `current_age == retirement_age` are unaffected.

#### Projected Assets Used Linear Accumulation Instead of Compound Growth

**Problem:** `projected_assets` was computed as:
`current_assets + years_to_retirement × average_annual_savings`.
This ignored investment growth on the existing corpus during the pre-retirement
period, significantly under-estimating wealth at retirement.

**Fix:** `calculate_fi_targets()` now compounds current assets at the typical
return rate and adds each year's savings with its own compounding tail:

```text
Growth Factor  = (1 + typical_return)^years_to_retirement
Projected Assets
    = current_assets × Growth Factor
      + average_annual_savings × (Growth Factor − 1) / typical_return
```

**Impact:** Projected assets, funding gap, percent-complete, and FI status
now reflect realistic compound growth. Section 7.1 of the Detailed Design
has been updated to match.

---

## Release 0.4 — 2026-07-26

### UX Improvements

#### FI Status and Simulation Clarification

**Problem:** The dashboard displayed "Not Yet FI" at the top and "Simulation: PASS" further down.
Both statements are mathematically correct but appeared contradictory to a first-time user.

**Change:** Added contextual captions to both results to make the distinction explicit.

- **FI Status card** now includes a caption explaining that the status reflects whether
  projected assets meet the selected target corpus, which includes a safety margin above
  the minimum survival corpus.
- **Simulation result banner** now clarifies that the PASS/FAIL result tests whether the
  projected retirement corpus actually covers all expenses over the full retirement duration,
  independently of the selected FI target and its margin.

#### Currency-Aware Default Financial Inputs

**Problem:** Switching the currency selector from INR to USD left the financial input fields
showing INR-scale values (e.g. ₹2,00,000/month and ₹10 Cr assets), which are several orders
of magnitude too large for a USD user.

**Change:** Financial input fields now carry currency-specific default values and reset
automatically when the user switches currency.

| Field | INR Default | USD Default |
|---|---|---|
| Monthly Expenses | ₹2,00,000 | $4,500 |
| Current Investable Assets | ₹10,00,00,000 (₹10 Cr) | $1,200,000 |
| Average Annual Savings | 0 | 0 |
| Annual Passive Income | 0 | 0 |

---

## Release 0.3

Initial working dashboard with FI status, corpus targets, 40-year projection chart,
stress tests, and scenario save/load.
