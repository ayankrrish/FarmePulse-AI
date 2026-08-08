"""
FarmPulse AI - Prompt Builder Service
Constructs context-aware prompts for the AI assistant using current application state.
"""

from typing import Dict, Optional, List
from datetime import datetime


def build_system_prompt() -> str:
    """
    Build the system prompt that defines the AI assistant's role and behavior.
    
    Returns:
        System prompt string
    """
    return """You are FarmPulse AI, a concise Farm Decision Assistant helping Indian farmers make smart decisions.

RESPONSE STYLE - VERY IMPORTANT:
- Be CONCISE and direct. Short answers only (2-5 sentences for most questions).
- Use simple, farmer-friendly language. Avoid jargon.
- Use Markdown formatting: **bold** for emphasis, bullet points for lists.
- Start with the answer, then briefly explain why.

RESPONSE LENGTH GUIDE:
- Simple factual questions: 1-2 sentences
- Decision questions (Should I sell/spray/harvest?): 3-5 sentences
- Explanations: Short bullets, not paragraphs
- Only give detailed answers if explicitly asked ("explain in detail")

RESPONSE FORMAT for recommendations:
**Recommendation:** [Action]
**Why:** [Brief reason with key data]
**Action:** [What to do next]

Example:
**Recommendation:** Wait to sell.
**Why:** Price is rising (₹2,450 → ₹2,680, +9.4%).
**Action:** Recheck market tomorrow.

RESPONSE FORMAT for price questions:
When answering "what would be the price" or "predicted price" questions:
- State the predicted price
- State the current price  
- State the expected change percentage
- State the MSP (if provided in context)
- Keep it concise (3-5 short lines)

Example:
**Predicted Price:** ₹11,815/quintal
**Current Price:** ₹9,633/quintal
**Change:** +22.7%
**MSP:** ₹8,682/quintal

DATA AVAILABILITY - CRITICAL:
- **Weather data** is available for ANY Indian location when provided in the context
- **Market data** (prices, predictions) is only available for specific crops and states
- These are INDEPENDENT - a location may have weather but no market data, or vice versa
- If asked about weather for any location and weather data is provided, use it
- If asked about market data for a location without market coverage, clearly state: "Market data is not available for that location"
- NEVER substitute data from one location into another location
- NEVER say a location is "invalid" just because market data is unavailable there

CONTEXT AWARENESS:
- Use the provided dashboard data (prices, MSP, trend) when available
- Use the provided weather data (temp, rain, wind, humidity, forecast) when available
- Use GPS location when available
- Never repeat information the user already knows from the dashboard
- Reference specific numbers from the data
- If weather context shows a specific location, that's the location for the weather answer

WEATHER-AWARE DECISIONS:
When answering weather-related questions, combine:
- Current weather conditions
- Hourly/daily forecast
- Agricultural metrics (soil, VPD, ET when available)
- Weather advisory if provided
- Crop context and market conditions (if available)

FARMING ADVICE:
- **Spraying:** Check rain probability, wind speed, temperature, humidity
  - Don't spray if rain >30%, wind >15 km/h, or extreme temperature
- **Harvest:** Check rain forecast, wind, temperature, crop readiness
  - Avoid if rain expected or high humidity
- **Irrigation:** Check soil moisture, rain forecast, ET, temperature
  - Skip if rain >50% or soil moisture already high
- **Disease Risk:** Check humidity, rain, temperature patterns
  - High risk when humidity >80% + warm temperature + rain

IMPORTANT RULES:
- NEVER invent prices, weather data, or statistics
- If weather data is missing, say: "I don't have weather data for that location"
- If market data is missing, say: "Market data is not available for that state/crop"
- Always use ₹ symbol for prices (e.g., ₹2,450/quintal)
- **For market price questions, ALWAYS mention the MSP when provided in context**
- When confidence is low (<40%), mention uncertainty
- Consider MSP as safety net in selling decisions
- Be action-oriented - end with clear next steps
- Use the exact location mentioned in the weather context when answering weather questions
- **Use ONLY the numerical values provided in the context - never calculate or estimate prices/MSP yourself**

Remember: Farmers need quick, clear advice they can act on immediately."""


