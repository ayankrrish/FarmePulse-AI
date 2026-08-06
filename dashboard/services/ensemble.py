"""
FarmPulse AI — Weighted Ensemble Predictor
Combines predictions from all available models using inverse-RMSE weighting.
Falls back gracefully when models are missing.
"""

import json
import logging
import os

import numpy as np

from config import (
    RESULTS_DIR,
    DEFAULT_ENSEMBLE_WEIGHTS,
    MSP_TABLE,
    TREND_LOOKBACK,
)

logger = logging.getLogger(__name__)


def _load_per_state_metrics():
    """Load per-state RMSE from the model selection results."""
    path = os.path.join(RESULTS_DIR, "model_selection_per_state.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _load_aggregate_metrics():
    """Load aggregate model metrics from results CSVs for weight computation."""
    import pandas as pd

    metrics = {}
    files = {
        "LSTM": ("lstm_results.csv", "LSTM_RMSE"),
        "Random Forest": ("rf_v2_vs_naive_results.csv", "RF_RMSE"),
        "ARIMA": ("arima_results.csv", "ARIMA_RMSE"),
        "SARIMA": ("sarima_results.csv", "SARIMA_RMSE"),
        "XGBoost": ("xgboost_results.csv", "XGB_RMSE"),
        "GRU": ("gru_results.csv", "GRU_RMSE"),
        "Prophet": ("prophet_results.csv", "Prophet_RMSE"),
    }
    for model_name, (filename, rmse_col) in files.items():
        path = os.path.join(RESULTS_DIR, filename)
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, index_col=0)
                if rmse_col in df.columns:
                    metrics[model_name] = df[rmse_col].to_dict()
            except Exception as e:
                logger.warning("Could not load %s: %s", filename, e)
    return metrics


# Cache loaded metrics
_per_state_metrics = None
_aggregate_metrics = None


def _get_per_state_metrics():
    global _per_state_metrics
    if _per_state_metrics is None:
        _per_state_metrics = _load_per_state_metrics()
    return _per_state_metrics


def _get_aggregate_metrics():
    global _aggregate_metrics
    if _aggregate_metrics is None:
        _aggregate_metrics = _load_aggregate_metrics()
    return _aggregate_metrics


def compute_ensemble_weights(crop, state, available_models):
    """
    Compute weights for available models based on inverse-RMSE.
    Models with lower RMSE on test data get proportionally higher weight.

    Args:
        crop: Crop name (e.g. "Chana")
        state: State name (e.g. "Gujarat")
        available_models: list of model names that produced predictions

    Returns:
        dict of {model_name: weight} summing to 1.0
    """
    per_state = _get_per_state_metrics()
    aggregate = _get_aggregate_metrics()

    # Try to get per-state RMSE for each available model
    rmse_values = {}
    for model in available_models:
        # Check per-state results first
        state_data = per_state.get(crop, {}).get(state, {})
        val_scores = state_data.get("validation_scores", {})

        if model in val_scores:
            rmse_values[model] = val_scores[model]
        elif model in aggregate and crop in aggregate[model]:
            rmse_values[model] = aggregate[model][crop]
        elif model in DEFAULT_ENSEMBLE_WEIGHTS:
            # Use default weight as fallback — assign a synthetic RMSE
            rmse_values[model] = 500.0  # neutral placeholder

    if not rmse_values:
        # Equal weights if no metrics available
        n = len(available_models)
        return {m: 1.0 / n for m in available_models}

    # Inverse-RMSE weighting: lower RMSE → higher weight
    inverse_rmse = {m: 1.0 / max(r, 1.0) for m, r in rmse_values.items()}
    total = sum(inverse_rmse.values())
    weights = {m: v / total for m, v in inverse_rmse.items()}

    return weights


def ensemble_predict(predictions_dict, crop, state):
    """
    Combine multiple model predictions into a weighted ensemble.

    Args:
        predictions_dict: dict of {model_name: predicted_price}
        crop: Crop name
        state: State name

    Returns:
        dict with ensemble_price, confidence, individual predictions, weights
    """
    if not predictions_dict:
        return {
            "ensemble_price": None,
            "confidence": 0,
            "models_used": [],
            "error": "No predictions available",
        }

    available = list(predictions_dict.keys())
    weights = compute_ensemble_weights(crop, state, available)

    # Weighted average
    ensemble_price = sum(
        predictions_dict[m] * weights.get(m, 0) for m in available
    )

    # Confidence score: based on agreement between models
    # Low standard deviation relative to mean → high confidence
    values = list(predictions_dict.values())
    if len(values) > 1:
        std = np.std(values)
        mean = np.mean(values)
        cv = std / max(mean, 1.0)  # coefficient of variation
        # Map CV to 0-100 confidence: CV=0 → 100, CV≥0.3 → ~20
        confidence = max(10, min(100, int(100 * (1 - cv / 0.3))))
    else:
        confidence = 60  # single model — moderate confidence

    # MSP comparison
    msp = MSP_TABLE.get(crop, 0)
    below_msp = ensemble_price < msp if msp else False

    return {
        "ensemble_price": round(ensemble_price, 2),
        "confidence": confidence,
        "models_used": available,
        "weights": {m: round(w, 4) for m, w in weights.items()},
        "individual_predictions": {
            m: round(v, 2) for m, v in predictions_dict.items()
        },
        "msp": msp,
        "below_msp": below_msp,
    }


def ensemble_forecast(forecasts_dict, crop, state):
    """
    Combine multi-step forecasts from multiple models.

    Args:
        forecasts_dict: dict of {model_name: [price1, price2, ...]}
        crop: Crop name
        state: State name

    Returns:
        dict with ensemble forecast path, confidence per step, etc.
    """
    if not forecasts_dict:
        return {"ensemble_path": [], "confidence": 0, "models_used": []}

    available = list(forecasts_dict.keys())
    weights = compute_ensemble_weights(crop, state, available)

    # Find max forecast length
    max_steps = max(len(v) for v in forecasts_dict.values())

    ensemble_path = []
    confidences = []

    for step in range(max_steps):
        step_preds = {}
        for model in available:
            path = forecasts_dict[model]
            if step < len(path):
                step_preds[model] = path[step]

        if not step_preds:
            break

        # Weighted average for this step
        step_weights = compute_ensemble_weights(crop, state, list(step_preds.keys()))
        price = sum(step_preds[m] * step_weights.get(m, 0) for m in step_preds)
        ensemble_path.append(round(price, 2))

        # Per-step confidence
        vals = list(step_preds.values())
        if len(vals) > 1:
            cv = np.std(vals) / max(np.mean(vals), 1.0)
            conf = max(10, min(100, int(100 * (1 - cv / 0.3))))
        else:
            conf = 60
        confidences.append(conf)

    return {
        "ensemble_path": ensemble_path,
        "confidence_per_step": confidences,
        "avg_confidence": int(np.mean(confidences)) if confidences else 0,
        "models_used": available,
        "weights": {m: round(w, 4) for m, w in weights.items()},
    }
