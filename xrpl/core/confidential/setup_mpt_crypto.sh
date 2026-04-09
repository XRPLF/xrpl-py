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
    mkdir -p "$INCLUDE_DIR/utility"

    # Download artifacts from latest successful workflow run
    echo "Downloading artifacts for $PLATFORM ($ARCH)..."

    # Determine artifact name based on platform and architecture
    case "$PLATFORM" in
        darwin)
            if [ "$ARCH" = "arm64" ]; then
                ARTIFACT_NAME="mpt-crypto-darwin-arm64"
            else
                ARTIFACT_NAME="mpt-crypto-darwin-x86_64"
            fi
            ;;
        linux)
            ARTIFACT_NAME="mpt-crypto-linux-x86_64"
            ;;
        windows)
            ARTIFACT_NAME="mpt-crypto-win32-x86_64"
            ;;
    esac

    # Use XRPLF/xrpl-py repository
    REPO="XRPLF/xrpl-py"
    echo "Using repository: $REPO"
    echo "Artifact: $ARTIFACT_NAME"

    # Download to temp directory first to handle nested structure
    TEMP_DOWNLOAD=$(mktemp -d)
    trap "rm -rf $TEMP_DOWNLOAD" EXIT

    cd "$REPO_ROOT"
    gh run download --repo "$REPO" --name "$ARTIFACT_NAME" --dir "$TEMP_DOWNLOAD" || {
        echo ""
        echo "ERROR: Failed to download artifacts."
        echo "Make sure there's a recent successful build of the workflow."
        echo "Check: https://github.com/XRPLF/xrpl-py/actions/workflows/build_mpt_crypto_libs.yml"
        echo ""
        echo "You can also build locally using: $0 build"
        exit 1
    }

    # Debug: Show what was downloaded
    echo "Downloaded files:"
    find "$TEMP_DOWNLOAD" -type f

    # Copy shared library to correct location
    echo "Copying shared library..."
    if [ "$PLATFORM" = "windows" ]; then
        find "$TEMP_DOWNLOAD" -name "*.dll" -exec cp {} "$LIBS_DIR/$LIB_SUBDIR/" \;
        # Also copy import library if present
        find "$TEMP_DOWNLOAD" -name "*.lib" -exec cp {} "$LIBS_DIR/$LIB_SUBDIR/" \; 2>/dev/null || true
    elif [ "$PLATFORM" = "darwin" ]; then
        find "$TEMP_DOWNLOAD" -name "*.dylib" -exec cp {} "$LIBS_DIR/$LIB_SUBDIR/" \;
    else
        find "$TEMP_DOWNLOAD" -name "*.so" -exec cp {} "$LIBS_DIR/$LIB_SUBDIR/" \;
    fi

    # Copy headers to correct location
    echo "Copying headers..."
    find "$TEMP_DOWNLOAD" -name "secp256k1_mpt.h" -exec cp {} "$INCLUDE_DIR/" \;
    find "$TEMP_DOWNLOAD" -name "secp256k1.h" -exec cp {} "$INCLUDE_DIR/" \; 2>/dev/null || true
    find "$TEMP_DOWNLOAD" -name "mpt_utility.h" -exec cp {} "$INCLUDE_DIR/utility/" \;

    # Verify files were copied
    echo ""
    echo "Verifying installation..."
    echo "Libraries in $LIBS_DIR/$LIB_SUBDIR:"
    ls -la "$LIBS_DIR/$LIB_SUBDIR/"

    echo ""
    echo "Headers in $INCLUDE_DIR:"
    ls -la "$INCLUDE_DIR/"

    echo ""
    echo "✅ Successfully downloaded MPT crypto binaries!"
    echo "   Libraries: $LIBS_DIR/$LIB_SUBDIR"
    echo "   Headers: $INCLUDE_DIR"
}

build_locally() {
    echo ""
    echo "=== Building MPT crypto shared library locally ==="
    echo ""
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
    conan remote add --index 0 xrplf https://conan.ripplex.io 2>/dev/null || true

    # Create temp directory
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf $TEMP_DIR" EXIT

    cd "$TEMP_DIR"

    # Clone mpt-crypto
    echo "Cloning mpt-crypto (mpt-utility branch)..."
    git clone --depth 1 https://github.com/XRPLF/mpt-crypto.git
    cd mpt-crypto

    # Build as shared library with static deps (matching CI / Java approach)
    case "$PLATFORM" in
        darwin|linux)
            CONAN_ARCH_ARGS=""
            CMAKE_ARCH_ARGS=""
            if [ "$PLATFORM" = "darwin" ]; then
                if [ "$ARCH" = "arm64" ]; then
                    CONAN_ARCH_ARGS="-s arch=armv8"
                    CMAKE_ARCH_ARGS="-DCMAKE_OSX_ARCHITECTURES=arm64"
                else
                    CONAN_ARCH_ARGS="-s arch=x86_64"
                    CMAKE_ARCH_ARGS="-DCMAKE_OSX_ARCHITECTURES=x86_64"
                fi
            fi

            echo "Installing dependencies via Conan..."
            conan install . \
                -of build \
                -b missing \
                -s build_type=Release \
                -o "&:shared=True" \
                -o "&:tests=False" \
                -o "secp256k1/*:shared=False" \
                -o "secp256k1/*:fPIC=True" \
                -o "openssl/*:shared=False" \
                -o "openssl/*:fPIC=True" \
                $CONAN_ARCH_ARGS

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
                -DCMAKE_BUILD_TYPE=Release \
                $CMAKE_ARCH_ARGS

            echo "Building..."
            cmake --build build --config Release

            # Copy shared library
            mkdir -p "$LIBS_DIR/$LIB_SUBDIR"
            if [ "$PLATFORM" = "darwin" ]; then
                find build -name "libmpt-crypto.dylib" -exec cp {} "$LIBS_DIR/$LIB_SUBDIR/" \;
            else
                find build -name "libmpt-crypto.so" -exec cp {} "$LIBS_DIR/$LIB_SUBDIR/" \;
            fi
            ;;
        windows)
            echo "Building shared library for Windows..."
            echo "Note: Windows local builds are complex. Consider downloading from CI instead."
            exit 1
            ;;
    esac

    # Copy headers
    mkdir -p "$INCLUDE_DIR"
    mkdir -p "$INCLUDE_DIR/utility"
    cp include/secp256k1_mpt.h "$INCLUDE_DIR/"
    cp include/utility/mpt_utility.h "$INCLUDE_DIR/utility/"

    echo ""
    echo "✅ Successfully built MPT crypto shared library!"
    echo "   Location: $LIBS_DIR/$LIB_SUBDIR"
    ls -lh "$LIBS_DIR/$LIB_SUBDIR/"
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

