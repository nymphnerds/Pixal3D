#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_pixal3d_common.sh"

purge=false
data_only=false
confirm=false
dry_run=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --purge) purge=true; shift ;;
    --data-only) data_only=true; shift ;;
    --yes) confirm=true; shift ;;
    --dry-run) dry_run=true; shift ;;
    *) shift ;;
  esac
done

if [[ "${confirm}" != "true" && "${dry_run}" != "true" ]]; then
  echo "Refusing to uninstall without --yes or --dry-run." >&2
  exit 2
fi

targets=()
if [[ "${data_only}" == "true" || "${purge}" == "true" ]]; then
  targets+=("${PIXAL3D_OUTPUT_DIR}" "${PIXAL3D_LOG_DIR}" "${PIXAL3D_CONFIG_DIR}")
fi
if [[ "${data_only}" != "true" ]]; then
  targets+=("${PIXAL3D_INSTALL_ROOT}")
fi

printf 'Would remove:\n'
printf '  %s\n' "${targets[@]}"
printf 'Would preserve shared runtime:\n'
printf '  %s\n' "${PIXAL3D_TRELLIS_VENV_DIR}"
printf '  %s\n' "${PIXAL3D_TRELLIS_RUNTIME_ROOT}/runtime"
printf '  %s\n' "${PIXAL3D_GGUF_RUNTIME_DIR}"
if [[ "${dry_run}" == "true" ]]; then
  exit 0
fi

"${SCRIPT_DIR}/pixal3d_stop.sh" || true
for target in "${targets[@]}"; do
  [[ -n "${target}" && -e "${target}" ]] && rm -rf "${target}"
done
echo "Pixal3D uninstall complete."
echo "Shared TRELLIS.2/Pixal3D runtime preserved at ${PIXAL3D_TRELLIS_VENV_DIR}."
