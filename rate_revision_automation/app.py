"""
Rate Revision Automation - Streamlit control panel
====================================================
Run with:  streamlit run app.py

A month picker, a Generate button, a preview of every letter/schedule about
to go out, and a Send section - this is the "button" version of the
pipeline, replacing a VBA macro with a proper (and much easier to extend) UI.

Must run on the machine that will do the sending (Windows, Outlook installed
and logged in) if you want the Send buttons to work - generation and preview
work anywhere.
"""
import io
import os
import platform
import shutil
import zipfile
from datetime import date

import openpyxl
import pandas as pd
import streamlit as st

import pipeline
import mailer

st.set_page_config(page_title="Rate Revision Automation", page_icon="📋", layout="wide")

NAVY = "#1F3864"
STEEL = "#2E5395"

st.markdown(f"""
<div style="background-color:{NAVY};padding:20px 28px;border-radius:6px;margin-bottom:0px;">
  <h1 style="color:white;margin:0;font-size:28px;">Rate Revision Automation</h1>
  <p style="color:#D6E0F0;margin:4px 0 0 0;font-size:14px;">
    Generate and send price increase letters &amp; rate schedules for clients due for notification.
  </p>
</div>
""", unsafe_allow_html=True)
st.write("")

if "manifest" not in st.session_state:
    st.session_state.manifest = None
if "target_month" not in st.session_state:
    st.session_state.target_month = None

# ---------------- Step 1: choose month & generate ----------------
st.subheader("1. Generate this month's pack")

col1, col2, col3 = st.columns([2, 1, 3])
with col1:
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    today = date.today()
    default_month_idx = today.month - 1
    sel_month = st.selectbox("Month", months, index=default_month_idx)
with col2:
    sel_year = st.number_input("Year", min_value=2024, max_value=2035, value=today.year, step=1)
with col3:
    st.write("")
    st.write("")
    generate_clicked = st.button("🔄  Generate pack", type="primary", use_container_width=True)

if generate_clicked:
    month_str = f"{sel_month} {sel_year}"
    with st.spinner(f"Reading tracker, matching clients due for notification in {month_str}..."):
        entries = pipeline.generate_pack(month_str)
    st.session_state.manifest = entries
    st.session_state.target_month = month_str
    if entries:
        st.success(f"Generated {len(entries)} letter + rate schedule pair(s) for {month_str}.")
    else:
        st.warning(f"No clients are due for notification in {month_str}. Nothing was generated.")

# ---------------- Step 2: review ----------------
if st.session_state.manifest:
    st.subheader(f"2. Review \u2013 {st.session_state.target_month}")

    entries = st.session_state.manifest
    df = pd.DataFrame([{
        "Client": e["client"],
        "Price Level": e["price_level"],
        "Sales Person": e["sp_name"],
        "Sales Person Email": e["sp_email"],
        "Effective Date": e["effective_date"].strftime("%d %B %Y"),
        "Rates": "⚠️ Placeholder" if e.get("placeholder_rates") else "✅ Standard",
    } for e in entries])

    st.dataframe(df, use_container_width=True, hide_index=True)

    n_placeholder = sum(1 for e in entries if e.get("placeholder_rates"))
    if n_placeholder:
        st.caption(f"⚠️ {n_placeholder} client(s) above are using placeholder/standard rates because "
                   f"their negotiated Price Level isn't in master_rates.xlsx yet.")

    with st.expander("🔍 Preview an individual letter & rate schedule"):
        client_names = [e["client"] for e in entries]
        picked = st.selectbox("Client", client_names)
        picked_entry = next(e for e in entries if e["client"] == picked)

        pcol1, pcol2 = st.columns(2)
        with pcol1:
            st.markdown(f"**Letter:** `{os.path.basename(picked_entry['letter_path'])}`")
            with open(picked_entry["letter_path"], "rb") as f:
                st.download_button("⬇ Download letter (.docx)", f, file_name=os.path.basename(picked_entry["letter_path"]))
        with pcol2:
            st.markdown(f"**Rate schedule:** `{os.path.basename(picked_entry['schedule_path'])}`")
            rate_rows = picked_entry.get("rate_rows") or []
            if rate_rows:
                rdf = pd.DataFrame(rate_rows)[["Category", "Item", "ChargeCode", "Rate"]]
                st.dataframe(rdf, use_container_width=True, hide_index=True, height=250)
            with open(picked_entry["schedule_path"], "rb") as f:
                st.download_button("⬇ Download rate schedule (.xlsx)", f, file_name=os.path.basename(picked_entry["schedule_path"]))

    # Download everything as one zip
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(pipeline.OUTPUT_DIR):
            for file in files:
                fp = os.path.join(root, file)
                arcname = os.path.relpath(fp, pipeline.OUTPUT_DIR)
                zf.write(fp, arcname)
    st.download_button("⬇ Download everything (.zip)", zip_buffer.getvalue(),
                        file_name=f"rate_revision_pack_{st.session_state.target_month.replace(' ', '_')}.zip",
                        use_container_width=False)

    # ---------------- Step 3: send ----------------
    st.subheader("3. Send to sales people")

    is_windows = platform.system() == "Windows"
    if not is_windows:
        st.info("This app isn't running on Windows right now, so Outlook can't be driven directly here "
                 "\u2013 the buttons below will run in **preview mode** (Dry run) regardless of your "
                 "selection. Run this same app on the Windows machine with Outlook installed to send for real.")

    mode = st.radio("Mode", ["Dry run (preview only)", "Create Outlook drafts (for review)", "Send now"],
                     horizontal=True)

    confirm = True
    if mode == "Send now":
        confirm = st.checkbox(f"I've reviewed the {len(entries)} letter(s) above and want to send them now.")

    send_clicked = st.button("📧  Execute", type="primary", disabled=(mode == "Send now" and not confirm))

    if send_clicked:
        dry_run = (mode == "Dry run (preview only)") or not is_windows
        draft_only = (mode == "Create Outlook drafts (for review)")
        try:
            with st.spinner("Working..."):
                results = mailer.send_all(dry_run=dry_run, draft_only=draft_only)
            rdf = pd.DataFrame(results)
            st.dataframe(rdf, use_container_width=True, hide_index=True)
            if dry_run:
                st.info("Preview only \u2013 nothing was sent or drafted.")
            else:
                st.success(f"Done: {len(results)} email(s) processed.")
        except RuntimeError as e:
            st.error(str(e))
else:
    st.caption("Pick a month above and click **Generate pack** to get started.")
