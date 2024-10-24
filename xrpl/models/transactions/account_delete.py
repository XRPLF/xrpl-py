"""Model for AccountDelete transaction type."""

from dataclasses import dataclass, field
from typing import Dict, Optional, Set

from typing_extensions import Self

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


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

    credential_ids: Optional[Set[str]] = None
    """Credentials associated with sender of this transaction. The credentials included
    must not be expired. If there are duplicates provided in the list, they will be
    silently de-duped."""

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        # Validation checks on the credential_ids field
        if self.credential_ids is not None:
            if len(self.credential_ids) == 0:
                errors["credential_ids"] = "CredentialIDs list cannot be empty."
            if len(self.credential_ids) > 8:
                errors[
                    "credential_ids"
                ] = "CredentialIDs list cannot have more than 8 elements."

        return errors
