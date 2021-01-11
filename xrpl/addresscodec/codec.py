import hashlib
import base58
import struct
from .exceptions import XRPLAddressCodecException

# base58 encodings: https://xrpl.org/base58-encodings.html
ACCOUNT_ID_PREFIX = [0x0] # Account address (20 bytes)
ACCOUNT_PUBLIC_KEY_PREFIX = [0x23] # value is 35; Account public key (33 bytes)
FAMILY_SEED_PREFIX = [0x21] # value is 33; Seed value (for secret keys) (16 bytes)
NODE_PUBLIC_PREFIX = [0x1C] # value is 28; Validation public key (33 bytes)

ED25519_SEED_PREFIX = [0x01, 0xE1, 0x4B] # [1, 225, 75]

XRPL_ALPHABET = b'rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz'

def encode(bytestring, prefix, expected_length):
    """
    bytestring: bytes
    prefix: list of ints (each int < 256)
    expected_length: int
    Returns the base58 encoding of the bytestring, with the given data prefix (which indicates type) and 
    while ensuring the bytestring is the expected length. 
    """
    if expected_length and len(bytestring) != expected_length:
        raise XRPLAddressCodecException('unexpected_payload_length: len(bytestring) does not match expected_length. Ensure that the bytes are a bytestring.')
    encoded_prefix = bytes(prefix)
    payload = encoded_prefix + bytestring
    return base58.b58encode_check(payload, alphabet=XRPL_ALPHABET).decode("utf-8")