"""`wireml` command-line entry.

Default behavior launches the TUI. Subcommands expose headless paths for
scripting and CI.
"""
from __future__ import annotations

import contextlib
import logging
import sys

import typer

from wireml import __version__

# Windows legacy consoles default to cp1252, which chokes on the Unicode
# arrows / bullets the TUI and CLI use. Force UTF-8 on supported Pythons.
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        with contextlib.suppress(OSError, ValueError):
            reconfigure(encoding="utf-8", errors="replace")

app = typer.Typer(
    name="wireml",
    help="Terminal-first no-code ML classifier — Teachable Machine for the foundation-model era.",
    add_completion=False,
    no_args_is_help=False,
)


@app.callback(invoke_without_command=True)
def default(ctx: typer.Context) -> None:
    """Launch the TUI if no subcommand was given."""
    if ctx.invoked_subcommand is None:
        from wireml.tui.app import WireMLApp

        WireMLApp().run()


@app.command()
def version() -> None:
    """Print the installed WireML version and exit."""
    typer.echo(f"wireml {__version__}")


@app.command()
def device() -> None:
    """Print the auto-detected compute device."""
    from wireml.device import detect_device

    info = detect_device()
    typer.echo(f"{info.type:<10} {info.name}")
    if info.vram_gb is not None:
        typer.echo(f"           {info.vram_gb} GB VRAM")
    if info.compute:
        typer.echo(f"           compute: {info.compute}")


@app.command()
def templates() -> None:
    """List built-in templates."""
    from wireml.templates import TEMPLATES

    for t in TEMPLATES:
        typer.echo(f"{t.slug:<20} {t.title}")
        typer.echo(f"                     {t.subtitle}")


demo_app = typer.Typer(help="Interactive end-to-end demos (webcam, etc).")
app.add_typer(demo_app, name="demo")


@demo_app.command("camera-check")
def demo_camera_check() -> None:
    """Probe every camera index 0–3 and report backend + resolution + fps.

    Use when the webcam demo looks blurry or fails to open — the results
    tell you which --camera index and which backend your host prefers.
    """
    try:
        import cv2
    except ImportError as exc:  # pragma: no cover
        typer.secho(
            "opencv not installed. Run: uv tool install 'git+https://github.com/tejasnaladala/wireml' --with 'wireml[ml,webcam]'",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1) from exc

    backends = [
        ("DirectShow", getattr(cv2, "CAP_DSHOW", 700)),
        ("MediaFoundation", getattr(cv2, "CAP_MSMF", 1400)),
        ("Any", cv2.CAP_ANY),
    ]
    any_found = False
    for idx in range(4):
        for name, backend in backends:
            cap = cv2.VideoCapture(idx, backend)
            if not cap.isOpened():
                cap.release()
                continue
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            ok, _ = cap.read()
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            status = "ok" if ok else "opened-no-frame"
            typer.echo(f"  camera {idx:<2} · {name:<16} · {w}x{h} @ {fps:.0f}fps · {status}")
            any_found = True
            break
    if not any_found:
        typer.secho("no cameras detected", fg=typer.colors.RED)


@demo_app.command("webcam")
def demo_webcam(
    classes: list[str] = typer.Argument(  # noqa: B008
        ...,
        help="Class names, e.g. `with-phone without-phone`. Need 2+.",
    ),
    min_samples: int = typer.Option(
        15,
        "--min-samples",
        "-m",
        help="Soft floor before you can advance to the next class. No upper limit.",
    ),
    camera: int = typer.Option(0, "--camera", "-c", help="Camera index (0, 1, …)."),
    sharpen: float = typer.Option(
        0.6,
        "--sharpen",
        help="Unsharp-mask amount [0.0–2.0]. Toggle with S, +/- to nudge, 0 to disable.",
    ),
    width: int = typer.Option(1920, "--width", help="Target capture width."),
    height: int = typer.Option(1080, "--height", help="Target capture height."),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Teachable-Machine-style webcam demo.

    Opens your webcam. HOLD SPACE to stream frames into the current class
    (release to stop). Press N to advance to the next class. After all
    classes are captured, trains a CLIP-based linear classifier and opens a
    live prediction window.

    Example:
        wireml demo webcam with-phone without-phone
    """
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )
    from wireml.demos.webcam import run as run_demo

    try:
        run_demo(
            class_names=classes,
            min_samples=min_samples,
            camera=camera,
            sharpen=sharpen,
            width=width,
            height=height,
        )
    except RuntimeError as exc:
        typer.secho(f"✗ {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc


@app.command()
def run(
    template: str = typer.Argument(..., help="Template slug (see `wireml templates`)"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Headless: execute a template end-to-end and print results."""
    import wireml.nodes  # noqa: F401 — registers runners
    from wireml.engine import engine
    from wireml.schema import StageState
    from wireml.templates import get_template

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )

    tmpl = get_template(template)
    if tmpl is None:
        typer.secho(f"unknown template: {template}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    pipeline = tmpl.build()

    def _progress(stage: StageState) -> None:
        status = stage.status.upper()
        msg = stage.message or ""
        typer.echo(f"  [{status:<7}] {stage.schema_id:<30} {msg}")

    typer.echo(f"▶ {pipeline.name}")
    try:
        engine.execute(pipeline, on_progress=_progress)
    except RuntimeError as exc:
        typer.secho(f"✗ pipeline failed: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc
    typer.secho("✓ pipeline complete", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
