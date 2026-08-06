"""
FarmPulse AI — Market Comparison Service
Compares predicted prices across states for the same crop.
Identifies best/worst markets, price spreads, and trend differences.
"""

import logging

logger = logging.getLogger(__name__)


def compare_markets(crop, state_predictions):
    """
    Compare predictions across multiple states for a given crop.

    Args:
        crop: Crop name
        state_predictions: dict of {
            state_name: {
                "current_price": float,
                "predicted_price": float,
                "change_pct": float,
                "method_used": str,
            }
        }

    Returns:
        dict with ranked markets, best/worst, spread analysis
    """
    if not state_predictions:
        return {"error": "No market data available", "markets": []}

    markets = []
    for state, data in state_predictions.items():
        current = data.get("current_price", 0)
        predicted = data.get("predicted_price", 0)
        change_pct = data.get("change_pct", 0)

        markets.append({
            "state": state,
            "current_price": round(current, 2),
            "predicted_price": round(predicted, 2),
            "change_pct": round(change_pct, 2),
            "method_used": data.get("method_used", "Unknown"),
            "trend": (
                "rising" if change_pct > 2
                else "falling" if change_pct < -2
                else "stable"
            ),
        })

    # Sort by predicted price (highest first = best market to sell)
    markets.sort(key=lambda x: x["predicted_price"], reverse=True)

    # Add rank
    for i, m in enumerate(markets):
        m["rank"] = i + 1

    best = markets[0] if markets else None
    worst = markets[-1] if markets else None

    # Price spread analysis
    predicted_prices = [m["predicted_price"] for m in markets]
    current_prices = [m["current_price"] for m in markets]

    spread = max(predicted_prices) - min(predicted_prices) if predicted_prices else 0
    avg_predicted = sum(predicted_prices) / len(predicted_prices) if predicted_prices else 0
    avg_current = sum(current_prices) / len(current_prices) if current_prices else 0

    return {
        "crop": crop,
        "markets": markets,
        "best_market": {
            "state": best["state"],
            "predicted_price": best["predicted_price"],
            "advantage": round(best["predicted_price"] - avg_predicted, 2),
        } if best else None,
        "worst_market": {
            "state": worst["state"],
            "predicted_price": worst["predicted_price"],
            "disadvantage": round(avg_predicted - worst["predicted_price"], 2),
        } if worst else None,
        "price_spread": round(spread, 2),
        "avg_predicted_price": round(avg_predicted, 2),
        "avg_current_price": round(avg_current, 2),
        "overall_trend": (
            "rising" if avg_predicted > avg_current * 1.02
            else "falling" if avg_predicted < avg_current * 0.98
            else "stable"
        ),
        "num_markets": len(markets),
    }
