"""This request gets information about an Automated Market Maker (AMM) instance."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.currencies import Currency
from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class AMMInfo(Request):
    """
    The `amm_info` method gets information about an Automated Market Maker
    (AMM) instance.
    """

    amm_account: Optional[str] = None
    """
    The address of the AMM pool to look up.
    """

    asset: Optional[Currency] = None
    """
    One of the assets of the AMM pool to look up.
    """

    asset2: Optional[Currency] = None
    """
    The other asset of the AMM pool.
    """

    method: RequestMethod = field(default=RequestMethod.AMM_INFO, init=False)

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()
        if (self.asset is None) != (self.asset2 is None):
            errors["assets"] = "Must have both `asset` and `asset2` fields."
        if (self.asset is None) == (self.amm_account is None):
            errors["params"] = "Must not have both `asset` and `amm_account` fields."
        return errors
