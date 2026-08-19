"""Core application settings for ScoutSphere backend using Pydantic BaseSettings."""

from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """System configuration parameters loaded from environment variables."""

    PROJECT_NAME: str = "ScoutSphere"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./scoutsphere.db"

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if "@db:" in v or "postgresql" in v:
            return "sqlite+aiosqlite:///./scoutsphere.db"
        return v

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"

    # Authentication
    JWT_SECRET: str = "super_secret_jwt_key_change_in_production_32bytes_min"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15
    GOOGLE_CLIENT_ID: str = ""

    # LLM Providers
    LLM_PROVIDER_CHAIN: str = "gemini,groq,openrouter,ollama"
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Embeddings
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def provider_list(self) -> List[str]:
        """Parses the comma-separated provider fallback chain into a list."""
        return [p.strip().lower() for p in self.LLM_PROVIDER_CHAIN.split(",") if p.strip()]


settings = Settings()
