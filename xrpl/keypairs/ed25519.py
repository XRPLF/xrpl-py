"""
Methods for deriving keypairs given an ED25519-encoded seed.

TODO - is there a way to do an interface for this?
"""
from hashlib import sha512
from typing import Final, Tuple

from ecpy.curves import Curve  # type: ignore
from ecpy.eddsa import EDDSA  # type: ignore
from ecpy.keys import ECPrivateKey, ECPublicKey  # type: ignore

from xrpl.keypairs.helpers import sha512_first_half

_PREFIX: Final[str] = "ED"
_CURVE: Final[Curve] = Curve.get_curve("Ed25519")
_SIGNER: Final[EDDSA] = EDDSA(sha512)


def derive_keypair(seed: bytes) -> Tuple[str, str]:
    """
    seed: an ED25519 seed from which to derive keypair
    :returns (private key, public key) derived from seed
    """
    # the private key is just the sha512_first_half of the seed and the public
    # key is derived from the private key using the curve.
    raw_private = sha512_first_half(seed)
    wrapped_private = ECPrivateKey(int.from_bytes(raw_private, "big"), _CURVE)
    wrapped_public = EDDSA.get_public_key(wrapped_private, sha512).W
    raw_public = _CURVE.encode_point(wrapped_public)
    return _key_format(raw_public), _key_format(raw_private)


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


def _key_format(raw_key: bytes) -> str:
    return (_PREFIX + raw_key.hex()).upper()
