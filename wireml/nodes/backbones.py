"""Image backbone runners (CLIP-B/32, CLIP-L/14, DINOv2-S, identity).

Runs on the detected device. Models are lazy-loaded under a lock so
concurrent stages don't race (audit H7). Torch/transformers are optional:
installing `wireml[ml]` pulls them in; without them the identity runner
is the only backbone that works.
"""
from __future__ import annotations

import logging
import threading
from typing import Any

from wireml.device import detect_device, to_torch_device
from wireml.engine import engine

logger = logging.getLogger(__name__)

_model_cache: dict[str, Any] = {}
_processor_cache: dict[str, Any] = {}
_cache_lock = threading.Lock()


def _load_model(cache_key: str, model_id: str, processor_cls: str = "AutoProcessor") -> tuple:
    """Load and cache a transformers model + processor pair with device placement."""
    with _cache_lock:
        if cache_key in _model_cache:
            return _model_cache[cache_key], _processor_cache[cache_key]

        try:
            from transformers import AutoImageProcessor, AutoModel, AutoProcessor
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "Install `wireml[ml]` to use CLIP / DINOv2 backbones"
            ) from exc

        device_info = detect_device()
        try:
            torch_device = to_torch_device(device_info)
        except NotImplementedError:
            logger.warning(
                "device %s has no torch mapping; running backbone on CPU", device_info.type
            )
            import torch

            torch_device = torch.device("cpu")

        logger.info("loading %s on %s", model_id, torch_device)
        model = AutoModel.from_pretrained(model_id)
        model.train(False)
        model = model.to(torch_device)
        proc_loader = AutoImageProcessor if processor_cls == "AutoImageProcessor" else AutoProcessor
        processor = proc_loader.from_pretrained(model_id)
        _model_cache[cache_key] = model
        _processor_cache[cache_key] = processor
        return model, processor


def _extract_clip_features(model_id: str, cache_key: str, images: list, normalize: bool) -> list:
    import torch

    model, processor = _load_model(cache_key, model_id)
    batch = processor(images=images, return_tensors="pt").to(model.device)
    with torch.no_grad():
        feats = model.get_image_features(**batch)
    if normalize:
        feats = feats / feats.norm(dim=-1, keepdim=True)
    # Audit C2 fix: explicitly return one vector per image (the model already does this,
    # but .tolist() on the 2D tensor gives a list-of-lists which is what we want).
    return feats.cpu().tolist()


@engine.register("backbone.identity")
def run_identity(_params: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """Pass features straight through. Used for synthetic-data pipelines."""
    return {"features": inputs.get("features") or []}


@engine.register("backbone.clip.vit-b-32")
def run_clip_b32(params: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    images = inputs.get("images") or []
    if not images:
        return {"features": []}
    normalize = bool(params.get("normalize", True))
    features = _extract_clip_features(
        "openai/clip-vit-base-patch32", "clip_b32", images, normalize
    )
    return {"features": features}


@engine.register("backbone.clip.vit-l-14")
def run_clip_l14(params: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    images = inputs.get("images") or []
    if not images:
        return {"features": []}
    normalize = bool(params.get("normalize", True))
    features = _extract_clip_features(
        "openai/clip-vit-large-patch14", "clip_l14", images, normalize
    )
    return {"features": features}


@engine.register("backbone.dinov2.small")
def run_dinov2_s(_params: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    import torch

    images = inputs.get("images") or []
    if not images:
        return {"features": []}

    model, processor = _load_model("dinov2_s", "facebook/dinov2-small", "AutoImageProcessor")
    batch = processor(images=images, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model(**batch)
    feats = out.last_hidden_state[:, 0]
    return {"features": feats.cpu().tolist()}
