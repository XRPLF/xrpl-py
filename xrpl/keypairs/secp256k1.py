"""Methods for deriving keypairs given an SECP256k1-encoded seed."""
# The process for using SECP256k1 is complex and more involved than ED25519.
#
# See https://xrpl.org/cryptographic-keys.html#secp256k1-key-derivation
# for an overview of the algorithm.
from hashlib import sha256
from typing import Callable, Tuple

from ecpy.curves import Curve  # type: ignore
from ecpy.ecdsa import ECDSA  # type: ignore
from ecpy.keys import ECPrivateKey, ECPublicKey  # type: ignore
from typing_extensions import Final, Literal

from xrpl.keypairs.exceptions import XRPLKeypairsException
from xrpl.keypairs.helpers import sha512_first_half

_CURVE: Final[Curve] = Curve.get_curve("secp256k1")
_GROUP_ORDER: Final[int] = _CURVE.order
_SIGNER: Final[ECDSA] = ECDSA("DER")

# String keys must be _KEY_LENGTH long
_KEY_LENGTH: Final[int] = 66
# Pad string keys with _PADDING_PREFIX to reach _KEY_LENGTH
_PADDING_PREFIX: Final[str] = "0"

# Generated sequence values are _SEQUENCE_SIZE bytes unsigned big-endian
_SEQUENCE_SIZE: Final[int] = 4
_SEQUENCE_MAX: Final[int] = 256 ** _SEQUENCE_SIZE

# Intermediate private keys are always padded with 4 bytes of zeros
_INTERMEDIATE_KEYPAIR_PADDING: Final[bytes] = (0).to_bytes(
    4,
    byteorder="big",
    signed=False,
)


def derive_keypair(decoded_seed: bytes, is_validator: bool) -> Tuple[str, str]:
    """
    Derives a keypair using SECP256k1.

    Args:
        decoded_seed: Decoded seed.
        is_validator: Whether to derive a validator keypair from this seed.

    Returns:
        A private and public key pair.
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
    Signs message in SECP256k1 using the given private key.

    Args:
        message: The message to sign in SECP256k1.
        private_key: The private key to use to sign the message.

    Returns:
        The signed message.
    """
    wrapped_private = ECPrivateKey(int(private_key, 16), _CURVE)
    return _SIGNER.sign_rfc6979(
        sha512_first_half(message),
        wrapped_private,
        sha256,
        canonical=True,
    )


def is_message_valid(message: str, signature: bytes, public_key: str) -> bool:
    """
    Verifies that message matches signature given public_key.

    Args:
        message: The message to validate.
        signature: The signature of the message.
        public_key: The public_key to use to verify the message.

    Returns:
        Whether the message matches the signature given the public key.
    """
    public_key_point = _CURVE.decode_point(bytes.fromhex(public_key))
    wrapped_public = ECPublicKey(public_key_point)
    return _SIGNER.verify(sha512_first_half(message), signature, wrapped_public)


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
    """
    Given bytes_input determine public/private keypair for a given phase of
    this algorithm. The difference between generating the root and
    intermediate keypairs is just what bytes are input by the caller and that
    the intermediate keypair needs to inject _INTERMEDIATE_KEYPAIR_PADDING
    into the value to hash to get the raw private key.
    """

    def _candidate_merger(candidate: bytes) -> bytes:
        if phase == "root":
            return bytes_input + candidate
        return bytes_input + _INTERMEDIATE_KEYPAIR_PADDING + candidate

    raw_private = _get_secret(_candidate_merger)
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
    to prepare a sequence candidate bytestring into
    a possible full candidate secret, returns the first sequence
    value that is valid. If none are valid, raises; however this
    should be so exceedingly rare as to ignore.
    """
    for raw_root in range(_SEQUENCE_MAX):
        root = raw_root.to_bytes(
            _SEQUENCE_SIZE,
            byteorder="big",
            signed=False,
        )
        candidate = sha512_first_half(candidate_merger(root))
        if _is_secret_valid(candidate):
            return candidate
    raise XRPLKeypairsException(
        """Could not determine a key pair.
        This is extremely improbable. Please try again.""",
    )


def _is_secret_valid(secret: bytes) -> bool:
    numerical_secret = int.from_bytes(secret, "big")
    return numerical_secret in range(1, _GROUP_ORDER)
