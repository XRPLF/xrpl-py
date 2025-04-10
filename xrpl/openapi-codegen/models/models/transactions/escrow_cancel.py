"""Model for EscrowCancel transaction type."""
from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class EscrowCancel(Transaction):
    """
    Return escrowed XRP to the sender.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.ESCROW_CANCEL,
        init=False
    )

    owner: str = REQUIRED
    """
    Address of the source account that funded the escrow payment.
    """

    offer_sequence: int = REQUIRED
    """
    Transaction sequence (or Ticket number) of EscrowCreate transaction that created the
    escrow to cancel.
    """


