"""
FarmPulse AI - Question Parser Service
Extracts crop, state, month, and year from natural language questions.
"""

import re
from datetime import datetime
from typing import Dict, Optional, List


# Crop name mappings (variations and common names)
CROP_MAPPINGS = {
    "tur": ["tur", "arhar", "pigeon pea", "red gram"],
    "chana": ["chana", "chickpea", "gram", "bengal gram"],
    "moong": ["moong", "mung", "green gram", "mung bean"],
}

# State name mappings
STATE_MAPPINGS = {
    "Karnataka": ["karnataka", "ka", "kar"],
    "Maharashtra": ["maharashtra", "mh", "maha"],
    "Madhya Pradesh": ["madhya pradesh", "mp", "madhya"],
    "Uttar Pradesh": ["uttar pradesh", "up", "uttar"],
    "Rajasthan": ["rajasthan", "raj", "rj"],
    "Gujarat": ["gujarat", "guj", "gj"],
    "Andhra Pradesh": ["andhra pradesh", "andhra", "ap"],
    "Telangana": ["telangana", "ts", "tg"],
    "Tamil Nadu": ["tamil nadu", "tn", "tamil"],
    "West Bengal": ["west bengal", "wb", "bengal"],
}

# Month name mappings
MONTH_MAPPINGS = {
    1: ["january", "jan"],
    2: ["february", "feb"],
    3: ["march", "mar"],
    4: ["april", "apr"],
    5: ["may"],
    6: ["june", "jun"],
    7: ["july", "jul"],
    8: ["august", "aug"],
    9: ["september", "sep", "sept"],
    10: ["october", "oct"],
    11: ["november", "nov"],
    12: ["december", "dec"],
}

# Relative time expressions
RELATIVE_TIME = {
    "next month": 1,
    "this month": 0,
    "current month": 0,
    "following month": 1,
    "upcoming month": 1,
}


def normalize_crop_name(crop_text: str) -> Optional[str]:
    """
    Normalize crop name to standard format.
    
    Args:
        crop_text: Raw crop name from question
        
    Returns:
        Normalized crop name (Tur, Chana, or Moong) or None
    """
    crop_lower = crop_text.lower().strip()
    
    for standard_name, variations in CROP_MAPPINGS.items():
        if crop_lower in variations:
            return standard_name.capitalize()
    
    return None


def normalize_state_name(state_text: str) -> Optional[str]:
    """
    Normalize state name to standard format.
    
    Args:
        state_text: Raw state name from question
        
    Returns:
        Normalized state name or None
    """
    state_lower = state_text.lower().strip()
    
    for standard_name, variations in STATE_MAPPINGS.items():
        if state_lower in variations:
            return standard_name
    
    return None


def extract_crop(question: str) -> Optional[str]:
    """
    Extract crop name from question.
    
    Args:
        question: User question
        
    Returns:
        Normalized crop name or None
    """
    question_lower = question.lower()
    
    # Check each crop mapping
    for standard_name, variations in CROP_MAPPINGS.items():
        for variation in variations:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(variation) + r'\b'
            if re.search(pattern, question_lower):
                return standard_name.capitalize()
    
    return None


def extract_state(question: str) -> Optional[str]:
    """
    Extract state name from question.
    
    Args:
        question: User question
        
    Returns:
        Normalized state name or None
    """
    question_lower = question.lower()
    
    # Check each state mapping
    for standard_name, variations in STATE_MAPPINGS.items():
        for variation in variations:
            pattern = r'\b' + re.escape(variation) + r'\b'
            if re.search(pattern, question_lower):
                return standard_name
    
    return None


