"""
Represents a VaultSet transaction on the XRP Ledger.
"""

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class VaultSet(Transaction):
    """
    Represents a VaultSet transaction on the XRP Ledger.
    """

    vault_id: str = REQUIRED  # type: ignore
    domain_id: Optional[str] = None
    data: Optional[str] = None
    asset_maximum: Optional[str] = None

    transaction_type: TransactionType = field(
        default=TransactionType.VAULT_SET,
        init=False,
    )
