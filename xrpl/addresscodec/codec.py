"""TODO: D100 Missing docstring in public module."""
import base58
from .exceptions import XRPLAddressCodecException
from .utils import XRPL_ALPHABET

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

ED25519 = "ed25519"
SECP256K1 = "secp256k1"
ALGORITHM_TO_PREFIX_MAP = {
    ED25519: ED25519_SEED_PREFIX,
    SECP256K1: FAMILY_SEED_PREFIX,
}
ALGORITHMS = list(ALGORITHM_TO_PREFIX_MAP)


def encode(bytestring, prefix, expected_length):
    """
    bytestring: bytes
    prefix: list of ints (each int < 256)
    expected_length: int

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


def decode(b58_string, prefix):
    """
    b58_string: string representing a base58 value
    prefix: the prefix prepended to the bytestring, in bytes

    Returns the byte decoding of the base58-encoded string
    """
    # TODO: (mvadari) Figure out if prefix is the right way to do this or if
    # there is a better way
    prefix_length = len(prefix)
    decoded = base58.b58decode_check(b58_string, alphabet=XRPL_ALPHABET)
    if decoded[:prefix_length] != prefix:
        raise XRPLAddressCodecException("Provided prefix is incorrect")
    return decoded[prefix_length:]


def encode_seed(entropy, encoding_type):
    """
    entropy: SEED_LENGTH bytes
    encoding_type: either ED25519 or SECP256K1

    Returns an encoded seed
    """
    if len(entropy) != SEED_LENGTH:
        raise XRPLAddressCodecException(
            "Entropy must have length {}".format(SEED_LENGTH)
        )
    if encoding_type not in ALGORITHMS:
        raise XRPLAddressCodecException(
            "Encoding type must be one of {}".format(ALGORITHMS)
        )

    prefix = ALGORITHM_TO_PREFIX_MAP[encoding_type]
    return encode(entropy, prefix, SEED_LENGTH)


def decode_seed(seed):
    """
    seed: b58 encoding of a seed

    Returns (decoded seed, its algorithm)
    """
    for algorithm in ALGORITHMS:
        prefix = ALGORITHM_TO_PREFIX_MAP[algorithm]
        try:
            decoded_result = decode(seed, bytes(prefix))
            return decoded_result, algorithm
        except XRPLAddressCodecException:
            # prefix is incorrect, wrong algorithm
            continue
    raise XRPLAddressCodecException(
        "Invalid seed; could not determine encoding algorithm"
    )


def encode_classic_address(bytestring):
    """
    bytestring: bytes to be encoded

    Returns the classic address encoding of these bytes as a base58 string
    """
    return encode(bytestring, CLASSIC_ADDRESS_PREFIX, CLASSIC_ADDRESS_LENGTH)


def decode_classic_address(classic_address):
    """
    classic_address: classic address to be decoded

    Returns the decoded bytes of the classic address
    """
    return decode(classic_address, bytes(CLASSIC_ADDRESS_PREFIX))


def encode_node_public_key(bytestring):
    """
    bytestring: bytes to be encoded

    Returns the node public key encoding of these bytes as a base58 string
    """
    return encode(bytestring, NODE_PUBLIC_KEY_PREFIX, NODE_PUBLIC_KEY_LENGTH)


def decode_node_public_key(node_public_key):
    """
    node_public_key: node public key to be decoded

    Returns the decoded bytes of the node public key
    """
    return decode(node_public_key, bytes(NODE_PUBLIC_KEY_PREFIX))


def encode_account_public_key(bytestring):
    """
    bytestring: bytes to be encoded

    Returns the account public key encoding of these bytes as a base58 string
    """
    return encode(bytestring, ACCOUNT_PUBLIC_KEY_PREFIX, ACCOUNT_PUBLIC_KEY_LENGTH)


def decode_account_public_key(account_public_key):
    """
    account_public_key: account public key to be decoded

    Returns the decoded bytes of the account public key
    """
    return decode(account_public_key, bytes(ACCOUNT_PUBLIC_KEY_PREFIX))
