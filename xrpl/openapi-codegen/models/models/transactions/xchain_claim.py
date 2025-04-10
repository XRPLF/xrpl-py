"""Model for XChainClaim transaction type."""
from dataclasses import dataclass, field
from typing import Any, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.xchain_bridge import XChainBridge
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class XChainClaim(Transaction):
    """
    The XChainClaim transaction completes a cross-chain transfer of value. It allows a user
    to claim the value on the destination chain - the equivalent of the value locked on the
    source chain. A user can only claim the value if they own the cross-chain claim ID
    associated with the value locked on the source chain (the Account field). The user can
    send the funds to anyone (the Destination field). This transaction is only needed if an
    OtherChainDestination isn't specified in the XChainCommit transaction, or if something
    goes wrong with the automatic transfer of funds.  If the transaction succeeds in moving
    funds, the referenced XChainOwnedClaimID ledger object will be destroyed. This prevents
    transaction replay. If the transaction fails, the XChainOwnedClaimID won't be destroyed
    and the transaction can be re-run with different parameters.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_CLAIM,
        init=False
    )

    amount: Optional[Any] = REQUIRED
    """
    The amount to claim on the destination chain. This must match the amount attested to on
    the attestations associated with this XChainClaimID.
    """

    destination: str = REQUIRED
    """
    The destination account on the destination chain. It must exist or the transaction will
    fail. However, if the transaction fails in this case, the sequence number and collected
    signatures won't be destroyed, and the transaction can be rerun with a different
    destination.
    """

    destination_tag: Optional[int] = None
    """
    (Optional) An integer destination tag.
    """

    x_chain_bridge: XChainBridge = REQUIRED
    x_chain_claim_id: str = REQUIRED
    """
    The unique integer ID for the cross-chain transfer that was referenced in the
    corresponding XChainCommit transaction.
    """

    def _get_errors(self: XChainClaim) -> Dict[str, str]:
        errors = super._get_errors()
        return errors


