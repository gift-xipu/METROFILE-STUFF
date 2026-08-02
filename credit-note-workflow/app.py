"""
Credit Note Workflow
----------------------
Automates the manual credit request process: upload an invoice, OCR
pulls out the key fields, you're prompted for what's being credited and
why, a clean requisition PDF is generated automatically, it's routed for
sign-off, and once finance confirms it's processed in the billing
system, it's logged straight into the Credit Note File -- no re-typing.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

import db
from ocr_extract import process_upload
from generate_requisition import generate_requisition_pdf
import docusign_integration as docusign

st.set_page_config(
    page_title="Credit Note Workflow",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()

APP_DIR = Path(__file__).parent
GENERATED_DIR = APP_DIR / "generated"
GENERATED_DIR.mkdir(exist_ok=True)

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
    h1, h2, h3 {{ color: {NAVY}; font-family: 'Georgia', serif; }}
    .subtitle {{ color: {GREY}; font-size: 1.05rem; margin-top: -10px; }}
    .badge {{
        display: inline-block; padding: 3px 10px; border-radius: 20px;
        font-size: 0.8rem; font-weight: 600; color: white;
    }}
    .badge-draft {{ background-color: {GREY}; }}
    .badge-pending {{ background-color: {AMBER}; }}
    .badge-approved {{ background-color: #2E7D32; }}
    .badge-processed {{ background-color: {NAVY}; }}
    .note-box {{
        background-color: #FBEEEE; border-left: 4px solid {RED};
        padding: 12px 16px; border-radius: 6px; font-size: 0.88rem; color: #262626;
    }}
</style>
""", unsafe_allow_html=True)

STATUS_BADGE = {
    "draft": '<span class="badge badge-draft">Draft</span>',
    "pending_approval": '<span class="badge badge-pending">Pending Approval</span>',
    "approved": '<span class="badge badge-approved">Approved</span>',
    "processed": '<span class="badge badge-processed">Processed</span>',
}

if "new_items" not in st.session_state:
    st.session_state.new_items = []
if "ocr_fields" not in st.session_state:
    st.session_state.ocr_fields = None

