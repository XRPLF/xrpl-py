#!/bin/bash
# Setup script for MPT crypto binaries for local development
#
# Downloads pre-built native libraries from XRPLF/mpt-crypto or builds locally.
# The binaries are self-contained shared libraries (.dylib/.so/.dll) with
# secp256k1 and OpenSSL statically linked in.
#
# Usage:
#   ./xrpl/core/confidential/setup_mpt_crypto.sh download             # from latest release
#   ./xrpl/core/confidential/setup_mpt_crypto.sh download --run ID    # from workflow run
#   ./xrpl/core/confidential/setup_mpt_crypto.sh build                # build locally
#
# If no argument is provided, it will prompt you to choose.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
LIBS_DIR="$SCRIPT_DIR/libs"
INCLUDE_DIR="$SCRIPT_DIR/include"
MPT_CRYPTO_REPO="XRPLF/mpt-crypto"

# Detect platform
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
    Darwin*)
        PLATFORM="darwin"
        LIB_SUBDIR="darwin"
        if [ "$ARCH" = "arm64" ]; then
            BUNDLE_SUBDIR="darwin-aarch64"
        else
            BUNDLE_SUBDIR="darwin-x86-64"
        fi
        LIB_NAME="libmpt-crypto.dylib"
        ;;
    Linux*)
        PLATFORM="linux"
        LIB_SUBDIR="linux"
        if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
            BUNDLE_SUBDIR="linux-aarch64"
        else
            BUNDLE_SUBDIR="linux-x86-64"
        fi
        LIB_NAME="libmpt-crypto.so"
        ;;
    MINGW*|MSYS*|CYGWIN*)
        PLATFORM="windows"
        LIB_SUBDIR="win32"
        BUNDLE_SUBDIR="win32-x86-64"
        LIB_NAME="mpt-crypto.dll"
        ;;
    *)
        echo "Unsupported platform: $OS"
        exit 1
        ;;
esac

echo "Detected platform: $PLATFORM ($ARCH)"
echo "  Bundle subdir: $BUNDLE_SUBDIR"
echo "  Local lib dir: $LIB_SUBDIR"

clean_stale_artifacts() {
    # Remove old compiled CFFI extensions and object files so the new library
    # is picked up on the next build. Without this, a stale .cpython-XY.so
    # built against an older library may be loaded instead.
    echo "Cleaning stale build artifacts..."
    rm -f "$SCRIPT_DIR"/_mpt_crypto*.so "$SCRIPT_DIR"/_mpt_crypto*.pyd \
          "$SCRIPT_DIR"/_mpt_crypto*.o  "$SCRIPT_DIR"/_mpt_crypto.c
    # Also clear __pycache__ so cached .pyc files don't reference old modules
    rm -rf "$SCRIPT_DIR"/__pycache__
}

