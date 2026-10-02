from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):

    # -------------------------
    # Application
    # -------------------------

    app_name: str = (
        "Autonomous Data Analyst"
    )

    environment: str = "development"

    debug: bool = False

    log_level: str = "INFO"

    max_upload_bytes: int = 100 * 1024 * 1024

    upload_chunk_size: int = 1024 * 1024

    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    allowed_hosts: str = "localhost,127.0.0.1,testserver"

    # -------------------------
    # LLM Settings
    # -------------------------

    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"
    
    perplexity_api_key: str = ""
    perplexity_model: str = "sonar"

    # -------------------------
    # PostgreSQL
    # -------------------------

    database_url: str = "postgresql+asyncpg://analyst:analyst_password@localhost:5432/autonomous_analyst"
    
    # -------------------------
    # Authentication
    # -------------------------

    secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # -------------------------
    # S3 Object Storage
    # -------------------------
    
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    s3_bucket_name: str | None = None
    s3_endpoint_url: str | None = None  # for MinIO/LocalStack
    
    # -------------------------
    # Celery / Redis
    # -------------------------
    
    redis_url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:

    return Settings()


settings = get_settings()
