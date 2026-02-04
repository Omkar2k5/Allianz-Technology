"""
Research-grade cloud region carbon intensity data
Sources: IEA, Ember Climate, AWS/GCP/Azure sustainability reports
"""

# AWS Regions - Complete list with grid carbon intensity
AWS_REGIONS = {
    # US Regions
    "us-east-1": {"country": "US", "city": "Virginia", "grid_carbon_g_kwh": 390, "lat": 37.4316, "lon": -78.6569},
    "us-east-2": {"country": "US", "city": "Ohio", "grid_carbon_g_kwh": 520, "lat": 40.4173, "lon": -82.9071},
    "us-west-1": {"country": "US", "city": "California", "grid_carbon_g_kwh": 200, "lat": 37.3541, "lon": -121.9552},
    "us-west-2": {"country": "US", "city": "Oregon", "grid_carbon_g_kwh": 120, "lat": 45.5945, "lon": -121.1786},
    
    # Europe
    "eu-west-1": {"country": "IE", "city": "Dublin", "grid_carbon_g_kwh": 290, "lat": 53.3498, "lon": -6.2603},
    "eu-west-2": {"country": "GB", "city": "London", "grid_carbon_g_kwh": 230, "lat": 51.5074, "lon": -0.1278},
    "eu-west-3": {"country": "FR", "city": "Paris", "grid_carbon_g_kwh": 60, "lat": 48.8566, "lon": 2.3522},
    "eu-central-1": {"country": "DE", "city": "Frankfurt", "grid_carbon_g_kwh": 360, "lat": 50.1109, "lon": 8.6821},
    "eu-central-2": {"country": "CH", "city": "Zurich", "grid_carbon_g_kwh": 30, "lat": 47.3769, "lon": 8.5417},
    "eu-north-1": {"country": "SE", "city": "Stockholm", "grid_carbon_g_kwh": 15, "lat": 59.3293, "lon": 18.0686},
    "eu-south-1": {"country": "IT", "city": "Milan", "grid_carbon_g_kwh": 280, "lat": 45.4642, "lon": 9.1900},
    "eu-south-2": {"country": "ES", "city": "Spain", "grid_carbon_g_kwh": 180, "lat": 40.4168, "lon": -3.7038},
    
    # Asia Pacific
    "ap-south-1": {"country": "IN", "city": "Mumbai", "grid_carbon_g_kwh": 670, "lat": 19.0760, "lon": 72.8777},
    "ap-south-2": {"country": "IN", "city": "Hyderabad", "grid_carbon_g_kwh": 670, "lat": 17.3850, "lon": 78.4867},
    "ap-southeast-1": {"country": "SG", "city": "Singapore", "grid_carbon_g_kwh": 430, "lat": 1.3521, "lon": 103.8198},
    "ap-southeast-2": {"country": "AU", "city": "Sydney", "grid_carbon_g_kwh": 650, "lat": -33.8688, "lon": 151.2093},
    "ap-southeast-3": {"country": "ID", "city": "Jakarta", "grid_carbon_g_kwh": 720, "lat": -6.2088, "lon": 106.8456},
    "ap-northeast-1": {"country": "JP", "city": "Tokyo", "grid_carbon_g_kwh": 470, "lat": 35.6762, "lon": 139.6503},
    "ap-northeast-2": {"country": "KR", "city": "Seoul", "grid_carbon_g_kwh": 420, "lat": 37.5665, "lon": 126.9780},
    "ap-northeast-3": {"country": "JP", "city": "Osaka", "grid_carbon_g_kwh": 470, "lat": 34.6937, "lon": 135.5023},
    "ap-east-1": {"country": "HK", "city": "Hong Kong", "grid_carbon_g_kwh": 650, "lat": 22.3193, "lon": 114.1694},
    
    # South America
    "sa-east-1": {"country": "BR", "city": "São Paulo", "grid_carbon_g_kwh": 90, "lat": -23.5505, "lon": -46.6333},
    
    # Middle East
    "me-south-1": {"country": "BH", "city": "Bahrain", "grid_carbon_g_kwh": 550, "lat": 26.0667, "lon": 50.5577},
    "me-central-1": {"country": "AE", "city": "UAE", "grid_carbon_g_kwh": 450, "lat": 25.2048, "lon": 55.2708},
    
    # Africa
    "af-south-1": {"country": "ZA", "city": "Cape Town", "grid_carbon_g_kwh": 850, "lat": -33.9249, "lon": 18.4241},
    
    # Canada
    "ca-central-1": {"country": "CA", "city": "Montreal", "grid_carbon_g_kwh": 30, "lat": 45.5017, "lon": -73.5673},
    "ca-west-1": {"country": "CA", "city": "Calgary", "grid_carbon_g_kwh": 600, "lat": 51.0447, "lon": -114.0719},
}

