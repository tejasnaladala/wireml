"""Regression tests for head runners."""
from __future__ import annotations

import numpy as np
import pytest

from wireml.nodes.deploy import run_export_onnx
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


def test_export_onnx_round_trips(tmp_path) -> None:
    onnx = pytest.importorskip("onnx")
    ort = pytest.importorskip("onnxruntime")

    features = [[0.0, 0.0], [0.1, 0.0], [5.0, 5.0], [5.1, 5.0]]
    labels = ["a", "a", "b", "b"]
    model = run_linear({"epochs": 200, "learning_rate": 0.1}, {
        "features": features,
        "labels": labels,
    })["model"]

    out_file = tmp_path / "head.onnx"
    result = run_export_onnx({"filename": str(out_file)}, {"model": model})
    assert out_file.exists()
    assert result["export"]["num_classes"] == 2
    assert result["export"]["classes"] == ["a", "b"]

    # The exported graph must reproduce the numpy head's argmax predictions.
    loaded = onnx.load(str(out_file))
    onnx.checker.check_model(loaded)
    session = ort.InferenceSession(str(out_file))
    logits = session.run(None, {"features": np.asarray(features, dtype=np.float32)})[0]
    onnx_preds = logits.argmax(axis=1).tolist()

    weights = np.asarray(model["weights"], dtype=np.float32)
    bias = np.asarray(model["bias"], dtype=np.float32)
    numpy_preds = (np.asarray(features, dtype=np.float32) @ weights.T + bias).argmax(axis=1).tolist()
    assert onnx_preds == numpy_preds


def test_export_onnx_rejects_knn() -> None:
    pytest.importorskip("onnx")
    model = run_knn({}, {"features": [[0.0, 0.0]], "labels": ["a"]})["model"]
    with pytest.raises(RuntimeError, match="only supports the linear head"):
        run_export_onnx({}, {"model": model})
