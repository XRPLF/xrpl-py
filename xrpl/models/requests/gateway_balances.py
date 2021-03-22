"""
This request calculates the total balances issued by a given account, optionally
excluding amounts held by operational addresses.

`See gateway_balances <https://xrpl.org/gateway_balances.html>`_
"""
from dataclasses import dataclass, field
from typing import List, Optional, Union

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class GatewayBalances(Request):
    """
    This request calculates the total balances issued by a given account, optionally
    excluding amounts held by operational addresses.

    `See gateway_balances <https://xrpl.org/gateway_balances.html>`_
    """

    #: This field is required.
    account: str = REQUIRED  # type: ignore
    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None
    method: RequestMethod = field(default=RequestMethod.GATEWAY_BALANCES, init=False)
    strict: bool = False
    hotwallet: Optional[Union[str, List[str]]] = None
