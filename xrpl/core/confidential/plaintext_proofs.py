"""
Equality plaintext proofs and same plaintext proofs.

This module provides functions for creating and verifying proofs about
plaintext values in ciphertexts (used for clawback and multi-recipient sends).
"""

from xrpl.core.confidential.crypto_bindings import ffi, lib

# Size constants
PUBKEY_COMPRESSED_SIZE = 33
CONTEXT_ID_SIZE = 32


def create_equality_plaintext_proof(
    ctx,
    pk_compressed: str,
    c2: str,
    c1: str,
    amount: int,
    private_key: str,
    context_id: str,
) -> str:
    """
    Create an equality proof for ConfidentialMPTClawback using the utility layer.

    Proves that the issuer knows the private key corresponding to the public key
    and that the encrypted amount matches the plaintext amount.

    Args:
        ctx: Ignored (kept for backward compatibility). Uses mpt_secp256k1_context().
        pk_compressed: 66-char hex string (33-byte compressed public key)
        c2: 66-char hex string (33-byte compressed C2 point)
        c1: 66-char hex string (33-byte compressed C1 point)
        amount: The plaintext amount
        private_key: 64-char hex string (32-byte private key)
        context_id: 64-char hex string (32-byte transaction context ID)

    Returns:
        196-char hex string (98-byte equality proof)
    """
    # Convert hex strings to bytes
    pk_bytes = bytes.fromhex(pk_compressed)
    c2_bytes = bytes.fromhex(c2)
    c1_bytes = bytes.fromhex(c1)
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
    proof = ffi.new("uint8_t[]", 98)
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

    return bytes(proof[0:98]).hex().upper()


def verify_equality_plaintext_proof(
    ctx,
    proof: str,
    pk_compressed: str,
    c2: str,
    c1: str,
    amount: int,
    context_id: str,
) -> bool:
    """
    Verify an equality plaintext proof (for ConfidentialMPTClawback).

    Note: The utility layer doesn't provide a verification function,
    so this still uses the low-level secp256k1 functions.

    Args:
        ctx: secp256k1 context (required for verification)
        proof: 196-char hex string (98-byte proof)
        pk_compressed: 66-char hex string (33-byte compressed public key)
        c2: 66-char hex string (33-byte compressed point)
        c1: 66-char hex string (33-byte compressed point)
        amount: The amount being clawed back
        context_id: 64-char hex string (32-byte context ID)

    Returns:
        True if proof is valid, False otherwise
    """
    # Convert hex strings to bytes
    proof_bytes = bytes.fromhex(proof)
    pk_bytes = bytes.fromhex(pk_compressed)
    c2_bytes = bytes.fromhex(c2)
    c1_bytes = bytes.fromhex(c1)
    context_id_bytes = bytes.fromhex(context_id)

    if len(proof_bytes) != 98:
        raise ValueError("proof must be 98 bytes")
    if len(pk_bytes) != PUBKEY_COMPRESSED_SIZE:
        raise ValueError(f"pk must be {PUBKEY_COMPRESSED_SIZE} bytes")
    if len(c2_bytes) != PUBKEY_COMPRESSED_SIZE:
        raise ValueError(f"c2 must be {PUBKEY_COMPRESSED_SIZE} bytes")
    if len(c1_bytes) != PUBKEY_COMPRESSED_SIZE:
        raise ValueError(f"c1 must be {PUBKEY_COMPRESSED_SIZE} bytes")
    if len(context_id_bytes) != CONTEXT_ID_SIZE:
        raise ValueError(f"context_id must be {CONTEXT_ID_SIZE} bytes")

    # Parse pk (compressed)
    pk_pubkey = ffi.new("secp256k1_pubkey *")
    result = lib.secp256k1_ec_pubkey_parse(ctx, pk_pubkey, pk_bytes, 33)
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
    # The C library expects (pk, c2, c1), as per the C++ reference test
    result = lib.secp256k1_equality_plaintext_verify(
        ctx, proof_bytes, pk_pubkey, c2_pk, c1_pk, amount, context_id_bytes
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

    Note: The utility layer doesn't provide a multi-ciphertext proof function yet,
    so this still uses the low-level secp256k1 functions.

    Args:
        ctx: secp256k1 context (required for proof generation)
        amount: The common plaintext amount
        ciphertexts: List of (c1, c2, pk_compressed, blinding) tuples
            - c1: 66-char hex string (33-byte compressed point)
            - c2: 66-char hex string (33-byte compressed point)
            - pk_compressed: 66-char hex string (33-byte compressed public key)
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
    for i, (c1, c2, pk_compressed, blinding) in enumerate(ciphertexts):
        # Convert hex strings to bytes
        c1_bytes = bytes.fromhex(c1)
        c2_bytes = bytes.fromhex(c2)
        pk_bytes = bytes.fromhex(pk_compressed)
        blinding_bytes = bytes.fromhex(blinding)

        if len(c1_bytes) != 33 or len(c2_bytes) != 33:
            raise ValueError(f"Ciphertext {i}: c1 and c2 must be 33 bytes")
        if len(pk_bytes) != 33:
            raise ValueError(f"Ciphertext {i}: pk must be 33 bytes (compressed)")
        if len(blinding_bytes) != 32:
            raise ValueError(f"Ciphertext {i}: blinding must be 32 bytes")

        lib.secp256k1_ec_pubkey_parse(ctx, R_array + i, c1_bytes, 33)
        lib.secp256k1_ec_pubkey_parse(ctx, S_array + i, c2_bytes, 33)
        lib.secp256k1_ec_pubkey_parse(ctx, Pk_array + i, pk_bytes, 33)

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

    Note: The utility layer doesn't provide a multi-ciphertext verification function yet,
    so this still uses the low-level secp256k1 functions.

    Args:
        ctx: secp256k1 context (required for verification)
        proof: Variable-length hex string (proof size depends on number of ciphertexts)
        ciphertexts: List of (c1, c2, pk) tuples where:
            - c1: 66-char hex string (33-byte compressed point)
            - c2: 66-char hex string (33-byte compressed point)
            - pk: 66-char hex string (33-byte compressed public key)
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
        if len(pk_bytes) != PUBKEY_COMPRESSED_SIZE:
            raise ValueError(f"pk[{i}] must be {PUBKEY_COMPRESSED_SIZE} bytes")

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

        # Parse pk (compressed)
        result = lib.secp256k1_ec_pubkey_parse(ctx, Pk_array + i, pk_bytes, 33)
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
