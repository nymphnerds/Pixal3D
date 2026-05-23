# Pixal3D Module And Blender Addon Handoff

Date: 2026-05-17

Canonical location: `/home/nymph/Pixal3D/docs/pixal3d_module_handoff.md`.
Older mirrored copies were removed to keep the Pixal3D handoff single-source.

Updated: 2026-05-19 after merging upstream `TencentARC/Pixal3D` through
`e3b2ac1` (`docs: add natten installation step in README`). The fork now
includes the official Pixal3D training pipeline and data preparation toolkit.

Updated: 2026-05-21 after web research on Pixal3D low-VRAM/ComfyUI work and
the shared TRELLIS.2/Pixal3D runtime uninstall problem.

Updated: 2026-05-21 after Manager self-update testing. Manager now reads a
top-level `manager` entry from `nymphs-registry/nymphs.json` using the same raw
registry fetch as modules. Tested flow: copied an older Manager release out of
the repo publish folder, bumped/published a newer Manager release, updated the
registry entry, waited for raw registry propagation, then saw
`local old | remote new | Update`. Do not test Manager update availability by
launching `NymphsCore/Manager/apps/NymphsCoreManager/publish/win-x64` directly;
that is the fresh dev build. Watch item: one launch briefly reported zero
installed module markers after mixed Desktop-release/dev-publish launch testing;
reopening showed all six modules installed/current again.

Updated: 2026-05-21 after Pixal3D `0.1.76`. Warmup/runtime setting changes now
use a clean backend process boundary: **Warm Up** restarts/reconnects the
backend automatically when Low VRAM, Texture NAF, or a runtime preset changes
after a previous warmup. **Clear GPU Memory** is the manual clean reset path.

Updated: 2026-05-22 after Pixal3D `0.1.77`. `Open GLB` and
`Clear GPU Memory` now live in the top command strip, `Use GPU for RMBG`
defaults on, and closing the Nymphs UI/WebView asks Pixal3D to stop all module
backends through the normal stop script.

Updated: 2026-05-22 after Pixal3D `0.1.78`. The top command strip now groups
`Warm Up` / `Generate` / `Export` separately from the lower-priority
`Open GLB` / `Clear GPU Memory` utilities.

Updated: 2026-05-22 after Pixal3D `0.1.79`. `Use GPU for RMBG` is forced on
when the Nymphs UI loads, even if a stale running process reports the previous
RMBG env state as off. The command rows were also aligned into full-width
source, run, and utility rows so they read more neatly in the fixed rail.

Updated: 2026-05-22 after Pixal3D `0.1.80`. Added a Manager `Kill` action
mapped to `scripts/pixal3d_stop.sh`. This is intentionally separate from the
web UI so it remains usable when FastAPI is blocked inside a long export.

Updated: 2026-05-22 after Pixal3D `0.1.81`. Moved the user-facing kill switch
into the Pixal3D UI command block, removed visible outer `Kill`/`Stop` module
buttons, changed embedded UI close to run the module `kill` action, and
compacted the in-UI source/run/utility command rows.

Updated: 2026-05-22 after Pixal3D `0.1.82`. Fixed the killed-during-warmup UI
state: Kill now clears stale warmup/progress timers, leaves Warm enabled, and
Warm restarts the backend through the module action bridge before warming.

Updated: 2026-05-22 after Pixal3D `0.1.83`. Clarified the killed-state recovery:
users stay in the same Pixal3D UI. After Kill, pressing Warm starts Pixal3D
again, reconnects, and warms without telling the user to reopen the UI.

Updated: 2026-05-22 after Pixal3D `0.1.84`. Moved blocking Nymph UI API calls
onto worker threads so the FastAPI event loop can keep answering `/progress`
during generation/export. The UI can now show backend stages instead of sitting
at `Queued`.

Updated: 2026-05-22 after Pixal3D `0.1.85`. Added conservative per-run CUDA
cleanup and memory breadcrumbs around MoGe camera estimation, latent generation,
and GLB export. This is aimed at the common second-run OOM failure without
changing install/runtime dependencies.

Updated: 2026-05-22 after Pixal3D `0.1.86`. Clarified in install-facing copy
that Fetch Models later downloads `briaai/RMBG-2.0`, and that users must accept
the BRIA Hugging Face access form with the same account used for the saved token
before Fetch Models can complete. The details-page BRIA link is labeled as the
next step.

Updated: 2026-05-22 after Pixal3D `0.1.88`. Added a module-owned installed
`NEXT STEP` action group that opens the BRIA form before Fetch Models. Keep this
in Pixal3D's `nymph.json`; do not hardcode Pixal3D/BRIA details in Manager.

Updated: 2026-05-22 after Pixal3D `0.1.89`. Moved the BRIA form prompt to
`ui.detail_primary_action` so the module owns the Details-pane `NEXT STEP`
button while Manager owns only the generic slot. The prompt is temporary and
shows only while Pixal3D reports `model_download_needed`.

Updated: 2026-05-22 after Pixal3D `0.1.90`. Kept the details copy minimal and
allowed the BRIA form action to remain visible during status timeout/checking so
the form link is not hidden when the module is still sorting itself out.

Updated: 2026-05-22 after Pixal3D `0.1.91`. Clarified the first/pre-install
details page: before Fetch Models, users must open the BRIA form and accept
access with the same Hugging Face account used for their token.

Updated: 2026-05-22 after Pixal3D `0.1.92`. Removed GGUF choices from the
normal Fetch Models UI/status because the released Pixal3D path only needs the
safetensors model caches right now. BRIA RMBG failures now emit a short
machine-readable next step so Manager can show `Fill BRIA form` instead of a
generic model-fetch failure.

Updated: 2026-05-22 after Pixal3D `0.1.93`. Fixed the normal Fetch Models
wrapper so `snapshot_download` receives `repo_id` only once, then fixed status
so the shared Low VRAM 1024/Standard 1536 safetensors profiles remain visible
as cached when only BRIA RMBG is missing.

Updated: 2026-05-22 after Pixal3D `0.1.94`. Tightened the available-state
Details copy so the official Pixal3D description and BRIA setup step do not
repeat each other.

Updated: 2026-05-22 after Pixal3D `0.1.95`. Restored the old module action
pattern: Model Fetch remains available after weights are cached, while only the
temporary BRIA `NEXT STEP` prompt is state-gated.

Updated: 2026-05-22 after Pixal3D `0.1.96`. Restored the install heading to
plain `INSTALL OPTIONS` so BRIA guidance stays with Details/Model Fetch, and
made fresh installs add the Python 3.10 apt source fallback before creating the
shared runtime venv.

Updated: 2026-05-22 after Pixal3D `0.1.97`. Added a short Details-pane note
explaining that the install options control the FlashAttention build, with
Auto-detect recommended and lower Max jobs/NVCC threads suggested after memory
failures.

Updated: 2026-05-22 after Pixal3D `0.1.98`. Fixed standalone shared-venv
install order: Pixal3D can install `utils3d` before `nvdiffrast` exists, then
the final full runtime validation checks `utils3d.pt` after native TRELLIS
extensions have been built.

Updated: 2026-05-22 after Pixal3D `0.1.99`. Made standalone Pixal3D install
self-heal a missing CUDA 13 toolkit/nvcc before building FlashAttention, using
the same WSL CUDA repository/keyring path as Base Runtime.

Updated: 2026-05-23 after Pixal3D `0.1.100` and `0.1.101` repeat-run crash
work. Detailed findings are in
`docs/pixal3d_second_run_oom_findings_2026-05-23.md`. Short version: the first
Manager generation/export can complete, but the second generation can still
crash WSL without a Python traceback. `0.1.100` reduced Manager CUDA pressure by
skipping the first decode/render path and clearing sparse/mesh state. `0.1.101`
copied the official UI model-viewer reset behavior so stale GLB/WebGL scenes are
not retained. The remaining failure looks like reuse of the same long-lived
Python/CUDA process after one complete Pixal3D run. Official upstream local
`app.py` has the same architecture and does not recycle the CUDA process between
runs. Next recommended fix: keep FlashAttention enabled, but automatically
recycle/reconnect/prewarm the backend after successful export so a second
generation never runs in the spent CUDA process.

## Goal

Research whether TencentARC/Pixal3D can become a Nymph module, whether it can
use the current TRELLIS GGUF fork as its backbone/runtime, and what the Blender
addon needs to expose it cleanly.

Short answer:

- A Pixal3D module is feasible.
- Pixal3D should be treated as requiring a TRELLIS.2-style backbone/runtime
  environment, not the current TRELLIS GGUF adapter runtime.
- Pixal3D inference appears to use `TencentARC/Pixal3D` checkpoints and does not
  appear to require the full regular `microsoft/TRELLIS.2-4B` release weights as
  a separate inference dependency.
- The Blender addon should treat Pixal3D as a separate 3D runtime/backend, not
  as another GGUF quant under the existing TRELLIS.2 GGUF runtime.
- New upstream training support is real, but it should not be folded into the
  first Blender inference module. Treat training as a later Pixal3D Trainer
  sidecar or module because it has different data, storage, runtime, and UX
  needs.
- The existing Nymph LoRA module cannot directly train Pixal3D. It is a
  Z-Image Turbo LoRA trainer using AI Toolkit. Its Manager/job UX patterns are
  useful, but Pixal3D training is full 3D flow-model training, not a Z-Image
  LoRA adapter workflow.

## Build Handoff V1: Achievable Implementation Plan

This is the implementation-grade plan. The research notes below explain why
these decisions were made; this section is what to hand to the implementer.

### Current Implementation Status 2026-05-19

The Pixal3D fork is now merged with upstream `TencentARC/Pixal3D` through
`e3b2ac1` and includes the official training pipeline, NATTEN install doc
change, and Nymph module wrapper.

Implemented in the Pixal3D module:

- `nymph.json` declares `pixal3d` as a repo-packaged `3d` module with API port
  `8096` and Gradio/WebView port `8097`.
- The module detail overview includes Pixal3D academic/non-commercial terms,
  the not-for-EU license wording, the BRIA RMBG-2.0 gated model notice, and a
  direct BRIA access form link: `https://huggingface.co/briaai/RMBG-2.0`.
- Lifecycle scripts now cover install, update, status, start, stop, logs,
  smoke test, model fetch, Gradio launch, weights folder, outputs folder, and
  uninstall.
- `scripts/api_server_pixal3d.py` exposes the Blender-compatible API surface:
  `/health`, `/server_info`, `/active_task`, and `/generate`.
- `scripts/gradio_pixal3d_module.py` launches the local Gradio test UI that the
  Manager can open inside the module details WebView.
- `app.py` and `inference.py` were adjusted so the module can run with explicit
  host/port/lazy-load settings and Blender-friendly GLB export knobs.
- Model fetch uses the shared `NymphsData` Hugging Face/Torch caches and can
  read the Manager-managed Hugging Face secret without printing the token.
- Fetch Models refuses to run unless `--license-ack yes` is supplied.

Local validation passed on 2026-05-19:

```text
bash -n scripts/*.sh
python -m py_compile scripts/api_server_pixal3d.py scripts/gradio_pixal3d_module.py app.py inference.py
python -m json.tool nymph.json
scripts/pixal3d_smoke_test.sh
scripts/pixal3d_status.sh
curl http://127.0.0.1:8096/health
curl http://127.0.0.1:8096/server_info
curl -I http://127.0.0.1:8097
```

Current local runtime state from `pixal3d_status.sh`:

```text
installed=true
env_ready=true
adapter_ready=true
runtime_ready=true
models_ready=true
aux_models_ready=true
running=true
api_running=true
gradio_running=true
health=ok
profile=low_vram_1024
resolution=1024
venv=/home/nymph/TRELLIS.2/.venv
```

Update 2026-05-20:

- The existing safetensors runtime remains the default and is still the only
  supported generation path.
- `Fetch Models` now includes experimental GGUF profile choices in the same
  profile dropdown: `GGUF Q5_K_M`, `GGUF Q6_K`, and `GGUF Q8_0`.
- These profiles fetch community quantized weights from
  `Aero-Ex/Pixal3D-GGUF` into the shared Hugging Face cache and record
  `NymphsData/config/pixal3d/quantized.env`.
- The Pixal3D API reports `weight_format`, `quant_repo`, `quant`, and
  `quant_runtime_supported` through `/server_info`.
- `quant_runtime_supported=false` is intentional. The current Pixal3D model
  loader still expects `.safetensors` via `pixal3d/models/__init__.py`; GGUF
  generation requires a loader bridge/adaptation before it can replace any flow
  model stage.
- If `PIXAL3D_WEIGHT_FORMAT` is manually set away from `safetensors`, `/generate`
  now returns HTTP 501 with an explicit "GGUF loader support is not implemented
  yet" message instead of failing obscurely inside model loading.

Update 2026-05-21 low-VRAM research:

- Official Pixal3D now documents low-VRAM inference and web demo support.
  Low-VRAM mode defaults to `1024` resolution, while standard mode defaults to
  `1536`.
- Official Pixal3D also documents `ATTN_BACKEND=sdpa` as an emergency fallback
  if flash-attn is unavailable. The Nymph module should keep flash-attn as the
  normal path, but this is useful diagnostic information.
- The upstream Hugging Face model card says May 2026 brought the improved
  TRELLIS.2-based implementation, inference/demo release, and training code.
- The upstream repository `LICENSE` is MIT for Tencent-published code, weights,
  parameters, and documentation. `NOTICE` says third-party components keep their
  own licenses; current third-party attributions include DINOv2 under Apache-2.0
  and TRELLIS.2, Direct3D-S2, and MoGe under MIT.
- No mature Pixal3D GGUF runtime equivalent to `Aero-Ex/Trellis2-GGUF` was found
  during the search. Treat Pixal3D GGUF as an experimental future branch, not a
  module dependency.
- `city96/ComfyUI-GGUF` confirms the general reason GGUF may eventually help:
  transformer/DiT models tend to tolerate quantization better than conv-heavy
  UNet-style models. Pixal3D has DiT stages, but a loader bridge is still needed
  before the downloaded Pixal3D GGUF weights can replace safetensors stages.

Community low-VRAM/ComfyUI findings:

- `Saganaki22/Pixal3D-ComfyUI` is now listed by upstream as a community project.
  Useful ideas to borrow:
  - Environment Check node that reports missing CUDA/runtime pieces before
    model load.
  - Explicit Unload Model node that clears Pixal3D pipeline cache and releases
    model handles.
  - Manual camera mode/FOV controls as an alternative to MoGe camera estimation.
  - FlashAttention 2/3 selection and `natten` fallback modes.
  - Troubleshooting guidance: do not let pip replace a working Torch install
    when testing random CUDA wheels; use `--no-deps` for manual CUDA wheels.
- `dreamrec/ComfyUI-Pixal3D` has the most useful 16GB tuning table found:
  - `1024_cascade`, `low_vram=true`, 12/12/12 steps, 32k tokens, 200k decim,
    2048 texture: about 14GB peak, around 3 minutes warm, described as balanced
    for 16GB cards.
  - `1024_cascade`, `low_vram=true`, 8/8/8 steps, 16k tokens: about 10GB peak,
    around 1.5-2 minutes warm, useful as a preview/tight-card mode.
  - `1024_cascade`, `low_vram=true`, 16/16/16 steps, 32k tokens, 4096 texture:
    about 17GB peak, so it may work on 16GB only with enough allocator headroom
    and no memory fragmentation.
  - `1536_cascade` with `low_vram=true` can work on RTX 5090-class cards but is
    around 32GB peak, not a target for RTX 4080 SUPER 16GB.
- `Rizzlord/ComfyUI-Pixal3D-D` looks like a different/experimental Pixal3D-D
  line, but its UX ideas are interesting: keep-model-loaded toggle, complete
  purge after generation, and 1024 refinement mode where `refine` is suggested
  for 16GB while `full` is for 24GB+.

Proposed Nymph 16GB profile plan:

- Add an explicit "4080S / 16GB Balanced" profile once the current install path
  is stable.
- Suggested defaults:
  - `low_vram=true`
  - `resolution=1024`
  - cascade/profile: `1024_cascade` if upstream exposes a clean switch
  - steps: start with 8/8/8 preview and 12/12/12 balanced
  - max tokens: 16k preview, 32k balanced
  - decimation: 200k balanced, 300k only after stable
  - texture: 2048 balanced, 4096 only after stable
  - keep warm/model cache off by default for 16GB until fragmentation behavior is
    measured
- Add or expose a "Free Pipeline" / "Unload Model" action before attempting
  higher-quality reruns on 16GB.
- Keep the safetensors path as the first stable 16GB target. Defer Pixal3D GGUF
  runtime work until we have a reliable safetensors baseline and a confirmed
  GGUF loader strategy.

Shared-runtime uninstall fix 2026-05-21:

- TRELLIS.2 `0.1.27` default uninstall now preserves
  `$HOME/TRELLIS.2/.venv`, `$HOME/TRELLIS.2/runtime`, and
  `$HOME/TRELLIS.2/.cache` when Pixal3D appears installed.
- TRELLIS.2 `--purge` still removes the full install root, but warns when
  Pixal3D appears installed because purge removes the shared runtime.
- Pixal3D `0.1.53` uninstall metadata/output now explicitly says the shared
  TRELLIS.2/Pixal3D runtime is preserved.
- Registry `69` publishes TRELLIS.2 `0.1.27` and Pixal3D `0.1.53`.
- Validation performed before push:
  - `bash -n` on affected uninstall/common scripts
  - `python3 -m json.tool` on manifests and registry
  - `git diff --check`
  - temp-tree destructive uninstall test proving TRELLIS preserves `.venv`,
    `runtime`, `.cache`, outputs, and logs while deleting wrapper files when
    Pixal3D is installed.

Nymph UI optimization implementation 2026-05-21:

- The NymphsCore UI is now the only advertised Pixal3D app surface. The
  upstream/official UI files remain in the repo only as reference code.
- `/`, `/nymph`, and `/official` all serve the Nymph UI so old launch paths do
  not accidentally open the reference UI.
- Added shared run profile definitions in `pixal3d_profiles.py`:
  - `preview_16gb`: 1024 low-VRAM, 8/8/8 steps, 16k tokens.
  - `balanced_16gb`: 1024 low-VRAM, 12/12/12 steps, 32k tokens, 200k faces,
    2048 texture.
  - `quality_16gb`: 1024 low-VRAM, 16/16/16 steps, 32k tokens, 300k faces,
    4096 texture, 768 texture NAF.
  - `high_vram_1536`: 1536 high-VRAM, 16/16/16 steps, 49k tokens, 4096 texture.
- Nymph UI now exposes run profile, low-VRAM mode, max tokens, texture NAF,
  face target, texture size, per-stage steps, and the existing guidance/camera
  controls. Manual edits switch the run profile to `Custom`.
- Added a `Free Pipeline` frontend action backed by `free_pipeline_api` to clear
  cached Pixal3D/MoGe/envmap state and release CUDA memory before a higher-risk
  run.
- Removed the default CUDA allocator fraction cap. `PIXAL3D_CUDA_MEMORY_FRACTION`
  is still honored if explicitly set, but no cap is applied by default.
- GLB export now uses PNG textures (`extension_webp=False`) for viewer/Blender
  compatibility.
- Added `scripts/benchmark_pixal3d_profiles.py` to run selected profiles against
  one image and append JSONL records with elapsed time, success/failure, output
  path, settings, and `nvidia-smi` memory samples.
