"""Model for PaymentChannelClaim transaction type."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from xrpl.models.amounts import Amount
from xrpl.models.flags import FlagInterface
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


class PaymentChannelClaimFlag(int, Enum):
    """
    Transactions of the PaymentChannelClaim type support additional values in the Flags
    field. This enum represents those options.

    `See PaymentChannelClaim Flags
    <https://xrpl.org/paymentchannelclaim.html#paymentchannelclaim-flags>`_
    """

    TF_RENEW = 0x00010000
    """
    Clear the channel's `Expiration` time. (`Expiration` is different from the
    channel's immutable `CancelAfter` time.) Only the source address of the payment
    channel can use this flag.
    """

    TF_CLOSE = 0x00020000
    """
    Request to close the channel. Only the channel source and destination addresses
    can use this flag. This flag closes the channel immediately if it has no more
    funds allocated to it after processing the current claim, or if the destination
    address uses it. If the source address uses this flag when the channel still
    holds a value, this schedules the channel to close after `SettleDelay` seconds have
    passed. (Specifically, this sets the `Expiration` of the channel to the close
    time of the previous ledger plus the channel's `SettleDelay` time, unless the
    channel already has an earlier `Expiration` time.) If the destination address
    uses this flag when the channel still holds an amount, any amount that remains
    after processing the claim is returned to the source address.
    """


class PaymentChannelClaimFlagInterface(FlagInterface):
    """
    Transactions of the PaymentChannelClaim type support additional values in the Flags
    field. This TypedDict represents those options.

    `See PaymentChannelClaim Flags
    <https://xrpl.org/paymentchannelclaim.html#paymentchannelclaim-flags>`_
    """

    TF_RENEW: bool
    TF_CLOSE: bool


@require_kwargs_on_init
@dataclass(frozen=True)
class PaymentChannelClaim(Transaction):
    """
    Represents a `PaymentChannelClaim <https://xrpl.org/paymentchannelclaim.html>`_
    transaction, which claims an amount from a `payment channel
    <https://xrpl.org/payment-channels.html>`_, adjusts
    channel's expiration, or both. This transaction can be used differently
    depending on the transaction sender's role in the specified channel.
    """

    channel: str = REQUIRED  # type: ignore
    """
    The unique ID of the payment channel, as a 64-character hexadecimal
    string. This field is required.

    :meta hide-value:
    """

    balance: Optional[Amount] = None
    """
    Total amount delivered by this channel after processing this claim. Required
    to deliver amount. Must be more than the total amount delivered by the channel
    so far, but not greater than the Amount of the signed claim. Must be provided
    except when closing the channel.
    """

    amount: Optional[Amount] = None
    """
    The amount authorized by the Signature. This must match the amount in the signed
    message. This is the cumulative amount that can be dispensed by the channel,
    including amounts previously redeemed. Required unless closing the channel.
    """

    signature: Optional[str] = None
    """
    The signature of the claim, as hexadecimal. This signature must be
    verifiable for the this channel and the given ``public_key`` and ``amount``
    values. May be omitted if closing the channel or if the sender of this
    transaction is the source address of the channel; required otherwise.
    """

    public_key: Optional[str] = None
    """
    The public key that should be used to verify the attached signature. Must
    match the `PublicKey` that was provided when the channel was created.
    Required if ``signature`` is provided.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.PAYMENT_CHANNEL_CLAIM,
        init=False,
    )
