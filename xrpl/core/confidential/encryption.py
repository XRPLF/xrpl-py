"""
ElGamal encryption and decryption functions.

This module provides functions for encrypting and decrypting amounts
using ElGamal encryption.
"""

import secrets
from typing import Optional, Tuple

from xrpl.core.confidential.crypto_bindings import ffi, lib

# Size constants
PUBKEY_COMPRESSED_SIZE = 33
BLINDING_FACTOR_SIZE = 32


def encrypt(
    ctx,
    pubkey_compressed: str,
    amount: int,
    blinding_factor: Optional[str] = None,
) -> Tuple[str, str, str]:
    """
    Encrypt an amount using ElGamal encryption via the utility layer.

    Args:
        ctx: Ignored (kept for backward compatibility). Uses mpt_secp256k1_context().
        pubkey_compressed: 66-char hex string (33-byte compressed public key)
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
    pubkey_bytes = bytes.fromhex(pubkey_compressed)
    if len(pubkey_bytes) != 33:
        raise ValueError("pubkey must be 33 bytes (compressed)")

    # Generate or use provided blinding factor
    if blinding_factor is None:
        blinding_bytes = secrets.token_bytes(32)
        blinding_factor = blinding_bytes.hex().upper()
    else:
        blinding_bytes = bytes.fromhex(blinding_factor)
        if len(blinding_bytes) != 32:
            raise ValueError("blinding_factor must be 32 bytes")

    # Encrypt using utility layer
    ciphertext = ffi.new("uint8_t[]", 66)
    result = lib.mpt_encrypt_amount(amount, pubkey_bytes, blinding_bytes, ciphertext)
    if result != 0:
        raise RuntimeError("Failed to encrypt")

    # Split ciphertext into c1 and c2
    c1_bytes = bytes(ciphertext[0:33])
    c2_bytes = bytes(ciphertext[33:66])

    return c1_bytes.hex().upper(), c2_bytes.hex().upper(), blinding_factor


def decrypt(ctx, privkey: str, c1: str, c2: str) -> int:
    """
    Decrypt an ElGamal ciphertext via the utility layer.

    Args:
        ctx: Ignored (kept for backward compatibility). Uses mpt_secp256k1_context().
        privkey: 64-char hex string (32-byte private key)
        c1: 66-char hex string (33-byte compressed C1 point)
        c2: 66-char hex string (33-byte compressed C2 point)

    Returns:
        The decrypted amount (uint64)

    Raises:
        RuntimeError: If decryption fails
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

    # Combine c1 and c2 into ciphertext
    ciphertext = c1_bytes + c2_bytes

    # Decrypt using utility layer
    amount = ffi.new("uint64_t *")
    result = lib.mpt_decrypt_amount(ciphertext, privkey_bytes, amount)
    if result != 0:
        raise RuntimeError("Failed to decrypt")

    return amount[0]
