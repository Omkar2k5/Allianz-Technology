"""
API endpoints for AI model specifications and recommendations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.database.connection import get_db
from app.database.models import ModelSpec, DatacenterInfo, GenAIRequest, User

router = APIRouter()


# Pydantic schemas
class ModelSpecResponse(BaseModel):
    model_name: str
    provider: str
    parameters: Optional[str]
    gpu_type: Optional[str]
    energy_kwh_per_1k_tokens: float
    co2_g_per_1k_tokens: float
    quality_score: Optional[float]
    cost_per_1k_input_tokens: Optional[float]
    cost_per_1k_output_tokens: Optional[float]
    is_measured: bool
    data_source: str
    
    class Config:
        from_attributes = True


class ModelComparisonResponse(BaseModel):
    model_name: str
    energy_kwh_per_1k_tokens: float
    co2_g_per_1k_tokens: float
    quality_score: Optional[float]
    cost_per_1k_tokens: float  # Average of input/output
    efficiency_score: float  # Quality per CO2


class UserImpactSummary(BaseModel):
    total_requests: int
    total_tokens: int
    total_energy_kwh: float
    total_co2_g: float
    most_used_model: str
    avg_tokens_per_request: int
    period_days: int


class ModelRecommendation(BaseModel):
    current_model: str
    recommended_model: str
    current_co2_g_per_day: float
    projected_co2_g_per_day: float
    co2_savings_percent: float
    quality_difference: str  # "similar", "slightly lower", "higher"
    reason: str


@router.get("/models", response_model=List[ModelSpecResponse])
async def list_models(
    provider: Optional[str] = None,
    min_quality: Optional[float] = None,
    max_co2: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    List all AI models with environmental specs
    Filter by provider, minimum quality score, or maximum CO2 emissions
    """
    query = db.query(ModelSpec)
    
    if provider:
        query = query.filter(ModelSpec.provider == provider)
    if min_quality:
        query = query.filter(ModelSpec.quality_score >= min_quality)
    if max_co2:
        query = query.filter(ModelSpec.co2_g_per_1k_tokens <= max_co2)
    
    models = query.order_by(ModelSpec.co2_g_per_1k_tokens).all()
    return models


@router.get("/models/{model_name}", response_model=ModelSpecResponse)
async def get_model(model_name: str, db: Session = Depends(get_db)):
    """Get detailed specs for a specific model"""
    model = db.query(ModelSpec).filter(ModelSpec.model_name == model_name).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.get("/models/compare", response_model=List[ModelComparisonResponse])
async def compare_models(
    models: List[str] = Query(..., description="List of model names to compare"),
    db: Session = Depends(get_db)
):
    """
    Compare multiple models side-by-side
    Returns efficiency scores (quality per CO2 unit)
    """
    model_specs = db.query(ModelSpec).filter(ModelSpec.model_name.in_(models)).all()
    
    if not model_specs:
        raise HTTPException(status_code=404, detail="No models found")
    
    comparisons = []
    for spec in model_specs:
        avg_cost = (
            (spec.cost_per_1k_input_tokens or 0) + 
            (spec.cost_per_1k_output_tokens or 0)
        ) / 2
        
        efficiency = (spec.quality_score or 50) / max(spec.co2_g_per_1k_tokens, 0.1)
        
        comparisons.append(ModelComparisonResponse(
            model_name=spec.model_name,
            energy_kwh_per_1k_tokens=spec.energy_kwh_per_1k_tokens,
            co2_g_per_1k_tokens=spec.co2_g_per_1k_tokens,
            quality_score=spec.quality_score,
            cost_per_1k_tokens=avg_cost,
            efficiency_score=efficiency
        ))
    
    # Sort by efficiency (highest first)
    comparisons.sort(key=lambda x: x.efficiency_score, reverse=True)
    return comparisons


