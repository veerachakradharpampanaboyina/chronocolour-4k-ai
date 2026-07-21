"""
ChronoColor 4K AI — Job API Endpoints

Handles job creation, progress tracking, listing, and cancellation.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from app.models.job import JobStatus
from app.schemas.job import (
    JobCancelResponse,
    JobCreateRequest,
    JobCreateResponse,
    JobDetailResponse,
    JobListResponse,
)
from app.schemas.pipeline import PipelinePresetInfo, get_preset_info
from app.services import job_service

router = APIRouter()


@router.post(
    "",
    response_model=JobCreateResponse,
    status_code=201,
    summary="Create a processing job",
)
async def create_job(request: JobCreateRequest) -> JobCreateResponse:
    """
    Create a new AI processing job for a video.

    The pipeline configuration controls which stages are enabled
    and which AI models are used. Use quality presets for convenience:
    - **fast**: Essential stages only, 1080p output
    - **balanced**: Full pipeline, 4K output (recommended)
    - **maximum**: Premium models, highest quality 4K output
    """
    return await job_service.create_job(
        video_id=request.video_id,
        pipeline_config=request.pipeline_config,
    )


@router.get(
    "",
    response_model=JobListResponse,
    summary="List processing jobs",
)
async def list_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[JobStatus] = Query(None, description="Filter by status"),
    video_id: Optional[str] = Query(None, description="Filter by video ID"),
) -> JobListResponse:
    """List all processing jobs with pagination and optional filters."""
    return await job_service.list_jobs(
        page=page, page_size=page_size, status=status, video_id=video_id
    )


@router.get(
    "/presets",
    response_model=list[PipelinePresetInfo],
    summary="Get pipeline quality presets",
)
async def get_presets() -> list[PipelinePresetInfo]:
    """Get available pipeline quality presets with descriptions."""
    return get_preset_info()


@router.get(
    "/{job_id}",
    response_model=JobDetailResponse,
    summary="Get job details",
)
async def get_job(job_id: str) -> JobDetailResponse:
    """
    Get full details for a processing job.

    Includes per-stage progress, estimated time remaining,
    and download URL when completed.
    """
    return await job_service.get_job(job_id)


@router.post(
    "/{job_id}/cancel",
    response_model=JobCancelResponse,
    summary="Cancel a running job",
)
async def cancel_job(job_id: str) -> JobCancelResponse:
    """
    Cancel a running or queued processing job.

    This will terminate the Celery task and mark the job as cancelled.
    Already completed or failed jobs cannot be cancelled.
    """
    return await job_service.cancel_job(job_id)
