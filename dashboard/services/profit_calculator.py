"""
FarmPulse AI — Profit Calculator
Detailed profit estimation with current vs. predicted comparison.
"""

import logging
from config import MSP_TABLE

logger = logging.getLogger(__name__)


def calculate_profit(
    crop,
    quantity_quintals,
    current_price,
    predicted_price,
    cost_per_quintal=None,
):
    """
    Calculate detailed profit estimates.

    Args:
        crop: Crop name
        quantity_quintals: Quantity in quintals
        current_price: Current market price Rs/quintal
        predicted_price: Predicted price Rs/quintal
        cost_per_quintal: Optional production cost Rs/quintal

    Returns:
        dict with revenue, profit, comparison, break-even analysis
    """
    msp = MSP_TABLE.get(crop, 0)

    # Revenue calculations
    current_revenue = current_price * quantity_quintals
    predicted_revenue = predicted_price * quantity_quintals
    msp_revenue = msp * quantity_quintals if msp else 0

    revenue_difference = predicted_revenue - current_revenue
    revenue_difference_pct = (
        (revenue_difference / max(current_revenue, 1)) * 100
    )

    result = {
        "crop": crop,
        "quantity_quintals": quantity_quintals,
        "current_price": round(current_price, 2),
        "predicted_price": round(predicted_price, 2),
        "msp": msp,
        # Revenue
        "current_revenue": round(current_revenue, 2),
        "predicted_revenue": round(predicted_revenue, 2),
        "msp_revenue": round(msp_revenue, 2),
        "revenue_difference": round(revenue_difference, 2),
        "revenue_difference_pct": round(revenue_difference_pct, 2),
        # Best option
        "best_option": "predicted" if predicted_revenue >= current_revenue else "current",
        "best_revenue": round(max(current_revenue, predicted_revenue, msp_revenue), 2),
    }

    # If production cost is provided, calculate actual profit
    if cost_per_quintal is not None and cost_per_quintal > 0:
        total_cost = cost_per_quintal * quantity_quintals
        current_profit = current_revenue - total_cost
        predicted_profit = predicted_revenue - total_cost
        msp_profit = msp_revenue - total_cost if msp else 0

        current_margin = (current_profit / max(current_revenue, 1)) * 100
        predicted_margin = (predicted_profit / max(predicted_revenue, 1)) * 100

        # Break-even quantity
        break_even_current = (
            total_cost / max(current_price, 1) if current_price > 0 else 0
        )
        break_even_predicted = (
            total_cost / max(predicted_price, 1) if predicted_price > 0 else 0
        )

        result.update({
            "cost_per_quintal": round(cost_per_quintal, 2),
            "total_cost": round(total_cost, 2),
            "current_profit": round(current_profit, 2),
            "predicted_profit": round(predicted_profit, 2),
            "msp_profit": round(msp_profit, 2),
            "current_margin_pct": round(current_margin, 2),
            "predicted_margin_pct": round(predicted_margin, 2),
            "profit_difference": round(predicted_profit - current_profit, 2),
            "break_even_quantity_current": round(break_even_current, 2),
            "break_even_quantity_predicted": round(break_even_predicted, 2),
        })

        # Recommendation based on profitability
        if predicted_profit > current_profit and predicted_profit > 0:
            result["profit_recommendation"] = (
                f"Waiting could increase profit by ₹{abs(predicted_profit - current_profit):,.0f}"
            )
        elif current_profit > predicted_profit and current_profit > 0:
            result["profit_recommendation"] = (
                f"Selling now is better — saves ₹{abs(current_profit - predicted_profit):,.0f} "
                f"vs waiting"
            )
        elif msp_profit > max(current_profit, predicted_profit):
            result["profit_recommendation"] = (
                f"MSP route gives the best return at ₹{msp_profit:,.0f}"
            )
        else:
            result["profit_recommendation"] = "Returns are marginal — consider all options"
    else:
        result["profit_recommendation"] = (
            "Enter production cost for detailed profit analysis"
        )

    return result
