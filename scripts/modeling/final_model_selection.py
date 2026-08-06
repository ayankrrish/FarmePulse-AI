"""
FarmPulse AI - Final Model Selection
Properly separates VALIDATION (used to pick the winning model per crop)
from TEST (used only to report final, honest performance numbers).

Without this separation, picking "LSTM for Tur" by looking directly at
test scores would be a subtle form of overfitting the model-selection
decision itself to that one test window.

Split layout per state-crop series (most recent months last):
  [ ... training ... ] [ 12 months validation ] [ 12 months test ]

Models compared: Naive (persist last value) and LSTM (already trained
and saved from train_lstm.py). Random Forest and ARIMA/SARIMA are
excluded here since they were already clearly and consistently
outperformed by naive/LSTM in every crop in the earlier comparison.
"""

import warnings
warnings.filterwarnings("ignore")

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import tensorflow as tf

INPUT_FILE = "../../data/processed/ceda_cleaned_data.csv"
WINDOW = 12
VAL_MONTHS = 12
TEST_MONTHS = 12

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])
df = df.dropna(subset=["modal_price"])


def evaluate_naive(series, holdout_months):
    """Naive = predict this month's price as the actual for holdout_months ago's target."""
    actual = series[-holdout_months:]
    pred = series[-(holdout_months + 1):-1]  # shifted by 1 = "persist last value"
    return actual, pred


def evaluate_lstm(model, series, scaler_train_portion, holdout_months):
    """Evaluate a pre-trained LSTM on a given holdout window."""
    scaler = MinMaxScaler()
    scaler.fit(scaler_train_portion.reshape(-1, 1))

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


selection_results = {}

for crop in df["crop_label"].unique():
    crop_df = df[df["crop_label"] == crop]

    lstm_path = f"../../models/lstm_model_{crop.lower()}.keras"
    lstm_model = tf.keras.models.load_model(lstm_path) if os.path.exists(lstm_path) else None

    val_naive_actual, val_naive_pred = [], []
    val_lstm_actual, val_lstm_pred = [], []
    test_naive_actual, test_naive_pred = [], []
    test_lstm_actual, test_lstm_pred = [], []

    for state in crop_df["state"].unique():
        series = crop_df[crop_df["state"] == state].sort_values("date")["modal_price"].values
        if len(series) <= WINDOW + VAL_MONTHS + TEST_MONTHS + 12:
            continue

        # Series WITHOUT the final test window (used for validation-time evaluation)
        series_for_val = series[:-TEST_MONTHS]
        train_for_val_scaler = series_for_val[:-VAL_MONTHS]  # scaler fit only on this

        # --- Validation window evaluation ---
        a, p = evaluate_naive(series_for_val, VAL_MONTHS)
        val_naive_actual.extend(a); val_naive_pred.extend(p)

        if lstm_model is not None:
            a, p = evaluate_lstm(lstm_model, series_for_val, train_for_val_scaler, VAL_MONTHS)
            val_lstm_actual.extend(a); val_lstm_pred.extend(p)

        # --- Test window evaluation (full series, true final holdout) ---
        train_for_test_scaler = series[:-TEST_MONTHS]
        a, p = evaluate_naive(series, TEST_MONTHS)
        test_naive_actual.extend(a); test_naive_pred.extend(p)

        if lstm_model is not None:
            a, p = evaluate_lstm(lstm_model, series, train_for_test_scaler, TEST_MONTHS)
            test_lstm_actual.extend(a); test_lstm_pred.extend(p)

    val_naive_rmse = np.sqrt(mean_squared_error(val_naive_actual, val_naive_pred))
    val_lstm_rmse = (np.sqrt(mean_squared_error(val_lstm_actual, val_lstm_pred))
                      if val_lstm_actual else np.inf)

    winner = "LSTM" if val_lstm_rmse < val_naive_rmse else "Naive"

    test_naive_rmse = np.sqrt(mean_squared_error(test_naive_actual, test_naive_pred))
    test_naive_r2 = r2_score(test_naive_actual, test_naive_pred)
    test_lstm_rmse = (np.sqrt(mean_squared_error(test_lstm_actual, test_lstm_pred))
                       if test_lstm_actual else np.inf)
    test_lstm_r2 = r2_score(test_lstm_actual, test_lstm_pred) if test_lstm_actual else None

    final_rmse = test_lstm_rmse if winner == "LSTM" else test_naive_rmse
    final_r2 = test_lstm_r2 if winner == "LSTM" else test_naive_r2

    selection_results[crop] = {
        "validation_naive_rmse": round(val_naive_rmse, 2),
        "validation_lstm_rmse": round(val_lstm_rmse, 2) if val_lstm_rmse != np.inf else None,
        "chosen_model": winner,
        "final_test_rmse": round(final_rmse, 2),
        "final_test_r2": round(final_r2, 4),
    }

    print(f"\n{crop}:")
    print(f"  Validation RMSE - Naive: {val_naive_rmse:.2f}  LSTM: {val_lstm_rmse:.2f}")
    print(f"  Chosen model: {winner}")
    print(f"  Final test performance: RMSE={final_rmse:.2f}  R2={final_r2:.4f}")

with open("../../results/model_selection.json", "w") as f:
    json.dump(selection_results, f, indent=2)

print("\n" + "=" * 60)
print("FINAL MODEL SELECTION (honest - chosen on validation, reported on test)")
print("=" * 60)
print(pd.DataFrame(selection_results).T.to_string())
print("\nSaved to results/model_selection.json")