"""
Represents a VaultDelete transaction on the XRP Ledger.
"""

from dataclasses import dataclass, field

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class VaultDelete(Transaction):
    """
    Represents a VaultDelete transaction on the XRP Ledger.
    """

    vault_id: str = REQUIRED  # type: ignore

    transaction_type: TransactionType = field(
        default=TransactionType.VAULT_DELETE,
        init=False,
    )
