"""This module encodes and decodes various types of base58 encodings."""

from typing import List, Tuple

import base58

from xrpl import CryptoAlgorithm
from xrpl.core.addresscodec.exceptions import XRPLAddressCodecException
from xrpl.core.addresscodec.utils import XRPL_ALPHABET

# base58 encodings: https://xrpl.org/base58-encodings.html
CLASSIC_ADDRESS_PREFIX = [0x0]  # Account address (20 bytes)
ACCOUNT_PUBLIC_KEY_PREFIX = [0x23]  # value is 35; Account public key (33 bytes)
FAMILY_SEED_PREFIX = [0x21]  # value is 33; Seed value (for secret keys) (16 bytes)
NODE_PUBLIC_KEY_PREFIX = [0x1C]  # value is 28; Validation public key (33 bytes)
ED25519_SEED_PREFIX = [0x01, 0xE1, 0x4B]  # [1, 225, 75]

SEED_LENGTH = 16
CLASSIC_ADDRESS_LENGTH = 20
NODE_PUBLIC_KEY_LENGTH = 33
ACCOUNT_PUBLIC_KEY_LENGTH = 33

_ALGORITHM_TO_PREFIX_MAP = {
    CryptoAlgorithm.ED25519: ED25519_SEED_PREFIX,
    CryptoAlgorithm.SECP256K1: FAMILY_SEED_PREFIX,
}
# Ensure that each algorithm has a prefix
assert len(_ALGORITHM_TO_PREFIX_MAP) == len(CryptoAlgorithm)


def _encode(bytestring: bytes, prefix: List[int], expected_length: int) -> str:
    """
    Returns the base58 encoding of the bytestring, with the given data prefix
    (which indicates type) and while ensuring the bytestring is the expected
    length.
    """
    if expected_length and len(bytestring) != expected_length:
        error_message = """unexpected_payload_length: len(bytestring) does not match expected_length.
        Ensure that the bytes are a bytestring."""
        raise XRPLAddressCodecException(error_message)
    encoded_prefix = bytes(prefix)
    payload = encoded_prefix + bytestring
    return base58.b58encode_check(payload, alphabet=XRPL_ALPHABET).decode("utf-8")


def _decode(b58_string: str, prefix: bytes) -> bytes:
    """
    b58_string: A base58 value
    prefix: The prefix prepended to the bytestring

    Returns the byte decoding of the base58-encoded string.
    """
    # TODO: (mvadari) Figure out if prefix is the right way to do this or if
    # there is a better way
    prefix_length = len(prefix)
    decoded = base58.b58decode_check(b58_string, alphabet=XRPL_ALPHABET)
    if decoded[:prefix_length] != prefix:
        raise XRPLAddressCodecException("Provided prefix is incorrect")
    return decoded[prefix_length:]


def encode_seed(entropy: bytes, encoding_type: CryptoAlgorithm) -> str:
    """
    Returns an encoded seed.

    Args:
        entropy: Entropy bytes of SEED_LENGTH.
        encoding_type: Either ED25519 or SECP256K1.

    Returns:
        An encoded seed.

    Raises:
        XRPLAddressCodecException: If entropy is not of length SEED_LENGTH
            or the encoding type is not one of CryptoAlgorithm.
    """
    if len(entropy) != SEED_LENGTH:
        raise XRPLAddressCodecException(f"Entropy must have length {SEED_LENGTH}")
    if encoding_type not in CryptoAlgorithm:
        raise XRPLAddressCodecException(
            f"Encoding type must be one of {CryptoAlgorithm}"
        )

    prefix = _ALGORITHM_TO_PREFIX_MAP[encoding_type]
    return _encode(entropy, prefix, SEED_LENGTH)


def decode_seed(seed: str) -> Tuple[bytes, CryptoAlgorithm]:
    """
    Returns (decoded seed, its algorithm).

    Args:
        seed: b58 encoding of a seed.

    Returns:
        (decoded seed, its algorithm).

    Raises:
        XRPLAddressCodecException: If the seed is invalid.
    """
    for algorithm in CryptoAlgorithm:
        prefix = _ALGORITHM_TO_PREFIX_MAP[algorithm]
        try:
            decoded_result = _decode(seed, bytes(prefix))
            return decoded_result, algorithm
        except XRPLAddressCodecException:
            # prefix is incorrect, wrong algorithm
            continue
    raise XRPLAddressCodecException(
        "Invalid seed; could not determine encoding algorithm"
    )


def encode_classic_address(bytestring: bytes) -> str:
    """
    Returns the classic address encoding of these bytes as a base58 string.

    Args:
        bytestring: Bytes to be encoded.

    Returns:
        The classic address encoding of these bytes as a base58 string.
    """
    return _encode(bytestring, CLASSIC_ADDRESS_PREFIX, CLASSIC_ADDRESS_LENGTH)


def decode_classic_address(classic_address: str) -> bytes:
    """
    Returns the decoded bytes of the classic address.

    Args:
        classic_address: Classic address to be decoded.

    Returns:
        The decoded bytes of the classic address.
    """
    return _decode(classic_address, bytes(CLASSIC_ADDRESS_PREFIX))


def encode_node_public_key(bytestring: bytes) -> str:
    """
    Returns the node public key encoding of these bytes as a base58 string.

    Args:
        bytestring: Bytes to be encoded.

    Returns:
        The node public key encoding of these bytes as a base58 string.
    """
    return _encode(bytestring, NODE_PUBLIC_KEY_PREFIX, NODE_PUBLIC_KEY_LENGTH)


def decode_node_public_key(node_public_key: str) -> bytes:
    """
    Returns the decoded bytes of the node public key

    Args:
        node_public_key: Node public key to be decoded.

    Returns:
        The decoded bytes of the node public key.

    """
    return _decode(node_public_key, bytes(NODE_PUBLIC_KEY_PREFIX))


def encode_account_public_key(bytestring: bytes) -> str:
    """
    Returns the account public key encoding of these bytes as a base58 string.

    Args:
        bytestring: Bytes to be encoded.

    Returns:
        The account public key encoding of these bytes as a base58 string.
    """
    return _encode(bytestring, ACCOUNT_PUBLIC_KEY_PREFIX, ACCOUNT_PUBLIC_KEY_LENGTH)


def decode_account_public_key(account_public_key: str) -> bytes:
    """
    Returns the decoded bytes of the account public key.

    Args:
        account_public_key: Account public key to be decoded.

    Returns:
        The decoded bytes of the account public key.
    """
    return _decode(account_public_key, bytes(ACCOUNT_PUBLIC_KEY_PREFIX))


def is_valid_classic_address(classic_address: str) -> bool:
    """
    Returns whether `classic_address` is a valid classic address.

    Args:
        classic_address: The classic address to validate.

    Returns:
        Whether `classic_address` is a valid classic address.
    """
    try:
        decode_classic_address(classic_address)
        return True
    except (XRPLAddressCodecException, ValueError):
        return False
