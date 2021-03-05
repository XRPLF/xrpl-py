"""
The XRP Ledger has two kinds of money: XRP, and issued
currencies. Both types have high precision, although their
formats are different.
"""
from typing import NewType, Union

from xrpl.models.currencies.issued_currency import IssuedCurrency
from xrpl.models.currencies.xrp import XRP

Currency = NewType("Currency", Union[XRP, IssuedCurrency])
