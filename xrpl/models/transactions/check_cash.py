"""
Attempts to redeem a Check object in the ledger to receive up to the amount
authorized by the corresponding CheckCreate transaction. Only the Destination
address of a Check can cash it with a CheckCash transaction. Cashing a check
this way is similar to executing a Payment initiated by the destination.

Since the funds for a check are not guaranteed, redeeming a Check can fail
because the sender does not have a high enough balance or because there is
not enough liquidity to deliver the funds. If this happens, the Check remains
in the ledger and the destination can try to cash it again later, or for a
different amount.

`See CheckCash <https://xrpl.org/checkcash.html>`_
"""
from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass
from typing import Dict, Optional

from xrpl.models.amount import Amount
from xrpl.models.transactions.transaction import REQUIRED, Transaction, TransactionType


@dataclass(frozen=True)
class CheckCash(Transaction):
    """
    Attempts to redeem a Check object in the ledger to receive up to the amount
    authorized by the corresponding CheckCreate transaction. Only the Destination
    address of a Check can cash it with a CheckCash transaction. Cashing a check
    this way is similar to executing a Payment initiated by the destination.

    Since the funds for a check are not guaranteed, redeeming a Check can fail
    because the sender does not have a high enough balance or because there is
    not enough liquidity to deliver the funds. If this happens, the Check remains
    in the ledger and the destination can try to cash it again later, or for a
    different amount.

    `See CheckCash <https://xrpl.org/checkcash.html>`_
    """

    check_id: str = REQUIRED
    amount: Optional[Amount] = None
    deliver_min: Optional[Amount] = None
    transaction_type: TransactionType = TransactionType.CheckCash

    def _get_errors(self: CheckCash) -> Dict[str, str]:
        errors = super()._get_errors()
        if not bool(self.amount is None) ^ bool(self.deliver_min is None):
            errors["amount"] = "amount or deliver_min must be set but not both"
            errors["deliver_min"] = "amount or deliver_min must be set but not both"
        return errors
