"""
FarmPulse AI - Intelligent Context Manager
Manages conversation context and determines what data to fetch based on questions.
"""

import re
from typing import Dict, List, Optional, Set
from datetime import datetime


class ConversationContext:
    """Manages conversation state and context across multiple turns."""
    
    def __init__(self):
        self.last_crop = None
        self.last_state = None
        self.last_month = None
        self.last_year = None
        self.last_prediction = None
        self.last_comparison = None
        self.question_history = []
    
    def update(self, crop: str = None, state: str = None, 
               month: int = None, year: int = None,
               prediction: Dict = None):
        """Update conversation context with new information."""
        if crop:
            self.last_crop = crop
        if state:
            self.last_state = state
        if month:
            self.last_month = month
        if year:
            self.last_year = year
        if prediction:
            self.last_prediction = prediction
    
    def add_question(self, question: str):
        """Add question to history."""
        self.question_history.append({
            "question": question,
            "timestamp": datetime.now(),
            "crop": self.last_crop,
            "state": self.last_state
        })
        # Keep last 20 questions
        if len(self.question_history) > 20:
            self.question_history = self.question_history[-20:]
    
    def get_context_summary(self) -> str:
        """Get a summary of recent conversation context."""
        parts = []
        if self.last_crop:
            parts.append(f"discussing {self.last_crop}")
        if self.last_state:
            parts.append(f"in {self.last_state}")
        return " ".join(parts) if parts else "general topic"


def detect_follow_up_question(question: str, context: ConversationContext) -> bool:
    """
    Detect if question is a follow-up that references previous context.
    
    Args:
        question: Current user question
        context: Conversation context
        
    Returns:
        True if this is a follow-up question
    """
    question_lower = question.lower()
    
    # Follow-up indicators
    follow_up_patterns = [
        r'\bit\b',  # "what about it"
        r'\bthat\b',  # "what about that"
        r'\bthis\b',  # "explain this"
        r'^what about',
        r'^how about',
        r'^and\b',
        r'^but\b',
        r'^also\b',
        r'^instead\b',
        r'^what if',
        r'^should i wait',
        r'^wait',
        r'compare.*with',  # "compare it with"
        r'versus',
        r'\bvs\b',
    ]
    
    for pattern in follow_up_patterns:
        if re.search(pattern, question_lower):
            return True
    
    # Check if question doesn't specify crop/state but context exists
    has_crop_mention = any(crop in question_lower for crop in ['tur', 'chana', 'moong', 'cotton', 'paddy'])
    has_state_mention = any(state in question_lower for state in ['karnataka', 'maharashtra', 'gujarat', 'telangana'])
    
    if not has_crop_mention and not has_state_mention and context.last_crop:
        return True
    
    return False


def determine_required_data(question: str, context: ConversationContext) -> Set[str]:
    """
    Determine what data modules are needed to answer the question.
    
    Args:
        question: User question
        context: Conversation context
        
    Returns:
        Set of required data types
    """
    question_lower = question.lower()
    required = set()
    
    # Price/prediction related
    price_keywords = ['price', 'mandi', 'market', 'rate', 'cost', 'forecast', 'prediction', 'expected']
    if any(kw in question_lower for kw in price_keywords):
        required.add('prediction')
    
    # Profit related
    profit_keywords = ['profit', 'revenue', 'earnings', 'income', 'return', 'money', 'earn']
    if any(kw in question_lower for kw in profit_keywords):
        required.add('profit')
        required.add('prediction')
    
    # MSP related
    msp_keywords = ['msp', 'minimum support', 'support price', 'government price']
    if any(kw in question_lower for kw in msp_keywords):
        required.add('msp')
    
    # Comparison related
    comparison_keywords = ['compare', 'versus', 'vs', 'better', 'best', 'difference', 'which']
    if any(kw in question_lower for kw in comparison_keywords):
        required.add('comparison')
        required.add('prediction')
    
    # Selling decision related
    sell_keywords = ['sell', 'selling', 'should i', 'when to', 'recommend']
    if any(kw in question_lower for kw in sell_keywords):
        required.add('prediction')
        required.add('recommendation')
        required.add('msp')
        required.add('trend')
    
    # Explanation related
    explain_keywords = ['why', 'explain', 'reason', 'how', 'what causes', 'because']
    if any(kw in question_lower for kw in explain_keywords):
        required.add('prediction')
        required.add('models')
        required.add('confidence')
        required.add('trend')
    
    # Historical related
    history_keywords = ['history', 'historical', 'past', 'previous', 'before', 'trend']
    if any(kw in question_lower for kw in history_keywords):
        required.add('historical')
        required.add('trend')
    
    # Risk related
    risk_keywords = ['risk', 'risky', 'safe', 'volatile', 'stability', 'uncertain']
    if any(kw in question_lower for kw in risk_keywords):
        required.add('prediction')
        required.add('confidence')
        required.add('recommendation')
    
    # If nothing specific detected, include basics
    if not required:
        required.add('prediction')
    
    return required


