"""
FarmPulse AI - CEDA Historical Data Exploration
Checks trends, seasonality, gaps, and data quality before any modeling begins.
Saves one plot per crop (all 8 states overlaid) so you can visually inspect
trends and seasonality.
"""

import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "ceda_historical_data.csv"

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])

print("=" * 60)
print("OVERALL SUMMARY")
print("=" * 60)
print(f"Total rows: {len(df)}")
print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
print(f"States: {sorted(df['state'].unique())}")
print(f"Crops: {sorted(df['crop_label'].unique())}")

print("\n" + "=" * 60)
print("MONTHS OF DATA PER STATE x CROP")
print("=" * 60)
pivot = df.groupby(["state", "crop_label"])["date"].nunique().unstack(fill_value=0)
print(pivot)

print("\n" + "=" * 60)
print("PRICE RANGE SANITY CHECK PER CROP")
print("=" * 60)
print(df.groupby("crop_label")["modal_price"].agg(["min", "max", "mean", "std"]))

print("\n" + "=" * 60)
print("GAP CHECK: are there missing months within each state-crop's own range?")
print("=" * 60)
for (state, crop), group in df.groupby(["state", "crop_label"]):
    group = group.sort_values("date")
    if len(group) < 2:
        continue
    full_range = pd.date_range(group["date"].min(), group["date"].max(), freq="MS")
    missing = len(full_range) - len(group)
    if missing > 0:
        print(f"  {state} - {crop}: {missing} missing months out of {len(full_range)} expected")

print("\n" + "=" * 60)
print("Saving trend plots (one per crop, all states overlaid)...")
print("=" * 60)

for crop in df["crop_label"].unique():
    crop_df = df[df["crop_label"] == crop]
    plt.figure(figsize=(12, 6))
    for state in crop_df["state"].unique():
        state_df = crop_df[crop_df["state"] == state].sort_values("date")
        if len(state_df) < 2:
            continue
        plt.plot(state_df["date"], state_df["modal_price"], marker="o", markersize=2, label=state)
    plt.title(f"{crop} - Monthly Modal Price by State (2015-2025)")
    plt.xlabel("Date")
    plt.ylabel("Modal Price (Rs/quintal)")
    plt.legend(fontsize=8)
    plt.tight_layout()
    filename = f"trend_{crop.lower()}.png"
    plt.savefig(filename, dpi=120)
    plt.close()
    print(f"  saved {filename}")

print("\nDone. Check the trend_*.png files in this folder.")