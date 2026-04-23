"""Webcam-based Teachable-Machine-style demo.

Three-phase flow:
  1. SELECT ROI      — drag a box over the area you want to train on.
                       Tight crops cut noise and are much more accurate.
  2. CAPTURE         — hold SPACE to stream frames for each class (no ceiling).
                       Press N to advance. F to refocus. ESC to cancel.
  3. LIVE INFERENCE  — after training, predictions stream live with probability
                       bars. Press R to redo ROI. ESC to quit.

Architecture:
  - A dedicated thread reads frames from the camera into a 1-slot buffer.
  - A dedicated inference worker pulls the latest frame, runs CLIP, and
    updates the prediction. The UI loop never blocks on inference.
"""
from __future__ import annotations

import datetime
import logging
import math
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

WINDOW = "WireML"
CAPTURE_ROOT = Path(
    os.environ.get("WIREML_CAPTURE_DIR") or (Path.home() / ".wireml" / "captures")
)

# ─── palette (BGR for cv2; mirrors wireml/tui/app.tcss) ─────────────────────
BG = (20, 14, 10)          # #0a0e14
SURFACE = (33, 25, 19)     # #131921
BORDER = (64, 50, 42)      # #2a3240
TEXT = (244, 236, 229)     # #e5ecf4
MUTED = (140, 122, 108)    # #6c7a8c
ACCENT = (246, 92, 139)    # #8b5cf6 lavender
DATA = (129, 185, 16)      # #10b981 green
BACKBONE = (246, 130, 59)  # #3b82f6 blue
HEAD = (11, 158, 245)      # #f59e0b amber
EVAL = (68, 68, 239)       # #ef4444 red
DEPLOY = (184, 184, 20)    # #14b8a6 teal
REC_RED = (68, 68, 239)

FONT = 0  # cv2.FONT_HERSHEY_SIMPLEX placeholder; overwritten after cv2 import
MONO_FONT = 0


def _init_fonts() -> None:
    """Bind cv2 font constants. Called after cv2 import."""
    import cv2

    global FONT, MONO_FONT
    FONT = cv2.FONT_HERSHEY_DUPLEX
    MONO_FONT = cv2.FONT_HERSHEY_PLAIN


# ═══════════════════════════════════════════════════════════════════════════
#                            DATA TYPES
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class _Capture:
    class_name: str
    frames: list = field(default_factory=list)


@dataclass(frozen=True)
class Roi:
    """Region of interest rectangle (top-left + size)."""

    x: int
    y: int
    w: int
    h: int

    def apply(self, frame):
        """Return the cropped BGR image."""
        return frame[self.y : self.y + self.h, self.x : self.x + self.w]

    def is_full(self, frame) -> bool:
        h, w = frame.shape[:2]
        return self.x == 0 and self.y == 0 and self.w == w and self.h == h


# ═══════════════════════════════════════════════════════════════════════════
#                            HUD DRAWING
# ═══════════════════════════════════════════════════════════════════════════


def _panel(frame, x: int, y: int, w: int, h: int, alpha: float = 0.85) -> None:
    """Translucent dark panel with a 1px lavender top stroke."""
    import cv2

    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + w, y + h), BG, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    cv2.line(frame, (x, y), (x + w, y), ACCENT, 1, cv2.LINE_AA)


def _corner_brackets(frame, x: int, y: int, w: int, h: int, color, size: int = 18) -> None:
    """Decorative L-brackets at the four corners of a rectangle."""
    import cv2

    t = 1
    # top-left
    cv2.line(frame, (x, y), (x + size, y), color, t, cv2.LINE_AA)
    cv2.line(frame, (x, y), (x, y + size), color, t, cv2.LINE_AA)
    # top-right
    cv2.line(frame, (x + w, y), (x + w - size, y), color, t, cv2.LINE_AA)
    cv2.line(frame, (x + w, y), (x + w, y + size), color, t, cv2.LINE_AA)
    # bottom-left
    cv2.line(frame, (x, y + h), (x + size, y + h), color, t, cv2.LINE_AA)
    cv2.line(frame, (x, y + h), (x, y + h - size), color, t, cv2.LINE_AA)
    # bottom-right
    cv2.line(frame, (x + w, y + h), (x + w - size, y + h), color, t, cv2.LINE_AA)
    cv2.line(frame, (x + w, y + h), (x + w, y + h - size), color, t, cv2.LINE_AA)


