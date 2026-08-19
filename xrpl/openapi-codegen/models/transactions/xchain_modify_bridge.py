"""Model for XChainModifyBridge transaction type."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.xchain_bridge import XChainBridge
from xrpl.models.xchain_modify_bridge_flag import XChainModifyBridgeFlag
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainModifyBridge(Transaction):
    """
    The XChainModifyBridge transaction allows bridge managers to modify the parameters of
    the bridge. They can only change the SignatureReward and the MinAccountCreateAmount.
    This transaction must be sent by the door account and requires the entities that control
    the witness servers to coordinate and provide the signatures for this transaction. This
    coordination happens outside the ledger.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_MODIFY_BRIDGE, init=False
    )

    min_account_create_amount: Optional[Any] = None
    """
    (Optional) The minimum amount, in XRP, required for a XChainAccountCreateCommit
    transaction. If this is not present, the XChainAccountCreateCommit transaction will
    fail. This field can only be present on XRP-XRP bridges.
    """

    signature_reward: Optional[Any] = None
    """
    (Optional) The signature reward split between the witnesses for submitting attestations.
    """

    x_chain_bridge: XChainBridge = REQUIRED

    def _get_errors(self: XChainModifyBridge) -> Dict[str, str]:
        errors = super._get_errors()
        if self.account not in [
            self.xchain_bridge.issuing_chain_door,
            self.xchain_bridge.locking_chain_door,
        ]:
            errors["XChainModifyBridge"] = (
                "`account` must be one of `xchain_bridge.issuing_chain_door`, or `xchain_bridge.locking_chain_door`"
            )
        return errors


class XChainModifyBridgeFlagInterface(FlagInterface):
    """
    Flags for the XChainModifyBridge transaction.
    """

    TF_CLEAR_ACCOUNT_CREATE_AMOUNT: bool


class XChainModifyBridgeFlag(int, Enum):
    """
    Flags for the XChainModifyBridge transaction.
    """

    TF_CLEAR_ACCOUNT_CREATE_AMOUNT = 0x00010000
    """
    Clears the MinAccountCreateAmount of the bridge.
    """
