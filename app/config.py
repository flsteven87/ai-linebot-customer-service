"""
Application configuration.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # App settings
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # LINE Bot credentials
    CHANNEL_ACCESS_TOKEN: Optional[str] = None
    CHANNEL_SECRET: Optional[str] = None
    
    # OpenAI API
    OPENAI_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: Optional[PostgresDsn] = None
    
    # Ngrok settings
    NGROK_AUTHTOKEN: Optional[str] = None
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"  # 允許額外的環境變數
    }

# Create global settings object
settings = Settings() 