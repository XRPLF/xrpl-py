"""
Equality plaintext proofs and same plaintext proofs.

This module provides functions for creating and verifying proofs about
plaintext values in ciphertexts (used for clawback and multi-recipient sends).
"""

from xrpl.core.confidential.crypto_bindings import ffi, lib

# Size constants
PUBKEY_UNCOMPRESSED_SIZE = 64
PUBKEY_COMPRESSED_SIZE = 33
CONTEXT_ID_SIZE = 32


def create_equality_plaintext_proof(
    ctx,
    pk_uncompressed: str,
    c2: str,
    c1: str,
    amount: int,
    blinding_factor: str,
    context_id: str,
) -> str:
    """
    Create an equality proof for ConfidentialMPTClawback.

    Proves that the issuer knows the blinding factor r such that:
    - C1 = r*G
    - C2 = amount*G + r*PK

    This allows the issuer to prove they know the exact encrypted balance
    without revealing the blinding factor.

    Args:
        pk_uncompressed: 128-char hex string (64-byte public key, issuer's)
        c2: 66-char hex string (33-byte compressed C2 point)
        c1: 66-char hex string (33-byte compressed C1 point)
        amount: The plaintext amount
        blinding_factor: 64-char hex string (32-byte blinding factor)
        context_id: 64-char hex string (32-byte transaction context ID)

    Returns:
        196-char hex string (98-byte equality proof)
    """
    # Convert hex strings to bytes
    pk_bytes = bytes.fromhex(pk_uncompressed)
    c2_bytes = bytes.fromhex(c2)
    c1_bytes = bytes.fromhex(c1)
    blinding_bytes = bytes.fromhex(blinding_factor)
    context_id_bytes = bytes.fromhex(context_id)

    if len(c1_bytes) != 33 or len(c2_bytes) != 33:
        raise ValueError("c1 and c2 must be 33 bytes")
    if len(pk_bytes) != 64:
        raise ValueError("pk must be 64 bytes")
    if len(blinding_bytes) != 32:
        raise ValueError("blinding_factor must be 32 bytes")
    if len(context_id_bytes) != 32:
        raise ValueError("context_id must be 32 bytes")

    # Parse points
    c1_pk = ffi.new("secp256k1_pubkey *")
    c2_pk = ffi.new("secp256k1_pubkey *")
    pk = ffi.new("secp256k1_pubkey *")

    lib.secp256k1_ec_pubkey_parse(ctx, c1_pk, c1_bytes, 33)
    lib.secp256k1_ec_pubkey_parse(ctx, c2_pk, c2_bytes, 33)

    pk_with_prefix = b"\x04" + pk_bytes
    lib.secp256k1_ec_pubkey_parse(ctx, pk, pk_with_prefix, 65)

    # Generate equality proof
    # The C library expects (c1, c2, pk_recipient) order
    proof = ffi.new("unsigned char[98]")
    result = lib.secp256k1_equality_plaintext_prove(
        ctx,
        proof,
        c1_pk,
        c2_pk,
        pk,
        amount,
        blinding_bytes,
        context_id_bytes,
    )
    if result != 1:
        raise RuntimeError("Failed to create equality proof")

    return bytes(proof[0:98]).hex().upper()


