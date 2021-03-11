"""
This request retrieves information about an account, its activity, and its XRP
balance.

All information retrieved is relative to a particular version of the ledger.

`See account_info <https://xrpl.org/account_info.html>`_
"""
from dataclasses import dataclass, field
from typing import Optional, Union

from xrpl.models.base_model import REQUIRED
from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AccountInfo(Request):
    """
    This request retrieves information about an account, its activity, and its XRP
    balance.

    All information retrieved is relative to a particular version of the ledger.

    `See account_info <https://xrpl.org/account_info.html>`_
    """

    account: str = REQUIRED
    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None
    method: RequestMethod = field(default=RequestMethod.ACCOUNT_INFO, init=False)
    queue: Optional[bool] = None
    signer_lists: Optional[bool] = None
    strict: Optional[bool] = False
