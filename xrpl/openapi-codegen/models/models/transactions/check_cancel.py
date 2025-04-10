"""Model for CheckCancel transaction type."""
from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class CheckCancel(Transaction):
    """
    Cancels an unredeemed Check, removing it from the ledger without sending any money. The
    source or the destination of the check can cancel a Check at any time using this
    transaction type. If the Check has expired, any address can cancel it.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.CHECK_CANCEL,
        init=False
    )

    check_id: str = REQUIRED
    """
    The ID of the Check ledger object to cancel, as a 64-character hexadecimal string.
    """


