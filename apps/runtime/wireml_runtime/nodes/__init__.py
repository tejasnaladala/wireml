"""Server-side node implementations. Each module registers runners into the
shared REGISTRY so main.py can dispatch by schema_id.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

REGISTRY: dict[str, Callable[[Any, dict[str, Any]], dict[str, Any]]] = {}


def register(schema_id: str):
    def decorator(fn: Callable[[Any, dict[str, Any]], dict[str, Any]]):
        REGISTRY[schema_id] = fn
        return fn

    return decorator


# Side-effect: each import registers its runners.
from . import backbones, heads  # noqa: F401,E402
from . import evaluation  # noqa: F401,E402


def supported_node_ids() -> list[str]:
    return sorted(REGISTRY.keys())
