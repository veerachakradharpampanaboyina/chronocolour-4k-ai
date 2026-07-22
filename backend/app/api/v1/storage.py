r"""
ChronoColor 4K AI — Local Storage Delivery Endpoint

Serves uploaded videos and processed result files directly from the local storage
directory (e.g. D:\chronocolor_storage) via HTTP.
"""

from __future__ import annotations

import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from app.config import get_settings

router = APIRouter()


@router.get(
    "/{bucket}/{key:path}",
    summary="Get or stream a stored file from local storage",
)
async def get_storage_file(bucket: str, key: str) -> FileResponse:
    """
    Serve a file from local storage bucket directory.

    Args:
        bucket: Storage bucket name (e.g., 'raw-videos', 'results', 'processed-frames')
        key: File key or relative path within the bucket

    Returns:
        FileResponse serving the local file with streaming support.
    """
    settings = get_settings()
    base_dir = Path(getattr(settings, "local_storage_dir", "D:\\chronocolor_storage"))
    
    # Fallback to default local storage if configured directory does not exist
    if not base_dir.exists():
        fallback_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))) / "local_storage"
        if fallback_dir.exists():
            base_dir = fallback_dir

    file_path = (base_dir / bucket / key).resolve()

    # Prevent directory traversal attacks
    try:
        bucket_dir = (base_dir / bucket).resolve()
        if not str(file_path).startswith(str(bucket_dir)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to requested path.",
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file path.",
        )

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{key}' not found in bucket '{bucket}'.",
        )

    # Determine filename and MIME content type
    filename = file_path.name
    ext = file_path.suffix.lower()

    media_types = {
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".avi": "video/x-msvideo",
        ".mov": "video/quicktime",
        ".mkv": "video/x-matroska",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".json": "application/json",
    }
    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename,
    )
