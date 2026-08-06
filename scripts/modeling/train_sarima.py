"""
FarmPulse AI - ARIMA v2 (auto order search + seasonality)
Fixes two problems with the v1 ARIMA baseline:
  1. Searches a small grid of (p,d,q) combinations per series, picks the
     best by AIC instead of guessing one fixed order.
  2. Adds a seasonal component (SARIMA) with a 12-month seasonal period,
     since pulse prices show clear yearly harvest-cycle seasonality
     (visible in the trend plots).
Also explicitly sets monthly frequency on the date index to remove the
"no frequency information" warnings AND ensure forecasts align correctly.
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import itertools
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

INPUT_FILE = "../../data/processed/ceda_cleaned_data.csv"
TEST_MONTHS = 12

# Small grid to search - keeps runtime reasonable while covering common orders
P_VALUES = [0, 1, 2]
D_VALUES = [1]
Q_VALUES = [0, 1, 2]
SEASONAL_ORDER = (1, 1, 1, 12)  # yearly seasonality, monthly data

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])
df = df.dropna(subset=["modal_price"])

results_by_crop = {}


def find_best_order(train_series):
    """Grid search (p,d,q) by AIC on the training data only."""
    best_aic = np.inf
    best_order = (1, 1, 1)
    for p, d, q in itertools.product(P_VALUES, D_VALUES, Q_VALUES):
        try:
            model = SARIMAX(train_series, order=(p, d, q),
                             seasonal_order=SEASONAL_ORDER,
                             enforce_stationarity=False, enforce_invertibility=False)
            fitted = model.fit(disp=False)
            if fitted.aic < best_aic:
                best_aic = fitted.aic
                best_order = (p, d, q)
        except Exception:
            continue
    return best_order


for crop in df["crop_label"].unique():
    crop_df = df[df["crop_label"] == crop]
    all_actual, all_pred = [], []
    per_state_results = []

    for state in crop_df["state"].unique():
        series = crop_df[crop_df["state"] == state].sort_values("date")
        series = series.set_index("date")["modal_price"]
        try:
            series.index = pd.DatetimeIndex(series.index, freq="MS")
        except ValueError:
            print(f"  {crop} - {state}: date gaps break continuous monthly index, skipping "
                  f"(this is a known limitation - see gap_report.csv)")
            continue

        if len(series) <= TEST_MONTHS + 24:  # need 2+ years for seasonal model to make sense
            print(f"  {crop} - {state}: too short for seasonal model, skipping")
            continue

        train = series.iloc[:-TEST_MONTHS]
        test = series.iloc[-TEST_MONTHS:]

        try:
            best_order = find_best_order(train)
            model = SARIMAX(train, order=best_order, seasonal_order=SEASONAL_ORDER,
                             enforce_stationarity=False, enforce_invertibility=False)
            fitted = model.fit(disp=False)
            forecast = fitted.forecast(steps=TEST_MONTHS)
        except Exception as e:
            print(f"  {crop} - {state}: SARIMA failed ({e}), skipping")
            continue

        all_actual.extend(test.values)
        all_pred.extend(forecast.values)

        state_rmse = np.sqrt(mean_squared_error(test.values, forecast.values))
        per_state_results.append((state, state_rmse, best_order))

    if not all_actual:
        print(f"{crop}: no valid SARIMA fits, skipping")
        continue

    rmse = np.sqrt(mean_squared_error(all_actual, all_pred))
    mae = mean_absolute_error(all_actual, all_pred)
    r2 = r2_score(all_actual, all_pred)

    results_by_crop[crop] = {"RMSE": rmse, "MAE": mae, "R2": r2}

    print(f"\n{crop} (SARIMA with seasonal 12): RMSE={rmse:.2f}  MAE={mae:.2f}  R2={r2:.4f}")
    print("  Per-state RMSE and chosen (p,d,q):")
    for state, s_rmse, order in sorted(per_state_results, key=lambda x: x[1]):
        print(f"    {state}: RMSE={s_rmse:.2f}  order={order}")

print("\n" + "=" * 60)
print("SARIMA SUMMARY (compare to results/arima_results.csv and rf_v2_vs_naive_results.csv)")
print("=" * 60)
summary_df = pd.DataFrame(results_by_crop).T
summary_df.columns = ["SARIMA_RMSE", "SARIMA_MAE", "SARIMA_R2"]
print(summary_df.round(2).to_string())
summary_df.to_csv("../../results/sarima_results.csv")
print("\nSaved to results/sarima_results.csv")