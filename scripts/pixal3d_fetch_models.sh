#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_pixal3d_common.sh"

profile="low_vram_1024"
license_ack="no"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      profile="${2:-}"
      shift 2
      ;;
    --profile=*)
      profile="${1#*=}"
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
Pixal3D is currently released under the MIT License for Tencent-published code,
parameters, weights, and documentation. Third-party components keep their
original licenses.
BRIA RMBG-2.0 is gated/non-commercial and requires the Hugging Face access form:
https://huggingface.co/briaai/RMBG-2.0
Rerun Fetch Models after selecting "I acknowledge" in the module action form.
EOF
  exit 2
fi

case "${profile}" in
  low_vram_1024)
    PIXAL3D_LOW_VRAM=1
    PIXAL3D_RESOLUTION=1024
    ;;
  standard_1536)
    PIXAL3D_LOW_VRAM=0
    PIXAL3D_RESOLUTION=1536
    ;;
  gguf_q4_k_m)
    exec "${SCRIPT_DIR}/pixal3d_fetch_quantized_models.sh" --quant Q4_K_M --license-ack "${license_ack}"
    ;;
  gguf_q5_k_m)
    exec "${SCRIPT_DIR}/pixal3d_fetch_quantized_models.sh" --quant Q5_K_M --license-ack "${license_ack}"
    ;;
  gguf_q6_k)
    exec "${SCRIPT_DIR}/pixal3d_fetch_quantized_models.sh" --quant Q6_K --license-ack "${license_ack}"
    ;;
  gguf_q8_0)
    exec "${SCRIPT_DIR}/pixal3d_fetch_quantized_models.sh" --quant Q8_0 --license-ack "${license_ack}"
    ;;
  *)
    echo "Unsupported Pixal3D profile: ${profile}" >&2
    exit 2
    ;;
esac

if [[ ! -x "$(pixal3d_python)" ]]; then
  echo "Pixal3D runtime is missing. Run scripts/install_pixal3d.sh first." >&2
  exit 1
fi

pixal3d_ensure_data_dirs
fetch_lock="${PIXAL3D_CONFIG_DIR}/fetch_models.lock"
exec 9>"${fetch_lock}"
if ! flock -n 9; then
  echo "MODEL FETCH STATUS: Pixal3D model fetch is already running; using existing fetch lock at ${fetch_lock}."
  echo "Pixal3D model fetch is already running."
  exit 0
fi

pixal3d_load_hf_token
if [[ -n "${NYMPHS3D_HF_TOKEN:-}" ]]; then
  export HF_TOKEN="${NYMPHS3D_HF_TOKEN}"
  export HUGGING_FACE_HUB_TOKEN="${NYMPHS3D_HF_TOKEN}"
fi

pixal3d_cache_repo_present() {
  local cache_name="$1"
  [[ -d "${NYMPHS3D_HF_CACHE_DIR}/${cache_name}/snapshots" ]] &&
    [[ -n "$(find "${NYMPHS3D_HF_CACHE_DIR}/${cache_name}/snapshots" -mindepth 1 -maxdepth 1 -type d -print -quit 2>/dev/null)" ]]
}

cat > "${PIXAL3D_PROFILE_FILE}" <<EOF
PIXAL3D_PROFILE=${profile}
PIXAL3D_VENV_DIR=${PIXAL3D_VENV_DIR}
PIXAL3D_LOW_VRAM=${PIXAL3D_LOW_VRAM}
PIXAL3D_RESOLUTION=${PIXAL3D_RESOLUTION}
PIXAL3D_MODEL_REPO=TencentARC/Pixal3D
EOF

if pixal3d_cache_repo_present "models--TencentARC--Pixal3D" &&
   pixal3d_cache_repo_present "models--Ruicheng--moge-2-vitl" &&
   pixal3d_cache_repo_present "models--camenduru--dinov3-vitl16-pretrain-lvd1689m" &&
   pixal3d_cache_repo_present "models--briaai--RMBG-2.0"; then
  echo "MODEL FETCH COMPLETE: phase=all status=complete models_ready=true aux_models_ready=true shared_cache=${NYMPHS3D_HF_CACHE_DIR}"
  echo "Pixal3D model fetch skipped: all required model caches are already present."
  exit 0
fi

echo "MODEL FETCH STARTED: Pixal3D ${profile} model fetch into ${NYMPHS3D_HF_CACHE_DIR}."

"$(pixal3d_python)" - <<'PY'
import os
import threading
import time
from huggingface_hub import snapshot_download
from pathlib import Path

