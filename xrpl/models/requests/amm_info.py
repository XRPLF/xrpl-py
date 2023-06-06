"""This request retrieves information about an AMM instance."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from xrpl.models.currencies import Currency
from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AMMInfo(Request):
    """
    This request retrieves information about an AMM instance.

    Must provide Asset and Asset2 params.
    """

    asset: Currency = REQUIRED  # type: ignore
    """
    Specifies one of the pool assets (XRP or token) of the AMM instance.
    """

    asset2: Currency = REQUIRED  # type: ignore
    """
    Specifies the other pool asset of the AMM instance.
    """

    method: RequestMethod = field(default=RequestMethod.AMM_INFO, init=False)

    def _get_errors(self: AMMInfo) -> Dict[str, str]:
        errors = super()._get_errors()
        return errors
