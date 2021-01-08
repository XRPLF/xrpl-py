import hashlib
import base58
import struct

# base58 encodings: https://xrpl.org/base58-encodings.html
ACCOUNT_ID = 0 # Account address (20 bytes)
ACCOUNT_PUBLIC_KEY = 0x23 # Account public key (33 bytes)
FAMILY_SEED = 0x21 # 33; Seed value (for secret keys) (16 bytes)
NODE_PUBLIC = 0x1C # 28; Validation public key (33 bytes)

ED25519_SEED = [0x01, 0xE1, 0x4B] # [1, 225, 75]

XRPL_ALPHABET = b'rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz'

def sha256(bytestring):
    """
    Returns the SHA256 hash of the provided bytestring. 
    """
    return hashlib.sha256(bytestring).digest()

def encode(bytestring, versions, expected_length):
    """
    Returns the base58 encoding of the bytestring, with the given data version type and 
    while ensuring the bytestring is the expected length. 
    """
    if expected_length and len(bytestring) != expected_length:
        raise Exception('unexpected_payload_length: len(bytestring) does not match expected_length. Ensure that the bytes are a bytestring.')
    encoded_versions = bytes(versions).ljust(1, b'\0')
    payload = encoded_versions + bytestring
    checksum = sha256(sha256(payload))[:4]
    return base58.b58encode(payload + checksum, alphabet=XRPL_ALPHABET).decode("utf-8")