AWS_DEFAULTS = {
    "provider": "aws",
    "pue": 1.15,
    "renewable_procurement_pct": 100.0,
    "confidence": "medium",
    "source": "AWS Sustainability Report 2024 + IEA Grid Data"
}

# Google Cloud Regions - Higher confidence due to CFE% reporting
GCP_REGIONS = {
    # Americas
    "us-central1": {"country": "US", "city": "Iowa", "grid_carbon_g_kwh": 450, "cfe_pct": 96, "lat": 41.2619, "lon": -95.8608},
    "us-east1": {"country": "US", "city": "South Carolina", "grid_carbon_g_kwh": 350, "cfe_pct": 89, "lat": 33.1960, "lon": -79.7626},
    "us-east4": {"country": "US", "city": "Virginia", "grid_carbon_g_kwh": 390, "cfe_pct": 90, "lat": 37.4316, "lon": -78.6569},
    "us-west1": {"country": "US", "city": "Oregon", "grid_carbon_g_kwh": 120, "cfe_pct": 97, "lat": 45.5945, "lon": -121.1786},
    "us-west2": {"country": "US", "city": "Los Angeles", "grid_carbon_g_kwh": 250, "cfe_pct": 85, "lat": 34.0522, "lon": -118.2437},
    "us-west3": {"country": "US", "city": "Salt Lake City", "grid_carbon_g_kwh": 550, "cfe_pct": 78, "lat": 40.7608, "lon": -111.8910},
    "us-west4": {"country": "US", "city": "Las Vegas", "grid_carbon_g_kwh": 400, "cfe_pct": 82, "lat": 36.1699, "lon": -115.1398},
    "northamerica-northeast1": {"country": "CA", "city": "Montreal", "grid_carbon_g_kwh": 30, "cfe_pct": 99, "lat": 45.5017, "lon": -73.5673},
    "northamerica-northeast2": {"country": "CA", "city": "Toronto", "grid_carbon_g_kwh": 40, "cfe_pct": 98, "lat": 43.6532, "lon": -79.3832},
    "southamerica-east1": {"country": "BR", "city": "São Paulo", "grid_carbon_g_kwh": 90, "cfe_pct": 92, "lat": -23.5505, "lon": -46.6333},
    "southamerica-west1": {"country": "CL", "city": "Santiago", "grid_carbon_g_kwh": 350, "cfe_pct": 75, "lat": -33.4489, "lon": -70.6693},
    
    # Europe
    "europe-west1": {"country": "BE", "city": "Belgium", "grid_carbon_g_kwh": 160, "cfe_pct": 94, "lat": 50.8503, "lon": 4.3517},
    "europe-west2": {"country": "GB", "city": "London", "grid_carbon_g_kwh": 230, "cfe_pct": 88, "lat": 51.5074, "lon": -0.1278},
    "europe-west3": {"country": "DE", "city": "Frankfurt", "grid_carbon_g_kwh": 360, "cfe_pct": 85, "lat": 50.1109, "lon": 8.6821},
    "europe-west4": {"country": "NL", "city": "Netherlands", "grid_carbon_g_kwh": 380, "cfe_pct": 91, "lat": 52.3676, "lon": 4.9041},
    "europe-west6": {"country": "CH", "city": "Zurich", "grid_carbon_g_kwh": 30, "cfe_pct": 99, "lat": 47.3769, "lon": 8.5417},
    "europe-west8": {"country": "IT", "city": "Milan", "grid_carbon_g_kwh": 280, "cfe_pct": 80, "lat": 45.4642, "lon": 9.1900},
    "europe-west9": {"country": "FR", "city": "Paris", "grid_carbon_g_kwh": 60, "cfe_pct": 96, "lat": 48.8566, "lon": 2.3522},
    "europe-north1": {"country": "FI", "city": "Finland", "grid_carbon_g_kwh": 80, "cfe_pct": 98, "lat": 60.1699, "lon": 24.9384},
    "europe-southwest1": {"country": "ES", "city": "Madrid", "grid_carbon_g_kwh": 180, "cfe_pct": 87, "lat": 40.4168, "lon": -3.7038},
    
    # Asia Pacific
    "asia-east1": {"country": "TW", "city": "Taiwan", "grid_carbon_g_kwh": 500, "cfe_pct": 70, "lat": 25.0330, "lon": 121.5654},
    "asia-east2": {"country": "HK", "city": "Hong Kong", "grid_carbon_g_kwh": 650, "cfe_pct": 65, "lat": 22.3193, "lon": 114.1694},
    "asia-northeast1": {"country": "JP", "city": "Tokyo", "grid_carbon_g_kwh": 470, "cfe_pct": 75, "lat": 35.6762, "lon": 139.6503},
    "asia-northeast2": {"country": "JP", "city": "Osaka", "grid_carbon_g_kwh": 470, "cfe_pct": 75, "lat": 34.6937, "lon": 135.5023},
    "asia-northeast3": {"country": "KR", "city": "Seoul", "grid_carbon_g_kwh": 420, "cfe_pct": 72, "lat": 37.5665, "lon": 126.9780},
    "asia-south1": {"country": "IN", "city": "Mumbai", "grid_carbon_g_kwh": 670, "cfe_pct": 60, "lat": 19.0760, "lon": 72.8777},
    "asia-south2": {"country": "IN", "city": "Delhi", "grid_carbon_g_kwh": 670, "cfe_pct": 60, "lat": 28.7041, "lon": 77.1025},
    "asia-southeast1": {"country": "SG", "city": "Singapore", "grid_carbon_g_kwh": 430, "cfe_pct": 68, "lat": 1.3521, "lon": 103.8198},
    "asia-southeast2": {"country": "ID", "city": "Jakarta", "grid_carbon_g_kwh": 720, "cfe_pct": 55, "lat": -6.2088, "lon": 106.8456},
    "australia-southeast1": {"country": "AU", "city": "Sydney", "grid_carbon_g_kwh": 650, "cfe_pct": 70, "lat": -33.8688, "lon": 151.2093},
    "australia-southeast2": {"country": "AU", "city": "Melbourne", "grid_carbon_g_kwh": 650, "cfe_pct": 70, "lat": -37.8136, "lon": 144.9631},
    
    # Middle East
    "me-west1": {"country": "IL", "city": "Tel Aviv", "grid_carbon_g_kwh": 520, "cfe_pct": 65, "lat": 32.0853, "lon": 34.7818},
}

