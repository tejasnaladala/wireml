<div align="center">

# WireML

**An interactive terminal workbench for image-classification pipelines.**

Launch image-folder, k-NN, and synthetic workflows, plus optional webcam capture, from a Textual dashboard. WireML detects the available compute backend, runs each pipeline stage, streams its log, and keeps results in the terminal.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI](https://github.com/tejasnaladala/wireml/actions/workflows/ci.yml/badge.svg)](https://github.com/tejasnaladala/wireml/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Textual](https://img.shields.io/badge/TUI-Textual-8b5cf6)

</div>

---

## Terminal workbench

Running `wireml` opens a keyboard-driven dashboard with the working areas used by the application:

```text
┌─ wire/ml ────────────────────────────────────────────────────────────────────┐
│  TRAINING LAUNCHPAD                       │  SYSTEM                           │
│  ◆ Synthetic demo                        │  detected device and runtime      │
│  ≡ k-NN · no training                    │                                   │
│  ▦ Image folder classifier               ├─ RECENT SESSIONS ─────────────────┤
│  ▶ Webcam: phone detector                │  captured training sessions       │
│  ◉ Webcam: attention monitor             │                                   │
│  ✋ Webcam: hand gestures                 ├─ KEYBINDINGS ──────────────────────┤
│  ✱ Webcam: custom classes                │  ↑↓ move · Enter launch · d doctor│
└───────────────────────────────────────────┴───────────────────────────────────┘
```

Selecting a pipeline opens its ordered stages beside a live run log and a results table. The dashboard also exposes device diagnostics and recent webcam capture sessions.

## Install

Install WireML as an isolated tool with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install git+https://github.com/tejasnaladala/wireml
```

If `uv` is not installed, the repository bootstrap script installs it first and then installs WireML:

```bash
curl -fsSL https://raw.githubusercontent.com/tejasnaladala/wireml/main/install.sh | sh
```

For the CLIP, DINOv2, Torch, and Transformers dependencies:

```bash
uv tool install "git+https://github.com/tejasnaladala/wireml" --with "wireml[ml]"
# bootstrap-script equivalent
WIREML_EXTRAS=ml curl -fsSL https://raw.githubusercontent.com/tejasnaladala/wireml/main/install.sh | sh
```

## Run

```bash
wireml                       # launch the TUI
wireml device                # show the detected compute device
wireml templates             # list built-in templates
wireml run demo-synthetic    # headless run, no downloads needed
wireml run export-onnx       # train a head and write wireml-model.onnx (wireml[deploy])
```

## How it works

WireML is a linear-pipeline executor on top of a small node catalog. Templates are pre-wired pipelines of stages; each stage delegates to a Python runner:

```
data.synthetic  →  backbone.identity  →  head.linear  →  eval.accuracy
```

The engine walks stages in order, routes outputs by port name, and reports progress via a callback the TUI renders live.

Classifier heads use a deterministic, class-stratified 80/20 split by default. Training sees only the training partition; accuracy and confusion-matrix stages consume only the held-out partition. The split seed and fraction are explicit head parameters.

**Node catalog (v1):**

| Category  | Nodes                                                                  |
| --------- | ---------------------------------------------------------------------- |
| Data      | `data.synthetic` · `data.upload`                                       |
| Backbone  | `backbone.clip.vit-b-32` · `backbone.clip.vit-l-14` · `backbone.dinov2.small` · `backbone.identity` |
| Head      | `head.linear` · `head.knn`                                             |
| Eval      | `eval.accuracy` · `eval.confusion`                                     |
| Deploy    | `deploy.export-onnx`                                                   |

`wireml[ml]` adds the CLIP / DINOv2 backbones via PyTorch + Transformers. `wireml[deploy]` adds ONNX export. The synthetic and k-NN templates run with neither.

`deploy.export-onnx` only handles the linear head — it lowers to a single `Gemm`, embeds the class names as graph metadata, and runs `onnx.checker` before writing. k-NN carries its training set at inference time and has no fixed-weight graph, so WireML rejects k-NN export with a clear error.

### Synthetic smoke test

`wireml run demo-synthetic` checks data routing, head training, held-out evaluation, and progress reporting without downloading a model. Its generated classes are deliberately easy to separate. Treat the resulting accuracy only as a plumbing check.

## Device support

`wireml device` reports the best backend the current machine exposes. Detection priority:

1. **CUDA** (NVIDIA)
2. **MLX** (Apple Silicon; `wireml[mlx]`)
3. **MPS** (Apple Silicon fallback) — PyTorch native Metal
4. **ROCm** (AMD) — auto-detected when torch has `version.hip` set
5. **DirectML** (Windows) — via `onnxruntime-directml` (`wireml[directml]`)
6. **XPU** (Intel) — via `torch.xpu`
7. **CPU** (fallback)

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
│   ├── nodes/                  runner implementations (data, backbones, heads, eval, deploy)
│   └── tui/                    Textual app, screens, and theme
├── tests/                      pytest suite (no model downloads in CI)
├── install.sh                  one-line installer
├── pyproject.toml              hatchling package
└── README.md
```

## License

MIT — see [LICENSE](LICENSE).
