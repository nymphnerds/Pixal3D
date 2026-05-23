#!/usr/bin/env python3
"""Repeat-run CUDA diagnostics for Pixal3D.

This intentionally runs multiple Pixal3D passes in one Python/CUDA process so
we can bisect the second-run crash that worker isolation avoids in Manager.
Do not use this as the normal user workflow.
"""

from __future__ import annotations

import argparse
import gc
import os
import resource
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import torch
from PIL import Image

import app as pixal_app


STAGE_ORDER = {
    "preprocess": 10,
    "camera": 20,
    "ss": 30,
    "shape-lr": 40,
    "upsample": 50,
    "shape-hr": 60,
    "tex": 70,
    "pack": 80,
    "decode": 90,
    "glb": 100,
}


class Tee:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self._file = path.open("a", encoding="utf-8", buffering=1)
        self.path = path

    def write(self, text: str):
        sys.__stdout__.write(text)
        sys.__stdout__.flush()
        self._file.write(text)
        self._file.flush()

    def flush(self):
        sys.__stdout__.flush()
        self._file.flush()


def _default_log_file() -> Path:
    log_dir = Path(os.path.expanduser(os.environ.get("PIXAL3D_LOG_DIR", "~/NymphsData/logs/pixal3d")))
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return log_dir / f"pixal3d-repeat-diagnostics-{stamp}.log"


def _log(message: str):
    print(message, flush=True)


def _rss_gb() -> float:
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Linux reports KiB here.
    return usage / 1024**2


