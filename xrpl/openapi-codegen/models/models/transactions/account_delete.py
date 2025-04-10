"""Model for AccountDelete transaction type."""
from dataclasses import dataclass, field
from typing import List, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class AccountDelete(Transaction):
    """
    An AccountDelete transaction deletes an account and any objects it owns in the XRP
    Ledger, if possible, sending the account's remaining XRP to a specified destination
    account.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.ACCOUNT_DELETE,
        init=False
    )

    credential_ids: Optional[List[str]] = None
    """
    (Optional) Set of Credentials to authorize a deposit made by this transaction. Each
    member of the array must be the ledger entry ID of a Credential entry in the ledger. For
    details, see Credential IDs.
    """

    destination: str = REQUIRED
    """
    (Required) The address of an account to receive any leftover XRP after deleting the
    sending account. Must be a funded account in the ledger, and must not be the sending
    account.
    """

    destination_tag: Optional[int] = None
    """
    (Optional) Arbitrary destination tag that identifies a hosted recipient or other
    information for the recipient of the deleted account's leftover XRP.
    """

    def _get_errors(self: AccountDelete) -> Dict[str, str]:
        errors = super._get_errors()
        if self.credential_ids is not None and len(self.credential_ids) < 1:
            errors["AccountDelete"] = "Field `credential_ids` must have a length greater than or equal to 1"
        if self.credential_ids is not None and len(self.credential_ids) > 8:
            errors["AccountDelete"] = "Field `credential_ids` must have a length less than or equal to 8"
        if len(self.credential_ids) != len(set(self.credential_ids)):
            errors["AccountDelete"] = "`credential_ids` list cannot contain duplicate values"
        return errors


