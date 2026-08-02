# 🧾 Credit Note Workflow

**From a scanned invoice to a signed-off, logged, reportable credit note — with nothing typed twice.**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B)
![Status](https://img.shields.io/badge/Status-Demo-yellow)

An end-to-end workflow automation tool covering document capture (OCR),
structured data entry, PDF generation, a multi-person approval chain,
and automatic reporting — built to replace a real seven-step manual
credit note process.

## The Problem

Issuing a credit note meant: hand-filling a requisition form, chasing
five separate people for signatures one at a time, manually processing
the credit in the billing system, and then **retyping the same
information again** into a monthly tracking spreadsheet for management.

## What It Does

1. **Upload an invoice** — a clean PDF, a scan, or a phone photo
2. **OCR reads out the key fields** automatically (invoice number, date,
   account, client) — shown back as editable fields, never trusted blindly,
   since scan quality varies
3. **Capture what's being credited** — what, how much, why, and who's
   responsible, one line at a time, across one invoice or several
4. **A clean requisition PDF is generated automatically** — credit value,
   re-invoice value, and net value all calculated, not typed by hand
5. **Routed for approval** through the same 5-person chain (Credit
   Supervisor → National Credit Manager → Sales Manager → Finance
   Manager → Managing Director), tracked in-app
6. **Finance processes it** in the billing system (still manual — see
   Limitations) and confirms the real credit note number
7. **The monthly Credit Note File builds itself** — every processed
   credit logs automatically, in the same column layout the business
   already reports from

## Tech Stack

- **Streamlit** — the interface
- **SQLite** — workflow state (draft → pending approval → approved → processed)
- **pytesseract + pdf2image** — OCR for scanned/photographed invoices
- **pdfplumber** — native text extraction for digital PDFs
- **reportlab** — generates the requisition PDF

## Screenshot

*Add a screenshot of the Review Flagged Invoices or Approvals screen here once deployed.*

## Run It Locally

```bash
git clone https://github.com/<your-username>/credit-note-workflow.git
cd credit-note-workflow
pip install -r requirements.txt
streamlit run app.py
```

**Also required on your system** (not pip-installable):

- macOS: `brew install tesseract poppler`
- Ubuntu/Debian: `sudo apt install tesseract-ocr poppler-utils`
- Windows: install [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and [poppler](https://github.com/oschwartz10612/poppler-windows), then add both to your PATH

## Deploy to Streamlit Community Cloud

1. Push this folder to a **public** GitHub repository — make sure
   `packages.txt` is included at the repo root (it tells Streamlit Cloud
   to install `tesseract-ocr` and `poppler-utils`, or OCR will fail silently)
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **New app**, select this repo, branch, and set the main file path to `app.py`
4. Click **Deploy**
5. Copy the live URL into your portfolio / CV

No API keys are required to demo the workflow — e-signing is simulated
in-app (see Limitations below).

## Project Structure

```
credit-note-workflow/
├── app.py                     # Streamlit app
├── db.py                      # SQLite data layer + approval chain
├── ocr_extract.py             # Invoice reading (text + OCR fallback)
├── generate_requisition.py    # Requisition PDF generation
├── docusign_integration.py    # Real e-signature integration point
├── requirements.txt
├── packages.txt                # System deps for Streamlit Cloud (tesseract, poppler)
└── README.md
```

## Known Limitations

- **E-signature is simulated, not live.** Real e-signing requires your
  own DocuSign developer account and API credentials, which can't be
  pre-configured without one. `docusign_integration.py` is fully
  structured for the real DocuSign eSignature API — wiring in real
  credentials is a credentials-and-testing task, not a redesign.
- **Billing system entry stays manual.** The underlying billing system
  has no API, so Finance still enters the approved credit by hand — this
  app removes everything *around* that step, not the step itself.
- OCR accuracy varies with scan/photo quality by design — every field
  is shown for human confirmation before submission, intentionally.

## Why This Project

Built as a practical example of automating a multi-stage business
process end to end — document capture, structured decision-making,
document generation, approval routing, and reporting — while being
explicit about the one step (a legacy system with no API) that
genuinely can't be automated away.