- Follow-up install fix: `nvdiffrec_render` compiled its CUDA objects on WSL but
  failed the final link with `/usr/bin/ld: cannot find -lcuda`. The NVIDIA
  driver stub exists at `/usr/lib/wsl/lib/libcuda.so`, so `v0.1.55` adds that
  path to `LIBRARY_PATH` and `LD_LIBRARY_PATH` only for the
  `nvdiffrec_render` build. Dev validation built and imported
  `nvdiffrec_render.light` and `nvdiffrec_render.renderutils._C` successfully.
- Follow-up partial-install fix: the first failed Pixal3D `0.1.55` retry wrote
  the `0.1.55` marker after runtime repair but left `nymph.json` at `0.1.54`
  because the installer only synced files when `pixal3d/` was missing.
  `v0.1.56` refreshes module files on every install/repair before runtime work.
- Follow-up Nymph UI startup fix: the shared TRELLIS.2/Pixal3D venv upgraded to
  Gradio `6.0.1`, where `gradio.Server` and `app.api()` are no longer available
  in the old form. `v0.1.57` keeps the Nymph UI as the only active browser
  surface by serving it through the FastAPI/uvicorn app and moving the frontend
  calls to direct `/api/preprocess`, `/api/generate_3d`,
  `/api/extract_glb_api`, and `/api/free_pipeline_api` endpoints instead of
  depending on `@gradio/client`.
- Follow-up Nymph UI clarity fix: `v0.1.58` widens the Run Profile selector,
  places Resolution next to the Low VRAM checkbox, renames the noob-hostile
  "Free Pipeline" action to "Clear GPU Memory", and stops stale source-prep
  progress from lingering after source preparation is disabled.
- Follow-up module action fix: `v0.1.59` adds a visible `Stop` module action
  that runs the module `stop` entrypoint, so users can stop Pixal3D from the
  module actions row without opening the side manage menu.
- Follow-up warmup UX fix: `v0.1.60` adds a manual `Warm Up` control in the
  NymphsCore UI. It calls a new backend warmup endpoint, shows model loading in
  the header and progress strip, and leaves the existing optional warm-on-open
  path available for future defaults/settings.
- Follow-up warmup/state fix: `v0.1.61` gives warmup a dedicated top progress
  strip, keeps source prep/generation/export progress below the preview, and
  gates source prep plus `Generate Preview` until warmup is ready. It also
  widens the locked Pixal3D control column, enlarges the source preview,
  compacts control buttons, and renames runtime presets with explicit settings
  such as `1024 low-VRAM / 12 steps`.
- Follow-up official-like flow fix: `v0.1.62` auto-starts warmup when the
  NymphsCore UI opens. Users can select an image while warmup runs; source prep
  starts after warmup is ready, `Generate Preview` unlocks after prep, and prep
  failures expose the backend error with `Retry Prep` and `Clear Source`
  controls instead of trapping the UI.
- Follow-up manual prep fix: `v0.1.63` keeps auto-warmup but makes source prep
  explicit. After selecting an image, the user clicks `Prepare Source`; failed
  prep keeps the same button available as `Retry Prep`. The warmup strip stays
  warmup-only, runtime presets update the Low VRAM checkbox correctly, and the
  source preview uses a portrait-friendly shape.
- Follow-up UI reset: `v0.1.67` saves the last usable pre-restyle UI from
  `0.1.63` as `docs/backups/nymph_pixal3d_legacy_0.1.63.html`, then replaces
  `nymph_pixal3d.html` with a new shell. The new shell keeps the working API
  script/DOM IDs, but moves advanced parameters behind a collapsed section,
  restores compact inline Manager-style commands, and avoids boxed command
  panels or a full-page source drop zone.
- Follow-up shell sizing fix: `v0.1.68` narrows the locked Pixal work rail,
  tightens command button widths, and fixes the result/GLB preview pane so it
  fills the available vertical grid area instead of collapsing to the empty
  message.
- Follow-up fixed rail fix: `v0.1.69` changes the Pixal work rail from a
  viewport-responsive width to a fixed `400px` column so it no longer resizes
  and the right preview keeps stable space.
- Follow-up compact rail fix: `v0.1.70` narrows the Pixal work rail to `360px`,
  removes the divider lines around the run-command buttons, and makes the
  source/run command buttons square tool buttons.
- Follow-up preview square fix: `v0.1.71` corrects the mistaken button-square
  change. Source/run buttons are compact horizontal commands again, and the
  source image preview/drop zone is the square element. The source and run
  command rows use thin fitted button strips inside the locked rail.
- Follow-up runtime-state hardening: `v0.1.75` prevents source replacement and
  GPU-memory clearing during active work, vendors the `model-viewer`/Lucide
  browser assets locally, shows the prepared image in the existing source pane
  after `Prepare Source`, preserves low-VRAM/Texture NAF settings through GLB
  export, and surfaces generation/export backend errors in the UI.
- Follow-up restart-safe warmup: `v0.1.76` adds deeper startup progress before
  the heavy generation call, reduces the ready warmup copy to `Warmed`,
  preserves the current GLB when the same source image is touched/selected
  again, and makes runtime-memory setting changes safe by restarting and
  reconnecting the backend before warming with the new settings.

The production module contract now intentionally uses the shared
`$HOME/TRELLIS.2/.venv` runtime. Pixal3D and TRELLIS.2 both create/repair that
same native CUDA/runtime venv, so whichever module is installed first prepares
the runtime for both modules. Pixal3D does not require TRELLIS model weights.

Install repair note:

- Pixal3D does not vendor TRELLIS.2 `o-voxel` source directly. When the shared
  runtime needs native `o_voxel`, Pixal3D install/repair fetches the official
  `microsoft/TRELLIS.2` runtime source into
  `$HOME/TRELLIS.2/runtime/TRELLIS.2-source`, initializes its Eigen submodule,
  and builds `o_voxel` from there.
- Do not run `git submodule update o-voxel/...` inside the Pixal3D checkout;
  Pixal3D has no such submodule. The shared runtime source owns that native
  build input.
- Pixal3D exposes the same install-time FlashAttention options as TRELLIS.2:
  GPU arch, `MAX_JOBS`, and `NVCC_THREADS`. These feed the shared runtime build
  through the same `TRELLIS_FLASH_ATTN_*` environment variables.

Manager/registry status:

- `NymphsModules/nymphs-registry` has a `pixal3d` entry. The Pixal3D module
  manifest owns the installed `NEXT STEP` BRIA form action.
- NymphsCore now treats display `kind`, content `category`, and install
  `packaging` as separate manifest/registry concepts. This lets modules show
  `// image` or `// 3d` while still installing as `repo`.
- Z-Image should use `category=image`, `kind=image`, `packaging=repo`.
- Pixal3D should use `category=3d`, `kind=3d` if a display kind is added later,
  and `packaging=repo`.

Addon status:

- A local NymphsAddon patch exists for Pixal3D as a third 3D backend, but it has
  not been committed or pushed yet.
- Local addon checks passed with `python3 -m py_compile Nymphs.py` and
  `git diff --check -- Nymphs.py`.
- Blender is not available on this machine's PATH, so the addon still needs a
  real Blender enable/start/probe/generate/import test before shipping.
- Keep Blender addon changes local until Pixal3D generation imports a textured
  GLB correctly in the target Blender build.

### Final Build Decision

Build Pixal3D as a separate Nymph module:

```text
module id:        pixal3d
install root:     $HOME/Pixal3D
venv:             $HOME/TRELLIS.2/.venv
port:             8096
api script:       scripts/api_server_pixal3d.py
model repo:       TencentARC/Pixal3D
default profile:  low_vram_1024
runtime profile:  shared TRELLIS.2/Pixal3D Python 3.10 + CUDA runtime
output format:    binary GLB response from POST /generate
```

Use the official TRELLIS.2 runtime install surface as the base recipe, but keep
Pixal3D independent from TRELLIS model weights and from the TRELLIS GGUF service.

Do this:

- Vendor or sync the upstream `TencentARC/Pixal3D` repo into `$HOME/Pixal3D`.
- Create or reuse the shared `$HOME/TRELLIS.2/.venv` runtime.
- Use a tested CUDA/Torch stack. The conservative upstream/HF-demo profile is
  Python 3.10, Torch 2.6.0/cu124, torchvision 0.21.0, CUDA Toolkit 12.4. Local
  validation on 2026-05-17 also proved the Nymph CUDA 13 profile works:
  Torch 2.11.0+cu130, CUDA Toolkit 13.0, RTX 4080 SUPER.
- Install TRELLIS.2 native runtime pieces into that venv:
  `flash-attn`, `nvdiffrast`, `cumesh`, `o-voxel`, `flex_gemm`, and the normal
  Python basics.
- Hard-require `ATTN_BACKEND=flash_attn` for the Pixal3D module. Do not silently
  fall back to SDPA.
- Install Pixal3D extra deps:
  `git+https://github.com/microsoft/MoGe.git`, `diffusers==0.37.1`,
  `accelerate==1.13.0`, `gradio`, `plyfile==1.1.3`, and a NATTEN wheel matching
  the chosen Torch/CUDA ABI. For local CUDA 13 validation this was
  `natten==0.21.6+torch2110cu130`.
- Install the official Pixal3D README `utils3d-0.0.2` wheel, then create the
  `utils3d.pt`/`utils3d.np` aliases that MoGe calls. Do not install
  `EasternJournalist/utils3d@3fab839f0be9931dac7c8488eb0e1600c236e183`; that
  newer API drops `utils3d.torch.intrinsics_from_fov_xy`, which Pixal3D and
  TRELLIS.2 rendering code still call.
- Fetch Pixal3D and auxiliary models into `$HOME/NymphsData` caches.
- Add Pixal3D as a full third Blender service with start/stop/probe/generate UI.
- Preserve upstream `train.py`, `configs/gen/*.json`, and `data_toolkit/` in
  the installed tree, but do not expose them as v1 Manager actions. They are
  future training-surface material.

Do not do this in v1:

- Do not require the TRELLIS GGUF module to be installed.
- Do not run Pixal3D through `trellis2_gguf`.
- Do not share the TRELLIS GGUF venv.
- Do not implement selected-mesh retexture through Pixal3D yet.
- Do not create a custom Manager WebView UI just for model selection.
- Do not return JSON from Pixal3D `/generate` in v1; the current Blender shape
  worker expects mesh bytes.
- Do not wire Pixal3D training into the current LoRA module. That module is
  Z-Image Turbo-specific and emits `.safetensors` LoRA adapters for image
  generation, not Pixal3D/TRELLIS.2 3D generator checkpoints.

### Official Source Conclusions

Official Pixal3D README:

- `main` is the latest branch and is based on TRELLIS.2.
- Installation says to follow TRELLIS.2 installation first.
- Then install Pixal3D `requirements.txt`.
- As of upstream `e3b2ac1`, NATTEN is a separate manual install step:
  `NATTEN_CUDA_ARCH="xx" NATTEN_N_WORKERS=xx pip install natten==0.21.0 --no-build-isolation`.
  Upstream removed `natten==0.21.0` from `requirements.txt` and added explicit
  pins for basics such as `pillow`, `imageio`, `opencv-python-headless`,
  `trimesh`, `transformers`, `zstandard`, `kornia`, and `timm`.
- Then install the `utils3d` wheel. Local validation found MoGe auto-FOV also
  needs `utils3d.pt`; the module creates that alias after installing the wheel.
- Low-VRAM mode is supported.
- Default resolution is 1536 normally and 1024 in low-VRAM mode.
- Upstream documents `ATTN_BACKEND=sdpa` as a fallback when flash-attn is absent,
  but the Nymph Pixal3D module should not expose or auto-use that fallback.
- `requirements-hfdemo.txt` is specifically for Hugging Face Spaces/H-series
  hardware and should not be the normal local install recipe.
- Upstream now includes official training code:
  `train.py`, eight staged configs under `configs/gen/`, and a
  `data_toolkit/` for downloading assets, rendering conditions, building
  metadata, view-aligned O-Voxel conversion, PBR/shape/sparse-structure latent
  encoding, and visualization.
- Pixal3D training is a three-stage cascade:
  sparse structure `32 -> 64`, shape `256 -> 512 -> 1024`, and texture
  `256 -> 512 -> 1024`.
- Training uses view-aligned projection conditioning, two views by default,
  DINOv3 projection features, optional NAF upsampling for shape/texture stages,
  TRELLIS.2 SC-VAE decoders, and distributed Torch launch support through
  `torch.multiprocessing.spawn`.

Official TRELLIS.2 README/install surface:

- Linux and NVIDIA GPU are the tested local target.
- CUDA toolkit is required to compile several packages.
- Official setup flags include:
  `--basic --flash-attn --nvdiffrast --nvdiffrec --cumesh --o-voxel --flexgemm`.
- TRELLIS.2 uses `o_voxel` for GLB export and `CuMesh`/`FlexGEMM`/`nvdiffrast`
  for native geometry/rendering paths.
- The official TRELLIS.2 pretrained model is `microsoft/TRELLIS.2-4B`, but that
  is the official TRELLIS.2 model dependency, not an observed separate Pixal3D
  inference dependency.

Local source comparison:

- `/home/nymph/NymphsModules/trellis/trellis2` matches a fresh official
  `microsoft/TRELLIS.2` clone at commit `5565d240...` in the compared source
  tree.
- Your TRELLIS module adds GGUF adapter scripts around that source:
  `scripts/api_server_trellis_gguf.py` and `scripts/trellis_gguf_common.py`.
- Pixal3D is not just official TRELLIS.2 with different weights. Compared to
  official `trellis2`, it adds and changes projection-specific code:
  `pixal3d/pipelines/pixal3d_image_to_3d.py`,
  `pixal3d/trainers/flow_matching/mixins/image_conditioned_proj.py`,
  `pixal3d/modules/attention/proj_attention.py`,
  `pixal3d/modules/sparse/attention/proj_attention.py`, and related modified
  transformer/attention paths.

Conclusion:

```text
The existing TRELLIS module install recipe is useful.
The existing TRELLIS GGUF service/runtime path is not the Pixal3D base.
The Pixal3D module must install/run the Pixal3D package itself.
The existing LoRA module UI/job architecture is useful as a pattern.
The existing LoRA module training backend is not a Pixal3D trainer.
```

### Training Update From Upstream 2026-05-19

The merged upstream commits add enough official training surface to plan a
future Pixal3D Trainer, but not enough to make it a small extension of the
current LoRA module.

New upstream files:

```text
train.py
configs/gen/ss_flow_img_dit_1_3B_32_bf16_proj_finetune.json
configs/gen/ss_flow_img_dit_1_3B_32_bf16_proj_finetune_ft64.json
configs/gen/slat_flow_img2shape_dit_1_3B_256_bf16_proj_finetune.json
configs/gen/slat_flow_img2shape_dit_1_3B_256_bf16_proj_finetune_ft512.json
configs/gen/slat_flow_img2shape_dit_1_3B_512_bf16_proj_finetune_ft1024.json
configs/gen/slat_flow_imgshape2tex_dit_1_3B_256_bf16_proj_finetune.json
configs/gen/slat_flow_imgshape2tex_dit_1_3B_512_bf16_proj_finetune.json
configs/gen/slat_flow_imgshape2tex_dit_1_3B_512_bf16_proj_finetune_ft1024.json
data_toolkit/
```

Training command shape:

```bash
python train.py \
  --config <CONFIG_JSON> \
  --output_dir <OUTPUT_DIR> \
  --data_dir '<DATA_DIR_JSON>'
```

`--data_dir` is not a simple image folder. It is a JSON object that points each
dataset to staged 3D assets:

```text
Sparse Structure: base, ss_latent, render_cond
Shape:            base, shape_latent, render_cond
Texture:          base, shape_latent, pbr_latent, render_cond
```

This means Pixal3D training needs a data preparation workflow before training
can even start. The toolkit path is:

```text
metadata -> download 3D assets -> dump mesh/PBR -> render condition views
-> view-aligned O-Voxels -> shape/PBR/SS latents -> train cascade stages
```

The Nymph implementation implication:

- V1 Pixal3D should stay inference-only from the Manager/Blender perspective.
- Keep `train.py`, `configs/gen/`, and `data_toolkit/` installed and documented
  so advanced users can inspect or run them manually.
- Plan a separate `pixal3d-trainer` module or a later Pixal3D module training
  tab once the inference module is stable.
- Do not present this as a small “LoRA training” feature. It is closer to a
  full 3D model training workbench.

### LoRA Module Compatibility Answer

Could the current Nymph LoRA module train Pixal3D?

Short answer: no, not directly.

What the current LoRA module does:

- Installs `$HOME/LoRA`.
- Uses `ostris/ai-toolkit`.
- Fetches `Tongyi-MAI/Z-Image-Turbo` and
  `ostris/zimage_turbo_training_adapter`.
- Builds AI Toolkit jobs with `arch: "zimage:turbo"`.
- Trains image-generation LoRA adapters and writes finished `.safetensors`
  under `$HOME/LoRA/loras`.

What Pixal3D training needs:

- Pixal3D/TRELLIS.2 model classes and trainers from this repo.
- Datasets made from 3D assets, not only captioned 2D images.
- Rendered condition views with camera transforms.
- View-aligned O-Voxels.
- Shape, PBR, and sparse-structure latents.
- Multi-stage checkpoint handoff between sparse structure, shape, and texture.
- Native TRELLIS.2/Pixal3D runtime extensions in the training venv.

Useful reuse from the LoRA module:

- Separate training sidecar pattern.
- `Fetch Training Assets` as a distinct Manager action.
- Module-owned local HTML for beginner training UX.
- Dataset/job/log/output folder conventions.
- Status fields for assets, active jobs, finished outputs, and retained data.

Do not reuse:

- AI Toolkit as the Pixal3D training backend.
- Z-Image Turbo training configs.
- The `.safetensors` LoRA output assumption as the product deliverable.
- The simple captioned-image dataset path as the Pixal3D data contract.

### Deliverable File Tree

Create:

```text
NymphsModules/pixal3d/
  nymph.json
  README.md
  docs/
    PIXAL3D_MODULE_NOTES.md
  scripts/
    _pixal3d_common.sh
    install_pixal3d.sh
    pixal3d_update.sh
    pixal3d_status.sh
    pixal3d_start.sh
    pixal3d_stop.sh
    pixal3d_logs.sh
    pixal3d_open.sh
    pixal3d_open_outputs.sh
    pixal3d_open_weights.sh
    pixal3d_fetch_models.sh
    pixal3d_smoke_test.sh
    pixal3d_uninstall.sh
    api_server_pixal3d.py
    pixal3d_model_common.py
```

The install step should copy/sync the module repo into:

```text
$HOME/Pixal3D
```

The installed root must contain:

```text
$HOME/Pixal3D/nymph.json
$HOME/Pixal3D/scripts/*.sh
$HOME/Pixal3D/scripts/api_server_pixal3d.py
$HOME/Pixal3D/pixal3d/
$HOME/Pixal3D/inference.py
$HOME/Pixal3D/app.py
$HOME/Pixal3D/requirements.txt
$HOME/Pixal3D/.nymph-module-version
$HOME/TRELLIS.2/.venv/
```

### Data And Cache Layout

Use:

```text
$HOME/NymphsData/outputs/pixal3d
$HOME/NymphsData/logs/pixal3d
$HOME/NymphsData/config/pixal3d
$HOME/NymphsData/cache/huggingface
$HOME/NymphsData/cache/huggingface-home
$HOME/NymphsData/cache/torch-hub
```

