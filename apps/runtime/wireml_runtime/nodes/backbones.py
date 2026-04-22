"""Image / text / audio backbone runners. Lazy-loads models and caches them
for the lifetime of the process. Models are automatically moved onto the
detected device (CUDA / MPS / MLX / CPU).
"""
from __future__ import annotations

import base64
import io
from typing import Any

import numpy as np
from PIL import Image

from ..device import detect_device, to_torch_device
from . import register

_model_cache: dict[str, Any] = {}
_processor_cache: dict[str, Any] = {}


def _decode_image(payload: Any) -> Image.Image:
    """Accept base64 data URLs, base64 strings, or raw numpy arrays."""
    if isinstance(payload, str):
        if payload.startswith("data:"):
            payload = payload.split(",", 1)[1]
        return Image.open(io.BytesIO(base64.b64decode(payload))).convert("RGB")
    if isinstance(payload, list):
        arr = np.array(payload, dtype=np.uint8)
        return Image.fromarray(arr)
    if isinstance(payload, dict) and payload.get("__blob"):
        raise ValueError("Blob payloads should be sent as base64 data URLs")
    raise TypeError(f"Unsupported image payload type: {type(payload).__name__}")


def _load_clip_image():
    if "clip_image" in _model_cache:
        return _model_cache["clip_image"], _processor_cache["clip_image"]
    from transformers import AutoModel, AutoProcessor

    model_id = "openai/clip-vit-base-patch32"
    device_info = detect_device()
    model = AutoModel.from_pretrained(model_id)
    model.train(False)
    model = model.to(to_torch_device(device_info))
    processor = AutoProcessor.from_pretrained(model_id)
    _model_cache["clip_image"] = model
    _processor_cache["clip_image"] = processor
    return model, processor


def _load_clip_l_image():
    if "clip_l_image" in _model_cache:
        return _model_cache["clip_l_image"], _processor_cache["clip_l_image"]
    from transformers import AutoModel, AutoProcessor

    model_id = "openai/clip-vit-large-patch14"
    device_info = detect_device()
    model = AutoModel.from_pretrained(model_id)
    model.train(False)
    model = model.to(to_torch_device(device_info))
    processor = AutoProcessor.from_pretrained(model_id)
    _model_cache["clip_l_image"] = model
    _processor_cache["clip_l_image"] = processor
    return model, processor


@register("backbone.clip.vit-b-32")
def run_clip_b32(node: Any, inputs: dict[str, Any]) -> dict[str, Any]:
    import torch

    images_in = inputs.get("images") or inputs.get("frames") or []
    if not images_in:
        return {"features": []}

    model, processor = _load_clip_image()
    pil_images = [_decode_image(x) for x in images_in]
    batch = processor(images=pil_images, return_tensors="pt").to(model.device)

    with torch.no_grad():
        feats = model.get_image_features(**batch)
    if node.params.get("normalize", True):
        feats = feats / feats.norm(dim=-1, keepdim=True)
    return {"features": feats.cpu().tolist()}


@register("backbone.clip.vit-l-14")
def run_clip_l14(node: Any, inputs: dict[str, Any]) -> dict[str, Any]:
    import torch

    images_in = inputs.get("images") or inputs.get("frames") or []
    if not images_in:
        return {"features": []}

    model, processor = _load_clip_l_image()
    pil_images = [_decode_image(x) for x in images_in]
    batch = processor(images=pil_images, return_tensors="pt").to(model.device)

    with torch.no_grad():
        feats = model.get_image_features(**batch)
    if node.params.get("normalize", True):
        feats = feats / feats.norm(dim=-1, keepdim=True)
    return {"features": feats.cpu().tolist()}


@register("backbone.clip.text-vit-b-32")
def run_clip_text(node: Any, inputs: dict[str, Any]) -> dict[str, Any]:
    import torch

    text_in = inputs.get("text") or []
    if not text_in:
        return {"features": []}

    model, processor = _load_clip_image()
    batch = processor(text=list(text_in), return_tensors="pt", padding=True).to(model.device)

    with torch.no_grad():
        feats = model.get_text_features(**batch)
    if node.params.get("normalize", True):
        feats = feats / feats.norm(dim=-1, keepdim=True)
    return {"features": feats.cpu().tolist()}


@register("backbone.dinov2.small")
def run_dinov2_s(_node: Any, inputs: dict[str, Any]) -> dict[str, Any]:
    import torch
    from transformers import AutoImageProcessor, AutoModel

    images_in = inputs.get("images") or inputs.get("frames") or []
    if not images_in:
        return {"features": []}

    if "dinov2_s" not in _model_cache:
        model_id = "facebook/dinov2-small"
        device_info = detect_device()
        model = AutoModel.from_pretrained(model_id)
        model.train(False)
        model = model.to(to_torch_device(device_info))
        processor = AutoImageProcessor.from_pretrained(model_id)
        _model_cache["dinov2_s"] = model
        _processor_cache["dinov2_s"] = processor

    model = _model_cache["dinov2_s"]
    processor = _processor_cache["dinov2_s"]
    pil_images = [_decode_image(x) for x in images_in]
    batch = processor(images=pil_images, return_tensors="pt").to(model.device)

    with torch.no_grad():
        out = model(**batch)
    feats = out.last_hidden_state[:, 0]
    return {"features": feats.cpu().tolist()}
