"""
ChronoColor 4K AI — Pipeline Configuration Schema

Provides pipeline preset configurations and validation.
"""

from __future__ import annotations

from pydantic import BaseModel

from app.models.job import PipelineConfig


# --- Quality Presets ---

QUALITY_PRESETS: dict[str, PipelineConfig] = {
    "fast": PipelineConfig(
        quality_preset="fast",
        enable_restoration=True,
        enable_super_resolution=True,
        enable_face_restoration=False,
        enable_scene_understanding=True,
        enable_object_detection=True,
        enable_object_tracking=False,
        enable_segmentation=False,
        enable_colorization=True,
        enable_temporal_memory=False,
        enable_optical_flow=False,
        enable_flicker_correction=True,
        enable_hdr_enhancement=False,
        enable_quality_assessment=False,
        target_resolution="1080p",
        restoration_model="nafnet",
        superres_model="real_esrgan",
        colorization_model="ddcolor",
    ),
    "balanced": PipelineConfig(
        quality_preset="balanced",
        enable_restoration=True,
        enable_super_resolution=True,
        enable_face_restoration=True,
        enable_scene_understanding=True,
        enable_object_detection=True,
        enable_object_tracking=True,
        enable_segmentation=True,
        enable_colorization=True,
        enable_temporal_memory=True,
        enable_optical_flow=True,
        enable_flicker_correction=True,
        enable_hdr_enhancement=True,
        enable_quality_assessment=True,
        target_resolution="4k",
        restoration_model="nafnet",
        superres_model="real_esrgan",
        face_model="codeformer",
        colorization_model="ddcolor",
    ),
    "maximum": PipelineConfig(
        quality_preset="maximum",
        enable_restoration=True,
        enable_super_resolution=True,
        enable_face_restoration=True,
        enable_scene_understanding=True,
        enable_object_detection=True,
        enable_object_tracking=True,
        enable_segmentation=True,
        enable_colorization=True,
        enable_temporal_memory=True,
        enable_optical_flow=True,
        enable_flicker_correction=True,
        enable_hdr_enhancement=True,
        enable_quality_assessment=True,
        target_resolution="4k",
        restoration_model="basicvsr_pp",
        superres_model="hat",
        face_model="codeformer",
        colorization_model="ddcolor",
        output_codec="libx265",
        enable_hdr_output=True,
    ),
}


class PipelinePresetInfo(BaseModel):
    """Info about a pipeline quality preset."""

    name: str
    display_name: str
    description: str
    estimated_time_multiplier: float
    active_stages: int
    target_resolution: str


def get_preset_info() -> list[PipelinePresetInfo]:
    """Get information about all available quality presets."""
    return [
        PipelinePresetInfo(
            name="fast",
            display_name="Fast",
            description="Quick processing with essential stages. Good for previews.",
            estimated_time_multiplier=0.3,
            active_stages=7,
            target_resolution="1080p",
        ),
        PipelinePresetInfo(
            name="balanced",
            display_name="Balanced",
            description="Full pipeline with optimal quality-speed balance. Recommended.",
            estimated_time_multiplier=1.0,
            active_stages=16,
            target_resolution="4K",
        ),
        PipelinePresetInfo(
            name="maximum",
            display_name="Maximum Quality",
            description="Highest quality with premium models. Longest processing time.",
            estimated_time_multiplier=2.5,
            active_stages=16,
            target_resolution="4K",
        ),
    ]
