"""
Create a Check object in the ledger, which is a deferred payment
that can be cashed by its intended destination. The sender of this
transaction is the sender of the Check.

`See CheckCreate <https://xrpl.org/checkcreate.html>`_
"""
from dataclasses import dataclass
from typing import Optional

from xrpl.models.amount import Amount
from xrpl.models.transactions.transaction import REQUIRED, Transaction, TransactionType


@dataclass(frozen=True)
class CheckCreate(Transaction):
    """
    Create a Check object in the ledger, which is a deferred payment
    that can be cashed by its intended destination. The sender of this
    transaction is the sender of the Check.

    `See CheckCreate <https://xrpl.org/checkcreate.html>`_
    """

    destination: str = REQUIRED
    send_max: Amount = REQUIRED
    destination_tag: Optional[int] = None
    expiration: Optional[int] = None
    invoice_id: Optional[int] = None
    transaction_type: TransactionType = TransactionType.CheckCreate
