"""
Generates realistic synthetic monthly 'actuals' data for six months
(Jul 2025 - Dec 2025), matching the reps and categories from the
extracted target data. Each rep's actuals are generated to vary
around their own target -- some hit it, some don't, some blow past it --
so the dashboard has a realistic mix to demonstrate achievement %
and commission calculations across a real date range.

This uses the anonymized rep names from rep_mapping.py, consistent with
the extracted target data.
"""
import pandas as pd
import numpy as np

np.random.seed(11)

targets = pd.read_csv("targets_normalized.csv", parse_dates=["Month"])

# Full 6-month demo window: Jul 2025 - Dec 2025, now available for all 16 reps
window = targets[(targets["Month"] >= "2025-07-01") & (targets["Month"] <= "2025-12-01")].copy()

# Each rep gets a "performance profile" - a rough multiplier around their target,
# with some month-to-month noise, so the dashboard shows realistic variation.
reps = window["Rep"].unique()
performance_profile = {}
for rep in reps:
    if rep == "House Account":
        performance_profile[rep] = 1.0
        continue
    # base performance level per rep: some strong, some struggling, most average
    base = np.random.choice([0.65, 0.85, 0.95, 1.05, 1.15, 1.30], p=[0.15, 0.2, 0.25, 0.2, 0.12, 0.08])
    performance_profile[rep] = base

records = []
for _, row in window.iterrows():
    rep = row["Rep"]
    category = row["Category"]
    month = row["Month"]
    target = row["Target Revenue (ZAR)"]

    base_perf = performance_profile.get(rep, 1.0)
    # add month-to-month noise (+/- 15%)
    noise = np.random.normal(1.0, 0.15)
    multiplier = max(base_perf * noise, 0)

    if target == 0:
        # reps/categories with no target: small incidental sales only, if any
        actual = round(np.random.choice([0, 0, 0, np.random.uniform(500, 5000)]), 2)
    else:
        actual = round(target * multiplier, 2)

    records.append({
        "Month": month,
        "Rep": rep,
        "Category": category,
        "Actual Revenue (ZAR)": actual,
    })

actuals_df = pd.DataFrame(records)
actuals_df.to_csv("monthly_actuals.csv", index=False)
print(f"Generated {len(actuals_df)} actuals rows across {actuals_df['Month'].nunique()} months and {actuals_df['Rep'].nunique()} reps")
print(actuals_df.head(15))
