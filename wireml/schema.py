"""Data types for nodes, pipelines, and execution results.

Pure Python — no TypeScript mirror any more. The TUI doesn't need JSON
interop with a browser client.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

DeviceType = Literal["cuda", "mps", "mlx", "rocm", "directml", "xpu", "cpu"]
Category = Literal["data", "preprocess", "backbone", "head", "eval", "deploy"]
ParamKind = Literal["string", "number", "enum", "boolean", "file", "json"]
ExecutionMode = Literal["reactive", "triggered"]


@dataclass(frozen=True)
class DeviceInfo:
    type: DeviceType
    name: str
    vram_gb: float | None = None
    compute: str | None = None


@dataclass(frozen=True)
class Port:
    name: str
    type: str
    optional: bool = False
    array: bool = False


@dataclass(frozen=True)
class ParamSpec:
    name: str
    kind: ParamKind
    default: Any = None
    options: tuple[str, ...] = ()
    min: float | None = None
    max: float | None = None
    step: float | None = None
    description: str | None = None


@dataclass(frozen=True)
class Capability:
    min_vram_gb: float | None = None
    local_only: bool = False
    download_mb: float | None = None


@dataclass(frozen=True)
class NodeSchema:
    id: str
    name: str
    category: Category
    description: str
    inputs: tuple[Port, ...] = ()
    outputs: tuple[Port, ...] = ()
    params: tuple[ParamSpec, ...] = ()
    capability: Capability = field(default_factory=Capability)
    execution_mode: ExecutionMode = "triggered"


@dataclass
class StageState:
    schema_id: str
    params: dict[str, Any] = field(default_factory=dict)
    status: Literal["idle", "running", "ok", "error"] = "idle"
    message: str | None = None
    outputs: dict[str, Any] = field(default_factory=dict)


@dataclass
class Pipeline:
    """A linear pipeline of stages — simpler than a full DAG, sufficient for the TUI."""

    name: str
    description: str = ""
    stages: list[StageState] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)

    def reset(self) -> None:
        for stage in self.stages:
            stage.status = "idle"
            stage.message = None
            stage.outputs = {}
