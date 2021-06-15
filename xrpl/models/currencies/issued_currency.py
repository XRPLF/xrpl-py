"""
Specifies an amount in an issued currency, but without a value field.
This format is used for some book order requests.

See https://xrpl.org/currency-formats.html#specifying-currency-amounts
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict

from typing_extensions import Final

from xrpl.models.base_model import BaseModel
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init

_CHAR: Final[str] = r"[A-Za-z\d\?!@#\$%\^&\*<>\(\){}\[\]\|]"
_CURRENCY_CODE: Final[str] = f"{_CHAR}{{3}}"
_HEX: Final[str] = f"{_CHAR}{{40}}"
_VALIDATOR: Final[re.Pattern[str]] = re.compile(
    f"(?:{_CURRENCY_CODE}|{_HEX})",
)


@require_kwargs_on_init
@dataclass(frozen=True)
class IssuedCurrency(BaseModel):
    """
    Specifies an amount in an issued currency, but without a value field.
    This format is used for some book order requests.

    See https://xrpl.org/currency-formats.html#specifying-currency-amounts
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

    def _get_errors(self: IssuedCurrency) -> Dict[str, str]:
        errors = super()._get_errors()
        if self.currency.upper() == "XRP":
            errors["currency"] = "Currency must not be XRP for issued currency"
        elif not _VALIDATOR.fullmatch(self.currency):
            errors["currency"] = f"Invalid currency {self.currency}"
        return errors
