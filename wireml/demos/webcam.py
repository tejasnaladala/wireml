"""Webcam-based Teachable-Machine-style demo.

Flow:
  1. Open the default webcam.
  2. For each class name, show a live preview with on-screen instructions.
     Press SPACE to capture a sample; captures stop automatically at the
     configured count. ESC cancels.
  3. Extract CLIP ViT-B/32 features for every captured sample.
  4. Train a linear softmax head (uses the existing wireml.nodes.heads runner).
  5. Open a live inference window showing the predicted class + confidence.
     Press ESC to quit.

Requires the `ml` and `webcam` extras:
    uv tool install "git+https://github.com/tejasnaladala/wireml" --with "wireml[ml,webcam]"
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

WINDOW = "WireML — webcam trainer"


@dataclass
class _Capture:
    class_name: str
    frames: list = field(default_factory=list)


def _lazy_imports():
    """Import heavy deps lazily so the module is importable without extras."""
    try:
        import cv2  # noqa: F401
        import numpy as np  # noqa: F401
        from PIL import Image  # noqa: F401
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "The webcam demo needs the `webcam` extra. Install with:\n"
            "  uv tool install 'git+https://github.com/tejasnaladala/wireml' "
            "--with 'wireml[ml,webcam]'"
        ) from exc
    try:
        import torch  # noqa: F401
        from transformers import AutoModel, AutoProcessor  # noqa: F401
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "The webcam demo needs the `ml` extra (torch + transformers). Install with:\n"
            "  uv tool install 'git+https://github.com/tejasnaladala/wireml' "
            "--with 'wireml[ml,webcam]'"
        ) from exc


def _open_camera(index: int):
    import cv2

    cap = cv2.VideoCapture(index, cv2.CAP_ANY)
    if not cap.isOpened():
        raise RuntimeError(
            f"could not open camera index {index}. Try a different index with --camera N."
        )
    # Most webcams default to 640x480 which is plenty for classification.
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return cap


def _draw_capture_hud(
    frame,
    class_name: str,
    captured: int,
    target: int,
    auto_capturing: bool,
    remaining_ms: int | None,
) -> None:
    import cv2

    h, w = frame.shape[:2]
    # dim strip at bottom
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, h - 110), (w, h), (10, 14, 20), -1)
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)

    cv2.putText(
        frame,
        f"CLASS  {class_name}",
        (16, h - 78),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (229, 236, 244),
        2,
        cv2.LINE_AA,
    )
    bar_x, bar_y, bar_w = 16, h - 55, 260
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + 10), (42, 50, 64), -1)
    filled = int(bar_w * (captured / max(target, 1)))
    cv2.rectangle(
        frame, (bar_x, bar_y), (bar_x + filled, bar_y + 10), (139, 92, 246), -1
    )
    cv2.putText(
        frame,
        f"{captured}/{target} samples",
        (bar_x, bar_y + 32),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (108, 122, 140),
        1,
        cv2.LINE_AA,
    )

    hint_y = h - 20
    if auto_capturing and remaining_ms is not None:
        hint = f"AUTO  capturing in {remaining_ms // 1000}.{(remaining_ms // 100) % 10}s   ESC to stop"
        colour = (16, 185, 129)
    else:
        hint = "SPACE: capture one    A: auto-capture    N: next class    ESC: cancel"
        colour = (108, 122, 140)
    cv2.putText(frame, hint, (w - 760, hint_y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, colour, 1, cv2.LINE_AA)


def _capture_class(cap, class_name: str, target: int) -> _Capture:
    """Record samples for one class. Returns when target frames captured or ESC pressed."""
    import cv2

    record = _Capture(class_name=class_name)
    auto_mode = False
    auto_every_ms = 200  # rate while auto-capturing
    next_auto_at = 0.0

    print(f"▶ capturing '{class_name}' — SPACE: one frame · A: auto · N: next · ESC: stop")
    while True:
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError("failed to read from camera")

        now_ms = time.monotonic() * 1000.0
        remaining = int(next_auto_at - now_ms) if auto_mode else None
        _draw_capture_hud(frame, class_name, len(record.frames), target, auto_mode, remaining)
        cv2.imshow(WINDOW, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            print(f"  stopped manually at {len(record.frames)} samples")
            break
        if key in (ord("a"), ord("A")):
            auto_mode = not auto_mode
            next_auto_at = now_ms + auto_every_ms
            print(f"  auto-capture {'on' if auto_mode else 'off'}")
        if key in (ord("n"), ord("N")):
            print(f"  advanced to next class at {len(record.frames)} samples")
            break
        if key == ord(" ") or (auto_mode and now_ms >= next_auto_at):
            record.frames.append(frame.copy())
            print(f"  ✓ captured {len(record.frames)}/{target}")
            next_auto_at = now_ms + auto_every_ms
            if len(record.frames) >= target:
                print(f"  ✓ reached target {target}, advancing")
                break

    return record


def _bgr_to_pil(bgr):
    import cv2
    from PIL import Image

    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def _extract_clip_features(images_bgr: list) -> list[list[float]]:
    """Run CLIP ViT-B/32 over a list of BGR frames. Uses auto-detected device."""
    import torch
    from transformers import AutoModel, AutoProcessor

    from wireml.device import detect_device, to_torch_device

    logger.info("loading CLIP ViT-B/32 (first run downloads ~335MB)")
    model = AutoModel.from_pretrained("openai/clip-vit-base-patch32")
    model.train(False)
    try:
        device = to_torch_device(detect_device())
    except NotImplementedError:
        device = torch.device("cpu")
    model = model.to(device)
    processor = AutoProcessor.from_pretrained("openai/clip-vit-base-patch32")

    pil_images = [_bgr_to_pil(img) for img in images_bgr]
    batch = processor(images=pil_images, return_tensors="pt").to(device)

    with torch.no_grad():
        feats = model.get_image_features(**batch)
    feats = feats / feats.norm(dim=-1, keepdim=True)
    return feats.cpu().tolist()


def _train_head(features: list[list[float]], labels: list[str]) -> dict:
    from wireml.nodes.heads import run_linear

    return run_linear(
        {"epochs": 150, "learning_rate": 0.05},
        {"features": features, "labels": labels},
    )["model"]


def _softmax(xs):
    import numpy as np

    arr = np.asarray(xs, dtype=np.float32)
    arr = arr - arr.max()
    exp = np.exp(arr)
    return exp / exp.sum()


def _predict(model, features: list[float]) -> tuple[str, list[tuple[str, float]]]:
    import numpy as np

    weights = np.asarray(model["weights"], dtype=np.float32)
    bias = np.asarray(model["bias"], dtype=np.float32)
    classes = model["classes"]
    logits = weights @ np.asarray(features, dtype=np.float32) + bias
    probs = _softmax(logits)
    pairs = sorted(zip(classes, probs.tolist(), strict=True), key=lambda p: -p[1])
    return pairs[0][0], pairs


def _draw_inference_hud(frame, label: str, scores: list[tuple[str, float]], fps: float) -> None:
    import cv2

    h, w = frame.shape[:2]
    overlay = frame.copy()
    panel_h = 28 + 26 * len(scores) + 36
    cv2.rectangle(overlay, (0, 0), (w, panel_h), (10, 14, 20), -1)
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)

    cv2.putText(
        frame,
        label.upper(),
        (16, 36),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (139, 92, 246),
        3,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        f"{fps:5.1f} fps",
        (w - 120, 36),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (108, 122, 140),
        1,
        cv2.LINE_AA,
    )

    y = 68
    for cls, score in scores:
        label_str = f"{cls:<16}  {score * 100:5.1f}%"
        cv2.putText(
            frame,
            label_str,
            (16, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (229, 236, 244),
            1,
            cv2.LINE_AA,
        )
        # bar
        bar_x = 260
        bar_w = int(280 * score)
        cv2.rectangle(frame, (bar_x, y - 12), (bar_x + 280, y - 4), (42, 50, 64), -1)
        cv2.rectangle(frame, (bar_x, y - 12), (bar_x + bar_w, y - 4), (139, 92, 246), -1)
        y += 26

    cv2.putText(
        frame,
        "ESC: quit",
        (16, y + 8),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (108, 122, 140),
        1,
        cv2.LINE_AA,
    )


def _run_inference_loop(cap, model) -> None:
    import cv2

    print("▶ live inference — ESC to quit")
    last = time.monotonic()
    fps = 0.0
    # Re-extract CLIP features on every Nth frame (expensive on CPU).
    every = 3
    step = 0
    prediction_label = "…"
    prediction_scores: list[tuple[str, float]] = []

    while True:
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError("failed to read from camera")
        step += 1
        if step % every == 0:
            try:
                feat = _extract_clip_features([frame])[0]
                prediction_label, prediction_scores = _predict(model, feat)
            except Exception as exc:  # pragma: no cover
                logger.warning("inference failed: %s", exc)

        now = time.monotonic()
        fps = 0.8 * fps + 0.2 / max(now - last, 1e-6)
        last = now

        _draw_inference_hud(frame, prediction_label, prediction_scores, fps)
        cv2.imshow(WINDOW, frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break


def run(
    class_names: list[str],
    samples_per_class: int = 30,
    camera: int = 0,
) -> None:
    """End-to-end flow: capture, train, and run live inference."""
    _lazy_imports()
    import cv2

    if len(class_names) < 2:
        raise ValueError("need at least 2 class names")

    cap = _open_camera(camera)
    try:
        captures: list[_Capture] = []
        for name in class_names:
            record = _capture_class(cap, name, samples_per_class)
            if not record.frames:
                raise RuntimeError(f"class '{name}' has no samples — aborting")
            captures.append(record)

        all_frames: list = []
        all_labels: list[str] = []
        for rec in captures:
            all_frames.extend(rec.frames)
            all_labels.extend([rec.class_name] * len(rec.frames))

        print(
            "\n▶ extracting CLIP features for "
            f"{len(all_frames)} samples across {len(class_names)} classes…"
        )
        features = _extract_clip_features(all_frames)
        print("▶ training linear head…")
        model = _train_head(features, all_labels)
        print(
            "✓ trained model with classes "
            + ", ".join(f"'{c}'" for c in model["classes"])
        )

        _run_inference_loop(cap, model)
    finally:
        cap.release()
        cv2.destroyAllWindows()
