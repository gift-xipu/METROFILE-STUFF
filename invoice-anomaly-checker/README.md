# 🧾 Invoice Anomaly Checker

**Catches billing errors before invoices reach the client — not after.**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B)
![Status](https://img.shields.io/badge/Status-Demo-yellow)

A lightweight anomaly-detection tool that replaces manual, ad-hoc invoice
review before month-end close. Upload an open-invoice export, and it
automatically flags duplicates, rate mismatches, and unusual amounts —
with a plain-language reason for every flag, reviewed on a simple
dashboard instead of a spreadsheet.

## The Problem

Before invoices close each month, someone has to manually eyeball every
open invoice for mistakes — duplicate charges, wrong rates, amounts that
don't look right. At any real volume, this doesn't scale, and errors
that slip through are usually only caught after the client complains.

## What It Does

- **Upload** an open-invoice spreadsheet (Excel export)
- **Automatically flags:**
  - **Duplicate invoices** — the same charge billed more than once
  - **Rate mismatches** — a rate more than 20% off the norm for that service
  - **Unusual amounts** — statistical outliers vs. similar historical charges
- **Reviews flagged items** on a clean dashboard, each with a plain-English
  reason, filterable by client or flag type
- **Tracks decisions** — Approved / Corrected / Escalated, with a live
  progress bar

## Tech Stack

- **Streamlit** — the interface
- **pandas** — data loading and anomaly-detection logic
- **openpyxl** — reading Excel exports

## Screenshot

*Add a screenshot of the Review Flagged Invoices screen here once deployed.*

## Run It Locally

```bash
git clone https://github.com/<your-username>/invoice-anomaly-checker.git
cd invoice-anomaly-checker
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`. Click **Load Sample Data** on the
Dashboard to try it immediately with the included example dataset (a
fictional South African storage company, 113 invoice line items, ZAR).

## Deploy to Streamlit Community Cloud

1. Push this folder to a **public** GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **New app**
4. Select this repository, the branch (usually `main`), and set the main file path to `app.py`
5. Click **Deploy** — Streamlit Cloud installs everything in `requirements.txt` automatically
6. Once live, copy the app URL into your portfolio / CV

No secrets or API keys are needed for this app — it runs entirely on
sample data and whatever file the user uploads.

## Project Structure

```
invoice-anomaly-checker/
├── app.py                                    # Streamlit app
├── requirements.txt
├── sample_data/
│   └── Open_Invoice_Download_Example_ZAR.xlsx # Demo dataset
└── README.md
```

## Known Limitations

- "Normal" is currently calculated from the uploaded batch itself. A
  production version would compare against a saved rolling history
  (e.g. the last 6 months), not just the current upload.
- Decisions made in the Review screen live only in the browser session —
  persisting them (file or database) is a natural next step.

## Why This Project

Built as a practical example of automating a repetitive finance-admin
task: turning a manual, error-prone spreadsheet review into a system
that catches what a person would otherwise only find by accident — or
too late.
