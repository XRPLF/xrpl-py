"""Model for XChainCreateBridge transaction type."""
from dataclasses import dataclass, field
from typing import Any, Optional
from xrpl.models.currencies import XRP
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.xchain_bridge import XChainBridge
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class XChainCreateBridge(Transaction):
    """
    The XChainCreateBridge transaction creates a new Bridge ledger object and defines a new
    cross-chain bridge entrance on the chain that the transaction is submitted on. It
    includes information about door accounts and assets for the bridge.  The transaction
    must be submitted first by the locking chain door account. To set up a valid bridge,
    door accounts on both chains must submit this transaction, in addition to setting up
    witness servers.  The complete production-grade setup would also include a SignerListSet
    transaction on the two door accounts for the witnesses’ signing keys, as well as
    disabling the door accounts’ master key. This ensures that the witness servers are truly
    in control of the funds.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_CREATE_BRIDGE,
        init=False
    )

    min_account_create_amount: Optional[Any] = None
    """
    (Optional) The minimum amount, in XRP, required for a XChainAccountCreateCommit
    transaction. If this isn't present, the XChainAccountCreateCommit transaction will fail.
    This field can only be present on XRP-XRP bridges.
    """

    signature_reward: Optional[Any] = REQUIRED
    """
    The total amount to pay the witness servers for their signatures. This amount will be
    split among the signers.
    """

    x_chain_bridge: XChainBridge = REQUIRED
    def _get_errors(self: XChainCreateBridge) -> Dict[str, str]:
        errors = super._get_errors()
        if self.account not in [self.xchain_bridge.issuing_chain_door,self.xchain_bridge.locking_chain_door]:
            errors["XChainCreateBridge"] = "`account` must be one of `xchain_bridge.issuing_chain_door`, or `xchain_bridge.locking_chain_door`"
        if (
            (self.xchain_bridge.issuing_chain_issue == XRP()) !=
            (self.xchain_bridge.locking_chain_issue == XRP())
        ):
            error["XChainCreateBridge"] = "`xchain_bridge.issuing_chain_issue`, `xchain_bridge.locking_chain_issue` must be XRP-XRP or IOU-IOU"
        return errors


