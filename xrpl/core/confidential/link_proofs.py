"""
ElGamal-Pedersen link proofs and balance link proofs.

This module provides functions for creating and verifying link proofs
that connect ElGamal ciphertexts with Pedersen commitments.
"""

from xrpl.core.confidential.crypto_bindings import ffi, lib

# Size constants
PUBKEY_COMPRESSED_SIZE = 33
CONTEXT_ID_SIZE = 32
ACCOUNT_ID_SIZE = 20
MPT_ISSUANCE_ID_SIZE = 32


def create_elgamal_pedersen_link_proof(  # noqa: PLR0913
    ctx,
    c1: str,
    c2: str,
    pk_compressed: str,
    pedersen_commitment: str,
    amount: int,
    amount_blinding: str,
    pedersen_blinding: str,
    context_id: str,
) -> str:
    """
    Create an ElGamal-Pedersen link proof using the utility layer.

    Proves that an ElGamal ciphertext (c1, c2) and a Pedersen commitment
    encrypt/commit to the same amount.

    Args:
        ctx: Ignored (kept for backward compatibility). Uses mpt_secp256k1_context().
        c1: 66-char hex string (33-byte compressed point)
        c2: 66-char hex string (33-byte compressed point)
        pk_compressed: 66-char hex string (33-byte compressed public key)
        pedersen_commitment: 66-char hex string (33-byte compressed commitment)
        amount: The amount being encrypted/committed
        amount_blinding: 64-char hex string (32-byte ElGamal blinding factor)
        pedersen_blinding: 64-char hex string (32-byte Pedersen blinding factor)
        context_id: 64-char hex string (32-byte transaction context ID)

    Returns:
        390-char hex string (195-byte link proof)
    """
    # Convert hex strings to bytes
    pk_bytes = bytes.fromhex(pk_compressed)
    amount_blinding_bytes = bytes.fromhex(amount_blinding)
    pedersen_blinding_bytes = bytes.fromhex(pedersen_blinding)
    context_id_bytes = bytes.fromhex(context_id)
    pc_bytes = bytes.fromhex(pedersen_commitment)

    if len(pk_bytes) != 33:
        raise ValueError("pk must be 33 bytes (compressed)")
    if len(pc_bytes) != 33:
        raise ValueError("pedersen_commitment must be 33 bytes (compressed)")
    if len(amount_blinding_bytes) != 32:
        raise ValueError("amount_blinding must be 32 bytes")
    if len(pedersen_blinding_bytes) != 32:
        raise ValueError("pedersen_blinding must be 32 bytes")
    if len(context_id_bytes) != 32:
        raise ValueError("context_id must be 32 bytes")

    # Create params struct
    params = ffi.new("mpt_pedersen_proof_params *")

    # Copy pedersen commitment
    for i in range(33):
        params.pedersen_commitment[i] = pc_bytes[i]

    # Set amount
    params.amount = amount

    # Copy ciphertext (c1 || c2)
    c1_bytes = bytes.fromhex(c1)
    c2_bytes = bytes.fromhex(c2)
    ciphertext = c1_bytes + c2_bytes
    for i in range(66):
        params.ciphertext[i] = ciphertext[i]

    # Copy blinding factor
    for i in range(32):
        params.blinding_factor[i] = pedersen_blinding_bytes[i]

    # Generate link proof using utility layer
    proof = ffi.new("uint8_t[195]")
    result = lib.mpt_get_amount_linkage_proof(
        pk_bytes,
        amount_blinding_bytes,
        context_id_bytes,
        params,
        proof,
    )
    if result != 0:
        raise RuntimeError("Failed to create ElGamal-Pedersen link proof")

    return bytes(proof[0:195]).hex().upper()


