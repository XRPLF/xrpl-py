"""Canonical sizes for Confidential MPT (XLS-0096) fields and zero-knowledge proofs.

Single source of truth for the model-layer length validations shared by the
``ConfidentialMPT*`` transactions. The byte sizes mirror the mpt-crypto library
constants (``SECP256K1_*_PROOF_SIZE`` / ``kMPT_*``); the native integration test
``tests/unit/core/confidential/test_utility_layer`` cross-checks them against the
compiled library so the two cannot silently drift across a version bump.

This module is pure-Python and importable without the native extension.
"""

from typing import Final

# --- Primitive byte sizes (mirror mpt_protocol.h) ---
SCHNORR_PROOF_SIZE: Final[int] = 64
ELGAMAL_TOTAL_SIZE: Final[int] = 66
PEDERSEN_COMMIT_SIZE: Final[int] = 33
BLINDING_FACTOR_SIZE: Final[int] = 32
PUBKEY_COMPRESSED_SIZE: Final[int] = 33

# --- Compact sigma + bulletproof component byte sizes ---
COMPACT_CLAWBACK_PROOF_SIZE: Final[int] = 64
COMPACT_CONVERTBACK_PROOF_SIZE: Final[int] = 128
COMPACT_STANDARD_PROOF_SIZE: Final[int] = 192
SINGLE_BULLETPROOF_SIZE: Final[int] = 688
DOUBLE_BULLETPROOF_SIZE: Final[int] = 754

# --- Composite ZKProof byte sizes (what the ZKProof field carries) ---
CLAWBACK_PROOF_SIZE: Final[int] = COMPACT_CLAWBACK_PROOF_SIZE  # 64
CONVERT_BACK_PROOF_SIZE: Final[int] = (
    COMPACT_CONVERTBACK_PROOF_SIZE + SINGLE_BULLETPROOF_SIZE
)  # 816
SEND_PROOF_SIZE: Final[int] = (
    COMPACT_STANDARD_PROOF_SIZE + DOUBLE_BULLETPROOF_SIZE
)  # 946

# --- Hex-character lengths used by model validation (2 hex chars per byte) ---
HOLDER_ENCRYPTION_KEY_LENGTH: Final[int] = PUBKEY_COMPRESSED_SIZE * 2  # 66
BLINDING_FACTOR_LENGTH: Final[int] = BLINDING_FACTOR_SIZE * 2  # 64
SCHNORR_PROOF_LENGTH: Final[int] = SCHNORR_PROOF_SIZE * 2  # 128
CIPHERTEXT_LENGTH: Final[int] = ELGAMAL_TOTAL_SIZE * 2  # 132
COMMITMENT_LENGTH: Final[int] = PEDERSEN_COMMIT_SIZE * 2  # 66
CLAWBACK_PROOF_LENGTH: Final[int] = CLAWBACK_PROOF_SIZE * 2  # 128
SEND_PROOF_LENGTH: Final[int] = SEND_PROOF_SIZE * 2  # 1892
CONVERT_BACK_PROOF_LENGTH: Final[int] = CONVERT_BACK_PROOF_SIZE * 2  # 1632
