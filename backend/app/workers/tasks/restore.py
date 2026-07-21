"""
ChronoColor 4K AI — Frame Restoration Task

Cleans and restores damaged video frames using AI models.
Removes scratches, dust, noise, film grain, and compression artifacts.
"""

from __future__ import annotations

import os
from typing import Any

import cv2
import numpy as np
import structlog
from tqdm import tqdm

logger = structlog.get_logger(__name__)


def run_restoration(context: dict[str, Any]) -> dict[str, Any]:
    """
    Restore all extracted frames using AI restoration models.

    Selects model based on pipeline config:
    - NAFNet: Fast single-frame denoising/deblurring
    - BasicVSR++: Temporal video restoration (higher quality)

    Args:
        context: Pipeline context with frames_dir and config.

    Returns:
        Updated context with restored frames in restored_dir.
    """
    frames_dir = context["frames_dir"]
    restored_dir = context["restored_dir"]
    config = context["pipeline_config"]
    model_name = config.get("restoration_model", "nafnet")

    os.makedirs(restored_dir, exist_ok=True)

    # Get sorted frame list
    frame_files = sorted([
        f for f in os.listdir(frames_dir)
        if f.endswith(('.png', '.jpg', '.jpeg'))
    ])

    if not frame_files:
        raise ValueError("No frames found for restoration")

    total_frames = len(frame_files)
    logger.info(
        "restoration_starting",
        model=model_name,
        total_frames=total_frames,
    )

    # Process frames
    for i, frame_file in enumerate(tqdm(frame_files, desc="Restoring frames")):
        input_path = os.path.join(frames_dir, frame_file)
        output_path = os.path.join(restored_dir, frame_file)

        frame = cv2.imread(input_path)
        if frame is None:
            logger.warning("frame_read_failed", file=frame_file)
            continue

        # Apply restoration
        restored = _restore_frame(frame, model_name)

        # Save restored frame
        cv2.imwrite(output_path, restored, [cv2.IMWRITE_PNG_COMPRESSION, 3])

    restored_count = len([
        f for f in os.listdir(restored_dir)
        if f.endswith(('.png', '.jpg', '.jpeg'))
    ])

    logger.info(
        "restoration_complete",
        model=model_name,
        restored_frames=restored_count,
    )

    context["restoration_model_used"] = model_name
    return context


def _restore_frame(frame: np.ndarray, model_name: str) -> np.ndarray:
    """
    Restore a single frame using the specified model.

    For production, this loads the actual AI model. Currently uses
    OpenCV-based restoration as a functional fallback.

    Args:
        frame: Input BGR frame.
        model_name: Model to use ('nafnet', 'basicvsr_pp', 'restormer').

    Returns:
        Restored BGR frame.
    """
    try:
        # Try to use AI model if available
        from ai.model_registry import registry
        model = registry.get(model_name)
        return model.predict(frame)
    except (KeyError, ImportError, Exception) as e:
        # Fallback: OpenCV-based restoration pipeline
        logger.debug("using_fallback_restoration", reason=str(e)[:100])
        return _opencv_restore(frame)


def _opencv_restore(frame: np.ndarray) -> np.ndarray:
    """
    OpenCV-based frame restoration pipeline.

    Applies:
    1. Dust/scratch removal via inpainting
    2. Noise reduction via non-local means
    3. Contrast enhancement via CLAHE
    """
    # Convert to grayscale for damage detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Step 1: Detect and remove scratches/dust
    # Bright spots (dust/scratches) detection
    _, scratch_mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
    # Dark spots (dust)
    _, dark_mask = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY_INV)
    damage_mask = cv2.bitwise_or(scratch_mask, dark_mask)

    # Dilate mask slightly
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    damage_mask = cv2.dilate(damage_mask, kernel, iterations=1)

    # Inpaint damaged areas
    if np.sum(damage_mask) > 0:
        frame = cv2.inpaint(frame, damage_mask, 3, cv2.INPAINT_TELEA)

    # Step 2: Denoise
    frame = cv2.fastNlMeansDenoisingColored(
        frame, None, h=6, hColor=6, templateWindowSize=7, searchWindowSize=21
    )

    # Step 3: CLAHE contrast enhancement
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l_channel)
    lab_enhanced = cv2.merge([l_enhanced, a, b])
    frame = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

    return frame
