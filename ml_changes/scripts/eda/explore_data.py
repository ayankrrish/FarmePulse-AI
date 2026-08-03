"""
FarmPulse AI - Data Exploration Script
Checks how much data you actually have per state/crop, so we know
which combinations have enough history to train a model on, and which
don't yet (or need CEDA historical backfill).
"""

import pandas as pd

INPUT_FILE = "farmpulse_raw_data.csv"

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])

print("=" * 60)
print("OVERALL SUMMARY")
print("=" * 60)
print(f"Total rows: {len(df)}")
print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
print(f"Unique dates collected so far: {df['date'].nunique()}")
print(f"States: {sorted(df['state'].unique())}")
print(f"Crops: {sorted(df['crop_label'].unique())}")
print(f"Unique mandis: {df['mandi'].nunique()}")

print("\n" + "=" * 60)
print("ROW COUNT PER STATE x CROP (this is what matters most)")
print("=" * 60)
pivot = df.groupby(["state", "crop_label"]).size().unstack(fill_value=0)
print(pivot)

print("\n" + "=" * 60)
print("DAYS OF DATA COLLECTED PER STATE x CROP")
print("=" * 60)
days_pivot = df.groupby(["state", "crop_label"])["date"].nunique().unstack(fill_value=0)
print(days_pivot)

print("\n" + "=" * 60)
print("PRICE SANITY CHECK (min / max / mean modal price per crop)")
print("=" * 60)
print(df.groupby("crop_label")["modal_price"].agg(["min", "max", "mean", "count"]))

print("\n" + "=" * 60)
print("MANDIS PER STATE (to see coverage width)")
print("=" * 60)
print(df.groupby("state")["mandi"].nunique().sort_values(ascending=False))

print("\n" + "=" * 60)
print("WARNING FLAGS")
print("=" * 60)
low_data = pivot[pivot.sum(axis=1) < 10]
if not low_data.empty:
    print("These states have very few total rows across all crops - check state name spelling or crop availability:")
    print(low_data)
else:
    print("No states with critically low row counts.")

# Flag suspicious price outliers (basic sanity check, not final cleaning)
for crop in df["crop_label"].unique():
    crop_df = df[df["crop_label"] == crop]
    q1, q3 = crop_df["modal_price"].quantile([0.05, 0.95])
    outliers = crop_df[(crop_df["modal_price"] < q1 * 0.3) | (crop_df["modal_price"] > q3 * 3)]
    if not outliers.empty:
        print(f"\nPossible price outliers in {crop} ({len(outliers)} rows):")
        print(outliers[["state", "mandi", "date", "modal_price"]])