Do not store reusable model files under `$HOME/Pixal3D` except transient
runtime cache files that belong to the source checkout. This keeps normal
uninstall safe.

### Manifest Contract

`nymph.json` must expose:

```json
{
  "manifest_version": 1,
  "id": "pixal3d",
  "name": "Pixal3D",
  "short_name": "PX",
  "version": "0.1.0",
  "description": "Local Pixal3D image-to-3D backend packaged as an installable Nymph module.",
  "category": "3d",
  "packaging": "repo",
  "install": {
    "title": "PIXAL3D RUNTIME OPTIONS",
    "root": "$HOME/Pixal3D",
    "entrypoint": "scripts/install_pixal3d.sh",
    "version_marker": "$HOME/Pixal3D/.nymph-module-version",
    "installed_markers": [
      "$HOME/Pixal3D/.nymph-module-version"
    ]
  },
  "runtime": {
    "host": "127.0.0.1",
    "port": 8096,
    "health_url": "http://127.0.0.1:8096/health",
    "server_info_url": "http://127.0.0.1:8096/server_info"
  }
}
```

The module detail page must carry license/access instructions before install or
model fetch. Put them in `overview.body` so the Manager's standard detail page
shows them without needing a custom WebView UI. Also expose the BRIA access form
as an explicit `overview.links` item; do not rely on users finding the link in a
long paragraph.

Use "acknowledgement" wording, not "waiver" wording. The module cannot waive or
override Pixal3D's or BRIA's license terms; it can only make the restrictions
clear and require the user to acknowledge that they are responsible for a
permitted use case before fetching gated/non-commercial weights.

Required module detail-page notices:

```text
License / use restrictions:
- Pixal3D's local LICENSE grants use only for academic purposes.
- Pixal3D's local LICENSE forbids commercial or production use.
- Pixal3D's local LICENSE states that Pixal3D is not intended for use within
  the European Union.
- Pixal3D is provided as-is, without warranty. Users are responsible for
  confirming that their use complies with Pixal3D, BRIA RMBG, Hugging Face, and
  any other dependency terms.

BRIA RMBG-2.0 access:
- Pixal3D's official pipeline uses briaai/RMBG-2.0 for background removal.
- briaai/RMBG-2.0 is gated on Hugging Face and released for non-commercial use.
- The module details page must include a direct BRIA access-form link:
  https://huggingface.co/briaai/RMBG-2.0
- A Hugging Face token alone is not enough. The same HF account must first open
  https://huggingface.co/briaai/RMBG-2.0, fill in BRIA's access form, and agree
  to BRIA's non-commercial/license terms.
- BRIA's form says contact information such as email and username may be shared
  with the repository authors.
- If the form is not accepted, model fetch or first run fails with
  GatedRepoError / HTTP 401 or 403.
```

Suggested `overview` shape:

```json
{
  "overview": {
    "body": "Pixal3D generates textured 3D assets from a single image using a TRELLIS.2-style backbone and Pixal3D projection pipeline.\\n\\nLicense and access notice:\\n- Pixal3D is for academic use only under its local LICENSE. It is not licensed for commercial or production use.\\n- Pixal3D's local LICENSE says it is not intended for use within the European Union.\\n- The official Pixal3D pipeline uses briaai/RMBG-2.0 for background removal. That model is gated on Hugging Face and released for non-commercial use.\\n- Before Fetch Models, open the BRIA RMBG-2.0 access form with the same Hugging Face account as your token, complete BRIA's form, and agree to BRIA's terms. BRIA's form indicates contact information may be shared with the repository authors.\\n- The user is responsible for confirming their intended use is allowed by Pixal3D, BRIA RMBG, Hugging Face, and dependency licenses.\\n\\nModel fetch guide:\\n- Install sets up code and runtime only. Fetch Models downloads Pixal3D checkpoints and auxiliary models.\\n- Start with Low VRAM 1024 on 16 GB GPUs.\\n- Fetch Models requires the license/access acknowledgement in the action form.",
    "links": [
      {
        "label": "Pixal3D model/license",
        "url": "https://huggingface.co/TencentARC/Pixal3D"
      },
      {
        "label": "BRIA RMBG-2.0 access form",
        "url": "https://huggingface.co/briaai/RMBG-2.0"
      },
      {
        "label": "BRIA RMBG-2.0 CC BY-NC license",
        "url": "https://creativecommons.org/licenses/by-nc/4.0/"
      }
    ]
  }
}
```

Add entrypoints:

```json
{
  "entrypoints": {
    "install": "scripts/install_pixal3d.sh",
    "update": "scripts/pixal3d_update.sh",
    "status": "scripts/pixal3d_status.sh",
    "start": "scripts/pixal3d_start.sh",
    "stop": "scripts/pixal3d_stop.sh",
    "open": "scripts/pixal3d_open.sh",
    "logs": "scripts/pixal3d_logs.sh",
    "fetch_models": "scripts/pixal3d_fetch_models.sh",
    "smoke_test": "scripts/pixal3d_smoke_test.sh",
    "uninstall": "scripts/pixal3d_uninstall.sh",
    "open_weights": "scripts/pixal3d_open_weights.sh",
    "open_outputs": "scripts/pixal3d_open_outputs.sh"
  }
}
```

Use native action groups for model/profile fetch:

```json
{
  "ui": {
    "sort_order": 45,
    "manager_action_groups": [
      {
        "id": "model_fetch",
        "title": "Model Fetch",
        "layout": "compact",
        "entrypoint": "fetch_models",
        "result": "show_logs",
        "visibility": "installed",
        "description": "Fetch Pixal3D checkpoints and auxiliary camera/background/projection models into shared NymphsData caches.",
        "fields": [
          {
            "name": "profile",
            "type": "select",
            "label": "Profile",
            "arg": "--profile",
            "default": "low_vram_1024",
            "options": [
              {
                "label": "Low VRAM 1024",
                "value": "low_vram_1024",
                "description": "Recommended first test; lower peak VRAM and 1024 cascade"
              },
              {
                "label": "Standard 1536",
                "value": "standard_1536",
                "description": "Heavier profile for high VRAM systems"
              }
            ]
          },
          {
            "name": "hf_token",
            "type": "secret",
            "label": "Hugging Face token",
            "secret_id": "huggingface.token",
            "env": "NYMPHS3D_HF_TOKEN",
            "optional": true
          },
          {
            "name": "license_ack",
            "type": "select",
            "label": "License/access acknowledgement",
            "arg": "--license-ack",
            "default": "no",
            "options": [
              {
                "label": "Not yet",
                "value": "no",
                "description": "Do not fetch gated/non-commercial Pixal3D assets yet"
              },
              {
                "label": "I acknowledge",
                "value": "yes",
                "description": "I understand Pixal3D is academic-only, not for commercial/production use, not intended for EU use, and BRIA RMBG requires its HF access form"
              }
            ]
          }
        ],
        "submit": {
          "label": "Fetch Models"
        }
      }
    ]
  }
}
```

### Install Script Contract

`install_pixal3d.sh` should:

1. Install system packages:
   `python3.10`, `python3.10-venv`, `python3.10-dev`, `git`, `curl`, `cmake`,
   `build-essential`, `pkg-config`, `libegl1-mesa-dev`, `libgl1`,
   `libglib2.0-0`, `ccache`, `ninja`, `libjpeg-dev`.
2. Sync module/upstream source into `$HOME/Pixal3D`.
3. Ensure the official `o-voxel/third_party/eigen` submodule or equivalent
   source exists for building `o_voxel`.
4. Create or repair `$HOME/TRELLIS.2/.venv` with Python 3.10.
5. Install PyTorch. Two profiles are now known:
   - Conservative upstream/HF-demo profile:
     `torch==2.6.0 torchvision==0.21.0 --index-url cu124`, native extensions
     built with CUDA Toolkit 12.4.
   - Locally validated Nymph CUDA 13 profile:
     `torch==2.11.0+cu130 torchvision==0.26.0+cu130`, native extensions built
     with CUDA Toolkit 13.0.
6. Install official TRELLIS.2 basics:
   `imageio`, `imageio-ffmpeg`, `tqdm`, `easydict`, `opencv-python-headless`,
   `ninja`, `trimesh`, `transformers`, `gradio==6.0.1`, `tensorboard`,
   `pandas`, `lpips`, `zstandard`, `kornia`, `timm`.
7. Install `utils3d` from Pixal3D's README wheel:
   `https://github.com/LDYang694/Storages/releases/download/20260430/utils3d-0.0.2-py3-none-any.whl`.
   Then create `utils3d.pt` and `utils3d.np` aliases for MoGe compatibility.
   Do not use `EasternJournalist/utils3d@3fab839f0be9931dac7c8488eb0e1600c236e183`;
   it lacks `utils3d.torch.intrinsics_from_fov_xy`.
8. Install Pixal3D requirements:
   `git+https://github.com/microsoft/MoGe.git`,
   `diffusers==0.37.1`, `accelerate==1.13.0`, `gradio`, `plyfile==1.1.3`.
   Install a NATTEN build matching the selected Torch/CUDA stack. The CUDA 13
   validation used `natten==0.21.6+torch2110cu130` from `https://whl.natten.org`.
9. Install native runtime extensions:
   `flash-attn`, `nvdiffrast`, `cumesh`, `flex_gemm`, `o-voxel`.
10. Compile-check:
   `scripts/api_server_pixal3d.py`, import `pixal3d`, import `o_voxel`,
   import `cumesh`, import `flex_gemm`, import `nvdiffrast.torch`, import
   `flash_attn`, and run a tiny CUDA flash-attn kernel smoke.
11. Write `$HOME/Pixal3D/.nymph-module-version`.

Install risk policy:

- If `flash-attn` fails to import or its CUDA kernel smoke fails, install should
  fail clearly. Do not continue with `ATTN_BACKEND=sdpa`.
- If NATTEN does not support the chosen Torch/CUDA ABI, fail with a clear
  message and point to the tested profile.
- Do not use `requirements-hfdemo.txt` by default. It is hardware-specific.

### Status Script Contract

`pixal3d_status.sh` must be fast enough for Manager status timeouts.

It should emit:

```text
id=pixal3d
name=Pixal3D
installed=true|false
runtime_present=true|false
data_present=true|false
version=...
env_ready=true|false
adapter_ready=true|false
runtime_ready=true|false
models_ready=true|false|unknown
aux_models_ready=true|false|unknown
running=true|false
state=available|installed|running|needs_attention
health=ok|unknown|degraded|model-download-needed|unreachable
url=http://127.0.0.1:8096
install_root=/home/nymph/Pixal3D
venv=/home/nymph/TRELLIS.2/.venv
logs_dir=/home/nymph/NymphsData/logs/pixal3d
outputs_dir=/home/nymph/NymphsData/outputs/pixal3d
config_dir=/home/nymph/NymphsData/config/pixal3d
hf_cache_dir=/home/nymph/NymphsData/cache/huggingface
torch_hub_dir=/home/nymph/NymphsData/cache/torch-hub
profile=low_vram_1024
marker=/home/nymph/Pixal3D/.nymph-module-version
detail=...
```

Lightweight runtime import check:

```text
import pixal3d
import o_voxel
import cumesh
import flex_gemm
import nvdiffrast.torch
```

Do not instantiate Pixal3D, DINO, MoGe, RMBG, or NAF in status.

### Model Fetch Contract

`pixal3d_fetch_models.sh` should accept:

```text
--profile low_vram_1024|standard_1536
--hf-token <token>
--license-ack yes|no
```

`--license-ack yes` should be required before downloading `TencentARC/Pixal3D`
or `briaai/RMBG-2.0`. If it is omitted or set to `no`, fail before network
downloads with a targeted message:

```text
LICENSE ACK REQUIRED:
Pixal3D is academic-only, not licensed for commercial or production use, and
its LICENSE says it is not intended for use within the European Union.
BRIA RMBG-2.0 is gated/non-commercial and requires the Hugging Face access form:
https://huggingface.co/briaai/RMBG-2.0
Rerun Fetch Models after selecting "I acknowledge" in the module action form.
```

It should download:

```text
TencentARC/Pixal3D
Ruicheng/moge-2-vitl
camenduru/dinov3-vitl16-pretrain-lvd1689m
briaai/RMBG-2.0
valeoai/NAF through torch.hub
```

`briaai/RMBG-2.0` is a gated Hugging Face model. A Hugging Face token is
necessary but not sufficient: the same HF account must first open
`https://huggingface.co/briaai/RMBG-2.0`, fill in BRIA's access form, and agree
to the non-commercial/license terms. If the form has not been accepted, fetch or
first pipeline load fails with `GatedRepoError` / HTTP `401` or `403` even when a
token is supplied. The fetch script should detect this and print a targeted
message instead of reporting a generic model-download failure.

Main Pixal3D `snapshot_download` allow patterns:

```text
pipeline.json
ckpts/*.json
ckpts/*.safetensors
README.md
```

Progress output should use readable lines:

```text
MODEL FETCH STARTED: step=1/5 repo=TencentARC/Pixal3D
MODEL FETCH STATUS: step=1/5 cache_total=...
MODEL FETCH COMPLETE: step=1/5 repo=TencentARC/Pixal3D root=...
```

After fetch, write:

```text
$HOME/NymphsData/config/pixal3d/profile.env
```

with:

```text
PIXAL3D_PROFILE=low_vram_1024
PIXAL3D_LOW_VRAM=1
PIXAL3D_RESOLUTION=1024
PIXAL3D_MODEL_REPO=TencentARC/Pixal3D
```

### API Server Contract

`api_server_pixal3d.py` should mirror the TRELLIS GGUF API shape because the
Blender addon already knows how to talk to it.

Endpoints:

```text
GET  /health
GET  /server_info
GET  /active_task
POST /generate
```

`POST /generate` must return raw GLB bytes with:

```text
Content-Type: model/gltf-binary
```

The current Blender `_job_worker` treats JSON from `/generate` as an error for
shape/texture jobs, then writes response bytes to a local `.glb` and imports it.
So binary GLB is required for full addon integration without rewriting the job
worker.

`/server_info` response:

```json
{
  "status": "ready",
  "backend": "Pixal3D",
  "model_path": "TencentARC/Pixal3D",
  "resolved_model_path": "/home/nymph/NymphsData/cache/huggingface/...",
  "subfolder": "",
  "enable_tex": true,
  "mesh_retexture": false,
  "enable_t23d": false,
  "texture_only": false,
  "low_vram": true,
  "resolution": 1024,
  "supported_resolutions": [1024, 1536],
  "attention_backend": "flash_attn",
  "sparse_conv_backend": "flex_gemm",
  "model_ready": true,
  "aux_models_ready": true,
  "runtime_distro": "NymphsCore",
  "runtime_user": "nymph",
  "hf_home": "/home/nymph/NymphsData/cache/huggingface-home",
  "torch_home": "/home/nymph/NymphsData/cache/torch-hub"
}
```

`/active_task` response should match current addon progress parsing style:

```json
{
  "status": "idle",
  "stage": "",
  "detail": "",
  "progress_current": null,
  "progress_total": null,
  "progress_percent": null,
  "message": ""
}
```

Generation flow:

1. Read JSON body.
2. Decode `image` base64.
3. Reject requests containing `mesh` with HTTP 400 in v1:
   Pixal3D selected-mesh retexture is not implemented.
4. Lazy-load `Pixal3DImageTo3DPipeline.from_pretrained(model_path)`.
5. Build four `DinoV3ProjFeatureExtractor` models.
6. Apply low-VRAM mode if configured.
7. Preprocess image via Pixal3D pipeline.
8. Estimate camera with MoGe, unless manual FOV is supplied.
9. Run `pipeline.run(..., pipeline_type="1024_cascade"|"1536_cascade")`.
10. Export GLB with `o_voxel.postprocess.to_glb`.
11. Export with `extension_webp=False` for Blender compatibility unless testing
    proves WebP imports cleanly.
12. Return raw GLB bytes.

Payload mapping:

```text
image                         -> required base64 image
seed                          -> Pixal3D seed
max_num_tokens                -> Pixal3D max_num_tokens
pipeline_type=1024_cascade    -> resolution=1024
pipeline_type=1536_cascade    -> resolution=1536
pixal3d_resolution            -> overrides pipeline_type if set
pixal3d_low_vram              -> low_vram
pixal3d_manual_fov            -> manual_fov
pixal3d_mesh_scale            -> mesh_scale
pixal3d_extend_pixel          -> extend_pixel
pixal3d_image_resolution      -> image_resolution
ss_sampling_steps             -> ss_sampling_steps
ss_guidance_strength          -> ss_guidance_strength
ss_guidance_rescale           -> ss_guidance_rescale
ss_rescale_t                  -> ss_rescale_t
shape_sampling_steps          -> shape_slat_sampling_steps
shape_guidance_strength       -> shape_slat_guidance_strength
shape_guidance_rescale        -> shape_slat_guidance_rescale
shape_rescale_t               -> shape_slat_rescale_t
tex_sampling_steps            -> tex_slat_sampling_steps
tex_guidance_strength         -> tex_slat_guidance_strength
tex_guidance_rescale          -> tex_slat_guidance_rescale
tex_rescale_t                 -> tex_slat_rescale_t
decimation_target             -> GLB export decimation_target
texture_size                  -> GLB export texture_size
```

Ignore unsupported TRELLIS GGUF-only fields without failing:

```text
gguf_quant
foreground_ratio
sparse_structure_resolution
sampler
sparse_structure_sampler
shape_sampler
tex_sampler
texture_alpha_mode
texture_double_sided
texture_bake_vertices
texture_custom_normals
texture_uv_method
texture_uv_angle
texture_inpainting
```

### Full Blender Addon Integration

File:

```text
NymphsAddon/Nymphs.py
```

Add constants:

```python
DEFAULT_REPO_PIXAL3D_PATH = "~/Pixal3D"
DEFAULT_PIXAL3D_PYTHON_PATH = "~/TRELLIS.2/.venv/bin/python"
DEFAULT_PIXAL3D_PORT = "8096"
DEFAULT_PIXAL3D_RESOLUTION = "1024"
```

Extend service maps:

```python
SERVICE_LABELS = {
    "n2d2": "Z-Image",
    "trellis": "TRELLIS.2 GGUF",
    "pixal3d": "Pixal3D",
}

SERVICE_PROP_PREFIXES = {
    "n2d2": "service_n2d2",
    "trellis": "service_trellis",
    "pixal3d": "service_pixal3d",
}

SERVICE_ORDER = ("n2d2", "trellis", "pixal3d")
```

Add state properties:

```python
shape_3d_runtime
service_pixal3d_enabled
service_pixal3d_port
service_pixal3d_show
service_pixal3d_launch_state
service_pixal3d_launch_detail
service_pixal3d_backend_summary
repo_pixal3d_path
pixal3d_python_path
pixal3d_low_vram
pixal3d_resolution
pixal3d_manual_fov
pixal3d_mesh_scale
pixal3d_extend_pixel
pixal3d_image_resolution
```

Change:

```python
def _selected_3d_service_key(state):
    value = getattr(state, "shape_3d_runtime", "trellis")
    return value if value in {"trellis", "pixal3d"} else "trellis"
```

Keep:

```python
def _selected_texture_service_key(state):
    return "trellis"
```

Reason: v1 Pixal3D generates image-to-textured-3D, but does not retexture an
arbitrary selected mesh.

Extend `_service_port` defaults:

```python
if service_key == "pixal3d":
    default = DEFAULT_PIXAL3D_PORT
elif service_key == "trellis":
    default = DEFAULT_TRELLIS_PORT
else:
    default = DEFAULT_N2D2_PORT
```

