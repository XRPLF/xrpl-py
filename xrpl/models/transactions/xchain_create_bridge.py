"""Model for a XChainCreateBridge transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from xrpl.models.currencies import XRP
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

    signature_reward: str = REQUIRED  # type: ignore

    min_account_create_amount: Optional[str] = None

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_CREATE_BRIDGE,
        init=False,
    )

    def _get_errors(self: XChainCreateBridge) -> Dict[str, str]:
        errors = super()._get_errors()

        bridge = self.xchain_bridge

        if bridge.locking_chain_door == bridge.issuing_chain_door:
            errors[
                "xchain_bridge"
            ] = "Cannot have the same door accounts on the locking and issuing chain."

        if self.account not in [bridge.locking_chain_door, bridge.issuing_chain_door]:
            errors[
                "account"
            ] = "Account must be either locking chain door or issuing chain door."

        if (bridge.locking_chain_issue == XRP()) != (
            bridge.issuing_chain_issue == XRP()
        ):
            errors["issue"] = "Bridge must be XRP-XRP or IOU-IOU."

        if (
            self.min_account_create_amount is not None
            and bridge.locking_chain_issue != XRP()
        ):
            errors[
                "min_account_create_amount"
            ] = "Cannot have MinAccountCreateAmount if bridge is IOU-IOU."

        if self.signature_reward is not None and not self.signature_reward.isnumeric():
            errors["signature_reward"] = "signature_reward must be numeric."

        if (
            self.min_account_create_amount is not None
            and not self.min_account_create_amount.isnumeric()
        ):
            errors[
                "min_account_create_amount_value"
            ] = "min_account_create_amount must be numeric."

        return errors
