"""Model for PaymentChannelFund transaction type."""
from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.amounts import get_amount_value
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class PaymentChannelFund(Transaction):
    """
    Add additional XRP to an open payment channel, and optionally update the expiration time
    of the channel. Only the source address of the channel can use this transaction.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.PAYMENT_CHANNEL_FUND,
        init=False
    )

    channel: str = REQUIRED
    """
    The unique ID of the channel to fund, as a 64-character hexadecimal string.
    """

    amount: str = REQUIRED
    """
    Amount of XRP, in drops, to add to the channel. Must be a positive amount of XRP.
    """

    expiration: Optional[int] = None
    """
    (Optional) New Expiration time to set for the channel, in seconds since the Ripple
    Epoch. This must be later than either the current time plus the SettleDelay of the
    channel, or the existing Expiration of the channel. After the Expiration time, any
    transaction that would access the channel closes the channel without taking its normal
    action. Any unspent XRP is returned to the source address when the channel closes.
    """

    def _get_errors(self: PaymentChannelFund) -> Dict[str, str]:
        errors = super._get_errors()
        if (
            self.amount is not None and 
            get_amount_value(self.amount) < 0
        ):
            return "`amount` value must be greater than 0"
        if (
            self.amount is not None 
            and self.amount != REQUIRED
            and not self.amount.isnumeric()
        ):
            errors["PaymentChannelFund"] = "`amount` must be numeric."
        return errors


