"""Model for EscrowCreate transaction type."""

from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class EscrowCreate(Transaction):
    """
    Sequester XRP until the escrow process either finishes or is canceled.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.ESCROW_CREATE, init=False
    )

    amount: str = REQUIRED
    """
    Amount of XRP, in drops, to deduct from the sender's balance and escrow. Once escrowed,
    the XRP can either go to the Destination address (after the FinishAfter time) or be
    returned to the sender (after the CancelAfter time).
    """

    destination: str = REQUIRED
    """
    Address to receive escrowed XRP.
    """

    cancel_after: Optional[int] = None
    """
    (Optional) The time, in seconds since the Ripple Epoch, when this escrow expires. This
    value is immutable; the funds can only be returned to the sender after this time.
    """

    finish_after: Optional[int] = None
    """
    (Optional) The time, in seconds since the Ripple Epoch, when the escrowed XRP can be
    released to the recipient. This value is immutable, and the funds can't be accessed
    until this time.
    """

    condition: Optional[str] = None
    """
    (Optional) Hex value representing a PREIMAGE-SHA-256 crypto-condition. The funds can
    only be delivered to the recipient if this condition is fulfilled. If the condition is
    not fulfilled before the expiration time specified in the CancelAfter field, the XRP can
    only revert to the sender.
    """

    destination_tag: Optional[int] = None
    """
    (Optional) Arbitrary tag to further specify the destination for this escrowed payment,
    such as a hosted recipient at the destination address.
    """

    def _get_errors(self: EscrowCreate) -> Dict[str, str]:
        errors = super._get_errors()
        if (
            self.finish_after is not None
            and self.cancel_after is not None
            and self.finish_after >= self.cancel_after
        ):
            errors["EscrowCreate"] = "finish_after must be less than cancel_after"
        return errors
