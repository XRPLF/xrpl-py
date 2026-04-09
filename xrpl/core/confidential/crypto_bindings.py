"""
Low-level bindings to the mpt-crypto C library.

This module handles importing the compiled C extension and provides
graceful error handling when the extension is not available.

The mpt-crypto library is distributed as a self-contained shared library
(.so/.dylib/.dll) with secp256k1 and OpenSSL statically linked in.
A thin CFFI extension (_mpt_crypto) is compiled at build time to provide
the Python bindings; it dynamically links to the shared library at runtime.
"""

import ctypes
import glob
import importlib.util
import os
import platform

# Find the compiled C extension in the current directory without modifying sys.path
# This avoids polluting sys.path with this directory which contains utils.py
# that could shadow the tests/unit/utils package during test discovery.
_current_dir = os.path.dirname(os.path.abspath(__file__))
_import_error = None
MPT_CRYPTO_AVAILABLE = False
ffi = None
lib = None


def _preload_shared_library():
    """
    Pre-load the mpt-crypto shared library so it's available when
    the CFFI extension is imported.  On macOS/Linux the rpath compiled
    into the CFFI extension should handle this, but on Windows (and as
    a fallback) we load it explicitly.
    """
    system = platform.system().lower()
    if system == "darwin":
        lib_subdir, lib_name = "darwin", "libmpt-crypto.dylib"
    elif system == "linux":
        lib_subdir, lib_name = "linux", "libmpt-crypto.so"
    elif system == "windows" or system.startswith("win"):
        lib_subdir, lib_name = "win32", "mpt-crypto.dll"
    else:
        return  # unsupported, let it fail later with a clear error

    lib_path = os.path.join(_current_dir, "libs", lib_subdir, lib_name)
    if os.path.exists(lib_path):
        try:
            ctypes.cdll.LoadLibrary(lib_path)
        except OSError:
            pass  # will surface as an ImportError later


# Pre-load before attempting to import the CFFI extension
_preload_shared_library()


def _find_extension_path():
    """Find the compiled C extension file."""
    for ext in [".so", ".pyd", ".dylib"]:
        candidate = os.path.join(_current_dir, f"_mpt_crypto{ext}")
        if os.path.exists(candidate):
            return candidate
        # Also check for platform-specific extensions like .cpython-39-darwin.so
        candidates = glob.glob(os.path.join(_current_dir, f"_mpt_crypto*{ext}"))
        if candidates:
            return candidates[0]
    return None


def _load_extension():
    """Try to load the mpt_crypto extension."""
    global ffi, lib, MPT_CRYPTO_AVAILABLE, _import_error

    # First try direct import (works if on sys.path or installed)
    try:
        from _mpt_crypto import ffi as _ffi
        from _mpt_crypto import lib as _lib

        ffi = _ffi
        lib = _lib
        MPT_CRYPTO_AVAILABLE = True
        return
    except ImportError:
        pass

    # Try to load from the current directory using importlib
    ext_path = _find_extension_path()
    if ext_path:
        try:
            spec = importlib.util.spec_from_file_location("_mpt_crypto", ext_path)
            if spec and spec.loader:
                _mpt_crypto = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(_mpt_crypto)
                ffi = _mpt_crypto.ffi
                lib = _mpt_crypto.lib
                MPT_CRYPTO_AVAILABLE = True
                return
        except Exception as exc:
            _import_error = exc

    # If we get here, the extension is not available
    MPT_CRYPTO_AVAILABLE = False


# Try to load the extension
_load_extension()


# Provide fallback objects if not available
if not MPT_CRYPTO_AVAILABLE:

    def _raise_not_available(*_args, **_kwargs):
        raise ImportError(
            "\n"
            "Confidential MPT support is not available.\n"
            "\n"
            "To enable confidential MPT features, run the setup script:\n"
            "  python -m xrpl.core.confidential.setup\n"
            "\n"
            "Or manually build the C extension:\n"
            "  python xrpl/core/confidential/build_mpt_crypto.py\n"
            "\n"
            f"Original error: {_import_error}\n"
        )

    # Create dummy objects that will raise the error when accessed
    class _DummyFFI:
        def __getattr__(self, name):
            _raise_not_available()

    class _DummyLib:
        def __getattr__(self, name):
            _raise_not_available()

    ffi = _DummyFFI()
    lib = _DummyLib()

# Constants (only set if library is available)
if MPT_CRYPTO_AVAILABLE:
    SECP256K1_CONTEXT_SIGN = lib.SECP256K1_CONTEXT_SIGN
    SECP256K1_CONTEXT_VERIFY = lib.SECP256K1_CONTEXT_VERIFY
    SECP256K1_EC_COMPRESSED = lib.SECP256K1_EC_COMPRESSED
    SECP256K1_EC_UNCOMPRESSED = lib.SECP256K1_EC_UNCOMPRESSED
else:
    SECP256K1_CONTEXT_SIGN = None
    SECP256K1_CONTEXT_VERIFY = None
    SECP256K1_EC_COMPRESSED = None
    SECP256K1_EC_UNCOMPRESSED = None

__all__ = [
    "ffi",
    "lib",
    "MPT_CRYPTO_AVAILABLE",
    "SECP256K1_CONTEXT_SIGN",
    "SECP256K1_CONTEXT_VERIFY",
    "SECP256K1_EC_COMPRESSED",
    "SECP256K1_EC_UNCOMPRESSED",
]
