"""Miscellaneous functions that are private to xrpl.keypairs."""
from hashlib import sha512


def _sha512_first_half(message):
    """
    First 32 chars of SHA-512 hash of input

    :param message: bytes input to hash
    :returns hash of message
    """
    hasher = sha512()
    hasher.update(message)
    return hasher.digest()[:32]
