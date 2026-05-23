# Pixal3D Second-Run OOM / WSL Crash Findings

Date: 2026-05-23

Scope: Pixal3D module source repo only. Testing referenced here was performed
through the normal Manager update/install path in the managed `NymphsCore` WSL
environment. No installed module files, markers, manifests, cached manifests, or
runtime state were hand-edited.

## Executive Summary

Pixal3D's repeat-run Manager failure is confirmed fixed as of `0.1.108`.

The final confirmed root cause had two layers:

- A repeat-run host-memory/RSS problem could take down WSL before Python raised
  a normal exception.
- After RSS trimming exposed the next failure cleanly, GLB export could fail
  during shape decode because an inferred subdivision mask collapsed the sparse
  tensor to zero coordinates.

The confirmed fixes were:

- `0.1.106`: trim the native CPU heap with `malloc_trim(0)` during cleanup and
  log process RSS. In the confirmed Manager run this reduced RSS from about
  `22.08 GB` to `15.89 GB` after generation cleanup and prevented the old WSL
  hard-crash pattern.
- `0.1.108`: keep one fallback child voxel for each active parent when inferred
  decoder subdivision masks are all false. This prevents shape decode from
  producing an empty sparse tensor and fixed the export crash:
  `IndexError: max(): Expected reduction dim 0 to have non-zero size`.

Current confirmed baseline: Pixal3D `0.1.108`.

Earlier notes in this document about `0.1.102` worker isolation are historical.
That experiment was reverted in `0.1.103` because it caused confusing double
pipeline loads and hangs. It is not the confirmed fix.

Before the fix, Pixal3D could complete a first Manager generation/export, then
crash the next run hard enough to take down WSL without a Python traceback. The
working conclusion at the time was that the crash was not ordinary Python object
retention and not primarily the embedded model viewer. Later evidence narrowed
that to native host-memory pressure plus a sparse decode collapse.

The official local Pixal3D app has the same long-lived process architecture. It
does not isolate generations in a fresh CUDA worker process and does not restart
the runtime after export. It uses FlashAttention by default, low-VRAM CPU/GPU
stage movement, and `torch.cuda.empty_cache()`, but those are still inside the
same Python process.

Historical follow-up: Pixal3D `0.1.102` tried isolated single-use CUDA workers
for the Manager custom UI while keeping FlashAttention enabled. That path was
not kept; it was reverted in `0.1.103`.

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

### Pixal3D 0.1.102

Historical experiment, later reverted in `0.1.103`.

Changes:

- Moved the Manager custom UI onto isolated single-use CUDA workers for source
  prep and combined generation/export.

Result:

- Did not become the final fix.
- Caused confusing double pipeline loads and hangs in the Manager flow.
- Reverted in `0.1.103`, restoring the warmed runtime flow.

### Pixal3D 0.1.106

Changes:

- Added process RSS logging.
- Added `malloc_trim(0)` in cleanup/free paths so native CPU heap pages return
  to WSL instead of staying resident after a run.

Evidence:

- In the confirmed Manager run, after generation cleanup logged:
  `rss=22.08 GB -> 15.89 GB`.
- This stopped the old WSL-wide hard-crash pattern and exposed the next failure
  as a normal Python export traceback.

Result:

- Fixed the host-memory/RSS side of the repeat-run failure.
- Did not by itself fix export for every latent.

### Pixal3D 0.1.108

Changes:

- During inference, decoder subdivision masks now preserve one fallback child
  voxel per active parent when all predicted children are false.

Why:

- The failing export traceback showed `decode_shape_slat` entered sparse
  convolution with an empty coordinate tensor:
  `IndexError: max(): Expected reduction dim 0 to have non-zero size`.
- The empty tensor was caused by an inferred subdivision mask erasing every
  child voxel from an active sparse parent.

Result:

- Confirmed fixed by the user in the Manager path.
- Current stable Pixal3D test baseline is `0.1.108`.

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

## Final Root Cause

