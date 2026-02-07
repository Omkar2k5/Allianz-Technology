"""
Agent Management API Routes
Handles agent registration, heartbeat, and log ingestion
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
import secrets
import hashlib
from datetime import datetime, timedelta

from app.database.connection import get_db
from app.database.models import Agent, GenAIRequest, Team
from app.models.agent_schemas import (
    AgentRegistration,
    AgentResponse,
    AgentHeartbeat,
    BulkLogsRequest,
    BulkLogsResponse,
    AgentStatsResponse
)
from app.auth.jwt import get_current_user
from app.database.models import User
from app.services.region_detector import region_detector

router = APIRouter()


def generate_api_key() -> str:
    """Generate a secure API key for agent"""
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """Hash API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_agent_api_key(
    agent_id: str = Header(..., alias="X-Agent-ID"),
    api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db)
) -> Agent:
    """Verify agent API key and return agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Verify API key
    api_key_hash = hash_api_key(api_key)
    if agent.api_key_hash != api_key_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return agent


@router.post("/register", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def register_agent(
    agent_data: AgentRegistration,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register a new desktop agent
    
    Requires authentication (admin user installing the agent)
    Returns agent info with API key (only shown once)
    """
    
    # Check if agent already exists
    existing = db.query(Agent).filter(
        Agent.computer_id == agent_data.computer_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent already registered for this computer"
        )
    
    # Verify team exists
    team = db.query(Team).filter(Team.id == agent_data.team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Generate API key
    api_key = generate_api_key()
    api_key_hash = hash_api_key(api_key)
    
    # Create agent
    new_agent = Agent(
        computer_id=agent_data.computer_id,
        computer_name=agent_data.computer_name,
        team_id=agent_data.team_id,
        agent_version=agent_data.agent_version,
        os_version=agent_data.os_version,
        installed_by=current_user.id,
        api_key_hash=api_key_hash,
        status='active',
        last_heartbeat=datetime.utcnow()
    )
    
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    
    # Return response with API key (only time it's shown)
    response = AgentResponse(
        id=str(new_agent.id),
        computer_id=new_agent.computer_id,
        computer_name=new_agent.computer_name,
        team_id=str(new_agent.team_id),
        agent_version=new_agent.agent_version,
        os_version=new_agent.os_version,
        status=new_agent.status,
        last_heartbeat=new_agent.last_heartbeat,
        installed_at=new_agent.installed_at,
        api_key=api_key  # Only returned on registration
    )
    
    return response


@router.post("/heartbeat")
async def agent_heartbeat(
    heartbeat: AgentHeartbeat,
    agent: Agent = Depends(verify_agent_api_key),
    db: Session = Depends(get_db)
):
    """
    Agent heartbeat - updates last_heartbeat timestamp
    
    Called every 5 minutes by agent to indicate it's still running
    """
    
    agent.last_heartbeat = datetime.utcnow()
    agent.status = heartbeat.status
    
    db.commit()
    
    return {
        "success": True,
        "message": "Heartbeat received",
        "next_heartbeat": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
    }


@router.post("/logs/bulk", response_model=BulkLogsResponse)
async def ingest_bulk_logs(
    bulk_request: BulkLogsRequest,
    agent: Agent = Depends(verify_agent_api_key),
    db: Session = Depends(get_db)
):
    """
    Bulk log ingestion from agent
    
    Accepts up to 1000 logs per request
    Inserts into genai_requests table
    """
    
    inserted = 0
    failed = 0
    errors = []
    
    for log in bulk_request.logs:
        try:
            # Create GenAI request record
            request = GenAIRequest(
                agent_id=agent.id,
                timestamp=log.timestamp,
                computer_name=log.computer_name,
                process_name=log.process_name,
                
                # Model info (we'll need to look up or create)
                model_name=log.model,
                provider=log.provider,
                
                # Tokens
                tokens_input=log.tokens_input,
                tokens_output=log.tokens_output,
                tokens_total=log.tokens_total,
                
                # Metrics
                cost_usd=log.cost_usd,
                energy_wh=log.energy_wh,
                co2_g=log.co2_g,
                
                # Performance
                latency_ms=log.latency_ms,
                
                # Hash
                request_hash=log.prompt_hash or "",
                
                # Region detection from server IP (if provided)
                region=None,
                carbon_intensity=400.0  # Default
            )
            
            # Detect region from server IP if provided
            if log.server_ip:
                try:
                    detected_region, carbon_intensity = region_detector.detect_region_from_ip(log.server_ip)
                    request.region = detected_region
                    request.carbon_intensity = carbon_intensity
                    
                    # Recalculate CO2 with region-specific carbon intensity
                    if log.energy_wh:
                        request.co2_g = log.energy_wh * (carbon_intensity / 1000.0)  # Convert gCO2/kWh to gCO2/Wh
                except Exception as e:
                    # Log error but don't fail the entire request
                    errors.append(f"Region detection failed for {log.server_ip}: {str(e)}")
            
            db.add(request)
            inserted += 1
            
        except Exception as e:
            failed += 1
            errors.append(f"Log {inserted + failed}: {str(e)}")
    
    # Commit all at once
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to insert logs: {str(e)}"
        )
    
    return BulkLogsResponse(
        success=failed == 0,
        inserted=inserted,
        failed=failed,
        errors=errors if errors else None
    )


@router.get("/{agent_id}/stats", response_model=AgentStatsResponse)
async def get_agent_stats(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics for a specific agent"""
    
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Get today's stats
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    today_requests = db.query(GenAIRequest).filter(
        GenAIRequest.agent_id == agent_id,
        GenAIRequest.timestamp >= today_start
    ).all()
    
    requests_today = len(today_requests)
    cost_today = sum(r.cost_usd or 0 for r in today_requests)
    co2_today = sum(r.co2_g or 0 for r in today_requests)
    
    # Get all-time stats
    all_requests = db.query(GenAIRequest).filter(
        GenAIRequest.agent_id == agent_id
    ).all()
    
    total_requests = len(all_requests)
    total_cost = sum(r.cost_usd or 0 for r in all_requests)
    total_co2 = sum(r.co2_g or 0 for r in all_requests)
    
    # Last request
    last_request = db.query(GenAIRequest).filter(
        GenAIRequest.agent_id == agent_id
    ).order_by(GenAIRequest.timestamp.desc()).first()
    
    return AgentStatsResponse(
        agent_id=str(agent.id),
        computer_name=agent.computer_name,
        status=agent.status,
        requests_today=requests_today,
        cost_today=cost_today,
        co2_today=co2_today,
        total_requests=total_requests,
        total_cost=total_cost,
        total_co2=total_co2,
        last_request=last_request.timestamp if last_request else None,
        last_heartbeat=agent.last_heartbeat
    )


@router.get("/", response_model=list[AgentResponse])
async def list_agents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all agents for current user's team"""
    
    agents = db.query(Agent).filter(
        Agent.team_id == current_user.team_id
    ).all()
    
    return [
        AgentResponse(
            id=str(agent.id),
            computer_id=agent.computer_id,
            computer_name=agent.computer_name,
            team_id=str(agent.team_id),
            agent_version=agent.agent_version,
            os_version=agent.os_version,
            status=agent.status,
            last_heartbeat=agent.last_heartbeat,
            installed_at=agent.installed_at
        )
        for agent in agents
    ]
