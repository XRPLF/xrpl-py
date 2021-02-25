"""
An Amount is an object specifying a currency, a quantity
of that currency, and the counterparty (issuer) on the trustline
that holds the value. For XRP, there is no counterparty.
"""
from xrpl.models.amount.amount import Amount, is_issued_currency, is_xrp
from xrpl.models.amount.issued_currency import IssuedCurrency

__all__ = ["Amount", "IssuedCurrency", "is_xrp", "is_issued_currency"]
