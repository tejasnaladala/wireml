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


@demo_app.command("webcam")
def demo_webcam(
    classes: list[str] = typer.Argument(  # noqa: B008
        ...,
        help="Class names, e.g. `with-phone without-phone`. Need 2+.",
    ),
    samples: int = typer.Option(30, "--samples", "-s", help="Samples per class."),
    camera: int = typer.Option(0, "--camera", "-c", help="Camera index (0, 1, …)."),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Teachable-Machine-style webcam demo.

    Opens your webcam, captures samples for each class, trains a CLIP-based
    linear classifier, and shows a live prediction overlay.

    Example:
        wireml demo webcam with-phone without-phone --samples 40
    """
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )
    from wireml.demos.webcam import run as run_demo

    try:
        run_demo(class_names=classes, samples_per_class=samples, camera=camera)
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
