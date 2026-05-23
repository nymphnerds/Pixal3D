# Pixal3D Second-Run OOM / WSL Crash Findings

Date: 2026-05-23

Scope: Pixal3D module source repo only. Testing referenced here was performed
through the normal Manager update/install path in the managed `NymphsCore` WSL
environment. No installed module files, markers, manifests, cached manifests, or
runtime state were hand-edited.

## Executive Summary

Pixal3D can complete a first Manager generation/export, then crash the next run
hard enough to take down WSL without a Python traceback. The strongest current
conclusion is that the crash is not ordinary Python object retention and not
primarily the embedded model viewer. It is repeat use of the same long-lived
Python/CUDA process after one complete Pixal3D run.

The official local Pixal3D app has the same long-lived process architecture. It
does not isolate generations in a fresh CUDA worker process and does not restart
the runtime after export. It uses FlashAttention by default, low-VRAM CPU/GPU
stage movement, and `torch.cuda.empty_cache()`, but those are still inside the
same Python process.

Implemented follow-up: Pixal3D `0.1.102` now uses isolated single-use CUDA
workers for the Manager custom UI while keeping FlashAttention enabled. The
Manager web/control process stays alive, source prep runs in a worker process,
Generate consumes one prewarmed worker for combined generation/export, and the
server starts another worker in the background for the next run.

## Observed Symptom

- First low-settings Manager generation can complete.
- GLB export can complete and load in the embedded Manager viewer.
- A second generation in the same Manager session can crash both the dev/test
  WSL environment rather than raising a recoverable Python OOM.
- Killing Pixal3D completely and warming again allows another first run.
- The user saw the issue solely from the Manager custom UI, not only Blender.

## Environment Notes

- Managed test distro: `NymphsCore`.
- Module version under test after normal Manager update: `0.1.101`.
- GPU reported after crash/restart inspection: RTX 4080 SUPER, 16376 MiB total.
- System RAM after crash/restart inspection: 23 GiB total, 16 GiB swap.
- CUDA path: user reports CUDA 13. Pixal3D works on this setup, but repeat runs
  are unstable.
- FlashAttention must remain enabled for this path. Do not propose SDPA as the
  normal solution for this issue.

## Upstream Comparison

Upstream checked on 2026-05-23:

- Remote: `TencentARC/Pixal3D`
- Ref: `upstream/master`
- Commit: `5098ba1f8c528f2c3e71a3ae88545e2826740d2b`
- Fork status at time of check: local/origin had no missing upstream commits.

Official app behavior:

- `app.py` sets `ATTN_BACKEND` to `flash_attn` by default.
- Low-VRAM mode keeps several models on CPU and moves them to GPU on demand.
- Low-VRAM cleanup calls `torch.cuda.empty_cache()`.
- `generate_3d` runs `pipeline.run(... return_latent=True)` and still uses the
  decoded mesh output for preview rendering before GLB export.
- `extract_glb_api` decodes the latent state again and runs `to_glb`.
- The app pre-initializes models before launch and keeps the same process alive.
- There is no backend restart after export.
- There is no one-shot worker process per generation.
- There is no CUDA process recycle between generation attempts.

Official UI behavior:

- `index.html` includes a Decimation slider mapped to `decimation_target` faces.
- The official UI destroys/recreates `<model-viewer>` before generation,
  extraction, and clear. Its comment says this fully purges the old WebGL mesh.
- The viewer reset is useful browser/WebGL cleanup, but it is not CUDA process
  isolation and did not stop the Manager second-run crash after we copied it.

Conclusion: this looks like an upstream robustness issue in the official local
app architecture, exposed severely by WSL/CUDA/native extension behavior on this
machine. The hosted demo may be protected by container scheduling or per-request
GPU lifecycle, but the official local app does not contain that protection.

## Nymph Patches Already Published

### Pixal3D 0.1.100

Pushed to `nymphnerds/Pixal3D`:

- Commit: `da52403`
- Registry: `registry_version 128`
- Registry commit: `4f07967`
- Raw manifest hash:
  `af67f6fbd263d4f8e52522f89eddbceb792e40ce74428bada20080feb370a341`

Changes:

- Added optional `PIXAL3D_AUTO_FREE_AFTER_GENERATION` and
  `PIXAL3D_AUTO_FREE_AFTER_EXPORT`, both defaulting false.
- Added sparse latent cache clearing and mesh tensor cleanup.
- Added CUDA synchronization before cleanup and stronger memory logging.
- Added process-level `nvidia-smi --query-compute-apps=pid,used_memory`
  breadcrumbs.
- Changed Manager generation to call
  `pipeline.run(... return_latent=True, decode_output=False)`.
- Added `decode_output` support to
  `pixal3d/pipelines/pixal3d_image_to_3d.py`.
- Changed packed state handling to detach CPU copies and clear sparse caches.

Purpose:

- Reduce repeated decode/render memory pressure in the Manager path.
- Keep the Manager path lighter than the official UI generation flow.

Result:

- Did not eliminate the second-run hard crash.

### Pixal3D 0.1.101

Pushed to `nymphnerds/Pixal3D`:

- Commit: `0921a56`
- Registry: `registry_version 129`
- Registry commit: `07468fb`
- Raw manifest hash:
  `94d9d6ff5479cac4f49c3e323d77726e2d80226025fe801d4de8a5ba0952c270`

Changes:

- Copied the official UI's important model-viewer lifecycle idea into the
  Manager UI.
- `renderModel(url)` now destroys/recreates `<model-viewer>` before assigning a
  new GLB.
- `setResultEmpty(message)` resets the viewer before generation, source
  replacement, clear, and empty states.

Purpose:

- Avoid retaining stale GLB/WebGL memory across runs.

