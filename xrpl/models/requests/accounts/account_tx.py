"""
This request retrieves from the ledger a list of transactions that involved the
specified account.

`See account_tx <https://xrpl.org/account_tx.html>`_
"""
from dataclasses import dataclass
from typing import Any, Optional, Union

from xrpl.models.base_model import REQUIRED
from xrpl.models.requests.request import Request, RequestMethod


@dataclass(frozen=True)
class AccountTx(Request):
    """
    This request retrieves from the ledger a list of transactions that involved the
    specified account.

    `See account_tx <https://xrpl.org/account_tx.html>`_
    """

    account: str = REQUIRED
    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None
    method: RequestMethod = RequestMethod.ACCOUNT_TX
    ledger_index_min: Optional[int] = None
    ledger_index_max: Optional[int] = None
    binary: Optional[bool] = False
    forward: bool = False
    limit: Optional[int] = None
    marker: Optional[Any] = None
