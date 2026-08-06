"""
FarmPulse AI - Flask Backend
Run with: python app.py  (from inside the dashboard/ folder)
Then open http://127.0.0.1:5000 in your browser.
"""

import json
import logging
import os
import sys
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
from flask import Flask, render_template, jsonify, request

from sklearn.preprocessing import MinMaxScaler

# Suppress statsmodels convergence warnings (noisy but harmless)
warnings.filterwarnings("ignore", category=UserWarning, module="statsmodels")
warnings.filterwarnings("ignore", category=FutureWarning, module="statsmodels")

# --------------- Logging Setup ---------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("farmpulse")

# --------------- Flask App ---------------
app = Flask(__name__, static_folder="static", static_url_path="/static")

DATA_DIR = "../data/processed"
MODELS_DIR = "../models"
RESULTS_DIR = "../results"
TREND_LOOKBACK = 3

# MSP table (Rs/quintal) - REPLACE with current year's official MSP figures
MSP_TABLE = {
    "Chana": 5650,
    "Moong": 8682,
    "Tur": 7550,
}

# --------------- Import Services ---------------
# Services are imported after app setup — they use config.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from services.ensemble import ensemble_predict, ensemble_forecast
from services.recommendation import generate_recommendation
from services.msp_alerts import get_msp_alert
from services.market_comparison import compare_markets
from services.profit_calculator import calculate_profit

# ---------------- Load everything once at startup ----------------

logger.info("Loading pipeline config and context data...")

with open(f"{MODELS_DIR}/final_pipeline_config.json") as f:
    CONFIG = json.load(f)

CONTEXT_DF = pd.read_csv(f"{DATA_DIR}/latest_context_all.csv", parse_dates=["date"])
TUR_CONTEXT_DF = pd.read_csv(f"{DATA_DIR}/tur_latest_context.csv", parse_dates=["date"])
TUR_MODEL_BUNDLE = joblib.load(f"{MODELS_DIR}/tur_final_model.joblib")

_lstm_cache = {}
_gru_cache = {}
_xgb_cache = {}
_rf_v2_cache = {}


def get_lstm_model(crop):
    if crop not in _lstm_cache:
        _lstm_cache[crop] = tf.keras.models.load_model(f"{MODELS_DIR}/lstm_model_{crop.lower()}.keras")
    return _lstm_cache[crop]


def get_gru_model(crop):
    """Load GRU model if available."""
    if crop not in _gru_cache:
        path = f"{MODELS_DIR}/gru_model_{crop.lower()}.keras"
        if os.path.exists(path):
            try:
                _gru_cache[crop] = tf.keras.models.load_model(path)
            except Exception as e:
                logger.warning(f"Failed to load GRU model for {crop}: {type(e).__name__}")
                _gru_cache[crop] = None
        else:
            _gru_cache[crop] = None
    return _gru_cache[crop]


def get_xgb_model(crop):
    """Load XGBoost model if available."""
    if crop not in _xgb_cache:
        path = f"{MODELS_DIR}/xgb_model_{crop.lower()}.joblib"
        if os.path.exists(path):
            _xgb_cache[crop] = joblib.load(path)
        else:
            _xgb_cache[crop] = None
    return _xgb_cache[crop]


def get_rf_v2_model(crop):
    """Load Random Forest v2 model (exists for all 3 crops)."""
    if crop not in _rf_v2_cache:
        path = f"{MODELS_DIR}/rf_model_v2_{crop.lower()}.joblib"
        if os.path.exists(path):
            _rf_v2_cache[crop] = joblib.load(path)
            logger.info("Loaded RF v2 model for %s", crop)
        else:
            _rf_v2_cache[crop] = None
    return _rf_v2_cache[crop]


logger.info("Startup complete. Models and data loaded.")


# ---------------- Prediction logic (same as before) ----------------

def predict_naive_flat(prices):
    return float(prices[-1])


def forecast_naive_flat(prices, steps):
    """Flat persistence stays flat for every future step - this is the
    honest limitation of naive persistence at longer horizons."""
    return [float(prices[-1])] * steps


def predict_naive_trend(prices, lookback=TREND_LOOKBACK):
    last_price = prices[-1]
    recent_diffs = np.diff(prices[-(lookback + 1):])
    drift = recent_diffs.mean() if len(recent_diffs) > 0 else 0
    return float(last_price + drift)


def forecast_naive_trend(prices, steps, lookback=TREND_LOOKBACK):
    recent_diffs = np.diff(prices[-(lookback + 1):])
    drift = recent_diffs.mean() if len(recent_diffs) > 0 else 0
    last_price = prices[-1]
    return [float(last_price + drift * (i + 1)) for i in range(steps)]


def predict_lstm(crop, prices):
    model = get_lstm_model(crop)
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(np.array(prices).reshape(-1, 1)).flatten()
    window = scaled[-12:].reshape(1, 12, 1)
    pred_scaled = model.predict(window, verbose=0).flatten()[0]
    return float(scaler.inverse_transform([[pred_scaled]])[0][0])


def forecast_lstm(crop, prices, steps):
    model = get_lstm_model(crop)
    scaler = MinMaxScaler()
    scaler.fit(np.array(prices).reshape(-1, 1))
    working_prices = list(prices)
    forecasts = []
    for _ in range(steps):
        scaled = scaler.transform(np.array(working_prices).reshape(-1, 1)).flatten()
        window = scaled[-12:].reshape(1, 12, 1)
        pred_scaled = model.predict(window, verbose=0).flatten()[0]
        pred = float(scaler.inverse_transform([[pred_scaled]])[0][0])
        forecasts.append(pred)
        working_prices.append(pred)  # feed prediction back in for the next step
    return forecasts


