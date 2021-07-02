"""Collection of public constants for XRPL."""
from enum import Enum
from re import Pattern, compile

from typing_extensions import Final


class CryptoAlgorithm(str, Enum):
    """Represents the supported cryptography algorithms."""

    ED25519 = "ed25519"
    SECP256K1 = "secp256k1"


class XRPLException(Exception):
    """Base Exception for XRPL library."""

    pass


ISO_CURRENCY_REGEX: Final[Pattern[str]] = compile("^[A-Z0-9]{3}$")
HEX_CURRENCY_REGEX: Final[Pattern[str]] = compile("^[A-F0-9]{40}$")
