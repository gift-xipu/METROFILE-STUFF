"""
Aligns every rep onto the same 12-month target cycle for presentation
purposes. The source workbook has 5 reps rolled forward to the new
target year (Jul 2025 - Jun 2026) and 11 reps still sitting on the old
year (Jul 2024 - Jun 2025) -- a real sync issue in the original file,
plus some reps have the same 12 months duplicated across both blocks.
For a coherent demo dashboard, we take each rep's most recent 12
distinct months per category and relabel them onto a shared
Jul 2025 - Jun 2026 calendar by position, keeping the real target
figures untouched.
"""
import pandas as pd

df = pd.read_csv("clean_targets.csv", parse_dates=["Month"])
SHARED_CYCLE = pd.date_range("2025-07-01", periods=12, freq="MS")

rows = []
for rep in df["Rep"].unique():
    rep_df = df[df["Rep"] == rep]
    for category in sorted(rep_df["Category"].unique()):
        cat_df = rep_df[rep_df["Category"] == category].copy()
        cat_df = cat_df.drop_duplicates(subset="Month", keep="last").sort_values("Month")
        cat_df = cat_df.tail(12)
        if len(cat_df) != 12:
            print(f"  skipping {rep} / {category}: only {len(cat_df)} distinct months found")
            continue
        for i, (_, r) in enumerate(cat_df.iterrows()):
            rows.append({
                "Rep": rep,
                "Category": category,
                "Month": SHARED_CYCLE[i],
                "Target Revenue (ZAR)": r["Target Revenue (ZAR)"],
            })

out = pd.DataFrame(rows)
out.to_csv("targets_normalized.csv", index=False)
print(f"\nNormalized {len(out)} rows across {out['Rep'].nunique()} reps, {out['Category'].nunique()} categories, {out['Month'].nunique()} months")
print(out.groupby("Rep").size())
