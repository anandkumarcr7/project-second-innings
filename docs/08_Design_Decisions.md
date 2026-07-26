# Project Second Innings
## Design Decisions

---

## DD-001 — Currency-Keyed Widget Keys for Default Reset

**Date:** 2026-07-26  
**Status:** Accepted

### Context

Streamlit preserves widget state across re-renders using widget keys. When a user switches
currency from INR to USD, the financial input widgets retain their previous INR-scale values
unless explicitly reset. Values such as ₹2,00,000/month and ₹10 Cr assets are several orders
of magnitude too large for a USD user, making the tool confusing and error-prone out of the box.

### Decision

Financial input widgets (`monthly_expenses`, `current_assets`, `average_annual_savings`,
`passive_income`) are assigned widget keys that include the selected currency as a suffix
(e.g. `monthly_expenses_INR`, `monthly_expenses_USD`).

When the user switches currency, Streamlit treats the new key as a new widget and initialises
it with the currency-appropriate default value, effectively resetting the inputs automatically.

### Consequences

- **Positive:** Users always see sensible, currency-scaled defaults immediately on switch.
- **Positive:** No explicit session-state management or reset callbacks are required.
- **Negative:** Switching currency discards any values the user had typed. This is intentional
  and expected — INR and USD values are not interchangeable.

---

## DD-002 — Contextual Captions for FI Status and Simulation Result

**Date:** 2026-07-26  
**Status:** Accepted

### Context

The dashboard can simultaneously show "Not Yet FI" (FI Status card) and
"Simulation: PASS" (40-Year Projection section). Both are mathematically correct:

- **Not Yet FI** means projected assets fall short of the selected target corpus, which
  includes a safety margin above the minimum survival corpus.
- **Simulation: PASS** means the projected corpus, even without that margin, is still
  sufficient to cover all expenses over the full retirement duration.

Without explanation, the two messages appear contradictory and erode user trust.

### Decision

Both results now display a short contextual caption:

- The FI Status caption names the selected target (e.g. Sleep Well) and explicitly states
  that the target includes a safety margin.
- The Simulation caption states that PASS/FAIL tests actual expense coverage from the
  projected corpus, independent of the chosen FI target.

### Consequences

- **Positive:** Users understand why both results can be true simultaneously.
- **Positive:** The distinction reinforces the concept of design margin as a confidence
  buffer, not a hard survival requirement.
- **Negative:** Slightly more text in the FI Status area; acceptable given the clarity gained.
