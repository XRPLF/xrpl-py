"""Model for a XChainClaim transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Union

from xrpl.models.amounts import Amount
from xrpl.models.currencies import XRP
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init
from xrpl.models.xchain_bridge import XChainBridge


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainClaim(Transaction):
    """Represents a XChainClaim transaction."""

    xchain_bridge: XChainBridge = REQUIRED  # type: ignore

    xchain_claim_id: Union[int, str] = REQUIRED  # type: ignore

    destination: str = REQUIRED  # type: ignore

    destination_tag: Optional[int] = None

    amount: Amount = REQUIRED  # type: ignore

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_CLAIM,
        init=False,
    )

    def _get_errors(self: XChainClaim) -> Dict[str, str]:
        errors = super()._get_errors()

        bridge = self.xchain_bridge
        currency = XRP() if isinstance(self.amount, str) else self.amount.to_currency()
        if (
            currency != bridge.locking_chain_issue
            and currency != bridge.issuing_chain_issue
        ):
            errors[
                "amount"
            ] = "Amount must match either locking chain issue or issuing chain issue."

        return errors