def verify_equality_plaintext_proof(
    ctx,
    proof: str,
    pk_uncompressed: str,
    c2: str,
    c1: str,
    amount: int,
    context_id: str,
) -> bool:
    """
    Verify an equality plaintext proof (for ConfidentialMPTClawback).

    Args:
        proof: 196-char hex string (98-byte proof)
        pk_uncompressed: 128-char hex string (64-byte public key, X || Y)
        c2: 66-char hex string (33-byte compressed point)
        c1: 66-char hex string (33-byte compressed point)
        amount: The amount being clawed back
        context_id: 64-char hex string (32-byte context ID)

    Returns:
        True if proof is valid, False otherwise
    """
    # Convert hex strings to bytes
    proof_bytes = bytes.fromhex(proof)
    pk_bytes = bytes.fromhex(pk_uncompressed)
    c2_bytes = bytes.fromhex(c2)
    c1_bytes = bytes.fromhex(c1)
    context_id_bytes = bytes.fromhex(context_id)

    if len(proof_bytes) != 98:
        raise ValueError("proof must be 98 bytes")
    if len(pk_bytes) != PUBKEY_UNCOMPRESSED_SIZE:
        raise ValueError(f"pk must be {PUBKEY_UNCOMPRESSED_SIZE} bytes")
    if len(c2_bytes) != PUBKEY_COMPRESSED_SIZE:
        raise ValueError(f"c2 must be {PUBKEY_COMPRESSED_SIZE} bytes")
    if len(c1_bytes) != PUBKEY_COMPRESSED_SIZE:
        raise ValueError(f"c1 must be {PUBKEY_COMPRESSED_SIZE} bytes")
    if len(context_id_bytes) != CONTEXT_ID_SIZE:
        raise ValueError(f"context_id must be {CONTEXT_ID_SIZE} bytes")

    # Parse pk
    pk_with_prefix = b"\x04" + pk_bytes
    pk_pubkey = ffi.new("secp256k1_pubkey *")
    result = lib.secp256k1_ec_pubkey_parse(ctx, pk_pubkey, pk_with_prefix, 65)
    if result != 1:
        raise RuntimeError("Failed to parse pk")

    # Parse c2, c1
    c2_pk = ffi.new("secp256k1_pubkey *")
    c1_pk = ffi.new("secp256k1_pubkey *")
    result = lib.secp256k1_ec_pubkey_parse(ctx, c2_pk, c2_bytes, 33)
    if result != 1:
        raise RuntimeError("Failed to parse c2")
    result = lib.secp256k1_ec_pubkey_parse(ctx, c1_pk, c1_bytes, 33)
    if result != 1:
        raise RuntimeError("Failed to parse c1")

    # Verify proof
    # The C library expects (c1, c2, pk), so pass them in that order
    result = lib.secp256k1_equality_plaintext_verify(
        ctx, proof_bytes, c1_pk, c2_pk, pk_pubkey, amount, context_id_bytes
    )

    return result == 1


def create_same_plaintext_proof_multi(  # noqa: PLR0914
    ctx,
    amount: int,
    ciphertexts: list,  # List of (c1, c2, pk, blinding) tuples (hex strings)
    context_id: str,
) -> str:
    """
    Create a proof that multiple ciphertexts encrypt the same amount.

    Args:
        amount: The common plaintext amount
        ciphertexts: List of (c1, c2, pk_uncompressed, blinding) tuples
            - c1: 66-char hex string (33-byte compressed point)
            - c2: 66-char hex string (33-byte compressed point)
            - pk_uncompressed: 128-char hex string (64-byte public key)
            - blinding: 64-char hex string (32-byte blinding factor)
        context_id: 64-char hex string (32-byte transaction context ID)

    Returns:
        Variable-length hex string proof
    """
    # Convert context_id to bytes
    context_id_bytes = bytes.fromhex(context_id)

    if len(context_id_bytes) != 32:
        raise ValueError("context_id must be 32 bytes")

    n = len(ciphertexts)
    if n < 2:
        raise ValueError("Need at least 2 ciphertexts")

    # Allocate arrays
    R_array = ffi.new(f"secp256k1_pubkey[{n}]")  # noqa: N806
    S_array = ffi.new(f"secp256k1_pubkey[{n}]")  # noqa: N806
    Pk_array = ffi.new(f"secp256k1_pubkey[{n}]")  # noqa: N806
    r_array = ffi.new(f"unsigned char[{n * 32}]")

    # Parse all ciphertexts
    for i, (c1, c2, pk_uncompressed, blinding) in enumerate(ciphertexts):
        # Convert hex strings to bytes
        c1_bytes = bytes.fromhex(c1)
        c2_bytes = bytes.fromhex(c2)
        pk_bytes = bytes.fromhex(pk_uncompressed)
        blinding_bytes = bytes.fromhex(blinding)

        if len(c1_bytes) != 33 or len(c2_bytes) != 33:
            raise ValueError(f"Ciphertext {i}: c1 and c2 must be 33 bytes")
        if len(pk_bytes) != 64:
            raise ValueError(f"Ciphertext {i}: pk must be 64 bytes")
        if len(blinding_bytes) != 32:
            raise ValueError(f"Ciphertext {i}: blinding must be 32 bytes")

        lib.secp256k1_ec_pubkey_parse(ctx, R_array + i, c1_bytes, 33)
        lib.secp256k1_ec_pubkey_parse(ctx, S_array + i, c2_bytes, 33)

        pk_with_prefix = b"\x04" + pk_bytes
        lib.secp256k1_ec_pubkey_parse(ctx, Pk_array + i, pk_with_prefix, 65)

        # Copy blinding factor
        for j in range(32):
            r_array[i * 32 + j] = blinding_bytes[j]

    # Calculate proof size
    proof_size = lib.secp256k1_mpt_prove_same_plaintext_multi_size(n)
    proof_out = ffi.new(f"unsigned char[{proof_size}]")
    proof_len = ffi.new("size_t *", proof_size)

    # Generate proof
    result = lib.secp256k1_mpt_prove_same_plaintext_multi(
        ctx,
        proof_out,
        proof_len,
        amount,
        n,
        R_array,
        S_array,
        Pk_array,
        r_array,
        context_id_bytes,
    )
    if result != 1:
        raise RuntimeError("Failed to create same plaintext proof")

    return bytes(proof_out[0 : proof_len[0]]).hex().upper()


