"""
ChronoColor 4K AI — Video API Schemas

Pydantic v2 schemas for video upload, listing, and detail endpoints.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.video import VideoAnalysis, VideoStatus


class VideoUploadResponse(BaseModel):
    """Response after successful video upload."""

    id: str
    filename: str
    original_filename: str
    file_size_bytes: int
    status: VideoStatus
    created_at: datetime
    message: str = "Video uploaded successfully"


class VideoListItem(BaseModel):
    """Compact video representation for list endpoints."""

    id: str
    filename: str
    original_filename: str
    file_size_bytes: int
    status: VideoStatus
    created_at: datetime
    updated_at: datetime
    duration_seconds: Optional[float] = None
    resolution: Optional[str] = None
    is_grayscale: Optional[bool] = None

    @classmethod
    def from_document(cls, video) -> VideoListItem:
        """Create from a Video document."""
        duration = None
        resolution = None
        is_grayscale = None

        if video.analysis:
            duration = video.analysis.duration_seconds
            resolution = f"{video.analysis.resolution_width}x{video.analysis.resolution_height}"
            is_grayscale = video.analysis.is_grayscale

        return cls(
            id=str(video.id),
            filename=video.filename,
            original_filename=video.original_filename,
            file_size_bytes=video.file_size_bytes,
            status=video.status,
            created_at=video.created_at,
            updated_at=video.updated_at,
            duration_seconds=duration,
            resolution=resolution,
            is_grayscale=is_grayscale,
        )


class VideoDetail(BaseModel):
    """Full video detail with analysis results."""

    id: str
    filename: str
    original_filename: str
    content_type: str
    file_size_bytes: int
    status: VideoStatus
    analysis: Optional[VideoAnalysis] = None
    tags: list[str] = Field(default_factory=list)
    description: str = ""
    created_at: datetime
    updated_at: datetime
    download_url: Optional[str] = None

    @classmethod
    def from_document(cls, video, download_url: str | None = None) -> VideoDetail:
        """Create from a Video document."""
        return cls(
            id=str(video.id),
            filename=video.filename,
            original_filename=video.original_filename,
            content_type=video.content_type,
            file_size_bytes=video.file_size_bytes,
            status=video.status,
            analysis=video.analysis,
            tags=video.tags,
            description=video.description,
            created_at=video.created_at,
            updated_at=video.updated_at,
            download_url=download_url,
        )


class VideoListResponse(BaseModel):
    """Paginated video list response."""

    videos: list[VideoListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
