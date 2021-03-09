"""
Represents a PaymentChannelCreate transaction on the XRP Ledger.
A PaymentChannelCreate transaction creates a unidirectional channel and
funds it with XRP. The address sending this transaction becomes the
"source address" of the payment channel.

`See PaymentChannelCreate <https://xrpl.org/paymentchannelcreate.html>`_
"""
from dataclasses import dataclass
from typing import Optional

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionType


@dataclass(frozen=True)
class PaymentChannelCreate(Transaction):
    """
    Represents a PaymentChannelCreate transaction on the XRP Ledger.
    A PaymentChannelCreate transaction creates a unidirectional channel and
    funds it with XRP. The address sending this transaction becomes the
    "source address" of the payment channel.

    `See PaymentChannelCreate <https://xrpl.org/paymentchannelcreate.html>`_
    """

    amount: Amount = REQUIRED
    destination: str = REQUIRED
    settle_delay: int = REQUIRED
    public_key: str = REQUIRED
    cancel_after: Optional[int] = None
    destination_tag: Optional[int] = None
    transaction_type: TransactionType = TransactionType.PAYMENT_CHANNEL_CREATE
