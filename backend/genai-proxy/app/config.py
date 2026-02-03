"""
Configuration settings for GenAI Proxy
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Proxy
    PROXY_PORT: int = 8001
    PROXY_LOG_LEVEL: str = "info"
    
    # Database
    DATABASE_URL: str = "postgresql://admin:password@localhost:5432/ecocompute"
    
    # External Services
    ANALYTICS_API_URL: str = "http://localhost:8000"
    
    # GenAI Provider API Keys
    # OpenRouter (for testing)
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # OpenAI (optional)
    OPENAI_API_KEY: str = ""
    AZURE_OPENAI_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    GOOGLE_AI_KEY: str = ""
    
    # Policy Enforcement
    ENABLE_POLICY_ENFORCEMENT: bool = True
    DEFAULT_POLICY_MODE: str = "warn"  # warn, block, or allow
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
