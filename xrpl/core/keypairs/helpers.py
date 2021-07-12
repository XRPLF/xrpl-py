"""Miscellaneous functions that are private to xrpl.core.keypairs."""
import hashlib


if "ripemd160" in hashlib.algorithms_available:
    ripemd160 = lambda x: hashlib.new("ripemd160", x).digest()
else:
    try:
        from Crypto.Hash import RIPEMD
        ripemd160 = lambda x: RIPEMD.new(x).digest()
    except ImportError:
        raise ImportError("""Your OpenSSL implementation does not include the RIPEMD160 """
                          """algorithm, which is required by XRPL, or pycrypto """
                          """needs installing""")


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
    Returns the account ID for a given public key. See
    https://xrpl.org/cryptographic-keys.html#account-id-and-address
    to learn about the relationship between keys and account IDs.

    Args:
        public_key: Unencoded public key.

    Returns:
        The account ID for the given public key.
    """
    sha_hash = hashlib.sha256(public_key).digest()
    return ripemd160(sha_hash)
