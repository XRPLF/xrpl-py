"""Model for AMMVote transaction type."""
from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.currency import Currency
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class AMMVote(Transaction):
    """
    Vote on the trading fee for an Automated Market Maker instance. Up to 8 accounts can
    vote in proportion to the amount of the AMM's LP Tokens they hold. Each new vote
    re-calculates the AMM's trading fee based on a weighted average of the votes.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.AMM_VOTE,
        init=False
    )

    asset: Currency = REQUIRED
    """
    (Required) The definition for one of the assets in the AMM's pool. In JSON, this is an
            object with currency and issuer fields (omit issuer for XRP).
    """

    asset2: Currency = REQUIRED
    """
    (Required) The definition for the other asset in the AMM's pool. In JSON, this is an
            object with currency and issuer fields (omit issuer for XRP).
    """

    trading_fee: int = REQUIRED
    """
    (Required) The proposed fee to vote for, in units of 1/100,000; a value of 1 is
    equivalent to 0.001%. The maximum value is 1000, indicating a 1% fee.
    """

    def _get_errors(self: AMMVote) -> Dict[str, str]:
        errors = super._get_errors()
        if self.trading_fee is not None and self.trading_fee < 0:
            errors["AMMVote"] = "Field `trading_fee` must have a value greater than or equal to 0"
        if self.trading_fee is not None and self.trading_fee > 1000:
            errors["AMMVote"] = "Field `trading_fee` must have a value less than or equal to 1000"
        return errors


