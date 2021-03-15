"""
Retrieve information about the public ledger.
`See ledger <https://xrpl.org/ledger.html>`_
"""
from dataclasses import dataclass, field
from typing import Optional, Union

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Ledger(Request):
    """
    Retrieve information about the public ledger.
    `See ledger <https://xrpl.org/ledger.html>`_
    """

    method: RequestMethod = field(default=RequestMethod.LEDGER, init=False)
    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None
    full: bool = False
    accounts: bool = False
    transactions: bool = False
    expand: bool = False
    owner_funds: bool = False
    binary: bool = False
    queue: bool = False
