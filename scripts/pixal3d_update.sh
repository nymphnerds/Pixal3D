#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_pixal3d_common.sh"

module_version="$(
  python3 - "${MODULE_ROOT}/nymph.json" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as handle:
    manifest = json.load(handle)
print(str(manifest.get("version", "unknown")).strip() or "unknown")
PY
)"

if pixal3d_gradio_is_running; then
  echo "Stopping Pixal3D UI before update so Python reloads changed module code and dependencies."
  "${SCRIPT_DIR}/pixal3d_stop_gradio.sh" || true
fi

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

if [[ -x "$(pixal3d_python)" ]]; then
  if ! pixal3d_validate_utils3d_api "$(pixal3d_python)"; then
    pixal3d_install_utils3d
  fi
  if ! pixal3d_validate_nvdiffrec_render "$(pixal3d_python)"; then
    pixal3d_install_nvdiffrec_render
  fi
else
  echo "Pixal3D runtime venv is missing; run Install when ready."
fi

printf '%s\n' "${module_version}" > "${PIXAL3D_INSTALL_ROOT}/.nymph-module-version"
echo "installed_module_version=${module_version}"
