"""
Specifies XRP as a currency, without a value. Normally, you will not use this
model as it does not specify an amount of XRP. In cases where you need to
specify an amount of XRP, you will use a string. However, for some book order
requests where currencies are specified without amounts, you may need to
specify the use of XRP, without a value. In these cases, you will use this
object.

See https://xrpl.org/currency-formats.html#specifying-currency-amounts
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Type, Union

from xrpl.models.base_model import BaseModel
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class XRP(BaseModel):
    """
    Specifies XRP as a currency, without a value. Normally, you will not use this
    model as it does not specify an amount of XRP. In cases where you need to
    specify an amount of XRP, you will use a string. However, for some book order
    requests where currencies are specified without amounts, you may need to
    specify the use of XRP, without a value. In these cases, you will use this
    object.

    See https://xrpl.org/currency-formats.html#specifying-currency-amounts
    """

    currency: str = field(default="XRP", init=False)

    @classmethod
    def from_dict(cls: Type[XRP], value: Dict[str, Any]) -> XRP:
        """
        Construct a new XRP from a dictionary of parameters.

        Args:
            value: The value to construct the XRP from.

        Returns:
            A new XRP object, constructed using the given parameters.

        Raises:
            XRPLModelException: If the dictionary provided is invalid.
        """
        if len(value) != 1 or "currency" not in value or value["currency"] != "XRP":
            raise XRPLModelException("Not a valid XRP type")
        return XRP()

    def to_dict(self: XRP) -> Dict[str, Any]:
        """
        Returns the dictionary representation of an XRP currency object.

        Returns:
            The dictionary representation of an XRP currency object.
        """
        return {**super().to_dict(), "currency": "XRP"}

    def to_amount(self: XRP, value: Union[str, int]) -> str:
        """
        Converts value to XRP.

        Args:
            value: The amount of XRP.

        Returns:
            A string representation of XRP amount.
        """
        return str(value)
