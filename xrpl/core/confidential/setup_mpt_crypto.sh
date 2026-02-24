#!/bin/bash
# Setup script for MPT crypto binaries for local development
#
# This script helps developers set up the MPT crypto binaries needed for
# confidential MPT features. It provides two options:
# 1. Download pre-built binaries from the latest CI run
# 2. Build binaries locally using the same process as CI
#
# Usage:
#   ./xrpl/core/confidential/setup_mpt_crypto.sh [download|build]
#
# If no argument is provided, it will prompt you to choose.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
LIBS_DIR="$SCRIPT_DIR/libs"
INCLUDE_DIR="$SCRIPT_DIR/include"

# Detect platform
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
    Darwin*)
        PLATFORM="darwin"
        LIB_SUBDIR="darwin"
        ;;
    Linux*)
        PLATFORM="linux"
        LIB_SUBDIR="linux"
        ;;
    MINGW*|MSYS*|CYGWIN*)
        PLATFORM="windows"
        LIB_SUBDIR="win32"
        ;;
    *)
        echo "Unsupported platform: $OS"
        exit 1
        ;;
esac

echo "Detected platform: $PLATFORM ($ARCH)"

download_from_ci() {
    echo ""
    echo "=== Downloading pre-built binaries from CI ==="
    echo ""

    # Check if gh CLI is installed
    if ! command -v gh &> /dev/null; then
        echo "ERROR: GitHub CLI (gh) is not installed."
        echo "Please install it from: https://cli.github.com/"
        echo ""
        echo "Or use the 'build' option to build locally."
        exit 1
    fi

    # Check if gh is authenticated
    if ! gh auth status &> /dev/null; then
        echo "GitHub CLI is not authenticated."
        echo "Please authenticate with GitHub:"
        echo ""
        gh auth login
        echo ""
    fi

    # Create directories
    mkdir -p "$LIBS_DIR/$LIB_SUBDIR"
    mkdir -p "$INCLUDE_DIR"

    # Download artifacts from latest successful workflow run
    echo "Downloading artifacts for $PLATFORM..."

    ARTIFACT_NAME="mpt-crypto-${PLATFORM}-${ARCH}"
    if [ "$PLATFORM" = "darwin" ]; then
        ARTIFACT_NAME="mpt-crypto-darwin-universal"
    fi

    # Use XRPLF/xrpl-py repository
    REPO="XRPLF/xrpl-py"
    echo "Using repository: $REPO"

    cd "$REPO_ROOT"
    gh run download --repo "$REPO" --name "$ARTIFACT_NAME" --dir "$LIBS_DIR/$LIB_SUBDIR" || {
        echo ""
        echo "ERROR: Failed to download artifacts."
        echo "Make sure there's a recent successful build of the workflow."
        echo "Check: https://github.com/XRPLF/xrpl-py/actions/workflows/build_mpt_crypto_libs.yml"
        echo ""
        echo "You can also build locally using: $0 build"
        exit 1
    }
    
    # Download secp256k1_mpt.h header
    echo "Downloading secp256k1_mpt.h header..."
    curl -sSL -o "$INCLUDE_DIR/secp256k1_mpt.h" \
        https://raw.githubusercontent.com/yinyiqian1/mpt-crypto/main/include/secp256k1_mpt.h
    
    echo ""
    echo "✅ Successfully downloaded MPT crypto binaries!"
    echo "   Location: $LIBS_DIR/$LIB_SUBDIR"
}

build_locally() {
    echo ""
    echo "=== Building MPT crypto binaries locally ==="
    echo ""
    echo "This will clone mpt-crypto and build it using the same process as CI."
    echo "This may take several minutes..."
    echo ""
    
    # Check for required tools
    if ! command -v cmake &> /dev/null; then
        echo "ERROR: cmake is not installed. Please install it first."
        exit 1
    fi
    
    if ! command -v conan &> /dev/null; then
        echo "ERROR: conan is not installed. Please install it first:"
        echo "  pip install conan"
        exit 1
    fi
    
    # Create temp directory
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf $TEMP_DIR" EXIT
    
    cd "$TEMP_DIR"
    
    # Clone mpt-crypto
    echo "Cloning mpt-crypto..."
    git clone --depth 1 https://github.com/yinyiqian1/mpt-crypto.git
    cd mpt-crypto
    
    # Build based on platform
    case "$PLATFORM" in
        darwin|linux)
            echo "Building static libraries with -fPIC..."
            conan install . --build=missing -s build_type=Release
            cmake -S . -B build \
                -DCMAKE_BUILD_TYPE=Release \
                -DBUILD_SHARED_LIBS=OFF \
                -DCMAKE_POSITION_INDEPENDENT_CODE=ON
            cmake --build build --config Release
            
            # Copy libraries
            mkdir -p "$LIBS_DIR/$LIB_SUBDIR"
            cp build/libmpt-crypto.a "$LIBS_DIR/$LIB_SUBDIR/"
            find ~/.conan2 -name "libsecp256k1.a" -exec cp {} "$LIBS_DIR/$LIB_SUBDIR/" \;
            ;;
        windows)
            echo "Building static libraries for Windows..."
            echo "Note: Windows builds are complex. Consider downloading from CI instead."
            exit 1
            ;;
    esac
    
    # Copy header
    mkdir -p "$INCLUDE_DIR"
    cp include/secp256k1_mpt.h "$INCLUDE_DIR/"
    
    echo ""
    echo "✅ Successfully built MPT crypto binaries!"
    echo "   Location: $LIBS_DIR/$LIB_SUBDIR"
}

# Main script
if [ $# -eq 0 ]; then
    echo ""
    echo "MPT Crypto Setup for Local Development"
    echo "======================================="
    echo ""
    echo "Choose an option:"
    echo "  1) Download pre-built binaries from CI (recommended)"
    echo "  2) Build locally from source"
    echo ""
    read -p "Enter choice [1-2]: " choice

    case $choice in
        1) download_from_ci ;;
        2) build_locally ;;
        *) echo "Invalid choice"; exit 1 ;;
    esac
else
    case "$1" in
        download) download_from_ci ;;
        build) build_locally ;;
        *)
            echo "Usage: $0 [download|build]"
            exit 1
            ;;
    esac
fi

echo ""
echo "Next steps:"
echo "  1. Build the Python extension: poetry run python xrpl/core/confidential/build_mpt_crypto.py"
echo "  2. Install with confidential extras: poetry install --extras confidential"
echo "  3. Run tests: poetry run python -m unittest discover xrpl/core/confidential/tests/"
echo ""

