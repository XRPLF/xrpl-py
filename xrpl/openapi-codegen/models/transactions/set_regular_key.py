"""Model for SetRegularKey transaction type."""

from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class SetRegularKey(Transaction):
    transaction_type: TransactionType = field(
        default=TransactionType.SET_REGULAR_KEY, init=False
    )

    regular_key: Optional[str] = None
    """
    (Optional) A base-58-encoded Address that indicates the regular key pair to be assigned
    to the account. If omitted, removes any existing regular key pair from the account. Must
    not match the master key pair for the address.
    """
