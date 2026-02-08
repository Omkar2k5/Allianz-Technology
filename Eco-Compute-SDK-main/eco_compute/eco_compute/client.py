"""
Main client for the Eco-Compute SDK.

This module provides the core EcoCompute client that wraps LLM API calls
and automatically tracks sustainability metrics including energy usage,
carbon emissions, and cost.

Features:
- Provider-agnostic LLM API wrapper
- Automatic sustainability estimation
- Non-intrusive telemetry
- Drop-in replacement design
"""

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

import requests

from eco_compute.estimators.carbon import estimate_carbon, get_carbon_intensity
from eco_compute.estimators.cost import estimate_cost
from eco_compute.estimators.energy import estimate_energy, get_energy_factor
from eco_compute.telemetry.sender import TelemetrySender, TelemetrySenderConfig
from eco_compute.types import (
    CallResult,
    EcoComputeConfig,
    EstimationResult,
    LLMConfig,
    LLMResponse,
    PolicyAction,
    RiskLevel,
    TelemetryRecord,
)
from eco_compute.utils.hash import generate_request_id, hash_request
from eco_compute.utils.system import get_computer_name, get_process_name

# Module logger
logger = logging.getLogger("eco_compute")


class EcoCompute:
    """
    The main Eco-Compute SDK client.
    
    Provides a clean, provider-agnostic interface for making LLM API calls
    while automatically tracking sustainability metrics.
    
    Example:
        >>> from eco_compute import EcoCompute, EcoComputeConfig
        >>> 
        >>> config = EcoComputeConfig(
        ...     telemetry_endpoint="https://api.example.com/telemetry",
        ...     telemetry_token="your-token",
        ...     region="us-west-2"
        ... )
        >>> 
        >>> eco = EcoCompute(config)
        >>> 
        >>> result = eco.call_llm(
        ...     prompt="Hello, how are you?",
        ...     config={
        ...         "model": "openai/gpt-4o-mini",
        ...         "api_key": "your-openrouter-key"
        ...     }
        ... )
        >>> 
        >>> print(result["response"])  # Original LLM response
        >>> print(result["estimation"]["co2_g"])  # Carbon footprint
    """
    
    def __init__(self, config: Optional[EcoComputeConfig] = None) -> None:
        """
        Initialize the EcoCompute client.
        
        Args:
            config: SDK configuration. If None, uses defaults.
        """
        self._config = config or EcoComputeConfig()
        
        # Initialize telemetry sender
        telemetry_config = TelemetrySenderConfig(
            endpoint=self._config.telemetry_endpoint,
            token=self._config.telemetry_token,
            enabled=self._config.telemetry_enabled,
            fail_silently=self._config.fail_silently,
            batch_size=self._config.batch_size,
            batch_timeout_seconds=self._config.batch_timeout_seconds
        )
        self._telemetry = TelemetrySender(telemetry_config)
        
        # Request session for connection pooling
        self._session = requests.Session()
        
        if self._config.debug:
            logging.basicConfig(level=logging.DEBUG)
            
    def login(self, email: str, password: str) -> bool:
        """
        Authenticate with the Eco-Compute backend using email/password.
        
        This retrieves an access token and user ID, automatically
        configuring the SDK for authenticated telemetry.
        
        Args:
            email: User email address
            password: User password
            
        Returns:
            True if authentication was successful
            
        Raises:
            ValueError: If api_base_url is not in config
            requests.exceptions.RequestException: If the request fails
        """
        if not self._config.api_base_url:
            raise ValueError("api_base_url must be configured in EcoComputeConfig to usage login()")
            
        url = f"{self._config.api_base_url.rstrip('/')}/auth/login"
        
        try:
            response = self._session.post(
                url,
                json={"email": email, "password": password},
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            token = data.get("access_token")
            user_data = data.get("user", {})
            user_id = user_data.get("id")
            
            if token:
                # Update configuration
                self._config.telemetry_token = token
                if user_id:
                    self._config.user_id = user_id
                
                # Update active telemetry sender
                self._telemetry.set_token(token)
                
                # Auto-configure telemetry endpoint if not set
                if not self._config.telemetry_endpoint:
                    endpoint = f"{self._config.api_base_url.rstrip('/')}/metrics"
                    self._config.telemetry_endpoint = endpoint
                    self._telemetry.set_endpoint(endpoint)
                
                if self._config.debug:
                    logger.info(f"Successfully logged in as {email}")
                return True
                
        except Exception as e:
            if self._config.debug:
                logger.error(f"Login failed: {e}")
            raise
            
        return False
    
    def call_llm(
        self,
        prompt: Union[str, List[Dict[str, Any]]],
        config: Union[LLMConfig, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Make an LLM API call with automatic sustainability tracking.
        
        This method wraps the OpenRouter API, captures token usage and latency,
        estimates sustainability metrics, and sends telemetry asynchronously.
        
        The original LLM response is returned unchanged.
        
        Args:
            prompt: The prompt string or list of message dicts
            config: LLM configuration (model, api_key, etc.)
        
        Returns:
            Dictionary containing:
            - response: The original LLM API response (unchanged)
            - estimation: Sustainability metrics (energy_wh, co2_g, cost_usd)
            - telemetry_id: ID of the telemetry record created
            - latency_ms: Request latency in milliseconds
        
        Raises:
            requests.exceptions.RequestException: If the LLM API call fails
        
        Example:
            >>> result = eco.call_llm(
            ...     "What is the capital of France?",
            ...     {"model": "openai/gpt-4o-mini", "api_key": "sk-..."}
            ... )
            >>> print(result["response"]["choices"][0]["message"]["content"])
            "The capital of France is Paris."
        """
        # Normalize config
        llm_config = self._normalize_config(config)
        
        # Generate request tracking
        request_id = generate_request_id()
        request_hash = hash_request(
            prompt if isinstance(prompt, str) else str(prompt),
            {"model": llm_config.model}
        )
        
        # Prepare messages
        messages = self._prepare_messages(prompt)
        
        # Make the API call with timing
        start_time = time.perf_counter()
        
        try:
            response = self._make_openrouter_request(messages, llm_config)
            response_json: Dict[str, Any] = response.json()
        except Exception as e:
            # Log error but don't crash for telemetry
            if self._config.debug:
                logger.error(f"LLM API call failed: {e}")
            raise
        
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        
        # Extract token usage
        usage = response_json.get("usage", {})
        tokens_input = usage.get("prompt_tokens", 0)
        tokens_output = usage.get("completion_tokens", 0)
        tokens_total = usage.get("total_tokens", tokens_input + tokens_output)
        
        # Get model info
        model_name = response_json.get("model", llm_config.model)
        provider = self._extract_provider(model_name, llm_config.provider)
        
        # Calculate sustainability metrics
        estimation = self._calculate_estimation(
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            tokens_total=tokens_total,
            model_name=model_name
        )
        
        # Create and send telemetry (non-blocking)
        telemetry_record = self._create_telemetry_record(
            request_id=request_id,
            request_hash=request_hash,
            model_name=model_name,
            provider=provider,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            tokens_total=tokens_total,
            estimation=estimation,
            latency_ms=latency_ms,
            llm_config=llm_config
        )
        
        self._telemetry.send(telemetry_record)
        
        # Consolidation for user-requested format
        metrics = {
            "tokens_total": estimation.tokens_total,
            "energy_wh": estimation.energy_wh,
            "co2_g": estimation.co2_g,
            "latency_ms": round(latency_ms, 2),
            "cost_usd": estimation.cost_usd,
            "model_name": model_name,
            "provider": provider,
            "region": self._config.region
        }
        
        # Return result with original response unchanged
        return {
            "response": response_json,
            "metrics": metrics,
            "estimation": {
                "energy_wh": estimation.energy_wh,
                "co2_g": estimation.co2_g,
                "cost_usd": estimation.cost_usd,
                "tokens_input": estimation.tokens_input,
                "tokens_output": estimation.tokens_output,
                "tokens_total": estimation.tokens_total,
                "carbon_intensity": estimation.carbon_intensity,
                "region": estimation.region,
                "model_energy_factor": estimation.model_energy_factor
            },
            "telemetry_id": request_id,
            "latency_ms": latency_ms
        }
    
    def _normalize_config(self, config: Union[LLMConfig, Dict[str, Any]]) -> LLMConfig:
        """Normalize config to LLMConfig dataclass."""
        if isinstance(config, LLMConfig):
            return config
        
        return LLMConfig(
            model=config.get("model", ""),
            api_key=config.get("api_key", ""),
            max_tokens=config.get("max_tokens"),
            temperature=config.get("temperature"),
            top_p=config.get("top_p"),
            stream=config.get("stream", False),
            provider=config.get("provider"),
            use_case=config.get("use_case", "general"),
            user_id=config.get("user_id", self._config.user_id),
            agent_id=config.get("agent_id"),
            app_id=config.get("app_id", self._config.app_id),
            model_id=config.get("model_id"),
            risk_level=config.get("risk_level", RiskLevel.LOW),
            meta_data=config.get("meta_data", {})
        )
    
    def _prepare_messages(
        self,
        prompt: Union[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Prepare messages for the API request."""
        if isinstance(prompt, str):
            return [{"role": "user", "content": prompt}]
        return prompt
    
    def _make_openrouter_request(
        self,
        messages: List[Dict[str, Any]],
        config: LLMConfig
    ) -> requests.Response:
        """Make a request to the OpenRouter API."""
        url = f"{self._config.openrouter_base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://eco-compute.dev",
            "X-Title": "Eco-Compute SDK"
        }
        
        payload: Dict[str, Any] = {
            "model": config.model,
            "messages": messages
        }
        
        if config.max_tokens is not None:
            payload["max_tokens"] = config.max_tokens
        if config.temperature is not None:
            payload["temperature"] = config.temperature
        if config.top_p is not None:
            payload["top_p"] = config.top_p
        if config.stream:
            payload["stream"] = config.stream
        
        response = self._session.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        return response
    
    def _extract_provider(
        self,
        model_name: str,
        config_provider: Optional[str]
    ) -> str:
        """Extract provider from model name or config."""
        if config_provider:
            return config_provider
        
        if "/" in model_name:
            return model_name.split("/")[0]
        
        return "unknown"
    
    def _calculate_estimation(
        self,
        tokens_input: int,
        tokens_output: int,
        tokens_total: int,
        model_name: str
    ) -> EstimationResult:
        """Calculate sustainability estimation metrics."""
        # Get energy factor
        energy_factor = get_energy_factor(
            model_name,
            self._config.model_energy_factors
        )
        
        # Estimate energy
        energy_wh = estimate_energy(
            tokens_total,
            model_name,
            self._config.model_energy_factors
        )
        
        # Get carbon intensity
        carbon_intensity = get_carbon_intensity(self._config.region)
        
        # Estimate carbon
        co2_g = estimate_carbon(energy_wh, self._config.region)
        
        # Estimate cost
        cost_usd = estimate_cost(
            tokens_input,
            tokens_output,
            model_name,
            self._config.model_pricing
        )
        
        return EstimationResult(
            energy_wh=energy_wh,
            co2_g=co2_g,
            cost_usd=cost_usd,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            tokens_total=tokens_total,
            carbon_intensity=carbon_intensity,
            region=self._config.region,
            model_energy_factor=energy_factor
        )
    
    def _create_telemetry_record(
        self,
        request_id: str,
        request_hash: str,
        model_name: str,
        provider: str,
        tokens_input: int,
        tokens_output: int,
        tokens_total: int,
        estimation: EstimationResult,
        latency_ms: float,
        llm_config: LLMConfig
    ) -> TelemetryRecord:
        """Create a telemetry record for the request."""
        now = datetime.now(timezone.utc)
        
        return TelemetryRecord(
            id=request_id,
            app_id=llm_config.app_id or self._config.app_id or "",
            model_id=llm_config.model_id or model_name,
            user_id=llm_config.user_id or "",
            agent_id=llm_config.agent_id or "",
            timestamp=now.isoformat(),
            request_hash=request_hash,
            computer_name=get_computer_name(),
            process_name=get_process_name(),
            model_name=model_name,
            provider=provider,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            tokens_total=tokens_total,
            energy_wh=estimation.energy_wh,
            co2_g=estimation.co2_g,
            region=self._config.region,
            carbon_intensity=estimation.carbon_intensity,
            latency_ms=latency_ms,
            use_case=llm_config.use_case,
            risk_level=llm_config.risk_level.value if isinstance(llm_config.risk_level, RiskLevel) else llm_config.risk_level,
            policy_applied="",
            policy_action=PolicyAction.ALLOW.value,
            cost_usd=estimation.cost_usd,
            meta_data=llm_config.meta_data,
            created_at=now.isoformat()
        )
    
    def estimate_only(
        self,
        tokens_input: int,
        tokens_output: int,
        model: str
    ) -> Dict[str, float]:
        """
        Estimate sustainability metrics without making an API call.
        
        Useful for cost/impact estimation before making actual requests.
        
        Args:
            tokens_input: Estimated input tokens
            tokens_output: Estimated output tokens
            model: Model name
        
        Returns:
            Dictionary with estimation metrics
        
        Example:
            >>> estimate = eco.estimate_only(1000, 500, "gpt-4")
            >>> print(f"Estimated cost: ${estimate['cost_usd']:.4f}")
        """
        tokens_total = tokens_input + tokens_output
        estimation = self._calculate_estimation(
            tokens_input, tokens_output, tokens_total, model
        )
        
        return {
            "energy_wh": estimation.energy_wh,
            "co2_g": estimation.co2_g,
            "cost_usd": estimation.cost_usd,
            "carbon_intensity": estimation.carbon_intensity,
            "region": estimation.region
        }
    
    def flush_telemetry(self, timeout_seconds: float = 10.0) -> None:
        """
        Flush pending telemetry records.
        
        Blocks until all queued records are sent or timeout expires.
        
        Args:
            timeout_seconds: Maximum time to wait
        """
        self._telemetry.flush(timeout_seconds)
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the client and cleanup resources.
        
        Args:
            wait: Whether to wait for pending telemetry
        """
        self._telemetry.shutdown(wait)
        self._session.close()
    
    def __enter__(self) -> "EcoCompute":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.shutdown()


# Convenience function for simple usage
def call_llm(
    prompt: Union[str, List[Dict[str, Any]]],
    config: Dict[str, Any],
    sdk_config: Optional[EcoComputeConfig] = None
) -> Dict[str, Any]:
    """
    Make an LLM call with sustainability tracking (convenience function).
    
    This is a simple wrapper that creates a temporary EcoCompute client
    for one-off calls. For multiple calls, use the EcoCompute class directly.
    
    Args:
        prompt: The prompt string or messages
        config: LLM configuration dict
        sdk_config: Optional SDK configuration
    
    Returns:
        Result dictionary with response and estimation
    
    Example:
        >>> from eco_compute import call_llm
        >>> 
        >>> result = call_llm(
        ...     "Hello!",
        ...     {"model": "openai/gpt-4o-mini", "api_key": "sk-..."}
        ... )
    """
    with EcoCompute(sdk_config) as eco:
        return eco.call_llm(prompt, config)