Extend `_compose_wsl_launch` with a Pixal3D branch:

```text
repo_path:     state.repo_pixal3d_path or ~/Pixal3D
python_path:   state.pixal3d_python_path or ~/TRELLIS.2/.venv/bin/python
script:        scripts/api_server_pixal3d.py
host/port:     0.0.0.0:<service_pixal3d_port>
log:           $HOME/NymphsData/logs/pixal3d/pixal3d-server.log
env:
  CUDA_HOME=/usr/local/cuda-12.4
  PIXAL3D_OUTPUT_DIR
  PIXAL3D_LOG_DIR
  PIXAL3D_CONFIG_DIR
  PIXAL3D_PID_FILE
  PIXAL3D_PORT
  PIXAL3D_HOST
  HF_HOME
  HF_HUB_CACHE
  NYMPHS3D_HF_CACHE_DIR
  TORCH_HOME
  ATTN_BACKEND
args:
  --host 0.0.0.0
  --port <port>
  --python-path <python_path>
  --model-path TencentARC/Pixal3D
  --resolution 1024|1536
  --low-vram or --no-low-vram
```

Extend `_stop_shell_for_service`:

```text
fuser -k <port>/tcp
pkill -f "scripts/api_server_pixal3d.py --host 0.0.0.0 --port <port>"
pkill -f "python scripts/api_server_pixal3d.py"
pkill -f "python3 scripts/api_server_pixal3d.py"
```

Extend backend parsing:

```python
def _backend_family(info):
    backend_name = str(info.get("backend", "")).strip().lower()
    if backend_name == "pixal3d":
        return "Pixal3D"
    ...
```

This must happen before any fallback that checks for `trellis` in text blobs.

Extend capabilities:

```python
if family == "Pixal3D":
    texture_enabled = bool(info.get("enable_tex", True))
    return {
        "family": "Pixal3D",
        "shape": not texture_only,
        "texture": texture_enabled,
        "retexture": bool(info.get("mesh_retexture", False)),
        "multiview": False,
        "text": False,
        "texture_only": texture_only,
    }
```

Extend summary parsing and fallback:

- `_summarize_server_info(info)` must produce:

```text
Pixal3D | TencentARC/Pixal3D | low_vram=true | resolution=1024 | attn=flash_attn | shape=true | tex=true | retexture=false | mv=false | text=false
```

- `_service_capabilities_from_summary` must recognize `"Pixal3D |"` and set
  `family="Pixal3D"`.
- `_fallback_server_capabilities` should return shape+texture for Pixal3D when
  Pixal3D is the selected runtime and launch is in progress.

Shape payload:

- Replace shape path use of `_with_trellis_runtime_payload` with a generic
  `_with_3d_runtime_payload`.
- For TRELLIS, keep adding `gguf_quant`.
- For Pixal3D, add:

```python
payload["pixal3d_low_vram"] = state.pixal3d_low_vram
payload["pixal3d_resolution"] = int(state.pixal3d_resolution)
payload["pixal3d_manual_fov"] = float(state.pixal3d_manual_fov)
payload["pixal3d_mesh_scale"] = float(state.pixal3d_mesh_scale)
payload["pixal3d_extend_pixel"] = int(state.pixal3d_extend_pixel)
payload["pixal3d_image_resolution"] = int(state.pixal3d_image_resolution)
```

Do not change `_job_worker` in v1. It already supports Pixal3D if Pixal3D
returns binary GLB bytes.

Server panel UI:

- `_draw_service_block` should show Pixal3D card and config details.
- For `pixal3d`, show:
  - Runtime: Pixal3D
  - Loaded: low_vram/resolution/attention if present in summary
  - Repo Path
  - Python Path
  - Server Port
- Do not show GGUF Quant in Pixal3D service card.

Shape panel UI:

- Add runtime selector at the top:
  `TRELLIS.2 GGUF` or `Pixal3D`.
- If selected service is TRELLIS:
  - show GGUF Quant
  - show existing TRELLIS controls
- If selected service is Pixal3D:
  - hide GGUF Quant
  - hide TRELLIS-only controls:
    foreground ratio, sparse structure resolution, sampler name dropdowns,
    GGUF material/UV/inpainting controls
  - show Pixal3D controls:
    low VRAM, resolution, manual FOV, mesh scale, extend pixel,
    image resolution
  - keep shared controls:
    source image, seed, shape texture checkbox, sampling steps/guidance values,
    max tokens, texture size, decimation target

Texture panel UI:

- Keep selected-mesh retexture locked to TRELLIS in v1.
- If TRELLIS is not running, texture panel should show TRELLIS start controls,
  not Pixal3D controls.

Probe/launch lifecycle:

- `_background_primary_probe` and `_background_server_probe` already use
  `service_key`; make sure they store Pixal3D service status through
  `_service_changes("pixal3d", ...)`.
- Only store available GGUF quants for `service_key == "trellis"`.
- When selected shape runtime is Pixal3D, mirror Pixal3D status into the primary
  `backend_family`, `server_supports_shape`, and `server_supports_texture`
  state fields.

Addon edit checklist by existing symbol:

```text
Constants:
  DEFAULT_REPO_PIXAL3D_PATH
  DEFAULT_PIXAL3D_PYTHON_PATH
  DEFAULT_PIXAL3D_PORT
  DEFAULT_PIXAL3D_RESOLUTION

Service maps:
  SERVICE_LABELS
  SERVICE_PROP_PREFIXES
  SERVICE_ORDER

Selection/routing:
  _selected_3d_service_key
  _selected_texture_service_key
  _service_port
  _service_api_root
  _service_runtime_is_available
  _fallback_server_capabilities
  _service_capabilities_from_summary

Payload:
  _with_trellis_runtime_payload -> replace shape use with _with_3d_runtime_payload
  _build_shape_payload
  _build_texture_payload stays TRELLIS-only

Backend info:
  _backend_family
  _server_capabilities_from_info
  _summarize_server_info
  _backend_display_name if needed

Launch/stop/probe:
  _compose_wsl_launch
  _stop_shell_for_service
  _backend_lifecycle
  _background_primary_probe
  _background_server_probe
  _background_active_probe should work unchanged if /active_task matches

State properties:
  class NymphsV2State

UI draw:
  _draw_service_block
  NYMPHSV2_PT_server if it assumes exactly two services
  NYMPHSV2_PT_shape
  NYMPHSV2_PT_texture should remain TRELLIS retexture

Operators:
  NYMPHSV2_OT_start_service should work after service maps
  NYMPHSV2_OT_stop_service should work after service maps
  NYMPHSV2_OT_probe_services should work if it loops SERVICE_ORDER
  NYMPHSV2_OT_run_shape_request should work after payload/capability updates
  NYMPHSV2_OT_run_texture_request should remain TRELLIS-only

Do not change in v1:
  _job_worker, as long as Pixal3D /generate returns binary GLB bytes
  _import_result, unless Blender material import proves Pixal3D GLB needs
  another material restoration path
```

### Validation Checklist

Module-only:

```bash
$HOME/Pixal3D/scripts/pixal3d_status.sh
$HOME/Pixal3D/scripts/pixal3d_fetch_models.sh --profile low_vram_1024
$HOME/Pixal3D/scripts/pixal3d_start.sh
curl -s http://127.0.0.1:8096/server_info
curl -s http://127.0.0.1:8096/active_task
```

API binary response:

```bash
python - <<'PY'
import base64, json, urllib.request
image = base64.b64encode(open('/home/nymph/Pixal3D/assets/images/0_img.png','rb').read()).decode()
payload = json.dumps({
    "image": image,
    "seed": 42,
    "texture": True,
    "pixal3d_low_vram": True,
    "pixal3d_resolution": 1024
}).encode()
req = urllib.request.Request(
    'http://127.0.0.1:8096/generate',
    data=payload,
    headers={'Content-Type': 'application/json'},
    method='POST',
)
with urllib.request.urlopen(req, timeout=1800) as r:
    print(r.status, r.headers.get('Content-Type'), r.headers.get('Content-Length'))
    open('/tmp/pixal3d-smoke.glb','wb').write(r.read())
PY
```

Expected:

```text
HTTP 200
Content-Type: model/gltf-binary
/tmp/pixal3d-smoke.glb imports into Blender with material/texture visible
```

Addon:

1. Install Pixal3D module in Manager.
2. Fetch Pixal3D models.
3. Open Blender.
4. Nymphs Server panel shows Z-Image, TRELLIS.2 GGUF, and Pixal3D.
5. Start Pixal3D.
6. Shape panel runtime selector chooses Pixal3D.
7. GGUF Quant is hidden.
8. Pixal3D controls are visible.
9. Generate Shape imports a textured GLB.
10. Switch runtime back to TRELLIS.2 GGUF.
11. TRELLIS shape generation still works.
12. Texture panel still retextures selected meshes with TRELLIS only.

### V1 Done Definition

V1 is complete when:

- Pixal3D module installs in NymphsCore from `nymph.json`.
- Status is reliable before install, after install, before fetch, after fetch,
  while running, and after stop.
- Pixal3D fetch is resumable and stores caches under `NymphsData`.
- Pixal3D API returns binary GLB from `/generate`.
- Blender addon can start/stop/probe Pixal3D as a third service.
- Blender addon can select Pixal3D for shape generation.
- Blender imports Pixal3D textured output.
- Existing TRELLIS GGUF and Z-Image paths still work.
- Selected-mesh texture panel remains TRELLIS-only and stable.

## Sources Checked

External:

- Pixal3D repo: `https://github.com/TencentARC/Pixal3D`
- Pixal3D README raw: `https://raw.githubusercontent.com/TencentARC/Pixal3D/master/README.md`
- Pixal3D model repo: `https://huggingface.co/TencentARC/Pixal3D`
- Pixal3D model config: `https://huggingface.co/TencentARC/Pixal3D/raw/main/pipeline.json`
- Pixal3D ckpts folder: `https://huggingface.co/TencentARC/Pixal3D/tree/main/ckpts`

Local cloned upstream snapshot during research:

```text
repo: TencentARC/Pixal3D
commit: 6a4b9f3787e3692257604937cd45cb54e80ac9a0
short:  6a4b9f3 2026-05-16 fix: align inference.py GLB export params with app.py (texture_size=4096, decimation=1M)
```

Local Nymph references:

```text
NymphsCore/docs/NYMPHS_MODULE_MAKING_GUIDE.md
NymphsCore/docs/NYMPH_MODULE_UI_STANDARD.md
NymphsModules/trellis/nymph.json
NymphsModules/trellis/docs/TRELLIS_MODULE_MIGRATION_NOTES.md
NymphsModules/trellis/scripts/api_server_trellis_gguf.py
NymphsModules/trellis/scripts/trellis_gguf_common.py
NymphsAddon/Nymphs.py
Handoffs/trellis_gguf_session_handoff.md
Handoffs/trellis_unexposed_hooks.md
```

## Upstream Pixal3D Facts

Pixal3D README says the `main` branch is the latest version and is based on the
TRELLIS.2 backbone. The README install instructions say to follow the TRELLIS.2
installation first, then install Pixal3D's extra requirements.

Important distinction for the backbone question:

```text
"based on TRELLIS.2 backbone" means Pixal3D expects TRELLIS.2-style code,
native extensions, and runtime behavior. It does not, by itself, mean the
regular Microsoft TRELLIS.2 released model weights are an extra Pixal3D
inference requirement.
```

The upstream inference entrypoint loads:

```python
MODEL_PATH = "TencentARC/Pixal3D"
pipeline = Pixal3DImageTo3DPipeline.from_pretrained(model_path)
```

It also loads these auxiliary models:

```text
Ruicheng/moge-2-vitl
camenduru/dinov3-vitl16-pretrain-lvd1689m
briaai/RMBG-2.0
NAF via valeoai/NAF torch hub path in projection feature extractor
```

Access note: `briaai/RMBG-2.0` is gated. During local validation on
2026-05-17, Pixal3D reached pipeline construction and then failed at
`AutoModelForImageSegmentation.from_pretrained("briaai/RMBG-2.0")` with
`GatedRepoError` until the user accepted BRIA's HF access form. Document this in
Manager UI/help text: the token must belong to an account that has already been
granted repository access.

Pixal3D model config currently names `Trellis2ImageTo3DPipeline`, but its model
entries are Pixal3D-local checkpoint paths:

```text
ckpts/ss_dec_conv3d_16l8_fp16
ckpts/ss_flow_img_dit_1_3B_64_bf16
ckpts/shape_dec_next_dc_f16c32_fp16
ckpts/slat_flow_img2shape_dit_1_3B_512_bf16
ckpts/slat_flow_img2shape_dit_1_3B_1024_bf16
ckpts/tex_dec_next_dc_f16c32_fp16
ckpts/slat_flow_imgshape2tex_dit_1_3B_1024_bf16
```

The Hugging Face `ckpts` folder is about `24 GB`. The listed `.safetensors`
files include:

```text
shape_dec_next_dc_f16c32_fp16.safetensors       ~948 MB
slat_flow_img2shape_dit_1_3B_1024_bf16          ~5.55 GB
slat_flow_img2shape_dit_1_3B_512_bf16           ~5.55 GB
slat_flow_imgshape2tex_dit_1_3B_1024_bf16       ~5.55 GB
ss_dec_conv3d_16l8_fp16                         ~148 MB
ss_flow_img_dit_1_3B_64_bf16                    ~5.36 GB
tex_dec_next_dc_f16c32_fp16                     ~948 MB
```

No GGUF files were found in `TencentARC/Pixal3D`.

## Answer: GGUF Fork Runtime Or Regular TRELLIS.2 Runtime?

The practical answer:

```text
Build Pixal3D against a TRELLIS.2-style runtime/backbone environment, not the
current TRELLIS GGUF adapter runtime.

Do not plan on the current TRELLIS GGUF fork being a drop-in Pixal3D backbone
unless it still exposes the original TRELLIS.2 pipeline classes, native modules,
and package layout Pixal3D imports.

Do not plan to fetch the full regular microsoft/TRELLIS.2-4B model bundle as a
separate required Pixal3D inference model dependency, based on the current
upstream Pixal3D code and HF config.
```

Pixal3D module model dependencies:

```text
TencentARC/Pixal3D
Ruicheng/moge-2-vitl
camenduru/dinov3-vitl16-pretrain-lvd1689m
briaai/RMBG-2.0
NAF support dependency, if not pulled automatically by torch hub
```

Not part of the Pixal3D inference dependency set:

```text
Aero-Ex/Trellis2-GGUF
current TRELLIS GGUF Q4_K_M/Q5_K_M/Q6_K/Q8_0 files
```

Possible exception:

- Some training/dataset code in the repo still contains older defaults pointing
  at `microsoft/TRELLIS.2-4B`, `JeffreyXiang/TRELLIS.2-4B`, or older TRELLIS
  repos. Those paths are not the main inference path. Keep the first module
  scope inference-only.

## Why The Current TRELLIS GGUF Runtime Is Not Enough

Current Nymph TRELLIS GGUF module is hardwired around:

```text
GGUF_MODEL_REPO_ID = Aero-Ex/Trellis2-GGUF
VALID_GGUF_QUANTS = Q4_K_M, Q5_K_M, Q6_K, Q8_0
from trellis2_gguf.pipelines import Trellis2ImageTo3DPipeline
model root layout: pipeline.json, Vision, shape/*.gguf, refiner/*.gguf, texture/*.gguf
```

Pixal3D uses:

```text
Pixal3DImageTo3DPipeline
TencentARC/Pixal3D safetensors checkpoints
projection-aware DINOv3 feature extractors
camera params from MoGe or manual FOV
only 1024_cascade and 1536_cascade pipeline types in Pixal3D proj mode
```

So Pixal3D should not be implemented by reusing the current GGUF adapter
runtime path.

The actual compatibility risk is the fork/runtime surface, not the model weight
format. Pixal3D imports the Pixal3D/TRELLIS.2-style pipeline and native runtime
stack directly. A GGUF-focused fork that replaced the loader with
`trellis2_gguf`, removed original pipeline classes, or changed native extension
layout will not be enough as the Pixal3D base runtime.

## Runtime Behavior To Preserve

Upstream Pixal3D inference flow:

1. Load Pixal3D pipeline from `TencentARC/Pixal3D`.
2. Build separate `DinoV3ProjFeatureExtractor` models for:
   - sparse structure
   - shape 512
   - shape 1024
   - texture 1024
3. Preprocess image with Pixal3D/TRELLIS-style background removal and crop.
4. Estimate camera params with MoGe unless user provides manual FOV.
5. Run Pixal3D projection-mode cascade pipeline:
   - `1024_cascade` in low-VRAM mode by default
   - `1536_cascade` in standard mode by default
6. Export textured GLB through `o_voxel.postprocess.to_glb`.
7. Apply Blender-friendly orientation transform.

Important upstream knobs:

```text
seed
low_vram
resolution: 1024 or 1536
manual_fov
mesh_scale
extend_pixel
image_resolution
max_num_tokens
ss_guidance_strength
ss_guidance_rescale
ss_sampling_steps
ss_rescale_t
shape_slat_guidance_strength
shape_slat_guidance_rescale
shape_slat_sampling_steps
shape_slat_rescale_t
tex_slat_guidance_strength
tex_slat_guidance_rescale
tex_slat_sampling_steps
tex_slat_rescale_t
decimation_target
texture_size
```

## Proposed Module

Module identity:

```text
id: pixal3d
name: Pixal3D
short_name: PX
category: 3d
install root: $HOME/Pixal3D
runtime port: 8096
data root: $HOME/NymphsData
outputs: $HOME/NymphsData/outputs/pixal3d
logs: $HOME/NymphsData/logs/pixal3d
config: $HOME/NymphsData/config/pixal3d
HF cache: $HOME/NymphsData/cache/huggingface
```

Recommended repo layout:

```text
nymph.json
README.md
docs/PIXAL3D_MODULE_HANDOFF.md
scripts/
  _pixal3d_common.sh
  install_pixal3d.sh
  pixal3d_status.sh
  pixal3d_start.sh
  pixal3d_stop.sh
  pixal3d_logs.sh
  pixal3d_open.sh
  pixal3d_open_outputs.sh
  pixal3d_open_weights.sh
  pixal3d_fetch_models.sh
  pixal3d_smoke_test.sh
  pixal3d_uninstall.sh
  api_server_pixal3d.py
ui/
  manager.html optional
```

Keep first implementation inference-only. Do not port Pixal3D training code.

## Proposed Manifest Shape

Use `NymphsModules/trellis/nymph.json` as the direct template, but replace the
GGUF quant action group with Pixal3D model fetch/profile controls.

Install fields:

```text
flash_attn_cuda_archs
flash_attn_jobs
flash_attn_nvcc_threads
```

These can likely mirror TRELLIS because upstream Pixal3D says to follow
TRELLIS.2 install first and uses `ATTN_BACKEND=flash_attn` by default.

Model fetch action group fields:

```text
profile:
  recommended_low_vram
  full_quality

hf_token:
  optional secret

license_ack:
  required select; must be "yes" before Fetch Models downloads Pixal3D or RMBG
```

Potential fetch modes:

```text
core_pixal3d      -> TencentARC/Pixal3D only
recommended       -> Pixal3D + MoGe + DINOv3 + RMBG + NAF if resolvable
all               -> same as recommended plus any optional app/demo assets
```

Be explicit in UI copy that the checkpoint download is large, around 24 GB for
Pixal3D ckpts before auxiliary model caches.

## Backend API Contract

