"""End-to-end smoke tests for the engine and templates."""
from __future__ import annotations

import pytest

import wireml.nodes  # noqa: F401  — registers runners
from wireml.engine import engine
from wireml.registry import NODE_SCHEMAS, get_schema, require_schema
from wireml.templates import TEMPLATES, get_template


def test_every_schema_has_a_runner() -> None:
    """Every non-deploy schema in the registry should be executable."""
    runnable = set(engine.supported_ids())
    missing = [
        s.id for s in NODE_SCHEMAS if s.category != "deploy" and s.id not in runnable
    ]
    assert not missing, f"runners missing for: {missing}"


def test_get_schema_unknown_returns_none() -> None:
    assert get_schema("not.a.real.node") is None


def test_require_schema_unknown_raises() -> None:
    with pytest.raises(KeyError):
        require_schema("not.a.real.node")


def test_synthetic_demo_template_end_to_end() -> None:
    tmpl = get_template("demo-synthetic")
    assert tmpl is not None
    pipeline = tmpl.build()

    events: list[str] = []
    engine.execute(pipeline, on_progress=lambda s: events.append(f"{s.status}:{s.schema_id}"))

    # All stages should have completed OK.
    statuses = [s.status for s in pipeline.stages]
    assert statuses == ["ok"] * len(statuses), f"stage statuses: {statuses}"

    # Final accuracy stage should be present and > 0.8 on the synthetic separation.
    final = pipeline.stages[-2]
    metrics = final.outputs["metrics"]
    assert metrics["accuracy"] > 0.8, f"synthetic accuracy was {metrics['accuracy']:.3f}"


def test_knn_template_end_to_end() -> None:
    tmpl = get_template("knn-zero-train")
    assert tmpl is not None
    pipeline = tmpl.build()
    engine.execute(pipeline)
    assert all(s.status == "ok" for s in pipeline.stages)


def test_every_template_builds() -> None:
    for tmpl in TEMPLATES:
        pipeline = tmpl.build()
        assert pipeline.stages, f"template {tmpl.slug} has no stages"
        for stage in pipeline.stages:
            assert get_schema(stage.schema_id), f"{tmpl.slug}: unknown schema {stage.schema_id}"
