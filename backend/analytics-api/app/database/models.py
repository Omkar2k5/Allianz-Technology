"""
SQLAlchemy database models
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database.connection import Base


class Team(Base):
    __tablename__ = "teams"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    organization = Column(String(255))
    subscription_tier = Column(String(50), default='free')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class App(Base):
    __tablename__ = "apps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id', ondelete='CASCADE'))
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
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    computer_id = Column(String(255), unique=True, nullable=False)
    computer_name = Column(String(255))
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id', ondelete='CASCADE'))
    agent_version = Column(String(50))
    os_version = Column(String(100))
    status = Column(String(20), default='active')
    last_heartbeat = Column(DateTime)
    installed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    installed_at = Column(DateTime, default=datetime.utcnow)
    api_key_hash = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GenAIRequest(Base):
    __tablename__ = "genai_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    app_id = Column(UUID(as_uuid=True), ForeignKey('apps.id', ondelete='CASCADE'))
    model_id = Column(UUID(as_uuid=True), ForeignKey('models.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id'))  # NEW: Agent tracking
    
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
    metadata = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Model(Base):
    __tablename__ = "models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    provider = Column(String(50), nullable=False)
    parameters = Column(String(50))
    energy_per_1k_tokens = Column(Float, nullable=False)
    co2_per_1k_tokens = Column(Float)
    efficiency_score = Column(String(5))
    tokens_per_sec = Column(Integer)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id', ondelete='CASCADE'))
    app_id = Column(UUID(as_uuid=True), ForeignKey('apps.id', ondelete='CASCADE'))
    
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
    
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id', ondelete='CASCADE'))
    app_id = Column(UUID(as_uuid=True), ForeignKey('apps.id', ondelete='CASCADE'))
    
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
    
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
