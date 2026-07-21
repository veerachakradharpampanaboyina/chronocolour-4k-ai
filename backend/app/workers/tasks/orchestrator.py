"""
ChronoColor 4K AI — Pipeline Orchestrator Task

Master Celery task that orchestrates the entire AI processing pipeline.
Chains all enabled stages, handles errors, and reports progress.
"""

from __future__ import annotations

import asyncio
import time
import traceback
from datetime import datetime, timezone
from typing import Any

import structlog
from celery import shared_task

from app.workers.celery_app import celery_app

logger = structlog.get_logger(__name__)


def _run_async(coro):
    """Run an async function from a synchronous Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _init_db():
    """Initialize database connection for worker context."""
    from app.config import get_settings
    from app.core.database import init_database

    settings = get_settings()
    await init_database(settings)


async def _get_job(job_id: str):
    """Fetch a job from the database."""
    from beanie import PydanticObjectId
    from app.models.job import Job

    return await Job.get(PydanticObjectId(job_id))


async def _publish_progress(job_id: str, stage: str, status: str,
                             progress: float, message: str):
    """Publish progress update via Redis Pub/Sub."""
    try:
        from app.config import get_settings
        from app.core.redis import init_redis, publish_progress

        settings = get_settings()
        await init_redis(settings)

        await publish_progress(job_id, {
            "type": "progress",
            "job_id": job_id,
            "stage": stage,
            "status": status,
            "progress": round(progress, 1),
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    except Exception as e:
        logger.warning("publish_progress_failed", error=str(e))


@celery_app.task(
    name="app.workers.tasks.orchestrator.run_pipeline",
    bind=True,
    max_retries=0,
    acks_late=True,
)
def run_pipeline(self, job_id: str) -> dict[str, Any]:
    """
    Master pipeline orchestrator task.

    Executes all enabled pipeline stages in sequence:
    1. Analyze → 2. Restore → 3. SuperRes → 4. Face Restore →
    5. Scene Detect → 6. Object Detect → 7. Object Track →
    8. Segment → 9. Colorize → 10. Temporal Memory →
    11. Optical Flow → 12. Flicker Correct → 13. HDR Enhance →
    14. Quality Assess → 15. Reconstruct → 16. Audio Sync

    Args:
        job_id: The processing job ID.

    Returns:
        Dict with final status and result metadata.
    """
    logger.info("pipeline_started", job_id=job_id, task_id=self.request.id)
    start_time = time.time()

    try:
        # Initialize database in worker context
        _run_async(_init_db())

        # Load job
        job = _run_async(_get_job(job_id))
        if not job:
            raise ValueError(f"Job not found: {job_id}")

        # Mark as running
        from app.models.job import JobStatus, StageStatus, PipelineStage

        job.mark_started(self.request.id)
        _run_async(job.save())

        # Build the execution plan from enabled stages
        stage_handlers = _get_stage_handlers()
        active_stages = job.get_active_stages()

        logger.info(
            "pipeline_executing",
            job_id=job_id,
            active_stages=[s.value for s in active_stages],
            total_stages=len(active_stages),
        )

        # Working directory for intermediate files
        import tempfile
        import os

        work_dir = tempfile.mkdtemp(prefix=f"chronocolor_{job_id[:8]}_")
        context = {
            "job_id": job_id,
            "video_id": job.video_id,
            "work_dir": work_dir,
            "pipeline_config": job.pipeline_config.model_dump(),
            "frames_dir": os.path.join(work_dir, "frames"),
            "restored_dir": os.path.join(work_dir, "restored"),
            "upscaled_dir": os.path.join(work_dir, "upscaled"),
            "colorized_dir": os.path.join(work_dir, "colorized"),
            "final_dir": os.path.join(work_dir, "final"),
            "analysis": {},
            "detections": {},
            "tracks": {},
            "segments": {},
            "scene_info": {},
            "color_memory": {},
            "flow_fields": {},
        }

        # Create working directories
        for dir_key in ["frames_dir", "restored_dir", "upscaled_dir",
                        "colorized_dir", "final_dir"]:
            os.makedirs(context[dir_key], exist_ok=True)

        # Execute each stage
        for stage in active_stages:
            handler = stage_handlers.get(stage)
            if not handler:
                logger.warning("no_handler_for_stage", stage=stage.value)
                continue

            logger.info("stage_starting", job_id=job_id, stage=stage.value)

            # Update stage status
            job.update_stage(stage, StageStatus.RUNNING, message="Processing...")
            _run_async(job.save())
            _run_async(_publish_progress(
                job_id, stage.value, "running", job.overall_progress,
                f"Starting {stage.value}..."
            ))

            try:
                # Execute the stage handler
                context = handler(context)

                # Mark stage as completed
                job.update_stage(
                    stage, StageStatus.COMPLETED,
                    progress=100.0,
                    message="Completed"
                )
                _run_async(job.save())
                _run_async(_publish_progress(
                    job_id, stage.value, "completed", job.overall_progress,
                    f"{stage.value} completed"
                ))

                logger.info("stage_completed", job_id=job_id, stage=stage.value)

            except Exception as stage_error:
                error_msg = str(stage_error)
                logger.error(
                    "stage_failed",
                    job_id=job_id,
                    stage=stage.value,
                    error=error_msg,
                    traceback=traceback.format_exc(),
                )

                # Mark stage as failed
                job.update_stage(
                    stage, StageStatus.FAILED,
                    error=error_msg,
                    message=f"Failed: {error_msg[:200]}"
                )

                # For critical stages, fail the entire pipeline
                critical_stages = {
                    PipelineStage.ANALYZE,
                    PipelineStage.COLORIZATION,
                    PipelineStage.RECONSTRUCTION,
                }

                if stage in critical_stages:
                    job.mark_failed(error_msg, stage.value)
                    _run_async(job.save())
                    _run_async(_publish_progress(
                        job_id, stage.value, "failed", job.overall_progress,
                        f"Pipeline failed at {stage.value}: {error_msg[:200]}"
                    ))
                    raise

                # For non-critical stages, log and continue
                logger.warning(
                    "stage_failed_non_critical",
                    job_id=job_id,
                    stage=stage.value,
                    error=error_msg,
                )
                _run_async(job.save())

        # Pipeline completed successfully
        elapsed = time.time() - start_time

        from app.models.job import JobResult

        result = JobResult(
            total_frames_processed=context.get("total_frames", 0),
            total_processing_time_seconds=elapsed,
            output_storage_bucket=context.get("output_bucket", ""),
            output_storage_key=context.get("output_key", ""),
            output_file_size_bytes=context.get("output_size", 0),
            output_resolution_width=context.get("output_width", 0),
            output_resolution_height=context.get("output_height", 0),
            output_fps=context.get("output_fps", 0.0),
        )

        job.mark_completed(result)
        _run_async(job.save())
        _run_async(_publish_progress(
            job_id, "complete", "completed", 100.0,
            f"Processing complete in {elapsed/60:.1f} minutes"
        ))

        logger.info(
            "pipeline_completed",
            job_id=job_id,
            elapsed_minutes=round(elapsed / 60, 1),
            total_frames=context.get("total_frames", 0),
        )

        # Cleanup working directory
        import shutil
        try:
            shutil.rmtree(work_dir, ignore_errors=True)
        except Exception:
            pass

        return {
            "status": "completed",
            "job_id": job_id,
            "elapsed_seconds": elapsed,
        }

    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = str(e)

        logger.error(
            "pipeline_failed",
            job_id=job_id,
            error=error_msg,
            elapsed_minutes=round(elapsed / 60, 1),
            traceback=traceback.format_exc(),
        )

        # Update job status
        try:
            job = _run_async(_get_job(job_id))
            if job and job.status != JobStatus.FAILED:
                job.mark_failed(error_msg)
                _run_async(job.save())
        except Exception:
            pass

        return {
            "status": "failed",
            "job_id": job_id,
            "error": error_msg,
            "elapsed_seconds": elapsed,
        }


def _get_stage_handlers() -> dict:
    """
    Get the handler function for each pipeline stage.

    Each handler takes a context dict and returns the updated context.
    Handlers are lazy-imported to avoid loading all AI modules upfront.
    """
    from app.models.job import PipelineStage

    def analyze_handler(ctx):
        from app.workers.tasks.analyze import run_analysis
        return run_analysis(ctx)

    def restore_handler(ctx):
        from app.workers.tasks.restore import run_restoration
        return run_restoration(ctx)

    def superres_handler(ctx):
        from app.workers.tasks.superres import run_super_resolution
        return run_super_resolution(ctx)

    def face_restore_handler(ctx):
        from app.workers.tasks.face_restore import run_face_restoration
        return run_face_restoration(ctx)

    def scene_detect_handler(ctx):
        from app.workers.tasks.scene_detect import run_scene_detection
        return run_scene_detection(ctx)

    def object_detect_handler(ctx):
        from app.workers.tasks.object_detect import run_object_detection
        return run_object_detection(ctx)

    def object_track_handler(ctx):
        from app.workers.tasks.object_track import run_object_tracking
        return run_object_tracking(ctx)

    def segment_handler(ctx):
        from app.workers.tasks.segment import run_segmentation
        return run_segmentation(ctx)

    def colorize_handler(ctx):
        from app.workers.tasks.colorize import run_colorization
        return run_colorization(ctx)

    def temporal_memory_handler(ctx):
        from app.workers.tasks.temporal_memory import run_temporal_memory
        return run_temporal_memory(ctx)

    def optical_flow_handler(ctx):
        from app.workers.tasks.optical_flow import run_optical_flow
        return run_optical_flow(ctx)

    def flicker_correct_handler(ctx):
        from app.workers.tasks.flicker_correct import run_flicker_correction
        return run_flicker_correction(ctx)

    def hdr_enhance_handler(ctx):
        from app.workers.tasks.hdr_enhance import run_hdr_enhancement
        return run_hdr_enhancement(ctx)

    def quality_assess_handler(ctx):
        from app.workers.tasks.quality_assess import run_quality_assessment
        return run_quality_assessment(ctx)

    def reconstruct_handler(ctx):
        from app.workers.tasks.reconstruct import run_reconstruction
        return run_reconstruction(ctx)

    def audio_sync_handler(ctx):
        from app.workers.tasks.audio_sync import run_audio_sync
        return run_audio_sync(ctx)

    return {
        PipelineStage.ANALYZE: analyze_handler,
        PipelineStage.RESTORE: restore_handler,
        PipelineStage.SUPER_RESOLUTION: superres_handler,
        PipelineStage.FACE_RESTORATION: face_restore_handler,
        PipelineStage.SCENE_UNDERSTANDING: scene_detect_handler,
        PipelineStage.OBJECT_DETECTION: object_detect_handler,
        PipelineStage.OBJECT_TRACKING: object_track_handler,
        PipelineStage.SEGMENTATION: segment_handler,
        PipelineStage.COLORIZATION: colorize_handler,
        PipelineStage.TEMPORAL_MEMORY: temporal_memory_handler,
        PipelineStage.OPTICAL_FLOW: optical_flow_handler,
        PipelineStage.FLICKER_CORRECTION: flicker_correct_handler,
        PipelineStage.HDR_ENHANCEMENT: hdr_enhance_handler,
        PipelineStage.QUALITY_ASSESSMENT: quality_assess_handler,
        PipelineStage.RECONSTRUCTION: reconstruct_handler,
        PipelineStage.AUDIO_SYNC: audio_sync_handler,
    }
