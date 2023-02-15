"""Model for a XChainModifyBridge transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from xrpl.models.currencies import XRP
from xrpl.models.flags import FlagInterface
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init
from xrpl.models.xchain_bridge import XChainBridge


class XChainModifyBridgeFlag(int, Enum):
    """
    Transactions of the XChainModifyBridge type support additional values in the Flags
    field. This enum represents those options.
    """

    TF_CLEAR_ACCOUNT_CREATE_AMOUNT = 0x00010000


class XChainModifyBridgeFlagInterface(FlagInterface):
    """
    Transactions of the XChainModifyBridge type support additional values in the Flags
    field. This TypedDict represents those options.
    """

    TF_CLEAR_ACCOUNT_CREATE_AMOUNT: bool


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainModifyBridge(Transaction):
    """Represents a XChainModifyBridge transaction."""

    xchain_bridge: XChainBridge = REQUIRED  # type: ignore

    signature_reward: Optional[str] = None

    min_account_create_amount: Optional[str] = None

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_MODIFY_BRIDGE,
        init=False,
    )

    def _get_errors(self: XChainModifyBridge) -> Dict[str, str]:
        errors = super()._get_errors()

        bridge = self.xchain_bridge

        if self.signature_reward is None and self.min_account_create_amount is None:
            errors[
                "xchain_modify_bridge"
            ] = "Must either change signature_reward or min_account_create_amount."

        if self.account not in [bridge.locking_chain_door, bridge.issuing_chain_door]:
            errors[
                "account"
            ] = "Account must be either locking chain door or issuing chain door."

        if self.signature_reward is not None and not self.signature_reward.isnumeric():
            errors["signature_reward"] = "`signature_reward` must be numeric."

        if (
            self.min_account_create_amount is not None
            and bridge.locking_chain_issue != XRP()
        ):
            errors[
                "min_account_create_amount"
            ] = "Cannot have MinAccountCreateAmount if bridge is IOU-IOU."

        if (
            self.min_account_create_amount is not None
            and not self.min_account_create_amount.isnumeric()
        ):
            errors[
                "min_account_create_amount_value"
            ] = "`min_account_create_amount` must be numeric."

        return errors
