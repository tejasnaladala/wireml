"""Deploy runners: export a trained head to a portable format.

The linear head is just `logits = features @ Wᵀ + b`, which is a single
Gemm node in ONNX. We build the graph directly with the `onnx` package so
export works without dragging in torch — install with `wireml[deploy]`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from wireml.engine import engine


@engine.register("deploy.export-onnx")
def run_export_onnx(params: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """Serialize a trained linear head to an ONNX file.

    Only the linear head is exportable: it maps to a single Gemm. k-NN keeps
    its training set at inference time and has no fixed-weight graph, so it is
    rejected with a clear message rather than silently producing garbage.
    """
    try:
        import onnx
        from onnx import TensorProto, helper, numpy_helper
    except ImportError as exc:  # pragma: no cover - exercised only without the extra
        raise RuntimeError(
            "ONNX export needs the `onnx` package — "
            "install with `uv tool install 'wireml[deploy]'`"
        ) from exc

    model = inputs.get("model")
    if not isinstance(model, dict):
        raise RuntimeError("deploy.export-onnx requires a trained model on its `model` input")
    if model.get("kind") != "linear":
        raise RuntimeError(
            f"deploy.export-onnx only supports the linear head, got kind={model.get('kind')!r}"
        )

    weights = np.asarray(model["weights"], dtype=np.float32)  # (num_classes, num_features)
    bias = np.asarray(model["bias"], dtype=np.float32)  # (num_classes,)
    classes = list(model.get("classes", []))
    num_classes, num_features = weights.shape

    filename = str(params.get("filename", "wireml-model.onnx"))
    opset = int(params.get("opset", 17))

    # logits = features @ Wᵀ + b  →  Gemm(features, W, b, transB=1)
    inp = helper.make_tensor_value_info("features", TensorProto.FLOAT, [None, num_features])
    out = helper.make_tensor_value_info("logits", TensorProto.FLOAT, [None, num_classes])

    w_init = numpy_helper.from_array(weights, name="W")
    b_init = numpy_helper.from_array(bias, name="b")
    gemm = helper.make_node(
        "Gemm", inputs=["features", "W", "b"], outputs=["logits"], transB=1
    )

    graph = helper.make_graph(
        [gemm], "wireml-linear-head", [inp], [out], initializer=[w_init, b_init]
    )
    # This graph only needs IR v10. Pinning it keeps exports loadable by the
    # oldest onnxruntime release supported by wireml[deploy], even when a newer
    # `onnx` package generated the file.
    onnx_model = helper.make_model(
        graph,
        ir_version=10,
        opset_imports=[helper.make_operatorsetid("", opset)],
    )
    # Record class names so a consumer can map logit index → label.
    if classes:
        meta = onnx_model.metadata_props.add()
        meta.key = "classes"
        meta.value = ",".join(classes)
    onnx.checker.check_model(onnx_model)

    out_path = Path(filename).expanduser()
    onnx.save(onnx_model, str(out_path))

    return {
        "export": {
            "path": str(out_path),
            "format": "onnx",
            "opset": opset,
            "classes": classes,
            "input_dim": int(num_features),
            "num_classes": int(num_classes),
        }
    }
