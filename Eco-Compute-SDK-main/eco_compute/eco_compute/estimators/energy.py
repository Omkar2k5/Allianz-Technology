"""
Energy estimation module for LLM API calls.

This module provides deterministic, explainable energy consumption
estimation based on token usage and model-specific energy factors.

Formula:
    energy_wh = tokens_total × model_energy_factor

The energy factor represents the estimated watt-hours consumed per token
for a given model, derived from published research and hardware specifications.
"""

from typing import Dict, Optional

# Default model energy factors (Wh per 1000 tokens)
# These values are estimates based on:
# - Published ML carbon footprint research
# - GPU power consumption specifications
# - Model parameter counts and inference requirements
#
# Sources:
# - Strubell et al. (2019) "Energy and Policy Considerations for Deep Learning in NLP"
# - Patterson et al. (2021) "Carbon Emissions and Large Neural Network Training"
# - Luccioni et al. (2023) "Estimating the Carbon Footprint of BLOOM"
#
# Note: These are conservative estimates. Actual values may vary based on
# hardware, batch size, and provider optimizations.

DEFAULT_MODEL_ENERGY_FACTORS: Dict[str, float] = {
    # OpenAI Models (Wh per 1000 tokens)
    "gpt-4": 0.0050,
    "gpt-4-turbo": 0.0045,
    "gpt-4-turbo-preview": 0.0045,
    "gpt-4o": 0.0040,
    "gpt-4o-mini": 0.0025,
    "gpt-3.5-turbo": 0.0015,
    "gpt-3.5-turbo-16k": 0.0018,
    "o1": 0.0060,
    "o1-mini": 0.0035,
    "o1-preview": 0.0055,
    
    # Anthropic Models
    "claude-3-opus": 0.0055,
    "claude-3-opus-20240229": 0.0055,
    "claude-3-sonnet": 0.0035,
    "claude-3-sonnet-20240229": 0.0035,
    "claude-3-haiku": 0.0015,
    "claude-3-haiku-20240307": 0.0015,
    "claude-3.5-sonnet": 0.0038,
    "claude-3.5-sonnet-20240620": 0.0038,
    "claude-3.5-haiku": 0.0018,
    "claude-2": 0.0040,
    "claude-2.1": 0.0040,
    "claude-instant": 0.0012,
    
    # Google Models
    "gemini-pro": 0.0030,
    "gemini-pro-vision": 0.0035,
    "gemini-1.5-pro": 0.0035,
    "gemini-1.5-flash": 0.0020,
    "gemini-ultra": 0.0060,
    "palm-2": 0.0025,
    
    # Meta Models
    "llama-2-7b": 0.0008,
    "llama-2-13b": 0.0012,
    "llama-2-70b": 0.0035,
    "llama-3-8b": 0.0010,
    "llama-3-70b": 0.0038,
    "llama-3.1-8b": 0.0010,
    "llama-3.1-70b": 0.0038,
    "llama-3.1-405b": 0.0080,
    "codellama-34b": 0.0020,
    
    # Mistral Models
    "mistral-7b": 0.0008,
    "mistral-7b-instruct": 0.0008,
    "mixtral-8x7b": 0.0025,
    "mixtral-8x7b-instruct": 0.0025,
    "mixtral-8x22b": 0.0045,
    "mistral-small": 0.0015,
    "mistral-medium": 0.0030,
    "mistral-large": 0.0045,
    
    # Cohere Models
    "command": 0.0020,
    "command-light": 0.0010,
    "command-r": 0.0025,
    "command-r-plus": 0.0040,
    
    # Other Models
    "phi-2": 0.0005,
    "phi-3-mini": 0.0006,
    "yi-34b": 0.0020,
    "qwen-72b": 0.0035,
    "deepseek-coder": 0.0015,
    
    # Default fallback
    "_default": 0.0025,
}


