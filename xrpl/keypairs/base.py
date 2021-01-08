"""Base functions for keypairs module."""

import hashlib


def hash(message):
    """Fundamental method, returning
    hash of input.

    :param message: input to hash
    :returns hash of message
    """
    hasher = hashlib.sha512()
    hasher.update(bytes(str(message), "UTF-8"))
    return hasher.digest()[:32]
