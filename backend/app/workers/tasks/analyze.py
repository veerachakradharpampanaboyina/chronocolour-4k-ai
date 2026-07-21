"""
ChronoColor 4K AI — Video Analysis Task

Analyzes input video properties using FFprobe and OpenCV.
Extracts resolution, FPS, noise/blur/damage levels, and scene changes.
"""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any

import cv2
import numpy as np
import structlog

logger = structlog.get_logger(__name__)


def run_analysis(context: dict[str, Any]) -> dict[str, Any]:
    """
    Analyze the input video and extract frames.

    Steps:
    1. Download video from storage
    2. Run FFprobe for technical metadata
    3. Analyze frames for quality metrics
    4. Detect scene changes
    5. Extract frames to disk

    Args:
        context: Pipeline context dict.

    Returns:
        Updated context with analysis results and extracted frames.
    """
    from app.config import get_settings
    from app.core.storage import download_file

    settings = get_settings()

    # --- Step 1: Download video from storage ---
    job_id = context["job_id"]
    video_id = context["video_id"]

    # Get video document for storage info
    import asyncio
    from beanie import PydanticObjectId
    from app.models.video import Video, VideoAnalysis

    loop = asyncio.new_event_loop()

    async def _get_video():
        from app.core.database import init_database
        await init_database(settings)
        return await Video.get(PydanticObjectId(video_id))

    video = loop.run_until_complete(_get_video())
    loop.close()

    if not video or not video.storage_key:
        raise ValueError(f"Video not found or not uploaded: {video_id}")

    # Download to working directory
    local_video_path = os.path.join(context["work_dir"], "input_video" +
                                     os.path.splitext(video.original_filename)[1])
    download_file(video.storage_bucket, video.storage_key, local_video_path)
    context["input_video_path"] = local_video_path

    logger.info("video_downloaded", path=local_video_path)

    # --- Step 2: FFprobe analysis ---
    probe_data = _run_ffprobe(local_video_path)

    # --- Step 3: OpenCV quality analysis ---
    quality_metrics = _analyze_quality(local_video_path, max_sample_frames=30)

    # --- Step 4: Build analysis result ---
    video_stream = _get_video_stream(probe_data)
    audio_stream = _get_audio_stream(probe_data)

    width = int(video_stream.get("width", 0))
    height = int(video_stream.get("height", 0))
    fps_parts = video_stream.get("r_frame_rate", "24/1").split("/")
    fps = float(fps_parts[0]) / float(fps_parts[1]) if len(fps_parts) == 2 else 24.0
    duration = float(probe_data.get("format", {}).get("duration", 0))
    total_frames = int(duration * fps)

    analysis = VideoAnalysis(
        resolution_width=width,
        resolution_height=height,
        fps=round(fps, 2),
        total_frames=total_frames,
        duration_seconds=round(duration, 2),
        codec=video_stream.get("codec_name", "unknown"),
        bitrate_kbps=int(probe_data.get("format", {}).get("bit_rate", 0)) // 1000,
        file_size_bytes=video.file_size_bytes,
        noise_level=quality_metrics["noise_level"],
        blur_level=quality_metrics["blur_level"],
        damage_level=quality_metrics["damage_level"],
        compression_artifact_level=quality_metrics["compression_artifact_level"],
        scene_change_count=quality_metrics["scene_change_count"],
        scene_change_timestamps=quality_metrics.get("scene_change_timestamps", []),
        is_grayscale=quality_metrics["is_grayscale"],
        has_audio=audio_stream is not None,
        audio_codec=audio_stream.get("codec_name", "") if audio_stream else "",
        audio_sample_rate=int(audio_stream.get("sample_rate", 0)) if audio_stream else 0,
    )

    # Update video document with analysis
    loop2 = asyncio.new_event_loop()

    async def _update_video():
        from app.core.database import init_database
        await init_database(settings)
        v = await Video.get(PydanticObjectId(video_id))
        if v:
            v.mark_analyzed(analysis)
            await v.save()

    loop2.run_until_complete(_update_video())
    loop2.close()

    # --- Step 5: Extract frames ---
    frames_dir = context["frames_dir"]
    _extract_frames(local_video_path, frames_dir, fps)

    frame_count = len([f for f in os.listdir(frames_dir) if f.endswith(('.png', '.jpg'))])

    # Update context
    context["analysis"] = analysis.model_dump()
    context["total_frames"] = frame_count
    context["fps"] = fps
    context["width"] = width
    context["height"] = height
    context["has_audio"] = analysis.has_audio

    logger.info(
        "analysis_complete",
        job_id=job_id,
        resolution=f"{width}x{height}",
        fps=fps,
        duration=duration,
        frames=frame_count,
        is_grayscale=analysis.is_grayscale,
    )

    return context


