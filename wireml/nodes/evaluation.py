"""Evaluation runners: accuracy + confusion matrix.

Audit M5 fix: both now use the exact same "predict → compare by index"
contract, and unknown labels are surfaced via an explicit `unknown_labels`
count instead of being silently skipped.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from wireml.engine import engine


def _predict(model: dict[str, Any], features: list[list[float]]) -> list[int]:
    kind = model.get("kind")
    features_array = np.asarray(features, dtype=np.float32)

    if kind == "linear":
        weights = np.asarray(model["weights"], dtype=np.float32)
        bias = np.asarray(model["bias"], dtype=np.float32)
        logits = features_array @ weights.T + bias
        return logits.argmax(axis=1).tolist()

    if kind == "knn":
        train = np.asarray(model["features"], dtype=np.float32)
        labels = model["labels"]
        classes = model["classes"]
        k = int(model.get("k", 5))
        metric = model.get("metric", "cosine")

        if metric == "cosine":
            xn = features_array / (np.linalg.norm(features_array, axis=1, keepdims=True) + 1e-9)
            tn = train / (np.linalg.norm(train, axis=1, keepdims=True) + 1e-9)
            sim = xn @ tn.T
            neighbors = np.argsort(-sim, axis=1)[:, :k]
        else:
            dists = np.linalg.norm(features_array[:, None, :] - train[None, :, :], axis=-1)
            neighbors = np.argsort(dists, axis=1)[:, :k]

        class_to_idx = {name: i for i, name in enumerate(classes)}
        preds: list[int] = []
        for row in neighbors:
            counts: dict[int, int] = {}
            for j in row:
                counts[class_to_idx[labels[int(j)]]] = (
                    counts.get(class_to_idx[labels[int(j)]], 0) + 1
                )
            preds.append(max(counts, key=counts.get))  # type: ignore[arg-type]
        return preds

    raise ValueError(f"unknown model kind: {kind!r}")


@engine.register("eval.accuracy")
def run_accuracy(_params: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    model = inputs.get("model")
    features = inputs.get("features") or []
    labels = inputs.get("labels") or []
    if model is None or not features or len(features) != len(labels):
        return {"metrics": {"accuracy": 0.0, "n": 0}}

    classes: list[str] = model.get("classes") or list(dict.fromkeys(labels))
    preds = _predict(model, features)
    known = [(p, lbl) for p, lbl in zip(preds, labels, strict=True) if lbl in classes]
    unknown = len(labels) - len(known)
    correct = sum(1 for p, lbl in known if classes[p] == lbl)
    return {
        "metrics": {
            "accuracy": correct / len(known) if known else 0.0,
            "n": len(known),
            "unknown_labels": unknown,
        }
    }


@engine.register("eval.confusion")
def run_confusion(_params: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    model = inputs.get("model")
    features = inputs.get("features") or []
    labels = inputs.get("labels") or []
    if model is None or not features or len(features) != len(labels):
        return {"metrics": {"matrix": [], "classes": []}}

    classes: list[str] = model.get("classes") or list(dict.fromkeys(labels))
    preds = _predict(model, features)
    n = len(classes)
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    class_to_idx = {name: i for i, name in enumerate(classes)}
    unknown = 0
    for p, lbl in zip(preds, labels, strict=True):
        if lbl in class_to_idx:
            matrix[class_to_idx[lbl]][p] += 1
        else:
            unknown += 1
    return {"metrics": {"matrix": matrix, "classes": classes, "unknown_labels": unknown}}
