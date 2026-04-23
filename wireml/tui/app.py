"""Top-level Textual application."""
from __future__ import annotations

from textual.app import App

from wireml.tui.screens.home import HomeScreen


class WireMLApp(App):
    """`wireml` — terminal workbench."""

    CSS_PATH = "app.tcss"
    TITLE = "WireML"
    SUB_TITLE = "no-code ML classifier · foundation models · GPU-aware"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("?", "help", "Help"),
    ]

    def on_mount(self) -> None:
        # Defer runner registration — the pipeline screen imports it lazily.
        # This keeps `wireml` -> dashboard snappy (no numpy/torch import cost).
        self.push_screen(HomeScreen())

    def action_help(self) -> None:
        self.notify(
            "↑↓ navigate · Enter launch · d doctor · r quick demo · q quit",
            title="shortcuts",
            timeout=5,
        )
