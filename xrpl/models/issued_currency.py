"""
An issued currency on the XRP Ledger.

See https://xrpl.org/basic-data-types.html#specifying-currency-amounts.
See https://xrpl.org/currency-formats.html#issued-currency-amounts.
"""
from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass
from typing import Dict

from xrpl.models.base_model import BaseModel


@dataclass(frozen=True)
class IssuedCurrency(BaseModel):
    """
    An issued currency on the XRP Ledger.

    See https://xrpl.org/basic-data-types.html#specifying-currency-amounts.
    See https://xrpl.org/currency-formats.html#issued-currency-amounts.
    """

    currency: str
    value: int
    issuer: str

    def _get_errors(self: IssuedCurrency) -> Dict[str, str]:
        errors = {}
        if not isinstance(self.currency, str):
            errors["currency"] = "currency provided is not a str"
        if not isinstance(self.value, int):
            errors["value"] = "value provided is not an int"
        if not isinstance(self.issuer, str):
            errors["issuer"] = "issuer provided is not a str"
        return errors
