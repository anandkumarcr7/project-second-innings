# Project Second Innings
## Release Notes

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
