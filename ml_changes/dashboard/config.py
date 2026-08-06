"""
FarmPulse AI — Centralized Configuration
All file paths, MSP values, model parameters, and feature flags
live here instead of being scattered across modules.
"""

import os

# --------------- Paths ---------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")

# --------------- Data Files ---------------
CONTEXT_CSV = os.path.join(DATA_DIR, "latest_context_all.csv")
TUR_CONTEXT_CSV = os.path.join(DATA_DIR, "tur_latest_context.csv")
CLEANED_DATA_CSV = os.path.join(DATA_DIR, "ceda_cleaned_data.csv")
MODEL_READY_CSV = os.path.join(DATA_DIR, "farmpulse_model_ready.csv")
PIPELINE_CONFIG_JSON = os.path.join(MODELS_DIR, "final_pipeline_config.json")
TUR_MODEL_PATH = os.path.join(MODELS_DIR, "tur_final_model.joblib")

# --------------- MSP Table (Rs/quintal) ---------------
# Source: Government of India, Commission for Agricultural Costs & Prices
# Updated for 2025-26 marketing season
MSP_TABLE = {
    "Chana": 5650,
    "Moong": 8682,
    "Tur": 7550,
}

# --------------- Model Parameters ---------------
TREND_LOOKBACK = 3          # months used for trend-adjusted naive
LSTM_WINDOW = 12            # months of history for LSTM/GRU input
MAX_FORECAST_MONTHS = 24    # cap on how far ahead we forecast
TEST_MONTHS = 12            # holdout months used during training

# --------------- Supported Crops & Models ---------------
SUPPORTED_CROPS = ["Chana", "Moong", "Tur"]

# Models available in the project (used by ensemble)
MODEL_TYPES = [
    "Random Forest",
    "LSTM",
    "GRU",
    "XGBoost",
    "ARIMA",
    "SARIMA",
    "Prophet",
    "Naive_flat",
    "Naive_trend",
]

# --------------- Ensemble Weights ---------------
# Default weights when all models are available.
# Based on inverse-RMSE from test results — lower RMSE → higher weight.
# These are overridden per crop-state by the ensemble service using
# actual RMSE values from results CSVs (inverse-RMSE weighting).
DEFAULT_ENSEMBLE_WEIGHTS = {
    "LSTM": 0.25,
    "Random Forest": 0.25,
    "GRU": 0.15,
    "XGBoost": 0.10,
    "ARIMA": 0.05,
    "SARIMA": 0.05,
    "Prophet": 0.05,
    "Naive_flat": 0.05,
    "Naive_trend": 0.05,
}

# --------------- MSP Alert Thresholds ---------------
MSP_ALERT_GREEN_THRESHOLD = 1.10   # >= 110% of MSP → Green
MSP_ALERT_YELLOW_THRESHOLD = 1.00  # >= 100% of MSP → Yellow
# Below 100% → Red

# --------------- Recommendation Thresholds ---------------
PRICE_RISE_THRESHOLD = 5.0     # % change to trigger "prices rising"
PRICE_FALL_THRESHOLD = -5.0    # % change to trigger "prices falling"
HIGH_VOLATILITY_THRESHOLD = 0.15  # coefficient of variation threshold

# --------------- Harvest Seasons (months) ---------------
# Used for seasonality features and recommendations
HARVEST_MONTHS = {
    "Chana": [3, 4],       # Rabi: harvested Mar-Apr
    "Moong": [9, 10],      # Kharif: harvested Sep-Oct
    "Tur": [1, 2, 3],      # Kharif (late): harvested Jan-Mar
}

# --------------- Flask Settings ---------------
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000
FLASK_DEBUG = True

# --------------- Logging ---------------
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
