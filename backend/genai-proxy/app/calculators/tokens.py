"""
Token counting utilities

Counts tokens for different models and providers
"""

import tiktoken
from typing import List, Dict


def count_tokens(messages: List[Dict], model: str = "gpt-3.5-turbo") -> int:
    """
    Count tokens in messages for a given model
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model name
        
    Returns:
        Total token count
    """
    
    try:
        # Get encoding for model
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback to cl100k_base for unknown models
        encoding = tiktoken.get_encoding("cl100k_base")
    
    # Count tokens
    num_tokens = 0
    
    for message in messages:
        # Every message follows <im_start>{role/name}\n{content}<im_end>\n
        num_tokens += 4  # Message overhead
        
        for key, value in message.items():
            if isinstance(value, str):
                num_tokens += len(encoding.encode(value))
            
            if key == "name":
                num_tokens += -1  # Role is always required and always 1 token
    
    num_tokens += 2  # Every reply is primed with <im_start>assistant
    
    return num_tokens


def count_tokens_text(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Count tokens in plain text
    
    Args:
        text: Input text
        model: Model name
        
    Returns:
        Token count
    """
    
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    return len(encoding.encode(text))


def estimate_cost(tokens_input: int, tokens_output: int, model: str) -> float:
    """
    Estimate cost in USD based on token usage
    
    Args:
        tokens_input: Input tokens
        tokens_output: Output tokens
        model: Model name
        
    Returns:
        Estimated cost in USD
    """
    
    # Pricing per 1M tokens (as of 2024)
    pricing = {
        "gpt-4": {"input": 30.0, "output": 60.0},
        "gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
        "claude-3-opus": {"input": 15.0, "output": 75.0},
        "claude-3-sonnet": {"input": 3.0, "output": 15.0},
        "default": {"input": 1.0, "output": 2.0}
    }
    
    model_pricing = pricing.get(model, pricing["default"])
    
    cost_input = (tokens_input / 1_000_000) * model_pricing["input"]
    cost_output = (tokens_output / 1_000_000) * model_pricing["output"]
    
    return round(cost_input + cost_output, 6)
