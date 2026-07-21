"""ChronoColor 4K AI — Flicker Correction Task"""
from __future__ import annotations
import os
from typing import Any
import cv2
import numpy as np
import structlog
from tqdm import tqdm

logger = structlog.get_logger(__name__)


def run_flicker_correction(context: dict[str, Any]) -> dict[str, Any]:
    """Smooth color flickering between adjacent frames."""
    colorized_dir = context["colorized_dir"]
    frame_files = sorted([f for f in os.listdir(colorized_dir) if f.endswith(('.png', '.jpg'))])

    if len(frame_files) < 3:
        return context

    # Temporal smoothing with sliding window
    window_size = 5
    buffer = []
    corrections = 0

    for i, frame_file in enumerate(tqdm(frame_files, desc="Flicker correction")):
        frame = cv2.imread(os.path.join(colorized_dir, frame_file))
        if frame is None:
            continue

        buffer.append(frame.astype(np.float32))

        if len(buffer) > window_size:
            buffer.pop(0)

        if len(buffer) >= 3:
            center_idx = len(buffer) // 2
            # Weighted temporal average
            weights = np.array([0.1, 0.2, 0.4, 0.2, 0.1][:len(buffer)])
            weights = weights / weights.sum()

            smoothed = np.zeros_like(buffer[center_idx])
            for j, w in enumerate(weights):
                smoothed += buffer[j] * w

            # Only apply correction if there's significant flicker
            diff = np.mean(np.abs(buffer[center_idx] - smoothed))
            if diff > 5.0:
                # Blend original with smoothed
                alpha = min(0.6, diff / 30.0)
                corrected = (buffer[center_idx] * (1 - alpha) + smoothed * alpha).astype(np.uint8)
                center_file = frame_files[max(0, i - len(buffer) // 2)]
                cv2.imwrite(os.path.join(colorized_dir, center_file), corrected)
                corrections += 1

    context["flicker_corrections"] = corrections
    logger.info("flicker_correction_complete", corrections=corrections)
    return context
