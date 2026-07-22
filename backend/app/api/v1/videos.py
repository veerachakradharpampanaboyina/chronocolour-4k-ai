"""
ChronoColor 4K AI — Video API Endpoints

Handles video upload, listing, detail retrieval, and deletion.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, File, Query, Response, UploadFile

from app.models.video import VideoStatus
from app.schemas.video import VideoDetail, VideoListResponse, VideoUploadResponse
from app.services import video_service

router = APIRouter()


@router.post(
    "/upload",
    response_model=VideoUploadResponse,
    status_code=201,
    summary="Upload a video file",
)
async def upload_video(
    file: UploadFile = File(..., description="Video file to upload"),
) -> VideoUploadResponse:
    """
    Upload a black & white video for processing.

    Supports: MP4, AVI, MOV, MKV, WebM, MPEG, FLV
    Maximum size: 5GB (configurable)
    """
    content = await file.read()
    return await video_service.upload_video(
        file_content=content,
        filename=file.filename or "unnamed.mp4",
        content_type=file.content_type or "video/mp4",
    )


@router.get(
    "",
    response_model=VideoListResponse,
    summary="List uploaded videos",
)
async def list_videos(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[VideoStatus] = Query(None, description="Filter by status"),
) -> VideoListResponse:
    """List all uploaded videos with pagination and optional status filter."""
    return await video_service.list_videos(
        page=page, page_size=page_size, status=status
    )


@router.get(
    "/{video_id}",
    response_model=VideoDetail,
    summary="Get video details",
)
async def get_video(video_id: str) -> VideoDetail:
    """Get full details for a specific video, including analysis results."""
    return await video_service.get_video(video_id)


@router.delete(
    "/{video_id}",
    status_code=204,
    response_class=Response,
    response_model=None,
    summary="Delete a video",
)
async def delete_video(video_id: str) -> Response:
    """Delete a video and its associated storage files."""
    await video_service.delete_video(video_id)
    return Response(status_code=204)
