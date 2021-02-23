"""
Represents a TrustSet transaction on the XRP Ledger.
Creates or modifies a trust line linking two accounts.

`See TrustSet <https://xrpl.org/trustset.html>`_
"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

from xrpl.models.amount import Amount
from xrpl.models.transactions.transaction import REQUIRED, Transaction, TransactionType


class TrustSetFlag(int, Enum):
    """
    Transactions of the TrustSet type support additional values in the Flags field.
    This enum represents those options.
    """

    TF_SET_AUTH = 0x00010000
    TF_SET_NO_RIPPLE = 0x00020000
    TF_CLEAR_NO_RIPPLE = 0x00040000
    TF_SET_FREEZE = 0x00100000
    TF_CLEAR_FREEZE = 0x00200000


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

    def _get_errors(self: Transaction) -> Dict[str, str]:
        # errors = super()._get_errors()
        pass
