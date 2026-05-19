#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_pixal3d_common.sh"

profile="${PIXAL3D_RUNTIME_PROFILE:-cuda13}"
pixal3d_ensure_data_dirs

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
  printf '0.1.0\n' > "${PIXAL3D_INSTALL_ROOT}/.nymph-module-version"
  echo "installed_module_version=0.1.0"
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

python3.10 -m venv "${PIXAL3D_VENV_DIR}"
"$(pixal3d_python)" -m pip install --upgrade pip setuptools wheel

if [[ "${profile}" == "cuda13" ]]; then
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
printf '0.1.0\n' > "${PIXAL3D_INSTALL_ROOT}/.nymph-module-version"
echo "installed_module_version=0.1.0"
echo "Pixal3D install finished. If native TRELLIS.2 extensions are missing, install/repair them before generation."
