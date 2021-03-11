"""
Represents a PaymentChannelClaim transaction on the XRP Ledger.
A PaymentChannelClaim transaction claims XRP from a payment channel, adjusts
the payment channel's expiration, or both. This transaction can be used differently
depending on the transaction sender's role in the specified channel.

`See PaymentChannelClaim <https://xrpl.org/paymentchannelclaim.html>`_
"""
from dataclasses import dataclass
from typing import Optional

from xrpl.models.base_model import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionType


@dataclass(frozen=True)
class PaymentChannelClaim(Transaction):
    """
    Represents a PaymentChannelClaim transaction on the XRP Ledger.
    A PaymentChannelClaim transaction claims XRP from a payment channel, adjusts
    the payment channel's expiration, or both. This transaction can be used differently
    depending on the transaction sender's role in the specified channel.

    `See PaymentChannelClaim <https://xrpl.org/paymentchannelclaim.html>`_
    """

    channel: str = REQUIRED  # type: ignore
    balance: Optional[str] = None
    amount: Optional[str] = None
    signature: Optional[str] = None
    public_key: Optional[str] = None
    transaction_type: TransactionType = TransactionType.PAYMENT_CHANNEL_CLAIM
