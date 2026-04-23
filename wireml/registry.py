"""Node catalog. Every stage the TUI can execute comes from here."""
from __future__ import annotations

from wireml.schema import Capability, NodeSchema, ParamSpec, Port

NODE_SCHEMAS: tuple[NodeSchema, ...] = (
    # ───────── DATA ─────────
    NodeSchema(
        id="data.upload",
        name="Upload images",
        category="data",
        description="Folder-per-class dataset. One subfolder per class name.",
        outputs=(Port("images", "image", array=True), Port("labels", "labels", array=True)),
        params=(
            ParamSpec(
                "folder",
                "file",
                default="",
                description="Path to a folder containing one subfolder per class",
            ),
        ),
        execution_mode="triggered",
    ),
    NodeSchema(
        id="data.synthetic",
        name="Synthetic demo data",
        category="data",
        description="Built-in toy features + labels for smoke-testing the pipeline.",
        outputs=(Port("features", "features", array=True), Port("labels", "labels", array=True)),
        params=(
            ParamSpec("num_per_class", "number", default=40, min=4, max=500),
            ParamSpec("num_classes", "number", default=3, min=2, max=10),
            ParamSpec("feature_dim", "number", default=16, min=2, max=512),
        ),
        execution_mode="triggered",
    ),
    # ───────── BACKBONE ─────────
    NodeSchema(
        id="backbone.clip.vit-b-32",
        name="CLIP ViT-B/32",
        category="backbone",
        description="OpenAI CLIP base. 512-dim image features.",
        inputs=(Port("images", "image", array=True),),
        outputs=(Port("features", "features", array=True),),
        params=(ParamSpec("normalize", "boolean", default=True),),
        capability=Capability(download_mb=335),
        execution_mode="triggered",
    ),
    NodeSchema(
        id="backbone.clip.vit-l-14",
        name="CLIP ViT-L/14",
        category="backbone",
        description="Larger CLIP. 768-dim features, higher accuracy.",
        inputs=(Port("images", "image", array=True),),
        outputs=(Port("features", "features", array=True),),
        params=(ParamSpec("normalize", "boolean", default=True),),
        capability=Capability(min_vram_gb=6, download_mb=1700),
        execution_mode="triggered",
    ),
    NodeSchema(
        id="backbone.dinov2.small",
        name="DINOv2 ViT-S/14",
        category="backbone",
        description="Meta DINOv2. 384-dim self-supervised image features.",
        inputs=(Port("images", "image", array=True),),
        outputs=(Port("features", "features", array=True),),
        capability=Capability(download_mb=88),
        execution_mode="triggered",
    ),
    NodeSchema(
        id="backbone.identity",
        name="Identity (pass-through)",
        category="backbone",
        description="No feature extraction — use when upstream already provides features.",
        inputs=(Port("features", "features", array=True),),
        outputs=(Port("features", "features", array=True),),
        execution_mode="reactive",
    ),
    # ───────── HEAD ─────────
    NodeSchema(
        id="head.linear",
        name="Linear classifier",
        category="head",
        description="Trainable linear softmax. Fast, works with modest data.",
        inputs=(Port("features", "features", array=True), Port("labels", "labels", array=True)),
        outputs=(Port("model", "model"),),
        params=(
            ParamSpec("epochs", "number", default=50, min=1, max=500),
            ParamSpec("learning_rate", "number", default=0.01, min=1e-5, max=1, step=1e-4),
        ),
    ),
    NodeSchema(
        id="head.knn",
        name="k-NN",
        category="head",
        description="Non-parametric nearest-neighbor. No training required.",
        inputs=(Port("features", "features", array=True), Port("labels", "labels", array=True)),
        outputs=(Port("model", "model"),),
        params=(
            ParamSpec("k", "number", default=5, min=1, max=50),
            ParamSpec("metric", "enum", default="cosine", options=("cosine", "euclidean")),
        ),
    ),
    # ───────── EVAL ─────────
    NodeSchema(
        id="eval.accuracy",
        name="Accuracy",
        category="eval",
        description="Top-1 accuracy on a held-out split.",
        inputs=(
            Port("model", "model"),
            Port("features", "features", array=True),
            Port("labels", "labels", array=True),
        ),
        outputs=(Port("metrics", "metrics"),),
    ),
    NodeSchema(
        id="eval.confusion",
        name="Confusion matrix",
        category="eval",
        description="Per-class confusion matrix.",
        inputs=(
            Port("model", "model"),
            Port("features", "features", array=True),
            Port("labels", "labels", array=True),
        ),
        outputs=(Port("metrics", "metrics"),),
    ),
    # ───────── DEPLOY ─────────
    NodeSchema(
        id="deploy.export-onnx",
        name="Export ONNX",
        category="deploy",
        description="Serialize the trained head to ONNX.",
        inputs=(Port("model", "model"),),
        params=(
            ParamSpec("filename", "string", default="wireml-model.onnx"),
            ParamSpec("opset", "number", default=17, min=11, max=20),
        ),
    ),
)


_BY_ID: dict[str, NodeSchema] = {s.id: s for s in NODE_SCHEMAS}


def get_schema(schema_id: str) -> NodeSchema | None:
    """Look up a node schema by id. Returns None for unknown ids (per audit H5)."""
    return _BY_ID.get(schema_id)


def require_schema(schema_id: str) -> NodeSchema:
    """Like get_schema but raises KeyError. Use only where unknown-schema is a bug."""
    schema = _BY_ID.get(schema_id)
    if schema is None:
        raise KeyError(f"Unknown node schema: {schema_id}")
    return schema
