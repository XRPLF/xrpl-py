"""
Python bindings for mpt-crypto C library using cffi.

This module provides a clean Python API for the mpt-crypto library,
which implements cryptographic operations for confidential MPT transactions.
"""

from typing import TYPE_CHECKING, List

from xrpl.ext.confidential.crypto_bindings import MPT_CRYPTO_AVAILABLE
from xrpl.ext.confidential.main import MPTCrypto

# The transaction builders import the ConfidentialMPT* models from CORE xrpl-py.
# Expose them lazily (PEP 562 __getattr__) so that importing this package — or
# using only the native crypto layer (MPTCrypto / crypto_bindings) — does not
# require a core xrpl-py that ships those models. Calling a builder imports
# transaction_builders at that point (and so needs the models only then). The
# TYPE_CHECKING block keeps the names resolvable for type checkers / IDEs.
if TYPE_CHECKING:
    from xrpl.ext.confidential.transaction_builders import (  # noqa: F401
        decrypt_confidential_balance,
        prepare_confidential_clawback,
        prepare_confidential_clawback_async,
        prepare_confidential_convert,
        prepare_confidential_convert_async,
        prepare_confidential_convert_back,
        prepare_confidential_convert_back_async,
        prepare_confidential_merge_inbox,
        prepare_confidential_merge_inbox_async,
        prepare_confidential_send,
        prepare_confidential_send_async,
    )

_LAZY_BUILDERS = frozenset(
    {
        "decrypt_confidential_balance",
        "prepare_confidential_clawback",
        "prepare_confidential_clawback_async",
        "prepare_confidential_convert",
        "prepare_confidential_convert_async",
        "prepare_confidential_convert_back",
        "prepare_confidential_convert_back_async",
        "prepare_confidential_merge_inbox",
        "prepare_confidential_merge_inbox_async",
        "prepare_confidential_send",
        "prepare_confidential_send_async",
    }
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
    # Transaction builders (resolved lazily via __getattr__)
    "prepare_confidential_convert",
    "prepare_confidential_merge_inbox",
    "prepare_confidential_send",
    "prepare_confidential_convert_back",
    "prepare_confidential_clawback",
    # Async transaction builders (resolved lazily via __getattr__)
    "prepare_confidential_convert_async",
    "prepare_confidential_merge_inbox_async",
    "prepare_confidential_send_async",
    "prepare_confidential_convert_back_async",
    "prepare_confidential_clawback_async",
    # Balance decryption helper (resolved lazily via __getattr__)
    "decrypt_confidential_balance",
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


def __getattr__(name: str) -> object:
    """Lazily import the transaction builders (see note above)."""
    if name in _LAZY_BUILDERS:
        from xrpl.ext.confidential import transaction_builders

        return getattr(transaction_builders, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> List[str]:
    return sorted(__all__)
