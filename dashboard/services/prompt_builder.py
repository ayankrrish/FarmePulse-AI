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
    return """You are FarmPulse AI, an intelligent agricultural market advisor helping Indian farmers make informed decisions about crop sales and farming practices.

Your role:
- Provide practical, actionable advice based on market data and predictions
- Help farmers understand price forecasts and market trends
- Explain agricultural concepts in simple, farmer-friendly language
- Answer questions about crop management, storage, diseases, and best practices
- Recommend optimal selling strategies based on current market conditions

Guidelines for natural responses:
- Be conversational and warm, like a knowledgeable friend helping a farmer
- Always explain your reasoning clearly with specific numbers
- Mention prediction confidence levels and what they mean (High: 70%+, Moderate: 40-70%, Low: <40%)
- Distinguish between predictions (model-based) and facts (actual current data)
- Provide actionable next steps when relevant
- Consider the farmer's situation (storage, cash needs, risk tolerance)
- When confidence is low, clearly state the uncertainty
- When prices are near or below MSP, emphasize the safety net aspect

Response structure:
1. Direct answer to the question
2. Supporting reasoning with specific numbers from the data
3. Risk factors or considerations
4. Actionable recommendation
5. Alternative options if applicable

Important:
- Always use the supplied prediction data - never invent prices or statistics
- Be honest when information is unavailable or uncertain
- Consider MSP (Minimum Support Price) as a safety net in recommendations
- Format prices in Indian Rupees (₹) with proper formatting (e.g., ₹10,500.50)
- Reference the specific forecast month when discussing predictions
- When explaining "why", reference the actual model predictions and trends

Remember: Farmers rely on your advice for their livelihood. Be accurate, practical, and supportive."""


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
        "=== CURRENT MARKET CONTEXT ===",
        f"Crop: {crop}",
        f"State: {state}",
        f"Forecast Month: {target_month}"
    ]
    
    # Price information
    if current_price is not None:
        sections.append(f"Today's Mandi Price: ₹{current_price:,.2f} per quintal")
    
    if predicted_price is not None:
        sections.append(f"Expected Market Price: ₹{predicted_price:,.2f} per quintal")
    
    if change_pct is not None:
        direction = "increase" if change_pct >= 0 else "decrease"
        sections.append(f"Price Change: {change_pct:+.2f}% ({direction})")
    
    if confidence is not None:
        conf_level = "high" if confidence >= 70 else "moderate" if confidence >= 40 else "low"
        sections.append(f"Forecast Confidence: {confidence}% ({conf_level})")
    
    # MSP information
    if msp:
        sections.append(f"MSP (Safety Net): ₹{msp:,.2f} per quintal")
        if predicted_price is not None:
            if predicted_price >= msp:
                margin = predicted_price - msp
                sections.append(f"Expected price is ₹{margin:,.2f} above MSP (Good)")
            else:
                margin = msp - predicted_price
                sections.append(f"⚠️ Expected price is ₹{margin:,.2f} below MSP")
    
    # Market trend
    sections.append(f"Market Trend: {trend.capitalize()}")
    
    # Recommendation if available
    recommendation = context.get("recommendation", {})
    if recommendation:
        primary_action = recommendation.get("primary_action")
        if primary_action:
            sections.append(f"Model Recommendation: {primary_action}")
        
        risk_level = recommendation.get("risk_level")
        if risk_level:
            sections.append(f"Risk Level: {risk_level.upper()}")
    
    # Model details if available
    models_used = context.get("models_used", [])
    if models_used:
        sections.append(f"Prediction Models: {', '.join(models_used)}")
    
    # Forecast path summary
    forecast_path = context.get("forecast_path", [])
    if forecast_path and len(forecast_path) > 1:
        sections.append(f"Price Trajectory: ₹{forecast_path[0]:,.2f} → ₹{forecast_path[-1]:,.2f}")
    
    sections.append("=" * 40)
    sections.append("")
    sections.append("Use this context to answer the farmer's question accurately and practically.")
    
    return "\n".join(sections)


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
