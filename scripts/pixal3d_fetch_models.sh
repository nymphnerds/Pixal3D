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
Pixal3D is academic-only, not licensed for commercial or production use, and
its LICENSE says it is not intended for use within the European Union.
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
pixal3d_load_hf_token
if [[ -n "${NYMPHS3D_HF_TOKEN:-}" ]]; then
  export HF_TOKEN="${NYMPHS3D_HF_TOKEN}"
  export HUGGING_FACE_HUB_TOKEN="${NYMPHS3D_HF_TOKEN}"
fi

cat > "${PIXAL3D_PROFILE_FILE}" <<EOF
PIXAL3D_PROFILE=${profile}
PIXAL3D_VENV_DIR=${PIXAL3D_VENV_DIR}
PIXAL3D_LOW_VRAM=${PIXAL3D_LOW_VRAM}
PIXAL3D_RESOLUTION=${PIXAL3D_RESOLUTION}
PIXAL3D_MODEL_REPO=TencentARC/Pixal3D
EOF

echo "MODEL DOWNLOAD STARTED phase=prepare status=downloading profile=${profile} shared_cache=${NYMPHS3D_HF_CACHE_DIR}"

"$(pixal3d_python)" - <<'PY'
import os
from huggingface_hub import snapshot_download

cache_dir = os.environ.get("NYMPHS3D_HF_CACHE_DIR")
token = os.environ.get("NYMPHS3D_HF_TOKEN") or os.environ.get("HF_TOKEN") or None
repos = [
    ("TencentARC/Pixal3D", ["pipeline.json", "ckpts/*.json", "ckpts/*.safetensors", "README.md"]),
    ("Ruicheng/moge-2-vitl", None),
    ("camenduru/dinov3-vitl16-pretrain-lvd1689m", None),
    ("briaai/RMBG-2.0", None),
]

for index, (repo_id, allow_patterns) in enumerate(repos, start=1):
    print(f"MODEL DOWNLOAD STARTED step={index}/{len(repos)} status=downloading repo={repo_id} shared_cache={cache_dir}", flush=True)
    kwargs = {"repo_id": repo_id, "cache_dir": cache_dir, "token": token}
    if allow_patterns:
        kwargs["allow_patterns"] = allow_patterns
    try:
        root = snapshot_download(**kwargs)
    except Exception as exc:
        print(f"MODEL DOWNLOAD FAILED step={index}/{len(repos)} status=failed repo={repo_id}", flush=True)
        if repo_id == "briaai/RMBG-2.0":
            raise SystemExit(
                "BRIA RMBG-2.0 download failed. Open https://huggingface.co/briaai/RMBG-2.0 "
                "with the same Hugging Face account, complete the access form, then rerun Fetch Models.\n"
                f"Original error: {exc}"
            )
        raise
    print(f"MODEL DOWNLOAD COMPLETE step={index}/{len(repos)} status=complete repo={repo_id} root={root}", flush=True)
print("MODEL DOWNLOAD COMPLETE phase=all status=complete", flush=True)
print("Pixal3D model fetch complete.", flush=True)
PY
