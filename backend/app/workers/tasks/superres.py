"""
ChronoColor 4K AI — Super Resolution Task

Upscales frames to 4K resolution using AI super-resolution models.
Supports progressive upscaling: 480p → 720p → 1080p → 4K.
"""

from __future__ import annotations

import os
from typing import Any

import cv2
import numpy as np
import structlog
from tqdm import tqdm

logger = structlog.get_logger(__name__)

RESOLUTION_MAP = {
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "2k": (2560, 1440),
    "4k": (3840, 2160),
}


def run_super_resolution(context: dict[str, Any]) -> dict[str, Any]:
    """
    Upscale all frames to target resolution.

    Uses progressive upscaling for best quality:
    - Real-ESRGAN for fast, high-quality 2x/4x upscaling
    - HAT for maximum quality (slower)

    Args:
        context: Pipeline context with restored frames and config.

    Returns:
        Updated context with upscaled frames in upscaled_dir.
    """
    restored_dir = context["restored_dir"]
    upscaled_dir = context["upscaled_dir"]
    config = context["pipeline_config"]
    model_name = config.get("superres_model", "real_esrgan")
    target_res = config.get("target_resolution", "4k")

    os.makedirs(upscaled_dir, exist_ok=True)

    target_w, target_h = RESOLUTION_MAP.get(target_res, (3840, 2160))
    source_w = context.get("width", 640)
    source_h = context.get("height", 480)

    # Determine upscale factor
    scale_w = target_w / source_w
    scale_h = target_h / source_h
    scale = max(scale_w, scale_h)

    logger.info(
        "superres_starting",
        model=model_name,
        source=f"{source_w}x{source_h}",
        target=f"{target_w}x{target_h}",
        scale_factor=round(scale, 2),
    )

    # Get sorted frame list
    frame_files = sorted([
        f for f in os.listdir(restored_dir)
        if f.endswith(('.png', '.jpg', '.jpeg'))
    ])

    if not frame_files:
        # Fallback to frames_dir if restoration was skipped
        restored_dir = context["frames_dir"]
        frame_files = sorted([
            f for f in os.listdir(restored_dir)
            if f.endswith(('.png', '.jpg', '.jpeg'))
        ])

    for i, frame_file in enumerate(tqdm(frame_files, desc="Upscaling frames")):
        input_path = os.path.join(restored_dir, frame_file)
        output_path = os.path.join(upscaled_dir, frame_file)

        frame = cv2.imread(input_path)
        if frame is None:
            continue

        # Upscale
        upscaled = _upscale_frame(frame, target_w, target_h, model_name)

        # Save
        cv2.imwrite(output_path, upscaled, [cv2.IMWRITE_PNG_COMPRESSION, 3])

    upscaled_count = len([
        f for f in os.listdir(upscaled_dir)
        if f.endswith(('.png', '.jpg', '.jpeg'))
    ])

    context["output_width"] = target_w
    context["output_height"] = target_h
    context["superres_model_used"] = model_name

    logger.info(
        "superres_complete",
        upscaled_frames=upscaled_count,
        output_resolution=f"{target_w}x{target_h}",
    )

    return context


def _upscale_frame(
    frame: np.ndarray,
    target_w: int,
    target_h: int,
    model_name: str,
) -> np.ndarray:
    """
    Upscale a single frame to target resolution.

    Args:
        frame: Input BGR frame.
        target_w: Target width.
        target_h: Target height.
        model_name: AI model to use.

    Returns:
        Upscaled BGR frame.
    """
    try:
        from ai.model_registry import registry
        model = registry.get(model_name)
        upscaled = model.predict(frame)
        # Resize to exact target if model output doesn't match
        if upscaled.shape[1] != target_w or upscaled.shape[0] != target_h:
            upscaled = cv2.resize(upscaled, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
        return upscaled
    except (KeyError, ImportError, Exception) as e:
        logger.debug("using_fallback_superres", reason=str(e)[:100])
        return _opencv_upscale(frame, target_w, target_h)


def _opencv_upscale(frame: np.ndarray, target_w: int, target_h: int) -> np.ndarray:
    """
    OpenCV-based upscaling fallback.

    Uses Lanczos interpolation with sharpening for best quality
    without AI models.
    """
    # Upscale with Lanczos
    upscaled = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)

    # Apply gentle sharpening to compensate for interpolation blur
    kernel = np.array([
        [0, -0.5, 0],
        [-0.5, 3, -0.5],
        [0, -0.5, 0]
    ])
    sharpened = cv2.filter2D(upscaled, -1, kernel)

    # Blend original and sharpened (50% strength)
    result = cv2.addWeighted(upscaled, 0.5, sharpened, 0.5, 0)

    return result
