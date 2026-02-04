"""
Agent-related Pydantic schemas for API requests/responses
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AgentRegistration(BaseModel):
    """Agent registration request"""
    computer_id: str = Field(..., description="Unique computer hardware ID")
    computer_name: str = Field(..., description="Windows computer name")
    team_id: str = Field(..., description="Organization/team ID")
    agent_version: str = Field(..., description="Agent version (e.g., 0.1.0)")
    os_version: str = Field(..., description="OS version (e.g., Windows 11 Pro)")
    installed_by: Optional[str] = Field(None, description="User ID who installed")


class AgentResponse(BaseModel):
    """Agent information response"""
    id: str
    computer_id: str
    computer_name: str
    team_id: str
    agent_version: str
    os_version: str
    status: str
    last_heartbeat: Optional[datetime]
    installed_at: datetime
    api_key: Optional[str] = None  # Only returned on registration
    
    class Config:
        from_attributes = True


class AgentHeartbeat(BaseModel):
    """Agent heartbeat request"""
    agent_id: str
    status: str = "active"
    stats: Optional[dict] = None  # Optional stats (requests_today, etc.)


class AIRequestLog(BaseModel):
    """Single AI request log from agent"""
    timestamp: datetime
    user_name: str
    computer_name: str
    process_name: Optional[str]
    
    provider: str  # openai, anthropic, etc.
    endpoint: str  # /v1/chat/completions
    model: str
    
    tokens_input: int
    tokens_output: int
    tokens_total: int
    
    cost_usd: float
    energy_wh: float
    co2_g: float
    
    latency_ms: int
    response_status: int
    
    prompt_hash: Optional[str] = None
    contains_pii: Optional[bool] = None


class BulkLogsRequest(BaseModel):
    """Bulk log upload from agent"""
    agent_id: str
    logs: list[AIRequestLog] = Field(..., max_length=1000)  # Max 1000 logs per batch


class BulkLogsResponse(BaseModel):
    """Response for bulk log upload"""
    success: bool
    inserted: int
    failed: int
    errors: Optional[list[str]] = None


class AgentStatsResponse(BaseModel):
    """Agent statistics"""
    agent_id: str
    computer_name: str
    status: str
    
    # Today's stats
    requests_today: int
    cost_today: float
    co2_today: float
    
    # All-time stats
    total_requests: int
    total_cost: float
    total_co2: float
    
    # Last activity
    last_request: Optional[datetime]
    last_heartbeat: Optional[datetime]
