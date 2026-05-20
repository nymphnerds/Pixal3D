#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_pixal3d_common.sh"

installed=false
runtime_present=false
data_present=false
env_ready=false
adapter_ready=false
runtime_ready=false
models_ready=unknown
aux_models_ready=unknown
quantized_models_ready=false
quantized_runtime_supported=false
api_running=false
gradio_running=false
version=not-installed
health=unavailable
state=available
marker="${PIXAL3D_INSTALL_ROOT}/.nymph-module-version"
detail="Not installed."
quantized_profile_file="${PIXAL3D_CONFIG_DIR}/quantized.env"

if [[ -f "${quantized_profile_file}" ]]; then
  # shellcheck disable=SC1090
  source "${quantized_profile_file}"
fi

if [[ -f "${marker}" ]]; then
  installed=true
  runtime_present=true
  version="$(head -n 1 "${marker}" 2>/dev/null || true)"
  [[ -n "${version}" ]] || version=unknown
  detail="Source installed."
fi

if [[ -d "${PIXAL3D_OUTPUT_DIR}" && -n "$(find "${PIXAL3D_OUTPUT_DIR}" -mindepth 1 -print -quit 2>/dev/null)" ]] ||
   [[ -d "${PIXAL3D_CONFIG_DIR}" && -n "$(find "${PIXAL3D_CONFIG_DIR}" -mindepth 1 -print -quit 2>/dev/null)" ]] ||
   [[ -d "${PIXAL3D_LOG_DIR}" && -n "$(find "${PIXAL3D_LOG_DIR}" -mindepth 1 -print -quit 2>/dev/null)" ]]; then
  data_present=true
fi

if [[ "${installed}" == "true" && -x "$(pixal3d_python)" ]]; then
  env_ready=true
  detail="Runtime environment present."
fi

if [[ "${installed}" == "true" && -f "${PIXAL3D_INSTALL_ROOT}/scripts/api_server_pixal3d.py" ]]; then
  adapter_ready=true
fi

if pixal3d_api_is_running; then
  api_running=true
  if pixal3d_probe_url "${PIXAL3D_SERVER_URL}/server_info" >/dev/null 2>&1; then
    health=ok
  else
    health=unreachable
  fi
fi

if pixal3d_gradio_is_running; then
  gradio_running=true
fi

if [[ "${env_ready}" == "true" && "${adapter_ready}" == "true" ]]; then
  if (
    cd "${PIXAL3D_INSTALL_ROOT}"
    "$(pixal3d_python)" -m py_compile scripts/api_server_pixal3d.py >/dev/null 2>&1
    "$(pixal3d_python)" - <<'PY' >/dev/null 2>&1
import importlib

for module_name in ("fastapi", "uvicorn", "PIL"):
    importlib.import_module(module_name)
PY
  ); then
    runtime_ready=true
    [[ "${health}" != "unreachable" ]] && health=ok
    detail="API wrapper imports are ready."
  else
    health=degraded
    detail="Runtime exists, but API wrapper dependencies are missing."
  fi
fi

pixal3d_cache_repo_present() {
  local cache_name="$1"
  [[ -d "${NYMPHS3D_HF_CACHE_DIR}/${cache_name}/snapshots" ]] &&
    [[ -n "$(find "${NYMPHS3D_HF_CACHE_DIR}/${cache_name}/snapshots" -mindepth 1 -maxdepth 1 -type d -print -quit 2>/dev/null)" ]]
}

pixal3d_cache_snapshot_file_present() {
  local cache_name="$1"
  local relative_path="$2"
  [[ -d "${NYMPHS3D_HF_CACHE_DIR}/${cache_name}/snapshots" ]] &&
    [[ -n "$(find "${NYMPHS3D_HF_CACHE_DIR}/${cache_name}/snapshots" -path "*/${relative_path}" -print -quit 2>/dev/null)" ]]
}

if pixal3d_cache_repo_present "models--TencentARC--Pixal3D"; then
  models_ready=true
else
  models_ready=false
fi

if pixal3d_cache_repo_present "models--Ruicheng--moge-2-vitl" &&
   pixal3d_cache_repo_present "models--camenduru--dinov3-vitl16-pretrain-lvd1689m" &&
   pixal3d_cache_repo_present "models--briaai--RMBG-2.0"; then
  aux_models_ready=true
else
  aux_models_ready=false
fi

