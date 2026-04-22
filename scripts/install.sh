#!/usr/bin/env bash
# One-shot install for WireML. Installs both the JS workspace and the
# Python runtime via uv. Use `docker compose up` if you prefer a
# zero-touch container setup instead.
set -euo pipefail

if ! command -v pnpm >/dev/null 2>&1; then
  echo "Installing pnpm via corepack..."
  corepack enable
  corepack prepare pnpm@10 --activate
fi

echo "==> pnpm install"
pnpm install

if command -v uv >/dev/null 2>&1; then
  echo "==> uv sync (apps/runtime)"
  (cd apps/runtime && uv sync)
else
  echo "uv not found — skipping Python runtime install."
  echo "  Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

echo "Done. Next:"
echo "  pnpm dev               # start the web UI"
echo "  pnpm dev:runtime       # start the local Python runtime (Power Mode)"
echo "  docker compose up      # or run both in containers"
