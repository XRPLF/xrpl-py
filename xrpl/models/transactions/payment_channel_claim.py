"""Model for PaymentChannelClaim transaction type."""
from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class PaymentChannelClaim(Transaction):
    """
    Represents a `PaymentChannelClaim <https://xrpl.org/paymentchannelclaim.html>`_
    transaction, which claims XRP from a `payment channel
    <https://xrpl.org/payment-channels.html>`_, adjusts
    channel's expiration, or both. This transaction can be used differently
    depending on the transaction sender's role in the specified channel.
    """

    #: The unique ID of the payment channel, as a 64-character hexadecimal
    #: string. This field is required.
    channel: str = REQUIRED  # type: ignore

    #: The cumulative amount of XRP to have delivered through this channel after
    #: processing this claim. Required unless closing the channel.
    balance: Optional[str] = None

    #: The cumulative amount of XRP that has been authorized to deliver by the
    #: attached claim signature. Required unless closing the channel.
    amount: Optional[str] = None

    #: The signature of the claim, as hexadecimal. This signature must be
    #: verifiable for the this channel and the given ``public_key`` and ``amount``
    #: values. May be omitted if closing the channel or if the sender of this
    #: transaction is the source address of the channel; required otherwise.
    signature: Optional[str] = None

    #: The public key that should be used to verify the attached signature. Must
    #: match the `PublicKey` that was provided when the channel was created.
    #: Required if ``signature`` is provided.
    public_key: Optional[str] = None

    transaction_type: TransactionType = field(
        default=TransactionType.PAYMENT_CHANNEL_CLAIM,
        init=False,
    )
