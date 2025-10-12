from pydantic_settings import BaseSettings
from typing import List, Union
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "Parlay App"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql://parlay_user:parlay_password@db:5432/parlay_db"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://frontend:3000",
    ]

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # External API Configuration
    ODDS_API_BASE_URL: str = "https://api.the-odds-api.com/v4"
    ODDS_API_KEY: str = "91077685ec8540c0d6018efa6226fb35"

    class Config:
        env_file = ".env"


settings = Settings()
