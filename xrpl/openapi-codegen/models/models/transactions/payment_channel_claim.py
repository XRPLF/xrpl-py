"""Model for PaymentChannelClaim transaction type."""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.payment_channel_claim_flag import PaymentChannelClaimFlag
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class PaymentChannelClaim(Transaction):
    """
    Claim XRP from a payment channel, adjust the payment channel's expiration, or both. 
    This transaction can be used differently depending on the transaction sender's role in
    the specified channel:  The source address of a channel can: - Send XRP from the channel
    to the destination with or without a signed Claim. - Set the channel to expire as soon
    as the channel's SettleDelay has passed. - Clear a pending Expiration time. - Close a
    channel immediately, with or without processing a claim first. The source address cannot
    close the channel immediately if the channel has XRP remaining.  The destination address
    of a channel can: - Receive XRP from the channel using a signed Claim. - Close the
    channel immediately after processing a Claim, refunding any unclaimed XRP to the
    channel's source.  Any address sending this transaction can: - Cause a channel to be
    closed if its Expiration or CancelAfter time is older than the previous ledger's close
    time. Any validly-formed PaymentChannelClaim transaction has this effect regardless of
    the contents of the transaction.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.PAYMENT_CHANNEL_CLAIM,
        init=False
    )

    amount: Optional[str] = None
    """
    (Optional) The amount of XRP, in drops, authorized by the Signature. This must match the
    amount in the signed message. This is the cumulative amount of XRP that can be dispensed
    by the channel, including XRP previously redeemed.
    """

    balance: Optional[str] = None
    """
    (Optional) Total amount of XRP, in drops, delivered by this channel after processing
    this claim. Required to deliver XRP. Must be more than the total amount delivered by the
    channel so far, but not greater than the Amount of the signed claim. Must be provided
    except when closing the channel.
    """

    channel: str = REQUIRED
    """
    The unique ID of the channel, as a 64-character hexadecimal string.
    """

    credential_ids: Optional[List[str]] = None
    """
    (Optional) Set of Credentials to authorize a deposit made by this transaction. Each
    member of the array must be the ledger entry ID of a Credential entry in the ledger.
    """

    public_key: Optional[str] = None
    """
    (Optional) The public key used for the signature, as hexadecimal. This must match the
    PublicKey stored in the ledger for the channel. Required unless the sender of the
    transaction is the source address of the channel and the Signature field is omitted.
    """

    signature: Optional[str] = None
    """
    (Optional) The signature of this claim, as hexadecimal. The signed message contains the
    channel ID and the amount of the claim. Required unless the sender of the transaction is
    the source address of the channel.
    """

    def _get_errors(self: PaymentChannelClaim) -> Dict[str, str]:
        errors = super._get_errors()
        if self.credential_ids is not None and len(self.credential_ids) < 1:
            errors["PaymentChannelClaim"] = "Field `credential_ids` must have a length greater than or equal to 1"
        if self.credential_ids is not None and len(self.credential_ids) > 8:
            errors["PaymentChannelClaim"] = "Field `credential_ids` must have a length less than or equal to 8"
        if len(self.credential_ids) != len(set(self.credential_ids)):
            errors["PaymentChannelClaim"] = "`credential_ids` list cannot contain duplicate values"
        return errors

class PaymentChannelClaimFlagInterface(FlagInterface):
    """
    Enum for PaymentChannelClaim Transaction Flags.
    """

    TF_RENEW: bool
    TF_CLOSE: bool

class PaymentChannelClaimFlag(int, Enum):
    """
    Enum for PaymentChannelClaim Transaction Flags.
    """

    TF_RENEW = 0x00010000
    """
    Clear the channel&#39;s Expiration time. Only the source address of the payment channel can use this flag.
    """

    TF_CLOSE = 0x00020000
    """
    Request to close the channel. Only the channel source and destination addresses can use this flag. This flag closes the channel immediately if it has no more XRP allocated after processing the current claim, or if the destination address uses it. If the source address uses this flag when the channel still holds XRP, this schedules the channel to close after SettleDelay seconds have passed.
    """


