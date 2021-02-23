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

from xrpl.models.transactions.transaction import REQUIRED, Transaction


@dataclass(frozen=True)
class EscrowCancel(Transaction):
    """
    Represents an AccountDelete transaction on the XRP Ledger.

    An AccountDelete transaction deletes an account and any objects it owns in the XRP
    Ledger, if possible, sending the account's remaining XRP to a specified destination
    account. See Deletion of Accounts for the requirements to delete an account.

    `See AccountDelete <https://xrpl.org/accountdelete.html>`_
    `See Deletion of Accounts <https://xrpl.org/accounts.html#deletion-of-accounts>`_
    """

    owner: str = REQUIRED
    offer_sequence: int = REQUIRED
