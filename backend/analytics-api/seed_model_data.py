"""
Seed database with AI model specifications from research
Sources:
- TokenPowerBench 2025
- Patterson et al. 2021 (GPT-3 training)
- MLPerf Power benchmarks
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.database.connection import SessionLocal, engine, Base
from app.database.models import ModelSpec, DatacenterInfo
import uuid

# Create tables
Base.metadata.create_all(bind=engine)

def seed_model_specs():
    """Seed model specifications with environmental impact data"""
    db = SessionLocal()
    
    models_data = [
        # Open Models - Measured (TokenPowerBench 2025)
        {
            "model_name": "llama-3-1b",
            "provider": "meta",
            "model_family": "llama",
            "parameters": "1B",
            "architecture": "transformer",
            "gpu_type": "H100",
            "energy_j_per_token": 0.5,  # Mid-range of 0.1-1 J/token
            "energy_kwh_per_1k_tokens": 0.0005,
            "co2_g_per_1k_tokens": 0.2,  # At 400g/kWh
            "quality_score": 65.0,
            "data_source": "TokenPowerBench 2025",
            "is_measured": True,
            "notes": "Measured on H100 with vLLM, range: 0.1-1 J/token"
        },
        {
            "model_name": "llama-3-8b",
            "provider": "meta",
            "model_family": "llama",
            "parameters": "8B",
            "architecture": "transformer",
            "gpu_type": "H100",
            "energy_j_per_token": 2.0,
            "energy_kwh_per_1k_tokens": 0.002,
            "co2_g_per_1k_tokens": 0.8,
            "quality_score": 75.0,
            "data_source": "Derived from TokenPowerBench (similar to Mistral-7B)",
            "is_measured": False,
            "notes": "Similar architecture to Mistral-7B"
        },
        {
            "model_name": "llama-3-70b",
            "provider": "meta",
            "model_family": "llama",
            "parameters": "70B",
            "architecture": "transformer",
            "gpu_type": "H100 (4x/node)",
            "energy_j_per_token": 7.0,  # ~7x llama-3-1b per TokenPowerBench
            "energy_kwh_per_1k_tokens": 0.007,
            "co2_g_per_1k_tokens": 2.8,
            "quality_score": 85.0,
            "data_source": "TokenPowerBench 2025 (super-linear scaling)",
            "is_measured": True,
            "notes": "vLLM/TensorRT-LLM, ~7x energy of 1B model"
        },
        {
            "model_name": "llama-3-405b",
            "provider": "meta",
            "model_family": "llama",
            "parameters": "405B",
            "architecture": "transformer",
            "gpu_type": "16x H100",
            "energy_j_per_token": 175.0,  # Average of 116-235 range
            "energy_kwh_per_1k_tokens": 0.175,
            "co2_g_per_1k_tokens": 70.0,
            "quality_score": 92.0,
            "data_source": "TokenPowerBench 2025",
            "is_measured": True,
            "notes": "Tensor Parallel (TP16/PP1), FP8 saves ~30%, range: 116-235 J/token"
        },
        {
            "model_name": "llama-2-70b",
            "provider": "meta",
            "model_family": "llama",
            "parameters": "70B",
            "architecture": "transformer",
            "gpu_type": "A100",
            "energy_j_per_token": 111.4,
            "energy_kwh_per_1k_tokens": 0.11,
            "co2_g_per_1k_tokens": 44.0,
            "quality_score": 82.0,
            "data_source": "MLPerf Inference v5.1 Power",
            "is_measured": True,
            "notes": "QA inference task, measured energy per sample"
        },
        {
            "model_name": "mistral-7b",
            "provider": "mistral",
            "model_family": "mistral",
            "parameters": "7B",
            "architecture": "transformer",
            "gpu_type": "A100/H100",
            "energy_j_per_token": 1.5,  # Mid-range of 1-2 J/token
            "energy_kwh_per_1k_tokens": 0.0015,
            "co2_g_per_1k_tokens": 0.6,
            "quality_score": 76.0,
            "data_source": "TokenPowerBench + MLPerf aligned",
            "is_measured": False,
            "notes": "Similar to llama-8b, range: 1-2 J/token"
        },
        {
            "model_name": "mixtral-8x7b",
            "provider": "mistral",
            "model_family": "mixtral",
            "parameters": "MoE (8x7B, ~8B active)",
            "architecture": "moe",
            "gpu_type": "H100",
            "energy_j_per_token": 5.0,  # Mid-range of 1-10 J/token
            "energy_kwh_per_1k_tokens": 0.005,
            "co2_g_per_1k_tokens": 2.0,
            "quality_score": 80.0,
            "data_source": "TokenPowerBench 2025",
            "is_measured": True,
            "notes": "Sparse MoE routing → 2-3x savings vs dense, range: 1-10 J/token"
        },
        {
            "model_name": "qwen-32b",
            "provider": "alibaba",
            "model_family": "qwen",
            "parameters": "32B",
            "architecture": "transformer",
            "gpu_type": "A100/H100",
            "energy_j_per_token": 10.0,
            "energy_kwh_per_1k_tokens": 0.01,
            "co2_g_per_1k_tokens": 4.0,
            "quality_score": 78.0,
            "data_source": "Scaled from TokenPowerBench",
            "is_measured": False,
            "notes": "Derived from scaling laws"
        },
        
        # Proprietary Models - Training Data (Patterson et al. 2021)
        {
            "model_name": "gpt-3",
            "provider": "openai",
            "model_family": "gpt",
            "parameters": "175B",
            "architecture": "transformer",
            "gpu_type": "1024x V100",
            "energy_j_per_token": 48.0,
            "energy_kwh_per_1k_tokens": 0.048,
            "co2_g_per_1k_tokens": 19.2,
            "training_energy_mwh": 1287.0,
            "training_co2_tons": 552.0,
            "quality_score": 70.0,
            "cost_per_1k_input_tokens": 0.0015,
            "cost_per_1k_output_tokens": 0.002,
            "data_source": "Patterson et al. 2021",
            "is_measured": False,
            "notes": "Training: 1,287 MWh, 552 tons CO2, PUE 1.1-1.55, US avg grid"
        },
        {
            "model_name": "t5-xxl-11b",
            "provider": "google",
            "model_family": "t5",
            "parameters": "11B",
            "architecture": "transformer",
            "gpu_type": "TPU v3",
            "energy_j_per_token": 5.0,
            "energy_kwh_per_1k_tokens": 0.005,
            "co2_g_per_1k_tokens": 2.0,
            "training_energy_mwh": 86.0,
            "quality_score": 72.0,
            "data_source": "Patterson et al. 2021",
            "is_measured": False,
            "notes": "Training: 86 MWh on TPU v3"
        },
        {
            "model_name": "meena-2.6b",
            "provider": "google",
            "model_family": "meena",
            "parameters": "2.6B",
            "architecture": "transformer",
            "gpu_type": "TPU",
            "energy_j_per_token": 2.0,
            "energy_kwh_per_1k_tokens": 0.002,
            "co2_g_per_1k_tokens": 0.8,
            "training_energy_mwh": 232.0,
            "quality_score": 68.0,
            "data_source": "Patterson et al. 2021",
            "is_measured": False,
            "notes": "Training: 232 MWh on TPU"
        },
        
        # Proprietary Models - Estimates (clearly labeled)
        {
            "model_name": "gpt-3.5-turbo",
            "provider": "openai",
            "model_family": "gpt",
            "parameters": "175B",
            "architecture": "transformer",
            "gpu_type": "A100",
            "energy_j_per_token": 4.0,
            "energy_kwh_per_1k_tokens": 0.004,
            "co2_g_per_1k_tokens": 1.6,
            "quality_score": 75.0,
            "cost_per_1k_input_tokens": 0.0005,
            "cost_per_1k_output_tokens": 0.0015,
            "data_source": "Scaled from GPT-3",
            "is_measured": False,
            "notes": "Optimized inference stack, estimated"
        },
        {
            "model_name": "gpt-4",
            "provider": "openai",
            "model_family": "gpt",
            "parameters": "~1.7T (estimated)",
            "architecture": "transformer",
            "gpu_type": "A100/H100",
            "energy_j_per_token": 20.0,
            "energy_kwh_per_1k_tokens": 0.02,
            "co2_g_per_1k_tokens": 8.0,
            "quality_score": 86.0,
            "cost_per_1k_input_tokens": 0.03,
            "cost_per_1k_output_tokens": 0.06,
            "data_source": "FLOPs-scaled estimates",
            "is_measured": False,
            "notes": "Batched inference, range: 0.01-0.03 kWh/1k, estimated"
        },
        {
            "model_name": "gpt-4-turbo",
            "provider": "openai",
            "model_family": "gpt",
            "parameters": "~1.7T (estimated)",
            "architecture": "transformer",
            "gpu_type": "H100",
            "energy_j_per_token": 10.0,
            "energy_kwh_per_1k_tokens": 0.01,
            "co2_g_per_1k_tokens": 4.0,
            "quality_score": 87.0,
            "cost_per_1k_input_tokens": 0.01,
            "cost_per_1k_output_tokens": 0.03,
            "data_source": "Estimated from GPT-4",
            "is_measured": False,
            "notes": "Faster inference than GPT-4, estimated"
        },
        {
            "model_name": "gpt-4o",
            "provider": "openai",
            "model_family": "gpt",
            "parameters": "unknown",
            "architecture": "transformer",
            "gpu_type": "H100",
            "energy_j_per_token": 0.3,
            "energy_kwh_per_1k_tokens": 0.0003,
            "co2_g_per_1k_tokens": 0.12,
            "quality_score": 88.0,
            "cost_per_1k_input_tokens": 0.005,
            "cost_per_1k_output_tokens": 0.015,
            "data_source": "Query-based public estimates",
            "is_measured": False,
            "notes": "0.3 Wh/query, ~1k tokens/query, highly optimized, estimated"
        },
        {
            "model_name": "claude-3-haiku",
            "provider": "anthropic",
            "model_family": "claude",
            "parameters": "~20-200B (estimated)",
            "architecture": "transformer",
            "gpu_type": "TPU/A100",
            "energy_j_per_token": 1.0,
            "energy_kwh_per_1k_tokens": 0.001,
            "co2_g_per_1k_tokens": 0.4,
            "quality_score": 75.0,
            "cost_per_1k_input_tokens": 0.00025,
            "cost_per_1k_output_tokens": 0.00125,
            "data_source": "Latency-based estimates",
            "is_measured": False,
            "notes": "128 tokens/sec, efficiency-focused, likely TPU, estimated"
        },
        {
            "model_name": "claude-3-sonnet",
            "provider": "anthropic",
            "model_family": "claude",
            "parameters": "~300B (estimated)",
            "architecture": "transformer",
            "gpu_type": "TPU/A100",
            "energy_j_per_token": 5.0,
            "energy_kwh_per_1k_tokens": 0.005,
            "co2_g_per_1k_tokens": 2.0,
            "quality_score": 82.0,
            "cost_per_1k_input_tokens": 0.003,
            "cost_per_1k_output_tokens": 0.015,
            "data_source": "Scaled estimates",
            "is_measured": False,
            "notes": "Balance of speed and quality, estimated"
        },
        {
            "model_name": "claude-3-opus",
            "provider": "anthropic",
            "model_family": "claude",
            "parameters": "~500B (estimated)",
            "architecture": "transformer",
            "gpu_type": "TPU/A100",
            "energy_j_per_token": 15.0,
            "energy_kwh_per_1k_tokens": 0.015,
            "co2_g_per_1k_tokens": 6.0,
            "quality_score": 86.0,
            "cost_per_1k_input_tokens": 0.015,
            "cost_per_1k_output_tokens": 0.075,
            "data_source": "Scaled estimates",
            "is_measured": False,
            "notes": "Highest quality Claude model, estimated"
        }
    ]
    
    for model_data in models_data:
        # Check if model already exists
        existing = db.query(ModelSpec).filter(ModelSpec.model_name == model_data["model_name"]).first()
        if existing:
            print(f"⏭️  Skipping {model_data['model_name']} (already exists)")
            continue
            
        model = ModelSpec(**model_data)
        db.add(model)
        print(f"✅ Added {model_data['model_name']}")
    
    db.commit()
    print(f"\n✅ Seeded {len(models_data)} model specifications")
    db.close()


def seed_datacenter_info():
    """Seed datacenter carbon intensity data"""
    db = SessionLocal()
    
    datacenters_data = [
        # US Regions
        {
            "provider": "openai",
            "region_code": "us-east-1",
            "region_name": "Virginia, USA",
            "country": "USA",
            "carbon_intensity_g_per_kwh": 400.0,
            "renewable_percent": 30.0,
            "pue": 1.2,
            "coal_percent": 20.0,
            "natural_gas_percent": 45.0,
            "nuclear_percent": 30.0,
            "hydro_percent": 3.0,
            "wind_percent": 1.0,
            "solar_percent": 1.0,
            "data_source": "EPA eGRID 2023"
        },
        {
            "provider": "openai",
            "region_code": "us-west-2",
            "region_name": "Oregon, USA",
            "country": "USA",
            "carbon_intensity_g_per_kwh": 100.0,
            "renewable_percent": 80.0,
            "pue": 1.1,
            "coal_percent": 5.0,
            "natural_gas_percent": 15.0,
            "nuclear_percent": 0.0,
            "hydro_percent": 60.0,
            "wind_percent": 15.0,
            "solar_percent": 5.0,
            "data_source": "EPA eGRID 2023"
        },
        {
            "provider": "anthropic",
            "region_code": "us-west-1",
            "region_name": "California, USA",
            "country": "USA",
            "carbon_intensity_g_per_kwh": 200.0,
            "renewable_percent": 60.0,
            "pue": 1.15,
            "coal_percent": 0.0,
            "natural_gas_percent": 40.0,
            "nuclear_percent": 10.0,
            "hydro_percent": 15.0,
            "wind_percent": 15.0,
            "solar_percent": 20.0,
            "data_source": "EPA eGRID 2023"
        },
        # Europe
        {
            "provider": "openai",
            "region_code": "eu-west-1",
            "region_name": "Ireland",
            "country": "Ireland",
            "carbon_intensity_g_per_kwh": 300.0,
            "renewable_percent": 45.0,
            "pue": 1.15,
            "coal_percent": 5.0,
            "natural_gas_percent": 50.0,
            "nuclear_percent": 0.0,
            "hydro_percent": 5.0,
            "wind_percent": 35.0,
            "solar_percent": 5.0,
            "data_source": "Electricity Maps 2024"
        },
        # Clean energy regions
        {
            "provider": "google",
            "region_code": "europe-north1",
            "region_name": "Finland",
            "country": "Finland",
            "carbon_intensity_g_per_kwh": 80.0,
            "renewable_percent": 85.0,
            "pue": 1.08,
            "coal_percent": 5.0,
            "natural_gas_percent": 10.0,
            "nuclear_percent": 35.0,
            "hydro_percent": 25.0,
            "wind_percent": 20.0,
            "solar_percent": 5.0,
            "data_source": "Electricity Maps 2024"
        }
    ]
    
    for dc_data in datacenters_data:
        # Check if datacenter already exists
        existing = db.query(DatacenterInfo).filter(
            DatacenterInfo.provider == dc_data["provider"],
            DatacenterInfo.region_code == dc_data["region_code"]
        ).first()
        if existing:
            print(f"⏭️  Skipping {dc_data['provider']}/{dc_data['region_code']} (already exists)")
            continue
            
        datacenter = DatacenterInfo(**dc_data)
        db.add(datacenter)
        print(f"✅ Added {dc_data['provider']}/{dc_data['region_code']}")
    
    db.commit()
    print(f"\n✅ Seeded {len(datacenters_data)} datacenter records")
    db.close()


if __name__ == "__main__":
    print("🌱 Seeding database with model specifications and datacenter data...\n")
    seed_model_specs()
    print()
    seed_datacenter_info()
    print("\n✅ Database seeding complete!")