The confirmed failure had two parts:

1. The warmed Pixal3D process could remain close to the WSL RAM ceiling after a
   complete generation/export. CUDA memory looked clean, but native CPU heap/RSS
   stayed high enough that the next heavy stage could trip WSL without a Python
   traceback.
2. Once RSS trimming prevented the hard WSL crash, GLB export could fail because
   shape decode let an all-false inferred subdivision mask collapse a sparse
   tensor to zero coordinates. The next sparse convolution then crashed while
   computing `spatial_shape`.

The key lesson: visible PyTorch CUDA allocation was not enough to diagnose this.
The fix needed both native process RSS cleanup and a sparse decoder guard.

## Historical Patch In 0.1.102

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

Status:

- Superseded. Reverted in `0.1.103`.
- The final confirmed fix is `0.1.108`, with the important runtime memory fix
  in `0.1.106`.

## Diagnostic Harness Added After 0.1.102

Source-only diagnostic tooling was added after the `0.1.102` publish to help
pinpoint the exact stage that poisons the long-lived CUDA process:

- Script: `scripts/pixal3d_repeat_diagnostics.py`
- Interpreter: run it with the Pixal3D/TRELLIS shared venv, not system Python:
  `/home/nymph/TRELLIS.2/.venv/bin/python`
- It deliberately runs multiple Pixal3D passes in one Python/CUDA process.
- It logs timestamps, PID, process RSS, PyTorch allocated/reserved/max memory,
  and `nvidia-smi` GPU memory at each stage.
- It can stop after `preprocess`, `camera`, `ss`, `shape-lr`, `upsample`,
  `shape-hr`, `tex`, `pack`, `decode`, or `glb`.
- It has `--cleanup-each-stage` and `--free-models-between-runs` switches to
  compare normal repeat behavior with more aggressive cleanup.

Suggested bisection sequence:

```bash
cd /home/nymph/Pixal3D
/home/nymph/TRELLIS.2/.venv/bin/python scripts/pixal3d_repeat_diagnostics.py --stop-after ss --repeats 2
/home/nymph/TRELLIS.2/.venv/bin/python scripts/pixal3d_repeat_diagnostics.py --stop-after shape-lr --repeats 2
/home/nymph/TRELLIS.2/.venv/bin/python scripts/pixal3d_repeat_diagnostics.py --stop-after shape-hr --repeats 2
/home/nymph/TRELLIS.2/.venv/bin/python scripts/pixal3d_repeat_diagnostics.py --stop-after tex --repeats 2
/home/nymph/TRELLIS.2/.venv/bin/python scripts/pixal3d_repeat_diagnostics.py --stop-after decode --repeats 2
/home/nymph/TRELLIS.2/.venv/bin/python scripts/pixal3d_repeat_diagnostics.py --stop-after glb --repeats 2
```

If WSL crashes, the last complete `[DIAG]` checkpoint in
`~/NymphsData/logs/pixal3d/pixal3d-repeat-diagnostics-*.log` is the current
best clue. This is a dangerous diagnostic path by design; it bypasses the
Manager worker-isolation safety net to reproduce the original failure.

## What Not To Do

- Do not disable FlashAttention as the primary fix.
- Do not lower settings and call the issue solved.
- Do not rely on `torch.cuda.empty_cache()` alone.
- Do not manually patch the installed Manager or installed module files to test.
- Do not update registry metadata for local-only experiments.
- Do not advertise a module version before the module commit and raw manifest
  are pushed and verified.

## Confirmed Testing Path

Confirmed after Manager updated to Pixal3D `0.1.108`:

1. Update Pixal3D through the normal Manager registry path.
2. Open the Manager custom Pixal3D UI.
3. Warm Up.
4. Prepare a source image.
5. Generate/export a GLB.
6. Run again without manually killing Pixal3D.
7. Verify WSL does not crash and export completes.

Result: confirmed fixed by the user. Keep `0.1.108` as the current stable
baseline for repeat-run Manager testing.