def _text(frame, text: str, pos, font=None, scale=0.55, color=TEXT, thickness=1) -> None:
    import cv2

    cv2.putText(
        frame, text, pos, font or FONT, scale, color, thickness, cv2.LINE_AA
    )


def _draw_top_bar(frame, status: str, device: str, sharpen: float = 0.0) -> None:
    """Top HUD: brand mark, mode badge, detected device, sharpen amount."""
    import cv2

    h, w = frame.shape[:2]
    bar_h = 36
    _panel(frame, 0, 0, w, bar_h, alpha=0.82)

    # brand
    cv2.rectangle(frame, (14, 10), (26, 22), ACCENT, -1)
    _text(frame, "WIRE/ML", (34, 22), scale=0.55, color=TEXT, thickness=2)

    _text(frame, status.upper(), (140, 22), scale=0.5, color=ACCENT, thickness=1)

    # right-aligned stack: sharpen + device
    right_x = w - 20
    device_str = f"DEVICE  {device.upper()}"
    device_size = cv2.getTextSize(device_str, FONT, 0.45, 1)[0]
    _text(frame, device_str, (right_x - device_size[0], 22), scale=0.45, color=MUTED)

    sharp_str = f"SHARPEN  {sharpen:.1f}"
    sharp_size = cv2.getTextSize(sharp_str, FONT, 0.45, 1)[0]
    sharp_x = right_x - device_size[0] - 24 - sharp_size[0]
    sharp_color = ACCENT if sharpen > 0 else MUTED
    _text(frame, sharp_str, (sharp_x, 22), scale=0.45, color=sharp_color)

    cv2.line(frame, (0, bar_h), (w, bar_h), BORDER, 1, cv2.LINE_AA)


def _draw_capture_hud(
    frame,
    class_name: str,
    captured: int,
    is_recording: bool,
    min_samples: int,
    device: str,
    class_index: int,
    total_classes: int,
    sharpen: float = 0.0,
) -> None:
    """Capture-phase HUD — class name, sample count, controls."""
    import cv2

    _draw_top_bar(frame, f"CAPTURE · {class_index + 1}/{total_classes}", device, sharpen)

    h, w = frame.shape[:2]
    panel_h = 86
    panel_y = h - panel_h
    _panel(frame, 0, panel_y, w, panel_h, alpha=0.82)

    # class label (mono caption + big sans name)
    _text(frame, f"CLASS  {class_index + 1}/{total_classes}", (20, panel_y + 20),
          scale=0.42, color=MUTED)
    _text(frame, class_name.upper(), (20, panel_y + 50),
          scale=1.0, color=TEXT, thickness=2)

    # sample counter right-aligned
    count_color = ACCENT if captured >= min_samples else HEAD
    count_label = f"{captured:04d}"
    size = cv2.getTextSize(count_label, FONT, 1.4, 2)[0]
    _text(frame, count_label, (w - 20 - size[0], panel_y + 52),
          scale=1.4, color=count_color, thickness=2)
    _text(frame, f"SAMPLES  MIN {min_samples}", (w - 20 - size[0], panel_y + 74),
          scale=0.42, color=MUTED)

    # REC indicator + hint strip
    if is_recording:
        pulse = 0.5 + 0.5 * math.sin(time.monotonic() * 6)  # 0→1→0
        pulse_thickness = int(1 + pulse * 2)
        cv2.circle(frame, (30, panel_y - 22), 6, REC_RED, -1, cv2.LINE_AA)
        cv2.circle(frame, (30, panel_y - 22), 10 + int(pulse * 4), REC_RED,
                   pulse_thickness, cv2.LINE_AA)
        _text(frame, "REC", (46, panel_y - 16), scale=0.55, color=REC_RED, thickness=2)
        _text(frame, "release SPACE to stop", (100, panel_y - 16),
              scale=0.45, color=MUTED)
    else:
        _text(
            frame,
            "[SPACE] hold to record   [N] next class   [F] refocus   [R] redo ROI   [ESC] quit",
            (20, panel_y - 12), scale=0.45, color=MUTED,
        )