def predict_tur(latest_row):
    model, feature_cols = TUR_MODEL_BUNDLE["model"], TUR_MODEL_BUNDLE["feature_cols"]
    X = latest_row[feature_cols].values.reshape(1, -1)
    return float(model.predict(X)[0])


def forecast_tur(state_rows, steps):
    """Recursively forecast Tur prices, updating lag features each step.
    Arrival quantity features are held at their last known value, since we
    don't have future arrival data - a documented simplification."""
    model, feature_cols = TUR_MODEL_BUNDLE["model"], TUR_MODEL_BUNDLE["feature_cols"]
    prices = list(state_rows["modal_price"].values)
    last_qty_lag1 = state_rows["qty_lag_1m"].iloc[-1]
    last_qty_roll3 = state_rows["qty_rolling_3m"].iloc[-1]
    last_date = state_rows["date"].iloc[-1]

    forecasts = []
    for i in range(steps):
        month = (last_date.month + i) % 12 + 1
        quarter = (month - 1) // 3 + 1
        row = pd.DataFrame([{
            "lag_1m": prices[-1],
            "lag_3m": prices[-3] if len(prices) >= 3 else prices[0],
            "lag_12m": prices[-12] if len(prices) >= 12 else prices[0],
            "rolling_3m_avg": np.mean(prices[-3:]),
            "month": month,
            "quarter": quarter,
            "qty_lag_1m": last_qty_lag1,
            "qty_rolling_3m": last_qty_roll3,
        }])
        pred = float(model.predict(row[feature_cols])[0])
        forecasts.append(pred)
        prices.append(pred)
    return forecasts


# ---------------- New prediction helpers (GRU, XGBoost) ----------------

def forecast_gru(crop, prices, steps):
    """Forecast using GRU model — same approach as LSTM."""
    model = get_gru_model(crop)
    if model is None:
        return None
    scaler = MinMaxScaler()
    scaler.fit(np.array(prices).reshape(-1, 1))
    working_prices = list(prices)
    forecasts = []
    for _ in range(steps):
        scaled = scaler.transform(np.array(working_prices).reshape(-1, 1)).flatten()
        window = scaled[-12:].reshape(1, 12, 1)
        pred_scaled = model.predict(window, verbose=0).flatten()[0]
        pred = float(scaler.inverse_transform([[pred_scaled]])[0][0])
        forecasts.append(pred)
        working_prices.append(pred)
    return forecasts


def forecast_xgboost(crop, prices, steps):
    """Forecast using XGBoost model — same recursive approach as RF."""
    bundle = get_xgb_model(crop)
    if bundle is None:
        return None
    model = bundle["model"]
    working_prices = list(prices)
    forecasts = []
    last_date = datetime.now()
    for i in range(steps):
        month = (last_date.month + i) % 12 + 1
        quarter = (month - 1) // 3 + 1
        row = pd.DataFrame([{
            "lag_1m": working_prices[-1],
            "lag_3m": working_prices[-3] if len(working_prices) >= 3 else working_prices[0],
            "lag_6m": working_prices[-6] if len(working_prices) >= 6 else working_prices[0],
            "lag_12m": working_prices[-12] if len(working_prices) >= 12 else working_prices[0],
            "rolling_3m_avg": np.mean(working_prices[-3:]),
            "rolling_6m_avg": np.mean(working_prices[-6:]) if len(working_prices) >= 6 else np.mean(working_prices),
            "month": month,
            "quarter": quarter,
        }])
        pred = float(model.predict(row[bundle["feature_cols"]])[0])
        forecasts.append(pred)
        working_prices.append(pred)
    return forecasts


def forecast_prophet(crop, prices, steps):
    """Forecast using Prophet — fit on-demand for each request.
    
    Prophet models are lightweight and fast to refit, so we don't persist
    model files. This follows the design documented in train_prophet.py.
    
    Args:
        crop: Crop name (not used, Prophet uses generic approach)
        prices: Historical price array
        steps: Number of months to forecast
        
    Returns:
        List of forecasted prices or None if fitting fails
    """
    try:
        from prophet import Prophet
        
        # Prepare data in Prophet format (ds = datestamp, y = value)
        series = pd.DataFrame({
            'ds': pd.date_range(end=pd.Timestamp.now(), periods=len(prices), freq='MS'),
            'y': prices
        })
        
        # Fit Prophet model with monthly seasonality
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode='additive',
            changepoint_prior_scale=0.05,
        )
        
        # Suppress Prophet's verbose logging
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model.fit(series)
        
        # Generate future dates and forecast
        future = model.make_future_dataframe(periods=steps, freq='MS')
        forecast = model.predict(future)
        
        # Extract forecasted values (last N rows)
        forecasted_values = forecast['yhat'].tail(steps).values
        
        # Validate results
        result = [float(v) for v in forecasted_values]
        if any(np.isnan(v) or np.isinf(v) for v in result):
            logger.warning("Prophet produced NaN/Inf values")
            return None
            
        return result
        
    except ImportError:
        logger.warning("Prophet not installed - skipping Prophet forecast")
        return None
    except Exception as e:
        logger.warning("Prophet forecast failed: %s", e)
        return None


