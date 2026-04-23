<div align="center">

# WireML

**Teachable Machine, re-imagined as a terminal TUI on modern foundation models.**
Auto-detects CUDA · MPS · MLX · ROCm · DirectML · XPU · CPU.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI](https://github.com/tejasnaladala/wireml/actions/workflows/ci.yml/badge.svg)](https://github.com/tejasnaladala/wireml/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Textual](https://img.shields.io/badge/TUI-Textual-8b5cf6)

</div>

---

## Install

One line. Installs [uv](https://astral.sh/uv) if needed, then installs WireML as an isolated global tool.

```bash
curl -fsSL https://raw.githubusercontent.com/tejasnaladala/wireml/main/install.sh | sh
```

Or, if you already have `uv`:

```bash
uv tool install git+https://github.com/tejasnaladala/wireml
```

To pull the ML extras (CLIP / DINOv2 / Torch / Transformers):

```bash
WIREML_EXTRAS=ml curl -fsSL https://raw.githubusercontent.com/tejasnaladala/wireml/main/install.sh | sh
# or
uv tool install "git+https://github.com/tejasnaladala/wireml" --with "wireml[ml]"
```

## Run

```bash
wireml                       # launch the TUI
wireml device                # show the detected compute device
wireml templates             # list built-in templates
wireml run demo-synthetic    # headless run — no downloads needed
```

## What you get

A dark, tight, single-binary-feel terminal workbench:

```
┌─ WireML · node-graph ML on foundation models — terminal edition ──────────────┐
│                                                                               │
│ ┌ TEMPLATES ─────────────────┐   ┌ DEVICE ────────────────────┐               │
│ │ ▸ Synthetic demo           │   │ CUDA     RTX 4090          │               │
│ │   Image classifier         │   │          24.0 GB VRAM      │               │
│ │   k-NN (no training)       │   │          sm_89             │               │
│ └────────────────────────────┘   │                             │               │
│                                   │ SHORTCUTS                   │               │
│                                   │   ↑↓    move selection      │               │
│                                   │   Enter open template       │               │
│                                   │   r     run synthetic demo  │               │
│                                   │   q     quit                │               │
│                                   └─────────────────────────────┘               │
│                                                                               │
└─ wireml 0.2.0 ───────────────────────────────────────────────────────────────┘
```

Every template opens a pipeline view with a run log and a results table.

## How it works

WireML is a linear-pipeline executor on top of a small node catalog. Templates are pre-wired pipelines of stages; each stage delegates to a Python runner:

```
data.synthetic  →  backbone.identity  →  head.linear  →  eval.accuracy
```

The engine walks stages in order, routes outputs by port name, and reports progress via a callback the TUI renders live.

**Node catalog (v1):**

| Category  | Nodes                                                                  |
| --------- | ---------------------------------------------------------------------- |
| Data      | `data.synthetic` · `data.upload`                                       |
| Backbone  | `backbone.clip.vit-b-32` · `backbone.clip.vit-l-14` · `backbone.dinov2.small` · `backbone.identity` |
| Head      | `head.linear` · `head.knn`                                             |
| Eval      | `eval.accuracy` · `eval.confusion`                                     |
| Deploy    | `deploy.export-onnx`                                                   |

`wireml[ml]` extras add the CLIP / DINOv2 backbones via PyTorch + Transformers. The synthetic + k-NN templates run without them.

## Device support

`wireml device` reports the best backend the current machine exposes. Detection priority:

1. **CUDA** (NVIDIA)
2. **MLX** (Apple Silicon) — fastest path on M-series Macs (`wireml[mlx]`)
3. **MPS** (Apple Silicon fallback) — PyTorch native Metal
4. **ROCm** (AMD) — auto-detected when torch has `version.hip` set
5. **DirectML** (Windows) — via `onnxruntime-directml` (`wireml[directml]`)
6. **XPU** (Intel) — via `torch.xpu`
7. **CPU** (always available)

## Development

```bash
git clone https://github.com/tejasnaladala/wireml
cd wireml
uv sync --extra dev
uv run pytest              # tests (no model downloads)
uv run ruff check wireml tests
uv run wireml              # launch TUI against your checkout
```

## Repo layout

```
wireml/
├── wireml/                     the Python package
│   ├── cli.py                  typer entry (launches TUI by default)
│   ├── device.py               CUDA / MPS / MLX / ROCm / DirectML autodetect
│   ├── engine.py               linear pipeline executor + runner registry
│   ├── registry.py             NodeSchema catalog
│   ├── templates.py            canonical pre-wired pipelines
│   ├── schema.py               data types (DeviceInfo, NodeSchema, Pipeline…)
│   ├── nodes/                  runner implementations (data, backbones, heads, eval)
│   └── tui/                    Textual app, screens, and theme
├── tests/                      pytest suite (no model downloads in CI)
├── docs/                       specs, audit, and historical prompt packs
├── install.sh                  one-line installer
├── pyproject.toml              hatchling package
└── README.md
```

## License

MIT — see [LICENSE](LICENSE).
