"""
FarmPulse AI - LSTM Model
Trains one LSTM per crop, pooling sequences from all 8 states together
(shared weights across states, like the Random Forest approach) so the
model can learn general price dynamics while still seeing state-specific
patterns through separately-normalized sequences.

Key design choices:
  - Each state's price series is normalized independently (MinMax fit on
    that state's TRAINING portion only) - this matters because Chana in
    Gujarat and Chana in Telangana can be on very different price scales,
    and pooling raw prices together would let high-price states dominate.
  - WINDOW=12 months of history -> predict the next month's price.
  - Same 12-month time-based holdout per state as all other models, so
    results are directly comparable to naive/RF/ARIMA/SARIMA.
"""

import warnings
warnings.filterwarnings("ignore")

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["OMP_NUM_THREADS"] = "1"

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

import tensorflow as tf
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.threading.set_inter_op_parallelism_threads(1)

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

tf.random.set_seed(42)
np.random.seed(42)

INPUT_FILE = "../../data/processed/ceda_cleaned_data.csv"
TEST_MONTHS = 12
WINDOW = 12  # months of history used to predict the next month

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])
df = df.dropna(subset=["modal_price"])

results_by_crop = {}


def make_sequences(prices, window):
    """Turn a 1D price array into (X, y) sliding-window sequences."""
    X, y = [], []
    for i in range(len(prices) - window):
        X.append(prices[i:i + window])
        y.append(prices[i + window])
    return np.array(X), np.array(y)


for crop in df["crop_label"].unique():
    crop_df = df[df["crop_label"] == crop]

    X_train_all, y_train_all = [], []
    test_sequences = []  # (state, X_test, y_test_actual, scaler)

    for state in crop_df["state"].unique():
        series = crop_df[crop_df["state"] == state].sort_values("date")["modal_price"].values

        if len(series) <= WINDOW + TEST_MONTHS + 12:
            continue  # not enough history for meaningful sequences

        train_prices = series[:-TEST_MONTHS]
        test_prices = series[-(TEST_MONTHS + WINDOW):]  # need WINDOW months before test starts

        # Scale using ONLY training data statistics - test data must never
        # influence the scaler, or we'd be leaking future information
        scaler = MinMaxScaler()
        train_scaled = scaler.fit_transform(train_prices.reshape(-1, 1)).flatten()
        test_scaled = scaler.transform(test_prices.reshape(-1, 1)).flatten()

        X_tr, y_tr = make_sequences(train_scaled, WINDOW)
        if len(X_tr) == 0:
            continue

        X_train_all.append(X_tr)
        y_train_all.append(y_tr)

        X_te, y_te_scaled = make_sequences(test_scaled, WINDOW)
        if len(X_te) == 0:
            continue

        test_sequences.append((state, X_te, y_te_scaled, scaler))

    if not X_train_all:
        print(f"{crop}: not enough data for LSTM, skipping")
        continue

    X_train = np.concatenate(X_train_all).reshape(-1, WINDOW, 1)
    y_train = np.concatenate(y_train_all)

    print(f"\nTraining LSTM for {crop}: {len(X_train)} training sequences pooled from all states...")

    model = Sequential([
        LSTM(32, activation="tanh", input_shape=(WINDOW, 1), return_sequences=False),
        Dropout(0.2),
        Dense(16, activation="relu"),
        Dense(1),
    ])
    model.compile(optimizer="adam", loss="mse")

    early_stop = EarlyStopping(monitor="loss", patience=10, restore_best_weights=True)
    model.fit(X_train, y_train, epochs=100, batch_size=16, verbose=0, callbacks=[early_stop])

    # Evaluate per state, then aggregate (same approach as ARIMA/SARIMA scripts)
    all_actual, all_pred = [], []
    per_state_results = []

    for state, X_te, y_te_scaled, scaler in test_sequences:
        X_te_reshaped = X_te.reshape(-1, WINDOW, 1)
        pred_scaled = model.predict(X_te_reshaped, verbose=0).flatten()

        # Invert scaling to get back to real price units
        pred_actual = scaler.inverse_transform(pred_scaled.reshape(-1, 1)).flatten()
        actual_actual = scaler.inverse_transform(y_te_scaled.reshape(-1, 1)).flatten()

        all_actual.extend(actual_actual)
        all_pred.extend(pred_actual)

        state_rmse = np.sqrt(mean_squared_error(actual_actual, pred_actual))
        per_state_results.append((state, state_rmse))

    if not all_actual:
        print(f"{crop}: no test sequences available, skipping evaluation")
        continue

    rmse = np.sqrt(mean_squared_error(all_actual, all_pred))
    mae = mean_absolute_error(all_actual, all_pred)
    r2 = r2_score(all_actual, all_pred)

    results_by_crop[crop] = {"RMSE": rmse, "MAE": mae, "R2": r2}

    print(f"{crop} (LSTM): RMSE={rmse:.2f}  MAE={mae:.2f}  R2={r2:.4f}")
    print("  Per-state RMSE:")
    for state, s_rmse in sorted(per_state_results, key=lambda x: x[1]):
        print(f"    {state}: {s_rmse:.2f}")

    model.save(f"../../models/lstm_model_{crop.lower()}.keras")

print("\n" + "=" * 60)
print("LSTM SUMMARY (compare to naive/RF/ARIMA/SARIMA results)")
print("=" * 60)
summary_df = pd.DataFrame(results_by_crop).T
summary_df.columns = ["LSTM_RMSE", "LSTM_MAE", "LSTM_R2"]
print(summary_df.round(2).to_string())
summary_df.to_csv("../../results/lstm_results.csv")
print("\nSaved to results/lstm_results.csv")