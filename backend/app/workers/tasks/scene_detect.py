"""
ChronoColor 4K AI — Scene Detection Task

Classifies video scenes to provide context for realistic colorization.
"""

from __future__ import annotations

import os
from typing import Any

import cv2
import numpy as np
import structlog

logger = structlog.get_logger(__name__)

SCENE_CATEGORIES = [
    "beach", "forest", "city", "night", "sunset", "snow",
    "indoor", "stadium", "rural", "mountain", "desert", "underwater",
]


def run_scene_detection(context: dict[str, Any]) -> dict[str, Any]:
    """Classify scenes in the video for colorization context."""
    frames_dir = context["upscaled_dir"] or context["frames_dir"]
    frame_files = sorted([
        f for f in os.listdir(frames_dir)
        if f.endswith(('.png', '.jpg', '.jpeg'))
    ])

    # Sample keyframes for scene classification
    sample_count = min(20, len(frame_files))
    indices = np.linspace(0, len(frame_files) - 1, sample_count, dtype=int)

    scene_results = {}
    for idx in indices:
        frame_path = os.path.join(frames_dir, frame_files[idx])
        frame = cv2.imread(frame_path)
        if frame is None:
            continue

        scene = _classify_scene(frame)
        scene_results[frame_files[idx]] = scene

    # Determine dominant scene
    scene_counts = {}
    for scene_info in scene_results.values():
        label = scene_info["label"]
        scene_counts[label] = scene_counts.get(label, 0) + 1

    dominant_scene = max(scene_counts, key=scene_counts.get) if scene_counts else "outdoor"

    context["scene_info"] = {
        "dominant_scene": dominant_scene,
        "per_frame_scenes": scene_results,
        "scene_distribution": scene_counts,
    }

    logger.info("scene_detection_complete", dominant=dominant_scene, distribution=scene_counts)
    return context


def _classify_scene(frame: np.ndarray) -> dict:
    """
    Classify a single frame's scene using heuristics.

    In production, this uses an EfficientNet classifier.
    Fallback uses color/texture analysis.
    """
    try:
        from ai.model_registry import registry
        model = registry.get("scene_classifier")
        return model.predict(frame)
    except Exception:
        return _heuristic_scene_classify(frame)


def _heuristic_scene_classify(frame: np.ndarray) -> dict:
    """Heuristic scene classification based on image statistics."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)
    std_brightness = np.std(gray)

    # Texture analysis
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.mean(edges) / 255.0

    h, w = gray.shape
    top_brightness = np.mean(gray[:h//3, :])
    bottom_brightness = np.mean(gray[2*h//3:, :])

    # Simple heuristics
    if mean_brightness < 60:
        label = "night"
    elif top_brightness > 180 and bottom_brightness < 120:
        label = "sunset"
    elif edge_density > 0.15:
        label = "city"
    elif edge_density < 0.05 and top_brightness > 150:
        label = "beach"
    elif std_brightness > 60:
        label = "forest"
    else:
        label = "outdoor"

    return {"label": label, "confidence": 0.6}
