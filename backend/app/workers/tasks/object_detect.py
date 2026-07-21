"""
ChronoColor 4K AI — Object Detection Task

Detects objects in frames using YOLOv11 for semantic colorization.
"""

from __future__ import annotations
import os
from typing import Any
import cv2
import numpy as np
import structlog
from tqdm import tqdm

logger = structlog.get_logger(__name__)


def run_object_detection(context: dict[str, Any]) -> dict[str, Any]:
    """Run object detection on all frames."""
    frames_dir = context["upscaled_dir"] or context["frames_dir"]
    frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith(('.png', '.jpg'))])

    detections = {}
    for frame_file in tqdm(frame_files, desc="Detecting objects"):
        frame_path = os.path.join(frames_dir, frame_file)
        frame = cv2.imread(frame_path)
        if frame is None:
            continue
        try:
            from ai.model_registry import registry
            model = registry.get("yolov11")
            dets = model.predict(frame)
        except Exception:
            dets = _fallback_detection(frame)
        detections[frame_file] = dets

    context["detections"] = detections
    total = sum(len(d) for d in detections.values())
    logger.info("object_detection_complete", total_detections=total)
    return context


def _fallback_detection(frame: np.ndarray) -> list[dict]:
    """Simple contour-based object detection fallback."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detections = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 1000:
            x, y, w, h = cv2.boundingRect(cnt)
            detections.append({"bbox": [x, y, w, h], "class": "object", "confidence": 0.5})
    return detections[:50]
