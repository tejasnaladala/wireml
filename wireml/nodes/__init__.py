"""Node runner modules. Importing this package registers all runners with
wireml.engine.engine.
"""
from __future__ import annotations

# Backbones import torch/transformers lazily inside their runners, but the
# module itself only touches those symbols on call — safe to import here.
from wireml.nodes import (  # noqa: F401
    backbones,  # noqa: F401
    data,
    evaluation,
    heads,
)
