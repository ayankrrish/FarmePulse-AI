"""
FarmPulse AI - Feature Engineering
Builds model-ready features per state-crop time series:
  - Lag features (previous 1, 3, 6, 12 months)
  - Rolling averages (3-month, 6-month)
  - Seasonality indicators (month number, quarter)
  - Year-over-year % change
  - Price momentum and volatility
  - Trend direction indicator
  - Finer date features (week, day of year)
  - Harvest season flag
  - Normalized price (min-max per series)
  - Outlier flag (IQR-based)
Drops rows with unresolved NaN gaps first (can't honestly interpolate those).
"""

import numpy as np
import pandas as pd

INPUT_FILE = "../../data/processed/ceda_cleaned_data.csv"
OUTPUT_FILE = "../../data/processed/farmpulse_model_ready.csv"

# Crop-specific harvest months (used for seasonality feature)
HARVEST_MONTHS = {
    "Chana": [3, 4],       # Rabi: harvested Mar-Apr
    "Moong": [9, 10],      # Kharif: harvested Sep-Oct
    "Tur": [1, 2, 3],      # Kharif (late): harvested Jan-Mar
}

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])

# Drop rows with unresolved large gaps (still NaN after cleaning step)
before = len(df)
df = df.dropna(subset=["modal_price"])
print(f"Dropped {before - len(df)} rows with unresolved gaps (kept {len(df)}).")

df = df.sort_values(["state", "crop_label", "date"])

feature_frames = []

for (state, crop), group in df.groupby(["state", "crop_label"]):
    group = group.sort_values("date").copy()

    # ---- Existing features (unchanged) ----

    # Lag features - previous known prices at different horizons
    for lag in [1, 3, 6, 12]:
        group[f"lag_{lag}m"] = group["modal_price"].shift(lag)

    # Rolling averages (based on past values only, no lookahead)
    group["rolling_3m_avg"] = group["modal_price"].shift(1).rolling(window=3).mean()
    group["rolling_6m_avg"] = group["modal_price"].shift(1).rolling(window=6).mean()

    # Seasonality indicators
    group["month"] = group["date"].dt.month
    group["quarter"] = group["date"].dt.quarter

    # Year-over-year percent change (vs 12 months ago)
    group["yoy_pct_change"] = (
        (group["modal_price"] - group["lag_12m"]) / group["lag_12m"] * 100
    )

    # ---- New features (appended — Phase I report requirements) ----

    # Finer-grained date features
    group["week_of_year"] = group["date"].dt.isocalendar().week.astype(int)
    group["day_of_year"] = group["date"].dt.dayofyear
    group["year"] = group["date"].dt.year

    # Price momentum: rate of change over 3 months (no lookahead)
    group["price_momentum"] = group["modal_price"].pct_change(periods=3) * 100

    # Price volatility: rolling 6-month std of past prices
    group["price_volatility"] = (
        group["modal_price"].shift(1).rolling(window=6).std()
    )

    # Trend direction: +1 rising, -1 falling, 0 stable (based on 3-month slope)
    rolling_diff = group["modal_price"].diff().rolling(window=3).mean()
    group["trend_direction"] = np.where(
        rolling_diff > 0, 1, np.where(rolling_diff < 0, -1, 0)
    )

    # Harvest season flag (crop-specific)
    harvest = HARVEST_MONTHS.get(crop, [])
    group["is_harvest_season"] = group["month"].isin(harvest).astype(int)

    # Normalized price (min-max within this state-crop series)
    p_min = group["modal_price"].min()
    p_max = group["modal_price"].max()
    if p_max > p_min:
        group["price_normalized"] = (
            (group["modal_price"] - p_min) / (p_max - p_min)
        )
    else:
        group["price_normalized"] = 0.5

    # Outlier flag (IQR-based — flags, does NOT remove data)
    q1 = group["modal_price"].quantile(0.25)
    q3 = group["modal_price"].quantile(0.75)
    iqr = q3 - q1
    group["is_outlier"] = (
        (group["modal_price"] < (q1 - 1.5 * iqr)) |
        (group["modal_price"] > (q3 + 1.5 * iqr))
    ).astype(int)

    feature_frames.append(group)

featured_df = pd.concat(feature_frames, ignore_index=True)

# Rows missing lag_12m (first year of each series) can't have full features -
# keep them for shorter-horizon models but flag via a completeness column
featured_df["has_full_features"] = featured_df["lag_12m"].notna()

featured_df.to_csv(OUTPUT_FILE, index=False)

print(f"\nSaved model-ready dataset to {OUTPUT_FILE}")
print(f"Total rows: {len(featured_df)}")
print(f"Rows with full 12-month lag history: {featured_df['has_full_features'].sum()}")
print(f"\nColumns: {list(featured_df.columns)}")
print("\nSample:")
print(featured_df[featured_df["has_full_features"]].head(3).to_string(index=False))