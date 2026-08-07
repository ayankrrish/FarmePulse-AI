"""
FarmPulse AI - Groq API Integration Service
Handles communication with Groq API for natural language agricultural advisory.
"""

import os
import logging
import requests
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Groq API Configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_TIMEOUT = 30  # seconds


class GroqAPIError(Exception):
    """Custom exception for Groq API errors."""
    pass


def get_api_key() -> Optional[str]:
    """
    Get Groq API key from environment variable.
    
    Returns:
        API key string or None if not found
    """
    return os.environ.get("GROQ_API_KEY")


def validate_api_key() -> bool:
    """
    Check if API key is configured.
    
    Returns:
        True if API key exists, False otherwise
    """
    api_key = get_api_key()
    return api_key is not None and len(api_key) > 0


def call_groq_api(
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> Dict:
    """
    Call Groq API with conversation messages.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        temperature: Sampling temperature (0.0 to 1.0)
        max_tokens: Maximum tokens in response
        
    Returns:
        API response dict
        
    Raises:
        GroqAPIError: If API call fails
    """
    api_key = get_api_key()
    
    if not api_key:
        raise GroqAPIError("GROQ_API_KEY environment variable not set")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        logger.info("Calling Groq API with %d messages", len(messages))
        
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=GROQ_TIMEOUT
        )
        
        # Handle HTTP errors
        if response.status_code == 401:
            raise GroqAPIError("Invalid API key")
        elif response.status_code == 429:
            raise GroqAPIError("Rate limit exceeded. Please try again later.")
        elif response.status_code >= 500:
            raise GroqAPIError("Groq API service unavailable. Please try again later.")
        elif response.status_code != 200:
            # Parse error response
            try:
                error_data = response.json()
                error_msg = error_data.get("error", {})
                if isinstance(error_msg, dict):
                    error_msg = error_msg.get("message", str(error_msg))
                raise GroqAPIError(f"API error: {error_msg}")
            except ValueError:
                # Response is not JSON
                raise GroqAPIError(f"API error: HTTP {response.status_code}")
        
        data = response.json()
        logger.info("Groq API call successful")
        return data
        
    except requests.exceptions.Timeout:
        raise GroqAPIError("Request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        raise GroqAPIError("Network connection error. Please check your internet connection.")
    except requests.exceptions.RequestException as e:
        logger.exception("Groq API request failed")
        raise GroqAPIError(f"Request failed: {str(e)}")
    except Exception as e:
        logger.exception("Unexpected error calling Groq API")
        raise GroqAPIError(f"Unexpected error: {str(e)}")


def extract_response_text(api_response: Dict) -> str:
    """
    Extract response text from Groq API response.
    
    Args:
        api_response: Raw API response dict
        
    Returns:
        Response text string
        
    Raises:
        GroqAPIError: If response format is invalid
    """
    try:
        # Verify api_response is a dict
        if not isinstance(api_response, dict):
            raise GroqAPIError(f"API response must be a dict, got {type(api_response).__name__}")
        
        choices = api_response.get("choices", [])
        
        if not choices:
            raise GroqAPIError("Empty response from API")
        
        # Verify choices is a list
        if not isinstance(choices, list):
            raise GroqAPIError(f"choices must be a list, got {type(choices).__name__}")
        
        # Get first choice
        first_choice = choices[0]
        
        if not isinstance(first_choice, dict):
            raise GroqAPIError(f"choice must be a dict, got {type(first_choice).__name__}")
        
        message = first_choice.get("message", {})
        
        if not isinstance(message, dict):
            raise GroqAPIError(f"message must be a dict, got {type(message).__name__}")
        
        content = message.get("content", "")
        
        if not isinstance(content, str):
            raise GroqAPIError(f"content must be a string, got {type(content).__name__}")
        
        if not content:
            raise GroqAPIError("No content in API response")
        
        return content.strip()
        
    except (KeyError, IndexError) as e:
        logger.exception("Failed to extract response text")
        raise GroqAPIError(f"Invalid response format: {str(e)}")


def get_ai_response(
    system_prompt: str,
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Get AI response for a user question with context.
    
    Args:
        system_prompt: System role and context prompt
        user_message: Current user question
        conversation_history: Previous messages (optional)
        
    Returns:
        AI response text
        
    Raises:
        GroqAPIError: If API call fails
    """
    # Build messages list
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history)
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})
    
    # Call API
    response = call_groq_api(messages)
    
    # Extract and return text
    return extract_response_text(response)
