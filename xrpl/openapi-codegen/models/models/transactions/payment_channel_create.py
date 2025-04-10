"""Model for PaymentChannelCreate transaction type."""
from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class PaymentChannelCreate(Transaction):
    """
    Create a payment channel and fund it with XRP. The address sending this transaction
    becomes the \"source address\" of the payment channel.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.PAYMENT_CHANNEL_CREATE,
        init=False
    )

    amount: str = REQUIRED
    """
    Amount of XRP, in drops, to deduct from the sender's balance and set aside in this
    channel. While the channel is open, the XRP can only go to the Destination address. When
    the channel closes, any unclaimed XRP is returned to the source address's balance.
    """

    destination: str = REQUIRED
    """
    Address to receive XRP claims against this channel. This is also known as the
    \"destination address\" for the channel. Cannot be the same as the sender (Account).
    """

    settle_delay: int = REQUIRED
    """
    Amount of time the source address must wait before closing the channel if it has
    unclaimed XRP.
    """

    public_key: str = REQUIRED
    """
    The 33-byte public key of the key pair the source will use to sign claims against this
    channel, in hexadecimal. This can be any secp256k1 or Ed25519 public key.
    """

    cancel_after: Optional[int] = None
    """
    (Optional) The time, in seconds since the Ripple Epoch, when this channel expires. Any
    transaction that would modify the channel after this time closes the channel without
    otherwise affecting it. This value is immutable; the channel can be closed earlier than
    this time but cannot remain open after this time.
    """

    destination_tag: Optional[int] = None
    """
    (Optional) Arbitrary tag to further specify the destination for this payment channel,
    such as a hosted recipient at the destination address.
    """

    def _get_errors(self: PaymentChannelCreate) -> Dict[str, str]:
        errors = super._get_errors()
        if self.destination is not None and self.destination == self.account:
            errors[PaymentChannelCreate] = "destination must not be equal to account."
        return errors


