"""Dashboard home screen — the launchpad for every training path."""
from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from wireml import __version__
from wireml.device import detect_device
from wireml.schema import DeviceInfo
from wireml.templates import TEMPLATES, Template
from wireml.tui.screens.pipeline import PipelineScreen


@dataclass(frozen=True)
class TrainTile:
    """A big clickable thing on the dashboard. Either opens a template or
    shells out to the webcam demo."""

    slug: str
    kind: str  # "template" or "webcam"
    category: str  # colors the left stripe
    title: str
    subtitle: str
    template_slug: str | None = None
    webcam_classes: tuple[str, ...] = ()


TILES: tuple[TrainTile, ...] = (
    TrainTile(
        slug="demo-synthetic",
        kind="template",
        category="demo",
        title="Synthetic demo",
        subtitle="Toy features → linear head. No downloads, no camera.",
        template_slug="demo-synthetic",
    ),
    TrainTile(
        slug="knn-zero-train",
        kind="template",
        category="head",
        title="k-NN, no training",
        subtitle="Same data path, non-parametric head. Instant.",
        template_slug="knn-zero-train",
    ),
    TrainTile(
        slug="image-classifier",
        kind="template",
        category="backbone",
        title="Image folder classifier",
        subtitle="Folder per class → CLIP → linear. Needs `wireml[ml]`.",
        template_slug="image-classifier",
    ),
    TrainTile(
        slug="webcam-phone",
        kind="webcam",
        category="data",
        title="Webcam: phone detector",
        subtitle="Train live: with-phone vs without-phone. CLIP-based.",
        webcam_classes=("with-phone", "without-phone"),
    ),
    TrainTile(
        slug="webcam-eyes",
        kind="webcam",
        category="data",
        title="Webcam: attention monitor",
        subtitle="eyes-open vs eyes-closed / looking-away. Live inference.",
        webcam_classes=("eyes-open", "eyes-closed", "looking-away"),
    ),
    TrainTile(
        slug="webcam-gesture",
        kind="webcam",
        category="data",
        title="Webcam: hand gestures",
        subtitle="Up to you — define any three classes live.",
        webcam_classes=("thumbs-up", "thumbs-down", "open-palm"),
    ),
    TrainTile(
        slug="webcam-custom",
        kind="webcam",
        category="eval",
        title="Webcam: custom classes",
        subtitle="You pick the classes in the prompt. Hold SPACE to record each.",
        webcam_classes=(),
    ),
)


# ─── widgets ────────────────────────────────────────────────────────────────


class DeviceChip(Static):
    """Big header chip reporting the auto-detected device."""

    DEFAULT_CSS = ""

    def __init__(self, info: DeviceInfo) -> None:
        self.info = info
        super().__init__(classes=f"chip chip-{info.type}")

    def render(self) -> str:
        vram = f" · {self.info.vram_gb} GB" if self.info.vram_gb is not None else ""
        compute = f" · {self.info.compute}" if self.info.compute else ""
        return (
            f"[b]◆ {self.info.type.upper():<8}[/b] "
            f"{self.info.name}"
            f"{vram}{compute}"
        )


class StatusChip(Static):
    """Mini status chip: extras installed, CLIP cached, etc."""

    def __init__(self, label: str, value: str, ok: bool) -> None:
        self._label = label
        self._value = value
        self._ok = ok
        super().__init__(classes="chip")

    def render(self) -> str:
        icon = "[ok]✓[/ok]" if self._ok else "[warn]—[/warn]"
        return (
            f"{icon}  [chip-label]{self._label}[/chip-label]  "
            f"{self._value}"
        )


class TrainTileButton(ListItem):
    """One tile in the training launcher grid."""

    def __init__(self, tile: TrainTile) -> None:
        self.tile = tile
        super().__init__(classes=f"tile -{tile.category}")

    def compose(self) -> ComposeResult:
        yield Static(
            f"[tile-cat][b]{self.tile.category.upper()}[/b][/tile-cat]\n"
            f"[tile-title]{self.tile.title}[/tile-title]\n"
            f"[tile-sub]{self.tile.subtitle}[/tile-sub]"
        )


# ─── screen ─────────────────────────────────────────────────────────────────


