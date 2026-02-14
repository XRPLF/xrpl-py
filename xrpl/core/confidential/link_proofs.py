"""
ElGamal-Pedersen link proofs and balance link proofs.

This module provides functions for creating and verifying link proofs
that connect ElGamal ciphertexts with Pedersen commitments.
"""

from xrpl.core.confidential.crypto_bindings import ffi, lib

# Size constants
PUBKEY_UNCOMPRESSED_SIZE = 64
PUBKEY_COMPRESSED_SIZE = 33
CONTEXT_ID_SIZE = 32
ACCOUNT_ID_SIZE = 20
MPT_ISSUANCE_ID_SIZE = 32


def create_elgamal_pedersen_link_proof(  # noqa: PLR0913
    ctx,
    c1: str,
    c2: str,
    pk_uncompressed: str,
    pedersen_commitment: str,
    amount: int,
    amount_blinding: str,
    pedersen_blinding: str,
    context_id: str,
) -> str:
    """
    Create an ElGamal-Pedersen link proof.

    Proves that an ElGamal ciphertext (c1, c2) and a Pedersen commitment
    encrypt/commit to the same amount.

    Args:
        c1: 66-char hex string (33-byte compressed point)
        c2: 66-char hex string (33-byte compressed point)
        pk_uncompressed: 128-char hex string (64-byte public key, X || Y)
        pedersen_commitment: 128-char hex string (64-byte commitment, X || Y)
        amount: The amount being encrypted/committed
        amount_blinding: 64-char hex string (32-byte ElGamal blinding factor)
        pedersen_blinding: 64-char hex string (32-byte Pedersen blinding factor)
        context_id: 64-char hex string (32-byte transaction context ID)

    Returns:
        390-char hex string (195-byte link proof)
    """
    # Convert hex strings to bytes
    c1_bytes = bytes.fromhex(c1)
    c2_bytes = bytes.fromhex(c2)
    pk_bytes = bytes.fromhex(pk_uncompressed)
    pc_bytes = bytes.fromhex(pedersen_commitment)
    amount_blinding_bytes = bytes.fromhex(amount_blinding)
    pedersen_blinding_bytes = bytes.fromhex(pedersen_blinding)
    context_id_bytes = bytes.fromhex(context_id)

    if len(c1_bytes) != 33 or len(c2_bytes) != 33:
        raise ValueError("c1 and c2 must be 33 bytes")
    if len(pk_bytes) != 64:
        raise ValueError("pk must be 64 bytes")
    if len(pc_bytes) != 64:
        raise ValueError("pedersen_commitment must be 64 bytes")
    if len(amount_blinding_bytes) != 32:
        raise ValueError("amount_blinding must be 32 bytes")
    if len(pedersen_blinding_bytes) != 32:
        raise ValueError("pedersen_blinding must be 32 bytes")
    if len(context_id_bytes) != 32:
        raise ValueError("context_id must be 32 bytes")

    # Parse points
    c1_pk = ffi.new("secp256k1_pubkey *")
    c2_pk = ffi.new("secp256k1_pubkey *")
    pk = ffi.new("secp256k1_pubkey *")
    pc = ffi.new("secp256k1_pubkey *")

    lib.secp256k1_ec_pubkey_parse(ctx, c1_pk, c1_bytes, 33)
    lib.secp256k1_ec_pubkey_parse(ctx, c2_pk, c2_bytes, 33)

    pk_with_prefix = b"\x04" + pk_bytes
    lib.secp256k1_ec_pubkey_parse(ctx, pk, pk_with_prefix, 65)

    pc_with_prefix = b"\x04" + pc_bytes
    lib.secp256k1_ec_pubkey_parse(ctx, pc, pc_with_prefix, 65)

    # Generate link proof
    proof = ffi.new("unsigned char[195]")
    result = lib.secp256k1_elgamal_pedersen_link_prove(
        ctx,
        proof,
        c1_pk,
        c2_pk,
        pk,
        pc,
        amount,
        amount_blinding_bytes,
        pedersen_blinding_bytes,
        context_id_bytes,
    )
    if result != 1:
        raise RuntimeError("Failed to create ElGamal-Pedersen link proof")

    return bytes(proof[0:195]).hex().upper()


