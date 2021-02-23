"""
Represents an AccountDelete transaction on the XRP Ledger.

An AccountDelete transaction deletes an account and any objects it owns in the XRP
Ledger, if possible, sending the account's remaining XRP to a specified destination
account. See Deletion of Accounts for the requirements to delete an account.

`See AccountDelete <https://xrpl.org/accountdelete.html>`_
`See Deletion of Accounts <https://xrpl.org/accounts.html#deletion-of-accounts>`_
"""
from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass
from typing import Dict, Optional

from xrpl.models.transactions.transaction import REQUIRED, Transaction, TransactionType


@dataclass(frozen=True)
class EscrowCreate(Transaction):
    """
    Represents an AccountDelete transaction on the XRP Ledger.

    An AccountDelete transaction deletes an account and any objects it owns in the XRP
    Ledger, if possible, sending the account's remaining XRP to a specified destination
    account. See Deletion of Accounts for the requirements to delete an account.

    `See AccountDelete <https://xrpl.org/accountdelete.html>`_
    `See Deletion of Accounts <https://xrpl.org/accounts.html#deletion-of-accounts>`_
    """

    amount: int = REQUIRED
    destination: str = REQUIRED
    destination_tag: Optional[int] = None
    cancel_after: Optional[int] = None
    finish_after: Optional[int] = None
    condition: Optional[str] = None
    transaction_type: str = TransactionType.EscrowCreate

    def _get_errors(self: EscrowCreate) -> Dict[str, str]:
        errors = {}
        if (
            self.cancel_after is not None
            and self.finish_after is not None
            and self.finish_after < self.cancel_after
        ):
            errors[
                "escrow_create"
            ] = "The finish_after time must be before the cancel_after time."

        return errors