if pixal3d_cache_snapshot_file_present "models--Aero-Ex--Pixal3D-GGUF" "Sparse/ss_flow_img_dit_1_3B_64_bf16_${PIXAL3D_QUANT}.gguf" &&
   pixal3d_cache_snapshot_file_present "models--Aero-Ex--Pixal3D-GGUF" "shape/slat_flow_img2shape_dit_1_3B_512_bf16_${PIXAL3D_QUANT}.gguf" &&
   pixal3d_cache_snapshot_file_present "models--Aero-Ex--Pixal3D-GGUF" "shape/slat_flow_img2shape_dit_1_3B_1024_bf16_${PIXAL3D_QUANT}.gguf" &&
   pixal3d_cache_snapshot_file_present "models--Aero-Ex--Pixal3D-GGUF" "texture/slat_flow_imgshape2tex_dit_1_3B_1024_bf16_${PIXAL3D_QUANT}.gguf" &&
   pixal3d_cache_snapshot_file_present "models--Aero-Ex--Pixal3D-GGUF" "decoder/ss_dec_conv3d_16l8_fp16.safetensors" &&
   pixal3d_cache_snapshot_file_present "models--Aero-Ex--Pixal3D-GGUF" "decoder/shape_dec_next_dc_f16c32_fp16.safetensors" &&
   pixal3d_cache_snapshot_file_present "models--Aero-Ex--Pixal3D-GGUF" "decoder/tex_dec_next_dc_f16c32_fp16.safetensors"; then
  quantized_models_ready=true
else
  quantized_models_ready=false
fi

if [[ "${PIXAL3D_QUANT_RUNTIME_SUPPORTED}" == "1" ]]; then
  quantized_runtime_supported=true
fi

if [[ "${installed}" == "true" && "${env_ready}" == "true" &&
      ( "${models_ready}" != "true" || "${aux_models_ready}" != "true" ) ]]; then
  health=model-download-needed
  if [[ "${models_ready}" != "true" && "${aux_models_ready}" != "true" ]]; then
    detail="Pixal3D model files and auxiliary model files need downloading. Use Fetch Models after accepting required access terms."
  elif [[ "${models_ready}" != "true" ]]; then
    detail="Pixal3D model files need downloading. Use Fetch Models after accepting required access terms."
  else
    detail="Pixal3D auxiliary model files need downloading. Use Fetch Models after accepting required access terms."
  fi
fi

service_running=false
if [[ "${api_running}" == "true" || "${gradio_running}" == "true" ]]; then
  service_running=true
fi

if [[ "${installed}" == "true" && "${service_running}" == "true" ]]; then
  state=running
elif [[ "${installed}" == "true" && "${env_ready}" != "true" ]]; then
  state=needs_attention
  health=degraded
  detail="Pixal3D source is installed, but the Python runtime is missing."
elif [[ "${installed}" == "true" && "${adapter_ready}" != "true" ]]; then
  state=needs_attention
  health=degraded
  detail="Pixal3D source is installed, but the API server wrapper is missing."
elif [[ "${installed}" == "true" && "${runtime_ready}" != "true" ]]; then
  state=needs_attention
elif [[ "${installed}" == "true" && ( "${models_ready}" != "true" || "${aux_models_ready}" != "true" ) ]]; then
  state=model_download_needed
  health=model-download-needed
elif [[ "${installed}" == "true" ]]; then
  state=installed
  [[ "${health}" == "unavailable" ]] && health=unknown
elif [[ "${data_present}" == "true" ]]; then
  detail="Pixal3D preserved data remains, but runtime files are not installed."
fi

cat <<EOF
id=pixal3d
name=Pixal3D
installed=${installed}
runtime_present=${runtime_present}
data_present=${data_present}
version=${version}
env_ready=${env_ready}
adapter_ready=${adapter_ready}
runtime_ready=${runtime_ready}
models_ready=${models_ready}
aux_models_ready=${aux_models_ready}
running=${service_running}
api_running=${api_running}
gradio_running=${gradio_running}
state=${state}
health=${health}
url=${PIXAL3D_SERVER_URL}
frontend_url=${PIXAL3D_GRADIO_URL}
install_root=${PIXAL3D_INSTALL_ROOT}
venv=${PIXAL3D_VENV_DIR}
logs_dir=${PIXAL3D_LOG_DIR}
outputs_dir=${PIXAL3D_OUTPUT_DIR}
config_dir=${PIXAL3D_CONFIG_DIR}
hf_cache_dir=${NYMPHS3D_HF_CACHE_DIR}
torch_home=${TORCH_HOME}
profile_file=${PIXAL3D_PROFILE_FILE}
profile=${PIXAL3D_PROFILE:-low_vram_1024}
low_vram=${PIXAL3D_LOW_VRAM}
resolution=${PIXAL3D_RESOLUTION}
weight_format=${PIXAL3D_WEIGHT_FORMAT}
quantized_repo=${PIXAL3D_QUANT_REPO}
quantized_quant=${PIXAL3D_QUANT}
quantized_models_ready=${quantized_models_ready}
quantized_runtime_supported=${quantized_runtime_supported}
marker=${marker}
detail=${detail}
EOF
