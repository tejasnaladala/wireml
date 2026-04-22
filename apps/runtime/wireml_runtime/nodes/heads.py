"""Trainable head runners: linear softmax, k-NN, zero-shot CLIP."""
from __future__ import annotations

from typing import Any

import numpy as np

from . import register


@register("head.linear")
def run_linear(node: Any, inputs: dict[str, Any]) -> dict[str, Any]:
    features = inputs.get("features") or []
    labels = inputs.get("labels") or []
    if not features or not labels:
        return {"model": None}

    X = np.array(features, dtype=np.float32)
    classes = list(dict.fromkeys(labels))
    label_to_idx = {c: i for i, c in enumerate(classes)}
    y = np.array([label_to_idx[label] for label in labels], dtype=np.int64)

    epochs = int(node.params.get("epochs", 50))
    lr = float(node.params.get("learningRate", 0.001))

    num_classes = len(classes)
    num_features = X.shape[1]
    W = np.random.randn(num_classes, num_features).astype(np.float32) * 0.01
    b = np.zeros(num_classes, dtype=np.float32)

    for _ in range(epochs):
        logits = X @ W.T + b
        logits -= logits.max(axis=1, keepdims=True)
        exps = np.exp(logits)
        probs = exps / exps.sum(axis=1, keepdims=True)
        onehot = np.zeros_like(probs)
        onehot[np.arange(len(y)), y] = 1
        grad = (probs - onehot) / len(y)
        W -= lr * grad.T @ X
        b -= lr * grad.sum(axis=0)

    return {
        "model": {
            "kind": "linear",
            "classes": classes,
            "weights": W.tolist(),
            "bias": b.tolist(),
        }
    }


@register("head.knn")
def run_knn(node: Any, inputs: dict[str, Any]) -> dict[str, Any]:
    features = inputs.get("features") or []
    labels = inputs.get("labels") or []
    if not features or not labels:
        return {"model": None}

    return {
        "model": {
            "kind": "knn",
            "k": int(node.params.get("k", 5)),
            "metric": node.params.get("metric", "cosine"),
            "features": features,
            "labels": labels,
            "classes": list(dict.fromkeys(labels)),
        }
    }


@register("head.zeroshot-clip")
def run_zeroshot_clip(node: Any, inputs: dict[str, Any]) -> dict[str, Any]:
    img_feats = inputs.get("imageFeatures") or []
    txt_feats = inputs.get("textFeatures") or []
    if not txt_feats:
        return {"model": None}

    return {
        "model": {
            "kind": "zero-shot-clip",
            "textFeatures": txt_feats,
            "imageFeatures": img_feats,
            "temperature": float(node.params.get("temperature", 100)),
        }
    }
