"""
An Amount is an object specifying a currency, a quantity of that currency, and the
counterparty (issuer) on the trustline that holds the value. For XRP, there is no
counterparty.
"""

from typing import Union

from typing_extensions import TypeGuard

from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.amounts.mpt_amount import MPTAmount

Amount = Union[IssuedCurrencyAmount, MPTAmount, str]


def is_xrp(amount: Amount) -> TypeGuard[str]:
    """
    Returns whether amount is an XRP value, as opposed to an issued currency
    or MPT value.

    Args:
        amount: The Amount object whose type is being checked.

    Returns:
        Whether the amount is an XRP value.
    """
    return isinstance(amount, str)


def is_issued_currency(amount: Amount) -> TypeGuard[IssuedCurrencyAmount]:
    """
    Returns whether amount is an issued currency value, as opposed to an XRP
    or MPT value.

    Args:
        amount: The Amount object whose type is being checked.

    Returns:
        Whether the amount is an issued currency value.
    """
    return isinstance(amount, IssuedCurrencyAmount)


def is_mpt(amount: Amount) -> TypeGuard[MPTAmount]:
    """
    Returns whether amount is an MPT value, as opposed to an XRP or
    an issued currency value.

    Args:
        amount: The Amount object whose type is being checked.

    Returns:
        Whether the amount is an issued currency value.
    """
    return isinstance(amount, MPTAmount)


def get_amount_value(amount: Amount) -> float:
    """
    Returns the value of an amount irrespective of its currency.

    Args:
        amount: The Amount object whose value we want.

    Returns:
        The value of the amount irrespective of its currency.
    """
    if is_xrp(amount):
        return float(amount)
    if is_issued_currency(amount):
        return float(amount.value)
    if is_mpt(amount):
        return float(amount.value)
    raise ValueError(f"Invalid amount: {repr(amount)}")