def forecast_rf_v2(crop, prices, steps):
    """Forecast using Random Forest v2 model — recursive lag-based.
    RF v2 models exist for all 3 crops with features:
    ['lag_1m', 'lag_3m', 'lag_6m', 'lag_12m', 'rolling_3m_avg', 'rolling_6m_avg', 'month', 'quarter']
    """
    bundle = get_rf_v2_model(crop)
    if bundle is None:
        return None
    model = bundle["model"]
    feature_cols = bundle["feature_cols"]
    working_prices = list(prices)
    last_date = datetime.now()
    forecasts = []
    for i in range(steps):
        month = (last_date.month + i) % 12 + 1
        quarter = (month - 1) // 3 + 1
        row = pd.DataFrame([{
            "lag_1m": working_prices[-1],
            "lag_3m": working_prices[-3] if len(working_prices) >= 3 else working_prices[0],
            "lag_6m": working_prices[-6] if len(working_prices) >= 6 else working_prices[0],
            "lag_12m": working_prices[-12] if len(working_prices) >= 12 else working_prices[0],
            "rolling_3m_avg": np.mean(working_prices[-3:]),
            "rolling_6m_avg": np.mean(working_prices[-6:]) if len(working_prices) >= 6 else np.mean(working_prices),
            "month": month,
            "quarter": quarter,
        }])
        pred = float(model.predict(row[feature_cols])[0])
        forecasts.append(pred)
        working_prices.append(pred)
    return forecasts


def forecast_arima(prices, steps):
    """Fit ARIMA(1,1,1) on the full price history and forecast N steps.
    ARIMA is stateless — re-fit each time from the historical series.
    This is fast for monthly data (~100-200 observations)."""
    try:
        from statsmodels.tsa.arima.model import ARIMA
        series = pd.Series(prices.copy() if hasattr(prices, 'copy') else list(prices))
        model = ARIMA(series, order=(1, 1, 1))
        fitted = model.fit()
        forecast = fitted.forecast(steps=steps)
        return [float(v) for v in forecast.values]
    except Exception as e:
        logger.warning("ARIMA forecast failed: %s", e)
        return None


def forecast_sarima(prices, steps):
    """Fit SARIMA with automatic fallback to simpler configurations.
    
    Tries multiple (p,d,q)(P,D,Q,s) configurations in order of complexity,
    from full seasonal model down to simple ARIMA, ensuring fault tolerance.
    
    Configuration priority:
    1. SARIMA(1,1,1)(1,1,0,12) - Full seasonal with trend
    2. SARIMA(1,1,0)(1,1,0,12) - Seasonal without MA
    3. SARIMA(0,1,1)(1,1,0,12) - Seasonal with MA only
    4. SARIMA(1,1,1)(1,0,0,12) - Seasonal without differencing
    5. SARIMA(1,1,0)(1,0,0,12) - Simpler seasonal
    6. SARIMA(0,1,1)(1,0,0,12) - MA seasonal
    7. ARIMA(1,1,1) - Non-seasonal fallback
    8. ARIMA(0,1,1) - Simpler ARIMA
    9. ARIMA(1,1,0) - Simplest ARIMA
    
    Args:
        prices: Historical price array
        steps: Number of periods to forecast
        
    Returns:
        tuple: (forecasts_list, config_name) or (None, None) if all fail
            forecasts_list: List of forecasted prices
            config_name: String identifying which configuration succeeded
    """
    try:
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        
        series = pd.Series(prices.copy() if hasattr(prices, 'copy') else list(prices))
        
        # Check minimum data requirements
        if len(series) < 12:
            logger.warning(f"SARIMA skipped: need 12+ months, have {len(series)}")
            return None, None
        
        # Configuration candidates: (order, seasonal_order, min_data_required, name)
        # Ordered from most to least complex
        configs = [
            # Full seasonal models (require 36+ months for seasonal differencing)
            ((1, 1, 1), (1, 1, 0, 12), 36, "SARIMA(1,1,1)(1,1,0,12)"),
            ((1, 1, 0), (1, 1, 0, 12), 36, "SARIMA(1,1,0)(1,1,0,12)"),
            ((0, 1, 1), (1, 1, 0, 12), 36, "SARIMA(0,1,1)(1,1,0,12)"),
            
            # Seasonal models without seasonal differencing (require 24+ months)
            ((1, 1, 1), (1, 0, 0, 12), 24, "SARIMA(1,1,1)(1,0,0,12)"),
            ((1, 1, 0), (1, 0, 0, 12), 24, "SARIMA(1,1,0)(1,0,0,12)"),
            ((0, 1, 1), (1, 0, 0, 12), 24, "SARIMA(0,1,1)(1,0,0,12)"),
            
            # ARIMA fallbacks (no seasonality, require 12+ months)
            ((1, 1, 1), (0, 0, 0, 0), 12, "ARIMA(1,1,1)"),
            ((0, 1, 1), (0, 0, 0, 0), 12, "ARIMA(0,1,1)"),
            ((1, 1, 0), (0, 0, 0, 0), 12, "ARIMA(1,1,0)"),
        ]
        
        # Try each configuration in order
        for order, seasonal_order, min_data, config_name in configs:
            # Skip if insufficient data for this configuration
            if len(series) < min_data:
                continue
            
            try:
                # Fit model with this configuration
                model = SARIMAX(
                    series,
                    order=order,
                    seasonal_order=seasonal_order,
                    enforce_stationarity=False,
                    enforce_invertibility=False
                )
                
                # Fit with limited iterations for faster convergence
                fitted = model.fit(
                    disp=False,
                    maxiter=50,
                    method='lbfgs'
                )
                
                # Generate forecast
                forecast = fitted.forecast(steps=steps)
                
                # Validate forecast values
                result = [float(v) for v in forecast.values]
                
                # Check for NaN/Inf
                if any(np.isnan(v) or np.isinf(v) for v in result):
                    logger.warning(f"SARIMA {config_name}: produced NaN/Inf, trying next config")
                    continue
                
                # Check for negative prices (invalid for this domain)
                if any(v < 0 for v in result):
                    logger.warning(f"SARIMA {config_name}: produced negative prices, trying next config")
                    continue
                
                # Check for unreasonably large values (> 10x current price)
                max_reasonable = max(prices) * 10
                if any(v > max_reasonable for v in result):
                    logger.warning(f"SARIMA {config_name}: produced unreasonable values, trying next config")
                    continue
                
                # Success! Return this forecast with config name
                logger.info(f"SARIMA succeeded with {config_name}")
                return result, config_name
                
            except Exception as e:
                # This configuration failed, try next one
                logger.warning(f"SARIMA {config_name} failed: {type(e).__name__}: {str(e)[:100]}")
                continue
        
        # All configurations failed
        logger.warning("SARIMA: all configurations failed to converge")
        return None, None
        
    except ImportError:
        logger.warning("statsmodels not installed - skipping SARIMA forecast")
        return None, None
    except Exception as e:
        logger.warning("SARIMA forecast failed with unexpected error: %s", e)
        return None, None


