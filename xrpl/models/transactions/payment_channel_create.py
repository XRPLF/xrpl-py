"""
Represents a PaymentChannelCreate transaction on the XRP Ledger.
A PaymentChannelCreate transaction creates a unidirectional channel and
funds it with XRP. The address sending this transaction becomes the
"source address" of the payment channel.

`See PaymentChannelCreate <https://xrpl.org/paymentchannelcreate.html>`_
"""
from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class PaymentChannelCreate(Transaction):
    """
    Represents a PaymentChannelCreate transaction on the XRP Ledger.
    A PaymentChannelCreate transaction creates a unidirectional channel and
    funds it with XRP. The address sending this transaction becomes the
    "source address" of the payment channel.

    `See PaymentChannelCreate <https://xrpl.org/paymentchannelcreate.html>`_
    """

    #: This field is required.
    amount: Amount = REQUIRED  # type: ignore
    #: This field is required.
    destination: str = REQUIRED  # type: ignore
    #: This field is required.
    settle_delay: int = REQUIRED  # type: ignore
    #: This field is required.
    public_key: str = REQUIRED  # type: ignore
    cancel_after: Optional[int] = None
    destination_tag: Optional[int] = None
    transaction_type: TransactionType = field(
        default=TransactionType.PAYMENT_CHANNEL_CREATE,
        init=False,
    )
