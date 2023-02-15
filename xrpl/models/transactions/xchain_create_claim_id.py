"""Model for a XChainCreateClaimID transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from xrpl.core.addresscodec import is_valid_classic_address
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init
from xrpl.models.xchain_bridge import XChainBridge


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainCreateClaimID(Transaction):
    """Represents a XChainCreateClaimID transaction."""

    xchain_bridge: XChainBridge = REQUIRED  # type: ignore

    signature_reward: str = REQUIRED  # type: ignore

    other_chain_source: str = REQUIRED  # type: ignore

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_CREATE_CLAIM_ID,
        init=False,
    )

    def _get_errors(self: XChainCreateClaimID) -> Dict[str, str]:
        errors = super()._get_errors()

        if self.signature_reward is not None and not self.signature_reward.isnumeric():
            errors["signature_reward"] = "`signature_reward` must be numeric."

        if not is_valid_classic_address(self.other_chain_source):
            errors[
                "other_chain_source"
            ] = "`other_chain_source` must be a valid XRPL address."

        return errors
