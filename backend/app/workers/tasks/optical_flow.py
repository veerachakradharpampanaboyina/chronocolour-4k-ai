"""ChronoColor 4K AI — Optical Flow Task"""
from __future__ import annotations
import os
from typing import Any
import cv2
import numpy as np
import structlog

logger = structlog.get_logger(__name__)


def run_optical_flow(context: dict[str, Any]) -> dict[str, Any]:
    """Compute optical flow for color propagation between frames."""
    colorized_dir = context["colorized_dir"]
    frame_files = sorted([f for f in os.listdir(colorized_dir) if f.endswith(('.png', '.jpg'))])

    if len(frame_files) < 2:
        context["flow_computed"] = False
        return context

    prev_gray = None
    flow_stats = {"frames_processed": 0, "avg_motion": 0.0}

    for i, frame_file in enumerate(frame_files):
        frame = cv2.imread(os.path.join(colorized_dir, frame_file))
        if frame is None:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_gray is not None:
            try:
                from ai.model_registry import registry
                model = registry.get("raft")
                flow = model.predict(prev_gray, gray)
            except Exception:
                flow = cv2.calcOpticalFlowFarneback(
                    prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
                )

            magnitude = np.sqrt(flow[:,:,0]**2 + flow[:,:,1]**2)
            flow_stats["avg_motion"] += np.mean(magnitude)
            flow_stats["frames_processed"] += 1

        prev_gray = gray

    if flow_stats["frames_processed"] > 0:
        flow_stats["avg_motion"] /= flow_stats["frames_processed"]

    context["flow_computed"] = True
    context["flow_stats"] = flow_stats
    logger.info("optical_flow_complete", **flow_stats)
    return context
