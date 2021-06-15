"""
This request retrieves from the ledger a list of transactions that involved the
specified account.

`See account_tx <https://xrpl.org/account_tx.html>`_
"""
from dataclasses import dataclass, field
from typing import Any, Optional, Union

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AccountTx(Request):
    """
    This request retrieves from the ledger a list of transactions that involved the
    specified account.

    `See account_tx <https://xrpl.org/account_tx.html>`_
    """

    account: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None
    method: RequestMethod = field(default=RequestMethod.ACCOUNT_TX, init=False)
    ledger_index_min: Optional[int] = None
    ledger_index_max: Optional[int] = None
    binary: bool = False
    forward: bool = False
    limit: Optional[int] = None
    # marker data shape is actually undefined in the spec, up to the
    # implementation of an individual server
    marker: Optional[Any] = None