GCP_DEFAULTS = {
    "provider": "gcp",
    "pue": 1.10,
    "renewable_procurement_pct": 100.0,
    "confidence": "high",
    "source": "Google Cloud Carbon Footprint + CFE% data 2024"
}

# Azure Regions - Derived from country-level grid data
AZURE_REGIONS = {
    # Americas
    "eastus": {"country": "US", "city": "Virginia", "grid_carbon_g_kwh": 390, "lat": 37.3719, "lon": -79.8164},
    "eastus2": {"country": "US", "city": "Virginia", "grid_carbon_g_kwh": 390, "lat": 36.6681, "lon": -78.3889},
    "westus": {"country": "US", "city": "California", "grid_carbon_g_kwh": 200, "lat": 37.783, "lon": -122.417},
    "westus2": {"country": "US", "city": "Washington", "grid_carbon_g_kwh": 100, "lat": 47.233, "lon": -119.852},
    "westus3": {"country": "US", "city": "Arizona", "grid_carbon_g_kwh": 380, "lat": 33.448, "lon": -112.074},
    "centralus": {"country": "US", "city": "Iowa", "grid_carbon_g_kwh": 450, "lat": 41.5908, "lon": -93.6208},
    "northcentralus": {"country": "US", "city": "Illinois", "grid_carbon_g_kwh": 420, "lat": 41.8819, "lon": -87.6278},
    "southcentralus": {"country": "US", "city": "Texas", "grid_carbon_g_kwh": 400, "lat": 29.4167, "lon": -98.5},
    "canadacentral": {"country": "CA", "city": "Toronto", "grid_carbon_g_kwh": 40, "lat": 43.653, "lon": -79.383},
    "canadaeast": {"country": "CA", "city": "Quebec", "grid_carbon_g_kwh": 10, "lat": 46.817, "lon": -71.217},
    "brazilsouth": {"country": "BR", "city": "São Paulo", "grid_carbon_g_kwh": 90, "lat": -23.55, "lon": -46.633},
    
    # Europe
    "northeurope": {"country": "IE", "city": "Dublin", "grid_carbon_g_kwh": 290, "lat": 53.3478, "lon": -6.2597},
    "westeurope": {"country": "NL", "city": "Netherlands", "grid_carbon_g_kwh": 380, "lat": 52.3667, "lon": 4.8945},
    "uksouth": {"country": "GB", "city": "London", "grid_carbon_g_kwh": 230, "lat": 50.941, "lon": -0.799},
    "ukwest": {"country": "GB", "city": "Cardiff", "grid_carbon_g_kwh": 230, "lat": 51.481, "lon": -3.179},
    "francecentral": {"country": "FR", "city": "Paris", "grid_carbon_g_kwh": 60, "lat": 46.3772, "lon": 2.3730},
    "germanywestcentral": {"country": "DE", "city": "Frankfurt", "grid_carbon_g_kwh": 360, "lat": 50.1109, "lon": 8.6821},
    "norwayeast": {"country": "NO", "city": "Oslo", "grid_carbon_g_kwh": 20, "lat": 59.9139, "lon": 10.7522},
    "switzerlandnorth": {"country": "CH", "city": "Zurich", "grid_carbon_g_kwh": 30, "lat": 47.451, "lon": 8.564},
    "swedencentral": {"country": "SE", "city": "Gävle", "grid_carbon_g_kwh": 15, "lat": 60.6749, "lon": 17.1413},
    
    # Asia Pacific
    "eastasia": {"country": "HK", "city": "Hong Kong", "grid_carbon_g_kwh": 650, "lat": 22.267, "lon": 114.188},
    "southeastasia": {"country": "SG", "city": "Singapore", "grid_carbon_g_kwh": 430, "lat": 1.283, "lon": 103.833},
    "japaneast": {"country": "JP", "city": "Tokyo", "grid_carbon_g_kwh": 470, "lat": 35.68, "lon": 139.77},
    "japanwest": {"country": "JP", "city": "Osaka", "grid_carbon_g_kwh": 470, "lat": 34.6939, "lon": 135.5022},
    "koreacentral": {"country": "KR", "city": "Seoul", "grid_carbon_g_kwh": 420, "lat": 37.5665, "lon": 126.978},
    "australiaeast": {"country": "AU", "city": "Sydney", "grid_carbon_g_kwh": 650, "lat": -33.86, "lon": 151.2094},
    "australiasoutheast": {"country": "AU", "city": "Melbourne", "grid_carbon_g_kwh": 650, "lat": -37.8136, "lon": 144.9631},
    "centralindia": {"country": "IN", "city": "Pune", "grid_carbon_g_kwh": 670, "lat": 18.5822, "lon": 73.9197},
    "southindia": {"country": "IN", "city": "Chennai", "grid_carbon_g_kwh": 670, "lat": 12.9822, "lon": 80.1636},
    
    # Middle East & Africa
    "uaenorth": {"country": "AE", "city": "Dubai", "grid_carbon_g_kwh": 450, "lat": 25.266, "lon": 55.316},
    "southafricanorth": {"country": "ZA", "city": "Johannesburg", "grid_carbon_g_kwh": 850, "lat": -25.731, "lon": 28.218},
}

AZURE_DEFAULTS = {
    "provider": "azure",
    "pue": 1.18,
    "renewable_procurement_pct": 100.0,
    "confidence": "medium",
    "source": "Azure Sustainability + Country Grid Data (IEA)"
}

# Country-level grid carbon factors (IEA 2023)
GRID_CARBON_BY_COUNTRY = {
    "US": 390,
    "CA": 120,
    "BR": 90,
    "GB": 230,
    "FR": 60,
    "DE": 360,
    "IT": 280,
    "ES": 180,
    "SE": 15,
    "NO": 20,
    "FI": 80,
    "CH": 30,
    "NL": 380,
    "BE": 160,
    "IE": 290,
    "JP": 470,
    "KR": 420,
    "CN": 550,
    "IN": 670,
    "SG": 430,
    "AU": 650,
    "NZ": 120,
    "ZA": 850,
    "AE": 450,
    "IL": 520,
}
