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
    Create a Pedersen commitment using the utility layer: PC = amount*G + blinding_factor*H

    Args:
        ctx: Ignored (kept for backward compatibility). Uses mpt_secp256k1_context().
        amount: The amount to commit to (uint64)
        blinding_factor: 64-char hex string (32-byte blinding factor)

    Returns:
        66-char hex string (33-byte compressed commitment point)
    """
    # Convert blinding factor from hex
    blinding_bytes = bytes.fromhex(blinding_factor)
    if len(blinding_bytes) != 32:
        raise ValueError("blinding_factor must be 32 bytes")

    # Create commitment using utility layer
    commitment = ffi.new("unsigned char[33]")
    result = lib.mpt_get_pedersen_commitment(amount, blinding_bytes, commitment)
    if result != 0:
        raise RuntimeError("Failed to create Pedersen commitment")

    # Return compressed commitment
    commitment_bytes = bytes(commitment[0:33])
    return commitment_bytes.hex().upper()


def create_bulletproof(
    ctx, amount: int, blinding_factor: str, pk_base_uncompressed: str, context_id: str = None
) -> str:
    """
    Create a Bulletproof range proof using the aggregated API (m=1).

    Args:
        amount: The amount to prove (uint64)
        blinding_factor: 64-char hex string (32-byte blinding factor)
        pk_base_uncompressed: 128-char hex string (64-byte H generator, X || Y)
        context_id: Optional 64-char hex string (32-byte context ID). If None, uses zeros.

    Returns:
        Variable-length hex string (proof, typically ~1024 bytes)
    """
    # Convert inputs from hex
    blinding_bytes = bytes.fromhex(blinding_factor)
    pk_base_bytes = bytes.fromhex(pk_base_uncompressed)

    # Generate or use provided context_id
    if context_id is None:
        context_id_bytes = b"\x00" * 32
    else:
        context_id_bytes = bytes.fromhex(context_id)
        if len(context_id_bytes) != 32:
            raise ValueError("context_id must be 32 bytes")

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

    # Create bulletproof using aggregated API with m=1
    proof = ffi.new("unsigned char[4096]")  # Max proof size for aggregated
    proof_len = ffi.new("size_t *", 4096)

    # Prepare arrays for aggregated API (single value)
    values = ffi.new("uint64_t[1]")
    values[0] = amount

    result = lib.secp256k1_bulletproof_prove_agg(
        ctx, proof, proof_len, values, blinding_bytes, 1, pk_base, context_id_bytes
    )
    if result != 1:
        raise RuntimeError("Failed to create bulletproof")

    return bytes(proof[0 : proof_len[0]]).hex().upper()


def verify_bulletproof(
    ctx, proof: str, commitment: str, pk_base_uncompressed: str, context_id: str = None
) -> bool:
    """
    Verify a Bulletproof range proof using the aggregated API (m=1).

    Args:
        proof: Variable-length hex string (proof bytes)
        commitment: 128-char hex string (64-byte Pedersen commitment, X || Y)
        pk_base_uncompressed: 128-char hex string (64-byte H generator, X || Y)
        context_id: Optional 64-char hex string (32-byte context ID). If None, uses zeros.

    Returns:
        True if proof is valid, False otherwise
    """
    # Convert hex strings to bytes
    proof_bytes = bytes.fromhex(proof)
    commitment_bytes = bytes.fromhex(commitment)
    pk_base_bytes = bytes.fromhex(pk_base_uncompressed)

    # Generate or use provided context_id
    if context_id is None:
        context_id_bytes = b"\x00" * 32
    else:
        context_id_bytes = bytes.fromhex(context_id)
        if len(context_id_bytes) != 32:
            raise ValueError("context_id must be 32 bytes")

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

    # Generate generator vectors for n = 64*m = 64*1 = 64
    n = 64
    G_vec = ffi.new("secp256k1_pubkey[64]")
    H_vec = ffi.new("secp256k1_pubkey[64]")

    result = lib.secp256k1_mpt_get_generator_vector(ctx, G_vec, n, b"G", 1)
    if result != 1:
        raise RuntimeError("Failed to generate G vector")

    result = lib.secp256k1_mpt_get_generator_vector(ctx, H_vec, n, b"H", 1)
    if result != 1:
        raise RuntimeError("Failed to generate H vector")

    # Prepare commitment array for aggregated API (single commitment)
    commitment_vec = ffi.new("secp256k1_pubkey[1]")
    commitment_vec[0] = commitment_pk[0]

    # Verify bulletproof using aggregated API with m=1
    result = lib.secp256k1_bulletproof_verify_agg(
        ctx,
        G_vec,
        H_vec,
        proof_bytes,
        len(proof_bytes),
        commitment_vec,
        1,
        pk_base,
        context_id_bytes,
    )

    return result == 1
