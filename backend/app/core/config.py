import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_PREFIX: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    # BACKEND_CORS_ORIGINS is a comma-separated list of origins
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "business-idea-scorer"
    
    # Database Settings
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "business_idea_scorer")
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        postgres_dsn = PostgresDsn.build(
            scheme="postgresql",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            path=f"/{values.data.get('POSTGRES_DB') or ''}",
        )
        return postgres_dsn
    
    # GPT API Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GPT_MODEL: str = os.getenv("GPT_MODEL", "gpt-4o")
    
    # Scoring System Weights
    WEIGHT_MARKET_BUSINESS_MODEL: float = float(os.getenv("WEIGHT_MARKET_BUSINESS_MODEL", "35"))
    WEIGHT_COMPETITIVE_LANDSCAPE: float = float(os.getenv("WEIGHT_COMPETITIVE_LANDSCAPE", "15"))
    WEIGHT_EXECUTION_TEAM: float = float(os.getenv("WEIGHT_EXECUTION_TEAM", "20"))
    WEIGHT_RISK_FACTORS: float = float(os.getenv("WEIGHT_RISK_FACTORS", "10"))
    WEIGHT_NETWORK_PLATFORM_RISKS: float = float(os.getenv("WEIGHT_NETWORK_PLATFORM_RISKS", "10"))
    WEIGHT_SOCIAL_ENVIRONMENTAL_IMPACT: float = float(os.getenv("WEIGHT_SOCIAL_ENVIRONMENTAL_IMPACT", "10"))
    
    # Maximum file upload size (in MB)
    MAX_UPLOAD_SIZE_MB: int = 10
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
