"""
Represents an EscrowCreate transaction on the XRP Ledger.

An EscrowCreate transaction sequesters XRP until the escrow process either finishes or
is canceled.

`See EscrowCreate <https://xrpl.org/escrowcreate.html>`_
"""
from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass
from typing import Dict, Optional

from xrpl.models.amounts import Amount
from xrpl.models.transactions.transaction import REQUIRED, Transaction, TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class EscrowCreate(Transaction):
    """
    Represents an EscrowCreate transaction on the XRP Ledger.

    An EscrowCreate transaction sequesters XRP until the escrow process either finishes
    or is canceled.

    `See EscrowCreate <https://xrpl.org/escrowcreate.html>`_
    """

    amount: Amount = REQUIRED
    destination: str = REQUIRED
    destination_tag: Optional[int] = None
    cancel_after: Optional[int] = None
    finish_after: Optional[int] = None
    condition: Optional[str] = None
    transaction_type: TransactionType = TransactionType.ESCROW_CREATE

    def _get_errors(self: EscrowCreate) -> Dict[str, str]:
        errors = super()._get_errors()
        if (
            self.cancel_after is not None
            and self.finish_after is not None
            and self.finish_after >= self.cancel_after
        ):
            errors[
                "EscrowCreate"
            ] = "The finish_after time must be before the cancel_after time."

        return errors
