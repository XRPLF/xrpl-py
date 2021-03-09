"""
Specifies an amount in an issued currency.

See https://xrpl.org/currency-formats.html#issued-currency-amounts.
"""
from dataclasses import dataclass

from xrpl.models.currencies.issued_currency import IssuedCurrency
from xrpl.models.required import REQUIRED


@dataclass(frozen=True)
class IssuedCurrencyAmount(IssuedCurrency):
    """
    Specifies an amount in an issued currency.

    See https://xrpl.org/currency-formats.html#issued-currency-amounts.
    """

    value: str = REQUIRED
