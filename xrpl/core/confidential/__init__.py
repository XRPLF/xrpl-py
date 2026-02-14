"""
Python bindings for mpt-crypto C library using cffi.

This module provides a clean Python API for the mpt-crypto library,
which implements cryptographic operations for confidential MPT transactions.
"""

from xrpl.core.confidential.crypto_bindings import MPT_CRYPTO_AVAILABLE
from xrpl.core.confidential.main import MPTCrypto
from xrpl.core.confidential.transaction_builders import (
    prepare_confidential_clawback,
    prepare_confidential_convert,
    prepare_confidential_convert_back,
    prepare_confidential_merge_inbox,
    prepare_confidential_send,
)

# Size constants
PRIVKEY_SIZE = 32
PUBKEY_UNCOMPRESSED_SIZE = 64
PUBKEY_COMPRESSED_SIZE = 33
SCHNORR_PROOF_SIZE = 65
BLINDING_FACTOR_SIZE = 32
CONTEXT_ID_SIZE = 32
ACCOUNT_ID_SIZE = 20
MPT_ISSUANCE_ID_SIZE = 24
EQUALITY_PROOF_SIZE = 98
SAME_PLAINTEXT_PROOF_SIZE = 261

__all__ = [
    # Core crypto class
    "MPTCrypto",
    "MPT_CRYPTO_AVAILABLE",
    # Transaction builders
    "prepare_confidential_convert",
    "prepare_confidential_merge_inbox",
    "prepare_confidential_send",
    "prepare_confidential_convert_back",
    "prepare_confidential_clawback",
    # Size constants
    "PRIVKEY_SIZE",
    "PUBKEY_UNCOMPRESSED_SIZE",
    "PUBKEY_COMPRESSED_SIZE",
    "SCHNORR_PROOF_SIZE",
    "BLINDING_FACTOR_SIZE",
    "CONTEXT_ID_SIZE",
    "ACCOUNT_ID_SIZE",
    "MPT_ISSUANCE_ID_SIZE",
    "EQUALITY_PROOF_SIZE",
    "SAME_PLAINTEXT_PROOF_SIZE",
]