# ---------------- Shared helpers ----------------

def _get_state_data(crop, state):
    """Get state rows and metadata — used by multiple routes."""
    if crop == "Tur":
        state_rows = TUR_CONTEXT_DF[TUR_CONTEXT_DF["state"] == state].sort_values("date")
    else:
        state_rows = CONTEXT_DF[
            (CONTEXT_DF["state"] == state) & (CONTEXT_DF["crop_label"] == crop)
        ].sort_values("date")

    if state_rows.empty:
        return None, None, None

    last_date = state_rows["date"].iloc[-1]
    current_price = float(state_rows["modal_price"].iloc[-1])
    return state_rows, last_date, current_price


def _compute_steps(target_date, last_date):
    """Convert target_date string to number of steps ahead."""
    if target_date:
        target_year, target_month = map(int, target_date.split("-"))
        steps = (target_year - last_date.year) * 12 + (target_month - last_date.month)
        if steps < 1:
            return None, f"Please choose a future month - latest known data is {last_date.strftime('%Y-%m')}."
        if steps > 24:
            steps = 24
        return steps, None
    return 1, None


def _build_forecast_labels(last_date, steps):
    """Build month labels for forecast path."""
    labels = []
    for i in range(steps):
        m = last_date.month + i + 1
        y = last_date.year + (m - 1) // 12
        m = (m - 1) % 12 + 1
        labels.append(f"{y}-{m:02d}")
    return labels


def _validate_crop_state(crop, state):
    """Validate crop/state combination. Returns error response or None."""
    if not crop or crop not in CONFIG:
        return jsonify({"error": f"Invalid crop: {crop}. Available: {list(CONFIG.keys())}"}), 400
    if not state or state not in CONFIG[crop]:
        return jsonify({"error": f"Invalid state: {state} for crop {crop}. Available: {sorted(CONFIG[crop].keys())}"}), 400
    return None


