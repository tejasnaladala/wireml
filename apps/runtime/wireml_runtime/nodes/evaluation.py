"""Evaluation runners: accuracy and confusion matrix."""
from __future__ import annotations

from typing import Any

import numpy as np

from . import register


def _predict_with_model(model: dict[str, Any], features: list[list[float]]) -> list[int]:
    kind = model.get("kind")
    X = np.array(features, dtype=np.float32)

    if kind == "linear":
        W = np.array(model["weights"], dtype=np.float32)
        b = np.array(model["bias"], dtype=np.float32)
        logits = X @ W.T + b
        return logits.argmax(axis=1).tolist()

    if kind == "knn":
        train = np.array(model["features"], dtype=np.float32)
        labels = model["labels"]
        classes = model["classes"]
        k = int(model.get("k", 5))
        metric = model.get("metric", "cosine")

        if metric == "cosine":
            Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
            Tn = train / (np.linalg.norm(train, axis=1, keepdims=True) + 1e-9)
            sim = Xn @ Tn.T
            neighbors = np.argsort(-sim, axis=1)[:, :k]
        else:
            dists = np.linalg.norm(X[:, None, :] - train[None, :, :], axis=-1)
            neighbors = np.argsort(dists, axis=1)[:, :k]

        preds: list[int] = []
        class_to_idx = {c: i for i, c in enumerate(classes)}
        for row in neighbors:
            counts: dict[int, int] = {}
            for j in row:
                lbl = labels[int(j)]
                cls = class_to_idx[lbl]
                counts[cls] = counts.get(cls, 0) + 1
            preds.append(max(counts.items(), key=lambda kv: kv[1])[0])
        return preds

    if kind == "zero-shot-clip":
        T = np.array(model["textFeatures"], dtype=np.float32)
        temp = float(model.get("temperature", 100))
        logits = X @ T.T * temp
        return logits.argmax(axis=1).tolist()

    raise ValueError(f"Unknown model kind: {kind}")


@register("eval.accuracy")
def run_accuracy(_node: Any, inputs: dict[str, Any]) -> dict[str, Any]:
    model = inputs.get("model")
    features = inputs.get("features") or []
    labels = inputs.get("labels") or []
    if model is None or not features or len(features) != len(labels):
        return {"metrics": {"accuracy": 0, "n": 0}}

    classes = model.get("classes") or list(dict.fromkeys(labels))
    preds = _predict_with_model(model, features)
    correct = sum(1 for p, lbl in zip(preds, labels) if classes[p] == lbl)
    return {"metrics": {"accuracy": correct / len(features), "n": len(features)}}


@register("eval.confusion")
def run_confusion(_node: Any, inputs: dict[str, Any]) -> dict[str, Any]:
    model = inputs.get("model")
    features = inputs.get("features") or []
    labels = inputs.get("labels") or []
    if model is None or not features or len(features) != len(labels):
        return {"metrics": {"matrix": [], "classes": []}}

    classes = model.get("classes") or list(dict.fromkeys(labels))
    preds = _predict_with_model(model, features)
    n = len(classes)
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    class_to_idx = {c: i for i, c in enumerate(classes)}
    for p, lbl in zip(preds, labels):
        if lbl in class_to_idx:
            matrix[class_to_idx[lbl]][p] += 1
    return {"metrics": {"matrix": matrix, "classes": classes}}
