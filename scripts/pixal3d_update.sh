#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_pixal3d_common.sh"

if [[ -d "${PIXAL3D_INSTALL_ROOT}/.git" ]]; then
  git -C "${PIXAL3D_INSTALL_ROOT}" pull --ff-only
elif [[ -d "${MODULE_ROOT}/pixal3d" ]]; then
  echo "Syncing Pixal3D module source into ${PIXAL3D_INSTALL_ROOT}..."
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
else
  echo "Pixal3D source is missing from update root: ${MODULE_ROOT}" >&2
  exit 1
fi
printf '0.1.0\n' > "${PIXAL3D_INSTALL_ROOT}/.nymph-module-version"
echo "installed_module_version=0.1.0"
