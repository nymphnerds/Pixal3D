import os
import subprocess
import argparse
import math
import re
import time
import shutil
import cv2
import torch
import numpy as np
import base64
import io
import json
import gc
import traceback
from datetime import datetime
from pathlib import Path
from typing import *
from PIL import Image

import threading
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass

# Lock for model initialization
init_lock = threading.Lock()

os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
os.environ.setdefault("ATTN_BACKEND", "flash_attn")
os.environ["FLEX_GEMM_AUTOTUNE_CACHE_PATH"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'autotune_cache.json')
os.environ["FLEX_GEMM_AUTOTUNER_VERBOSE"] = '1'

try:
    import spaces
except ImportError:
    class _SpacesFallback:
        @staticmethod
        def GPU(*args, **kwargs):
            def decorator(func):
                return func
            return decorator
    spaces = _SpacesFallback()
try:
    from gradio import Server
except ImportError:
    from gradio.routes import App as _GradioApp

    class Server(_GradioApp):
        def api(self):
            def decorator(func):
                return func
            return decorator

        def launch(self, *, server_name="127.0.0.1", server_port=7860, share=False, **kwargs):
            if share:
                print("Pixal3D share links are not supported with this Gradio server backend.")
            import uvicorn

            uvicorn.run(self, host=server_name, port=server_port)
from gradio.data_classes import FileData
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException, UploadFile

from pixal3d.modules.sparse import SparseTensor
from pixal3d.pipelines import Pixal3DImageTo3DPipeline
from pixal3d.renderers import EnvMap
from pixal3d.utils import render_utils
from pixal3d_profiles import get_profile, list_profiles, normalize_profile_id
import o_voxel

# ============================================================================
# Constants & Defaults
# ============================================================================

MAX_SEED = np.iinfo(np.int32).max
OUTPUT_DIR = os.path.abspath(os.path.expanduser(
    os.environ.get("PIXAL3D_OUTPUT_DIR", os.path.join("~", "NymphsData", "outputs", "pixal3d"))
))
TMP_DIR = os.path.abspath(os.path.expanduser(
    os.environ.get("PIXAL3D_TMP_DIR", os.path.join(OUTPUT_DIR, "tmp"))
))
DEFAULT_PROFILE = normalize_profile_id(os.environ.get("PIXAL3D_RUN_PROFILE") or os.environ.get("PIXAL3D_PROFILE"))
DEFAULT_PROFILE_SETTINGS = get_profile(DEFAULT_PROFILE)
DEFAULT_TEXTURE_SIZE = int(os.environ.get("PIXAL3D_TEXTURE_SIZE", str(DEFAULT_PROFILE_SETTINGS["texture_size"])))
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

MODES = [
    {"name": "Normal", "icon": "assets/app/normal.png", "render_key": "normal"},
    {"name": "Clay render", "icon": "assets/app/clay.png", "render_key": "clay"},
    {"name": "Base color", "icon": "assets/app/basecolor.png", "render_key": "base_color"},
    {"name": "HDRI forest", "icon": "assets/app/hdri_forest.png", "render_key": "shaded_forest"},
    {"name": "HDRI sunset", "icon": "assets/app/hdri_sunset.png", "render_key": "shaded_sunset"},
    {"name": "HDRI courtyard", "icon": "assets/app/hdri_courtyard.png", "render_key": "shaded_courtyard"},
]
STEPS = 8

# Cascade parameters
CASCADE_LR_RESOLUTION = 512
CASCADE_MAX_NUM_TOKENS = int(os.environ.get("PIXAL3D_MAX_NUM_TOKENS", str(DEFAULT_PROFILE_SETTINGS["max_num_tokens"])))

# MoGe defaults
MOGE_MODEL_NAME = "Ruicheng/moge-2-vitl"
WILD_MESH_SCALE = 1.0
WILD_EXTEND_PIXEL = 0
WILD_IMAGE_RESOLUTION = 512

# Image Cond Model configs
IMAGE_COND_CONFIGS = {
    "ss": {
        "model_name": "camenduru/dinov3-vitl16-pretrain-lvd1689m",
        "image_size": 512,
        "grid_resolution": 16,
    },
    "shape_512": {
        "model_name": "camenduru/dinov3-vitl16-pretrain-lvd1689m",
        "image_size": 512,
        "grid_resolution": 32,
        "use_naf_upsample": True,
        "naf_target_size": 512,
    },
    "shape_1024": {
        "model_name": "camenduru/dinov3-vitl16-pretrain-lvd1689m",
        "image_size": 1024,
        "grid_resolution": 64,
        "use_naf_upsample": True,
        "naf_target_size": 512,
    },
    "tex_1024": {
        "model_name": "camenduru/dinov3-vitl16-pretrain-lvd1689m",
        "image_size": 1024,
        "grid_resolution": 64,
        "use_naf_upsample": True,
        "naf_target_size": 1024,
    },
}

def resolve_texture_naf_target_size(low_vram: bool, requested: int | None = None) -> int:
    if requested:
        value = requested
    else:
        value = os.environ.get("PIXAL3D_TEXTURE_NAF_TARGET_SIZE")
    if value in (None, ""):
        return 512 if low_vram else 1024
    value = int(value)
    if value not in {512, 768, 1024}:
        raise ValueError(f"Unsupported PIXAL3D_TEXTURE_NAF_TARGET_SIZE: {value}")
    return value

# ============================================================================
# Model Loading
# ============================================================================

