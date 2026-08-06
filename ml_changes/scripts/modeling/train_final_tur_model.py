"""
FarmPulse AI - Final Tur Model (Production)
Trains the winning approach for Tur specifically: Random Forest with
arrival quantity features included. This beat every other approach
tried for Tur (R2=0.85 vs naive's 0.77).
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib

PRICE_FILE = "../../data/processed/ceda_cleaned_data.csv"
QTY_FILE = "../../data/raw/ceda_quantities_data.csv"

price_df = pd.read_csv(PRICE_FILE, parse_dates=["date"])
price_df = price_df.dropna(subset=["modal_price"])
qty_df = pd.read_csv(QTY_FILE, parse_dates=["date"])

merged = pd.merge(price_df, qty_df, on=["state", "crop_label", "date"], how="left")
tur_df = merged[merged["crop_label"] == "Tur"].copy()

feature_frames = []
for state, group in tur_df.groupby("state"):
    group = group.sort_values("date").copy()
    group["lag_1m"] = group["modal_price"].shift(1)
    group["lag_3m"] = group["modal_price"].shift(3)
    group["lag_12m"] = group["modal_price"].shift(12)
    group["rolling_3m_avg"] = group["modal_price"].shift(1).rolling(3).mean()
    group["month"] = group["date"].dt.month
    group["quarter"] = group["date"].dt.quarter
    group["qty_lag_1m"] = group["arrival_qty"].shift(1)
    group["qty_rolling_3m"] = group["arrival_qty"].shift(1).rolling(3).mean()
    feature_frames.append(group)

tur_full = pd.concat(feature_frames, ignore_index=True)

FEATURE_COLS = ["lag_1m", "lag_3m", "lag_12m", "rolling_3m_avg", "month", "quarter",
                "qty_lag_1m", "qty_rolling_3m"]

clean_df = tur_full.dropna(subset=FEATURE_COLS + ["modal_price"])

# Train on ALL available data (this is now the final production model,
# not a held-out test - test evaluation already happened in the A/B test)
X = clean_df[FEATURE_COLS]
y = clean_df["modal_price"]

model = RandomForestRegressor(n_estimators=300, max_depth=5, min_samples_leaf=10,
                               random_state=42, n_jobs=-1)
model.fit(X, y)

joblib.dump({"model": model, "feature_cols": FEATURE_COLS}, "../../models/tur_final_model.joblib")

print(f"Trained final Tur model on {len(clean_df)} rows.")
print(f"Features used: {FEATURE_COLS}")
print("Saved to models/tur_final_model.joblib")

# Also save the most recent known values per state, needed at prediction
# time to build the feature row for a new forecast
latest_per_state = tur_full.sort_values("date").groupby("state").tail(4)
latest_per_state.to_csv("../../data/processed/tur_latest_context.csv", index=False)
print("Saved recent context data to data/processed/tur_latest_context.csv")