cache_dir = os.environ.get("NYMPHS3D_HF_CACHE_DIR")
token = os.environ.get("NYMPHS3D_HF_TOKEN") or os.environ.get("HF_TOKEN") or None
repos = [
    ("TencentARC/Pixal3D", ["pipeline.json", "ckpts/*.json", "ckpts/*.safetensors", "README.md"]),
    ("Ruicheng/moge-2-vitl", None),
    ("camenduru/dinov3-vitl16-pretrain-lvd1689m", None),
    ("briaai/RMBG-2.0", None),
]

def format_bytes(size):
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    value = float(max(0, size))
    unit = 0
    while value >= 1024 and unit < len(units) - 1:
        value /= 1024
        unit += 1
    if unit == 0:
        return f"{int(value)} {units[unit]}"
    return f"{value:.2f} {units[unit]}"

def repo_cache_dir(repo_id):
    if not cache_dir:
        return None
    return Path(cache_dir) / f"models--{repo_id.replace('/', '--')}"

def cache_stats(path):
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

def emit_fetch_status(step, total, repo_id, path, start_bytes):
    files, bytes_now, partials = cache_stats(path)
    print(
        "MODEL FETCH STATUS: "
        f"step={step}/{total} repo={repo_id} status=downloading "
        f"this_repo_cache={format_bytes(bytes_now)} "
        f"active_download_files={partials}",
        flush=True,
    )

def print_fetch_status(step, total, repo_id, path, start_bytes, stop_event):
    emit_fetch_status(step, total, repo_id, path, start_bytes)
    while not stop_event.wait(5):
        emit_fetch_status(step, total, repo_id, path, start_bytes)

def snapshot_download_with_retries(step, total, display_repo_id, **kwargs):
    attempts = 3
    for attempt in range(1, attempts + 1):
        try:
            return snapshot_download(**kwargs)
        except Exception as exc:
            if attempt >= attempts:
                raise
            print(
                "MODEL FETCH STATUS: "
                f"step {step}/{total} {display_repo_id} download was interrupted ({type(exc).__name__}). "
                f"Retrying attempt {attempt + 1}/{attempts} using the existing cache.",
                flush=True,
            )
            time.sleep(min(30, 5 * attempt))
    raise RuntimeError("unreachable retry state")

for index, (repo_id, allow_patterns) in enumerate(repos, start=1):
    total = len(repos)
    cache_path = repo_cache_dir(repo_id)
    _, start_bytes, _ = cache_stats(cache_path)
    print(
        f"MODEL FETCH STARTED: step {index}/{total} downloading {repo_id} into {cache_dir}.",
        flush=True,
    )
    stop_event = threading.Event()
    reporter = threading.Thread(
        target=print_fetch_status,
        args=(index, total, repo_id, cache_path, start_bytes, stop_event),
        daemon=True,
    )
    reporter.start()
    kwargs = {"repo_id": repo_id, "cache_dir": cache_dir, "token": token}
    if allow_patterns:
        kwargs["allow_patterns"] = allow_patterns
    try:
        root = snapshot_download_with_retries(index, total, repo_id, **kwargs)
    except Exception as exc:
        stop_event.set()
        reporter.join(timeout=1)
        if repo_id == "briaai/RMBG-2.0":
            print(
                "MODEL FETCH FAILED: "
                f"step={index}/{total} repo={repo_id} status=failed "
                "error=bria_access_needed "
                "next_step=Fill BRIA form, accept access, then run Fetch Models again. "
                "link=https://huggingface.co/briaai/RMBG-2.0",
                flush=True,
            )
            raise SystemExit(
                "BRIA access needed. Fill BRIA form, accept access, then run Fetch Models again.\n"
                "https://huggingface.co/briaai/RMBG-2.0\n"
                f"Original error: {exc}"
            )
        print(
            "MODEL FETCH FAILED: "
            f"step={index}/{total} repo={repo_id} status=failed error=download_failed",
            flush=True,
        )
        raise
    stop_event.set()
    reporter.join(timeout=1)
    files, bytes_now, partials = cache_stats(cache_path)
    print(
        "MODEL FETCH STATUS: "
        f"step={index}/{total} repo={repo_id} status=complete "
        f"this_repo_cache={format_bytes(bytes_now)} "
        f"active_download_files={partials}",
        flush=True,
    )
    print(f"MODEL FETCH COMPLETE: step {index}/{total} {repo_id} ready at {root}.", flush=True)
print("MODEL FETCH COMPLETE: Pixal3D model fetch finished.", flush=True)
print("Pixal3D model fetch complete.", flush=True)
PY
