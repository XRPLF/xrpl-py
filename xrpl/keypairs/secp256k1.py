"""Methods for deriving keypairs given an SECP256k1-encoded seed."""
# The process for using SECP256k1 is complex and more involved than ED25519.
#
# See https://xrpl.org/cryptographic-keys.html#secp256k1-key-derivation
# for an overview of the algorithm.
from struct import pack
from typing import Callable, Final, Generator, Literal, Tuple

from ecpy.curves import Curve  # type: ignore
from ecpy.ecdsa import ECDSA  # type: ignore
from ecpy.keys import ECPrivateKey, ECPublicKey  # type: ignore

from xrpl.keypairs.exceptions import KeypairException
from xrpl.keypairs.helpers import sha512_first_half

_CURVE: Final[Curve] = Curve.get_curve("secp256k1")
_GROUP_ORDER: Final[int] = _CURVE.order
_SIGNER: Final[ECDSA] = ECDSA()

# keys must be _KEY_LENGTH long and may be left padded
# with _PADDING_PREFIX to accomplish that
_KEY_LENGTH: Final[int] = 66
_PADDING_PREFIX: Final[str] = "0"

# generated sequence values are 4 byte unsigned big-endian.
#
# _SEQUENCE_MAX is the largest number that can be represented in
# this scheme + 1.
#
# _SEQUENCE_BYTE_FORMAT_STRING is a format string representing
# _SEQUENCE_SIZE unsigned big-endian bytes.
_SEQUENCE_SIZE: Final[int] = 4
_SEQUENCE_MAX: Final[int] = 256 ** _SEQUENCE_SIZE
_SEQUENCE_BYTE_FORMAT_STRING: Final[str] = ">{}".format("B" * _SEQUENCE_SIZE)

# intermediate private keys are always padded with 4 bytes of zeros
_INTERMEDIATE_KEYPAIR_PADDING: Final[bytes] = pack(">BBBB", 0, 0, 0, 0)


def derive_keypair(decoded_seed: bytes, is_validator: bool) -> Tuple[str, str]:
    """
    :param decoded_seed: :bytes decoded seed
    is_validator: if True indicates that caller wishes to derive a validator
    keypair from this seed.
    :returns (private key :string, public key :string)
    """
    root_public, root_private = _do_derive_part(decoded_seed, "root")
    # validator keys just stop at the first pass
    if is_validator:
        return _format_keys(root_public, root_private)

    mid_public, mid_private = _do_derive_part(
        _public_key_to_bytes(root_public),
        "mid",
    )
    final_public, final_private = _derive_final_pair(
        root_public,
        root_private,
        mid_public,
        mid_private,
    )
    return _format_keys(final_public, final_private)


def sign(message: str, private_key: str) -> bytes:
    """
    Sign message in SECP256k1 given private-key
    returns: :bytes
    """
    wrapped_private = ECPrivateKey(int(private_key, 16), _CURVE)
    return _SIGNER.sign(message, wrapped_private)


def is_message_valid(message: str, signature: bytes, public_key: str) -> bool:
    """
    Verify that message matches signature given public_key
    :param message: string
    :param signature: string
    :param public_key: string
    :returns :boolean
    """
    public_key_point = _CURVE.decode_point(bytes.fromhex(public_key))
    wrapped_public = ECPublicKey(public_key_point)
    return _SIGNER.verify(message, signature, wrapped_public)


def _format_keys(public: ECPublicKey, private: ECPrivateKey) -> Tuple[str, str]:
    # returning a list comprehension triggers mypy (appropriately, because
    # then we're actually returning a list), so doing this very inelegantly
    return (
        _format_key(_public_key_to_str(public)),
        _format_key(_private_key_to_str(private)),
    )


def _format_key(keystr: str) -> str:
    return keystr.rjust(_KEY_LENGTH, _PADDING_PREFIX).upper()


def _public_key_to_bytes(key: ECPublicKey) -> bytes:
    return bytes(_CURVE.encode_point(key.W, compressed=True))


def _public_key_to_str(key: ECPublicKey) -> str:
    return _public_key_to_bytes(key).hex()


def _private_key_to_str(key: ECPrivateKey) -> str:
    return format(key.d, "x")


def _do_derive_part(
    bytes_input: bytes, phase: Literal["root", "mid"]
) -> Tuple[ECPublicKey, ECPrivateKey]:
    def candidate_merger(candidate: bytes) -> bytes:
        if phase == "root":
            return bytes_input + candidate
        return bytes_input + _INTERMEDIATE_KEYPAIR_PADDING + candidate

    raw_private = _get_secret(candidate_merger)
    wrapped_private = ECPrivateKey(int.from_bytes(raw_private, "big"), _CURVE)
    return wrapped_private.get_public_key(), wrapped_private


def _derive_final_pair(
    root_public: ECPublicKey,
    root_private: ECPrivateKey,
    mid_public: ECPublicKey,
    mid_private: ECPrivateKey,
) -> Tuple[ECPublicKey, ECPrivateKey]:
    raw_private = (root_private.d + mid_private.d) % _GROUP_ORDER
    wrapped_private = ECPrivateKey(raw_private, _CURVE)
    wrapped_public = ECPublicKey(_CURVE.add_point(root_public.W, mid_public.W))
    return wrapped_public, wrapped_private


def _get_secret(candidate_merger: Callable[[bytes], bytes]) -> bytes:
    """
    Given a function `candidate_merger` that knows how
    to prepare a sequence_candidate bytesting from into
    a possible full candidate secret, returns the first sequence
    value that is valid. If none are valid, raises, however this
    should be so exceedingly rare as to ignore.
    """
    for root in _root_sequence():
        candidate = sha512_first_half(candidate_merger(root))
        if _is_secret_valid(candidate):
            return candidate
    raise KeypairException(
        """Could not determine a key pair.
        This is extremely improbable. Please try again.""",
    )


def _is_secret_valid(secret: bytes) -> bool:
    numerical_secret = int.from_bytes(secret, "big")
    return numerical_secret in range(1, _GROUP_ORDER)


def _root_sequence() -> Generator[bytes, None, None]:
    """Generates all possible root values"""
    for raw_root in range(_SEQUENCE_MAX):
        # get digits of root via integer division and modulo
        # but stepping backwards from _SEQUENCE_SIZE...0
        root_digits = [
            (raw_root // 256 ** i) % 256 for i in reversed(range(_SEQUENCE_SIZE))
        ]
        root = pack(_SEQUENCE_BYTE_FORMAT_STRING, *root_digits)
        yield root
