"""
ChronoColor 4K AI — Processing Job Document Model

MongoDB document model for AI processing jobs.
Tracks pipeline configuration, per-stage progress, and results.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from beanie import Document, Indexed, Link
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job processing lifecycle states."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineStage(str, Enum):
    """All available pipeline stages in processing order."""

    ANALYZE = "analyze"
    RESTORE = "restore"
    SUPER_RESOLUTION = "super_resolution"
    FACE_RESTORATION = "face_restoration"
    SCENE_UNDERSTANDING = "scene_understanding"
    OBJECT_DETECTION = "object_detection"
    OBJECT_TRACKING = "object_tracking"
    SEGMENTATION = "segmentation"
    COLORIZATION = "colorization"
    TEMPORAL_MEMORY = "temporal_memory"
    OPTICAL_FLOW = "optical_flow"
    FLICKER_CORRECTION = "flicker_correction"
    HDR_ENHANCEMENT = "hdr_enhancement"
    QUALITY_ASSESSMENT = "quality_assessment"
    RECONSTRUCTION = "reconstruction"
    AUDIO_SYNC = "audio_sync"


class StageStatus(str, Enum):
    """Status of an individual pipeline stage."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StageProgress(BaseModel):
    """Progress tracking for a single pipeline stage."""

    stage: PipelineStage
    status: StageStatus = StageStatus.PENDING
    progress_percent: float = 0.0
    message: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    error: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PipelineConfig(BaseModel):
    """User-configurable pipeline settings."""

    # Quality preset
    quality_preset: str = "balanced"  # fast, balanced, maximum

    # Toggle pipeline stages (all enabled by default)
    enable_restoration: bool = True
    enable_super_resolution: bool = True
    enable_face_restoration: bool = True
    enable_scene_understanding: bool = True
    enable_object_detection: bool = True
    enable_object_tracking: bool = True
    enable_segmentation: bool = True
    enable_colorization: bool = True
    enable_temporal_memory: bool = True
    enable_optical_flow: bool = True
    enable_flicker_correction: bool = True
    enable_hdr_enhancement: bool = True
    enable_quality_assessment: bool = True

    # Model overrides (None = use defaults from settings)
    restoration_model: Optional[str] = None
    superres_model: Optional[str] = None
    face_model: Optional[str] = None
    colorization_model: Optional[str] = None

    # Output settings
    target_resolution: str = "4k"  # 720p, 1080p, 2k, 4k
    output_format: str = "mp4"  # mp4, mov, webm
    output_codec: str = "libx265"  # libx265, libx264, prores
    output_fps: Optional[float] = None  # None = keep original FPS
    enable_hdr_output: bool = True


class JobResult(BaseModel):
    """Final job results and output references."""

    output_storage_bucket: str = ""
    output_storage_key: str = ""
    output_file_size_bytes: int = 0
    output_resolution_width: int = 0
    output_resolution_height: int = 0
    output_duration_seconds: float = 0.0
    output_fps: float = 0.0
    output_codec: str = ""

    # Quality metrics
    avg_ssim: float = 0.0
    avg_psnr: float = 0.0
    avg_niqe: float = 0.0
    temporal_consistency_score: float = 0.0

    # Processing statistics
    total_frames_processed: int = 0
    total_processing_time_seconds: float = 0.0
    gpu_hours_used: float = 0.0


