"""
Carbon calculation engine

Calculates CO₂ emissions based on energy consumption and regional carbon intensity
"""

from typing import Dict

# Regional carbon intensity (kg CO₂ per kWh)
CARBON_INTENSITY_BY_REGION: Dict[str, float] = {
    # AWS Regions
    "us-east-1": 0.4,      # US East (N. Virginia) - coal-heavy
    "us-east-2": 0.35,     # US East (Ohio)
    "us-west-1": 0.25,     # US West (N. California)
    "us-west-2": 0.2,      # US West (Oregon) - hydro-heavy
    
    "eu-west-1": 0.12,     # EU West (Ireland) - wind-heavy
    "eu-west-2": 0.15,     # EU West (London)
    "eu-west-3": 0.1,      # EU West (Paris) - nuclear-heavy
    "eu-central-1": 0.15,  # EU Central (Frankfurt)
    
    "ap-southeast-1": 0.5, # Asia Pacific (Singapore)
    "ap-southeast-2": 0.45,# Asia Pacific (Sydney)
    "ap-northeast-1": 0.35,# Asia Pacific (Tokyo)
    
    "ca-central-1": 0.05,  # Canada (Central) - hydro-heavy
    
    # Azure Regions
    "eastus": 0.4,
    "westus": 0.2,
    "northeurope": 0.12,
    "westeurope": 0.15,
    
    # GCP Regions
    "us-central1": 0.3,
    "us-west1": 0.2,
    "europe-west1": 0.12,
    "europe-west4": 0.1,
    
    # Default fallback
    "default": 0.3
}


def calculate_carbon(energy_wh: float, region: str) -> float:
    """
    Calculate CO₂ emissions in grams
    
    Args:
        energy_wh: Energy consumption in Watt-hours
        region: Cloud region code
        
    Returns:
        CO₂ emissions in grams
        
    Formula:
        CO₂ (g) = Energy (Wh) × Carbon_Intensity (kg CO₂/kWh) × 1000 / 1000
                = Energy (Wh) × Carbon_Intensity (kg CO₂/kWh)
    """
    
    # Get carbon intensity for region
    carbon_intensity = CARBON_INTENSITY_BY_REGION.get(
        region.lower(), 
        CARBON_INTENSITY_BY_REGION["default"]
    )
    
    # Convert Wh to kWh
    energy_kwh = energy_wh / 1000.0
    
    # Calculate CO₂ in kg
    co2_kg = energy_kwh * carbon_intensity
    
    # Convert to grams
    co2_g = co2_kg * 1000
    
    return round(co2_g, 4)


def get_region_renewable_percentage(region: str) -> float:
    """
    Get renewable energy percentage for a region
    
    Args:
        region: Cloud region code
        
    Returns:
        Renewable energy percentage (0-100)
    """
    renewable_map = {
        "us-west-2": 65.0,
        "eu-west-3": 85.0,
        "ca-central-1": 95.0,
        "eu-west-1": 70.0,
        "us-east-1": 25.0,
        "default": 30.0
    }
    
    return renewable_map.get(region.lower(), renewable_map["default"])


def recommend_low_carbon_region(current_region: str) -> Dict[str, any]:
    """
    Recommend a lower-carbon alternative region
    
    Args:
        current_region: Current cloud region
        
    Returns:
        Dict with recommendation details
    """
    current_intensity = CARBON_INTENSITY_BY_REGION.get(
        current_region.lower(),
        CARBON_INTENSITY_BY_REGION["default"]
    )
    
    # Find regions with lower carbon intensity
    better_regions = [
        (region, intensity)
        for region, intensity in CARBON_INTENSITY_BY_REGION.items()
        if intensity < current_intensity and region != "default"
    ]
    
    if not better_regions:
        return {
            "has_recommendation": False,
            "message": "Current region is already optimal"
        }
    
    # Get best region
    best_region, best_intensity = min(better_regions, key=lambda x: x[1])
    
    # Calculate potential savings
    savings_percent = ((current_intensity - best_intensity) / current_intensity) * 100
    
    return {
        "has_recommendation": True,
        "current_region": current_region,
        "current_intensity": current_intensity,
        "recommended_region": best_region,
        "recommended_intensity": best_intensity,
        "savings_percent": round(savings_percent, 1),
        "message": f"Migrating to {best_region} could reduce CO₂ by {round(savings_percent, 1)}%"
    }