def build_image_cond_model(config: dict):
    from pixal3d.trainers.flow_matching.mixins.image_conditioned_proj import DinoV3ProjFeatureExtractor
    model = DinoV3ProjFeatureExtractor(**config)
    model.eval()
    return model

def load_moge_model(device="cuda", model_name=MOGE_MODEL_NAME):
    from moge.model.v2 import MoGeModel
    moge_model = MoGeModel.from_pretrained(model_name).to(device)
    moge_model.eval()
    return moge_model

# Global instances (lazy loaded or loaded at start)
pipeline = None
moge_model = None
envmap = None
LOW_VRAM = os.environ.get("PIXAL3D_LOW_VRAM", os.environ.get("LOW_VRAM", "1" if DEFAULT_PROFILE_SETTINGS["low_vram"] else "0")) == "1"
runtime_settings = {
    "low_vram": None,
    "texture_naf_target_size": None,
}
warmup_lock = threading.Lock()
warmup_state = {
    "status": "idle",
    "stage": "Waiting",
    "step": 0,
    "total": 5,
    "done": False,
    "error": "",
}
warmup_thread_lock = threading.Lock()
warmup_thread = None

def _set_warmup(status: str, stage: str, step: int, total: int = 5, *, done: bool = False, error: str = ""):
    with warmup_lock:
        warmup_state.update({
            "status": status,
            "stage": stage,
            "step": step,
            "total": total,
            "done": done,
            "error": error,
        })

def _warmup_snapshot():
    with warmup_lock:
        return dict(warmup_state)


def _warm_models_worker(low_vram: bool | None = None, texture_naf_target_size: int | None = None):
    try:
        init_models(low_vram=low_vram, texture_naf_target_size=texture_naf_target_size)
    except Exception as exc:
        print(f"[Warmup] Pixal3D model warmup failed: {exc}")


def start_model_warmup(low_vram: bool | None = None, texture_naf_target_size: int | None = None) -> Dict[str, Any]:
    global warmup_thread
    snapshot = _warmup_snapshot()
    if snapshot.get("status") == "loading":
        return snapshot

    if (
        pipeline is not None
        and runtime_settings["low_vram"] == (LOW_VRAM if low_vram is None else bool(low_vram))
        and runtime_settings["texture_naf_target_size"] == resolve_texture_naf_target_size(
            LOW_VRAM if low_vram is None else bool(low_vram),
            texture_naf_target_size,
        )
    ):
        _set_warmup("ready", "Model ready", 5, done=True)
        return _warmup_snapshot()

    _set_warmup("loading", "Starting Pixal3D warmup", 0)
    with warmup_thread_lock:
        if warmup_thread is not None and warmup_thread.is_alive():
            return _warmup_snapshot()
        warmup_thread = threading.Thread(
            target=_warm_models_worker,
            kwargs={
                "low_vram": low_vram,
                "texture_naf_target_size": texture_naf_target_size,
            },
            name="pixal3d-manual-warmup",
            daemon=True,
        )
        warmup_thread.start()
    return _warmup_snapshot()

def configure_cuda_memory_limit():
    raw_value = os.environ.get("PIXAL3D_CUDA_MEMORY_FRACTION")
    if raw_value is None:
        return
    value = raw_value.strip()
    if not value or value in {"0", "1", "1.0"}:
        return
    if not torch.cuda.is_available():
        return
    try:
        fraction = float(value)
    except ValueError:
        print(f"[CUDA] Ignoring invalid PIXAL3D_CUDA_MEMORY_FRACTION={value!r}")
        return
    if not 0 < fraction <= 1:
        print(f"[CUDA] Ignoring out-of-range PIXAL3D_CUDA_MEMORY_FRACTION={fraction}")
        return
    try:
        torch.cuda.set_per_process_memory_fraction(fraction)
        print(f"[CUDA] Per-process memory fraction capped at {fraction:.2f}")
    except Exception as exc:
        print(f"[CUDA] Could not set memory fraction: {exc}")


def _free_models_locked(reason: str = ""):
    global pipeline, moge_model, envmap
    if reason:
        print(f"[Pipeline] Freeing Pixal3D runtime: {reason}")
    pipeline = None
    moge_model = None
    envmap = None
    runtime_settings["low_vram"] = None
    runtime_settings["texture_naf_target_size"] = None
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        try:
            torch.cuda.ipc_collect()
        except Exception:
            pass
    _set_warmup("idle", "Pipeline freed", 0, done=False)


