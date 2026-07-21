"""
ChronoColor 4K AI — Health Check Endpoints

System health and readiness endpoints for monitoring and orchestration.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    version: str
    timestamp: str
    environment: str
    checks: dict[str, str]


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    System health check.

    Verifies connectivity to MongoDB, Redis, and MinIO.
    Used by Docker health checks and load balancers.
    """
    from app.config import get_settings

    settings = get_settings()
    checks: dict[str, str] = {}

    # Check MongoDB
    try:
        from app.core.database import get_database

        db = get_database()
        await db.command("ping")
        checks["mongodb"] = "healthy"
    except Exception as e:
        checks["mongodb"] = f"unhealthy: {str(e)[:100]}"

    # Check Redis
    try:
        from app.core.redis import get_redis

        redis = get_redis()
        await redis.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)[:100]}"

    # Check MinIO
    try:
        from app.core.storage import get_s3_client, get_storage_settings

        client = get_s3_client()
        storage_settings = get_storage_settings()
        client.head_bucket(Bucket=storage_settings.storage_bucket_raw)
        checks["storage"] = "healthy"
    except Exception as e:
        checks["storage"] = f"unhealthy: {str(e)[:100]}"

    # Overall status
    all_healthy = all(v == "healthy" for v in checks.values())

    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        service="ChronoColor 4K AI",
        version="1.0.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
        environment=settings.app_env,
        checks=checks,
    )


class ReadinessResponse(BaseModel):
    """Readiness check response."""

    ready: bool
    message: str


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check() -> ReadinessResponse:
    """
    Readiness check for orchestration systems.

    Returns ready=true only when all critical services are available.
    """
    try:
        from app.core.database import get_database
        from app.core.redis import get_redis

        db = get_database()
        await db.command("ping")

        redis = get_redis()
        await redis.ping()

        return ReadinessResponse(ready=True, message="All systems operational")
    except Exception as e:
        return ReadinessResponse(ready=False, message=f"Not ready: {str(e)[:200]}")
