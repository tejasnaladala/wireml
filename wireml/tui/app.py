"""Top-level Textual application. Boots into a splash, then the dashboard."""
from __future__ import annotations

from textual.app import App


class WireMLApp(App):
    """wire/ml — animated terminal workbench."""

    CSS_PATH = "app.tcss"
    TITLE = "wire/ml"
    SUB_TITLE = "no-code ml · foundation models · terminal native"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("?", "help", "Help"),
    ]

    def on_mount(self) -> None:
        # Splash plays a 2s boot sequence, then auto-switches to the dashboard.
        from wireml.tui.screens.splash import SplashScreen

        self.push_screen(SplashScreen())

    def action_help(self) -> None:
        self.notify(
            "↑↓ navigate · Enter launch · d doctor · r quick demo · q quit",
            title="shortcuts",
            timeout=5,
        )
