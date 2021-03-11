"""
This request calculates the total balances issued by a given account, optionally
excluding amounts held by operational addresses.

`See gateway_balances <https://xrpl.org/gateway_balances.html>`_
"""
from dataclasses import dataclass
from typing import List, Optional, Union

from xrpl.models.base_model import REQUIRED
from xrpl.models.requests.request import Request, RequestMethod


@dataclass(frozen=True)
class GatewayBalances(Request):
    """
    This request calculates the total balances issued by a given account, optionally
    excluding amounts held by operational addresses.

    `See gateway_balances <https://xrpl.org/gateway_balances.html>`_
    """

    account: str = REQUIRED  # type: ignore
    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None
    method: RequestMethod = RequestMethod.GATEWAY_BALANCES
    strict: Optional[bool] = False
    hotwallet: Optional[Union[str, List[str]]] = None
