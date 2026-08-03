"""
FarmPulse AI — XGBoost Model
Uses the exact same feature set, train/test split, and evaluation
methodology as train_random_forest_v2.py for direct comparison.
XGBoost adds gradient boosting with early stopping for better
generalization on the lag-dominated feature space.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

try:
    from xgboost import XGBRegressor
except ImportError:
    print("ERROR: xgboost not installed. Run: pip install xgboost")
    raise

# --------------- Paths (pathlib-based) ---------------
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = DATA_DIR / "farmpulse_model_ready.csv"
if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {INPUT_FILE}")

TEST_MONTHS = 12

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])
df = df[df["has_full_features"]].copy()

# Same feature set as RF v2 — for fair comparison
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

    model = XGBRegressor(
        n_estimators=500,
        max_depth=4,
        learning_rate=0.05,
        min_child_weight=10,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        early_stopping_rounds=20,
        eval_metric="rmse",
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    preds = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, preds))
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    # Naive baseline for comparison
    naive_preds = test_df["lag_1m"]
    naive_rmse = np.sqrt(mean_squared_error(y_test, naive_preds))

    results.append({
        "crop": crop,
        "XGB_RMSE": round(rmse, 2),
        "XGB_MAE": round(mae, 2),
        "XGB_R2": round(r2, 4),
        "Naive_RMSE": round(naive_rmse, 2),
        "XGB_beats_naive": rmse < naive_rmse,
        "best_iteration": model.best_iteration if hasattr(model, 'best_iteration') else None,
    })

    print(f"{crop} (XGBoost): RMSE={rmse:.2f}  MAE={mae:.2f}  R2={r2:.4f}  "
          f"(Naive RMSE={naive_rmse:.2f}, beats={rmse < naive_rmse})")

    # Save model
    joblib.dump(
        {"model": model, "feature_cols": FEATURE_COLS},
        str(MODELS_DIR / f"xgb_model_{crop.lower()}.joblib"),
    )

print("\n" + "=" * 60)
print("XGBOOST SUMMARY")
print("=" * 60)
results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))
results_df.to_csv(str(RESULTS_DIR / "xgboost_results.csv"), index=False)
print("\nSaved models to models/xgb_model_*.joblib")
print("Saved results to results/xgboost_results.csv")