def verify_elgamal_pedersen_link_proof(
    ctx,
    proof: str,
    c1: str,
    c2: str,
    pk_compressed: str,
    pedersen_commitment: str,
    context_id: str,
) -> bool:
    """
    Verify an ElGamal-Pedersen link proof.

    Note: The utility layer doesn't provide a verification function,
    so this still uses the low-level secp256k1 functions.

    Args:
        ctx: secp256k1 context (required for verification)
        proof: 390-char hex string (195-byte proof)
        c1: 66-char hex string (33-byte compressed point)
        c2: 66-char hex string (33-byte compressed point)
        pk_compressed: 66-char hex string (33-byte compressed public key)
        pedersen_commitment: 66-char hex string (33-byte compressed commitment)
        context_id: 64-char hex string (32-byte context ID)

    Returns:
        True if proof is valid, False otherwise
    """
    # Convert hex strings to bytes
    proof_bytes = bytes.fromhex(proof)
    c1_bytes = bytes.fromhex(c1)
    c2_bytes = bytes.fromhex(c2)
    pk_bytes = bytes.fromhex(pk_compressed)
    pc_bytes = bytes.fromhex(pedersen_commitment)
    context_id_bytes = bytes.fromhex(context_id)

    if len(proof_bytes) != 195:
        raise ValueError("proof must be 195 bytes")
    if len(c1_bytes) != PUBKEY_COMPRESSED_SIZE:
        raise ValueError(f"c1 must be {PUBKEY_COMPRESSED_SIZE} bytes")
    if len(c2_bytes) != PUBKEY_COMPRESSED_SIZE:
        raise ValueError(f"c2 must be {PUBKEY_COMPRESSED_SIZE} bytes")
    if len(pk_bytes) != PUBKEY_COMPRESSED_SIZE:
        raise ValueError(f"pk must be {PUBKEY_COMPRESSED_SIZE} bytes")
    if len(pc_bytes) != PUBKEY_COMPRESSED_SIZE:
        raise ValueError(f"pedersen_commitment must be {PUBKEY_COMPRESSED_SIZE} bytes")
    if len(context_id_bytes) != CONTEXT_ID_SIZE:
        raise ValueError(f"context_id must be {CONTEXT_ID_SIZE} bytes")

    # Parse points
    c1_pk = ffi.new("secp256k1_pubkey *")
    c2_pk = ffi.new("secp256k1_pubkey *")
    pk = ffi.new("secp256k1_pubkey *")
    pc = ffi.new("secp256k1_pubkey *")

    # Parse c1, c2 (compressed)
    result = lib.secp256k1_ec_pubkey_parse(ctx, c1_pk, c1_bytes, 33)
    if result != 1:
        raise RuntimeError("Failed to parse c1")
    result = lib.secp256k1_ec_pubkey_parse(ctx, c2_pk, c2_bytes, 33)
    if result != 1:
        raise RuntimeError("Failed to parse c2")

    # Parse pk (compressed)
    result = lib.secp256k1_ec_pubkey_parse(ctx, pk, pk_bytes, 33)
    if result != 1:
        raise RuntimeError("Failed to parse pk")

    # Parse pedersen_commitment (compressed)
    result = lib.secp256k1_ec_pubkey_parse(ctx, pc, pc_bytes, 33)
    if result != 1:
        raise RuntimeError("Failed to parse pedersen_commitment")

    # Verify proof
    result = lib.secp256k1_elgamal_pedersen_link_verify(
        ctx, proof_bytes, c1_pk, c2_pk, pk, pc, context_id_bytes
    )

    return result == 1


def create_balance_link_proof(  # noqa: PLR0913
    ctx,
    pk_compressed: str,
    c2: str,
    c1: str,
    pedersen_commitment: str,
    amount: int,
    private_key: str,
    pedersen_blinding: str,
    context_id: str,
) -> str:
    """
    Create a balance link proof using the utility layer.

    This is specifically for proving the link between the current balance
    ciphertext (from ledger) and the balance commitment.

    Args:
        ctx: Ignored (kept for backward compatibility). Uses mpt_secp256k1_context().
        pk_compressed: 66-char hex string (33-byte compressed public key)
        c2: 66-char hex string (33-byte compressed C2 point)
        c1: 66-char hex string (33-byte compressed C1 point)
        pedersen_commitment: 66-char hex string (33-byte compressed Pedersen commitment)
        amount: The plaintext balance amount
        private_key: 64-char hex string (32-byte ElGamal private key)
        pedersen_blinding: 64-char hex string (32-byte Pedersen blinding rho)
        context_id: 64-char hex string (32-byte transaction context ID)

    Returns:
        390-char hex string (195-byte balance link proof)
    """
    # Convert hex strings to bytes
    pk_bytes = bytes.fromhex(pk_compressed)
    c2_bytes = bytes.fromhex(c2)
    c1_bytes = bytes.fromhex(c1)
    pcm_bytes = bytes.fromhex(pedersen_commitment)
    private_key_bytes = bytes.fromhex(private_key)
    pedersen_blinding_bytes = bytes.fromhex(pedersen_blinding)
    context_id_bytes = bytes.fromhex(context_id)

    if len(c1_bytes) != 33 or len(c2_bytes) != 33:
        raise ValueError("c1 and c2 must be 33 bytes")
    if len(pk_bytes) != 33:
        raise ValueError("pk must be 33 bytes (compressed)")
    if len(pcm_bytes) != 33:
        raise ValueError("pedersen_commitment must be 33 bytes (compressed)")
    if len(private_key_bytes) != 32:
        raise ValueError("private_key must be 32 bytes")
    if len(pedersen_blinding_bytes) != 32:
        raise ValueError("pedersen_blinding must be 32 bytes")
    if len(context_id_bytes) != 32:
        raise ValueError("context_id must be 32 bytes")

    # Create params struct
    params = ffi.new("mpt_pedersen_proof_params *")

    # Copy pedersen commitment
    for i in range(33):
        params.pedersen_commitment[i] = pcm_bytes[i]

    # Set amount
    params.amount = amount

    # Copy ciphertext (c1 || c2)
    ciphertext = c1_bytes + c2_bytes
    for i in range(66):
        params.ciphertext[i] = ciphertext[i]

    # Copy blinding factor
    for i in range(32):
        params.blinding_factor[i] = pedersen_blinding_bytes[i]

    # Generate balance link proof using utility layer
    proof = ffi.new("uint8_t[]", 195)
    result = lib.mpt_get_balance_linkage_proof(
        private_key_bytes,
        pk_bytes,
        context_id_bytes,
        params,
        proof,
    )
    if result != 0:
        raise RuntimeError("Failed to create balance link proof")

    return bytes(proof[0:195]).hex().upper()
