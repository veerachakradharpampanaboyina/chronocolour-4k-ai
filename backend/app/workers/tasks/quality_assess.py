"""ChronoColor 4K AI — Quality Assessment Task"""
from __future__ import annotations
import os
from typing import Any
import cv2
import numpy as np
import structlog

logger = structlog.get_logger(__name__)


def run_quality_assessment(context: dict[str, Any]) -> dict[str, Any]:
    """Assess quality of processed frames using no-reference metrics."""
    final_dir = context["final_dir"]
    if not os.path.exists(final_dir) or not os.listdir(final_dir):
        final_dir = context["colorized_dir"]

    frame_files = sorted([f for f in os.listdir(final_dir) if f.endswith(('.png', '.jpg'))])
    sample_count = min(20, len(frame_files))
    indices = np.linspace(0, len(frame_files) - 1, sample_count, dtype=int)

    scores = []
    for idx in indices:
        frame = cv2.imread(os.path.join(final_dir, frame_files[idx]))
        if frame is None:
            continue
        score = _compute_brisque_approx(frame)
        scores.append(score)

    avg_score = float(np.mean(scores)) if scores else 0.0
    context["quality_score"] = avg_score
    context["quality_scores"] = [float(s) for s in scores]

    logger.info("quality_assessment_complete", avg_score=round(avg_score, 2), samples=len(scores))
    return context


def _compute_brisque_approx(frame: np.ndarray) -> float:
    """Approximate BRISQUE-like no-reference quality score (0-100, higher=better)."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float64)

    # Local mean and variance
    mu = cv2.GaussianBlur(gray, (7, 7), 1.5)
    mu_sq = mu * mu
    sigma = np.sqrt(np.abs(cv2.GaussianBlur(gray * gray, (7, 7), 1.5) - mu_sq))

    # MSCN (Mean Subtracted Contrast Normalized)
    mscn = (gray - mu) / (sigma + 1e-7)
    mscn_mean = np.mean(np.abs(mscn))
    mscn_std = np.std(mscn)

    # Sharpness via Laplacian
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    sharpness = min(100, laplacian_var / 50.0)

    # Combined score
    quality = (sharpness * 0.4 + mscn_std * 30 + (1 - mscn_mean) * 30)
    return float(np.clip(quality, 0, 100))
