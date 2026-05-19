#!/usr/bin/env python3
"""Local Gradio UI for the Nymph Pixal3D module."""

from __future__ import annotations

import argparse
import os
import tempfile
import time
from pathlib import Path

import gradio as gr


def _bool_env(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _generate(
    image,
    low_vram: bool,
    resolution: int,
    seed: int,
    manual_fov: float,
    texture_size: int,
    decimation_target: int,
    ss_steps: int,
    shape_steps: int,
    tex_steps: int,
):
    if image is None:
        raise gr.Error("Choose an image first.")

    from inference import run_inference

    output_dir = Path(os.environ.get("PIXAL3D_OUTPUT_DIR") or Path.home() / "NymphsData" / "outputs" / "pixal3d")
    output_dir.mkdir(parents=True, exist_ok=True)
    input_path = output_dir / f"gradio_input_{int(time.time() * 1000)}.png"
    output_path = output_dir / f"gradio_pixal3d_{int(time.time() * 1000)}.glb"
    image.save(input_path)

    run_inference(
        image_path=str(input_path),
        output_path=str(output_path),
        seed=int(seed),
        ss_sampling_steps=int(ss_steps),
        shape_slat_sampling_steps=int(shape_steps),
        tex_slat_sampling_steps=int(tex_steps),
        model_path=os.environ.get("PIXAL3D_MODEL_REPO", "TencentARC/Pixal3D"),
        manual_fov=float(manual_fov),
        low_vram=bool(low_vram),
        resolution=int(resolution),
        decimation_target=int(decimation_target),
        texture_size=int(texture_size),
        extension_webp=False,
    )
    return str(output_path), str(output_path)


def build_ui(default_low_vram: bool, default_resolution: int) -> gr.Blocks:
    with gr.Blocks(title="Pixal3D") as demo:
        gr.Markdown("# Pixal3D")
        gr.Markdown("Generate a textured GLB from one image. The model loads when you click Generate.")
        with gr.Row():
            with gr.Column(scale=1):
                image = gr.Image(label="Image", type="pil")
                low_vram = gr.Checkbox(label="Low VRAM", value=default_low_vram)
                resolution = gr.Dropdown(
                    label="Resolution",
                    choices=[1024, 1536],
                    value=default_resolution,
                    allow_custom_value=False,
                )
                seed = gr.Number(label="Seed", value=42, precision=0)
                manual_fov = gr.Number(label="Manual FOV radians (-1 for MoGe)", value=-1.0)
                with gr.Accordion("Advanced", open=False):
                    texture_size = gr.Dropdown(label="Texture Size", choices=[1024, 2048, 4096], value=4096)
                    decimation_target = gr.Number(label="Face Target", value=1000000, precision=0)
                    ss_steps = gr.Slider(label="Structure Steps", minimum=4, maximum=32, value=12, step=1)
                    shape_steps = gr.Slider(label="Shape Steps", minimum=4, maximum=32, value=12, step=1)
                    tex_steps = gr.Slider(label="Texture Steps", minimum=4, maximum=32, value=12, step=1)
                generate = gr.Button("Generate", variant="primary")
            with gr.Column(scale=1):
                model = gr.Model3D(label="Generated GLB")
                output_path = gr.Textbox(label="Output Path", interactive=False)

        generate.click(
            _generate,
            inputs=[
                image,
                low_vram,
                resolution,
                seed,
                manual_fov,
                texture_size,
                decimation_target,
                ss_steps,
                shape_steps,
                tex_steps,
            ],
            outputs=[model, output_path],
        )
    return demo


def main() -> None:
    parser = argparse.ArgumentParser(description="Pixal3D local Gradio UI")
    parser.add_argument("--host", default=os.environ.get("GRADIO_SERVER_NAME", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("GRADIO_SERVER_PORT", "8097")))
    parser.add_argument("--share", action="store_true")
    parser.add_argument("--low-vram", action="store_true", default=_bool_env("PIXAL3D_LOW_VRAM", True))
    parser.add_argument("--no-low-vram", action="store_false", dest="low_vram")
    parser.add_argument("--resolution", type=int, default=int(os.environ.get("PIXAL3D_RESOLUTION", "1024")))
    args = parser.parse_args()

    os.environ["PIXAL3D_LOW_VRAM"] = "1" if args.low_vram else "0"
    os.environ["PIXAL3D_RESOLUTION"] = str(args.resolution)
    os.environ.setdefault("ATTN_BACKEND", "flash_attn")

    demo = build_ui(args.low_vram, args.resolution)
    demo.launch(server_name=args.host, server_port=args.port, share=args.share, show_error=True)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
