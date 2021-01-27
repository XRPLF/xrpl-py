"""Methods for deriving keypairs given an ED25519-encoded seed."""
from hashlib import sha512
from typing import Final, Tuple

from ecpy.curves import Curve  # type: ignore
from ecpy.eddsa import EDDSA  # type: ignore
from ecpy.keys import ECPrivateKey, ECPublicKey  # type: ignore

from xrpl.keypairs.exceptions import XRPLKeypairsException
from xrpl.keypairs.helpers import sha512_first_half

_PREFIX: Final[str] = "ED"
_CURVE: Final[Curve] = Curve.get_curve("Ed25519")
_SIGNER: Final[EDDSA] = EDDSA(sha512)


def derive_keypair(decoded_seed: bytes, is_validator: bool) -> Tuple[str, str]:
    """
    decoded_seed: an ED25519 seed from which to derive keypair
    is_validator: if True indicates that caller wishes to derive a validator keypair
    from this seed, however, that is always invalid for this algorithm and
    will cause this function to raise.
    :returns (private key, public key) derived from seed
    """
    if is_validator:
        raise XRPLKeypairsException("validator keypairs cannot use ED25519")

    raw_private = sha512_first_half(decoded_seed)
    private = ECPrivateKey(int.from_bytes(raw_private, "big"), _CURVE)
    public = EDDSA.get_public_key(private, sha512)
    return (
        _format_key(_public_key_to_str(public)),
        _format_key(_private_key_to_str(private)),
    )


def sign(message: str, private_key: str) -> bytes:
    """
    param: message: message to sign
    param: private_key: key with which to sign message
    returns: signature of message signed using private_key
    """
    raw_private = private_key[len(_PREFIX) :]
    wrapped_private = ECPrivateKey(int(raw_private, 16), _CURVE)
    return _SIGNER.sign(message, wrapped_private)


def is_message_valid(message: str, signature: bytes, public_key: str) -> bool:
    """
    param: message: message to check against signature
    param: signature: signature of message to to verify
    param: public_key: public key corresponding to private key used to
    generate signature
    :returns: True if message is valid given signature and public_key
    """
    raw_public = public_key[len(_PREFIX) :]
    public_key_point = _CURVE.decode_point(bytes.fromhex(raw_public))
    wrapped_public = ECPublicKey(public_key_point)
    return _SIGNER.verify(message, signature, wrapped_public)


def _public_key_to_str(key: ECPublicKey) -> str:
    return _CURVE.encode_point(key.W).hex()


def _private_key_to_str(key: ECPrivateKey) -> str:
    return format(key.d, "x")


def _format_key(keystr: str) -> str:
    return (_PREFIX + keystr).upper()
