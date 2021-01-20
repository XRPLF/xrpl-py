"""Methods for deriving keypairs given an SECP256k1-encoded seed."""
from ecpy.curves import Curve

_PREFIX = "00"
_CURVE = Curve.get_curve("secp256k1")


def derive(entropy):
    """
    :param entropy: raw entropy
    :returns (private key, public key)
    """
    pass


def sign(message, private_key):
    """Sign message in SECP256k1 given private-key"""
    pass


def is_message_valid(message, signature, public_key):
    """Verify that message matches signature given public_key"""
    pass
