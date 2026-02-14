"""
Low-level bindings to the mpt-crypto C library.

This module handles importing the compiled C extension and provides
graceful error handling when the extension is not available.
"""

import os
import sys

# Add the current directory to sys.path to allow importing the compiled C extension
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

try:
    from _mpt_crypto import ffi, lib

    MPT_CRYPTO_AVAILABLE = True
except ImportError as exc:
    MPT_CRYPTO_AVAILABLE = False
    _import_error = exc

    # Provide a helpful error message
    def _raise_not_available(*args, **kwargs):
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
        ) from _import_error

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
