# Eco-Compute SDK

[![PyPI version](https://badge.fury.io/py/eco-compute.svg)](https://badge.fury.io/py/eco-compute)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Type Hints](https://img.shields.io/badge/type_hints-yes-brightgreen.svg)](https://docs.python.org/3/library/typing.html)

A lightweight, provider-agnostic Python SDK that wraps LLM API calls and automatically tracks **energy usage**, **carbon emissions**, **cost**, and **sustainability metrics** for Generative AI requests.

Built for **enterprise ESG reporting**, **AI sustainability analytics**, and **responsible AI adoption**.

## Features

- 🌱 **Sustainability Tracking** - Automatic energy, carbon, and cost estimation
- 🔌 **Provider Agnostic** - Works with any LLM via OpenRouter
- 📊 **Explainable Metrics** - Deterministic, auditable calculations
- 🚀 **Non-Intrusive** - Async telemetry, never crashes host app
- 🔒 **Enterprise Ready** - Full type hints, ESG-compliant schema
- 📦 **Drop-in Replacement** - Minimal code changes required

## Installation

```bash
pip install eco-compute
```

Or install from source:

```bash
git clone https://github.com/eco-compute/eco-compute-sdk.git
cd eco-compute-sdk
pip install -e .
```

## Quick Start

```python
from eco_compute import EcoCompute, EcoComputeConfig

# Configure the SDK
config = EcoComputeConfig(
    telemetry_endpoint="https://api.example.com/telemetry",  # Optional
    telemetry_token="your-bearer-token",                     # Optional
    region="us-west-2"  # For carbon intensity calculation
)

# Create client
eco = EcoCompute(config)

# Make LLM call with sustainability tracking
result = eco.call_llm(
    prompt="What is the capital of France?",
    config={
        "model": "openai/gpt-4o-mini",
        "api_key": "your-openrouter-api-key"
    }
)

# Access the original response (unchanged)
print(result["response"]["choices"][0]["message"]["content"])

# Access sustainability metrics
print(f"Energy: {result['estimation']['energy_wh']:.6f} Wh")
print(f"Carbon: {result['estimation']['co2_g']:.6f} g CO2")
print(f"Cost: ${result['estimation']['cost_usd']:.6f}")
```

## Configuration Options

```python
from eco_compute import EcoComputeConfig

config = EcoComputeConfig(
    # Telemetry settings
    telemetry_endpoint="https://api.example.com/telemetry",
    telemetry_token="your-bearer-token",
    telemetry_enabled=True,
    
    # OpenRouter settings
    openrouter_base_url="https://openrouter.ai/api/v1",
    
    # Carbon calculation
    region="us-west-2",  # AWS Oregon (150 gCO2/kWh)
    default_carbon_intensity=400.0,  # gCO2/kWh fallback
    
    # Custom model factors (Wh per 1000 tokens)
    model_energy_factors={
        "my-custom-model": 0.0030
    },
    
    # Custom pricing (USD per 1M tokens)
    model_pricing={
        "my-custom-model": {"input": 1.00, "output": 2.00}
    },
    
    # Behavior
    fail_silently=True,  # Never crash due to telemetry
    batch_size=10,       # Batch telemetry records
    debug=False          # Enable debug logging
)
```

## LLM Request Configuration

```python
result = eco.call_llm(
    prompt="Your prompt here",
    config={
        # Required
        "model": "openai/gpt-4o-mini",
        "api_key": "your-api-key",
        
        # Optional LLM parameters
        "max_tokens": 1000,
        "temperature": 0.7,
        "top_p": 0.9,
        
        # Optional tracking metadata
        "use_case": "customer_support",
        "user_id": "user-123",
        "agent_id": "agent-456",
        "app_id": "my-app",
        "risk_level": "low",  # low, medium, high, critical
        "meta_data": {"department": "sales"}
    }
)
```

## Telemetry Schema

All telemetry records follow this ESG-compliant schema:

```python
{
    "id": "uuid",
    "app_id": "my-app",
    "model_id": "openai/gpt-4o-mini",
    "user_id": "user-123",
    "agent_id": "agent-456",
    "timestamp": "2024-01-15T10:30:00Z",
    "request_hash": "sha256-hash",
    "computer_name": "DESKTOP-ABC123",
    "process_name": "python",
    "model_name": "openai/gpt-4o-mini",
    "provider": "openai",
    "tokens_input": 50,
    "tokens_output": 100,
    "tokens_total": 150,
    "energy_wh": 0.000375,
    "co2_g": 0.00005625,
    "region": "us-west-2",
    "carbon_intensity": 150.0,
    "latency_ms": 1234.56,
    "use_case": "customer_support",
    "risk_level": "low",
    "policy_applied": "",
    "policy_action": "allow",
    "cost_usd": 0.000075,
    "meta_data": {"department": "sales"},
    "created_at": "2024-01-15T10:30:00Z"
}
```

## Sustainability Formulas

### Energy Estimation

```
energy_wh = tokens_total × (model_energy_factor / 1000)
```

Model energy factors are derived from published ML carbon footprint research and represent estimated Wh per 1000 tokens.

### Carbon Estimation

```
co2_g = (energy_wh / 1000) × carbon_intensity
```

Carbon intensity values are region-specific (gCO2/kWh) based on EPA eGRID, IEA data, and cloud provider reports.

### Cost Estimation

```
cost_usd = (tokens_input × input_price / 1M) + (tokens_output × output_price / 1M)
```

## Standalone Estimators

Use the estimators directly without making API calls:

```python
from eco_compute import (
    estimate_energy,
    estimate_carbon,
    estimate_cost,
    compare_regions,
    compare_models_cost,
    get_cleanest_regions
)

# Estimate energy for a request
energy_wh = estimate_energy(tokens_total=1000, model_name="gpt-4")
print(f"Energy: {energy_wh} Wh")

# Estimate carbon emissions
co2_g = estimate_carbon(energy_wh=0.005, region="us-east")
print(f"Carbon: {co2_g} g CO2")

# Compare carbon across regions
comparison = compare_regions(energy_wh=1.0)
print(comparison)  # {"us-east": 0.4, "eu-north-1": 0.03, ...}

# Find the cleanest regions
cleanest = get_cleanest_regions(top_n=5)
print(cleanest)  # [("nuclear", 15.0), ("wind", 15.0), ...]

# Compare costs across models
cost_comparison = compare_models_cost(tokens_input=1000, tokens_output=500)
print(cost_comparison)
```

## Pre-Request Estimation

Estimate costs before making requests:

```python
eco = EcoCompute(config)

# Estimate without making an API call
estimate = eco.estimate_only(
    tokens_input=1000,
    tokens_output=500,
    model="gpt-4"
)

print(f"Estimated cost: ${estimate['cost_usd']:.4f}")
print(f"Estimated carbon: {estimate['co2_g']:.6f} g CO2")
```

## Context Manager

Use as a context manager for automatic cleanup:

```python
from eco_compute import EcoCompute, EcoComputeConfig

with EcoCompute(EcoComputeConfig(region="eu-north-1")) as eco:
    result = eco.call_llm(
        "Hello!",
        {"model": "openai/gpt-4o-mini", "api_key": "..."}
    )
    print(result["estimation"]["co2_g"])
# Telemetry is automatically flushed and resources cleaned up
```

## Supported Models

The SDK includes energy factors and pricing for 50+ models including:

- **OpenAI**: GPT-4, GPT-4 Turbo, GPT-4o, GPT-3.5 Turbo, o1
- **Anthropic**: Claude 3 Opus/Sonnet/Haiku, Claude 3.5 Sonnet
- **Google**: Gemini Pro, Gemini 1.5 Pro/Flash, Gemini Ultra
- **Meta**: Llama 2/3/3.1 (7B to 405B), CodeLlama
- **Mistral**: Mistral 7B, Mixtral 8x7B/8x22B, Mistral Large
- **Cohere**: Command, Command-R, Command-R+
- **Others**: Phi-2/3, Yi-34B, Qwen-72B, DeepSeek

Unknown models use conservative default estimates.

## Supported Regions

Carbon intensity data for 40+ regions including:

- **US**: us-east, us-west-1, us-west-2, us-central
- **Europe**: eu-west-1/2/3, eu-central-1, eu-north-1
- **Asia Pacific**: ap-northeast-1/2, ap-southeast-1/2, ap-south-1
- **Other**: Canada, Brazil, Middle East, Africa

## Development

```bash
# Clone the repository
git clone https://github.com/eco-compute/eco-compute-sdk.git
cd eco-compute-sdk

# Install dev dependencies
pip install -e ".[dev]"

# Run type checking
mypy eco_compute

# Format code
black eco_compute
isort eco_compute

# Run linting
flake8 eco_compute
```

## Building and Publishing

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI
twine upload dist/*
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) first.

## Enterprise Support

For enterprise deployments, custom integrations, or sustainability consulting, contact us at ecocompute@example.com.

---

Built with 💚 for a sustainable AI future.
