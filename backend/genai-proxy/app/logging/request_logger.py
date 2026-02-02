"""
Request logger

Logs GenAI requests to Analytics API
"""

import httpx
import logging
from typing import Dict
from app.config import settings

logger = logging.getLogger(__name__)


async def log_request(request_data: Dict):
    """
    Log request to Analytics API
    
    Args:
        request_data: Dictionary containing request metadata
    """
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.ANALYTICS_API_URL}/api/v1/requests/log",
                json=request_data,
                timeout=5.0
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to log request: {response.status_code}")
            else:
                logger.debug(f"Request logged successfully: {request_data.get('request_hash')}")
                
    except Exception as e:
        logger.error(f"Error logging request: {e}")
        # Don't fail the main request if logging fails
