"""
Naive baseline comparison: "predict last month's price" (lag_1m) vs
the trained Random Forest. If RF doesn't clearly beat this, the model
isn't actually learning anything useful beyond persistence.
"""

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

INPUT_FILE = "../../data/processed/farmpulse_model_ready.csv"
TEST_MONTHS = 12

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])
df = df[df["has_full_features"]].copy()

results = []

for crop in df["crop_label"].unique():
    crop_df = df[df["crop_label"] == crop].copy()
    crop_df = crop_df.sort_values("date")

    test_frames = []
    for state in crop_df["state"].unique():
        state_rows = crop_df[crop_df["state"] == state].sort_values("date")
        if len(state_rows) <= TEST_MONTHS:
            continue
        test_frames.append(state_rows.iloc[-TEST_MONTHS:])

    test_df = pd.concat(test_frames)

    actual = test_df["modal_price"]
    naive_pred = test_df["lag_1m"]  # "predict last month's price"

    rmse = np.sqrt(mean_squared_error(actual, naive_pred))
    mae = mean_absolute_error(actual, naive_pred)
    r2 = r2_score(actual, naive_pred)

    results.append({"crop": crop, "RMSE": round(rmse, 2), "MAE": round(mae, 2), "R2": round(r2, 4)})

print("NAIVE BASELINE (predict last month's price) - same test set as Random Forest:")
print(pd.DataFrame(results).to_string(index=False))
print("\nCompare this table to rf_baseline_results.csv - Random Forest should have")
print("LOWER RMSE/MAE and HIGHER R2 than this naive baseline. If not, the model")
print("isn't actually adding value over simple persistence.")