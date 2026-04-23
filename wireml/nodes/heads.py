"""Classification heads: linear softmax, k-NN."""
from __future__ import annotations

from typing import Any

import numpy as np

from wireml.engine import engine


@engine.register("head.linear")
def run_linear(params: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    features = inputs.get("features") or []
    labels = inputs.get("labels") or []
    if not features or not labels:
        raise RuntimeError("head.linear requires features + labels")
    if len(features) != len(labels):
        raise RuntimeError(
            f"features/labels length mismatch: {len(features)} vs {len(labels)}"
        )

    features_array = np.asarray(features, dtype=np.float32)
    classes = list(dict.fromkeys(labels))
    label_to_idx = {name: i for i, name in enumerate(classes)}
    y = np.asarray([label_to_idx[lbl] for lbl in labels], dtype=np.int64)

    epochs = int(params.get("epochs", 50))
    learning_rate = float(params.get("learning_rate", 0.01))

    num_classes = len(classes)
    num_features = features_array.shape[1]
    rng = np.random.default_rng(0)
    weights = rng.standard_normal((num_classes, num_features)).astype(np.float32) * 0.01
    bias = np.zeros(num_classes, dtype=np.float32)

    for _ in range(epochs):
        logits = features_array @ weights.T + bias
        logits -= logits.max(axis=1, keepdims=True)
        exps = np.exp(logits)
        probs = exps / exps.sum(axis=1, keepdims=True)
        onehot = np.zeros_like(probs)
        onehot[np.arange(len(y)), y] = 1
        grad = (probs - onehot) / len(y)
        weights -= learning_rate * grad.T @ features_array
        bias -= learning_rate * grad.sum(axis=0)

    return {
        "model": {
            "kind": "linear",
            "classes": classes,
            "weights": weights.tolist(),
            "bias": bias.tolist(),
        }
    }


@engine.register("head.knn")
def run_knn(params: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    features = inputs.get("features") or []
    labels = inputs.get("labels") or []
    if not features or not labels:
        raise RuntimeError("head.knn requires features + labels")

    return {
        "model": {
            "kind": "knn",
            "k": int(params.get("k", 5)),
            "metric": params.get("metric", "cosine"),
            "features": features,
            "labels": labels,
            "classes": list(dict.fromkeys(labels)),
        }
    }
