"""
Specifies an amount in an issued currency, but without a value field.
This format is used for some book order requests.

See https://xrpl.org/currency-formats.html#specifying-currency-amounts
"""
from __future__ import annotations

from dataclasses import dataclass

# not using `from import` to work around a circular dependency
import xrpl.models.amounts
from xrpl.models.currencies.issued_currency_base import IssuedCurrencyBase
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class IssuedCurrency(IssuedCurrencyBase):
    """
    Specifies an amount in an issued currency, but without a value field.
    This format is used for some book order requests.

    See https://xrpl.org/currency-formats.html#specifying-currency-amounts
    """

    def to_amount(
        self: IssuedCurrency, value: str
    ) -> xrpl.models.amounts.IssuedCurrencyAmount:
        """
        Build an IssuedCurrencyAmount from this IssuedCurrency.

        Args:
            value: the amount for the resulting IssuedCurrencyAmount.

        Returns:
            The IssuedCurrencyAmount for this IssuedCurrency.
        """
        return xrpl.models.amounts.IssuedCurrencyAmount(
            currency=self.currency,
            issuer=self.issuer,
            value=value,
        )