def _collect_all_forecasts(crop, state, state_rows, prices, steps):
    """Collect forecasts from ALL available models for ensemble.
    This is the single source of truth for multi-model predictions.
    Every endpoint should call this instead of individual model functions.

    Returns:
        tuple: (forecasts_dict, status_dict)
            forecasts_dict: {model_name: [price1, price2, ...]}
            status_dict: {model_name: status_string} for diagnostics
    """
    forecasts = {}
    status = {}

    # 1. Tur-specific RF (with arrival quantity features)
    if crop == "Tur":
        try:
            forecasts["Random Forest"] = forecast_tur(state_rows, steps)
            status["Random Forest"] = "success"
        except Exception as e:
            logger.warning("RF(Tur) forecast failed for %s/%s: %s", crop, state, e)
            status["Random Forest"] = f"error: {type(e).__name__}"

    # 2. Random Forest v2 (exists for all 3 crops)
    try:
        rf_path = forecast_rf_v2(crop, prices, steps)
        if rf_path is not None:
            forecasts["Random Forest"] = rf_path  # overrides Tur RF if both exist
            status["Random Forest"] = "success"
        elif "Random Forest" not in status:
            status["Random Forest"] = "model_not_found"
    except Exception as e:
        logger.warning("RF v2 forecast failed for %s/%s: %s", crop, state, e)
        status["Random Forest"] = f"error: {type(e).__name__}"

    # 3. LSTM (exists for all 3 crops)
    try:
        forecasts["LSTM"] = forecast_lstm(crop, prices, steps)
        status["LSTM"] = "success"
    except Exception as e:
        logger.warning("LSTM forecast failed for %s/%s: %s", crop, state, e)
        status["LSTM"] = f"error: {type(e).__name__}"

    # 4. GRU (if trained)
    try:
        gru_path = forecast_gru(crop, prices, steps)
        if gru_path is not None:
            forecasts["GRU"] = gru_path
            status["GRU"] = "success"
        else:
            # Check if model file exists but failed to load
            gru_model_path = f"{MODELS_DIR}/gru_model_{crop.lower()}.keras"
            if os.path.exists(gru_model_path):
                status["GRU"] = "model_load_failed"
            else:
                status["GRU"] = "model_not_found"
    except Exception as e:
        logger.warning("GRU forecast failed for %s/%s: %s", crop, state, e)
        status["GRU"] = f"error: {type(e).__name__}"

    # 5. XGBoost (if trained)
    try:
        xgb_path = forecast_xgboost(crop, prices, steps)
        if xgb_path is not None:
            forecasts["XGBoost"] = xgb_path
            status["XGBoost"] = "success"
        else:
            # Check if model file exists but module missing
            xgb_model_path = f"{MODELS_DIR}/xgb_model_{crop.lower()}.joblib"
            if os.path.exists(xgb_model_path):
                status["XGBoost"] = "environment_missing"
            else:
                status["XGBoost"] = "model_not_found"
    except Exception as e:
        logger.warning("XGBoost forecast failed for %s/%s: %s", crop, state, e)
        # Check if it's an import error
        if "xgboost" in str(e).lower() or isinstance(e, (ImportError, ModuleNotFoundError)):
            status["XGBoost"] = "environment_missing"
        else:
            status["XGBoost"] = f"error: {type(e).__name__}"

    # 6. ARIMA (fit on-demand)
    try:
        arima_path = forecast_arima(prices, steps)
        if arima_path is not None:
            forecasts["ARIMA"] = arima_path
            status["ARIMA"] = "success"
        else:
            status["ARIMA"] = "convergence_failed"
    except Exception as e:
        logger.warning("ARIMA forecast failed for %s/%s: %s", crop, state, e)
        status["ARIMA"] = f"error: {type(e).__name__}"

    # 7. SARIMA (fit on-demand)
    try:
        sarima_result = forecast_sarima(prices, steps)
        if sarima_result[0] is not None:
            forecasts["SARIMA"] = sarima_result[0]
            config_used = sarima_result[1]
            
            # Expose which configuration actually succeeded
            # True SARIMA has seasonal component, ARIMA fallbacks don't
            if "ARIMA" in config_used:
                status["SARIMA"] = f"success (fallback: {config_used})"
            else:
                status["SARIMA"] = f"success ({config_used})"
        else:
            status["SARIMA"] = "convergence_failed"
    except Exception as e:
        logger.warning("SARIMA forecast failed for %s/%s: %s", crop, state, e)
        status["SARIMA"] = f"error: {type(e).__name__}"

    # 8. Prophet (fit on-demand)
    try:
        prophet_path = forecast_prophet(crop, prices, steps)
        if prophet_path is not None:
            forecasts["Prophet"] = prophet_path
            status["Prophet"] = "success"
        else:
            status["Prophet"] = "environment_missing"
    except ImportError:
        logger.warning("Prophet not installed for %s/%s", crop, state)
        status["Prophet"] = "environment_missing"
    except Exception as e:
        logger.warning("Prophet forecast failed for %s/%s: %s", crop, state, e)
        status["Prophet"] = f"error: {type(e).__name__}"

    # 9. Naive baselines (always available)
    forecasts["Naive_flat"] = forecast_naive_flat(prices, steps)
    status["Naive_flat"] = "success"
    forecasts["Naive_trend"] = forecast_naive_trend(prices, steps)
    status["Naive_trend"] = "success"

    return forecasts, status


def _get_ensemble_prediction(crop, state, state_rows, prices, steps):
    """Full ensemble pipeline: collect all models → compute weighted ensemble.
    Returns (ensemble_result, forecast_result, forecasts_dict, status_dict)."""
    forecasts_dict, status_dict = _collect_all_forecasts(crop, state, state_rows, prices, steps)

    # Build single-step predictions for ensemble weighting
    single_preds = {m: path[-1] for m, path in forecasts_dict.items()}
    ensemble_result = ensemble_predict(single_preds, crop, state)
    forecast_result = ensemble_forecast(forecasts_dict, crop, state)

    return ensemble_result, forecast_result, forecasts_dict, status_dict


# ---------------- Routes (existing — unchanged) ----------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/config")
def get_config():
    """Returns which crops/states are available, for populating dropdowns."""
    return jsonify({crop: sorted(list(states.keys())) for crop, states in CONFIG.items()})


@app.route("/api/predict")
def predict():
    crop = request.args.get("crop")
    state = request.args.get("state")
    target_date = request.args.get("target_date")  # optional, format YYYY-MM

    if crop not in CONFIG or state not in CONFIG[crop]:
        return jsonify({"error": "Invalid crop/state combination"}), 400

    try:
        if crop == "Tur":
            state_rows = TUR_CONTEXT_DF[TUR_CONTEXT_DF["state"] == state].sort_values("date")
        else:
            state_rows = CONTEXT_DF[(CONTEXT_DF["state"] == state) &
                                     (CONTEXT_DF["crop_label"] == crop)].sort_values("date")

        last_date = state_rows["date"].iloc[-1]
        current_price = float(state_rows["modal_price"].iloc[-1])

        # Work out how many months ahead the requested date is
        if target_date:
            target_year, target_month = map(int, target_date.split("-"))
            steps = (target_year - last_date.year) * 12 + (target_month - last_date.month)
            if steps < 1:
                return jsonify({"error": "Please choose a future month - "
                                          f"latest known data is {last_date.strftime('%Y-%m')}."}), 400
            if steps > 24:
                steps = 24  # cap - forecasts this far out are too unreliable to extend further
        else:
            steps = 1

        if crop == "Tur":
            path = forecast_tur(state_rows, steps)
            method_used = "Random Forest (with arrival quantity)"
        else:
            prices = state_rows["modal_price"].values
            method = CONFIG[crop][state]["method"]
            if method == "Naive_flat":
                path = forecast_naive_flat(prices, steps)
                method_used = "Persistence (last known price)"
            elif method == "Naive_trend":
                path = forecast_naive_trend(prices, steps)
                method_used = "Trend-adjusted persistence"
            else:
                path = forecast_lstm(crop, prices, steps)
                method_used = "LSTM (deep learning)"

        prediction = path[-1]
        msp = MSP_TABLE[crop]
        change_pct = (prediction - current_price) / current_price * 100

        history = state_rows[["date", "modal_price"]].copy()
        history["date"] = history["date"].dt.strftime("%Y-%m")

        # Build forecast path with month labels, for plotting the future segment
        forecast_labels = []
        for i in range(steps):
            m = last_date.month + i + 1
            y = last_date.year + (m - 1) // 12
            m = (m - 1) % 12 + 1
            forecast_labels.append(f"{y}-{m:02d}")

        return jsonify({
            "crop": crop,
            "state": state,
            "current_price": round(current_price, 2),
            "predicted_price": round(prediction, 2),
            "change_pct": round(change_pct, 2),
            "msp": msp,
            "below_msp": prediction < msp,
            "method_used": method_used,
            "history": history.to_dict(orient="records"),
            "forecast_path": [round(p, 2) for p in path],
            "forecast_labels": forecast_labels,
            "steps_ahead": steps,
            "target_month": forecast_labels[-1],
        })

    except Exception as e:
        logger.exception("Prediction error for %s/%s", crop, state)
        return jsonify({"error": str(e)}), 500


