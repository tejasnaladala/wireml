"""Scrolling status ticker — sweeps across the bottom with live data."""
from __future__ import annotations

import importlib.util
import time
from datetime import datetime

from rich.text import Text
from textual.widget import Widget


def _mod_version(mod: str) -> str | None:
    if importlib.util.find_spec(mod) is None:
        return None
    try:
        m = importlib.import_module(mod)
        return getattr(m, "__version__", "present")
    except Exception:
        return None


class StatusTicker(Widget):
    """Marquee-style ticker. Cycles through live stats separated by chevrons."""

    DEFAULT_CSS = """
    StatusTicker {
        background: #0a0e14;
        color: #6c7a8c;
        height: 1;
        padding: 0 2;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._offset = 0
        self._stats_cache: list[tuple[str, str]] = []
        self._stats_next_refresh = 0.0

    def on_mount(self) -> None:
        self.set_interval(1 / 10, self._tick)

    def _tick(self) -> None:
        self._offset = (self._offset + 1) % 10_000
        self.refresh()

    def _stats(self) -> list[tuple[str, str]]:
        now = time.monotonic()
        if now < self._stats_next_refresh and self._stats_cache:
            return self._stats_cache
        self._stats_next_refresh = now + 2.0

        from pathlib import Path

        cap = Path.home() / ".wireml" / "captures"
        sessions = sorted(cap.glob("*"), reverse=True)[:5] if cap.exists() else []
        session_count = len(list(cap.glob("*"))) if cap.exists() else 0
        latest_session = sessions[0].name if sessions else "none"

        clip_cached = (
            Path.home() / ".cache" / "huggingface" / "hub"
            / "models--openai--clip-vit-base-patch32"
        ).exists()

        items: list[tuple[str, str]] = [
            ("STATUS", "READY"),
            ("TIME", datetime.now().strftime("%H:%M:%S")),
            ("SESSIONS", str(session_count)),
            ("LATEST", latest_session),
            ("CLIP", "CACHED" if clip_cached else "NOT-YET"),
        ]
        if (v := _mod_version("torch")) is not None:
            items.append(("TORCH", v))
        if (v := _mod_version("cv2")) is not None:
            items.append(("CV2", v))
        if (v := _mod_version("transformers")) is not None:
            items.append(("TRF", v))
        self._stats_cache = items
        return items

    def render(self) -> Text:
        line = Text()
        sep = Text("  ◆  ", style="rgb(139,92,246)")
        for label, value in self._stats():
            line.append(f"{label}:", style="rgb(108,122,140)")
            line.append(f" {value}", style="rgb(229,236,244) bold")
            line.append(sep)
        # Add an animated cursor at the end for "live" feel.
        cursor = "▮" if (self._offset // 5) % 2 == 0 else " "
        line.append(cursor, style="rgb(139,92,246) bold")
        return line
