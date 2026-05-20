#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_pixal3d_common.sh"

profile="${PIXAL3D_RUNTIME_PROFILE:-trellis_runtime}"
pixal3d_ensure_data_dirs

pixal3d_map_flash_attn_cuda_arch() {
  local compute_cap="$1"
  local major="${compute_cap%%.*}"

  case "${major}" in
    8) echo "80" ;;
    9) echo "90" ;;
    10) echo "100" ;;
    11) echo "110" ;;
    12) echo "120" ;;
  esac
}

pixal3d_detect_compute_cap() {
  local compute_cap=""

  if ! command -v nvidia-smi >/dev/null 2>&1; then
    return 0
  fi

  compute_cap="$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | head -n 1 | tr -d '[:space:]' || true)"
  if [[ "${compute_cap}" =~ ^[0-9]+\.[0-9]+$ ]]; then
    echo "${compute_cap}"
  fi
}

pixal3d_resolve_flash_attn_cuda_archs() {
  local detected_caps=""
  local compute_cap=""
  local arch=""

  if ! command -v nvidia-smi >/dev/null 2>&1; then
    return 0
  fi

  detected_caps="$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null || true)"
  while IFS= read -r compute_cap; do
    compute_cap="$(tr -d '[:space:]' <<< "${compute_cap}")"
    if [[ ! "${compute_cap}" =~ ^[0-9]+\.[0-9]+$ ]]; then
      continue
    fi

    arch="$(pixal3d_map_flash_attn_cuda_arch "${compute_cap}")"
    if [[ -z "${arch}" ]]; then
      continue
    fi

    echo "${arch}"
    return 0
  done <<< "${detected_caps}"
}

pixal3d_normalize_flash_attn_cuda_archs() {
  local raw="$1"
  local arch=""
  local selected_arch=""

  raw="$(tr ', ' ';;' <<< "${raw}")"
  while IFS= read -r arch; do
    arch="$(tr -d '[:space:]' <<< "${arch}")"
    arch="${arch,,}"
    arch="${arch#sm}"
    [[ -z "${arch}" ]] && continue

    case "${arch}" in
      80|90|100|110|120)
        ;;
      *)
        echo "Invalid TRELLIS_FLASH_ATTN_CUDA_ARCHS value: ${arch}" >&2
        echo "Use auto or one of: sm80, sm90, sm100, sm110, sm120." >&2
        return 1
        ;;
    esac

    if [[ -n "${selected_arch}" && "${selected_arch}" != "${arch}" ]]; then
      echo "TRELLIS_FLASH_ATTN_CUDA_ARCHS accepts one target arch for this install, not '${raw}'." >&2
      echo "Choose one GPU target in the Manager dropdown so flash-attn does not compile multiple arch families." >&2
      return 1
    fi

    selected_arch="${arch}"
  done < <(tr ';' '\n' <<< "${raw}")

  echo "${selected_arch}"
}

pixal3d_sync_trellis_runtime_source() {
  local source_dir="${PIXAL3D_TRELLIS_SOURCE_DIR}"
  local eigen_dir="${source_dir}/o-voxel/third_party/eigen"

  if [[ ! -d "${source_dir}/.git" ]]; then
    rm -rf "${source_dir}"
    mkdir -p "$(dirname "${source_dir}")"
    echo "Cloning TRELLIS.2 runtime source for native Pixal3D dependencies"
    GIT_TERMINAL_PROMPT=0 git clone --filter=blob:none --no-checkout "${PIXAL3D_TRELLIS_SOURCE_REPO}" "${source_dir}"
  fi

  echo "Syncing TRELLIS.2 runtime source to ${PIXAL3D_TRELLIS_SOURCE_REF}"
  GIT_TERMINAL_PROMPT=0 git -C "${source_dir}" fetch --depth 1 origin "${PIXAL3D_TRELLIS_SOURCE_REF}"
  git -C "${source_dir}" checkout --detach FETCH_HEAD
  GIT_TERMINAL_PROMPT=0 git -C "${source_dir}" submodule update --init --recursive o-voxel/third_party/eigen

  if [[ ! -f "${eigen_dir}/Eigen/Core" ]]; then
    echo "Expected Eigen submodule is missing from ${eigen_dir}." >&2
    echo "Repair or remove ${source_dir}, then retry Pixal3D Install/Repair." >&2
    exit 1
  fi

  if [[ ! -f "${source_dir}/o-voxel/setup.py" ]]; then
    echo "Expected o-voxel source is missing from ${source_dir}/o-voxel." >&2
    echo "Repair or remove ${source_dir}, then retry Pixal3D Install/Repair." >&2
    exit 1
  fi
}

