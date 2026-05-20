#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_pixal3d_common.sh"

if pixal3d_gradio_is_running; then
  echo "Pixal3D Gradio is already running."
  echo "url=${PIXAL3D_GRADIO_URL}"
  echo "module_ui_url=${PIXAL3D_GRADIO_URL}"
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

log_file="${PIXAL3D_LOG_DIR}/pixal3d-gradio.log"
echo "Starting Pixal3D Gradio at ${PIXAL3D_GRADIO_URL}"
(
  cd "${PIXAL3D_INSTALL_ROOT}"
  export GRADIO_SERVER_NAME="${PIXAL3D_GRADIO_HOST}"
  export GRADIO_SERVER_PORT="${PIXAL3D_GRADIO_PORT}"
  export LOW_VRAM="${PIXAL3D_LOW_VRAM}"
  export PIXAL3D_OUTPUT_DIR PIXAL3D_TEXTURE_SIZE PIXAL3D_TEXTURE_NAF_TARGET_SIZE
  setsid "$(pixal3d_python)" -u app.py \
    --host "${PIXAL3D_GRADIO_HOST}" \
    --port "${PIXAL3D_GRADIO_PORT}" \
    --lazy-load \
    --warm-on-start \
    $([[ "${PIXAL3D_LOW_VRAM}" == "1" ]] && printf '%s' "--low-vram" || printf '%s' "--no-low-vram") \
    >"${log_file}" 2>&1 < /dev/null &
  echo $! > "${PIXAL3D_GRADIO_PID_FILE}"
)

gradio_pid="$(cat "${PIXAL3D_GRADIO_PID_FILE}" 2>/dev/null || true)"
for _ in $(seq 1 60); do
  if [[ -n "${gradio_pid}" ]] && ! kill -0 "${gradio_pid}" 2>/dev/null; then
    rm -f "${PIXAL3D_GRADIO_PID_FILE}"
    echo "Pixal3D Gradio exited while starting. Check ${log_file}" >&2
    tail -n 40 "${log_file}" >&2 || true
    exit 1
  fi
  if [[ -n "${gradio_pid}" ]] && kill -0 "${gradio_pid}" 2>/dev/null &&
     pixal3d_probe_url "${PIXAL3D_GRADIO_URL}" >/dev/null 2>&1; then
    echo "Pixal3D Gradio started."
    echo "url=${PIXAL3D_GRADIO_URL}"
    echo "module_ui_url=${PIXAL3D_GRADIO_URL}"
    exit 0
  fi
  sleep 1
done

echo "Pixal3D Gradio did not answer before timeout. Check ${log_file}" >&2
exit 1
