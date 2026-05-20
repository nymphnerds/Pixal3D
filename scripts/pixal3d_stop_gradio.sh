#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_pixal3d_common.sh"

if [[ -f "${PIXAL3D_GRADIO_PID_FILE}" ]]; then
  gradio_pid="$(cat "${PIXAL3D_GRADIO_PID_FILE}" 2>/dev/null || true)"
  if [[ -n "${gradio_pid}" ]] && kill -0 "${gradio_pid}" 2>/dev/null; then
    echo "Stopping Pixal3D Gradio pid=${gradio_pid}"
    kill -- "-${gradio_pid}" 2>/dev/null || kill "${gradio_pid}" 2>/dev/null || true
    for _ in $(seq 1 2); do
      kill -0 "${gradio_pid}" 2>/dev/null || break
      sleep 0.25
    done
    kill -9 -- "-${gradio_pid}" 2>/dev/null || kill -9 "${gradio_pid}" 2>/dev/null || true
  fi
  rm -f "${PIXAL3D_GRADIO_PID_FILE}"
fi

pkill -f "scripts/gradio_pixal3d_module.py" >/dev/null 2>&1 || true
pkill -f "app.py .*--port ${PIXAL3D_GRADIO_PORT}" >/dev/null 2>&1 || true
(command -v fuser >/dev/null 2>&1 && timeout 1 fuser -k "${PIXAL3D_GRADIO_PORT}/tcp" >/dev/null 2>&1) || true
echo "Pixal3D Gradio stopped."
