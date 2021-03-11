"""
Represents an EscrowCancel transaction on the XRP Ledger.

An EscrowCancel transaction returns escrowed XRP to the sender.

`See EscrowCancel <https://xrpl.org/escrowcancel.html>`_
"""

from dataclasses import dataclass

from xrpl.models.base_model import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionType


@dataclass(frozen=True)
class EscrowCancel(Transaction):
    """
    Represents an EscrowCancel transaction on the XRP Ledger.

    An EscrowCancel transaction returns escrowed XRP to the sender.

    `See EscrowCancel <https://xrpl.org/escrowcancel.html>`_
    """

    owner: str = REQUIRED  # type: ignore
    offer_sequence: int = REQUIRED  # type: ignore
    transaction_type: TransactionType = TransactionType.ESCROW_CANCEL
