import streamlit as st
import json

st.set_page_config(page_title="Consulting Boutique Revenue & Valuation", page_icon="📈", layout="wide")

st.title("📈 Consulting Boutique Revenue & Valuation Calculator")
st.caption("Model funnel → utilisation → realization → EBITDA → valuation (incl. digital uplift).")

with st.sidebar:
    st.header("Quick Actions")
    preset = st.selectbox("Scenario presets", ["Baseline", "Improve win rate", "Reduce discounting", "Raise realization", "Balanced uplift"])
    st.markdown("---")
    st.write("Save/Load Scenario")
    load_text = st.text_area("Paste a saved scenario JSON to load", height=120, label_visibility="collapsed")
    load_btn = st.button("Load scenario from JSON")
    st.markdown("---")
    save_btn = st.button("Show scenario JSON")

# Default state
state = {
    "fte": 15,
    "hoursPerFte": 1800,
    "utilTarget": 0.75,
    "utilActual": 0.62,
    "rate": 220,
    "enquiriesPerMonth": 40,
    "qualRate": 0.60,
    "proposalRate": 0.70,
    "winRate": 0.32,
    "projectValue": 65000,
    "salesCycleDays": 45,
    "proposalDays": 7,
    "discount": 0.08,
    "realization": 0.92,
    "writeoffs": 0.02,
    "scope": 0.03,
    "badDebt": 0.01,
    "overrunHoursPct": 0.04,
    "dso": 45,
    "cancelRate": 0.02,
    "ebitdaMargin": 0.25,
    "baseMultiple": 7.0,
    "digitalUplift": 0.57,
}

# Apply preset
if preset == "Improve win rate":
    state["winRate"] = 0.40
elif preset == "Reduce discounting":
    state["discount"] = 0.05
elif preset == "Raise realization":
    state["realization"] = 0.95
elif preset == "Balanced uplift":
    state.update({"winRate":0.38, "discount":0.06, "realization":0.95, "utilActual":0.68})

# Load from JSON if requested
if load_btn and load_text.strip():
    try:
        loaded = json.loads(load_text)
        for k in state:
            if k in loaded:
                state[k] = loaded[k]
        st.success("Loaded scenario from JSON.")
    except Exception as e:
        st.error(f"Could not parse JSON: {e}")

# Show JSON if requested
if save_btn:
    st.markdown("#### Scenario JSON")
    st.code(json.dumps(state, indent=2), language="json")

# --- Layout ---
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.subheader("Firm Profile")
    state["fte"] = st.number_input("Consultants (FTE)", min_value=1, step=1, value=int(state["fte"]))
    state["hoursPerFte"] = st.number_input("Hours / consultant / year", min_value=100, step=10, value=int(state["hoursPerFte"]))
    state["utilTarget"] = st.number_input("Target utilisation", min_value=0.0, max_value=1.0, step=0.01, value=float(state["utilTarget"]))
    state["utilActual"] = st.number_input("Actual utilisation", min_value=0.0, max_value=1.0, step=0.01, value=float(state["utilActual"]))
    state["rate"] = st.number_input("Blended billable rate", min_value=0.0, step=10.0, value=float(state["rate"]))

with col2:
    st.subheader("Funnel")
    state["enquiriesPerMonth"] = st.number_input("Enquiries / month", min_value=0, step=1, value=int(state["enquiriesPerMonth"]))
    state["qualRate"] = st.number_input("Qualification rate → opps", min_value=0.0, max_value=1.0, step=0.01, value=float(state["qualRate"]))
    state["proposalRate"] = st.number_input("Proposal rate (opps→props)", min_value=0.0, max_value=1.0, step=0.01, value=float(state["proposalRate"]))
    state["winRate"] = st.number_input("Win rate (props→signed)", min_value=0.0, max_value=1.0, step=0.01, value=float(state["winRate"]))
    state["projectValue"] = st.number_input("Avg project value (fees)", min_value=0.0, step=1000.0, value=float(state["projectValue"]))

with col3:
    st.subheader("Timing")
    state["salesCycleDays"] = st.number_input("Sales cycle (days)", min_value=0, step=1, value=int(state["salesCycleDays"]))
    state["proposalDays"] = st.number_input("Proposal turnaround (days)", min_value=0, step=1, value=int(state["proposalDays"]))
    state["dso"] = st.number_input("DSO (days)", min_value=0, step=1, value=int(state["dso"]))
    state["cancelRate"] = st.number_input("Cancellation / early term", min_value=0.0, max_value=1.0, step=0.01, value=float(state["cancelRate"]))
    state["overrunHoursPct"] = st.number_input("Overrun hours not billed", min_value=0.0, max_value=1.0, step=0.01, value=float(state["overrunHoursPct"]))