# ---------------- New API Routes ----------------

@app.route("/api/ensemble_predict")
def api_ensemble_predict():
    """Weighted ensemble prediction combining all available models."""
    crop = request.args.get("crop")
    state = request.args.get("state")
    target_date = request.args.get("target_date")

    validation_error = _validate_crop_state(crop, state)
    if validation_error:
        return validation_error

    try:
        state_rows, last_date, current_price = _get_state_data(crop, state)
        if state_rows is None:
            return jsonify({"error": "No data found for this crop/state"}), 404

        steps, error_msg = _compute_steps(target_date, last_date)
        if error_msg:
            return jsonify({"error": error_msg}), 400

        prices = state_rows["modal_price"].values

        # Collect forecasts from ALL available models via central helper
        ensemble_result, forecast_result, forecasts_dict, status_dict = \
            _get_ensemble_prediction(crop, state, state_rows, prices, steps)

        forecast_labels = _build_forecast_labels(last_date, steps)

        history = state_rows[["date", "modal_price"]].copy()
        history["date"] = history["date"].dt.strftime("%Y-%m")

        change_pct = (
            (ensemble_result["ensemble_price"] - current_price)
            / current_price * 100
        )

        return jsonify({
            "crop": crop,
            "state": state,
            "current_price": round(current_price, 2),
            "ensemble_price": ensemble_result["ensemble_price"],
            "change_pct": round(change_pct, 2),
            "confidence": ensemble_result["confidence"],
            "models_used": ensemble_result["models_used"],
            "weights": ensemble_result["weights"],
            "individual_predictions": ensemble_result["individual_predictions"],
            "model_status": status_dict,  # NEW: diagnostic information
            "msp": ensemble_result["msp"],
            "below_msp": ensemble_result["below_msp"],
            "ensemble_path": forecast_result["ensemble_path"],
            "confidence_per_step": forecast_result["confidence_per_step"],
            "individual_forecasts": {
                m: [round(p, 2) for p in path]
                for m, path in forecasts_dict.items()
            },
            "forecast_labels": forecast_labels,
            "history": history.to_dict(orient="records"),
            "steps_ahead": steps,
            "target_month": forecast_labels[-1],
        })

    except Exception as e:
        logger.exception("Ensemble prediction error for %s/%s", crop, state)
        return jsonify({"error": str(e)}), 500


@app.route("/api/recommendation")
def api_recommendation():
    """Generate human-readable recommendation based on prediction."""
    crop = request.args.get("crop")
    state = request.args.get("state")
    target_date = request.args.get("target_date")

    validation_error = _validate_crop_state(crop, state)
    if validation_error:
        return validation_error

    try:
        state_rows, last_date, current_price = _get_state_data(crop, state)
        if state_rows is None:
            return jsonify({"error": "No data found"}), 404

        steps, error_msg = _compute_steps(target_date, last_date)
        if error_msg:
            return jsonify({"error": error_msg}), 400

        prices = state_rows["modal_price"].values

        # Use ensemble prediction
        ensemble_result, forecast_result, forecasts_dict, status_dict = \
            _get_ensemble_prediction(crop, state, state_rows, prices, steps)

        predicted_price = ensemble_result["ensemble_price"]
        path = forecast_result["ensemble_path"]

        recommendation = generate_recommendation(
            crop=crop,
            state=state,
            current_price=current_price,
            predicted_price=predicted_price,
            history_prices=list(prices),
            forecast_path=path,
            confidence=ensemble_result["confidence"],
            current_month=last_date.month,
        )

        recommendation["crop"] = crop
        recommendation["state"] = state
        recommendation["current_price"] = round(current_price, 2)
        recommendation["predicted_price"] = round(predicted_price, 2)
        recommendation["models_used"] = ensemble_result["models_used"]
        recommendation["ensemble_confidence"] = ensemble_result["confidence"]

        return jsonify(recommendation)

    except Exception as e:
        logger.exception("Recommendation error for %s/%s", crop, state)
        return jsonify({"error": str(e)}), 500


