"""
ChronoColor 4K AI — Application Configuration

All settings are loaded from environment variables with sensible defaults.
Uses Pydantic Settings for type-safe configuration with validation.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "ChronoColor 4K AI"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    use_local_services: bool = True  # Use in-memory mocks instead of Docker services

    # --- FastAPI ---
    api_host: str = "0.0.0.0"
    api_port: int = 8005
    api_workers: int = 4
    api_cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    # --- MongoDB ---
    mongodb_uri: str = "mongodb://chronocolor:chronocolor_secret@localhost:27017"
    mongodb_database: str = "chronocolor"

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_db: int = 1
    redis_pubsub_db: int = 2

    # --- MinIO / S3 Storage ---
    storage_endpoint: str = "localhost:9000"
    storage_access_key: str = "chronocolor_access"
    storage_secret_key: str = "chronocolor_secret_key"
    storage_bucket_raw: str = "raw-videos"
    storage_bucket_frames: str = "processed-frames"
    storage_bucket_results: str = "results"
    storage_use_ssl: bool = False
    storage_region: str = "us-east-1"
    local_storage_dir: str = "D:\\chronocolor_storage"

    # --- Celery ---
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    celery_task_always_eager: bool = False

    # --- GPU ---
    gpu_device_ids: str = "0"
    gpu_memory_fraction: float = 0.9
    gpu_allow_growth: bool = True

    # --- AI Models ---
    models_dir: str = "/app/models"
    default_superres_model: str = "real_esrgan"
    default_face_model: str = "codeformer"
    default_colorization_model: str = "ddcolor"
    default_restoration_model: str = "nafnet"
    default_flow_model: str = "raft"

    # --- Video Processing ---
    max_video_size_mb: int = 5000
    max_video_duration_seconds: int = 600
    ffmpeg_threads: int = 4
    output_video_codec: str = "libx265"
    output_video_crf: int = 18
    output_video_preset: str = "slow"

    # --- Security ---
    secret_key: str = "change-this-to-a-random-64-char-string-in-production"
    access_token_expire_minutes: int = 1440

    # --- Frontend ---
    next_public_api_url: str = "http://localhost:8000"
    next_public_ws_url: str = "ws://localhost:8000"

    @field_validator("api_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def gpu_device_list(self) -> list[int]:
        """Parse GPU device IDs from comma-separated string."""
        return [int(d.strip()) for d in self.gpu_device_ids.split(",")]

    @property
    def models_path(self) -> Path:
        """Get the models directory as a Path object."""
        return Path(self.models_dir)

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == "production"

    @property
    def storage_url(self) -> str:
        """Full storage endpoint URL."""
        protocol = "https" if self.storage_use_ssl else "http"
        return f"{protocol}://{self.storage_endpoint}"

    @property
    def all_storage_buckets(self) -> list[str]:
        """List of all storage buckets to create on startup."""
        return [
            self.storage_bucket_raw,
            self.storage_bucket_frames,
            self.storage_bucket_results,
        ]


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.
    Uses lru_cache so settings are loaded once and reused.
    """
    return Settings()
