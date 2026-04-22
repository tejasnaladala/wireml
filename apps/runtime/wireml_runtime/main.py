"""FastAPI entry point for the WireML local runtime."""
from __future__ import annotations

import traceback
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .device import detect_device
from .nodes import REGISTRY, supported_node_ids
from .schema import (
    DeviceDescriptor,
    NodeError,
    NodeExecutionResult,
    RunNodeRequest,
    RuntimeCapabilities,
)

app = FastAPI(title="WireML runtime", version=__version__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


_device_info = None


def _lazy_device() -> DeviceDescriptor:
    global _device_info
    if _device_info is None:
        dev = detect_device()
        _device_info = DeviceDescriptor(
            type=dev.type,
            name=dev.name,
            vram_gb=dev.vram_gb,
            compute=dev.compute,
        )
    return _device_info


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "version": __version__, "device": _lazy_device().model_dump()}


@app.get("/capabilities", response_model=RuntimeCapabilities)
def capabilities() -> RuntimeCapabilities:
    return RuntimeCapabilities(
        kind="local",
        device=_lazy_device(),
        supportedNodes=supported_node_ids(),
        version=__version__,
    )


@app.post("/runNode", response_model=NodeExecutionResult)
def run_node(req: RunNodeRequest) -> NodeExecutionResult:
    runner = REGISTRY.get(req.node.schema_id)
    if runner is None:
        return NodeExecutionResult(
            outputs={},
            error=NodeError(message=f"No local runner for schema {req.node.schema_id}"),
        )
    try:
        outputs = runner(req.node, req.inputs)
        return NodeExecutionResult(outputs=outputs)
    except Exception as exc:  # pragma: no cover - user-facing error surface
        return NodeExecutionResult(
            outputs={},
            error=NodeError(message=str(exc), stack=traceback.format_exc()),
        )
