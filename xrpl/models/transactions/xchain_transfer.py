"""Model for a XChainTransfer transaction type."""

from dataclasses import dataclass, field

from xrpl.models.required import REQUIRED
from xrpl.models.sidechain import Sidechain
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainTransfer(Transaction):
    """Represents a XChainTransfer transaction."""

    sidechain: Sidechain = REQUIRED  # type: ignore

    xchain_sequence: int = REQUIRED  # type: ignore

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_DOOR_CREATE,
        init=False,
    )
