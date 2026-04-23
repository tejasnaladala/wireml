"""Doctor screen — mirrors `wireml doctor` but rendered as a modal inside the TUI."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Static


def _mod(name: str) -> tuple[bool, str]:
    spec = importlib.util.find_spec(name)
    if spec is None:
        return False, "—"
    try:
        m = importlib.import_module(name)
        return True, getattr(m, "__version__", "present")
    except Exception:
        return False, "import failed"


class DoctorScreen(ModalScreen):
    BINDINGS = [Binding("escape", "dismiss", "Close")]

    def compose(self) -> ComposeResult:
        from wireml import __version__
        from wireml.device import detect_device

        info = detect_device()
        table = DataTable(zebra_stripes=True)
        table.add_columns("check", "status", "detail")

        mods = ("torch", "transformers", "cv2", "pynput", "mlx", "numpy", "pillow")
        rows = [
            ("wireml", "ok", f"v{__version__}"),
            ("python", "ok", sys.version.split()[0]),
            ("device", "ok", f"{info.type}  ·  {info.name}"),
        ]
        for mod in mods:
            present, ver = _mod(mod)
            rows.append((mod, "ok" if present else "missing", ver))

        hf_cache = Path.home() / ".cache" / "huggingface" / "hub" / "models--openai--clip-vit-base-patch32"
        rows.append((
            "clip cached",
            "ok" if hf_cache.exists() else "not yet",
            str(hf_cache) if hf_cache.exists() else "runs on first webcam demo",
        ))

        cap_dir = Path.home() / ".wireml" / "captures"
        sessions = list(cap_dir.glob("*")) if cap_dir.exists() else []
        rows.append(("capture sessions", "ok" if sessions else "none", f"{len(sessions)}"))

        for check, status, detail in rows:
            table.add_row(check, status, detail)

        yield Vertical(
            Static(
                "[b]WireML · doctor[/b]\n[muted]hit ESC to close[/muted]",
            ),
            table,
            id="modal",
        )

    def action_dismiss(self) -> None:
        self.app.pop_screen()
