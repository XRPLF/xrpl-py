"""TODO: docstring"""
from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass
from typing import Any, Dict

from xrpl.models.base_model import BaseModel


@dataclass(frozen=True)
class IssuedCurrency(BaseModel):
    """TODO: docstring"""

    currency: str
    value: int
    issuer: str

    @classmethod
    def from_dict(cls: IssuedCurrency, value: Dict[str, Any]) -> IssuedCurrency:
        """TODO: docstring"""
        assert isinstance(value["currency"], str)
        assert isinstance(value["value"], int)
        assert isinstance(value["issuer"], str)
        return IssuedCurrency(
            currency=value["currency"], value=value["value"], issuer=value["issuer"]
        )

    def to_json(self) -> Dict[str, Any]:
        """TODO: docstring"""
        return {"currency": self.currency, "value": self.value, "issuer": self.issuer}
