"""Home screen: pick a template, see the detected device, jump in."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from wireml import __version__
from wireml.device import detect_device
from wireml.schema import DeviceInfo
from wireml.templates import TEMPLATES, Template
from wireml.tui.screens.pipeline import PipelineScreen


class TemplateRow(ListItem):
    """One template row. Carries the template reference so the screen can open it."""

    def __init__(self, template: Template) -> None:
        super().__init__()
        self.template = template

    def compose(self) -> ComposeResult:
        title = f"[b]{self.template.title}[/b]"
        tags = "  ".join(f"[dim]{t}[/dim]" for t in self.template.tags)
        yield Static(f"{title}\n[dim]{self.template.subtitle}[/dim]\n{tags}")


class HomeScreen(Screen):
    """Landing. Template picker + device chip + nav hints."""

    BINDINGS = [
        Binding("enter", "open", "Open"),
        Binding("r", "run_default", "Run demo"),
        Binding("q", "app.quit", "Quit"),
    ]

    device: reactive[DeviceInfo | None] = reactive(None)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Vertical(
            Static(
                "[b]WireML[/b]   [dim]Terminal workbench for no-code ML classification[/dim]",
                classes="panel-title",
                id="brand",
            ),
            Horizontal(
                Vertical(
                    Label("TEMPLATES", classes="panel-title"),
                    ListView(
                        *(TemplateRow(t) for t in TEMPLATES),
                        id="templates",
                    ),
                    classes="panel",
                ),
                Vertical(
                    Label("DEVICE", classes="panel-title"),
                    Static(id="device-info"),
                    Label("\n\nSHORTCUTS", classes="panel-title"),
                    Static(
                        "[b accent]↑↓[/b accent]   move selection\n"
                        "[b accent]Enter[/b accent] open template\n"
                        "[b accent]r[/b accent]    run synthetic demo\n"
                        "[b accent]q[/b accent]    quit",
                        classes="muted",
                    ),
                    Label("\n\nVERSION", classes="panel-title"),
                    Static(f"[dim]wireml {__version__}[/dim]"),
                    classes="panel",
                ),
                id="app-grid",
            ),
            id="home-root",
        )
        yield Footer()

    def on_mount(self) -> None:
        info = detect_device()
        self.device = info
        self.query_one("#device-info", Static).update(self._format_device(info))
        self.query_one("#templates", ListView).focus()

    @staticmethod
    def _format_device(info: DeviceInfo) -> str:
        chip_color = {
            "cuda": "backbone",
            "rocm": "backbone",
            "mps": "accent",
            "mlx": "accent",
            "directml": "warn",
            "xpu": "data",
            "cpu": "muted",
        }.get(info.type, "muted")
        lines = [f"[b {chip_color}]{info.type.upper():<9}[/b {chip_color}] {info.name}"]
        if info.vram_gb is not None:
            lines.append(f"[dim]           {info.vram_gb} GB VRAM[/dim]")
        if info.compute:
            lines.append(f"[dim]           {info.compute}[/dim]")
        return "\n".join(lines)

    def action_open(self) -> None:
        listview = self.query_one("#templates", ListView)
        selected = listview.highlighted_child
        if isinstance(selected, TemplateRow):
            self.app.push_screen(PipelineScreen(selected.template))

    def action_run_default(self) -> None:
        # Jump straight into the first (synthetic) template and auto-run.
        self.app.push_screen(PipelineScreen(TEMPLATES[0], autorun=True))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if isinstance(event.item, TemplateRow):
            self.app.push_screen(PipelineScreen(event.item.template))
