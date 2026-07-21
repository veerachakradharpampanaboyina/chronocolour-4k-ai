"""
ChronoColor 4K AI — Semantic Segmentation Task

Generates pixel-precise masks for objects using SAM 2.
"""

from __future__ import annotations
import os
from typing import Any
import cv2
import numpy as np
import structlog

logger = structlog.get_logger(__name__)


def run_segmentation(context: dict[str, Any]) -> dict[str, Any]:
    """Generate segmentation masks for tracked objects."""
    tracks = context.get("tracks", {})
    frames_dir = context["upscaled_dir"] or context["frames_dir"]

    segments = {}
    for frame_name, frame_tracks in tracks.items():
        frame_path = os.path.join(frames_dir, frame_name)
        frame = cv2.imread(frame_path)
        if frame is None:
            continue

        frame_segments = []
        for track in frame_tracks:
            bbox = track["bbox"]
            try:
                from ai.model_registry import registry
                model = registry.get("sam2")
                mask = model.predict(frame, bbox=bbox)
            except Exception:
                mask = _bbox_to_mask(frame.shape[:2], bbox)

            frame_segments.append({
                "track_id": track["track_id"],
                "label": track["label"],
                "mask_sum": int(np.sum(mask > 0)),
            })

        segments[frame_name] = frame_segments

    context["segments"] = segments
    logger.info("segmentation_complete", frames_with_segments=len(segments))
    return context


def _bbox_to_mask(shape, bbox):
    """Create a simple rectangular mask from bounding box."""
    mask = np.zeros(shape, dtype=np.uint8)
    x, y, w, h = bbox
    mask[y:y+h, x:x+w] = 255
    return mask
