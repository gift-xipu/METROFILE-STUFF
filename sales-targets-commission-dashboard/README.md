# 📈 Sales Targets & Commission Dashboard

**Replaces a fragile 19-tab Excel workbook with one dashboard everyone can trust.**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B)
![Status](https://img.shields.io/badge/Status-Demo-yellow)

An ETL pipeline and dashboard that replaces a real, heavily manual sales
target and commission workbook — 13 hand-copied rep tabs, live `#REF!`
calculation errors, and a monthly reconciliation done entirely by hand.

## The Problem

Every month, actual sales figures were manually pasted into a workbook
and reconciled against 13 separate salesperson target tabs to calculate
commission. The company-wide summary tab — the report management
actually read — contained visible, unresolved calculation errors.

## What It Does

- **Extracts real targets** directly from all 13 rep sheets, bypassing
  the broken summary formulas entirely (see `pipeline/extract_targets.py`)
- **Normalizes inconsistent data** found along the way: some months were
  stored as free-text labels (`"Sept-25"`) instead of real dates, and
  some reps hadn't been rolled onto the current target year
- **Calculates commission automatically:**
  - Base commission — 5% of actual sales, confirmed against real
    transaction data with zero exceptions
  - Achievement bonus — a clearly labelled *placeholder* tier, pending
    confirmation from Finance (the original bonus-calculation tabs were
    deleted from the source file and could not be recovered)
- **Dashboard** with three views: Monthly Overview, Rep Drill-Down (see
  exactly how one person's number was built), and Trends Across Months

## Tech Stack

- **Streamlit** — the dashboard
- **pandas** — target extraction, normalization, and commission calculation
- **openpyxl** — reading the original `.xlsm` workbook
- **python-dateutil** — resolving inconsistent date formats

## Screenshot

*Add a screenshot of the Monthly Overview or Rep Drill-Down screen here once deployed.*

## Run It Locally

```bash
git clone https://github.com/<your-username>/sales-targets-commission-dashboard.git
cd sales-targets-commission-dashboard
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`, pre-loaded with six months of sample
data (July–December, 16 anonymized reps, real extracted target figures
with synthetic actuals).

## Deploy to Streamlit Community Cloud

1. Push this folder to a **public** GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **New app**, select this repo, branch, and set the main file path to `app.py`
4. Click **Deploy**
5. Copy the live URL into your portfolio / CV

No secrets or API keys required — the app runs entirely on the bundled
sample data.

## Project Structure

```
sales-targets-commission-dashboard/
├── app.py                          # Streamlit dashboard
├── requirements.txt
├── rep_mapping.py                  # Anonymized name mapping
├── pipeline/                       # Reference: how the sample data was built
│   ├── extract_targets.py          # Pulls clean targets from the .xlsm
│   ├── normalize_targets.py        # Aligns all reps to one 12-month cycle
│   ├── generate_synthetic_actuals.py
│   ├── calculate_commissions.py    # Achievement % + commission logic
│   └── rep_mapping.py
├── sample_data/
│   ├── targets_normalized.csv
│   ├── monthly_actuals.csv
│   ├── category_detail.csv
│   └── commission_summary.csv
└── README.md
```

The `pipeline/` scripts aren't needed to run the dashboard day-to-day —
they're included to show the full extraction-to-calculation process, and
to reprocess a new month of real data when available.

## Known Limitations

- **The achievement bonus tier is a placeholder**, not a confirmed
  business rule — clearly labelled in the dashboard itself. Do not use
  these figures for real commission payouts until confirmed with Finance.
- Monthly actuals in this demo are synthetic (varied realistically around
  each rep's real target); only the target figures themselves are real,
  extracted from the source workbook.

## Why This Project

Built as a practical example of untangling a legacy Excel process:
finding the real data-quality issues hiding inside it, deciding what's
safe to automate outright vs. what genuinely needs a human sign-off, and
being transparent about that line rather than papering over it.
