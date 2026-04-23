"""Regression tests for head runners."""
from __future__ import annotations

import numpy as np

from wireml.nodes.evaluation import run_accuracy, run_confusion
from wireml.nodes.heads import run_knn, run_linear


def test_linear_trains_and_evaluates() -> None:
    rng = np.random.default_rng(42)
    class_a = rng.normal(loc=[0, 0], scale=0.1, size=(20, 2)).tolist()
    class_b = rng.normal(loc=[5, 5], scale=0.1, size=(20, 2)).tolist()
    features = class_a + class_b
    labels = ["a"] * 20 + ["b"] * 20

    result = run_linear({"epochs": 200, "learning_rate": 0.05}, {
        "features": features,
        "labels": labels,
    })
    model = result["model"]
    assert model is not None
    assert model["classes"] == ["a", "b"]

    acc = run_accuracy({}, {"model": model, "features": features, "labels": labels})
    assert acc["metrics"]["accuracy"] > 0.95
    assert acc["metrics"]["n"] == 40


def test_knn_confusion_matrix() -> None:
    features = [[0, 0], [0.1, 0.1], [5, 5], [5.1, 5.1]]
    labels = ["a", "a", "b", "b"]
    model_result = run_knn({"k": 1, "metric": "euclidean"}, {
        "features": features,
        "labels": labels,
    })
    conf = run_confusion({}, {
        "model": model_result["model"],
        "features": features,
        "labels": labels,
    })
    matrix = conf["metrics"]["matrix"]
    assert matrix == [[2, 0], [0, 2]]