def verify_elgamal_pedersen_link_proof(
    ctx,
    proof: str,
    c1: str,
    c2: str,
    pk_uncompressed: str,
    pedersen_commitment: str,
    context_id: str,
) -> bool:
    """
    Verify an ElGamal-Pedersen link proof.

    Args:
        proof: 390-char hex string (195-byte proof)
        c1: 66-char hex string (33-byte compressed point)
        c2: 66-char hex string (33-byte compressed point)
        pk_uncompressed: 128-char hex string (64-byte public key, X || Y)
        pedersen_commitment: 128-char hex string (64-byte commitment, X || Y)
        context_id: 64-char hex string (32-byte context ID)

    Returns:
        True if proof is valid, False otherwise
    """
    # Convert hex strings to bytes
    proof_bytes = bytes.fromhex(proof)
    c1_bytes = bytes.fromhex(c1)
    c2_bytes = bytes.fromhex(c2)
    pk_bytes = bytes.fromhex(pk_uncompressed)
    pc_bytes = bytes.fromhex(pedersen_commitment)
    context_id_bytes = bytes.fromhex(context_id)

    if len(proof_bytes) != 195:
        raise ValueError("proof must be 195 bytes")
    if len(c1_bytes) != PUBKEY_COMPRESSED_SIZE:
        raise ValueError(f"c1 must be {PUBKEY_COMPRESSED_SIZE} bytes")
    if len(c2_bytes) != PUBKEY_COMPRESSED_SIZE:
        raise ValueError(f"c2 must be {PUBKEY_COMPRESSED_SIZE} bytes")
    if len(pk_bytes) != PUBKEY_UNCOMPRESSED_SIZE:
        raise ValueError(f"pk must be {PUBKEY_UNCOMPRESSED_SIZE} bytes")
    if len(pc_bytes) != PUBKEY_UNCOMPRESSED_SIZE:
        raise ValueError(
            f"pedersen_commitment must be {PUBKEY_UNCOMPRESSED_SIZE} bytes"
        )
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

    # Parse pk (uncompressed)
    pk_with_prefix = b"\x04" + pk_bytes
    result = lib.secp256k1_ec_pubkey_parse(ctx, pk, pk_with_prefix, 65)
    if result != 1:
        raise RuntimeError("Failed to parse pk")

    # Parse pedersen_commitment (uncompressed)
    pc_with_prefix = b"\x04" + pc_bytes
    result = lib.secp256k1_ec_pubkey_parse(ctx, pc, pc_with_prefix, 65)
    if result != 1:
        raise RuntimeError("Failed to parse pedersen_commitment")

    # Verify proof
    result = lib.secp256k1_elgamal_pedersen_link_verify(
        ctx, proof_bytes, c1_pk, c2_pk, pk, pc, context_id_bytes
    )

    return result == 1


def create_balance_link_proof(  # noqa: PLR0913
    ctx,
    pk_uncompressed: str,
    c2: str,
    c1: str,
    pedersen_commitment: str,
    amount: int,
    private_key: str,
    pedersen_blinding: str,
    context_id: str,
) -> str:
    """
    Create a balance link proof (uses SWAPPED parameter order).

    This is specifically for proving the link between the current balance
    ciphertext (from ledger) and the balance commitment.

    The verification function expects: (pk, c2, c1, pcm, context)
    So the proof generation must use the same order.

    Args:
        pk_uncompressed: 128-char hex string (64-byte public key, FIRST)
        c2: 66-char hex string (33-byte compressed C2 point, SECOND)
        c1: 66-char hex string (33-byte compressed C1 point, THIRD)
        pedersen_commitment: 128-char hex string (64-byte Pedersen, X + Y)
        amount: The plaintext balance amount
        private_key: 64-char hex string (32-byte ElGamal private key)
        pedersen_blinding: 64-char hex string (32-byte Pedersen blinding rho)
        context_id: 64-char hex string (32-byte transaction context ID)

    Returns:
        390-char hex string (195-byte balance link proof)
    """
    # Convert hex strings to bytes
    pk_bytes = bytes.fromhex(pk_uncompressed)
    c2_bytes = bytes.fromhex(c2)
    c1_bytes = bytes.fromhex(c1)
    pcm_bytes = bytes.fromhex(pedersen_commitment)
    private_key_bytes = bytes.fromhex(private_key)
    pedersen_blinding_bytes = bytes.fromhex(pedersen_blinding)
    context_id_bytes = bytes.fromhex(context_id)

    if len(c1_bytes) != 33 or len(c2_bytes) != 33:
        raise ValueError("c1 and c2 must be 33 bytes")
    if len(pk_bytes) != 64:
        raise ValueError("pk must be 64 bytes")
    if len(pcm_bytes) != 64:
        raise ValueError("pedersen_commitment must be 64 bytes")
    if len(private_key_bytes) != 32:
        raise ValueError("private_key must be 32 bytes")
    if len(pedersen_blinding_bytes) != 32:
        raise ValueError("pedersen_blinding must be 32 bytes")
    if len(context_id_bytes) != 32:
        raise ValueError("context_id must be 32 bytes")

    # Parse points
    c1_pk = ffi.new("secp256k1_pubkey *")
    c2_pk = ffi.new("secp256k1_pubkey *")
    pk = ffi.new("secp256k1_pubkey *")
    pcm = ffi.new("secp256k1_pubkey *")

    lib.secp256k1_ec_pubkey_parse(ctx, c1_pk, c1_bytes, 33)
    lib.secp256k1_ec_pubkey_parse(ctx, c2_pk, c2_bytes, 33)

    pk_with_prefix = b"\x04" + pk_bytes
    lib.secp256k1_ec_pubkey_parse(ctx, pk, pk_with_prefix, 65)

    # Parse uncompressed Pedersen commitment (add 0x04 prefix)
    pcm_with_prefix = b"\x04" + pcm_bytes
    lib.secp256k1_ec_pubkey_parse(ctx, pcm, pcm_with_prefix, 65)

    # Generate proof with SWAPPED order: pk, c2, c1 (not c1, c2, pk)
    proof = ffi.new("unsigned char[195]")
    result = lib.secp256k1_elgamal_pedersen_link_prove(
        ctx,
        proof,
        pk,  # PK FIRST (swapped!)
        c2_pk,  # C2 second (swapped!)
        c1_pk,  # C1 third (swapped!)
        pcm,
        amount,
        private_key_bytes,  # Use private key, not blinding factor
        pedersen_blinding_bytes,
        context_id_bytes,
    )
    if result != 1:
        raise RuntimeError("Failed to create balance link proof")

    return bytes(proof[0:195]).hex().upper()
