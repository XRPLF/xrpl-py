"""This request gets information about an Automated Market Maker (AMM) instance."""
from __future__ import annotations

from dataclasses import dataclass, field

from xrpl.models.currencies import Currency
from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AMMInfo(Request):
    """
    The `amm_info` method gets information about an Automated Market Maker
    (AMM) instance.
    """

    asset: Currency = REQUIRED  # type: ignore
    """
    One of the assets of the AMM pool to look up. This field is required.
    """

    asset2: Currency = REQUIRED  # type: ignore
    """
    The other asset of the AMM pool. This field is required.
    """

    method: RequestMethod = field(default=RequestMethod.AMM_INFO, init=False)