def init_models(low_vram: bool | None = None, texture_naf_target_size: int | None = None, force_reload: bool = False):
    global pipeline, moge_model, envmap
    global LOW_VRAM
    desired_low_vram = LOW_VRAM if low_vram is None else bool(low_vram)
    desired_texture_naf = resolve_texture_naf_target_size(desired_low_vram, texture_naf_target_size)
    with init_lock:
        if (
            pipeline is not None
            and not force_reload
            and runtime_settings["low_vram"] == desired_low_vram
            and runtime_settings["texture_naf_target_size"] == desired_texture_naf
        ):
            _set_warmup("ready", "Model ready", 5, done=True)
            return

        if pipeline is not None:
            _free_models_locked("runtime profile changed")

        try:
            LOW_VRAM = desired_low_vram
            _set_warmup("loading", "Checking GPU", 0)
            configure_cuda_memory_limit()
            # GPU / CUDA Diagnostics (runs when GPU is allocated)
            import subprocess as _sp
            print("=" * 60)
            print("[Diagnostics] PyTorch version:", torch.__version__)
            print("[Diagnostics] CUDA available:", torch.cuda.is_available())
            if torch.cuda.is_available():
                print("[Diagnostics] CUDA version:", torch.version.cuda)
                print("[Diagnostics] cuDNN version:", torch.backends.cudnn.version())
                for i in range(torch.cuda.device_count()):
                    name = torch.cuda.get_device_name(i)
                    cap = torch.cuda.get_device_capability(i)
                    mem = torch.cuda.get_device_properties(i).total_memory / 1024**3
                    print(f"[Diagnostics] GPU {i}: {name}, sm_{cap[0]}{cap[1]}, {mem:.1f} GB")
            try:
                res = _sp.run(["nvidia-smi", "--query-gpu=name,compute_cap,memory.total", "--format=csv,noheader"], capture_output=True, text=True, timeout=10)
                print("[Diagnostics] nvidia-smi:", res.stdout.strip())
            except Exception as e:
                print(f"[Diagnostics] nvidia-smi failed: {e}")
            print("=" * 60)

            model_path = "TencentARC/Pixal3D"
            _set_warmup("loading", "Loading Pixal3D pipeline", 1)
            print(f"[Pipeline] Loading from {model_path}...")
            pipeline = Pixal3DImageTo3DPipeline.from_pretrained(model_path)

            _set_warmup("loading", "Building image conditioners", 2)
            print("[ImageCond] Building DinoV3ProjFeatureExtractor models...")
            tex_naf_target = desired_texture_naf
            IMAGE_COND_CONFIGS["tex_1024"]["naf_target_size"] = tex_naf_target
            print(f"[ImageCond] Texture NAF target size: {tex_naf_target}")
            pipeline.image_cond_model_ss = build_image_cond_model(IMAGE_COND_CONFIGS["ss"])
            pipeline.image_cond_model_shape_512 = build_image_cond_model(IMAGE_COND_CONFIGS["shape_512"])
            pipeline.image_cond_model_shape_1024 = build_image_cond_model(IMAGE_COND_CONFIGS["shape_1024"])
            pipeline.image_cond_model_tex_1024 = build_image_cond_model(IMAGE_COND_CONFIGS["tex_1024"])

            _set_warmup("loading", "Preparing NAF upsamplers", 3)
            if LOW_VRAM:
                # Low-VRAM mode: models stay on CPU, loaded to GPU on-demand per stage.
                print("[NAF] Pre-downloading NAF upsampler weights (CPU only)...")
                for attr in ['image_cond_model_ss', 'image_cond_model_shape_512',
                             'image_cond_model_shape_1024', 'image_cond_model_tex_1024']:
                    m = getattr(pipeline, attr, None)
                    if m is not None and getattr(m, 'use_naf_upsample', False):
                        m._load_naf()
                pipeline._device = torch.device("cuda")
                pipeline.low_vram = True
                print("[Pipeline] Low-VRAM mode enabled.")
            else:
                # Standard mode: all models loaded to GPU at once.
                pipeline.low_vram = False
                pipeline.cuda()
                pipeline.image_cond_model_ss.cuda()
                pipeline.image_cond_model_shape_512.cuda()
                pipeline.image_cond_model_shape_1024.cuda()
                pipeline.image_cond_model_tex_1024.cuda()
                print("[NAF] Pre-loading NAF upsampler model...")
                for attr in ['image_cond_model_ss', 'image_cond_model_shape_512',
                             'image_cond_model_shape_1024', 'image_cond_model_tex_1024']:
                    m = getattr(pipeline, attr, None)
                    if m is not None and getattr(m, 'use_naf_upsample', False):
                        m._load_naf()

            _set_warmup("loading", "Loading MoGe camera model", 4)
            print("[MoGe-2] Loading model for camera estimation...")
            if LOW_VRAM:
                # Low-VRAM: load MoGe to CPU, move to GPU on-demand per request.
                moge_model = load_moge_model(device="cpu")
                print("[MoGe-2] Low-VRAM mode: MoGe stays on CPU, loaded to GPU on-demand.")
            else:
                moge_model = load_moge_model(device="cuda")

            _set_warmup("loading", "Loading environment maps", 5)
            print("[EnvMap] Loading environment maps...")
            _base = os.path.dirname(os.path.abspath(__file__))
            _envmap_device = 'cpu' if LOW_VRAM else 'cuda'
            envmap = {
                'forest': EnvMap(torch.tensor(cv2.cvtColor(cv2.imread(os.path.join(_base, 'assets/hdri/forest.exr'), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGR2RGB), dtype=torch.float32, device=_envmap_device)),
                'sunset': EnvMap(torch.tensor(cv2.cvtColor(cv2.imread(os.path.join(_base, 'assets/hdri/sunset.exr'), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGR2RGB), dtype=torch.float32, device=_envmap_device)),
                'courtyard': EnvMap(torch.tensor(cv2.cvtColor(cv2.imread(os.path.join(_base, 'assets/hdri/courtyard.exr'), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGR2RGB), dtype=torch.float32, device=_envmap_device)),
            }
            runtime_settings["low_vram"] = LOW_VRAM
            runtime_settings["texture_naf_target_size"] = tex_naf_target
            _set_warmup("ready", "Model ready", 5, done=True)
        except Exception as exc:
            _set_warmup("error", "Model preload failed", 0, done=True, error=str(exc))
            raise

def delayed_init_models(delay_seconds: float):
    if delay_seconds > 0:
        time.sleep(delay_seconds)
    if pipeline is None:
        init_models()

# ============================================================================
# Utilities
# ============================================================================

def compute_f_pixels(camera_angle_x: float, resolution: int) -> float:
    focal_length = 16.0 / torch.tan(torch.tensor(camera_angle_x / 2.0))
    f_pixels = focal_length * resolution / 32.0
    return float(f_pixels.item())

def distance_from_fov(camera_angle_x, grid_point, target_point, mesh_scale, image_resolution):
    rotation_matrix = torch.tensor([[1.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0]])
    gp = grid_point.to(torch.float32) @ rotation_matrix.T
    gp = gp / mesh_scale / 2
    xw, yw, zw = gp[0].item(), gp[1].item(), gp[2].item()
    xt, yt = float(target_point[0].item()), float(target_point[1].item())
    f_pixels = compute_f_pixels(camera_angle_x, image_resolution)
    x_ndc = xt - image_resolution / 2.0
    y_ndc = -(yt - image_resolution / 2.0)
    distance_x = f_pixels * xw / x_ndc - yw
    return {"distance_from_x": float(distance_x), "f_pixels": float(f_pixels)}

def get_camera_params_wild_moge(image_path, device="cuda", mesh_scale=1.0, extend_pixel=0, image_resolution=512):
    pil_image = Image.open(image_path).convert("RGB")
    width, height = pil_image.size
    image_np = np.array(pil_image).astype(np.float32) / 255.0
    image_tensor = torch.from_numpy(image_np).permute(2, 0, 1).to(device)
    if LOW_VRAM:
        moge_model.to(device)
    with torch.no_grad():
        output = moge_model.infer(image_tensor)
    if LOW_VRAM:
        moge_model.cpu()
        torch.cuda.empty_cache()
    intrinsics = output["intrinsics"].squeeze().cpu().numpy()
    fx_normalized = intrinsics[0, 0]
    fx = fx_normalized * width
    camera_angle_x = 2 * math.atan(width / (2 * fx))

    grid_point = torch.tensor([-1.0, 0.0, 0.0])
    distance = distance_from_fov(
        camera_angle_x, grid_point,
        torch.tensor([0 - extend_pixel, image_resolution - 1 + extend_pixel]),
        mesh_scale, image_resolution
    )["distance_from_x"]
    return {'camera_angle_x': camera_angle_x, 'distance': distance, 'mesh_scale': mesh_scale}

def pack_state(shape_slat, tex_slat, res):
    state_data = {
        'shape_slat_feats': shape_slat.feats.cpu().numpy(),
        'tex_slat_feats': tex_slat.feats.cpu().numpy(),
        'coords': shape_slat.coords.cpu().numpy(),
        'res': res,
    }
    import random
    state_path = os.path.join(TMP_DIR, f"state_{int(time.time()*1000)}_{random.randint(0,9999):04d}.npz")
    np.savez_compressed(state_path, **state_data)
    return state_path

def unpack_state(state_path):
    data = np.load(state_path)
    shape_slat = SparseTensor(
        feats=torch.from_numpy(data['shape_slat_feats']).cuda(),
        coords=torch.from_numpy(data['coords']).cuda(),
    )
    tex_slat = shape_slat.replace(torch.from_numpy(data['tex_slat_feats']).cuda())
    return shape_slat, tex_slat, int(data['res'])

# ============================================================================
# Progress Tracking (file-based, cross-process safe for @spaces.GPU)
# ============================================================================

import asyncio
from fastapi.responses import JSONResponse
from fastapi import Request

PROGRESS_DIR = os.path.join(TMP_DIR, '_progress')
os.makedirs(PROGRESS_DIR, exist_ok=True)
PREPROCESSED_DIR = os.path.join(TMP_DIR, '_preprocessed')
os.makedirs(PREPROCESSED_DIR, exist_ok=True)

_thread_local = threading.local()

def _safe_session_id(session_id: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id or "")
    return cleaned[:96] or "default"

def _preprocessed_file(session_id: str) -> str:
    return os.path.join(PREPROCESSED_DIR, f"{_safe_session_id(session_id)}.png")

def _progress_file(session_id: str) -> str:
    """Return path to a session's progress JSON file."""
    return os.path.join(PROGRESS_DIR, f"{session_id}.json")

def _reset_progress(session_id: str):
    _thread_local.active_session = session_id
    _write_progress_file(session_id, {"stage": "Queued for Pixal3D worker", "step": 0, "total": 0, "done": False})

def _update_progress(stage: str, step: int, total: int):
    session_id = getattr(_thread_local, 'active_session', '')
    if session_id:
        _write_progress_file(session_id, {"stage": stage, "step": step, "total": total, "done": False})

def _finish_progress():
    session_id = getattr(_thread_local, 'active_session', '')
    if session_id:
        _write_progress_file(session_id, {"done": True})

def _write_progress_file(session_id: str, data: dict):
    """Atomically write progress JSON to a file (cross-process safe)."""
    path = _progress_file(session_id)
    tmp_path = path + ".tmp"
    try:
        with open(tmp_path, 'w') as f:
            json.dump(data, f)
        os.replace(tmp_path, path)  # atomic on POSIX
    except Exception:
        pass

# Monkey-patch tqdm to intercept progress
import tqdm as _tqdm_module

_original_tqdm = _tqdm_module.tqdm

class _TqdmProgressInterceptor(_original_tqdm):
    """Wraps tqdm to push progress updates to SSE."""
    def __init__(self, *args, **kwargs):
        self._stage_desc = kwargs.get('desc', 'Processing')
        super().__init__(*args, **kwargs)
    
    def set_description(self, desc=None, refresh=True):
        self._stage_desc = desc or 'Processing'
        super().set_description(desc, refresh)
    
    def update(self, n=1):
        super().update(n)
        _update_progress(self._stage_desc, self.n, self.total or 0)

# Patch tqdm globally
_tqdm_module.tqdm = _TqdmProgressInterceptor
# Also patch the direct import in the sampler module and render_utils
import pixal3d.pipelines.samplers.flow_euler as _fe_module
_fe_module.tqdm = _TqdmProgressInterceptor
import pixal3d.utils.render_utils as _ru_module
_ru_module.tqdm = _TqdmProgressInterceptor
import o_voxel.postprocess as _ovp_module
_ovp_module.tqdm = _TqdmProgressInterceptor

# ============================================================================
# API Implementation
# ============================================================================

app = Server()

@app.get("/")
async def homepage():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nymph_pixal3d.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/nymph")
async def nymph_homepage():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nymph_pixal3d.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/official")
async def official_homepage():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nymph_pixal3d.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/app_config")
async def get_config():
    """Return server configuration for frontend (e.g. LOW_VRAM mode)."""
    active_profile = get_profile(DEFAULT_PROFILE)
    return JSONResponse({
        "low_vram": LOW_VRAM,
        "output_dir": OUTPUT_DIR,
        "texture_size": DEFAULT_TEXTURE_SIZE,
        "texture_naf_target_size": resolve_texture_naf_target_size(LOW_VRAM),
        "run_profile": active_profile["id"],
        "optimization_profiles": list_profiles(),
        "max_num_tokens": CASCADE_MAX_NUM_TOKENS,
        "decimation_target": active_profile["decimation_target"],
        "profile": os.environ.get("PIXAL3D_PROFILE", "low_vram_1024"),
        "weight_format": os.environ.get("PIXAL3D_WEIGHT_FORMAT", "safetensors"),
        "gguf_quant": os.environ.get("PIXAL3D_QUANT", "Q5_K_M"),
        "gguf_supported": os.environ.get("PIXAL3D_QUANT_RUNTIME_SUPPORTED", "0") == "1",
        "rembg_keep_gpu": os.environ.get("PIXAL3D_REMBG_KEEP_GPU", "0") == "1",
        "cuda_memory_fraction": os.environ.get("PIXAL3D_CUDA_MEMORY_FRACTION", ""),
    })

@app.get("/progress")
async def progress_poll(request: Request):
    """Polling endpoint for real-time progress updates during generation."""
    session_id = request.query_params.get("session_id", "")
    path = _progress_file(session_id)
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        return JSONResponse(data)
    except (FileNotFoundError, json.JSONDecodeError):
        return JSONResponse({"stage": "Queued for Pixal3D worker", "step": 0, "total": 0, "done": False})

@app.get("/warmup_status")
async def warmup_status():
    return JSONResponse(_warmup_snapshot())


@app.post("/api/warmup")
async def warmup_nymph_api(request: Request):
    payload = await request.json()
    snapshot = start_model_warmup(
        low_vram=_as_bool(payload.get("low_vram"), LOW_VRAM),
        texture_naf_target_size=int(payload.get("texture_naf_target_size") or 0),
    )
    return JSONResponse({"data": [snapshot]})


def _file_url(path: str) -> str:
    resolved = os.path.abspath(path)
    for root, prefix in ((TMP_DIR, "/tmp"), (OUTPUT_DIR, "/outputs")):
        root_abs = os.path.abspath(root)
        try:
            rel = os.path.relpath(resolved, root_abs)
        except ValueError:
            continue
        if rel != os.pardir and not rel.startswith(os.pardir + os.sep):
            return f"{prefix}/{rel.replace(os.sep, '/')}"
    return f"/tmp/{os.path.basename(resolved)}"


def _file_response(path: str) -> Dict[str, str]:
    return {"path": os.path.abspath(path), "url": _file_url(path)}


def _file_path(file: Any) -> str:
    if isinstance(file, dict):
        return str(file["path"])
    return str(file.path)


def _as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


async def _request_payload(request: Request) -> Dict[str, Any]:
    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" not in content_type:
        return await request.json()

    form = await request.form()
    payload: Dict[str, Any] = {}
    for key, value in form.multi_items():
        if isinstance(value, UploadFile) or (hasattr(value, "filename") and hasattr(value, "read")):
            suffix = Path(value.filename or "upload.png").suffix or ".png"
            out_path = os.path.join(TMP_DIR, f"upload_{int(time.time() * 1000)}{suffix}")
            data = await value.read()
            with open(out_path, "wb") as f:
                f.write(data)
            payload[key] = {"path": out_path}
        else:
            payload[key] = value
    return payload


def _payload_file(payload: Dict[str, Any]) -> FileData:
    image = payload.get("image") or {}
    if isinstance(image, dict):
        path = image.get("path")
    else:
        path = None
    if not path:
        path = payload.get("image_path")
    if not path:
        raise ValueError("Missing image path")
    return FileData(path=os.path.abspath(str(path)))


@app.post("/api/preprocess")
async def preprocess_nymph_api(request: Request):
    payload = await _request_payload(request)
    try:
        result = preprocess(
            image=_payload_file(payload),
            rembg_keep_gpu=_as_bool(payload.get("rembg_keep_gpu")),
            session_id=str(payload.get("session_id") or ""),
            low_vram=_as_bool(payload.get("low_vram"), True),
            texture_naf_target_size=int(payload.get("texture_naf_target_size") or 0),
        )
        return JSONResponse({"data": [_file_response(_file_path(result))]})
    except Exception as exc:
        print("[NymphUI] Source preprocessing failed:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc) or exc.__class__.__name__) from exc


@app.post("/api/generate_3d")
async def generate_3d_nymph_api(request: Request):
    payload = await _request_payload(request)
    result = generate_3d(
        image=_payload_file(payload),
        seed=int(payload.get("seed") or 42),
        resolution=int(payload.get("resolution") or 1024),
        ss_guidance_strength=float(payload.get("ss_guidance_strength") or 7.5),
        ss_guidance_rescale=float(payload.get("ss_guidance_rescale") or 0.7),
        ss_sampling_steps=int(payload.get("ss_sampling_steps") or 12),
        ss_rescale_t=float(payload.get("ss_rescale_t") or 5.0),
        shape_slat_guidance_strength=float(payload.get("shape_slat_guidance_strength") or 7.5),
        shape_slat_guidance_rescale=float(payload.get("shape_slat_guidance_rescale") or 0.5),
        shape_slat_sampling_steps=int(payload.get("shape_slat_sampling_steps") or 12),
        shape_slat_rescale_t=float(payload.get("shape_slat_rescale_t") or 3.0),
        tex_slat_guidance_strength=float(payload.get("tex_slat_guidance_strength") or 1.0),
        tex_slat_guidance_rescale=float(payload.get("tex_slat_guidance_rescale") or 0.0),
        tex_slat_sampling_steps=int(payload.get("tex_slat_sampling_steps") or 12),
        tex_slat_rescale_t=float(payload.get("tex_slat_rescale_t") or 3.0),
        manual_fov=float(payload.get("manual_fov") or -1.0),
        fov_unit=str(payload.get("fov_unit") or "deg"),
        source_preprocessed=_as_bool(payload.get("source_preprocessed"), True),
        session_id=str(payload.get("session_id") or ""),
        profile_id=str(payload.get("profile_id") or "balanced_16gb"),
        low_vram=_as_bool(payload.get("low_vram"), True),
        max_num_tokens=int(payload.get("max_num_tokens") or CASCADE_MAX_NUM_TOKENS),
        texture_naf_target_size=int(payload.get("texture_naf_target_size") or 0),
    )
    result["render_paths"] = {
        mode: [_file_response(_file_path(file)) for file in files]
        for mode, files in result.get("render_paths", {}).items()
    }
    return JSONResponse({"data": [result]})


@app.post("/api/extract_glb_api")
async def extract_glb_nymph_api(request: Request):
    payload = await request.json()
    result = extract_glb_api(
        state_path=str(payload.get("state_path") or ""),
        decimation_target=int(payload.get("decimation_target") or 1000000),
        texture_size=int(payload.get("texture_size") or DEFAULT_TEXTURE_SIZE),
        session_id=str(payload.get("session_id") or ""),
    )
    return JSONResponse({"data": [_file_response(_file_path(result))]})


@app.post("/api/free_pipeline_api")
async def free_pipeline_nymph_api(request: Request):
    payload = await request.json()
    return JSONResponse({"data": [free_pipeline_api(session_id=str(payload.get("session_id") or ""))]})


@app.api()
@spaces.GPU(duration=30)
def preprocess(
    image: FileData,
    rembg_keep_gpu: bool = False,
    session_id: str = "",
    low_vram: bool = True,
    texture_naf_target_size: int = 0,
) -> FileData:
    _reset_progress(session_id)
    _update_progress("Loading Pixal3D models", 0, 3)
    init_models(
        low_vram=bool(low_vram),
        texture_naf_target_size=int(texture_naf_target_size) or None,
    )
    _update_progress("Preprocessing source image", 1, 3)
    img = Image.open(image["path"])
    os.environ["PIXAL3D_REMBG_KEEP_GPU"] = "1" if rembg_keep_gpu else "0"
    processed = pipeline.preprocess_image(img)
    _update_progress("Saving preprocessed image", 2, 3)
    out_path = _preprocessed_file(session_id) if session_id else os.path.join(TMP_DIR, f"preprocessed_{int(time.time()*1000)}.png")
    processed.save(out_path)
    _finish_progress()
    return FileData(path=out_path)

@app.api()
@spaces.GPU(duration=120)
def generate_3d(
    image: FileData, 
    seed: int, 
    resolution: int,
    ss_guidance_strength: float = 7.5,
    ss_guidance_rescale: float = 0.7,
    ss_sampling_steps: int = 12,
    ss_rescale_t: float = 5.0,
    shape_slat_guidance_strength: float = 7.5,
    shape_slat_guidance_rescale: float = 0.5,
    shape_slat_sampling_steps: int = 12,
    shape_slat_rescale_t: float = 3.0,
    tex_slat_guidance_strength: float = 1.0,
    tex_slat_guidance_rescale: float = 0.0,
    tex_slat_sampling_steps: int = 12,
    tex_slat_rescale_t: float = 3.0,
    manual_fov: float = -1.0,
    fov_unit: str = "deg",
    source_preprocessed: bool = True,
    session_id: str = "",
    profile_id: str = "balanced_16gb",
    low_vram: bool = True,
    max_num_tokens: int = CASCADE_MAX_NUM_TOKENS,
    texture_naf_target_size: int = 0,
) -> Dict:
    _reset_progress(session_id)
    _update_progress("Loading Pixal3D models", 0, 8)
    active_profile = get_profile(profile_id)
    effective_low_vram = bool(low_vram)
    effective_texture_naf = int(texture_naf_target_size or active_profile["texture_naf_target_size"])
    effective_max_tokens = int(max_num_tokens or active_profile["max_num_tokens"])
    init_models(
        low_vram=effective_low_vram,
        texture_naf_target_size=effective_texture_naf,
    )
    
    torch.manual_seed(seed)
    hr_resolution = int(resolution)
    
    if source_preprocessed:
        _update_progress("Using preprocessed source image", 1, 8)
    else:
        _update_progress("Using original source image", 1, 8)
    image_preprocessed = Image.open(image["path"]).convert("RGBA")
    _update_progress("Saving prepared image", 2, 8)
    temp_processed_path = os.path.join(TMP_DIR, f"temp_proc_{session_id[:8]}_{int(time.time()*1000)}.png")
    image_preprocessed.save(temp_processed_path)
    
    if manual_fov > 0:
        _update_progress("Using manual camera FOV", 3, 8)
        # Convert to radians based on unit
        if fov_unit == "rad":
            camera_angle_x = float(manual_fov)
            fov_deg = math.degrees(manual_fov)
        else:
            camera_angle_x = math.radians(manual_fov)
            fov_deg = float(manual_fov)
        grid_point = torch.tensor([-1.0, 0.0, 0.0])
        distance = distance_from_fov(
            camera_angle_x, grid_point,
            torch.tensor([0 - WILD_EXTEND_PIXEL, WILD_IMAGE_RESOLUTION - 1 + WILD_EXTEND_PIXEL]),
            WILD_MESH_SCALE, WILD_IMAGE_RESOLUTION
        )["distance_from_x"]
        camera_params = {'camera_angle_x': camera_angle_x, 'distance': distance, 'mesh_scale': WILD_MESH_SCALE}
        print(f"[Camera] Using manual FOV: {fov_deg:.2f}° ({camera_angle_x:.4f} rad), distance: {distance:.4f}")
    else:
        _update_progress("Estimating camera with MoGe", 3, 8)
        camera_params = get_camera_params_wild_moge(
            temp_processed_path, device="cuda",
            mesh_scale=WILD_MESH_SCALE, extend_pixel=WILD_EXTEND_PIXEL,
            image_resolution=WILD_IMAGE_RESOLUTION,
        )
    _update_progress("Camera ready", 4, 8)
    
    ss_sampler_override = {"steps": ss_sampling_steps, "guidance_strength": ss_guidance_strength,
                           "guidance_rescale": ss_guidance_rescale, "rescale_t": ss_rescale_t}
    shape_sampler_override = {"steps": shape_slat_sampling_steps, "guidance_strength": shape_slat_guidance_strength,
                              "guidance_rescale": shape_slat_guidance_rescale, "rescale_t": shape_slat_rescale_t}
    tex_sampler_override = {"steps": tex_slat_sampling_steps, "guidance_strength": tex_slat_guidance_strength,
                            "guidance_rescale": tex_slat_guidance_rescale, "rescale_t": tex_slat_rescale_t}

    pipeline_type = f"{hr_resolution}_cascade"
    _update_progress("Sampling structure, shape, and texture", 5, 8)
    mesh_list, (shape_slat, tex_slat, res) = pipeline.run(
        image_preprocessed,
        camera_params=camera_params,
        seed=seed,
        sparse_structure_sampler_params=ss_sampler_override,
        shape_slat_sampler_params=shape_sampler_override,
        tex_slat_sampler_params=tex_sampler_override,
        preprocess_image=False,
        return_latent=True,
        pipeline_type=pipeline_type,
        max_num_tokens=effective_max_tokens,
    )
    
    mesh = mesh_list[0]
    _update_progress("Packing latent preview state", 6, 8)
    state_path = pack_state(shape_slat, tex_slat, res)
    
    _update_progress("Rendering preview frames", 7, 8)
    mesh.simplify(16777216)
    cam_dist = camera_params['distance']
    near = max(0.01, cam_dist - 2.0)
    far = cam_dist + 10.0
    if LOW_VRAM:
        for v in envmap.values():
            v.image = v.image.cuda()
            if hasattr(v, '_nvdiffrec_envlight'):
                del v._nvdiffrec_envlight
    renders = render_utils.render_proj_aligned_video(
        mesh, camera_angle_x=camera_params['camera_angle_x'],
        distance=cam_dist, resolution=1024,
        num_frames=STEPS, envmap=envmap,
        near=near, far=far,
    )
    if LOW_VRAM:
        for v in envmap.values():
            if hasattr(v, '_nvdiffrec_envlight'):
                del v._nvdiffrec_envlight
            v.image = v.image.cpu()
        torch.cuda.empty_cache()
    _update_progress("Saving preview frames", 8, 8)
    
    # Save renders and return paths
    render_files = {}
    for mode_key, frames in renders.items():
        mode_files = []
        for i, frame in enumerate(frames):
            p = os.path.abspath(os.path.join(TMP_DIR, f"render_{mode_key}_{i}_{int(time.time()*1000)}.jpg"))
            Image.fromarray(frame).save(p, quality=85)
            mode_files.append(FileData(path=p))
        render_files[mode_key] = mode_files

    _finish_progress()
    return {
        "render_paths": render_files,
        "state_path": os.path.abspath(state_path),
        "camera_angle_x": camera_params['camera_angle_x'],
        "distance": camera_params['distance'],
    }

@app.api()
@spaces.GPU(duration=240)
def extract_glb_api(state_path: str, decimation_target: int, texture_size: int, session_id: str = "") -> FileData:
    _reset_progress(session_id)
    _update_progress("Loading Pixal3D models", 0, 4)
    init_models()
    _update_progress("Decoding latent mesh", 1, 4)
    
    shape_slat, tex_slat, res = unpack_state(state_path)
    mesh = pipeline.decode_latent(shape_slat, tex_slat, res)[0]
    _update_progress("Building GLB mesh and textures", 2, 4)
    
    glb = o_voxel.postprocess.to_glb(
        vertices=mesh.vertices, faces=mesh.faces, attr_volume=mesh.attrs,
        coords=mesh.coords, attr_layout=pipeline.pbr_attr_layout,
        grid_size=res, aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
        decimation_target=decimation_target, texture_size=texture_size,
        remesh=True, remesh_band=1, remesh_project=0, use_tqdm=True,
    )
    rot = np.array([
        [-1,  0,  0,  0],
        [ 0,  0, -1,  0],
        [ 0, -1,  0,  0],
        [ 0,  0,  0,  1],
    ], dtype=np.float64)
    glb.apply_transform(rot)
    
    _update_progress("Exporting GLB file", 3, 4)
    out_glb = os.path.join(OUTPUT_DIR, f"pixal3d_app_{int(time.time()*1000)}.glb")
    glb.export(out_glb, extension_webp=False)
    _finish_progress()
    return FileData(path=out_glb)


@app.api()
def free_pipeline_api(session_id: str = "") -> Dict:
    _reset_progress(session_id)
    _update_progress("Freeing Pixal3D pipeline", 1, 1)
    with init_lock:
        _free_models_locked("manual frontend request")
    _finish_progress()
    return {"freed": True}

# Mount assets and tmp for direct access
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.mount("/tmp", StaticFiles(directory=TMP_DIR), name="tmp")
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

def ensure_utils3d_moge_aliases():
    import importlib
    import utils3d

    missing = []
    for alias_name in ("pt", "np"):
        try:
            importlib.import_module(f"utils3d.{alias_name}")
        except ModuleNotFoundError:
            missing.append(alias_name)

    if missing:
        importlib.import_module("utils3d.torch")
        importlib.import_module("utils3d.numpy")
        package_root = Path(utils3d.__file__).resolve().parent
        if "pt" in missing:
            (package_root / "pt.py").write_text("from .torch import *\n", encoding="utf-8")
        if "np" in missing:
            (package_root / "np.py").write_text("from .numpy import *\n", encoding="utf-8")
        importlib.invalidate_caches()

    utils3d_torch = importlib.import_module("utils3d.torch")
    if not hasattr(utils3d_torch, "intrinsics_from_fov_xy"):
        raise RuntimeError("Installed utils3d is missing intrinsics_from_fov_xy")
    importlib.import_module("utils3d.pt")
    importlib.import_module("utils3d.np")


if __name__ == "__main__":
    import sys
    parser = argparse.ArgumentParser(description="Pixal3D Demo Server")
    parser.add_argument("--low_vram", "--low-vram", action="store_true", default=None,
                        help="Enable low-VRAM mode: models lazy-load to GPU per stage.")
    parser.add_argument("--no-low-vram", action="store_false", dest="low_vram")
    parser.add_argument("--host", default=os.environ.get("GRADIO_SERVER_NAME", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("GRADIO_SERVER_PORT", "8097")))
    parser.add_argument("--share", action="store_true", help="Enable Gradio share link.")
    parser.add_argument("--lazy-load", action="store_true", help="Start the UI before loading models.")
    parser.add_argument("--warm-on-start", action="store_true", help="Start the UI immediately and initialize models in the background.")
    parser.add_argument("--warmup-delay", type=float, default=float(os.environ.get("PIXAL3D_WARMUP_DELAY", "0")),
                        help="Start model preload after this many seconds; 0 disables delayed preload unless --warm-on-start is set.")
    parser.add_argument("--reinstall-utils3d", action="store_true", help="Reinstall upstream utils3d wheel before launch.")
    args, remaining = parser.parse_known_args()
    if args.low_vram is not None:
        LOW_VRAM = bool(args.low_vram)

    if args.reinstall_utils3d or os.environ.get("PIXAL3D_REINSTALL_UTILS3D") == "1":
        subprocess.run([
            sys.executable, "-m", "pip", "install", "--force-reinstall", "--no-deps",
            "https://github.com/LDYang694/Storages/releases/download/20260430/utils3d-0.0.2-py3-none-any.whl"
        ], check=True)
        ensure_utils3d_moge_aliases()
    
    if args.warm_on_start:
        start_model_warmup()
    elif args.lazy_load and args.warmup_delay > 0:
        threading.Thread(target=delayed_init_models, args=(args.warmup_delay,), name="pixal3d-model-delayed-warmup", daemon=True).start()
    elif not args.lazy_load:
        init_models()
    
    app.launch(
        show_error=True,
        share=args.share,
        server_name=args.host,
        server_port=args.port,
        allowed_paths=[TMP_DIR, OUTPUT_DIR],
    )