Result:

- The WebGL viewer retention bug was real and worth fixing.
- It did not eliminate the second-run hard crash.

## Latest Manager/Test Evidence

After updating through Manager to `0.1.101`, the Manager log showed:

- `pixal3d: update available 0.1.100 -> 0.1.101`
- Manager update fetched `https://raw.githubusercontent.com/nymphnerds/Pixal3D/master/nymph.json`
- `installed_module_version=0.1.101`
- Later status: `pixal3d: current (0.1.101, remote 0.1.101)`
- Pixal3D opened at `http://127.0.0.1:8097/nymph`

Latest successful first-run output:

- `/home/nymph/NymphsData/outputs/pixal3d/pixal3d_app_1779537934241.glb`
- Size: about 16.7 MB

Latest `pixal3d-gradio.log` after crash showed:

- First generation/export completed.
- After first generation cleanup, PyTorch reported about:
  - allocated: `0.84 GB`
  - reserved: `0.91 GB`
  - max allocated: `7.02 GB`
- After first GLB export cleanup, PyTorch reported about:
  - allocated: `0.84 GB`
  - reserved: `0.91 GB`
  - max allocated: `4.33 GB`
- The GLB was served successfully with HTTP 200.
- Before the second generation, two `/api/preprocess` requests appeared.
- The second generation began and progressed into sparse structure sampling.
- The log stopped without Python traceback, explicit CUDA OOM, or clean FastAPI
  error.

Interpretation:

- Python-level cleanup appears low after the first export.
- The crash is not captured as a Python exception.
- The failing layer is likely native CUDA/driver/extension state during reuse of
  the same process.
- Duplicate preprocess requests are a UI race/state clue and should be fixed,
  but they are not enough by themselves to explain a WSL-wide hard crash.

## Why The Viewer Is Probably Not The Root Cause

The generated GLB was about 16.7 MB. It can expand in browser/WebGL memory, and
the official UI reset confirms stale viewer memory is a real concern. However:

- A model-viewer retention leak should mostly affect the WebView/browser side.
- The second crash still happened after the Manager viewer reset patch.
- The crash happens during the next CUDA-heavy generation stage, with no Python
  traceback.
- The Python backend process disappears rather than reporting a recoverable app
  error.

Conclusion: viewer cleanup should stay, but it is not sufficient.

## Current Root-Cause Hypothesis

The first full Pixal3D run leaves unsafe native CUDA process state behind. This
may involve some combination of:

- PyTorch CUDA allocator state.
- FlashAttention kernels.
- Sparse/flex-gemm CUDA extension state.
- MoGe camera estimation.
- NVDiffRec/rendering or mesh/export related CUDA libraries.
- WSL GPU bridge behavior after a native CUDA fault.

The key problem is repeat generation inside the same Python/CUDA process, not
just peak settings and not just visible allocated VRAM.

## Implemented Patch In 0.1.102

Pixal3D `0.1.102` implements single-use CUDA runtime behavior for the Manager
path while keeping FlashAttention enabled.

Implemented approach:

- `PIXAL3D_WORKER_ISOLATION` defaults on for the Manager backend.
- Warm Up starts a single-use isolated worker process instead of loading the
  model into the web/control process.
- Source preprocessing discards any pending generation worker, preprocesses in
  its own subprocess, then starts the next generation worker in the background.
- Generate calls a new combined `/api/generate_glb` endpoint rather than
  calling `/generate_3d` and `/extract_glb_api` separately from the UI.
- The combined endpoint sends the task to one prewarmed worker. That worker runs
  generation and GLB export, writes the result, and exits.
- After a successful GLB, the stable server starts the next isolated worker in
  the background.
- `prepareSource()` now ignores duplicate clicks while preprocessing is already
  active.

User-facing goal:

- Do not ask the user to manually kill/reopen/warm.
- Keep the UI honest by showing the worker warmup state.
- Avoid running a second generation inside a spent CUDA process.

Validation completed before publishing:

- `python3 -m py_compile app.py inference.py scripts/api_server_pixal3d.py scripts/gradio_pixal3d_module.py pixal3d/pipelines/pixal3d_image_to_3d.py`
- `python3 -m json.tool nymph.json`
- `git diff --check`
- Import sanity check in `/home/nymph/TRELLIS.2/.venv/bin/python` confirmed
  `worker_isolation True` and FlashAttention selected.

Published artifacts:

- Baseline rollback tag:
  `pixal3d-0.1.101-second-run-oom-baseline`
- Pixal3D commit: `361b6d8`
- Pixal3D version: `0.1.102`
- Verified raw manifest hash:
  `eced511cc027fd88ceb8a904bfbba682e9a076e0d39814dad10a99faaeb7cdc5`
- Registry commit: `51ee26e`
- Registry version: `130`

## What Not To Do

- Do not disable FlashAttention as the primary fix.
- Do not lower settings and call the issue solved.
- Do not rely on `torch.cuda.empty_cache()` alone.
- Do not manually patch the installed Manager or installed module files to test.
- Do not update registry metadata for local-only experiments.
- Do not advertise a module version before the module commit and raw manifest
  are pushed and verified.

## Next Testing Path

After Manager sees Pixal3D `0.1.102` through registry `130`:

1. Update Pixal3D through the normal Manager registry path.
2. Open the Manager custom Pixal3D UI.
3. Warm Up and wait for the isolated worker to become ready.
4. Prepare a source image.
5. Wait for the next isolated generation worker to become ready.
6. Generate/export the first GLB.
7. Let the next background worker warm while inspecting the result.
8. Generate/export a second GLB without manually killing Pixal3D.
9. Try pressing Generate during the worker warmup window and verify it waits or
   gives a clear status rather than running in a stale CUDA process.
