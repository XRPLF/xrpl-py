#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# stage-source.sh  —  copy the package source into this build project (host-side)
#
# PEP 517 builds are isolated to the project directory (packaging/confidential/),
# so the source at <repo>/xrpl/ext/confidential/ must be copied in before the
# wheel build. Run this on the HOST in CI before invoking cibuildwheel (on Linux,
# cibuildwheel only mounts the project dir into the manylinux container, so the
# staged copy must already be present).
#
# Preserves the PEP 420 namespace: creates xrpl/ and xrpl/ext/ as plain
# directories WITHOUT __init__.py; only xrpl/ext/confidential/ is a package.
# The staged xrpl/ tree is gitignored.
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$PROJECT_ROOT/../.." && pwd)"

SRC="$REPO_ROOT/xrpl/ext/confidential"
DST="$PROJECT_ROOT/xrpl/ext/confidential"

echo "==> Staging $SRC -> $DST"
rm -rf "$PROJECT_ROOT/xrpl"
mkdir -p "$PROJECT_ROOT/xrpl/ext"
cp -R "$SRC" "$DST"

# Drop any build artifacts copied along; libs/ is repopulated by before-all.
rm -rf "$DST"/__pycache__ "$DST"/_mpt_crypto.* "$DST"/build "$DST"/libs/*/*.dylib \
       "$DST"/libs/*/*.so "$DST"/libs/*/*.dll 2>/dev/null || true

# Guard the namespace invariant.
if [ -f "$PROJECT_ROOT/xrpl/__init__.py" ] || [ -f "$PROJECT_ROOT/xrpl/ext/__init__.py" ]; then
  echo "ERROR: xrpl/ or xrpl/ext/ has __init__.py — breaks the PEP 420 namespace" >&2
  exit 1
fi
echo "==> Staged (namespace preserved). Contents:"
find "$PROJECT_ROOT/xrpl" -maxdepth 3 -type d | sort
