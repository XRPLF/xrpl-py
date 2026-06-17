"""
The transaction_entry method retrieves information on a single transaction from a
specific ledger version. (The tx method, by contrast, searches all ledgers for the
specified transaction. We recommend using that method instead.)

`See transaction_entry <https://xrpl.org/transaction_entry.html>`_
"""

from __future__ import annotations

from dataclasses import dataclass, field

from xrpl.models.requests.request import LookupByLedgerRequest, Request, RequestMethod
from xrpl.models.required import REQUIRED


@dataclass(frozen=True, kw_only=True)
class TransactionEntry(Request, LookupByLedgerRequest):
    """
    The transaction_entry method retrieves information on a single transaction from a
    specific ledger version. (The tx method, by contrast, searches all ledgers for the
    specified transaction. We recommend using that method instead.)

    `See transaction_entry <https://xrpl.org/transaction_entry.html>`_
    """

    method: RequestMethod = field(default=RequestMethod.TRANSACTION_ENTRY, init=False)
    tx_hash: str = REQUIRED
    """
    This field is required.

    :meta hide-value:
    """