def extract_month_year(question: str, current_date: Optional[datetime] = None) -> tuple[Optional[int], Optional[int]]:
    """
    Extract month and year from question.
    
    Args:
        question: User question
        current_date: Reference date (defaults to now)
        
    Returns:
        Tuple of (month, year) or (None, None)
    """
    if current_date is None:
        current_date = datetime.now()
    
    question_lower = question.lower()
    
    # Check for relative time expressions first
    for expression, offset in RELATIVE_TIME.items():
        if expression in question_lower:
            target_month = current_date.month + offset
            target_year = current_date.year
            
            # Handle month overflow
            if target_month > 12:
                target_month = target_month - 12
                target_year += 1
            elif target_month < 1:
                target_month = target_month + 12
                target_year -= 1
            
            return target_month, target_year
    
    # Extract explicit month names
    month = None
    for month_num, month_names in MONTH_MAPPINGS.items():
        for month_name in month_names:
            pattern = r'\b' + re.escape(month_name) + r'\b'
            if re.search(pattern, question_lower):
                month = month_num
                break
        if month:
            break
    
    # Extract year (look for 4-digit year)
    year_match = re.search(r'\b(20\d{2})\b', question)
    year = int(year_match.group(1)) if year_match else None
    
    # If month found but no year, use current year or next year based on month
    if month and not year:
        if month < current_date.month:
            year = current_date.year + 1
        else:
            year = current_date.year
    
    return month, year


def parse_question(question: str, fallback_crop: Optional[str] = None, 
                  fallback_state: Optional[str] = None,
                  fallback_month: Optional[int] = None,
                  fallback_year: Optional[int] = None) -> Dict:
    """
    Parse natural language question to extract parameters.
    
    Args:
        question: User question
        fallback_crop: Default crop if not found in question
        fallback_state: Default state if not found in question
        fallback_month: Default month if not found in question
        fallback_year: Default year if not found in question
        
    Returns:
        Dictionary with extracted parameters and flags indicating what was found
    """
    # Extract parameters from question
    extracted_crop = extract_crop(question)
    extracted_state = extract_state(question)
    extracted_month, extracted_year = extract_month_year(question)
    
    # Determine final values
    crop = extracted_crop if extracted_crop else fallback_crop
    state = extracted_state if extracted_state else fallback_state
    month = extracted_month if extracted_month else fallback_month
    year = extracted_year if extracted_year else fallback_year
    
    return {
        "crop": crop,
        "state": state,
        "month": month,
        "year": year,
        "extracted_crop": extracted_crop is not None,
        "extracted_state": extracted_state is not None,
        "extracted_month": extracted_month is not None,
        "extracted_year": extracted_year is not None,
        "has_any_extraction": any([
            extracted_crop is not None,
            extracted_state is not None,
            extracted_month is not None,
            extracted_year is not None
        ])
    }


def extract_comparison_requests(question: str) -> List[Dict]:
    """
    Detect if question asks for comparison between multiple crops/states.
    
    Args:
        question: User question
        
    Returns:
        List of parameter sets for comparison
    """
    question_lower = question.lower()
    
    # Check for comparison keywords
    comparison_keywords = ["compare", "versus", "vs", "or", "better than", "difference between"]
    has_comparison = any(keyword in question_lower for keyword in comparison_keywords)
    
    if not has_comparison:
        return []
    
    # Extract all crops mentioned
    crops = []
    for standard_name, variations in CROP_MAPPINGS.items():
        for variation in variations:
            pattern = r'\b' + re.escape(variation) + r'\b'
            if re.search(pattern, question_lower):
                crops.append(standard_name.capitalize())
                break
    
    # Extract all states mentioned
    states = []
    for standard_name, variations in STATE_MAPPINGS.items():
        for variation in variations:
            pattern = r'\b' + re.escape(variation) + r'\b'
            if re.search(pattern, question_lower):
                states.append(standard_name)
                break
    
    # Extract month/year
    month, year = extract_month_year(question)
    
    # Build comparison sets
    comparisons = []
    
    # If multiple crops mentioned
    if len(crops) >= 2:
        for crop in crops:
            comparisons.append({
                "crop": crop,
                "state": states[0] if states else None,
                "month": month,
                "year": year
            })
    # If multiple states mentioned
    elif len(states) >= 2:
        for state in states:
            comparisons.append({
                "crop": crops[0] if crops else None,
                "state": state,
                "month": month,
                "year": year
            })
    
    return comparisons


def is_price_question(question: str) -> bool:
    """
    Determine if question is asking about prices or predictions.
    
    Args:
        question: User question
        
    Returns:
        True if question is price-related
    """
    question_lower = question.lower()
    
    price_keywords = [
        "price", "mandi", "market", "sell", "selling", "forecast",
        "prediction", "predicted", "expected", "will be",
        "profit", "revenue", "msp", "rate", "cost"
    ]
    
    return any(keyword in question_lower for keyword in price_keywords)