def _draw_inference_hud(
    frame, label: str, scores: list, fps: float, device: str, sharpen: float = 0.0
) -> None:
    import cv2

    _draw_top_bar(frame, "LIVE INFERENCE", device, sharpen)

    h, w = frame.shape[:2]
    panel_w = 320
    panel_h = 48 + 30 * max(len(scores), 1) + 20
    panel_x = 20
    panel_y = 60
    _panel(frame, panel_x, panel_y, panel_w, panel_h, alpha=0.85)
    _corner_brackets(frame, panel_x, panel_y, panel_w, panel_h, ACCENT, size=14)

    _text(frame, "PREDICTION", (panel_x + 14, panel_y + 22),
          scale=0.42, color=MUTED)

    # big label
    label_str = label.upper()
    _text(frame, label_str, (panel_x + 14, panel_y + 58),
          scale=0.95, color=ACCENT, thickness=2)

    y = panel_y + 96
    for idx, (cls, score) in enumerate(scores):
        row_color = TEXT if idx == 0 else MUTED
        _text(frame, cls, (panel_x + 14, y), scale=0.45, color=row_color)
        _text(frame, f"{score * 100:5.1f}%", (panel_x + 150, y),
              font=MONO_FONT, scale=1.0, color=row_color, thickness=1)
        # bar
        bar_x = panel_x + 210
        bar_w = panel_w - 224
        cv2.rectangle(frame, (bar_x, y - 10), (bar_x + bar_w, y - 4), BORDER, -1)
        filled = int(bar_w * score)
        cv2.rectangle(frame, (bar_x, y - 10), (bar_x + filled, y - 4), ACCENT, -1)
        y += 28

    # footer
    footer_y = panel_y + panel_h - 10
    _text(frame, f"{fps:4.0f} fps", (panel_x + 14, footer_y),
          font=MONO_FONT, scale=0.9, color=MUTED)
    _text(frame, "[R] redo ROI   [ESC] quit", (panel_x + 100, footer_y),
          scale=0.4, color=MUTED)


def _draw_roi(frame, roi: Roi, label: str = "ROI") -> None:
    """Draw the ROI overlay — brackets + dim outside, crosshairs on center."""
    import cv2

    h, w = frame.shape[:2]
    # dim outside of ROI
    mask = frame.copy()
    cv2.rectangle(mask, (0, 0), (w, h), (0, 0, 0), -1)
    cv2.rectangle(mask, (roi.x, roi.y), (roi.x + roi.w, roi.y + roi.h), (255, 255, 255), -1)
    alpha_mask = mask.astype(float) / 255.0
    # inverse: alpha over outside
    outside_dim = frame.copy()
    cv2.rectangle(outside_dim, (0, 0), (w, h), (0, 0, 0), -1)
    # Blend: where mask is white, keep frame; where black, use a dimmed version.
    dim = cv2.addWeighted(frame, 0.35, outside_dim, 0.65, 0)
    frame[:] = (frame * alpha_mask + dim * (1 - alpha_mask)).astype(frame.dtype)

    _corner_brackets(frame, roi.x, roi.y, roi.w, roi.h, ACCENT, size=24)
    cv2.line(frame, (roi.x, roi.y), (roi.x + roi.w, roi.y + roi.h), ACCENT, 1, cv2.LINE_AA)
    _text(frame, label, (roi.x + 4, roi.y - 8), scale=0.42, color=ACCENT)


# ═══════════════════════════════════════════════════════════════════════════
#                          CAMERA + THREADS
# ═══════════════════════════════════════════════════════════════════════════


