"""
ChronoColor 4K AI — Redis Connection Manager

Provides Redis connection for caching and Pub/Sub (real-time progress updates).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import redis.asyncio as aioredis
import structlog

if TYPE_CHECKING:
    from app.config import Settings

logger = structlog.get_logger(__name__)

# Module-level references
_redis_client: aioredis.Redis | None = None
_pubsub_client: aioredis.Redis | None = None


async def init_redis(settings: Settings) -> aioredis.Redis:
    """
    Initialize Redis connections for caching and Pub/Sub.

    Args:
        settings: Application settings with Redis URL.

    Returns:
        The main Redis client instance.
    """
    global _redis_client, _pubsub_client

    logger.info("connecting_to_redis", url=settings.redis_url)

    # Main client (cache + Celery result backend)
    _redis_client = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
        socket_connect_timeout=5,
        retry_on_timeout=True,
    )

    # Separate client for Pub/Sub (progress updates)
    pubsub_url = settings.redis_url.rsplit("/", 1)[0] + f"/{settings.redis_pubsub_db}"
    _pubsub_client = aioredis.from_url(
        pubsub_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=10,
    )

    # Verify connection
    await _redis_client.ping()
    logger.info("redis_connected")

    return _redis_client


async def close_redis() -> None:
    """Close Redis connections gracefully."""
    global _redis_client, _pubsub_client

    if _redis_client:
        await _redis_client.close()
        _redis_client = None

    if _pubsub_client:
        await _pubsub_client.close()
        _pubsub_client = None

    logger.info("redis_disconnected")


def get_redis() -> aioredis.Redis:
    """Get the main Redis client."""
    if _redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return _redis_client


def get_pubsub_redis() -> aioredis.Redis:
    """Get the Pub/Sub Redis client (separate connection for subscribe)."""
    if _pubsub_client is None:
        raise RuntimeError("Redis Pub/Sub not initialized. Call init_redis() first.")
    return _pubsub_client


async def publish_progress(job_id: str, data: dict) -> None:
    """
    Publish a progress update for a processing job.

    Args:
        job_id: The job identifier.
        data: Progress data dict (stage, progress, message, etc.)
    """
    import orjson

    client = get_pubsub_redis()
    channel = f"job:{job_id}:progress"
    payload = orjson.dumps(data).decode("utf-8")
    await client.publish(channel, payload)
