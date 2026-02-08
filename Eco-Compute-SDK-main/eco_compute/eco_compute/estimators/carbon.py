"""
Carbon emissions estimation module for LLM API calls.

This module provides deterministic, explainable carbon footprint
estimation based on energy consumption and regional carbon intensity.

Formula:
    co2_g = (energy_wh / 1000) × carbon_intensity

Where carbon_intensity is measured in gCO2 per kWh of electricity.
"""

from typing import Dict, Optional

# Regional carbon intensity values (gCO2 per kWh)
# These values represent the average carbon intensity of electricity
# generation in different regions/locations.
#
# Sources:
# - EPA eGRID (US regions)
# - European Environment Agency (EU regions)
# - IEA Electricity Maps
# - Cloud provider sustainability reports
#
# Note: Carbon intensity varies significantly by time of day and season.
# These are annual average values. For real-time accuracy, consider
# integrating with services like ElectricityMaps or WattTime.

DEFAULT_CARBON_INTENSITY: Dict[str, float] = {
    # US Regions (gCO2/kWh)
    "us-east": 400.0,          # Virginia, Ohio - mixed grid
    "us-east-1": 400.0,        # AWS N. Virginia
    "us-east-2": 450.0,        # AWS Ohio
    "us-west": 250.0,          # California, Oregon - cleaner grid
    "us-west-1": 230.0,        # AWS N. California
    "us-west-2": 150.0,        # AWS Oregon - hydro heavy
    "us-central": 500.0,       # Central US - coal heavy
    "us-south": 450.0,         # Texas - natural gas
    
    # European Regions
    "eu-west": 300.0,          # Ireland, UK, Netherlands
    "eu-west-1": 350.0,        # AWS Ireland
    "eu-west-2": 250.0,        # AWS London
    "eu-west-3": 60.0,         # AWS Paris - nuclear
    "eu-central": 350.0,       # Germany, Poland
    "eu-central-1": 350.0,     # AWS Frankfurt
    "eu-north": 50.0,          # Nordics - renewable heavy
    "eu-north-1": 30.0,        # AWS Stockholm
    "eu-south": 300.0,         # Southern Europe
    
    # Asia Pacific
    "ap-northeast": 500.0,     # Japan, Korea
    "ap-northeast-1": 450.0,   # AWS Tokyo
    "ap-northeast-2": 500.0,   # AWS Seoul
    "ap-southeast": 550.0,     # Singapore, Sydney
    "ap-southeast-1": 400.0,   # AWS Singapore
    "ap-southeast-2": 650.0,   # AWS Sydney
    "ap-south": 700.0,         # India - coal heavy
    "ap-south-1": 700.0,       # AWS Mumbai
    
    # Other Regions
    "canada": 150.0,           # Canada - hydro heavy
    "ca-central-1": 150.0,     # AWS Montreal
    "brazil": 100.0,           # Brazil - hydro heavy
    "sa-east-1": 100.0,        # AWS São Paulo
    "middle-east": 500.0,      # Middle East
    "africa": 600.0,           # Africa average
    "china": 600.0,            # China - coal heavy
    "china-east": 600.0,
    "china-north": 650.0,
    
    # Cloud Provider Specific
    "azure-east-us": 400.0,
    "azure-west-us": 250.0,
    "azure-north-europe": 300.0,
    "azure-west-europe": 350.0,
    "gcp-us-central1": 450.0,
    "gcp-us-east1": 400.0,
    "gcp-us-west1": 150.0,
    "gcp-europe-west1": 250.0,
    "gcp-europe-north1": 50.0,
    
    # Special values
    "renewable": 20.0,         # 100% renewable powered
    "nuclear": 15.0,           # Nuclear powered
    "hydro": 25.0,             # Hydroelectric
    "solar": 40.0,             # Solar with storage
    "wind": 15.0,              # Wind powered
    
    # Default fallback (global average)
    "_default": 400.0,
}


def get_carbon_intensity(
    region: str,
    custom_intensities: Optional[Dict[str, float]] = None
) -> float:
    """
    Get the carbon intensity for a specific region.
    
    Looks up the carbon intensity (gCO2/kWh) for the given region,
    falling back to a global average if not found.
    
    Args:
        region: Region identifier (e.g., 'us-east', 'eu-west-1')
        custom_intensities: Optional custom intensities to override defaults
    
    Returns:
        Carbon intensity in gCO2 per kWh
    
    Example:
        >>> get_carbon_intensity("us-west-2")
        150.0
        
        >>> get_carbon_intensity("eu-north-1")
        30.0
    """
    # Normalize region name
    region_lower = region.lower().strip()
    
    # Check custom intensities first
    if custom_intensities:
        if region_lower in custom_intensities:
            return custom_intensities[region_lower]
        if region in custom_intensities:
            return custom_intensities[region]
    
    # Check default intensities
    if region_lower in DEFAULT_CARBON_INTENSITY:
        return DEFAULT_CARBON_INTENSITY[region_lower]
    if region in DEFAULT_CARBON_INTENSITY:
        return DEFAULT_CARBON_INTENSITY[region]
    
    # Try partial matching
    for key in DEFAULT_CARBON_INTENSITY:
        if region_lower.startswith(key) or key.startswith(region_lower):
            return DEFAULT_CARBON_INTENSITY[key]
    
    # Return default
    return DEFAULT_CARBON_INTENSITY["_default"]