def build_context_prompt(context: Dict) -> str:
    """
    Build the context prompt from current application state.
    
    Args:
        context: Dictionary containing prediction context
        
    Returns:
        Context prompt string
    """
    # Check if this is a comparison context
    if context.get("is_comparison"):
        return _build_comparison_prompt(context)
    
    crop = context.get("crop", "Unknown")
    state = context.get("state", "Unknown")
    current_price = context.get("current_price")
    predicted_price = context.get("predicted_price")
    change_pct = context.get("change_pct")
    confidence = context.get("confidence")
    msp = context.get("msp")
    trend = context.get("trend", "stable")
    target_month = context.get("target_month", "next month")
    
    # Build context sections
    sections = [
        "=== MARKET CONTEXT ===",
        f"Crop: {crop}",
        f"Location: {state}",
        f"Forecast: {target_month}"
    ]
    
    # Price information
    if current_price is not None:
        sections.append(f"Current Price: ₹{current_price:,.2f}/quintal")
    
    if predicted_price is not None:
        sections.append(f"Predicted Price: ₹{predicted_price:,.2f}/quintal")
    
    if change_pct is not None:
        direction = "↑" if change_pct >= 0 else "↓"
        sections.append(f"Change: {direction} {abs(change_pct):.1f}%")
    
    if confidence is not None:
        conf_level = "High" if confidence >= 70 else "Medium" if confidence >= 40 else "Low"
        sections.append(f"Confidence: {conf_level} ({confidence}%)")
    
    # MSP information
    if msp:
        sections.append(f"MSP: ₹{msp:,.2f}/quintal")
        if predicted_price is not None:
            if predicted_price >= msp:
                margin = predicted_price - msp
                sections.append(f"  ✓ ₹{margin:,.0f} above MSP")
            else:
                margin = msp - predicted_price
                sections.append(f"  ⚠ ₹{margin:,.0f} below MSP")
    
    # Trend
    sections.append(f"Trend: {trend.capitalize()}")
    
    # Recommendation if available
    recommendation = context.get("recommendation", {})
    if recommendation:
        primary_action = recommendation.get("primary_action")
        if primary_action:
            sections.append(f"Recommendation: {primary_action}")
        
        risk_level = recommendation.get("risk_level")
        if risk_level:
            sections.append(f"Risk: {risk_level.upper()}")
    
    # Add weather context if available
    weather = context.get("weather")
    if weather:
        sections.append("")
        sections.append("=== WEATHER CONTEXT ===")
        sections.extend(_build_weather_section(weather))
    
    # Add GPS location if available
    gps = context.get("gps")
    if gps and gps.get("city"):
        sections.append(f"GPS Location: {gps['city']}, {gps.get('district', '')} (±{gps.get('accuracy', 0)}m)")
    
    sections.append("=" * 40)
    
    return "\n".join(sections)


def _build_weather_section(weather: Dict) -> List[str]:
    """
    Build weather context section.
    
    Args:
        weather: Weather data dictionary
        
    Returns:
        List of weather context lines
    """
    lines = []
    
    current = weather.get("current", {})
    today = weather.get("today", {})
    location = weather.get("location", {})
    agriculture = weather.get("agriculture", {})
    advisory = weather.get("advisory")
    
    # Location
    if location.get("city"):
        lines.append(f"Location: {location['city']}, {location.get('state', '')}")
    
    # Current conditions
    if current.get("temperature") is not None:
        temp = current["temperature"]
        feels = current.get("feels_like", temp)
        lines.append(f"Temperature: {temp}°C (feels {feels}°C)")
    
    if current.get("humidity") is not None:
        lines.append(f"Humidity: {current['humidity']}%")
    
    if current.get("wind_speed") is not None:
        wind = current["wind_speed"]
        lines.append(f"Wind: {wind} km/h")
    
    # Rain probability
    if today.get("precipitation_probability") is not None:
        rain_prob = today["precipitation_probability"]
        lines.append(f"Rain Probability: {rain_prob}%")
    
    if today.get("precipitation") is not None and today["precipitation"] > 0:
        lines.append(f"Expected Rain: {today['precipitation']} mm")
    
    # UV Index
    if current.get("uv_index") is not None:
        uv = current["uv_index"]
        uv_level = "Extreme" if uv > 10 else "High" if uv > 7 else "Moderate" if uv > 5 else "Low"
        lines.append(f"UV Index: {uv} ({uv_level})")
    
    # Agricultural metrics
    if agriculture:
        if agriculture.get("soil_temperature") is not None:
            lines.append(f"Soil Temp: {agriculture['soil_temperature']:.1f}°C")
        
        if agriculture.get("soil_moisture") is not None:
            sm = agriculture["soil_moisture"]
            sm_status = "Dry" if sm < 0.15 else "Wet" if sm > 0.35 else "Optimal"
            lines.append(f"Soil Moisture: {sm_status} ({sm:.2f})")
        
        if agriculture.get("vapour_pressure_deficit") is not None:
            vpd = agriculture["vapour_pressure_deficit"]
            vpd_status = "High stress" if vpd > 2.5 else "Low stress" if vpd < 0.5 else "Optimal"
            lines.append(f"VPD: {vpd:.2f} kPa ({vpd_status})")
    
    # Hourly forecast summary (next 12 hours)
    hourly = weather.get("hourly", [])
    if hourly and len(hourly) >= 12:
        next_12h_rain = [h.get("precipitation_probability", 0) for h in hourly[:12]]
        if next_12h_rain:
            max_rain_12h = max(next_12h_rain)
            if max_rain_12h > 30:
                lines.append(f"Next 12h: {max_rain_12h}% rain probability")
    
    # Daily forecast summary (tomorrow)
    daily = weather.get("daily", [])
    if daily and len(daily) >= 2:
        tomorrow = daily[1]
        tomorrow_rain = tomorrow.get("precipitation_probability", 0)
        if tomorrow_rain > 30:
            lines.append(f"Tomorrow: {tomorrow_rain}% rain probability")
    
    # Weather advisory if available
    if advisory:
        lines.append(f"Advisory: {advisory[:150]}")  # First 150 chars
    
    return lines


