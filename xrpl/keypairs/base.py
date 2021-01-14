"""Base functions for keypairs module."""

import hashlib
import binascii
import random
from xrpl import addresscodec
from .exceptions import XRPLKeypairsException


def _hash(message):
    """Fundamental method, returning
    hash of input.

    :param message: input to hash
    :returns hash of message
    """
    hasher = hashlib.sha512()
    hasher.update(bytes(str(message), "UTF-8"))
    return hasher.digest()[:32]


def _compute_public_key_hash(public_key_bytes):
    """TODO (greg) - implemented these private funcs not sure they will be
    needed atm"""
    sha_hasher = hashlib.sha256()
    sha_hasher.update(bytes(str(public_key_bytes), "UTF-8"))
    hash256 = sha_hasher.digest()

    ripe_hasher = hashlib.new("ripemd160")
    ripe_hasher.update(hash256)
    return ripe_hasher.digest()


def _get_algorithm_from_key(key):
    """TODO (greg) - implemented these private funcs not sure they will be
    needed atm"""
    bytes_from_key = binascii.unhexlify(key)
    if len(bytes_from_key) == 33 and bytes_from_key[0] == 0xED:
        return "ed25519"
    return "ecdsa-secp256k1"


def generate_seed(entropy=None, algorithm=addresscodec.ED25519):
    """TODO (greg): not sure it's useful to even have this wrapper"""
    if entropy is None:
        return addresscodec.encode_seed(random.randbytes(16), algorithm)
    if len(entropy) >= 16:
        return addresscodec.encode_seed(entropy[:16], algorithm)
    raise XRPLKeypairsException(
        """provided entropy {} is too short; must
    have length of at least 16""".format(
            entropy
        )
    )
