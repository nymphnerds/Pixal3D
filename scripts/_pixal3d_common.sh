#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

PIXAL3D_INSTALL_ROOT="${PIXAL3D_INSTALL_ROOT:-$HOME/Pixal3D}"
PIXAL3D_TRELLIS_RUNTIME_ROOT="${PIXAL3D_TRELLIS_RUNTIME_ROOT:-$HOME/TRELLIS.2}"
PIXAL3D_TRELLIS_VENV_DIR="${PIXAL3D_TRELLIS_VENV_DIR:-$PIXAL3D_TRELLIS_RUNTIME_ROOT/.venv}"
PIXAL3D_VENV_DIR="${PIXAL3D_VENV_DIR:-$PIXAL3D_INSTALL_ROOT/.venv}"
NYMPHS_DATA_ROOT="${NYMPHS_DATA_ROOT:-$HOME/NymphsData}"
PIXAL3D_CONFIG_DIR="${PIXAL3D_CONFIG_DIR:-$NYMPHS_DATA_ROOT/config/pixal3d}"
PIXAL3D_PROFILE_FILE="${PIXAL3D_PROFILE_FILE:-$PIXAL3D_CONFIG_DIR/profile.env}"
PIXAL3D_OUTPUT_DIR="${PIXAL3D_OUTPUT_DIR:-$NYMPHS_DATA_ROOT/outputs/pixal3d}"
PIXAL3D_LOG_DIR="${PIXAL3D_LOG_DIR:-$NYMPHS_DATA_ROOT/logs/pixal3d}"
PIXAL3D_PID_FILE="${PIXAL3D_PID_FILE:-$PIXAL3D_LOG_DIR/pixal3d-api.pid}"
PIXAL3D_GRADIO_PID_FILE="${PIXAL3D_GRADIO_PID_FILE:-$PIXAL3D_LOG_DIR/pixal3d-gradio.pid}"
PIXAL3D_HOST="${PIXAL3D_HOST:-127.0.0.1}"
PIXAL3D_PORT="${PIXAL3D_PORT:-8096}"
PIXAL3D_GRADIO_HOST="${PIXAL3D_GRADIO_HOST:-127.0.0.1}"
PIXAL3D_GRADIO_PORT="${PIXAL3D_GRADIO_PORT:-8097}"
PIXAL3D_SERVER_URL="${PIXAL3D_SERVER_URL:-http://${PIXAL3D_HOST}:${PIXAL3D_PORT}}"
PIXAL3D_GRADIO_URL="${PIXAL3D_GRADIO_URL:-http://${PIXAL3D_GRADIO_HOST}:${PIXAL3D_GRADIO_PORT}}"
PIXAL3D_MODEL_REPO="${PIXAL3D_MODEL_REPO:-TencentARC/Pixal3D}"
PIXAL3D_LOW_VRAM="${PIXAL3D_LOW_VRAM:-1}"
PIXAL3D_RESOLUTION="${PIXAL3D_RESOLUTION:-1024}"
PIXAL3D_WEIGHT_FORMAT="${PIXAL3D_WEIGHT_FORMAT:-safetensors}"
PIXAL3D_QUANT_REPO="${PIXAL3D_QUANT_REPO:-Aero-Ex/Pixal3D-GGUF}"
PIXAL3D_QUANT="${PIXAL3D_QUANT:-Q5_K_M}"
PIXAL3D_QUANT_RUNTIME_SUPPORTED="${PIXAL3D_QUANT_RUNTIME_SUPPORTED:-0}"

if [[ -f "${PIXAL3D_PROFILE_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${PIXAL3D_PROFILE_FILE}"
fi

export OPENCV_IO_ENABLE_OPENEXR="${OPENCV_IO_ENABLE_OPENEXR:-1}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
export HF_HUB_DISABLE_XET="${HF_HUB_DISABLE_XET:-1}"
export HF_HUB_ENABLE_HF_TRANSFER="${HF_HUB_ENABLE_HF_TRANSFER:-0}"
export NYMPHS3D_HF_CACHE_DIR="${NYMPHS3D_HF_CACHE_DIR:-$NYMPHS_DATA_ROOT/cache/huggingface}"
export HF_HOME="${HF_HOME:-$NYMPHS_DATA_ROOT/cache/huggingface-home}"
export HF_HUB_CACHE="${HF_HUB_CACHE:-$NYMPHS3D_HF_CACHE_DIR}"
export TORCH_HOME="${TORCH_HOME:-$NYMPHS_DATA_ROOT/cache/torch-hub}"
export PIXAL3D_OUTPUT_DIR PIXAL3D_LOG_DIR PIXAL3D_CONFIG_DIR PIXAL3D_MODEL_REPO PIXAL3D_LOW_VRAM PIXAL3D_RESOLUTION
export PIXAL3D_WEIGHT_FORMAT PIXAL3D_QUANT_REPO PIXAL3D_QUANT PIXAL3D_QUANT_RUNTIME_SUPPORTED

if [[ -d /usr/local/cuda-13.0 ]]; then
  export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda-13.0}"
elif [[ -d /usr/local/cuda-12.4 ]]; then
  export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda-12.4}"
