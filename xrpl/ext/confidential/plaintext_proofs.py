"""
Equality plaintext proofs and same plaintext proofs.

This module provides functions for creating and verifying proofs about
plaintext values in ciphertexts (used for clawback and multi-recipient sends).
"""

from xrpl.ext.confidential.crypto_bindings import ffi, lib

# Size constants
PUBKEY_COMPRESSED_SIZE = 33
CONTEXT_ID_SIZE = 32


def create_clawback_proof(
    ctx: object,
    pk_compressed: str,
    c1: str,
    c2: str,
    amount: int,
    private_key: str,
    context_id: str,
) -> str:
    """
    Create a compact sigma proof for ConfidentialMPTClawback using the utility layer.

    Proves that the issuer knows the private key corresponding to the public key
    and that the encrypted amount matches the plaintext amount.

    Args:
        ctx: Ignored (kept for backward compatibility). Uses mpt_secp256k1_context().
        pk_compressed: 66-char hex string (33-byte compressed public key)
        c1: 66-char hex string (33-byte compressed C1 point)
        c2: 66-char hex string (33-byte compressed C2 point)
        amount: The plaintext amount
        private_key: 64-char hex string (32-byte private key)
        context_id: 64-char hex string (32-byte transaction context ID)

    Returns:
        Hex string of compact sigma proof (SECP256K1_COMPACT_CLAWBACK_PROOF_SIZE bytes)
    """
    # Convert hex strings to bytes
    pk_bytes = bytes.fromhex(pk_compressed)
    c1_bytes = bytes.fromhex(c1)
    c2_bytes = bytes.fromhex(c2)
    private_key_bytes = bytes.fromhex(private_key)
    context_id_bytes = bytes.fromhex(context_id)

    if len(c1_bytes) != 33 or len(c2_bytes) != 33:
        raise ValueError("c1 and c2 must be 33 bytes")
    if len(pk_bytes) != 33:
        raise ValueError("pk must be 33 bytes (compressed)")
    if len(private_key_bytes) != 32:
        raise ValueError("private_key must be 32 bytes")
    if len(context_id_bytes) != 32:
        raise ValueError("context_id must be 32 bytes")

    # Create encrypted amount (c1 || c2)
    encrypted_amount = c1_bytes + c2_bytes

    # Generate clawback proof using utility layer
    proof_size = lib.SECP256K1_COMPACT_CLAWBACK_PROOF_SIZE
    proof = ffi.new(f"uint8_t[{proof_size}]")
    result = lib.mpt_get_clawback_proof(
        private_key_bytes,
        pk_bytes,
        context_id_bytes,
        amount,
        encrypted_amount,
        proof,
    )
    if result != 0:
        raise RuntimeError("Failed to create clawback proof")

    return bytes(proof[0:proof_size]).hex().upper()


def verify_clawback_proof(
    ctx: object,
    proof: str,
    amount: int,
    pk_compressed: str,
    ciphertext: str,
    context_id: str,
) -> bool:
    """
    Verify a ConfidentialMPTClawback proof using the utility layer.

    Args:
        ctx: Ignored (kept for backward compatibility). Uses mpt_secp256k1_context().
        proof: Hex string of compact sigma proof
        amount: The amount being clawed back
        pk_compressed: 66-char hex string (33-byte compressed public key)
        ciphertext: 132-char hex string (66-byte ciphertext, c1 || c2)
        context_id: 64-char hex string (32-byte context ID)

    Returns:
        True if proof is valid, False otherwise
    """
    proof_bytes = bytes.fromhex(proof)
    pk_bytes = bytes.fromhex(pk_compressed)
    ciphertext_bytes = bytes.fromhex(ciphertext)
    context_id_bytes = bytes.fromhex(context_id)

    if len(pk_bytes) != PUBKEY_COMPRESSED_SIZE:
        raise ValueError(f"pk must be {PUBKEY_COMPRESSED_SIZE} bytes")
    if len(ciphertext_bytes) != 66:
        raise ValueError("ciphertext must be 66 bytes")
    if len(context_id_bytes) != CONTEXT_ID_SIZE:
        raise ValueError(f"context_id must be {CONTEXT_ID_SIZE} bytes")

    result = lib.mpt_verify_clawback_proof(
        proof_bytes, amount, pk_bytes, ciphertext_bytes, context_id_bytes
    )

    return result == 0


# NOTE: create_same_plaintext_proof_multi / verify_same_plaintext_proof_multi
# were removed: the underlying secp256k1_mpt_*_same_plaintext_multi primitives
# no longer exist in mpt-crypto (see MPT_CRYPTO_VERSION), and the prover path
# uses the bundled mpt_get_confidential_send_proof instead.
