"""Model for AMMVote transaction type."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.amm_instance_create import AMM_MAX_TRADING_FEE
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AMMVote(Transaction):
    """
    AMMVote is used for submitting a vote for the trading fee of an AMM Instance.

    Any XRPL account that holds LPToken for an AMM instance may submit this
    transaction to vote for the trading fee for that instance.
    """

    amm_id: str = REQUIRED  # type: ignore
    """
    A hash that uniquely identifies the AMM instance. This field is required.
    """

    fee_val: int = REQUIRED  # type: ignore
    """
    Specifies the fee, in basis point.
    Valid values for this field are between 0 and 65000 inclusive.
    A value of 1 is equivalent to 1/10 bps or 0.001%, allowing trading fee
    between 0% and 65%. This field is required.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.AMM_VOTE,
        init=False,
    )

    def _get_errors(self: AMMVote) -> Dict[str, str]:
        return {
            key: value
            for key, value in {
                **super()._get_errors(),
                "fee_val": self._get_fee_val_error(),
            }.items()
            if value is not None
        }

    def _get_fee_val_error(self: AMMVote) -> Optional[str]:
        if self.fee_val < 0 or self.fee_val > AMM_MAX_TRADING_FEE:
            return f"Must be between 0 and {AMM_MAX_TRADING_FEE}"
        return None
