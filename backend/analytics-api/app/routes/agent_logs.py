from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
import logging

from app.database.connection import get_db
from app.database.models import GenAIRequest, Agent, User

router = APIRouter()
logger = logging.getLogger(__name__)

class AgentLogItem(BaseModel):
    request_id: str
    timestamp: str
    user_id: str
    user_name: Optional[str] = None
    computer_name: Optional[str] = None
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: int
    region: Optional[str] = None

class BatchLogRequest(BaseModel):
    logs: List[AgentLogItem]

class BatchLogResponse(BaseModel):
    synced_count: int
    failed_ids: List[str]

@router.post("/logs/batch", response_model=BatchLogResponse)
async def upload_batch_logs(request: BatchLogRequest, db: Session = Depends(get_db)):
    """
    Batch upload AI request logs from desktop agent
    """
    synced_count = 0
    failed_ids = []
    
    logger.info(f"Received batch of {len(request.logs)} logs from agent")
    
    for log in request.logs:
        try:
            # Check if log already exists
            log_uuid = uuid.UUID(log.request_id)
            existing = db.query(GenAIRequest).filter(GenAIRequest.id == log_uuid).first()
            
            if existing:
                # Skip duplicate
                continue
                
            # Parse timestamp
            try:
                ts = datetime.fromisoformat(log.timestamp.replace('Z', '+00:00'))
            except ValueError:
                ts = datetime.utcnow()
                
            # Find or create agent record (implied by computer_name/user)
            # For now, we'll try to link to an existing agent or user
            
            user_uuid = None
            try:
                user_uuid = uuid.UUID(log.user_id)
            except ValueError:
                pass
            
            # Create request record
            new_request = GenAIRequest(
                id=log_uuid,
                user_id=user_uuid,
                timestamp=ts,
                provider=log.provider,
                model_name=log.model,
                request_hash=log.request_id, # Use ID as hash for now
                
                computer_name=log.computer_name,
                
                tokens_input=log.prompt_tokens,
                tokens_output=log.completion_tokens,
                tokens_total=log.total_tokens,
                
                latency_ms=log.latency_ms,
                region=log.region or "unknown",
                
                # Default values
                energy_wh=0.0, # To be calculated
                co2_g=0.0,     # To be calculated
                cost_usd=0.0   # To be calculated
            )
            
            # Calculate metrics (simplified logic for now)
            # In a real system, we'd look up Model specs
            # Assuming average: 0.002 kWh per 1k tokens? simpler: 
            # cost: assume $0.002/1k input, $0.006/1k output (GPT-4ish)
            
            # Using very rough estimates just to populate fields
            new_request.energy_wh = (log.total_tokens / 1000.0) * 0.1 
            new_request.co2_g = new_request.energy_wh * 400.0 # 400g/kWh global avg
            
            db.add(new_request)
            synced_count += 1
            
        except Exception as e:
            logger.error(f"Failed to process log {log.request_id}: {e}")
            failed_ids.append(log.request_id)
            
    try:
        db.commit()
    except Exception as e:
        logger.error(f"Failed to commit batch: {e}")
        db.rollback()
        return BatchLogResponse(synced_count=0, failed_ids=[l.request_id for l in request.logs])
        
    return BatchLogResponse(
        synced_count=synced_count,
        failed_ids=failed_ids
    )
