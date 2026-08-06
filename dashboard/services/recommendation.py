"""
FarmPulse AI — Recommendation Engine
Generates human-readable, actionable recommendations from prediction data.
No fake AI — all logic is derived from actual prediction outputs.
"""

import logging
import numpy as np

from config import (
    MSP_TABLE,
    PRICE_RISE_THRESHOLD,
    PRICE_FALL_THRESHOLD,
    HIGH_VOLATILITY_THRESHOLD,
    HARVEST_MONTHS,
)

logger = logging.getLogger(__name__)


def _assess_volatility(prices):
    """Compute coefficient of variation as a volatility measure."""
    if len(prices) < 3:
        return 0.0, "insufficient_data"

    recent = prices[-6:] if len(prices) >= 6 else prices
    cv = float(np.std(recent) / max(np.mean(recent), 1.0))

    if cv > HIGH_VOLATILITY_THRESHOLD:
        return cv, "high"
    elif cv > HIGH_VOLATILITY_THRESHOLD * 0.5:
        return cv, "medium"
    else:
        return cv, "low"


def _compute_trend(prices, window=3):
    """Compute trend direction from recent prices."""
    if len(prices) < window + 1:
        return 0.0, "stable"

    recent = prices[-(window + 1):]
    diffs = np.diff(recent)
    avg_change = float(np.mean(diffs))
    pct_change = avg_change / max(abs(recent[-2]), 1.0) * 100

    if pct_change > 2.0:
        return pct_change, "rising"
    elif pct_change < -2.0:
        return pct_change, "falling"
    else:
        return pct_change, "stable"


def generate_recommendation(
    crop,
    state,
    current_price,
    predicted_price,
    history_prices=None,
    forecast_path=None,
    confidence=None,
    current_month=None,
):
    """
    Generate a comprehensive, human-readable recommendation.

    Args:
        crop: Crop name
        state: State name
        current_price: Current price in Rs/quintal
        predicted_price: Predicted price (next period)
        history_prices: list of recent historical prices (optional)
        forecast_path: list of multi-step forecast prices (optional)
        confidence: prediction confidence score 0-100 (optional)
        current_month: current month number 1-12 (optional)

    Returns:
        dict with primary_action, details, risk_level, factors, etc.
    """
    msp = MSP_TABLE.get(crop, 0)
    change = predicted_price - current_price
    change_pct = (change / max(current_price, 1.0)) * 100

    # --- Primary action ---
    if change_pct > PRICE_RISE_THRESHOLD:
        primary_action = "Hold — Prices Rising"
        action_icon = "📈"
        action_detail = (
            f"Prices are expected to rise by {change_pct:.1f}% "
            f"(₹{current_price:.0f} → ₹{predicted_price:.0f}). "
            f"Consider holding your stock for better returns."
        )
    elif change_pct < PRICE_FALL_THRESHOLD:
        primary_action = "Sell Today"
        action_icon = "📉"
        action_detail = (
            f"Prices are expected to fall by {abs(change_pct):.1f}% "
            f"(₹{current_price:.0f} → ₹{predicted_price:.0f}). "
            f"Selling now would lock in the current higher price."
        )
    elif predicted_price < msp and msp > 0:
        primary_action = "Sell via Government Procurement"
        action_icon = "🏛️"
        action_detail = (
            f"Predicted price ₹{predicted_price:.0f} is below MSP ₹{msp}. "
            f"Register with NAFED/FCI procurement centers for guaranteed MSP."
        )
    else:
        primary_action = "Monitor Market"
        action_icon = "👁️"
        action_detail = (
            f"Prices are relatively stable (expected change: {change_pct:+.1f}%). "
            f"No urgent action needed — continue monitoring."
        )

    # --- Volatility assessment ---
    volatility_cv, volatility_level = 0.0, "unknown"
    if history_prices is not None and len(history_prices) >= 3:
        volatility_cv, volatility_level = _assess_volatility(history_prices)

    # --- Trend analysis ---
    trend_pct, trend_direction = 0.0, "unknown"
    if history_prices is not None and len(history_prices) >= 4:
        trend_pct, trend_direction = _compute_trend(history_prices)

    # --- Risk assessment ---
    risk_factors = []
    if volatility_level == "high":
        risk_factors.append("High price volatility in recent months")
    if predicted_price < msp and msp > 0:
        risk_factors.append("Predicted price below MSP")
    if confidence is not None and confidence < 40:
        risk_factors.append("Low prediction confidence — models disagree")
    if forecast_path and len(forecast_path) > 3:
        late_change = (forecast_path[-1] - forecast_path[0]) / max(forecast_path[0], 1) * 100
        if abs(late_change) > 15:
            risk_factors.append("High uncertainty in longer-term forecast")

    if len(risk_factors) >= 2:
        risk_level = "high"
    elif len(risk_factors) == 1:
        risk_level = "medium"
    else:
        risk_level = "low"

    # --- Seasonality note ---
    season_note = None
    if current_month is not None and crop in HARVEST_MONTHS:
        harvest = HARVEST_MONTHS[crop]
        if current_month in harvest:
            season_note = (
                f"This is harvest season for {crop}. Supply is typically high, "
                f"which can depress prices. Consider storage if feasible."
            )
        months_to_harvest = min(
            (h - current_month) % 12 for h in harvest
        )
        if 1 <= months_to_harvest <= 2:
            season_note = (
                f"Harvest season is approaching ({months_to_harvest} month{'s' if months_to_harvest > 1 else ''} away). "
                f"Prices may dip as new supply enters the market."
            )

    # --- Wait recommendation ---
    wait_days = None
    if forecast_path and len(forecast_path) >= 2:
        # Find the peak in forecast path
        peak_idx = int(np.argmax(forecast_path))
        if peak_idx > 0 and forecast_path[peak_idx] > current_price * 1.03:
            wait_days = (peak_idx + 1) * 30  # months to days approximation
            wait_note = (
                f"Prices may peak in approximately {peak_idx + 1} month(s) "
                f"at ₹{forecast_path[peak_idx]:.0f}."
            )
        else:
            wait_note = None
    else:
        wait_note = None

    return {
        "primary_action": primary_action,
        "action_icon": action_icon,
        "action_detail": action_detail,
        "price_change_pct": round(change_pct, 2),
        "trend_direction": trend_direction,
        "trend_pct": round(trend_pct, 2),
        "volatility_level": volatility_level,
        "volatility_cv": round(volatility_cv, 4),
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "season_note": season_note,
        "wait_recommendation": wait_note,
        "wait_days": wait_days,
        "msp": msp,
        "confidence": confidence,
    }
