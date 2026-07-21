"""ChronoColor 4K AI — Audio Synchronization Task"""
from __future__ import annotations
import os
import subprocess
from typing import Any
import structlog

logger = structlog.get_logger(__name__)


def run_audio_sync(context: dict[str, Any]) -> dict[str, Any]:
    """Mux original audio with the reconstructed color video."""
    has_audio = context.get("has_audio", False)
    reconstructed_path = context.get("reconstructed_video_path")
    input_video_path = context.get("input_video_path")
    work_dir = context["work_dir"]
    job_id = context["job_id"]

    if not reconstructed_path or not os.path.exists(reconstructed_path):
        raise ValueError("No reconstructed video found")

    final_output_path = os.path.join(work_dir, "final_output.mp4")

    if has_audio and input_video_path and os.path.exists(input_video_path):
        # Mux audio from original video into new video
        cmd = [
            "ffmpeg",
            "-i", reconstructed_path,
            "-i", input_video_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-map", "0:v:0",
            "-map", "1:a:0?",
            "-shortest",
            final_output_path,
            "-y",
            "-loglevel", "error",
        ]
        logger.info("audio_sync_muxing")
    else:
        # No audio — just copy the video
        cmd = ["ffmpeg", "-i", reconstructed_path, "-c", "copy", final_output_path, "-y", "-loglevel", "error"]
        logger.info("audio_sync_no_audio")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    if result.returncode != 0:
        # Fallback: use video without audio
        import shutil
        shutil.copy2(reconstructed_path, final_output_path)
        logger.warning("audio_mux_failed", error=result.stderr[:200])

    # Upload final result to storage
    from app.config import get_settings
    from app.core.storage import upload_file_path

    settings = get_settings()
    output_key = f"results/{job_id}/final_output.mp4"
    upload_file_path(final_output_path, settings.storage_bucket_results, output_key, "video/mp4")

    output_size = os.path.getsize(final_output_path) if os.path.exists(final_output_path) else 0
    context["output_bucket"] = settings.storage_bucket_results
    context["output_key"] = output_key
    context["output_size"] = output_size

    logger.info("audio_sync_complete", output_key=output_key, size_mb=round(output_size/(1024*1024), 1))
    return context
