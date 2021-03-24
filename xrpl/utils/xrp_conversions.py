"""Conversions between XRP drops and native number types."""

from decimal import Context, Decimal, InvalidOperation, setcontext
from re import match
from typing import Union

from xrpl import XRPLException

ONE_DROP = Decimal("0.000001")  #: Indivisible unit of XRP
MAX_XRP = Decimal(10 ** 11)  #: 100 billion decimal XRP
MAX_DROPS = Decimal(10 ** 17)  #: Maximum possible number of drops of XRP

# Drops should be an integer string. MAY have (positive) exponent.
# See also: https://xrpl.org/currency-formats.html#string-numbers
_DROPS_REGEX = r"^\s*([1-9][0-9Ee-]{0,17}|0)\s*$"

_DROPS_CONTEXT = Context(prec=18, Emin=0, Emax=18)


def xrp_to_drops(xrp: Union[int, float, Decimal]) -> str:
    """
    Convert a numeric XRP amount to drops of XRP.

    Args:
        xrp: Numeric representation of whole XRP

    Returns:
        Equivalent amount in drops of XRP

    Raises:
        XRPTypeException: if ``xrp`` is given as a string
        XRPRangeException: if the given amount of XRP is invalid
    """
    if type(xrp) == str:  # type: ignore
        # This protects people from passing drops to this function and getting
        # a million times as many drops back.
        raise XRPTypeException(
            "XRP provided as a string. Use a number format"
            "like ``Decimal`` or ``int``."
        )
    setcontext(_DROPS_CONTEXT)
    try:
        xrp_d = Decimal(xrp)

        if xrp_d < ONE_DROP and xrp_d != 0:
            raise XRPRangeException(f"XRP amount {xrp} is too small.")
        if xrp_d > MAX_XRP:
            raise XRPRangeException(f"XRP amount {xrp} is too large.")
    except InvalidOperation:
        raise XRPRangeException(f"Not a valid amount of XRP: '{xrp}'")

    drops_amount = (xrp_d / ONE_DROP).quantize(Decimal(1))
    drops_str = str(drops_amount)

    # This should never happen, but is a precaution against Decimal doing
    # something unexpected.
    if not match(_DROPS_REGEX, drops_str):
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
        XRPRangeException: if the given number of drops is invalid
    """
    setcontext(_DROPS_CONTEXT)
    if not match(_DROPS_REGEX, drops):
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


class XRPTypeException(XRPLException):
    """Exception for string XRP amounts (use a Decimal for decimal XRP)."""

    pass
