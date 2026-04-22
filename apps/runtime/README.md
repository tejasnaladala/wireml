# WireML runtime

Local Python execution backend for WireML. Serves a FastAPI endpoint that:

- Auto-detects GPU capabilities at startup (CUDA, MPS, MLX, ROCm, DirectML, XPU, CPU).
- Mirrors the node contracts defined in `packages/nodes` (identical inputs, outputs, parameters).
- Runs heavy models that don't fit in the browser (CLIP ViT-L, DINOv2-L, Whisper-medium, LoRA fine-tunes).

## Quickstart

```bash
# In the monorepo root
docker compose up runtime      # recommended (handles CUDA drivers via container)

# Or with uv (recommended for Mac / Linux dev)
cd apps/runtime
uv sync
uv run wireml-runtime
```

The frontend (apps/web) will auto-detect the running runtime on port 8787 and
flip into **Power Mode**.
