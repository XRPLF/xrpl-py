"""Model for AMMCreate transaction type."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from typing_extensions import Final

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init

AMM_MAX_TRADING_FEE: Final[int] = 1000


@require_kwargs_on_init
@dataclass(frozen=True)
class AMMCreate(Transaction):
    """
    AMMCreate is used to create AccountRoot and the corresponding AMM
    ledger entries.
    This allows for the creation of only one AMM instance per unique asset pair.
    """

    amount: Amount = REQUIRED  # type: ignore
    """
    Specifies one of the pool assets (XRP or token) of the AMM instance.
    This field is required.
    """

    amount2: Amount = REQUIRED  # type: ignore
    """
    Specifies the other pool asset of the AMM instance. This field is required.
    """

    trading_fee: int = REQUIRED  # type: ignore
    """
    Specifies the fee, in basis point, to be charged
    to the traders for the trades executed against the AMM instance.
    Trading fee is a percentage of the trading volume.
    Valid values for this field are between 0 and 1000 inclusive.
    A value of 1 is equivalent to 1/10 bps or 0.001%, allowing trading fee
    between 0% and 1%. This field is required.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.AMM_CREATE,
        init=False,
    )

    def _get_errors(self: AMMCreate) -> Dict[str, str]:
        return {
            key: value
            for key, value in {
                **super()._get_errors(),
                "trading_fee": self._get_trading_fee_error(),
            }.items()
            if value is not None
        }

    def _get_trading_fee_error(self: AMMCreate) -> Optional[str]:
        if self.trading_fee < 0 or self.trading_fee > AMM_MAX_TRADING_FEE:
            return f"Must be between 0 and {AMM_MAX_TRADING_FEE}"
        return None
