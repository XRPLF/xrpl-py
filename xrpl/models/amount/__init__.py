"""
An Amount is an object specifying a currency, a quantity
of that currency, and the counterparty (issuer) on the trustline
that holds the value. For XRP, there is no counterparty.
"""
from xrpl.models.amount.amount import Amount
from xrpl.models.amount.issued_currency_amount import IssuedCurrencyAmount

__all__ = [
    "Amount",
    "IssuedCurrencyAmount",
]
