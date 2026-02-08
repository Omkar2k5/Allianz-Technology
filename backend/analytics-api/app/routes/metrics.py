
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.database.connection import get_db
from app.database.models import GenAIRequest, User
from app.auth.jwt import get_current_user
from app.models.metrics_schemas import TelemetryBatch, MetricsResponse

router = APIRouter()

@router.post("/", response_model=MetricsResponse, status_code=status.HTTP_201_CREATED)
async def log_metrics(
    batch: TelemetryBatch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log telemetry metrics from the Eco-Compute SDK.
    Requires authentication.
    """
    processed_count = 0
    
    for record in batch.records:
        try:
            # Parse timestamp
            try:
                # SDK sends ISO format, e.g. "2024-01-15T10:30:00Z"
                # Python 3.11+ supports fromisoformat with Z
                ts = datetime.fromisoformat(record.timestamp.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                ts = datetime.utcnow()
                
            # Create GenAIRequest object
            genai_request = GenAIRequest(
                id=uuid.UUID(record.id),
                user_id=current_user.id, # Link to authenticated user
                timestamp=ts,
                request_hash=record.request_hash or "unknown",
                
                # Agent/System metadata
                computer_name=record.computer_name,
                
                # LLM Metadata
                model_name=record.model_name,
                provider=record.provider,
                
                # Token usage
                tokens_input=record.tokens_input,
                tokens_output=record.tokens_output,
                tokens_total=record.tokens_total,
                
                # Metrics
                energy_wh=record.energy_wh,
                co2_g=record.co2_g,
                
                # Context
                region=record.region,
                latency_ms=int(record.latency_ms) if record.latency_ms else 0,
                
                policy_applied=record.policy_applied == "true" or bool(record.policy_applied),
                
                meta_data=record.meta_data
            )
            
            db.add(genai_request)
            processed_count += 1
            
        except Exception as e:
            # We log error but continue processing other records in the batch
            import logging
            logging.error(f"Failed to process record {record.id}: {str(e)}")
            continue
            
    db.commit()
    
    return MetricsResponse(
        message="Metrics logged successfully",
        processed_count=processed_count
    )

@router.get("/test")
async def test_endpoint():
    return {"message": "Metrics endpoint is active"}
