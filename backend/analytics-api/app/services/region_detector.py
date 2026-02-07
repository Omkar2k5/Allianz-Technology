"""
Region Detection Service

Detects datacenter regions from IP addresses and maps them to carbon intensity values.
"""

import requests
from typing import Optional, Dict, Tuple
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# Cloud region carbon intensity mapping (gCO2/kWh)
# Source: IEA, Ember Climate, Cloud Provider Sustainability Reports
REGION_CARBON_INTENSITY = {
    # AWS Regions
    "us-east-1": 390,      # Virginia, US
    "us-east-2": 450,      # Ohio, US
    "us-west-1": 200,      # California, US
    "us-west-2": 120,      # Oregon, US
    "ca-central-1": 10,    # Quebec, Canada
    "eu-west-1": 290,      # Ireland
    "eu-west-2": 250,      # London, UK
    "eu-central-1": 360,   # Frankfurt, Germany
    "eu-north-1": 15,      # Stockholm, Sweden
    "ap-southeast-1": 430, # Singapore
    "ap-south-1": 670,     # Mumbai, India
    "ap-northeast-1": 480, # Tokyo, Japan
    "sa-east-1": 90,       # São Paulo, Brazil
    
    # GCP Regions
    "us-central1": 390,    # Iowa, US
    "us-west1": 200,       # Oregon, US
    "europe-west1": 60,    # Belgium
    "europe-west4": 30,    # Netherlands
    "europe-north1": 80,   # Finland
    "asia-southeast1": 430,# Singapore
    "asia-south1": 670,    # Mumbai, India
    
    # Azure Regions
    "eastus": 390,         # Virginia, US
    "westus": 200,         # California, US
    "northeurope": 290,    # Ireland
    "westeurope": 360,     # Netherlands
    "francecentral": 60,   # France
    "norwayeast": 20,      # Norway
    
    # Default fallback
    "unknown": 400,        # Global average
}

# Major city to region mapping for geolocation results
CITY_TO_REGION = {
    "ashburn": "us-east-1",
    "virginia": "us-east-1",
    "columbus": "us-east-2",
    "ohio": "us-east-2",
    "san francisco": "us-west-1",
    "california": "us-west-1",
    "portland": "us-west-2",
    "oregon": "us-west-2",
    "seattle": "us-west-2",
    "montreal": "ca-central-1",
    "quebec": "ca-central-1",
    "dublin": "eu-west-1",
    "ireland": "eu-west-1",
    "london": "eu-west-2",
    "frankfurt": "eu-central-1",
    "germany": "eu-central-1",
    "stockholm": "eu-north-1",
    "sweden": "eu-north-1",
    "singapore": "ap-southeast-1",
    "mumbai": "ap-south-1",
    "india": "ap-south-1",
    "tokyo": "ap-northeast-1",
    "japan": "ap-northeast-1",
    "são paulo": "sa-east-1",
    "brazil": "sa-east-1",
}


class RegionDetector:
    """Detects datacenter regions from IP addresses"""
    
    def __init__(self):
        self.cache = {}
    
    @lru_cache(maxsize=1000)
    def detect_region_from_ip(self, ip_address: str) -> Tuple[Optional[str], int]:
        """
        Detect region from IP address using geolocation.
        
        Returns:
            Tuple of (region_code, carbon_intensity_gco2_kwh)
        """
        try:
            # Use ipapi.co for free IP geolocation
            response = requests.get(
                f"https://ipapi.co/{ip_address}/json/",
                timeout=2
            )
            
            if response.status_code == 200:
                data = response.json()
                city = data.get("city", "").lower()
                country = data.get("country_name", "").lower()
                
                # Try to map city to cloud region
                region = self._map_location_to_region(city, country)
                carbon_intensity = REGION_CARBON_INTENSITY.get(region, 400)
                
                logger.info(f"Detected region {region} (carbon: {carbon_intensity} gCO2/kWh) for IP {ip_address}")
                return region, carbon_intensity
            
        except Exception as e:
            logger.warning(f"Failed to geolocate IP {ip_address}: {e}")
        
        # Fallback to unknown region
        return "unknown", 400
    
    def _map_location_to_region(self, city: str, country: str) -> str:
        """Map city/country to cloud region code"""
        
        # Check city mapping first
        for key, region in CITY_TO_REGION.items():
            if key in city.lower():
                return region
        
        # Fallback to country-based estimation
        country_defaults = {
            "united states": "us-east-1",
            "canada": "ca-central-1",
            "united kingdom": "eu-west-2",
            "ireland": "eu-west-1",
            "germany": "eu-central-1",
            "france": "francecentral",
            "sweden": "eu-north-1",
            "norway": "norwayeast",
            "singapore": "ap-southeast-1",
            "india": "ap-south-1",
            "japan": "ap-northeast-1",
            "brazil": "sa-east-1",
        }
        
        return country_defaults.get(country.lower(), "unknown")
    
    def get_carbon_intensity(self, region: Optional[str]) -> int:
        """Get carbon intensity for a region"""
        if not region:
            return 400
        return REGION_CARBON_INTENSITY.get(region, 400)
    
    def detect_user_region(self) -> Tuple[Optional[str], int]:
        """
        Detect user's region from their public IP.
        This should be called once and cached.
        """
        try:
            # Get user's public IP
            response = requests.get("https://api.ipify.org?format=json", timeout=2)
            if response.status_code == 200:
                user_ip = response.json().get("ip")
                return self.detect_region_from_ip(user_ip)
        except Exception as e:
            logger.warning(f"Failed to detect user region: {e}")
        
        return "unknown", 400


# Global instance
region_detector = RegionDetector()
