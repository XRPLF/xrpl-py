"""Collection of public constants for XRPL"""
from enum import Enum


class CryptoAlgorithm(Enum):
    """Represents the supported cryptography algorithms"""

    ED25519 = 0
    SECP256K1 = 1