def _lazy_imports():
    try:
        import cv2  # noqa: F401
        import numpy as np  # noqa: F401
        from PIL import Image  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "Install the webcam extra: "
            "uv tool install 'git+https://github.com/tejasnaladala/wireml' "
            "--with 'wireml[ml,webcam]'"
        ) from exc
    try:
        import torch  # noqa: F401
        from transformers import CLIPModel, CLIPProcessor  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "Install the ml extra: "
            "uv tool install 'git+https://github.com/tejasnaladala/wireml' "
            "--with 'wireml[ml,webcam]'"
        ) from exc
    try:
        from pynput import keyboard  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "Install the webcam extra (pynput): "
            "pip install 'wireml[webcam]'"
        ) from exc


def _open_camera(index: int, target_w: int = 1920, target_h: int = 1080):
    import platform

    import cv2

    prefer_dshow = platform.system() == "Windows"
    backends: list[int] = (
        [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY] if prefer_dshow else [cv2.CAP_ANY]
    )

    cap = None
    for backend in backends:
        cap = cv2.VideoCapture(index, backend)
        if cap.isOpened():
            logger.info("opened camera %s via backend %s", index, backend)
            break
        cap.release()
        cap = None

    if cap is None or not cap.isOpened():
        raise RuntimeError(
            f"could not open camera index {index}. "
            "Close other apps using the webcam (Teams, Zoom, OBS) or try --camera 1."
        )

    # MJPG → enables higher resolution @ 30 fps on most UVC cams (YUY2 caps out
    # earlier). Set fourcc *before* requesting resolution.
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, target_w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, target_h)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)

    # Crank driver-level sharpness if the UVC backend exposes it. No-op otherwise.
    import contextlib

    for prop, value in (
        (cv2.CAP_PROP_SHARPNESS, 100),
        (cv2.CAP_PROP_CONTRAST, 140),
        (cv2.CAP_PROP_SATURATION, 128),
    ):
        with contextlib.suppress(Exception):
            cap.set(prop, value)

    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    print(f"camera: {actual_w}x{actual_h} @ {actual_fps:.0f} fps", flush=True)

    for _ in range(5):
        cap.read()
    return cap


def _sharpen_frame(frame, amount: float):
    """Unsharp mask. Cheap & real-time. amount=0 disables, 0.4–0.9 is usable,
    >1.2 looks crunchy. Called once in the grabber so all consumers see the
    same sharpened frame (display, capture, inference all consistent).
    """
    if amount <= 0:
        return frame
    import cv2

    blurred = cv2.GaussianBlur(frame, (0, 0), sigmaX=1.0)
    return cv2.addWeighted(frame, 1 + amount, blurred, -amount, 0)


class _FrameGrabber:
    """Dedicated thread that keeps the latest frame in a 1-slot buffer and
    applies sharpening once. Eliminates cap.read() stalls from the UI loop.
    """

    def __init__(self, cap, sharpen: float = 0.6):
        self._cap = cap
        self._frame = None
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._sharpen = sharpen
        self._thread = threading.Thread(target=self._run, daemon=True, name="grabber")
        self._thread.start()

    def _run(self) -> None:
        while not self._stop.is_set():
            ok, frame = self._cap.read()
            if not ok:
                time.sleep(0.005)
                continue
            if self._sharpen > 0:
                frame = _sharpen_frame(frame, self._sharpen)
            with self._lock:
                self._frame = frame

    def latest(self):
        with self._lock:
            return None if self._frame is None else self._frame.copy()

    @property
    def sharpen(self) -> float:
        return self._sharpen

    def set_sharpen(self, amount: float) -> None:
        self._sharpen = max(0.0, min(amount, 2.0))

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=1.0)


class _InferenceWorker:
    """Runs CLIP on the most recently submitted frame, off-thread."""

    def __init__(self, model: dict):
        self._model = model
        self._latest_frame = None
        self._latest_result: tuple[str, list[tuple[str, float]]] = ("…", [])
        self._lock = threading.Lock()
        self._new_frame = threading.Event()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True, name="inference")
        self._thread.start()

    def submit(self, frame) -> None:
        with self._lock:
            self._latest_frame = frame
        self._new_frame.set()

    def result(self) -> tuple[str, list[tuple[str, float]]]:
        with self._lock:
            return self._latest_result

    def _run(self) -> None:
        while not self._stop.is_set():
            self._new_frame.wait(timeout=0.1)
            self._new_frame.clear()
            with self._lock:
                frame = None if self._latest_frame is None else self._latest_frame.copy()
                self._latest_frame = None
            if frame is None:
                continue
            try:
                feat = _extract_clip_features([frame])[0]
                pred, scores = _predict(self._model, feat)
                with self._lock:
                    self._latest_result = (pred, scores)
            except Exception as exc:
                logger.warning("inference worker error: %s", exc)

    def stop(self) -> None:
        self._stop.set()
        self._new_frame.set()
        self._thread.join(timeout=1.0)


