"""Various utility functions for working with keypairs."""

import binascii
import hashlib

def bytes_to_hex(input_bytes):
    """:param input_bytes: input to convert
    :returns hex representation of input
    """
    # don't use input_bytes.hex() to provide support
    # for older python3 versions
    return binascii.hexlify(input_bytes)

def hex_to_bytes(input_hex):
    """:param input_hex: input to convert
    :returns bytes representation of input
    """
    return binascii.unhexlify(input_hex)

def compute_public_key_hash(public_key_bytes):
    """:param public_key_bytes: public key input
    :returns hash of input
    """
    sha_hasher = hashlib.sha256()
    sha_hasher.update(public_key_bytes)
    hash256 = sha_hasher.digest()

    ripe_hasher = hashlib.new("ripemd160")
    ripe_hasher.update(hash256)
    return ripe_hasher.digest()
