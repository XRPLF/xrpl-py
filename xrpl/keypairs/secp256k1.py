"""Methods for deriving keypairs given an SECP256k1-encoded seed."""
from ecpy.curves import Curve  # type: ignore

_CURVE = Curve.get_curve("secp256k1")


def derive_keypair(entropy):
    """TODO: placeholder."""
    pass


def sign(message, private_key):
    """TODO: placeholder."""
    pass


def is_message_valid(message, signature, public_key):
    """TODO: placeholder."""
    pass
