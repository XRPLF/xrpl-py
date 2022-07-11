"""Model for a XChainCreateClaimID transaction type."""

from dataclasses import dataclass, field

from xrpl.models.amounts import Amount
from xrpl.models.bridge import Bridge
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainCreateClaimID(Transaction):
    """Represents a XChainCreateClaimID transaction."""

    bridge: Bridge = REQUIRED  # type: ignore

    signature_reward: Amount = REQUIRED  # type: ignore

    other_chain_account: str = REQUIRED  # type: ignore

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_CREATE_CLAIM_ID,
        init=False,
    )
