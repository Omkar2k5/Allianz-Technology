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


class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    organization = Column(String(255))
    subscription_tier = Column(String(50), default='free')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class App(Base):
    __tablename__ = "apps"
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    team_id = Column(Uuid, ForeignKey('teams.id', ondelete='CASCADE'))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    environment = Column(String(50), default='production')
    api_key_hash = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Agent(Base):
    """Desktop monitoring agent installed on a computer"""
    __tablename__ = "agents"
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    computer_id = Column(String(255), unique=True, nullable=False)
    computer_name = Column(String(255))
    team_id = Column(Uuid, ForeignKey('teams.id', ondelete='CASCADE'))
    agent_version = Column(String(50))
    os_version = Column(String(100))
    status = Column(String(20), default='active')
    last_heartbeat = Column(DateTime)
    installed_by = Column(Uuid, ForeignKey('users.id'))
    installed_at = Column(DateTime, default=datetime.utcnow)
    api_key_hash = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GenAIRequest(Base):
    __tablename__ = "genai_requests"
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    app_id = Column(Uuid, ForeignKey('apps.id', ondelete='CASCADE'))
    model_id = Column(Uuid, ForeignKey('models.id'))
    user_id = Column(Uuid, ForeignKey('users.id'))
    agent_id = Column(Uuid, ForeignKey('agents.id'))  # NEW: Agent tracking
    
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    request_hash = Column(String(64), nullable=False)
    
    # Agent-specific metadata
    computer_name = Column(String(255))  # NEW
    process_name = Column(String(255))   # NEW
    
    model_name = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)
    
    tokens_input = Column(Integer, nullable=False)
    tokens_output = Column(Integer, nullable=False)
    tokens_total = Column(Integer, nullable=False)
    
    energy_wh = Column(Float)
    co2_g = Column(Float)
    
    region = Column(String(50))
    carbon_intensity = Column(Float)
    
    latency_ms = Column(Integer)
    
    use_case = Column(String(100))
    risk_level = Column(String(20))
    
    policy_applied = Column(Boolean, default=False)
    policy_action = Column(String(50))
    
    cost_usd = Column(Float)
    cost_usd = Column(Float)
    meta_data = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Model(Base):
    __tablename__ = "models"
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    provider = Column(String(50), nullable=False)
    parameters = Column(String(50))
    energy_per_1k_tokens = Column(Float, nullable=False)
    co2_per_1k_tokens = Column(Float)
    efficiency_score = Column(String(5))
    tokens_per_sec = Column(Integer)
    is_active = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    team_id = Column(Uuid, ForeignKey('teams.id', ondelete='CASCADE'))
    app_id = Column(Uuid, ForeignKey('apps.id', ondelete='CASCADE'))
    
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    metric_name = Column(String(100))
    metric_value = Column(Float)
    threshold_value = Column(Float)
    
    status = Column(String(20), default='active')
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    resolved_at = Column(DateTime)
    
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    team_id = Column(Uuid, ForeignKey('teams.id', ondelete='CASCADE'))
    app_id = Column(Uuid, ForeignKey('apps.id', ondelete='CASCADE'))
    
    recommendation_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    estimated_co2_savings_g = Column(Float)
    estimated_cost_savings_usd = Column(Float)
    estimated_energy_savings_wh = Column(Float)
    
    difficulty = Column(String(20))
    implementation_steps = Column(Text)
    
    status = Column(String(20), default='pending')
    applied_at = Column(DateTime)
    
    applied_at = Column(DateTime)
    
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


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


class UserModelRecommendation(Base):
    """Store personalized model recommendations for users"""
    __tablename__ = "user_model_recommendations"
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Current usage analysis
    current_model = Column(String(255))
    avg_tokens_per_request = Column(Integer)
    requests_per_day = Column(Integer)
    current_co2_g_per_day = Column(Float)
    current_energy_kwh_per_day = Column(Float)
    
    # Recommended alternative
    recommended_model = Column(String(255))
    projected_co2_g_per_day = Column(Float)
    projected_energy_kwh_per_day = Column(Float)
    
    # Savings
    co2_savings_percent = Column(Float)
    energy_savings_percent = Column(Float)
    quality_difference_percent = Column(Float)  # Negative if lower quality
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

