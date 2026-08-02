"""
Invoice Anomaly Checker
------------------------
A simple, non-technical-friendly Streamlit app that lets an administrator
upload an open-invoice spreadsheet, automatically flags anything unusual
(duplicates, rate mismatches, unusual amounts), and provides a clear
review screen to approve, correct, or escalate flagged invoices before
month-end close.
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# --------------------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Invoice Anomaly Checker",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

SAMPLE_FILE = Path(__file__).parent / "sample_data" / "Open_Invoice_Download_Example_ZAR.xlsx"

# --------------------------------------------------------------------------
# STYLING
# --------------------------------------------------------------------------
NAVY = "#1F3864"
NAVY_LIGHT = "#2E5090"
CREAM = "#F7F5F0"
GREEN = "#1E7B45"
AMBER = "#B4740E"
RED = "#B3261E"
GREY = "#6B6B6B"

st.markdown(f"""
<style>
    .stApp {{
        background-color: {CREAM};
    }}
    section[data-testid="stSidebar"] {{
        background-color: {NAVY};
    }}
    section[data-testid="stSidebar"] * {{
        color: #F7F5F0 !important;
    }}
    section[data-testid="stSidebar"] .stRadio label {{
        font-size: 1.05rem;
        padding: 6px 0;
    }}
    div[data-testid="stMetric"] {{
        background-color: white;
        border: 1px solid #E3E0D8;
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    div[data-testid="stMetricLabel"] {{
        font-size: 0.95rem;
        color: {GREY};
    }}
    h1, h2, h3 {{
        color: {NAVY};
        font-family: 'Georgia', serif;
    }}
    .subtitle {{
        color: {GREY};
        font-size: 1.05rem;
        margin-top: -10px;
    }}
    .flag-badge {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        color: white;
    }}
    .flag-duplicate {{ background-color: {RED}; }}
    .flag-rate {{ background-color: {AMBER}; }}
    .flag-amount {{ background-color: #C46210; }}
    .flag-clean {{ background-color: {GREEN}; }}
    .stButton button {{
        border-radius: 8px;
        font-weight: 600;
    }}
    .step-card {{
        background-color: white;
        border: 1px solid #E3E0D8;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 10px;
    }}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# SESSION STATE
# --------------------------------------------------------------------------
if "invoice_df" not in st.session_state:
    st.session_state.invoice_df = None
if "decisions" not in st.session_state:
    st.session_state.decisions = {}

# --------------------------------------------------------------------------
# ANOMALY DETECTION LOGIC
# --------------------------------------------------------------------------
def run_anomaly_checks(df: pd.DataFrame) -> pd.DataFrame:
    """Apply duplicate, rate, and amount checks. Returns df with Flag / Reason columns."""
    df = df.copy()
    df["Flag"] = "Clean"
    df["Flag Reason"] = ""

    # 1. Duplicate detection: same invoice number + service + amount appearing more than once
    dup_key = df["Invoice Number"].astype(str) + "|" + df["Service Description"].astype(str) + "|" + df["Total Amount (ZAR)"].astype(str)
    dup_counts = dup_key.value_counts()
    is_dup = dup_key.map(dup_counts) > 1
    df.loc[is_dup, "Flag"] = "Duplicate"
    df.loc[is_dup, "Flag Reason"] = "This exact charge appears more than once for this invoice."

    # 2. Rate check: compare each row's rate to the median rate for that service across all clients
    median_rates = df.groupby("Service Description")["Rate (ZAR)"].median()
    df["_median_rate"] = df["Service Description"].map(median_rates)
    rate_deviation = (df["Rate (ZAR)"] - df["_median_rate"]).abs() / df["_median_rate"]
    rate_flag = (rate_deviation > 0.20) & (df["Flag"] == "Clean")
    df.loc[rate_flag, "Flag"] = "Rate Mismatch"
    df.loc[rate_flag, "Flag Reason"] = df.loc[rate_flag].apply(
        lambda r: f"Rate of R{r['Rate (ZAR)']:.2f} is more than 20% away from the usual rate of R{r['_median_rate']:.2f} for this service.",
        axis=1
    )

    # 3. Amount outlier check: z-score of total amount within each service category
    def flag_amount_outliers(group):
        if len(group) < 3:
            return pd.Series([False] * len(group), index=group.index)
        mean = group["Total Amount (ZAR)"].mean()
        std = group["Total Amount (ZAR)"].std()
        if std == 0 or np.isnan(std):
            return pd.Series([False] * len(group), index=group.index)
        z = (group["Total Amount (ZAR)"] - mean) / std
        return z.abs() > 2

    outlier_mask = df.groupby("Service Description", group_keys=False).apply(flag_amount_outliers)
    amount_flag = outlier_mask & (df["Flag"] == "Clean")
    df.loc[amount_flag, "Flag"] = "Unusual Amount"
    df.loc[amount_flag, "Flag Reason"] = "Total amount is significantly higher than usual for this type of charge."

    df.drop(columns=["_median_rate"], inplace=True)
    return df


def badge_html(flag: str) -> str:
    mapping = {
        "Clean": ("flag-clean", "✓ Clean"),
        "Duplicate": ("flag-duplicate", "⚠ Duplicate"),
        "Rate Mismatch": ("flag-rate", "⚠ Rate Mismatch"),
        "Unusual Amount": ("flag-amount", "⚠ Unusual Amount"),
    }
    cls, label = mapping.get(flag, ("flag-clean", flag))
    return f'<span class="flag-badge {cls}">{label}</span>'


# --------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------------------------------
st.sidebar.markdown("## 📦 StoreSafe")
st.sidebar.markdown("Invoice Anomaly Checker")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Go to",
    ["🏠 Dashboard", "📤 Upload Invoices", "🔍 Review Flagged Invoices", "📚 All Invoices"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='font-size:0.85rem; opacity:0.75;'>Runs before month-end close, "
    "checking open invoices for duplicates, rate mismatches, and unusual amounts "
    "before they're sent to clients.</div>",
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# PAGE: DASHBOARD
# --------------------------------------------------------------------------
if page == "🏠 Dashboard":
    st.markdown("# Invoice Anomaly Checker")
    st.markdown('<p class="subtitle">A quick health check on open invoices before they close.</p>', unsafe_allow_html=True)
    st.write("")

    if st.session_state.invoice_df is None:
        st.info("👋 No invoices loaded yet. Head to **Upload Invoices** to get started, or load the sample data to explore the app.")
        if st.button("Load Sample Data", type="primary"):
            df = pd.read_excel(SAMPLE_FILE)
            st.session_state.invoice_df = run_anomaly_checks(df)
            st.rerun()
    else:
        df = st.session_state.invoice_df
        total_invoices = df["Invoice Number"].nunique()
        total_lines = len(df)
        flagged = df[df["Flag"] != "Clean"]
        flagged_lines = len(flagged)
        total_value = df["Total Amount (ZAR)"].sum()
        flagged_value = flagged["Total Amount (ZAR)"].sum()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Open Invoices", f"{total_invoices}")
        c2.metric("Line Items Checked", f"{total_lines}")
        c3.metric("Items Flagged", f"{flagged_lines}", delta=f"{flagged_lines/total_lines*100:.0f}% of lines" if total_lines else None, delta_color="off")
        c4.metric("Value Under Review", f"R {flagged_value:,.2f}")

        st.write("")
        st.markdown("### What's happening")
        colA, colB = st.columns([2, 1])

        with colA:
            if flagged_lines > 0:
                st.warning(f"**{flagged_lines} line item(s)** across **{flagged['Invoice Number'].nunique()} invoice(s)** need a quick look before these invoices are closed.")
                breakdown = flagged["Flag"].value_counts()
                for flag_type, count in breakdown.items():
                    st.markdown(f"{badge_html(flag_type)} &nbsp; {count} item(s)", unsafe_allow_html=True)
            else:
                st.success("Nothing flagged. All open invoices look consistent with historical patterns.")

        with colB:
            st.markdown("**Total value of open invoices**")
            st.markdown(f"### R {total_value:,.2f}")

        st.write("")
        if flagged_lines > 0:
            st.markdown("Head to **🔍 Review Flagged Invoices** to work through these before month-end close.")

# --------------------------------------------------------------------------
# PAGE: UPLOAD
# --------------------------------------------------------------------------
elif page == "📤 Upload Invoices":
    st.markdown("# Upload Invoices")
    st.markdown('<p class="subtitle">Upload the open-invoice spreadsheet exported from your accounting system.</p>', unsafe_allow_html=True)
    st.write("")

    st.markdown("""
    <div class="step-card">
    <b>Before you upload:</b><br>
    Export your open (not yet closed) invoices from your accounting system as an Excel file.
    It should include columns for client name, invoice number, date, service description,
    rate, quantity, and total amount.
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    uploaded = st.file_uploader("Drag and drop your invoice file here, or click to browse", type=["xlsx", "xls"])

    col1, col2 = st.columns([1, 3])
    with col1:
        use_sample = st.button("Or use sample data instead")

    if uploaded is not None:
        try:
            df = pd.read_excel(uploaded)
            required_cols = {"Client Name", "Invoice Number", "Service Description", "Rate (ZAR)", "Total Amount (ZAR)"}
            missing = required_cols - set(df.columns)
            if missing:
                st.error(f"This file is missing expected columns: {', '.join(missing)}. Please check the export and try again.")
            else:
                st.session_state.invoice_df = run_anomaly_checks(df)
                st.success(f"✅ Loaded {len(df)} line items across {df['Invoice Number'].nunique()} invoices. Checks have been run automatically.")
                st.dataframe(df.head(10), use_container_width=True, hide_index=True)
                st.markdown("Head to **🔍 Review Flagged Invoices** to see the results.")
        except Exception as e:
            st.error(f"Couldn't read that file. Please make sure it's a valid Excel export. ({e})")

    if use_sample:
        df = pd.read_excel(SAMPLE_FILE)
        st.session_state.invoice_df = run_anomaly_checks(df)
        st.success(f"✅ Sample data loaded: {len(df)} line items across {df['Invoice Number'].nunique()} invoices.")
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)
        st.markdown("Head to **🔍 Review Flagged Invoices** to see the results.")

# --------------------------------------------------------------------------
# PAGE: REVIEW FLAGGED INVOICES
# --------------------------------------------------------------------------
elif page == "🔍 Review Flagged Invoices":
    st.markdown("# Review Flagged Invoices")
    st.markdown('<p class="subtitle">Everything below needs a quick decision before it can be closed.</p>', unsafe_allow_html=True)
    st.write("")

    if st.session_state.invoice_df is None:
        st.info("No invoices loaded yet. Go to **Upload Invoices** first.")
    else:
        df = st.session_state.invoice_df
        flagged = df[df["Flag"] != "Clean"].copy()

        if flagged.empty:
            st.success("Nothing to review — all invoices are clean.")
        else:
            # Filters
            fc1, fc2 = st.columns([2, 2])
            with fc1:
                clients = ["All clients"] + sorted(flagged["Client Name"].unique().tolist())
                client_filter = st.selectbox("Filter by client", clients)
            with fc2:
                flag_types = ["All flag types"] + sorted(flagged["Flag"].unique().tolist())
                flag_filter = st.selectbox("Filter by flag type", flag_types)

            view = flagged.copy()
            if client_filter != "All clients":
                view = view[view["Client Name"] == client_filter]
            if flag_filter != "All flag types":
                view = view[view["Flag"] == flag_filter]

            st.write("")
            st.markdown(f"**{len(view)} item(s)** match your filters")
            st.write("")

            for idx, row in view.iterrows():
                key = f"decision_{idx}"
                current = st.session_state.decisions.get(idx, "Pending")

                with st.container():
                    c1, c2, c3 = st.columns([3, 5, 2])
                    with c1:
                        st.markdown(f"**{row['Client Name']}**")
                        st.caption(f"Invoice {row['Invoice Number']} · {row['Invoice Date']}")
                        st.markdown(badge_html(row["Flag"]), unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"**{row['Service Description']}**")
                        st.write(f"R {row['Total Amount (ZAR)']:,.2f}  ·  Rate: R {row['Rate (ZAR)']:,.2f}  ·  Qty: {row['Quantity']}")
                        st.caption(f"💡 {row['Flag Reason']}")
                    with c3:
                        decision = st.selectbox(
                            "Decision",
                            ["Pending", "Approved", "Corrected", "Escalated"],
                            index=["Pending", "Approved", "Corrected", "Escalated"].index(current),
                            key=key,
                            label_visibility="collapsed",
                        )
                        st.session_state.decisions[idx] = decision
                    st.markdown("<hr style='margin:6px 0; opacity:0.2;'>", unsafe_allow_html=True)

            st.write("")
            resolved = sum(1 for v in st.session_state.decisions.values() if v != "Pending")
            st.progress(resolved / len(flagged) if len(flagged) else 0, text=f"{resolved} of {len(flagged)} flagged items resolved")

            if resolved == len(flagged) and len(flagged) > 0:
                st.success("🎉 All flagged items have a decision recorded. These invoices are ready to close.")

# --------------------------------------------------------------------------
# PAGE: ALL INVOICES
# --------------------------------------------------------------------------
elif page == "📚 All Invoices":
    st.markdown("# All Open Invoices")
    st.markdown('<p class="subtitle">The full list currently loaded, clean and flagged items alike.</p>', unsafe_allow_html=True)
    st.write("")

    if st.session_state.invoice_df is None:
        st.info("No invoices loaded yet. Go to **Upload Invoices** first.")
    else:
        df = st.session_state.invoice_df.copy()
        search = st.text_input("🔎 Search by client, invoice number, or service")
        if search:
            mask = df.apply(lambda r: search.lower() in str(r.values).lower(), axis=1)
            df = df[mask]

        display_df = df[["Client Name", "Invoice Number", "Invoice Date", "Service Description",
                          "Rate (ZAR)", "Quantity", "Total Amount (ZAR)", "Flag"]]
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rate (ZAR)": st.column_config.NumberColumn(format="R %.2f"),
                "Total Amount (ZAR)": st.column_config.NumberColumn(format="R %.2f"),
            },
        )
        st.caption(f"Showing {len(df)} of {len(st.session_state.invoice_df)} line items")
