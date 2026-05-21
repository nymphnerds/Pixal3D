#!/usr/bin/env python3
"""Run Pixal3D profiles against one image and write comparable results."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pixal3d_profiles import get_profile, list_profiles, normalize_profile_id


def gpu_memory_mb() -> int | None:
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        return None
    first = result.stdout.strip().splitlines()[0].strip()
    try:
        return int(first)
    except ValueError:
        return None


def run_profile(image: Path, output_dir: Path, profile_id: str, seed: int, manual_fov: float) -> dict:
    from inference import run_inference

    profile = get_profile(profile_id)
    started = time.perf_counter()
    before_mb = gpu_memory_mb()
    output_path = output_dir / f"pixal3d_{profile['id']}_{int(time.time())}.glb"
    record = {
        "profile": profile["id"],
        "label": profile["label"],
        "settings": profile,
        "output_path": str(output_path),
        "seed": seed,
        "started_at": int(time.time()),
        "gpu_memory_before_mb": before_mb,
        "success": False,
    }
    try:
        run_inference(
            image_path=str(image),
            output_path=str(output_path),
            seed=seed,
            ss_sampling_steps=int(profile["ss_sampling_steps"]),
            shape_slat_sampling_steps=int(profile["shape_slat_sampling_steps"]),
            tex_slat_sampling_steps=int(profile["tex_slat_sampling_steps"]),
            max_num_tokens=int(profile["max_num_tokens"]),
            manual_fov=manual_fov,
            low_vram=bool(profile["low_vram"]),
            resolution=int(profile["resolution"]),
            decimation_target=int(profile["decimation_target"]),
            texture_size=int(profile["texture_size"]),
            texture_naf_target_size=int(profile["texture_naf_target_size"]),
            extension_webp=False,
        )
        record["success"] = True
    except Exception as exc:
        record["error"] = str(exc)
        record["traceback"] = traceback.format_exc()
    finally:
        record["elapsed_seconds"] = round(time.perf_counter() - started, 3)
        record["gpu_memory_after_mb"] = gpu_memory_mb()
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark Pixal3D run profiles.")
    parser.add_argument("--image", default="", help="Input image path.")
    parser.add_argument("--output-dir", default=str(Path.home() / "NymphsData" / "outputs" / "pixal3d" / "benchmarks"))
    parser.add_argument("--profiles", nargs="+", default=["preview_16gb", "balanced_16gb"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--manual-fov", type=float, default=-1.0)
    parser.add_argument("--jsonl", default="")
    parser.add_argument("--list-profiles", action="store_true")
    args = parser.parse_args()

    if args.list_profiles:
        print(json.dumps(list_profiles(), indent=2))
        return 0

    if not args.image:
        print("--image is required unless --list-profiles is used.", file=sys.stderr)
        return 2

    image = Path(args.image).expanduser().resolve()
    if not image.is_file():
        print(f"Input image not found: {image}", file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = Path(args.jsonl).expanduser().resolve() if args.jsonl else output_dir / "pixal3d_profile_benchmark.jsonl"

    results = []
    with jsonl_path.open("a", encoding="utf-8") as handle:
        for requested in args.profiles:
            profile_id = normalize_profile_id(requested)
            print(f"[benchmark] running {profile_id}")
            record = run_profile(image, output_dir, profile_id, args.seed, args.manual_fov)
            handle.write(json.dumps(record, sort_keys=True) + "\n")
            handle.flush()
            results.append(record)
            status = "ok" if record["success"] else "failed"
            print(f"[benchmark] {profile_id}: {status}, {record['elapsed_seconds']}s")

    print(json.dumps(results, indent=2))
    return 0 if all(item["success"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