def estimate_carbon(
    energy_wh: float,
    region: str = "us-east",
    custom_intensities: Optional[Dict[str, float]] = None
) -> float:
    """
    Estimate carbon emissions for energy consumption.
    
    Uses the formula:
        co2_g = (energy_wh / 1000) × carbon_intensity
    
    Energy is in Wh, carbon intensity is in gCO2/kWh, so we divide
    energy by 1000 to convert to kWh.
    
    Args:
        energy_wh: Energy consumption in watt-hours
        region: Region for carbon intensity lookup
        custom_intensities: Optional custom intensities
    
    Returns:
        Estimated CO2 emissions in grams
    
    Example:
        >>> estimate_carbon(1.0, "us-east")
        0.4  # grams CO2
        
        >>> estimate_carbon(1.0, "eu-north-1")
        0.03  # grams CO2 (Sweden, clean grid)
    """
    if energy_wh <= 0:
        return 0.0
    
    intensity = get_carbon_intensity(region, custom_intensities)
    
    # Convert Wh to kWh and multiply by intensity
    co2_g = (energy_wh / 1000.0) * intensity
    
    return round(co2_g, 10)


def estimate_carbon_detailed(
    energy_wh: float,
    region: str = "us-east",
    custom_intensities: Optional[Dict[str, float]] = None
) -> Dict[str, float]:
    """
    Estimate carbon emissions with detailed breakdown.
    
    Args:
        energy_wh: Energy consumption in watt-hours
        region: Region for carbon intensity lookup
        custom_intensities: Optional custom intensities
    
    Returns:
        Dictionary with carbon breakdown:
        - co2_g: CO2 emissions in grams
        - co2_kg: CO2 emissions in kilograms
        - carbon_intensity: Carbon intensity used
        - energy_kwh: Energy in kilowatt-hours
    
    Example:
        >>> estimate_carbon_detailed(5.0, "us-west-2")
        {
            'co2_g': 0.75,
            'co2_kg': 0.00075,
            'carbon_intensity': 150.0,
            'energy_kwh': 0.005
        }
    """
    if energy_wh <= 0:
        return {
            "co2_g": 0.0,
            "co2_kg": 0.0,
            "carbon_intensity": get_carbon_intensity(region, custom_intensities),
            "energy_kwh": 0.0
        }
    
    intensity = get_carbon_intensity(region, custom_intensities)
    energy_kwh = energy_wh / 1000.0
    co2_g = energy_kwh * intensity
    co2_kg = co2_g / 1000.0
    
    return {
        "co2_g": round(co2_g, 10),
        "co2_kg": round(co2_kg, 13),
        "carbon_intensity": intensity,
        "energy_kwh": round(energy_kwh, 10)
    }


def compare_regions(
    energy_wh: float,
    regions: Optional[list] = None
) -> Dict[str, float]:
    """
    Compare carbon emissions across multiple regions.
    
    Useful for showing the impact of region selection on carbon footprint.
    
    Args:
        energy_wh: Energy consumption in watt-hours
        regions: List of regions to compare (default: common regions)
    
    Returns:
        Dictionary mapping region names to CO2 emissions (grams)
    
    Example:
        >>> compare_regions(1.0, ["us-east", "eu-north-1", "ap-south-1"])
        {
            'us-east': 0.4,
            'eu-north-1': 0.03,
            'ap-south-1': 0.7
        }
    """
    if regions is None:
        regions = ["us-east", "us-west-2", "eu-west-1", "eu-north-1", "ap-southeast-1"]
    
    return {
        region: estimate_carbon(energy_wh, region)
        for region in regions
    }


def list_supported_regions() -> list:
    """
    List all regions with defined carbon intensities.
    
    Returns:
        List of region identifiers
    """
    return [k for k in DEFAULT_CARBON_INTENSITY.keys() if k != "_default"]


def get_cleanest_regions(top_n: int = 5) -> list:
    """
    Get the cleanest (lowest carbon) regions.
    
    Args:
        top_n: Number of regions to return
    
    Returns:
        List of (region, intensity) tuples sorted by intensity
    """
    sorted_regions = sorted(
        [(k, v) for k, v in DEFAULT_CARBON_INTENSITY.items() if k != "_default"],
        key=lambda x: x[1]
    )
    return sorted_regions[:top_n]


def get_default_intensity() -> float:
    """
    Get the default carbon intensity used for unknown regions.
    
    Returns:
        Default carbon intensity in gCO2 per kWh
    """
    return DEFAULT_CARBON_INTENSITY["_default"]
