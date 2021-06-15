"""
The transaction_entry method retrieves information on a single transaction from a
specific ledger version. (The tx method, by contrast, searches all ledgers for the
specified transaction. We recommend using that method instead.)

`See transaction_entry <https://xrpl.org/transaction_entry.html>`_
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Union

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class TransactionEntry(Request):
    """
    The transaction_entry method retrieves information on a single transaction from a
    specific ledger version. (The tx method, by contrast, searches all ledgers for the
    specified transaction. We recommend using that method instead.)

    `See transaction_entry <https://xrpl.org/transaction_entry.html>`_
    """

    method: RequestMethod = field(default=RequestMethod.TRANSACTION_ENTRY, init=False)
    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None
    tx_hash: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """
