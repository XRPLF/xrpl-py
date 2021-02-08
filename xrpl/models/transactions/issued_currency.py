"""TODO: docstring"""
from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class IssuedCurrency:
    """TODO: docstring"""

    currency: str
    value: int
    issuer: str

    @classmethod
    def from_value(cls: IssuedCurrency, value: Dict[str, Any]) -> IssuedCurrency:
        """TODO: docstring"""
        assert isinstance(value["currency"], str)
        assert isinstance(value["value"], int)
        assert isinstance(value["issuer"], str)
        return IssuedCurrency(
            currency=value["currency"], value=value["value"], issuer=value["issuer"]
        )
