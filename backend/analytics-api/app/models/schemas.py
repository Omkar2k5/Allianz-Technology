"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# Dashboard Schemas
class AlertSchema(BaseModel):
    id: str
    type: str
    severity: str
    title: str
    message: str


class RecommendationSchema(BaseModel):
    id: str
    type: str
    title: str
    estimated_savings_co2_g: float
    difficulty: str


class DashboardOverview(BaseModel):
    total_calls: int
    calls_growth_percent: float
    total_energy_wh: float
    total_co2_g: float
    avg_latency_ms: int
    period_days: int
    alerts: List[AlertSchema]
    recommendations: List[RecommendationSchema]


# Usage Schemas
class DailyUsage(BaseModel):
    date: str
    calls: int
    tokens: int


class ModelDistribution(BaseModel):
    model: str
    calls: int
    tokens: int


class UsageMetrics(BaseModel):
    daily_usage: List[DailyUsage]
    model_distribution: List[ModelDistribution]


# Energy Schemas
class EnergyByModel(BaseModel):
    model: str
    energy_wh: float


class EnergyMetrics(BaseModel):
    total_energy_wh: float
    by_model: List[EnergyByModel]


# Emissions Schemas
class EmissionsByRegion(BaseModel):
    region: str
    co2_g: float
    requests: int


class MonthlyEmissions(BaseModel):
    month: str
    co2_g: float


class EmissionsMetrics(BaseModel):
    total_co2_g: float
    by_region: List[EmissionsByRegion]
    monthly_trend: List[MonthlyEmissions]
