"""Dashboard home screen — animated banner, training launchpad, live ticker."""
from __future__ import annotations

import importlib.util
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from wireml.device import detect_device
from wireml.schema import DeviceInfo
from wireml.templates import TEMPLATES, Template
from wireml.tui.screens.pipeline import PipelineScreen
from wireml.tui.widgets.banner import AnimatedBanner
from wireml.tui.widgets.ticker import StatusTicker

# ─── tile data ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class TrainTile:
    slug: str
    kind: str  # "template" or "webcam"
    category: str
    title: str
    subtitle: str
    glyph: str  # 2-char glyph shown on the left
    template_slug: str | None = None
    webcam_classes: tuple[str, ...] = ()


TILES: tuple[TrainTile, ...] = (
    TrainTile(
        slug="demo-synthetic",
        kind="template",
        category="demo",
        glyph="◆",
        title="Synthetic demo",
        subtitle="toy features → linear head. no downloads. verify.",
        template_slug="demo-synthetic",
    ),
    TrainTile(
        slug="knn-zero-train",
        kind="template",
        category="head",
        glyph="≡",
        title="k-NN · no training",
        subtitle="non-parametric head. instant inference.",
        template_slug="knn-zero-train",
    ),
    TrainTile(
        slug="image-classifier",
        kind="template",
        category="backbone",
        glyph="▦",
        title="Image folder classifier",
        subtitle="folder per class → CLIP → linear.",
        template_slug="image-classifier",
    ),
    TrainTile(
        slug="webcam-phone",
        kind="webcam",
        category="data",
        glyph="▶",
        title="Webcam: phone detector",
        subtitle="with-phone vs without-phone. CLIP + live infer.",
        webcam_classes=("with-phone", "without-phone"),
    ),
    TrainTile(
        slug="webcam-eyes",
        kind="webcam",
        category="data",
        glyph="◉",
        title="Webcam: attention monitor",
        subtitle="eyes-open / eyes-closed / looking-away.",
        webcam_classes=("eyes-open", "eyes-closed", "looking-away"),
    ),
    TrainTile(
        slug="webcam-gesture",
        kind="webcam",
        category="data",
        glyph="✋",
        title="Webcam: hand gestures",
        subtitle="thumbs-up / thumbs-down / open-palm.",
        webcam_classes=("thumbs-up", "thumbs-down", "open-palm"),
    ),
    TrainTile(
        slug="webcam-custom",
        kind="webcam",
        category="eval",
        glyph="✱",
        title="Webcam: custom classes",
        subtitle="type your own class names. hold SPACE per class.",
        webcam_classes=(),
    ),
)


CATEGORY_COLOR = {
    "demo":     (139, 92, 246),  # lavender
    "data":     (16, 185, 129),  # green
    "backbone": (59, 130, 246),  # blue
    "head":     (245, 158, 11),  # amber
    "eval":     (239, 68, 68),   # red
    "deploy":   (20, 184, 166),  # teal
}


# ─── breathing tile widget ──────────────────────────────────────────────────


class TileWidget(ListItem):
    """A tile with a hover/focus breathing glow and category-colored stripe."""

    DEFAULT_CSS = """
    TileWidget {
        background: #0a0e14;
        border: round #2a3240;
        padding: 0 1;
        margin: 0;
        height: 5;
    }
    """

    def __init__(self, tile: TrainTile) -> None:
        self.tile = tile
        super().__init__()
        self._phase = 0.0

    def on_mount(self) -> None:
        self.set_interval(1 / 20, self._tick)

    def _tick(self) -> None:
        self._phase += 0.08
        # Only refresh when highlighted — saves CPU.
        if self.has_class("-highlight"):
            self.refresh()

    def render(self) -> Text:
        t = self.tile
        r, g, b = CATEGORY_COLOR.get(t.category, (139, 92, 246))

        # breathing intensity 0.75 → 1.0
        highlighted = self.has_class("-highlight")
        if highlighted:
            breathe = 0.85 + 0.15 * (0.5 + 0.5 * math.sin(self._phase))
            title_color = f"rgb({r},{g},{b})"
            glyph_style = f"rgb({int(r * breathe)},{int(g * breathe)},{int(b * breathe)}) bold"
            title_style = f"{title_color} bold"
            subtitle_style = "rgb(229,236,244)"
            category_style = "rgb(139,92,246) bold"
        else:
            glyph_style = f"rgb({r},{g},{b})"
            title_style = "rgb(229,236,244) bold"
            subtitle_style = "rgb(108,122,140)"
            category_style = "rgb(108,122,140) bold"

        text = Text()
        text.append(f"  {t.glyph}  ", style=glyph_style)
        text.append(t.category.upper(), style=category_style)
        text.append("\n     ")
        text.append(t.title, style=title_style)
        text.append("\n     ")
        text.append(t.subtitle, style=subtitle_style)
        return text


