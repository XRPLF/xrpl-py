"""Model for a XChainCommit transaction type."""

from dataclasses import dataclass, field
from typing import Optional, Union

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init
from xrpl.models.xchain_bridge import XChainBridge


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainCommit(Transaction):
    """Represents a XChainCommit transaction."""

    xchain_bridge: XChainBridge = REQUIRED  # type: ignore

    xchain_claim_id: Union[int, str] = REQUIRED  # type: ignore

    amount: Amount = REQUIRED  # type: ignore

    other_chain_destination: Optional[str] = None

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_COMMIT,
        init=False,
    )
