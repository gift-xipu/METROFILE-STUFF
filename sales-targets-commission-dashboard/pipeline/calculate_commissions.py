"""
Merges actuals against targets, calculates achievement %, and applies
the commission model:

  - Base commission: 5% of actual revenue (confirmed from the real ERP
    export - every transaction line matched this exactly, no exceptions)
  - Bonus: a PLACEHOLDER tiered bonus on top, applied to a rep's total
    monthly revenue once their overall monthly achievement % is known.
    This tier table is a stand-in until the real rule is confirmed --
    it is intentionally kept as a simple, editable table rather than
    buried in calculation logic.
"""
import pandas as pd

BASE_COMMISSION_RATE = 0.05

# PLACEHOLDER bonus tiers -- confirm real values with finance/management.
# (min achievement %, max achievement %, bonus rate applied to actual revenue)
BONUS_TIERS = [
    (0, 80, 0.00),
    (80, 100, 0.01),
    (100, 120, 0.02),
    (120, float("inf"), 0.03),
]

def bonus_rate_for_achievement(pct):
    for low, high, rate in BONUS_TIERS:
        if low <= pct < high:
            return rate
    return 0.0

def main():
    targets = pd.read_csv("targets_normalized.csv", parse_dates=["Month"])
    actuals = pd.read_csv("monthly_actuals.csv", parse_dates=["Month"])

    merged = pd.merge(
        actuals, targets,
        on=["Rep", "Category", "Month"],
        how="left",
        suffixes=("", "_target"),
    ).fillna(0)

    # --- Category level detail ---
    merged["Achievement %"] = merged.apply(
        lambda r: round((r["Actual Revenue (ZAR)"] / r["Target Revenue (ZAR)"]) * 100, 1)
        if r["Target Revenue (ZAR)"] > 0 else (100.0 if r["Actual Revenue (ZAR)"] == 0 else None),
        axis=1,
    )
    merged["Base Commission (ZAR)"] = round(merged["Actual Revenue (ZAR)"] * BASE_COMMISSION_RATE, 2)

    # --- Rep + Month level summary (achievement is measured on TOTAL revenue, not per category) ---
    summary = merged.groupby(["Rep", "Month"], as_index=False).agg(
        **{
            "Actual Revenue (ZAR)": ("Actual Revenue (ZAR)", "sum"),
            "Target Revenue (ZAR)": ("Target Revenue (ZAR)", "sum"),
        }
    )
    summary["Achievement %"] = summary.apply(
        lambda r: round((r["Actual Revenue (ZAR)"] / r["Target Revenue (ZAR)"]) * 100, 1)
        if r["Target Revenue (ZAR)"] > 0 else 0.0,
        axis=1,
    )
    summary["Base Commission (ZAR)"] = round(summary["Actual Revenue (ZAR)"] * BASE_COMMISSION_RATE, 2)
    summary["Bonus Rate Applied"] = summary["Achievement %"].apply(bonus_rate_for_achievement)
    summary["Bonus (ZAR)"] = round(summary["Actual Revenue (ZAR)"] * summary["Bonus Rate Applied"], 2)
    summary["Total Commission (ZAR)"] = summary["Base Commission (ZAR)"] + summary["Bonus (ZAR)"]

    merged.to_csv("category_detail.csv", index=False)
    summary.to_csv("commission_summary.csv", index=False)

    print(f"Category-level detail: {len(merged)} rows -> category_detail.csv")
    print(f"Rep/month commission summary: {len(summary)} rows -> commission_summary.csv\n")
    print(summary.sort_values(["Month", "Total Commission (ZAR)"], ascending=[True, False]).head(15).to_string(index=False))

if __name__ == "__main__":
    main()
