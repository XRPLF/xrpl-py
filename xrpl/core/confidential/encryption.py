"""
ElGamal encryption and decryption functions.

This module provides functions for encrypting and decrypting amounts
using ElGamal encryption.
"""

import secrets
from typing import Optional, Tuple

from xrpl.core.confidential.crypto_bindings import (
    SECP256K1_EC_COMPRESSED,
    SECP256K1_EC_UNCOMPRESSED,
    ffi,
    lib,
)

# Size constants
PUBKEY_UNCOMPRESSED_SIZE = 64
PUBKEY_COMPRESSED_SIZE = 33
BLINDING_FACTOR_SIZE = 32


def encrypt(
    ctx,
    pubkey_uncompressed: str,
    amount: int,
    blinding_factor: Optional[str] = None,
) -> Tuple[str, str, str]:
    """
    Encrypt an amount using ElGamal encryption.

    Args:
        pubkey_uncompressed: 128-char hex string (64-byte public key, X || Y)
        amount: The amount to encrypt (uint64)
        blinding_factor: Optional 64-char hex string (32-byte blinding factor).
                        If not provided, a random one is generated.

    Returns:
        Tuple of (c1, c2, blinding_factor) as hex strings:
        - c1: 66-char hex string (33-byte compressed point)
        - c2: 66-char hex string (33-byte compressed point)
        - blinding_factor: 64-char hex string (32-byte blinding factor)
    """
    # Convert public key from hex
    pubkey_bytes = bytes.fromhex(pubkey_uncompressed)
    if len(pubkey_bytes) != 64:
        raise ValueError("pubkey must be 64 bytes (uncompressed, X || Y)")

    # Generate or use provided blinding factor
    if blinding_factor is None:
        blinding_bytes = secrets.token_bytes(32)
        blinding_factor = blinding_bytes.hex().upper()
    else:
        blinding_bytes = bytes.fromhex(blinding_factor)
        if len(blinding_bytes) != 32:
            raise ValueError("blinding_factor must be 32 bytes")

    # Parse public key (add 0x04 prefix for uncompressed format)
    pk_with_prefix = b"\x04" + pubkey_bytes
    pubkey_parsed = ffi.new("secp256k1_pubkey *")
    result = lib.secp256k1_ec_pubkey_parse(ctx, pubkey_parsed, pk_with_prefix, 65)
    if result != 1:
        raise RuntimeError("Failed to parse public key")

    # Encrypt
    c1 = ffi.new("secp256k1_pubkey *")
    c2 = ffi.new("secp256k1_pubkey *")
    result = lib.secp256k1_elgamal_encrypt(
        ctx, c1, c2, pubkey_parsed, amount, blinding_bytes
    )
    if result != 1:
        raise RuntimeError("Failed to encrypt")

    # Serialize c1 and c2 (compressed)
    c1_bytes = _serialize_pubkey(ctx, c1, compressed=True)
    c2_bytes = _serialize_pubkey(ctx, c2, compressed=True)

    return c1_bytes.hex().upper(), c2_bytes.hex().upper(), blinding_factor


def _serialize_pubkey(ctx, pubkey, compressed: bool = True) -> bytes:
    """Serialize a secp256k1_pubkey to bytes."""
    if compressed:
        output = ffi.new("unsigned char[33]")
        output_len = ffi.new("size_t *", 33)
        flags = SECP256K1_EC_COMPRESSED
    else:
        output = ffi.new("unsigned char[65]")
        output_len = ffi.new("size_t *", 65)
        flags = SECP256K1_EC_UNCOMPRESSED

    result = lib.secp256k1_ec_pubkey_serialize(ctx, output, output_len, pubkey, flags)
    if result != 1:
        raise RuntimeError("Failed to serialize public key")

    return bytes(output[0 : output_len[0]])


def decrypt(ctx, privkey: str, c1: str, c2: str) -> int:
    """
    Decrypt an ElGamal ciphertext.

    Note: This uses a brute-force discrete log solver, so it only works
    for relatively small amounts (up to ~10^6 in reasonable time).

    Args:
        privkey: 64-char hex string (32-byte private key)
        c1: 66-char hex string (33-byte compressed C1 point)
        c2: 66-char hex string (33-byte compressed C2 point)

    Returns:
        The decrypted amount (uint64)

    Raises:
        RuntimeError: If decryption fails (e.g., amount too large)
    """
    # Convert hex strings to bytes
    privkey_bytes = bytes.fromhex(privkey)
    c1_bytes = bytes.fromhex(c1)
    c2_bytes = bytes.fromhex(c2)

    if len(privkey_bytes) != 32:
        raise ValueError("privkey must be 32 bytes")
    if len(c1_bytes) != 33:
        raise ValueError("c1 must be 33 bytes (compressed)")
    if len(c2_bytes) != 33:
        raise ValueError("c2 must be 33 bytes (compressed)")

    # Parse c1 and c2
    c1_parsed = ffi.new("secp256k1_pubkey *")
    c2_parsed = ffi.new("secp256k1_pubkey *")
    result = lib.secp256k1_ec_pubkey_parse(ctx, c1_parsed, c1_bytes, 33)
    if result != 1:
        raise RuntimeError("Failed to parse c1")
    result = lib.secp256k1_ec_pubkey_parse(ctx, c2_parsed, c2_bytes, 33)
    if result != 1:
        raise RuntimeError("Failed to parse c2")

    # Decrypt
    amount = ffi.new("uint64_t *")
    result = lib.secp256k1_elgamal_decrypt(ctx, amount, c1_parsed, c2_parsed, privkey_bytes)
    if result != 1:
        raise RuntimeError("Failed to decrypt")

    return amount[0]