Expose the same minimal HTTP contract as TRELLIS so the Blender addon can reuse
as much as possible:

```text
GET  /health
GET  /server_info
GET  /active_task
POST /generate
```

`/server_info` should return something like:

```json
{
  "status": "ready",
  "backend": "Pixal3D",
  "model_path": "TencentARC/Pixal3D",
  "resolved_model_path": "...",
  "subfolder": "main",
  "enable_tex": true,
  "mesh_retexture": false,
  "enable_t23d": false,
  "texture_only": false,
  "supports_manual_fov": true,
  "supports_low_vram": true,
  "supports_resolution": ["1024_cascade", "1536_cascade"],
  "model_ready": true,
  "aux_models_ready": true,
  "attention_backend": "flash_attn",
  "runtime_distro": "...",
  "runtime_user": "...",
  "hf_home": "..."
}
```

For first pass, `mesh_retexture=false`. Pixal3D's public app generates a textured
asset from an image and exports GLB. It does not expose the same selected-mesh
retexture path as the current TRELLIS GGUF adapter.

`POST /generate` should accept current addon-compatible fields where practical:

```text
image: base64 image
seed
remove_background
texture
max_num_tokens
texture_size
decimation_target
ss_sampling_steps
ss_guidance_strength
ss_guidance_rescale
ss_rescale_t
shape_sampling_steps
shape_guidance_strength
shape_guidance_rescale
shape_rescale_t
tex_sampling_steps
tex_guidance_strength
tex_guidance_rescale
tex_rescale_t
```

Add Pixal3D-specific optional fields:

```text
pixal3d_low_vram: bool
pixal3d_resolution: 1024|1536
pixal3d_manual_fov: float degrees or radians, choose one and document
pixal3d_mesh_scale: float
pixal3d_extend_pixel: int
pixal3d_image_resolution: int
```

Server should convert current TRELLIS-style payload names into upstream
Pixal3D names internally:

```text
shape_sampling_steps           -> shape_slat_sampling_steps
shape_guidance_strength        -> shape_slat_guidance_strength
shape_guidance_rescale         -> shape_slat_guidance_rescale
shape_rescale_t                -> shape_slat_rescale_t
pipeline_type 1024_cascade     -> resolution 1024
pipeline_type 1536_cascade     -> resolution 1536
```

Ignore unsupported fields harmlessly:

```text
gguf_quant
foreground_ratio
sparse_structure_resolution
sampler overrides
texture_alpha_mode
texture_double_sided
texture_uv_method
texture_inpainting
texture_bake_vertices
texture_custom_normals
retexture mesh payload
```

## Backend Implementation Notes

Do not shell out to `inference.py` for every request in the production adapter
unless a first smoke test needs the shortest path. A persistent API server is
better because it can cache:

```text
Pixal3D pipeline
projection DINOv3 feature extractors
RMBG model
possibly MoGe in CPU/low-VRAM mode
```

Use upstream's low-VRAM mode by default for a first Nymph module because the
current product target has cared about 16 GB class GPUs. Standard mode can be an
advanced module setting after validation.

Upstream low-VRAM behavior:

- keeps models on CPU and moves each stage to GPU on demand
- defaults to 1024 resolution
- can force 1536 with `--resolution 1536`, but this should be treated as risky
  until tested locally

Recommended first defaults:

```text
low_vram=true
resolution=1024
max_num_tokens=49152
texture_size=2048 or 4096 after local test
decimation_target=500000 or 1000000 after local test
manual_fov disabled / auto MoGe
mesh_scale=1.0
extend_pixel=0
image_resolution=512
```

## Blender Addon Addition Plan

Current addon 3D shape path is hard-coded to one selected service:

```python
def _selected_3d_service_key(state):
    return "trellis"
```

Current service registry only has:

```python
SERVICE_LABELS = {
    "n2d2": "Z-Image",
    "trellis": "TRELLIS.2 GGUF",
}
SERVICE_ORDER = ("n2d2", "trellis")
```

Add Pixal3D as a separate service:

```python
DEFAULT_PIXAL3D_PORT = "8096"
DEFAULT_REPO_PIXAL3D_PATH = "~/Pixal3D"
DEFAULT_PIXAL3D_PYTHON_PATH = "~/TRELLIS.2/.venv/bin/python"

SERVICE_LABELS["pixal3d"] = "Pixal3D"
SERVICE_PROP_PREFIXES["pixal3d"] = "service_pixal3d"
SERVICE_ORDER = ("n2d2", "trellis", "pixal3d")
```

Add state fields:

```text
service_pixal3d_enabled
service_pixal3d_port
service_pixal3d_show
service_pixal3d_launch_state
service_pixal3d_launch_detail
service_pixal3d_backend_summary
repo_pixal3d_path
pixal3d_python_path
pixal3d_low_vram
pixal3d_resolution
pixal3d_manual_fov
pixal3d_mesh_scale
pixal3d_extend_pixel
pixal3d_image_resolution
```

Add a user-facing selector for 3D runtime:

```text
Shape Runtime:
  TRELLIS.2 GGUF
  Pixal3D
```

Then make:

```python
def _selected_3d_service_key(state):
    return "pixal3d" if state.shape_backend == "PIXAL3D" else "trellis"
```

Texture selected-mesh retexture should stay on TRELLIS for first pass:

```python
def _selected_texture_service_key(state):
    return "trellis"
```

Pixal3D should not appear in the `Nymphs Texture` selected-mesh retexture panel
until a real backend method exists for mesh retexturing.

## Blender Addon Launch Plan

Extend `_service_port` default selection:

```text
n2d2    -> 8090
trellis -> 8095
pixal3d -> 8096
```

Extend `_compose_wsl_launch` with a Pixal3D branch:

```text
repo_path = state.repo_pixal3d_path or ~/Pixal3D
python_path = state.pixal3d_python_path or ~/TRELLIS.2/.venv/bin/python
script_name = scripts/api_server_pixal3d.py
PIXAL3D_OUTPUT_DIR=$HOME/NymphsData/outputs/pixal3d
PIXAL3D_LOG_DIR=$HOME/NymphsData/logs/pixal3d
PIXAL3D_CONFIG_DIR=$HOME/NymphsData/config/pixal3d
PIXAL3D_PORT=<port>
PIXAL3D_HOST=0.0.0.0
PIXAL3D_LOW_VRAM=1/0
```

Launch args:

```text
--host 0.0.0.0
--port 8096
--python-path <python_path>
--low-vram or --no-low-vram
--resolution 1024|1536
```

Extend `_stop_shell_for_service`:

```text
pkill -f "scripts/api_server_pixal3d.py --host 0.0.0.0 --port <port>"
```

Extend `_runtime_vram_estimate`:

```text
Pixal3D low-VRAM: 16 GB target, resolution 1024, MoGe camera estimation
Pixal3D standard: high VRAM, resolution 1536
```

## Blender Addon Capability Parsing

Extend `_backend_family(info)`:

```python
if backend_name == "pixal3d":
    return "Pixal3D"
```

Extend `_server_capabilities_from_info(info)`:

```text
family=Pixal3D
shape=true unless texture_only
texture=enable_tex true
retexture=false for first pass
multiview=false
text=false
```

Extend `_summarize_server_info(info)` to display:

```text
Pixal3D | TencentARC/Pixal3D | low_vram=true | resolution=1024 | attn=flash_attn | shape=true | tex=true | retexture=false
```

Do not let Pixal3D summaries accidentally become `TRELLIS.2` only because
`model_path` or `subfolder` contains "trellis". Use explicit `backend=Pixal3D`
from the server.

## Blender Addon Payload Plan

Current `_build_shape_payload` can mostly work if the Pixal3D API accepts
TRELLIS-style fields and ignores unsupported GGUF-only fields.

Add a backend-specific payload extender:

```python
def _with_3d_runtime_payload(state, payload):
    service_key = _selected_3d_service_key(state)
    if service_key == "trellis":
        payload["gguf_quant"] = state.trellis_gguf_quant
    elif service_key == "pixal3d":
        payload["pixal3d_low_vram"] = state.pixal3d_low_vram
        payload["pixal3d_resolution"] = state.pixal3d_resolution
        payload["pixal3d_manual_fov"] = state.pixal3d_manual_fov
        payload["pixal3d_mesh_scale"] = state.pixal3d_mesh_scale
        payload["pixal3d_extend_pixel"] = state.pixal3d_extend_pixel
        payload["pixal3d_image_resolution"] = state.pixal3d_image_resolution
    return payload
```

Then replace `_with_trellis_runtime_payload(...)` calls in shape payload path.
Keep texture/retexture payload TRELLIS-specific for now.

UI gating:

- Hide `GGUF Quant` when Pixal3D is selected.
- Hide GGUF-only controls for Pixal3D:
  - foreground ratio
  - sparse structure resolution
  - global/stage sampler name overrides
  - GGUF texture material controls
  - UV/inpainting controls from the GGUF adapter
- Show Pixal3D controls:
  - Low VRAM
  - Resolution 1024/1536
  - Manual FOV optional
  - Mesh scale
  - Extend pixel
  - Image resolution

Suggested first UI copy:

```text
Pixal3D uses camera-aware pixel projection. Auto camera uses MoGe; manual FOV is
for correcting difficult source images.
```

## Manager Module UI

A full custom Manager UI is optional for the first pass. Native action groups in
`nymph.json` are enough for:

```text
Fetch Models
Low-VRAM profile selector
Open Weights
Open Outputs
Smoke Test
Logs
```

If a `ui/manager.html` is added later, keep it for compact status/test controls,
not for long downloads during page load. Long fetches should use
`nymphs-module-action://fetch_models` or native `manager_action_groups`.

## Validation Plan

Phase 1: local upstream smoke test outside Nymph module.

```bash
cd /tmp/Pixal3D
python inference.py --image assets/images/0_img.png --output /tmp/pixal3d-test.glb --low_vram --resolution 1024
```

Phase 2: module install/fetch/status/start.

```bash
~/Pixal3D/scripts/pixal3d_status.sh
~/Pixal3D/scripts/pixal3d_fetch_models.sh
~/Pixal3D/scripts/pixal3d_start.sh
curl -s http://127.0.0.1:8096/server_info
curl -s http://127.0.0.1:8096/active_task
```

Phase 3: API generate smoke.

- Send a small image as base64 to `/generate`.
- Confirm GLB bytes return.
- Confirm output imports into Blender with correct orientation.
- Confirm textures are visible in Blender. Upstream CLI exports with
  `extension_webp=True`; Nymph TRELLIS GGUF disabled WebP for Blender
  compatibility. Test both; prefer standard PNG embedded GLB if WebP imports as
  geometry-only on target Blender versions.

Phase 4: addon integration.

- Start Pixal3D from `Nymphs Server`.
- Select Pixal3D in `Nymphs Shape`.
- Generate Shape + Texture.
- Confirm progress polling via `/active_task`.
- Confirm output imports and result folder opens.
- Confirm `Nymphs Texture` still uses TRELLIS for selected-mesh retexture.

### Local Validation Results 2026-05-17

Validation environment:

```text
GPU: NVIDIA GeForce RTX 4080 SUPER, compute capability 8.9
Driver: 595.79, driver-reported CUDA 13.2
Toolkit: /usr/local/cuda-13.0, nvcc V13.0.88
Python: 3.10.20
Torch: 2.11.0+cu130
Torch CUDA runtime: 13.0
torchvision: 0.26.0+cu130
Transformers: 4.57.3
tokenizers: 0.22.1
huggingface-hub: 0.36.2
NATTEN: 0.21.6+torch2110cu130 / import reports 0.21.6
diffusers: 0.37.1
accelerate: 1.13.0
gradio: 6.0.1
plyfile: 1.1.3
opencv-python: 4.13.0.92
MoGe: 2.0.0
pipeline:
  git+https://github.com/EasternJournalist/pipeline.git@866f059d2a05cde05e4a52211ec5051fd5f276d6
utils3d:
  https://github.com/LDYang694/Storages/releases/download/20260430/utils3d-0.0.2-py3-none-any.whl
  plus generated utils3d.pt/utils3d.np aliases for MoGe compatibility
```

Dependency health check:

```text
pip check: No broken requirements found.
```

Validated imports/native deps:

```text
flash_attn 2.8.3
nvdiffrast.torch
cumesh
flex_gemm
o_voxel
natten
moge
pixal3d.pipelines.pixal3d_image_to_3d
```

FlashAttention validation:

```text
Upstream `inference.py` uses `os.environ.setdefault("ATTN_BACKEND", "flash_attn")`.
The successful smoke commands did not set `ATTN_BACKEND=sdpa`, so Pixal3D used
the upstream default `flash_attn` backend.
Additional CUDA kernel smoke on 2026-05-17:
flash_attn_qkvpacked_func -> output shape (2, 128, 8, 64), dtype torch.float16,
all finite.
```

The generation logs also explicitly printed:

```text
[SPARSE] Conv backend: flex_gemm; Attention backend: flash_attn
[ATTENTION] Using backend: flash_attn
```

End-to-end smoke tests:

```text
1. Official Pixal3D + unauthenticated official RMBG:
   command:
     python inference.py --image assets/images/0_img.png --low_vram --resolution 1024 --fov 0.8575560450553894
   result:
     FAILED before generation
   reason:
     briaai/RMBG-2.0 is gated. Without authenticated accepted access, Hugging Face
     returned GatedRepoError / HTTP 401 for config.json.

2. Public BiRefNet substitute before Transformers pin:
   command:
     python inference.py --image assets/images/0_img.png --low_vram --resolution 1024 --fov 0.8575560450553894
   result:
     FAILED during DINO feature extraction
   reason:
     transformers==5.5.4 exposes a DINOv3 model shape Pixal3D does not expect:
     AttributeError: 'DINOv3ViTModel' object has no attribute 'layer'

3. Public BiRefNet substitute after Transformers pin:
   command:
     python inference.py --image assets/images/0_img.png --low_vram --resolution 1024 --fov 0.8575560450553894
   result:
     PASSED
   output:
     /home/nymph/NymphsData/outputs/pixal3d-validation/pixal3d_smoke_public_birefnet_lowvram_1024_after_tf_pin.glb
     37,646,140 bytes, glTF binary v2

4. Official Pixal3D + official gated BRIA RMBG after HF access form acceptance:
   command:
     python inference.py --image assets/images/0_img.png --low_vram --resolution 1024 --fov 0.8575560450553894
   result:
     PASSED
   output:
     /home/nymph/NymphsData/outputs/pixal3d-validation/pixal3d_smoke_official_rmbg_lowvram_1024.glb
     37,431,340 bytes, glTF binary v2
```

Successful run behavior observed in logs:

```text
Pipeline loaded from TencentARC/Pixal3D for the official smoke.
Low-VRAM mode was enabled.
Manual FOV was used: 49.13 degrees / 0.8576 rad, distance=1.0938.
Pipeline type was 1024_cascade.
Sampling stages completed:
  - sparse structure (proj), 12 steps
  - shape SLat (proj), 12 steps
  - HR shape SLat (proj, 1024), 12 steps
  - texture SLat (proj), 12 steps
GLB extraction completed all 6 phases:
  - Building BVH
  - Cleaning mesh
  - Parameterizing new mesh
  - Sampling attributes
  - Finalizing mesh
```

GLB validation:

```text
file:
  both successful outputs are glTF binary model, version 2

trimesh:
  both outputs opened as trimesh.Scene with 1 geometry
```

Warnings seen but not blockers:

```text
transformers/timm emitted FutureWarning messages for old timm import paths.
cumesh emitted a torch.cross deprecation warning during remeshing.
Hugging Face warned that remote code files were downloaded for BiRefNet/RMBG.
Module implementation should pin revisions where practical when using
trust_remote_code-style model code.
```

MoGe auto camera validation:

```text
MoGeModel.from_pretrained("Ruicheng/moge-2-vitl") loaded on CUDA.
get_camera_params_wild_moge(...) returned:
camera_angle_x=0.4432972744377575
distance=2.218759536743164
mesh_scale=1.0
```

Dependency corrections discovered during validation:

```text
CUDA 13 works for this stack:
torch==2.11.0+cu130, torchvision==0.26.0+cu130, natten==0.21.6+torch2110cu130,
flash_attn==2.8.3, CUDA Toolkit 13.0, RTX 4080 SUPER.

transformers==5.5.4 fails Pixal3D DINO extraction:
AttributeError: 'DINOv3ViTModel' object has no attribute 'layer'

transformers==4.57.3 works and exposes DINOv3ViTModel.layer.

The README-level `natten==0.21.0` is not the validated CUDA 13 target. Use the
Torch/CUDA-matched NATTEN wheel from https://whl.natten.org.

Pixal3D README utils3d-0.0.2 wheel includes the legacy
`utils3d.torch.intrinsics_from_fov_xy` API needed by Pixal3D/TRELLIS.2 render
paths. MoGe auto camera also needs `utils3d.pt`, so the module creates
`utils3d.pt` and `utils3d.np` aliases after installing the wheel.

Do not install `EasternJournalist/utils3d@3fab839f0be9931dac7c8488eb0e1600c236e183`
for Pixal3D. It satisfies the newer MoGe-style import shape after alias repair
but lacks `intrinsics_from_fov_xy`, causing generation to finish sampling and
then fail during render/projection.
```

Implementation lessons learned:

```text
- Treat CUDA 13 as validated, not speculative, for the exact package set above.
- Treat flash-attn as required. Do not add a silent SDPA fallback in Nymph.
- Fetch Models must explicitly handle BRIA RMBG gated access. Token plus accepted
  HF form is required; token alone can still fail.
- The module details page must explain Pixal3D academic-only/non-commercial,
  no-production, not-for-EU license language and link directly to the BRIA form.
- Use an acknowledgement gate before downloading Pixal3D/RMBG weights; do not
  call it a waiver.
- Pin Transformers to 4.57.3 until Pixal3D updates its DINO extraction code for
  newer Transformers model internals.
- Use the Pixal3D README `utils3d-0.0.2` wheel and create `utils3d.pt` /
  `utils3d.np` aliases for auto camera. Do not use MoGe's newer pinned
  `utils3d` commit for Pixal3D; it lacks `intrinsics_from_fov_xy`.
- Do not base Pixal3D on the TRELLIS GGUF loader. It needs the TRELLIS.2-style
  native/runtime surface but loads TencentARC/Pixal3D checkpoints directly.
- Keep NAF prefetch in the fetch path; first use downloads the GitHub repo and
  naf_release.pth into the torch hub cache.
- Standard 1536 and Blender texture import remain unvalidated; keep low_vram
  1024 as the default first profile.
```

## Risks And Open Questions

- VRAM: upstream standard mode is likely too heavy for a 16 GB default; keep
  low-VRAM default until tested.
- Model size: Pixal3D ckpts are around 24 GB before auxiliary models.
- Dependency friction: MoGe and Pixal3D disagree in docs around `utils3d`.
  Pixal3D needs the README wheel because render/projection paths call
  `utils3d.torch.intrinsics_from_fov_xy`; MoGe needs `utils3d.pt`, so the module
  creates `pt`/`np` aliases after installing the wheel.
- `flash_attn`: upstream defaults `ATTN_BACKEND=flash_attn`. Although upstream
  documents `ATTN_BACKEND=sdpa` as a fallback, this Nymph module should hard
  require flash-attn and fail fast if import or CUDA kernel smoke fails.
- NAF: confirm whether `torch.hub.load("valeoai/NAF", "naf", ...)` needs a
  separate prefetch path for offline/managed installs.
