"""
Eco-Compute SDK - Sustainability Tracking for LLM API Calls

A lightweight, provider-agnostic Python SDK that wraps LLM API calls and
automatically tracks energy usage, carbon emissions, cost, and sustainability
metrics for Generative AI requests.

Features:
- Provider-agnostic LLM wrapper (OpenRouter)
- Automatic sustainability estimation (energy, carbon, cost)
- Non-blocking async telemetry
- Enterprise-ready ESG reporting
- Type-safe with full type hints
- Drop-in replacement design

Quick Start:
    >>> from eco_compute import EcoCompute, EcoComputeConfig
    >>> 
    >>> config = EcoComputeConfig(
    ...     telemetry_endpoint="https://api.example.com/telemetry",
    ...     telemetry_token="your-token",
    ...     region="us-west-2"
    ... )
    >>> 
    >>> eco = EcoCompute(config)
    >>> 
    >>> result = eco.call_llm(
    ...     "What is the capital of France?",
    ...     {
    ...         "model": "openai/gpt-4o-mini",
    ...         "api_key": "your-openrouter-key"
    ...     }
    ... )
    >>> 
    >>> print(result["response"]["choices"][0]["message"]["content"])
    >>> print(f"Carbon footprint: {result['estimation']['co2_g']:.6f}g CO2")

For more information, see the README.md or visit the project repository.
"""

__version__ = "0.1.0"
__author__ = "Eco-Compute Contributors"
__license__ = "MIT"

# Core exports
from eco_compute.client import EcoCompute, call_llm
from eco_compute.types import (
    CallResult,
    EcoComputeConfig,
    EstimationResult,
    LLMConfig,
    LLMResponse,
    PolicyAction,
    RiskLevel,
    TelemetryRecord,
)

# Estimator exports
from eco_compute.estimators import (
    compare_models_cost,
    compare_regions,
    estimate_carbon,
    estimate_cost,
    estimate_energy,
    get_carbon_intensity,
    get_cleanest_regions,
    get_energy_factor,
    get_model_pricing,
)

# Telemetry exports
from eco_compute.telemetry import TelemetrySender, TelemetrySenderConfig, create_sender

# Utility exports
from eco_compute.utils import (
    generate_request_id,
    get_computer_name,
    get_platform_info,
    get_process_name,
    hash_request,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    # Core
    "EcoCompute",
    "EcoComputeConfig",
    "call_llm",
    # Types
    "LLMConfig",
    "LLMResponse",
    "TelemetryRecord",
    "EstimationResult",
    "CallResult",
    "RiskLevel",
    "PolicyAction",
    # Estimators
    "estimate_energy",
    "estimate_carbon",
    "estimate_cost",
    "get_energy_factor",
    "get_carbon_intensity",
    "get_model_pricing",
    "compare_regions",
    "compare_models_cost",
    "get_cleanest_regions",
    # Telemetry
    "TelemetrySender",
    "TelemetrySenderConfig",
    "create_sender",
    # Utils
    "hash_request",
    "generate_request_id",
    "get_computer_name",
    "get_process_name",
    "get_platform_info",
]
