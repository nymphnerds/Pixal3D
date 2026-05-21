# Pixal3D UI From-Scratch Brief

Created: 2026-05-21

This document exists because the recent Pixal3D Nymph UI work did not follow the
intended meaning of "from scratch". It restyled and rearranged old UI pieces
instead of designing a new Pixal3D workflow surface.

## Meaning Of From Scratch

For this task, "from scratch" means:

- Build a new user-facing `nymph_pixal3d.html` layout from a blank design.
- Use the current backend API and required DOM IDs only as wiring constraints.
- Do not preserve the old source/action/parameter layout.
- Do not wrap the old controls in new boxes.
- Do not keep the full parameter wall as the primary experience.
- Do not rely on small CSS tweaks to make the old UI acceptable.

The old UI can be referenced only to understand required data fields and API
calls.

## Visual Target

The UI must feel like NymphsCore Manager and the NymphsCore website:

- Dark, open, editorial/tool-like layout.
- Minimal framed boxes.
- No card-heavy dashboard look.
- No boxed panels around every group of controls.
- `//` command language where it already fits the app.
- Teal as the main action colour.
- Lime as a sharp status/accent colour.
- Amber only for selected/attention states.
- Gradients are allowed, but only when subtle and purposeful.
- No rainbow-looking controls or broad decorative colour bands.

## Workflow Target

The UI should be built around the actual Pixal3D workflow:

1. Load or drop a source image.
2. Warm up the model.
3. Prepare the source image.
4. Generate preview frames.
5. Export or open the GLB.

Warm-up must have its own top progress area.

Source prep, generation, and export must use a separate progress area.

Generate must not be available until the required model/source state is ready.

## Layout Direction

The default app window should not be dominated by the source image drop zone or
a huge parameter form.

Required direction:

- Left side: source image, core actions, and essential runtime choices.
- Right side: generated preview / GLB result gets priority.
- Advanced parameters should be visually secondary, collapsed, tucked lower, or
grouped in a way that does not dominate the first screen.
- The source preview must show the whole selected image without cropping.
- The preview/result area must have enough space to inspect output.
- Buttons should be compact and command-like, not stretched slabs.

## Current Failure To Avoid

Do not repeat these mistakes:

- Huge source drop area taking most of the page.
- Reusing the same old two-column parameter wall.
- Creating big boxed command panels.
- Making the UI look like a generic web form.
- Treating "from scratch" as a CSS-only restyle.
- Publishing visual changes before the layout has been discussed.

## Implementation Rule

Before the next Pixal3D UI implementation:

1. Inspect the real NymphsCore Manager XAML and NymphsCore website CSS.
2. Propose a short layout plan to the user.
3. Wait for agreement.
4. Then implement the new UI.

The current working backend/script logic may be reused, but the visible
HTML/CSS layout should be rebuilt as a new design.

## Session Requests And Requirements

This section captures the requests made during the 2026-05-21 Pixal3D session.
Treat these as requirements for the next pass unless the user explicitly changes
direction.

### Collaboration Workflow

- Inspecting logs, code, docs, and repo state is always okay.
- Do not make major implementation changes before explaining the plan and
  getting agreement.
- When the user is asking a question or discussing an option, do not treat that
  as approval to implement.
- The user tests from a separate NymphsCore WSL/test install. Do not manually
  sync test files around the registry/update path.
- Normal release flow matters: change source, bump module version, push module,
  update registry hash/version, push registry, then the user tests through
  Manager update.
- If Manager itself changes, build and publish Manager through its normal build
  output. Do not create extra publish/build folders.
- Keep docs current, but do not bury important current state inside old notes.
- Keep one latest/canonical handoff source to avoid confusion.

### Registry And Update Path

- The module update path must be tested as an end user through Manager.
- Registry must point to the exact raw `nymph.json` hash for the pushed module
  version.
- Do not manually fake or bypass the registry update during testing.
- When publishing Pixal3D, update `nymphs-registry` with the new
  `manifest_version`, `manifest_hash`, and bumped `registry_version`.
- Wait for raw GitHub propagation when needed so the Manager does not see stale
  metadata.

### Runtime And Install Constraints

- Pixal3D and TRELLIS.2 share `$HOME/TRELLIS.2/.venv`.
- TRELLIS.2 must remain functional after Pixal3D install/repair/uninstall.
- Pixal3D install and TRELLIS.2 install scripts should mirror each other where
  they manage shared runtime dependencies.
- Do not cap FlashAttention build jobs/threads outside the explicit install UI
  options.
