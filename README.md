<div align="center">

# WireML

**Teachable Machine, re-imagined as a node-graph workbench on modern foundation models — browser-first, GPU-ready locally.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI](https://github.com/tejasnaladala/wireml/actions/workflows/ci.yml/badge.svg)](https://github.com/tejasnaladala/wireml/actions/workflows/ci.yml)
[![Deploy](https://github.com/tejasnaladala/wireml/actions/workflows/deploy-web.yml/badge.svg)](https://tejasnaladala.github.io/wireml/)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![WebGPU](https://img.shields.io/badge/WebGPU-ready-8b5cf6)
![CUDA · MPS · MLX · ROCm · DirectML](https://img.shields.io/badge/GPU-CUDA%20%C2%B7%20MPS%20%C2%B7%20MLX%20%C2%B7%20ROCm%20%C2%B7%20DirectML-f59e0b)

</div>

---

Google's Teachable Machine (2019) made no-code ML approachable for millions. Its three-panel flow (**Data → Training → Preview**) is opinionated and hard-coded. **WireML** takes the same spirit and rebuilds it on a node-graph canvas: every capability — data sources, foundation-model backbones, training heads, evaluators, deployers — is a draggable, wireable node. Templates hide the complexity for beginners; power users get the full canvas.

## Why WireML

- **n8n / ComfyUI ergonomics for classical ML.** Wire nodes together visually. Every feature is a composable node.
- **Foundation-model era.** CLIP, DINOv2, SigLIP, Whisper, MediaPipe out of the box. Bring-your-own HF Hub model works too.
- **Zero-backend by default.** The hosted demo runs entirely on WebGPU in your browser. Data never leaves the tab.
- **Power mode on your hardware.** Clone the repo, `docker compose up`, and the Python runtime auto-detects **CUDA / MPS / MLX / ROCm / DirectML / XPU / CPU** — the same graph now runs on real GPU, unlocking larger models.
- **Portable graphs.** A WireML graph is a single JSON file. Authored in-browser, runs identically on the local runtime.

## Quickstart

**Hosted mode (web only) — no install:**
```bash
pnpm install
pnpm dev
# → http://localhost:5173
```

**Power mode — adds local GPU access:**
```bash
docker compose up
# Web UI:      http://localhost:8080
# Runtime API: http://localhost:8787/health
```

Or run the backend bare-metal with [uv](https://github.com/astral-sh/uv):
```bash
cd apps/runtime
uv sync
uv run wireml-runtime
```

Open the web UI — a **"Power Mode"** badge appears when the runtime is reachable, and heavy nodes (CLIP-L, DINOv2-L, future LoRA fine-tunes) light up in the library.

## How it works

```
          ┌──────────────────────────┐
          │   React Flow canvas      │
          │   (GraphJSON = truth)    │
          └────────────┬─────────────┘
                       │
         ┌─────────────┴──────────────┐
         ▼                            ▼
   WebGraphRunner              LocalGraphRunner
   (browser)                   (optional Python backend)

   • Transformers.js           • PyTorch / MLX
   • ONNX Runtime Web          • Auto device detect:
   • WebGPU kernels              CUDA · MPS · MLX · ROCm ·
   • OPFS dataset I/O            DirectML · XPU · CPU
```

Both runtimes implement the same `GraphRunner` interface and share node contracts in [`packages/nodes`](packages/nodes). A graph authored in one runs identically in the other — capability-gated nodes automatically light up when the heavier runtime is available.

### Execution semantics — mixed

Every node declares how it runs:
- **Reactive** — data sources, backbones, live previews. Recompute whenever upstream emits new output. This preserves the "point webcam, see probabilities move" magic from Teachable Machine.
- **Triggered** — training, evaluation, export. Fire only on explicit Run.

## The node catalog (v1)

| Category | Nodes |
| --- | --- |
| **Data** | Webcam · Upload images · Microphone |
| **Backbone** | CLIP ViT-B/32 (image+text) · DINOv2-S · MobileNetV3 · Whisper-tiny · MediaPipe Pose · CLIP ViT-L/14 (local-only) |
| **Head** | Linear · k-NN · Zero-shot CLIP |
| **Eval** | Accuracy · Confusion matrix |
| **Deploy** | Live preview · ONNX export · Shareable URL |

Templates shipped: **Image classifier**, **Sound classifier**, **Pose classifier**, **Zero-shot classifier**.

The full roadmap (video / tabular / time-series modalities, agentic LLM assistant, synthetic-data augmentation, federated training, edge export targets) lives in [docs/specs](docs/specs).

## Repo layout

```
wireml/
├── apps/
│   ├── web/            React + Vite UI. Ships as the hosted demo.
│   └── runtime/        Python FastAPI + PyTorch. Optional Power Mode backend.
├── packages/
│   ├── nodes/          Shared NodeSchema / GraphJSON contracts.
│   └── templates/      Pre-wired GraphJSON templates.
├── docker-compose.yml  One-command install for both runtimes.
├── scripts/install.sh
└── docs/specs/         Design specs & roadmap.
```

## Development

```bash
pnpm install             # install JS deps
pnpm dev                 # frontend only
pnpm dev:runtime         # uvicorn reload on port 8787

pnpm typecheck           # tsc across all packages
pnpm test                # vitest on web

cd apps/runtime
uv run pytest            # runtime tests
```

## Contributing

Issues and PRs welcome. See [docs/specs](docs/specs) for the design, [CONTRIBUTING.md](CONTRIBUTING.md) for the development contract.

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">
<sub>Built with <a href="https://react.dev">React</a> · <a href="https://reactflow.dev">React Flow</a> · <a href="https://huggingface.co/docs/transformers.js">Transformers.js</a> · <a href="https://fastapi.tiangolo.com">FastAPI</a> · <a href="https://pytorch.org">PyTorch</a> · <a href="https://ml-explore.github.io/mlx/">MLX</a></sub>
</div>
