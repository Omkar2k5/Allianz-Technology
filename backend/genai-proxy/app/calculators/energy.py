"""
Energy calculation engine

Calculates energy consumption based on token usage and model type
"""

from typing import Dict

# Energy profiles for different models (kWh per 1000 tokens)
MODEL_ENERGY_PROFILES: Dict[str, float] = {
    # OpenAI
    "gpt-4": 0.0008,
    "gpt-4-turbo": 0.0007,
    "gpt-3.5-turbo": 0.0003,
    "gpt-3.5-turbo-16k": 0.0004,
    
    # Anthropic
    "claude-3-opus": 0.0007,
    "claude-3-sonnet": 0.0005,
    "claude-3-haiku": 0.0002,
    
    # Google
    "gemini-pro": 0.0009,
    "gemini-ultra": 0.0012,
    
    # Meta
    "llama-3-70b": 0.0006,
    "llama-3-8b": 0.0002,
    
    # Default fallback
    "default": 0.0005
}


def calculate_energy(tokens: int, model: str) -> float:
    """
    Calculate energy consumption in Watt-hours (Wh)
    
    Args:
        tokens: Total number of tokens (input + output)
        model: Model name
        
    Returns:
        Energy consumption in Wh
        
    Formula:
        Energy (Wh) = (tokens / 1000) × model_energy_per_1k_tokens × 1000
    """
    
    # Get energy profile for model
    energy_per_1k = MODEL_ENERGY_PROFILES.get(model, MODEL_ENERGY_PROFILES["default"])
    
    # Calculate energy in kWh
    energy_kwh = (tokens / 1000.0) * energy_per_1k
    
    # Convert to Wh
    energy_wh = energy_kwh * 1000
    
    return round(energy_wh, 4)


def get_model_efficiency_score(model: str) -> str:
    """
    Get efficiency score for a model (A+ to D)
    
    Args:
        model: Model name
        
    Returns:
        Efficiency score (A+, A, B, C, D)
    """
    energy = MODEL_ENERGY_PROFILES.get(model, MODEL_ENERGY_PROFILES["default"])
    
    if energy <= 0.0002:
        return "A+"
    elif energy <= 0.0004:
        return "A"
    elif energy <= 0.0006:
        return "B"
    elif energy <= 0.0008:
        return "C"
    else:
        return "D"
