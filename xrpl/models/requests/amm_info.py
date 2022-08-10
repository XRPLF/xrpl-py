"""This request retrieves information about an AMM instance."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from xrpl.models.amounts import Amount
from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AMMInfo(Request):
    """This request retrieves information about an AMM instance."""

    method: RequestMethod = field(default=RequestMethod.AMM_INFO, init=False)
    AMMHash: Optional[str] = None
    Asset1: Optional[Amount] = None
    Asset2: Optional[Amount] = None

    def _get_errors(self: AMMInfo) -> Dict[str, str]:
        errors = super()._get_errors()
        if self.AMMHash is None:
            if self.Asset1 is None and self.Asset2 is None:
                errors[
                    "AMMInfo"
                ] = "Must set either `AMMHash` or both `Asset1` and `Asset2`"
            elif self.Asset1 is None and self.Asset2 is not None:
                errors[
                    "AMMInfo"
                ] = "Missing `Asset1`. Must set both `Asset1` and `Asset2`"
            elif self.Asset1 is not None and self.Asset2 is None:
                errors[
                    "AMMInfo"
                ] = "Missing `Asset2`. Must set both `Asset1` and `Asset2`"
        return errors
