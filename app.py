"""
Project Second Innings — Streamlit Dashboard

Run with:  streamlit run app.py

Password is read from the APP_PASSWORD environment variable (or Streamlit secrets).
Set it before starting the app — never hardcode credentials in source files.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from second_innings.engine import calculate_fi_targets, run_stress_tests, simulate
from second_innings.models import RetirementScenario
from second_innings.scenario_io import load_scenario, save_scenario

_PRIVATE_DIR = Path("data/private")

# ── Password gate ─────────────────────────────────────────────────────────────
# Read from Streamlit secrets (cloud) or APP_PASSWORD env var (local).
# Set the env var before running:  $env:APP_PASSWORD = "your-password"
try:
    _EXPECTED = st.secrets.get("APP_PASSWORD", None)
except Exception:
    _EXPECTED = None
if _EXPECTED is None:
    _EXPECTED = os.environ.get("APP_PASSWORD", "")

if _EXPECTED:
    _entered = st.sidebar.text_input("Password", type="password", key="_pw")
    if _entered != _EXPECTED:
        st.sidebar.warning("Enter the password to continue.")
        st.stop()

# ── Formatting helpers ────────────────────────────────────────────────────────

def _fmt(value: float, currency: str = "INR") -> str:
    """Format a monetary amount with currency-appropriate suffix."""
    abs_v = abs(value)
    sign = "-" if value < 0 else ""
    if currency == "USD":
        if abs_v >= 1_000_000:
            return f"{sign}${abs_v / 1_000_000:.2f} Mn"
        if abs_v >= 1_000:
            return f"{sign}${abs_v / 1_000:.2f} K"
        return f"{sign}${abs_v:,.0f}"
    else:  # INR
        if abs_v >= 1e7:
            return f"{sign}₹{abs_v / 1e7:.2f} Cr"
        if abs_v >= 1e5:
            return f"{sign}₹{abs_v / 1e5:.2f} L"
        return f"{sign}₹{abs_v:,.0f}"


def _pct(value: float) -> str:
    return f"{value:.1f}%"


# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Project Second Innings",
    page_icon="🏏",
    layout="wide",
)

st.title("🏏 Project Second Innings")
st.caption("Financial Independence Planning — private, local, deterministic")

# ── Sidebar: all inputs ───────────────────────────────────────────────────────

with st.sidebar:
    st.header("Retirement Assumptions")

    scenario_name = st.text_input("Scenario Name", value="FIRE Planning", max_chars=50)
    currency = st.selectbox("Currency", ["INR", "USD"], index=0)
    _symbol = "₹" if currency == "INR" else "$"

    st.subheader("👤 Personal")
    current_age = st.number_input("Current Age", min_value=18, max_value=80, value=35, step=1)
    retirement_age = st.number_input("Retirement Age", min_value=18, max_value=90, value=45, step=1)
    retirement_duration = st.number_input(
        "Retirement Duration (years)", min_value=1, max_value=60, value=40, step=1
    )

    st.subheader("💰 Finances")
    _step_small = 500 if currency == "USD" else 10_000
    _step_medium = 1_000 if currency == "USD" else 100_000
    _step_large = 10_000 if currency == "USD" else 1_000_000
    monthly_expenses = st.number_input(
        f"Monthly Expenses ({_symbol})", min_value=0, value=200_000, step=_step_small,
        help="Current retirement monthly spend in today's money"
    )
    current_assets = st.number_input(
        f"Current Investable Assets ({_symbol})", min_value=0, value=100_000_000, step=_step_large
    )
    average_annual_savings = st.number_input(
        f"Average Annual Savings ({_symbol})", min_value=0, value=0, step=_step_medium,
        help="Expected savings added each year between now and retirement"
    )
    passive_income = st.number_input(
        f"Annual Passive Income ({_symbol})", min_value=0, value=0, step=_step_medium,
        help="Rental / dividend income received after retirement"
    )

    st.subheader("📈 Return Assumptions")
    conservative_return = st.slider("Conservative Return (%)", 1.0, 15.0, 7.0, 0.5) / 100
    typical_return = st.slider("Typical Return (%)", 1.0, 20.0, 9.0, 0.5) / 100
    optimistic_return = st.slider("Optimistic Return (%)", 1.0, 25.0, 11.0, 0.5) / 100

    st.subheader("📊 Macro Assumptions")
    inflation_rate = st.slider("Inflation Rate (%)", 1.0, 15.0, 7.0, 0.5) / 100
    tax_rate = st.slider("Effective Tax Rate on Returns (%)", 0.0, 30.0, 10.0, 0.5) / 100

    st.subheader("🛡️ Design Margins")
    sleep_well_margin = st.slider("Sleep Well Margin (%)", 0.0, 50.0, 10.0, 5.0) / 100
    sleep_best_margin = st.slider("Sleep Best Margin (%)", 0.0, 100.0, 25.0, 5.0) / 100

    st.subheader("🎯 FI Target")
    selected_target = st.selectbox(
        "Evaluate against",
        ["sleep_okay", "sleep_well", "sleep_best"],
        index=1,
        format_func=lambda x: {"sleep_okay": "Sleep Okay", "sleep_well": "Sleep Well",
                                "sleep_best": "Sleep Best"}[x],
    )

# ── Bind currency-aware formatter ────────────────────────────────────────────
_fmt_base = _fmt
_fmt = lambda v: _fmt_base(v, currency)          # noqa: E731
real_col = f"Real Corpus (Today {_symbol})"

# ── Build scenario (validate inputs) ─────────────────────────────────────────

try:
    scenario = RetirementScenario(
        scenario_name=scenario_name,
        current_age=int(current_age),
        retirement_age=int(retirement_age),
        retirement_duration_years=int(retirement_duration),
        monthly_expenses=float(monthly_expenses),
        current_assets=float(current_assets),
        annual_passive_income=float(passive_income),
        inflation_rate=inflation_rate,
        conservative_return=conservative_return,
        typical_return=typical_return,
        optimistic_return=optimistic_return,
        effective_tax_rate=tax_rate,
        sleep_well_margin=sleep_well_margin,
        sleep_best_margin=sleep_best_margin,
        average_annual_savings=float(average_annual_savings),
        currency=currency,
    )
except ValueError as exc:
    st.error(f"Input error: {exc}")
    st.stop()

if retirement_age <= current_age:
    st.error(f"Retirement age ({int(retirement_age)}) must be greater than current age ({int(current_age)}).")
    st.stop()

# ── Calculations (cached on input fingerprint) ────────────────────────────────

@st.cache_data
def _calculate(scenario_json: str, target: str):
    sc = RetirementScenario(**json.loads(scenario_json))
    fi = calculate_fi_targets(sc, selected_target=target)
    sim = simulate(sc, fi.projected_assets, sc.typical_return)
    stress = run_stress_tests(sc, opening_corpus=fi.projected_assets)
    return fi, sim, stress

import dataclasses as _dc
_scenario_json = json.dumps(_dc.asdict(scenario))
fi, sim, stress_results = _calculate(_scenario_json, selected_target)

# ── Section 1: FI Status ──────────────────────────────────────────────────────

st.header("Financial Independence Status")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if fi.fi_status == "FI Achieved":
        st.success(f"**{fi.fi_status}**")
    else:
        st.warning(f"**{fi.fi_status}**")

with col2:
    st.metric(
        "Projected Assets at Retirement",
        _fmt(fi.projected_assets),
        delta=_fmt(fi.projected_assets - fi.current_assets) + " from savings"
        if fi.projected_assets != fi.current_assets else None,
    )

with col3:
    target_label = selected_target.replace("_", " ").title()
    st.metric(f"Target ({target_label})", _fmt(
        {"sleep_okay": fi.sleep_okay_corpus,
         "sleep_well": fi.sleep_well_corpus,
         "sleep_best": fi.sleep_best_corpus}[selected_target]
    ))

with col4:
    gap = fi.funding_gap
    st.metric(
        "Funding Gap",
        _fmt(abs(gap)),
        delta=f"{'Surplus' if gap <= 0 else 'Deficit'}",
        delta_color="normal" if gap <= 0 else "inverse",
    )

st.progress(min(fi.percent_complete / 100, 1.0),
            text=f"{fi.percent_complete:.1f}% of {target_label} target")

# ── Section 2: Corpus Targets ─────────────────────────────────────────────────

st.header("Corpus Targets")

t1, t2, t3 = st.columns(3)

with t1:
    delta_okay = fi.projected_assets - fi.sleep_okay_corpus
    st.metric(
        "😴 Sleep Okay",
        _fmt(fi.sleep_okay_corpus),
        delta=f"{_fmt(abs(delta_okay))} {'surplus' if delta_okay >= 0 else 'needed'}",
        delta_color="normal" if delta_okay >= 0 else "inverse",
        help="Minimum corpus under the typical return assumption.",
    )

with t2:
    delta_well = fi.projected_assets - fi.sleep_well_corpus
    st.metric(
        "🌙 Sleep Well",
        _fmt(fi.sleep_well_corpus),
        delta=f"{_fmt(abs(delta_well))} {'surplus' if delta_well >= 0 else 'needed'}",
        delta_color="normal" if delta_well >= 0 else "inverse",
        help=f"Conservative corpus + {sleep_well_margin*100:.0f}% design margin.",
    )

with t3:
    delta_best = fi.projected_assets - fi.sleep_best_corpus
    st.metric(
        "⭐ Sleep Best",
        _fmt(fi.sleep_best_corpus),
        delta=f"{_fmt(abs(delta_best))} {'surplus' if delta_best >= 0 else 'needed'}",
        delta_color="normal" if delta_best >= 0 else "inverse",
        help=f"Conservative corpus + {sleep_best_margin*100:.0f}% design margin.",
    )

# ── Assumption summary ────────────────────────────────────────────────────────

with st.expander("Active Assumptions", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**Monthly Expenses:** {_fmt(monthly_expenses)}")
        st.markdown(f"**Annual Passive Income:** {_fmt(passive_income)}")
        st.markdown(f"**Current Assets:** {_fmt(current_assets)}")
        st.markdown(f"**Average Annual Savings:** {_fmt(average_annual_savings)}")
        st.markdown(f"**Projected Assets at Retirement:** {_fmt(fi.projected_assets)}")
    with c2:
        st.markdown(f"**Inflation:** {_pct(inflation_rate * 100)}")
        st.markdown(f"**Conservative Return:** {_pct(conservative_return * 100)}")
        st.markdown(f"**Typical Return:** {_pct(typical_return * 100)}")
        st.markdown(f"**Optimistic Return:** {_pct(optimistic_return * 100)}")
    with c3:
        st.markdown(f"**Tax Rate:** {_pct(tax_rate * 100)}")
        st.markdown(f"**Retirement Duration:** {retirement_duration} years")
        st.markdown(f"**Sleep Well Margin:** {_pct(sleep_well_margin * 100)}")
        st.markdown(f"**Sleep Best Margin:** {_pct(sleep_best_margin * 100)}")

# ── Section 3: 40-Year Projection ─────────────────────────────────────────────

st.header("40-Year Retirement Projection")

if sim.result == "PASS":
    st.success(f"Simulation: **PASS** — corpus survives all {retirement_duration} years.")
else:
    st.error(f"Simulation: **FAIL** — corpus exhausted in year **{sim.failure_year}** "
             f"(age {scenario.retirement_age + sim.failure_year - 1}).")

# Build DataFrame
rows = []
for r in sim.projection:
    rows.append({
        "Year": r.year,
        "Age": r.age,
        "Opening Corpus": r.opening_corpus,
        "Investment Growth": r.investment_growth,
        "Taxes": r.taxes,
        "Expenses": r.expenses,
        "Passive Income": r.passive_income,
        "Net Withdrawal": r.net_withdrawal,
        "Closing Corpus": r.closing_corpus,
        real_col: r.real_closing_corpus,
        "Status": r.status,
    })
df = pd.DataFrame(rows)

# Chart
chart_df = df[["Year", "Closing Corpus", real_col]].set_index("Year")
st.line_chart(chart_df, color=["#1f77b4", "#ff7f0e"])
st.caption("Blue = Nominal corpus  |  Orange = Inflation-adjusted corpus (today's purchasing power)")

# Table
with st.expander("Year-by-Year Table", expanded=False):
    display_df = df.copy()
    for col in ["Opening Corpus", "Investment Growth", "Taxes", "Expenses",
                "Passive Income", "Net Withdrawal", "Closing Corpus", real_col]:
        display_df[col] = display_df[col].apply(_fmt)

    def _highlight_fail(row):
        return ["background-color: #ffe0e0" if row["Status"] == "FAIL" else "" for _ in row]

    st.dataframe(display_df.style.apply(_highlight_fail, axis=1), width="stretch")

    # CSV download
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv_bytes,
        file_name=f"{scenario_name}_projection.csv",
        mime="text/csv",
    )

# ── Section 4: Stress Tests ───────────────────────────────────────────────────

st.header("Stress Tests")

pass_count = sum(1 for r in stress_results if r.result == "PASS")
fail_count = len(stress_results) - pass_count

scol1, scol2 = st.columns(2)
with scol1:
    if fail_count == 0:
        st.success(f"Overall: **{pass_count}/{len(stress_results)} PASS** — all stress tests passed.")
    else:
        st.error(f"Overall: **{fail_count}/{len(stress_results)} FAIL** — some stress tests failed.")

stress_rows = []
for r in stress_results:
    stress_rows.append({
        "Test": r.test_name,
        "Result": r.result,
        "Failure Year": r.failure_year,  # None renders as empty cell; keeps column integer-typed
        "Ending Corpus": _fmt(r.ending_corpus),
        "Severity": r.severity,
        "Changes": ", ".join(f"{k}={v}" for k, v in r.assumptions_changed.items()),
    })

stress_df = pd.DataFrame(stress_rows)

def _highlight_stress(row):
    color = "#ffe0e0" if row["Result"] == "FAIL" else "#e0f5e0"
    return [f"background-color: {color}"] * len(row)

st.dataframe(
    stress_df.style.apply(_highlight_stress, axis=1),
    width="stretch",
    hide_index=True,
)

# ── Section 5: Scenario Management ───────────────────────────────────────────

st.header("Scenario Management")

sm_col1, sm_col2 = st.columns(2)

with sm_col1:
    st.subheader("Save")
    if st.button("Save Current Scenario", type="primary"):
        _PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
        path = _PRIVATE_DIR / f"{scenario_name.replace(' ', '_')}.json"
        save_scenario(scenario, path)
        st.success(f"Saved to `{path}`")

with sm_col2:
    st.subheader("Load")
    uploaded = st.file_uploader("Upload a scenario JSON file", type="json")
    if uploaded:
        try:
            import tempfile, os
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
                tmp.write(uploaded.read())
                tmp_path = Path(tmp.name)
            loaded = load_scenario(tmp_path)
            os.unlink(tmp_path)
            st.success(f"Loaded: **{loaded.scenario_name}**")
            st.json(dataclasses.asdict(loaded))
        except ValueError as exc:
            st.error(str(exc))

# ── Footer ────────────────────────────────────────────────────────────────────

st.divider()
st.caption(
    f"Model version {scenario.model_version}  ·  "
    f"Retirement age {retirement_age}  ·  "
    f"Duration {retirement_duration} years  ·  "
    "All data is local — nothing is sent to any server."
)
