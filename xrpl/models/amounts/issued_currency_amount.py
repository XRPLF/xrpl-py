"""
Specifies an amount in an issued currency.

See https://xrpl.org/currency-formats.html#issued-currency-amounts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Type, Union, cast

from xrpl.models.currencies import XRP, Currency, IssuedCurrency
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class IssuedCurrencyAmount(IssuedCurrency):
    """
    Specifies an amount in an issued currency.

    See https://xrpl.org/currency-formats.html#issued-currency-amounts.
    """

    value: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    @classmethod
    def from_issued_currency(
        cls: Type[IssuedCurrencyAmount], issued_currency: Currency, value: str
    ) -> Union[IssuedCurrencyAmount, str]:
        """
        Build an IssuedCurrencyAmount from an IssuedCurrency.

        Args:
            issued_currency: The issued currency to use.
            value: The amount of issued currency.

        Returns:
            An IssuedCurrencyAmount with the provided value in the provided issued
            currency.
        """
        if isinstance(issued_currency, XRP):
            return value
        return cast(
            IssuedCurrencyAmount,
            cls.from_dict({**issued_currency.to_dict(), "value": value}),
        )

    def get_issued_currency(self: IssuedCurrencyAmount) -> IssuedCurrency:
        """
        Build an IssuedCurrency from this IssuedCurrencyAmount.

        Returns:
            The IssuedCurrency for this IssuedCurrencyAmount.
        """
        return IssuedCurrency(issuer=self.issuer, currency=self.currency)
