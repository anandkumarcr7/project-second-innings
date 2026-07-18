# Project Second Innings
## System Requirements Specification

**Document Version:** 0.1  
**Status:** Draft  
**Project Owners:** Anand Kumar and Harini  

---

# 1. Purpose

This document defines the functional and non-functional requirements for Project Second Innings.

The system will help users estimate the corpus required for Financial Independence, compare current assets against that target, review long-term projections, and evaluate retirement risk under selected assumptions.

---

# 2. Scope

The initial release will provide:

- deterministic retirement simulation,
- corpus calculation,
- comparison of current assets against FI targets,
- 40-year annual projections,
- scenario analysis,
- deterministic stress testing,
- scenario save/load,
- CSV and PDF export,
- local-first data handling.

Monte Carlo simulation, live account integration, and advanced tax modeling are outside the initial release.

---

# 3. Definitions

| Term | Definition |
|---|---|
| FI | Financial Independence |
| Corpus | Investable assets available to fund retirement |
| Sleep Okay | Minimum corpus that passes the nominal retirement model |
| Sleep Well | Corpus that includes additional stress tolerance and design margin |
| Sleep Best | Conservative boundary-condition corpus with the highest design margin |
| Scenario | A named set of retirement assumptions |
| Stress Test | A deterministic adverse-case simulation |
| Real Corpus | Corpus expressed in current purchasing-power terms |
| Passive Income | Income received after retirement that offsets expenses |

---

# 4. Functional Requirements

## 4.1 Input Requirements

### FR-001 — Monthly Expenses

The system shall allow the user to enter current monthly retirement expenses.

### FR-002 — Investable Assets

The system shall allow the user to enter current investable or liquid assets.

### FR-003 — Passive Income

The system shall allow the user to enter expected passive income after retirement.

### FR-004 — Inflation

The system shall allow the user to enter an expected annual inflation rate.

### FR-005 — Return Assumptions

The system shall allow the user to enter:

- conservative return,
- typical return,
- optimistic return.

### FR-006 — Retirement Duration

The system shall allow the user to enter the expected retirement duration in years.

### FR-007 — Retirement Age

The system shall allow the user to enter the planned retirement age.

### FR-008 — Currency

The system shall allow the user to select the display currency.

The initial supported currency shall be INR.

### FR-009 — Tax Rate

The system shall allow the user to enter a simplified effective tax rate on investment returns.

### FR-010 — Design Margin

The system shall allow the user to configure the design margin used for Sleep Well and Sleep Best targets.

---

## 4.2 Corpus Calculation Requirements

### FR-011 — Minimum FI Corpus

The system shall calculate the minimum starting corpus required to sustain the selected retirement lifestyle for the selected retirement duration.

### FR-012 — Sleep Okay Target

The system shall calculate the Sleep Okay corpus using the nominal or typical-return scenario.

### FR-013 — Sleep Well Target

The system shall calculate the Sleep Well corpus using selected stress assumptions and an explicit design margin.

### FR-014 — Sleep Best Target

The system shall calculate the Sleep Best corpus using the conservative return assumption and an explicit design margin.

### FR-015 — Current Asset Comparison

The system shall compare current investable assets against the selected FI corpus target.

### FR-016 — Funding Gap

The system shall calculate and display:

- current assets,
- target corpus,
- absolute funding gap,
- percentage of target achieved.

### FR-017 — FI Status

The system shall display whether the user has achieved FI under the selected target definition.

---

## 4.3 Projection Requirements

### FR-018 — Annual Projection

The system shall generate a year-by-year retirement projection.

### FR-019 — Projection Horizon

The projection shall cover the full selected retirement duration.

The default duration shall be 40 years.

### FR-020 — Projection Columns

The annual projection shall include:

- year,
- age,
- opening corpus,
- investment growth,
- taxes,
- annual expenses,
- passive income,
- net withdrawal,
- closing corpus.

### FR-021 — Real Corpus

The system shall display the inflation-adjusted closing corpus for each year.

### FR-022 — Failure Year

If the corpus is exhausted, the system shall identify the first year in which the closing corpus becomes negative.

### FR-023 — Pass or Fail

The system shall classify a deterministic simulation as PASS or FAIL.

---

## 4.4 Scenario Analysis Requirements

### FR-024 — Interactive Input Changes

The system shall recalculate results when the user changes an input assumption.

### FR-025 — Immediate Update

The system should update deterministic results without requiring the user to reload the application.

### FR-026 — What-If Analysis

The system shall support what-if analysis for at least:

- monthly expenses,
- inflation,
- retirement age,
- retirement duration,
- returns,
- passive income,
- current assets.

### FR-027 — Assumption Summary

The system shall display the active assumptions used to generate each result.

---

## 4.5 Stress-Test Requirements

### FR-028 — Run Stress Test

The system shall provide a user action to run predefined stress tests.

### FR-029 — Initial Stress Scenarios

The initial stress suite shall include:

- early market crash,
- prolonged weak returns,
- elevated inflation,
- longer retirement duration,
- temporary spending increase,
- loss of passive income.

### FR-030 — Stress-Test Result

For each deterministic stress test, the system shall display:

- PASS or FAIL,
- failure year, if applicable,
- ending corpus,
- scenario assumptions.

### FR-031 — Overall Stress Status

The system shall provide an overall stress-test summary.

### FR-032 — Dominant Failure Mode

If one or more stress tests fail, the system should identify the most severe or earliest failure mode.

---

## 4.6 Scenario Management Requirements

### FR-033 — Save Scenario

The system shall allow the user to save a named set of assumptions.

### FR-034 — Load Scenario

The system shall allow the user to load a previously saved scenario.

### FR-035 — Delete Scenario

The system should allow the user to delete a saved scenario.

### FR-036 — Scenario Metadata

A saved scenario shall include:

- scenario name,
- assumptions,
- creation date,
- last modified date,
- model version.

### FR-037 — Compare Scenarios

A future release should allow the user to compare two or more saved scenarios.

---

## 4.7 Export Requirements

### FR-038 — CSV Export

The system shall allow the user to export the annual projection table as CSV.

### FR-039 — PDF Export

The system shall allow the user to generate a PDF summary report.

### FR-040 — Exported Assumptions

Exported reports shall include the assumptions used to generate the results.

### FR-041 — Exported Results

Exported reports shall include:

- Sleep Okay corpus,
- Sleep Well corpus,
- Sleep Best corpus,
- current asset comparison,
- stress-test summary,
- annual projection.

---

# 6. Data Requirements

### DR-001 — Scenario Storage

Saved scenarios shall use a human-readable local format.

JSON is the proposed format for the initial release.

### DR-002 — Private Data Location

Personal data shall be stored in a Git-ignored directory.

Proposed location:

```text
data/private/