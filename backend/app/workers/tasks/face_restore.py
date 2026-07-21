"""
ChronoColor 4K AI — Face Restoration Task

Detects and restores faces in video frames using GFPGAN/CodeFormer.
"""

from __future__ import annotations

import os
from typing import Any

import cv2
import numpy as np
import structlog
from tqdm import tqdm

logger = structlog.get_logger(__name__)


def run_face_restoration(context: dict[str, Any]) -> dict[str, Any]:
    """
    Detect and restore faces in all frames.

    Uses face detection to locate faces, then enhances them with
    GFPGAN or CodeFormer, blending results back into the full frame.
    """
    upscaled_dir = context["upscaled_dir"]
    config = context["pipeline_config"]
    model_name = config.get("face_model", "codeformer")

    frame_files = sorted([
        f for f in os.listdir(upscaled_dir)
        if f.endswith(('.png', '.jpg', '.jpeg'))
    ])

    if not frame_files:
        upscaled_dir = context.get("restored_dir", context["frames_dir"])
        frame_files = sorted([
            f for f in os.listdir(upscaled_dir)
            if f.endswith(('.png', '.jpg', '.jpeg'))
        ])

    faces_restored = 0
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    for frame_file in tqdm(frame_files, desc="Restoring faces"):
        frame_path = os.path.join(upscaled_dir, frame_file)
        frame = cv2.imread(frame_path)
        if frame is None:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))

        if len(faces) > 0:
            for (x, y, w, h) in faces:
                # Expand face region by 30%
                pad = int(max(w, h) * 0.3)
                x1 = max(0, x - pad)
                y1 = max(0, y - pad)
                x2 = min(frame.shape[1], x + w + pad)
                y2 = min(frame.shape[0], y + h + pad)

                face_crop = frame[y1:y2, x1:x2].copy()

                try:
                    from ai.model_registry import registry
                    model = registry.get(model_name)
                    enhanced = model.predict(face_crop)
                except Exception:
                    enhanced = _enhance_face_opencv(face_crop)

                # Resize enhanced face to match crop
                enhanced = cv2.resize(enhanced, (x2 - x1, y2 - y1))

                # Blend with Gaussian feathering
                mask = np.zeros((y2 - y1, x2 - x1), dtype=np.float32)
                cv2.ellipse(mask, ((x2-x1)//2, (y2-y1)//2),
                           ((x2-x1)//2 - 5, (y2-y1)//2 - 5), 0, 0, 360, 1, -1)
                mask = cv2.GaussianBlur(mask, (21, 21), 10)
                mask_3ch = np.stack([mask] * 3, axis=-1)

                blended = (enhanced * mask_3ch + frame[y1:y2, x1:x2] * (1 - mask_3ch)).astype(np.uint8)
                frame[y1:y2, x1:x2] = blended
                faces_restored += 1

            cv2.imwrite(frame_path, frame, [cv2.IMWRITE_PNG_COMPRESSION, 3])

    context["faces_restored"] = faces_restored
    logger.info("face_restoration_complete", faces_restored=faces_restored)
    return context


def _enhance_face_opencv(face: np.ndarray) -> np.ndarray:
    """OpenCV fallback for face enhancement."""
    # Bilateral filter for skin smoothing while keeping edges
    smoothed = cv2.bilateralFilter(face, 9, 75, 75)
    # CLAHE for local contrast
    lab = cv2.cvtColor(smoothed, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(4, 4))
    l = clahe.apply(l)
    enhanced = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
    return enhanced
