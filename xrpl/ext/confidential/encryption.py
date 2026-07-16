"""
ElGamal encryption and decryption functions.

This module provides functions for encrypting and decrypting amounts
using ElGamal encryption.
"""

from typing import Optional, Tuple

from xrpl.ext.confidential.crypto_bindings import ffi, lib

# Size constants
PUBKEY_COMPRESSED_SIZE = 33
BLINDING_FACTOR_SIZE = 32

# Fallback upper bound for the decrypt discrete-log search when no tighter
# bound (e.g. an issuance's MaximumAmount) is supplied. ~1,000,000 keeps a
# single decrypt well under a few seconds; larger amounts must pass an explicit
# range_high. See decrypt() and transaction_builders for ledger-derived bounds.
DEFAULT_DECRYPT_RANGE_HIGH = 1_000_000


def encrypt(
    ctx: object,
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

    # Generate or use provided blinding factor. Use the library's generator
    # (not raw random bytes) so the scalar is reduced against the secp256k1
    # curve order and is a valid ElGamal randomness scalar.
    if blinding_factor is None:
        bf_buf = ffi.new("uint8_t[32]")
        if lib.mpt_generate_blinding_factor(bf_buf) != 0:
            raise RuntimeError("Failed to generate blinding factor")
        blinding_bytes = bytes(bf_buf[0:32])
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


def decrypt(
    ctx: object,
    privkey: str,
    c1: str,
    c2: str,
    range_low: int = 0,
    range_high: int = DEFAULT_DECRYPT_RANGE_HIGH,
) -> int:
    """
    Decrypt an ElGamal ciphertext via the utility layer.

    Decryption recovers the amount by a brute-force discrete-log search over
    ``[range_low, range_high]`` (inclusive). Cost scales linearly with the
    width of the range (~3s per 1,000,000 on Apple Silicon), so callers should
    bound it as tightly as they can — typically by the issuance's maximum
    amount. See ``transaction_builders`` for how the range is derived from the
    MPTokenIssuance on the ledger.

    Args:
        ctx: Ignored (kept for backward compatibility). Uses mpt_secp256k1_context().
        privkey: 64-char hex string (32-byte private key)
        c1: 66-char hex string (33-byte compressed C1 point)
        c2: 66-char hex string (33-byte compressed C2 point)
        range_low: Inclusive lower bound of the search range (default 0).
        range_high: Inclusive upper bound of the search range.

    Returns:
        The decrypted amount (uint64)

    Raises:
        ValueError: If inputs are malformed or range_low > range_high.
        RuntimeError: If decryption fails (e.g. amount outside the range).
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
    if range_low > range_high:
        raise ValueError("range_low must be <= range_high")

    # Combine c1 and c2 into ciphertext
    ciphertext = c1_bytes + c2_bytes

    # Decrypt using utility layer (brute-force DL search over the given range)
    amount = ffi.new("uint64_t *")
    result = lib.mpt_decrypt_amount(
        ciphertext, privkey_bytes, amount, range_low, range_high
    )
    if result != 0:
        raise RuntimeError(
            "Failed to decrypt: amount not found in range "
            f"[{range_low}, {range_high}] (error code: {result})"
        )

    return amount[0]
