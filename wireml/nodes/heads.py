"""Classification heads: linear softmax, k-NN."""
from __future__ import annotations

from typing import Any

import numpy as np

from wireml.engine import engine


def _stratified_holdout(
    features: list[list[float]],
    labels: list[str],
    sample_ids: list[str],
    holdout_fraction: float,
    seed: int,
) -> dict[str, Any]:
    """Return deterministic, class-stratified train and evaluation partitions."""
    if len(features) != len(labels) or len(features) != len(sample_ids):
        raise RuntimeError(
            "features, labels, and sample_ids must contain the same number of samples"
        )
    if not 0.0 < holdout_fraction < 1.0:
        raise RuntimeError("holdout_fraction must be between 0 and 1")
    if len(set(sample_ids)) != len(sample_ids):
        raise RuntimeError("sample_ids must be unique before splitting")

    by_class: dict[str, list[int]] = {}
    for index, label in enumerate(labels):
        by_class.setdefault(label, []).append(index)

    too_small = [label for label, indices in by_class.items() if len(indices) < 2]
    if too_small:
        names = ", ".join(sorted(too_small))
        raise RuntimeError(f"each class needs at least two samples for a holdout split: {names}")

    rng = np.random.default_rng(seed)
    train_indices: list[int] = []
    eval_indices: list[int] = []
    for indices in by_class.values():
        shuffled = np.asarray(indices, dtype=np.int64)
        rng.shuffle(shuffled)
        eval_count = min(len(indices) - 1, max(1, round(len(indices) * holdout_fraction)))
        eval_indices.extend(int(index) for index in shuffled[:eval_count])
        train_indices.extend(int(index) for index in shuffled[eval_count:])

    rng.shuffle(train_indices)
    rng.shuffle(eval_indices)

    def select(values: list[Any], indices: list[int]) -> list[Any]:
        return [values[index] for index in indices]

    return {
        "classes": list(dict.fromkeys(labels)),
        "train_features": select(features, train_indices),
        "train_labels": select(labels, train_indices),
        "eval_features": select(features, eval_indices),
        "eval_labels": select(labels, eval_indices),
        "split": {
            "seed": seed,
            "holdout_fraction": holdout_fraction,
            "train_sample_ids": select(sample_ids, train_indices),
            "eval_sample_ids": select(sample_ids, eval_indices),
        },
    }


def _split_inputs(params: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    features = inputs.get("features") or []
    labels = inputs.get("labels") or []
    if not features or not labels:
        raise RuntimeError("classifier head requires features + labels")
    sample_ids = inputs.get("sample_ids") or [f"sample:{i}" for i in range(len(features))]
    return _stratified_holdout(
        features,
        labels,
        sample_ids,
        holdout_fraction=float(params.get("holdout_fraction", 0.2)),
        seed=int(params.get("split_seed", 42)),
    )


@engine.register("head.linear")
def run_linear(params: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    split = _split_inputs(params, inputs)
    features = split["train_features"]
    labels = split["train_labels"]

    features_array = np.asarray(features, dtype=np.float32)
    classes = split["classes"]
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
        },
        "eval_features": split["eval_features"],
        "eval_labels": split["eval_labels"],
        "split": split["split"],
    }


@engine.register("head.knn")
def run_knn(params: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    split = _split_inputs(params, inputs)
    features = split["train_features"]
    labels = split["train_labels"]

    return {
        "model": {
            "kind": "knn",
            "k": int(params.get("k", 5)),
            "metric": params.get("metric", "cosine"),
            "features": features,
            "labels": labels,
            "classes": split["classes"],
        },
        "eval_features": split["eval_features"],
        "eval_labels": split["eval_labels"],
        "split": split["split"],
    }