def get_energy_factor(
    model_name: str,
    custom_factors: Optional[Dict[str, float]] = None
) -> float:
    """
    Get the energy factor for a specific model.
    
    Looks up the energy factor (Wh per 1000 tokens) for the given model,
    falling back to a conservative default if not found.
    
    Args:
        model_name: Full model name (e.g., 'openai/gpt-4' or 'gpt-4')
        custom_factors: Optional custom energy factors to override defaults
    
    Returns:
        Energy factor in Wh per 1000 tokens
    
    Example:
        >>> get_energy_factor("gpt-4")
        0.005
        
        >>> get_energy_factor("openai/gpt-4")
        0.005
    """
    # Check custom factors first
    if custom_factors:
        if model_name in custom_factors:
            return custom_factors[model_name]
        
        # Try without provider prefix
        base_name = _extract_model_name(model_name)
        if base_name in custom_factors:
            return custom_factors[base_name]
    
    # Check default factors
    if model_name in DEFAULT_MODEL_ENERGY_FACTORS:
        return DEFAULT_MODEL_ENERGY_FACTORS[model_name]
    
    # Try without provider prefix
    base_name = _extract_model_name(model_name)
    if base_name in DEFAULT_MODEL_ENERGY_FACTORS:
        return DEFAULT_MODEL_ENERGY_FACTORS[base_name]
    
    # Try partial matching for versioned models
    for key in DEFAULT_MODEL_ENERGY_FACTORS:
        if base_name.startswith(key) or key.startswith(base_name):
            return DEFAULT_MODEL_ENERGY_FACTORS[key]
    
    # Return default
    return DEFAULT_MODEL_ENERGY_FACTORS["_default"]


def _extract_model_name(full_name: str) -> str:
    """
    Extract the base model name from a full model identifier.
    
    Args:
        full_name: Full model name (e.g., 'openai/gpt-4-turbo-preview')
    
    Returns:
        Base model name (e.g., 'gpt-4-turbo-preview')
    """
    # Remove provider prefix
    if "/" in full_name:
        return full_name.split("/", 1)[1]
    return full_name


def estimate_energy(
    tokens_total: int,
    model_name: str,
    custom_factors: Optional[Dict[str, float]] = None
) -> float:
    """
    Estimate energy consumption for an LLM request.
    
    Uses the formula:
        energy_wh = tokens_total × (model_energy_factor / 1000)
    
    The energy factor is in Wh per 1000 tokens, so we divide by 1000
    to get Wh per token.
    
    Args:
        tokens_total: Total number of tokens (input + output)
        model_name: Model identifier for energy factor lookup
        custom_factors: Optional custom energy factors
    
    Returns:
        Estimated energy consumption in watt-hours (Wh)
    
    Example:
        >>> estimate_energy(1000, "gpt-4")
        0.005  # Wh
        
        >>> estimate_energy(5000, "claude-3-haiku")
        0.0075  # Wh
    """
    if tokens_total <= 0:
        return 0.0
    
    factor = get_energy_factor(model_name, custom_factors)
    
    # factor is Wh per 1000 tokens
    energy_wh = tokens_total * (factor / 1000.0)
    
    return round(energy_wh, 10)


def estimate_energy_detailed(
    tokens_input: int,
    tokens_output: int,
    model_name: str,
    custom_factors: Optional[Dict[str, float]] = None,
    output_multiplier: float = 1.0
) -> Dict[str, float]:
    """
    Estimate energy consumption with detailed breakdown.
    
    Optionally applies a multiplier to output tokens to account for
    the typically higher computational cost of generation vs. processing.
    
    Args:
        tokens_input: Number of input/prompt tokens
        tokens_output: Number of output/completion tokens
        model_name: Model identifier for energy factor lookup
        custom_factors: Optional custom energy factors
        output_multiplier: Multiplier for output token cost (default: 1.0)
    
    Returns:
        Dictionary with energy breakdown:
        - energy_input_wh: Energy for input processing
        - energy_output_wh: Energy for output generation
        - energy_total_wh: Total energy consumption
        - model_factor: Energy factor used
    
    Example:
        >>> estimate_energy_detailed(500, 200, "gpt-4", output_multiplier=1.5)
        {
            'energy_input_wh': 0.0025,
            'energy_output_wh': 0.0015,
            'energy_total_wh': 0.004,
            'model_factor': 0.005
        }
    """
    if tokens_input < 0:
        tokens_input = 0
    if tokens_output < 0:
        tokens_output = 0
    
    factor = get_energy_factor(model_name, custom_factors)
    factor_per_token = factor / 1000.0
    
    energy_input = tokens_input * factor_per_token
    energy_output = tokens_output * factor_per_token * output_multiplier
    energy_total = energy_input + energy_output
    
    return {
        "energy_input_wh": round(energy_input, 10),
        "energy_output_wh": round(energy_output, 10),
        "energy_total_wh": round(energy_total, 10),
        "model_factor": factor
    }


def list_supported_models() -> list:
    """
    List all models with defined energy factors.
    
    Returns:
        List of model names with energy factors defined
    """
    return [k for k in DEFAULT_MODEL_ENERGY_FACTORS.keys() if k != "_default"]


def get_default_factor() -> float:
    """
    Get the default energy factor used for unknown models.
    
    Returns:
        Default energy factor in Wh per 1000 tokens
    """
    return DEFAULT_MODEL_ENERGY_FACTORS["_default"]
