"""Basic device detection tests. These assert that detection always returns
a valid DeviceInfo with a known type, regardless of the host machine.
"""
from __future__ import annotations

from wireml_runtime.device import DeviceInfo, detect_device


def test_detect_returns_valid_device() -> None:
    info = detect_device()
    assert isinstance(info, DeviceInfo)
    assert info.type in {"cuda", "mps", "mlx", "rocm", "directml", "xpu", "cpu"}
    assert info.name, "device name should be non-empty"
