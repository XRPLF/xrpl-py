"""Model for a XChainCreateBridge transaction type."""

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init
from xrpl.models.xchain_bridge import XChainBridge


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainCreateBridge(Transaction):
    """Represents a XChainCreateBridge transaction."""

    xchain_bridge: XChainBridge = REQUIRED  # type: ignore

    signature_reward: Amount = REQUIRED  # type: ignore

    min_account_create_amount: Optional[Amount] = None

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_CREATE_BRIDGE,
        init=False,
    )
