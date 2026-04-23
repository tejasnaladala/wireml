"""Pipeline executor. Walks a linear pipeline of stages, threading outputs
by port name into the next stage.

Emits progress via an optional callback so the TUI can show per-stage
status without reaching into engine internals.
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from wireml.registry import require_schema
from wireml.schema import Pipeline, StageState

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[StageState], None]
NodeRunner = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]


class Engine:
    """Executes pipelines by dispatching to registered node runners."""

    def __init__(self) -> None:
        self._runners: dict[str, NodeRunner] = {}

    def register(self, schema_id: str) -> Callable[[NodeRunner], NodeRunner]:
        """Decorator that registers a runner under a schema id."""

        def wrap(fn: NodeRunner) -> NodeRunner:
            self._runners[schema_id] = fn
            return fn

        return wrap

    def supported_ids(self) -> list[str]:
        return sorted(self._runners.keys())

    def execute(
        self,
        pipeline: Pipeline,
        on_progress: ProgressCallback | None = None,
    ) -> dict[str, Any]:
        """Run every stage in order. Returns the accumulated port state.

        Raises RuntimeError on the first stage that fails — the caller can
        inspect pipeline.stages[i].status / .message for per-stage context.
        """
        pipeline.reset()
        state: dict[str, Any] = {"classes": list(pipeline.classes)}

        for stage in pipeline.stages:
            schema = require_schema(stage.schema_id)
            runner = self._runners.get(stage.schema_id)
            if runner is None:
                stage.status = "error"
                stage.message = f"no runner registered for {stage.schema_id}"
                if on_progress:
                    on_progress(stage)
                raise RuntimeError(stage.message)

            stage.status = "running"
            stage.message = None
            if on_progress:
                on_progress(stage)

            inputs = {port.name: state[port.name] for port in schema.inputs if port.name in state}

            try:
                outputs = runner(stage.params, inputs)
            except Exception as exc:
                logger.exception("stage %s failed", stage.schema_id)
                stage.status = "error"
                stage.message = str(exc)
                if on_progress:
                    on_progress(stage)
                raise RuntimeError(f"{stage.schema_id}: {exc}") from exc

            state.update(outputs)
            stage.outputs = outputs
            stage.status = "ok"
            stage.message = _short_message(schema.id, outputs)
            if on_progress:
                on_progress(stage)

        return state


def _short_message(schema_id: str, outputs: dict[str, Any]) -> str:
    """Make per-stage success messages readable in the TUI status column."""
    if "features" in outputs:
        feats = outputs["features"]
        return f"{len(feats)} × {len(feats[0]) if feats else 0}"
    if "model" in outputs and isinstance(outputs["model"], dict):
        kind = outputs["model"].get("kind", "model")
        classes = outputs["model"].get("classes", [])
        return f"{kind} · {len(classes)} classes"
    if "metrics" in outputs:
        metrics = outputs["metrics"]
        if "accuracy" in metrics:
            return f"accuracy {metrics['accuracy']:.3f} · n={metrics.get('n', '?')}"
        if "matrix" in metrics:
            return f"{len(metrics.get('classes', []))}×{len(metrics.get('classes', []))} matrix"
    if schema_id.startswith("data."):
        imgs = outputs.get("images") or outputs.get("features") or []
        return f"{len(imgs)} samples"
    return "ok"


# Module-level singleton — runners register themselves on import.
engine = Engine()
