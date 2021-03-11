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

from dataclasses import dataclass
from typing import Dict

from xrpl.models.base_model import BaseModel
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

    currency: str = "XRP"

    def _get_errors(self: XRP) -> Dict[str, str]:
        errors = super()._get_errors()
        if self.currency.upper() != "XRP":
            errors["currency"] = "Currency must be XRP for XRP currency"
        return errors