# --------------------------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------------------------
st.sidebar.markdown("## 🧾 Credit Note Workflow")
st.sidebar.markdown("From invoice to approved credit, no re-typing.")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Go to",
    ["🏠 Dashboard", "📤 New Credit Request", "✍️ Approvals", "✅ Finance Processing", "📊 Monthly Report"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='font-size:0.82rem; opacity:0.75;'>"
    "E-signature step uses a simulated approval flow in this demo. "
    "See docusign_integration.py for how real DocuSign credentials plug in."
    "</div>",
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# PAGE: DASHBOARD
# --------------------------------------------------------------------------
if page == "🏠 Dashboard":
    st.markdown("# Dashboard")
    st.markdown('<p class="subtitle">Every credit request, wherever it is in the process.</p>', unsafe_allow_html=True)
    st.write("")

    all_requests = db.list_requests()
    draft = [r for r in all_requests if r["status"] == "draft"]
    pending = [r for r in all_requests if r["status"] == "pending_approval"]
    approved = [r for r in all_requests if r["status"] == "approved"]
    processed = [r for r in all_requests if r["status"] == "processed"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Drafts", len(draft))
    c2.metric("Awaiting Sign-off", len(pending))
    c3.metric("Approved, Not Yet Processed", len(approved))
    c4.metric("Processed This Session", len(processed))

    st.write("")
    st.markdown("### All requests")
    if not all_requests:
        st.info("No credit requests yet. Start one under **New Credit Request**.")
    else:
        for r in all_requests:
            items = db.get_request_items(r["id"])
            total = sum(i["credit_amount"] or 0 for i in items)
            c1, c2, c3 = st.columns([3, 4, 2])
            with c1:
                st.markdown(f"**Request #{r['id']} — {r['client_name']}**")
                st.markdown(STATUS_BADGE.get(r["status"], r["status"]), unsafe_allow_html=True)
            with c2:
                st.write(f"{len(items)} line item(s)  ·  Account {r['account_no']}  ·  {r['region']}")
                st.caption(f"Created {r['created_at'][:16].replace('T', ' ')}")
            with c3:
                st.markdown(f"### R {total:,.2f}")
            st.markdown("<hr style='margin:4px 0; opacity:0.15;'>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# PAGE: NEW CREDIT REQUEST
# --------------------------------------------------------------------------
elif page == "📤 New Credit Request":
    st.markdown("# New Credit Request")
    st.markdown('<p class="subtitle">Upload an invoice, confirm the details, and add what needs crediting.</p>', unsafe_allow_html=True)
    st.write("")

    st.markdown("### 1. Upload the invoice")
    uploaded = st.file_uploader(
        "Invoice (PDF, or a photo/scan — JPG, PNG)",
        type=["pdf", "png", "jpg", "jpeg"],
    )

    if uploaded is not None and st.button("Read invoice"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded.name).suffix) as tmp:
            tmp.write(uploaded.getvalue())
            tmp_path = tmp.name
        with st.spinner("Reading invoice..."):
            try:
                text, fields = process_upload(tmp_path, Path(uploaded.name).suffix)
                st.session_state.ocr_fields = fields
                st.success("Invoice read. Please check the fields below — scanned documents aren't always perfect, so confirm everything before continuing.")
            except Exception as e:
                st.error(f"Couldn't read that file: {e}")

    if st.session_state.ocr_fields is not None:
        st.markdown("### 2. Confirm the extracted details")
        st.caption("Edit anything that wasn't read correctly.")
        f = st.session_state.ocr_fields
        c1, c2 = st.columns(2)
        with c1:
            client_name = st.text_input("Client name", value=f.get("client_name", ""))
            account_no = st.text_input("Account number", value=f.get("account_no", ""))
            invoice_no = st.text_input("Invoice number", value=f.get("invoice_no", ""))
        with c2:
            region = st.text_input("Region", value=f.get("region", ""))
            dept = st.text_input("Department", value="")
            invoice_date = st.text_input("Invoice date", value=f.get("invoice_date", ""))

        st.write("")
        st.markdown("### 3. What's being credited?")
        st.caption("Add one line at a time. You can add more than one — for the same invoice, or a different one.")

        with st.form("add_item_form", clear_on_submit=True):
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                item_invoice_no = st.text_input("Invoice number", value=invoice_no)
                charge_code = st.text_input("Charge code (e.g. LHF, SM2)")
            with fc2:
                description = st.text_input("Description (e.g. Location Handling Fee)")
                qty = st.number_input("Quantity", min_value=0.0, value=1.0)
            with fc3:
                rate = st.number_input("Rate (R, excl. VAT)", min_value=0.0, value=0.0)
                credit_amount = st.number_input("Credit amount (R, excl. VAT)", min_value=0.0, value=0.0)
            reinvoice_amount = st.number_input("Re-invoice amount, if applicable (R, excl. VAT)", min_value=0.0, value=0.0)
            reason = st.text_area("Reason for this credit")
            fc4, fc5 = st.columns(2)
            with fc4:
                responsible_person = st.text_input("Who is responsible for this credit?")
            with fc5:
                responsible_dept = st.text_input("Their department (e.g. Sales, Operations, Billing)")

            add_clicked = st.form_submit_button("Add this line item")
            if add_clicked:
                st.session_state.new_items.append({
                    "invoice_no": item_invoice_no, "invoice_date": invoice_date,
                    "charge_code": charge_code, "description": description,
                    "qty": qty, "rate": rate, "credit_amount": credit_amount,
                    "reinvoice_amount": reinvoice_amount, "reason": reason,
                    "responsible_person": responsible_person, "responsible_dept": responsible_dept,
                })
                st.rerun()

        if st.session_state.new_items:
            st.write("")
            st.markdown(f"**{len(st.session_state.new_items)} line item(s) added so far:**")
            items_df = pd.DataFrame(st.session_state.new_items)
            st.dataframe(
                items_df[["invoice_no", "charge_code", "description", "credit_amount", "reinvoice_amount", "reason"]],
                use_container_width=True, hide_index=True,
            )
            total_credit = sum(i["credit_amount"] for i in st.session_state.new_items)
            st.markdown(f"**Total credit value: R {total_credit:,.2f}**")

            st.write("")
            if st.button("Create requisition and submit for approval", type="primary"):
                request_id = db.create_request(client_name, account_no, region, dept, "Credit Controller")
                for item in st.session_state.new_items:
                    db.add_request_item(request_id, **item)
                db.submit_for_approval(request_id)

                req = db.get_request(request_id)
                items = db.get_request_items(request_id)
                approvals = db.get_approvals(request_id)
                pdf_path = GENERATED_DIR / f"requisition_{request_id}.pdf"
                generate_requisition_pdf(str(pdf_path), req, items, approvals)

                st.session_state.new_items = []
                st.session_state.ocr_fields = None
                st.success(f"Request #{request_id} created and sent for approval.")
                st.rerun()

# --------------------------------------------------------------------------
# PAGE: APPROVALS
# --------------------------------------------------------------------------
elif page == "✍️ Approvals":
    st.markdown("# Approvals")
    st.markdown('<p class="subtitle">Track sign-off through the approval chain.</p>', unsafe_allow_html=True)
    st.write("")

    pending_requests = db.list_requests(status="pending_approval")
    approved_requests = db.list_requests(status="approved")

    if not pending_requests and not approved_requests:
        st.info("Nothing awaiting approval right now.")

    for r in pending_requests + approved_requests:
        items = db.get_request_items(r["id"])
        approvals = db.get_approvals(r["id"])
        total = sum(i["credit_amount"] or 0 for i in items)

        with st.expander(f"Request #{r['id']} — {r['client_name']} — R {total:,.2f}", expanded=(r["status"] == "pending_approval")):
            st.markdown(STATUS_BADGE.get(r["status"], r["status"]), unsafe_allow_html=True)
            st.write("")
            for a in approvals:
                icon = "✅" if a["status"] == "signed" else "⏳"
                st.write(f"{icon} **{a['approver_role']}** — {a['approver_name']}  ·  {a['status'].upper()}" + (f"  ·  {a['signed_at'][:16].replace('T',' ')}" if a["signed_at"] else ""))

            pdf_path = GENERATED_DIR / f"requisition_{r['id']}.pdf"
            if pdf_path.exists():
                with open(pdf_path, "rb") as f:
                    st.download_button("Download requisition PDF", f, file_name=f"requisition_{r['id']}.pdf", key=f"dl_{r['id']}")

            if r["status"] == "pending_approval":
                next_pending = next((a for a in approvals if a["status"] == "pending"), None)
                if next_pending:
                    if st.button(f"Sign as {next_pending['approver_name']} ({next_pending['approver_role']})", key=f"sign_{r['id']}"):
                        db.sign_next_approval(r["id"])
                        st.rerun()

# --------------------------------------------------------------------------
# PAGE: FINANCE PROCESSING
# --------------------------------------------------------------------------
elif page == "✅ Finance Processing":
    st.markdown("# Finance Processing")
    st.markdown('<p class="subtitle">Once processed in the billing system, confirm the real credit note number here — everything else is already filled in.</p>', unsafe_allow_html=True)
    st.write("")

    approved_requests = db.list_requests(status="approved")
    if not approved_requests:
        st.info("Nothing approved and waiting to be processed right now.")

    for r in approved_requests:
        items = db.get_request_items(r["id"])
        total = sum(i["credit_amount"] or 0 for i in items)
        with st.expander(f"Request #{r['id']} — {r['client_name']} — R {total:,.2f}", expanded=True):
            st.dataframe(
                pd.DataFrame(items)[["invoice_no", "charge_code", "description", "credit_amount", "reinvoice_amount", "reason", "responsible_person"]],
                use_container_width=True, hide_index=True,
            )
            st.write("")
            st.markdown("**Enter the credit note number issued by the billing system for each line:**")
            credit_no_map = {}
            for it in items:
                credit_no = st.text_input(
                    f"Credit note number — {it['invoice_no']} ({it['description']})",
                    key=f"creditno_{it['id']}",
                )
                credit_no_map[it["id"]] = credit_no
            billing_system = st.selectbox("Billing system used", ["METROMANAGER", "X3"], key=f"bs_{r['id']}")

            if st.button("Mark as processed and log to Credit Note File", key=f"process_{r['id']}", type="primary"):
                if all(credit_no_map.values()):
                    db.mark_processed(r["id"], credit_no_map, billing_system)
                    st.success(f"Request #{r['id']} logged to the Credit Note File. No re-typing needed.")
                    st.rerun()
                else:
                    st.warning("Please enter a credit note number for every line item before marking as processed.")

# --------------------------------------------------------------------------
# PAGE: MONTHLY REPORT
# --------------------------------------------------------------------------
elif page == "📊 Monthly Report":
    st.markdown("# Monthly Report")
    st.markdown('<p class="subtitle">The Credit Note File — built automatically as requests are processed.</p>', unsafe_allow_html=True)
    st.write("")

    all_rows = db.get_credit_note_file()
    if not all_rows:
        st.info("No processed credit notes yet this session. Once Finance marks requests as processed, they'll appear here automatically.")
    else:
        df = pd.DataFrame(all_rows)
        c1, c2, c3 = st.columns(3)
        c1.metric("Credit Notes Logged", len(df))
        c2.metric("Total Credited (Excl. VAT)", f"R {df['cr_amt_excl'].sum():,.2f}")
        c3.metric("Total Net Effect", f"R {df['net_effect'].sum():,.2f}")

        st.write("")
        st.markdown("### By responsible department")
        by_dept = df.groupby("department")["cr_amt_excl"].sum().sort_values(ascending=False)
        st.bar_chart(by_dept)

        st.write("")
        st.markdown("### Full Credit Note File")
        display_cols = ["company", "region", "credit_no", "credit_note_date", "month", "year",
                         "invoice_no", "invoice_date", "account_no", "dept", "acct_name",
                         "cr_amt_excl", "reinvoice_value", "net_effect", "credit_controller",
                         "department", "responsible_person", "reason", "billing_system"]
        st.dataframe(
            df[display_cols],
            use_container_width=True, hide_index=True,
            column_config={
                "cr_amt_excl": st.column_config.NumberColumn("CrAmtExcl", format="R %.2f"),
                "reinvoice_value": st.column_config.NumberColumn("Re-Invoice Value", format="R %.2f"),
                "net_effect": st.column_config.NumberColumn("Net Effect", format="R %.2f"),
            },
        )

        csv = df[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button("Download as CSV (for the monthly report)", csv, file_name="credit_note_file.csv", mime="text/csv")
