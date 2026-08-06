"""
FarmPulse AI — Prophet Model
Facebook Prophet for each crop-state time series.
Prophet handles seasonality and trends natively, making it well-suited
for monthly agricultural price data with yearly harvest cycles.

Uses the same 12-month holdout methodology as all other models.
Prophet models are lightweight and fast to refit, so we don't persist
model files — they're retrained on demand when needed for forecasting.
Results are saved for comparison with other models.
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

try:
    from prophet import Prophet
except ImportError:
    print("ERROR: prophet not installed. Run: pip install prophet")
    raise

# --------------- Paths (pathlib-based) ---------------
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed"
RESULTS_DIR = BASE_DIR / "results"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = DATA_DIR / "ceda_cleaned_data.csv"
if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {INPUT_FILE}")

TEST_MONTHS = 12

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])
df = df.dropna(subset=["modal_price"])

results_by_crop = {}

for crop in df["crop_label"].unique():
    crop_df = df[df["crop_label"] == crop]
    all_actual, all_pred = [], []
    per_state_results = []

    for state in crop_df["state"].unique():
        series = crop_df[crop_df["state"] == state].sort_values("date")
        series = series[["date", "modal_price"]].copy()
        series.columns = ["ds", "y"]  # Prophet's required column names

        if len(series) <= TEST_MONTHS + 24:
            print(f"  {crop} - {state}: too short for Prophet, skipping")
            continue

        train = series.iloc[:-TEST_MONTHS]
        test = series.iloc[-TEST_MONTHS:]

        try:
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=False,   # monthly data, no weekly pattern
                daily_seasonality=False,
                seasonality_mode="multiplicative",
                changepoint_prior_scale=0.05,  # conservative — less overfitting
            )
            model.fit(train)

            # Make future dataframe covering the test period
            future = model.make_future_dataframe(periods=TEST_MONTHS, freq="MS")
            forecast = model.predict(future)

            # Extract predictions for the test period only
            pred_values = forecast.iloc[-TEST_MONTHS:]["yhat"].values
            actual_values = test["y"].values

            all_actual.extend(actual_values)
            all_pred.extend(pred_values)

            state_rmse = np.sqrt(mean_squared_error(actual_values, pred_values))
            per_state_results.append((state, state_rmse))

        except Exception as e:
            print(f"  {crop} - {state}: Prophet failed ({e}), skipping")
            continue

    if not all_actual:
        print(f"{crop}: no valid Prophet fits, skipping")
        continue

    rmse = np.sqrt(mean_squared_error(all_actual, all_pred))
    mae = mean_absolute_error(all_actual, all_pred)
    r2 = r2_score(all_actual, all_pred)

    results_by_crop[crop] = {"RMSE": rmse, "MAE": mae, "R2": r2}

    print(f"\n{crop} (Prophet): RMSE={rmse:.2f}  MAE={mae:.2f}  R2={r2:.4f}")
    print("  Per-state RMSE:")
    for state, s_rmse in sorted(per_state_results, key=lambda x: x[1]):
        print(f"    {state}: {s_rmse:.2f}")

print("\n" + "=" * 60)
print("PROPHET SUMMARY")
print("=" * 60)
summary_df = pd.DataFrame(results_by_crop).T
summary_df.columns = ["Prophet_RMSE", "Prophet_MAE", "Prophet_R2"]
print(summary_df.round(2).to_string())
summary_df.to_csv(str(RESULTS_DIR / "prophet_results.csv"))
print("\nSaved to results/prophet_results.csv")