# ═══════════════════════════════════════════════════════════════════════════
#                            KEY LISTENER
# ═══════════════════════════════════════════════════════════════════════════


def _make_key_listener():
    from pynput import keyboard

    held: set = set()

    def _norm(key):
        if hasattr(key, "char") and key.char:
            return key.char.lower()
        return key

    def on_press(key):
        held.add(_norm(key))

    def on_release(key):
        held.discard(_norm(key))

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.daemon = True
    listener.start()

    class _L:
        def held_space(self) -> bool:
            return keyboard.Key.space in held

        def held_key(self, char: str) -> bool:
            return char.lower() in held

        def stop(self) -> None:
            listener.stop()

    return _L()


# ═══════════════════════════════════════════════════════════════════════════
#                            ROI SELECTION
# ═══════════════════════════════════════════════════════════════════════════


def _select_roi(grabber: _FrameGrabber, current: Roi | None = None) -> Roi:
    """Interactive ROI selection. Click-drag to draw, ENTER to confirm,
    SPACE to reset to full frame, ESC to cancel (keeps current).
    """
    import cv2

    ref_frame = None
    while ref_frame is None:
        ref_frame = grabber.latest()
        if ref_frame is None:
            time.sleep(0.01)

    h, w = ref_frame.shape[:2]
    if current is None:
        current = Roi(0, 0, w, h)

    selecting = False
    start_pt = (0, 0)
    end_pt = (0, 0)
    confirmed: list[Roi] = []

    def on_mouse(event, x, y, flags, param):
        nonlocal selecting, start_pt, end_pt
        if event == cv2.EVENT_LBUTTONDOWN:
            selecting = True
            start_pt = (x, y)
            end_pt = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE and selecting:
            end_pt = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            selecting = False
            end_pt = (x, y)
            x0, y0 = min(start_pt[0], end_pt[0]), min(start_pt[1], end_pt[1])
            x1, y1 = max(start_pt[0], end_pt[0]), max(start_pt[1], end_pt[1])
            if x1 - x0 >= 16 and y1 - y0 >= 16:
                confirmed.append(Roi(x0, y0, x1 - x0, y1 - y0))

    cv2.setMouseCallback(WINDOW, on_mouse)
    print("▶ select ROI — click-drag a box · SPACE reset full · ENTER confirm · ESC quit",
          flush=True)

    try:
        while True:
            frame = grabber.latest()
            if frame is None:
                time.sleep(0.005)
                continue
            h, w = frame.shape[:2]

            display = frame.copy()
            _draw_top_bar(display, "SELECT ROI", "--", grabber.sharpen)

            # Active drag rectangle
            if selecting:
                x0, y0 = min(start_pt[0], end_pt[0]), min(start_pt[1], end_pt[1])
                x1, y1 = max(start_pt[0], end_pt[0]), max(start_pt[1], end_pt[1])
                live = Roi(x0, y0, max(x1 - x0, 1), max(y1 - y0, 1))
                _draw_roi(display, live, label="DRAG")
            elif confirmed:
                _draw_roi(display, confirmed[-1], label="ROI")
            elif current is not None and not current.is_full(display):
                _draw_roi(display, current, label="CURRENT")

            # panel
            panel_y = h - 56
            _panel(display, 0, panel_y, w, 56, alpha=0.82)
            _text(display, "SELECT REGION OF INTEREST",
                  (20, panel_y + 22), scale=0.55, color=TEXT, thickness=1)
            _text(
                display,
                "click-drag to crop   [SPACE] use full frame   [ENTER] confirm   [ESC] quit",
                (20, panel_y + 42), scale=0.45, color=MUTED,
            )

            cv2.imshow(WINDOW, display)
            key = cv2.waitKey(1) & 0xFF

            if key == 13:  # ENTER
                if confirmed:
                    chosen = confirmed[-1]
                    print(
                        f"  ✓ ROI {chosen.w}x{chosen.h} at ({chosen.x},{chosen.y})",
                        flush=True,
                    )
                    cv2.setMouseCallback(WINDOW, lambda *_: None)
                    return chosen
                if current is not None:
                    print("  ✓ keeping current ROI", flush=True)
                    cv2.setMouseCallback(WINDOW, lambda *_: None)
                    return current
            if key == ord(" "):
                confirmed.clear()
                print("  · reset to full frame", flush=True)
            if key == 27:  # ESC
                print("  · ESC — keeping current ROI", flush=True)
                cv2.setMouseCallback(WINDOW, lambda *_: None)
                return current or Roi(0, 0, w, h)
    finally:
        cv2.setMouseCallback(WINDOW, lambda *_: None)


