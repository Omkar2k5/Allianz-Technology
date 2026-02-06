"""
Configuration settings for Analytics API
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # API
    API_PORT: int = 8000
    API_LOG_LEVEL: str = "info"
    
    # Database
    DATABASE_URL: str = "postgresql://admin:password@localhost:5432/ecocompute"
    
    # Authentication
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://frontend:3000",
        "http://localhost:5173"
    ]
    
    # External Services
    PROXY_URL: str = "http://genai-proxy:8001"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
