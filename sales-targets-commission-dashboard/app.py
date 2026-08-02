"""
Sales Targets & Commission Dashboard
--------------------------------------
Replaces the fragile 19-tab Product Sales Targets workbook with a single,
readable dashboard. Loads pre-calculated monthly data (actuals vs targets,
achievement %, and commission) and lets anyone step through each month,
drill into a specific salesperson, and see exactly how their commission
was calculated.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Sales Targets & Commission Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "sample_data"

NAVY = "#1F3864"
CREAM = "#F7F5F0"
GREEN = "#1E7B45"
AMBER = "#B4740E"
RED = "#B3261E"
GREY = "#6B6B6B"

st.markdown(f"""
<style>
    .stApp {{ background-color: {CREAM}; }}
    section[data-testid="stSidebar"] {{ background-color: {NAVY}; }}
    section[data-testid="stSidebar"] * {{ color: #F7F5F0 !important; }}
    div[data-testid="stMetric"] {{
        background-color: white; border: 1px solid #E3E0D8; border-radius: 10px;
        padding: 16px 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    div[data-testid="stMetricLabel"] {{ font-size: 0.9rem; color: {GREY}; }}
    h1, h2, h3 {{ color: {NAVY}; font-family: 'Georgia', serif; }}
    .subtitle {{ color: {GREY}; font-size: 1.05rem; margin-top: -10px; }}
    .badge {{
        display: inline-block; padding: 3px 10px; border-radius: 20px;
        font-size: 0.8rem; font-weight: 600; color: white;
    }}
    .badge-good {{ background-color: {GREEN}; }}
    .badge-mid {{ background-color: {AMBER}; }}
    .badge-low {{ background-color: {RED}; }}
    .badge-none {{ background-color: {GREY}; }}
    .note-box {{
        background-color: #FBEEEE; border-left: 4px solid {RED};
        padding: 12px 16px; border-radius: 6px; font-size: 0.9rem; color: #262626;
    }}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------------------------
@st.cache_data
def load_data():
    category_detail = pd.read_csv(DATA_DIR / "category_detail.csv", parse_dates=["Month"])
    commission_summary = pd.read_csv(DATA_DIR / "commission_summary.csv", parse_dates=["Month"])
    return category_detail, commission_summary

category_detail, commission_summary = load_data()
all_months = sorted(commission_summary["Month"].unique())
month_labels = {m: pd.Timestamp(m).strftime("%B %Y") for m in all_months}

def achievement_badge(pct, has_target):
    if not has_target:
        return '<span class="badge badge-none">No Target Set</span>'
    if pct >= 100:
        return f'<span class="badge badge-good">{pct:.0f}% of target</span>'
    elif pct >= 80:
        return f'<span class="badge badge-mid">{pct:.0f}% of target</span>'
    else:
        return f'<span class="badge badge-low">{pct:.0f}% of target</span>'

# --------------------------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------------------------
st.sidebar.markdown("## 📈 Sales & Commission")
st.sidebar.markdown("Targets, actuals, and commission — automated.")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Go to",
    ["🏠 Monthly Overview", "🔍 Rep Drill-Down", "📊 Trends Across Months"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
selected_month = st.sidebar.selectbox(
    "Viewing month",
    all_months,
    format_func=lambda m: month_labels[m],
    index=len(all_months) - 1,
)

st.sidebar.markdown(
    "<div style='font-size:0.82rem; opacity:0.75; margin-top:10px;'>"
    "Base commission is 5% of actual sales, confirmed from real transaction data. "
    "The achievement bonus tiers are a placeholder pending confirmation from finance."
    "</div>",
    unsafe_allow_html=True,
)

month_data = commission_summary[commission_summary["Month"] == selected_month].copy()
month_cat_data = category_detail[category_detail["Month"] == selected_month].copy()

# --------------------------------------------------------------------------
# PAGE: MONTHLY OVERVIEW
# --------------------------------------------------------------------------
if page == "🏠 Monthly Overview":
    st.markdown("# Monthly Overview")
    st.markdown(f'<p class="subtitle">{month_labels[selected_month]} — company-wide performance and commission.</p>', unsafe_allow_html=True)
    st.write("")

    total_actual = month_data["Actual Revenue (ZAR)"].sum()
    total_target = month_data["Target Revenue (ZAR)"].sum()
    total_commission = month_data["Total Commission (ZAR)"].sum()
    reps_on_target = (month_data["Achievement %"] >= 100).sum()
    reps_with_target = (month_data["Target Revenue (ZAR)"] > 0).sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Sales", f"R {total_actual:,.0f}")
    c2.metric("Total Target", f"R {total_target:,.0f}")
    c3.metric("Commission Payable", f"R {total_commission:,.0f}")
    c4.metric("Reps On/Over Target", f"{reps_on_target} / {reps_with_target}")

    st.write("")
    st.markdown("### Performance by salesperson")

    display = month_data.sort_values("Total Commission (ZAR)", ascending=False).copy()
    for _, row in display.iterrows():
        has_target = row["Target Revenue (ZAR)"] > 0
        c1, c2, c3 = st.columns([3, 4, 2])
        with c1:
            st.markdown(f"**{row['Rep']}**")
            st.markdown(achievement_badge(row["Achievement %"], has_target), unsafe_allow_html=True)
        with c2:
            st.write(f"Sales: R {row['Actual Revenue (ZAR)']:,.0f}" + (f"  ·  Target: R {row['Target Revenue (ZAR)']:,.0f}" if has_target else "  ·  No target set this cycle"))
            st.caption(f"Base commission R {row['Base Commission (ZAR)']:,.0f} + bonus R {row['Bonus (ZAR)']:,.0f}")
        with c3:
            st.markdown(f"### R {row['Total Commission (ZAR)']:,.0f}")
        st.markdown("<hr style='margin:4px 0; opacity:0.15;'>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# PAGE: REP DRILL-DOWN
# --------------------------------------------------------------------------
elif page == "🔍 Rep Drill-Down":
    st.markdown("# Rep Drill-Down")
    st.markdown('<p class="subtitle">See exactly how one person\'s commission was calculated.</p>', unsafe_allow_html=True)
    st.write("")

    reps = sorted(commission_summary["Rep"].unique())
    selected_rep = st.selectbox("Select a salesperson", reps)

    rep_summary = commission_summary[commission_summary["Rep"] == selected_rep].sort_values("Month")
    rep_month = rep_summary[rep_summary["Month"] == selected_month]

    if not rep_month.empty:
        row = rep_month.iloc[0]
        has_target = row["Target Revenue (ZAR)"] > 0

        st.markdown(f"### {selected_rep} — {month_labels[selected_month]}")
        st.markdown(achievement_badge(row["Achievement %"], has_target), unsafe_allow_html=True)
        st.write("")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Actual Sales", f"R {row['Actual Revenue (ZAR)']:,.0f}")
        c2.metric("Target", f"R {row['Target Revenue (ZAR)']:,.0f}" if has_target else "Not set")
        c3.metric("Base Commission (5%)", f"R {row['Base Commission (ZAR)']:,.0f}")
        c4.metric("Bonus", f"R {row['Bonus (ZAR)']:,.0f}", delta=f"{row['Bonus Rate Applied']*100:.0f}% tier" if row['Bonus Rate Applied'] > 0 else None, delta_color="off")

        st.write("")
        st.markdown(f"#### Total commission payable: R {row['Total Commission (ZAR)']:,.0f}")

        st.write("")
        st.markdown("### Breakdown by product category")
        rep_cat = month_cat_data[month_cat_data["Rep"] == selected_rep][
            ["Category", "Actual Revenue (ZAR)", "Target Revenue (ZAR)", "Base Commission (ZAR)"]
        ].sort_values("Actual Revenue (ZAR)", ascending=False)
        st.dataframe(
            rep_cat,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Actual Revenue (ZAR)": st.column_config.NumberColumn(format="R %.2f"),
                "Target Revenue (ZAR)": st.column_config.NumberColumn(format="R %.2f"),
                "Base Commission (ZAR)": st.column_config.NumberColumn(format="R %.2f"),
            },
        )

        st.write("")
        st.markdown("### Trend across all months")
        trend = rep_summary.set_index("Month")[["Actual Revenue (ZAR)", "Target Revenue (ZAR)"]]
        st.line_chart(trend)
    else:
        st.info("No data for this salesperson in the selected month.")

# --------------------------------------------------------------------------
# PAGE: TRENDS ACROSS MONTHS
# --------------------------------------------------------------------------
elif page == "📊 Trends Across Months":
    st.markdown("# Trends Across Months")
    st.markdown('<p class="subtitle">How the whole team is tracking, month to month.</p>', unsafe_allow_html=True)
    st.write("")

    monthly_totals = commission_summary.groupby("Month", as_index=False).agg(
        **{
            "Total Sales (ZAR)": ("Actual Revenue (ZAR)", "sum"),
            "Total Target (ZAR)": ("Target Revenue (ZAR)", "sum"),
            "Total Commission (ZAR)": ("Total Commission (ZAR)", "sum"),
        }
    ).set_index("Month")

    st.markdown("### Sales vs Target, company-wide")
    st.line_chart(monthly_totals[["Total Sales (ZAR)", "Total Target (ZAR)"]])

    st.markdown("### Total commission paid, by month")
    st.bar_chart(monthly_totals[["Total Commission (ZAR)"]])

    st.write("")
    st.markdown("### Achievement % by salesperson, across all months")
    pivot = commission_summary.pivot_table(
        index="Rep", columns="Month", values="Achievement %", aggfunc="first"
    )
    pivot.columns = [month_labels[c] for c in pivot.columns]
    st.dataframe(
        pivot.style.format("{:.0f}%").background_gradient(cmap="RdYlGn", vmin=0, vmax=150),
        use_container_width=True,
    )

    st.markdown(
        '<div class="note-box">Achievement bonus tiers used in this demo are a placeholder '
        '(0% below 80% of target, 1% from 80–100%, 2% from 100–120%, 3% above 120%). '
        'These need to be confirmed against the real commission policy before this replaces '
        'the manual process.</div>',
        unsafe_allow_html=True,
    )