pixal3d_install_flash_attn() {
  local flash_attn_jobs="${TRELLIS_FLASH_ATTN_MAX_JOBS:-${NYMPHS3D_TRELLIS_FLASH_ATTN_MAX_JOBS:-4}}"
  local flash_attn_nvcc_threads="${TRELLIS_FLASH_ATTN_NVCC_THREADS:-${NYMPHS3D_TRELLIS_FLASH_ATTN_NVCC_THREADS:-2}}"
  local requested_flash_attn_archs="${TRELLIS_FLASH_ATTN_CUDA_ARCHS:-${NYMPHS3D_TRELLIS_FLASH_ATTN_CUDA_ARCHS:-${FLASH_ATTN_CUDA_ARCHS:-}}}"
  local flash_attn_archs=""
  local -a flash_attn_env=()

  if "$(pixal3d_python)" -c 'import flash_attn' >/dev/null 2>&1; then
    echo "flash-attn already available in shared TRELLIS runtime."
    return 0
  fi

  echo "Installing required flash-attn into shared TRELLIS.2/Pixal3D runtime."
  echo "flash-attn install command: pip install flash-attn --no-build-isolation"

  if [[ -n "${requested_flash_attn_archs}" &&
        "${requested_flash_attn_archs,,}" != "auto" ]]; then
    flash_attn_archs="$(pixal3d_normalize_flash_attn_cuda_archs "${requested_flash_attn_archs}")"
  fi
  if [[ -z "${flash_attn_archs}" ]]; then
    flash_attn_archs="$(pixal3d_resolve_flash_attn_cuda_archs)"
  fi
  if [[ -n "${flash_attn_archs}" ]]; then
    if [[ -n "${requested_flash_attn_archs}" && "${requested_flash_attn_archs,,}" != "auto" ]]; then
      echo "Using explicit flash-attn CUDA arch list: ${flash_attn_archs}"
    else
      echo "Auto-selected flash-attn CUDA arch list: ${flash_attn_archs}"
    fi
    echo "Set TRELLIS_FLASH_ATTN_CUDA_ARCHS to override this GPU arch selection."
    flash_attn_env+=("FLASH_ATTN_CUDA_ARCHS=${flash_attn_archs}")
  else
    echo "Could not select one flash-attn CUDA arch target." >&2
    echo "Choose a GPU target manually in the Manager so flash-attn does not compile its broad package default arch list." >&2
    exit 1
  fi

  "$(pixal3d_pip)" install packaging psutil ninja

  if [[ ! "${flash_attn_jobs}" =~ ^[0-9]+$ || "${flash_attn_jobs}" -lt 1 ]]; then
    echo "Invalid TRELLIS_FLASH_ATTN_MAX_JOBS value: ${flash_attn_jobs}" >&2
    exit 1
  fi
  echo "Limiting flash-attn build parallelism with MAX_JOBS=${flash_attn_jobs}."
  flash_attn_env+=("MAX_JOBS=${flash_attn_jobs}")
  flash_attn_env+=("CMAKE_BUILD_PARALLEL_LEVEL=${flash_attn_jobs}")
  flash_attn_env+=("MAKEFLAGS=-j${flash_attn_jobs}")
  flash_attn_env+=("NINJAFLAGS=-j${flash_attn_jobs}")

  if [[ -n "${flash_attn_nvcc_threads}" ]]; then
    if [[ ! "${flash_attn_nvcc_threads}" =~ ^[0-9]+$ || "${flash_attn_nvcc_threads}" -lt 1 ]]; then
      echo "Invalid TRELLIS_FLASH_ATTN_NVCC_THREADS value: ${flash_attn_nvcc_threads}" >&2
      exit 1
    fi
    echo "Using NVCC_THREADS=${flash_attn_nvcc_threads} for flash-attn."
    flash_attn_env+=("NVCC_THREADS=${flash_attn_nvcc_threads}")
  fi

  env "${flash_attn_env[@]}" "$(pixal3d_pip)" install --no-build-isolation flash-attn
}

