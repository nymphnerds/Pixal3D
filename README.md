
<div align="center">

# Pixal3D: Pixel-Aligned 3D Generation from Images

<h3>SIGGRAPH 2026</h3>

<small>[Dong-Yang Li](https://ldyang694.github.io/)¹ · [Wang Zhao](https://thuzhaowang.github.io/)²* · [Yuxin Chen](https://orcid.org/0000-0002-7854-1072)² · [Wenbo Hu](https://wbhu.github.io/)² · [Meng-Hao Guo](https://menghaoguo.github.io/)¹ · [Fang-Lue Zhang](https://fanglue.github.io/)³ · [Ying Shan](https://www.linkedin.com/in/YingShanProfile)² · [Shi-Min Hu](https://cg.cs.tsinghua.edu.cn/shimin.htm)¹✉</small>

¹Tsinghua University (BNRist) &nbsp;&nbsp; ²Tencent ARC Lab &nbsp;&nbsp; ³Victoria University of Wellington

*Project lead &nbsp;&nbsp; ✉Corresponding author

</div>

<div align="center">
  <a href="https://ldyang694.github.io/projects/pixal3d/"><img src=https://img.shields.io/badge/Project%20Page-333399.svg?logo=googlehome height=22px></a>
  <a href="https://huggingface.co/spaces/TencentARC/Pixal3D"><img src=https://img.shields.io/badge/%F0%9F%A4%97%20Demo-276cb4.svg height=22px></a>
  <a href="https://huggingface.co/TencentARC/Pixal3D"><img src=https://img.shields.io/badge/%F0%9F%A4%97%20Models-d96902.svg height=22px></a>
  <a href="https://arxiv.org/abs/2605.10922"><img src=https://img.shields.io/badge/Arxiv-b5212f.svg?logo=arxiv height=22px></a>
  <a href="LICENSE"><img src=https://img.shields.io/badge/License-MIT-yellow.svg height=22px></a>
</div>

<div align="center">
    <img src="assets/teaser.png" alt="Teaser image of Pixal3D"/>
</div>

**Pixal3D** generates high-fidelity 3D assets from a single image. Unlike previous methods that loosely inject image features via attention, Pixal3D explicitly lifts pixel features into 3D through back-projection, establishing direct pixel-to-3D correspondences. This enables near-reconstruction-level fidelity with detailed geometry and PBR textures.

---

## ✨ News

- **May 2026**: Release training code and data preparation toolkit. 🔧
- **May 2026**: Release the improved version based on [Trellis.2](https://github.com/microsoft/TRELLIS.2) backbone. 💪
- **May 2026**: Release inference code and online demo. 🤗
- **Apr 2026**: Our paper is accepted to SIGGRAPH 2026! 🎉

## 📌 Branches

| Branch | Description |
|--------|-------------|
| `main` | **Latest version** — improved implementation based on [Trellis.2](https://github.com/microsoft/TRELLIS.2) backbone with better performance. |
| `paper` | **Paper version** — original implementation based on [Direct3D-S2](https://github.com/DreamTechAI/Direct3D-S2), corresponding to results reported in our SIGGRAPH 2026 paper. |

> If you want to reproduce the results in our paper, please switch to the `paper` branch.

## 🎮 Try It Online

You can try Pixal3D directly in your browser without any installation via our Hugging Face Gradio demo:

👉 [**Launch Demo**](https://huggingface.co/spaces/TencentARC/Pixal3D)

## 🚀 Getting Started

### NymphsCore Module Runtime

The NymphsCore module installer uses one shared native runtime venv for
TRELLIS.2 and Pixal3D:

```text
$HOME/TRELLIS.2/.venv
```

Installing Pixal3D creates or repairs that shared venv automatically if it is
missing. Installing TRELLIS.2 uses the same venv and also leaves it
Pixal3D-ready. Pixal3D does not require TRELLIS model weights; Pixal3D model
files are fetched separately into the shared `NymphsData` cache.

Pixal3D uses the official `utils3d-0.0.2` wheel from the upstream README, then
adds `utils3d.pt` and `utils3d.np` aliases for MoGe auto-camera compatibility.
Do not replace it with MoGe's newer pinned `utils3d` commit for Pixal3D; that
commit lacks `utils3d.torch.intrinsics_from_fov_xy`, which Pixal3D render and
projection paths still call.

Module updates stop the local Pixal3D UI before syncing files or repairing
Python dependencies. This is intentional: a running Gradio/Python process can
keep stale imports alive even after the shared venv has been repaired.
Install/Repair also refreshes module files every time it runs, so retrying after
a failed partial install updates stale UI, script, manifest, and documentation
files before repairing the shared runtime.

The NymphsCore UI is the supported local app surface for this module. It exposes
optimized run profiles for 16 GB GPUs, the low-VRAM toggle, max-token budget,
texture NAF size, face target, texture size, per-stage sampling controls, and a
manual **Free Pipeline** action for clearing cached models before higher-risk
runs. The upstream HTML app is kept in the repository only as reference code.

The NymphsCore runtime is performance-first and expects `flash_attn` to be
installed in the shared venv. Do not treat SDPA/naive attention as a normal
generation path for this module.

Pixal3D also builds the Pixal-specific `nvdiffrec_render` helper into the shared
venv. On WSL, that build must link against the NVIDIA driver stub in
`/usr/lib/wsl/lib`; the installer adds that library path only for this renderer
build.

### Installation

#### Step 1: Follow TRELLIS.2 Installation

Please first follow the installation guide of [TRELLIS.2](https://github.com/microsoft/TRELLIS.2) to set up the base environment.

#### Step 2: Install Additional Dependencies

```bash
pip install -r requirements.txt
```

#### Step 3: Install natten

```bash
NATTEN_CUDA_ARCH="xx" NATTEN_N_WORKERS=xx pip install natten==0.21.0 --no-build-isolation
```

Please replace `xx` with the CUDA architecture and the number of build workers suitable for your machine.

#### Step 4: Install utils3d

```bash
pip install https://github.com/LDYang694/Storages/releases/download/20260430/utils3d-0.0.2-py3-none-any.whl
```

> **Note**: `requirements-hfdemo.txt` is for the Hugging Face Spaces demo (H-series GPU architecture) and may not be compatible with other architectures.

### Usage

#### Inference

Generate a GLB mesh from a single image:

```bash
python inference.py --image assets/images/0_img.png --output ./output.glb
```

**Low-VRAM mode** (reduces peak VRAM by loading models on-demand):

```bash
python inference.py --image assets/images/0_img.png --output ./output.glb --low_vram
```

By default, the pipeline resolution is **1536** (standard mode) or **1024** (low-VRAM mode). You can override this with `--resolution`:

```bash
# Force 1536 even in low-VRAM mode
python inference.py --image assets/images/0_img.png --output ./output.glb --low_vram --resolution 1536

# Force 1024 in standard mode
python inference.py --image assets/images/0_img.png --output ./output.glb --resolution 1024
```

For the NymphsCore module, `flash_attn` is required for the supported fast path.

### NymphsCore Web UI

The local server opens the NymphsCore Pixal3D UI, which is the supported module
interface for interactive generation and testing.

```bash
python app.py 
```

Low-VRAM mode is available for the NymphsCore UI. The profile selector provides
`Preview 16GB`, `Balanced 16GB`, `Quality 16GB`, and `1536 High VRAM` presets;
changing individual controls switches the run to `Custom`.

```bash
python app.py --low_vram
# or via environment variable:
LOW_VRAM=1 python app.py
```

To compare profiles against one image and write JSONL timing/results records:

```bash
scripts/benchmark_pixal3d_profiles.py --image assets/images/0_img.png --profiles preview_16gb balanced_16gb
```
## 🔧 Training

We provide the full training codebase for reproducing Pixal3D from scratch.

### Data Preparation

Prepare view-aligned O-Voxel data and rendered condition images by following the data toolkit instructions:

> 📂 **[data_toolkit/README.md](data_toolkit/README.md)**

### Overview

Pixal3D is trained as a three-stage cascade, each progressively increasing resolution:

| Stage | Model | Resolutions | Config Prefix |
|-------|-------|-------------|---------------|
| 1 | Sparse Structure | 32 → 64 | `ss_flow_img_dit_*_proj_finetune` |
| 2 | Shape | 256 → 512 → 1024 | `slat_flow_img2shape_*_proj_finetune` |
| 3 | Texture | 256 → 512 → 1024 | `slat_flow_imgshape2tex_*_proj_finetune` |

All stages use **pixel-aligned projection conditioning** and **view-aligned latents** (2 views by default). Within each stage, start from the lowest resolution and progressively fine-tune to higher resolutions by setting `finetune_ckpt` in the config.

### Quick Start

```sh
python train.py \
  --config <CONFIG_JSON> \
  --output_dir <OUTPUT_DIR> \
  --data_dir '<DATA_DIR_JSON>'
```

`--data_dir` is a JSON string describing the dataset layout. Different stages require different keys:

| Stage | Required keys |
|-------|---------------|
| Sparse Structure | `base`, `ss_latent`, `render_cond` |
| Shape | `base`, `shape_latent`, `render_cond` |
| Texture | `base`, `shape_latent`, `pbr_latent`, `render_cond` |

### Example: Training All Three Stages

Below we show the full training sequence using ObjaverseXL as an example. Each higher-resolution step requires updating `finetune_ckpt` in its config JSON to point to the previous checkpoint.

<details>
<summary><b>Stage 1: Sparse Structure (32 → 64)</b></summary>

```sh
# Resolution 32
python train.py \
  --config configs/gen/ss_flow_img_dit_1_3B_32_bf16_proj_finetune.json \
  --output_dir results/ss_32 \
  --data_dir '{"ObjaverseXL_sketchfab": {"base": "datasets/ObjaverseXL_sketchfab", "ss_latent": "datasets/ObjaverseXL_sketchfab/ss_latents/ss_enc_conv3d_16l8_fp16_64_view", "render_cond": "datasets/ObjaverseXL_sketchfab/renders_cond"}}'

# Resolution 64 (set finetune_ckpt → results/ss_32 checkpoint)
python train.py \
  --config configs/gen/ss_flow_img_dit_1_3B_32_bf16_proj_finetune_ft64.json \
  --output_dir results/ss_ft64 \
  --data_dir '{"ObjaverseXL_sketchfab": {"base": "datasets/ObjaverseXL_sketchfab", "ss_latent": "datasets/ObjaverseXL_sketchfab/ss_latents/ss_enc_conv3d_16l8_fp16_64_view", "render_cond": "datasets/ObjaverseXL_sketchfab/renders_cond"}}'
```
</details>

<details>
<summary><b>Stage 2: Shape (256 → 512 → 1024)</b></summary>

```sh
# Resolution 256
python train.py \
  --config configs/gen/slat_flow_img2shape_dit_1_3B_256_bf16_proj_finetune.json \
  --output_dir results/shape_256 \
  --data_dir '{"ObjaverseXL_sketchfab": {"base": "datasets/ObjaverseXL_sketchfab", "shape_latent": "datasets/ObjaverseXL_sketchfab/shape_latents/shape_enc_next_dc_f16c32_fp16_256_view", "render_cond": "datasets/ObjaverseXL_sketchfab/renders_cond"}}'

# Resolution 512
python train.py \
  --config configs/gen/slat_flow_img2shape_dit_1_3B_256_bf16_proj_finetune_ft512.json \
  --output_dir results/shape_ft512 \
  --data_dir '{"ObjaverseXL_sketchfab": {"base": "datasets/ObjaverseXL_sketchfab", "shape_latent": "datasets/ObjaverseXL_sketchfab/shape_latents/shape_enc_next_dc_f16c32_fp16_512_view", "render_cond": "datasets/ObjaverseXL_sketchfab/renders_cond"}}'

# Resolution 1024
python train.py \
  --config configs/gen/slat_flow_img2shape_dit_1_3B_512_bf16_proj_finetune_ft1024.json \
  --output_dir results/shape_ft1024 \
  --data_dir '{"ObjaverseXL_sketchfab": {"base": "datasets/ObjaverseXL_sketchfab", "shape_latent": "datasets/ObjaverseXL_sketchfab/shape_latents/shape_enc_next_dc_f16c32_fp16_1024_view", "render_cond": "datasets/ObjaverseXL_sketchfab/renders_cond"}}'
```
</details>

<details>
<summary><b>Stage 3: Texture (256 → 512 → 1024)</b></summary>

```sh
# Resolution 256
python train.py \
  --config configs/gen/slat_flow_imgshape2tex_dit_1_3B_256_bf16_proj_finetune.json \
  --output_dir results/tex_256 \
  --data_dir '{"ObjaverseXL_sketchfab": {"base": "datasets/ObjaverseXL_sketchfab", "shape_latent": "datasets/ObjaverseXL_sketchfab/shape_latents/shape_enc_next_dc_f16c32_fp16_256_view", "pbr_latent": "datasets/ObjaverseXL_sketchfab/pbr_latents/tex_enc_next_dc_f16c32_fp16_256_view", "render_cond": "datasets/ObjaverseXL_sketchfab/renders_cond"}}'

# Resolution 512
python train.py \
  --config configs/gen/slat_flow_imgshape2tex_dit_1_3B_512_bf16_proj_finetune.json \
  --output_dir results/tex_512 \
  --data_dir '{"ObjaverseXL_sketchfab": {"base": "datasets/ObjaverseXL_sketchfab", "shape_latent": "datasets/ObjaverseXL_sketchfab/shape_latents/shape_enc_next_dc_f16c32_fp16_512_view", "pbr_latent": "datasets/ObjaverseXL_sketchfab/pbr_latents/tex_enc_next_dc_f16c32_fp16_512_view", "render_cond": "datasets/ObjaverseXL_sketchfab/renders_cond"}}'

# Resolution 1024
python train.py \
  --config configs/gen/slat_flow_imgshape2tex_dit_1_3B_512_bf16_proj_finetune_ft1024.json \
  --output_dir results/tex_ft1024 \
  --data_dir '{"ObjaverseXL_sketchfab": {"base": "datasets/ObjaverseXL_sketchfab", "shape_latent": "datasets/ObjaverseXL_sketchfab/shape_latents/shape_enc_next_dc_f16c32_fp16_1024_view", "pbr_latent": "datasets/ObjaverseXL_sketchfab/pbr_latents/tex_enc_next_dc_f16c32_fp16_1024_view", "render_cond": "datasets/ObjaverseXL_sketchfab/renders_cond"}}'
```
</details>

### Additional Options

<details>
<summary><b>All command-line arguments</b></summary>

| Argument | Description | Default |
|----------|-------------|---------|
| `--config` | Config JSON path | *required* |
| `--output_dir` | Output directory | *required* |
| `--data_dir` | Dataset JSON string | `./data/` |
| `--load_dir` | Checkpoint load directory | `output_dir` |
| `--ckpt` | Resume from step | `latest` |
| `--auto_retry` | Retries on failure | `3` |
| `--tryrun` | Dry run | `false` |
| `--profile` | Profiling | `false` |
| `--num_nodes` | Number of nodes | `1` |
| `--node_rank` | Current node rank | `0` |
| `--num_gpus` | GPUs per node | all |
| `--master_addr` | Master address | `localhost` |
| `--master_port` | Master port | `12666` |
| `--use_wandb` | Enable W&B logging | `false` |
| `--wandb_project` | W&B project | `trellis2-training` |
| `--wandb_name` | W&B run name | basename of `output_dir` |
| `--wandb_id` | W&B run ID (resume) | — |

</details>

## 🌐 Community Projects

We thank the community for building extensions and deployment guides for Pixal3D!

- [Pixal3D-ComfyUI](https://github.com/Saganaki22/Pixal3D-ComfyUI) — ComfyUI integration with deployment guides for Windows, WSL, and more.

## 🤗 Acknowledgements

This project is heavily built upon [Trellis.2](https://github.com/microsoft/TRELLIS.2) and [Direct3D-S2](https://github.com/DreamTechAI/Direct3D-S2). We sincerely thank the authors for their outstanding work on scalable 3D generation , which serves as the foundation of our codebase and model architecture.

We also thank the following repos for their great contributions:

- [Direct3D-S2](https://github.com/DreamTechAI/Direct3D-S2)
- [Trellis](https://github.com/microsoft/TRELLIS)
- [Trellis.2](https://github.com/microsoft/TRELLIS.2)

## 📄 Citation

If you find this work useful, please consider citing:

```bibtex
@article{li2026pixal3d,
    title={Pixal3D: Pixel-Aligned 3D Generation from Images},
    author={Li, Dong-Yang and Zhao, Wang and Chen, Yuxin and Hu, Wenbo and Guo, Meng-Hao and Zhang, Fang-Lue and Shan, Ying and Hu, Shi-Min},
    journal={arXiv preprint arXiv:2605.10922},
    year={2026}
}
```

## 📜 License

This project is released under the [MIT License](LICENSE). The third-party components included in this project remain licensed under their respective original terms; see [NOTICE](NOTICE) for the full list of dependencies and their licenses.