fi
if [[ -n "${CUDA_HOME:-}" ]]; then
  export PATH="${CUDA_HOME}/bin:${PATH}"
  export LD_LIBRARY_PATH="${CUDA_HOME}/lib64:${LD_LIBRARY_PATH:-}"
fi

pixal3d_ensure_data_dirs() {
  mkdir -p "${PIXAL3D_LOG_DIR}" "${PIXAL3D_OUTPUT_DIR}" "${PIXAL3D_CONFIG_DIR}" "${NYMPHS3D_HF_CACHE_DIR}" "${HF_HOME}" "${TORCH_HOME}"
}

pixal3d_python() {
  printf '%s\n' "${PIXAL3D_VENV_DIR}/bin/python"
}

pixal3d_pip() {
  printf '%s\n' "${PIXAL3D_VENV_DIR}/bin/pip"
}

pixal3d_load_hf_token() {
  if [[ -n "${NYMPHS3D_HF_TOKEN:-}" || -n "${HF_TOKEN:-}" || -n "${HUGGING_FACE_HUB_TOKEN:-}" ]]; then
    return 0
  fi

  local token
  token="$(
    python3 - <<'PY'
import json
import os
from pathlib import Path

paths = [
    Path.home() / ".config" / "NymphsCore" / "shared-secrets.json",
    Path.home() / "NymphsData" / "config" / "shared-secrets.json",
    Path.home() / "NymphsData" / "shared-secrets.json",
]
users_root = Path("/mnt/c/Users")
if users_root.exists():
    paths.extend(users_root.glob("*/AppData/Local/NymphsCore/shared-secrets.json"))

for path in paths:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        continue
    token = (
        data.get("HuggingFaceToken")
        or data.get("huggingFaceToken")
        or data.get("huggingface_token")
        or data.get("hf_token")
        or ""
    )
    if token:
        print(token.strip())
        break
PY
  )"

  if [[ -n "${token}" ]]; then
    export NYMPHS3D_HF_TOKEN="${token}"
    export HF_TOKEN="${token}"
    export HUGGING_FACE_HUB_TOKEN="${token}"
  fi
}

pixal3d_api_is_running() {
  if [[ -f "${PIXAL3D_PID_FILE}" ]]; then
    local pid
    pid="$(cat "${PIXAL3D_PID_FILE}" 2>/dev/null || true)"
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
      return 0
    fi
  fi
  return 1
}

pixal3d_gradio_is_running() {
  if [[ -f "${PIXAL3D_GRADIO_PID_FILE}" ]]; then
    local pid
    pid="$(cat "${PIXAL3D_GRADIO_PID_FILE}" 2>/dev/null || true)"
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
      return 0
    fi
  fi
  return 1
}

pixal3d_probe_url() {
  local url="${1}"
  python3 - "${url}" <<'PY'
import sys
from urllib.request import urlopen

try:
    with urlopen(sys.argv[1], timeout=2) as response:
        print(response.read().decode("utf-8", errors="replace"))
except Exception as exc:
    raise SystemExit(str(exc))
PY
}

pixal3d_validate_runtime_stack() {
  local python_bin="${1:-$(pixal3d_python)}"
  [[ -x "${python_bin}" ]] || return 1
  "${python_bin}" - <<'PY' >/dev/null 2>&1
import importlib

for module_name in (
    "torch",
    "natten",
    "flash_attn",
    "cumesh",
    "flex_gemm",
    "o_voxel",
    "nvdiffrast.torch",
    "moge",
    "utils3d",
):
    importlib.import_module(module_name)
PY
}

pixal3d_print_trellis_runtime_prerequisite() {
  cat <<'EOF'
Install or repair Pixal3D first.

Pixal3D uses the shared TRELLIS.2/Pixal3D runtime venv.
Install or Repair Pixal3D creates that runtime automatically if it is missing.
You do not need to fetch TRELLIS model weights for Pixal3D.
EOF
}
