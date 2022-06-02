"""Model for a XChainSeqNumCreate transaction type."""

from dataclasses import dataclass, field

from xrpl.models.required import REQUIRED
from xrpl.models.sidechain import Sidechain
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainSeqNumCreate(Transaction):
    """Represents a XChainSeqNumCreate transaction."""

    sidechain: Sidechain = REQUIRED  # type: ignore

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_SEQ_NUM_CREATE,
        init=False,
    )
