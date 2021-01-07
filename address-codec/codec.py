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
    return hashlib.sha256(bytestring).digest()

def encode(bytestring, versions, expected_length):
    if expected_length and len(bytestring) != expected_length:
        raise Exception('unexpected_payload_length: len(bytestring) does not match expected_length. Ensure that the bytes are a bytestring.')
    encoded_versions = bytes(versions).ljust(1, b'\0')
    payload = encoded_versions + bytestring
    checksum = sha256(sha256(payload))[:4]
    return base58.b58encode(payload + checksum, alphabet=XRPL_ALPHABET).decode("utf-8")

base58_string = 'rJrRMgiRgrU6hDF4pgu5DXQdWyPbY35ErN'
hex_string = 'BA8E78626EE42C41B46D46C3048DF3A1C3C87072'
encoded_hex = bytes.fromhex(hex_string)

result = encode(encoded_hex, [ACCOUNT_ID], 20)
print(result)
print(base58_string)
assert(result == base58_string)

# pubkey_hex = '0303E20EC6B4A39A629815AE02C0A1393B9225E3B890CAE45B59F42FA29BE9668D'

# pubkey = bytes.fromhex(pubkey_hex)
# assert(len(pubkey)==33)

# pubkey_inner_hash = sha256(pubkey)
# pubkey_outer_hash = hashlib.new('ripemd160')
# pubkey_outer_hash.update(pubkey_inner_hash)
# account_id = pubkey_outer_hash.digest()

# address_type_prefix = bytes([0x00])
# payload = address_type_prefix + account_id
# print(payload)
# checksum_hash1 = sha256(payload)
# checksum_hash2 = sha256(checksum_hash1)
# print(checksum_hash2)
# checksum = checksum_hash2[:4]
# print(checksum, checksum.hex())
# # checksum = b'\x94\xb9\xf5\x8e' #int: 2495214990
# # print(checksum, checksum.hex())

# data_to_encode = payload + checksum
# address = base58.b58encode(data_to_encode, alphabet=XRPL_ALPHABET)
# print(address)
# print(b'rnBFvgZphmN39GWzUJeUitaP22Fr9be75H')