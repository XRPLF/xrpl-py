"""
Represents an EscrowCancel transaction on the XRP Ledger.

An EscrowCancel transaction returns escrowed XRP to the sender.

`See EscrowCancel <https://xrpl.org/escrowcancel.html>`_
"""

from dataclasses import dataclass, field

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class EscrowCancel(Transaction):
    """
    Represents an EscrowCancel transaction on the XRP Ledger.

    An EscrowCancel transaction returns escrowed XRP to the sender.

    `See EscrowCancel <https://xrpl.org/escrowcancel.html>`_
    """

    owner: str = REQUIRED  # type: ignore
    offer_sequence: int = REQUIRED  # type: ignore
    transaction_type: TransactionType = field(
        default=TransactionType.ESCROW_CANCEL,
        init=False,
    )
