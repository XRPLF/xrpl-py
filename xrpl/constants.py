"""Collection of public constants for XRPL."""
import re
from enum import Enum

from typing_extensions import Final


class CryptoAlgorithm(str, Enum):
    """Represents the supported cryptography algorithms."""

    ED25519 = "ed25519"
    SECP256K1 = "secp256k1"


class XRPLException(Exception):
    """Base Exception for XRPL library."""

    pass


ISO_CURRENCY_REGEX: Final[re.Pattern[str]] = re.compile(f"^[A-Z0-9]{3}$")
HEX_CURRENCY_REGEX: Final[re.Pattern[str]] = re.compile(f"^[A-F0-9]{40}$")
