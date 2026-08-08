"""
FarmPulse AI — Intent Detection Service
Classifies user questions and routes to appropriate data sources.
"""

import logging
import re

logger = logging.getLogger(__name__)


class Intent:
    """User intent types"""
    WEATHER = 'weather'
    MARKET_PRICE = 'market_price'
    PRICE_FORECAST = 'price_forecast'
    MSP = 'msp'
    SELLING_DECISION = 'selling_decision'
    PROFIT = 'profit'
    SPRAYING = 'spraying'
    IRRIGATION = 'irrigation'
    HARVESTING = 'harvesting'
    DISEASE = 'disease'
    FARMING_GENERAL = 'farming_general'
    COMPARISON = 'comparison'
    FOLLOW_UP = 'follow_up'
    UNKNOWN = 'unknown'


def detect_intent(question, conversation_context=None):
    """
    Detect the primary intent of a user question.
    
    Args:
        question: User's question text
        conversation_context: Previous conversation context (optional)
        
    Returns:
        dict with 'intent', 'confidence', 'requires_weather', 'requires_market'
    """
    question_lower = question.lower()
    
    # Weather intent patterns
    weather_keywords = [
        'weather', 'temperature', 'temp', 'rain', 'raining', 'rainfall',
        'humidity', 'wind', 'cloudy', 'sunny', 'forecast', 'climate',
        'hot', 'cold', 'warm', 'cool', 'wet', 'dry'
    ]
    
    # Spraying intent patterns
    spraying_keywords = ['spray', 'spraying', 'pesticide', 'insecticide', 'fungicide']
    
    # Irrigation intent patterns
    irrigation_keywords = ['irrigate', 'irrigation', 'water', 'watering']
    
    # Harvesting intent patterns
    harvesting_keywords = ['harvest', 'harvesting', 'reap', 'reaping', 'cutting']
    
    # Market/price intent patterns
    price_keywords = ['price', 'cost', 'rate', 'value', 'worth', 'mandi']
    
    # MSP intent patterns
    msp_keywords = ['msp', 'minimum support price', 'support price']
    
    # Selling decision patterns
    selling_keywords = ['sell', 'selling', 'should i sell', 'wait', 'hold']
    
    # Profit patterns
    profit_keywords = ['profit', 'earn', 'earning', 'income', 'revenue']
    
    # Comparison patterns
    comparison_keywords = ['compare', 'comparison', 'versus', 'vs', 'better', 'best', 'which']
    
    # Disease/farming patterns
    disease_keywords = ['disease', 'pest', 'fungus', 'infection', 'symptom']
    
    # Follow-up patterns
    followup_patterns = [
        r'^what about',
        r'^how about',
        r'^and\s+\w+',
        r'^tomorrow',
        r'^next',
        r'^that',
        r'^there$'
    ]
    
    # Check for follow-up first
    for pattern in followup_patterns:
        if re.search(pattern, question_lower):
            return {
                'intent': Intent.FOLLOW_UP,
                'confidence': 0.9,
                'requires_weather': conversation_context and 'weather' in str(conversation_context),
                'requires_market': conversation_context and 'market' in str(conversation_context)
            }
    
    # Weather-specific agricultural questions
    if any(keyword in question_lower for keyword in spraying_keywords):
        return {
            'intent': Intent.SPRAYING,
            'confidence': 0.95,
            'requires_weather': True,
            'requires_market': False
        }
    
    if any(keyword in question_lower for keyword in irrigation_keywords):
        return {
            'intent': Intent.IRRIGATION,
            'confidence': 0.95,
            'requires_weather': True,
            'requires_market': False
        }
    
    if any(keyword in question_lower for keyword in harvesting_keywords):
        # Harvesting can benefit from both weather and market data
        return {
            'intent': Intent.HARVESTING,
            'confidence': 0.9,
            'requires_weather': True,
            'requires_market': 'sell' in question_lower or 'price' in question_lower
        }
    
    # Pure weather questions
    if any(keyword in question_lower for keyword in weather_keywords):
        return {
            'intent': Intent.WEATHER,
            'confidence': 0.9,
            'requires_weather': True,
            'requires_market': False
        }
    
    # MSP questions
    if any(keyword in question_lower for keyword in msp_keywords):
        return {
            'intent': Intent.MSP,
            'confidence': 0.95,
            'requires_weather': False,
            'requires_market': True
        }
    
    # Selling decisions
    if any(keyword in question_lower for keyword in selling_keywords):
        # Selling decisions benefit from both weather and market
        return {
            'intent': Intent.SELLING_DECISION,
            'confidence': 0.85,
            'requires_weather': True,
            'requires_market': True
        }
    
    # Profit questions
    if any(keyword in question_lower for keyword in profit_keywords):
        return {
            'intent': Intent.PROFIT,
            'confidence': 0.9,
            'requires_weather': False,
            'requires_market': True
        }
    
    # Comparison questions
    if any(keyword in question_lower for keyword in comparison_keywords):
        return {
            'intent': Intent.COMPARISON,
            'confidence': 0.85,
            'requires_weather': any(w in question_lower for w in weather_keywords),
            'requires_market': any(p in question_lower for p in price_keywords)
        }
    
    # Price/market questions
    if any(keyword in question_lower for keyword in price_keywords):
        if 'forecast' in question_lower or 'predict' in question_lower or 'future' in question_lower:
            return {
                'intent': Intent.PRICE_FORECAST,
                'confidence': 0.9,
                'requires_weather': False,
                'requires_market': True
            }
        return {
            'intent': Intent.MARKET_PRICE,
            'confidence': 0.85,
            'requires_weather': False,
            'requires_market': True
        }
    
    # Disease questions
    if any(keyword in question_lower for keyword in disease_keywords):
        return {
            'intent': Intent.DISEASE,
            'confidence': 0.9,
            'requires_weather': True,  # Weather affects disease
            'requires_market': False
        }
    
    # General farming (default for agricultural questions)
    farming_keywords = ['crop', 'farm', 'field', 'soil', 'fertilizer', 'seed']
    if any(keyword in question_lower for keyword in farming_keywords):
        return {
            'intent': Intent.FARMING_GENERAL,
            'confidence': 0.7,
            'requires_weather': False,
            'requires_market': False
        }
    
    # Unknown intent
    return {
        'intent': Intent.UNKNOWN,
        'confidence': 0.5,
        'requires_weather': False,
        'requires_market': False
    }


def requires_location_specific_weather(intent_result):
    """
    Check if the intent requires location-specific weather data.
    
    Args:
        intent_result: Result from detect_intent()
        
    Returns:
        bool
    """
    return intent_result.get('requires_weather', False)
