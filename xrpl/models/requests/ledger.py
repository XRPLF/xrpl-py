"""
Retrieve information about the public ledger.
`See ledger <https://xrpl.org/ledger.html>`_
"""
from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.requests.ledger_entry import LedgerEntryType
from xrpl.models.requests.request import LookupByLedgerRequest, Request, RequestMethod
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Ledger(Request, LookupByLedgerRequest):
    """
    Retrieve information about the public ledger.
    `See ledger <https://xrpl.org/ledger.html>`_
    """

    method: RequestMethod = field(default=RequestMethod.LEDGER, init=False)
    full: bool = False
    accounts: bool = False
    transactions: bool = False
    expand: bool = False
    owner_funds: bool = False
    binary: bool = False
    queue: bool = False
    type: Optional[LedgerEntryType] = None