def build_intelligent_context(question: str, base_context: Dict, 
                              required_data: Set[str],
                              conversation_ctx: ConversationContext) -> Dict:
    """
    Build intelligent context with only relevant information.
    
    Args:
        question: User question
        base_context: Base prediction context
        required_data: Set of required data types
        conversation_ctx: Conversation context
        
    Returns:
        Enhanced context dictionary
    """
    context = base_context.copy()
    
    # Add conversation context
    context['conversation_summary'] = conversation_ctx.get_context_summary()
    context['is_follow_up'] = detect_follow_up_question(question, conversation_ctx)
    
    # Add metadata about what was included
    context['included_modules'] = list(required_data)
    
    # Mark if this needs comparison
    context['needs_comparison'] = 'comparison' in required_data
    
    # Mark if this needs explanation
    context['needs_explanation'] = 'why' in question.lower() or 'explain' in question.lower()
    
    return context


def extract_time_reference(question: str, current_context: ConversationContext) -> tuple[Optional[int], Optional[int]]:
    """
    Extract time reference from follow-up questions like "what about next month?"
    
    Args:
        question: User question
        current_context: Conversation context
        
    Returns:
        Tuple of (month, year) or (None, None)
    """
    question_lower = question.lower()
    
    # Relative references
    if 'next month' in question_lower or 'following month' in question_lower:
        if current_context.last_month and current_context.last_year:
            month = current_context.last_month + 1
            year = current_context.last_year
            if month > 12:
                month = 1
                year += 1
            return month, year
    
    if 'this month' in question_lower or 'current month' in question_lower:
        now = datetime.now()
        return now.month, now.year
    
    if 'previous month' in question_lower or 'last month' in question_lower:
        if current_context.last_month and current_context.last_year:
            month = current_context.last_month - 1
            year = current_context.last_year
            if month < 1:
                month = 12
                year -= 1
            return month, year
    
    return None, None


def extract_comparison_reference(question: str, current_context: ConversationContext) -> Optional[Dict]:
    """
    Extract comparison reference from follow-up like "compare it with Gujarat"
    
    Args:
        question: User question
        current_context: Conversation context
        
    Returns:
        Comparison parameters or None
    """
    question_lower = question.lower()
    
    # Pattern: "compare (it/this/that) with X"
    patterns = [
        r'compare\s+(?:it|this|that)\s+with\s+(\w+)',
        r'versus\s+(\w+)',
        r'vs\s+(\w+)',
        r'compared to\s+(\w+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, question_lower)
        if match:
            compare_with = match.group(1)
            
            # Try to identify if it's a state or crop
            from services.question_parser import normalize_state_name, normalize_crop_name
            
            state = normalize_state_name(compare_with)
            crop = normalize_crop_name(compare_with)
            
            if state or crop:
                return {
                    "compare_state": state,
                    "compare_crop": crop,
                    "base_crop": current_context.last_crop,
                    "base_state": current_context.last_state
                }
    
    return None


def should_use_cached_prediction(question: str, last_prediction: Dict, 
                                 current_params: Dict) -> bool:
    """
    Determine if we can reuse the last prediction instead of fetching new data.
    
    Args:
        question: User question
        last_prediction: Last fetched prediction
        current_params: Current request parameters
        
    Returns:
        True if cached prediction can be used
    """
    if not last_prediction:
        return False
    
    # Check if parameters match
    if (last_prediction.get('crop') == current_params.get('crop') and
        last_prediction.get('state') == current_params.get('state') and
        last_prediction.get('target_month') == current_params.get('target_month')):
        
        # Check if it's a follow-up question that doesn't need fresh data
        question_lower = question.lower()
        
        # These questions can use cached data
        reusable_patterns = [
            'why', 'explain', 'how', 'what causes',
            'should i', 'recommend', 'advice',
            'tell me more', 'details'
        ]
        
        if any(pattern in question_lower for pattern in reusable_patterns):
            return True
    
    return False
