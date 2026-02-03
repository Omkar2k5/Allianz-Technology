"""
Eco-Compute GenAI Sustainability Proxy

Application-aware reverse proxy that intercepts GenAI requests to:
- Count tokens
- Calculate energy consumption
- Estimate CO₂ emissions
- Enforce policies
- Log metrics
- Forward to providers
"""

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
import logging
from contextlib import asynccontextmanager
from typing import Optional
import hashlib
import time

from app.config import settings
from app.calculators.energy import calculate_energy
from app.calculators.carbon import calculate_carbon
from app.calculators.tokens import count_tokens
from app.providers import openai_client, azure_client
from app.logging.request_logger import log_request
from app.policies.enforcer import enforce_policies

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting GenAI Sustainability Proxy...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Policy Enforcement: {'Enabled' if settings.ENABLE_POLICY_ENFORCEMENT else 'Disabled'}")
    
    yield
    
    logger.info("Shutting down GenAI Proxy...")


# Create FastAPI app
app = FastAPI(
    title="GenAI Sustainability Proxy",
    description="Application-aware proxy for environmental impact tracking",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs"
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "genai-proxy",
        "version": "1.0.0"
    }


@app.post("/v1/chat/completions")
async def proxy_openai_chat(
    request: Request,
    x_app_id: Optional[str] = Header(None),
    x_use_case: Optional[str] = Header(None),
    x_risk_level: Optional[str] = Header(None)
):
    """
    Proxy endpoint for OpenAI chat completions
    
    Intercepts requests, calculates environmental impact, and forwards to OpenAI
    """
    start_time = time.time()
    
    try:
        # Parse request body
        body = await request.json()
        model = body.get("model", "gpt-3.5-turbo")
        messages = body.get("messages", [])
        
        # Extract metadata from headers
        metadata = {
            "app_id": x_app_id,
            "use_case": x_use_case or "general",
            "risk_level": x_risk_level or "medium",
            "model": model,
            "provider": "openai"
        }
        
        # Count input tokens
        input_tokens = count_tokens(messages, model)
        
        # Create request hash (NO actual prompt storage)
        request_hash = hashlib.sha256(str(messages).encode()).hexdigest()
        
        # Policy enforcement
        if settings.ENABLE_POLICY_ENFORCEMENT:
            policy_result = await enforce_policies(metadata, model)
            if policy_result["action"] == "block":
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "Policy violation",
                        "message": policy_result["message"],
                        "policy": policy_result["policy_name"]
                    }
                )
            elif policy_result["action"] == "downgrade":
                # Downgrade model
                model = policy_result["downgrade_to"]
                body["model"] = model
                logger.info(f"Model downgraded to {model} due to policy")
        
        # Forward request to OpenRouter or OpenAI
        # Determine which provider to use
        if settings.OPENROUTER_API_KEY:
            # Use OpenRouter
            api_url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
            api_key = settings.OPENROUTER_API_KEY
            logger.info(f"Forwarding to OpenRouter: {model}")
        elif settings.OPENAI_API_KEY:
            # Use OpenAI
            api_url = "https://api.openai.com/v1/chat/completions"
            api_key = settings.OPENAI_API_KEY
            logger.info(f"Forwarding to OpenAI: {model}")
        else:
            raise HTTPException(
                status_code=500,
                detail="No API key configured. Please set OPENROUTER_API_KEY or OPENAI_API_KEY"
            )
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                api_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",  # Required for OpenRouter
                    "X-Title": "Eco-Compute"  # Optional for OpenRouter
                },
                json=body,
                timeout=60.0
            )
        
        if response.status_code != 200:
            logger.error(f"OpenAI API error: {response.status_code}")
            return JSONResponse(
                status_code=response.status_code,
                content=response.json()
            )
        
        # Parse response
        response_data = response.json()
        
        # Extract output tokens
        usage = response_data.get("usage", {})
        output_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", input_tokens + output_tokens)
        
        # Calculate environmental impact
        energy_wh = calculate_energy(total_tokens, model)
        
        # Get region from request or default
        region = request.headers.get("x-region", "us-east-1")
        co2_g = calculate_carbon(energy_wh, region)
        
        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Log request to Analytics API
        await log_request({
            "app_id": x_app_id,
            "model": model,
            "provider": "openai",
            "request_hash": request_hash,
            "tokens_input": input_tokens,
            "tokens_output": output_tokens,
            "tokens_total": total_tokens,
            "energy_wh": energy_wh,
            "co2_g": co2_g,
            "region": region,
            "latency_ms": latency_ms,
            "use_case": metadata["use_case"],
            "risk_level": metadata["risk_level"],
            "policy_applied": settings.ENABLE_POLICY_ENFORCEMENT,
            "policy_action": policy_result.get("action", "allowed") if settings.ENABLE_POLICY_ENFORCEMENT else "allowed"
        })
        
        # Add sustainability headers to response
        response_headers = {
            "X-Energy-Wh": str(energy_wh),
            "X-CO2-g": str(co2_g),
            "X-Tokens-Total": str(total_tokens),
            "X-Region": region
        }
        
        return JSONResponse(
            content=response_data,
            headers=response_headers
        )
        
    except Exception as e:
        logger.error(f"Proxy error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/completions")
async def proxy_openai_completions(
    request: Request,
    x_app_id: Optional[str] = Header(None),
    x_use_case: Optional[str] = Header(None),
    x_risk_level: Optional[str] = Header(None)
):
    """Proxy endpoint for OpenAI text completions"""
    # Similar implementation to chat completions
    return {"message": "Text completions endpoint - implementation similar to chat"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "GenAI Sustainability Proxy",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/v1/chat/completions",
            "completions": "/v1/completions",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PROXY_PORT,
        reload=settings.DEBUG
    )
