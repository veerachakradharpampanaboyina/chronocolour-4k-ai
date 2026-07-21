"""ChronoColor 4K AI — HDR Enhancement Task"""
from __future__ import annotations
import os
from typing import Any
import cv2
import numpy as np
import structlog
from tqdm import tqdm

logger = structlog.get_logger(__name__)


def run_hdr_enhancement(context: dict[str, Any]) -> dict[str, Any]:
    """Enhance dynamic range, contrast, and shadow/highlight detail."""
    colorized_dir = context["colorized_dir"]
    final_dir = context["final_dir"]
    os.makedirs(final_dir, exist_ok=True)

    frame_files = sorted([f for f in os.listdir(colorized_dir) if f.endswith(('.png', '.jpg'))])

    for frame_file in tqdm(frame_files, desc="HDR enhancement"):
        input_path = os.path.join(colorized_dir, frame_file)
        output_path = os.path.join(final_dir, frame_file)

        frame = cv2.imread(input_path)
        if frame is None:
            continue

        enhanced = _apply_hdr(frame)
        cv2.imwrite(output_path, enhanced, [cv2.IMWRITE_PNG_COMPRESSION, 3])

    logger.info("hdr_enhancement_complete", frames=len(frame_files))
    return context


def _apply_hdr(frame: np.ndarray) -> np.ndarray:
    """Apply HDR-like enhancement to a single frame."""
    # Local tone mapping via CLAHE on L channel
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # Adaptive CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)

    # Shadow recovery
    shadow_mask = (l < 60).astype(np.float32)
    shadow_boost = np.clip(l_enhanced.astype(np.float32) * 1.3, 0, 255).astype(np.uint8)
    l_enhanced = (l_enhanced * (1 - shadow_mask) + shadow_boost * shadow_mask).astype(np.uint8)

    # Highlight recovery
    highlight_mask = (l > 200).astype(np.float32)
    highlight_tamed = np.clip(l_enhanced.astype(np.float32) * 0.9, 0, 255).astype(np.uint8)
    l_enhanced = (l_enhanced * (1 - highlight_mask) + highlight_tamed * highlight_mask).astype(np.uint8)

    lab_enhanced = cv2.merge([l_enhanced, a, b])
    result = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

    # Slight saturation boost for cinematic look
    hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.1, 0, 255)
    result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    return result
