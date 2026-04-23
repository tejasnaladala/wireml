#!/usr/bin/env bash
# WireML one-line installer.
#
#   curl -fsSL https://raw.githubusercontent.com/tejasnaladala/wireml/main/install.sh | sh
#
# Installs uv (if missing) and then `uv tool install git+https://github.com/tejasnaladala/wireml`.
# The `wireml` command lands on your PATH. Re-run to upgrade.
set -euo pipefail

REPO_URL="${WIREML_REPO:-https://github.com/tejasnaladala/wireml}"
EXTRAS="${WIREML_EXTRAS:-}"   # e.g. `ml` for CLIP/DINOv2, or `ml,mlx` on Apple Silicon.

info() { printf '\033[1;35m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m==>\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m!!\033[0m %s\n' "$*" >&2; exit 1; }

# 1. uv — the modern Python package installer. Idempotent.
if ! command -v uv >/dev/null 2>&1; then
  info "Installing uv (https://astral.sh/uv)…"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # shellcheck source=/dev/null
  [ -f "$HOME/.local/bin/env" ] && . "$HOME/.local/bin/env" || true
  [ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env" || true
  export PATH="$HOME/.local/bin:$PATH"
  command -v uv >/dev/null 2>&1 || die "uv install didn't expose the binary on PATH"
fi

# 2. install WireML as a uv tool (global, isolated virtualenv).
TARGET="git+${REPO_URL}"
if [ -n "$EXTRAS" ]; then
  TARGET="wireml[${EXTRAS}] @ ${TARGET#git+}"
  info "Installing wireml[${EXTRAS}] from ${REPO_URL}…"
  uv tool install --force "$TARGET" --from "git+${REPO_URL}"
else
  info "Installing wireml from ${REPO_URL}…"
  uv tool install --force "$TARGET"
fi

# 3. sanity.
if ! command -v wireml >/dev/null 2>&1; then
  warn "'wireml' not on PATH. Ensure \$HOME/.local/bin is in your PATH and reopen your shell."
else
  info "Installed. Launch with:   wireml"
  info "                          wireml device"
  info "                          wireml run demo-synthetic"
fi
