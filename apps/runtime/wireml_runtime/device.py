"""GPU device detection and fast-path selection.

Supports every common backend so `docker compose up` works identically on
CUDA laptops, Apple Silicon, ROCm, Intel XPU, and CPU-only boxes.
"""
from __future__ import annotations

import importlib
import platform
import shutil
from dataclasses import dataclass
from typing import Literal, cast

DeviceType = Literal[
    "cuda",
    "mps",
    "mlx",
    "rocm",
    "directml",
    "xpu",
    "cpu",
]


@dataclass
class DeviceInfo:
    type: DeviceType
    name: str
    vram_gb: float | None
    compute: str | None


def _try_cuda() -> DeviceInfo | None:
    try:
        import torch
    except ImportError:
        return None
    if not torch.cuda.is_available():
        return None
    # If this is a ROCm build, torch.version.hip is set.
    is_rocm = getattr(torch.version, "hip", None) is not None
    idx = torch.cuda.current_device()
    props = torch.cuda.get_device_properties(idx)
    return DeviceInfo(
        type="rocm" if is_rocm else "cuda",
        name=props.name,
        vram_gb=round(props.total_memory / 1024**3, 2),
        compute=f"sm_{props.major}{props.minor}" if not is_rocm else "rocm",
    )


def _try_mlx() -> DeviceInfo | None:
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        return None
    try:
        importlib.import_module("mlx.core")
    except ImportError:
        return None
    return DeviceInfo(
        type="mlx",
        name=f"Apple Silicon ({platform.processor() or 'arm64'})",
        vram_gb=None,  # unified memory; queryable via sysctl if needed
        compute="mlx",
    )


def _try_mps() -> DeviceInfo | None:
    try:
        import torch
    except ImportError:
        return None
    if not getattr(torch.backends, "mps", None):
        return None
    if not torch.backends.mps.is_available():
        return None
    return DeviceInfo(
        type="mps",
        name=f"Apple Silicon ({platform.processor() or 'arm64'})",
        vram_gb=None,
        compute="mps",
    )


def _try_directml() -> DeviceInfo | None:
    if platform.system() != "Windows":
        return None
    try:
        importlib.import_module("onnxruntime.providers.DmlExecutionProvider")
        return DeviceInfo(
            type="directml",
            name="DirectML GPU",
            vram_gb=None,
            compute="directml",
        )
    except Exception:
        return None


def _try_xpu() -> DeviceInfo | None:
    try:
        import torch
    except ImportError:
        return None
    xpu = getattr(torch, "xpu", None)
    if xpu is None:
        return None
    if not xpu.is_available():
        return None
    idx = xpu.current_device()
    name = xpu.get_device_name(idx)
    return DeviceInfo(type="xpu", name=name, vram_gb=None, compute="xpu")


def detect_device() -> DeviceInfo:
    """Return the best available device. Ordering reflects performance preference.

    Priority:
      1. CUDA (NVIDIA) — broadest model support, fastest inference
      2. MLX (Apple Silicon) — fastest path on M-series Macs
      3. MPS (Apple Silicon fallback) — PyTorch native Metal path
      4. ROCm (AMD)
      5. DirectML (Windows, any GPU)
      6. XPU (Intel)
      7. CPU
    """
    for detector in (
        _try_cuda,
        _try_mlx,
        _try_mps,
        _try_directml,
        _try_xpu,
    ):
        info = detector()
        if info is not None:
            return info

    return DeviceInfo(
        type="cpu",
        name=platform.processor() or "CPU",
        vram_gb=None,
        compute=f"{platform.machine()} · {shutil.which('python') or 'python'}",
    )


def to_torch_device(device: DeviceInfo):
    """Map a DeviceInfo to a torch device string."""
    import torch  # local import — torch is optional at detection time

    if device.type == "cuda":
        return torch.device("cuda")
    if device.type == "rocm":
        return torch.device("cuda")  # ROCm builds expose cuda API
    if device.type == "mps":
        return torch.device("mps")
    if device.type == "xpu":
        return torch.device(cast("str", "xpu"))
    return torch.device("cpu")