class DeviceChip(Widget):
    """Animated device chip with a pulsing accent dot."""

    DEFAULT_CSS = """
    DeviceChip {
        background: #0a0e14;
        border: round #2a3240;
        padding: 0 2;
        height: 3;
        margin-top: 1;
    }
    """

    def __init__(self, info: DeviceInfo) -> None:
        self.info = info
        super().__init__()
        self._tick = 0

    def on_mount(self) -> None:
        self.set_interval(1 / 10, self._step)

    def _step(self) -> None:
        self._tick += 1
        self.refresh()

    def render(self) -> Text:
        dot_on = (self._tick // 6) % 2 == 0
        line = Text()
        line.append("● " if dot_on else "○ ", style="rgb(139,92,246) bold")
        line.append(f"{self.info.type.upper():<8}", style="rgb(139,92,246) bold")
        line.append(f"  {self.info.name}", style="rgb(229,236,244)")
        if self.info.vram_gb is not None:
            line.append(f"  ·  {self.info.vram_gb} GB", style="rgb(108,122,140)")
        if self.info.compute:
            line.append(f"  ·  {self.info.compute}", style="rgb(108,122,140)")
        return line


# ─── screen ─────────────────────────────────────────────────────────────────


class HomeScreen(Screen):
    BINDINGS = [
        Binding("enter", "launch", "Launch"),
        Binding("r", "quick_run", "Quick demo"),
        Binding("d", "show_doctor", "Doctor"),
        Binding("q", "app.quit", "Quit"),
    ]

    CSS = """
    HomeScreen {
        background: #0a0e14;
    }

    #dash-root {
        layout: vertical;
        background: #0a0e14;
    }

    #hero-wrap {
        padding: 1 3 0 3;
        height: auto;
        background: #0a0e14;
    }

    #dash-body {
        layout: horizontal;
        height: 1fr;
        padding: 0 2 0 2;
    }

    .col-train { width: 2fr; }
    .col-side  { width: 1fr; }

    .panel {
        background: #0f141c;
        border: round #2a3240;
        padding: 1 2;
        margin: 0 1;
        height: 1fr;
        overflow-y: auto;
    }

    .panel-title {
        color: #6c7a8c;
        text-style: bold;
        margin-bottom: 1;
    }

    ListView {
        background: #0f141c;
        border: none;
        height: auto;
    }

    ListItem.-highlight {
        border: round #8b5cf6;
    }

    StatusTicker {
        border-top: solid #2a3240;
        background: #0a0e14;
    }

    .chip-mini {
        padding: 0 2;
        color: #e5ecf4;
        height: 1;
    }
    """

    def compose(self) -> ComposeResult:
        info = detect_device()
        yield Header(show_clock=False)

        yield Vertical(
            Vertical(
                AnimatedBanner(),
                DeviceChip(info),
                id="hero-wrap",
            ),
            Horizontal(
                Vertical(
                    Label("◈  TRAINING LAUNCHPAD", classes="panel-title"),
                    ListView(*(TileWidget(t) for t in TILES), id="tiles"),
                    classes="panel col-train",
                ),
                Vertical(
                    Label("◈  SYSTEM", classes="panel-title"),
                    VerticalScroll(id="system-panel"),
                    Label("\n◈  RECENT SESSIONS", classes="panel-title"),
                    VerticalScroll(id="sessions-panel"),
                    Label("\n◈  KEYBINDINGS", classes="panel-title"),
                    Static(
                        "[rgb(139,92,246) bold]↑↓[/]    move selection\n"
                        "[rgb(139,92,246) bold]Enter[/] launch\n"
                        "[rgb(139,92,246) bold]r[/]    quick synthetic demo\n"
                        "[rgb(139,92,246) bold]d[/]    doctor\n"
                        "[rgb(139,92,246) bold]q[/]    quit"
                    ),
                    classes="panel col-side",
                ),
                id="dash-body",
            ),
            StatusTicker(),
            id="dash-root",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#tiles", ListView).focus()
        self._render_system()
        self._render_sessions()

    # ─── panels ─────────────────────────────────────────────────────────

    def _render_system(self) -> None:
        panel = self.query_one("#system-panel", VerticalScroll)
        rows = [
            ("python", _python_version(), True),
            ("torch", _mod_version("torch"), _mod_exists("torch")),
            ("transformers", _mod_version("transformers"), _mod_exists("transformers")),
            ("opencv", _mod_version("cv2"), _mod_exists("cv2")),
            ("pynput", _mod_version("pynput"), _mod_exists("pynput")),
            ("clip cached", _clip_cached_label(), _clip_cached()),
        ]
        for label, value, ok in rows:
            icon = "[rgb(16,185,129)]✓[/]" if ok else "[rgb(245,158,11)]—[/]"
            panel.mount(
                Static(
                    f"  {icon} [rgb(108,122,140) bold]{label:<14}[/] "
                    f"[rgb(229,236,244)]{value}[/]",
                    classes="chip-mini",
                )
            )

    def _render_sessions(self) -> None:
        panel = self.query_one("#sessions-panel", VerticalScroll)
        cap = Path.home() / ".wireml" / "captures"
        sessions = sorted(cap.glob("*"), reverse=True)[:5] if cap.exists() else []
        if not sessions:
            panel.mount(
                Static(
                    "  [rgb(108,122,140)]no sessions yet — train one below[/]",
                    classes="chip-mini",
                )
            )
            return
        for sess in sessions:
            classes = sorted(p.name for p in sess.iterdir() if p.is_dir())
            total = sum(1 for p in sess.rglob("*.jpg"))
            when = datetime.fromtimestamp(sess.stat().st_mtime).strftime("%H:%M")
            panel.mount(
                Static(
                    f"  [rgb(139,92,246)]▸[/] [rgb(229,236,244) bold]{sess.name}[/]\n"
                    f"     [rgb(108,122,140)]{when} · {total} frames · "
                    f"{'/'.join(classes) or '(empty)'}[/]",
                    classes="chip-mini",
                )
            )

    # ─── actions ────────────────────────────────────────────────────────

    def action_launch(self) -> None:
        item = self.query_one("#tiles", ListView).highlighted_child
        if isinstance(item, TileWidget):
            self._launch_tile(item.tile)

    def action_quick_run(self) -> None:
        tmpl = next((t for t in TILES if t.template_slug == "demo-synthetic"), None)
        if tmpl:
            self._launch_tile(tmpl, autorun=True)

    def action_show_doctor(self) -> None:
        from wireml.tui.screens.doctor import DoctorScreen

        self.app.push_screen(DoctorScreen())

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if isinstance(event.item, TileWidget):
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
            from wireml.tui.screens.custom_classes import CustomClassesModal

            self.app.push_screen(
                CustomClassesModal(on_submit=self._launch_webcam_with)
            )

    def _launch_webcam_with(self, classes: list[str]) -> None:
        missing = [m for m in ("cv2", "torch") if not _mod_exists(m)]
        if missing:
            self.notify(
                f"missing extras: {', '.join(missing)} — "
                "install with `uv tool install 'wireml[ml,webcam]'`",
                severity="error",
                timeout=10,
            )
            return

        self._spawn_demo(classes)
        self.notify(
            f"▶ launching webcam trainer: {' · '.join(classes)}",
            title="wireml",
            timeout=5,
        )

    @work(thread=True, exclusive=False)
    def _spawn_demo(self, classes: list[str]) -> None:
        import subprocess
        import sys
        from shutil import which

        args = [sys.executable, "-m", "wireml", "demo", "webcam", *classes, "-m", "20"]

        if sys.platform == "win32":
            subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE)  # noqa: S603
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
    return "present" if _clip_cached() else "not yet"
