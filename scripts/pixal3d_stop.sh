#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_pixal3d_common.sh"

stop_pid_file() {
  local pid_file="$1"
  local label="$2"
  if [[ -f "${pid_file}" ]]; then
    local pid
    pid="$(cat "${pid_file}" 2>/dev/null || true)"
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
      echo "Stopping ${label} pid=${pid}"
      kill "${pid}" 2>/dev/null || true
      for _ in $(seq 1 10); do
        kill -0 "${pid}" 2>/dev/null || break
        sleep 1
      done
      kill -9 "${pid}" 2>/dev/null || true
    fi
    rm -f "${pid_file}"
  fi
}

stop_pid_file "${PIXAL3D_PID_FILE}" "Pixal3D API"
stop_pid_file "${PIXAL3D_GRADIO_PID_FILE}" "Pixal3D Gradio"

(command -v fuser >/dev/null 2>&1 && fuser -k "${PIXAL3D_PORT}/tcp" >/dev/null 2>&1) || true
(command -v fuser >/dev/null 2>&1 && fuser -k "${PIXAL3D_GRADIO_PORT}/tcp" >/dev/null 2>&1) || true
pkill -f "scripts/api_server_pixal3d.py" >/dev/null 2>&1 || true
pkill -f "scripts/gradio_pixal3d_module.py" >/dev/null 2>&1 || true
pkill -f "Pixal3D/app.py" >/dev/null 2>&1 || true
echo "Pixal3D stopped."
