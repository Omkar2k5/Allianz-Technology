"""
Type definitions for the Eco-Compute SDK.

This module contains all type definitions, dataclasses, and TypedDicts
used throughout the SDK for strong typing and IDE support.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict, Union


class RiskLevel(str, Enum):
    """Risk level classification for LLM requests."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PolicyAction(str, Enum):
    """Actions that can be taken by policy enforcement."""
    
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    LOG_ONLY = "log_only"


class TelemetryRecord(TypedDict, total=False):
    """
    Complete telemetry record schema for sustainability tracking.
    
    This schema is designed for enterprise ESG reporting, AI sustainability
    analytics, and responsible AI adoption tracking.
    """
    
    # Identifiers
    id: str
    app_id: str
    model_id: str
    user_id: str
    agent_id: str
    
    # Timestamps
    timestamp: str
    created_at: str
    
    # Request tracking
    request_hash: str
    
    # System information
    computer_name: str
    process_name: str
    
    # Model information
    model_name: str
    provider: str
    
    # Token usage
    tokens_input: int
    tokens_output: int
    tokens_total: int
    
    # Sustainability metrics
    energy_wh: float
    co2_g: float
    region: str
    carbon_intensity: float
    
    # Performance
    latency_ms: float
    
    # Policy and governance
    use_case: str
    risk_level: str
    policy_applied: str
    policy_action: str
    
    # Cost tracking
    cost_usd: float
    
    # Extensibility
    meta_data: Dict[str, Any]


class LLMResponse(TypedDict, total=False):
    """Structure of an LLM API response."""
    
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


@dataclass
class LLMConfig:
    """
    Configuration for an LLM API request.
    
    Attributes:
        model: The model identifier (e.g., 'openai/gpt-4', 'anthropic/claude-3-opus')
        api_key: API key for authentication
        max_tokens: Maximum tokens in the response
        temperature: Sampling temperature (0.0 to 2.0)
        top_p: Nucleus sampling parameter
        stream: Whether to stream the response
        provider: LLM provider (auto-detected from model if not specified)
        use_case: Business use case for tracking
        user_id: User identifier for tracking
        agent_id: Agent identifier for tracking
        app_id: Application identifier for tracking
        model_id: Custom model identifier for tracking
        risk_level: Risk classification for the request
        meta_data: Additional metadata for tracking
    """
    
    model: str
    api_key: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    stream: bool = False
    provider: Optional[str] = None
    use_case: str = "general"
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    app_id: Optional[str] = None
    model_id: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.LOW
    meta_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Auto-detect provider from model name if not specified."""
        if self.provider is None:
            if "/" in self.model:
                self.provider = self.model.split("/")[0]
            else:
                self.provider = "unknown"


@dataclass
class EcoComputeConfig:
    """
    Configuration for the Eco-Compute SDK.
    
    Attributes:
        telemetry_endpoint: URL for telemetry data submission
        telemetry_token: Bearer token for telemetry authentication
        telemetry_enabled: Whether telemetry collection is enabled
        openrouter_base_url: Base URL for OpenRouter API
        region: Geographic region for carbon intensity calculation
        default_carbon_intensity: Fallback carbon intensity (gCO2/kWh)
        model_energy_factors: Custom energy factors per token by model
        model_pricing: Custom pricing per token by model
        fail_silently: Whether to suppress telemetry errors
        batch_size: Number of records to batch before sending
        batch_timeout_seconds: Maximum time to wait before sending batch
        app_id: Default application identifier
        user_id: Authenticated user identifier
        debug: Enable debug logging
        api_base_url: Base URL for the Eco-Compute backend API (for auth & metrics)
    """
    
    telemetry_endpoint: Optional[str] = None
    telemetry_token: Optional[str] = None
    telemetry_enabled: bool = True
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    region: str = "us-east"
    default_carbon_intensity: float = 400.0  # gCO2/kWh
    model_energy_factors: Optional[Dict[str, float]] = None
    model_pricing: Optional[Dict[str, Dict[str, float]]] = None
    fail_silently: bool = True
    batch_size: int = 10
    batch_timeout_seconds: float = 30.0
    app_id: Optional[str] = None
    user_id: Optional[str] = None
    debug: bool = False
    api_base_url: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Set default values for optional dictionaries."""
        if self.model_energy_factors is None:
            self.model_energy_factors = {}
        if self.model_pricing is None:
            self.model_pricing = {}


@dataclass
class EstimationResult:
    """
    Result of sustainability estimation calculations.
    
    Attributes:
        energy_wh: Estimated energy consumption in watt-hours
        co2_g: Estimated carbon emissions in grams CO2
        cost_usd: Estimated cost in USD
        tokens_input: Number of input tokens
        tokens_output: Number of output tokens
        tokens_total: Total number of tokens
        carbon_intensity: Carbon intensity used (gCO2/kWh)
        region: Region used for carbon intensity
        model_energy_factor: Energy factor used (Wh per token)
    """
    
    energy_wh: float
    co2_g: float
    cost_usd: float
    tokens_input: int
    tokens_output: int
    tokens_total: int
    carbon_intensity: float
    region: str
    model_energy_factor: float


@dataclass
class CallResult:
    """
    Complete result from an LLM API call including sustainability metrics.
    
    Attributes:
        response: The original LLM response (unchanged)
        estimation: Sustainability estimation results
        telemetry_id: ID of the telemetry record created
        latency_ms: Request latency in milliseconds
    """
    
    response: Dict[str, Any]
    estimation: EstimationResult
    telemetry_id: str
    latency_ms: float
