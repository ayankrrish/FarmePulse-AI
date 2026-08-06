"""
FarmPulse AI - Random Forest Baseline Model
Trains one Random Forest per crop (Tur, Moong, Chana), with 'state' as a
categorical feature so a single model learns state-level differences.

Uses a TIME-BASED train/test split (last 12 months held out as test) -
NOT a random split, since shuffling would leak future prices into training
and give artificially good (fake) results.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

INPUT_FILE = "farmpulse_model_ready.csv"
TEST_MONTHS = 12  # holdout period per state-crop series

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])

# Only use rows with full feature history (need lag_12m to exist)
df = df[df["has_full_features"]].copy()

FEATURE_COLS = ["lag_1m", "lag_3m", "lag_6m", "lag_12m",
                "rolling_3m_avg", "rolling_6m_avg", "month", "quarter"]
TARGET_COL = "modal_price"

results = []
trained_models = {}

for crop in df["crop_label"].unique():
    crop_df = df[df["crop_label"] == crop].copy()

    # One-hot encode state so the model learns state-specific patterns
    crop_df = pd.get_dummies(crop_df, columns=["state"], prefix="state")
    state_dummy_cols = [c for c in crop_df.columns if c.startswith("state_")]
    all_feature_cols = FEATURE_COLS + state_dummy_cols

    # Time-based split: for EACH state, hold out the last TEST_MONTHS rows
    crop_df = crop_df.sort_values("date")
    train_frames, test_frames = [], []
    for state_col in state_dummy_cols:
        state_rows = crop_df[crop_df[state_col] == 1].sort_values("date")
        if len(state_rows) <= TEST_MONTHS:
            train_frames.append(state_rows)  # too short to hold out - keep all in train
            continue
        train_frames.append(state_rows.iloc[:-TEST_MONTHS])
        test_frames.append(state_rows.iloc[-TEST_MONTHS:])

    train_df = pd.concat(train_frames)
    test_df = pd.concat(test_frames) if test_frames else pd.DataFrame()

    if test_df.empty:
        print(f"Skipping {crop} - not enough data for a test split.")
        continue

    X_train, y_train = train_df[all_feature_cols], train_df[TARGET_COL]
    X_test, y_test = test_df[all_feature_cols], test_df[TARGET_COL]

    model = RandomForestRegressor(
        n_estimators=200, max_depth=12, random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, preds))
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    results.append({
        "crop": crop,
        "train_rows": len(train_df),
        "test_rows": len(test_df),
        "RMSE": round(rmse, 2),
        "MAE": round(mae, 2),
        "R2": round(r2, 4),
    })

    trained_models[crop] = {
        "model": model,
        "feature_cols": all_feature_cols,
    }

    joblib.dump(trained_models[crop], f"rf_model_{crop.lower()}.joblib")

    print(f"\n{crop}: RMSE={rmse:.2f}  MAE={mae:.2f}  R2={r2:.4f}")
    print(f"  Sample predictions vs actual (first 5 test rows):")
    comparison = pd.DataFrame({
        "actual": y_test.values[:5],
        "predicted": preds[:5]
    })
    print(comparison.to_string(index=False))

print("\n" + "=" * 60)
print("FINAL RESULTS TABLE (baseline Random Forest)")
print("=" * 60)
results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))
results_df.to_csv("rf_baseline_results.csv", index=False)
print("\nSaved results table to rf_baseline_results.csv")
print("Saved trained models as rf_model_<crop>.joblib")