#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# fetch-prebuilt-natives.sh  —  CONSUME prebuilt libmpt-crypto (Windows only)
#
# cibuildwheel `before-all` on Windows. Windows has no manylinux-style glibc
# floor, so we use the upstream prebuilt DLL directly and let delvewheel vendor
# it into the wheel.
#
# Assumes scripts/stage-source.sh has already staged the package here. Drops the
# DLL into the layout build_mpt_crypto.py expects:
#   xrpl/ext/confidential/libs/win32/mpt-crypto.dll
# (Headers are vendored in git under xrpl/ext/confidential/include/.)
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PKG="$PROJECT_ROOT/xrpl/ext/confidential"

# shellcheck disable=SC1091
source "$PROJECT_ROOT/version.env"

BUNDLE="mpt-crypto-natives-${MPT_CRYPTO_VERSION}.tar.gz"
URL="https://github.com/${MPT_CRYPTO_REPO}/releases/download/${MPT_CRYPTO_VERSION}/${BUNDLE}"
TMP="$(mktemp -d)"

echo "==> Downloading $URL"
curl -fsSL -o "$TMP/$BUNDLE" "$URL"

# Supply-chain pin: refuse to build against an unexpected artifact.
if [ -n "${BUNDLE_SHA256:-}" ] && [ "${BUNDLE_SHA256}" != "REPLACE_ME_WITH_RELEASE_ASSET_SHA256" ]; then
  echo "${BUNDLE_SHA256}  $TMP/$BUNDLE" | sha256sum -c - \
    || { echo "ERROR: sha256 mismatch for $BUNDLE" >&2; exit 1; }
else
  echo "ERROR: BUNDLE_SHA256 is not pinned in version.env — refusing to stage an" >&2
  echo "unverified native artifact into a published wheel. Set BUNDLE_SHA256 to the" >&2
  echo "sha256 of $BUNDLE before building. Observed (unverified) hash:" >&2
  sha256sum "$TMP/$BUNDLE" >&2
  exit 1
fi

tar -xzf "$TMP/$BUNDLE" -C "$TMP"
mkdir -p "$PKG/libs/win32"
# The self-contained STATIC archive is linked INTO the CFFI extension
# (build_mpt_crypto.py uses extra_objects=[mpt-crypto-static.lib]); no DLL is
# shipped or loaded at runtime. The manifest lists the Win32 system libs to
# co-link.
if [ -f "$TMP/win32-x86-64/mpt-crypto-static.lib" ]; then
  cp "$TMP/win32-x86-64/mpt-crypto-static.lib" "$PKG/libs/win32/"
  cp "$TMP/win32-x86-64/mpt-crypto-static.link-libs.txt" "$PKG/libs/win32/"
else
  echo "ERROR: mpt-crypto-static.lib (self-contained static archive) missing from" >&2
  echo "the natives bundle; the CFFI extension cannot link on Windows without it." >&2
  echo "Use an mpt-crypto release whose win32-x86-64 bundle includes it." >&2
  exit 1
fi

echo "==> Staged library:"
find "$PKG/libs" -type f | sort
