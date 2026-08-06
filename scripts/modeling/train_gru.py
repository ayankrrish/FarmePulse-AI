"""
FarmPulse AI — GRU Model
Architecture mirrors train_lstm.py but uses GRU layers instead of LSTM.
GRUs have fewer parameters (no separate cell state), so they train faster
and can generalize better on smaller datasets like ours.

Same design choices as LSTM:
  - Per-state normalization (MinMax fit on training portion only)
  - WINDOW=12 months of history → predict next month
  - Pooled training across all states per crop
  - Same 12-month time-based holdout per state
"""

import warnings
warnings.filterwarnings("ignore")

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["OMP_NUM_THREADS"] = "1"

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

import tensorflow as tf
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.threading.set_inter_op_parallelism_threads(1)

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

tf.random.set_seed(42)
np.random.seed(42)

# --------------- Paths (pathlib-based) ---------------
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = DATA_DIR / "ceda_cleaned_data.csv"
if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {INPUT_FILE}")

TEST_MONTHS = 12
WINDOW = 12  # same window as LSTM


def make_sequences(prices, window):
    """Turn a 1D price array into (X, y) sliding-window sequences."""
    X, y = [], []
    for i in range(len(prices) - window):
        X.append(prices[i:i + window])
        y.append(prices[i + window])
    return np.array(X), np.array(y)


df = pd.read_csv(INPUT_FILE, parse_dates=["date"])
df = df.dropna(subset=["modal_price"])

results_by_crop = {}

for crop in df["crop_label"].unique():
    crop_df = df[df["crop_label"] == crop]

    X_train_all, y_train_all = [], []
    test_sequences = []

    for state in crop_df["state"].unique():
        series = crop_df[crop_df["state"] == state].sort_values("date")["modal_price"].values

        if len(series) <= WINDOW + TEST_MONTHS + 12:
            continue

        train_prices = series[:-TEST_MONTHS]
        test_prices = series[-(TEST_MONTHS + WINDOW):]

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
        print(f"{crop}: not enough data for GRU, skipping")
        continue

    X_train = np.concatenate(X_train_all).reshape(-1, WINDOW, 1)
    y_train = np.concatenate(y_train_all)

    print(f"\nTraining GRU for {crop}: {len(X_train)} training sequences...")

    model = Sequential([
        GRU(32, activation="tanh", input_shape=(WINDOW, 1), return_sequences=False),
        Dropout(0.2),
        Dense(16, activation="relu"),
        Dense(1),
    ])
    model.compile(optimizer="adam", loss="mse")

    early_stop = EarlyStopping(monitor="loss", patience=10, restore_best_weights=True)
    model.fit(X_train, y_train, epochs=100, batch_size=16, verbose=0, callbacks=[early_stop])

    # Evaluate per state
    all_actual, all_pred = [], []
    per_state_results = []

    for state, X_te, y_te_scaled, scaler in test_sequences:
        X_te_reshaped = X_te.reshape(-1, WINDOW, 1)
        pred_scaled = model.predict(X_te_reshaped, verbose=0).flatten()

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

    print(f"{crop} (GRU): RMSE={rmse:.2f}  MAE={mae:.2f}  R2={r2:.4f}")
    print("  Per-state RMSE:")
    for state, s_rmse in sorted(per_state_results, key=lambda x: x[1]):
        print(f"    {state}: {s_rmse:.2f}")

    model.save(str(MODELS_DIR / f"gru_model_{crop.lower()}.keras"))

print("\n" + "=" * 60)
print("GRU SUMMARY (compare to LSTM and other models)")
print("=" * 60)
summary_df = pd.DataFrame(results_by_crop).T
summary_df.columns = ["GRU_RMSE", "GRU_MAE", "GRU_R2"]
print(summary_df.round(2).to_string())
summary_df.to_csv(str(RESULTS_DIR / "gru_results.csv"))
print("\nSaved models to models/gru_model_*.keras")
print("Saved results to results/gru_results.csv")
