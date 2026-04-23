"""Boot splash: animated banner + typewriter boot log, then transitions to Home."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Static

from wireml.tui.widgets.banner import AnimatedBanner

BOOT_LINES = [
    "[ 0.00s ] wire/ml v0.2.0 · no-code ml runtime",
    "[ 0.03s ] probing compute device .............. ok",
    "[ 0.07s ] scanning ~/.wireml/captures ......... ok",
    "[ 0.11s ] checking huggingface cache .......... ok",
    "[ 0.14s ] locking accent to #8b5cf6 ........... ok",
    "[ 0.17s ] registering node runners ............ ok",
    "[ 0.20s ] warming textual runtime .............. ok",
    "[ 0.23s ] ready. press any key to enter.",
]


class SplashScreen(Screen):
    """Plays once at app boot. Fades to HomeScreen after the boot log finishes."""

    CSS = """
    SplashScreen {
        background: #0a0e14;
        align: center middle;
    }

    #splash-root {
        width: 90%;
        max-width: 90;
        height: auto;
        align: center middle;
    }

    #boot-log {
        padding: 2 0 0 2;
        color: #10b981;
        height: auto;
    }

    #splash-cta {
        padding: 2 0 0 2;
        color: #6c7a8c;
    }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            AnimatedBanner(tagline="teachable machine · reimagined for the terminal"),
            Static("", id="boot-log"),
            Static("", id="splash-cta"),
            id="splash-root",
        )

    def on_mount(self) -> None:
        # Start the boot log typewriter.
        self._line_idx = 0
        self._char_idx = 0
        self._typewriter_interval = self.set_interval(0.012, self._type_next_char)
        # After a fixed total time, auto-advance to home if no keypress.
        self._auto_advance = self.set_timer(2.2, self._goto_home)

    def _type_next_char(self) -> None:
        log = self.query_one("#boot-log", Static)
        if self._line_idx >= len(BOOT_LINES):
            self._typewriter_interval.stop()
            cta = self.query_one("#splash-cta", Static)
            cta.update("[rgb(139,92,246)]▮[/] [rgb(108,122,140)]press any key …[/]")
            return

        lines_out: list[str] = []
        for _i, line in enumerate(BOOT_LINES[: self._line_idx]):
            lines_out.append(f"[rgb(16,185,129)]{line}[/]")
        current = BOOT_LINES[self._line_idx]
        partial = current[: self._char_idx]
        caret = "▌" if (self._char_idx % 2 == 0) else " "
        lines_out.append(f"[rgb(16,185,129)]{partial}[/][rgb(139,92,246)]{caret}[/]")
        log.update("\n".join(lines_out))

        self._char_idx += 1
        if self._char_idx > len(current):
            self._line_idx += 1
            self._char_idx = 0

    def _goto_home(self) -> None:
        if not self.is_mounted:
            return
        # Import lazily so splash paints immediately on app start.
        from wireml.tui.screens.home import HomeScreen

        self.app.switch_screen(HomeScreen())

    def on_key(self, _event) -> None:
        self._goto_home()
