"""
Dashboard data endpoints
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.database.connection import get_db
from app.models.schemas import DashboardOverview, UsageMetrics, EnergyMetrics, EmissionsMetrics
from app.database import models

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    app_id: Optional[str] = Query(None, description="Filter by app ID"),
    days: int = Query(7, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get dashboard overview with key metrics
    
    Returns:
        - Total AI calls
        - Total energy consumption
        - CO2 emissions
        - Average model efficiency
        - Recent alerts
        - Top recommendations
    """
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Base query
    query = db.query(models.GenAIRequest).filter(
        models.GenAIRequest.timestamp >= start_date,
        models.GenAIRequest.timestamp <= end_date
    )
    
    if app_id:
        query = query.filter(models.GenAIRequest.app_id == app_id)
    
    # Aggregate metrics
    metrics = query.with_entities(
        func.count(models.GenAIRequest.id).label('total_calls'),
        func.sum(models.GenAIRequest.tokens_total).label('total_tokens'),
        func.sum(models.GenAIRequest.energy_wh).label('total_energy'),
        func.sum(models.GenAIRequest.co2_g).label('total_co2'),
        func.avg(models.GenAIRequest.latency_ms).label('avg_latency')
    ).first()
    
    # Calculate growth (compare with previous period)
    prev_start = start_date - timedelta(days=days)
    prev_query = db.query(models.GenAIRequest).filter(
        models.GenAIRequest.timestamp >= prev_start,
        models.GenAIRequest.timestamp < start_date
    )
    
    if app_id:
        prev_query = prev_query.filter(models.GenAIRequest.app_id == app_id)
    
    prev_metrics = prev_query.with_entities(
        func.count(models.GenAIRequest.id).label('total_calls')
    ).first()
    
    # Calculate growth percentage
    calls_growth = 0
    if prev_metrics and prev_metrics.total_calls:
        calls_growth = ((metrics.total_calls - prev_metrics.total_calls) / prev_metrics.total_calls) * 100
    
    # Get recent alerts
    alerts = db.query(models.Alert).filter(
        models.Alert.status == 'active'
    ).order_by(desc(models.Alert.created_at)).limit(5).all()
    
    # Get top recommendations
    recommendations = db.query(models.Recommendation).filter(
        models.Recommendation.status == 'pending'
    ).order_by(desc(models.Recommendation.estimated_co2_savings_g)).limit(3).all()
    
    return {
        "total_calls": metrics.total_calls or 0,
        "calls_growth_percent": round(calls_growth, 1),
        "total_energy_wh": float(metrics.total_energy or 0),
        "total_co2_g": float(metrics.total_co2 or 0),
        "avg_latency_ms": int(metrics.avg_latency or 0),
        "period_days": days,
        "alerts": [
            {
                "id": str(alert.id),
                "type": alert.alert_type,
                "severity": alert.severity,
                "title": alert.title,
                "message": alert.message
            }
            for alert in alerts
        ],
        "recommendations": [
            {
                "id": str(rec.id),
                "type": rec.recommendation_type,
                "title": rec.title,
                "estimated_savings_co2_g": float(rec.estimated_co2_savings_g or 0),
                "difficulty": rec.difficulty
            }
            for rec in recommendations
        ]
    }


