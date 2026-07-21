"""
ChronoColor 4K AI — Object Tracking Task

Assigns persistent IDs to detected objects across frames using ByteTrack.
"""

from __future__ import annotations
import os
from typing import Any
import structlog

logger = structlog.get_logger(__name__)


def run_object_tracking(context: dict[str, Any]) -> dict[str, Any]:
    """
    Track detected objects across frames with persistent IDs.
    Example: Person_001 maintains same ID across all frames.
    """
    detections = context.get("detections", {})
    if not detections:
        logger.warning("no_detections_for_tracking")
        context["tracks"] = {}
        return context

    tracks = {}
    next_track_id = 1
    prev_objects = []

    for frame_name in sorted(detections.keys()):
        frame_dets = detections[frame_name]
        frame_tracks = []

        for det in frame_dets:
            bbox = det.get("bbox", [0, 0, 0, 0])
            cls = det.get("class", "object")

            # Simple IoU-based tracking (production uses ByteTrack)
            matched_id = _match_to_previous(bbox, prev_objects)
            if matched_id is None:
                matched_id = next_track_id
                next_track_id += 1

            track_label = f"{cls}_{matched_id:03d}"
            frame_tracks.append({
                "track_id": matched_id,
                "label": track_label,
                "class": cls,
                "bbox": bbox,
            })

        tracks[frame_name] = frame_tracks
        prev_objects = frame_tracks

    context["tracks"] = tracks
    unique_tracks = len(set(
        t["track_id"] for frame_tracks in tracks.values() for t in frame_tracks
    ))
    logger.info("tracking_complete", unique_tracks=unique_tracks)
    return context


def _match_to_previous(bbox, prev_objects, iou_threshold=0.3):
    """Match a detection to a previous frame's tracked object via IoU."""
    best_iou = 0
    best_id = None
    for prev in prev_objects:
        iou = _compute_iou(bbox, prev["bbox"])
        if iou > best_iou and iou > iou_threshold:
            best_iou = iou
            best_id = prev["track_id"]
    return best_id


def _compute_iou(box1, box2):
    """Compute Intersection over Union between two [x, y, w, h] boxes."""
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    xi1 = max(x1, x2)
    yi1 = max(y1, y2)
    xi2 = min(x1 + w1, x2 + w2)
    yi2 = min(y1 + h1, y2 + h2)
    inter = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    union = w1 * h1 + w2 * h2 - inter
    return inter / union if union > 0 else 0
