"""
FarmPulse AI - Multi-Horizon Forecast Comparison
Tests RF vs naive baseline at 1, 3, and 6 month forecast horizons.
Hypothesis: naive persistence is strong at 1 month, but should weaken
significantly at longer horizons - which is where ML should show real value,
and which is the horizon that actually matters for farmer selling decisions.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

INPUT_FILE = "../../data/processed/farmpulse_model_ready.csv"
TEST_MONTHS = 12
HORIZONS = [1, 3, 6]

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])
df = df[df["has_full_features"]].copy()

FEATURE_COLS = ["modal_price", "lag_1m", "lag_3m", "lag_6m", "lag_12m",
                "rolling_3m_avg", "rolling_6m_avg", "month", "quarter"]

all_results = []

for horizon in HORIZONS:
    print(f"\n{'='*60}")
    print(f"FORECAST HORIZON: {horizon} month(s) ahead")
    print(f"{'='*60}")

    for crop in df["crop_label"].unique():
        crop_df = df[df["crop_label"] == crop].copy().sort_values("date")

        # Build the target: price 'horizon' months in the future
        horizon_frames = []
        for state, group in crop_df.groupby("state"):
            group = group.sort_values("date").copy()
            group["target"] = group["modal_price"].shift(-horizon)
            group["naive_pred"] = group["modal_price"]  # "future price = current price"
            horizon_frames.append(group)
        crop_df_h = pd.concat(horizon_frames).dropna(subset=["target"])

        train_frames, test_frames = [], []
        for state in crop_df_h["state"].unique():
            state_rows = crop_df_h[crop_df_h["state"] == state].sort_values("date")
            if len(state_rows) <= TEST_MONTHS:
                train_frames.append(state_rows)
                continue
            train_frames.append(state_rows.iloc[:-TEST_MONTHS])
            test_frames.append(state_rows.iloc[-TEST_MONTHS:])

        train_df = pd.concat(train_frames)
        test_df = pd.concat(test_frames)

        X_train, y_train = train_df[FEATURE_COLS], train_df["target"]
        X_test, y_test = test_df[FEATURE_COLS], test_df["target"]

        model = RandomForestRegressor(
            n_estimators=300, max_depth=5, min_samples_leaf=10,
            random_state=42, n_jobs=-1,
        )
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        rmse = np.sqrt(mean_squared_error(y_test, preds))
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)

        naive_preds = test_df["naive_pred"]
        naive_rmse = np.sqrt(mean_squared_error(y_test, naive_preds))
        naive_mae = mean_absolute_error(y_test, naive_preds)
        naive_r2 = r2_score(y_test, naive_preds)

        all_results.append({
            "horizon_months": horizon, "crop": crop,
            "RF_RMSE": round(rmse, 2), "Naive_RMSE": round(naive_rmse, 2),
            "RF_MAE": round(mae, 2), "Naive_MAE": round(naive_mae, 2),
            "RF_R2": round(r2, 4), "Naive_R2": round(naive_r2, 4),
            "RF_beats_naive_RMSE": rmse < naive_rmse,
        })

results_df = pd.DataFrame(all_results)
print("\n\nFULL RESULTS TABLE:")
print(results_df.to_string(index=False))
results_df.to_csv("multi_horizon_results.csv", index=False)
print("\nSaved to multi_horizon_results.csv")