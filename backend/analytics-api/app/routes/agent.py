"""
Endpoint for agents (Desktop/Mobile) to log AI requests
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import logging

from app.database.connection import get_db
from app.database.models import GenAIRequest, User
from app.models.agent_schemas import AIRequestLog

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/log", status_code=status.HTTP_201_CREATED)
async def log_ai_request(
    log_data: AIRequestLog,
    x_agent_id: str = Header(None, alias="X-Agent-ID"),
    db: Session = Depends(get_db)
):
    """
    Log a single AI request from an agent
    """
    try:
        # Find user if possible (optional for now, can perform lookup by ID or name)
        # For now, we assume the agent sends a valid user_id in the log_data if available
        # or we might need to lookup based on the computer_name/agent_id
        
        # log_data.user_name is sent, but we might want to link to actual User table
        # user = db.query(User).filter(User.email == log_data.user_name).first()
        # user_id = user.id if user else None
        
        # Create request record
        new_request = GenAIRequest(
            id=uuid.uuid4(),
            timestamp=log_data.timestamp.replace(tzinfo=None) if log_data.timestamp else datetime.utcnow(),
            request_hash=log_data.prompt_hash or str(uuid.uuid4()), # Fallback if hash missing
            
            computer_name=log_data.computer_name,
            model_name=log_data.model,
            provider=log_data.provider,
            
            tokens_input=log_data.tokens_input or 0,
            tokens_output=log_data.tokens_output or 0,
            tokens_total=log_data.tokens_total or 0,
            
            energy_wh=log_data.energy_wh,
            co2_g=log_data.co2_g,
            
            region=log_data.region,
            latency_ms=log_data.latency_ms,
            
            # user_id=user_id # TODO: Link to actual user
        )
        
        db.add(new_request)
        db.commit()
        
        return {"status": "logged", "id": str(new_request.id)}
        
    except Exception as e:
        logger.error(f"Error logging AI request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
