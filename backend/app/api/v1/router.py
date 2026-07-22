"""
ChronoColor 4K AI — API v1 Router

Main router that assembles all v1 API endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.results import router as results_router
from app.api.v1.storage import router as storage_router
from app.api.v1.videos import router as videos_router
from app.api.v1.websocket import router as ws_router

api_router = APIRouter()

# Include sub-routers
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(videos_router, prefix="/videos", tags=["Videos"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(results_router, prefix="/results", tags=["Results"])
api_router.include_router(storage_router, prefix="/storage", tags=["Storage"])
api_router.include_router(ws_router, prefix="/ws", tags=["WebSocket"])
