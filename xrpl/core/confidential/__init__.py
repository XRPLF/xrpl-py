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

# Size constants (matching mpt_utility.h)
PRIVKEY_SIZE = 32
PUBKEY_COMPRESSED_SIZE = 33
SCHNORR_PROOF_SIZE = 64
BLINDING_FACTOR_SIZE = 32
CONTEXT_ID_SIZE = 32
ACCOUNT_ID_SIZE = 20
MPT_ISSUANCE_ID_SIZE = 24
ELGAMAL_CIPHER_SIZE = 33
ELGAMAL_TOTAL_SIZE = 66
PEDERSEN_COMMIT_SIZE = 33
SINGLE_BULLETPROOF_SIZE = 688
DOUBLE_BULLETPROOF_SIZE = 754

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
    "PUBKEY_COMPRESSED_SIZE",
    "SCHNORR_PROOF_SIZE",
    "BLINDING_FACTOR_SIZE",
    "CONTEXT_ID_SIZE",
    "ACCOUNT_ID_SIZE",
    "MPT_ISSUANCE_ID_SIZE",
    "ELGAMAL_CIPHER_SIZE",
    "ELGAMAL_TOTAL_SIZE",
    "PEDERSEN_COMMIT_SIZE",
    "SINGLE_BULLETPROOF_SIZE",
    "DOUBLE_BULLETPROOF_SIZE",
]
