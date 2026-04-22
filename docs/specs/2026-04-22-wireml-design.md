# WireML — Design Spec

**Date:** 2026-04-22
**Status:** Approved by operator, proceeding to implementation.

---

## 1. The Pitch

WireML is a **node-graph visual ML workbench** — think ComfyUI for classical ML / transfer learning. It replaces Google Teachable Machine's fixed three-panel UI (Data → Training → Preview) with a visual canvas where every capability is a composable, wired-together node. Templates hide the complexity for beginners; power users drop into the full canvas.

**One-line pitch:**
> Teachable Machine, re-imagined as a node-graph workbench on modern foundation models — runs in your browser on WebGPU, or locally on any GPU (CUDA / MPS / MLX / ROCm / DirectML).

## 2. Distribution

Two runtime modes, same UI, same graph JSON:

| Mode | Host | GPU access | Model ceiling |
| --- | --- | --- | --- |
| **Hosted demo** | static site (Vercel / Pages) | browser WebGPU | CLIP-B, DINOv2-S, Whisper-tiny/base, MobileNet, MediaPipe |
| **Power mode** | `git clone && docker compose up` | native PyTorch auto-detects CUDA / MPS / MLX / ROCm / DirectML / XPU, CPU fallback | unlimited — big CLIP-L, DINOv2-L, Whisper-medium, LoRA fine-tunes |

Frontend pings `localhost:8787/health` on load. Local backend present → unlock heavier nodes + flip a `Power Mode` badge. Otherwise ship WebGPU-only node library.

## 3. Core Abstractions

- **NodeSchema** — declares `inputs`, `outputs`, `params`, `capability` (e.g. `{ minVramGb: 4 }`), and `executionMode: "reactive" | "triggered"`.
- **GraphJSON** — portable DAG. Identical serialization across runtimes.
- **GraphRunner** — interface with `WebGraphRunner` (Transformers.js / ONNX Runtime Web) and `LocalGraphRunner` (FastAPI client proxy) implementations.

### Node categories (colour-coded in UI)

| Category | Color | Examples |
| --- | --- | --- |
| Data | green | Webcam, Upload, Mic, URL, Screen capture, Synthetic (SD) |
| Preprocess | violet | Resize, Augment, Normalize, Windowing |
| Backbone | blue | CLIP ViT-B/32, DINOv2-S, SigLIP, MobileNetV3, Whisper-tiny, MediaPipe Pose, BGE Text |
| Head | amber | Linear, kNN, Zero-shot CLIP, Prototype, LoRA |
| Eval | red | Accuracy, Confusion Matrix, Saliency, Fairness, Prototypes |
| Deploy | teal | ONNX export, TFJS export, Core ML, WebGPU runtime link, HTTP API, Shareable URL |

### Execution semantics

- **Data + Preview nodes** execute reactively (frame arrives → recompute downstream → UI updates live). This preserves the TM "point webcam, see probabilities move" magic.
- **Training nodes** execute on explicit click. Expensive operations stay explicit.
- Each schema declares its `executionMode`, read by the scheduler.

## 4. Repo Shape (monorepo)

```
wireml/
├── apps/
│   ├── web/                   Vite + React + TS + React Flow + Tailwind + Zustand
│   └── runtime/               Python + FastAPI + PyTorch/MLX
├── packages/
│   ├── nodes/                 Shared node schemas (TypeScript)
│   └── templates/             Canonical GraphJSON templates
├── docker-compose.yml
├── scripts/install.sh
├── .github/workflows/
├── docs/
└── README.md
```

`docker compose up` → builds and runs both. Hosted demo deploys just `apps/web` to Vercel. pnpm workspaces for JS/TS, uv for Python.

## 5. v1 Feature Scope (flagship tier)

Shipping day one:
- React Flow canvas with pan / zoom / select / wire
- Template gallery (≥ 3 templates)
- Node library sidebar grouped by category
- Core nodes: Webcam, Upload, Mic, CLIP image, CLIP text, DINOv2-S, Whisper-tiny, MediaPipe Pose, Linear, kNN, Zero-shot CLIP, Live Preview, Accuracy + Confusion Matrix, ONNX export, Shareable URL
- WebGraphRunner using Transformers.js + ONNX Runtime Web + WebGPU
- LocalGraphRunner skeleton (FastAPI, GPU autodetect, at least three matching node implementations)
- Graph persistence to IndexedDB + URL hash sharing
- Docker compose + Dockerfile
- README with portfolio pitch, architecture diagram, quickstart
- GitHub Actions CI (frontend typecheck + build, backend lint + pytest)

Deferred to roadmap:
- Agentic LLM assistant (Hook 2 content)
- Synthetic data via SD
- Video / tabular / time-series modalities
- Federated + collaborative training
- Core ML / Jetson / microcontroller export targets

## 6. Stack Commitments

- **Frontend:** React 18 + TypeScript + Vite, React Flow, Tailwind, Zustand (graph state), Transformers.js, ONNX Runtime Web, `@huggingface/hub`.
- **Backend:** Python 3.11, FastAPI, Uvicorn, PyTorch 2.4+, MLX (conditional on Apple Silicon), onnxruntime, transformers, pydantic. Managed by `uv`.
- **Infra:** Docker Compose, GitHub Actions, Vercel for hosted demo.
- **Testing:** Vitest for web, pytest for runtime, Playwright for one e2e smoke test.

## 7. Error Handling, Capability Gating

- Nodes declare `capability`. UI filters library by available runtime; if user attempts to run a graph with unavailable nodes, UI offers to switch to Power Mode or swap to an equivalent node.
- GraphRunner wraps every node with try/catch → structured error bubbles in UI (inline on the offending node).
- Model download errors surface with explicit retry + fallback suggestions.

## 8. Risks & Mitigations

- **Cold-load WebGPU models are large** → ship service worker + persistent cache; show download progress UI.
- **WebGPU browser support (Firefox lag)** → detect & fall back to WASM; warn user.
- **Runtime drift between Web and Local** → contract tests in `packages/nodes/` run both runtimes against canonical fixtures in CI.
- **Scope creep** → v1 scope is fenced above; extensions live in a `roadmap.md` with issue links.

## 9. Marketing Surface

Separate from the app itself, a 3D immersive scroll-animated site will live (optionally) under `apps/site/` or a separate `wireml-site/` repo. Its prompt pack is produced at the end of this build for handoff to Claude-based design generation.
