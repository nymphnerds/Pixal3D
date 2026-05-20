#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_pixal3d_common.sh"

quant="${PIXAL3D_QUANT:-Q5_K_M}"
license_ack="no"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --quant)
      quant="${2:-}"
      shift 2
      ;;
    --quant=*)
      quant="${1#*=}"
      shift
      ;;
    --license-ack|--license_ack)
      license_ack="${2:-no}"
      shift 2
      ;;
    --license-ack=*|--license_ack=*)
      license_ack="${1#*=}"
      shift
      ;;
    --hf-token|--hf_token)
      export NYMPHS3D_HF_TOKEN="${2:-}"
      shift 2
      ;;
    --hf-token=*|--hf_token=*)
      export NYMPHS3D_HF_TOKEN="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 2
      ;;
  esac
done

if [[ "${license_ack}" != "yes" ]]; then
  cat >&2 <<'EOF'
LICENSE ACK REQUIRED:
This experimental fetch downloads community GGUF conversions of Pixal3D weights.
Pixal3D remains academic-only, not licensed for commercial or production use,
and its LICENSE says it is not intended for use within the European Union.
Rerun after selecting the license/access acknowledgement in the action form.
EOF
  exit 2
fi

case "${quant}" in
  Q5_K_M|Q6_K|Q8_0)
    ;;
  *)
    echo "Unsupported Pixal3D GGUF quant: ${quant}" >&2
    echo "Supported values: Q5_K_M, Q6_K, Q8_0" >&2
    exit 2
    ;;
esac

if [[ ! -x "$(pixal3d_python)" ]]; then
  echo "Pixal3D runtime is missing. Run scripts/install_pixal3d.sh first." >&2
  exit 1
fi

pixal3d_ensure_data_dirs
fetch_lock="${PIXAL3D_CONFIG_DIR}/fetch_quantized_models.lock"
exec 9>"${fetch_lock}"
if ! flock -n 9; then
  echo "MODEL FETCH STATUS: Pixal3D GGUF fetch is already running; using existing fetch lock at ${fetch_lock}."
  echo "Pixal3D quantized weight fetch is already running."
  exit 0
fi

pixal3d_load_hf_token
if [[ -n "${NYMPHS3D_HF_TOKEN:-}" ]]; then
  export HF_TOKEN="${NYMPHS3D_HF_TOKEN}"
  export HUGGING_FACE_HUB_TOKEN="${NYMPHS3D_HF_TOKEN}"
fi

cat > "${PIXAL3D_CONFIG_DIR}/quantized.env" <<EOF
PIXAL3D_WEIGHT_FORMAT=gguf-experimental
PIXAL3D_QUANT_REPO=${PIXAL3D_QUANT_REPO}
PIXAL3D_QUANT=${quant}
PIXAL3D_QUANT_RUNTIME_SUPPORTED=0
EOF

echo "MODEL FETCH STARTED: Pixal3D GGUF ${quant} from ${PIXAL3D_QUANT_REPO} into ${NYMPHS3D_HF_CACHE_DIR}."

"$(pixal3d_python)" - "${quant}" <<'PY'
import os
import sys
import threading
from pathlib import Path

from huggingface_hub import snapshot_download

quant = sys.argv[1]
repo_id = os.environ.get("PIXAL3D_QUANT_REPO", "Aero-Ex/Pixal3D-GGUF")
cache_dir = os.environ.get("NYMPHS3D_HF_CACHE_DIR")
token = os.environ.get("NYMPHS3D_HF_TOKEN") or os.environ.get("HF_TOKEN") or None

allow_patterns = [
    "README.md",
    "pipeline.json",
    f"Sparse/*_{quant}.gguf",
    "Sparse/*.json",
    f"shape/*_{quant}.gguf",
    "shape/*.json",
    f"texture/*_{quant}.gguf",
    "texture/*.json",
    "decoder/*.json",
    "decoder/*.safetensors",
]