@router.get("/user/impact", response_model=UserImpactSummary)
async def get_user_impact(
    user_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Calculate user's environmental impact over the last N days
    """
    from uuid import UUID
    user_uuid = UUID(user_id)
    
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # Get user's requests
    requests = db.query(GenAIRequest).filter(
        GenAIRequest.user_id == user_uuid,
        GenAIRequest.timestamp >= since_date
    ).all()
    
    if not requests:
        raise HTTPException(status_code=404, detail="No requests found for user")
    
    total_tokens = sum(r.tokens_total for r in requests)
    total_requests = len(requests)
    
    # Calculate environmental impact
    total_energy_kwh = 0.0
    total_co2_g = 0.0
    model_counts = {}
    
    for req in requests:
        # Try to get model spec
        model_spec = db.query(ModelSpec).filter(
            ModelSpec.model_name == req.model_name
        ).first()
        
        if model_spec:
            tokens_k = req.tokens_total / 1000.0
            total_energy_kwh += model_spec.energy_kwh_per_1k_tokens * tokens_k
            total_co2_g += model_spec.co2_g_per_1k_tokens * tokens_k
        else:
            # Fallback: use average estimate
            tokens_k = req.tokens_total / 1000.0
            total_energy_kwh += 0.01 * tokens_k  # 0.01 kWh/1k tokens average
            total_co2_g += 4.0 * tokens_k  # 4g CO2/1k tokens average
        
        # Count model usage
        model_counts[req.model_name] = model_counts.get(req.model_name, 0) + 1
    
    most_used_model = max(model_counts, key=model_counts.get)
    avg_tokens = total_tokens // total_requests if total_requests > 0 else 0
    
    return UserImpactSummary(
        total_requests=total_requests,
        total_tokens=total_tokens,
        total_energy_kwh=round(total_energy_kwh, 4),
        total_co2_g=round(total_co2_g, 2),
        most_used_model=most_used_model,
        avg_tokens_per_request=avg_tokens,
        period_days=days
    )


@router.get("/user/recommendations", response_model=List[ModelRecommendation])
async def get_recommendations(
    user_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get eco-friendly model recommendations based on user's usage pattern
    """
    from uuid import UUID
    user_uuid = UUID(user_id)
    
    # Get user's impact summary
    impact = await get_user_impact(user_id, days, db)
    
    # Get current model spec
    current_model_spec = db.query(ModelSpec).filter(
        ModelSpec.model_name == impact.most_used_model
    ).first()
    
    if not current_model_spec:
        raise HTTPException(status_code=404, detail="Current model specs not found")
    
    # Calculate current daily CO2
    daily_requests = impact.total_requests / impact.period_days
    current_co2_per_day = impact.total_co2_g / impact.period_days
    
    # Find alternatives with similar or better quality but lower CO2
    min_quality = (current_model_spec.quality_score or 70) * 0.85  # Allow 15% quality drop
    
    alternatives = db.query(ModelSpec).filter(
        ModelSpec.model_name != impact.most_used_model,
        ModelSpec.co2_g_per_1k_tokens < current_model_spec.co2_g_per_1k_tokens,
        ModelSpec.quality_score >= min_quality
    ).order_by(ModelSpec.co2_g_per_1k_tokens).limit(3).all()
    
    recommendations = []
    for alt in alternatives:
        # Calculate projected CO2
        tokens_per_day = (impact.total_tokens / impact.period_days) / 1000.0
        projected_co2_per_day = alt.co2_g_per_1k_tokens * tokens_per_day
        
        savings_percent = ((current_co2_per_day - projected_co2_per_day) / current_co2_per_day) * 100
        
        # Quality comparison
        quality_diff = alt.quality_score - (current_model_spec.quality_score or 70)
        if quality_diff >= 0:
            quality_desc = "similar or better"
        elif quality_diff >= -5:
            quality_desc = "slightly lower"
        else:
            quality_desc = "lower"
        
        reason = f"Uses {alt.gpu_type} with {alt.energy_kwh_per_1k_tokens:.4f} kWh/1k tokens"
        
        recommendations.append(ModelRecommendation(
            current_model=impact.most_used_model,
            recommended_model=alt.model_name,
            current_co2_g_per_day=round(current_co2_per_day, 2),
            projected_co2_g_per_day=round(projected_co2_per_day, 2),
            co2_savings_percent=round(savings_percent, 1),
            quality_difference=quality_desc,
            reason=reason
        ))
    
    return recommendations
