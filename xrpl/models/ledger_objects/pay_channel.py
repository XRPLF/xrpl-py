"""Models for the Ledger Object `PayChannel`"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class PayChannel(LedgerObject):
    """The model for the `PayChannel` Ledger Object"""

    account: str = REQUIRED  # type: ignore
    """
    The source address that owns this payment channel. This comes from the sending
    address of the transaction that created the channel. This field is required.
    """

    amount: str = REQUIRED  # type: ignore
    """
    Total XRP, in drops, that has been allocated to this channel. This includes XRP
    that has been paid to the destination address. This is initially set by the
    transaction that created the channel and can be increased if the source address
    sends a `PaymentChannelFund` transaction. This field is required.
    """

    balance: str = REQUIRED  # type: ignore
    """
    Total XRP, in drops, already paid out by the channel. The difference between this
    value and the `Amount` field is how much XRP can still be paid to the destination
    address with PaymentChannelClaim transactions. If the channel closes, the remaining
    difference is returned to the source address. This field is required.
    """

    destination: str = REQUIRED  # type: ignore
    """
    The destination address for this payment channel. While the payment channel is open,
    this address is the only one that can receive XRP from the channel. This comes from
    the `Destination` field of the transaction that created the channel. This field is
    required.
    """

    destination_tag: Optional[int] = None
    """
    An arbitrary tag to further specify the destination for this payment channel, such
    as a hosted recipient at the destination address.
    """

    destination_node: Optional[str] = None
    """
    A hint indicating which page of the destination's owner directory links to this
    entry, in case the directory consists of multiple pages. Omitted on payment
    channels created before enabling the fixPayChanRecipientOwnerDir amendment.
    """

    owner_node: str = REQUIRED  # type: ignore
    """
    A hint indicating which page of the source address's owner directory links to this
    entry, in case the directory consists of multiple pages. This field is required.
    """

    public_key: str = REQUIRED  # type: ignore
    """
    Public key, in hexadecimal, of the key pair that can be used to sign claims against
    this channel. This can be any valid secp256k1 or Ed25519 public key. This is set by
    the transaction that created the channel and must match the public key used in
    claims against the channel. The channel source address can also send XRP from this
    channel to the destination without signed claims. This field is required.
    """

    previous_txn_id: str = REQUIRED  # type: ignore
    """
    The identifying hash of the transaction that most recently modified this entry.
    This field is required.
    """

    previous_txn_lgr_seq: int = REQUIRED  # type: ignore
    """
    The index of the ledger that contains the transaction that most recently modified
    this entry. This field is required.
    """

    settle_delay: int = REQUIRED  # type: ignore
    """
    Number of seconds the source address must wait to close the channel if it still has
    any XRP in it. Smaller values mean that the destination address has less time to
    redeem any outstanding claims after the source address requests to close the
    channel. Can be any value that fits in a 32-bit unsigned integer (0 to 2^32-1).
    This is set by the transaction that creates the channel. This field is required.
    """

    expiration: Optional[int] = None
    """
    The mutable expiration time for this payment channel, in seconds since the Ripple
    Epoch. The channel is expired if this value is present and smaller than the
    previous ledger's close_time field. See Channel Expiration for more details.
    """

    cancel_after: Optional[int] = None
    """
    The immutable expiration time for this payment channel, in seconds since the Ripple
    Epoch. This channel is expired if this value is present and smaller than the
    previous ledger's close_time field. This is optionally set by the transaction that
    created the channel, and cannot be changed. This field is required.
    """

    source_tag: Optional[int] = None
    """
    An arbitrary tag to further specify the source for this payment channel, such as a
    hosted recipient at the owner's address.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.PAY_CHANNEL,
        init=False,
    )