def _build_comparison_prompt(context: Dict) -> str:
    """
    Build comparison context prompt for multiple crops/states.
    
    Args:
        context: Dictionary containing comparison data
        
    Returns:
        Comparison context prompt string
    """
    sections = [
        "=== MARKET COMPARISON CONTEXT ===",
        ""
    ]
    
    comparison_items = context.get("comparison", [])
    
    for i, item in enumerate(comparison_items, 1):
        sections.append(f"Option {i}: {item['crop']} in {item['state']}")
        sections.append(f"  Current Price: ₹{item['current_price']:,.2f}")
        sections.append(f"  Predicted Price: ₹{item['predicted_price']:,.2f}")
        sections.append(f"  Change: {item['change_pct']:+.2f}%")
        sections.append(f"  Confidence: {item['confidence']}%")
        sections.append(f"  MSP: ₹{item['msp']:,.2f}")
        sections.append(f"  Trend: {item['trend'].capitalize()}")
        
        rec = item.get("recommendation", {})
        if rec and rec.get("primary_action"):
            sections.append(f"  Recommendation: {rec['primary_action']}")
        
        sections.append("")
    
    sections.append("=" * 40)
    sections.append("Compare these options and provide clear analysis to help the farmer decide.")
    
    return "\n".join(sections)


def build_full_prompt(
    user_question: str,
    context: Dict,
    include_general_knowledge: bool = True
) -> tuple[str, str]:
    """
    Build complete system and user prompts for the AI.
    
    Args:
        user_question: The farmer's question
        context: Application context dictionary
        include_general_knowledge: Whether to allow general farming questions
        
    Returns:
        Tuple of (system_prompt, user_prompt_with_context)
    """
    system_prompt = build_system_prompt()
    
    # Build context section
    context_section = build_context_prompt(context)
    
    # Build user prompt with context
    if include_general_knowledge:
        user_prompt = f"{context_section}\n\nFarmer's Question: {user_question}"
    else:
        user_prompt = f"{context_section}\n\nFarmer's Question: {user_question}\n\nNote: Please answer based only on the provided context data."
    
    return system_prompt, user_prompt


def format_conversation_history(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Format conversation history for API consumption.
    
    Args:
        messages: List of message dicts with 'role' and 'text' keys
        
    Returns:
        Formatted messages list with 'role' and 'content' keys
    """
    formatted = []
    for msg in messages:
        role = msg.get("role", "user")
        text = msg.get("text", "")
        
        if role in ["user", "assistant"] and text:
            formatted.append({
                "role": role,
                "content": text
            })
    
    return formatted


def summarize_context_for_history(context: Dict) -> str:
    """
    Create a brief context summary for conversation history.
    Used to remind the AI of context in multi-turn conversations.
    
    Args:
        context: Application context dictionary
        
    Returns:
        Brief context summary string
    """
    crop = context.get("crop", "Unknown")
    state = context.get("state", "Unknown")
    predicted_price = context.get("predicted_price")
    change_pct = context.get("change_pct")
    
    summary_parts = [f"{crop} in {state}"]
    
    if predicted_price is not None:
        summary_parts.append(f"predicted at ₹{predicted_price:,.2f}")
    
    if change_pct is not None:
        summary_parts.append(f"({change_pct:+.1f}%)")
    
    return " - ".join(summary_parts)


def validate_context(context: Dict) -> bool:
    """
    Validate that essential context fields are present.
    
    Args:
        context: Context dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["crop", "state"]
    return all(field in context and context[field] for field in required_fields)


def sanitize_user_input(user_input: str, max_length: int = 1000) -> str:
    """
    Sanitize and validate user input.
    
    Args:
        user_input: Raw user input string
        max_length: Maximum allowed length
        
    Returns:
        Sanitized input string
        
    Raises:
        ValueError: If input is invalid
    """
    if not user_input or not user_input.strip():
        raise ValueError("Question cannot be empty")
    
    sanitized = user_input.strip()
    
    if len(sanitized) > max_length:
        raise ValueError(f"Question too long (max {max_length} characters)")
    
    # Remove potential injection patterns (basic sanitization)
    # The API will handle more sophisticated filtering
    dangerous_patterns = ["<script", "javascript:", "onerror="]
    for pattern in dangerous_patterns:
        if pattern.lower() in sanitized.lower():
            raise ValueError("Invalid input detected")
    
    return sanitized
