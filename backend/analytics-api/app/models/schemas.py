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
    tokens_input: Optional[int] = 0
    tokens_output: Optional[int] = 0
    avg_latency: Optional[float] = 0


class UsageMetrics(BaseModel):
    daily_usage: List[DailyUsage]
    model_distribution: List[ModelDistribution]


# Energy Schemas
class EnergyByModel(BaseModel):
    model: str
    energy_wh: float


class DailyEnergy(BaseModel):
    date: str
    energy_wh: float


class ActivityLog(BaseModel):
    timestamp: str
    computer_name: Optional[str] = "Unknown"
    model: str
    tokens: int
    latency_ms: int
    energy_wh: float
    co2_g: float


class EnergyMetrics(BaseModel):
    total_energy_wh: float
    by_model: List[EnergyByModel]
    daily_energy: List[DailyEnergy]
    recent_activity: List[ActivityLog]


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
