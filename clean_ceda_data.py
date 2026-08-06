"""
FarmPulse AI - Data Cleaning Pass
For each state-crop combination:
  1. Builds the FULL expected monthly date range (from that series' own start to end)
  2. Identifies missing months
  3. Fills small gaps (<= 2 consecutive missing months) via linear interpolation
  4. Leaves larger gaps as NaN and flags them - these should NOT be interpolated
     blindly, since a 6+ month gap likely means a real reporting break, not a
     smooth price transition
  5. Outputs a cleaned file + a gap report you can put directly in your report's
     "data limitations" section
"""

import pandas as pd

INPUT_FILE = "ceda_historical_data.csv"
OUTPUT_FILE = "ceda_cleaned_data.csv"
GAP_REPORT_FILE = "gap_report.csv"

MAX_GAP_TO_INTERPOLATE = 2  # months

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])

cleaned_frames = []
gap_report_rows = []

for (state, crop), group in df.groupby(["state", "crop_label"]):
    group = group.sort_values("date").set_index("date")

    # Build the full expected monthly range for this series
    full_range = pd.date_range(group.index.min(), group.index.max(), freq="MS")
    reindexed = group.reindex(full_range)

    total_expected = len(full_range)
    total_missing = reindexed["modal_price"].isna().sum()

    # Find gap lengths (consecutive missing runs)
    is_missing = reindexed["modal_price"].isna()
    gap_lengths = []
    current_gap = 0
    for val in is_missing:
        if val:
            current_gap += 1
        else:
            if current_gap > 0:
                gap_lengths.append(current_gap)
            current_gap = 0
    if current_gap > 0:
        gap_lengths.append(current_gap)

    max_gap = max(gap_lengths) if gap_lengths else 0

    # Interpolate only small gaps; leave large gaps as NaN (real reporting breaks)
    for col in ["min_price", "max_price", "modal_price"]:
        reindexed[col] = reindexed[col].interpolate(
            method="linear", limit=MAX_GAP_TO_INTERPOLATE, limit_area="inside"
        )

    reindexed["state"] = state
    reindexed["crop_label"] = crop
    reindexed = reindexed.reset_index().rename(columns={"index": "date"})

    cleaned_frames.append(reindexed)

    gap_report_rows.append({
        "state": state,
        "crop_label": crop,
        "expected_months": total_expected,
        "missing_months": total_missing,
        "largest_gap_months": max_gap,
        "pct_missing": round(100 * total_missing / total_expected, 1),
    })

cleaned_df = pd.concat(cleaned_frames, ignore_index=True)
gap_report = pd.DataFrame(gap_report_rows).sort_values("pct_missing", ascending=False)

# Drop rows still NaN (large gaps we deliberately didn't interpolate)
still_missing = cleaned_df["modal_price"].isna().sum()
final_df = cleaned_df.dropna(subset=["modal_price"])

cleaned_df.to_csv(OUTPUT_FILE, index=False)
gap_report.to_csv(GAP_REPORT_FILE, index=False)

print("=" * 60)
print("CLEANING SUMMARY")
print("=" * 60)
print(f"Total rows before: {len(df)}")
print(f"Total rows after reindexing to full monthly grid: {len(cleaned_df)}")
print(f"Rows still missing after interpolation (large gaps, left as-is): {still_missing}")
print(f"\nSaved cleaned data (includes NaN for large gaps) to: {OUTPUT_FILE}")
print(f"Saved gap report to: {GAP_REPORT_FILE}")

print("\n" + "=" * 60)
print("GAP REPORT (worst first) - put this in your report's limitations section")
print("=" * 60)
print(gap_report.to_string(index=False))