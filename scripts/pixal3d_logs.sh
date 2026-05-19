#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_pixal3d_common.sh"

pixal3d_ensure_data_dirs
touch "${PIXAL3D_LOG_DIR}/pixal3d-api.log" "${PIXAL3D_LOG_DIR}/pixal3d-gradio.log"
echo "${PIXAL3D_LOG_DIR}/pixal3d-api.log"
