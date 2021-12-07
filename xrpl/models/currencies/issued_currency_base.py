"""
A base interface for IssuedCurrency and
IssuedCurrencyAmount.

:meta private:
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

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
        return {
            key: value
            for key, value in {
                **super()._get_errors(),
                "currency": self._get_currency_error(),
            }.items()
            if value is not None
        }

    def _get_currency_error(self: IssuedCurrencyBase) -> Optional[str]:
        if self.currency.upper() == "XRP":
            return "Currency must not be XRP for issued currency"
        if not _is_valid_currency(self.currency):
            return f"Invalid currency {self.currency}"
        return None
