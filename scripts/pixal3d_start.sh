#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_pixal3d_common.sh"

if pixal3d_api_is_running; then
  echo "Pixal3D API is already running at ${PIXAL3D_SERVER_URL}"
  exit 0
fi

if [[ ! -x "$(pixal3d_python)" ]]; then
  echo "Pixal3D runtime is missing. Run scripts/install_pixal3d.sh first." >&2
  exit 1
fi

if ! pixal3d_validate_runtime_stack; then
  pixal3d_print_trellis_runtime_prerequisite
  exit 1
fi

pixal3d_ensure_data_dirs
pixal3d_load_hf_token
log_file="${PIXAL3D_LOG_DIR}/pixal3d-api.log"
echo "Starting Pixal3D API at ${PIXAL3D_SERVER_URL}"
(
  cd "${PIXAL3D_INSTALL_ROOT}"
  setsid "$(pixal3d_python)" -u scripts/api_server_pixal3d.py \
    --host "${PIXAL3D_HOST}" \
    --port "${PIXAL3D_PORT}" \
    --model-path "${PIXAL3D_MODEL_REPO}" \
    --resolution "${PIXAL3D_RESOLUTION}" \
    $([[ "${PIXAL3D_LOW_VRAM}" == "1" ]] && printf '%s' "--low-vram" || printf '%s' "--no-low-vram") \
    >"${log_file}" 2>&1 < /dev/null &
  echo $! > "${PIXAL3D_PID_FILE}"
)

for _ in $(seq 1 30); do
  if pixal3d_probe_url "${PIXAL3D_SERVER_URL}/server_info" >/dev/null 2>&1; then
    echo "Pixal3D API started."
    exit 0
  fi
  sleep 1
done

echo "Pixal3D API did not answer before timeout. Check ${log_file}" >&2
exit 1