# ═══════════════════════════════════════════════════════════════════════════
#                            CLIP MODEL
# ═══════════════════════════════════════════════════════════════════════════


_clip_model = None
_clip_processor = None
_clip_device = None


def _get_clip():
    global _clip_model, _clip_processor, _clip_device
    if _clip_model is not None:
        return _clip_model, _clip_processor, _clip_device

    import torch
    from transformers import CLIPModel, CLIPProcessor

    from wireml.device import detect_device, to_torch_device

    print("▶ loading CLIP ViT-B/32…", flush=True)
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    model.train(False)
    try:
        device = to_torch_device(detect_device())
    except NotImplementedError:
        device = torch.device("cpu")
    model = model.to(device)
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    _clip_model, _clip_processor, _clip_device = model, processor, device

    # Warm-up — first call is slower. Run a dummy once.
    import numpy as np

    dummy = np.zeros((224, 224, 3), dtype=np.uint8)
    _extract_clip_features([dummy])
    print("✓ CLIP ready", flush=True)
    return model, processor, device


def _unwrap_image_features(output):
    import torch

    if torch.is_tensor(output):
        return output
    for attr in ("image_embeds", "pooler_output"):
        value = getattr(output, attr, None)
        if torch.is_tensor(value):
            return value
    last = getattr(output, "last_hidden_state", None)
    if torch.is_tensor(last):
        return last[:, 0]
    raise RuntimeError(f"unexpected CLIP output: {type(output).__name__}")


def _bgr_to_pil(bgr):
    import cv2
    from PIL import Image

    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def _extract_clip_features(images_bgr: list) -> list[list[float]]:
    import torch

    model, processor, device = _get_clip()
    pil_images = [_bgr_to_pil(img) for img in images_bgr]
    batch = processor(images=pil_images, return_tensors="pt").to(device)
    with torch.no_grad():
        output = model.get_image_features(**batch)
    feats = _unwrap_image_features(output)
    feats = feats / feats.norm(dim=-1, keepdim=True)
    return feats.cpu().tolist()


# ═══════════════════════════════════════════════════════════════════════════
#                        TRAINING + PREDICTION
# ═══════════════════════════════════════════════════════════════════════════


def _train_head(features: list[list[float]], labels: list[str]) -> dict:
    from wireml.nodes.heads import run_linear

    return run_linear(
        {"epochs": 200, "learning_rate": 0.05},
        {"features": features, "labels": labels},
    )["model"]


def _softmax(xs):
    import numpy as np

    arr = np.asarray(xs, dtype=np.float32)
    arr = arr - arr.max()
    exp = np.exp(arr)
    return exp / exp.sum()


def _predict(model: dict, features: list[float]) -> tuple[str, list[tuple[str, float]]]:
    import numpy as np

    weights = np.asarray(model["weights"], dtype=np.float32)
    bias = np.asarray(model["bias"], dtype=np.float32)
    classes = model["classes"]
    logits = weights @ np.asarray(features, dtype=np.float32) + bias
    probs = _softmax(logits)
    pairs = sorted(zip(classes, probs.tolist(), strict=True), key=lambda p: -p[1])
    return pairs[0][0], pairs


