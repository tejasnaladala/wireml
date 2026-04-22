"""Pydantic mirror of the TypeScript NodeSchema / GraphJSON contracts.

The shapes here match packages/nodes/src/schema.ts exactly — a graph
authored in the browser can be POSTed verbatim to /runNode.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

DeviceType = Literal[
    "cuda",
    "mps",
    "mlx",
    "rocm",
    "directml",
    "xpu",
    "cpu",
    "webgpu",
]


class DeviceDescriptor(BaseModel):
    type: DeviceType
    name: str
    vram_gb: float | None = Field(default=None, alias="vramGb")
    compute: str | None = None

    model_config = {"populate_by_name": True}


class RuntimeCapabilities(BaseModel):
    kind: Literal["local", "web"]
    device: DeviceDescriptor
    supported_nodes: list[str] = Field(alias="supportedNodes")
    version: str

    model_config = {"populate_by_name": True}


class NodeInstance(BaseModel):
    id: str
    schema_id: str = Field(alias="schemaId")
    position: dict[str, float]
    params: dict[str, Any]

    model_config = {"populate_by_name": True}


class RunNodeRequest(BaseModel):
    node: NodeInstance
    inputs: dict[str, Any]


class NodeError(BaseModel):
    message: str
    stack: str | None = None


class NodeExecutionResult(BaseModel):
    outputs: dict[str, Any]
    error: NodeError | None = None
