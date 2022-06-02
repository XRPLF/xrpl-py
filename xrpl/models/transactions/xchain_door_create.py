"""Model for a XChainDoorCreate transaction type."""

from dataclasses import dataclass, field
from typing import List

from xrpl.models.required import REQUIRED
from xrpl.models.sidechain import Sidechain
from xrpl.models.transactions.signer_list_set import SignerEntry
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainDoorCreate(Transaction):
    """Represents a XChainDoorCreate transaction."""

    sidechain: Sidechain = REQUIRED  # type: ignore

    signer_entries: List[SignerEntry] = REQUIRED  # type: ignore

    signer_quorum: int = REQUIRED  # type: ignore

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_DOOR_CREATE,
        init=False,
    )
