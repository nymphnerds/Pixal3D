#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_pixal3d_common.sh"

if [[ -d "${PIXAL3D_INSTALL_ROOT}/.git" ]]; then
  git -C "${PIXAL3D_INSTALL_ROOT}" pull --ff-only
else
  echo "Pixal3D install root is not a git checkout: ${PIXAL3D_INSTALL_ROOT}" >&2
  exit 1
fi
printf '0.1.0\n' > "${PIXAL3D_INSTALL_ROOT}/.nymph-module-version"
echo "installed_module_version=0.1.0"
