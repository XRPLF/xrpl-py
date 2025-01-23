"""
Represents a VaultClawback transaction on the XRP Ledger.
"""

from dataclasses import dataclass, field
from typing import Optional, Union

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class VaultClawback(Transaction):
    """
    Represents a VaultClawback transaction on the XRP Ledger.
    """

    vault_id: str = REQUIRED  # type: ignore
    holder: str = REQUIRED  # type: ignore
    amount: Optional[int] = None

    transaction_type: TransactionType = field(
        default=TransactionType.VAULT_CLAWBACK,
        init=False,
    )
