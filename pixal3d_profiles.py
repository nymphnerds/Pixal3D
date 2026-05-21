"""Runtime profile presets for Pixal3D local testing.

These are UI/API defaults only. Every value remains overrideable from the
advanced controls so real hardware testing can decide which profile wins.
"""

from __future__ import annotations

from copy import deepcopy


PROFILE_ORDER = [
    "preview_16gb",
    "balanced_16gb",
    "quality_16gb",
    "high_vram_1536",
]


OPTIMIZATION_PROFILES = {
    "preview_16gb": {
        "id": "preview_16gb",
        "label": "Preview 16GB",
        "description": "Fast 1024 low-VRAM test pass.",
        "low_vram": True,
        "resolution": 1024,
        "ss_sampling_steps": 8,
        "shape_slat_sampling_steps": 8,
        "tex_slat_sampling_steps": 8,
        "max_num_tokens": 16384,
        "decimation_target": 100000,
        "texture_size": 2048,
        "texture_naf_target_size": 512,
    },
    "balanced_16gb": {
        "id": "balanced_16gb",
        "label": "Balanced 16GB",
        "description": "Best first target for RTX 4080 SUPER 16GB.",
        "low_vram": True,
        "resolution": 1024,
        "ss_sampling_steps": 12,
        "shape_slat_sampling_steps": 12,
        "tex_slat_sampling_steps": 12,
        "max_num_tokens": 32768,
        "decimation_target": 200000,
        "texture_size": 2048,
        "texture_naf_target_size": 512,
    },
    "quality_16gb": {
        "id": "quality_16gb",
        "label": "Quality 16GB",
        "description": "Higher-detail 1024 run; may need a freshly freed pipeline.",
        "low_vram": True,
        "resolution": 1024,
        "ss_sampling_steps": 16,
        "shape_slat_sampling_steps": 16,
        "tex_slat_sampling_steps": 16,
        "max_num_tokens": 32768,
        "decimation_target": 300000,
        "texture_size": 4096,
        "texture_naf_target_size": 768,
    },
    "high_vram_1536": {
        "id": "high_vram_1536",
        "label": "1536 High VRAM",
        "description": "Heavy quality profile for 24GB+ cards.",
        "low_vram": False,
        "resolution": 1536,
        "ss_sampling_steps": 16,
        "shape_slat_sampling_steps": 16,
        "tex_slat_sampling_steps": 16,
        "max_num_tokens": 49152,
        "decimation_target": 300000,
        "texture_size": 4096,
        "texture_naf_target_size": 1024,
    },
}


PROFILE_ALIASES = {
    "low_vram_1024": "balanced_16gb",
    "standard_1536": "high_vram_1536",
    "balanced": "balanced_16gb",
    "preview": "preview_16gb",
    "quality": "quality_16gb",
    "1536": "high_vram_1536",
}


def normalize_profile_id(profile_id: str | None, default: str = "balanced_16gb") -> str:
    value = (profile_id or default).strip().lower()
    value = PROFILE_ALIASES.get(value, value)
    if value not in OPTIMIZATION_PROFILES:
        return default
    return value


def get_profile(profile_id: str | None, default: str = "balanced_16gb") -> dict:
    return deepcopy(OPTIMIZATION_PROFILES[normalize_profile_id(profile_id, default)])


def list_profiles() -> list[dict]:
    return [get_profile(profile_id) for profile_id in PROFILE_ORDER]