class HomeScreen(Screen):
    """Dashboard: device chip · training launchpad · status panel · recent sessions."""

    BINDINGS = [
        Binding("enter", "launch", "Launch selected"),
        Binding("r", "quick_run", "Quick synthetic demo"),
        Binding("d", "show_doctor", "Doctor"),
        Binding("q", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        info = detect_device()
        yield Header(show_clock=False)

        yield Vertical(
            Vertical(
                Static(
                    "[hero-brand]▮▮ WIRE/ML[/hero-brand]  "
                    "[muted]terminal workbench · v"
                    f"{__version__}[/muted]",
                ),
                Static(
                    "[hero-title]No-code ML classifier for the foundation-model era.[/hero-title]",
                ),
                Static(
                    "[hero-sub]pick a training path below — webcam, image folder, or synthetic.[/hero-sub]",
                ),
                DeviceChip(info),
                classes="hero",
            ),
            Horizontal(
                Vertical(
                    Label("TRAINING LAUNCHPAD", classes="panel-title"),
                    ListView(*(TrainTileButton(t) for t in TILES), id="tiles"),
                    classes="panel col-train",
                ),
                Vertical(
                    Label("SYSTEM", classes="panel-title"),
                    VerticalScroll(id="system-panel"),
                    Label("\nRECENT SESSIONS", classes="panel-title"),
                    VerticalScroll(id="sessions-panel"),
                    Label("\nSHORTCUTS", classes="panel-title"),
                    Static(
                        "[kbd]↑↓[/kbd]    move selection\n"
                        "[kbd]Enter[/kbd] launch tile\n"
                        "[kbd]r[/kbd]    quick synthetic demo\n"
                        "[kbd]d[/kbd]    doctor / health-check\n"
                        "[kbd]q[/kbd]    quit",
                    ),
                    classes="panel col-side",
                ),
                classes="dash-grid",
            ),
            id="dash-root",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#tiles", ListView).focus()
        self._render_system()
        self._render_sessions()

    # ─── system / sessions panels ─────────────────────────────────────────

    def _render_system(self) -> None:
        panel = self.query_one("#system-panel", VerticalScroll)
        checks = [
            ("python", _python_version(), True),
            ("torch", _mod_version("torch"), _mod_exists("torch")),
            ("transformers", _mod_version("transformers"), _mod_exists("transformers")),
            ("opencv", _mod_version("cv2"), _mod_exists("cv2")),
            ("pynput", _mod_version("pynput"), _mod_exists("pynput")),
            ("clip cached", _clip_cached_label(), _clip_cached()),
        ]
        for label, value, ok in checks:
            panel.mount(StatusChip(label, value, ok))

    def _render_sessions(self) -> None:
        panel = self.query_one("#sessions-panel", VerticalScroll)
        cap = Path.home() / ".wireml" / "captures"
        sessions = sorted(cap.glob("*"), reverse=True)[:5] if cap.exists() else []
        if not sessions:
            panel.mount(Static("[muted]no sessions yet — run the webcam demo to record one[/muted]"))
            return
        for sess in sessions:
            classes = sorted(p.name for p in sess.iterdir() if p.is_dir())
            total = sum(1 for p in sess.rglob("*.jpg"))
            when = datetime.fromtimestamp(sess.stat().st_mtime).strftime("%b %d · %H:%M")
            panel.mount(
                Static(
                    f"[session-title]{sess.name}[/session-title]\n"
                    f"[session-meta]{when} · {total} frames · "
                    f"{'/'.join(classes) or 'no classes'}[/session-meta]"
                )
            )

    # ─── actions ─────────────────────────────────────────────────────────

    def action_launch(self) -> None:
        item = self.query_one("#tiles", ListView).highlighted_child
        if isinstance(item, TrainTileButton):
            self._launch_tile(item.tile)

    def action_quick_run(self) -> None:
        tmpl = next((t for t in TILES if t.template_slug == "demo-synthetic"), None)
        if tmpl:
            self._launch_tile(tmpl, autorun=True)

    def action_show_doctor(self) -> None:
        from wireml.tui.screens.doctor import DoctorScreen

        self.app.push_screen(DoctorScreen())

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if isinstance(event.item, TrainTileButton):
            self._launch_tile(event.item.tile)

    def _launch_tile(self, tile: TrainTile, autorun: bool = False) -> None:
        if tile.kind == "template":
            template = _find_template(tile.template_slug or "")
            if template is None:
                self.notify(f"unknown template {tile.template_slug}", severity="error")
                return
            self.app.push_screen(PipelineScreen(template, autorun=autorun))
            return

        if tile.kind == "webcam":
            if tile.webcam_classes:
                self._launch_webcam_with(list(tile.webcam_classes))
                return
            # Custom-classes tile: prompt for class names.
            from wireml.tui.screens.custom_classes import CustomClassesModal

            self.app.push_screen(
                CustomClassesModal(on_submit=self._launch_webcam_with)
            )

    def _launch_webcam_with(self, classes: list[str]) -> None:
        """Pre-flight check + detach the webcam demo into its own console."""
        missing = [m for m in ("cv2", "torch") if not _mod_exists(m)]
        if missing:
            self.notify(
                f"Install extras first: uv tool install 'wireml[ml,webcam]' "
                f"(missing: {', '.join(missing)})",
                severity="error",
                timeout=10,
            )
            return

        self._spawn_demo(classes)
        self.notify(
            f"launching webcam trainer — classes: {', '.join(classes)}",
            title="WireML",
            timeout=5,
        )

    @work(thread=True, exclusive=False)
    def _spawn_demo(self, classes: list[str]) -> None:
        """Fork the demo as a detached process. Windows → CREATE_NEW_CONSOLE.
        macOS/Linux → launch inside an available terminal emulator.
        """
        import subprocess
        import sys
        from shutil import which

        args = [sys.executable, "-m", "wireml", "demo", "webcam", *classes, "-m", "20"]

        if sys.platform == "win32":
            subprocess.Popen(  # noqa: S603
                args,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        else:
            term = (
                which("x-terminal-emulator")
                or which("gnome-terminal")
                or which("konsole")
                or which("alacritty")
                or which("kitty")
                or which("wezterm")
            )
            if term:
                subprocess.Popen([term, "-e", *args])  # noqa: S603
            else:
                subprocess.Popen(args)  # noqa: S603


# ─── helpers ────────────────────────────────────────────────────────────────


def _find_template(slug: str) -> Template | None:
    return next((t for t in TEMPLATES if t.slug == slug), None)


def _mod_exists(mod: str) -> bool:
    return importlib.util.find_spec(mod) is not None


def _mod_version(mod: str) -> str:
    spec = importlib.util.find_spec(mod)
    if spec is None:
        return "—"
    try:
        m = importlib.import_module(mod)
        return getattr(m, "__version__", "present")
    except Exception:
        return "present"


def _python_version() -> str:
    import sys

    return sys.version.split()[0]


def _clip_cached() -> bool:
    path = Path.home() / ".cache" / "huggingface" / "hub" / "models--openai--clip-vit-base-patch32"
    return path.exists()


def _clip_cached_label() -> str:
    return "present" if _clip_cached() else "not yet · runs on first webcam demo"
