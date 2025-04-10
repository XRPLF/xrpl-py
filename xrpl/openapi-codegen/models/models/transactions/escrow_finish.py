"""Model for EscrowFinish transaction type."""
from dataclasses import dataclass, field
from typing import List, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class EscrowFinish(Transaction):
    """
    Deliver XRP from an escrow (held payment) to the recipient.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.ESCROW_FINISH,
        init=False
    )

    owner: str = REQUIRED
    """
    (Required) Address of the source account that funded the escrow.
    """

    offer_sequence: int = REQUIRED
    """
    (Required) Transaction sequence of EscrowCreate transaction that created the escrow to
    finish.
    """

    condition: Optional[str] = None
    """
    (Optional) Hex value matching the previously-supplied PREIMAGE-SHA-256 crypto-condition
    of the escrow.
    """

    credential_ids: Optional[List[str]] = None
    """
    (Optional) Set of Credentials to authorize a deposit made by this transaction. Each
    member of the array must be the ledger entry ID of a Credential entry in the ledger. For
    details, see Credential IDs.
    """

    fulfillment: Optional[str] = None
    """
    (Optional) Hex value of the PREIMAGE-SHA-256 crypto-condition fulfillment matching the
    escrow's Condition.
    """

    def _get_errors(self: EscrowFinish) -> Dict[str, str]:
        errors = super._get_errors()
        if (self.condition is not None) != (self.fulfillment is not None):
            errors["EscrowFinish"] = "Both `condition` and `fulfillment` are required if any is presented."
        if self.credential_ids is not None and len(self.credential_ids) < 1:
            errors["EscrowFinish"] = "Field `credential_ids` must have a length greater than or equal to 1"
        if self.credential_ids is not None and len(self.credential_ids) > 8:
            errors["EscrowFinish"] = "Field `credential_ids` must have a length less than or equal to 8"
        if len(self.credential_ids) != len(set(self.credential_ids)):
            errors["EscrowFinish"] = "`credential_ids` list cannot contain duplicate values"
        return errors


