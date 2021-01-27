"""Miscellaneous functions that are private to xrpl.keypairs."""
import hashlib

assert (
    "ripemd160" in hashlib.algorithms_available
), """Your OpenSSL implementation does not include the RIPEMD160 algorithm,
    which is required by XRPL"""


def sha512_first_half(message: bytes) -> bytes:
    """
    Returns the first 32 bytes of SHA-512 hash of message.

    Args:
        message: Bytes input to hash.

    Returns:
        The first 32 bytes of SHA-512 hash of message.
    """
    return hashlib.sha512(message).digest()[:32]


def get_account_id(public_key: bytes) -> bytes:
    """
    :param public_key: unencoded public key
    :returns the account_id, which is defined as the RIPEMD160 of the SHA256
    of the input
    """
    sha_hash = hashlib.sha256(public_key).digest()
    return hashlib.new("ripemd160", sha_hash).digest()
