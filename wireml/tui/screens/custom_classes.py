"""Modal for entering custom webcam class names."""
from __future__ import annotations

from collections.abc import Callable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static


class CustomClassesModal(ModalScreen):
    """Ask the user for 2–6 space-separated class names, then invoke callback."""

    BINDINGS = [
        Binding("escape", "dismiss", "Cancel"),
        Binding("enter", "submit", "Launch"),
    ]

    def __init__(self, on_submit: Callable[[list[str]], None]) -> None:
        super().__init__()
        self._on_submit = on_submit

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(
                "[b]CUSTOM WEBCAM CLASSES[/b]\n"
                "[muted]enter 2–6 class names separated by spaces[/muted]",
            ),
            Input(
                value="happy sad surprised",
                placeholder="e.g. happy sad surprised",
                id="classes-input",
            ),
            Static(
                "[muted]after launching: click the webcam window, drag an ROI, "
                "press ENTER, then hold SPACE for each class.[/muted]",
            ),
            Horizontal(
                Button("Launch", id="launch", variant="primary"),
                Button("Cancel", id="cancel"),
            ),
            id="modal",
        )

    def on_mount(self) -> None:
        self.query_one("#classes-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "launch":
            self.action_submit()
        else:
            self.action_dismiss()

    def on_input_submitted(self, _event: Input.Submitted) -> None:
        self.action_submit()

    def action_submit(self) -> None:
        raw = self.query_one("#classes-input", Input).value.strip()
        classes = [c for c in raw.split() if c]
        if len(classes) < 2:
            self.notify("need at least two class names", severity="error")
            return
        if len(classes) > 6:
            self.notify("capped at 6 classes", severity="warning")
            classes = classes[:6]
        cb = self._on_submit
        self.app.pop_screen()
        cb(classes)

    def action_dismiss(self) -> None:
        self.app.pop_screen()