- Blender GLB textures: test `extension_webp=True` vs `False`.
- Retexture: do not promise selected-mesh retexture until implemented and tested.
- Registry: `pixal3d` has been published to
  `NymphsModules/nymphs-registry/nymphs.json`. Keep future manifest changes in
  sync with the registry entry, especially `category`, `kind`, `packaging`, and
  the license/access overview text.

## Recommended First Implementation Order

1. Create `NymphsModules/pixal3d` from the TRELLIS module shape.
2. Build `install_pixal3d.sh` with separate venv and Pixal3D requirements.
3. Build `pixal3d_fetch_models.sh` for `TencentARC/Pixal3D` and auxiliary model
   caches.
4. Build `api_server_pixal3d.py` using upstream `inference.py` logic but with a
   persistent process and Nymph-compatible `/server_info`, `/active_task`, and
   `/generate`.
5. Validate low-VRAM 1024 generation from curl.
6. Add addon service entry for Pixal3D on port 8096.
7. Add shape runtime selector and Pixal3D-specific payload/UI controls.
8. Test Blender import and texture visibility.
9. Add registry entry after module repo is pushed and raw `nymph.json` opens.

## Deep Dive Addendum: Nymphs Backbone Contracts

This addendum is based on a code read of the current Manager, module examples,
and Blender addon, plus a fresh clone of `TencentARC/Pixal3D` at:

```text
6a4b9f3787e3692257604937cd45cb54e80ac9a0
6a4b9f3 2026-05-16 fix: align inference.py GLB export params with app.py (texture_size=4096, decimation=1M)
```

The main architectural conclusion:

```text
Pixal3D should be its own Nymph module and its own Blender service.
Do not bolt it onto the TRELLIS GGUF quant switch.
Do not require the existing TRELLIS GGUF module to be installed.
```

Reason:

- The Manager can discover and run any module from `nymph.json` plus lifecycle
  scripts.
- The addon hardcodes service keys, backend labels, ports, paths, and payload
  behavior.
- Pixal3D shares TRELLIS.2 code lineage, but it is not a GGUF backend and it
  does not load `Aero-Ex/Trellis2-GGUF`.
- Pixal3D upstream assumes a TRELLIS.2 base environment for native packages such
  as `o_voxel`, `cumesh`, `flex_gemm`, `nvdiffrast`, and attention/sparse
  kernels. The Nymph module must own that install recipe instead of assuming
  some other module's venv happens to exist.

Docs audited for the module standard:

```text
NymphsCore/docs/NYMPHS_MODULE_MAKING_GUIDE.md
NymphsCore/docs/NYMPH_MODULE_UI_STANDARD.md
```

Relevant doc rules applied here:

- The Manager owns the shell, registry, installed/available grouping, and
  standard lifecycle rail.
- The module owns install/update/uninstall/status/start/stop/open/logs,
  dependency setup, model fetch, custom actions, and runtime/data folders.
- Model fetch must be a module-owned action, preferably a native
  `ui.manager_action_groups` form.
- Generated outputs, logs, config, and reusable caches should live under
  `$HOME/NymphsData`.
- `Delete Data` must not blindly wipe shared caches like Hugging Face cache.
- Custom `ui/manager.html` is optional. Do not build one just to choose model
  downloads; native action groups are the intended fit.
- Status must be fast, timeout-safe, and safe when files are missing.

## Manager Backbone Findings

Manager manifest model:

```text
NymphModuleManifestInfo
  Id
  Name
  ShortName
  Category
  Kind
  Version
  Description
  OverviewDetail
  OverviewLinks
  ManifestUrl
  RepositoryUrl
  SourceSummary
  InstallRoot
  InstallFields
  InstallOptionsTitle
  ManagerUiTitle
  Capabilities
  ManagerActions
  ManagerActionGroups
  DevCapabilities
  SortOrder
```

The Manager reads:

- `install.root` or `install.path`, falling back to `runtime.install_root`.
- `install.fields` using the same field parser as action groups.
- `entrypoints` for standard lifecycle actions.
- `ui.manager_actions` for native buttons.
- `ui.manager_action_groups` for action forms such as model fetch.
- `ui.manager_ui` only when a custom installed UI is provided.

The Manager does not need hardcoded C# changes for Pixal3D if the module follows
the normal manifest/script contract. The Blender addon does need changes because
it has fixed service keys: `n2d2` and `trellis`.

## Manager Action Resolution

After install, Manager prefers the installed conventional script path:

```text
$INSTALL_ROOT/scripts/<module_id>_<action>.sh
```

For `pixal3d`, that means:

```text
$HOME/Pixal3D/scripts/pixal3d_status.sh
$HOME/Pixal3D/scripts/pixal3d_start.sh
$HOME/Pixal3D/scripts/pixal3d_stop.sh
$HOME/Pixal3D/scripts/pixal3d_logs.sh
...
```

If a conventional script is missing, Manager can resolve entrypoints from
`$INSTALL_ROOT/nymph.json` or the cached repo manifest. For a robust module, keep
both:

- conventional script names
- explicit `entrypoints` in `nymph.json`

Status actions are wrapped with a short timeout:

```text
Manager status timeout: 8 seconds overall
shell action status timeout prefix: timeout 6s
```

Therefore `pixal3d_status.sh` must not import torch, instantiate Pixal3D, scan
huge HF caches deeply, or touch the network. It should check marker files,
import readiness with a short lightweight Python command only after the venv is
present, and report `models_ready=false` quickly if cache files are missing.

## Status Output Contract

Manager parses only `key=value` lines. Important keys are:

```text
id
name
installed
runtime_present
data_present
version
env_ready
adapter_ready
runtime_ready
models_ready
running
state
health
url
install_root
venv
logs_dir
outputs_dir
config_dir
hf_cache_dir
marker
detail
```

Recommended Pixal3D status output:

```text
id=pixal3d
name=Pixal3D
installed=true
runtime_present=true
data_present=false
version=0.1.0
env_ready=true
adapter_ready=true
runtime_ready=true
models_ready=false
aux_models_ready=false
running=false
state=needs_attention
health=model-download-needed
url=http://127.0.0.1:8096
install_root=/home/nymph/Pixal3D
venv=/home/nymph/TRELLIS.2/.venv
logs_dir=/home/nymph/NymphsData/logs/pixal3d
outputs_dir=/home/nymph/NymphsData/outputs/pixal3d
config_dir=/home/nymph/NymphsData/config/pixal3d
hf_cache_dir=/home/nymph/NymphsData/cache/huggingface
torch_hub_dir=/home/nymph/NymphsData/cache/torch-hub
model_repo=TencentARC/Pixal3D
aux_repos=Ruicheng/moge-2-vitl,camenduru/dinov3-vitl16-pretrain-lvd1689m,briaai/RMBG-2.0,valeoai/NAF
profile=low_vram_1024
marker=/home/nymph/Pixal3D/.nymph-module-version
detail=Runtime exists, but Pixal3D model files are incomplete. Use Fetch Models.
```

Manager UI behavior to rely on:

- `models_ready=false` becomes "Model download needed".
- `runtime_present=true` and `data_present=true` show secondary details.
- `url` appears in module secondary status when installed.
- `health=model-download-needed` or `health=degraded` makes the card require
  attention.
- `running=true` makes the card green.

## Pixal3D `nymph.json` Blueprint

Recommended identity:

```json
{
  "manifest_version": 1,
  "id": "pixal3d",
  "name": "Pixal3D",
  "short_name": "PX",
  "version": "0.1.0",
  "description": "Local Pixal3D image-to-3D backend packaged as an installable Nymph module.",
  "category": "3d",
  "packaging": "repo"
}
```

Recommended install/runtime roots:

```json
{
  "install": {
    "title": "PIXAL3D RUNTIME OPTIONS",
    "root": "$HOME/Pixal3D",
    "entrypoint": "scripts/install_pixal3d.sh",
    "version_marker": "$HOME/Pixal3D/.nymph-module-version",
    "installed_markers": [
      "$HOME/Pixal3D/.nymph-module-version"
    ]
  },
  "runtime": {
    "host": "127.0.0.1",
    "port": 8096,
    "health_url": "http://127.0.0.1:8096/health",
    "server_info_url": "http://127.0.0.1:8096/server_info"
  }
}
```

Recommended artifacts:

```json
{
  "artifacts": {
    "models_root": "$HOME/NymphsData/models",
    "cache_root": "$HOME/NymphsData/cache",
    "outputs_root": "$HOME/NymphsData/outputs/pixal3d",
    "logs_root": "$HOME/NymphsData/logs/pixal3d",
    "config_root": "$HOME/NymphsData/config/pixal3d",
    "huggingface_cache": "$HOME/NymphsData/cache/huggingface",
    "torch_hub": "$HOME/NymphsData/cache/torch-hub",
    "legacy_outputs_root": "$HOME/Pixal3D/outputs",
    "legacy_logs_root": "$HOME/Pixal3D/logs"
  }
}
```

Recommended entrypoints:

```json
{
  "entrypoints": {
    "install": "scripts/install_pixal3d.sh",
    "update": "scripts/pixal3d_update.sh",
    "status": "scripts/pixal3d_status.sh",
    "start": "scripts/pixal3d_start.sh",
    "stop": "scripts/pixal3d_stop.sh",
    "open": "scripts/pixal3d_open.sh",
    "logs": "scripts/pixal3d_logs.sh",
    "fetch_models": "scripts/pixal3d_fetch_models.sh",
    "smoke_test": "scripts/pixal3d_smoke_test.sh",
    "uninstall": "scripts/pixal3d_uninstall.sh",
    "open_weights": "scripts/pixal3d_open_weights.sh",
    "open_outputs": "scripts/pixal3d_open_outputs.sh"
  }
}
```

Recommended Manager actions:

```json
{
  "ui": {
    "sort_order": 45,
    "manager_action_groups": [
      {
        "id": "model_fetch",
        "title": "Model Fetch",
        "layout": "compact",
        "entrypoint": "fetch_models",
        "result": "show_logs",
        "visibility": "installed",
        "description": "Install sets up the Pixal3D runtime only. Fetch Models downloads TencentARC/Pixal3D and auxiliary camera/background/projection models. This does not download TRELLIS GGUF quants.",
        "fields": [
          {
            "name": "profile",
            "type": "select",
            "label": "Profile",
            "arg": "--profile",
            "default": "low_vram_1024",
            "options": [
              {
                "label": "Low VRAM 1024",
                "value": "low_vram_1024",
                "description": "Recommended first test; lower peak VRAM and 1024 cascade"
              },
              {
                "label": "Standard 1536",
                "value": "standard_1536",
                "description": "Heavier profile for high VRAM systems"
              }
            ]
          },
          {
            "name": "hf_token",
            "type": "secret",
            "label": "Hugging Face token",
            "secret_id": "huggingface.token",
            "env": "NYMPHS3D_HF_TOKEN",
            "optional": true
          },
          {
            "name": "license_ack",
            "type": "select",
            "label": "License/access acknowledgement",
            "arg": "--license-ack",
            "default": "no",
            "options": [
              {
                "label": "Not yet",
                "value": "no",
                "description": "Do not fetch gated/non-commercial Pixal3D assets yet"
              },
              {
                "label": "I acknowledge",
                "value": "yes",
                "description": "I understand Pixal3D is academic-only, not for commercial/production use, not intended for EU use, and BRIA RMBG requires its HF access form"
              }
            ]
          }
        ],
        "submit": {
          "label": "Fetch Models"
        }
      }
    ]
  }
}
```

## Module Directory Layout

Recommended first repo layout:

```text
NymphsModules/pixal3d/
  nymph.json
  README.md
  docs/
    PIXAL3D_MODULE_NOTES.md
  scripts/
    _pixal3d_common.sh
    install_pixal3d.sh
    pixal3d_update.sh
    pixal3d_status.sh
    pixal3d_start.sh
    pixal3d_stop.sh
    pixal3d_logs.sh
    pixal3d_open.sh
    pixal3d_open_outputs.sh
    pixal3d_open_weights.sh
    pixal3d_fetch_models.sh
    pixal3d_smoke_test.sh
    pixal3d_uninstall.sh
    api_server_pixal3d.py
    pixal3d_model_common.py
  patches/
    README.md
```

If we vendor/derive from upstream Pixal3D directly, the installed root should
contain upstream code plus Nymph scripts:

```text
$HOME/Pixal3D/
  pixal3d/
  assets/
  inference.py
  app.py
  requirements.txt
  scripts/
  .venv/
  .nymph-module-version
```

## `_pixal3d_common.sh` Blueprint

Core variables:

```bash
PIXAL3D_INSTALL_ROOT="${PIXAL3D_INSTALL_ROOT:-${NYMPHS3D_PIXAL3D_DIR:-$HOME/Pixal3D}}"
PIXAL3D_VENV_DIR="${PIXAL3D_VENV_DIR:-$PIXAL3D_INSTALL_ROOT/.venv}"
NYMPHS_DATA_ROOT="${NYMPHS_DATA_ROOT:-$HOME/NymphsData}"
PIXAL3D_CONFIG_DIR="${PIXAL3D_CONFIG_DIR:-$NYMPHS_DATA_ROOT/config/pixal3d}"
PIXAL3D_PRESET_FILE="${PIXAL3D_PRESET_FILE:-$PIXAL3D_CONFIG_DIR/profile.env}"
PIXAL3D_OUTPUT_DIR="${PIXAL3D_OUTPUT_DIR:-$NYMPHS_DATA_ROOT/outputs/pixal3d}"
PIXAL3D_LOG_DIR="${PIXAL3D_LOG_DIR:-$NYMPHS_DATA_ROOT/logs/pixal3d}"
PIXAL3D_PID_FILE="${PIXAL3D_PID_FILE:-$PIXAL3D_LOG_DIR/pixal3d.pid}"
PIXAL3D_HOST="${PIXAL3D_HOST:-127.0.0.1}"
PIXAL3D_PORT="${PIXAL3D_PORT:-8096}"
PIXAL3D_SERVER_URL="${PIXAL3D_SERVER_URL:-http://${PIXAL3D_HOST}:${PIXAL3D_PORT}}"
PIXAL3D_MODEL_REPO_ID="${PIXAL3D_MODEL_REPO_ID:-TencentARC/Pixal3D}"
PIXAL3D_MOGE_REPO_ID="${PIXAL3D_MOGE_REPO_ID:-Ruicheng/moge-2-vitl}"
PIXAL3D_DINOV3_REPO_ID="${PIXAL3D_DINOV3_REPO_ID:-camenduru/dinov3-vitl16-pretrain-lvd1689m}"
PIXAL3D_RMBG_REPO_ID="${PIXAL3D_RMBG_REPO_ID:-briaai/RMBG-2.0}"
```

Environment exports:

```bash
export OPENCV_IO_ENABLE_OPENEXR="${OPENCV_IO_ENABLE_OPENEXR:-1}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
export HF_HUB_DISABLE_XET="${HF_HUB_DISABLE_XET:-1}"
export NYMPHS3D_HF_CACHE_DIR="${NYMPHS3D_HF_CACHE_DIR:-$NYMPHS_DATA_ROOT/cache/huggingface}"
export HF_HOME="${HF_HOME:-$NYMPHS_DATA_ROOT/cache/huggingface-home}"
export HF_HUB_CACHE="${HF_HUB_CACHE:-$NYMPHS3D_HF_CACHE_DIR}"
export TORCH_HOME="${TORCH_HOME:-$NYMPHS_DATA_ROOT/cache/torch-hub}"
export PIXAL3D_OUTPUT_DIR
export PIXAL3D_MODEL_REPO_ID
```

Functions should mirror TRELLIS:

```bash
pixal3d_ensure_data_dirs
pixal3d_python
pixal3d_pip
pixal3d_is_running
pixal3d_probe_url
pixal3d_site_packages_dir
```

## Install Script Design

The install script should be conservative and separate from TRELLIS GGUF:

```text
1. Install system packages:
   python3.10, python3.10-venv, python3.10-dev, git, curl, cmake,
   build-essential, pkg-config, libegl1-mesa-dev, libgl1, libglib2.0-0,
   ccache, ninja.

2. Sync module/upstream source into $HOME/Pixal3D.

3. Create or repair $HOME/TRELLIS.2/.venv with Python 3.10.

4. Install/upgrade pip, setuptools, wheel, ninja.

5. Install PyTorch. Start with the same torch policy as TRELLIS module unless
   Pixal3D dependency testing proves a stricter pin is required.

6. Install base TRELLIS/Pixal3D Python deps:
   imageio, imageio-ffmpeg, tqdm, easydict, opencv-python-headless, trimesh,
   transformers, gradio, tensorboard, pandas, lpips, zstandard, kornia, timm,
   psutil, plyfile, diffusers==0.37.1, accelerate==1.13.0.

7. Install Pixal3D extra deps:
   git+https://github.com/microsoft/MoGe.git
   natten==0.21.0
   https://github.com/LDYang694/Storages/releases/download/20260430/utils3d-0.0.2-py3-none-any.whl

8. Install native TRELLIS-style runtime pieces:
   flash-attn
   CuMesh
   FlexGEMM
   nvdiffrast
   o-voxel

9. Compile-check scripts/api_server_pixal3d.py.

10. Write .nymph-module-version.
```

Critical install decision:

```text
Do rely on $HOME/TRELLIS.2/.venv for the shared native runtime.
Do not require TRELLIS model weights for Pixal3D.
Do not require the TRELLIS GGUF service to be running for Pixal3D.
```

Why: Pixal3D and TRELLIS.2 share the heavy CUDA/native Python stack. Each module
installer must be able to create or repair the shared venv so the user does not
have to discover a hidden prerequisite.

Native package source choices:

- Best first pass: reuse the TRELLIS module's pinned install strategy for
  `CuMesh`, `FlexGEMM`, `nvdiffrast`, `utils3d`, and `o-voxel`.
- Investigate whether upstream Pixal3D works with prebuilt wheels from
  `requirements-hfdemo.txt`, but do not make H-series demo wheels the default
  for local Nymph installs. They are documented upstream as HF demo specific.
- Do not expose `ATTN_BACKEND=sdpa` as an install/runtime fallback for this
  module. The module should set/require `ATTN_BACKEND=flash_attn` and fail fast
  if flash-attn is unavailable.

## Model Fetch Design

Fetch script should download all model files into shared Nymph cache roots, not
inside disposable runtime directories:

```text
$HOME/NymphsData/cache/huggingface
$HOME/NymphsData/cache/huggingface-home
$HOME/NymphsData/cache/torch-hub
```

Required main repo:

```text
TencentARC/Pixal3D
```

Allow patterns for snapshot download:

```text
pipeline.json
ckpts/*.json
ckpts/*.safetensors
README.md
```

Auxiliary repos:

```text
Ruicheng/moge-2-vitl
camenduru/dinov3-vitl16-pretrain-lvd1689m
briaai/RMBG-2.0
valeoai/NAF via torch.hub
```

Fetch script should emit progress lines similar to TRELLIS:

```text
MODEL FETCH STARTED: step=1/5 repo=TencentARC/Pixal3D
MODEL FETCH STATUS: step=1/5 status=downloading cache_total=...
MODEL FETCH COMPLETE: step=1/5 repo=TencentARC/Pixal3D root=...
```

Recommended steps:

```text
1. Main Pixal3D ckpts.
2. DINOv3 model.
3. MoGe model.
4. RMBG model.
5. NAF torch hub prefetch.
```

RMBG fetch must handle the gated-model case explicitly. Suggested behavior:

