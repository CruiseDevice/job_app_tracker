import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

# Get the backend directory path
BACKEND_DIR = Path(__file__).parent.parent
DATABASE_PATH = BACKEND_DIR / "database.db"

class Settings(BaseSettings):
    # Database
    database_url: str = f"sqlite:///{DATABASE_PATH}"
    
    # API Settings
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    debug: bool = True
    
    # Email credentials (simple IMAP approach)
    email_address: Optional[str] = None
    email_password: Optional[str] = None
    
    # OpenAI API
    openai_api_key: Optional[str] = None
    
    # Email monitoring
    email_check_interval: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"

settings = Settings()