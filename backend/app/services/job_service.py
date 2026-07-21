"""
ChronoColor 4K AI — Job Service

Business logic for creating, tracking, and managing processing jobs.
"""

from __future__ import annotations

import math
from typing import Optional

import structlog
from beanie import PydanticObjectId

from app.core.exceptions import (
    JobAlreadyRunningError,
    JobCancellationError,
    JobNotFoundError,
    VideoNotFoundError,
)
from app.core.storage import generate_presigned_url
from app.models.job import Job, JobStatus, PipelineConfig
from app.models.video import Video
from app.schemas.job import (
    JobCancelResponse,
    JobCreateResponse,
    JobDetailResponse,
    JobListItem,
    JobListResponse,
)

logger = structlog.get_logger(__name__)


async def create_job(
    video_id: str,
    pipeline_config: PipelineConfig,
) -> JobCreateResponse:
    """
    Create a new processing job for a video.

    Args:
        video_id: Source video document ID.
        pipeline_config: Pipeline configuration.

    Returns:
        JobCreateResponse with job metadata.
    """
    # Verify video exists
    video = await Video.get(PydanticObjectId(video_id))
    if not video:
        raise VideoNotFoundError(video_id)

    # Check for existing running jobs for this video
    existing = await Job.find(
        Job.video_id == video_id,
        Job.status.is_in([JobStatus.PENDING, JobStatus.QUEUED, JobStatus.RUNNING]),
    ).first_or_none()

    if existing:
        raise JobAlreadyRunningError(str(existing.id))

    # Create job document
    job = Job(
        video_id=video_id,
        video_filename=video.original_filename,
        pipeline_config=pipeline_config,
    )
    job.initialize_stages()
    await job.insert()

    # Dispatch to Celery
    from app.workers.tasks.orchestrator import run_pipeline

    task = run_pipeline.delay(str(job.id))

    # Update job with Celery task ID
    job.status = JobStatus.QUEUED
    job.celery_task_id = task.id
    await job.save()

    active_stages = job.get_active_stages()

    logger.info(
        "job_created",
        job_id=str(job.id),
        video_id=video_id,
        preset=pipeline_config.quality_preset,
        active_stages=len(active_stages),
    )

    return JobCreateResponse(
        id=str(job.id),
        video_id=video_id,
        status=job.status,
        pipeline_config=pipeline_config,
        total_stages=len(job.stages),
        active_stages=len(active_stages),
        created_at=job.created_at,
    )


async def get_job(job_id: str) -> JobDetailResponse:
    """
    Get full job detail with per-stage progress.

    Args:
        job_id: Job document ID.

    Returns:
        JobDetailResponse with stage progress and results.
    """
    job = await Job.get(PydanticObjectId(job_id))
    if not job:
        raise JobNotFoundError(job_id)

    # Generate download URL if completed
    download_url = None
    if job.result and job.result.output_storage_bucket:
        download_url = generate_presigned_url(
            job.result.output_storage_bucket,
            job.result.output_storage_key,
            expires_in=3600,
        )

    # Estimate remaining time
    estimated_time = _estimate_remaining_time(job)

    return JobDetailResponse.from_document(
        job,
        download_url=download_url,
        estimated_time=estimated_time,
    )


async def list_jobs(
    page: int = 1,
    page_size: int = 20,
    status: Optional[JobStatus] = None,
    video_id: Optional[str] = None,
) -> JobListResponse:
    """
    List jobs with pagination and optional filters.

    Args:
        page: Page number (1-indexed).
        page_size: Items per page.
        status: Optional status filter.
        video_id: Optional video ID filter.

    Returns:
        Paginated JobListResponse.
    """
    # Build query filters
    filters = []
    if status:
        filters.append(Job.status == status)
    if video_id:
        filters.append(Job.video_id == video_id)

    # Count total
    query = Job.find(*filters) if filters else Job.find()
    total = await query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    # Fetch page
    skip = (page - 1) * page_size
    jobs = (
        await Job.find(*filters)
        .sort(-Job.created_at)
        .skip(skip)
        .limit(page_size)
        .to_list()
    )

    return JobListResponse(
        jobs=[JobListItem.from_document(j) for j in jobs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


async def cancel_job(job_id: str) -> JobCancelResponse:
    """
    Cancel a running or queued job.

    Args:
        job_id: Job document ID.

    Returns:
        JobCancelResponse confirming cancellation.
    """
    job = await Job.get(PydanticObjectId(job_id))
    if not job:
        raise JobNotFoundError(job_id)

    if job.status not in (JobStatus.PENDING, JobStatus.QUEUED, JobStatus.RUNNING):
        raise JobCancellationError(job_id, job.status.value)

    # Revoke Celery task
    if job.celery_task_id:
        from app.workers.celery_app import celery_app

        celery_app.control.revoke(job.celery_task_id, terminate=True)

    job.mark_cancelled()
    await job.save()

    logger.info("job_cancelled", job_id=job_id)

    return JobCancelResponse(
        id=str(job.id),
        status=job.status,
    )


def _estimate_remaining_time(job: Job) -> float | None:
    """
    Estimate remaining processing time based on completed stages.

    Returns:
        Estimated seconds remaining, or None if unable to estimate.
    """
    if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
        return 0.0

    if not job.started_at:
        return None

    from datetime import datetime, timezone

    elapsed = (datetime.now(timezone.utc) - job.started_at).total_seconds()

    if job.overall_progress > 0:
        total_estimated = elapsed / (job.overall_progress / 100.0)
        remaining = total_estimated - elapsed
        return max(0.0, remaining)

    return None
