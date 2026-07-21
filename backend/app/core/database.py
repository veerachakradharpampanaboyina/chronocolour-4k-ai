"""
ChronoColor 4K AI — MongoDB Database Connection

Provides async MongoDB connection via Motor and Beanie ODM.
Handles connection lifecycle and document model initialization.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

if TYPE_CHECKING:
    from app.config import Settings

logger = structlog.get_logger(__name__)

# Module-level client reference
_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


async def init_database(settings: Settings) -> AsyncIOMotorDatabase:
    """
    Initialize MongoDB connection and Beanie ODM.

    Args:
        settings: Application settings with MongoDB URI and database name.

    Returns:
        The initialized Motor database instance.
    """
    global _client, _database

    logger.info(
        "connecting_to_mongodb",
        database=settings.mongodb_database,
    )

    _client = AsyncIOMotorClient(
        settings.mongodb_uri,
        maxPoolSize=50,
        minPoolSize=10,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
    )

    _database = _client[settings.mongodb_database]

    # Import document models for Beanie initialization
    from app.models.job import Job
    from app.models.video import Video

    await init_beanie(
        database=_database,
        document_models=[Video, Job],
    )

    # Verify connection
    await _client.admin.command("ping")
    logger.info("mongodb_connected", database=settings.mongodb_database)

    return _database


async def close_database() -> None:
    """Close MongoDB connection gracefully."""
    global _client, _database

    if _client:
        _client.close()
        _client = None
        _database = None
        logger.info("mongodb_disconnected")


def get_database() -> AsyncIOMotorDatabase:
    """
    Get the active database instance.

    Returns:
        The Motor database instance.

    Raises:
        RuntimeError: If database has not been initialized.
    """
    if _database is None:
        raise RuntimeError(
            "Database not initialized. Call init_database() first."
        )
    return _database