pixal3d_install_natten() {
  local natten_workers="${PIXAL3D_NATTEN_WORKERS:-${NATTEN_N_WORKERS:-4}}"
  local compute_cap

  if "$(pixal3d_python)" -c 'import natten' >/dev/null 2>&1; then
    echo "natten already available in shared TRELLIS runtime."
    return 0
  fi

  compute_cap="$(pixal3d_detect_compute_cap)"
  if [[ -n "${compute_cap}" ]]; then
    echo "Installing natten into shared TRELLIS runtime for CUDA ${compute_cap}."
    env "NATTEN_CUDA_ARCH=${compute_cap}" "NATTEN_N_WORKERS=${natten_workers}" \
      "$(pixal3d_pip)" install natten==0.21.0 --no-build-isolation
  else
    echo "Installing natten into shared TRELLIS runtime."
    env "NATTEN_N_WORKERS=${natten_workers}" \
      "$(pixal3d_pip)" install natten==0.21.0 --no-build-isolation
  fi
}

pixal3d_install_shared_trellis_runtime() {
  local detected_cc=""

  echo "Ensuring shared TRELLIS.2/Pixal3D runtime venv at ${PIXAL3D_TRELLIS_VENV_DIR}"
  mkdir -p "${PIXAL3D_TRELLIS_RUNTIME_ROOT}"
  PIXAL3D_VENV_DIR="${PIXAL3D_TRELLIS_VENV_DIR}"

  if [[ -d "${PIXAL3D_VENV_DIR}" ]] && {
    [[ ! -x "$(pixal3d_python)" ]] ||
    [[ ! -x "$(pixal3d_pip)" ]] ||
    ! "$(pixal3d_python)" -m pip --version >/dev/null 2>&1
  }; then
    echo "Removing incomplete shared TRELLIS runtime venv at ${PIXAL3D_VENV_DIR}"
    rm -rf "${PIXAL3D_VENV_DIR}"
  fi

  if [[ ! -x "$(pixal3d_python)" ]]; then
    echo "Creating shared TRELLIS runtime venv"
    python3.10 -m venv "${PIXAL3D_VENV_DIR}"
  fi

  if [[ ! -x "$(pixal3d_python)" ]] || ! "$(pixal3d_python)" -m pip --version >/dev/null 2>&1; then
    echo "Shared TRELLIS runtime venv was created, but Python/pip is missing. Repair Python 3.10 venv tooling and retry." >&2
    exit 1
  fi

  export PATH="${PIXAL3D_VENV_DIR}/bin:${PATH}"
  "$(pixal3d_python)" --version
  "$(pixal3d_pip)" install --upgrade pip setuptools wheel ninja

  if ! "$(pixal3d_python)" -c 'import torch, torchvision' >/dev/null 2>&1; then
    echo "Installing PyTorch into shared TRELLIS runtime"
    "$(pixal3d_pip)" install torch==2.11.0 torchvision torchaudio --index-url "${PIXAL3D_TORCH_INDEX_URL:-https://download.pytorch.org/whl/cu130}"
  fi

  "$(pixal3d_pip)" install -r "${PIXAL3D_INSTALL_ROOT}/requirements.txt"
  "$(pixal3d_pip)" install fastapi uvicorn pillow plyfile packaging psutil ninja
  "$(pixal3d_pip)" install "git+https://github.com/EasternJournalist/utils3d.git@${PIXAL3D_UTILS3D_REF:-9a4eb15e4021b67b12c460c7057d642626897ec8}"

  if [[ -n "${TRELLIS_CUDA_ARCH_LIST:-${NYMPHS3D_TRELLIS_CUDA_ARCH_LIST:-}}" ]]; then
    export TORCH_CUDA_ARCH_LIST="${TRELLIS_CUDA_ARCH_LIST:-${NYMPHS3D_TRELLIS_CUDA_ARCH_LIST:-}}"
  else
    detected_cc="$(pixal3d_detect_compute_cap)"
    if [[ -n "${detected_cc}" ]]; then
      export TORCH_CUDA_ARCH_LIST="${detected_cc}"
    fi
  fi

  pixal3d_install_flash_attn
  pixal3d_install_natten

  if ! "$(pixal3d_python)" - <<'PY' >/dev/null 2>&1
import importlib

for module_name in ("cumesh", "flex_gemm", "o_voxel", "nvdiffrast.torch"):
    importlib.import_module(module_name)
PY
  then
    echo "Building TRELLIS native runtime extensions into shared runtime"
    pixal3d_sync_trellis_runtime_source
    "$(pixal3d_pip)" install --no-build-isolation \
      "git+https://github.com/JeffreyXiang/CuMesh.git@${PIXAL3D_CUMESH_REF:-cf1a2f07304b5fe388ed86a16e4a0474599df914}" \
      "git+https://github.com/JeffreyXiang/FlexGEMM.git@${PIXAL3D_FLEXGEMM_REF:-6dd94a859c26ee8246888502eada3dd8ad85532e}" \
      "git+https://github.com/NVlabs/nvdiffrast.git@${PIXAL3D_NVDIFFRAST_REF:-253ac4fcea7de5f396371124af597e6cc957bfae}"

    "$(pixal3d_pip)" install --no-build-isolation --no-deps "${PIXAL3D_TRELLIS_SOURCE_DIR}/o-voxel"
  fi

  if ! pixal3d_validate_runtime_stack "$(pixal3d_python)"; then
    echo "Shared TRELLIS runtime install finished, but required Pixal3D imports are still missing." >&2
    exit 1
  fi
}

