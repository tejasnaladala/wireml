#!/usr/bin/env bash
# WireML — one-line installer.
#
#   curl -fsSL https://raw.githubusercontent.com/tejasnaladala/wireml/main/install.sh | sh
#
# Installs uv (if missing), then `uv tool install git+https://github.com/tejasnaladala/wireml`
# with the full ml + webcam extras so `wireml demo webcam ...` works out of the box.
#
# Env knobs:
#   WIREML_EXTRAS   comma list of extras to install (default: "ml,webcam")
#   WIREML_REPO     override the git URL (for forks)
#   WIREML_REF      pin to a tag/branch/sha (e.g. WIREML_REF=v0.2.0)
set -euo pipefail

REPO_URL="${WIREML_REPO:-https://github.com/tejasnaladala/wireml}"
REF="${WIREML_REF:-}"
EXTRAS="${WIREML_EXTRAS:-ml,webcam}"

# ─── pretty output ──────────────────────────────────────────────────────────
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  readonly LAV=$'\033[38;5;141m'
  readonly DIM=$'\033[2m'
  readonly BOLD=$'\033[1m'
  readonly RED=$'\033[31m'
  readonly GRN=$'\033[32m'
  readonly YEL=$'\033[33m'
  readonly RST=$'\033[0m'
else
  readonly LAV="" DIM="" BOLD="" RED="" GRN="" YEL="" RST=""
fi

banner() {
  cat <<BANNER
${LAV}${BOLD}
    ▮▮   wire/ml
${RST}${DIM}    teachable machine for the foundation-model era${RST}
${DIM}    ────────────────────────────────────────────────${RST}
BANNER
}

step()  { printf '%s▶%s  %s\n' "$LAV"  "$RST" "$*"; }
ok()    { printf '%s✓%s  %s\n' "$GRN"  "$RST" "$*"; }
warn()  { printf '%s!%s  %s\n' "$YEL"  "$RST" "$*" >&2; }
die()   { printf '%s✗%s  %s\n' "$RED"  "$RST" "$*" >&2; exit 1; }

# ─── detect environment ────────────────────────────────────────────────────
banner

UNAME="$(uname -s 2>/dev/null || echo Unknown)"
case "$UNAME" in
  Linux*)   PLATFORM=linux  ;;
  Darwin*)  PLATFORM=macos  ;;
  MINGW*|MSYS*|CYGWIN*) PLATFORM=windows ;;
  *)        PLATFORM=other ;;
esac
step "platform ${BOLD}${PLATFORM}${RST}   ${DIM}extras: ${EXTRAS}${RST}"

# ─── 1. uv ─────────────────────────────────────────────────────────────────
if ! command -v uv >/dev/null 2>&1; then
  step "installing uv (astral.sh/uv) — one-time"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # Source uv's env file so it's on PATH for the rest of this script.
  if [ -f "$HOME/.local/bin/env" ]; then
    # shellcheck source=/dev/null
    . "$HOME/.local/bin/env"
  fi
  if [ -f "$HOME/.cargo/env" ]; then
    # shellcheck source=/dev/null
    . "$HOME/.cargo/env"
  fi
  export PATH="$HOME/.local/bin:$PATH"
  command -v uv >/dev/null 2>&1 || die "uv not on PATH after install — reopen your shell and re-run."
  ok "uv installed"
else
  ok "uv $(uv --version | awk '{print $2}') already present"
fi

# ─── 2. wireml ─────────────────────────────────────────────────────────────
SOURCE="git+${REPO_URL}"
if [ -n "$REF" ]; then
  SOURCE="${SOURCE}@${REF}"
fi

EXTRAS_ARGS=""
if [ -n "$EXTRAS" ]; then
  # Split by comma, prepend --with each.
  OLD_IFS="$IFS"
  IFS=','
  for extra in $EXTRAS; do
    EXTRAS_ARGS="$EXTRAS_ARGS --with wireml[$extra]"
  done
  IFS="$OLD_IFS"
fi

step "installing wireml from ${DIM}${REPO_URL}${RST}"
# shellcheck disable=SC2086
uv tool install --force $EXTRAS_ARGS "$SOURCE"

# ─── 3. sanity ─────────────────────────────────────────────────────────────
if ! command -v wireml >/dev/null 2>&1; then
  warn "'wireml' not on PATH. Ensure \$HOME/.local/bin is exported in your shell rc."
  warn "   e.g. echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
  exit 0
fi

VERSION=$(wireml version 2>/dev/null || echo "unknown")
ok "${VERSION} installed"

cat <<DONE

${BOLD}try it now${RST}
  ${LAV}wireml${RST}                                   ${DIM}launch the dashboard${RST}
  ${LAV}wireml doctor${RST}                            ${DIM}health check${RST}
  ${LAV}wireml demo webcam with-phone without-phone${RST}   ${DIM}train live${RST}

${DIM}docs: ${REPO_URL}${RST}
DONE
