"""
Cancels an unredeemed Check, removing it from the ledger without sending any money.
The source or the destination of the check can cancel a Check at any time using this
transaction type. If the Check has expired, any address can cancel it.

`See CheckCancel <https://xrpl.org/checkcancel.html>`_
"""
from dataclasses import dataclass

from xrpl.models.transactions.transaction import REQUIRED, Transaction, TransactionType


@dataclass(frozen=True)
class CheckCancel(Transaction):
    """
    Cancels an unredeemed Check, removing it from the ledger without sending any money.
    The source or the destination of the check can cancel a Check at any time using this
    transaction type. If the Check has expired, any address can cancel it.

    `See CheckCancel <https://xrpl.org/checkcancel.html>`_
    """

    check_id: str = REQUIRED
    transaction_type: TransactionType = TransactionType.CheckCancel
