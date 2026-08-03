"""
FarmPulse AI - Model Selection v2
Two improvements over the first version:
  1. Selection happens per (state, crop) pair, not pooled per crop -
     some states may genuinely benefit from LSTM even where the
     crop-wide average favors naive persistence.
  2. Adds "trend-adjusted naive" (Holt-style drift) as a third
     candidate: next_price = last_price + average_recent_trend,
     instead of assuming price is perfectly flat.
Selection is made on the VALIDATION window; final numbers are reported
on the untouched TEST window, same honest methodology as before.
"""

import warnings
warnings.filterwarnings("ignore")

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
import tensorflow as tf

INPUT_FILE = "../../data/processed/ceda_cleaned_data.csv"
WINDOW = 12
VAL_MONTHS = 12
TEST_MONTHS = 12
TREND_LOOKBACK = 3  # months used to estimate recent drift

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])
df = df.dropna(subset=["modal_price"])


def predict_naive_flat(series, holdout_months):
    actual = series[-holdout_months:]
    pred = series[-(holdout_months + 1):-1]
    return actual, pred


def predict_naive_trend(series, holdout_months, lookback=TREND_LOOKBACK):
    """next = last_known_price + average change over the last `lookback` months."""
    actual = series[-holdout_months:]
    preds = []
    for i in range(len(series) - holdout_months, len(series)):
        history = series[:i]
        last_price = history[-1]
        recent_diffs = np.diff(history[-(lookback + 1):])
        drift = recent_diffs.mean() if len(recent_diffs) > 0 else 0
        preds.append(last_price + drift)
    return actual, np.array(preds)


def predict_lstm(model, series, scaler_fit_portion, holdout_months):
    scaler = MinMaxScaler()
    scaler.fit(scaler_fit_portion.reshape(-1, 1))
    holdout_with_lookback = series[-(holdout_months + WINDOW):]
    scaled = scaler.transform(holdout_with_lookback.reshape(-1, 1)).flatten()

    X, y = [], []
    for i in range(len(scaled) - WINDOW):
        X.append(scaled[i:i + WINDOW])
        y.append(scaled[i + WINDOW])
    X = np.array(X).reshape(-1, WINDOW, 1)
    y = np.array(y)

    pred_scaled = model.predict(X, verbose=0).flatten()
    pred = scaler.inverse_transform(pred_scaled.reshape(-1, 1)).flatten()
    actual = scaler.inverse_transform(y.reshape(-1, 1)).flatten()
    return actual, pred


final_selections = {}

for crop in df["crop_label"].unique():
    crop_df = df[df["crop_label"] == crop]

    lstm_path = f"../../models/lstm_model_{crop.lower()}.keras"
    lstm_model = tf.keras.models.load_model(lstm_path) if os.path.exists(lstm_path) else None

    final_selections[crop] = {}

    for state in crop_df["state"].unique():
        series = crop_df[crop_df["state"] == state].sort_values("date")["modal_price"].values
        if len(series) <= WINDOW + VAL_MONTHS + TEST_MONTHS + 12:
            continue

        series_for_val = series[:-TEST_MONTHS]
        train_for_val_scaler = series_for_val[:-VAL_MONTHS]

        # --- Validation: compare all 3 candidates ---
        candidates = {}

        a, p = predict_naive_flat(series_for_val, VAL_MONTHS)
        candidates["Naive_flat"] = np.sqrt(mean_squared_error(a, p))

        a, p = predict_naive_trend(series_for_val, VAL_MONTHS)
        candidates["Naive_trend"] = np.sqrt(mean_squared_error(a, p))

        if lstm_model is not None:
            a, p = predict_lstm(lstm_model, series_for_val, train_for_val_scaler, VAL_MONTHS)
            candidates["LSTM"] = np.sqrt(mean_squared_error(a, p))

        winner = min(candidates, key=candidates.get)

        # --- Test: report final honest performance of the WINNER only ---
        train_for_test_scaler = series[:-TEST_MONTHS]
        if winner == "Naive_flat":
            a, p = predict_naive_flat(series, TEST_MONTHS)
        elif winner == "Naive_trend":
            a, p = predict_naive_trend(series, TEST_MONTHS)
        else:
            a, p = predict_lstm(lstm_model, series, train_for_test_scaler, TEST_MONTHS)

        test_rmse = np.sqrt(mean_squared_error(a, p))
        test_r2 = r2_score(a, p)

        final_selections[crop][state] = {
            "validation_scores": {k: round(v, 2) for k, v in candidates.items()},
            "chosen_model": winner,
            "test_rmse": round(test_rmse, 2),
            "test_r2": round(test_r2, 4),
        }

        print(f"{crop} - {state}: chosen={winner}  test_RMSE={test_rmse:.2f}  test_R2={test_r2:.4f}")

with open("../../results/model_selection_per_state.json", "w") as f:
    json.dump(final_selections, f, indent=2)

print("\nSaved to results/model_selection_per_state.json")

print("\n" + "=" * 60)
print("SUMMARY: how often each model won, per crop")
print("=" * 60)
for crop, states in final_selections.items():
    winners = [v["chosen_model"] for v in states.values()]
    counts = pd.Series(winners).value_counts()
    print(f"\n{crop}:")
    print(counts.to_string())