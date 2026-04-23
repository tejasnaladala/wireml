"""Built-in pipeline templates. A template is a linear sequence of stages."""
from __future__ import annotations

from dataclasses import dataclass

from wireml.schema import Pipeline, StageState


@dataclass(frozen=True)
class Template:
    slug: str
    title: str
    subtitle: str
    tags: tuple[str, ...]
    build: callable  # () -> Pipeline


def _image_classifier() -> Pipeline:
    return Pipeline(
        name="Image classifier",
        description="Folder of images per class → CLIP features → linear head → accuracy.",
        classes=["class_a", "class_b"],
        stages=[
            StageState(schema_id="data.upload", params={"folder": ""}),
            StageState(schema_id="backbone.clip.vit-b-32", params={"normalize": True}),
            StageState(schema_id="head.linear", params={"epochs": 80, "learning_rate": 0.05}),
            StageState(schema_id="eval.accuracy", params={}),
            StageState(schema_id="eval.confusion", params={}),
        ],
    )


def _demo_synthetic() -> Pipeline:
    return Pipeline(
        name="Synthetic demo",
        description="No model downloads, no data needed — train a linear head on toy features.",
        classes=["alpha", "beta", "gamma"],
        stages=[
            StageState(
                schema_id="data.synthetic",
                params={"num_per_class": 40, "num_classes": 3, "feature_dim": 16},
            ),
            StageState(schema_id="backbone.identity", params={}),
            StageState(schema_id="head.linear", params={"epochs": 120, "learning_rate": 0.1}),
            StageState(schema_id="eval.accuracy", params={}),
            StageState(schema_id="eval.confusion", params={}),
        ],
    )


def _knn_zero_train() -> Pipeline:
    return Pipeline(
        name="k-NN (no training)",
        description="Same data path, but k-NN instead of a trained head — no gradient descent.",
        classes=["class_a", "class_b"],
        stages=[
            StageState(schema_id="data.synthetic", params={"num_per_class": 30, "num_classes": 3}),
            StageState(schema_id="backbone.identity", params={}),
            StageState(schema_id="head.knn", params={"k": 5, "metric": "cosine"}),
            StageState(schema_id="eval.accuracy", params={}),
        ],
    )


TEMPLATES: tuple[Template, ...] = (
    Template(
        slug="demo-synthetic",
        title="Synthetic demo",
        subtitle="Toy features · linear head · no downloads. Verify the pipeline works.",
        tags=("beginner", "demo", "offline"),
        build=_demo_synthetic,
    ),
    Template(
        slug="image-classifier",
        title="Image classifier",
        subtitle="Folder per class → CLIP ViT-B/32 → linear head. Needs `pip install wireml[ml]`.",
        tags=("image", "clip"),
        build=_image_classifier,
    ),
    Template(
        slug="knn-zero-train",
        title="k-NN (no training)",
        subtitle="Skip gradient descent. k-NN at inference.",
        tags=("beginner", "knn", "offline"),
        build=_knn_zero_train,
    ),
)


def get_template(slug: str) -> Template | None:
    for t in TEMPLATES:
        if t.slug == slug:
            return t
    return None
