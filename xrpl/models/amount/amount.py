"""
An Amount is an object specifying a currency, a quantity
of that currency, and the counterparty (issuer) on the trustline
that holds the value. For XRP, there is no counterparty.
"""
from typing import NewType, Union

from xrpl.models.amount.issued_currency import IssuedCurrency

Amount = NewType("Amount", Union[str, IssuedCurrency])


def is_xrp(amount: Amount) -> bool:
    """
    Returns whether amount is an XRP value, as opposed to an issued currency.

    Returns:
        Whether the amount is an XRP value.
    """
    return isinstance(amount, str)


def is_issued_currency(amount: Amount) -> bool:
    """
    Returns whether amount is an issued currency value, as opposed to an XRP value.

    Returns:
        Whether the amount is an issued currency value.
    """
    return isinstance(amount, IssuedCurrency)
