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

The recommended next fix is automatic process isolation/recycle while keeping
FlashAttention enabled: after a successful export, treat the CUDA worker as
spent, start a fresh backend process, reconnect, and prewarm it in the
background so the next Generate does not run inside the poisoned process.

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

## Recommended Next Patch

Implement automatic single-use CUDA runtime behavior for the Manager path while
keeping FlashAttention enabled.

Minimum viable approach:

- After successful GLB export, mark the current CUDA runtime as stale/spent.
- Start a backend restart/reconnect cycle automatically, using the existing
  `/api/restart_runtime` machinery.
- After reconnect, warm the fresh backend automatically in the background.
- Preserve the selected source and prepared source state when possible.
- If the user presses Generate while recycle/prewarm is still running, wait for
  it instead of allowing a second generation in the old process.
- Fix duplicate preprocess calls by guarding `prepareSource()` when
  `preprocessing` is already true.

User-facing goal:

- Do not ask the user to manually kill/reopen/warm.
- Keep the UI honest with status such as "Preparing next run".
- Hide most of the restart/warm cost by doing it immediately after export while
  the user is inspecting the result.

Preferred long-term architecture:

- Keep the UI/FastAPI control server alive.
- Run the heavy Pixal3D generate/export operation inside a one-shot CUDA worker
  subprocess.
- Return the final GLB to the stable server, then terminate the worker.
- Optionally prewarm the next worker in the background.

The one-shot worker design is cleaner than restarting the whole UI backend, but
it is a larger change. The restart/reconnect/prewarm path is the smaller next
step because the module already has `/api/restart_runtime`, `waitForBackend()`,
and warmup polling.

## What Not To Do

- Do not disable FlashAttention as the primary fix.
- Do not lower settings and call the issue solved.
- Do not rely on `torch.cuda.empty_cache()` alone.
- Do not manually patch the installed Manager or installed module files to test.
- Do not update registry metadata for local-only experiments.
- Do not advertise a module version before the module commit and raw manifest
  are pushed and verified.

## Next Testing Path

After the next patch is implemented:

1. Bump Pixal3D module version.
2. Push `nymphnerds/Pixal3D`.
3. Verify raw `nymph.json` from GitHub.
4. Update `nymphs-registry/nymphs.json` only after the raw module manifest is
   public and correct.
5. Push registry.
6. In Manager, update Pixal3D through the normal registry path.
7. Test:
   - First generation/export.
   - Let automatic recycle/prewarm complete.
   - Second generation/export without manually killing Pixal3D.
   - Try pressing Generate during the recycle window and verify it waits or
     gives a clear status rather than running in the stale process.

