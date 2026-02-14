"""
Utility functions for confidential MPT operations.

This module provides helper functions for working with confidential MPT
transactions, including coordinate conversion and data formatting.
"""


def bytes_to_hex(data: bytes) -> str:
    """
    Convert bytes to uppercase hexadecimal string.

    This is the standard format used by XRPL for binary data in transactions.

    Args:
        data: Bytes to convert

    Returns:
        Uppercase hexadecimal string representation

    Example:
        >>> from xrpl.core.confidential.utils import bytes_to_hex
        >>> data = b"\\x01\\x02\\x03\\x04"
        >>> bytes_to_hex(data)
        '01020304'
    """
    return data.hex().upper()


def reverse_coordinates(pk_bytes: bytes) -> bytes:
    """
    Reverse byte order of X and Y coordinates for rippled compatibility.

    Rippled expects little-endian coordinates, but the C library outputs
    big-endian (standard secp256k1 format). This function converts between
    the two formats.

    Args:
        pk_bytes: 64-byte uncompressed public key (X + Y coordinates)

    Returns:
        64-byte public key with reversed coordinates

    Raises:
        ValueError: If pk_bytes is not exactly 64 bytes

    Example:
        >>> from xrpl.core.confidential import MPTCrypto
        >>> from xrpl.core.confidential.utils import reverse_coordinates
        >>> crypto = MPTCrypto()
        >>> privkey, pubkey = crypto.generate_keypair()
        >>> pubkey_reversed = reverse_coordinates(pubkey)
        >>> # Use pubkey_reversed in transactions
    """
    if len(pk_bytes) != 64:
        raise ValueError(f"Expected 64 bytes, got {len(pk_bytes)}")

    x_coord = pk_bytes[:32]
    y_coord = pk_bytes[32:64]
    return bytes(reversed(x_coord)) + bytes(reversed(y_coord))
