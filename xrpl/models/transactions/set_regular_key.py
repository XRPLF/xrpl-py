"""
Represents a SetRegularKey transaction on the XRP Ledger.

A SetRegularKey transaction assigns, changes, or removes the regular key pair
associated with an account. You can protect your account by assigning a regular key
pair to it and using it instead of the master key pair to sign transactions whenever
possible. If your regular key pair is compromised, but your master key pair is not, you
can use a SetRegularKey transaction to regain control of your account.

`See SetRegularKey <https://xrpl.org/setregularkey.html>`_
"""
from dataclasses import dataclass
from typing import Optional

from xrpl.models.transactions.transaction import Transaction, TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class SetRegularKey(Transaction):
    """
    Represents a SetRegularKey transaction on the XRP Ledger.

    A SetRegularKey transaction assigns, changes, or removes the regular key pair
    associated with an account.You can protect your account by assigning a regular key
    pair to it and using it instead of the master key pair to sign transactions
    whenever possible. If your regular key pair is compromised, but your master key
    pair is not, you can use a SetRegularKey transaction to regain control of your
    account.

    `See SetRegularKey <https://xrpl.org/setregularkey.html>`_
    """

    regular_key: Optional[str] = None
    transaction_type: TransactionType = TransactionType.SET_REGULAR_KEY
