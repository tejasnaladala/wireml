"""Animated ASCII-art banner with cycling gradient colors.

Think: zphisher-style hacker banner, but on the WireML palette (lavender → cyan →
magenta). Hue shifts every frame; rendered entirely through Rich markup so Textual
repaints cheaply.
"""
from __future__ import annotations

import math

from rich.text import Text
from textual.widget import Widget

# 6-line block banner. Raw so the sharp corners read clean on most fonts.
# fmt: off
BANNER = r"""
 ██╗    ██╗██╗██████╗ ███████╗   ███╗   ███╗██╗
 ██║    ██║██║██╔══██╗██╔════╝   ████╗ ████║██║
 ██║ █╗ ██║██║██████╔╝█████╗     ██╔████╔██║██║
 ██║███╗██║██║██╔══██╗██╔══╝     ██║╚██╔╝██║██║
 ╚███╔███╔╝██║██║  ██║███████╗██╗██║ ╚═╝ ██║███████╗
  ╚══╝╚══╝ ╚═╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝     ╚═╝╚══════╝
""".strip("\n")
# fmt: on

# Cyclical palette: lavender → magenta → pink → cyan → back.
# Each entry is (r, g, b) — we lerp between stops based on `t`.
GRADIENT_STOPS = [
    (0.00, (139, 92, 246)),   # lavender #8b5cf6
    (0.25, (255, 92, 206)),   # hot pink
    (0.50, (0, 229, 255)),    # cyan
    (0.75, (122, 138, 253)),  # periwinkle
    (1.00, (139, 92, 246)),   # loop
]


def _lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def gradient_color(phase: float) -> tuple[int, int, int]:
    """phase ∈ [0, 1]. Returns an RGB triple somewhere along the palette."""
    phase = phase - math.floor(phase)
    for i in range(len(GRADIENT_STOPS) - 1):
        p0, c0 = GRADIENT_STOPS[i]
        p1, c1 = GRADIENT_STOPS[i + 1]
        if p0 <= phase <= p1:
            t = (phase - p0) / (p1 - p0 or 1)
            return _lerp(c0, c1, t)
    return GRADIENT_STOPS[0][1]


class AnimatedBanner(Widget):
    """ASCII banner that cycles through the gradient. One-line tagline below."""

    DEFAULT_CSS = """
    AnimatedBanner {
        height: auto;
        padding: 0;
        background: #0a0e14;
    }
    """

    def __init__(self, tagline: str = "no-code ml · foundation models · terminal native") -> None:
        super().__init__()
        self.tagline = tagline
        self._frame = 0

    def on_mount(self) -> None:
        self.set_interval(1 / 20, self._tick)  # 20 fps

    def _tick(self) -> None:
        self._frame = (self._frame + 1) % 200
        self.refresh()

    def render(self) -> Text:
        text = Text()
        lines = BANNER.split("\n")
        width = max(len(line) for line in lines)
        shift = self._frame / 200.0
        for li, line in enumerate(lines):
            for ci, ch in enumerate(line):
                if ch == " ":
                    text.append(ch)
                    continue
                phase = (ci / width + shift + li * 0.02) % 1.0
                r, g, b = gradient_color(phase)
                text.append(ch, style=f"rgb({r},{g},{b})")
            text.append("\n")
        text.append(" ")
        text.append("◆ ", style="rgb(139,92,246) bold")
        text.append(self.tagline, style="rgb(108,122,140)")
        return text
