"""Collection of public constants for XRPL."""
from enum import Enum

CryptoAlgorithm = Enum("CryptoAlgorithm", "ED25519 SECP256K1")


class XRPLException(Exception):
    """Base Exception for XRPL library."""

    pass