```text
MODEL FETCH NEEDS ACCESS: repo=briaai/RMBG-2.0
Open https://huggingface.co/briaai/RMBG-2.0, complete BRIA's access form,
then rerun Fetch Models with a Hugging Face token from the same account.
```

Fetch should also refuse before any download unless the Manager action passes
`--license-ack yes`:

```text
LICENSE ACK REQUIRED:
Pixal3D permits academic use only, forbids commercial/production use, and says
it is not intended for use within the European Union.
BRIA RMBG-2.0 requires the Hugging Face access form:
https://huggingface.co/briaai/RMBG-2.0
Select "I acknowledge" in Fetch Models before downloading gated/non-commercial
weights.
```

NAF prefetch can be implemented by running a small Python snippet in the venv:

```python
import os
import torch
os.environ.setdefault("TORCH_HOME", os.path.expanduser("~/NymphsData/cache/torch-hub"))
torch.hub.load("valeoai/NAF", "naf", pretrained=True, device="cpu", trust_repo=True)
```

Status should not require the NAF hub call. The fetch/smoke test can verify it.

## API Server Blueprint

File:

```text
scripts/api_server_pixal3d.py
```

Required endpoints:

```text
GET  /health
GET  /server_info
GET  /active_task
POST /generate
```

Optional helpful endpoints:

```text
GET /outputs
GET /config
POST /reload
```

`/server_info` should return:

```json
{
  "status": "ok",
  "backend": "Pixal3D",
  "model_path": "TencentARC/Pixal3D",
  "subfolder": "",
  "device": "cuda",
  "dtype": "bf16/fp16 mixed",
  "enable_tex": true,
  "mesh_retexture": false,
  "texture_only": false,
  "low_vram": true,
  "resolution": 1024,
  "supported_resolutions": [1024, 1536],
  "attention_backend": "flash_attn",
  "model_cache_ready": true,
  "aux_models_ready": true,
  "runtime_distro": "NymphsCore",
  "output_dir": "/home/nymph/NymphsData/outputs/pixal3d"
}
```

`/active_task` should match addon expectations:

```json
{
  "id": "uuid-or-empty",
  "status": "idle|queued|processing|complete|failed",
  "stage": "Sampling HR shape SLat",
  "detail": "Pixal3D 1024 cascade",
  "progress": "3/5",
  "error": ""
}
```

The server should keep one active task at a time. Reject concurrent `/generate`
with HTTP 409 or queue exactly one request only if the addon already handles
queued state.

## API Generate Mapping

Accept current TRELLIS-style shape payloads so the addon patch can be smaller:

```text
image
seed
pipeline_type
max_num_tokens
texture_size
decimation_target
ss_sampling_steps
ss_guidance_strength
ss_guidance_rescale
ss_rescale_t
shape_sampling_steps
shape_guidance_strength
shape_guidance_rescale
shape_rescale_t
tex_sampling_steps
tex_guidance_strength
tex_guidance_rescale
tex_rescale_t
```

Map to Pixal3D names:

```text
shape_sampling_steps        -> shape_slat_sampling_steps
shape_guidance_strength     -> shape_slat_guidance_strength
shape_guidance_rescale      -> shape_slat_guidance_rescale
shape_rescale_t             -> shape_slat_rescale_t
tex_sampling_steps          -> tex_slat_sampling_steps
tex_guidance_strength       -> tex_slat_guidance_strength
tex_guidance_rescale        -> tex_slat_guidance_rescale
tex_rescale_t               -> tex_slat_rescale_t
pipeline_type=1024_cascade  -> resolution=1024
pipeline_type=1536_cascade  -> resolution=1536
```

Add Pixal3D-specific fields:

```text
pixal3d_low_vram
pixal3d_resolution
pixal3d_manual_fov
pixal3d_fov_unit
pixal3d_mesh_scale
pixal3d_extend_pixel
pixal3d_image_resolution
```

Ignore unsupported TRELLIS GGUF-only fields:

```text
gguf_quant
foreground_ratio
sparse_structure_resolution
sampler
sparse_structure_sampler
shape_sampler
tex_sampler
texture_alpha_mode
texture_double_sided
texture_bake_vertices
texture_custom_normals
texture_uv_method
texture_uv_angle
texture_inpainting
```

Return raw GLB bytes from `/generate`:

```text
HTTP 200
Content-Type: model/gltf-binary
Body: <binary .glb bytes>
```

The current Blender addon shape worker treats JSON from `/generate` as an
error, writes response bytes to a local `.glb`, and imports that file. A JSON
path/base64 response would require changing `_job_worker`, so do not use JSON as
the v1 generate response.

## Pixal3D Runtime Flow

Use upstream `inference.py` logic but refactor for a long-lived process:

```text
1. Decode incoming base64 image to a temp file or PIL image.
2. Initialize pipeline lazily on first request or at startup, depending on CLI.
3. Preprocess image with Pixal3D RMBG.
4. Estimate camera with MoGe unless manual FOV is provided.
5. Build sampler override dictionaries.
6. Run `pipeline.run(..., return_latent=True, pipeline_type="1024_cascade" or "1536_cascade")`.
7. Convert to GLB with `o_voxel.postprocess.to_glb`.
8. Apply upstream rotation transform.
9. Export GLB to `$PIXAL3D_OUTPUT_DIR` for logs/reuse.
10. Return the GLB file bytes as `model/gltf-binary`.
```

Default runtime profile:

```text
low_vram=true
resolution=1024
manual_fov=-1
mesh_scale=1.0
extend_pixel=0
image_resolution=512
max_num_tokens=49152
decimation_target=1000000
texture_size=4096 upstream, but test 2048/4096 in Blender
```

For Blender compatibility, test:

```text
glb.export(..., extension_webp=True)
glb.export(..., extension_webp=False)
```

If Blender imports geometry but not textures with WebP, default the Nymph API to
`extension_webp=False` even though upstream uses `True`.

## Blender Addon Patch Map

File:

```text
NymphsAddon/Nymphs.py
```

Add constants near current TRELLIS constants:

```python
DEFAULT_REPO_PIXAL3D_PATH = "~/Pixal3D"
DEFAULT_PIXAL3D_PYTHON_PATH = "~/TRELLIS.2/.venv/bin/python"
DEFAULT_PIXAL3D_PORT = "8096"
DEFAULT_PIXAL3D_RESOLUTION = "1024"
```

Extend service maps:

```python
SERVICE_LABELS = {
    "n2d2": "Z-Image",
    "trellis": "TRELLIS.2 GGUF",
    "pixal3d": "Pixal3D",
}

SERVICE_PROP_PREFIXES = {
    "n2d2": "service_n2d2",
    "trellis": "service_trellis",
    "pixal3d": "service_pixal3d",
}

SERVICE_ORDER = ("n2d2", "trellis", "pixal3d")
```

Add a 3D runtime selector instead of hardcoded `_selected_3d_service_key`:

```python
shape_3d_runtime: EnumProperty(
    name="Shape Runtime",
    items=(
        ("trellis", "TRELLIS.2 GGUF", "Use the quantized TRELLIS.2 GGUF backend"),
        ("pixal3d", "Pixal3D", "Use Pixal3D camera-aware pixel-projection backend"),
    ),
    default="trellis",
)
```

Then:

```python
def _selected_3d_service_key(state):
    value = getattr(state, "shape_3d_runtime", "trellis")
    return value if value in {"trellis", "pixal3d"} else "trellis"
```

Keep selected-mesh retexture on TRELLIS:

```python
def _selected_texture_service_key(state):
    return "trellis"
```

Add Pixal3D service state fields:

```python
service_pixal3d_enabled
service_pixal3d_port
service_pixal3d_show
service_pixal3d_launch_state
service_pixal3d_launch_detail
service_pixal3d_backend_summary
repo_pixal3d_path
pixal3d_python_path
pixal3d_low_vram
pixal3d_resolution
pixal3d_manual_fov
pixal3d_mesh_scale
pixal3d_extend_pixel
pixal3d_image_resolution
```

Extend `_service_port` default selection:

```python
if service_key == "pixal3d":
    default = DEFAULT_PIXAL3D_PORT
elif service_key == "trellis":
    default = DEFAULT_TRELLIS_PORT
else:
    default = DEFAULT_N2D2_PORT
```

Extend `_compose_wsl_launch` with a Pixal3D branch:

```text
repo_path: state.repo_pixal3d_path or ~/Pixal3D
python_path: state.pixal3d_python_path or ~/TRELLIS.2/.venv/bin/python
script: scripts/api_server_pixal3d.py
env:
  PIXAL3D_OUTPUT_DIR=$HOME/NymphsData/outputs/pixal3d
  PIXAL3D_LOG_DIR=$HOME/NymphsData/logs/pixal3d
  PIXAL3D_CONFIG_DIR=$HOME/NymphsData/config/pixal3d
  PIXAL3D_PID_FILE=$HOME/NymphsData/logs/pixal3d/pixal3d.pid
  PIXAL3D_PORT=<port>
  PIXAL3D_HOST=0.0.0.0
  TORCH_HOME=$HOME/NymphsData/cache/torch-hub
args:
  --host 0.0.0.0
  --port <port>
  --model-path TencentARC/Pixal3D
  --resolution 1024|1536
  --low-vram or --no-low-vram
```

Extend `_stop_shell_for_service`:

```text
pkill -f "scripts/api_server_pixal3d.py --host 0.0.0.0 --port <port>"
pkill -f "python scripts/api_server_pixal3d.py"
pkill -f "python3 scripts/api_server_pixal3d.py"
```

Extend backend family parsing:

```python
if backend_name == "pixal3d":
    return "Pixal3D"
```

Do this before fallback blob checks that might see "trellis" in a config path.

Extend capabilities:

```python
if family == "Pixal3D":
    return {
        "family": "Pixal3D",
        "shape": not texture_only,
        "texture": bool(info.get("enable_tex", True)),
        "retexture": bool(info.get("mesh_retexture", False)),
        "multiview": False,
        "text": False,
        "texture_only": texture_only,
    }
```

Extend server summary:

```text
Pixal3D | TencentARC/Pixal3D | low_vram=true | resolution=1024 | attn=flash_attn | shape=true | tex=true | retexture=false
```

## Addon UI Gating

Current shape panel draws `trellis_gguf_quant` before any workflow controls.
For Pixal3D:

- Show shape runtime selector first.
- If selected service is TRELLIS, show GGUF Quant.
- If selected service is Pixal3D, hide GGUF Quant.
- Draw service control row for the selected service.
- Reuse image path, seed, shape/texture checkbox, and sampler step controls
  where compatible.
- Hide TRELLIS-only material/UV/inpainting options for Pixal3D.
- Show Pixal3D camera controls near shape settings:
  - low VRAM toggle
  - resolution enum
  - manual FOV float; `-1` means auto MoGe
  - mesh scale
  - extend pixel
  - image resolution

Current texture panel should remain TRELLIS-only for first pass:

- Leave `_selected_texture_service_key(state)` returning `"trellis"`.
- Keep GGUF Quant in texture panel.
- Do not show Pixal3D there until selected-mesh retexture is actually
  implemented.

## Backbone Compatibility Answer

The precise answer to the backbone/runtime question:

```text
Pixal3D should not be built against the GGUF adapter runtime as its base. It
needs a TRELLIS.2-style code/native runtime surface.

The current TRELLIS GGUF fork is only usable as a base if it still preserves the
original TRELLIS.2/Pixal3D-compatible imports, native extensions, and pipeline
layout Pixal3D expects. If the fork is centered around `trellis2_gguf` loaders
and GGUF-specific model layout, treat it as incompatible for Pixal3D.

The regular released microsoft/TRELLIS.2-4B model weights do not appear to be a
separate Pixal3D inference dependency. Pixal3D inference loads
TencentARC/Pixal3D checkpoints.
```

More detail:

- `TencentARC/Pixal3D` provides its own safetensors checkpoint set.
- Its HF `pipeline.json` references `ckpts/...` under `TencentARC/Pixal3D`.
- The upstream inference path calls
  `Pixal3DImageTo3DPipeline.from_pretrained("TencentARC/Pixal3D")`.
- The current Nymph TRELLIS module loads
  `trellis2_gguf.pipelines.Trellis2ImageTo3DPipeline.from_pretrained(..., enable_gguf=True, gguf_quant=...)`.
- These are different loaders and weight formats.

## Acceptance Criteria

Module acceptance:

- `pixal3d_status.sh` completes under Manager status timeout.
- Install creates or repairs `$HOME/TRELLIS.2/.venv` and writes `.nymph-module-version`.
- Status reports `models_ready=false` before model fetch, without crashing.
- Fetch Models downloads main and auxiliary models into `NymphsData` caches.
- Start launches `http://127.0.0.1:8096`.
- `/server_info` returns `backend=Pixal3D`.
- `/active_task` returns idle/processing states compatible with addon polling.
- `/generate` accepts addon shape payload and returns a textured GLB.
- `pixal3d_stop.sh` stops the API process and cleans stale PID state.
- Uninstall preserves outputs/logs/cache by default.

Addon acceptance:

- Nymphs Server panel shows Pixal3D as a third service.
- Shape panel can select TRELLIS.2 GGUF or Pixal3D.
- TRELLIS behavior is unchanged when TRELLIS is selected.
- Pixal3D selection hides GGUF Quant and launches port 8096.
- Pixal3D generation imports a GLB into Blender.
- Texture panel still uses TRELLIS for selected-mesh retexture.

Current addon gate: these acceptance items are not complete until tested inside
Blender. Do not push or release the addon Pixal3D integration from compile-only
validation.

Research spike acceptance:

- Verify `natten==0.21.0` with the chosen Torch/CUDA stack.
- Verify `o_voxel`, `cumesh`, `flex_gemm`, and `nvdiffrast` build in the
  Pixal3D venv.
- Verify `ATTN_BACKEND=flash_attn` is active and a tiny flash-attn CUDA kernel
  smoke passes. Do not accept SDPA fallback for Pixal3D.
- Verify WebP vs non-WebP GLB texture import in target Blender.
- Measure VRAM for low_vram 1024 and standard 1536 on the user's actual GPU.

## 2026-05-20 Update: Real Pixal3D GGUF Path

Earlier notes in this handoff warned not to base Pixal3D on the TRELLIS GGUF
adapter because the original assumption was that `trellis2_gguf` only supported
`Aero-Ex/Trellis2-GGUF`. That assumption is incomplete.

Double-check result:

- The ComfyUI GGUF source already has an explicit `Pixal3D-GGUF` mode.
- In `ComfyUI-Trellis2-GGUF/nodes.py`, `modelname == "Pixal3D-GGUF"` switches
  the model repo to `Aero-Ex/Pixal3D-GGUF`.
- In `ComfyUI-Trellis2-GGUF/model_manager.py`, `PIXAL3D_REPO_PATH_MAP` maps:
  - `ss_dec_`, `shape_dec_`, `tex_dec_` to `decoder/`
  - `ss_flow_` to `Sparse/`
  - `slat_flow_img2shape_` to `shape/`
  - `slat_flow_imgshape2tex_` to `texture/`
- The ComfyUI loader then calls
  `Trellis2ImageTo3DPipeline.from_pretrained(..., enable_gguf=True, gguf_quant=..., isPixal3D=True)`.
- The Nymph TRELLIS module already adapted this ComfyUI GGUF stack to standalone
  use in the shared `$HOME/TRELLIS.2/.venv` by installing:
  - `trellis2_gguf`
  - `ComfyUI-GGUF` loader files: `ops.py`, `dequant.py`, `loader.py`
  - `gguf`, `sdnq`, `rembg`, `open3d`, `pymeshlab`, `meshlib`, and related runtime deps
  - standalone ComfyUI stubs and local-path resolution in
    `NymphsModules/trellis/scripts/trellis_gguf_common.py`

Therefore the real Pixal3D GGUF path is not to add a fake UI toggle or to
dequantize GGUF into ordinary safetensors. The real path is to reuse the working
TRELLIS standalone GGUF adaptation and invoke the existing Pixal3D branch of
`trellis2_gguf`.

Implementation target:

1. Add a Pixal3D equivalent of `trellis_gguf_common.py`, adapted for:
   - `GGUF_MODEL_REPO_ID = "Aero-Ex/Pixal3D-GGUF"`
   - Pixal3D cache dir `models--Aero-Ex--Pixal3D-GGUF`
   - required directories `Sparse`, `shape`, `texture`, and `decoder`
   - no TRELLIS support checkpoint requirement unless the imported loader proves
     one is still needed for a specific path
2. Ensure Pixal3D install/update verifies the shared venv already has the
   GGUF runtime bits from the TRELLIS module, or installs only those missing
   bits without rebuilding FlashAttention.
3. When `PIXAL3D_WEIGHT_FORMAT=gguf-experimental`, load via:

```python
from trellis2_gguf.pipelines import Trellis2ImageTo3DPipeline

pipeline = Trellis2ImageTo3DPipeline.from_pretrained(
    str(model_root),
    keep_models_loaded=False,
    enable_gguf=True,
    gguf_quant=quant,
    precision="bf16",
    isPixal3D=True,
)
```

4. Patch/bridge any Pixal3D-specific preprocessing, image-conditioner, camera,
   MoGe, and official app expectations around that pipeline object.
5. Add `Q4_K_M` to Pixal3D fetch/profile choices. The GGUF repo publishes Q4
   files and it is the most useful first VRAM test on the RTX 4080-class target.
6. Keep the current safetensors path as the default until GGUF completes a real
   generation smoke test. Do not expose GGUF as a normal user-facing runtime
   option until it actually produces a GLB.

Current conclusion:

- The GGUF weights are not useless.
- The module's current GGUF fetch-only behavior is incomplete.
- The fastest real bridge is to reuse the TRELLIS module's proven standalone
  `trellis2_gguf` method with `isPixal3D=True`.

## 2026-05-20 Update: NymphsCore App Shell

Keep the upstream Pixal3D app available at `/official` and the NymphsCore-owned
app available at `/nymph`.

Current app shell direction:

- Reference image and result preview are locked side by side in the main stage.
- The reference pane and GLB/result pane share the same footprint and scale with
  the WebView window.
- Controls live in the left column and scroll independently.
- Generation now skips preview-frame rendering in the Nymphs UI path. It samples
  the 3D latent model, packs state for export, builds the GLB, and loads the
  embedded model-viewer.
- Open Gradio starts the UI quickly, then begins a delayed model preload by
  default (`PIXAL3D_WARMUP_DELAY=3`). The app polls `/warmup_status` and shows
  model loading progress in the Run panel. Set `PIXAL3D_WARMUP_DELAY=0` to
  disable preload or `PIXAL3D_WARM_ON_START=1` only for deliberate immediate
  warmup tests.
- Texture export defaults to 1024.

GGUF fetch/status now includes `Q4_K_M` and accepts both the nested repo layout
and the root-level GGUF files published by the community Pixal3D GGUF repo.
GGUF remains experimental and must stay behind safetensors until a real
end-to-end GLB smoke test passes.

## 2026-05-20 Update: Official Ui + Nymphs Ui Buttons

Correction to the app shell routing:

- The upstream Pixal3D UI is a custom official HTML app, not the stock Gradio
  interface. It is served by the Gradio server and uses Gradio API endpoints.
- Manager should expose it as `Official Ui`.
- Manager should expose the NymphsCore custom app as `Nymphs Ui`.
- Both actions start the same local server on port 8097; only the opened path
  differs:
  - `Official Ui` -> `/official`
  - `Nymphs Ui` -> `/nymph`

