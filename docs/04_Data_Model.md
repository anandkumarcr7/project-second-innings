# Project Second Innings
## Data Model

**Version:** 0.1  
**Status:** Draft  

---

# 1. Purpose

Define the main data structures used by the application.

The initial model should remain simple enough to understand, test, save, and extend.

---

# 2. Retirement Scenario

A retirement scenario contains all user assumptions.

| Field | Type | Description |
|---|---|---|
| scenario_name | text | User-defined scenario name |
| current_age | number | User's current age |
| retirement_age | number | Planned retirement age |
| retirement_duration_years | number | Number of retirement years |
| monthly_expenses | currency | Current monthly retirement expenses (today's money) |
| current_assets | currency | Current investable assets |
| annual_passive_income | currency | Passive income after retirement |
| average_annual_savings | currency | Savings added each pre-retirement year |
| inflation_rate | percentage | Expected annual inflation |
| risk_free_return | percentage | Risk-free / FD rate — used for Sleep Best target |
| conservative_return | percentage | Conservative annual return — used for Sleep Well target |
| typical_return | percentage | Typical annual return — used for Sleep Okay target |
| optimistic_return | percentage | Optimistic annual return |
| effective_tax_rate | percentage | Simplified tax rate on returns |
| currency | text | Display currency — "INR" or "USD" |
| model_version | text | Calculation model version |

---

# 3. Annual Projection Record

The simulation generates one record for each retirement year.

| Field | Type | Description |
|---|---|---|
| year | integer | Retirement year number |
| age | number | User age during the year |
| opening_corpus | currency | Corpus / nest egg at the start of the year |
| gross_investment_growth | currency | Investment growth before tax |
| taxes | currency | Tax applied to positive growth |
| investment_growth | currency | Net growth after tax (gross − taxes) |
| expenses | currency | Inflation-adjusted annual expenses |
| passive_income | currency | Passive income received |
| net_withdrawal | currency | Expenses less passive income |
| closing_corpus | currency | Corpus / nest egg at the end of the year |
| real_closing_corpus | currency | Closing corpus in today's purchasing power |
| status | text | PASS or FAIL |

---

# 4. Simulation Result

A simulation result contains:

| Field | Description |
|---|---|
| scenario | Assumptions used |
| opening_corpus | Starting corpus |
| ending_corpus | Corpus at end of retirement |
| result | PASS or FAIL |
| failure_year | First failed year, if any |
| projection | Annual projection records |

---

# 5. FI Target Result

The corpus calculator returns:

| Field | Description |
|---|---|
| sleep_okay_corpus | Minimum corpus assuming typical return |
| sleep_well_corpus | Minimum corpus assuming conservative return |
| sleep_best_corpus | Minimum corpus assuming risk-free / FD return |
| current_assets | Current investable assets |
| projected_assets | Current assets compounded to retirement + savings |
| selected_target | Target selected by user |
| funding_gap | Selected target minus projected assets |
| percent_complete | Projected assets as % of selected target |
| fi_status | FI Achieved or Not Yet FI |

---

# 6. Stress-Test Result

Each stress-test result contains:

| Field | Description |
|---|---|
| test_name | Name of stress scenario |
| assumptions_changed | Changes from base scenario |
| result | PASS or FAIL |
| failure_year | First failure year |
| ending_corpus | Corpus remaining at end |
| severity | Relative severity of failure |

---

# 7. Saved Scenario

Saved scenarios will use JSON.

Example:

```json
{
  "scenario_name": "India 2028",
  "current_age": 38,
  "retirement_age": 40,
  "retirement_duration_years": 40,
  "monthly_expenses": 200000,
  "current_assets": 114000000,
  "annual_passive_income": 0,
  "average_annual_savings": 0,
  "inflation_rate": 0.07,
  "risk_free_return": 0.04,
  "conservative_return": 0.07,
  "typical_return": 0.09,
  "optimistic_return": 0.11,
  "effective_tax_rate": 0.10,
  "currency": "INR",
  "model_version": "0.1"
}
```

For a USD scenario, set `"currency": "USD"`. Monetary values are always stored as plain numbers; the currency field controls display formatting only.