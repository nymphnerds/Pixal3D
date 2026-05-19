#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_pixal3d_common.sh"

mkdir -p "${PIXAL3D_OUTPUT_DIR}"
echo "${PIXAL3D_OUTPUT_DIR}"
