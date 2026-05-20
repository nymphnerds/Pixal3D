#!/usr/bin/env python3
"""Small Nymphs/Blender API wrapper for Pixal3D.

The heavy Pixal3D imports are intentionally lazy so /health and /server_info can
answer even while the model cache is still being prepared.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

APP = FastAPI(title="Pixal3D Nymph API")
ACTIVE_TASK: dict[str, Any] = {
    "status": "idle",
    "stage": "",
    "detail": "",
    "progress_current": None,
    "progress_total": None,
    "progress_percent": None,
    "message": "",
}
TASK_LOCK = threading.Lock()


def _set_task(**updates: Any) -> None:
    with TASK_LOCK:
        ACTIVE_TASK.update(updates)


def _task_snapshot() -> dict[str, Any]:
    with TASK_LOCK:
        return dict(ACTIVE_TASK)


def _bool_env(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _decode_image_payload(raw: str) -> bytes:
    if not raw:
        raise HTTPException(status_code=400, detail="Missing image payload.")
    if "," in raw and raw.split(",", 1)[0].lower().startswith("data:"):
        raw = raw.split(",", 1)[1]
    try:
        return base64.b64decode(raw, validate=False)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image payload: {exc}") from exc


def _as_int(value: Any, default: int) -> int:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except Exception:
        return default


def _as_float(value: Any, default: float) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _resolution_from_payload(payload: dict[str, Any], default: int) -> int:
    explicit = _as_int(payload.get("pixal3d_resolution") or payload.get("resolution"), 0)
    if explicit in {1024, 1536}:
        return explicit
    pipeline_type = str(payload.get("pipeline_type") or "").strip()
    if pipeline_type.startswith("1536"):
        return 1536
    if pipeline_type.startswith("1024"):
        return 1024
    return default


@APP.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "backend": "Pixal3D"}


@APP.get("/server_info")
def server_info() -> dict[str, Any]:
    low_vram = _bool_env("PIXAL3D_LOW_VRAM", True)
    resolution = _as_int(os.environ.get("PIXAL3D_RESOLUTION"), 1024 if low_vram else 1536)
    model_path = os.environ.get("PIXAL3D_MODEL_REPO", "TencentARC/Pixal3D")
    weight_format = os.environ.get("PIXAL3D_WEIGHT_FORMAT", "safetensors")
    return {
        "status": "ready",
        "backend": "Pixal3D",
        "model_path": model_path,
        "resolved_model_path": model_path,
        "subfolder": "",
        "enable_tex": True,
        "mesh_retexture": False,
        "enable_t23d": False,
        "texture_only": False,
        "low_vram": low_vram,
        "resolution": resolution,
        "supported_resolutions": [1024, 1536],
        "weight_format": weight_format,
        "quant_repo": os.environ.get("PIXAL3D_QUANT_REPO", "Aero-Ex/Pixal3D-GGUF"),
        "quant": os.environ.get("PIXAL3D_QUANT", "Q5_K_M"),
        "quant_runtime_supported": _bool_env("PIXAL3D_QUANT_RUNTIME_SUPPORTED", False),
        "texture_naf_target_size": _as_int(os.environ.get("PIXAL3D_TEXTURE_NAF_TARGET_SIZE"), 512 if low_vram else 1024),
        "attention_backend": os.environ.get("ATTN_BACKEND", "flash_attn"),
        "sparse_conv_backend": "flex_gemm",
        "model_ready": None,
        "aux_models_ready": None,
        "runtime_distro": os.environ.get("NYMPHS3D_WSL_DISTRO", ""),
        "runtime_user": os.environ.get("NYMPHS3D_WSL_USER", ""),
        "hf_home": os.environ.get("HF_HOME", ""),
        "hf_cache": os.environ.get("HF_HUB_CACHE", ""),
        "torch_home": os.environ.get("TORCH_HOME", ""),
    }


@APP.get("/active_task")
def active_task() -> dict[str, Any]:
    return _task_snapshot()


@APP.post("/generate")
async def generate(request: Request) -> Response:
    payload = await request.json()
    if payload.get("mesh"):
        raise HTTPException(status_code=400, detail="Pixal3D v1 does not support selected-mesh retexture.")

    weight_format = str(payload.get("weight_format") or os.environ.get("PIXAL3D_WEIGHT_FORMAT") or "safetensors")
    if weight_format != "safetensors":
        raise HTTPException(
            status_code=501,
            detail=(
                "Pixal3D GGUF weights can be fetched for adapter testing, but the current "
                "runtime still uses safetensors. GGUF loader support is not implemented yet."
            ),
        )

    image_bytes = _decode_image_payload(str(payload.get("image") or ""))
    low_vram = bool(payload.get("pixal3d_low_vram", _bool_env("PIXAL3D_LOW_VRAM", True)))
    default_resolution = _as_int(os.environ.get("PIXAL3D_RESOLUTION"), 1024 if low_vram else 1536)
    resolution = _resolution_from_payload(payload, default_resolution)
    model_path = str(payload.get("model_path") or os.environ.get("PIXAL3D_MODEL_REPO") or "TencentARC/Pixal3D")
    output_dir = Path(os.environ.get("PIXAL3D_OUTPUT_DIR") or str(Path.home() / "NymphsData" / "outputs" / "pixal3d"))
    output_dir.mkdir(parents=True, exist_ok=True)

    _set_task(
        status="processing",
        stage="initializing",
        detail="Preparing Pixal3D request",
        progress_current=None,
        progress_total=None,
        progress_percent=None,
        message="",
    )

    suffix = ".png"
    with tempfile.NamedTemporaryFile(prefix="pixal3d_input_", suffix=suffix, delete=False) as image_file:
        image_file.write(image_bytes)
        image_path = image_file.name

    output_path = output_dir / f"pixal3d_{int(time.time() * 1000)}.glb"
    try:
        _set_task(stage="generate", detail=f"Running Pixal3D {resolution} cascade")
        from inference import run_inference

        await asyncio.to_thread(
            run_inference,
            image_path=image_path,
            output_path=str(output_path),
            seed=_as_int(payload.get("seed"), 42),
            ss_guidance_strength=_as_float(payload.get("ss_guidance_strength"), 7.5),
            ss_guidance_rescale=_as_float(payload.get("ss_guidance_rescale"), 0.7),
            ss_sampling_steps=_as_int(payload.get("ss_sampling_steps"), 12),
            ss_rescale_t=_as_float(payload.get("ss_rescale_t"), 5.0),
            shape_slat_guidance_strength=_as_float(payload.get("shape_guidance_strength"), 7.5),
            shape_slat_guidance_rescale=_as_float(payload.get("shape_guidance_rescale"), 0.5),
            shape_slat_sampling_steps=_as_int(payload.get("shape_sampling_steps"), 12),
            shape_slat_rescale_t=_as_float(payload.get("shape_rescale_t"), 3.0),
            tex_slat_guidance_strength=_as_float(payload.get("tex_guidance_strength"), 1.0),
            tex_slat_guidance_rescale=_as_float(payload.get("tex_guidance_rescale"), 0.0),
            tex_slat_sampling_steps=_as_int(payload.get("tex_sampling_steps"), 12),
            tex_slat_rescale_t=_as_float(payload.get("tex_rescale_t"), 3.0),
            mesh_scale=_as_float(payload.get("pixal3d_mesh_scale"), 1.0),
            extend_pixel=_as_int(payload.get("pixal3d_extend_pixel"), 0),
            image_resolution=_as_int(payload.get("pixal3d_image_resolution"), 512),
            max_num_tokens=_as_int(payload.get("max_num_tokens"), 49152),
            model_path=model_path,
            manual_fov=_as_float(payload.get("pixal3d_manual_fov"), -1.0),
            low_vram=low_vram,
            resolution=resolution,
            decimation_target=_as_int(payload.get("decimation_target"), 1000000),
            texture_size=_as_int(payload.get("texture_size"), 4096),
            texture_naf_target_size=(
                _as_int(
                    payload.get("pixal3d_texture_naf_target_size")
                    or payload.get("texture_naf_target_size")
                    or os.environ.get("PIXAL3D_TEXTURE_NAF_TARGET_SIZE"),
                    0,
                )
                or None
            ),
            extension_webp=False,
        )
        data = output_path.read_bytes()
        _set_task(status="idle", stage="", detail="", message=f"Saved {output_path}")
        return Response(content=data, media_type="model/gltf-binary")
    except HTTPException:
        _set_task(status="failed", stage="error", detail="Request failed")
        raise
    except Exception as exc:
        _set_task(status="failed", stage="error", detail=str(exc), message=str(exc))
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        try:
            os.unlink(image_path)
        except OSError:
            pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Pixal3D Nymph API server")
    parser.add_argument("--host", default=os.environ.get("PIXAL3D_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PIXAL3D_PORT", "8096")))
    parser.add_argument("--model-path", default=os.environ.get("PIXAL3D_MODEL_REPO", "TencentARC/Pixal3D"))
    parser.add_argument("--resolution", type=int, default=int(os.environ.get("PIXAL3D_RESOLUTION", "1024")))
    parser.add_argument("--low-vram", action="store_true", default=_bool_env("PIXAL3D_LOW_VRAM", True))
    parser.add_argument("--no-low-vram", action="store_false", dest="low_vram")
    parser.add_argument("--weight-format", default=os.environ.get("PIXAL3D_WEIGHT_FORMAT", "safetensors"))
    parser.add_argument("--python-path", default="")
    args = parser.parse_args()

    os.environ["PIXAL3D_MODEL_REPO"] = args.model_path
    os.environ["PIXAL3D_RESOLUTION"] = str(args.resolution)
    os.environ["PIXAL3D_LOW_VRAM"] = "1" if args.low_vram else "0"
    os.environ["PIXAL3D_WEIGHT_FORMAT"] = str(args.weight_format or "safetensors")
    os.environ.setdefault("ATTN_BACKEND", "flash_attn")

    import uvicorn

    uvicorn.run(APP, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
