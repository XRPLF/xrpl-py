"""
Pedersen commitments and Bulletproof range proofs.

This module provides functions for creating Pedersen commitments and
generating/verifying Bulletproof range proofs.
"""

from xrpl.core.confidential.crypto_bindings import ffi, lib

# Size constants
PUBKEY_UNCOMPRESSED_SIZE = 64
PUBKEY_COMPRESSED_SIZE = 33


def create_pedersen_commitment(ctx, amount: int, blinding_factor: str) -> str:
    """
    Create a Pedersen commitment: PC = amount*G + blinding_factor*H

    Args:
        amount: The amount to commit to (uint64)
        blinding_factor: 64-char hex string (32-byte blinding factor)

    Returns:
        128-char hex string (64-byte uncompressed commitment point, X || Y)
    """
    # Convert blinding factor from hex
    blinding_bytes = bytes.fromhex(blinding_factor)
    if len(blinding_bytes) != 32:
        raise ValueError("blinding_factor must be 32 bytes")

    # Create commitment
    commitment = ffi.new("secp256k1_pubkey *")
    result = lib.secp256k1_mpt_pedersen_commit(ctx, commitment, amount, blinding_bytes)
    if result != 1:
        raise RuntimeError("Failed to create Pedersen commitment")

    # Serialize commitment (uncompressed)
    output = ffi.new("unsigned char[65]")
    output_len = ffi.new("size_t *", 65)
    from xrpl.core.confidential.crypto_bindings import SECP256K1_EC_UNCOMPRESSED

    result = lib.secp256k1_ec_pubkey_serialize(
        ctx, output, output_len, commitment, SECP256K1_EC_UNCOMPRESSED
    )
    if result != 1:
        raise RuntimeError("Failed to serialize commitment")

    # Return without 0x04 prefix
    commitment_bytes = bytes(output[1:65])
    return commitment_bytes.hex().upper()


def create_bulletproof(
    ctx, amount: int, blinding_factor: str, pk_base_uncompressed: str
) -> str:
    """
    Create a Bulletproof range proof.

    Args:
        amount: The amount to prove (uint64)
        blinding_factor: 64-char hex string (32-byte blinding factor)
        pk_base_uncompressed: 128-char hex string (64-byte H generator, X || Y)

    Returns:
        Variable-length hex string (proof, typically ~1024 bytes)
    """
    # Convert inputs from hex
    blinding_bytes = bytes.fromhex(blinding_factor)
    pk_base_bytes = bytes.fromhex(pk_base_uncompressed)

    if len(blinding_bytes) != 32:
        raise ValueError("blinding_factor must be 32 bytes")
    if len(pk_base_bytes) != 64:
        raise ValueError("pk_base must be 64 bytes")

    # Parse pk_base (H generator)
    pk_base_with_prefix = b"\x04" + pk_base_bytes
    pk_base = ffi.new("secp256k1_pubkey *")
    result = lib.secp256k1_ec_pubkey_parse(ctx, pk_base, pk_base_with_prefix, 65)
    if result != 1:
        raise RuntimeError("Failed to parse pk_base")

    # Create bulletproof
    proof = ffi.new("unsigned char[2048]")  # Max proof size
    proof_len = ffi.new("size_t *", 2048)
    result = lib.secp256k1_bulletproof_prove(
        ctx, proof, proof_len, amount, blinding_bytes, pk_base, 0
    )
    if result != 1:
        raise RuntimeError("Failed to create bulletproof")

    return bytes(proof[0 : proof_len[0]]).hex().upper()


def verify_bulletproof(
    ctx, proof: str, commitment: str, pk_base_uncompressed: str
) -> bool:
    """
    Verify a Bulletproof range proof.

    Args:
        proof: Variable-length hex string (proof bytes)
        commitment: 128-char hex string (64-byte Pedersen commitment, X || Y)
        pk_base_uncompressed: 128-char hex string (64-byte H generator, X || Y)

    Returns:
        True if proof is valid, False otherwise
    """
    # Convert hex strings to bytes
    proof_bytes = bytes.fromhex(proof)
    commitment_bytes = bytes.fromhex(commitment)
    pk_base_bytes = bytes.fromhex(pk_base_uncompressed)

    if len(commitment_bytes) != PUBKEY_UNCOMPRESSED_SIZE:
        raise ValueError(f"commitment must be {PUBKEY_UNCOMPRESSED_SIZE} bytes")
    if len(pk_base_bytes) != PUBKEY_UNCOMPRESSED_SIZE:
        raise ValueError(f"pk_base must be {PUBKEY_UNCOMPRESSED_SIZE} bytes")

    # Parse commitment
    commitment_with_prefix = b"\x04" + commitment_bytes
    commitment_pk = ffi.new("secp256k1_pubkey *")
    result = lib.secp256k1_ec_pubkey_parse(
        ctx, commitment_pk, commitment_with_prefix, 65
    )
    if result != 1:
        raise RuntimeError("Failed to parse commitment")

    # Parse pk_base
    pk_base_with_prefix = b"\x04" + pk_base_bytes
    pk_base = ffi.new("secp256k1_pubkey *")
    result = lib.secp256k1_ec_pubkey_parse(ctx, pk_base, pk_base_with_prefix, 65)
    if result != 1:
        raise RuntimeError("Failed to parse pk_base")

    # Verify bulletproof
    result = lib.secp256k1_bulletproof_verify(
        ctx, proof_bytes, len(proof_bytes), commitment_pk, pk_base
    )

    return result == 1