# ═══════════════════════════════════════════════════════════════════════════
#                            CAPTURE LOOP
# ═══════════════════════════════════════════════════════════════════════════


def _capture_class(
    grabber: _FrameGrabber,
    cap,
    class_name: str,
    listener,
    min_samples: int,
    roi: Roi,
    device_label: str,
    class_index: int,
    total_classes: int,
    session_dir: Path | None,
) -> _Capture:
    """Open-ended capture: hold SPACE to stream, release to stop, N to advance."""
    import cv2

    record = _Capture(class_name=class_name)
    class_dir = None
    if session_dir is not None:
        class_dir = session_dir / class_name.replace("/", "_").replace(" ", "_")
        class_dir.mkdir(parents=True, exist_ok=True)

    max_rate_hz = 15
    min_dt = 1.0 / max_rate_hz
    last_capture = 0.0
    last_n = 0.0
    last_f = 0.0
    last_r = 0.0

    print(f"▶ '{class_name}' — HOLD SPACE to record  ·  N next  ·  F refocus  ·  R redo ROI",
          flush=True)

    while True:
        frame = grabber.latest()
        if frame is None:
            time.sleep(0.005)
            continue
        # Window closed?
        if cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
            break

        is_recording = listener.held_space()
        now = time.monotonic()

        if is_recording and (now - last_capture) >= min_dt:
            crop = roi.apply(frame)
            record.frames.append(crop.copy())
            if class_dir is not None:
                cv2.imwrite(
                    str(class_dir / f"frame_{len(record.frames):04d}.jpg"),
                    crop, [int(cv2.IMWRITE_JPEG_QUALITY), 90],
                )
            last_capture = now

        # draw
        display = frame.copy()
        if not roi.is_full(display):
            _draw_roi(display, roi, label="ROI")
        _draw_capture_hud(
            display, class_name, len(record.frames), is_recording, min_samples,
            device_label, class_index, total_classes, grabber.sharpen,
        )
        cv2.imshow(WINDOW, display)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:
            print(f"  ESC at {len(record.frames)} samples", flush=True)
            break
        if (key in (ord("n"), ord("N")) or listener.held_key("n")) and (now - last_n) > 0.4:
            last_n = now
            if len(record.frames) < min_samples:
                print(
                    f"  !  need {min_samples}+ (have {len(record.frames)})",
                    flush=True,
                )
                continue
            print(
                f"  ✓ '{class_name}' done at {len(record.frames)} samples",
                flush=True,
            )
            break
        if (key in (ord("f"), ord("F")) or listener.held_key("f")) and (now - last_f) > 0.5:
            last_f = now
            cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            print("  ↻ refocused", flush=True)
        if (key in (ord("r"), ord("R")) or listener.held_key("r")) and (now - last_r) > 0.5:
            last_r = now
            return record  # signal: caller should redo ROI
        if key == ord("+") or key == ord("="):
            grabber.set_sharpen(grabber.sharpen + 0.1)
        if key == ord("-") or key == ord("_"):
            grabber.set_sharpen(grabber.sharpen - 0.1)
        if (key in (ord("s"), ord("S")) or listener.held_key("s")) and (now - last_r) > 0.4:
            grabber.set_sharpen(0.0 if grabber.sharpen > 0 else 0.6)

    return record


# ═══════════════════════════════════════════════════════════════════════════
#                            INFERENCE LOOP
# ═══════════════════════════════════════════════════════════════════════════


