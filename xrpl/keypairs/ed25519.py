"""
Methods for deriving keypairs given an ED25519-encoded seed.

TODO - is there a way to do an interface for this?
"""
from hashlib import sha512
from typing import Final, Tuple

from ecpy.curves import Curve
from ecpy.eddsa import EDDSA
from ecpy.keys import ECPrivateKey, ECPublicKey

from xrpl.keypairs import helpers

_PREFIX: Final[str] = "ED"
_CURVE: Final[Curve] = Curve.get_curve("Ed25519")
_SIGNER: Final[EDDSA] = EDDSA(sha512)


def derive(seed: str) -> Tuple[str, str]:
    """
    seed: an ED25519 seed from which to derive keypair
    :returns (private key, public key) derived from seed
    """
    raw_private = helpers._sha512_first_half(seed)
    wrapped_private = ECPrivateKey(int(raw_private.hex(), 16), _CURVE)
    wrapped_public = EDDSA.get_public_key(wrapped_private, sha512).W
    raw_public = _CURVE.encode_point(wrapped_public)
    return [_key_format(raw) for raw in [raw_public, raw_private]]


def sign(message: str, private_key: str) -> bytes:
    """
    Sign message in ED25519 given private-key
    returns: :bytes
    """
    raw_private = private_key[len(_PREFIX) :]
    wrapped_private = ECPrivateKey(int(raw_private, 16), _CURVE)
    return _SIGNER.sign(message, wrapped_private)


def is_message_valid(message: str, signature: bytes, public_key: str) -> bool:
    """:returns: True if message is valid given signature"""
    raw_public = public_key[len(_PREFIX) :]
    public_key_point = _CURVE.decode_point(bytes.fromhex(raw_public))
    wrapped_public = ECPublicKey(public_key_point)
    return _SIGNER.verify(message, signature, wrapped_public)


def _key_format(raw_key: str) -> str:
    return (_PREFIX + raw_key.hex()).upper()
