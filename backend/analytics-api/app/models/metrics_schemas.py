from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class TelemetryRecord(BaseModel):
    id: str
    app_id: Optional[str] = None
    model_id: Optional[str] = None
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    
    timestamp: str
    created_at: str
    
    request_hash: Optional[str] = None
    
    computer_name: Optional[str] = None
    process_name: Optional[str] = None
    
    model_name: str
    provider: str
    
    tokens_input: int
    tokens_output: int
    tokens_total: int
    
    energy_wh: float
    co2_g: float
    region: Optional[str] = None
    carbon_intensity: Optional[float] = None
    
    latency_ms: Optional[float] = None
    
    use_case: Optional[str] = None
    risk_level: Optional[str] = None
    policy_applied: Optional[str] = None
    policy_action: Optional[str] = None
    
    cost_usd: Optional[float] = None
    
    meta_data: Optional[Dict[str, Any]] = None

class TelemetryBatch(BaseModel):
    records: List[TelemetryRecord]
    sdk_version: Optional[str] = None
    timestamp: Optional[str] = None

class MetricsResponse(BaseModel):
    message: str
    processed_count: int
