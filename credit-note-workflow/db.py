"""
Data layer for the Credit Note Workflow app.
Uses SQLite since this workflow has real multi-stage state
(draft -> pending approval -> approved -> processed) unlike a simple
flat report, plus a 5-person approval chain that needs to be tracked
per-request.
"""
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "credit_workflow.db"

APPROVAL_CHAIN = [
    ("Credit Supervisor", "Tammy Morrison"),
    ("National Credit Manager", "Noeline Clark"),
    ("Sales Manager", "Jackie Potgieter"),
    ("Finance Manager", "Deena Pillay"),
    ("Managing Director", "Shivan Mansingh"),
]

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            client_name TEXT,
            account_no TEXT,
            region TEXT,
            dept TEXT,
            credit_controller TEXT,
            status TEXT DEFAULT 'draft'
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS request_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER,
            invoice_no TEXT,
            invoice_date TEXT,
            charge_code TEXT,
            description TEXT,
            qty REAL,
            rate REAL,
            credit_amount REAL,
            reinvoice_amount REAL,
            reason TEXT,
            responsible_person TEXT,
            responsible_dept TEXT,
            FOREIGN KEY(request_id) REFERENCES requests(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER,
            order_index INTEGER,
            approver_role TEXT,
            approver_name TEXT,
            status TEXT DEFAULT 'pending',
            signed_at TEXT,
            FOREIGN KEY(request_id) REFERENCES requests(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS credit_note_file (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER,
            company TEXT,
            region TEXT,
            credit_no TEXT,
            credit_note_date TEXT,
            month TEXT,
            year INTEGER,
            invoice_no TEXT,
            invoice_date TEXT,
            account_no TEXT,
            dept TEXT,
            acct_name TEXT,
            cr_amt_excl REAL,
            reinvoice_value REAL,
            net_effect REAL,
            credit_controller TEXT,
            department TEXT,
            responsible_person TEXT,
            reason TEXT,
            billing_system TEXT,
            processed_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def create_request(client_name, account_no, region, dept, credit_controller):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO requests (created_at, client_name, account_no, region, dept, credit_controller, status) VALUES (?,?,?,?,?,?,?)",
        (datetime.now().isoformat(), client_name, account_no, region, dept, credit_controller, "draft"),
    )
    request_id = c.lastrowid
    conn.commit()
    conn.close()
    return request_id

def add_request_item(request_id, invoice_no, invoice_date, charge_code, description,
                      qty, rate, credit_amount, reinvoice_amount, reason,
                      responsible_person, responsible_dept):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO request_items
        (request_id, invoice_no, invoice_date, charge_code, description, qty, rate,
         credit_amount, reinvoice_amount, reason, responsible_person, responsible_dept)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (request_id, invoice_no, invoice_date, charge_code, description, qty, rate,
          credit_amount, reinvoice_amount, reason, responsible_person, responsible_dept))
    conn.commit()
    conn.close()

def get_request_items(request_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM request_items WHERE request_id=?", (request_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_request(request_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM requests WHERE id=?", (request_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def list_requests(status=None):
    conn = get_conn()
    if status:
        rows = conn.execute("SELECT * FROM requests WHERE status=? ORDER BY id DESC", (status,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM requests ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def submit_for_approval(request_id):
    conn = get_conn()
    c = conn.cursor()
    for i, (role, name) in enumerate(APPROVAL_CHAIN):
        c.execute(
            "INSERT INTO approvals (request_id, order_index, approver_role, approver_name, status) VALUES (?,?,?,?,?)",
            (request_id, i, role, name, "pending"),
        )
    c.execute("UPDATE requests SET status=? WHERE id=?", ("pending_approval", request_id))
    conn.commit()
    conn.close()

def get_approvals(request_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM approvals WHERE request_id=? ORDER BY order_index", (request_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def sign_next_approval(request_id):
    """Simulates the next pending approver signing via DocuSign.
    See docusign_integration.py for where this plugs into the real API."""
    conn = get_conn()
    c = conn.cursor()
    next_approval = c.execute(
        "SELECT * FROM approvals WHERE request_id=? AND status='pending' ORDER BY order_index LIMIT 1",
        (request_id,),
    ).fetchone()
    if next_approval:
        c.execute(
            "UPDATE approvals SET status='signed', signed_at=? WHERE id=?",
            (datetime.now().isoformat(), next_approval["id"]),
        )
        remaining = c.execute(
            "SELECT COUNT(*) as cnt FROM approvals WHERE request_id=? AND status='pending'",
            (request_id,),
        ).fetchone()["cnt"]
        if remaining == 0:
            c.execute("UPDATE requests SET status='approved' WHERE id=?", (request_id,))
        conn.commit()
    conn.close()

def mark_processed(request_id, credit_no_map, billing_system="METROMANAGER"):
    """
    Called by finance once they've manually entered the credit(s) into the
    billing system. credit_no_map: {request_item_id: real_credit_note_number}
    Writes one row per line item into credit_note_file, auto-filled from
    data already captured earlier in the workflow -- finance only has to
    type in the credit note number the billing system generated.
    """
    req = get_request(request_id)
    items = get_request_items(request_id)
    now = datetime.now()
    conn = get_conn()
    c = conn.cursor()
    for item in items:
        credit_no = credit_no_map.get(item["id"], "")
        net_effect = (item["credit_amount"] or 0) - (item["reinvoice_amount"] or 0)
        c.execute("""
            INSERT INTO credit_note_file
            (request_id, company, region, credit_no, credit_note_date, month, year,
             invoice_no, invoice_date, account_no, dept, acct_name, cr_amt_excl,
             reinvoice_value, net_effect, credit_controller, department,
             responsible_person, reason, billing_system, processed_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            request_id, "Metrofile", req["region"], credit_no, now.strftime("%Y-%m-%d"),
            now.strftime("%B"), now.year, item["invoice_no"], item["invoice_date"],
            req["account_no"], req["dept"], req["client_name"], item["credit_amount"],
            item["reinvoice_amount"], -net_effect, req["credit_controller"],
            item["responsible_dept"], item["responsible_person"], item["reason"],
            billing_system, now.isoformat(),
        ))
    c.execute("UPDATE requests SET status='processed' WHERE id=?", (request_id,))
    conn.commit()
    conn.close()

def get_credit_note_file(month=None, year=None):
    conn = get_conn()
    query = "SELECT * FROM credit_note_file"
    params = []
    if month and year:
        query += " WHERE month=? AND year=?"
        params = [month, year]
    query += " ORDER BY id DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]
