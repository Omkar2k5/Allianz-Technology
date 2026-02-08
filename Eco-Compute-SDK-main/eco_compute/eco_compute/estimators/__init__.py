"""
Sustainability estimators for the Eco-Compute SDK.

This package provides estimators for:
- Energy consumption (Wh)
- Carbon emissions (gCO2)
- Cost (USD)
"""

from eco_compute.estimators.carbon import (
    compare_regions,
    estimate_carbon,
    estimate_carbon_detailed,
    get_carbon_intensity,
    get_cleanest_regions,
    get_default_intensity,
    list_supported_regions,
)
from eco_compute.estimators.cost import (
    compare_models_cost,
    estimate_cost,
    estimate_cost_detailed,
    get_cheapest_models,
    get_model_pricing,
    list_supported_models as list_priced_models,
)
from eco_compute.estimators.energy import (
    estimate_energy,
    estimate_energy_detailed,
    get_default_factor,
    get_energy_factor,
    list_supported_models as list_energy_models,
)

__all__ = [
    # Energy
    "estimate_energy",
    "estimate_energy_detailed",
    "get_energy_factor",
    "get_default_factor",
    "list_energy_models",
    # Carbon
    "estimate_carbon",
    "estimate_carbon_detailed",
    "get_carbon_intensity",
    "get_default_intensity",
    "compare_regions",
    "get_cleanest_regions",
    "list_supported_regions",
    # Cost
    "estimate_cost",
    "estimate_cost_detailed",
    "get_model_pricing",
    "compare_models_cost",
    "get_cheapest_models",
    "list_priced_models",
]
