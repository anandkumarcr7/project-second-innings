# Project Second Innings
## Project Charter

**Document Version:** 0.1  
**Status:** Draft  
**Project Owners:** Anand Kumar and Harini  
**Project Type:** Personal financial planning and retirement simulation application  
**Primary Technology:** Python and Streamlit  

---

# 1. Project Vision

Build a private financial independence planning application that helps our family understand when we can retire, how much corpus we need, and which variables most strongly affect retirement success.

The system should behave more like a design qualification tool than a generic financial calculator.

It should make assumptions visible, risk very visible!, support stress testing, and allow results to be visualized.

---

# 2. Problem Statement

We need a tool that needed to work for us based on the margin of safety that would let us sleep well at night. Traditional tools either used complicated rules or didn't have stress test options. We wanted to build a tool that makes assumptions and risk visible to us. 

---

# 3. Project Objectives

The project shall:

1. Estimate the corpus required for a selected lifestyle or monthly expenditure.
2. Provide three retirement confidence targets:
   - Sleep Best at Night
   - Sleep Well at Night
   - Sleep Okay at Night
3. Generate a year-by-year retirement projection and spit out a 40 year corpus state table for different scenarios.
4. Model inflation, returns, passive income, taxes, and retirement duration. We've ended up with unrealistic numbers even if we missed one of the parameters.
5. Support stress tests like market crashes.
6. Compare current investable assets against target corpus.
7. Preserve user privacy by keeping personal financial data local by default.
9. Support contribution from both Anand and Harini through Git-based version control.
10. Be amenable to more advanced retirement modeling in future versions for our little Duggu when he's ready ;-)

---

# 4. Primary Users

## 4.1 Initial Users

- Anand Kumar
- Harini

## 4.2 Future Users

Potential future users may include:

- close friends,
- family members,
- technically inclined users who want a transparent retirement model,
- users who prefer private financial tools.

The first release is designed for personal use of Anand & Harini.

---

# 5. Key Use Cases

The system should eventually support the following high-level use cases:

1. Enter current retirement assumptions.
2. Calculate required Financial Independence corpus.
3. Compare current assets with required corpus.
4. Review annual corpus depletion or growth over 40 years.
5. Run stress scenarios like market crashes.
6. Identify the dominant retirement risk.
7. Evaluate the effect of turning the following knobs:
   - retiring later,
   - reducing expenses,
   - increasing savings,
   - changing asset allocation,
   - adding passive income,
   - or extending the retirement horizon.
8. Save and reload scenarios.
9. Export results for discussion and review.

---

# 6. Project Scope

## 6.1 In Scope for Initial Development

The initial system will include:

- deterministic retirement simulation,
- configurable monthly expenses,
- configurable retirement duration,
- inflation assumptions,
- conservative, typical, and optimistic return assumptions,
- passive income,
- simplified effective taxation,
- current investable assets,
- minimum corpus solver,
- three retirement confidence targets,
- annual projection table,
- stress-test capability,
- local data storage,
- CSV export,
- Streamlit dashboard,
- automated unit tests.

## 6.2 Future Scope

Future versions may include:

- 60/40 portfolio modeling,
- separate equity and fixed-income buckets,
- annual rebalancing,
- capital-gains taxation,
- historical return sequence replay,
- Monte Carlo simulation,
- pre-retirement accumulation modeling,
- RSU modeling,
- home-sale proceeds,
- education goals,
- healthcare costs,
- withdrawal ordering,
- multiple currencies,
- India and US tax treatment,
- encrypted cloud backup,
- user authentication,
- hosted deployment.

---

# 8. Design Principles

The project will follow these principles:

## 8.1 Privacy First

Personal financial data should remain local unless the user explicitly chooses otherwise.

## 8.2 Assumptions Must Be Visible

Every output should show the assumptions used to generate it.

## 8.3 Deterministic Before Probabilistic

The deterministic engine must be understood and verified before stress testing using Monte Carlo or historical simulation is added.

## 8.4 Separate Logic from User Interface

The financial calculation engine must remain independent from Streamlit.

## 8.5 Explain Failure Modes

The system should report not only whether a scenario fails, but when and why it fails.

## 8.6 Margin of Safety

Retirement targets should include explicit design margin rather than hidden assumptions.

## 8.7 Incremental Development

The project will be developed in small, reviewable releases.

---

# 9. Success Criteria

The project will be considered successful when:

1. Anand and Harini can run the application locally.
2. The application calculates retirement corpus for a 40-year horizon.
3. The application produces:
   - Sleep Best,
   - Sleep Well,
   - Sleep Okay targets.
4. The annual projection table is mathematically consistent.
5. Reference financial cases pass automated tests.
6. Stress tests generate repeatable PASS/FAIL results.
7. No personal financial data is committed to Git.
8. Both contributors can safely create branches and merge changes.
9. The model assumptions are documented.
10. The result is useful enough to support an annual retirement design review.

---

# 10. Initial Deliverables

The initial project deliverables are:

| Deliverable | Description |
|---|---|
| Project Charter | Defines vision, scope, objectives, and success criteria |
| System Requirements | Defines what the application shall do |
| Use Cases | Defines user interactions and expected outcomes |
| System Architecture | Defines major modules and data flow |
| Data Model | Defines key entities and interfaces |
| Detailed Design | Defines equations and algorithms |
| Verification Plan | Defines qualification tests |
| Roadmap | Defines release sequence |
| Source Repository | Private GitHub repository |
| MVP Application | Local Streamlit retirement dashboard |

---

# 11. Risks

| Risk | Impact | Initial Mitigation |
|---|---|---|
| Incorrect financial equations | High | Manual reference cases and unit tests |
| Hidden assumptions | High | Display and document all assumptions |
| Scope expansion | Medium | Use phased release roadmap |
| Tax modeling complexity | High | Use simplified model in v0.1 |
| Privacy leak through Git | High | Ignore local financial data files |
| Overconfidence in outputs | High | Display limitations and scenario sensitivity |
| Collaboration conflicts | Medium | Feature branches and pull requests |
| Model becoming hard to maintain | Medium | Modular architecture and documentation |

---

# 12. Constraints

The project shall initially operate under the following constraints:

- Python-based implementation.
- Streamlit user interface.
- Private GitHub repository.
- Local-first execution.
- No dependency on paid financial APIs.
- No live brokerage connection.
- No storage of passwords or banking credentials.
- Initial retirement horizon of 40 years.
- Supported display currencies: INR and USD.
- Initial post-retirement earned income assumption of zero.

---

# 13. Version Control

Major changes to assumptions, architecture, or scope should be recorded in:

```text
docs/08_Design_Decisions.md