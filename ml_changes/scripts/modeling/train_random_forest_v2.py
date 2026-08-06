"""
FarmPulse AI - Random Forest v2 (simplified, tuned)
Drops state dummy columns (confirmed near-zero importance, pure noise).
Uses shallower trees + higher min_samples_leaf to stop overfitting around
the dominant lag_1m signal. Compares directly against naive baseline
in the same run.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

INPUT_FILE = "../../data/processed/farmpulse_model_ready.csv"
TEST_MONTHS = 12

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])
df = df[df["has_full_features"]].copy()

# Simplified feature set - no state dummies, since they added zero value
FEATURE_COLS = ["lag_1m", "lag_3m", "lag_6m", "lag_12m",
                "rolling_3m_avg", "rolling_6m_avg", "month", "quarter"]
TARGET_COL = "modal_price"

results = []

for crop in df["crop_label"].unique():
    crop_df = df[df["crop_label"] == crop].copy().sort_values("date")

    train_frames, test_frames = [], []
    for state in crop_df["state"].unique():
        state_rows = crop_df[crop_df["state"] == state].sort_values("date")
        if len(state_rows) <= TEST_MONTHS:
            train_frames.append(state_rows)
            continue
        train_frames.append(state_rows.iloc[:-TEST_MONTHS])
        test_frames.append(state_rows.iloc[-TEST_MONTHS:])

    train_df = pd.concat(train_frames)
    test_df = pd.concat(test_frames)

    X_train, y_train = train_df[FEATURE_COLS], train_df[TARGET_COL]
    X_test, y_test = test_df[FEATURE_COLS], test_df[TARGET_COL]

    # Tuned to be much less prone to overfitting around the dominant lag_1m signal:
    # shallower trees, larger leaf size, more trees to average out noise
    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=5,
        min_samples_leaf=10,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, preds))
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    # naive baseline on the same exact test set, for direct comparison
    naive_preds = test_df["lag_1m"]
    naive_rmse = np.sqrt(mean_squared_error(y_test, naive_preds))
    naive_mae = mean_absolute_error(y_test, naive_preds)
    naive_r2 = r2_score(y_test, naive_preds)

    results.append({
        "crop": crop,
        "RF_RMSE": round(rmse, 2), "RF_MAE": round(mae, 2), "RF_R2": round(r2, 4),
        "Naive_RMSE": round(naive_rmse, 2), "Naive_MAE": round(naive_mae, 2), "Naive_R2": round(naive_r2, 4),
        "RF_beats_naive": rmse < naive_rmse,
    })

    joblib.dump({"model": model, "feature_cols": FEATURE_COLS}, f"rf_model_v2_{crop.lower()}.joblib")

results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))
results_df.to_csv("rf_v2_vs_naive_results.csv", index=False)
print("\nSaved to rf_v2_vs_naive_results.csv")