"""
ChronoColor 4K AI — FastAPI Application Entry Point

Configures the FastAPI app with lifespan management, middleware,
CORS, and API routing.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.api.v1.router import api_router
from app.config import get_settings
from app.core.database import close_database, init_database
from app.core.redis import close_redis, init_redis
from app.core.storage import init_storage

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Initializes and tears down database, Redis, and storage connections.
    """
    settings = get_settings()

    # --- Startup ---
    logger.info(
        "starting_application",
        app_name=settings.app_name,
        environment=settings.app_env,
    )

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    # Initialize services
    await init_database(settings)
    await init_redis(settings)
    await init_storage(settings)

    logger.info("application_started", api_docs="/docs")

    yield

    # --- Shutdown ---
    logger.info("shutting_down_application")
    await close_redis()
    await close_database()
    logger.info("application_stopped")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description=(
            "Transform Black & White Videos into Cinematic 4K Color Masterpieces. "
            "AI-powered video colorization, restoration, and upscaling pipeline."
        ),
        version="1.0.0",
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # --- CORS ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api_cors_origins,
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- API Routes ---
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
