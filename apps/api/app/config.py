from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    app_env: str = "development"
    log_level: str = "INFO"
    api_cors_origins: str = "http://localhost:3000"
    database_url: str = "sqlite:///./evidence_rag.db"
    upload_dir: Path = Path("./uploads")
    max_upload_bytes: int = 10 * 1024 * 1024

    chunk_size_chars: int = Field(default=1200, ge=300, le=4000)
    chunk_overlap_chars: int = Field(default=180, ge=0, le=1000)
    default_top_k: int = Field(default=5, ge=1, le=10)
    max_top_k: int = Field(default=10, ge=1, le=25)
    min_evidence_score: float = Field(default=0.18, ge=-1, le=1)
    min_lexical_coverage: float = Field(default=0.35, ge=0, le=1)

    ai_provider: str = "mock"
    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-5-mini"
    embedding_dimensions: int = Field(default=1536, ge=32, le=4096)
    openai_input_usd_per_million: float = Field(default=0, ge=0)
    openai_output_usd_per_million: float = Field(default=0, ge=0)
    openai_embedding_usd_per_million: float = Field(default=0, ge=0)

    @field_validator("ai_provider")
    @classmethod
    def validate_provider(cls, value: str) -> str:
        normalized = value.lower().strip()
        if normalized not in {"mock", "openai"}:
            raise ValueError("AI_PROVIDER must be 'mock' or 'openai'")
        return normalized

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.api_cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
