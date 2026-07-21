"""
ChronoColor 4K AI — Job API Schemas

Pydantic v2 schemas for job creation, listing, progress tracking, and results.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models.job import (
    JobResult,
    JobStatus,
    PipelineConfig,
    PipelineStage,
    StageProgress,
    StageStatus,
)


class JobCreateRequest(BaseModel):
    """Request to create a new processing job."""

    video_id: str
    pipeline_config: PipelineConfig = Field(default_factory=PipelineConfig)


class JobCreateResponse(BaseModel):
    """Response after creating a processing job."""

    id: str
    video_id: str
    status: JobStatus
    pipeline_config: PipelineConfig
    total_stages: int
    active_stages: int
    created_at: datetime
    message: str = "Processing job created and queued"


class StageProgressResponse(BaseModel):
    """Progress data for a single pipeline stage."""

    stage: PipelineStage
    stage_display_name: str
    status: StageStatus
    progress_percent: float
    message: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    error: Optional[str] = None

    @classmethod
    def from_model(cls, stage_progress: StageProgress) -> StageProgressResponse:
        """Create from a StageProgress model."""
        display_names = {
            PipelineStage.ANALYZE: "Video Analysis",
            PipelineStage.RESTORE: "Frame Restoration",
            PipelineStage.SUPER_RESOLUTION: "4K Super Resolution",
            PipelineStage.FACE_RESTORATION: "Face Restoration",
            PipelineStage.SCENE_UNDERSTANDING: "Scene Understanding",
            PipelineStage.OBJECT_DETECTION: "Object Detection",
            PipelineStage.OBJECT_TRACKING: "Object Tracking",
            PipelineStage.SEGMENTATION: "Semantic Segmentation",
            PipelineStage.COLORIZATION: "AI Colorization",
            PipelineStage.TEMPORAL_MEMORY: "Temporal Color Memory",
            PipelineStage.OPTICAL_FLOW: "Optical Flow Propagation",
            PipelineStage.FLICKER_CORRECTION: "Flicker Correction",
            PipelineStage.HDR_ENHANCEMENT: "HDR Enhancement",
            PipelineStage.QUALITY_ASSESSMENT: "Quality Assessment",
            PipelineStage.RECONSTRUCTION: "Video Reconstruction",
            PipelineStage.AUDIO_SYNC: "Audio Synchronization",
        }

        return cls(
            stage=stage_progress.stage,
            stage_display_name=display_names.get(
                stage_progress.stage, stage_progress.stage.value
            ),
            status=stage_progress.status,
            progress_percent=stage_progress.progress_percent,
            message=stage_progress.message,
            started_at=stage_progress.started_at,
            completed_at=stage_progress.completed_at,
            duration_seconds=stage_progress.duration_seconds,
            error=stage_progress.error,
        )


class JobDetailResponse(BaseModel):
    """Full job detail with per-stage progress."""

    id: str
    video_id: str
    video_filename: str
    status: JobStatus
    overall_progress: float
    current_stage: Optional[str] = None
    current_stage_display_name: Optional[str] = None
    pipeline_config: PipelineConfig
    stages: list[StageProgressResponse]
    result: Optional[JobResult] = None
    error_message: Optional[str] = None
    error_stage: Optional[str] = None
    celery_task_id: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_time_remaining_seconds: Optional[float] = None
    download_url: Optional[str] = None

    @classmethod
    def from_document(
        cls,
        job,
        download_url: str | None = None,
        estimated_time: float | None = None,
    ) -> JobDetailResponse:
        """Create from a Job document."""
        display_names = {
            PipelineStage.ANALYZE: "Video Analysis",
            PipelineStage.RESTORE: "Frame Restoration",
            PipelineStage.SUPER_RESOLUTION: "4K Super Resolution",
            PipelineStage.FACE_RESTORATION: "Face Restoration",
            PipelineStage.SCENE_UNDERSTANDING: "Scene Understanding",
            PipelineStage.OBJECT_DETECTION: "Object Detection",
            PipelineStage.OBJECT_TRACKING: "Object Tracking",
            PipelineStage.SEGMENTATION: "Semantic Segmentation",
            PipelineStage.COLORIZATION: "AI Colorization",
            PipelineStage.TEMPORAL_MEMORY: "Temporal Color Memory",
            PipelineStage.OPTICAL_FLOW: "Optical Flow Propagation",
            PipelineStage.FLICKER_CORRECTION: "Flicker Correction",
            PipelineStage.HDR_ENHANCEMENT: "HDR Enhancement",
            PipelineStage.QUALITY_ASSESSMENT: "Quality Assessment",
            PipelineStage.RECONSTRUCTION: "Video Reconstruction",
            PipelineStage.AUDIO_SYNC: "Audio Synchronization",
        }

        current_display = None
        if job.current_stage:
            current_display = display_names.get(
                job.current_stage, job.current_stage.value
            )

        return cls(
            id=str(job.id),
            video_id=job.video_id,
            video_filename=job.video_filename,
            status=job.status,
            overall_progress=job.overall_progress,
            current_stage=job.current_stage.value if job.current_stage else None,
            current_stage_display_name=current_display,
            pipeline_config=job.pipeline_config,
            stages=[StageProgressResponse.from_model(s) for s in job.stages],
            result=job.result,
            error_message=job.error_message,
            error_stage=job.error_stage,
            celery_task_id=job.celery_task_id,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            estimated_time_remaining_seconds=estimated_time,
            download_url=download_url,
        )


class JobListItem(BaseModel):
    """Compact job representation for list endpoints."""

    id: str
    video_id: str
    video_filename: str
    status: JobStatus
    overall_progress: float
    current_stage: Optional[str] = None
    current_stage_display_name: Optional[str] = None
    quality_preset: str
    target_resolution: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @classmethod
    def from_document(cls, job) -> JobListItem:
        """Create from a Job document."""
        display_names = {
            PipelineStage.ANALYZE: "Video Analysis",
            PipelineStage.RESTORE: "Frame Restoration",
            PipelineStage.SUPER_RESOLUTION: "4K Super Resolution",
            PipelineStage.FACE_RESTORATION: "Face Restoration",
            PipelineStage.SCENE_UNDERSTANDING: "Scene Understanding",
            PipelineStage.OBJECT_DETECTION: "Object Detection",
            PipelineStage.OBJECT_TRACKING: "Object Tracking",
            PipelineStage.SEGMENTATION: "Semantic Segmentation",
            PipelineStage.COLORIZATION: "AI Colorization",
            PipelineStage.TEMPORAL_MEMORY: "Temporal Color Memory",
            PipelineStage.OPTICAL_FLOW: "Optical Flow Propagation",
            PipelineStage.FLICKER_CORRECTION: "Flicker Correction",
            PipelineStage.HDR_ENHANCEMENT: "HDR Enhancement",
            PipelineStage.QUALITY_ASSESSMENT: "Quality Assessment",
            PipelineStage.RECONSTRUCTION: "Video Reconstruction",
            PipelineStage.AUDIO_SYNC: "Audio Synchronization",
        }

        current_display = None
        if job.current_stage:
            current_display = display_names.get(
                job.current_stage, job.current_stage.value
            )

        return cls(
            id=str(job.id),
            video_id=job.video_id,
            video_filename=job.video_filename,
            status=job.status,
            overall_progress=job.overall_progress,
            current_stage=job.current_stage.value if job.current_stage else None,
            current_stage_display_name=current_display,
            quality_preset=job.pipeline_config.quality_preset,
            target_resolution=job.pipeline_config.target_resolution,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
        )


class JobListResponse(BaseModel):
    """Paginated job list response."""

    jobs: list[JobListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class JobCancelResponse(BaseModel):
    """Response after cancelling a job."""

    id: str
    status: JobStatus
    message: str = "Job cancelled successfully"