required_files = [
    f"Sparse/ss_flow_img_dit_1_3B_64_bf16_{quant}.gguf",
    f"shape/slat_flow_img2shape_dit_1_3B_512_bf16_{quant}.gguf",
    f"shape/slat_flow_img2shape_dit_1_3B_1024_bf16_{quant}.gguf",
    f"texture/slat_flow_imgshape2tex_dit_1_3B_1024_bf16_{quant}.gguf",
    "decoder/ss_dec_conv3d_16l8_fp16.safetensors",
    "decoder/shape_dec_next_dc_f16c32_fp16.safetensors",
    "decoder/tex_dec_next_dc_f16c32_fp16.safetensors",
    "pipeline.json",
]


def format_bytes(size: int) -> str:
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    value = float(max(0, size))
    unit = 0
    while value >= 1024 and unit < len(units) - 1:
        value /= 1024
        unit += 1
    if unit == 0:
        return f"{int(value)} {units[unit]}"
    return f"{value:.2f} {units[unit]}"


def repo_cache_dir(repo: str) -> Path | None:
    if not cache_dir:
        return None
    return Path(cache_dir) / f"models--{repo.replace('/', '--')}"


def cache_stats(path: Path | None) -> tuple[int, int, int]:
    if path is None or not path.exists():
        return 0, 0, 0
    file_count = 0
    byte_count = 0
    partial_count = 0
    for item in path.rglob("*"):
        try:
            if not item.is_file():
                continue
            file_count += 1
            byte_count += item.stat().st_size
            name = item.name.lower()
            if name.endswith(".incomplete") or ".incomplete" in name or name.endswith(".lock"):
                partial_count += 1
        except OSError:
            continue
    return file_count, byte_count, partial_count


def emit_status(path: Path | None, start_bytes: int) -> None:
    files, bytes_now, partials = cache_stats(path)
    downloaded = max(0, bytes_now - start_bytes)
    print(
        "MODEL FETCH STATUS: "
        f"Pixal3D GGUF {quant} downloading from {repo_id} - "
        f"{format_bytes(bytes_now)} cached, +{format_bytes(downloaded)} this run, "
        f"{partials} active download files, {files} cache files.",
        flush=True,
    )


def reporter(path: Path | None, start_bytes: int, stop_event: threading.Event) -> None:
    emit_status(path, start_bytes)
    while not stop_event.wait(5):
        emit_status(path, start_bytes)


cache_path = repo_cache_dir(repo_id)
_, start_bytes, _ = cache_stats(cache_path)
stop_event = threading.Event()
thread = threading.Thread(target=reporter, args=(cache_path, start_bytes, stop_event), daemon=True)
thread.start()
try:
    root = snapshot_download(
        repo_id=repo_id,
        cache_dir=cache_dir,
        token=token,
        allow_patterns=allow_patterns,
    )
finally:
    stop_event.set()
    thread.join(timeout=1)

root_path = Path(root)
missing = [name for name in required_files if not (root_path / name).exists()]
files, bytes_now, partials = cache_stats(cache_path)
print(
    "MODEL FETCH STATUS: "
    f"Pixal3D GGUF {quant} download complete - {format_bytes(bytes_now)} cached, "
    f"{files} cache files, {partials} active download files.",
    flush=True,
)
if missing:
    print("MODEL FETCH FAILED: Pixal3D GGUF download finished but required files are missing.")
    for name in missing:
        print(f"missing={name}")
    raise SystemExit(1)

print(
    "MODEL FETCH COMPLETE: "
    f"Pixal3D GGUF {quant} files are ready at {root_path}. Runtime support is still disabled.",
    flush=True,
)
print(
    "Pixal3D GGUF weights are downloaded for experimentation. "
    "The current Pixal3D runtime still uses safetensors until the GGUF loader bridge is implemented.",
    flush=True,
)
PY
