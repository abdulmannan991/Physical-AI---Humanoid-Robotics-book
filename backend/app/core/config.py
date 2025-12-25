"""
Core Configuration Module

Loads and validates all environment variables using Pydantic Settings.
All API keys and sensitive configuration must be loaded from environment variables only.

Constitution: backend/.specify/memory/constitution.md (Section 5.3 - No hardcoded secrets)
"""

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are loaded from .env file or environment variables.
    NO hardcoded secrets allowed (Constitution Section 5.3).
    """

    # Application
    APP_NAME: str = "rag-chatbot-backend"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: str = Field(default="INFO")

    # API Configuration
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins"
    )
    ADMIN_API_KEY: str = Field(
        ...,
        description="Secret API key for admin endpoints (required)"
    )
    RATE_LIMIT_PER_MINUTE: int = Field(default=10)
    REQUEST_TIMEOUT: int = Field(default=30)

    # Cohere (LLM and Embeddings)
    COHERE_API_KEY: str = Field(
        ...,
        description="Cohere API key for LLM and embeddings (required)"
    )
    COHERE_CHAT_MODEL: str = Field(default="command-r-plus-08-2024")
    EMBEDDING_MODEL_NAME: str = Field(default="embed-english-v3.0")
    ENABLE_COHERE_RERANKING: bool = Field(default=False)

    # Qdrant Vector Database
    QDRANT_URL: str = Field(default="http://localhost:6333")
    QDRANT_API_KEY: Optional[str] = Field(default=None)
    QDRANT_COLLECTION_NAME: str = Field(default="course_content")
    QDRANT_VECTOR_SIZE: int = Field(default=1024)

    # Neon PostgreSQL
    DATABASE_URL: str = Field(
        ...,
        description="Neon PostgreSQL connection string (required)"
    )
    DB_POOL_MIN_SIZE: int = Field(default=2)
    DB_POOL_MAX_SIZE: int = Field(default=10)

    # JWT Authentication
    JWT_SECRET_KEY: str = Field(
        ...,
        description="Secret key for JWT token signing (required, 256-bit minimum)"
    )
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440)  # 1 day
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(default=10080)  # 7 days

    # RAG Configuration
    RETRIEVAL_TOP_K: int = Field(default=5, ge=1, le=10)
    CONFIDENCE_THRESHOLD: float = Field(default=0.2, ge=0.0, le=1.0)
    MAX_CHUNK_SIZE: int = Field(default=512)
    CHUNK_OVERLAP: int = Field(default=50)
    ENABLE_RERANKING: bool = Field(default=False)

    # Content Ingestion
    DOCS_PATH: str = Field(default="../docs")
    INGESTION_FILE_PATTERNS: str = Field(default="*.md,*.mdx")
    INGESTION_EXCLUDE_PATTERNS: str = Field(
        default="**/node_modules/**,**/build/**"
    )

    # Performance
    WORKERS: int = Field(default=4)
    ENABLE_EMBEDDING_CACHE: bool = Field(default=True)
    CACHE_TTL: int = Field(default=3600)

    # Monitoring
    ENABLE_METRICS: bool = Field(default=False)
    SENTRY_DSN: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: str) -> str:
        """Validate CORS origins format"""
        origins = [origin.strip() for origin in v.split(",")]
        for origin in origins:
            if not origin.startswith(("http://", "https://")):
                raise ValueError(
                    f"Invalid CORS origin: {origin}. Must start with http:// or https://"
                )
        return v

    @field_validator("QDRANT_VECTOR_SIZE")
    @classmethod
    def validate_vector_size(cls, v: int) -> int:
        """Validate vector size matches Cohere embed-english-v3.0 (1024 dimensions)"""
        if v != 1024:
            raise ValueError(
                f"QDRANT_VECTOR_SIZE must be 1024 to match Cohere embed-english-v3.0, got {v}"
            )
        return v

    def get_cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
# This will be imported throughout the application
settings = Settings()
