"""
An Amount is an object specifying a currency, a quantity
of that currency, and the counterparty (issuer) on the trustline
that holds the value. For XRP, there is no counterparty.
"""
from xrpl.models.amounts.amount import (
    Amount,
    get_amount_value,
    is_issued_currency,
    is_xrp,
)
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount

__all__ = [
    "Amount",
    "IssuedCurrencyAmount",
    "is_xrp",
    "is_issued_currency",
    "get_amount_value",
]
