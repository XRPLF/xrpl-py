"""
An Amount is an object specifying a currency, a quantity
of that currency, and the counterparty (issuer) on the trustline
that holds the value. For XRP, there is no counterparty.
"""
from typing import NewType, Union

from xrpl.models.amount.issued_currency import IssuedCurrency

Amount = NewType("Amount", Union[str, IssuedCurrency])
