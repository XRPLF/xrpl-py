"""Model for a XChainAccountCreateCommit transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

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

    signature_reward: str = REQUIRED  # type: ignore

    destination: str = REQUIRED  # type: ignore

    amount: str = REQUIRED  # type: ignore

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_ACCOUNT_CREATE_COMMIT,
        init=False,
    )

    def _get_errors(self: XChainAccountCreateCommit) -> Dict[str, str]:
        errors = super()._get_errors()

        if self.signature_reward is not None and not self.signature_reward.isnumeric():
            errors["signature_reward"] = "`signature_reward` must be numeric."

        if self.amount is not None and not self.amount.isnumeric():
            errors["amount"] = "`amount` must be numeric."

        return errors
