"""
Keypair generation and Schnorr proof of knowledge functions.

This module provides functions for generating ElGamal keypairs and
creating/verifying Schnorr proofs of knowledge.
"""

import secrets
from typing import Optional, Tuple

from xrpl.core.confidential.crypto_bindings import ffi, lib

# Size constants
PRIVKEY_SIZE = 32
PUBKEY_COMPRESSED_SIZE = 33
SCHNORR_PROOF_SIZE = 64
CONTEXT_ID_SIZE = 32


def generate_keypair(ctx=None) -> Tuple[str, str]:
    """
    Generate an ElGamal keypair using the utility layer.

    Args:
        ctx: Ignored (kept for backward compatibility). Uses mpt_secp256k1_context().

    Returns:
        Tuple of (privkey, pubkey_compressed) as hex strings:
        - privkey: 64-char hex string (32 bytes)
        - pubkey_compressed: 66-char hex string (33 bytes, compressed format)
    """
    # Allocate as uint8_t[] to match the pointer type expected by mpt_generate_keypair
    privkey = ffi.new("uint8_t[]", 32)
    pubkey = ffi.new("uint8_t[]", 33)

    result = lib.mpt_generate_keypair(privkey, pubkey)
    if result != 0:
        raise RuntimeError("Failed to generate keypair")

    # Return private key and compressed public key
    privkey_bytes = bytes(privkey[0:32])
    pubkey_bytes = bytes(pubkey[0:33])

    # Convert to hex strings
    return privkey_bytes.hex().upper(), pubkey_bytes.hex().upper()


def generate_keypair_with_pok(
    ctx=None, context_id: Optional[str] = None
) -> Tuple[str, str, str]:
    """
    Generate an ElGamal keypair with a Schnorr proof of knowledge.

    Args:
        ctx: Ignored (kept for backward compatibility). Uses mpt_secp256k1_context().
        context_id: Optional 64-char hex string (32-byte context ID).
                   If not provided, a random one is generated.

    Returns:
        Tuple of (privkey, pubkey_compressed, proof) as hex strings
    """
    privkey, pubkey = generate_keypair(ctx)

    if context_id is None:
        context_id = secrets.token_bytes(32).hex().upper()

    proof = generate_pok(ctx, privkey, pubkey, context_id)

    return privkey, pubkey, proof


def generate_pok(ctx, privkey: str, pubkey_compressed: str, context_id: str) -> str:
    """
    Generate a Schnorr proof of knowledge using the utility layer.

    Args:
        ctx: Ignored (kept for backward compatibility). Uses mpt_secp256k1_context().
        privkey: 64-char hex string (32-byte private key)
        pubkey_compressed: 66-char hex string (33-byte compressed public key)
        context_id: 64-char hex string (32-byte context ID)

    Returns:
        128-char hex string (64-byte Schnorr proof)
    """
    # Convert hex strings to bytes
    privkey_bytes = bytes.fromhex(privkey)
    pubkey_bytes = bytes.fromhex(pubkey_compressed)
    context_id_bytes = bytes.fromhex(context_id)

    if len(privkey_bytes) != 32:
        raise ValueError("privkey must be 32 bytes")
    if len(pubkey_bytes) != 33:
        raise ValueError("pubkey must be 33 bytes (compressed)")
    if len(context_id_bytes) != 32:
        raise ValueError("context_id must be 32 bytes")

    # Generate Schnorr proof using utility layer
    proof = ffi.new("uint8_t[]", 64)
    result = lib.mpt_get_convert_proof(
        pubkey_bytes, privkey_bytes, context_id_bytes, proof
    )
    if result != 0:
        raise RuntimeError("Failed to generate Schnorr proof")

    return bytes(proof[0:64]).hex().upper()


def verify_pok(ctx, pubkey_compressed: str, proof: str, context_id: str) -> bool:
    """
    Verify a Schnorr proof of knowledge of secret key.

    Args:
        ctx: Ignored (kept for backward compatibility). Uses mpt_verify_convert_proof.
        pubkey_compressed: 66-char hex string (33-byte compressed public key)
        proof: 128-char hex string (64-byte Schnorr proof)
        context_id: 64-char hex string (32-byte context ID)

    Returns:
        True if proof is valid, False otherwise
    """
    # Convert hex strings to bytes
    pubkey_bytes = bytes.fromhex(pubkey_compressed)
    proof_bytes = bytes.fromhex(proof)
    context_id_bytes = bytes.fromhex(context_id)

    if len(pubkey_bytes) != PUBKEY_COMPRESSED_SIZE:
        raise ValueError(f"pubkey must be {PUBKEY_COMPRESSED_SIZE} bytes")
    if len(proof_bytes) != SCHNORR_PROOF_SIZE:
        raise ValueError(f"proof must be {SCHNORR_PROOF_SIZE} bytes")
    if len(context_id_bytes) != CONTEXT_ID_SIZE:
        raise ValueError(f"context_id must be {CONTEXT_ID_SIZE} bytes")

    # Verify using utility layer (returns 0 on success, -1 on failure)
    result = lib.mpt_verify_convert_proof(proof_bytes, pubkey_bytes, context_id_bytes)

    return result == 0
