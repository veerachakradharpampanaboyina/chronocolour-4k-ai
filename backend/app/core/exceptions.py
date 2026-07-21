"""
ChronoColor 4K AI — Custom Exception Classes

Structured exceptions for API error handling with HTTP status codes.
"""

from __future__ import annotations

from fastapi import HTTPException, status


class ChronoColorError(Exception):
    """Base exception for all ChronoColor errors."""

    def __init__(self, message: str, detail: str | None = None):
        self.message = message
        self.detail = detail
        super().__init__(self.message)


# --- Resource Errors ---


class VideoNotFoundError(HTTPException):
    """Raised when a video resource is not found."""

    def __init__(self, video_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video not found: {video_id}",
        )


class JobNotFoundError(HTTPException):
    """Raised when a processing job is not found."""

    def __init__(self, job_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Processing job not found: {job_id}",
        )


# --- Validation Errors ---


class VideoValidationError(HTTPException):
    """Raised when video validation fails (format, size, duration)."""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Video validation failed: {detail}",
        )


class PipelineConfigError(HTTPException):
    """Raised when pipeline configuration is invalid."""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid pipeline configuration: {detail}",
        )


# --- Processing Errors ---


class PipelineError(ChronoColorError):
    """Raised when the AI processing pipeline fails."""

    def __init__(self, stage: str, message: str, detail: str | None = None):
        self.stage = stage
        super().__init__(
            message=f"Pipeline failed at stage '{stage}': {message}",
            detail=detail,
        )


class ModelLoadError(ChronoColorError):
    """Raised when an AI model fails to load."""

    def __init__(self, model_name: str, reason: str):
        self.model_name = model_name
        super().__init__(
            message=f"Failed to load model '{model_name}': {reason}",
        )


class GPUMemoryError(ChronoColorError):
    """Raised when GPU memory is insufficient for model inference."""

    def __init__(self, required_mb: int, available_mb: int):
        self.required_mb = required_mb
        self.available_mb = available_mb
        super().__init__(
            message=(
                f"Insufficient GPU memory: {required_mb}MB required, "
                f"{available_mb}MB available"
            ),
        )


# --- Storage Errors ---


class StorageError(ChronoColorError):
    """Raised when S3/MinIO operations fail."""

    def __init__(self, operation: str, message: str):
        self.operation = operation
        super().__init__(
            message=f"Storage {operation} failed: {message}",
        )


# --- Job State Errors ---


class JobAlreadyRunningError(HTTPException):
    """Raised when attempting to start a job that's already processing."""

    def __init__(self, job_id: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job is already running: {job_id}",
        )


class JobCancellationError(HTTPException):
    """Raised when a job cannot be cancelled (already completed/failed)."""

    def __init__(self, job_id: str, current_status: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot cancel job {job_id} in status: {current_status}",
        )
