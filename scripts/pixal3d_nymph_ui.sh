#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PIXAL3D_GRADIO_OPEN_PATH="/nymph"
exec "${SCRIPT_DIR}/pixal3d_gradio.sh"
