# Project Second Innings
## Release Notes

---

## Release 0.8 — 2026-08-12

### New Feature

#### Historical Crisis Replays in the Stress-Test Suite

Five new stress tests replay actual market and inflation history against the
user's own plan: the **Great Depression (1929–38)**, **Stagflation (1973–82)**,
the **Japan Lost Decade (1990–99)**, **Dot-com + GFC (2000–09)**, and
**Retiring into the GFC (2008–17)**.

The 2008 crash appears in two windows on purpose — as year 9 of the 2000–09
window and as year 1 of the 2008–17 window — to expose sequence-of-returns
risk. The same −37% year is survivable late and often fatal early.

Each maps year 1 of retirement to the first year of the crisis and applies that
year's real nominal equity return alongside that year's real CPI print, so the
deflation of the 1930s and the double-digit inflation of the 1970s are modelled
faithfully rather than being flattened into a single average. Years past the
ten-year window revert to the user's own assumptions.

Historical CPI is injected through the existing `expense_multiplier_sequence`
hook, so no change to the core simulation loop was required.

These scenarios assume a 100% equity portfolio and are intentionally severe; a
caption under the stress-test table now says so.

### Bug Fix

- Loading a scenario file crashed with `NameError` because the sidebar JSON
  preview referenced `dataclasses.asdict` while only the `_dc` alias was
  imported.

### Documentation

- Tax-rate tooltip now explains that tax is applied to all annual growth as a
  conservative simplification, whereas real capital-gains tax is only due on
  realised gains at withdrawal.

---

## Release 0.7 — 2026-08-11

### Bug Fix

#### Passive Income Not Counted in Pre-Retirement Corpus Accumulation

**Problem:** `annual_passive_income` was only used to reduce withdrawals during
retirement. Passive income received before retirement (dividends, rental income,
interest) was not contributing to corpus accumulation, understating projected assets.

**Fix:** `calculate_fi_targets()` now adds `annual_passive_income` to
`average_annual_savings` to form the total annual pre-retirement inflow used
in the projected-assets formula. `annual_passive_income` therefore applies to
both phases: it builds the corpus before retirement and offsets withdrawals after.

The sidebar help text and Section 7.1 of the Detailed Design have been updated.

---

## Release 0.6 — 2026-08-09

### UX Improvements

#### Year-by-Year Table Restructured

- **Investment growth split** into three columns: *Gross Investment Growth* (before tax),
  *Taxes*, and *Net Investment Growth* (after tax), making the tax impact explicit.
- **Real Corpus / Nest Egg column removed** — the column showed closing corpus deflated
  to today’s purchasing power; users found it redundant alongside the nominal figure.
- **Status column removed** — FAIL rows are already highlighted in red; the text column
  was redundant.
- **Scenario selector added** — a radio button (Conservative / Typical / Optimistic)
  above the table lets users switch which return scenario the table reflects.
  The CSV download filename includes the selected scenario.

#### Sidebar Layout Compacted

- Current Age and Retirement Age placed side-by-side in two columns.
- Annual Savings and Passive Income placed side-by-side.
- Return Assumptions, Macro & Tax, and FI Target moved into collapsed expanders,
  reducing the initial sidebar height and eliminating the need to scroll for
  most common use cases.

#### Terminology: “Corpus / Nest Egg”

All user-facing labels now read “Corpus / Nest Egg” so the term is accessible
to both Indian users (who know “corpus”) and Western users (who recognise
“nest egg”).

#### Chart Annotation for Negative Corpus Crossings

A caption below the 40-year projection chart explains why higher-return curves
can become more negative than lower-return curves once the corpus is exhausted:
higher rates compound the deficit faster, which is a modelling artefact rather
than a real-world scenario.

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

#### Sleep Well / Sleep Best Redesigned — Return-Rate Based Targets

**Problem:** Sleep Well and Sleep Best shared the same conservative-return base corpus
and only differed by arbitrary percentage margins (10% and 25%), which had no clear
financial meaning and were confusing to users.

**Fix:** Each tier now uses a distinct, user-controlled return-rate assumption:

| Target | Return assumption | Meaning |
|---|---|---|
| Sleep Okay | Typical return | Markets perform as expected |
| Sleep Well | Conservative return | Markets underperform |
| Sleep Best | Risk-free / FD return | Everything in bonds / FDs |

`RetirementScenario` gains a `risk_free_return` field (default 4%) and loses
`sleep_well_margin` and `sleep_best_margin`. The sidebar exposes a
"Risk-Free Return / FD Rate" slider in the Return Assumptions section.

**Impact:** Sleep Best corpus values will generally be larger and more conservative
than before (a 4% FD assumption requires more corpus than conservative-return + 25%).
Section 6 of the Detailed Design has been updated.

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
