"""
An issued currency on the XRP Ledger.

See https://xrpl.org/basic-data-types.html#specifying-currency-amounts.
See https://xrpl.org/currency-formats.html#issued-currency-amounts.
"""
from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass
from typing import Any, Dict

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

    @classmethod
    def from_dict(cls: IssuedCurrency, value: Dict[str, Any]) -> IssuedCurrency:
        """
        Construct an IssuedCurrency from a dictionary of parameters.

        Args:
            value: The dictionary to construct an IssuedCurrency from.

        Returns:
            The IssuedCurrency constructed from value.
        """
        assert isinstance(value["currency"], str)
        assert isinstance(value["value"], int)
        assert isinstance(value["issuer"], str)
        return cls(**value)
