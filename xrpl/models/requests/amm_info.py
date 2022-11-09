"""This request retrieves information about an AMM instance."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from xrpl.models.currencies import Currency
from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AMMInfo(Request):
    """
    This request retrieves information about an AMM instance.

    Must provide either AMMID or both Asset and Asset2 params.
    """

    amm_id: Optional[str] = None
    """
    A hash that uniquely identifies the AMM instance.
    """

    asset: Optional[Currency] = None
    """
    Specifies one of the pool assets (XRP or token) of the AMM instance.
    """

    asset2: Optional[Currency] = None
    """
    Specifies the other pool asset of the AMM instance.
    """

    method: RequestMethod = field(default=RequestMethod.AMM_INFO, init=False)

    def _get_errors(self: AMMInfo) -> Dict[str, str]:
        errors = super()._get_errors()
        if self.amm_id is None:
            if self.asset is None and self.asset2 is None:
                errors[
                    "AMMInfo"
                ] = "Must set either `amm_id` or both `asset` and `asset2`"
            elif self.asset is None and self.asset2 is not None:
                errors[
                    "AMMInfo"
                ] = "Missing `asset`. Must set both `asset` and `asset2`"
            elif self.asset is not None and self.asset2 is None:
                errors[
                    "AMMInfo"
                ] = "Missing `asset2`. Must set both `asset` and `asset2`"
        return errors
