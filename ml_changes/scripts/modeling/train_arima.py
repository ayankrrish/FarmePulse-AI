"""
FarmPulse AI - ARIMA Baseline Model
Fits one ARIMA(1,1,1) model per state-crop time series (not one model for
all states like Random Forest - ARIMA works on a single series at a time).
Uses the same 12-month holdout test methodology as the RF/naive comparison,
so results are directly comparable across all three approaches.
"""

import warnings
warnings.filterwarnings("ignore")  # statsmodels is noisy about convergence warnings

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

INPUT_FILE = "../../data/processed/ceda_cleaned_data.csv"
TEST_MONTHS = 12
ARIMA_ORDER = (1, 1, 1)  # (p, d, q) - simple starting point

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])
df = df.dropna(subset=["modal_price"])

results_by_crop = {}  # crop -> list of (actual, predicted) across all states

for crop in df["crop_label"].unique():
    crop_df = df[df["crop_label"] == crop]
    all_actual, all_pred = [], []
    per_state_results = []

    for state in crop_df["state"].unique():
        series = crop_df[crop_df["state"] == state].sort_values("date")
        series = series.set_index("date")["modal_price"]

        if len(series) <= TEST_MONTHS + 10:  # need reasonable history to fit ARIMA
            continue

        train = series.iloc[:-TEST_MONTHS]
        test = series.iloc[-TEST_MONTHS:]

        try:
            model = ARIMA(train, order=ARIMA_ORDER)
            fitted = model.fit()
            forecast = fitted.forecast(steps=TEST_MONTHS)
        except Exception as e:
            print(f"  {crop} - {state}: ARIMA failed ({e}), skipping")
            continue

        all_actual.extend(test.values)
        all_pred.extend(forecast.values)

        state_rmse = np.sqrt(mean_squared_error(test.values, forecast.values))
        per_state_results.append((state, state_rmse))

    if not all_actual:
        print(f"{crop}: no valid ARIMA fits, skipping")
        continue

    rmse = np.sqrt(mean_squared_error(all_actual, all_pred))
    mae = mean_absolute_error(all_actual, all_pred)
    r2 = r2_score(all_actual, all_pred)

    results_by_crop[crop] = {"RMSE": rmse, "MAE": mae, "R2": r2}

    print(f"\n{crop} (ARIMA{ARIMA_ORDER}): RMSE={rmse:.2f}  MAE={mae:.2f}  R2={r2:.4f}")
    print("  Per-state RMSE:")
    for state, s_rmse in sorted(per_state_results, key=lambda x: x[1]):
        print(f"    {state}: {s_rmse:.2f}")

print("\n" + "=" * 60)
print("ARIMA SUMMARY (compare to rf_v2_vs_naive_results.csv)")
print("=" * 60)
summary_df = pd.DataFrame(results_by_crop).T
summary_df.columns = ["ARIMA_RMSE", "ARIMA_MAE", "ARIMA_R2"]
print(summary_df.round(2).to_string())
summary_df.to_csv("../../results/arima_results.csv")
print("\nSaved to results/arima_results.csv")