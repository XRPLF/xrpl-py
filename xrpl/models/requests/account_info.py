"""
This request retrieves information about an account, its activity, and its XRP
balance.

All information retrieved is relative to a particular version of the ledger.

`See account_info <https://xrpl.org/account_info.html>`_
"""

from dataclasses import dataclass, field

from xrpl.models.requests.request import LookupByLedgerRequest, Request, RequestMethod
from xrpl.models.required import REQUIRED


@dataclass(frozen=True, kw_only=True)
class AccountInfo(Request, LookupByLedgerRequest):
    """
    This request retrieves information about an account, its activity, and its XRP
    balance.

    All information retrieved is relative to a particular version of the ledger.

    `See account_info <https://xrpl.org/account_info.html>`_
    """

    account: str = REQUIRED
    """
    This field is required.

    :meta hide-value:
    """

    method: RequestMethod = field(default=RequestMethod.ACCOUNT_INFO, init=False)
    queue: bool = False
    signer_lists: bool = False
    strict: bool = False
