"""Device auto-detection is idempotent and returns a valid backend."""
from __future__ import annotations

from wireml.device import detect_device
from wireml.schema import DeviceInfo


def test_detect_returns_valid_device() -> None:
    info = detect_device()
    assert isinstance(info, DeviceInfo)
    assert info.type in {"cuda", "mps", "mlx", "rocm", "directml", "xpu", "cpu"}
    assert info.name, "device name should be non-empty"


def test_detect_is_cached() -> None:
    assert detect_device() is detect_device()