module_version="$(
  python3 - "${MODULE_ROOT}/nymph.json" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as handle:
    manifest = json.load(handle)
print(str(manifest.get("version", "unknown")).strip() or "unknown")
PY
)"

if [[ ! -d "${PIXAL3D_INSTALL_ROOT}/pixal3d" && -d "${MODULE_ROOT}/pixal3d" ]]; then
  echo "Syncing Pixal3D source into ${PIXAL3D_INSTALL_ROOT}..."
  mkdir -p "${PIXAL3D_INSTALL_ROOT}"
  (
    cd "${MODULE_ROOT}"
    tar \
      --exclude='./.git' \
      --exclude='./.venv' \
      --exclude='./__pycache__' \
      -cf - .
  ) | (
    cd "${PIXAL3D_INSTALL_ROOT}"
    tar -xf -
  )
fi

if [[ "${profile}" == "manual" ]]; then
  echo "Manual profile selected. Creating module folders and marker only."
  mkdir -p "${PIXAL3D_INSTALL_ROOT}" "${PIXAL3D_VENV_DIR}"
  cat > "${PIXAL3D_PROFILE_FILE}" <<EOF
PIXAL3D_PROFILE=manual
PIXAL3D_VENV_DIR=${PIXAL3D_VENV_DIR}
PIXAL3D_LOW_VRAM=${PIXAL3D_LOW_VRAM}
PIXAL3D_RESOLUTION=${PIXAL3D_RESOLUTION}
PIXAL3D_MODEL_REPO=${PIXAL3D_MODEL_REPO}
EOF
  printf '%s\n' "${module_version}" > "${PIXAL3D_INSTALL_ROOT}/.nymph-module-version"
  echo "installed_module_version=${module_version}"
  exit 0
fi

