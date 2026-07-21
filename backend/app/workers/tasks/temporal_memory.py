"""ChronoColor 4K AI — Temporal Color Memory Task"""
from __future__ import annotations
import os
from typing import Any
import cv2
import numpy as np
import structlog

logger = structlog.get_logger(__name__)


def run_temporal_memory(context: dict[str, Any]) -> dict[str, Any]:
    """Maintain consistent colors for tracked objects across frames."""
    colorized_dir = context["colorized_dir"]
    tracks = context.get("tracks", {})

    color_memory = {}  # track_id -> running average RGB

    frame_files = sorted([f for f in os.listdir(colorized_dir) if f.endswith(('.png', '.jpg'))])

    for frame_file in frame_files:
        frame_path = os.path.join(colorized_dir, frame_file)
        frame = cv2.imread(frame_path)
        if frame is None:
            continue

        frame_tracks = tracks.get(frame_file, [])
        modified = False

        for track in frame_tracks:
            tid = track["track_id"]
            bbox = track["bbox"]
            x, y, w, h = bbox

            # Sample color from region
            roi = frame[max(0,y):min(frame.shape[0],y+h), max(0,x):min(frame.shape[1],x+w)]
            if roi.size == 0:
                continue

            current_color = np.mean(roi, axis=(0, 1))

            if tid in color_memory:
                stored_color = color_memory[tid]
                color_diff = np.linalg.norm(current_color - stored_color)

                if color_diff > 40:  # Significant color shift — correct it
                    # Blend toward stored color
                    correction = stored_color * 0.7 + current_color * 0.3
                    scale = correction / (current_color + 1e-6)
                    scale = np.clip(scale, 0.5, 1.5)

                    corrected_roi = (roi.astype(np.float32) * scale).clip(0, 255).astype(np.uint8)
                    frame[max(0,y):min(frame.shape[0],y+h), max(0,x):min(frame.shape[1],x+w)] = corrected_roi
                    modified = True

                    # Slow update of stored color
                    color_memory[tid] = stored_color * 0.95 + current_color * 0.05
                else:
                    color_memory[tid] = stored_color * 0.9 + current_color * 0.1
            else:
                color_memory[tid] = current_color

        if modified:
            cv2.imwrite(frame_path, frame, [cv2.IMWRITE_PNG_COMPRESSION, 3])

    context["color_memory"] = {str(k): v.tolist() for k, v in color_memory.items()}
    logger.info("temporal_memory_complete", tracked_objects=len(color_memory))
    return context
