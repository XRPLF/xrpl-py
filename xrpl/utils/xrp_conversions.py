"""Conversions between XRP drops and native number types."""

import re
from decimal import Decimal, InvalidOperation, localcontext
from typing import Pattern, Union

from typing_extensions import Final

from xrpl.constants import DROPS_DECIMAL_CONTEXT, XRPLException

ONE_DROP: Final[Decimal] = Decimal("0.000001")
"""Indivisible unit of XRP"""

MAX_XRP: Final[Decimal] = Decimal(10**11)
"""100 billion decimal XRP"""

MAX_DROPS: Final[Decimal] = Decimal(10**17)
"""Maximum possible drops of XRP"""

# Drops should be an integer string. MAY have (positive) exponent.
# See also: https://xrpl.org/currency-formats.html#string-numbers
_DROPS_REGEX: Final[Pattern[str]] = re.compile("(?:[1-9][0-9Ee-]{0,17}|0)")


def xrp_to_drops(xrp: Union[int, float, Decimal]) -> str:
    """
    Convert a numeric XRP amount to drops of XRP.

    Args:
        xrp: Numeric representation of whole XRP

    Returns:
        Equivalent amount in drops of XRP

    Raises:
        TypeError: if ``xrp`` is given as a string
        XRPRangeException: if the given amount of XRP is invalid, including
            when it has more than 6 decimal places (i.e. a fraction of a drop)
    """
    if isinstance(xrp, str):
        # This protects people from passing drops to this function and getting
        # a million times as many drops back.
        raise TypeError(
            "XRP provided as a string. Use a number format like Decimal or int."
        )
    with localcontext(DROPS_DECIMAL_CONTEXT):
        try:
            if isinstance(xrp, float):
                # Use the shortest round-trip string, as xrpl.js does: the
                # exact binary expansion of a float (e.g. 0.1) has far more
                # than 6 decimal places, but its repr is what the caller meant.
                xrp_d = Decimal(str(xrp))
            else:
                xrp_d = Decimal(xrp)
        except InvalidOperation:
            raise XRPRangeException(f"Not a valid amount of XRP: '{xrp}'")

        if not xrp_d.is_finite():  # NaN or an Infinity
            raise XRPRangeException(f"Not a valid amount of XRP: '{xrp}'")

        if xrp_d < ONE_DROP and xrp_d != 0:
            raise XRPRangeException(f"XRP amount {xrp} is too small.")
        if xrp_d > MAX_XRP:
            raise XRPRangeException(f"XRP amount {xrp} is too large.")

        # A drop is indivisible: silently rounding an amount with more than
        # 6 decimal places could convert to more drops than the caller gave
        # (round-half-even rounds up), so reject it instead, as xrpl.js does.
        try:
            is_whole_drops = xrp_d == xrp_d.quantize(ONE_DROP)
        except InvalidOperation:
            is_whole_drops = False
        if not is_whole_drops:
            raise XRPRangeException(f"XRP amount {xrp} has too many decimal places.")

        drops_amount = (xrp_d / ONE_DROP).quantize(Decimal(1))
        drops_str = str(drops_amount).strip()

        # This should never happen, but is a precaution against Decimal doing
        # something unexpected.
        if not _DROPS_REGEX.fullmatch(drops_str):
            raise XRPRangeException(
                f"xrp_to_drops failed sanity check. Value "
                f"'{drops_str}' does not match the drops regex"
            )

    return drops_str


def drops_to_xrp(drops: str) -> Decimal:
    """
    Convert from drops to decimal XRP.

    Args:
        drops: String representing indivisible drops of XRP

    Returns:
        Decimal representation of the same amount of XRP

    Raises:
        TypeError: if ``drops`` not given as a string
        XRPRangeException: if the given number of drops is invalid
    """
    if not isinstance(drops, str):
        raise TypeError(f"Drops must be provided as string (got {type(drops)})")
    drops = drops.strip()
    with localcontext(DROPS_DECIMAL_CONTEXT):
        if not _DROPS_REGEX.fullmatch(drops):
            raise XRPRangeException(f"Not a valid amount of drops: '{drops}'")
        try:
            drops_d = Decimal(drops)
        except InvalidOperation:
            raise XRPRangeException(f"Not a valid amount of drops: '{drops}'")
        xrp_d = drops_d * ONE_DROP
        if xrp_d > MAX_XRP:
            raise XRPRangeException(f"Drops amount {drops} is too large.")
        return xrp_d


class XRPRangeException(XRPLException):
    """Exception for invalid XRP amounts."""

    pass
