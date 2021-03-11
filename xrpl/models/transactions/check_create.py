"""
Represents a CheckCreate transaction on the XRP ledger, which
creates a Check object. A Check object is a deferred payment
that can be cashed by its intended destination. The sender of this
transaction is the sender of the Check.

`See CheckCreate <https://xrpl.org/checkcreate.html>`_
"""
from dataclasses import dataclass
from typing import Optional

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class CheckCreate(Transaction):
    """
    Represents a CheckCreate transaction on the XRP ledger, which
    creates a Check object. A Check object is a deferred payment
    that can be cashed by its intended destination. The sender of this
    transaction is the sender of the Check.

    `See CheckCreate <https://xrpl.org/checkcreate.html>`_
    """

    destination: str = REQUIRED  # type: ignore
    send_max: Amount = REQUIRED  # type: ignore
    destination_tag: Optional[int] = None
    expiration: Optional[int] = None
    invoice_id: Optional[str] = None
    transaction_type: TransactionType = TransactionType.CHECK_CREATE