@app.route("/api/msp_alert")
def api_msp_alert():
    """Get MSP alert status for a crop/state."""
    crop = request.args.get("crop")
    state = request.args.get("state")

    validation_error = _validate_crop_state(crop, state)
    if validation_error:
        return validation_error

    try:
        state_rows, last_date, current_price = _get_state_data(crop, state)
        if state_rows is None:
            return jsonify({"error": "No data found"}), 404

        prices = state_rows["modal_price"].values

        # Use ensemble for MSP alert
        ensemble_result, _, _, _ = \
            _get_ensemble_prediction(crop, state, state_rows, prices, 1)

        predicted = ensemble_result["ensemble_price"]

        alert = get_msp_alert(crop, predicted, current_price)
        alert["models_used"] = ensemble_result["models_used"]
        alert["ensemble_confidence"] = ensemble_result["confidence"]
        alert["crop"] = crop
        alert["state"] = state

        return jsonify(alert)

    except Exception as e:
        logger.exception("MSP alert error for %s/%s", crop, state)
        return jsonify({"error": str(e)}), 500


@app.route("/api/market_comparison")
def api_market_comparison():
    """Compare predictions across all states for a given crop."""
    crop = request.args.get("crop")

    if not crop or crop not in CONFIG:
        return jsonify({"error": f"Invalid crop. Available: {list(CONFIG.keys())}"}), 400

    try:
        state_predictions = {}
        for state in CONFIG[crop]:
            state_rows, last_date, current_price = _get_state_data(crop, state)
            if state_rows is None:
                continue

            prices = state_rows["modal_price"].values

            # Use ensemble for each state
            ensemble_result, _, _, _ = \
                _get_ensemble_prediction(crop, state, state_rows, prices, 1)

            predicted = ensemble_result["ensemble_price"]
            change_pct = (predicted - current_price) / current_price * 100

            state_predictions[state] = {
                "current_price": current_price,
                "predicted_price": predicted,
                "change_pct": change_pct,
                "method_used": f"Ensemble ({len(ensemble_result['models_used'])} models)",
            }

        result = compare_markets(crop, state_predictions)
        return jsonify(result)

    except Exception as e:
        logger.exception("Market comparison error for %s", crop)
        return jsonify({"error": str(e)}), 500


@app.route("/api/profit_estimate")
def api_profit_estimate():
    """Calculate detailed profit estimate."""
    crop = request.args.get("crop")
    state = request.args.get("state")

    validation_error = _validate_crop_state(crop, state)
    if validation_error:
        return validation_error

    try:
        quantity = float(request.args.get("quantity", 10))
        cost = request.args.get("cost")
        cost = float(cost) if cost else None
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid quantity or cost value"}), 400

    try:
        state_rows, last_date, current_price = _get_state_data(crop, state)
        if state_rows is None:
            return jsonify({"error": "No data found"}), 404

        prices = state_rows["modal_price"].values

        # Use ensemble for profit estimate
        ensemble_result, _, _, _ = \
            _get_ensemble_prediction(crop, state, state_rows, prices, 1)

        predicted = ensemble_result["ensemble_price"]

        result = calculate_profit(
            crop=crop,
            quantity_quintals=quantity,
            current_price=current_price,
            predicted_price=predicted,
            cost_per_quintal=cost,
        )
        result["models_used"] = ensemble_result["models_used"]
        result["ensemble_confidence"] = ensemble_result["confidence"]

        result["state"] = state
        return jsonify(result)

    except Exception as e:
        logger.exception("Profit estimate error for %s/%s", crop, state)
        return jsonify({"error": str(e)}), 500


@app.route("/api/dashboard_summary")
def api_dashboard_summary():
    """Aggregated dashboard data — all key metrics in one call."""
    crop = request.args.get("crop")
    state = request.args.get("state")

    validation_error = _validate_crop_state(crop, state)
    if validation_error:
        return validation_error

    try:
        state_rows, last_date, current_price = _get_state_data(crop, state)
        if state_rows is None:
            return jsonify({"error": "No data found"}), 404

        prices = state_rows["modal_price"].values

        # Use ensemble for dashboard — this is the core change
        ensemble_result, forecast_result, forecasts_dict, status_dict = \
            _get_ensemble_prediction(crop, state, state_rows, prices, 7)

        path = forecast_result["ensemble_path"]
        predicted_1 = path[0] if path else ensemble_result["ensemble_price"]
        predicted_7 = path[-1] if len(path) >= 7 else predicted_1
        change_pct = (predicted_1 - current_price) / current_price * 100

        # Trend direction from recent prices
        if len(prices) >= 4:
            recent_diffs = np.diff(prices[-4:])
            trend = "rising" if np.mean(recent_diffs) > 0 else "falling" if np.mean(recent_diffs) < 0 else "stable"
        else:
            trend = "stable"

        # MSP alert
        msp = MSP_TABLE.get(crop, 0)
        alert = get_msp_alert(crop, predicted_1, current_price)

        # Recommendation
        rec = generate_recommendation(
            crop=crop, state=state,
            current_price=current_price, predicted_price=predicted_1,
            history_prices=list(prices), forecast_path=path,
            confidence=ensemble_result["confidence"],
            current_month=last_date.month,
        )

        # History for sparkline
        history = state_rows[["date", "modal_price"]].copy()
        history["date"] = history["date"].dt.strftime("%Y-%m")

        forecast_labels = _build_forecast_labels(last_date, 7)

        return jsonify({
            "crop": crop,
            "state": state,
            "current_price": round(current_price, 2),
            "predicted_price": round(predicted_1, 2),
            "predicted_7d": round(predicted_7, 2),
            "change_pct": round(change_pct, 2),
            "trend": trend,
            "method_used": f"Ensemble ({len(ensemble_result['models_used'])} models)",
            "msp": msp,
            "msp_alert": alert,
            "recommendation": rec,
            "forecast_path": [round(p, 2) for p in path],
            "forecast_labels": forecast_labels,
            "history": history.to_dict(orient="records"),
            "last_updated": last_date.strftime("%Y-%m-%d"),
            "confidence": ensemble_result["confidence"],
            "models_used": ensemble_result["models_used"],
            "weights": ensemble_result["weights"],
            "individual_predictions": ensemble_result["individual_predictions"],
            "ensemble_price": ensemble_result["ensemble_price"],
        })

    except Exception as e:
        logger.exception("Dashboard summary error for %s/%s", crop, state)
        return jsonify({"error": str(e)}), 500


