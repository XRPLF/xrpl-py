"""Model for DIDDelete transaction type."""
from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class DIDDelete(Transaction):
    """
    Delete the DID ledger entry associated with the specified Account field.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.DID_DELETE,
        init=False
    )


