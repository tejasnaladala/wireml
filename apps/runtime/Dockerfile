# Multi-stage build: CUDA base for GPU hosts, CPU fallback otherwise.
# Users on Mac / Apple Silicon should prefer `uv` directly (apps/runtime).

ARG BASE_IMAGE=python:3.11-slim
FROM ${BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System deps for PIL, OpenCV-style ops, and healthcheck.
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
       curl \
       libjpeg-dev \
       zlib1g-dev \
       libpng-dev \
       libgl1 \
       libglib2.0-0 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md ./
COPY wireml_runtime ./wireml_runtime

RUN pip install --upgrade pip \
  && pip install .

EXPOSE 8787
HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
  CMD curl -fsS http://localhost:8787/health || exit 1

CMD ["uvicorn", "wireml_runtime.main:app", "--host", "0.0.0.0", "--port", "8787"]
