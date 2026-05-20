#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_pixal3d_common.sh"

if [[ ! -x "$(pixal3d_python)" ]]; then
  echo "Pixal3D runtime is missing. Run install first." >&2
  exit 1
fi

if ! pixal3d_validate_runtime_stack; then
  pixal3d_print_trellis_runtime_prerequisite
  exit 1
fi

(
  cd "${PIXAL3D_INSTALL_ROOT}"
  "$(pixal3d_python)" -m py_compile scripts/api_server_pixal3d.py inference.py app.py
  "$(pixal3d_python)" - <<'PY'
import importlib

for module_name in ("fastapi", "uvicorn", "PIL"):
    importlib.import_module(module_name)
print("Pixal3D smoke test passed: API wrapper dependencies import.")
PY
)
