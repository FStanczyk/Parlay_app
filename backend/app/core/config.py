from pydantic_settings import BaseSettings
from typing import List
import os
import json


class Settings(BaseSettings):
    PROJECT_NAME: str = "Parlay App"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # CORS - supports JSON array or comma-separated string from env
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://frontend:3000",
    ]

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # External API Configuration
    ODDS_API_BASE_URL: str = "https://api.the-odds-api.com/v4"
    ODDS_API_KEY: str

    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        cors_env = os.getenv("BACKEND_CORS_ORIGINS")
        if cors_env:
            try:
                self.BACKEND_CORS_ORIGINS = json.loads(cors_env)
            except json.JSONDecodeError:
                self.BACKEND_CORS_ORIGINS = [
                    origin.strip() for origin in cors_env.split(",") if origin.strip()
                ]


settings = Settings()