def _run_inference_loop(grabber: _FrameGrabber, model: dict, roi: Roi, device_label: str) -> bool:
    """Main inference UI. Returns True if user wants to redo ROI."""
    import cv2

    inference = _InferenceWorker(model)
    print("▶ live inference — R: redo ROI · ESC: quit", flush=True)

    last = time.monotonic()
    fps = 0.0
    try:
        while True:
            frame = grabber.latest()
            if frame is None:
                time.sleep(0.003)
                continue
            if cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
                return False

            cropped = roi.apply(frame)
            inference.submit(cropped)
            pred, scores = inference.result()

            now = time.monotonic()
            fps = 0.85 * fps + 0.15 / max(now - last, 1e-6)
            last = now

            display = frame.copy()
            if not roi.is_full(display):
                _draw_roi(display, roi, label="ROI")
            _draw_inference_hud(display, pred, scores, fps, device_label, grabber.sharpen)
            cv2.imshow(WINDOW, display)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                return False
            if key in (ord("r"), ord("R")):
                return True
            if key == ord("+") or key == ord("="):
                grabber.set_sharpen(grabber.sharpen + 0.1)
            if key == ord("-") or key == ord("_"):
                grabber.set_sharpen(grabber.sharpen - 0.1)
            if key in (ord("s"), ord("S")):
                grabber.set_sharpen(0.0 if grabber.sharpen > 0 else 0.6)
    finally:
        inference.stop()


# ═══════════════════════════════════════════════════════════════════════════
#                            TOP-LEVEL RUN
# ═══════════════════════════════════════════════════════════════════════════


def run(
    class_names: list[str],
    min_samples: int = 15,
    camera: int = 0,
    sharpen: float = 0.6,
    width: int = 1920,
    height: int = 1080,
) -> None:
    _lazy_imports()
    import cv2

    _init_fonts()

    if len(class_names) < 2:
        raise ValueError("need at least 2 class names")

    # Silence noisy libraries that would otherwise spam the log.
    for name in ("httpx", "httpcore", "filelock", "huggingface_hub"):
        logging.getLogger(name).setLevel(logging.WARNING)

    cap = _open_camera(camera, target_w=width, target_h=height)
    # The window must exist *before* we call setMouseCallback inside the ROI flow.
    cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW, 1280, 720)  # screen-friendly default; 1080p frames downsample nicely

    grabber = _FrameGrabber(cap, sharpen=sharpen)
    listener = _make_key_listener()
    session_dir = CAPTURE_ROOT / datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    session_dir.mkdir(parents=True, exist_ok=True)
    print(f"session: {session_dir}", flush=True)

    # Device label for HUD
    from wireml.device import detect_device

    device_info = detect_device()
    device_label = f"{device_info.type} · {device_info.name[:20]}"

    try:
        _get_clip()  # warmup + first-run download

        # Phase 1 — ROI selection
        roi = _select_roi(grabber, current=None)

        # Phase 2 — capture
        captures: list[_Capture] = []
        idx = 0
        while idx < len(class_names):
            name = class_names[idx]
            record = _capture_class(
                grabber, cap, name, listener, min_samples, roi, device_label,
                idx, len(class_names), session_dir,
            )
            # if the user pressed R mid-capture, redo ROI and retry THIS class
            if not record.frames:
                raise RuntimeError(f"'{name}' has no samples — aborting")
            captures.append(record)
            idx += 1

        all_frames: list = []
        all_labels: list[str] = []
        for rec in captures:
            all_frames.extend(rec.frames)
            all_labels.extend([rec.class_name] * len(rec.frames))

        print(
            f"▶ extracting features for {len(all_frames)} samples "
            f"across {len(class_names)} classes…", flush=True,
        )
        features: list[list[float]] = []
        chunk = 32
        for i in range(0, len(all_frames), chunk):
            features.extend(_extract_clip_features(all_frames[i : i + chunk]))
            print(
                f"  features {min(i + chunk, len(all_frames))}/{len(all_frames)}",
                flush=True,
            )

        print("▶ training linear head…", flush=True)
        model = _train_head(features, all_labels)
        print("✓ trained: " + ", ".join(f"'{c}'" for c in model["classes"]), flush=True)

        # Phase 3 — live inference (with optional ROI redo)
        while True:
            redo_roi = _run_inference_loop(grabber, model, roi, device_label)
            if not redo_roi:
                break
            roi = _select_roi(grabber, current=roi)
    finally:
        listener.stop()
        grabber.stop()
        cap.release()
        cv2.destroyAllWindows()