def _nvidia_summary() -> str:
    smi = shutil_which("nvidia-smi")
    if not smi:
        return "nvidia-smi=missing"
    try:
        result = subprocess.run(
            [
                smi,
                "--query-gpu=memory.used,memory.free,memory.total",
                "--format=csv,noheader,nounits",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=3,
        )
        line = (result.stdout or "").strip().splitlines()[0]
        used, free, total = [int(part.strip()) for part in line.split(",")[:3]]
        return f"gpu_memory=used:{used / 1024:.2f}GB free:{free / 1024:.2f}GB total:{total / 1024:.2f}GB"
    except Exception as exc:
        return f"nvidia-smi=failed:{exc}"


def shutil_which(name: str) -> str | None:
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(directory) / name
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def checkpoint(label: str, *, cleanup: bool = False):
    _log(f"[DIAG] {datetime.now().isoformat(timespec='seconds')} {label} pid={os.getpid()} rss_max={_rss_gb():.2f}GB {_nvidia_summary()}")
    if torch.cuda.is_available():
        try:
            torch.cuda.synchronize()
        except Exception as exc:
            _log(f"[DIAG] cuda synchronize failed at {label}: {exc}")
    pixal_app._cuda_memory_report(f"diag {label}")
    if cleanup:
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            try:
                torch.cuda.ipc_collect()
            except Exception:
                pass
        pixal_app._cuda_memory_report(f"diag {label} after cleanup")


def should_stop(args: argparse.Namespace, stage: str) -> bool:
    return STAGE_ORDER[stage] >= STAGE_ORDER[args.stop_after]


def sampler_params(args: argparse.Namespace):
    ss = {
        "steps": args.ss_steps,
        "guidance_strength": args.ss_guidance,
        "guidance_rescale": args.ss_rescale,
        "rescale_t": args.ss_rescale_t,
    }
    shape = {
        "steps": args.shape_steps,
        "guidance_strength": args.shape_guidance,
        "guidance_rescale": args.shape_rescale,
        "rescale_t": args.shape_rescale_t,
    }
    tex = {
        "steps": args.tex_steps,
        "guidance_strength": args.tex_guidance,
        "guidance_rescale": args.tex_rescale,
        "rescale_t": args.tex_rescale_t,
    }
    return ss, shape, tex


def cleanup_objects(objects: list[Any], label: str):
    for obj in objects:
        pixal_app._clear_sparse_cache(obj, label)
        pixal_app._drop_mesh_tensors(obj)
    del objects
    checkpoint(f"{label} cleanup", cleanup=True)


def run_pass(args: argparse.Namespace, pass_index: int) -> dict[str, Any]:
    label = f"pass {pass_index}"
    _log(f"[DIAG] ===== {label} start =====")
    checkpoint(f"{label} before init", cleanup=args.cleanup_each_stage)

    pixal_app.init_models(
        low_vram=args.low_vram,
        texture_naf_target_size=args.texture_naf_target_size or None,
    )
    pipe = pixal_app.pipeline
    if pipe is None:
        raise RuntimeError("Pixal3D pipeline did not initialize")
    checkpoint(f"{label} after init", cleanup=args.cleanup_each_stage)

    image = Image.open(args.image).convert("RGBA")
    if args.skip_preprocess:
        image_preprocessed = image
        _log(f"[DIAG] {label} preprocess skipped")
    else:
        os.environ["PIXAL3D_REMBG_KEEP_GPU"] = "1" if args.rembg_keep_gpu else "0"
        image_preprocessed = pipe.preprocess_image(image)
    processed_path = pixal_app.TMP_DIR + f"/diag_{os.getpid()}_{pass_index}_{int(time.time() * 1000)}.png"
    image_preprocessed.save(processed_path)
    checkpoint(f"{label} after preprocess", cleanup=args.cleanup_each_stage)
    if should_stop(args, "preprocess"):
        return {"processed_path": processed_path}

    if args.manual_fov > 0:
        camera_angle_x = float(args.manual_fov)
        if args.fov_unit == "deg":
            camera_angle_x = np.deg2rad(camera_angle_x)
        distance = pixal_app.distance_from_fov(
            camera_angle_x,
            torch.tensor([-1.0, 0.0, 0.0]),
            torch.tensor([0 - pixal_app.WILD_EXTEND_PIXEL, pixal_app.WILD_IMAGE_RESOLUTION - 1 + pixal_app.WILD_EXTEND_PIXEL]),
            pixal_app.WILD_MESH_SCALE,
            pixal_app.WILD_IMAGE_RESOLUTION,
        )["distance_from_x"]
        camera_params = {"camera_angle_x": camera_angle_x, "distance": distance, "mesh_scale": pixal_app.WILD_MESH_SCALE}
    else:
        camera_params = pixal_app.get_camera_params_wild_moge(
            processed_path,
            device="cuda",
            mesh_scale=pixal_app.WILD_MESH_SCALE,
            extend_pixel=pixal_app.WILD_EXTEND_PIXEL,
            image_resolution=pixal_app.WILD_IMAGE_RESOLUTION,
        )
    checkpoint(f"{label} after camera", cleanup=args.cleanup_each_stage)
    if should_stop(args, "camera"):
        return {"processed_path": processed_path, "camera_params": camera_params}

    ss_params, shape_params, tex_params = sampler_params(args)
    torch.manual_seed(args.seed + pass_index - 1)
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()

    camera_angle_x = camera_params["camera_angle_x"]
    distance = camera_params["distance"]
    mesh_scale = camera_params.get("mesh_scale", 1.0)
    actual_hr_resolution = int(args.resolution)
    pipeline_type = f"{actual_hr_resolution}_cascade"
    if pipeline_type not in {"1024_cascade", "1536_cascade"}:
        raise ValueError("Diagnostics currently support 1024 or 1536 cascade resolutions")

    with torch.inference_mode():
        cond_ss = pipe.get_proj_cond_ss(
            [image_preprocessed],
            camera_angle_x=camera_angle_x,
            distance=distance,
            mesh_scale=mesh_scale,
        )
        coords = pipe.sample_sparse_structure(cond_ss, 32, 1, ss_params)
        del cond_ss
        checkpoint(f"{label} after sparse structure tokens={coords.shape[0]}", cleanup=args.cleanup_each_stage)
        if should_stop(args, "ss"):
            cleanup_objects([coords], f"{label} stop ss")
            return {"coords": int(coords.shape[0])}

        cond_shape_lr = pipe.get_proj_cond_shape(
            pipe.image_cond_model_shape_512,
            [image_preprocessed],
            coords,
            camera_angle_x=camera_angle_x,
            distance=distance,
            mesh_scale=mesh_scale,
        )
        lr_slat = pipe.sample_shape_slat(
            cond_shape_lr,
            pipe.models["shape_slat_flow_model_512"],
            coords,
            shape_params,
        )
        del cond_shape_lr
        checkpoint(f"{label} after shape LR", cleanup=args.cleanup_each_stage)
        if should_stop(args, "shape-lr"):
            cleanup_objects([lr_slat], f"{label} stop shape-lr")
            return {"coords": int(coords.shape[0])}

        if pipe.low_vram:
            pipe.models["shape_slat_decoder"].to(pipe.device)
            pipe.models["shape_slat_decoder"].low_vram = True
        hr_coords = pipe.models["shape_slat_decoder"].upsample(lr_slat, upsample_times=4)
        if pipe.low_vram:
            pipe.models["shape_slat_decoder"].cpu()
            pipe.models["shape_slat_decoder"].low_vram = False
        checkpoint(f"{label} after shape upsample", cleanup=args.cleanup_each_stage)
        if should_stop(args, "upsample"):
            cleanup_objects([lr_slat], f"{label} stop upsample")
            del hr_coords
            return {"coords": int(coords.shape[0])}

        lr_resolution = 512
        while True:
            grid_res = actual_hr_resolution // 16
            quant_coords = torch.cat([
                hr_coords[:, :1],
                ((hr_coords[:, 1:] + 0.5) / lr_resolution * (grid_res - 1)).round().int(),
            ], dim=1)
            hr_coords_unique = quant_coords.unique(dim=0)
            num_tokens = hr_coords_unique.shape[0]
            if num_tokens < args.max_tokens or actual_hr_resolution == 1024:
                break
            actual_hr_resolution -= 128

        actual_grid_res = actual_hr_resolution // 16
        del lr_slat, hr_coords, quant_coords
        checkpoint(
            f"{label} after HR coord quantization tokens={num_tokens} resolution={actual_hr_resolution}",
            cleanup=args.cleanup_each_stage,
        )

        cond_shape_hr = pipe.get_proj_cond_shape(
            pipe.image_cond_model_shape_1024,
            [image_preprocessed],
            hr_coords_unique,
            camera_angle_x=camera_angle_x,
            distance=distance,
            mesh_scale=mesh_scale,
            grid_resolution_override=actual_grid_res,
        )
        noise_hr = pixal_app.SparseTensor(
            feats=torch.randn(hr_coords_unique.shape[0], pipe.models["shape_slat_flow_model_1024"].in_channels).to(pipe.device),
            coords=hr_coords_unique,
        )
        sampler_params_hr = {**pipe.shape_slat_sampler_params, **shape_params}
        flow_model_hr = pipe.models["shape_slat_flow_model_1024"]
        if pipe.low_vram:
            flow_model_hr.to(pipe.device)
        hr_slat = pipe.shape_slat_sampler.sample(
            flow_model_hr,
            noise_hr,
            **cond_shape_hr,
            **sampler_params_hr,
            verbose=True,
            tqdm_desc=f"Diag sampling HR shape SLat ({actual_hr_resolution})",
        ).samples
        if pipe.low_vram:
            flow_model_hr.cpu()
        std = torch.tensor(pipe.shape_slat_normalization["std"])[None].to(hr_slat.device)
        mean = torch.tensor(pipe.shape_slat_normalization["mean"])[None].to(hr_slat.device)
        shape_slat = hr_slat * std + mean
        del cond_shape_hr, noise_hr, hr_slat, hr_coords_unique
        checkpoint(f"{label} after shape HR", cleanup=args.cleanup_each_stage)
        if should_stop(args, "shape-hr"):
            cleanup_objects([shape_slat], f"{label} stop shape-hr")
            return {"resolution": actual_hr_resolution}

        tex_grid_res = actual_hr_resolution // 16
        cond_tex = pipe.get_proj_cond_shape(
            pipe.image_cond_model_tex_1024,
            [image_preprocessed],
            shape_slat.coords,
            camera_angle_x=camera_angle_x,
            distance=distance,
            mesh_scale=mesh_scale,
            grid_resolution_override=tex_grid_res,
        )
        tex_slat = pipe.sample_tex_slat(
            cond_tex,
            pipe.models["tex_slat_flow_model_1024"],
            shape_slat,
            tex_params,
        )
        del cond_tex
        checkpoint(f"{label} after texture", cleanup=args.cleanup_each_stage)
        if should_stop(args, "tex"):
            cleanup_objects([shape_slat, tex_slat], f"{label} stop tex")
            return {"resolution": actual_hr_resolution}

        state_path = pixal_app.pack_state(shape_slat, tex_slat, actual_hr_resolution)
        checkpoint(f"{label} after state pack {state_path}", cleanup=args.cleanup_each_stage)
        if should_stop(args, "pack"):
            cleanup_objects([shape_slat, tex_slat], f"{label} stop pack")
            return {"state_path": state_path}

        mesh = pipe.decode_latent(shape_slat, tex_slat, actual_hr_resolution)[0]
        checkpoint(f"{label} after decode", cleanup=args.cleanup_each_stage)
        if should_stop(args, "decode"):
            cleanup_objects([shape_slat, tex_slat, mesh], f"{label} stop decode")
            return {"state_path": state_path}

        glb = pixal_app.o_voxel.postprocess.to_glb(
            vertices=mesh.vertices,
            faces=mesh.faces,
            attr_volume=mesh.attrs,
            coords=mesh.coords,
            attr_layout=pipe.pbr_attr_layout,
            grid_size=actual_hr_resolution,
            aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
            decimation_target=args.decimation_target,
            texture_size=args.texture_size,
            remesh=True,
            remesh_band=1,
            remesh_project=0,
            use_tqdm=True,
        )
        rot = np.array([
            [-1, 0, 0, 0],
            [0, 0, -1, 0],
            [0, -1, 0, 0],
            [0, 0, 0, 1],
        ], dtype=np.float64)
        glb.apply_transform(rot)
        out_path = Path(pixal_app.OUTPUT_DIR) / f"pixal3d_diag_{pass_index}_{int(time.time() * 1000)}.glb"
        glb.export(out_path, extension_webp=False)
        checkpoint(f"{label} after GLB export {out_path}", cleanup=args.cleanup_each_stage)
        cleanup_objects([shape_slat, tex_slat, mesh], f"{label} final")
        del glb
        return {"state_path": state_path, "glb_path": str(out_path), "resolution": actual_hr_resolution}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run staged Pixal3D repeat diagnostics in one CUDA process.")
    parser.add_argument("--image", default=str(REPO_ROOT / "assets/images/0_img.png"))
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--stop-after", choices=list(STAGE_ORDER), default="glb")
    parser.add_argument("--low-vram", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--skip-preprocess", action="store_true")
    parser.add_argument("--rembg-keep-gpu", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--resolution", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--ss-steps", type=int, default=12)
    parser.add_argument("--shape-steps", type=int, default=12)
    parser.add_argument("--tex-steps", type=int, default=12)
    parser.add_argument("--ss-guidance", type=float, default=7.5)
    parser.add_argument("--ss-rescale", type=float, default=0.7)
    parser.add_argument("--ss-rescale-t", type=float, default=5.0)
    parser.add_argument("--shape-guidance", type=float, default=7.5)
    parser.add_argument("--shape-rescale", type=float, default=0.5)
    parser.add_argument("--shape-rescale-t", type=float, default=3.0)
    parser.add_argument("--tex-guidance", type=float, default=1.0)
    parser.add_argument("--tex-rescale", type=float, default=0.0)
    parser.add_argument("--tex-rescale-t", type=float, default=3.0)
    parser.add_argument("--manual-fov", type=float, default=-1.0)
    parser.add_argument("--fov-unit", choices=["deg", "rad"], default="deg")
    parser.add_argument("--max-tokens", type=int, default=pixal_app.CASCADE_MAX_NUM_TOKENS)
    parser.add_argument("--texture-naf-target-size", type=int, default=512)
    parser.add_argument("--decimation-target", type=int, default=1_000_000)
    parser.add_argument("--texture-size", type=int, default=1024)
    parser.add_argument("--cleanup-each-stage", action="store_true")
    parser.add_argument("--free-models-between-runs", action="store_true")
    parser.add_argument("--log-file", default=str(_default_log_file()))
    return parser.parse_args()


def main():
    args = parse_args()
    log_path = Path(args.log_file).expanduser().resolve()
    sys.stdout = Tee(log_path)
    sys.stderr = sys.stdout
    _log(f"[DIAG] log_file={log_path}")
    _log(f"[DIAG] repo={REPO_ROOT}")
    _log(f"[DIAG] image={Path(args.image).resolve()}")
    _log(f"[DIAG] stop_after={args.stop_after} repeats={args.repeats} low_vram={args.low_vram}")
    _log(f"[DIAG] torch={torch.__version__} cuda_available={torch.cuda.is_available()} cuda={torch.version.cuda}")
    _log(f"[DIAG] ATTN_BACKEND={os.environ.get('ATTN_BACKEND')} PYTORCH_CUDA_ALLOC_CONF={os.environ.get('PYTORCH_CUDA_ALLOC_CONF')}")
    checkpoint("process start", cleanup=True)

    results = []
    try:
        for index in range(1, args.repeats + 1):
            results.append(run_pass(args, index))
            checkpoint(f"pass {index} complete", cleanup=True)
            if args.free_models_between_runs:
                with pixal_app.init_lock:
                    pixal_app._free_models_locked(f"diagnostic free between pass {index}")
                checkpoint(f"pass {index} after model free", cleanup=True)
        _log(f"[DIAG] completed results={results}")
    except Exception:
        _log("[DIAG] diagnostic run failed with exception")
        traceback.print_exc()
        checkpoint("exception", cleanup=True)
        raise


if __name__ == "__main__":
    main()
