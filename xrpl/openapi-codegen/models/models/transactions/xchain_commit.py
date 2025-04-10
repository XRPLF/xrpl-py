"""Model for XChainCommit transaction type."""
from dataclasses import dataclass, field
from typing import Any, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.xchain_bridge import XChainBridge
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class XChainCommit(Transaction):
    """
    The XChainCommit is the second step in a cross-chain transfer. It puts assets into trust
    on the locking chain so that they can be wrapped on the issuing chain, or burns wrapped
    assets on the issuing chain so that they can be returned on the locking chain.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_COMMIT,
        init=False
    )

    amount: Optional[Any] = REQUIRED
    """
    The asset to commit, and the quantity. This must match the door account's
    LockingChainIssue (if on the locking chain) or the door account's IssuingChainIssue (if
    on the issuing chain).
    """

    other_chain_destination: Optional[str] = None
    """
    (Optional) The destination account on the destination chain. If this is not specified,
    the account that submitted the XChainCreateClaimID transaction on the destination chain
    will need to submit a XChainClaim transaction to claim the funds.
    """

    x_chain_bridge: XChainBridge = REQUIRED
    x_chain_claim_id: str = REQUIRED
    """
    The unique integer ID for a cross-chain transfer. This must be acquired on the
    destination chain (via a XChainCreateClaimID transaction) and checked from a validated
    ledger before submitting this transaction. If an incorrect sequence number is specified,
    the funds will be lost.
    """


