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

SEED_LENGTH = 16

XRPL_ALPHABET = b'rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz'

ED25519 = 'ed25519'
SECP256K1 = 'secp256k1'

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

def decode(b58_string, prefix_length):
    """
    b58_string: string representing a base58 value
    prefix_length: int representing the length in bytes of the prefix prepended to the bytestring

    Returns the byte decoding of the base58-encoded string
    """
    # TODO: (mvadari) Figure out if prefix_length is the right way to do this or if there is a better way
    return base58.b58decode_check(b58_string, alphabet=XRPL_ALPHABET)[prefix_length:]

def encode_seed(entropy, encoding_type):
    """
    entropy: SEED_LENGTH bytes
    encoding_type: either ED25519 or SECP256K1

    Returns an encoded seed
    """
    if len(entropy) != SEED_LENGTH:
        raise XRPLAddressCodecException('Entropy must have length {}'.format(SEED_LENGTH))

    if encoding_type == ED25519:
        prefix = ED25519_SEED_PREFIX
    elif encoding_type == SECP256K1:
        prefix = FAMILY_SEED_PREFIX
    else:
        raise XRPLAddressCodecException('Encoding type is not valid; must be either \'{}\' or \'{}\''.format(SECP256K1, ED25519))
    
    return encode(entropy, prefix, SEED_LENGTH)

