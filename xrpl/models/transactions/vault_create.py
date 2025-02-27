"""
Represents a VaultCreate transaction on the XRP Ledger.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from xrpl.models.amounts import Amount
from xrpl.models.currencies import Currency
from xrpl.models.flags import FlagInterface
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


class VaultCreateFlag(int, Enum):

    TF_VAULT_PRIVATE = 0x0001
    TF_VAULT_SHARE_NON_TRANSFERABLE = 0x0002


class VaultCreateFlagInterface(FlagInterface):

    TF_VAULT_PRIVATE: bool
    TF_VAULT_SHARE_NON_TRANSFERABLE: bool


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class VaultCreate(Transaction):
    """
    Represents a VaultCreate transaction on the XRP Ledger.
    """

    data: Optional[str] = None
    # Keshava: TODO: Include MPT Issue in Asset field
    asset: Currency = REQUIRED  # type: ignore
    asset_maximum: Optional[str] = None
    mptoken_metadata: Optional[str] = None
    permissioned_domain_id: Optional[str] = None

    transaction_type: TransactionType = field(
        default=TransactionType.VAULT_CREATE,
        init=False,
    )
