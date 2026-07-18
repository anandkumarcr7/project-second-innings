# Project Second Innings
## System Architecture Specification

**Document Version:** 0.1  
**Status:** Draft  
**Project Owners:** Anand Kumar and Harini  

---

# 1. Purpose

This document defines the top-level software architecture for Project Second Innings.

The architecture separates:

- user interface,
- financial calculations,
- corpus solving,
- stress testing,
- data persistence,
- reporting,
- and validation.

The primary architectural goal is to ensure that the financial logic can be tested independently of the Streamlit user interface.

---

# 2. Architectural Principles

The system shall follow these principles:

1. Calculation logic shall remain independent of the user interface.
2. Inputs shall be validated before simulation.
3. The same deterministic inputs shall produce the same outputs.
4. Personal financial data shall remain local by default.
5. Every major result shall retain the assumptions used to generate it.
6. Stress scenarios shall reuse the same simulation engine as normal scenarios.
7. Export functions shall consume simulation results rather than recalculate them.
8. The system shall support incremental extension without rewriting the core engine.

---

# 3. System Context

```text
┌─────────────────────────┐
│          User           │
│                         │
│ Anand / Harini / Friend │
└────────────┬────────────┘
             │
             │ Inputs and commands
             ▼
┌─────────────────────────┐
│ Streamlit Web Interface │
└────────────┬────────────┘
             │
             │ Validated assumptions
             ▼
┌─────────────────────────┐
│ Retirement Calculation  │
│ System                  │
└────────────┬────────────┘
             │
             │ Results
             ▼
┌─────────────────────────┐
│ Dashboard / Tables /    │
│ Reports / Exports       │
└─────────────────────────┘

# Top Level Architecture

┌──────────────────────────────────────────────────────┐
│                  Presentation Layer                  │
│                                                      │
│  Streamlit Dashboard                                 │
│  - Input controls                                    │
│  - Result cards                                      │
│  - Projection charts                                 │
│  - Stress-test controls                              │
│  - Scenario management                               │
└────────────────────────┬─────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│                  Application Layer                   │
│                                                      │
│  Scenario Controller                                 │
│  - Coordinates user actions                          │
│  - Selects calculation mode                          │
│  - Builds simulation requests                        │
│  - Formats application-level results                 │
└───────────────┬─────────────────┬────────────────────┘
                │                 │
                ▼                 ▼
┌─────────────────────────┐  ┌─────────────────────────┐
│ Financial Engine        │  │ Stress-Test Engine      │
│                         │  │                         │
│ - Annual simulation     │  │ - Builds adverse cases  │
│ - Inflation             │  │ - Runs test suite       │
│ - Returns               │  │ - Summarizes failures   │
│ - Taxes                 │  │ - Identifies risk       │
│ - Passive income        │  │                         │
└────────────┬────────────┘  └────────────┬────────────┘
             │                            │
             └──────────────┬─────────────┘
                            ▼
                 ┌──────────────────────┐
                 │ Corpus Solver        │
                 │                      │
                 │ - Minimum corpus     │
                 │ - Sleep Okay         │
                 │ - Sleep Well         │
                 │ - Sleep Best         │
                 └──────────┬───────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────┐
│                    Data Layer                        │
│                                                      │
│ - Scenario storage                                   │
│ - Configuration                                      │
│ - Sample data                                        │
│ - JSON serialization                                 │
└────────────────────────┬─────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│                 Reporting Layer                      │
│                                                      │
│ - CSV export                                         │
│ - PDF report                                         │
│ - Assumption summary                                 │
│ - Projection table                                   │
└──────────────────────────────────────────────────────┘