"""Model for CheckCash transaction type."""

from dataclasses import dataclass, field
from typing import Any, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class CheckCash(Transaction):
    """
    Attempts to redeem a Check object in the ledger to receive up to the amount authorized
    by the corresponding CheckCreate transaction. Only the Destination address of a Check
    can cash it with a CheckCash transaction. Cashing a check this way is similar to
    executing a Payment initiated by the destination.  Since the funds for a check are not
    guaranteed, redeeming a Check can fail because the sender does not have a high enough
    balance or because there is not enough liquidity to deliver the funds. If this happens,
    the Check remains in the ledger and the destination can try to cash it again later, or
    for a different amount.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.CHECK_CASH, init=False
    )

    check_id: str = REQUIRED
    """
    The ID of the Check ledger object to cash, as a 64-character hexadecimal string.
    """

    amount: Optional[Any] = None
    """
    (Optional) Redeem the Check for exactly this amount, if possible. The currency must
    match that of the SendMax of the corresponding CheckCreate transaction. You must provide
    either this field or DeliverMin.
    """

    deliver_min: Optional[Any] = None
    """
    (Optional) Redeem the Check for at least this amount and for as much as possible. The
    currency must match that of the SendMax of the corresponding CheckCreate transaction.
    You must provide either this field or Amount.
    """

    def _get_errors(self: CheckCash) -> Dict[str, str]:
        errors = super._get_errors()
        if (self.amount is None) ^ (self.deliver_min is None):
            errors["CheckCash"] = (
                "Either `amount` and `deliver_min` must be set but not both."
            )
        return errors
