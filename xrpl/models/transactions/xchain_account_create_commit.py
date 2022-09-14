"""Model for a XChainAccountCreateCommit transaction type."""

from dataclasses import dataclass, field

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init
from xrpl.models.xchain_bridge import XChainBridge


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainAccountCreateCommit(Transaction):
    """Represents a XChainAccountCreateCommit transaction."""

    xchain_bridge: XChainBridge = REQUIRED  # type: ignore

    signature_reward: Amount = REQUIRED  # type: ignore

    destination: str = REQUIRED  # type: ignore

    amount: Amount = REQUIRED  # type: ignore

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_ACCOUNT_CREATE_COMMIT,
        init=False,
    )