# ──────────────────────────────────────────────────────────────────────────
# Download from XRPLF/mpt-crypto
# ──────────────────────────────────────────────────────────────────────────
download_from_mpt_crypto() {
    local RUN_ID="$1"

    echo ""
    echo "=== Downloading pre-built binaries from $MPT_CRYPTO_REPO ==="
    echo ""

    clean_stale_artifacts

    # Check if gh CLI is installed and authenticated
    if ! command -v gh &> /dev/null; then
        echo "ERROR: GitHub CLI (gh) is not installed."
        echo "Please install it from: https://cli.github.com/"
        exit 1
    fi

    if ! gh auth status &> /dev/null; then
        echo "GitHub CLI is not authenticated. Please run: gh auth login"
        exit 1
    fi

    # Create temp directory for download
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf $TEMP_DIR" EXIT

    if [ -n "$RUN_ID" ]; then
        # ── Download from a specific workflow run ──
        echo "Downloading from workflow run: $RUN_ID"
        echo "Fetching mpt-crypto-natives-bundle artifact..."

        gh run download "$RUN_ID" \
            --repo "$MPT_CRYPTO_REPO" \
            --name mpt-crypto-natives-bundle \
            --dir "$TEMP_DIR" || {
            echo ""
            echo "ERROR: Failed to download bundle from run $RUN_ID."
            echo "Check: https://github.com/$MPT_CRYPTO_REPO/actions/runs/$RUN_ID"
            exit 1
        }

        TARBALL="$TEMP_DIR/mpt-crypto-natives.tar.gz"
    else
        # ── Download from the latest release ──
        echo "Looking for latest release with native binaries..."

        # Find the latest release that has a natives tarball attached
        TARBALL_NAME=$(gh release list --repo "$MPT_CRYPTO_REPO" --limit 10 --json tagName,assets \
            --jq '.[].tagName' | while read -r tag; do
            ASSET=$(gh release view "$tag" --repo "$MPT_CRYPTO_REPO" --json assets \
                --jq '.assets[].name' 2>/dev/null | grep "mpt-crypto-natives" | head -1)
            if [ -n "$ASSET" ]; then
                echo "$tag:$ASSET"
                break
            fi
        done)

        if [ -z "$TARBALL_NAME" ]; then
            echo ""
            echo "No release with native binaries found."
            echo "To download from a specific CI run instead, use:"
            echo "  $0 download --run <RUN_ID>"
            echo ""
            echo "Find run IDs at:"
            echo "  https://github.com/$MPT_CRYPTO_REPO/actions/workflows/build-shared-libs.yml"
            exit 1
        fi

        TAG="${TARBALL_NAME%%:*}"
        ASSET="${TARBALL_NAME##*:}"
        echo "Found release: $TAG (asset: $ASSET)"

        gh release download "$TAG" \
            --repo "$MPT_CRYPTO_REPO" \
            --pattern "$ASSET" \
            --dir "$TEMP_DIR" || {
            echo "ERROR: Failed to download from release $TAG."
            exit 1
        }

        TARBALL="$TEMP_DIR/$ASSET"
    fi

    # ── Extract and install ──
    if [ ! -f "$TARBALL" ]; then
        echo "ERROR: Tarball not found at $TARBALL"
        exit 1
    fi

    echo "Extracting $TARBALL..."
    EXTRACT_DIR="$TEMP_DIR/extracted"
    mkdir -p "$EXTRACT_DIR"
    tar xzf "$TARBALL" -C "$EXTRACT_DIR"

    echo "Contents:"
    find "$EXTRACT_DIR" -type f | sort

    # Copy the shared library for this platform
    # Bundle uses OS-arch dirs (e.g. darwin-aarch64/), xrpl-py uses OS-only (e.g. darwin/)
    SRC_LIB="$EXTRACT_DIR/$BUNDLE_SUBDIR/$LIB_NAME"
    if [ ! -f "$SRC_LIB" ]; then
        echo "ERROR: Library not found: $SRC_LIB"
        echo "Available platform directories:"
        ls -d "$EXTRACT_DIR"/*/ 2>/dev/null || echo "  (none)"
        exit 1
    fi

    mkdir -p "$LIBS_DIR/$LIB_SUBDIR"
    cp "$SRC_LIB" "$LIBS_DIR/$LIB_SUBDIR/"
    echo "Installed: $LIBS_DIR/$LIB_SUBDIR/$LIB_NAME"

    # On Windows, also copy the import library if present
    if [ "$PLATFORM" = "windows" ]; then
        find "$EXTRACT_DIR/$BUNDLE_SUBDIR" -name "*.lib" -exec cp {} "$LIBS_DIR/$LIB_SUBDIR/" \; 2>/dev/null || true
    fi

    # Copy headers
    mkdir -p "$INCLUDE_DIR/utility"
    if [ -d "$EXTRACT_DIR/include" ]; then
        cp "$EXTRACT_DIR/include/secp256k1_mpt.h" "$INCLUDE_DIR/" 2>/dev/null || true
        cp "$EXTRACT_DIR/include/utility/mpt_utility.h" "$INCLUDE_DIR/utility/" 2>/dev/null || true
        echo "Installed headers from bundle"
    else
        echo "WARNING: No headers found in bundle. Fetching from repo..."
        gh api "repos/$MPT_CRYPTO_REPO/contents/include/secp256k1_mpt.h" \
            --jq '.content' | base64 -d > "$INCLUDE_DIR/secp256k1_mpt.h"
        gh api "repos/$MPT_CRYPTO_REPO/contents/include/utility/mpt_utility.h" \
            --jq '.content' | base64 -d > "$INCLUDE_DIR/utility/mpt_utility.h"
        echo "Installed headers from repo"
    fi

    # Verify
    echo ""
    echo "=== Verification ==="
    echo "Library:"
    ls -lh "$LIBS_DIR/$LIB_SUBDIR/$LIB_NAME"
    file "$LIBS_DIR/$LIB_SUBDIR/$LIB_NAME"
    echo ""
    echo "Headers:"
    ls -lh "$INCLUDE_DIR/secp256k1_mpt.h" "$INCLUDE_DIR/utility/mpt_utility.h" 2>/dev/null || echo "  (missing)"

    echo ""
    echo "Done! Binaries installed from $MPT_CRYPTO_REPO."
}

# ──────────────────────────────────────────────────────────────────────────
# Build locally from source
# ──────────────────────────────────────────────────────────────────────────
build_locally() {
    echo ""
    echo "=== Building MPT crypto shared library locally ==="
    echo ""

    clean_stale_artifacts
    echo "This will clone mpt-crypto and build it as a shared library"
    echo "with secp256k1 and OpenSSL statically linked in."
    echo "This may take several minutes..."
    echo ""

    # Check for required tools
    if ! command -v cmake &> /dev/null; then
        echo "ERROR: cmake is not installed. Please install it first."
        exit 1
    fi

    if ! command -v conan &> /dev/null; then
        echo "ERROR: conan is not installed. Please install it first:"
        echo "  pip install 'conan>=2.0.0'"
        exit 1
    fi

    # Ensure Conan profile exists
    conan profile detect --force
    conan remote add --index 0 --force xrplf https://conan.ripplex.io 2>/dev/null || true

    # Create temp directory
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf $TEMP_DIR" EXIT

    cd "$TEMP_DIR"

    # Clone mpt-crypto
    echo "Cloning $MPT_CRYPTO_REPO..."
    git clone --depth 1 "https://github.com/$MPT_CRYPTO_REPO.git"
    cd mpt-crypto

    # Build as shared library with static deps
    case "$PLATFORM" in
        darwin|linux)
            echo "Installing dependencies via Conan..."
            conan install . \
                -of build \
                --build=missing \
                -s build_type=Release \
                -o "&:shared=True" \
                -o "&:tests=False" \
                -o "secp256k1/*:shared=False" \
                -o "secp256k1/*:fPIC=True" \
                -o "openssl/*:shared=False" \
                -o "openssl/*:fPIC=True"

            TOOLCHAIN=$(find build -name "conan_toolchain.cmake" -print -quit)

            # Use Ninja if available, otherwise fall back to Unix Makefiles
            if command -v ninja &> /dev/null; then
                CMAKE_GENERATOR="Ninja"
            else
                CMAKE_GENERATOR="Unix Makefiles"
                echo "Note: Ninja not found, using Make instead."
            fi

            echo "Configuring CMake (generator: $CMAKE_GENERATOR)..."
            cmake -B build -S . \
                -G "$CMAKE_GENERATOR" \
                -DCMAKE_TOOLCHAIN_FILE="$TOOLCHAIN" \
                -DCMAKE_BUILD_TYPE=Release

            echo "Building..."
            cmake --build build --config Release

            # Copy shared library
            mkdir -p "$LIBS_DIR/$LIB_SUBDIR"
            find build -maxdepth 2 -name "$LIB_NAME" -exec cp {} "$LIBS_DIR/$LIB_SUBDIR/" \;
            ;;
        windows)
            echo "Windows local builds are not yet supported."
            echo "Use: $0 download --run <RUN_ID>"
            exit 1
            ;;
    esac

    # Copy headers
    mkdir -p "$INCLUDE_DIR/utility"
    cp include/secp256k1_mpt.h "$INCLUDE_DIR/"
    cp include/utility/mpt_utility.h "$INCLUDE_DIR/utility/"

    echo ""
    echo "Done! Built and installed from source."
    echo "Library: $LIBS_DIR/$LIB_SUBDIR/"
    ls -lh "$LIBS_DIR/$LIB_SUBDIR/"
}

# ──────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────
if [ $# -eq 0 ]; then
    echo ""
    echo "MPT Crypto Setup for Local Development"
    echo "======================================="
    echo "Source: $MPT_CRYPTO_REPO"
    echo ""
    echo "Choose an option:"
    echo "  1) Download pre-built binaries (recommended)"
    echo "  2) Build locally from source"
    echo ""
    read -p "Enter choice [1-2]: " choice

    case $choice in
        1) download_from_mpt_crypto ;;
        2) build_locally ;;
        *) echo "Invalid choice"; exit 1 ;;
    esac
else
    case "$1" in
        download)
            shift
            RUN_ID=""
            while [ $# -gt 0 ]; do
                case "$1" in
                    --run)
                        RUN_ID="$2"
                        shift 2
                        ;;
                    *)
                        echo "Unknown option: $1"
                        echo "Usage: $0 download [--run RUN_ID]"
                        exit 1
                        ;;
                esac
            done
            download_from_mpt_crypto "$RUN_ID"
            ;;
        build)
            build_locally
            ;;
        *)
            echo "Usage: $0 [download [--run RUN_ID] | build]"
            exit 1
            ;;
    esac
fi

echo ""
echo "Next steps:"
echo "  1. Build the CFFI extension:"
echo "       poetry run python xrpl/core/confidential/build_mpt_crypto.py"
echo "  2. Run tests:"
echo "       poetry run python -m unittest tests.unit.core.confidential.test_utility_layer -v"
echo ""
