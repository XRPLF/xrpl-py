"""Methods for deriving keypairs given an SECP256k1-encoded seed."""
from typing import Any

from ecpy.curves import Curve  # type: ignore

_CURVE = Curve.get_curve("secp256k1")


def derive_keypair(entropy: Any) -> None:
    """TODO: placeholder."""
    pass


def sign(message: Any, private_key: Any) -> None:
    """TODO: placeholder."""
    pass


def is_message_valid(message: Any, signature: Any, public_key: Any) -> None:
    """TODO: placeholder."""
    pass
