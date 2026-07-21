"""ChronoColor 4K AI — Video Reconstruction Task"""
from __future__ import annotations
import os
import subprocess
from typing import Any
import structlog

logger = structlog.get_logger(__name__)


def run_reconstruction(context: dict[str, Any]) -> dict[str, Any]:
    """Reconstruct processed frames into a video file using FFmpeg."""
    final_dir = context["final_dir"]
    if not os.path.exists(final_dir) or not os.listdir(final_dir):
        final_dir = context["colorized_dir"]

    config = context["pipeline_config"]
    fps = context.get("fps", 24)
    work_dir = context["work_dir"]
    output_path = os.path.join(work_dir, "output_video.mp4")

    codec = config.get("output_codec", "libx265")
    crf = 18

    frame_pattern = os.path.join(final_dir, "frame_%06d.png")

    cmd = [
        "ffmpeg",
        "-framerate", str(fps),
        "-i", frame_pattern,
        "-c:v", codec,
        "-crf", str(crf),
        "-preset", "slow",
        "-pix_fmt", "yuv420p10le" if config.get("enable_hdr_output") else "yuv420p",
        "-movflags", "+faststart",
        output_path,
        "-y",
        "-loglevel", "error",
    ]

    logger.info("reconstruction_starting", codec=codec, fps=fps)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)

    if result.returncode != 0:
        raise RuntimeError(f"Video reconstruction failed: {result.stderr[:500]}")

    output_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
    context["reconstructed_video_path"] = output_path
    context["output_size"] = output_size
    context["output_fps"] = fps

    logger.info("reconstruction_complete", output_size_mb=round(output_size / (1024*1024), 1))
    return context
