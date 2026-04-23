"""Top-level Textual application."""
from __future__ import annotations

from textual.app import App

import wireml.nodes  # noqa: F401 — registers runners with the engine
from wireml.tui.screens.home import HomeScreen


class WireMLApp(App):
    """`wireml` — terminal workbench."""

    CSS_PATH = "app.tcss"
    TITLE = "WireML"
    SUB_TITLE = "node-graph ML on foundation models — terminal edition"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("?", "help", "Help"),
    ]

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())

    def action_help(self) -> None:
        self.bell()
        self.notify(
            "Navigate: ↑↓ · Enter to open · Tab between panels · q to quit",
            title="Help",
            timeout=5,
        )