- Do not silently fall back from FlashAttention for Pixal3D; speed is paramount.
- Pixal3D has been validated in this environment on the newer CUDA 13 path even
  if official docs mention older CUDA.
- `nvdiffrec_render` / `nvdiffrec_render.light` must be installed and repaired
  correctly in the shared runtime.
- Pixal3D uninstall must not remove the shared TRELLIS.2 runtime or cached
  FlashAttention build used by TRELLIS.2.

### Pixal3D App Surface

- Only the NymphsCore custom UI matters now.
- Do not expose or prioritize the official Pixal3D UI.
- The official app may be used as behavioral reference only.
- The Nymphs UI should be better than the official app, not a small wrapper
  around it.

### Warm-Up And Progress

- Warm-up should start automatically when the UI opens.
- A manual `Warm Up` button is still required because settings changes can make
  the warmed model stale.
- Warm-up must have its own separate top progress bar.
- Warm-up progress must not reuse or interfere with the main generation progress
  bar.
- Generate must not be possible until warm-up/model state is ready.
- Runtime-affecting changes should mark warm-up as required again.
- Warm-up state should be clear to a non-technical user.

### Source Prep

- Source prep should be a manual step, not something that fires invisibly.
- Prep should not start before the model is ready.
- Prep needs visible progress/status.
- Prep failure must not trap the UI.
- After prep failure, the user must be able to retry prep or clear the source.
- `Prepare source image` must remain understandable and tied to what the system
  will do.
- `Use GPU for RMBG` belongs to source prep behavior, not warm-up.

### Preview And Image Handling

- The source preview must show the whole selected image.
- Source image must not be cropped, zoomed, or clipped.
- The source preview should not take the whole page.
- The preview/result side should have enough space to inspect generated output.
- The default app window should feel balanced, not dominated by either a giant
  source upload zone or a giant parameter form.
- Right side/result area can resize; left control/work area should feel stable.

### Controls And Labels

- Buttons under source and run actions should be compact and app-like.
- Buttons should use the NymphsCore `//` command language where appropriate.
- Do not make stretched slab buttons.
- Do not wrap the same controls in big boxes and call it a redesign.
- Do not use vague names like `Free Pipeline`; use clear user-facing terms such
  as `Clear GPU Memory`.
- Runtime/profile labels should be technical and honest, not vague hardware
  names.
- Avoid shortening labels so much that meaning is lost.
- Weight/profile dropdown text must fit without clipping.
- Low VRAM checkbox must reflect the selected preset; if all presets are low
  VRAM, that should be clear and not misleading.

### Parameters

- Do not keep the old full parameter wall as the primary first-screen
  experience.
- Important controls should be visible first.
- Advanced parameters should be visually secondary, collapsed, lower, or grouped
  so they do not dominate.
- The next design should decide which controls are essential for Pixal3D's
  target workflow before rendering all fields.

### Visual Style

- Match the NymphsCore Manager and website visual language.
- The app/site does not use lots of boxes; do not make the Pixal UI box-heavy.
- Use dark open surfaces with restrained structure.
- Use teal, lime, and amber wisely.
- Gradients can work, but must be subtle and purposeful.
- Do not create a rainbow-looking control.
- Avoid generic web-form styling.
- Avoid card-heavy dashboard styling.
- Avoid giant bordered panels around every control group.
- Keep the first screen clean, useful, and polished.

### Rejected Approaches

- Re-skinning the old layout.
- Wrapping the old layout in command panels.
- Keeping the full old parameter grid as the main UI.
- Giant source drop zone.
- Big boxed command sections.
- Stretched button slabs.
- Any change that looks effectively the same to the user.
- Publishing another visual attempt before the layout direction is discussed.

### Recovery Note

If the live Pixal3D UI is bad for testing, the safest recovery is to roll the
registry back to the last usable Pixal3D module version, then restart the UI
design process from this brief.

## 2026-05-21 Reset Action

- The last usable pre-restyle UI was recovered from Pixal3D commit `2818c7c`
  and saved as `docs/backups/nymph_pixal3d_legacy_0.1.63.html`.
- `nymph_pixal3d.html` was then replaced with a new shell instead of reusing the
  failed boxed `0.1.66` layout.
- The new shell keeps the existing backend/script IDs, but changes the visible
  structure:
  - compact source area, not a full-page upload zone
  - source/run commands as inline Manager-style buttons, not boxed command
    panels
  - core runtime controls visible first
  - advanced parameters collapsed behind `Advanced parameters`
  - right-side generated preview remains the main inspection surface
- `v0.1.68` narrows the locked Pixal work rail, tightens command button sizing,
  and restores the result/GLB preview pane to fill its vertical grid area.
