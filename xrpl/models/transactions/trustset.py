"""
Represents a TrustSet transaction on the XRP Ledger.
Creates or modifies a trust line linking two accounts.

`See TrustSet <https://xrpl.org/trustset.html>`_
"""
from dataclasses import dataclass
from typing import Optional

from xrpl.models.amount import Amount
from xrpl.models.transactions.transaction import REQUIRED, Transaction, TransactionType


@dataclass(frozen=True)
class TrustSet(Transaction):
    """
    Represents a TrustSet transaction on the XRP Ledger.
    Creates or modifies a trust line linking two accounts.

    `See TrustSet <https://xrpl.org/trustset.html>`_
    """

    limit_amount: Amount = REQUIRED
    quality_in: Optional[int] = None
    quality_out: Optional[int] = None
    transaction_type: TransactionType = TransactionType.TrustSet
