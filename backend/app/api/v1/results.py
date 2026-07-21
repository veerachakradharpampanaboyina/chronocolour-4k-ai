"""
ChronoColor 4K AI — Results API Endpoints

Handles result downloads and frame previews.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.core.exceptions import JobNotFoundError
from app.core.storage import generate_presigned_url
from app.models.job import Job, JobStatus
from beanie import PydanticObjectId

router = APIRouter()


@router.get(
    "/{job_id}/download",
    summary="Download processed video",
)
async def download_result(job_id: str) -> RedirectResponse:
    """
    Get a download URL for the processed video.

    Redirects to a presigned S3/MinIO URL valid for 1 hour.
    Only available for completed jobs.
    """
    job = await Job.get(PydanticObjectId(job_id))
    if not job:
        raise JobNotFoundError(job_id)

    if job.status != JobStatus.COMPLETED or not job.result:
        raise JobNotFoundError(job_id)

    download_url = generate_presigned_url(
        bucket=job.result.output_storage_bucket,
        key=job.result.output_storage_key,
        expires_in=3600,
    )

    return RedirectResponse(url=download_url)


@router.get(
    "/{job_id}/preview/{frame_number}",
    summary="Preview a processed frame",
)
async def preview_frame(job_id: str, frame_number: int) -> RedirectResponse:
    """
    Get a preview of a specific processed frame.

    Useful for inspecting colorization quality before downloading
    the full video.
    """
    job = await Job.get(PydanticObjectId(job_id))
    if not job:
        raise JobNotFoundError(job_id)

    from app.config import get_settings

    settings = get_settings()

    # Frame previews are stored in the frames bucket
    frame_key = f"jobs/{job_id}/preview/frame_{frame_number:06d}.jpg"
    preview_url = generate_presigned_url(
        bucket=settings.storage_bucket_frames,
        key=frame_key,
        expires_in=600,
    )

    return RedirectResponse(url=preview_url)
