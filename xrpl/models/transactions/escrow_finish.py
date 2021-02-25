"""
Represents an EscrowFinish transaction on the XRP Ledger.

An EscrowFinish transaction delivers XRP from a held payment to the recipient.

`See EscrowFinish <https://xrpl.org/escrowfinish.html>`_
"""
from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass
from typing import Dict, Optional

from xrpl.models.transactions.transaction import REQUIRED, Transaction, TransactionType


@dataclass(frozen=True)
class EscrowFinish(Transaction):
    """
    Represents an EscrowFinish transaction on the XRP Ledger.

    An EscrowFinish transaction delivers XRP from a held payment to the recipient.

    `See EscrowFinish <https://xrpl.org/escrowfinish.html>`_
    """

    owner: str = REQUIRED
    offer_sequence: int = REQUIRED
    condition: Optional[str] = None
    fulfillment: Optional[str] = None
    transaction_type: TransactionType = TransactionType.EscrowFinish

    def _get_errors(self: EscrowFinish) -> Dict[str, str]:
        errors = super()._get_errors()
        if self.condition and not self.fulfillment:
            errors[
                "fulfillment"
            ] = "If condition is specified, fulfillment must also be specified."
        if self.fulfillment and not self.condition:
            errors[
                "condition"
            ] = "If fulfillment is specified, condition must also be specified."

        return errors
