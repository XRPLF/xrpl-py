"""Model for AccountDelete transaction type."""

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AccountDelete(Transaction):
    """
    Represents an `AccountDelete transaction
    <https://xrpl.org/accountdelete.html>`_, which deletes an account and any
    objects it owns in the XRP Ledger, if possible, sending the account's remaining
    XRP to a specified destination account.

    See `Deletion of Accounts
    <https://xrpl.org/accounts.html#deletion-of-accounts>`_ for the requirements to
    delete an account.
    """

    #: The address of the account to send any remaining XRP to.
    #: This field is required.
    destination: str = REQUIRED  # type: ignore

    #: The `destination tag
    #: <https://xrpl.org/source-and-destination-tags.html>`_ at the
    #: ``destination`` account where funds should be sent.
    destination_tag: Optional[int] = None

    transaction_type: TransactionType = field(
        default=TransactionType.ACCOUNT_DELETE,
        init=False,
    )
