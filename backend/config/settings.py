from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # database
    database_url: str = "sqlite:///./database.db"

    # api settings
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    debug: bool = True

settings = Settings()