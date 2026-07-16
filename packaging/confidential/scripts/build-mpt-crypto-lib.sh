#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# build-mpt-crypto-lib.sh  —  BUILD libmpt-crypto FROM SOURCE (Linux + macOS)
#
# cibuildwheel `before-all` on Linux/macOS. Prioritizes BROAD COMPATIBILITY:
#   • Linux : runs INSIDE the manylinux_2_28 container, pinning the
#             glibc/libstdc++ floor so auditwheel accepts the result. (The
#             upstream prebuilt .so is built on Ubuntu 24.04 and would be
#             rejected by auditwheel.)
#   • macOS : MACOSX_DEPLOYMENT_TARGET=13.0 so the wheel installs on macOS 13+.
# Windows takes the prebuilt path instead — see fetch-prebuilt-natives.sh.
#
# Assumes scripts/stage-source.sh has already staged the package here. Drops the
# built library into the layout build_mpt_crypto.py expects:
#   xrpl/ext/confidential/libs/{linux,darwin}/libmpt-crypto.{so,dylib}
# (Headers are vendored in git under xrpl/ext/confidential/include/.)
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PKG="$PROJECT_ROOT/xrpl/ext/confidential"

# shellcheck disable=SC1091
source "$PROJECT_ROOT/version.env"

echo "==> build-mpt-crypto-lib.sh: mpt-crypto $MPT_CRYPTO_VERSION on $(uname -s)/$(uname -m)"

# ── 1. Toolchain (manylinux ships gcc but not git/conan/cmake/ninja) ──
if command -v dnf >/dev/null 2>&1; then
  dnf install -y git perl make >/dev/null 2>&1 || true
elif command -v yum >/dev/null 2>&1; then
  yum install -y git perl make >/dev/null 2>&1 || true
fi
# Constrain build-tool major versions so an upstream release can't silently
# pull an incompatible (or compromised) new major into the wheel-build pipeline.
# Bump these bounds deliberately and validate in the wheel CI.
python3 -m pip install --upgrade --quiet "conan>=2,<3" "ninja>=1.11,<2" "cmake>=3.28,<4"

# ── 2. Fetch the pinned source ──
SRC="$(mktemp -d)/mpt-crypto"
git clone --depth 1 --branch "$MPT_CRYPTO_VERSION" \
  "https://github.com/${MPT_CRYPTO_REPO}.git" "$SRC"

# Supply-chain: git tags are mutable (force-pushable). Verify the checked-out
# commit matches the pinned immutable SHA BEFORE running upstream's build
# script, so a moved/tampered tag can't inject code into published wheels.
ACTUAL_SHA="$(git -C "$SRC" rev-parse HEAD)"
if [ "${ACTUAL_SHA}" != "${MPT_CRYPTO_COMMIT}" ]; then
  echo "ERROR: tag ${MPT_CRYPTO_VERSION} resolved to ${ACTUAL_SHA}," >&2
  echo "       expected pinned commit ${MPT_CRYPTO_COMMIT}." >&2
  echo "       The tag may have been moved or tampered with; refusing to build." >&2
  exit 1
fi

# ── 3. Build via upstream's own script (keeps us ABI-aligned) ──
pushd "$SRC" >/dev/null
if [ "$(uname -s)" = "Darwin" ]; then
  export MACOSX_DEPLOYMENT_TARGET="${MACOSX_DEPLOYMENT_TARGET:-13.0}"
fi
bash ./.github/scripts/build-shared-lib.sh
popd >/dev/null

# ── 4. Stage the built library into the package's libs/<platform>/ ──
if [ "$(uname -s)" = "Darwin" ]; then
  mkdir -p "$PKG/libs/darwin"
  cp "$SRC/build/libmpt-crypto.dylib" "$PKG/libs/darwin/"
else
  mkdir -p "$PKG/libs/linux"
  cp "$SRC/build/libmpt-crypto.so" "$PKG/libs/linux/"
fi

echo "==> Staged library:"
find "$PKG/libs" -type f | sort
