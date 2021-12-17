"""Collection of public constants for XRPL."""
from decimal import Context
from enum import Enum
from re import compile
from typing import Pattern

from typing_extensions import Final


class CryptoAlgorithm(str, Enum):
    """Represents the supported cryptography algorithms."""

    ED25519 = "ed25519"
    SECP256K1 = "secp256k1"


class XRPLException(Exception):
    """Base Exception for XRPL library."""

    pass


ISO_CURRENCY_REGEX: Final[Pattern[str]] = compile("^[A-Z0-9]{3}$")
"""
:meta private:
"""

HEX_CURRENCY_REGEX: Final[Pattern[str]] = compile("^[A-F0-9]{40}$")
"""
:meta private:
"""

# Constants for validating amounts.
MIN_IOU_EXPONENT: Final[int] = -96
"""
:meta private:
"""
MAX_IOU_EXPONENT: Final[int] = 80
"""
:meta private:
"""
MAX_IOU_PRECISION: Final[int] = 16
"""
:meta private:
"""
MIN_MANTISSA: Final[int] = 10 ** 15
"""
:meta private:
"""
MAX_MANTISSA: Final[int] = 10 ** 16 - 1
"""
:meta private:
"""

# Configure Decimal
IOU_CONTEXT: Final[Context] = Context(
    prec=MAX_IOU_PRECISION, Emax=MAX_IOU_EXPONENT, Emin=MIN_IOU_EXPONENT
)
"""
Decimal context for working with IOUs.
:meta private:
"""


DROPS_CONTEXT: Final[Context] = Context(prec=18, Emin=0, Emax=18)
"""
Decimal context for working with drops.
:meta private:
"""
