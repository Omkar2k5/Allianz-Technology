"""
Cost estimation module for LLM API calls.

This module provides cost estimation based on token usage and
model-specific pricing from various LLM providers.

Pricing is based on input and output tokens separately, as most
providers charge different rates for each.
"""

from typing import Dict, Optional, Tuple

# Default model pricing (USD per 1M tokens)
# Pricing is separated into input and output costs
#
# Format: {"model_name": {"input": price_per_1M, "output": price_per_1M}}
#
# Sources:
# - OpenAI pricing page
# - Anthropic pricing page
# - Google AI pricing page
# - OpenRouter pricing API
#
# Note: Prices are subject to change. These represent list prices as of
# the SDK development date. For accurate billing, verify with providers.

DEFAULT_MODEL_PRICING: Dict[str, Dict[str, float]] = {
    # OpenAI Models (USD per 1M tokens)
    "gpt-4": {"input": 30.00, "output": 60.00},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-4-turbo-preview": {"input": 10.00, "output": 30.00},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "gpt-3.5-turbo-16k": {"input": 3.00, "output": 4.00},
    "o1": {"input": 15.00, "output": 60.00},
    "o1-mini": {"input": 3.00, "output": 12.00},
    "o1-preview": {"input": 15.00, "output": 60.00},
    
    # Anthropic Models
    "claude-3-opus": {"input": 15.00, "output": 75.00},
    "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    "claude-3-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
    "claude-3-haiku": {"input": 0.25, "output": 1.25},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    "claude-3.5-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3.5-sonnet-20240620": {"input": 3.00, "output": 15.00},
    "claude-3.5-haiku": {"input": 0.80, "output": 4.00},
    "claude-2": {"input": 8.00, "output": 24.00},
    "claude-2.1": {"input": 8.00, "output": 24.00},
    "claude-instant": {"input": 0.80, "output": 2.40},
    
    # Google Models
    "gemini-pro": {"input": 0.50, "output": 1.50},
    "gemini-pro-vision": {"input": 0.50, "output": 1.50},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-ultra": {"input": 10.00, "output": 30.00},
    
    # Meta Models (via OpenRouter/providers)
    "llama-2-7b": {"input": 0.05, "output": 0.05},
    "llama-2-13b": {"input": 0.10, "output": 0.10},
    "llama-2-70b": {"input": 0.65, "output": 0.80},
    "llama-3-8b": {"input": 0.06, "output": 0.06},
    "llama-3-70b": {"input": 0.59, "output": 0.79},
    "llama-3.1-8b": {"input": 0.06, "output": 0.06},
    "llama-3.1-70b": {"input": 0.59, "output": 0.79},
    "llama-3.1-405b": {"input": 3.00, "output": 3.00},
    "codellama-34b": {"input": 0.35, "output": 0.35},
    
    # Mistral Models
    "mistral-7b": {"input": 0.05, "output": 0.05},
    "mistral-7b-instruct": {"input": 0.05, "output": 0.05},
    "mixtral-8x7b": {"input": 0.24, "output": 0.24},
    "mixtral-8x7b-instruct": {"input": 0.24, "output": 0.24},
    "mixtral-8x22b": {"input": 0.65, "output": 0.65},
    "mistral-small": {"input": 0.20, "output": 0.60},
    "mistral-medium": {"input": 2.70, "output": 8.10},
    "mistral-large": {"input": 4.00, "output": 12.00},
    
    # Cohere Models
    "command": {"input": 1.00, "output": 2.00},
    "command-light": {"input": 0.30, "output": 0.60},
    "command-r": {"input": 0.50, "output": 1.50},
    "command-r-plus": {"input": 3.00, "output": 15.00},
    
    # Other Models
    "phi-2": {"input": 0.03, "output": 0.03},
    "phi-3-mini": {"input": 0.04, "output": 0.04},
    "yi-34b": {"input": 0.20, "output": 0.20},
    "qwen-72b": {"input": 0.55, "output": 0.55},
    "deepseek-coder": {"input": 0.14, "output": 0.28},
    
    # Default fallback (conservative estimate)
    "_default": {"input": 1.00, "output": 3.00},
}


def get_model_pricing(
    model_name: str,
    custom_pricing: Optional[Dict[str, Dict[str, float]]] = None
) -> Tuple[float, float]:
    """
    Get the pricing for a specific model.
    
    Returns input and output pricing in USD per 1M tokens.
    
    Args:
        model_name: Model identifier (e.g., 'openai/gpt-4' or 'gpt-4')
        custom_pricing: Optional custom pricing to override defaults
    
    Returns:
        Tuple of (input_price_per_1M, output_price_per_1M)
    
    Example:
        >>> get_model_pricing("gpt-4o-mini")
        (0.15, 0.60)
    """
    # Check custom pricing first
    if custom_pricing:
        pricing = _lookup_pricing(model_name, custom_pricing)
        if pricing:
            return pricing
    
    # Check default pricing
    pricing = _lookup_pricing(model_name, DEFAULT_MODEL_PRICING)
    if pricing:
        return pricing
    
    # Return default
    default = DEFAULT_MODEL_PRICING["_default"]
    return (default["input"], default["output"])


def _lookup_pricing(
    model_name: str,
    pricing_dict: Dict[str, Dict[str, float]]
) -> Optional[Tuple[float, float]]:
    """
    Look up pricing in a pricing dictionary.
    
    Args:
        model_name: Model identifier
        pricing_dict: Pricing dictionary to search
    
    Returns:
        Tuple of (input, output) prices or None if not found
    """
    # Direct match
    if model_name in pricing_dict:
        p = pricing_dict[model_name]
        return (p["input"], p["output"])
    
    # Try without provider prefix
    base_name = _extract_model_name(model_name)
    if base_name in pricing_dict:
        p = pricing_dict[base_name]
        return (p["input"], p["output"])
    
    # Try partial matching for versioned models
    for key in pricing_dict:
        if key != "_default":
            if base_name.startswith(key) or key.startswith(base_name):
                p = pricing_dict[key]
                return (p["input"], p["output"])
    
    return None


