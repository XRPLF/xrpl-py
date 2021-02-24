"""
Represents a DepositPreauth transaction on the XRP Ledger.

A DepositPreauth transaction gives another account pre-approval to deliver payments
to the sender of this transaction.

`See Deposit Authorization <https://xrpl.org/depositauth.html>`_
`See DepositPreauth <https://xrpl.org/depositauth.html>`_
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from xrpl.models.transactions.transaction import Transaction


@dataclass(frozen=True)
class DepositPreauth(Transaction):
    """
    Represents a DepositPreauth transaction on the XRP Ledger.

    A DepositPreauth transaction gives another account pre-approval to deliver payments
    to the sender of this transaction.

    `See Deposit Authorization <https://xrpl.org/depositauth.html>`_
    `See DepositPreauth <https://xrpl.org/depositauth.html>`_
    """

    authorize: Optional[str] = None
    deauthorize: Optional[str] = None

    def _get_errors(self: DepositPreauth) -> Dict[str, str]:
        errors = {}
        if self.authorize and self.deauthorize:
            errors[
                "DepositPreauth"
            ] = "One of authorize and deauthorize must be set, not both."

        if not self.authorize and not self.deauthorize:
            errors["DepositPreauth"] = "One of authorize and deauthorize must be set."

        return errors
