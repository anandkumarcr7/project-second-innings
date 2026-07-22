# UC-001 - Determine Financial Independence Corpus Required
## Goal 
- Determine the minimum corpus required to achieve Financial Independence (FI) under the selected assumptions and indicate whether the user's current assets satisfy the target
## Primary Actor
- User
## Pre-Conditions
- Retirement Assumptions entered
## Inputs
- Monthly Expenses
- Inflation
- Returns
- Passive Income
- Retirement Duration
## Outputs
- Sleep Okay
- Sleep Well
- Sleep Best
## Acceptance Criteria
Corpus Calculated successfully

# UC-002 - Compare Current Assets
## Goal
- "Am I on track for FI (Financial Independence)"
## Outpus
- Current Assets = ₹11.4 Cr
- Target = ₹15.6 Cr
- Gap = ₹4.2 Cr 
- Status or Gap in %

# UC-003 - View Retirement Projection
## Goal
- 40 year table showing 
| Year | Opening Corpus | Investment Return | Expenses | Passive Income | Closing Corpus |

# UC-004 - Stress Test
-  A "Run Stress Test" button that outputs PASS/FAIL and also a success rate = x%

# UC-005 - Turning the knobs for "What if" analysis
- User changes monthly spending or inflation or retirement age etc. Everything must update instantly

# UC-006 - Save Scenario
- User has the ability to save different scenarios

# UC-007 - Export
- Generate CSV and / or PDF

# UC-008 - Review Assumptions
- Ensure that the user understands assumptions behind every result
- Outputs
    - Inflation = 7%
    - Return = 9%
    - Retirement Duration = 40 years
    - Passive Income = 0

# UC-009 - Compare Scenarios
- Compare Scenario A vs Scenario B side by side

# UC-010 - Project Assets at Retirement
## Goal
- Estimate how much investable corpus the user will have accumulated by the planned retirement age, by augmenting current assets with future savings
## Primary Actor
- User
## Inputs
- Current Assets
- Average Annual Savings
- Current Age
- Retirement Age
## Formula
- Projected Assets at Retirement = Current Assets + (Retirement Age − Current Age) × Average Annual Savings
## Outputs
- Projected Assets at Retirement
- Updated FI gap based on projected assets instead of current assets
- Updated FI status (FI Achieved / Not Yet FI) based on projected assets
## Acceptance Criteria
- When Average Annual Savings = 0, Projected Assets = Current Assets and all existing FI calculations are unchanged
- Projected Assets increases linearly with Average Annual Savings
- The 40-year retirement projection and stress tests use Projected Assets as the opening corpus


