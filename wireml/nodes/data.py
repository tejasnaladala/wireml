"""Data-source runners: synthetic features + folder-of-images upload."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np

from wireml.engine import engine

logger = logging.getLogger(__name__)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


@engine.register("data.synthetic")
def run_synthetic(params: dict[str, Any], _inputs: dict[str, Any]) -> dict[str, Any]:
    """Deterministic toy features for smoke tests — no model downloads required."""
    num_per_class = int(params.get("num_per_class", 40))
    num_classes = int(params.get("num_classes", 3))
    feature_dim = int(params.get("feature_dim", 16))
    rng = np.random.default_rng(42)

    # Each class gets a fixed random centroid; samples are centroid + gaussian noise.
    centroids = rng.normal(0, 3, size=(num_classes, feature_dim)).astype(np.float32)
    features: list[list[float]] = []
    labels: list[str] = []
    class_names = [f"class_{chr(ord('a') + i)}" for i in range(num_classes)]

    for idx, name in enumerate(class_names):
        samples = centroids[idx] + rng.normal(0, 0.4, size=(num_per_class, feature_dim))
        features.extend(samples.astype(np.float32).tolist())
        labels.extend([name] * num_per_class)

    return {"features": features, "labels": labels, "classes": class_names}


@engine.register("data.upload")
def run_upload(params: dict[str, Any], _inputs: dict[str, Any]) -> dict[str, Any]:
    """Read a folder-per-class dataset. Each subdirectory becomes a class.

    Returns raw PIL images and string labels — the backbone stage will do
    feature extraction. On folders with no images, raises a clear error.
    """
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Pillow is required for data.upload") from exc

    folder = Path(str(params.get("folder", ""))).expanduser()
    if not folder.is_dir():
        raise RuntimeError(f"{folder!s} is not a directory")

    class_dirs = sorted(p for p in folder.iterdir() if p.is_dir())
    if not class_dirs:
        raise RuntimeError(f"{folder!s} contains no subdirectories — expected one per class")

    images: list[Any] = []
    labels: list[str] = []
    class_names: list[str] = []
    for class_dir in class_dirs:
        class_names.append(class_dir.name)
        for file in sorted(class_dir.iterdir()):
            if file.suffix.lower() not in IMAGE_EXTS:
                continue
            try:
                img = Image.open(file).convert("RGB")
            except Exception as exc:
                logger.warning("skipping unreadable image %s: %s", file, exc)
                continue
            images.append(img)
            labels.append(class_dir.name)

    if not images:
        raise RuntimeError(f"no images found under {folder!s}")

    return {"images": images, "labels": labels, "classes": class_names}
