"""
A base interface for IssuedCurrency and
IssuedCurrencyAmount.

:meta private:
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from xrpl.constants import HEX_CURRENCY_REGEX, ISO_CURRENCY_REGEX
from xrpl.models.base_model import BaseModel
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


def _is_valid_currency(candidate: str) -> bool:
    return bool(
        ISO_CURRENCY_REGEX.fullmatch(candidate)
        or HEX_CURRENCY_REGEX.fullmatch(candidate)
    )


@require_kwargs_on_init
@dataclass(frozen=True)
class IssuedCurrencyBase(BaseModel):
    """
    A base interface for IssuedCurrency and
    IssuedCurrencyAmount.

    :meta private:
    """

    currency: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    issuer: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    def _get_errors(self: IssuedCurrencyBase) -> Dict[str, str]:
        errors = super()._get_errors()
        if self.currency.upper() == "XRP":
            errors["currency"] = "Currency must not be XRP for issued currency"
        elif not _is_valid_currency(self.currency):
            errors["currency"] = f"Invalid currency {self.currency}"
        return errors
