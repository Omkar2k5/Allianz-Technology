from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database.connection import get_db
from app.database import models
from app.models.schemas import ModelSpecSchema
from app.auth.jwt import get_current_user
from app.database.models import User

router = APIRouter()

@router.get("/", response_model=List[ModelSpecSchema])
async def get_model_specs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all available model specifications and environmental data
    """
    specs = db.query(models.ModelSpec).all()
    
    # Map to schema
    return [
        ModelSpecSchema(
            id=str(spec.id),
            model_name=spec.model_name,
            provider=spec.provider,
            parameters=spec.parameters,
            energy_kwh_per_1k_tokens=spec.energy_kwh_per_1k_tokens,
            co2_g_per_1k_tokens=spec.co2_g_per_1k_tokens,
            quality_score=spec.quality_score,
            cost_per_1k_input_tokens=spec.cost_per_1k_input_tokens,
            cost_per_1k_output_tokens=spec.cost_per_1k_output_tokens
        )
        for spec in specs
    ]
