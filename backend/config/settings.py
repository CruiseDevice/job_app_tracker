import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./database.db"
    
    # API Settings
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    debug: bool = True
    
    # Google API
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    
    # OpenAI API
    openai_api_key: Optional[str] = None
    
    # Email monitoring
    email_check_interval: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"

settings = Settings()