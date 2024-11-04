"""Model for AccountDelete transaction type."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import (
    KW_ONLY_DATACLASS,
    require_kwargs_on_init,
    validate_credential_ids,
)


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
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

    destination: str = REQUIRED  # type: ignore
    """
    The address of the account to which to send any remaining XRP.
    This field is required.

    :meta hide-value:
    """

    destination_tag: Optional[int] = None
    """
    The `destination tag
    <https://xrpl.org/source-and-destination-tags.html>`_ at the
    ``destination`` account where funds should be sent.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.ACCOUNT_DELETE,
        init=False,
    )

    credential_ids: Optional[List[str]] = None
    """Credentials associated with sender of this transaction. The credentials included
    must not be expired. The list must not be empty when specified and cannot contain
    more than 8 credentials."""

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        errors.update(validate_credential_ids(self.credential_ids))
        return errors
