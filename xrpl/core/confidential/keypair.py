"""
Keypair generation and Schnorr proof of knowledge functions.

This module provides functions for generating ElGamal keypairs and
creating/verifying Schnorr proofs of knowledge.
"""

import secrets
from typing import Optional, Tuple

from xrpl.core.confidential.crypto_bindings import SECP256K1_EC_UNCOMPRESSED, ffi, lib

# Size constants
PRIVKEY_SIZE = 32
PUBKEY_UNCOMPRESSED_SIZE = 64
SCHNORR_PROOF_SIZE = 65
CONTEXT_ID_SIZE = 32


def generate_keypair(ctx) -> Tuple[str, str]:
    """
    Generate an ElGamal keypair.

    Returns:
        Tuple of (privkey, pubkey_uncompressed) as hex strings:
        - privkey: 64-char hex string (32 bytes)
        - pubkey_uncompressed: 128-char hex string (64 bytes, X || Y coordinates)
    """
    privkey = ffi.new("unsigned char[32]")
    pubkey = ffi.new("secp256k1_pubkey *")

    result = lib.secp256k1_elgamal_generate_keypair(ctx, privkey, pubkey)
    if result != 1:
        raise RuntimeError("Failed to generate keypair")

    # Serialize public key to uncompressed format (64 bytes)
    output = ffi.new("unsigned char[65]")  # 65 for uncompressed with prefix
    outputlen = ffi.new("size_t *", 65)

    result = lib.secp256k1_ec_pubkey_serialize(
        ctx, output, outputlen, pubkey, SECP256K1_EC_UNCOMPRESSED
    )
    if result != 1:
        raise RuntimeError("Failed to serialize public key")

    # Return private key and public key WITHOUT the 0x04 prefix (just X||Y)
    privkey_bytes = bytes(privkey[0:32])
    pubkey_bytes = bytes(output[1:65])  # Skip the 0x04 prefix

    # Convert to hex strings
    return privkey_bytes.hex().upper(), pubkey_bytes.hex().upper()


def generate_keypair_with_pok(
    ctx, context_id: Optional[str] = None
) -> Tuple[str, str, str]:
    """
    Generate an ElGamal keypair with a Schnorr proof of knowledge.

    Args:
        context_id: Optional 64-char hex string (32-byte context ID).
                   If not provided, a random one is generated.

    Returns:
        Tuple of (privkey, pubkey_uncompressed, proof) as hex strings
    """
    privkey, pubkey = generate_keypair(ctx)

    if context_id is None:
        context_id = secrets.token_bytes(32).hex().upper()

    proof = generate_pok(ctx, privkey, pubkey, context_id)

    return privkey, pubkey, proof


def generate_pok(ctx, privkey: str, pubkey_uncompressed: str, context_id: str) -> str:
    """
    Generate a Schnorr proof of knowledge of the secret key.

    Args:
        privkey: 64-char hex string (32-byte private key)
        pubkey_uncompressed: 128-char hex string (64-byte public key, X || Y)
        context_id: 64-char hex string (32-byte context ID)

    Returns:
        130-char hex string (65-byte Schnorr proof)
    """
    # Convert hex strings to bytes
    privkey_bytes = bytes.fromhex(privkey)
    pubkey_bytes = bytes.fromhex(pubkey_uncompressed)
    context_id_bytes = bytes.fromhex(context_id)

    if len(privkey_bytes) != 32:
        raise ValueError("privkey must be 32 bytes")
    if len(pubkey_bytes) != 64:
        raise ValueError("pubkey must be 64 bytes (uncompressed, X || Y)")
    if len(context_id_bytes) != 32:
        raise ValueError("context_id must be 32 bytes")

    # Parse public key (add 0x04 prefix for uncompressed format)
    pk_with_prefix = b"\x04" + pubkey_bytes
    pubkey_parsed = ffi.new("secp256k1_pubkey *")
    result = lib.secp256k1_ec_pubkey_parse(ctx, pubkey_parsed, pk_with_prefix, 65)
    if result != 1:
        raise RuntimeError("Failed to parse public key")

    # Generate Schnorr proof
    proof = ffi.new("unsigned char[65]")
    result = lib.secp256k1_mpt_pok_sk_prove(
        ctx, proof, pubkey_parsed, privkey_bytes, context_id_bytes
    )
    if result != 1:
        raise RuntimeError("Failed to generate Schnorr proof")

    return bytes(proof[0:65]).hex().upper()


def verify_pok(ctx, pubkey_uncompressed: str, proof: str, context_id: str) -> bool:
    """
    Verify a Schnorr proof of knowledge of secret key.

    Args:
        pubkey_uncompressed: 128-char hex string (64-byte public key, X || Y)
        proof: 130-char hex string (65-byte Schnorr proof)
        context_id: 64-char hex string (32-byte context ID)

    Returns:
        True if proof is valid, False otherwise
    """
    # Convert hex strings to bytes
    pubkey_bytes = bytes.fromhex(pubkey_uncompressed)
    proof_bytes = bytes.fromhex(proof)
    context_id_bytes = bytes.fromhex(context_id)

    if len(pubkey_bytes) != PUBKEY_UNCOMPRESSED_SIZE:
        raise ValueError(f"pubkey must be {PUBKEY_UNCOMPRESSED_SIZE} bytes")
    if len(proof_bytes) != SCHNORR_PROOF_SIZE:
        raise ValueError(f"proof must be {SCHNORR_PROOF_SIZE} bytes")
    if len(context_id_bytes) != CONTEXT_ID_SIZE:
        raise ValueError(f"context_id must be {CONTEXT_ID_SIZE} bytes")

    # Parse public key (add 0x04 prefix for uncompressed format)
    pk_with_prefix = b"\x04" + pubkey_bytes
    pubkey_parsed = ffi.new("secp256k1_pubkey *")
    result = lib.secp256k1_ec_pubkey_parse(ctx, pubkey_parsed, pk_with_prefix, 65)
    if result != 1:
        raise RuntimeError("Failed to parse public key")

    # Verify proof
    result = lib.secp256k1_mpt_pok_sk_verify(
        ctx, proof_bytes, pubkey_parsed, context_id_bytes
    )

    return result == 1
