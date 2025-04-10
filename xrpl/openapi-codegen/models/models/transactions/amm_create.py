"""Model for AMMCreate transaction type."""
from dataclasses import dataclass, field
from typing import Any, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class AMMCreate(Transaction):
    """
    Create a new Automated Market Maker (AMM) instance for trading a pair of assets
    (fungible tokens or XRP). Creates both an AMM entry and a special AccountRoot entry to
    represent the AMM. Also transfers ownership of the starting balance of both assets from
    the sender to the created AccountRoot and issues an initial balance of liquidity
    provider tokens (LP Tokens) from the AMM account to the sender.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.AMM_CREATE,
        init=False
    )

    amount: Optional[Any] = REQUIRED
    """
    (Required) The first of the two assets to fund this AMM with. This must be a positive
    amount.
    """

    amount2: Optional[Any] = REQUIRED
    """
    (Required) The second of the two assets to fund this AMM with. This must be a positive
    amount.
    """

    trading_fee: int = REQUIRED
    """
    (Required) The fee to charge for trades against this AMM instance, in units of
    1/100,000; a value of 1 is equivalent to 0.001%. The maximum value is 1000, indicating a
    1% fee. The minimum value is 0.
    """

    def _get_errors(self: AMMCreate) -> Dict[str, str]:
        errors = super._get_errors()
        if self.trading_fee is not None and self.trading_fee < 0:
            errors["AMMCreate"] = "Field `trading_fee` must have a value greater than or equal to 0"
        if self.trading_fee is not None and self.trading_fee > 1000:
            errors["AMMCreate"] = "Field `trading_fee` must have a value less than or equal to 1000"
        return errors


