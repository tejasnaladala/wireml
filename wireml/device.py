"""GPU device detection and fast-path selection.

Lazy-imports heavy dependencies so the package is importable with just
the base extras. Audit fix C5: DirectML probe uses
onnxruntime.get_available_providers(), not a non-existent submodule.
"""
from __future__ import annotations

import importlib
import logging
import platform
import shutil
from functools import lru_cache

from wireml.schema import DeviceInfo

logger = logging.getLogger(__name__)


def _try_cuda() -> DeviceInfo | None:
    try:
        import torch
    except ImportError:
        return None
    if not torch.cuda.is_available():
        return None
    is_rocm = getattr(torch.version, "hip", None) is not None
    idx = torch.cuda.current_device()
    props = torch.cuda.get_device_properties(idx)
    return DeviceInfo(
        type="rocm" if is_rocm else "cuda",
        name=props.name,
        vram_gb=round(props.total_memory / 1024**3, 2),
        compute="rocm" if is_rocm else f"sm_{props.major}{props.minor}",
    )


def _try_mlx() -> DeviceInfo | None:
    if platform.system() != "Darwin" or platform.machine() not in {"arm64", "aarch64"}:
        return None
    try:
        importlib.import_module("mlx.core")
    except ImportError:
        return None
    return DeviceInfo(
        type="mlx",
        name=f"Apple Silicon ({platform.processor() or 'arm64'})",
        vram_gb=None,
        compute="mlx",
    )


def _try_mps() -> DeviceInfo | None:
    try:
        import torch
    except ImportError:
        return None
    mps = getattr(torch.backends, "mps", None)
    if mps is None or not mps.is_available():
        return None
    return DeviceInfo(
        type="mps",
        name=f"Apple Silicon ({platform.processor() or 'arm64'})",
        vram_gb=None,
        compute="mps",
    )


def _try_directml() -> DeviceInfo | None:
    """DirectML is exposed by onnxruntime-directml as an execution provider."""
    if platform.system() != "Windows":
        return None
    try:
        import onnxruntime as ort
    except ImportError:
        return None
    if "DmlExecutionProvider" not in ort.get_available_providers():
        return None
    return DeviceInfo(type="directml", name="DirectML GPU", vram_gb=None, compute="directml")


def _try_xpu() -> DeviceInfo | None:
    try:
        import torch
    except ImportError:
        return None
    xpu = getattr(torch, "xpu", None)
    if xpu is None or not xpu.is_available():
        return None
    idx = xpu.current_device()
    return DeviceInfo(type="xpu", name=xpu.get_device_name(idx), vram_gb=None, compute="xpu")


@lru_cache(maxsize=1)
def detect_device() -> DeviceInfo:
    """Return the best available device. Cached for the process lifetime.

    Priority:
      1. CUDA (NVIDIA)          — broadest model support, fastest inference
      2. MLX (Apple Silicon)    — fastest path on M-series Macs
      3. MPS (Apple Silicon)    — PyTorch native Metal fallback
      4. ROCm (AMD)             — detected via torch.cuda with hip set
      5. DirectML (Windows)     — via onnxruntime-directml
      6. XPU (Intel)            — via torch.xpu
      7. CPU                    — fallback
    """
    for detector in (_try_cuda, _try_mlx, _try_mps, _try_directml, _try_xpu):
        info = detector()
        if info is not None:
            logger.info("Detected device: %s (%s)", info.type, info.name)
            return info

    info = DeviceInfo(
        type="cpu",
        name=platform.processor() or "CPU",
        vram_gb=None,
        compute=f"{platform.machine()} · {shutil.which('python') or 'python'}",
    )
    logger.info("Falling back to CPU: %s", info.name)
    return info


def to_torch_device(device: DeviceInfo) -> object:
    """Map a DeviceInfo to a torch.device. Raises for non-torch backends (audit H8)."""
    import torch

    if device.type in {"cuda", "rocm"}:
        return torch.device("cuda")
    if device.type == "mps":
        return torch.device("mps")
    if device.type == "xpu":
        return torch.device("xpu")
    if device.type == "cpu":
        return torch.device("cpu")
    raise NotImplementedError(
        f"Device type {device.type!r} is not mapped to a torch.device. "
        "Use an MLX-specific code path or switch to CPU."
    )