def verify_same_plaintext_proof_multi(  # noqa: PLR0914
    ctx,
    proof: str,
    ciphertexts: list,  # List of (c1, c2, pk) tuples (hex strings, no blinding)
    context_id: str,
) -> bool:
    """
    Verify a proof that multiple ciphertexts encrypt the same amount.

    Args:
        proof: Variable-length hex string (proof size depends on number of ciphertexts)
        ciphertexts: List of (c1, c2, pk) tuples where:
            - c1: 66-char hex string (33-byte compressed point)
            - c2: 66-char hex string (33-byte compressed point)
            - pk: 128-char hex string (64-byte public key, X || Y)
        context_id: 64-char hex string (32-byte context ID)

    Returns:
        True if proof is valid, False otherwise
    """
    # Convert hex strings to bytes
    proof_bytes = bytes.fromhex(proof)
    context_id_bytes = bytes.fromhex(context_id)

    if len(context_id_bytes) != CONTEXT_ID_SIZE:
        raise ValueError(f"context_id must be {CONTEXT_ID_SIZE} bytes")

    n = len(ciphertexts)
    if n < 2:
        raise ValueError("Need at least 2 ciphertexts")

    # Allocate arrays
    R_array = ffi.new(f"secp256k1_pubkey[{n}]")  # noqa: N806
    S_array = ffi.new(f"secp256k1_pubkey[{n}]")  # noqa: N806
    Pk_array = ffi.new(f"secp256k1_pubkey[{n}]")  # noqa: N806

    # Parse all ciphertexts
    for i, (c1_hex, c2_hex, pk_hex) in enumerate(ciphertexts):
        c1_bytes = bytes.fromhex(c1_hex)
        c2_bytes = bytes.fromhex(c2_hex)
        pk_bytes = bytes.fromhex(pk_hex)

        if len(c1_bytes) != PUBKEY_COMPRESSED_SIZE:
            raise ValueError(f"c1[{i}] must be {PUBKEY_COMPRESSED_SIZE} bytes")
        if len(c2_bytes) != PUBKEY_COMPRESSED_SIZE:
            raise ValueError(f"c2[{i}] must be {PUBKEY_COMPRESSED_SIZE} bytes")
        if len(pk_bytes) != PUBKEY_UNCOMPRESSED_SIZE:
            raise ValueError(f"pk[{i}] must be {PUBKEY_UNCOMPRESSED_SIZE} bytes")

        # Parse c1 (R)
        result = lib.secp256k1_ec_pubkey_parse(
            ctx, R_array + i, c1_bytes, PUBKEY_COMPRESSED_SIZE
        )
        if result != 1:
            raise RuntimeError(f"Failed to parse c1[{i}]")

        # Parse c2 (S)
        result = lib.secp256k1_ec_pubkey_parse(
            ctx, S_array + i, c2_bytes, PUBKEY_COMPRESSED_SIZE
        )
        if result != 1:
            raise RuntimeError(f"Failed to parse c2[{i}]")

        # Parse pk
        pk_with_prefix = b"\x04" + pk_bytes
        result = lib.secp256k1_ec_pubkey_parse(ctx, Pk_array + i, pk_with_prefix, 65)
        if result != 1:
            raise RuntimeError(f"Failed to parse pk[{i}]")

    # Verify proof
    result = lib.secp256k1_mpt_verify_same_plaintext_multi(
        ctx,
        proof_bytes,
        len(proof_bytes),
        n,
        R_array,
        S_array,
        Pk_array,
        context_id_bytes,
    )

    return result == 1