@app.route("/api/model_metrics")
def api_model_metrics():
    """Return model comparison metrics from results files."""
    try:
        metrics = {}

        # Load each results file
        results_files = {
            "Random Forest": ("rf_v2_vs_naive_results.csv", ["RF_RMSE", "RF_MAE", "RF_R2"]),
            "LSTM": ("lstm_results.csv", ["LSTM_RMSE", "LSTM_MAE", "LSTM_R2"]),
            "ARIMA": ("arima_results.csv", ["ARIMA_RMSE", "ARIMA_MAE", "ARIMA_R2"]),
            "SARIMA": ("sarima_results.csv", ["SARIMA_RMSE", "SARIMA_MAE", "SARIMA_R2"]),
        }

        # Also check for optional models
        optional_files = {
            "XGBoost": ("xgboost_results.csv", ["XGB_RMSE", "XGB_MAE", "XGB_R2"]),
            "GRU": ("gru_results.csv", ["GRU_RMSE", "GRU_MAE", "GRU_R2"]),
            "Prophet": ("prophet_results.csv", ["Prophet_RMSE", "Prophet_MAE", "Prophet_R2"]),
        }
        results_files.update(optional_files)

        for model_name, (filename, cols) in results_files.items():
            filepath = os.path.join(RESULTS_DIR, filename)
            if os.path.exists(filepath):
                try:
                    df = pd.read_csv(filepath, index_col=0)
                    model_data = {}
                    for crop in df.index:
                        crop_metrics = {}
                        for col in cols:
                            if col in df.columns:
                                val = df.loc[crop, col]
                                key = col.split("_", 1)[1] if "_" in col else col
                                crop_metrics[key] = round(float(val), 4) if pd.notna(val) else None
                        if crop_metrics:
                            model_data[crop] = crop_metrics
                    if model_data:
                        metrics[model_name] = model_data
                except Exception as e:
                    logger.warning("Could not load %s: %s", filename, e)

        return jsonify({
            "models": metrics,
            "available_models": list(metrics.keys()),
        })

    except Exception as e:
        logger.exception("Model metrics error")
        return jsonify({"error": str(e)}), 500


def _feature_importance_from_bundle(model_name, bundle):
    """Extract persisted feature importances without running a prediction.

    Only tree-based bundles expose this attribute. The response deliberately
    omits a model rather than deriving an approximation from another source.
    """
    if not bundle:
        return None

    model = bundle.get("model") if isinstance(bundle, dict) else None
    feature_cols = bundle.get("feature_cols") if isinstance(bundle, dict) else None
    importances = getattr(model, "feature_importances_", None)

    if importances is None or not feature_cols or len(importances) != len(feature_cols):
        return None

    rows = [
        {"feature": str(feature), "importance": round(float(importance), 6)}
        for feature, importance in zip(feature_cols, importances)
        if np.isfinite(importance)
    ]
    rows.sort(key=lambda row: row["importance"], reverse=True)
    return {"model": model_name, "features": rows}


@app.route("/api/analytics_metadata")
def api_analytics_metadata():
    """Return read-only provenance for the academic analytics experience.

    This endpoint reads the trained model bundles and recorded project files
    only. It does not alter prediction, ensemble weighting, or model state.
    """
    crop = request.args.get("crop")
    if not crop or crop not in CONFIG:
        return jsonify({"error": f"Invalid crop. Available: {list(CONFIG.keys())}"}), 400

    feature_importance = []
    for model_name, loader in (
        ("Random Forest", get_rf_v2_model),
        ("XGBoost", get_xgb_model),
    ):
        try:
            result = _feature_importance_from_bundle(model_name, loader(crop))
            if result:
                feature_importance.append(result)
        except Exception as e:
            logger.warning("Could not read %s feature importance for %s: %s", model_name, crop, e)

    artifact_paths = [
        os.path.join(MODELS_DIR, f"rf_model_v2_{crop.lower()}.joblib"),
        os.path.join(MODELS_DIR, f"xgb_model_{crop.lower()}.joblib"),
        os.path.join(MODELS_DIR, f"lstm_model_{crop.lower()}.keras"),
        os.path.join(MODELS_DIR, f"gru_model_{crop.lower()}.keras"),
    ]
    available_timestamps = [
        os.path.getmtime(path) for path in artifact_paths if os.path.exists(path)
    ]
    latest_artifact = (
        datetime.fromtimestamp(max(available_timestamps)).isoformat(timespec="seconds")
        if available_timestamps else None
    )

    return jsonify({
        "crop": crop,
        "feature_importance": feature_importance,
        "feature_importance_available": bool(feature_importance),
        "latest_model_artifact_modified": latest_artifact,
        "evaluation": {
            "holdout_months": 12,
            "holdout_note": "The training scripts use a 12-month holdout for eligible state series.",
            "mape": None,
            "validation_dataset_size": None,
        },
    })

# ---------------- Error Handlers ----------------

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)