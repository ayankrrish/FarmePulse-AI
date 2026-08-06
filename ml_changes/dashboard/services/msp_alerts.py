"""
FarmPulse AI — MSP Alert System
Three-tier alert based on predicted price vs Minimum Support Price.
  Green  → Price ≥ 110% of MSP (comfortable margin)
  Yellow → Price between 100%–110% of MSP (caution zone)
  Red    → Price < 100% of MSP (below MSP)
"""

import logging
from config import MSP_TABLE, MSP_ALERT_GREEN_THRESHOLD, MSP_ALERT_YELLOW_THRESHOLD

logger = logging.getLogger(__name__)


def get_msp_alert(crop, predicted_price, current_price=None):
    """
    Generate an MSP alert for a given crop and predicted price.

    Args:
        crop: Crop name (e.g. "Chana")
        predicted_price: Predicted price in Rs/quintal
        current_price: Optional current price for comparison

    Returns:
        dict with alert_level, color, message, recommendation, and details
    """
    msp = MSP_TABLE.get(crop)
    if msp is None:
        return {
            "alert_level": "unknown",
            "color": "#888888",
            "message": f"MSP data not available for {crop}",
            "recommendation": "Check official MSP notifications",
            "msp": None,
        }

    ratio = predicted_price / msp
    diff = predicted_price - msp
    diff_pct = (diff / msp) * 100

    if ratio >= MSP_ALERT_GREEN_THRESHOLD:
        alert_level = "green"
        color = "#10B981"
        icon = "✅"
        message = f"Above MSP by ₹{diff:.0f} ({diff_pct:+.1f}%)"
        recommendation = (
            "Price is well above MSP. Sell in open market for maximum returns. "
            "No need for government procurement channels."
        )
    elif ratio >= MSP_ALERT_YELLOW_THRESHOLD:
        alert_level = "yellow"
        color = "#F59E0B"
        icon = "⚠️"
        message = f"Near MSP — only ₹{diff:.0f} above ({diff_pct:+.1f}%)"
        recommendation = (
            "Price is close to MSP. Monitor market closely. "
            "Consider registering at the nearest government procurement center as a backup. "
            "Small price dips could push you below MSP."
        )
    else:
        alert_level = "red"
        color = "#EF4444"
        icon = "🔴"
        message = f"Below MSP by ₹{abs(diff):.0f} ({diff_pct:+.1f}%)"
        recommendation = (
            "Predicted price is below MSP. Strongly consider selling through "
            "government procurement channels (e.g., NAFED, FCI) to get guaranteed MSP. "
            "Avoid selling in open market at current rates."
        )

    result = {
        "alert_level": alert_level,
        "color": color,
        "icon": icon,
        "message": message,
        "recommendation": recommendation,
        "msp": msp,
        "predicted_price": round(predicted_price, 2),
        "difference": round(diff, 2),
        "difference_pct": round(diff_pct, 2),
        "ratio": round(ratio, 4),
    }

    # Add current price context if available
    if current_price is not None:
        current_diff = current_price - msp
        current_ratio = current_price / msp
        if current_ratio >= MSP_ALERT_GREEN_THRESHOLD:
            current_level = "green"
        elif current_ratio >= MSP_ALERT_YELLOW_THRESHOLD:
            current_level = "yellow"
        else:
            current_level = "red"

        result["current_price"] = round(current_price, 2)
        result["current_msp_difference"] = round(current_diff, 2)
        result["current_alert_level"] = current_level
        result["trend"] = (
            "improving" if alert_level == "green" and current_level != "green"
            else "worsening" if alert_level == "red" and current_level != "red"
            else "stable"
        )

    return result


def get_all_crop_alerts(predictions):
    """
    Generate MSP alerts for multiple crops at once.

    Args:
        predictions: dict of {crop: {"predicted_price": ..., "current_price": ...}}

    Returns:
        dict of {crop: alert_dict}
    """
    alerts = {}
    for crop, data in predictions.items():
        alerts[crop] = get_msp_alert(
            crop,
            data.get("predicted_price", 0),
            data.get("current_price"),
        )
    return alerts
