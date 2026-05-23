#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_pixal3d_common.sh"

export PIXAL3D_GRADIO_OPEN_PATH="${PIXAL3D_GRADIO_OPEN_PATH:-/nymph}"
exec "${SCRIPT_DIR}/pixal3d_gradio.sh"
