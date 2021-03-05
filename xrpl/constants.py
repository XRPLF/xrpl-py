"""Collection of public constants for XRPL."""
from enum import Enum


class CryptoAlgorithm(str, Enum):
    """Represents the supported cryptography algorithms."""

    ED25519 = "ED25519"
    SECP256K1 = "SECP256K1"


class XRPLException(Exception):
    """Base Exception for XRPL library."""

    pass