## 2026-05-21 Update: Utils3d Dependency And Stale UI Fixes

Latest behavior state:

- Pixal3D module: `0.1.45`
- Registry: `registry_version` 65
- Pixal3D commit: `3146bc14343ea559c44db552f88f0a3950b6581f`
- Manifest hash:
  `e1243d74b15cd943f33a5b616b6e14af5c13002ea68cb1ce856098c433f780d9`

Failure that triggered this update:

- A Nymphs Ui generation in the test WSL distro reached the expensive Pixal3D
  sampling stages, including texture sampling, then failed during preview/render
  projection.
- The concrete crash was:
  `AttributeError: module 'utils3d.torch' has no attribute 'intrinsics_from_fov_xy'`.
- This was not a NATTEN/FlashAttention failure and not a hidden preprocessing
  handoff failure. The dependency stack had the wrong `utils3d` API for Pixal3D.
- After the venv was repaired, a still-running Gradio process continued failing
  with the same traceback because it had already imported the old `utils3d`
  module. Fresh Python in the test WSL could call
  `utils3d.torch.intrinsics_from_fov_xy`; the live UI process could not.

Correct dependency rule:

- Install Pixal3D's official README wheel:
  `https://github.com/LDYang694/Storages/releases/download/20260430/utils3d-0.0.2-py3-none-any.whl`.
- After installing it, create `utils3d.pt` and `utils3d.np` alias files so MoGe
  auto-camera imports still work.
- Do not install `EasternJournalist/utils3d@3fab839f0be9931dac7c8488eb0e1600c236e183`
  for Pixal3D. That newer commit has the MoGe-style import shape after alias
  repair, but it drops `utils3d.torch.intrinsics_from_fov_xy`, which Pixal3D and
  TRELLIS.2 render/projection code still call.

Installer/update behavior after `0.1.45`:

- `install_pixal3d.sh` installs the official Pixal3D `utils3d` wheel and verifies
  `utils3d.torch.intrinsics_from_fov_xy`.
- `pixal3d_update.sh` stops the Pixal3D UI before syncing files or repairing
  Python dependencies so Gradio reloads changed module code and fixed imports on
  next launch.
- `pixal3d_update.sh` checks the installed shared venv and repairs only
  `utils3d` if the wrong API is present.
- This update path should not rebuild FlashAttention or NATTEN.
- Smoke/runtime validation now imports `utils3d.torch`, `utils3d.pt`, and
  `utils3d.np`, and fails fast if `intrinsics_from_fov_xy` is missing.
- `pixal3d_gradio_is_running` checks both the pid file and the local Gradio URL
  so a stale/missing pid file does not hide a running UI on port 8097.

Test/dev WSL reminder:

- User-facing Manager tests run in the `NymphsCore` WSL distro, not the dev WSL.
- From dev WSL, inspect test WSL with:

```bash
WSL_INTEROP=/run/WSL/1_interop /mnt/c/WINDOWS/system32/wsl.exe -d NymphsCore --cd /home/nymph -- bash -lc '...'
```

Current Nymphs Ui flow:

- `Nymphs Ui` opens `/nymph`; `Official Ui` opens `/official`.
- Warmup starts automatically when the UI opens.
- The source image can be selected before warmup. When `Prepare source image`
  is enabled, preprocessing is manual via `Prepare Source` after warmup is
  ready so it does not secretly become the warmup path or overwrite warmup
  progress.
- After `Prepare Source`, the prepared image replaces the original inside the
  existing source pane. No separate source window is opened.
- Turning `Prepare source image` off sends the original image to generation.
- `Use GPU for RMBG` belongs to the preprocess stage.
- Warmup has its own top progress strip directly under the Pixal3D status bar.
- Source prep, generation, and GLB export share the separate progress strip
  underneath the preview.
- The warmed state text is intentionally short: `Warmed`.
- Runtime-memory settings are process-bound. If Low VRAM, Texture NAF, or a
  runtime preset changes after warmup, pressing `Warm Up` restarts/reconnects
  the Pixal3D backend in the background, then warms the new settings. `Clear GPU
  Memory` performs the same clean backend reset manually so the user can change
  settings before the next warmup. Do not implement in-process heavy reloads for
  these controls in the Blender addon; copy this one-button restart/reconnect
  contract instead.

## 2026-05-21 Update: Nymphs Ui Startup Chrome Cleanup

Latest behavior state:

- Pixal3D module: `0.1.74`
- The Manager module page already supplies the Pixal3D title, so the Nymphs Ui
  no longer renders its own large sidebar title/subtitle block.
- The inner result-pane `Result` label was removed because the top result/action
  strip already identifies the workspace state.
- Background/manual model warmup no longer writes into the main result-strip
  progress. As of `0.1.62`, warmup starts automatically on UI open and uses a
  full dedicated top warmup strip with its own bar.
- The main result-strip progress is reserved for source prep, generation, and
  GLB export so delayed preload stages such as `Loading MoGe camera model` do
  not flash over `Image ready`.
- Nymphs Ui scrollbars use thin teal thumbs with transparent tracks, matching
  the rest of the app instead of the wide native gray scrollbar.
- Weight/profile dropdowns now use explicit technical labels instead of vague
  hardware-vibe names. Examples: `1024 low-VRAM / 12 steps`,
  `1536 full-VRAM / 16 steps`, and `GGUF Q5_K_M experimental`.
- The failed boxed `0.1.66` shell was replaced in `v0.1.67`. The last usable
  pre-restyle UI is backed up at
  `docs/backups/nymph_pixal3d_legacy_0.1.63.html`. The live shell now uses a
  compact source area, inline Manager-style commands, visible core runtime
  controls, and collapsed advanced parameters.
- `v0.1.68` keeps the Pixal control rail narrower and restores the right-side
  result pane height.
- `v0.1.69` locks the Pixal control rail at `400px` instead of scaling it with
  viewport width.
- `v0.1.70` narrows the locked rail to `360px`, removes button-adjacent
  separator lines, and squares the main command buttons.
- `v0.1.71` restores horizontal command buttons and makes the source preview
  square. The source/run command buttons are thin fitted strips, not square
  tiles.
- `v0.1.72` keeps the square source preview but forces the original image to
  render contained inside it, so transparent PNGs and tall sources are not
  clipped. Prep now stores the preprocessed file internally without replacing
  the visible source preview, shortens the run labels to `Generate` and
  `Export`, and fixes the Nymphs custom API `FileData` path handling used by
  prep/generation.
- `v0.1.73` makes `Generate` continue from preview-frame generation into GLB
  export and loads the output in the embedded `model-viewer`, closer to the
  official `gr.Model3D` experience. The preview filmstrip remains underneath as
  a secondary inspection aid. Progress completion now writes explicit final
  states instead of leaving the UI on stale `Starting`, and the viewer asks
  `model-viewer` to reframe after load/resize so the result view survives
  window resizing.
- `v0.1.74` removes the preview-frame render/save step and the filmstrip from
  the Nymphs UI path. `Generate` now samples the 3D latent model, packs the
  model state, exports the GLB, and gives the full result pane to the embedded
  interactive `model-viewer`.
- The main generation progress strip moved below the preview; the topbar area
  now contains status/runtime plus the separate warmup strip.
- `nvdiffrec_render.light` is a required shared TRELLIS.2/Pixal3D runtime import.
  Both Pixal3D and TRELLIS module install/update scripts should validate and
  repair it in `$HOME/TRELLIS.2/.venv`.
- Do not downgrade to the older upstream README CUDA/Torch path while fixing
  this. The Nymph module remains validated on CUDA 13.0 with
  `torch==2.11.0+cu130`; the `nvdiffrec` source branch is used because TRELLIS
  renderers import `nvdiffrec_render`, not because the whole runtime should
  follow the older official dependency profile.

## 2026-05-21 End-Of-Session Pickup

Superseded published state:

- Pixal3D module version: `0.1.74`
- Pixal3D commit: `71dfac3` (`Remove Pixal3D preview frame path`)
- Registry commit: `b92f45c` (`Update Pixal3D registry to 0.1.74`)
- Registry version: `92`
- Registry Pixal3D manifest hash:
  `50232e8285621789f0d02334282419b971741c9e81a3ad792dbaf2bb3e8b4954`

What changed in the final published patch:

- `Generate Preview` is now `Generate`; `Export GLB` is now `Export`.
- The source preview/drop area remains square, but the original selected image
  is rendered with contain behavior inside it so the full image is visible.
- The visible source preview no longer swaps to Pixal3D's preprocessed output;
  prep output is stored internally for generation only.
- `preprocess()` and `generate_3d()` use `_file_path(image)` instead of
  `image["path"]`, fixing the Nymphs custom API error:
  `'FileData' object is not subscriptable`.
- The left Pixal work rail remains locked at `360px` and command buttons remain
  thin horizontal strips, not square tiles.
- `Generate` no longer renders or saves 2D preview frames in the Nymphs UI path.
  It goes straight from latent model generation to GLB export.
- The right result area is now dedicated to the interactive embedded
  `model-viewer`; the old filmstrip is removed.
- Progress final states are explicit, so completed work should not remain stuck
  on `Starting`/queued text.

First tests for the next session:

1. In the test WSL/Manager path, update Pixal3D to `0.1.74`.
2. Open the Nymphs UI and confirm the update came through the registry path, not
   a manual file sync.
3. Drop the transparent character PNG again and confirm the whole image is
   visible inside the square preview.
4. Let warmup finish, run `Prepare Source`, and confirm prep no longer fails
   with `FileData`.
5. Click `Generate` and confirm it does not render a preview-frame filmstrip.
6. Confirm the GLB appears in the full-size embedded model viewer and survives
   window resizing.

## 2026-05-21 Pixal3D 0.1.76 Pickup

Published state:

- Pixal3D module version: `0.1.76`
- Pixal3D commit: `0c40bc2` (`Make Pixal3D warmup restart-safe`)
- Registry commit: `67ef202` (`Publish Pixal3D 0.1.76`)
- Registry version: `95`
- Registry Pixal3D manifest hash:
  `45800b67a03b0903fb8bd64ed9e989efc6a69fb7cd1f1ad95e1e6b7ef62a5755`

What changed:

- Generation startup progress now starts before the runtime lock and mirrors
  expensive model-load stages into the existing progress strip, so the UI no
  longer sits on vague `Queued` text during slow startup.
- The warmup ready state now shows `Warmed`.
- Selecting/touching the same source image no longer clears the current GLB
  preview. A real different source file still resets generation state.
- `Warm Up` detects changed runtime-memory settings and performs a backend
  restart/reconnect before warming with those settings. The visible UI stays
  open and polls `/health` until the replacement backend is ready.
- `Clear GPU Memory` restarts/reconnects the backend as a manual clean reset,
  clears the warmed runtime key, and lets the user change runtime settings
  safely before the next warmup.
- Backend `/health`, `/server_info`, and `/api/restart_runtime` were added to
  support the restart/reconnect handshake from the already-loaded WebView page.

Test next through Manager:

1. Update Pixal3D to `0.1.76` from the registry path.
2. Open the Nymphs UI and confirm warmup reaches `Warmed`.
3. Prepare a source, generate, and confirm GLB export loads in the existing
   model viewer.
4. Touch/select the same source image and confirm the GLB preview remains.
5. Change Low VRAM or Texture NAF after warmup, then press `Warm Up`; the UI
   should show restart/reconnect progress, stay open, and warm the new settings.
6. Press `Clear GPU Memory`, change a runtime-memory setting, then press
   `Warm Up`; this should also warm from a clean backend process.

Workflow reminder for future agents:

- The user tests as an end user in a separate NymphsCore WSL/test install.
- Do not manually sync files into the test install unless explicitly requested.
- For publishable module changes: patch source, bump `nymph.json`, push Pixal3D,
  update the registry manifest version/hash, bump registry version, push
  registry, then let the user update through Manager.
- Inspecting/log tailing is fine. Major design or behavior changes must be
  discussed first and agreed before editing.

## 2026-05-22 Pixal3D 0.1.77 Pickup

Source changes prepared for publish:

- Pixal3D module version: `0.1.77`
- UI layout: `Open GLB` and `Clear GPU Memory` moved from the Status section
  into the top command strip with `Warm Up`, `Generate`, and `Export`.
- `Clear GPU Memory` remains the current `0.1.76` clean reset path: it restarts
  and reconnects the backend, then leaves the model cold until the user presses
  `Warm Up`.
- Closing/unloading the Nymphs UI now sends `/api/stop_runtime` by
  `sendBeacon`/keepalive fetch. The backend endpoint launches
  `scripts/pixal3d_stop.sh`, so both the Pixal3D API backend and the Nymphs UI
  backend are stopped.
- `Use GPU for RMBG` defaults on in both the server config and the HTML fallback
  checkbox state.

Test next through Manager after publish:

1. Update Pixal3D to `0.1.77` from the registry path.
2. Open the Nymphs UI and confirm the five top commands are arranged neatly.
3. Confirm `Use GPU for RMBG` is checked by default.
4. Press `Clear GPU Memory` and confirm it still performs the clean reset flow,
   then leaves warmup required.
5. Close the Pixal3D UI/Manager app and confirm Pixal3D API/UI processes are no
   longer running.

## 2026-05-22 Pixal3D 0.1.78 Pickup

Local source state, pending publish at the time of this note:

- Pixal3D module version: `0.1.78`
- The command area under source prep is split into two visual groups:
  `Warm Up`, `Generate`, and `Export` share the primary run row; `Open GLB` and
  `Clear GPU Memory` sit together as the lower-priority utility row.
- No backend behavior changed from `0.1.77`.

Test next through Manager after publish:

1. Update Pixal3D to `0.1.78` from the registry path.
2. Open the Nymphs UI and confirm the source, run, and utility command groups
   read as distinct, tidy rows in the 360px rail.

## 2026-05-22 Pixal3D 0.1.79 Pickup

Local source state, pending publish at the time of this note:

- Pixal3D module version: `0.1.79`
- `Use GPU for RMBG` is explicitly checked after `/app_config` loads instead of
  trusting a stale `PIXAL3D_REMBG_KEEP_GPU=0` value from a previous process.
- The backend preprocess function also defaults `rembg_keep_gpu=True` if called
  without an explicit UI value.
- The source/run/utility command rows use aligned full-width rows, single-line
  labels, and the ready warmup button text now says `Warmed`.

Test next through Manager after publish:

1. Update Pixal3D to `0.1.79` from the registry path.
2. Open the Nymphs UI and confirm `Use GPU for RMBG` is checked by default
   before touching any controls.
3. Confirm the command rows are aligned, single-line, and visually separated
   from Runtime.

## 2026-05-22 Pixal3D 0.1.80 Pickup

Local source state, pending publish at the time of this note:

- Pixal3D module version: `0.1.80`
- Added `entrypoints.kill`, mapped to `scripts/pixal3d_stop.sh`.
- Added a Manager action labeled `Kill`, using the `kill` entrypoint.
- Purpose: give users an always-present out-of-process kill switch when the
  Pixal3D UI/API is blocked during export and cannot answer `/health` or other
  web requests.

Test next through Manager after publish:

1. Update Pixal3D to `0.1.80` from the registry path.
2. Confirm `// Kill` appears in the Manager action strip even before a run.
3. During a stuck export, press `// Kill` and confirm Pixal3D API/UI processes
   are stopped.

## 2026-05-22 Pixal3D 0.1.81 Pickup

Local source state, pending publish at the time of this note:

- Pixal3D module version: `0.1.81`
- The Pixal3D UI command block now has compact source, run, and utility rows.
- The visible `Kill` switch is inside the Pixal3D UI, beside `Open GLB` and
  `Clear GPU`.
- The installed `kill` entrypoint remains in `nymph.json`, but visible outer
  `Kill` and `Stop` manager action buttons were removed from Pixal3D.
- `ui.manager_ui.stop_action` now points at `kill`, so closing the embedded UI
  runs the full Pixal3D stop script.

Test next through Manager after publish:

1. Update Pixal3D to `0.1.81` from the registry path.
2. Open the Pixal3D UI and confirm the button rows are compact and aligned:
   `Prepare/Clear`, `Warm/Generate/Export`, `Open GLB/Clear GPU/Kill`.
3. Start an export and press the in-UI `Kill`; confirm the backend stops even
   if the API is busy.
4. Reopen Pixal3D, then close the embedded UI; confirm Pixal3D backend
   processes are stopped.

## 2026-05-22 Pixal3D 0.1.82 Pickup

Local source state, pending publish at the time of this note:

- Pixal3D module version: `0.1.82`
- Fixed stale UI state when `Kill` is pressed during warmup.
- `Kill` immediately resets `busy`, `warmupActive`, `modelReady`, warmup timers,
  and progress timers, then shows a consistent `Killed` state.
- Pressing `Warm` after `Kill` starts Pixal3D through the module action bridge,
  waits for the backend to answer, then runs warmup.

Test next through Manager after publish:

1. Update Pixal3D to `0.1.82` from the registry path.
2. Open Pixal3D, start Warm, then press in-UI `Kill`.
3. Confirm the warmup strip changes to `Killed` and the `Warm` button is
   enabled.
4. Press `Warm` again and confirm Pixal3D restarts and warms normally.

## 2026-05-22 Pixal3D 0.1.83 Pickup

Local source state, pending publish at the time of this note:

- Pixal3D module version: `0.1.83`
- Removes the confusing killed-state copy that told users to reopen/open the UI.
- After `Kill`, the same visible `Warm` button is the recovery path: it starts
  Pixal3D again through the module action bridge, reconnects, then warms.

Test next through Manager after publish:

1. Update Pixal3D to `0.1.83` from the registry path.
2. Start Warm, press in-UI `Kill`, confirm the UI says `Killed`.
3. Press `Warm` again in the same UI. It should start Pixal3D, reconnect, and
   warm without requiring Open UI/reopen.

## 2026-05-22 Pixal3D 0.1.84 Pickup

Local source state, pending publish at the time of this note:

- Pixal3D module version: `0.1.84`
- `preprocess`, `generate_3d`, `extract_glb_api`, and `free_pipeline_api` are
  dispatched through worker threads from the Nymph UI FastAPI endpoints.
- This keeps the event loop free to serve `/progress` while the backend is
  loading models, estimating camera, sampling, decoding, remeshing, and
  exporting GLB.

Test next through Manager after publish:

1. Update Pixal3D to `0.1.84` from the registry path.
2. Start generation and confirm the status strip advances beyond `Queued`.
3. During export, confirm it shows backend stages such as decoding/building
   mesh/exporting rather than staying on a generic wait state.

## 2026-05-22 Pixal3D 0.1.85 Pickup

Local source state, pending publish at the time of this note:

- Pixal3D module version: `0.1.85`
- Keeps the `0.1.84` worker-thread progress responsiveness.
- Adds CUDA memory breadcrumbs before/after generation and GLB export.
- Explicitly drops large per-run references after generation and export:
  preprocessed image, generated mesh list, shape/texture latents, decoded mesh,
  GLB scene, and state-file arrays.
- Calls `gc.collect()`, `torch.cuda.empty_cache()`, and `torch.cuda.ipc_collect()`
  after MoGe camera estimation, generation cleanup, and GLB export cleanup.

Test next through Manager after publish:

1. Update Pixal3D to `0.1.85` from the registry path.
2. Generate/export once, then generate/export a second time without restarting.
3. Check logs for `[CUDA] ... allocated/reserved/max_allocated` breadcrumbs.
4. If second-run OOM remains, compare the cleanup logs; next likely mitigation
   is a controlled backend restart after completed GLB export.