@router.get("/usage", response_model=UsageMetrics)
async def get_usage_metrics(
    app_id: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get usage tracking metrics"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Daily usage trend
    daily_usage = db.query(
        func.date(models.GenAIRequest.timestamp).label('date'),
        func.count(models.GenAIRequest.id).label('calls'),
        func.sum(models.GenAIRequest.tokens_total).label('tokens')
    ).filter(
        models.GenAIRequest.timestamp >= start_date,
        models.GenAIRequest.timestamp <= end_date
    )
    
    if app_id:
        daily_usage = daily_usage.filter(models.GenAIRequest.app_id == app_id)
    
    daily_usage = daily_usage.group_by(func.date(models.GenAIRequest.timestamp)).all()
    
    # Model distribution
    model_dist = db.query(
        models.GenAIRequest.model_name,
        func.count(models.GenAIRequest.id).label('calls'),
        func.sum(models.GenAIRequest.tokens_total).label('tokens')
    ).filter(
        models.GenAIRequest.timestamp >= start_date,
        models.GenAIRequest.timestamp <= end_date
    )
    
    if app_id:
        model_dist = model_dist.filter(models.GenAIRequest.app_id == app_id)
    
    model_dist = model_dist.group_by(models.GenAIRequest.model_name).all()
    
    return {
        "daily_usage": [
            {
                "date": str(row.date),
                "calls": row.calls,
                "tokens": row.tokens
            }
            for row in daily_usage
        ],
        "model_distribution": [
            {
                "model": row.model_name,
                "calls": row.calls,
                "tokens": row.tokens
            }
            for row in model_dist
        ]
    }


@router.get("/energy", response_model=EnergyMetrics)
async def get_energy_metrics(
    app_id: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get energy consumption metrics"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Total energy
    total = db.query(
        func.sum(models.GenAIRequest.energy_wh).label('total_energy')
    ).filter(
        models.GenAIRequest.timestamp >= start_date,
        models.GenAIRequest.timestamp <= end_date
    )
    
    if app_id:
        total = total.filter(models.GenAIRequest.app_id == app_id)
    
    total = total.first()
    
    # Energy by model
    by_model = db.query(
        models.GenAIRequest.model_name,
        func.sum(models.GenAIRequest.energy_wh).label('energy')
    ).filter(
        models.GenAIRequest.timestamp >= start_date,
        models.GenAIRequest.timestamp <= end_date
    )
    
    if app_id:
        by_model = by_model.filter(models.GenAIRequest.app_id == app_id)
    
    by_model = by_model.group_by(models.GenAIRequest.model_name).all()
    
    return {
        "total_energy_wh": float(total.total_energy or 0),
        "by_model": [
            {
                "model": row.model_name,
                "energy_wh": float(row.energy)
            }
            for row in by_model
        ]
    }


@router.get("/emissions", response_model=EmissionsMetrics)
async def get_emissions_metrics(
    app_id: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get carbon emissions metrics"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Total CO2
    total = db.query(
        func.sum(models.GenAIRequest.co2_g).label('total_co2')
    ).filter(
        models.GenAIRequest.timestamp >= start_date,
        models.GenAIRequest.timestamp <= end_date
    )
    
    if app_id:
        total = total.filter(models.GenAIRequest.app_id == app_id)
    
    total = total.first()
    
    # CO2 by region
    by_region = db.query(
        models.GenAIRequest.region,
        func.sum(models.GenAIRequest.co2_g).label('co2'),
        func.count(models.GenAIRequest.id).label('requests')
    ).filter(
        models.GenAIRequest.timestamp >= start_date,
        models.GenAIRequest.timestamp <= end_date
    )
    
    if app_id:
        by_region = by_region.filter(models.GenAIRequest.app_id == app_id)
    
    by_region = by_region.group_by(models.GenAIRequest.region).all()
    
    # Monthly trend
    monthly = db.query(
        func.date_trunc('month', models.GenAIRequest.timestamp).label('month'),
        func.sum(models.GenAIRequest.co2_g).label('co2')
    ).filter(
        models.GenAIRequest.timestamp >= start_date,
        models.GenAIRequest.timestamp <= end_date
    )
    
    if app_id:
        monthly = monthly.filter(models.GenAIRequest.app_id == app_id)
    
    monthly = monthly.group_by(func.date_trunc('month', models.GenAIRequest.timestamp)).all()
    
    return {
        "total_co2_g": float(total.total_co2 or 0),
        "by_region": [
            {
                "region": row.region or "unknown",
                "co2_g": float(row.co2),
                "requests": row.requests
            }
            for row in by_region
        ],
        "monthly_trend": [
            {
                "month": str(row.month),
                "co2_g": float(row.co2)
            }
            for row in monthly
        ]
    }
