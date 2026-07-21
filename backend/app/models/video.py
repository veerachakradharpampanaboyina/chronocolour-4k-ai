"""
ChronoColor 4K AI — Video Document Model

MongoDB document model for uploaded video files.
Stores metadata, analysis results, and storage references.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from beanie import Document, Indexed
from pydantic import BaseModel, Field


class VideoStatus(str, Enum):
    """Video processing lifecycle states."""

    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"


class VideoAnalysis(BaseModel):
    """Results from the video analyzer module."""

    resolution_width: int = 0
    resolution_height: int = 0
    fps: float = 0.0
    total_frames: int = 0
    duration_seconds: float = 0.0
    codec: str = ""
    bitrate_kbps: int = 0
    file_size_bytes: int = 0

    # Quality metrics (0.0 - 1.0, higher = worse)
    noise_level: float = 0.0
    blur_level: float = 0.0
    damage_level: float = 0.0
    compression_artifact_level: float = 0.0

    # Scene information
    scene_change_count: int = 0
    scene_change_timestamps: list[float] = Field(default_factory=list)

    # Color information
    is_grayscale: bool = True
    has_audio: bool = False
    audio_codec: str = ""
    audio_sample_rate: int = 0


class Video(Document):
    """MongoDB document for a video file."""

    # Core fields
    filename: str
    original_filename: str
    content_type: str = "video/mp4"
    file_size_bytes: int = 0

    # Status
    status: VideoStatus = VideoStatus.UPLOADING

    # Storage references
    storage_bucket: str = ""
    storage_key: str = ""

    # Analysis results (populated after analysis stage)
    analysis: Optional[VideoAnalysis] = None

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Tags and metadata
    tags: list[str] = Field(default_factory=list)
    description: str = ""

    class Settings:
        name = "videos"
        indexes = [
            "status",
            "created_at",
        ]

    def mark_uploaded(self, bucket: str, key: str, size: int) -> None:
        """Mark video as successfully uploaded."""
        self.status = VideoStatus.UPLOADED
        self.storage_bucket = bucket
        self.storage_key = key
        self.file_size_bytes = size
        self.updated_at = datetime.now(timezone.utc)

    def mark_analyzed(self, analysis: VideoAnalysis) -> None:
        """Mark video as analyzed with results."""
        self.status = VideoStatus.ANALYZED
        self.analysis = analysis
        self.updated_at = datetime.now(timezone.utc)

    def mark_failed(self) -> None:
        """Mark video as failed."""
        self.status = VideoStatus.FAILED
        self.updated_at = datetime.now(timezone.utc)
