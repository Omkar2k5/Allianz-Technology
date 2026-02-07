"""
SQLAlchemy database models
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey, Text, Uuid
# from sqlalchemy.dialects.postgresql import UUID # Removed for SQLite compatibility
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database.connection import Base



class User(Base):
    __tablename__ = "users"
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class App(Base):
    __tablename__ = "apps"
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    # team_id = Column(Uuid, ForeignKey('teams.id', ondelete='CASCADE')) # Removed team_id
    name = Column(String(255), nullable=False)
    description = Column(Text)
    environment = Column(String(50), default='production')
    api_key_hash = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GenAIRequest(Base):
    __tablename__ = "genai_requests"
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey('users.id'))
    
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    request_hash = Column(String(64), nullable=False)
    
    # Agent-specific metadata
    computer_name = Column(String(255))  # NEW
    
    model_name = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)
    
    tokens_input = Column(Integer, nullable=False)
    tokens_output = Column(Integer, nullable=False)
    tokens_total = Column(Integer, nullable=False)
    
    energy_wh = Column(Float)
    co2_g = Column(Float)
    
    region = Column(String(50))
    
    latency_ms = Column(Integer)
    
    policy_applied = Column(Boolean, default=False)
    
    meta_data = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)








class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey('users.id', ondelete='CASCADE'))
    
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class ModelSpec(Base):
    """AI Model specifications with environmental impact data"""
    __tablename__ = "model_specs"
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    
    # Model identification
    model_name = Column(String(255), unique=True, nullable=False, index=True)
    provider = Column(String(100), nullable=False)  # openai, anthropic, meta, etc.
    model_family = Column(String(100))  # llama, gpt, claude, etc.
    
    # Model characteristics
    parameters = Column(String(50))  # "70B", "405B", etc.
    architecture = Column(String(100))  # "transformer", "moe", etc.
    gpu_type = Column(String(100))  # "H100", "A100", "TPU v3"
    
    # Energy & Environmental Impact
    energy_j_per_token = Column(Float)  # Joules per token (decode)
    energy_kwh_per_1k_tokens = Column(Float)  # kWh per 1000 tokens
    co2_g_per_1k_tokens = Column(Float)  # grams CO2 per 1000 tokens (at 400g/kWh)
    
    # Training impact (one-time)
    training_energy_mwh = Column(Float, nullable=True)  # MWh for training
    training_co2_tons = Column(Float, nullable=True)  # Tons CO2 for training
    
    # Performance metrics
    quality_score = Column(Float, nullable=True)  # MMLU or similar benchmark
    latency_ms_per_token = Column(Float, nullable=True)  # Average latency
    
    # Pricing (USD)
    cost_per_1k_input_tokens = Column(Float, nullable=True)
    cost_per_1k_output_tokens = Column(Float, nullable=True)
    
    # Metadata
    data_source = Column(String(255))  # "TokenPowerBench 2025", "Patterson et al. 2021"
    is_measured = Column(Boolean, default=False)  # True if measured, False if estimated
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DatacenterInfo(Base):
    """Datacenter location and carbon intensity information"""
    __tablename__ = "datacenter_info"
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    
    # Identification
    provider = Column(String(100), nullable=False)  # openai, anthropic, google, etc.
    region_code = Column(String(50), nullable=False)  # us-east-1, us-west-2, etc.
    region_name = Column(String(255))  # "Virginia, USA", "Oregon, USA"
    
    # Location
    country = Column(String(100))
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Energy & Carbon
    carbon_intensity_g_per_kwh = Column(Float)  # gCO2/kWh for the grid
    renewable_percent = Column(Float)  # % renewable energy (0-100)
    pue = Column(Float, default=1.2)  # Power Usage Effectiveness
    
    # Energy sources breakdown
    coal_percent = Column(Float, nullable=True)
    natural_gas_percent = Column(Float, nullable=True)
    nuclear_percent = Column(Float, nullable=True)
    hydro_percent = Column(Float, nullable=True)
    wind_percent = Column(Float, nullable=True)
    solar_percent = Column(Float, nullable=True)
    
    # Metadata
    data_source = Column(String(255))  # "Electricity Maps", "EPA eGRID"
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)




