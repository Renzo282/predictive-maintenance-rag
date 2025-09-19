"""
Application configuration settings
"""
import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    
    # Database Configuration
    DATABASE_URL: str
    
    # Notification Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Slack Configuration
    SLACK_BOT_TOKEN: Optional[str] = None
    SLACK_CHANNEL: Optional[str] = None
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Monitoring
    PROMETHEUS_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # ML Model Configuration
    MODEL_UPDATE_INTERVAL: int = 3600  # seconds
    PREDICTION_THRESHOLD: float = 0.8
    ANOMALY_THRESHOLD: float = 0.7
    
    # RAG Configuration
    VECTOR_STORE_PATH: str = "./data/vector_store"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