with col4:
    st.subheader("Pricing & Realization")
    state["discount"] = st.number_input("Avg discount on rate", min_value=0.0, max_value=1.0, step=0.01, value=float(state["discount"]))
    state["realization"] = st.number_input("Realization (billed/recorded)", min_value=0.0, max_value=1.0, step=0.01, value=float(state["realization"]))
    state["writeoffs"] = st.number_input("Write-offs / credits", min_value=0.0, max_value=1.0, step=0.01, value=float(state["writeoffs"]))
    state["scope"] = st.number_input("Uncompensated scope creep", min_value=0.0, max_value=1.0, step=0.01, value=float(state["scope"]))
    state["badDebt"] = st.number_input("Bad debt", min_value=0.0, max_value=1.0, step=0.01, value=float(state["badDebt"]))

with col5:
    st.subheader("Valuation")
    state["ebitdaMargin"] = st.number_input("EBITDA margin", min_value=0.0, max_value=1.0, step=0.01, value=float(state["ebitdaMargin"]))
    state["baseMultiple"] = st.number_input("Base multiple (× EBITDA)", min_value=0.0, step=0.1, value=float(state["baseMultiple"]))
    state["digitalUplift"] = st.number_input("Digital uplift (+%)", min_value=0.0, step=0.01, value=float(state["digitalUplift"]))

# --- Calculations ---
targetBillableHours = state["fte"] * state["hoursPerFte"] * state["utilTarget"]
actualBillableHours  = state["fte"] * state["hoursPerFte"] * state["utilActual"]
capacityRevenueTarget = targetBillableHours * state["rate"]
capacityRevenueActual = actualBillableHours * state["rate"]

enquiriesYear = state["enquiriesPerMonth"] * 12
qualified = enquiriesYear * state["qualRate"]
proposals = qualified * state["proposalRate"]
wins = proposals * state["winRate"]
pipelineRevenue = wins * state["projectValue"]

idealBookable = min(capacityRevenueTarget, pipelineRevenue)

afterPriceReal = (1 - state["discount"]) * state["realization"]
afterPostDelivery = (1 - state["writeoffs"] - state["scope"] - state["badDebt"])
capacityAfterPriceReal = capacityRevenueTarget * afterPriceReal
revenueCapacityView = capacityAfterPriceReal * afterPostDelivery
actualRevenue = min(revenueCapacityView, pipelineRevenue)

leakage = idealBookable - actualRevenue
leakagePct = (leakage / idealBookable) if idealBookable > 0 else 0.0

demandShortfall = max(0.0, capacityRevenueTarget - pipelineRevenue)
utilGap = (targetBillableHours - actualBillableHours) * state["rate"]
priceRealLoss = idealBookable * (1 - afterPriceReal)
postLoss = idealBookable * (state["writeoffs"] + state["scope"] + state["badDebt"])

ebitda = actualRevenue * state["ebitdaMargin"]
valBase = ebitda * state["baseMultiple"]
valDigital = valBase * (1 + state["digitalUplift"])
valUplift = valDigital - valBase

# --- Results KPIs ---
def money(x): 
    try:
        return f"${x:,.0f}"
    except:
        return "—"

k1, k2, k3 = st.columns(3)
with k1:
    st.metric("Ideal Bookable Revenue", money(idealBookable))
with k2:
    st.metric("Actual Revenue", money(actualRevenue))
with k3:
    st.metric("Revenue Leakage", money(leakage), delta=f"{leakagePct*100:.1f}%", delta_color="inverse")

st.markdown("---")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.subheader("Demand Shortfall")
    st.write(money(demandShortfall))
with c2:
    st.subheader("Utilisation Gap")
    st.write(money(utilGap))
with c3:
    st.subheader("Pricing & Realization Loss")
    st.write(money(priceRealLoss))
with c4:
    st.subheader("Post‑Delivery Loss")
    st.write(money(postLoss))

st.markdown("---")

v1, v2, v3, v4 = st.columns(4)
with v1:
    st.subheader("EBITDA (from Actual)")
    st.write(money(ebitda))
with v2:
    st.subheader("Valuation (Base)")
    st.write(money(valBase))
with v3:
    st.subheader("Valuation (Digital +57%)")
    st.write(money(valDigital))
with v4:
    st.subheader("Valuation Uplift (Extra EV)")
    st.success(money(valUplift))

st.caption("Notes: Breakdown components overlap (don’t sum). Improve win rate, reduce discounting, protect scope, lift realization, speed proposals, and reduce DSO to raise revenue and exit value.")
