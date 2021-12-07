"""
Specifies an amount in an issued currency.

See https://xrpl.org/currency-formats.html#issued-currency-amounts.
"""
from __future__ import annotations

from dataclasses import dataclass

from xrpl.models.currencies.issued_currency import IssuedCurrency
from xrpl.models.currencies.issued_currency_base import IssuedCurrencyBase
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class IssuedCurrencyAmount(IssuedCurrencyBase):
    """
    Specifies an amount in an issued currency.

    See https://xrpl.org/currency-formats.html#issued-currency-amounts.
    """

    value: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    def to_currency(self: IssuedCurrencyAmount) -> IssuedCurrency:
        """
        Build an IssuedCurrency from this IssuedCurrencyAmount.

        Returns:
            The IssuedCurrency for this IssuedCurrencyAmount.
        """
        return IssuedCurrency(issuer=self.issuer, currency=self.currency)