def _extract_model_name(full_name: str) -> str:
    """
    Extract the base model name from a full model identifier.
    
    Args:
        full_name: Full model name (e.g., 'openai/gpt-4-turbo')
    
    Returns:
        Base model name (e.g., 'gpt-4-turbo')
    """
    if "/" in full_name:
        return full_name.split("/", 1)[1]
    return full_name


def estimate_cost(
    tokens_input: int,
    tokens_output: int,
    model_name: str,
    custom_pricing: Optional[Dict[str, Dict[str, float]]] = None
) -> float:
    """
    Estimate the cost of an LLM request in USD.
    
    Uses the formula:
        cost = (tokens_input × input_price / 1M) + (tokens_output × output_price / 1M)
    
    Args:
        tokens_input: Number of input/prompt tokens
        tokens_output: Number of output/completion tokens
        model_name: Model identifier for pricing lookup
        custom_pricing: Optional custom pricing dictionary
    
    Returns:
        Estimated cost in USD
    
    Example:
        >>> estimate_cost(1000, 500, "gpt-4o-mini")
        0.00045  # $0.00045
        
        >>> estimate_cost(1000, 500, "gpt-4")
        0.06  # $0.06
    """
    if tokens_input < 0:
        tokens_input = 0
    if tokens_output < 0:
        tokens_output = 0
    
    input_price, output_price = get_model_pricing(model_name, custom_pricing)
    
    # Prices are per 1M tokens
    cost_input = tokens_input * (input_price / 1_000_000)
    cost_output = tokens_output * (output_price / 1_000_000)
    
    total_cost = cost_input + cost_output
    
    return round(total_cost, 10)


def estimate_cost_detailed(
    tokens_input: int,
    tokens_output: int,
    model_name: str,
    custom_pricing: Optional[Dict[str, Dict[str, float]]] = None
) -> Dict[str, float]:
    """
    Estimate cost with detailed breakdown.
    
    Args:
        tokens_input: Number of input tokens
        tokens_output: Number of output tokens
        model_name: Model identifier
        custom_pricing: Optional custom pricing
    
    Returns:
        Dictionary with cost breakdown:
        - cost_input: Cost for input tokens
        - cost_output: Cost for output tokens
        - cost_total: Total cost
        - input_price_per_1m: Input price per 1M tokens
        - output_price_per_1m: Output price per 1M tokens
    
    Example:
        >>> estimate_cost_detailed(1000, 500, "gpt-4")
        {
            'cost_input': 0.03,
            'cost_output': 0.03,
            'cost_total': 0.06,
            'input_price_per_1m': 30.0,
            'output_price_per_1m': 60.0
        }
    """
    if tokens_input < 0:
        tokens_input = 0
    if tokens_output < 0:
        tokens_output = 0
    
    input_price, output_price = get_model_pricing(model_name, custom_pricing)
    
    cost_input = tokens_input * (input_price / 1_000_000)
    cost_output = tokens_output * (output_price / 1_000_000)
    
    return {
        "cost_input": round(cost_input, 10),
        "cost_output": round(cost_output, 10),
        "cost_total": round(cost_input + cost_output, 10),
        "input_price_per_1m": input_price,
        "output_price_per_1m": output_price
    }


def compare_models_cost(
    tokens_input: int,
    tokens_output: int,
    models: Optional[list] = None
) -> Dict[str, float]:
    """
    Compare costs across multiple models.
    
    Useful for showing cost differences between model choices.
    
    Args:
        tokens_input: Number of input tokens
        tokens_output: Number of output tokens
        models: List of models to compare (default: popular models)
    
    Returns:
        Dictionary mapping model names to estimated costs
    
    Example:
        >>> compare_models_cost(1000, 500)
        {
            'gpt-4': 0.06,
            'gpt-4o-mini': 0.00045,
            'claude-3-haiku': 0.000875,
            ...
        }
    """
    if models is None:
        models = [
            "gpt-4", "gpt-4o", "gpt-4o-mini",
            "claude-3-opus", "claude-3-sonnet", "claude-3-haiku",
            "gemini-1.5-pro", "gemini-1.5-flash",
            "llama-3-70b", "mixtral-8x7b"
        ]
    
    return {
        model: estimate_cost(tokens_input, tokens_output, model)
        for model in models
    }


def list_supported_models() -> list:
    """
    List all models with defined pricing.
    
    Returns:
        List of model names with pricing defined
    """
    return [k for k in DEFAULT_MODEL_PRICING.keys() if k != "_default"]


def get_cheapest_models(top_n: int = 5, token_ratio: float = 0.5) -> list:
    """
    Get the cheapest models based on a typical token ratio.
    
    Args:
        top_n: Number of models to return
        token_ratio: Ratio of output to input tokens (default: 0.5)
    
    Returns:
        List of (model, estimated_cost_per_1k_total_tokens) tuples
    """
    costs = []
    
    for model, pricing in DEFAULT_MODEL_PRICING.items():
        if model == "_default":
            continue
        
        # Estimate cost for 1000 tokens with given ratio
        input_tokens = int(1000 / (1 + token_ratio))
        output_tokens = 1000 - input_tokens
        
        cost = estimate_cost(input_tokens, output_tokens, model)
        costs.append((model, cost))
    
    costs.sort(key=lambda x: x[1])
    return costs[:top_n]