class Job(Document):
    """MongoDB document for a processing job."""

    # Reference to source video
    video_id: str
    video_filename: str = ""

    # Configuration
    pipeline_config: PipelineConfig = Field(default_factory=PipelineConfig)

    # Status
    status: JobStatus = JobStatus.PENDING
    overall_progress: float = 0.0
    current_stage: Optional[PipelineStage] = None

    # Per-stage progress
    stages: list[StageProgress] = Field(default_factory=list)

    # Celery task tracking
    celery_task_id: Optional[str] = None

    # Results (populated after completion)
    result: Optional[JobResult] = None

    # Error information
    error_message: Optional[str] = None
    error_stage: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "jobs"
        indexes = [
            "video_id",
            "status",
            "created_at",
        ]

    def initialize_stages(self) -> None:
        """Create stage progress entries based on pipeline config."""
        config = self.pipeline_config
        stage_map = [
            (PipelineStage.ANALYZE, True),  # Always run
            (PipelineStage.RESTORE, config.enable_restoration),
            (PipelineStage.SUPER_RESOLUTION, config.enable_super_resolution),
            (PipelineStage.FACE_RESTORATION, config.enable_face_restoration),
            (PipelineStage.SCENE_UNDERSTANDING, config.enable_scene_understanding),
            (PipelineStage.OBJECT_DETECTION, config.enable_object_detection),
            (PipelineStage.OBJECT_TRACKING, config.enable_object_tracking),
            (PipelineStage.SEGMENTATION, config.enable_segmentation),
            (PipelineStage.COLORIZATION, config.enable_colorization),
            (PipelineStage.TEMPORAL_MEMORY, config.enable_temporal_memory),
            (PipelineStage.OPTICAL_FLOW, config.enable_optical_flow),
            (PipelineStage.FLICKER_CORRECTION, config.enable_flicker_correction),
            (PipelineStage.HDR_ENHANCEMENT, config.enable_hdr_enhancement),
            (PipelineStage.QUALITY_ASSESSMENT, config.enable_quality_assessment),
            (PipelineStage.RECONSTRUCTION, True),  # Always run
            (PipelineStage.AUDIO_SYNC, True),  # Always run
        ]

        self.stages = []
        for stage, enabled in stage_map:
            if enabled:
                self.stages.append(StageProgress(stage=stage))
            else:
                self.stages.append(
                    StageProgress(stage=stage, status=StageStatus.SKIPPED)
                )

    def get_active_stages(self) -> list[PipelineStage]:
        """Get list of non-skipped stages."""
        return [s.stage for s in self.stages if s.status != StageStatus.SKIPPED]

    def update_stage(
        self,
        stage: PipelineStage,
        status: StageStatus,
        progress: float = 0.0,
        message: str = "",
        error: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        """Update progress for a specific stage."""
        for s in self.stages:
            if s.stage == stage:
                s.status = status
                s.progress_percent = progress
                s.message = message
                if error:
                    s.error = error
                if metadata:
                    s.metadata = metadata
                if status == StageStatus.RUNNING and s.started_at is None:
                    s.started_at = datetime.now(timezone.utc)
                if status in (StageStatus.COMPLETED, StageStatus.FAILED):
                    s.completed_at = datetime.now(timezone.utc)
                    if s.started_at:
                        st = s.started_at.replace(tzinfo=timezone.utc) if s.started_at.tzinfo is None else s.started_at
                        s.duration_seconds = (
                            s.completed_at - st
                        ).total_seconds()
                break

        # Update overall progress
        active_stages = [s for s in self.stages if s.status != StageStatus.SKIPPED]
        if active_stages:
            self.overall_progress = sum(
                s.progress_percent for s in active_stages
            ) / len(active_stages)

        self.current_stage = stage
        self.updated_at = datetime.now(timezone.utc)

    def mark_started(self, celery_task_id: str) -> None:
        """Mark job as started."""
        self.status = JobStatus.RUNNING
        self.celery_task_id = celery_task_id
        self.started_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def mark_completed(self, result: JobResult) -> None:
        """Mark job as completed with results."""
        self.status = JobStatus.COMPLETED
        self.overall_progress = 100.0
        self.result = result
        self.completed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def mark_failed(self, error: str, stage: str | None = None) -> None:
        """Mark job as failed."""
        self.status = JobStatus.FAILED
        self.error_message = error
        self.error_stage = stage
        self.completed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def mark_cancelled(self) -> None:
        """Mark job as cancelled."""
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