if [[ ! -d "${PIXAL3D_INSTALL_ROOT}/pixal3d" ]]; then
  echo "Pixal3D source is missing at ${PIXAL3D_INSTALL_ROOT}." >&2
  echo "The Manager should clone nymphnerds/Pixal3D into this install root before running this script." >&2
  exit 1
fi

echo "Installing Pixal3D runtime profile: ${profile}"
sudo apt-get update
sudo apt-get install -y python3.10 python3.10-venv python3.10-dev git curl cmake build-essential pkg-config libegl1-mesa-dev libgl1 libglib2.0-0 ccache ninja-build libjpeg-dev

if [[ "${profile}" == "trellis_runtime" ]]; then
  pixal3d_install_shared_trellis_runtime
  cat > "${PIXAL3D_PROFILE_FILE}" <<EOF
PIXAL3D_PROFILE=low_vram_1024
PIXAL3D_RUNTIME_PROFILE=trellis_runtime
PIXAL3D_VENV_DIR=${PIXAL3D_TRELLIS_VENV_DIR}
PIXAL3D_LOW_VRAM=1
PIXAL3D_RESOLUTION=1024
PIXAL3D_MODEL_REPO=TencentARC/Pixal3D
EOF
  "$(pixal3d_python)" -m py_compile "${PIXAL3D_INSTALL_ROOT}/scripts/api_server_pixal3d.py"
  printf '%s\n' "${module_version}" > "${PIXAL3D_INSTALL_ROOT}/.nymph-module-version"
  echo "installed_module_version=${module_version}"
  echo "Pixal3D install finished. Shared TRELLIS.2/Pixal3D runtime is ready at ${PIXAL3D_TRELLIS_VENV_DIR}."
  echo "TRELLIS.2 model weights are not required for Pixal3D."
  exit 0
fi

if [[ -d "${PIXAL3D_VENV_DIR}" ]] && {
  [[ ! -x "$(pixal3d_python)" ]] ||
  [[ ! -x "$(pixal3d_pip)" ]] ||
  ! "$(pixal3d_python)" -m pip --version >/dev/null 2>&1
}; then
  echo "Removing incomplete Pixal3D venv at ${PIXAL3D_VENV_DIR}"
  rm -rf "${PIXAL3D_VENV_DIR}"
fi

if [[ ! -x "$(pixal3d_python)" ]]; then
  echo "Creating Pixal3D venv at ${PIXAL3D_VENV_DIR}"
  python3.10 -m venv "${PIXAL3D_VENV_DIR}"
fi

if [[ ! -x "$(pixal3d_python)" ]] || ! "$(pixal3d_python)" -m pip --version >/dev/null 2>&1; then
  echo "Pixal3D venv was created, but Python/pip is missing. Repair Python 3.10 venv tooling and retry." >&2
  exit 1
fi

"$(pixal3d_python)" -m pip install --upgrade pip setuptools wheel

if [[ "${profile}" == "cuda13" ]]; then
  echo "Pixal3D dedicated CUDA 13 runtime is experimental. The supported user path is the TRELLIS.2 module runtime profile." >&2
  "$(pixal3d_pip)" install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cu130
fi

"$(pixal3d_pip)" install -r "${PIXAL3D_INSTALL_ROOT}/requirements.txt"
"$(pixal3d_pip)" install fastapi uvicorn pillow plyfile

cat > "${PIXAL3D_PROFILE_FILE}" <<EOF
PIXAL3D_PROFILE=low_vram_1024
PIXAL3D_LOW_VRAM=1
PIXAL3D_RESOLUTION=1024
PIXAL3D_MODEL_REPO=TencentARC/Pixal3D
EOF

"$(pixal3d_python)" -m py_compile "${PIXAL3D_INSTALL_ROOT}/scripts/api_server_pixal3d.py"
printf '%s\n' "${module_version}" > "${PIXAL3D_INSTALL_ROOT}/.nymph-module-version"
echo "installed_module_version=${module_version}"
echo "Pixal3D install finished. If native TRELLIS.2 extensions are missing, install/repair them before generation."