def _run_ffprobe(video_path: str) -> dict:
    """Run FFprobe and return parsed JSON output."""
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"FFprobe failed: {result.stderr[:500]}")
    return json.loads(result.stdout)


def _get_video_stream(probe_data: dict) -> dict:
    """Extract the first video stream from FFprobe data."""
    for stream in probe_data.get("streams", []):
        if stream.get("codec_type") == "video":
            return stream
    return {}


def _get_audio_stream(probe_data: dict) -> dict | None:
    """Extract the first audio stream from FFprobe data."""
    for stream in probe_data.get("streams", []):
        if stream.get("codec_type") == "audio":
            return stream
    return None


def _analyze_quality(video_path: str, max_sample_frames: int = 30) -> dict:
    """
    Analyze video quality by sampling frames.

    Measures noise, blur, damage, and compression artifacts.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    sample_indices = np.linspace(0, total_frames - 1, min(max_sample_frames, total_frames), dtype=int)

    noise_scores = []
    blur_scores = []
    damage_scores = []
    artifact_scores = []
    grayscale_votes = []
    prev_hist = None
    scene_changes = []

    for idx in sample_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Noise level (Laplacian variance — lower = noisier for smooth images)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        noise = min(1.0, np.var(laplacian) / 5000.0)
        noise_scores.append(1.0 - noise)

        # Blur level (gradient magnitude)
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        grad_mag = np.sqrt(grad_x**2 + grad_y**2)
        blur = min(1.0, 1.0 - np.mean(grad_mag) / 100.0)
        blur_scores.append(max(0.0, blur))

        # Damage level (bright spots / scratches via morphological ops)
        _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        damage = np.sum(thresh > 0) / thresh.size
        damage_scores.append(min(1.0, damage * 10))

        # Compression artifacts (block boundary detection)
        block_size = 8
        h, w = gray.shape
        block_h, block_w = h // block_size, w // block_size
        if block_h > 0 and block_w > 0:
            edges = cv2.Canny(gray, 50, 150)
            artifact = np.mean(edges[::block_size, :]) + np.mean(edges[:, ::block_size])
            artifact_scores.append(min(1.0, artifact / 100.0))

        # Grayscale detection
        if len(frame.shape) == 3:
            b, g, r = cv2.split(frame)
            color_diff = np.mean(np.abs(r.astype(float) - g.astype(float))) + \
                        np.mean(np.abs(g.astype(float) - b.astype(float)))
            grayscale_votes.append(color_diff < 10)
        else:
            grayscale_votes.append(True)

        # Scene change detection (histogram comparison)
        hist = cv2.calcHist([gray], [0], None, [64], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        if prev_hist is not None:
            similarity = cv2.compareHist(
                prev_hist, hist, cv2.HISTCMP_CORREL
            )
            if similarity < 0.7:
                timestamp = idx / max(1, cap.get(cv2.CAP_PROP_FPS) or 24)
                scene_changes.append(round(timestamp, 2))
        prev_hist = hist

    cap.release()

    return {
        "noise_level": round(float(np.mean(noise_scores)) if noise_scores else 0.0, 3),
        "blur_level": round(float(np.mean(blur_scores)) if blur_scores else 0.0, 3),
        "damage_level": round(float(np.mean(damage_scores)) if damage_scores else 0.0, 3),
        "compression_artifact_level": round(
            float(np.mean(artifact_scores)) if artifact_scores else 0.0, 3
        ),
        "is_grayscale": sum(grayscale_votes) > len(grayscale_votes) * 0.8 if grayscale_votes else True,
        "scene_change_count": len(scene_changes),
        "scene_change_timestamps": scene_changes[:50],
    }


def _extract_frames(video_path: str, output_dir: str, fps: float) -> int:
    """
    Extract all frames from video using FFmpeg.

    Args:
        video_path: Path to input video.
        output_dir: Directory to save frames.
        fps: Target FPS for extraction.

    Returns:
        Number of frames extracted.
    """
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"fps={fps}",
        "-qscale:v", "2",
        os.path.join(output_dir, "frame_%06d.png"),
        "-y",
        "-loglevel", "error",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    if result.returncode != 0:
        raise RuntimeError(f"Frame extraction failed: {result.stderr[:500]}")

    frame_count = len([f for f in os.listdir(output_dir) if f.endswith('.png')])
    logger.info("frames_extracted", count=frame_count, output_dir=output_dir)
    return frame_count
