"""Miscellaneous functions that are private to xrpl.keypairs."""
from hashlib import sha512


def sha512_first_half(message: bytes) -> str:
    """
    :param message: bytes input to hash
    :returns first 32 chars of SHA-512 hash of message
    """
    hasher = sha512()
    hasher.update(message)
    return hasher.digest()[:32]
