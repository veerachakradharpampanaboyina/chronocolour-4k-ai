"""
ChronoColor 4K AI — Video Service

Business logic for video upload, retrieval, and management.
"""

from __future__ import annotations

import math
import uuid
from typing import Optional

import structlog
from beanie import PydanticObjectId

from app.config import get_settings
from app.core.exceptions import VideoNotFoundError, VideoValidationError
from app.core.storage import (
    delete_file,
    generate_presigned_url,
    upload_file,
)
from app.models.video import Video, VideoStatus
from app.schemas.video import (
    VideoDetail,
    VideoListItem,
    VideoListResponse,
    VideoUploadResponse,
)

logger = structlog.get_logger(__name__)


ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/avi",
    "video/x-msvideo",
    "video/quicktime",
    "video/x-matroska",
    "video/webm",
    "video/mpeg",
    "video/x-flv",
    "application/octet-stream",  # Fallback for undetected types
}

ALLOWED_EXTENSIONS = {
    ".mp4", ".avi", ".mov", ".mkv", ".webm", ".mpeg", ".mpg", ".flv", ".wmv",
}


async def upload_video(
    file_content: bytes,
    filename: str,
    content_type: str,
) -> VideoUploadResponse:
    """
    Handle video file upload.

    Args:
        file_content: Raw file bytes.
        filename: Original filename.
        content_type: MIME type.

    Returns:
        VideoUploadResponse with video metadata.
    """
    settings = get_settings()

    # Validate file type
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise VideoValidationError(
            f"Unsupported file format: {ext}. "
            f"Supported: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Validate file size
    file_size = len(file_content)
    max_size = settings.max_video_size_mb * 1024 * 1024
    if file_size > max_size:
        raise VideoValidationError(
            f"File too large: {file_size / (1024*1024):.1f}MB. "
            f"Maximum: {settings.max_video_size_mb}MB"
        )

    # Generate unique storage key
    unique_id = uuid.uuid4().hex[:12]
    safe_filename = f"{unique_id}_{filename}"
    storage_key = f"uploads/{safe_filename}"

    # Create Video document
    video = Video(
        filename=safe_filename,
        original_filename=filename,
        content_type=content_type or "video/mp4",
        file_size_bytes=file_size,
        status=VideoStatus.UPLOADING,
    )
    await video.insert()

    # Upload to storage
    import io
    bucket = settings.storage_bucket_raw
    upload_file(io.BytesIO(file_content), bucket, storage_key, content_type)

    # Update document
    video.mark_uploaded(bucket, storage_key, file_size)
    await video.save()

    logger.info(
        "video_uploaded",
        video_id=str(video.id),
        filename=filename,
        size_mb=round(file_size / (1024 * 1024), 2),
    )

    return VideoUploadResponse(
        id=str(video.id),
        filename=video.filename,
        original_filename=video.original_filename,
        file_size_bytes=video.file_size_bytes,
        status=video.status,
        created_at=video.created_at,
    )


async def get_video(video_id: str) -> VideoDetail:
    """
    Get full video detail by ID.

    Args:
        video_id: Video document ID.

    Returns:
        VideoDetail with analysis results and download URL.
    """
    video = await Video.get(PydanticObjectId(video_id))
    if not video:
        raise VideoNotFoundError(video_id)

    # Generate download URL if video is uploaded
    download_url = None
    if video.storage_bucket and video.storage_key:
        download_url = generate_presigned_url(
            video.storage_bucket, video.storage_key, expires_in=3600
        )

    return VideoDetail.from_document(video, download_url=download_url)


async def list_videos(
    page: int = 1,
    page_size: int = 20,
    status: Optional[VideoStatus] = None,
) -> VideoListResponse:
    """
    List videos with pagination and optional status filter.

    Args:
        page: Page number (1-indexed).
        page_size: Items per page.
        status: Optional status filter.

    Returns:
        Paginated VideoListResponse.
    """
    # Build query
    query = {}
    if status:
        query["status"] = status.value

    # Count total
    total = await Video.find(query).count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    # Fetch page
    skip = (page - 1) * page_size
    videos = (
        await Video.find(query)
        .sort(-Video.created_at)
        .skip(skip)
        .limit(page_size)
        .to_list()
    )

    return VideoListResponse(
        videos=[VideoListItem.from_document(v) for v in videos],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


async def delete_video(video_id: str) -> None:
    """
    Delete a video and its storage files.

    Args:
        video_id: Video document ID.
    """
    video = await Video.get(PydanticObjectId(video_id))
    if not video:
        raise VideoNotFoundError(video_id)

    # Delete from storage
    if video.storage_bucket and video.storage_key:
        try:
            delete_file(video.storage_bucket, video.storage_key)
        except Exception as e:
            logger.warning(
                "storage_delete_failed",
                video_id=video_id,
                error=str(e),
            )

    # Delete document
    await video.delete()
    logger.info("video_deleted", video_id=video_id)
